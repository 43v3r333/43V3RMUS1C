"""
Media asset repository for data access.
"""
import uuid
from typing import List, Optional
from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.media_execution import MediaAsset, AssetStatus


class MediaAssetRepository:
    """Repository for media asset data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, asset_id: uuid.UUID) -> Optional[MediaAsset]:
        """Get asset by ID"""
        return self.db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
    
    def get_by_slug(self, slug: str) -> Optional[MediaAsset]:
        """Get asset by slug"""
        return self.db.query(MediaAsset).filter(MediaAsset.slug == slug).first()
    
    def get_by_md5(self, md5_hash: str) -> Optional[MediaAsset]:
        """Get asset by content hash (for deduplication)"""
        return self.db.query(MediaAsset).filter(MediaAsset.md5_hash == md5_hash).first()
    
    def list_assets(
        self,
        project_id: Optional[uuid.UUID] = None,
        artist_id: Optional[uuid.UUID] = None,
        asset_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[MediaAsset]:
        """List assets with filters"""
        query = self.db.query(MediaAsset)
        
        # Filters
        if project_id:
            query = query.filter(MediaAsset.project_id == project_id)
        if artist_id:
            query = query.filter(MediaAsset.artist_id == artist_id)
        if asset_type:
            query = query.filter(MediaAsset.asset_type == asset_type)
        if status:
            query = query.filter(MediaAsset.status == status)
        if search:
            query = query.filter(
                or_(
                    MediaAsset.name.ilike(f"%{search}%"),
                    MediaAsset.original_filename.ilike(f"%{search}%")
                )
            )
        
        # Soft delete filter
        query = query.filter(MediaAsset.deleted_at.is_(None))
        
        return query.order_by(
            MediaAsset.created_at.desc()
        ).offset(offset).limit(limit).all()
    
    def count_assets(
        self,
        project_id: Optional[uuid.UUID] = None,
        asset_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> int:
        """Count assets matching filters"""
        query = self.db.query(MediaAsset)
        
        if project_id:
            query = query.filter(MediaAsset.project_id == project_id)
        if asset_type:
            query = query.filter(MediaAsset.asset_type == asset_type)
        if status:
            query = query.filter(MediaAsset.status == status)
        
        return query.filter(MediaAsset.deleted_at.is_(None)).count()
    
    def create(self, asset: MediaAsset) -> MediaAsset:
        """Create new asset"""
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset
    
    def update(self, asset_id: uuid.UUID, updates: dict) -> MediaAsset:
        """Update asset"""
        asset = self.get_by_id(asset_id)
        
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")
        
        for key, value in updates.items():
            if hasattr(asset, key):
                setattr(asset, key, value)
        
        asset.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(asset)
        
        return asset
    
    def soft_delete(self, asset_id: uuid.UUID) -> MediaAsset:
        """Soft delete asset"""
        asset = self.get_by_id(asset_id)
        
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")
        
        asset.deleted_at = datetime.utcnow()
        self.db.commit()
        
        return asset
    
    def hard_delete(self, asset_id: uuid.UUID) -> bool:
        """Permanently delete asset"""
        asset = self.get_by_id(asset_id)
        
        if not asset:
            return False
        
        self.db.delete(asset)
        self.db.commit()
        
        return True
    
    def get_by_project(self, project_id: uuid.UUID) -> List[MediaAsset]:
        """Get all assets for a project"""
        return self.db.query(MediaAsset).filter(
            MediaAsset.project_id == project_id,
            MediaAsset.deleted_at.is_(None)
        ).all()
    
    def get_by_type(self, asset_type: str, limit: int = 50) -> List[MediaAsset]:
        """Get assets by type"""
        return self.db.query(MediaAsset).filter(
            MediaAsset.asset_type == asset_type,
            MediaAsset.deleted_at.is_(None)
        ).order_by(MediaAsset.created_at.desc()).limit(limit).all()
    
    def get_recent(self, limit: int = 10) -> List[MediaAsset]:
        """Get recently created assets"""
        return self.db.query(MediaAsset).filter(
            MediaAsset.deleted_at.is_(None)
        ).order_by(MediaAsset.created_at.desc()).limit(limit).all()
    
    def get_orphaned(self) -> List[MediaAsset]:
        """Get assets not associated with any project"""
        return self.db.query(MediaAsset).filter(
            MediaAsset.project_id.is_(None),
            MediaAsset.deleted_at.is_(None)
        ).all()
    
    def bulk_update_status(self, asset_ids: List[uuid.UUID], status: str) -> int:
        """Bulk update status for multiple assets"""
        count = self.db.query(MediaAsset).filter(
            MediaAsset.id.in_(asset_ids)
        ).update(
            {MediaAsset.status: status, MediaAsset.updated_at: datetime.utcnow()},
            synchronize_session=False
        )
        self.db.commit()
        return count