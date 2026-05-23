"""
User service for business logic
"""
from typing import Optional, List
from uuid import UUID

from ..core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from ..models.user import User, Role
from ..schemas.user import UserCreate, UserUpdate
from ..repositories.user_repository import UserRepository, RoleRepository
from .base import BaseService


class UserService(BaseService[User]):
    """User service with business logic"""
    
    def __init__(self, repository: UserRepository):
        super().__init__(repository)
        self.repo = repository
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.repo.get_by_email(email)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.repo.get_by_username(username)
    
    def get_by_email_or_username(self, identifier: str) -> Optional[User]:
        """Get user by email or username"""
        return self.repo.get_by_email_or_username(identifier)
    
    def search(self, query: str, skip: int = 0, limit: int = 20) -> List[User]:
        """Search users"""
        return self.repo.search(query, skip, limit)
    
    def create(self, user_data: UserCreate) -> User:
        """Create new user with hashed password"""
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role_id=user_data.role_id,
        )
        return self.repo.create(user)
    
    def update(self, user: User, user_data: UserUpdate) -> User:
        """Update user"""
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        return self.repo.update(user)
    
    def authenticate(self, identifier: str, password: str) -> Optional[User]:
        """Authenticate user"""
        user = self.get_by_email_or_username(identifier)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
    
    def create_tokens(self, user: User) -> dict:
        """Create access and refresh tokens"""
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    
    def change_password(self, user: User, current_password: str, new_password: str) -> bool:
        """Change user password"""
        if not verify_password(current_password, user.hashed_password):
            return False
        user.hashed_password = get_password_hash(new_password)
        self.repo.update(user)
        return True


class RoleService(BaseService[Role]):
    """Role service"""
    
    def __init__(self, repository: RoleRepository):
        super().__init__(repository)
        self.repo = repository
    
    def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name"""
        return self.repo.get_by_name(name)