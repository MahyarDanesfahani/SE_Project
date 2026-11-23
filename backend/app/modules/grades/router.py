from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course, GradeRecord, User
from app.modules.identity.dependencies import get_current_user

router = APIRouter(prefix="/grades", tags=["grades"])


class GradeCreate(BaseModel):
    course_id: UUID
    term_title: str = Field(min_length=1, max_length=100)
    grade: Decimal | None = Field(default=None, ge=0, le=20)
    source: str = Field(default="manual", pattern="^(manual|official|imported)$")
    is_verified: bool = False


class GradeResponse(GradeCreate):
    id: UUID


class GpaResponse(BaseModel):
    gpa: Decimal | None
    total_credits: int
    graded_courses: int
    incomplete_courses: int
    is_complete: bool


@router.post("", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
def create_grade(payload: GradeCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> GradeRecord:
    if db.get(Course, payload.course_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="درس پیدا نشد")
    record = GradeRecord(user_id=user.id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[GradeResponse])
def list_grades(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[GradeRecord]:
    return list(db.scalars(select(GradeRecord).where(GradeRecord.user_id == user.id)).all())


@router.get("/gpa", response_model=GpaResponse)
def calculate_gpa(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> GpaResponse:
    records = list(db.scalars(select(GradeRecord).where(GradeRecord.user_id == user.id)).all())
    course_ids = [record.course_id for record in records]
    courses = {course.id: course for course in db.scalars(select(Course).where(Course.id.in_(course_ids))).all()} if course_ids else {}
    graded = [(record, courses.get(record.course_id)) for record in records if record.grade is not None and record.is_verified]
    incomplete = len(records) - len(graded)
    credits = sum(course.credits for _, course in graded if course is not None)
    weighted = sum(Decimal(str(record.grade)) * course.credits for record, course in graded if course is not None)
    return GpaResponse(gpa=(weighted / credits).quantize(Decimal("0.01")) if credits else None, total_credits=credits, graded_courses=len(graded), incomplete_courses=incomplete, is_complete=incomplete == 0)
