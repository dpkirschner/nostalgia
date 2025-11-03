from typing import Optional, Sequence
from abc import abstractmethod

from app.repositories.base import IRepository
from app.models.location import Location


class BoundingBox:
    def __init__(self, west: float, south: float, east: float, north: float):
        self.west = west
        self.south = south
        self.east = east
        self.north = north


class ILocationRepository(IRepository[Location, int]):
    @abstractmethod
    async def find_by_coordinates(
        self, lat: float, lon: float, tolerance: float = 0.0001
    ) -> Optional[Location]:
        pass

    @abstractmethod
    async def find_in_bounding_box(self, bbox: BoundingBox, limit: int = 300) -> Sequence[Location]:
        pass

    @abstractmethod
    async def find_with_current_tenancy(
        self, bbox: BoundingBox, limit: int = 300
    ) -> Sequence[dict]:
        pass
