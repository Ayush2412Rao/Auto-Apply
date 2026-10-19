from fastapi import APIRouter
from backend.app.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "env": settings.APP_ENV,
        "gemini_model": settings.GEMINI_MODEL,
        "timezone": settings.TIMEZONE
    }
