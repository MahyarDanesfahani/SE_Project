from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Announcement(Base):
    __tablename__ = "announcements"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    university_id: Mapped[UUID | None] = mapped_column(ForeignKey("universities.id"), index=True)
    title: Mapped[str] = mapped_column(String(250))
    body: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(80), default="general")
    source_name: Mapped[str] = mapped_column(String(150))
    source_url: Mapped[str] = mapped_column(String(500))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    __table_args__ = (UniqueConstraint("university_id", "source_url", name="uq_announcement_source"),)
