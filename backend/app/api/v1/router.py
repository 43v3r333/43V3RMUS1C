"""
API v1 router - aggregates all endpoint routers
"""
from fastapi import APIRouter

from .endpoints.auth import router as auth_router
from .endpoints.users import router as users_router, roles_router
from .endpoints.media import router as media_router
from .endpoints.assets import router as assets_router
from .endpoints.workflows import router as workflows_router, prompts_router
from .endpoints.health import router as health_router
from .endpoints.cognitive import router as cognitive_router
from .coherence import router as coherence_router
from .execution_fabric import router as execution_fabric_router

api_router = APIRouter(prefix="/api/v1")

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(roles_router)
api_router.include_router(media_router)
api_router.include_router(assets_router)
api_router.include_router(workflows_router)
api_router.include_router(prompts_router)
api_router.include_router(health_router)
api_router.include_router(cognitive_router)
api_router.include_router(coherence_router)
api_router.include_router(execution_fabric_router)