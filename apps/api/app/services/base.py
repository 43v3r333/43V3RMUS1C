"""
Base service layer
"""
import logging
from typing import Generic, TypeVar, Optional, List, Type
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType")
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(Generic[ModelType, RepositoryType]):
    """Base service with common business logic"""
    
    def __init__(self, repository: RepositoryType):
        """
        Initialize service
        
        Args:
            repository: Repository instance
        """
        self.repository = repository
    
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get entity by ID"""
        return await self.repository.get_by_id(id)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all entities"""
        return await self.repository.get_all(skip, limit)
    
    async def create(self, obj: ModelType) -> ModelType:
        """Create new entity"""
        return await self.repository.create(obj)
    
    async def update(self, obj: ModelType) -> ModelType:
        """Update existing entity"""
        return await self.repository.update(obj)
    
    async def delete(self, obj: ModelType, hard: bool = False) -> bool:
        """Delete entity"""
        return await self.repository.delete(obj, hard)
    
    async def count(self) -> int:
        """Count entities"""
        return await self.repository.count()
    
    async def exists(self, id: UUID) -> bool:
        """Check if entity exists"""
        return await self.repository.exists(id)