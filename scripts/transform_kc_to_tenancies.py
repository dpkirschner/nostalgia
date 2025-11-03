import asyncio
import logging
from collections import defaultdict
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Tuple, Optional, List

from dateutil.relativedelta import relativedelta
from sqlalchemy import (
    select,
    func,
    update,
    and_,
    desc,
    distinct,
    Table,
    Column,
    String,
    Float,
    Date,
    Integer,
    MetaData,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Row

from app.db.session import AsyncSessionLocal, AsyncSession
from app.models.location import Location
from app.models.tenancy import Tenancy
from app.core.config import settings

# --- Setup & Constants ---

logger = logging.getLogger(__name__)

SOURCE_TYPE_SEED = "seed"
DATASET_KC_INSPECTIONS = "king_county_food_inspections"
DEFAULT_TENANCY_CATEGORY = "UNKNOWN"

# Define the staging view as a SQLAlchemy Table object
metadata = MetaData()
v_kc_norm = Table(
    "v_kc_norm",
    metadata,
    Column("biz", String),
    Column("street", String),
    Column("city", String),
    Column("state", String),
    Column("zip", String),
    Column("lat6", Float),
    Column("lon6", Float),
    Column("inspection_dt", Date),
    Column("row_id", Integer),
    schema="staging",
)


# --- Data Structures ---


class TransformStats:
    def __init__(self):
        self.source_rows = 0
        self.valid_rows = 0
        self.locations_created = 0
        self.tenancies_upserted = 0
        self.consistency_fixes = 0
        self.skipped_rows = 0


def _normalize_address(address: Optional[str]) -> str:
    if not address:
        return ""
    return address.upper().strip()


class LocationCache:
    def __init__(self):
        self.cache: Dict[Tuple[float, float, str], int] = {}

    def get(self, lat: float, lon: float, address: str) -> Optional[int]:
        key = (lat, lon, _normalize_address(address))
        return self.cache.get(key)

    def set(self, lat: float, lon: float, address: str, location_id: int):
        key = (lat, lon, _normalize_address(address))
        self.cache[key] = location_id

    def __len__(self) -> int:
        return len(self.cache)


# --- Database Functions ---


async def preload_location_cache(session: AsyncSession, cache: LocationCache):
    """
    Pre-loads all existing locations from the database into the cache
    to prevent N+1 queries in the main loop.
    """
    logger.info("Pre-loading location cache...")
    stmt = select(Location.id, Location.lat, Location.lon, Location.address)
    result = await session.execute(stmt)
    for loc in result.all():
        cache.set(loc.lat, loc.lon, loc.address, loc.id)
    logger.info(f"Pre-loaded {len(cache)} locations.")


async def get_or_create_location(
    session: AsyncSession,
    lat: float,
    lon: float,
    address: str,
    cache: LocationCache,
    stats: TransformStats,
) -> int:
    """
    Gets a location ID from the cache or creates a new one.
    The N+1 select query is removed; this function now only hits the
    DB for *new* locations.
    """
    norm_address = _normalize_address(address)
    cached_id = cache.get(lat, lon, norm_address)
    if cached_id:
        return cached_id

    # Not in cache, create it
    location = Location(lat=lat, lon=lon, address=norm_address)
    session.add(location)
    await session.flush()  # Flush to get the new location.id

    stats.locations_created += 1
    cache.set(lat, lon, norm_address, location.id)
    return location.id


async def fetch_normalized_inspections(session: AsyncSession) -> List[Row]:
    """Fetches all inspection data, correctly ordered for grouping."""
    query = select(v_kc_norm).order_by(
        v_kc_norm.c.lat6,
        v_kc_norm.c.lon6,
        v_kc_norm.c.street,
        v_kc_norm.c.biz,
        v_kc_norm.c.inspection_dt,
    )

    result = await session.execute(query)
    return result.all()


async def group_into_tenancy_candidates(
    inspections: List[Row],
    location_cache: LocationCache,
    session: AsyncSession,
    stats: TransformStats,
) -> List[Dict]:
    """
    Groups inspection rows into distinct tenancy candidates based on
    a composite key of (location_id, business_name).
    """
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
                "type": SOURCE_TYPE_SEED,
                "dataset": DATASET_KC_INSPECTIONS,
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
                "category": DEFAULT_TENANCY_CATEGORY,
            }
        )

    return tenancy_candidates


def calculate_is_current(
    end_date: Optional[date], recent_months: int
) -> bool:
    """Accurately calculates if a tenancy is current."""
    if end_date is None:
        return False

    cutoff_date = datetime.now().date() - relativedelta(
        months=recent_months
    )
    return end_date >= cutoff_date


async def upsert_tenancies(
    session: AsyncSession, candidates: List[Dict], stats: TransformStats
):
    """
    Performs a single, batch "upsert" for a list of tenancy candidates.
    """
    if not candidates:
        return

    recent_months = settings.recent_months
    values_list = []

    for candidate in candidates:
        is_current = calculate_is_current(
            candidate["end_date"], recent_months
        )
        values_list.append(
            {
                "location_id": candidate["location_id"],
                "business_name": candidate["business_name"],
                "start_date": candidate["start_date"],
                "end_date": candidate["end_date"],
                "is_current": is_current,
                "sources": candidate["sources"],
                "category": candidate["category"],
            }
        )

    stmt = insert(Tenancy).values(values_list)

    stmt = stmt.on_conflict_do_update(
        index_elements=["location_id", "business_name"],
        set_={
            "start_date": func.least(Tenancy.start_date, stmt.excluded.start_date),
            "end_date": func.greatest(Tenancy.end_date, stmt.excluded.end_date),
            "is_current": stmt.excluded.is_current,
            "sources": stmt.excluded.sources,
            # Note: category is not updated on conflict, only set on insert
        },
    )

    result = await session.execute(stmt)
    stats.tenancies_upserted += result.rowcount


async def enforce_consistency(session: AsyncSession, stats: TransformStats):
    """
    Ensures data consistency by:
    1. Setting `is_current = false` for all but the most recent tenancy
       at locations with multiple "current" tenancies.
    2. Setting `is_current = false` for any tenancies that haven't
       been seen in `OUTDATED_TENANCY_MONTHS`.
    """
    fixes = 0

    # 1. Fix locations with multiple current tenancies
    latest_per_location_cte = (
        select(
            Tenancy.location_id,
            func.max(Tenancy.end_date).label("max_end_date"),
        )
        .where(Tenancy.is_current == True)
        .group_by(Tenancy.location_id)
        .having(func.count(Tenancy.id) > 1)
        .cte("latest_per_location")
    )

    # Subquery to find rows that are NOT the max_end_date
    subquery = (
        select(Tenancy.id)
        .join(
            latest_per_location_cte,
            Tenancy.location_id == latest_per_location_cte.c.location_id,
        )
        .where(Tenancy.end_date < latest_per_location_cte.c.max_end_date)
        .where(Tenancy.is_current == True)
    )

    update_multi_current_stmt = (
        update(Tenancy)
        .where(Tenancy.id.in_(subquery))
        .values(is_current=False)
    )

    result = await session.execute(update_multi_current_stmt)
    fixes += result.rowcount

    # 2. Fix outdated tenancies
    outdated_cutoff = datetime.now().date() - relativedelta(
        months=settings.outdated_tenancy_months
    )

    update_outdated_stmt = (
        update(Tenancy)
        .where(Tenancy.is_current == True)
        .where(Tenancy.end_date < outdated_cutoff)
        .values(is_current=False)
    )

    result = await session.execute(update_outdated_stmt)
    fixes += result.rowcount

    stats.consistency_fixes = fixes


# --- Reporting & Main Execution ---


async def generate_qa_report(session: AsyncSession, stats: TransformStats):
    """Logs a QA report to the console."""
    logger.info("\n" + "=" * 80)
    logger.info("QA REPORT")
    logger.info("=" * 80)

    logger.info(f"\nProcessing Summary:")
    logger.info(f"  Total source rows (from v_kc_norm): {stats.source_rows}")
    logger.info(f"  Valid rows processed: {stats.valid_rows}")
    logger.info(f"  Skipped rows: {stats.skipped_rows}")

    logger.info(f"\nData Created/Updated:")
    logger.info(f"  New locations created: {stats.locations_created}")
    logger.info(f"  Tenancies upserted: {stats.tenancies_upserted}")
    logger.info(f"  Consistency fixes applied: {stats.consistency_fixes}")

    # Top 10 Locations
    stmt_top_loc = (
        select(
            Location.id,
            Location.address,
            Location.lat,
            Location.lon,
            func.count(Tenancy.id).label("tenancy_count"),
        )
        .join(Tenancy, Tenancy.location_id == Location.id)
        .group_by(Location.id)
        .order_by(desc("tenancy_count"))
        .limit(10)
    )
    result = await session.execute(stmt_top_loc)
    top_locations = result.fetchall()

    logger.info(f"\nTop 10 Locations by Tenancy Count:")
    for idx, loc in enumerate(top_locations, 1):
        logger.info(
            f"  {idx}. {loc.address[:50]:50} | ({loc.lat:.6f}, {loc.lon:.6f}) | {loc.tenancy_count} tenancies"
        )

    # Sample Current Tenancies
    recent_cutoff = datetime.now().date() - relativedelta(months=6)
    stmt_recent = (
        select(Tenancy.business_name, Location.address, Tenancy.end_date)
        .join(Location, Location.id == Tenancy.location_id)
        .where(
            and_(
                Tenancy.is_current == True,
                Tenancy.end_date >= recent_cutoff,
            )
        )
        .order_by(desc(Tenancy.end_date))
        .limit(10)
    )
    result = await session.execute(stmt_recent)
    recent_current = result.fetchall()

    logger.info(f"\nSample Current Tenancies (last 6 months):")
    for idx, tenancy in enumerate(recent_current, 1):
        logger.info(
            f"  {idx}. {tenancy.business_name[:40]:40} | {tenancy.address[:30]:30} | {tenancy.end_date}"
        )

    # Totals
    current_count = await session.scalar(
        select(func.count(Tenancy.id)).where(Tenancy.is_current == True)
    )
    logger.info(f"\nTotal current tenancies: {current_count}")

    locations_with_tenancies = await session.scalar(
        select(func.count(distinct(Tenancy.location_id)))
    )
    logger.info(f"Locations with tenancies: {locations_with_tenancies}")


async def transform_kc_to_tenancies(batch_size: int = 4000):
    stats = TransformStats()
    location_cache = LocationCache()

    async with AsyncSessionLocal() as session:
        await preload_location_cache(session, location_cache)

        logger.info("Fetching normalized inspections from staging.v_kc_norm...")
        inspections = await fetch_normalized_inspections(session)
        stats.source_rows = len(inspections)
        logger.info(
            f"Fetched {stats.source_rows} normalized inspection records"
        )

        if stats.source_rows == 0:
            logger.warning("\nNo data to process. Exiting.")
            return

        logger.info("\nGrouping inspections into tenancy candidates...")
        tenancy_candidates = await group_into_tenancy_candidates(
            inspections, location_cache, session, stats
        )
        logger.info(f"Created {len(tenancy_candidates)} tenancy candidates")
        await session.commit()  # Commit new locations
        logger.info(f"Committed {stats.locations_created} new locations.")


        logger.info("\nUpserting tenancies (with batch logic)...")
        for i in range(0, len(tenancy_candidates), batch_size):
            batch = tenancy_candidates[i : i + batch_size]
            await upsert_tenancies(session, batch, stats)
            await session.commit()
            logger.info(
                f"  Committed batch: {i + len(batch)}/{len(tenancy_candidates)} candidates processed"
            )

        logger.info("\nEnforcing consistency (one current per location)...")
        await enforce_consistency(session, stats)
        await session.commit()
        logger.info("Consistency enforcement complete")

        await generate_qa_report(session, stats)

        logger.info("\n" + "=" * 80)
        logger.info("TRANSFORMATION COMPLETE")
        logger.info("=" * 80)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()
        ],
    )
    
    # Example: get batch size from settings or keep default
    batch_size = getattr(settings, "ETL_BATCH_SIZE", 4000)

    logger.info("=" * 80)
    logger.info("KC FOOD INSPECTIONS → LOCATIONS & TENANCIES TRANSFORMATION")
    logger.info("=" * 80)
    logger.info(f"\nConfiguration:")
    logger.info(f"  Round places: {settings.round_places}")
    logger.info(
        f"  Recent months threshold: {settings.recent_months}"
    )
    logger.info(
        f"  Outdated tenancy months: {settings.outdated_tenancy_months}"
    )
    logger.info(f"  Batch size: {batch_size}")
    logger.info("\n" + "-" * 80 + "\n")

    asyncio.run(transform_kc_to_tenancies(batch_size))