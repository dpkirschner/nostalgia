from typing import Sequence
from abc import abstractmethod

from app.repositories.base import IRepository
from app.models.memory_submission import MemorySubmission


class IMemoryRepository(IRepository[MemorySubmission, int]):
    @abstractmethod
    async def find_by_location(self, location_id: int) -> Sequence[MemorySubmission]:
        pass

    @abstractmethod
    async def find_by_status(self, status: str) -> Sequence[MemorySubmission]:
        pass

    @abstractmethod
    async def find_pending(self, limit: int = 50) -> Sequence[MemorySubmission]:
        pass
