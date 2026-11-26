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
    role: str


class StudentProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=150)
    student_number: str | None = Field(default=None, max_length=50)
    field_of_study: str | None = Field(default=None, max_length=150)
    degree_level: str | None = Field(default=None, max_length=50)
    faculty: str | None = Field(default=None, max_length=150)
    admission_year: int | None = Field(default=None, ge=1300, le=1600)


class StudentProfileResponse(StudentProfileUpdate):
    id: UUID
    user_id: UUID
