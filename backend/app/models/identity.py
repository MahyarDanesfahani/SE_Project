from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class University(Base):
    __tablename__ = "universities"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(150))
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    users: Mapped[list["User"]] = relationship(back_populates="university")


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String(30), default="student", server_default="student", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    university_id: Mapped[UUID | None] = mapped_column(ForeignKey("universities.id"), index=True)
    university: Mapped[University | None] = relationship(back_populates="users")
    profile: Mapped["StudentProfile | None"] = relationship(back_populates="user", uselist=False)


class StudentProfile(Base):
    __tablename__ = "student_profiles"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(150))
    student_number: Mapped[str | None] = mapped_column(String(50), index=True)
    field_of_study: Mapped[str | None] = mapped_column(String(150))
    degree_level: Mapped[str | None] = mapped_column(String(50))
    faculty: Mapped[str | None] = mapped_column(String(150))
    admission_year: Mapped[int | None]
    user: Mapped[User] = relationship(back_populates="profile")
