from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.location_repository import ILocationRepository, BoundingBox
from app.repositories.tenancy_repository import ITenancyRepository
from app.db.postgres.postgres_location_repository import PostgresLocationRepository
from app.db.postgres.postgres_tenancy_repository import PostgresTenancyRepository
from app.schemas.location import LocationDetail, TimelineEntry


class LocationService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._location_repo: ILocationRepository = PostgresLocationRepository(session)
        self._tenancy_repo: ITenancyRepository = PostgresTenancyRepository(session)

    async def get_location_by_id(self, location_id: int) -> Optional[LocationDetail]:
        location = await self._location_repo.get_by_id(location_id)
        if not location:
            return None

        tenancies = await self._tenancy_repo.find_by_location(location_id, limit=3)

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

        return LocationDetail(
            id=location.id,
            lat=location.lat,
            lon=location.lon,
            address=location.address,
            timeline=timeline,
        )

    async def find_locations_in_area(
        self, bbox: BoundingBox, limit: int = 300
    ) -> Sequence[dict]:
        return await self._location_repo.find_with_current_tenancy(bbox, limit)

    async def create_location(
        self, lat: float, lon: float, address: str
    ) -> LocationDetail:
        from app.models.location import Location

        existing = await self._location_repo.find_by_coordinates(lat, lon)
        if existing:
            return await self.get_location_by_id(existing.id)

        location = Location(lat=lat, lon=lon, address=address)
        created = await self._location_repo.create(location)
        await self._session.commit()

        return await self.get_location_by_id(created.id)
