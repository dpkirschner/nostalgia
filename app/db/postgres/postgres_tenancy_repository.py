from typing import Sequence
from datetime import date
from sqlalchemy import select, or_, and_

from app.db.postgres.postgres_repository import PostgresRepository
from app.repositories.tenancy_repository import ITenancyRepository
from app.models.tenancy import Tenancy


class PostgresTenancyRepository(PostgresRepository[Tenancy, int], ITenancyRepository):
    def __init__(self, session):
        super().__init__(session, Tenancy)

    async def find_by_location(self, location_id: int, limit: int = 3) -> Sequence[Tenancy]:
        stmt = (
            select(self._model)
            .where(self._model.location_id == location_id)
            .order_by(
                self._model.is_current.desc(),
                self._model.end_date.desc().nulls_first(),
                self._model.created_at.desc(),
            )
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def find_current_by_location(self, location_id: int) -> Sequence[Tenancy]:
        stmt = select(self._model).where(
            and_(
                self._model.location_id == location_id,
                self._model.is_current == True,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def find_by_business_name(self, business_name: str) -> Sequence[Tenancy]:
        stmt = select(self._model).where(self._model.business_name.ilike(f"%{business_name}%"))
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def find_by_date_range(
        self, location_id: int, start_date: date, end_date: date
    ) -> Sequence[Tenancy]:
        stmt = select(self._model).where(
            and_(
                self._model.location_id == location_id,
                or_(
                    and_(
                        self._model.start_date <= end_date,
                        self._model.end_date >= start_date,
                    ),
                    and_(
                        self._model.start_date <= end_date,
                        self._model.end_date.is_(None),
                    ),
                ),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
