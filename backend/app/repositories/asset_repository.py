"""
Asset repository for media and generated assets
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..models.asset import MediaAsset, GeneratedAsset
from .base import BaseRepository


class MediaAssetRepository(BaseRepository[MediaAsset]):
    """Media asset repository"""
    
    def __init__(self, db: Session):
        super().__init__(MediaAsset, db)
    
    def get_by_type(self, asset_type: str, skip: int = 0, limit: int = 20) -> List[MediaAsset]:
        """Get assets by type"""
        return self.db.query(MediaAsset).filter(
            MediaAsset.asset_type == asset_type,
            MediaAsset.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_project(self, project_id: UUID, skip: int = 0, limit: int = 20) -> List[MediaAsset]:
        """Get assets by project"""
        return self.db.query(MediaAsset).filter(
            MediaAsset.project_id == project_id,
            MediaAsset.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_track(self, track_id: UUID, skip: int = 0, limit: int = 20) -> List[MediaAsset]:
        """Get assets by track"""
        return self.db.query(MediaAsset).filter(
            MediaAsset.track_id == track_id,
            MediaAsset.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 20) -> List[MediaAsset]:
        """Get assets by status"""
        return self.db.query(MediaAsset).filter(
            MediaAsset.status == status,
            MediaAsset.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def search(self, query: str, skip: int = 0, limit: int = 20) -> List[MediaAsset]:
        """Search assets by name"""
        return self.db.query(MediaAsset).filter(
            MediaAsset.name.ilike(f"%{query}%"),
            MediaAsset.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_pending(self, limit: int = 20) -> List[MediaAsset]:
        """Get pending assets for processing"""
        return self.db.query(MediaAsset).filter(
            MediaAsset.status == "pending",
            MediaAsset.deleted_at.is_(None)
        ).limit(limit).all()


class GeneratedAssetRepository(BaseRepository[GeneratedAsset]):
    """Generated asset repository"""
    
    def __init__(self, db: Session):
        super().__init__(GeneratedAsset, db)
    
    def get_by_type(self, asset_type: str, skip: int = 0, limit: int = 20) -> List[GeneratedAsset]:
        """Get generated assets by type"""
        return self.db.query(GeneratedAsset).filter(
            GeneratedAsset.asset_type == asset_type,
            GeneratedAsset.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_generation_type(self, generation_type: str, skip: int = 0, limit: int = 20) -> List[GeneratedAsset]:
        """Get generated assets by generation type"""
        return self.db.query(GeneratedAsset).filter(
            GeneratedAsset.generation_type == generation_type,
            GeneratedAsset.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_project(self, project_id: UUID, skip: int = 0, limit: int = 20) -> List[GeneratedAsset]:
        """Get generated assets by project"""
        return self.db.query(GeneratedAsset).filter(
            GeneratedAsset.project_id == project_id,
            GeneratedAsset.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 20) -> List[GeneratedAsset]:
        """Get generated assets by status"""
        return self.db.query(GeneratedAsset).filter(
            GeneratedAsset.status == status,
            GeneratedAsset.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_recent(self, limit: int = 20) -> List[GeneratedAsset]:
        """Get recent generated assets"""
        return self.db.query(GeneratedAsset).filter(
            GeneratedAsset.deleted_at.is_(None)
        ).order_by(GeneratedAsset.created_at.desc()).limit(limit).all()
    
    def increment_use_count(self, prompt_id: UUID) -> None:
        """Increment prompt use count"""
        pass  # This would be in AIPromptRepository