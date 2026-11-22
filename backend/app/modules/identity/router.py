from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import User
from app.modules.identity.dependencies import get_current_user
from app.modules.identity.schemas import LoginRequest, ProfileResponse, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["identity"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    email = payload.email.strip().lower()
    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="این ایمیل قبلاً ثبت شده است")
    user = User(email=email, password_hash=hash_password(payload.password), university_id=payload.university_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    email = payload.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="ایمیل یا رمز عبور نادرست است")
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=ProfileResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
