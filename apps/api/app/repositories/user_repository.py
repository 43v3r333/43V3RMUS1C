"""
User repository
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, Role, Permission
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        stmt = select(User).options(
            selectinload(User.role).selectinload(Role.permissions)
        ).where(
            and_(
                User.email == email,
                User.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        stmt = select(User).where(
            and_(
                User.username == username,
                User.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_with_relations(self, id: UUID) -> Optional[User]:
        """Get user with role and permissions"""
        stmt = select(User).options(
            selectinload(User.role).selectinload(Role.permissions)
        ).where(User.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class RoleRepository(BaseRepository[Role]):
    """Repository for Role model"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Role, db)
    
    async def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name"""
        stmt = select(Role).where(
            and_(
                Role.name == name,
                Role.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class PermissionRepository(BaseRepository[Permission]):
    """Repository for Permission model"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Permission, db)