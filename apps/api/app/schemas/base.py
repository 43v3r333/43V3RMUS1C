"""
Base Pydantic schemas for consistent API responses
"""
from datetime import datetime
from typing import Generic, TypeVar, Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields"""
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class BaseResponse(TimestampSchema):
    """Base response schema with timestamps"""
    pass


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    
    items: List[T]
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    per_page: int = Field(description="Items per page")
    has_more: bool = Field(description="Whether there are more pages")
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        per_page: int,
    ) -> "PaginatedResponse[T]":
        """Create a paginated response"""
        return cls(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            has_more=(page * per_page) < total,
        )


class ErrorResponse(BaseSchema):
    """Error response schema"""
    
    detail: str = Field(description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")
    field: Optional[str] = Field(default=None, description="Field that caused the error")


class SuccessResponse(BaseSchema):
    """Simple success response"""
    
    success: bool = True
    message: str = "Operation completed successfully"


class HealthResponse(BaseSchema):
    """Health check response"""
    
    status: str
    version: str
    database: Optional[str] = None


class TokenPayload(BaseSchema):
    """JWT token payload schema"""
    
    sub: str
    exp: int
    iat: int
    type: str = "access"


class RefreshTokenPayload(TokenPayload):
    """Refresh token payload"""
    
    type: str = "refresh"