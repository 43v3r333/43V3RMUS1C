"""
FastAPI Dependency Injection
"""
import logging
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import verify_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

# HTTP Bearer scheme
security = HTTPBearer(auto_error=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    async for session in get_async_db():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
    
    Returns:
        Current authenticated user
    
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = verify_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_session),
) -> User | None:
    """
    Get current user if authenticated, None otherwise
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
    
    Returns:
        Current user or None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


async def get_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user and verify superuser status
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Superuser
    
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required",
        )
    
    return current_user


def require_role(role_names: list[str]):
    """
    Dependency factory for role-based access control
    
    Args:
        role_names: List of allowed role names
    
    Returns:
        Dependency function
    """
    async def check_role(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role and current_user.role.name not in role_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    
    return check_role