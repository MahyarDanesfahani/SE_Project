from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    university_id: UUID | None = None


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    is_active: bool
    university_id: UUID | None
