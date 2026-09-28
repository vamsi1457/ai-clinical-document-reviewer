from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.analysis import router as analysis_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="", tags=["Health"])
api_router.include_router(analysis_router, prefix="", tags=["Clinical Analysis"])

__all__ = ["api_router"]
