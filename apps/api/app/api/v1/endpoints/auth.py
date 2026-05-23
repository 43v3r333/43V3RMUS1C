"""
Authentication endpoints
"""
import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_refresh_token
from app.core.deps import get_async_db, get_current_user
from app.schemas.user import (
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    UserCreate,
    PasswordChange,
)
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Register a new user account
    """
    user_service = UserService(db)
    
    # Check if email exists
    if await user_service.email_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if username exists
    if await user_service.username_exists(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create user
    user = await user_service.create_user(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )
    
    logger.info(f"New user registered: {user.email}")
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Authenticate user and return tokens
    """
    user_service = UserService(db)
    
    user = await user_service.authenticate(
        username=credentials.username,
        password=credentials.password,
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    logger.info(f"User logged in: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Refresh access token using refresh token
    """
    payload = verify_refresh_token(request.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user),
):
    """
    Get current authenticated user information
    """
    return current_user


@router.post("/logout")
async def logout(
    current_user = Depends(get_current_user),
):
    """
    Logout current user (client should discard tokens)
    """
    # In a stateless JWT system, logout is handled client-side
    # Token invalidation would require a token blacklist (Redis)
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Logged out successfully"}


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Change current user's password
    """
    user_service = UserService(db)
    
    # Verify current password
    if not await user_service.authenticate(current_user.username, password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    
    # Update password
    await user_service.update_password(current_user, password_data.new_password)
    
    logger.info(f"Password changed for user: {current_user.email}")
    return {"message": "Password changed successfully"}