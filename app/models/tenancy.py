from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Tenancy(Base):
    __tablename__ = "tenancies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False
    )
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sources: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    location: Mapped["Location"] = relationship("Location", back_populates="tenancies")

    __table_args__ = (
        Index("idx_tenancies_location_id", "location_id"),
    )
