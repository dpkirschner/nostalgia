from typing import Sequence
from sqlalchemy import select

from app.db.supabase.supabase_repository import SupabaseRepository
from app.repositories.memory_repository import IMemoryRepository
from app.models.memory_submission import MemorySubmission


class SupabaseMemoryRepository(
    SupabaseRepository[MemorySubmission, int], IMemoryRepository
):
    def __init__(self, session):
        super().__init__(session, MemorySubmission)

    async def find_by_location(self, location_id: int) -> Sequence[MemorySubmission]:
        stmt = (
            select(self._model)
            .where(self._model.location_id == location_id)
            .order_by(self._model.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def find_by_status(self, status: str) -> Sequence[MemorySubmission]:
        stmt = (
            select(self._model)
            .where(self._model.status == status)
            .order_by(self._model.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def find_pending(self, limit: int = 50) -> Sequence[MemorySubmission]:
        stmt = (
            select(self._model)
            .where(self._model.status == "pending")
            .order_by(self._model.created_at.asc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
