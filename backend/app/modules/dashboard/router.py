from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Announcement, Course, Exam, GradeRecord, ScheduleScenario, Task, User
from app.modules.identity.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardMetric(BaseModel):
    value: str
    label: str


class DashboardEvent(BaseModel):
    id: UUID
    type: str
    title: str
    starts_at: datetime | None
    status: str | None


class DashboardAnnouncement(BaseModel):
    id: UUID
    title: str
    category: str
    source_name: str
    published_at: datetime | None


class DashboardResponse(BaseModel):
    greeting: str
    metrics: list[DashboardMetric]
    upcoming: list[DashboardEvent]
    announcements: list[DashboardAnnouncement]


@router.get("", response_model=DashboardResponse)
def get_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DashboardResponse:
    grades = list(db.scalars(select(GradeRecord).where(GradeRecord.user_id == user.id, GradeRecord.is_verified.is_(True), GradeRecord.grade.is_not(None))).all())
    courses = {course.id: course for course in db.scalars(select(Course).where(Course.id.in_([g.course_id for g in grades]))).all()} if grades else {}
    credits = sum(courses[g.course_id].credits for g in grades if g.course_id in courses)
    weighted = sum(Decimal(str(g.grade)) * courses[g.course_id].credits for g in grades if g.course_id in courses)
    gpa = str((weighted / credits).quantize(Decimal("0.01"))) if credits else "—"
    now = datetime.now(timezone.utc)
    exams = list(db.scalars(select(Exam).where(Exam.owner_user_id == user.id, Exam.starts_at >= now).order_by(Exam.starts_at).limit(5)).all())
    tasks = list(db.scalars(select(Task).where(Task.owner_user_id == user.id, Task.status.in_(["todo", "in_progress"]), Task.due_at.is_not(None)).order_by(Task.due_at).limit(5)).all())
    upcoming = [DashboardEvent(id=e.id, type="exam", title=f"امتحان {e.term_title}", starts_at=e.starts_at, status="scheduled") for e in exams]
    upcoming.extend(DashboardEvent(id=t.id, type="task", title=t.title, starts_at=t.due_at, status=t.status) for t in tasks)
    announcements = list(db.scalars(select(Announcement).where(Announcement.university_id == user.university_id, Announcement.is_valid.is_(True)).order_by(Announcement.received_at.desc()).limit(5)).all())
    scenario_count = db.scalar(select(func.count()).select_from(ScheduleScenario).where(ScheduleScenario.owner_user_id == user.id)) or 0
    return DashboardResponse(greeting=f"سلام، {user.email}", metrics=[DashboardMetric(value=gpa, label="معدل تأییدشده"), DashboardMetric(value=str(len(grades)), label="نمره‌های ثبت‌شده"), DashboardMetric(value=str(len(tasks)), label="وظایف باز"), DashboardMetric(value=str(scenario_count), label="سناریوهای انتخاب واحد")], upcoming=sorted(upcoming, key=lambda item: item.starts_at or datetime.max)[:5], announcements=[DashboardAnnouncement(id=a.id, title=a.title, category=a.category, source_name=a.source_name, published_at=a.published_at) for a in announcements])
