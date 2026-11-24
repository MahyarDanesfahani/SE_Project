from fastapi import APIRouter

from app.api.health import router as health_router
from app.modules.identity.router import router as identity_router
from app.modules.curriculum.router import router as curriculum_router
from app.modules.offerings.router import router as offerings_router
from app.modules.curriculum.records import router as records_router
from app.modules.grades.router import router as grades_router
from app.modules.planning.router import router as planning_router
from app.modules.announcements.router import router as announcements_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.feedback.router import router as feedback_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(identity_router)
api_router.include_router(curriculum_router)
api_router.include_router(offerings_router)
api_router.include_router(records_router)
api_router.include_router(grades_router)
api_router.include_router(planning_router)
api_router.include_router(announcements_router)
api_router.include_router(dashboard_router)
api_router.include_router(feedback_router)
