from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models import Course, Curriculum, CurriculumCourse, User
from app.modules.identity.dependencies import get_current_user
from app.modules.curriculum.schemas import CourseCreate, CourseResponse, CurriculumCreate, CurriculumResponse

router = APIRouter(prefix="/curricula", tags=["curriculum"])


def _to_response(curriculum: Curriculum) -> CurriculumResponse:
    return CurriculumResponse(
        id=curriculum.id,
        title=curriculum.title,
        major=curriculum.major,
        admission_year=curriculum.admission_year,
        version=curriculum.version,
        source_name=curriculum.source_name,
        courses=[CourseResponse(id=item.course.id, code=item.course.code, title=item.course.title, credits=item.course.credits, course_type=item.course.course_type, semester_number=item.semester_number, status=item.status) for item in curriculum.courses],
    )


def _get_owned(curriculum_id: UUID, user: User, db: Session) -> Curriculum:
    curriculum = db.scalar(select(Curriculum).options(joinedload(Curriculum.courses).joinedload(CurriculumCourse.course)).where(Curriculum.id == curriculum_id, Curriculum.owner_user_id == user.id))
    if curriculum is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="چارت درسی پیدا نشد")
    return curriculum


@router.post("", response_model=CurriculumResponse, status_code=status.HTTP_201_CREATED)
def create_curriculum(payload: CurriculumCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CurriculumResponse:
    curriculum = Curriculum(owner_user_id=user.id, university_id=user.university_id, **payload.model_dump())
    db.add(curriculum)
    db.commit()
    db.refresh(curriculum)
    return _to_response(curriculum)


@router.get("/{curriculum_id}", response_model=CurriculumResponse)
def get_curriculum(curriculum_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CurriculumResponse:
    return _to_response(_get_owned(curriculum_id, user, db))


@router.post("/{curriculum_id}/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def add_course(curriculum_id: UUID, payload: CourseCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CourseResponse:
    curriculum = _get_owned(curriculum_id, user, db)
    course = db.scalar(select(Course).where(Course.code == payload.code.strip()))
    if course is None:
        course = Course(code=payload.code.strip(), title=payload.title.strip(), credits=payload.credits, course_type=payload.course_type)
        db.add(course)
        db.flush()
    elif course.title != payload.title.strip() or course.credits != payload.credits:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="کد درس با اطلاعات متفاوت وجود دارد")
    if any(item.course_id == course.id for item in curriculum.courses):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="این درس قبلاً در چارت ثبت شده است")
    link = CurriculumCourse(curriculum_id=curriculum.id, course_id=course.id, semester_number=payload.semester_number, status=payload.status)
    db.add(link)
    db.commit()
    return CourseResponse(id=course.id, code=course.code, title=course.title, credits=course.credits, course_type=course.course_type, semester_number=link.semester_number, status=link.status)
