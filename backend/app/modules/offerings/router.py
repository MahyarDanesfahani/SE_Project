from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models import ClassSession, Course, CourseOffering, CoursePrerequisite, ScheduleScenario, ScheduleScenarioItem, StudentCourseRecord, Term, User
from app.modules.identity.dependencies import get_current_user
from app.modules.offerings.schemas import OfferingCreate, OfferingResponse, SessionCreate, SessionResponse, TermCreate, TermResponse
from app.modules.offerings.optimizer import generate_valid_scenarios
from app.modules.offerings.optimizer_schemas import GenerateScheduleRequest, GenerateScheduleResponse, GeneratedScenario

router = APIRouter(prefix="/offerings", tags=["course-offerings"])


def _offering_response(offering: CourseOffering) -> OfferingResponse:
    return OfferingResponse(id=offering.id, term_id=offering.term_id, course_id=offering.course_id, course_code=offering.course.code, course_title=offering.course.title, section=offering.section, instructor=offering.instructor, capacity=offering.capacity, credits=offering.credits, sessions=[SessionResponse(id=s.id, weekday=s.weekday, start_time=s.start_time, end_time=s.end_time, room=s.room) for s in offering.sessions])


@router.post("/terms", response_model=TermResponse, status_code=status.HTTP_201_CREATED)
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


@router.post("/schedule/generate", response_model=GenerateScheduleResponse)
def generate_schedule(payload: GenerateScheduleRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> GenerateScheduleResponse:
    offerings = list(db.scalars(select(CourseOffering).options(joinedload(CourseOffering.sessions)).where(CourseOffering.id.in_(payload.offering_ids), CourseOffering.owner_user_id == user.id, CourseOffering.term_id == payload.term_id)).unique().all())
    if len(offerings) != len(set(payload.offering_ids)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="یک یا چند گروه درسی پیدا نشد")
    course_ids = {offering.course_id for offering in offerings}
    prerequisites = list(db.scalars(select(CoursePrerequisite).where(CoursePrerequisite.course_id.in_(course_ids), CoursePrerequisite.relation_type == "prerequisite")).all())
    passed_course_ids = set(db.scalars(select(StudentCourseRecord.course_id).where(StudentCourseRecord.user_id == user.id, StudentCourseRecord.status == "passed")).all())
    blocked_courses = {item.course_id for item in prerequisites if item.prerequisite_course_id not in passed_course_ids}
    offerings = [offering for offering in offerings if offering.course_id not in blocked_courses]
    if not offerings:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="پیش‌نیاز درس‌های انتخاب‌شده گذرانده نشده است")
    groups: dict[UUID, list[CourseOffering]] = {}
    for offering in offerings:
        groups.setdefault(offering.course_id, []).append(offering)
    scenarios = generate_valid_scenarios(list(groups.values()), payload.max_scenarios)
    if not scenarios:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="هیچ برنامه‌ای بدون تداخل زمانی پیدا نشد")
    result: list[GeneratedScenario] = []
    for index, selected in enumerate(scenarios, start=1):
        scenario = ScheduleScenario(owner_user_id=user.id, term_id=payload.term_id, name=f"سناریو {index}", score=sum(item.credits for item in selected))
        db.add(scenario)
        db.flush()
        for offering in selected:
            db.add(ScheduleScenarioItem(scenario_id=scenario.id, offering_id=offering.id))
        result.append(GeneratedScenario(id=scenario.id, name=scenario.name, score=scenario.score, offering_ids=[item.id for item in selected]))
    db.commit()
    return GenerateScheduleResponse(scenarios=result)
