from app.models import CourseStatus


def test_confirmed_status_is_supported() -> None:
    assert CourseStatus("required") is CourseStatus.REQUIRED
