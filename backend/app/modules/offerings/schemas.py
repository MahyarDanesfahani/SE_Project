from datetime import date, time
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class TermCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    academic_year: str = Field(min_length=4, max_length=20)
    semester_number: int = Field(ge=1, le=3)
    starts_on: date | None = None
    ends_on: date | None = None


class TermResponse(TermCreate):
    id: UUID
    university_id: UUID | None


class OfferingCreate(BaseModel):
    term_id: UUID
    course_id: UUID
    section: str = Field(min_length=1, max_length=30)
    instructor: str | None = Field(default=None, max_length=150)
    capacity: int | None = Field(default=None, ge=0)
    credits: int = Field(ge=1, le=10)


class SessionCreate(BaseModel):
    weekday: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    room: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.start_time >= self.end_time:
            raise ValueError("زمان پایان باید بعد از زمان شروع باشد")
        return self


class SessionResponse(SessionCreate):
    id: UUID


class OfferingResponse(BaseModel):
    id: UUID
    term_id: UUID
    course_id: UUID
    course_code: str
    course_title: str
    section: str
    instructor: str | None
    capacity: int | None
    credits: int
    sessions: list[SessionResponse]
