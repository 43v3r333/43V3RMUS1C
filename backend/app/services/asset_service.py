"""
Asset services for media and generated assets
"""
from typing import Optional, List
from uuid import UUID

from ..models.asset import MediaAsset, GeneratedAsset
from ..schemas.asset import MediaAssetCreate, MediaAssetUpdate, GeneratedAssetCreate, GeneratedAssetUpdate
from ..repositories.asset_repository import MediaAssetRepository, GeneratedAssetRepository
from .base import BaseService


class MediaAssetService(BaseService[MediaAsset]):
    """Media asset service"""
    
    def __init__(self, repository: MediaAssetRepository):
        super().__init__(repository)
        self.repo = repository
    
    def get_by_type(self, asset_type: str, skip: int = 0, limit: int = 20) -> List[MediaAsset]:
        """Get assets by type"""
        return self.repo.get_by_type(asset_type, skip, limit)
    
    def get_by_project(self, project_id: UUID, skip: int = 0, limit: int = 20) -> List[MediaAsset]:
        """Get assets by project"""
        return self.repo.get_by_project(project_id, skip, limit)
    
    def get_by_track(self, track_id: UUID, skip: int = 0, limit: int = 20) -> List[MediaAsset]:
        """Get assets by track"""
        return self.repo.get_by_track(track_id, skip, limit)
    
    def get_pending(self, limit: int = 20) -> List[MediaAsset]:
        """Get pending assets"""
        return self.repo.get_pending(limit)
    
    def create(self, asset_data: MediaAssetCreate) -> MediaAsset:
        """Create new media asset"""
        asset = MediaAsset(
            name=asset_data.name,
            file_name=asset_data.file_name,
            file_path=asset_data.file_path,
            file_size=asset_data.file_size,
            asset_type=asset_data.asset_type,
            mime_type=asset_data.mime_type,
            duration=asset_data.duration,
            width=asset_data.width,
            height=asset_data.height,
            project_id=asset_data.project_id,
            track_id=asset_data.track_id,
        )
        return self.repo.create(asset)
    
    def update_status(self, asset: MediaAsset, status: str) -> MediaAsset:
        """Update asset status"""
        asset.status = status
        return self.repo.update(asset)
    
    def update(self, asset: MediaAsset, asset_data: MediaAssetUpdate) -> MediaAsset:
        """Update asset"""
        update_data = asset_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(asset, field):
                setattr(asset, field, value)
        return self.repo.update(asset)


class GeneratedAssetService(BaseService[GeneratedAsset]):
    """Generated asset service"""
    
    def __init__(self, repository: GeneratedAssetRepository):
        super().__init__(repository)
        self.repo = repository
    
    def get_by_type(self, asset_type: str, skip: int = 0, limit: int = 20) -> List[GeneratedAsset]:
        """Get generated assets by type"""
        return self.repo.get_by_type(asset_type, skip, limit)
    
    def get_by_generation_type(self, generation_type: str, skip: int = 0, limit: int = 20) -> List[GeneratedAsset]:
        """Get generated assets by generation type"""
        return self.repo.get_by_generation_type(generation_type, skip, limit)
    
    def get_by_project(self, project_id: UUID, skip: int = 0, limit: int = 20) -> List[GeneratedAsset]:
        """Get generated assets by project"""
        return self.repo.get_by_project(project_id, skip, limit)
    
    def get_recent(self, limit: int = 20) -> List[GeneratedAsset]:
        """Get recent generated assets"""
        return self.repo.get_recent(limit)
    
    def create(self, asset_data: GeneratedAssetCreate) -> GeneratedAsset:
        """Create new generated asset"""
        asset = GeneratedAsset(
            name=asset_data.name,
            asset_type=asset_data.asset_type,
            generation_type=asset_data.generation_type,
            prompt=asset_data.prompt,
            negative_prompt=asset_data.negative_prompt,
            parameters=asset_data.parameters,
            project_id=asset_data.project_id,
            campaign_id=asset_data.campaign_id,
        )
        return self.repo.create(asset)
    
    def update_status(
        self,
        asset: GeneratedAsset,
        status: str,
        output_path: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> GeneratedAsset:
        """Update generated asset status"""
        asset.status = status
        if output_path:
            asset.output_path = output_path
        if error_message:
            asset.error_message = error_message
        return self.repo.update(asset)
    
    def update(self, asset: GeneratedAsset, asset_data: GeneratedAssetUpdate) -> GeneratedAsset:
        """Update generated asset"""
        update_data = asset_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(asset, field):
                setattr(asset, field, value)
        return self.repo.update(asset)