from uuid import UUID

from sqlalchemy.orm import Session

from app.models import AuditLog


def record_audit(db: Session, actor_user_id: UUID | None, action: str, resource_type: str, resource_id: str | None = None, result: str = "success", metadata: dict | None = None) -> None:
    db.add(AuditLog(actor_user_id=actor_user_id, action=action, resource_type=resource_type, resource_id=resource_id, result=result, metadata_json=metadata))
