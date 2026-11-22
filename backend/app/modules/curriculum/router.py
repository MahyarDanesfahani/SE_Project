from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models import Course, CourseStatus, Curriculum, CurriculumCourse, User
from app.modules.identity.dependencies import get_current_user
from app.core.config import get_settings
from app.modules.curriculum.importer import parse_course_file
from app.modules.curriculum.schemas import CourseCreate, CourseImportConfirm, CourseImportPreview, CourseImportRow, CourseResponse, CurriculumCreate, CurriculumResponse

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


@router.post("/{curriculum_id}/import/preview", response_model=CourseImportPreview)
async def preview_course_import(curriculum_id: UUID, file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CourseImportPreview:
    _get_owned(curriculum_id, user, db)
    content = await file.read(get_settings().max_upload_size_bytes + 1)
    if len(content) > get_settings().max_upload_size_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="حجم فایل بیش از حد مجاز است")
    try:
        rows = parse_course_file(file.filename or "", content)
    except (UnicodeDecodeError, ValueError, KeyError, OSError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    preview_rows = [CourseImportRow(row_number=row.row_number, code=row.code, title=row.title, credits=row.credits, semester_number=row.semester_number, status=row.status, errors=row.errors) for row in rows]
    invalid = sum(bool(row.errors) for row in rows)
    return CourseImportPreview(filename=file.filename or "unknown", total_rows=len(rows), valid_rows=len(rows) - invalid, invalid_rows=invalid, rows=preview_rows)


@router.post("/{curriculum_id}/import/confirm", response_model=CurriculumResponse)
def confirm_course_import(curriculum_id: UUID, payload: CourseImportConfirm, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CurriculumResponse:
    curriculum = _get_owned(curriculum_id, user, db)
    invalid_rows = [row.row_number for row in payload.rows if row.errors or row.credits is None]
    if invalid_rows:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"ردیف‌های نامعتبر: {invalid_rows}")
    codes = [row.code.strip().lower() for row in payload.rows]
    if len(codes) != len(set(codes)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="کد درس تکراری در Preview وجود دارد")
    existing_course_ids = {item.course_id for item in curriculum.courses}
    existing_codes = {item.course.code for item in curriculum.courses}
    if existing_codes.intersection(codes):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="یکی از درس‌ها قبلاً در این چارت ثبت شده است")
    try:
        for row in payload.rows:
            code = row.code.strip().lower()
            course = db.scalar(select(Course).where(Course.code == code))
            if course is None:
                course = Course(code=code, title=row.title.strip(), credits=row.credits, course_type="core")
                db.add(course)
                db.flush()
            elif course.title != row.title.strip() or course.credits != row.credits:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"اطلاعات کد درس {code} متفاوت است")
            if course.id in existing_course_ids:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"درس {code} تکراری است")
            db.add(CurriculumCourse(curriculum_id=curriculum.id, course_id=course.id, semester_number=row.semester_number, status=CourseStatus(row.status)))
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="وضعیت یکی از درس‌ها معتبر نیست") from exc
    return _to_response(_get_owned(curriculum_id, user, db))
