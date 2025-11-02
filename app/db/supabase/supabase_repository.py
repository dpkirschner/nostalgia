from typing import TypeVar, Generic, Type, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from app.repositories.base import BaseRepository
from app.db.base import Base

T = TypeVar("T", bound=Base)
ID = TypeVar("ID")


class SupabaseRepository(BaseRepository[T, ID], Generic[T, ID]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        super().__init__(session)
        self._model = model

    async def get_by_id(self, id: ID) -> Optional[T]:
        stmt = select(self._model).where(self._model.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[T]:
        stmt = select(self._model).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, id: ID, entity: T) -> Optional[T]:
        existing = await self.get_by_id(id)
        if not existing:
            return None

        for key, value in entity.__dict__.items():
            if not key.startswith("_"):
                setattr(existing, key, value)

        await self._session.flush()
        await self._session.refresh(existing)
        return existing

    async def delete(self, id: ID) -> bool:
        stmt = delete(self._model).where(self._model.id == id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def exists(self, id: ID) -> bool:
        stmt = select(func.count()).select_from(self._model).where(self._model.id == id)
        result = await self._session.execute(stmt)
        count = result.scalar()
        return count > 0

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self._model)
        result = await self._session.execute(stmt)
        return result.scalar()
