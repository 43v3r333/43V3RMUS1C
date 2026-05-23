"""
Health check endpoints
"""
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Basic health check
    """
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.app_env,
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness check with database connection status
    """
    from app.core.database import check_db_connection
    
    db_connected = await check_db_connection()
    
    return {
        "status": "ready" if db_connected else "degraded",
        "database": "connected" if db_connected else "disconnected",
        "version": settings.app_version,
        "environment": settings.app_env,
    }


@router.get("/live")
async def liveness_check():
    """
    Liveness check
    """
    return {"status": "alive"}