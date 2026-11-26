from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import AnyHttpUrl, BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Announcement, User
from app.modules.identity.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/announcements", tags=["announcements"])


class AnnouncementCreate(BaseModel):
    title: str = Field(min_length=1, max_length=250)
    body: str = Field(min_length=1)
    category: str = Field(default="general", max_length=80)
    source_name: str = Field(min_length=1, max_length=150)
    source_url: AnyHttpUrl
    published_at: datetime | None = None


class AnnouncementResponse(AnnouncementCreate):
    id: UUID
    received_at: datetime
    is_valid: bool


@router.post("", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
def create_announcement(payload: AnnouncementCreate, user: User = Depends(require_admin), db: Session = Depends(get_db)) -> Announcement:
    source_url = str(payload.source_url)
    existing = db.scalar(select(Announcement).where(Announcement.university_id == user.university_id, Announcement.source_url == source_url))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="این اطلاعیه قبلاً ثبت شده است")
    announcement = Announcement(university_id=user.university_id, source_url=source_url, **payload.model_dump(exclude={"source_url"}))
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement


@router.get("", response_model=list[AnnouncementResponse])
def list_announcements(search: str | None = Query(default=None, max_length=100), category: str | None = Query(default=None, max_length=80), user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Announcement]:
    query = select(Announcement).where(Announcement.university_id == user.university_id, Announcement.is_valid.is_(True)).order_by(Announcement.published_at.desc().nullslast(), Announcement.received_at.desc())
    if search:
        query = query.where(Announcement.title.ilike(f"%{search}%"))
    if category:
        query = query.where(Announcement.category == category)
    return list(db.scalars(query).all())
