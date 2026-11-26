from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.modules.identity.dependencies import require_admin


def test_student_cannot_use_admin_dependency() -> None:
    with pytest.raises(HTTPException) as error:
        require_admin(SimpleNamespace(role="student"))
    assert error.value.status_code == 403


def test_admin_can_use_admin_dependency() -> None:
    user = SimpleNamespace(role="admin")
    assert require_admin(user) is user
