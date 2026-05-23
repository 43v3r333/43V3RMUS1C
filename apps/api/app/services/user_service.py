"""
User service
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, Role
from app.repositories.user_repository import UserRepository, RoleRepository
from app.services.base import BaseService
from app.core.security import get_password_hash, verify_password


class UserService(BaseService[User, UserRepository]):
    """Service for user operations"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(UserRepository(db))
        self.db = db
        self.role_repo = RoleRepository(db)
    
    async def create_user(
        self,
        email: str,
        username: str,
        password: str,
        **kwargs
    ) -> User:
        """Create new user with hashed password"""
        user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            **kwargs
        )
        return await self.repository.create(user)
    
    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user by username/email and password"""
        # Try to find by email or username
        user = await self.repository.get_by_email(username)
        if not user:
            user = await self.repository.get_by_username(username)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await self.repository.get_by_email(email)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return await self.repository.get_by_username(username)
    
    async def email_exists(self, email: str) -> bool:
        """Check if email is already registered"""
        user = await self.repository.get_by_email(email)
        return user is not None
    
    async def username_exists(self, username: str) -> bool:
        """Check if username is already taken"""
        user = await self.repository.get_by_username(username)
        return user is not None
    
    async def update_password(self, user: User, new_password: str) -> User:
        """Update user password"""
        user.hashed_password = get_password_hash(new_password)
        return await self.repository.update(user)
    
    async def set_role(self, user: User, role_id: UUID) -> User:
        """Set user role"""
        role = await self.role_repo.get_by_id(role_id)
        if role:
            user.role_id = role_id
            return await self.repository.update(user)
        return user


class RoleService(BaseService[Role, RoleRepository]):
    """Service for role operations"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(RoleRepository(db))