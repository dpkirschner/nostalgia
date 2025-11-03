import asyncio
import sys
from collections import defaultdict
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Dict, Tuple, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, select
from sqlalchemy.dialects.postgresql import insert

from app.db.session import AsyncSessionLocal
from app.models.location import Location
from app.models.tenancy import Tenancy
from app.core.config import settings


class TransformStats:
    def __init__(self):
        self.source_rows = 0
        self.valid_rows = 0
        self.locations_created = 0
        self.tenancies_created = 0
        self.tenancies_updated = 0
        self.consistency_fixes = 0
        self.skipped_rows = 0


class LocationCache:
    def __init__(self):
        self.cache: Dict[Tuple[float, float, str], int] = {}

    def get(self, lat: float, lon: float, address: str) -> Optional[int]:
        key = (lat, lon, address)
        return self.cache.get(key)

    def set(self, lat: float, lon: float, address: str, location_id: int):
        key = (lat, lon, address)
        self.cache[key] = location_id


async def get_or_create_location(
    session, lat: float, lon: float, address: str, cache: LocationCache, stats: TransformStats
) -> int:
    cached_id = cache.get(lat, lon, address)
    if cached_id:
        return cached_id

    result = await session.execute(
        select(Location.id)
        .where(Location.lat == lat)
        .where(Location.lon == lon)
        .where(Location.address == address)
    )
    existing = result.scalar_one_or_none()

    if existing:
        cache.set(lat, lon, address, existing)
        return existing

    location = Location(lat=lat, lon=lon, address=address)
    session.add(location)
    await session.flush()

    stats.locations_created += 1
    cache.set(lat, lon, address, location.id)
    return location.id


async def fetch_normalized_inspections(session):
    query = text(
        """
        SELECT
            biz,
            street,
            city,
            state,
            zip,
            lat6,
            lon6,
            inspection_dt,
            row_id
        FROM staging.v_kc_norm
        ORDER BY lat6, lon6, street, biz, inspection_dt
    """
    )

    result = await session.execute(query)
    return result.fetchall()


async def group_into_tenancy_candidates(inspections, location_cache, session, stats):
    candidates = defaultdict(
        lambda: {
            "location_id": None,
            "business_name": None,
            "dates": [],
            "address": None,
            "lat": None,
            "lon": None,
        }
    )

    for row in inspections:
        biz = row.biz
        street = row.street
        lat6 = float(row.lat6)
        lon6 = float(row.lon6)
        inspection_dt = row.inspection_dt

        stats.valid_rows += 1

        location_id = await get_or_create_location(
            session, lat6, lon6, street, location_cache, stats
        )

        key = (location_id, biz)
        candidate = candidates[key]

        if candidate["location_id"] is None:
            candidate["location_id"] = location_id
            candidate["business_name"] = biz
            candidate["address"] = street
            candidate["lat"] = lat6
            candidate["lon"] = lon6

        if inspection_dt:
            candidate["dates"].append(inspection_dt)

    tenancy_candidates = []
    for (location_id, business_name), data in candidates.items():
        if not data["dates"]:
            start_date = None
            end_date = None
        else:
            start_date = min(data["dates"])
            end_date = max(data["dates"])

        sources = [
            {
                "type": "seed",
                "dataset": "king_county_food_inspections",
                "first_seen": start_date.isoformat() if start_date else None,
                "last_seen": end_date.isoformat() if end_date else None,
                "inspection_count": len(data["dates"]),
            }
        ]

        tenancy_candidates.append(
            {
                "location_id": location_id,
                "business_name": business_name,
                "start_date": start_date,
                "end_date": end_date,
                "sources": sources,
                "address": data["address"],
            }
        )

    return tenancy_candidates


def calculate_is_current(end_date: Optional[date], recent_months: int) -> bool:
    if end_date is None:
        return False

    cutoff_date = datetime.now().date() - timedelta(days=recent_months * 30)
    return end_date >= cutoff_date


async def upsert_tenancies(session, candidates, stats):
    recent_months = settings.recent_months

    for candidate in candidates:
        location_id = candidate["location_id"]
        business_name = candidate["business_name"]
        start_date = candidate["start_date"]
        end_date = candidate["end_date"]
        sources = candidate["sources"]

        is_current = calculate_is_current(end_date, recent_months)

        stmt = insert(Tenancy).values(
            location_id=location_id,
            business_name=business_name,
            start_date=start_date,
            end_date=end_date,
            is_current=is_current,
            sources=sources,
            category=None,
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["location_id", "business_name"],
            set_={
                "start_date": text("LEAST(tenancies.start_date, EXCLUDED.start_date)"),
                "end_date": text("GREATEST(tenancies.end_date, EXCLUDED.end_date)"),
                "is_current": stmt.excluded.is_current,
                "sources": stmt.excluded.sources,
            },
        )

        result = await session.execute(stmt)
        if result.rowcount == 1:
            stats.tenancies_created += 1
        else:
            stats.tenancies_updated += 1


async def enforce_consistency(session, stats):
    query = text(
        """
        WITH latest_per_location AS (
            SELECT
                location_id,
                MAX(end_date) AS max_end_date
            FROM tenancies
            WHERE is_current = true
            GROUP BY location_id
            HAVING COUNT(*) > 1
        )
        UPDATE tenancies
        SET is_current = false
        WHERE is_current = true
        AND (location_id, end_date) IN (
            SELECT l.location_id, t.end_date
            FROM latest_per_location l
            JOIN tenancies t ON t.location_id = l.location_id
            WHERE t.end_date < l.max_end_date
        )
    """
    )

    result = await session.execute(query)
    fixes = result.rowcount

    query_outdated = text(
        """
        UPDATE tenancies
        SET is_current = false
        WHERE is_current = true
        AND end_date < CURRENT_DATE - INTERVAL '18 months'
    """
    )

    result = await session.execute(query_outdated)
    fixes += result.rowcount

    stats.consistency_fixes = fixes


async def generate_qa_report(session, stats):
    print("\n" + "=" * 80)
    print("QA REPORT")
    print("=" * 80)

    print(f"\nProcessing Summary:")
    print(f"  Total source rows (from v_kc_norm): {stats.source_rows}")
    print(f"  Valid rows processed: {stats.valid_rows}")
    print(f"  Skipped rows: {stats.skipped_rows}")

    print(f"\nData Created/Updated:")
    print(f"  New locations created: {stats.locations_created}")
    print(f"  New tenancies created: {stats.tenancies_created}")
    print(f"  Existing tenancies updated: {stats.tenancies_updated}")
    print(f"  Consistency fixes applied: {stats.consistency_fixes}")

    result = await session.execute(
        text(
            """
        SELECT
            l.id,
            l.address,
            l.lat,
            l.lon,
            COUNT(t.id) AS tenancy_count
        FROM locations l
        JOIN tenancies t ON t.location_id = l.id
        GROUP BY l.id, l.address, l.lat, l.lon
        ORDER BY tenancy_count DESC
        LIMIT 10
    """
        )
    )
    top_locations = result.fetchall()

    print(f"\nTop 10 Locations by Tenancy Count:")
    for idx, loc in enumerate(top_locations, 1):
        print(
            f"  {idx}. {loc.address[:50]:50} | ({loc.lat:.6f}, {loc.lon:.6f}) | {loc.tenancy_count} tenancies"
        )

    result = await session.execute(
        text(
            """
        SELECT
            t.business_name,
            l.address,
            t.end_date,
            t.is_current
        FROM tenancies t
        JOIN locations l ON l.id = t.location_id
        WHERE t.is_current = true
        AND t.end_date >= CURRENT_DATE - INTERVAL '6 months'
        ORDER BY t.end_date DESC
        LIMIT 10
    """
        )
    )
    recent_current = result.fetchall()

    print(f"\nSample Current Tenancies (last 6 months):")
    for idx, tenancy in enumerate(recent_current, 1):
        print(
            f"  {idx}. {tenancy.business_name[:40]:40} | {tenancy.address[:30]:30} | {tenancy.end_date}"
        )

    result = await session.execute(
        text(
            """
        SELECT COUNT(*) AS total
        FROM tenancies
        WHERE is_current = true
    """
        )
    )
    current_count = result.scalar()
    print(f"\nTotal current tenancies: {current_count}")

    result = await session.execute(
        text(
            """
        SELECT COUNT(DISTINCT location_id) AS total
        FROM tenancies
    """
        )
    )
    locations_with_tenancies = result.scalar()
    print(f"Locations with tenancies: {locations_with_tenancies}")


async def transform_kc_to_tenancies(batch_size: int = 5000):
    stats = TransformStats()
    location_cache = LocationCache()

    async with AsyncSessionLocal() as session:
        print("Fetching normalized inspections from staging.v_kc_norm...")
        inspections = await fetch_normalized_inspections(session)
        stats.source_rows = len(inspections)
        print(f"Fetched {stats.source_rows} normalized inspection records")

        if stats.source_rows == 0:
            print("\nNo data to process. Exiting.")
            return

        print("\nGrouping inspections into tenancy candidates...")
        tenancy_candidates = await group_into_tenancy_candidates(
            inspections, location_cache, session, stats
        )
        print(f"Created {len(tenancy_candidates)} tenancy candidates")

        print("\nUpserting tenancies (with idempotent logic)...")
        batch = []
        for idx, candidate in enumerate(tenancy_candidates, 1):
            batch.append(candidate)

            if len(batch) >= batch_size:
                await upsert_tenancies(session, batch, stats)
                await session.commit()
                print(f"  Committed batch: {idx}/{len(tenancy_candidates)} candidates processed")
                batch = []

        if batch:
            await upsert_tenancies(session, batch, stats)
            await session.commit()
            print(f"  Committed final batch: {len(tenancy_candidates)} candidates processed")

        print("\nEnforcing consistency (one current per location)...")
        await enforce_consistency(session, stats)
        await session.commit()
        print("Consistency enforcement complete")

        await generate_qa_report(session, stats)

        print("\n" + "=" * 80)
        print("TRANSFORMATION COMPLETE")
        print("=" * 80)


if __name__ == "__main__":
    batch_size = 5000
    if len(sys.argv) >= 2:
        try:
            batch_size = int(sys.argv[1])
        except ValueError:
            print(f"Warning: Invalid batch_size '{sys.argv[1]}', using default: 5000")

    print("=" * 80)
    print("KC FOOD INSPECTIONS → LOCATIONS & TENANCIES TRANSFORMATION")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  Round places: {settings.round_places}")
    print(f"  Recent months threshold: {settings.recent_months}")
    print(f"  Batch size: {batch_size}")
    print("\n" + "-" * 80 + "\n")

    asyncio.run(transform_kc_to_tenancies(batch_size))
