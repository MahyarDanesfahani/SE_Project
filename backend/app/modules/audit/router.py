from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AuditLog, User
from app.modules.identity.dependencies import get_current_user

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditResponse(BaseModel):
    id: UUID
    action: str
    resource_type: str
    resource_id: str | None
    result: str
    created_at: datetime


@router.get("/me", response_model=list[AuditResponse])
def list_my_audit(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[AuditLog]:
    return list(db.scalars(select(AuditLog).where(AuditLog.actor_user_id == user.id).order_by(AuditLog.created_at.desc()).limit(100)).all())
