from uuid import uuid4

from app.core.security import create_access_token, hash_password, verify_password


def test_password_hash_round_trip() -> None:
    password = "correct horse battery staple"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong password", hashed)


def test_access_token_contains_user_subject() -> None:
    import jwt

    from app.core.config import get_settings

    user_id = uuid4()
    token = create_access_token(user_id)
    payload = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
    assert payload["sub"] == str(user_id)
