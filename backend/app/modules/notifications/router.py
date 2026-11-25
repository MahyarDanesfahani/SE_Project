from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.audit import record_audit
from app.models import Notification, User
from app.modules.identity.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1)
    channel: str = Field(default="in_app", pattern="^in_app$")


class NotificationResponse(NotificationCreate):
    id: UUID
    is_read: bool


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(payload: NotificationCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Notification:
    notification = Notification(user_id=user.id, **payload.model_dump())
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


@router.get("", response_model=list[NotificationResponse])
def list_notifications(unread_only: bool = False, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Notification]:
    query = select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc())
    if unread_only:
        query = query.where(Notification.is_read.is_(False))
    return list(db.scalars(query).all())


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_read(notification_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Notification:
    notification = db.scalar(select(Notification).where(Notification.id == notification_id, Notification.user_id == user.id))
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="اعلان پیدا نشد")
    notification.is_read = True
    record_audit(db, user.id, "notification.read", "notification", str(notification.id))
    db.commit()
    db.refresh(notification)
    return notification
