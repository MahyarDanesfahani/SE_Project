from fastapi import APIRouter

from app.api.health import router as health_router
from app.modules.identity.router import router as identity_router
from app.modules.curriculum.router import router as curriculum_router
from app.modules.offerings.router import router as offerings_router
from app.modules.curriculum.records import router as records_router
from app.modules.grades.router import router as grades_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(identity_router)
api_router.include_router(curriculum_router)
api_router.include_router(offerings_router)
api_router.include_router(records_router)
api_router.include_router(grades_router)
