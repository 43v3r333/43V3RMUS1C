"""
User management endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from app.core.deps import get_current_active_user, require_role
from ....schemas.user import (
    UserCreate, UserUpdate, UserResponse,
    RoleCreate, RoleUpdate, RoleResponse,
)
from ....services.user_service import UserService, RoleService
from ....repositories.user_repository import UserRepository, RoleRepository, PermissionRepository

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    
    user = user_service.update(current_user, user_data)
    return user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin", "manager"))
):
    """List all users (admin/manager only)"""
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    
    users = user_service.get_all(skip, limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get user by ID"""
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    
    user = user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Update user (admin only)"""
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    
    user = user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = user_service.update(user, user_data)
    return updated_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Delete user (admin only) - soft delete"""
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    
    user = user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_service.repository.delete(user)
    return {"message": "User deleted successfully"}


# Roles endpoints
roles_router = APIRouter(prefix="/roles", tags=["roles"])


@roles_router.get("/", response_model=List[RoleResponse])
async def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """List all roles (admin only)"""
    role_repo = RoleRepository(db)
    role_service = RoleService(role_repo)
    
    roles = role_service.get_all(skip, limit)
    return roles


@roles_router.post("/", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Create new role (admin only)"""
    role_repo = RoleRepository(db)
    role_service = RoleService(role_repo)
    
    existing = role_service.get_by_name(role_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already exists"
        )
    
    # Create role with permissions
    from ....models.user import Role, Permission
    role = Role(name=role_data.name, description=role_data.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    
    if role_data.permission_ids:
        perm_repo = PermissionRepository(db)
        for perm_id in role_data.permission_ids:
            perm = perm_repo.get_by_id(perm_id)
            if perm:
                role.permissions.append(perm)
        db.commit()
    
    return role


@roles_router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Get role by ID (admin only)"""
    role_repo = RoleRepository(db)
    role_service = RoleService(role_repo)
    
    role = role_service.get_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


@roles_router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: UUID,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Update role (admin only)"""
    role_repo = RoleRepository(db)
    role_service = RoleService(role_repo)
    
    role = role_service.get_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    update_data = role_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "permission_ids" and value:
            perm_repo = PermissionRepository(db)
            role.permissions = []
            for perm_id in value:
                perm = perm_repo.get_by_id(perm_id)
                if perm:
                    role.permissions.append(perm)
        elif hasattr(role, field):
            setattr(role, field, value)
    
    db.commit()
    db.refresh(role)
    return role