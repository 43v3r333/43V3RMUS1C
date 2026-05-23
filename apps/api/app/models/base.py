"""
Base model class with common fields
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declared_attr

from app.core.database import Base


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    
    deleted_at = Column(DateTime, nullable=True)
    
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class UUIDPrimaryKeyMixin:
    """Mixin for UUID primary key"""
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class BaseModel(Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin):
    """
    Base model class with common mixins
    
    Provides:
    - UUID primary key
    - Created at timestamp
    - Updated at timestamp
    - Soft delete functionality
    """
    
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name"""
        import re
        # Convert CamelCase to snake_case
        name = cls.__name__
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, uuid.UUID):
                value = str(value)
            result[column.name] = value
        return result
    
    def to_safe_dict(self) -> dict:
        """Convert model to dictionary excluding sensitive fields"""
        return self.to_dict()