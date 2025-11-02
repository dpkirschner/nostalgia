from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import Counter

from app.db.session import get_db
from app.models.location import Location
from app.models.tenancy import Tenancy
from app.schemas.location import LocationDetail, LocationsResponse, PinOut, TimelineEntry

router = APIRouter(prefix="/v1/locations", tags=["locations"])

pins_returned_counter = Counter(
    "wutbh_pins_returned_total",
    "Total number of location pins returned"
)

detail_view_counter = Counter(
    "wutbh_detail_view_total",
    "Total number of location detail views"
)


@router.get("", response_model=LocationsResponse)
async def get_locations(
    bbox: str = Query(..., description="Bounding box: west,south,east,north"),
    limit: int = Query(300, ge=1, le=1000),
    cursor: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    try:
        coords = [float(x) for x in bbox.split(",")]
        if len(coords) != 4:
            raise ValueError("bbox must have exactly 4 coordinates")
        west, south, east, north = coords

        if not (-180 <= west <= 180 and -180 <= east <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        if not (-90 <= south <= 90 and -90 <= north <= 90):
            raise ValueError("Latitude must be between -90 and 90")

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid bbox format. Expected 'west,south,east,north': {str(e)}"
        )

    query = text("""
        SELECT
            l.id,
            l.lat,
            l.lon,
            l.address,
            v.business_name as current_business,
            v.category as current_category
        FROM locations l
        LEFT JOIN v_latest_tenancy v ON l.id = v.location_id
        WHERE l.lat BETWEEN :south AND :north
          AND l.lon BETWEEN :west AND :east
        ORDER BY l.id
        LIMIT :limit
    """)

    result = await db.execute(
        query,
        {
            "south": south,
            "north": north,
            "west": west,
            "east": east,
            "limit": limit
        }
    )
    rows = result.fetchall()

    pins = [
        PinOut(
            id=row.id,
            lat=row.lat,
            lon=row.lon,
            address=row.address,
            current_business=row.current_business,
            current_category=row.current_category,
        )
        for row in rows
    ]

    pins_returned_counter.inc(len(pins))

    return LocationsResponse(
        locations=pins,
        count=len(pins),
        cursor=None
    )


@router.get("/{location_id}", response_model=LocationDetail)
async def get_location_detail(
    location_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    result = await db.execute(
        select(Tenancy)
        .where(Tenancy.location_id == location_id)
        .order_by(
            Tenancy.is_current.desc(),
            Tenancy.end_date.desc().nulls_first(),
            Tenancy.created_at.desc()
        )
        .limit(3)
    )
    tenancies = result.scalars().all()

    timeline = [
        TimelineEntry(
            business_name=t.business_name,
            category=t.category,
            start_date=t.start_date,
            end_date=t.end_date,
            is_current=t.is_current,
        )
        for t in tenancies
    ]

    detail_view_counter.inc()

    return LocationDetail(
        id=location.id,
        lat=location.lat,
        lon=location.lon,
        address=location.address,
        timeline=timeline,
    )
