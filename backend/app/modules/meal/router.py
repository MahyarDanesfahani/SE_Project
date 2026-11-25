from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import MealMenuItem, MealReservation, MealReservationStatus, User
from app.modules.identity.dependencies import get_current_user
from app.modules.meal.adapter import MealConnectionStatus

router = APIRouter(prefix="/meal", tags=["meal"])


class MenuCreate(BaseModel):
    service_date: date
    meal_type: str = Field(min_length=1, max_length=30)
    title: str = Field(min_length=1, max_length=200)
    price: int | None = Field(default=None, ge=0)


class MenuResponse(MenuCreate):
    id: UUID
    source_name: str
    source_url: str


class ReservationResponse(BaseModel):
    id: UUID
    menu_item_id: UUID
    status: MealReservationStatus


class ConnectionResponse(BaseModel):
    provider: str
    configured: bool
    status: str
    message: str


@router.get("/connection", response_model=ConnectionResponse)
def connection_status(user: User = Depends(get_current_user)) -> ConnectionResponse:
    return ConnectionResponse(**MealConnectionStatus().__dict__)


@router.post("/menu", response_model=MenuResponse, status_code=status.HTTP_201_CREATED)
def create_demo_menu(payload: MenuCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MealMenuItem:
    item = MealMenuItem(university_id=user.university_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/menu", response_model=list[MenuResponse])
def list_menu(service_date: date | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[MealMenuItem]:
    query = select(MealMenuItem).where(MealMenuItem.university_id == user.university_id)
    if service_date:
        query = query.where(MealMenuItem.service_date == service_date)
    return list(db.scalars(query.order_by(MealMenuItem.service_date, MealMenuItem.meal_type)).all())


@router.post("/reservations/{menu_item_id}", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def request_demo_reservation(menu_item_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MealReservation:
    item = db.scalar(select(MealMenuItem).where(MealMenuItem.id == menu_item_id, MealMenuItem.university_id == user.university_id))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="منوی غذا پیدا نشد")
    reservation = MealReservation(user_id=user.id, menu_item_id=item.id, status=MealReservationStatus.PENDING_INTERNAL)
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation
