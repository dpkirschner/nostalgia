from typing import TypeVar, Generic, Optional, Sequence
from abc import ABC, abstractmethod

T = TypeVar("T")
ID = TypeVar("ID")


class IRepository(ABC, Generic[T, ID]):
    @abstractmethod
    async def get_by_id(self, id: ID) -> Optional[T]:
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[T]:
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        pass

    @abstractmethod
    async def update(self, id: ID, entity: T) -> Optional[T]:
        pass

    @abstractmethod
    async def delete(self, id: ID) -> bool:
        pass

    @abstractmethod
    async def exists(self, id: ID) -> bool:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass


class BaseRepository(IRepository[T, ID], ABC, Generic[T, ID]):
    def __init__(self, session):
        self._session = session
