from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class MemorySubmission(Base):
    __tablename__ = "memory_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False
    )
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    proof_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="anon", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    location: Mapped["Location"] = relationship("Location", back_populates="memory_submissions")

    __table_args__ = (
        Index("idx_memory_submissions_location_id", "location_id"),
        Index("idx_memory_submissions_status", "status"),
    )
