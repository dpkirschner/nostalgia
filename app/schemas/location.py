from datetime import date
from pydantic import BaseModel, Field


class PinOut(BaseModel):
    id: int
    lat: float
    lon: float
    address: str
    current_business: str | None = None
    current_category: str | None = None


class TimelineEntry(BaseModel):
    business_name: str
    category: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool


class LocationDetail(BaseModel):
    id: int
    lat: float
    lon: float
    address: str
    timeline: list[TimelineEntry]


class LocationsResponse(BaseModel):
    locations: list[PinOut]
    count: int
    cursor: str | None = None
