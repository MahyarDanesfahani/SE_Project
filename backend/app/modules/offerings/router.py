from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models import ClassSession, Course, CourseOffering, Term, User
from app.modules.identity.dependencies import get_current_user
from app.modules.offerings.schemas import OfferingCreate, OfferingResponse, SessionCreate, SessionResponse, TermCreate

router = APIRouter(prefix="/offerings", tags=["course-offerings"])


def _offering_response(offering: CourseOffering) -> OfferingResponse:
    return OfferingResponse(id=offering.id, term_id=offering.term_id, course_id=offering.course_id, course_code=offering.course.code, course_title=offering.course.title, section=offering.section, instructor=offering.instructor, capacity=offering.capacity, credits=offering.credits, sessions=[SessionResponse(id=s.id, weekday=s.weekday, start_time=s.start_time, end_time=s.end_time, room=s.room) for s in offering.sessions])


@router.post("/terms", status_code=status.HTTP_201_CREATED)
def create_term(payload: TermCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Term:
    term = Term(university_id=user.university_id, **payload.model_dump())
    db.add(term)
    db.commit()
    db.refresh(term)
    return term


@router.post("", response_model=OfferingResponse, status_code=status.HTTP_201_CREATED)
def create_offering(payload: OfferingCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> OfferingResponse:
    term = db.scalar(select(Term).where(Term.id == payload.term_id, Term.university_id == user.university_id))
    course = db.get(Course, payload.course_id)
    if term is None or course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="نیمسال یا درس پیدا نشد")
    offering = CourseOffering(owner_user_id=user.id, **payload.model_dump())
    db.add(offering)
    db.commit()
    offering = db.execute(select(CourseOffering).options(joinedload(CourseOffering.course), joinedload(CourseOffering.sessions)).where(CourseOffering.id == offering.id)).unique().scalar_one()
    return _offering_response(offering)


@router.post("/{offering_id}/sessions", response_model=OfferingResponse)
def add_session(offering_id: UUID, payload: SessionCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> OfferingResponse:
    offering = db.execute(select(CourseOffering).options(joinedload(CourseOffering.course), joinedload(CourseOffering.sessions)).where(CourseOffering.id == offering_id, CourseOffering.owner_user_id == user.id)).unique().scalar_one_or_none()
    if offering is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="گروه درسی پیدا نشد")
    offering.sessions.append(ClassSession(**payload.model_dump()))
    db.commit()
    offering = db.execute(select(CourseOffering).options(joinedload(CourseOffering.course), joinedload(CourseOffering.sessions)).where(CourseOffering.id == offering_id)).unique().scalar_one()
    return _offering_response(offering)
