from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.memory_repository import IMemoryRepository
from app.db.postgres.postgres_memory_repository import PostgresMemoryRepository
from app.schemas.memory import MemorySubmissionCreate, MemorySubmissionResponse
from app.models.memory_submission import MemorySubmission
from app.core.logging import get_logger

logger = get_logger(__name__)


class MemoryService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._memory_repo: IMemoryRepository = PostgresMemoryRepository(session)

    async def submit_memory(
        self, memory_data: MemorySubmissionCreate
    ) -> MemorySubmissionResponse:
        logger.info(
            f"Submitting memory for location {memory_data.location_id}: {memory_data.business_name}"
        )

        memory = MemorySubmission(
            location_id=memory_data.location_id,
            business_name=memory_data.business_name,
            start_year=memory_data.start_year,
            end_year=memory_data.end_year,
            note=memory_data.note,
            proof_url=memory_data.proof_url,
            source="anon",
            status="pending",
        )

        created = await self._memory_repo.create(memory)
        await self._session.commit()
        logger.info(f"Memory submission created with id {created.id}")

        return MemorySubmissionResponse(
            id=created.id,
            location_id=created.location_id,
            business_name=created.business_name,
            status=created.status,
        )

    async def get_pending_reviews(self, limit: int = 50) -> Sequence[MemorySubmission]:
        return await self._memory_repo.find_pending(limit)

    async def get_by_location(self, location_id: int) -> Sequence[MemorySubmission]:
        return await self._memory_repo.find_by_location(location_id)
