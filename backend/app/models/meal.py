from datetime import date, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class MealReservationStatus(StrEnum):
    PENDING_INTERNAL = "pending_internal"
    CONFIRMED_EXTERNAL = "confirmed_external"
    FAILED = "failed"
    UNKNOWN = "unknown"


class MealMenuItem(Base):
    __tablename__ = "meal_menu_items"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    university_id: Mapped[UUID | None] = mapped_column(ForeignKey("universities.id"), index=True)
    service_date: Mapped[date] = mapped_column(Date)
    meal_type: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(200))
    price: Mapped[int | None] = mapped_column(Integer)
    source_name: Mapped[str] = mapped_column(String(150), default="manual_demo")
    source_url: Mapped[str] = mapped_column(String(500), default="https://student.znu.ac.ir/")
    __table_args__ = (UniqueConstraint("university_id", "service_date", "meal_type", name="uq_meal_menu_slot"),)


class MealReservation(Base):
    __tablename__ = "meal_reservations"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    menu_item_id: Mapped[UUID] = mapped_column(ForeignKey("meal_menu_items.id"), index=True)
    status: Mapped[MealReservationStatus] = mapped_column(String(30), default=MealReservationStatus.PENDING_INTERNAL)
    external_reference: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
