"""
Base repository with common database operations
"""
from typing import TypeVar, Generic, Optional, List, Type
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get entity by ID with soft delete check"""
        query = self.db.query(self.model).filter(
            self.model.id == id,
            self.model.deleted_at.is_(None)
        )
        return query.first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all non-deleted entities"""
        return self.db.query(self.model).filter(
            self.model.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def create(self, obj: ModelType) -> ModelType:
        """Create new entity"""
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def update(self, obj: ModelType) -> ModelType:
        """Update existing entity"""
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, obj: ModelType, soft: bool = True) -> None:
        """Delete entity (soft by default)"""
        if soft:
            obj.soft_delete()
            self.db.commit()
        else:
            self.db.delete(obj)
            self.db.commit()
    
    def count(self) -> int:
        """Count non-deleted entities"""
        return self.db.query(self.model).filter(
            self.model.deleted_at.is_(None)
        ).count()
    
    def exists(self, id: UUID) -> bool:
        """Check if entity exists and is not deleted"""
        return self.db.query(self.model).filter(
            self.model.id == id,
            self.model.deleted_at.is_(None)
        ).count() > 0