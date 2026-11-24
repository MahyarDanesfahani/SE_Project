from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TeacherSurvey(Base):
    __tablename__ = "teacher_surveys"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    teacher_name: Mapped[str] = mapped_column(String(150))
    course_id: Mapped[UUID | None] = mapped_column(ForeignKey("courses.id"), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    minimum_responses: Mapped[int] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    questions: Mapped[list["SurveyQuestion"]] = relationship(cascade="all, delete-orphan")


class SurveyQuestion(Base):
    __tablename__ = "survey_questions"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    survey_id: Mapped[UUID] = mapped_column(ForeignKey("teacher_surveys.id"), index=True)
    text: Mapped[str] = mapped_column(String(300))
    order_number: Mapped[int] = mapped_column(Integer)


class SurveyResponse(Base):
    __tablename__ = "survey_responses"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    survey_id: Mapped[UUID] = mapped_column(ForeignKey("teacher_surveys.id"), index=True)
    respondent_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    answers: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint("survey_id", "respondent_user_id", name="uq_survey_response_once"),)
