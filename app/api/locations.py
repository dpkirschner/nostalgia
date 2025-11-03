from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import Counter

from app.db.postgres import get_db
from app.services.location_service import LocationService
from app.repositories.location_repository import BoundingBox
from app.schemas.location import LocationDetail, LocationsResponse, PinOut

router = APIRouter(prefix="/v1/locations", tags=["locations"])

pins_returned_counter = Counter(
    "wutbh_pins_returned_total", "Total number of location pins returned"
)

detail_view_counter = Counter("wutbh_detail_view_total", "Total number of location detail views")


def get_location_service(session: AsyncSession = Depends(get_db)) -> LocationService:
    return LocationService(session)


@router.get("", response_model=LocationsResponse)
async def get_locations(
    bbox: str = Query(..., description="Bounding box: west,south,east,north"),
    limit: int = Query(300, ge=1, le=1000),
    cursor: str | None = Query(None),
    service: LocationService = Depends(get_location_service),
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
            detail=f"Invalid bbox format. Expected 'west,south,east,north': {str(e)}",
        )

    bounding_box = BoundingBox(west, south, east, north)
    rows = await service.find_locations_in_area(bounding_box, limit)

    pins = [
        PinOut(
            id=row["id"],
            lat=row["lat"],
            lon=row["lon"],
            address=row["address"],
            current_business=row["current_business"],
            current_category=row["current_category"],
        )
        for row in rows
    ]

    pins_returned_counter.inc(len(pins))

    return LocationsResponse(locations=pins, count=len(pins), cursor=None)


@router.get("/{location_id}", response_model=LocationDetail)
async def get_location_detail(
    location_id: int,
    service: LocationService = Depends(get_location_service),
):
    location = await service.get_location_by_id(location_id)

    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    detail_view_counter.inc()

    return location
