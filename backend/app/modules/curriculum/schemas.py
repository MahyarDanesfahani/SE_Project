from uuid import UUID

from pydantic import BaseModel, Field

from app.models import CourseStatus


class CurriculumCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    major: str | None = Field(default=None, max_length=150)
    admission_year: int | None = Field(default=None, ge=1300, le=1600)
    version: str = Field(default="1.0", max_length=50)
    source_name: str | None = Field(default=None, max_length=255)


class CourseCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=200)
    credits: int = Field(ge=1, le=10)
    course_type: str = Field(default="core", max_length=50)
    semester_number: int | None = Field(default=None, ge=1, le=20)
    status: CourseStatus = CourseStatus.REQUIRED


class CourseResponse(BaseModel):
    id: UUID
    code: str
    title: str
    credits: int
    course_type: str
    semester_number: int | None
    status: CourseStatus


class CurriculumResponse(BaseModel):
    id: UUID
    title: str
    major: str | None
    admission_year: int | None
    version: str
    source_name: str | None
    courses: list[CourseResponse] = Field(default_factory=list)


class CourseImportRow(BaseModel):
    row_number: int
    code: str
    title: str
    credits: int | None
    semester_number: int | None
    status: str
    errors: list[str]


class CourseImportPreview(BaseModel):
    filename: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    rows: list[CourseImportRow]


class CourseImportConfirm(BaseModel):
    rows: list[CourseImportRow] = Field(min_length=1, max_length=500)
