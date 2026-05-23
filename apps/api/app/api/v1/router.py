"""
API v1 router - aggregates all endpoint routers
"""
from fastapi import APIRouter

from .endpoints.auth import router as auth_router
from .endpoints.users import router as users_router, roles_router
from .endpoints.media import router as media_router
from .endpoints.assets import router as assets_router
from .endpoints.workflows import router as workflows_router, prompts_router, render_jobs_router
from .endpoints.campaigns import router as campaigns_router, social_accounts_router, social_posts_router
from .endpoints.health import router as health_router

api_router = APIRouter(prefix="/api/v1")

# Include all routers
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(roles_router, prefix="/roles", tags=["Roles"])
api_router.include_router(media_router, prefix="/media", tags=["Media"])
api_router.include_router(assets_router, prefix="/assets", tags=["Assets"])
api_router.include_router(workflows_router, prefix="/workflows", tags=["Workflows"])
api_router.include_router(render_jobs_router, prefix="/render-jobs", tags=["Render Jobs"])
api_router.include_router(prompts_router, prefix="/prompts", tags=["AI Prompts"])
api_router.include_router(campaigns_router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(social_accounts_router, prefix="/social-accounts", tags=["Social Accounts"])
api_router.include_router(social_posts_router, prefix="/social-posts", tags=["Social Posts"])