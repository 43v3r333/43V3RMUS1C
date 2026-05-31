"""
Base repository with common CRUD operations
"""
from typing import Generic, TypeVar, Type, Optional, List, Any
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base repository with common database operations"""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialize repository
        
        Args:
            model: SQLAlchemy model class
            db: Async database session
        """
        self.model = model
        self.db = db
    
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get entity by ID"""
        stmt = select(self.model).where(
            and_(
                self.model.id == id,
                self.model.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all entities with pagination"""
        stmt = select(self.model).where(
            self.model.deleted_at.is_(None)
        ).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def create(self, obj: ModelType) -> ModelType:
        """Create new entity"""
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj
    
    async def update(self, obj: ModelType) -> ModelType:
        """Update existing entity"""
        await self.db.flush()
        await self.db.refresh(obj)
        return obj
    
    async def delete(self, obj: ModelType, hard: bool = False) -> bool:
        """Delete entity (soft or hard delete)"""
        if hard:
            await self.db.delete(obj)
        else:
            from datetime import datetime
            obj.deleted_at = datetime.utcnow()
            await self.db.flush()
        return True
    
    async def count(self) -> int:
        """Count all non-deleted entities"""
        stmt = select(func.count()).select_from(self.model).where(
            self.model.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()
    
    async def exists(self, id: UUID) -> bool:
        """Check if entity exists"""
        stmt = select(func.count()).select_from(self.model).where(
            and_(
                self.model.id == id,
                self.model.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one() > 0
    
    async def paginate(
        self,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[dict] = None,
        order_by: Optional[str] = None,
    ) -> tuple[List[ModelType], int]:
        """
        Paginate entities
        
        Args:
            page: Page number (1-based)
            per_page: Items per page
            filters: Optional filter conditions
            order_by: Optional ordering field
        
        Returns:
            Tuple of (items, total_count)
        """
        # Base query
        stmt = select(self.model).where(self.model.deleted_at.is_(None))
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    column = getattr(self.model, key)
                    if value is not None:
                        if isinstance(value, list):
                            stmt = stmt.where(column.in_(value))
                        else:
                            stmt = stmt.where(column == value)
        
        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()
        
        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            stmt = stmt.order_by(getattr(self.model, order_by))
        else:
            stmt = stmt.order_by(self.model.created_at.desc())
        
        # Apply pagination
        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total