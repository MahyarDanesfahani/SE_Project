from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models import SurveyQuestion, SurveyResponse, TeacherSurvey, User
from app.modules.identity.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/surveys", tags=["teacher-feedback"])


class SurveyCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    teacher_name: str = Field(min_length=1, max_length=150)
    course_id: UUID | None = None
    minimum_responses: int = Field(default=5, ge=3, le=100)
    questions: list[str] = Field(min_length=1, max_length=20)


class SurveyResponseCreate(BaseModel):
    answers: dict[UUID, int]


class SurveySummary(BaseModel):
    id: UUID
    title: str
    teacher_name: str
    question_count: int
    response_count: int


class SurveyResult(BaseModel):
    survey_id: UUID
    response_count: int
    minimum_responses: int
    averages: dict[str, float]


@router.post("", response_model=SurveySummary, status_code=status.HTTP_201_CREATED)
def create_survey(payload: SurveyCreate, user: User = Depends(require_admin), db: Session = Depends(get_db)) -> SurveySummary:
    survey = TeacherSurvey(owner_user_id=user.id, title=payload.title, teacher_name=payload.teacher_name, course_id=payload.course_id, minimum_responses=payload.minimum_responses)
    survey.questions = [SurveyQuestion(text=text, order_number=index) for index, text in enumerate(payload.questions, start=1)]
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return SurveySummary(id=survey.id, title=survey.title, teacher_name=survey.teacher_name, question_count=len(survey.questions), response_count=0)


@router.get("", response_model=list[SurveySummary])
def list_surveys(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[SurveySummary]:
    surveys = list(db.scalars(select(TeacherSurvey).options(joinedload(TeacherSurvey.questions)).where(TeacherSurvey.is_active.is_(True), TeacherSurvey.owner_user_id == user.id)).unique().all())
    return [SurveySummary(id=s.id, title=s.title, teacher_name=s.teacher_name, question_count=len(s.questions), response_count=db.scalar(select(func.count()).where(SurveyResponse.survey_id == s.id)) or 0) for s in surveys]


@router.post("/{survey_id}/responses", status_code=status.HTTP_201_CREATED)
def submit_response(survey_id: UUID, payload: SurveyResponseCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, str]:
    survey = db.get(TeacherSurvey, survey_id)
    if survey is None or not survey.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="نظرسنجی پیدا نشد")
    question_ids = {question.id for question in db.scalars(select(SurveyQuestion).where(SurveyQuestion.survey_id == survey_id)).all()}
    if set(payload.answers) != question_ids or any(score < 1 or score > 5 for score in payload.answers.values()):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="پاسخ‌ها باید برای همه پرسش‌ها و بین ۱ تا ۵ باشند")
    if db.scalar(select(SurveyResponse).where(SurveyResponse.survey_id == survey_id, SurveyResponse.respondent_user_id == user.id)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="قبلاً در این نظرسنجی پاسخ داده‌اید")
    db.add(SurveyResponse(survey_id=survey_id, respondent_user_id=user.id, answers={str(k): v for k, v in payload.answers.items()}))
    db.commit()
    return {"status": "submitted"}


@router.get("/{survey_id}/results", response_model=SurveyResult)
def survey_results(survey_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> SurveyResult:
    survey = db.get(TeacherSurvey, survey_id)
    if survey is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="نظرسنجی پیدا نشد")
    responses = list(db.scalars(select(SurveyResponse).where(SurveyResponse.survey_id == survey_id)).all())
    if len(responses) < survey.minimum_responses:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="نتیجه تا رسیدن به حداقل پاسخ‌ها قابل نمایش نیست")
    averages = {str(question.id): round(sum(response.answers.get(str(question.id), 0) for response in responses) / len(responses), 2) for question in survey.questions}
    return SurveyResult(survey_id=survey_id, response_count=len(responses), minimum_responses=survey.minimum_responses, averages=averages)
