"""
Storage Domain Models - Storage management
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class StorageProvider(str, Enum):
    """Storage provider types"""
    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"
    AZURE = "azure"
    MINIO = "minio"


class StorageTier(str, Enum):
    """Storage tier levels"""
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    ARCHIVE = "archive"


class StorageAsset(BaseModel):
    """Storage asset model for tracking stored files"""
    __tablename__ = "storage_assets"
    
    # Asset identification
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Storage info
    provider: Mapped[str] = mapped_column(String(50), default=StorageProvider.LOCAL.value, index=True)
    bucket: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    region: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Content info
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    
    # Lifecycle
    storage_tier: Mapped[str] = mapped_column(String(20), default=StorageTier.HOT.value, index=True)
    last_accessed: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metadata
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # References
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    project_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    media_asset_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("media_assets.id"), nullable=True)


class StorageQuota(BaseModel):
    """Storage quota model"""
    __tablename__ = "storage_quotas"
    
    owner_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Quota limits
    max_storage_bytes: Mapped[int] = mapped_column(Integer, default=10 * 1024 * 1024 * 1024)  # 10GB
    max_file_count: Mapped[int] = mapped_column(Integer, default=1000)
    
    # Current usage
    current_storage_bytes: Mapped[int] = mapped_column(Integer, default=0)
    current_file_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Usage tracking
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)