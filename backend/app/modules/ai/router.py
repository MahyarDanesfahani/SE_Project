from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import AIConversation, AIMessage, User
from app.modules.ai.provider import NotConfiguredProvider
from app.modules.identity.dependencies import get_current_user

router = APIRouter(prefix="/ai", tags=["ai-assistant"])

class ChatRequest(BaseModel):
    conversation_id: UUID | None = None
    message: str = Field(min_length=1, max_length=4000)

class ChatResponse(BaseModel):
    conversation_id: UUID
    provider: str
    configured: bool
    reply: str

@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ChatResponse:
    conversation = db.get(AIConversation, payload.conversation_id) if payload.conversation_id else None
    if conversation is not None and conversation.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="گفتگو پیدا نشد")
    if conversation is None:
        conversation = AIConversation(user_id=user.id)
        db.add(conversation)
        db.flush()
    db.add(AIMessage(conversation_id=conversation.id, role="user", content=payload.message, provider="local"))
    reply = NotConfiguredProvider().reply(payload.message)
    db.add(AIMessage(conversation_id=conversation.id, role="assistant", content=reply.content, provider=reply.provider))
    db.commit()
    return ChatResponse(conversation_id=conversation.id, provider=reply.provider, configured=reply.configured, reply=reply.content)
