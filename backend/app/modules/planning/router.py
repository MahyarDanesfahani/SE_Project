from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Course, Exam, Task, User
from app.modules.identity.dependencies import get_current_user

router = APIRouter(tags=["planning"])


class ExamCreate(BaseModel):
    course_id: UUID
    term_title: str = Field(min_length=1, max_length=100)
    starts_at: datetime
    location: str | None = Field(default=None, max_length=150)
    notes: str | None = None


class ExamResponse(ExamCreate):
    id: UUID
    type: str = "exam"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    course_id: UUID | None = None
    due_at: datetime | None = None
    priority: int = Field(default=2, ge=1, le=3)
    status: str = Field(default="todo", pattern="^(todo|in_progress|done|cancelled)$")


class TaskResponse(TaskCreate):
    id: UUID
    type: str = "task"


class CalendarItem(BaseModel):
    id: UUID
    type: str
    title: str
    starts_at: datetime | None
    location: str | None
    status: str | None


@router.post("/exams", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
def create_exam(payload: ExamCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Exam:
    if db.get(Course, payload.course_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="درس پیدا نشد")
    exam = Exam(owner_user_id=user.id, **payload.model_dump())
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


@router.get("/exams", response_model=list[ExamResponse])
def list_exams(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Exam]:
    return list(db.scalars(select(Exam).where(Exam.owner_user_id == user.id).order_by(Exam.starts_at)).all())


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Task:
    if payload.course_id and db.get(Course, payload.course_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="درس پیدا نشد")
    task = Task(owner_user_id=user.id, **payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks", response_model=list[TaskResponse])
def list_tasks(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Task]:
    return list(db.scalars(select(Task).where(Task.owner_user_id == user.id).order_by(Task.due_at)).all())


@router.get("/calendar", response_model=list[CalendarItem])
def calendar(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[CalendarItem]:
    exams = list(db.scalars(select(Exam).where(Exam.owner_user_id == user.id)).all())
    tasks = list(db.scalars(select(Task).where(Task.owner_user_id == user.id)).all())
    items = [CalendarItem(id=exam.id, type="exam", title=f"امتحان {exam.term_title}", starts_at=exam.starts_at, location=exam.location, status="scheduled") for exam in exams]
    items.extend(CalendarItem(id=task.id, type="task", title=task.title, starts_at=task.due_at, location=None, status=task.status) for task in tasks)
    return sorted(items, key=lambda item: item.starts_at or datetime.max)
