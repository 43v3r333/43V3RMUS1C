"""
User, Role, and Permission models
"""
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel


class Role(BaseModel):
    """Role model for RBAC"""
    __tablename__ = "roles"
    
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")


class Permission(BaseModel):
    """Permission model"""
    __tablename__ = "permissions"
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    resource = Column(String(50), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")


class User(BaseModel):
    """User model"""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=True)
    role = relationship("Role", backref="users")
    
    # Relationships
    artists = relationship("Artist", back_populates="user", foreign_keys="Artist.user_id")
    projects = relationship("Project", back_populates="owner")
    campaigns = relationship("Campaign", back_populates="created_by")
    workflows = relationship("Workflow", back_populates="created_by")
    
    @property
    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Check if user has specific permission"""
        if self.is_superuser:
            return True
        return any(
            p.resource == resource and p.action == action
            for p in self.role.permissions
        )