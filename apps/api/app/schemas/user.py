"""
User-related Pydantic schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.schemas.base import BaseSchema, TimestampSchema


class UserBase(BaseSchema):
    """Base user schema"""
    
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(default=None, max_length=500)


class UserCreate(UserBase):
    """User creation schema"""
    
    password: str = Field(min_length=8, max_length=100)


class UserUpdate(BaseSchema):
    """User update schema"""
    
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(default=None, max_length=500)


class UserResponse(TimestampSchema):
    """User response schema"""
    
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    is_superuser: bool
    is_verified: bool
    role_id: Optional[UUID] = None


class UserLogin(BaseSchema):
    """Login request schema"""
    
    username: str
    password: str


class TokenResponse(BaseSchema):
    """Token response schema"""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseSchema):
    """Refresh token request schema"""
    
    refresh_token: str


class PasswordChange(BaseSchema):
    """Password change request schema"""
    
    current_password: str
    new_password: str = Field(min_length=8)


class PasswordResetRequest(BaseSchema):
    """Password reset request schema"""
    
    email: EmailStr


class PasswordResetConfirm(BaseSchema):
    """Password reset confirmation schema"""
    
    token: str
    new_password: str = Field(min_length=8)


class RoleBase(BaseSchema):
    """Base role schema"""
    
    name: str = Field(min_length=2, max_length=50)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Role creation schema"""
    pass


class RoleResponse(TimestampSchema):
    """Role response schema"""
    
    name: str
    description: Optional[str] = None


class PermissionBase(BaseSchema):
    """Base permission schema"""
    
    name: str = Field(min_length=2, max_length=100)
    resource: str = Field(min_length=2, max_length=50)
    action: str = Field(min_length=2, max_length=50)
    description: Optional[str] = None


class PermissionResponse(TimestampSchema):
    """Permission response schema"""
    
    name: str
    resource: str
    action: str
    description: Optional[str] = None