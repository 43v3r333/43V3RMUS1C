"""
Asset models: MediaAsset, GeneratedAsset
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class MediaAsset(BaseModel):
    """Media asset model for uploaded files"""
    
    __tablename__ = "media_assets"
    
    name = Column(String(255), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # in bytes
    mime_type = Column(String(100), nullable=True)
    
    # Asset classification
    asset_type = Column(String(50), nullable=False, index=True)  # audio, video, image, document
    status = Column(String(50), default="pending", index=True)  # pending, processing, ready, failed
    
    # Media properties
    duration = Column(Integer, nullable=True)  # for audio/video in seconds
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Ownership
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    track_id = Column(UUID(as_uuid=True), ForeignKey("tracks.id"), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="media_assets", lazy="selectin")
    track = relationship("Track", back_populates="media_assets", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<MediaAsset(id={self.id}, name={self.name}, type={self.asset_type})>"


class GeneratedAsset(BaseModel):
    """Generated asset model for AI-created content"""
    
    __tablename__ = "generated_assets"
    
    name = Column(String(255), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False, index=True)  # audio, video, image, text
    generation_type = Column(String(50), nullable=False)  # tts, music, image, video
    
    # Prompt information
    prompt = Column(Text, nullable=True)
    negative_prompt = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True)
    
    # Output files
    output_path = Column(String(500), nullable=True)
    output_url = Column(String(500), nullable=True)
    preview_url = Column(String(500), nullable=True)
    
    # Status
    status = Column(String(50), default="pending", index=True)  # pending, processing, ready, failed
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Performance metrics
    generation_time = Column(Integer, nullable=True)  # in seconds
    
    # Ownership
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="generated_assets", lazy="selectin")
    campaign = relationship("Campaign", back_populates="generated_assets", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<GeneratedAsset(id={self.id}, name={self.name}, type={self.asset_type})>"