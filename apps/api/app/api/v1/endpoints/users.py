"""
User management endpoints
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_async_db, get_current_user, get_superuser
from app.models.user import User, Role
from app.schemas.user import UserResponse, UserUpdate, RoleResponse, RoleCreate
from app.schemas.base import PaginatedResponse
from app.services.user_service import UserService, RoleService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_superuser),
):
    """
    List all users (superuser only)
    """
    user_service = UserService(db)
    
    # In production, implement search filter
    users, total = await user_service.repository.paginate(page, per_page)
    
    return PaginatedResponse.create(users, total, page, per_page)


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user profile
    """
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get user by ID
    """
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update user profile
    """
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Users can only update themselves (unless superuser)
    if str(user.id) != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )
    
    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    user = await user_service.update(user)
    logger.info(f"User updated: {user.id}")
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_superuser),
):
    """
    Delete user (superuser only, soft delete)
    """
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    await user_service.delete(user)
    logger.info(f"User deleted: {user.id}")
    
    return None


# ============ Role Endpoints ============

roles_router = APIRouter()


@roles_router.get("/", response_model=PaginatedResponse[RoleResponse])
async def list_roles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_superuser),
):
    """
    List all roles (superuser only)
    """
    role_service = RoleService(db)
    roles, total = await role_service.repository.paginate(page, per_page)
    
    return PaginatedResponse.create(roles, total, page, per_page)


@roles_router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_superuser),
):
    """
    Create new role (superuser only)
    """
    role_service = RoleService(db)
    
    # Check if role exists
    existing = await role_service.repository.get_by_name(role_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already exists",
        )
    
    role = Role(name=role_data.name, description=role_data.description)
    role = await role_service.create(role)
    
    logger.info(f"Role created: {role.name}")
    return role


@roles_router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get role by ID
    """
    role_service = RoleService(db)
    role = await role_service.get_by_id(role_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    
    return role


@roles_router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_superuser),
):
    """
    Delete role (superuser only)
    """
    role_service = RoleService(db)
    role = await role_service.get_by_id(role_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    
    await role_service.delete(role)
    logger.info(f"Role deleted: {role.id}")
    
    return None