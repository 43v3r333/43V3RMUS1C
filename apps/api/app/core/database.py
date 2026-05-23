"""
Database Configuration and Session Management
"""
import logging
from contextlib import contextmanager
from typing import Generator, AsyncGenerator

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# SQLAlchemy metadata
metadata = MetaData(naming_convention=convention)

# Base class for models
Base = declarative_base(metadata=metadata)

# Sync engine (for migrations and sync operations)
engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    echo=settings.database_echo,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Async engine (for FastAPI async endpoints)
async_engine = create_async_engine(
    settings.database_url_async,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    echo=settings.database_echo,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)


def get_db() -> Generator[Session, None, None]:
    """
    Get database session (sync)
    Usage: Depends on get_db in FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session (async)
    Usage: Depends on get_async_db in FastAPI
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions
    Usage: For background tasks and workers
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db() -> None:
    """Initialize database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections"""
    await async_engine.dispose()


async def check_db_connection() -> bool:
    """Check if database connection is healthy"""
    try:
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False