from app.models import CourseStatus


def test_course_status_values_match_domain_contract() -> None:
    assert CourseStatus.REQUIRED.value == "required"
    assert CourseStatus.PASSED.value == "passed"
    assert CourseStatus.IN_PROGRESS.value == "in_progress"
