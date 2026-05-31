"""
Base service with common operations
"""
from typing import TypeVar, Generic, Optional, List, Type
from uuid import UUID

from ..models.base import BaseModel
from ..repositories.base import BaseRepository

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseService(Generic[ModelType]):
    """Base service layer with common business logic"""
    
    def __init__(self, repository: BaseRepository[ModelType]):
        self.repository = repository
    
    def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get entity by ID"""
        return self.repository.get_by_id(id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all entities"""
        return self.repository.get_all(skip, limit)
    
    def count(self) -> int:
        """Count entities"""
        return self.repository.count()
    
    def exists(self, id: UUID) -> bool:
        """Check if entity exists"""
        return self.repository.exists(id)