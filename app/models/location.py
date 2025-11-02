from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    tenancies: Mapped[list["Tenancy"]] = relationship(
        "Tenancy", back_populates="location", lazy="selectin"
    )
    memory_submissions: Mapped[list["MemorySubmission"]] = relationship(
        "MemorySubmission", back_populates="location", lazy="selectin"
    )

    __table_args__ = (
        Index("idx_locations_lat_lon", "lat", "lon"),
    )
