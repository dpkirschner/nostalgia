from typing import Sequence
from abc import abstractmethod
from datetime import date

from app.repositories.base import IRepository
from app.models.tenancy import Tenancy


class ITenancyRepository(IRepository[Tenancy, int]):
    @abstractmethod
    async def find_by_location(self, location_id: int, limit: int = 3) -> Sequence[Tenancy]:
        pass

    @abstractmethod
    async def find_current_by_location(self, location_id: int) -> Sequence[Tenancy]:
        pass

    @abstractmethod
    async def find_by_business_name(self, business_name: str) -> Sequence[Tenancy]:
        pass

    @abstractmethod
    async def find_by_date_range(
        self, location_id: int, start_date: date, end_date: date
    ) -> Sequence[Tenancy]:
        pass
