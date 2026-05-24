"""
Storage Services - Storage management operations
"""
import os
import hashlib
import logging
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from pathlib import Path
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from .models import StorageProvider, StorageTier, StorageAsset, StorageQuota

logger = logging.getLogger(__name__)


class StorageManager:
    """
    Storage manager for file storage operations.
    Handles file storage, retrieval, lifecycle management,
    and quota tracking.
    """
    
    def __init__(
        self,
        db: AsyncSession,
        base_path: str = "./storage",
    ):
        self.db = db
        self.base_path = Path(base_path)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure storage directories exist"""
        directories = [
            self.base_path / "media",
            self.base_path / "rendered",
            self.base_path / "thumbnails",
            self.base_path / "waveforms",
            self.base_path / "temp",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def store_file(
        self,
        file_content: bytes,
        file_name: str,
        mime_type: Optional[str] = None,
        owner_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        media_asset_id: Optional[UUID] = None,
        storage_type: str = "media",
        tags: Optional[List[str]] = None,
    ) -> StorageAsset:
        """Store a file and create asset record"""
        # Calculate checksum
        checksum = hashlib.sha256(file_content).hexdigest()
        
        # Determine path
        file_path = self.base_path / storage_type / f"{checksum}_{file_name}"
        
        # Write file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Create asset
        asset = StorageAsset(
            name=file_name,
            file_name=file_name,
            file_path=str(file_path),
            file_size=len(file_content),
            mime_type=mime_type,
            checksum=checksum,
            owner_id=owner_id,
            project_id=project_id,
            media_asset_id=media_asset_id,
            tags=tags,
        )
        
        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)
        
        return asset
    
    async def store_file_from_path(
        self,
        source_path: str,
        file_name: Optional[str] = None,
        owner_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        media_asset_id: Optional[UUID] = None,
        storage_type: str = "media",
    ) -> StorageAsset:
        """Store a file from existing path"""
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        file_name = file_name or source.name
        file_size = source.stat().st_size
        
        # Calculate checksum
        hasher = hashlib.sha256()
        with open(source, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        checksum = hasher.hexdigest()
        
        # Determine path
        dest_path = self.base_path / storage_type / f"{checksum}_{file_name}"
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        import shutil
        shutil.copy2(source, dest_path)
        
        # Create asset
        asset = StorageAsset(
            name=file_name,
            file_name=file_name,
            file_path=str(dest_path),
            file_size=file_size,
            checksum=checksum,
            owner_id=owner_id,
            project_id=project_id,
            media_asset_id=media_asset_id,
        )
        
        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)
        
        return asset
    
    async def get_asset(self, asset_id: UUID) -> Optional[StorageAsset]:
        """Get storage asset by ID"""
        result = await self.db.execute(
            select(StorageAsset).where(StorageAsset.id == asset_id)
        )
        return result.scalar_one_or_none()
    
    async def get_asset_by_checksum(self, checksum: str) -> Optional[StorageAsset]:
        """Get storage asset by checksum"""
        result = await self.db.execute(
            select(StorageAsset).where(StorageAsset.checksum == checksum)
        )
        return result.scalar_one_or_none()
    
    async def delete_asset(self, asset: StorageAsset) -> bool:
        """Delete storage asset and file"""
        try:
            # Delete file
            file_path = Path(asset.file_path)
            if file_path.exists():
                file_path.unlink()
            
            # Delete record
            await self.db.delete(asset)
            await self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting asset: {e}")
            return False
    
    async def update_access(self, asset: StorageAsset) -> StorageAsset:
        """Update asset access tracking"""
        asset.last_accessed = datetime.utcnow()
        asset.access_count += 1
        
        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)
        
        return asset
    
    async def get_user_usage(self, owner_id: UUID) -> Dict[str, Any]:
        """Get storage usage for user"""
        result = await self.db.execute(
            select(
                func.count(StorageAsset.id).label("file_count"),
                func.sum(StorageAsset.file_size).label("total_size"),
            ).where(StorageAsset.owner_id == owner_id)
        )
        
        row = result.one()
        
        return {
            "file_count": row.file_count or 0,
            "total_size": row.total_size or 0,
        }
    
    async def check_quota(
        self,
        owner_id: UUID,
        additional_size: int = 0,
    ) -> Tuple[bool, Optional[str]]:
        """Check if user has quota for additional storage"""
        result = await self.db.execute(
            select(StorageQuota).where(StorageQuota.owner_id == owner_id)
        )
        quota = result.scalar_one_or_none()
        
        if not quota:
            return True, None  # No quota set
        
        usage = await self.get_user_usage(owner_id)
        
        if usage["total_size"] + additional_size > quota.max_storage_bytes:
            return False, f"Storage quota exceeded ({quota.max_storage_bytes} bytes limit)"
        
        if usage["file_count"] >= quota.max_file_count:
            return False, f"File count quota exceeded ({quota.max_file_count} files limit)"
        
        return True, None
    
    async def set_quota(
        self,
        owner_id: UUID,
        max_storage_bytes: int = 10 * 1024 * 1024 * 1024,
        max_file_count: int = 1000,
    ) -> StorageQuota:
        """Set or update user storage quota"""
        result = await self.db.execute(
            select(StorageQuota).where(StorageQuota.owner_id == owner_id)
        )
        quota = result.scalar_one_or_none()
        
        if quota:
            quota.max_storage_bytes = max_storage_bytes
            quota.max_file_count = max_file_count
        else:
            quota = StorageQuota(
                owner_id=owner_id,
                max_storage_bytes=max_storage_bytes,
                max_file_count=max_file_count,
            )
            self.db.add(quota)
        
        await self.db.commit()
        await self.db.refresh(quota)
        
        return quota