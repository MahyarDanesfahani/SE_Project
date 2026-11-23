from datetime import date, datetime, time
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Term(Base):
    __tablename__ = "terms"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    university_id: Mapped[UUID | None] = mapped_column(ForeignKey("universities.id"), index=True)
    title: Mapped[str] = mapped_column(String(100))
    academic_year: Mapped[str] = mapped_column(String(20))
    semester_number: Mapped[int] = mapped_column(Integer)
    starts_on: Mapped[date | None] = mapped_column(Date)
    ends_on: Mapped[date | None] = mapped_column(Date)
    __table_args__ = (UniqueConstraint("university_id", "academic_year", "semester_number", name="uq_term_scope"),)


class CourseOffering(Base):
    __tablename__ = "course_offerings"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    term_id: Mapped[UUID] = mapped_column(ForeignKey("terms.id"), index=True)
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id"), index=True)
    section: Mapped[str] = mapped_column(String(30))
    instructor: Mapped[str | None] = mapped_column(String(150))
    capacity: Mapped[int | None] = mapped_column(Integer)
    credits: Mapped[int] = mapped_column(Integer)
    capacity_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sessions: Mapped[list["ClassSession"]] = relationship(back_populates="offering", cascade="all, delete-orphan")
    course: Mapped["Course"] = relationship()
    __table_args__ = (UniqueConstraint("owner_user_id", "term_id", "course_id", "section", name="uq_offering_section"),)


class ClassSession(Base):
    __tablename__ = "class_sessions"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    offering_id: Mapped[UUID] = mapped_column(ForeignKey("course_offerings.id"), index=True)
    weekday: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    room: Mapped[str | None] = mapped_column(String(100))
    offering: Mapped[CourseOffering] = relationship(back_populates="sessions")
