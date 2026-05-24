"""
FastAPI application entry point
43V3R CORE - Cognitive Operating System
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.router import api_router
from app.api.v1.websocket_cognitive import router as cognitive_ws_router

# Configure logging
_JSON_LOG_FORMAT = '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
_TEXT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=_JSON_LOG_FORMAT if settings.log_format == "json" else _TEXT_LOG_FORMAT,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.app_env}")

    # Import and register all domain model base classes
    # to ensure they are connected to the metadata
    _register_domains()

    yield

    logger.info(f"Shutting down {settings.app_name}")


def _register_domains():
    """Import all domain modules to register SQLAlchemy models."""
    try:
        from app.domains import (
            cognitive,
            semantic,
            agent,
            learning,
            knowledge_graph,
            forecasting,
            creative,
            governance,
            feedback,
        )
        logger.info("All cognitive domain modules registered")
    except Exception as e:
        logger.warning(f"Some domain modules not registered: {e}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="43V3R CORE - Autonomous Media Operating System with Cognitive Intelligence",
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url="/redoc" if settings.app_env == "development" else None,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
        }
    )


# Include API router
app.include_router(api_router)

# Include cognitive WebSocket router
app.include_router(cognitive_ws_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "cognitive_core": "active",
    }