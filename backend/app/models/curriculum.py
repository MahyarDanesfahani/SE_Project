from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class CourseStatus(StrEnum):
    REQUIRED = "required"
    ELECTIVE = "elective"
    PASSED = "passed"
    IN_PROGRESS = "in_progress"
    REMAINING = "remaining"


class Curriculum(Base):
    __tablename__ = "curricula"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    university_id: Mapped[UUID | None] = mapped_column(ForeignKey("universities.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    major: Mapped[str | None] = mapped_column(String(150))
    admission_year: Mapped[int | None]
    version: Mapped[str] = mapped_column(String(50), default="1.0")
    source_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    courses: Mapped[list["CurriculumCourse"]] = relationship(back_populates="curriculum", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(50), index=True)
    title: Mapped[str] = mapped_column(String(200))
    credits: Mapped[int] = mapped_column(Integer)
    course_type: Mapped[str] = mapped_column(String(50), default="core")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint("code", name="uq_courses_code"),)


class CurriculumCourse(Base):
    __tablename__ = "curriculum_courses"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    curriculum_id: Mapped[UUID] = mapped_column(ForeignKey("curricula.id"), index=True)
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id"), index=True)
    semester_number: Mapped[int | None]
    status: Mapped[CourseStatus] = mapped_column(Enum(CourseStatus), default=CourseStatus.REQUIRED)
    curriculum: Mapped[Curriculum] = relationship(back_populates="courses")
    course: Mapped[Course] = relationship()
    __table_args__ = (UniqueConstraint("curriculum_id", "course_id", name="uq_curriculum_course"),)


class CoursePrerequisite(Base):
    __tablename__ = "course_prerequisites"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id"), index=True)
    prerequisite_course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id"), index=True)
    relation_type: Mapped[str] = mapped_column(String(20), default="prerequisite")
    __table_args__ = (UniqueConstraint("course_id", "prerequisite_course_id", name="uq_course_prerequisite"),)
