from typing import Optional, Sequence
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

from app.db.postgres.postgres_repository import PostgresRepository
from app.repositories.location_repository import ILocationRepository, BoundingBox
from app.models.location import Location


class PostgresLocationRepository(PostgresRepository[Location, int], ILocationRepository):
    def __init__(self, session):
        super().__init__(session, Location)

    async def find_by_coordinates(
        self, lat: float, lon: float, tolerance: float = 0.0001
    ) -> Optional[Location]:
        stmt = select(self._model).where(
            (self._model.lat.between(lat - tolerance, lat + tolerance))
            & (self._model.lon.between(lon - tolerance, lon + tolerance))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_in_bounding_box(self, bbox: BoundingBox, limit: int = 300) -> Sequence[Location]:
        stmt = (
            select(self._model)
            .where(
                (self._model.lat.between(bbox.south, bbox.north))
                & (self._model.lon.between(bbox.west, bbox.east))
            )
            .options(selectinload(self._model.tenancies))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def find_with_current_tenancy(
        self, bbox: BoundingBox, limit: int = 300
    ) -> Sequence[dict]:
        query = text(
            """
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
        """
        )

        result = await self._session.execute(
            query,
            {
                "south": bbox.south,
                "north": bbox.north,
                "west": bbox.west,
                "east": bbox.east,
                "limit": limit,
            },
        )

        return [dict(row._mapping) for row in result]
