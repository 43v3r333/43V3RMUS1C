"""
User model
"""
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """User model for authentication and authorization"""
    
    __tablename__ = "users"
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile fields
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(String(500), nullable=True)
    
    # Status fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=True)
    role = relationship("Role", back_populates="users", lazy="selectin")
    
    # Social accounts
    social_accounts = relationship("SocialAccount", back_populates="user", lazy="selectin")
    
    # Projects
    projects = relationship("Project", back_populates="owner", lazy="selectin")
    
    # AI prompts
    prompts = relationship("AIPrompt", back_populates="creator", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p) or self.username


class Role(BaseModel):
    """Role model for RBAC"""
    
    __tablename__ = "roles"
    
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="role", lazy="selectin")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"


class Permission(BaseModel):
    """Permission model for fine-grained access control"""
    
    __tablename__ = "permissions"
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    resource = Column(String(50), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    
    # Relationships
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name={self.name})>"


class RolePermission(BaseModel):
    """Association table for role-permission many-to-many relationship"""
    
    __tablename__ = "role_permissions"
    
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False, primary_key=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id"), nullable=False, primary_key=True)


# Import other models
from app.models.media import Artist, Album, Track, Project
from app.models.asset import MediaAsset, GeneratedAsset
from app.models.campaign import Campaign, SocialAccount, SocialPost
from app.models.workflow import Workflow, RenderJob, AutomationJob, AIPrompt
from app.models.analytics import AnalyticsEvent, TrendData, PlatformMetric, BrandProfile
from app.models.system import SystemLog