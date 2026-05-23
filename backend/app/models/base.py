"""
Base model with common fields for all tables
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID

from ..core.database import Base


class BaseModel(Base):
    """Abstract base model with common fields"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    def soft_delete(self):
        """Mark record as deleted"""
        self.deleted_at = datetime.utcnow()
    
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None