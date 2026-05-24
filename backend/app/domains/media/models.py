"""
Media Domain Models - Media lifecycle and asset management
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, JSON, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class MediaType(str, Enum):
    """Media file types"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    OTHER = "other"


class MediaStatus(str, Enum):
    """Media processing status"""
    UPLOADED = "uploaded"
    VALIDATING = "validating"
    VALIDATED = "validated"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    TRANSFORMING = "transforming"
    READY = "ready"
    FAILED = "failed"


class MediaAsset(BaseModel):
    """Core media asset model"""
    __tablename__ = "media_assets"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    media_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default=MediaStatus.UPLOADED.value, index=True)
    
    # Media metadata
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    frame_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bitrate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sample_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    channels: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Analysis results
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    fingerprint: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    
    # Processing state
    processing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    project_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="media_assets")
    
    track_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tracks.id"), nullable=True)
    track: Mapped[Optional["Track"]] = relationship("Track", back_populates="media_assets")
    
    # Waveform data relationship
    waveform_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("waveform_data.id"), nullable=True)
    waveform: Mapped[Optional["WaveformData"]] = relationship("WaveformData", back_populates="media_asset")


@dataclass
class MediaFile:
    """Media file descriptor"""
    path: str
    name: str
    size: int
    mime_type: str
    media_type: MediaType
    created_at: datetime = field(default_factory=datetime.utcnow)
    checksum: Optional[str] = None


@dataclass
class ProcessingResult:
    """Media processing result"""
    success: bool
    asset_id: Optional[UUID] = None
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration: Optional[int] = None
    dimensions: Optional[tuple] = None
    error: Optional[str] = None
    processing_time: float = 0.0


class MediaValidationRule:
    """Validation rule for media files"""
    
    def __init__(
        self,
        allowed_types: List[MediaType],
        max_size: int = 1024 * 1024 * 1024,  # 1GB
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None,
    ):
        self.allowed_types = allowed_types
        self.max_size = max_size
        self.min_duration = min_duration
        self.max_duration = max_duration
    
    def validate(self, media_file: MediaFile) -> tuple[bool, Optional[str]]:
        """Validate media file against rules"""
        if media_file.media_type not in self.allowed_types:
            return False, f"File type {media_file.media_type} not allowed"
        
        if media_file.size > self.max_size:
            return False, f"File size {media_file.size} exceeds maximum {self.max_size}"
        
        return True, None


# Import for relationship
from ...models.media import Project, Track
from .models import WaveformData