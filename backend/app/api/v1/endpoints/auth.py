"""
Authentication endpoints
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.security import verify_refresh_token, create_access_token, create_refresh_token
from ....schemas.user import TokenResponse, TokenRefreshRequest, LoginRequest
from ....services.user_service import UserService
from ....repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login with email/username and password"""
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    
    user = user_service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = user_service.create_tokens(user)
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        expires_in=1800  # 30 minutes
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    payload = verify_refresh_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    
    user_id = payload.get("sub")
    user = user_service.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    tokens = user_service.create_tokens(user)
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        expires_in=1800
    )


@router.post("/logout")
async def logout():
    """Logout - client should discard tokens"""
    return {"message": "Successfully logged out"}