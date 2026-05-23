"""
User repository for database operations
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..models.user import User, Role, Permission
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """User repository with custom queries"""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(
            User.email == email,
            User.deleted_at.is_(None)
        ).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(
            User.username == username,
            User.deleted_at.is_(None)
        ).first()
    
    def get_by_email_or_username(self, identifier: str) -> Optional[User]:
        """Get user by email or username"""
        return self.db.query(User).filter(
            or_(
                User.email == identifier,
                User.username == identifier
            ),
            User.deleted_at.is_(None)
        ).first()
    
    def search(self, query: str, skip: int = 0, limit: int = 20) -> List[User]:
        """Search users by name or username"""
        search_filter = or_(
            User.username.ilike(f"%{query}%"),
            User.email.ilike(f"%{query}%"),
            User.first_name.ilike(f"%{query}%"),
            User.last_name.ilike(f"%{query}%")
        )
        return self.db.query(User).filter(
            search_filter,
            User.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users"""
        return self.db.query(User).filter(
            User.is_active == True,
            User.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_role(self, role_id: UUID, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role"""
        return self.db.query(User).filter(
            User.role_id == role_id,
            User.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()


class RoleRepository(BaseRepository[Role]):
    """Role repository"""
    
    def __init__(self, db: Session):
        super().__init__(Role, db)
    
    def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name"""
        return self.db.query(Role).filter(
            Role.name == name,
            Role.deleted_at.is_(None)
        ).first()
    
    def get_with_permissions(self, role_id: UUID) -> Optional[Role]:
        """Get role with eager loaded permissions"""
        return self.db.query(Role).filter(
            Role.id == role_id
        ).first()


class PermissionRepository(BaseRepository[Permission]):
    """Permission repository"""
    
    def __init__(self, db: Session):
        super().__init__(Permission, db)
    
    def get_by_resource_action(self, resource: str, action: str) -> Optional[Permission]:
        """Get permission by resource and action"""
        return self.db.query(Permission).filter(
            Permission.resource == resource,
            Permission.action == action,
            Permission.deleted_at.is_(None)
        ).first()
    
    def get_by_names(self, names: List[str]) -> List[Permission]:
        """Get multiple permissions by names"""
        return self.db.query(Permission).filter(
            Permission.name.in_(names),
            Permission.deleted_at.is_(None)
        ).all()