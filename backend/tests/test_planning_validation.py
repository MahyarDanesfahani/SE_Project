import pytest
from pydantic import ValidationError

from app.modules.planning.router import ExamCreate


def test_exam_requires_timezone_agnostic_datetime_shape() -> None:
    with pytest.raises(ValidationError):
        ExamCreate(course_id="not-a-uuid", term_title="1405-1", starts_at="bad")
