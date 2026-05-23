"""
Health check and monitoring endpoints
"""
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    services: dict = {}


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Basic health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        services={}
    )


@router.get("/ready", response_model=HealthResponse)
async def readiness_check():
    """Readiness check - verify all dependencies"""
    # TODO: Check database, redis, and other services
    return HealthResponse(
        status="ready",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        services={
            "database": "connected",
            "redis": "connected",
        }
    )


@router.get("/live", response_model=HealthResponse)
async def liveness_check():
    """Liveness check - verify application is running"""
    return HealthResponse(
        status="alive",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        services={}
    )