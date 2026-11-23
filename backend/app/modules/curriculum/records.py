from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course, StudentCourseRecord, User
from app.modules.identity.dependencies import get_current_user

router = APIRouter(prefix="/academic-records", tags=["academic-records"])


class RecordCreate(BaseModel):
    course_id: UUID
    term_title: str | None = Field(default=None, max_length=100)
    status: str = Field(default="passed", pattern="^(passed|failed|in_progress|dropped)$")
    grade: int | None = Field(default=None, ge=0, le=20)


class RecordResponse(RecordCreate):
    id: UUID


@router.post("", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(payload: RecordCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudentCourseRecord:
    if db.get(Course, payload.course_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="درس پیدا نشد")
    record = StudentCourseRecord(user_id=user.id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[RecordResponse])
def list_records(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[StudentCourseRecord]:
    return list(db.scalars(select(StudentCourseRecord).where(StudentCourseRecord.user_id == user.id)).all())
