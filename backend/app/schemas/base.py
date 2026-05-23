"""
Base schemas with common fields
"""
from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: datetime
    updated_at: datetime


class UUIDMixin(BaseModel):
    """Mixin for UUID id field"""
    id: UUID


class BaseSchema(TimestampMixin, UUIDMixin):
    """Base schema combining common mixins"""
    model_config = ConfigDict(from_attributes=True)


class SoftDeleteSchema(BaseModel):
    """Schema for soft delete support"""
    deleted_at: Optional[datetime] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    per_page: int = 20
    total: Optional[int] = None
    has_more: bool = False


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str = "Operation completed"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    code: str
    details: Optional[Any] = None