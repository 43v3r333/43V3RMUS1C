"""
Media asset and generation models
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class AssetType(str, enum.Enum):
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    OTHER = "other"


class AssetStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class MediaAsset(BaseModel):
    """Media asset model for storing uploaded files"""
    __tablename__ = "media_assets"
    
    name = Column(String(255), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # bytes
    mime_type = Column(String(100), nullable=True)
    asset_type = Column(String(50), nullable=False, index=True)  # audio, video, image, document
    status = Column(String(50), default=AssetStatus.PENDING.value, index=True)
    
    duration = Column(Integer, nullable=True)  # seconds (for audio/video)
    width = Column(Integer, nullable=True)  # pixels (for images/videos)
    height = Column(Integer, nullable=True)  # pixels
    
    metadata = Column(JSON, nullable=True)  # Additional metadata
    tags = Column(JSON, nullable=True)
    
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    project = relationship("Project", back_populates="media_assets")
    
    track_id = Column(UUID(as_uuid=True), ForeignKey("tracks.id"), nullable=True)
    track = relationship("Track", back_populates="media_assets")


class GeneratedAsset(BaseModel):
    """Generated AI asset model"""
    __tablename__ = "generated_assets"
    
    name = Column(String(255), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False, index=True)  # image, video, audio
    generation_type = Column(String(50), nullable=False)  # tts, music, visual, etc.
    
    prompt = Column(Text, nullable=True)
    negative_prompt = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True)
    
    output_path = Column(String(500), nullable=True)
    output_url = Column(String(500), nullable=True)
    preview_url = Column(String(500), nullable=True)
    
    status = Column(String(50), default=AssetStatus.PENDING.value, index=True)
    error_message = Column(Text, nullable=True)
    
    generation_time = Column(Integer, nullable=True)  # seconds
    
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    project = relationship("Project", back_populates="generated_assets")
    
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    campaign = relationship("Campaign", back_populates="generated_assets")