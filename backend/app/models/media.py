"""
Artist and music metadata models
"""
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import BaseModel


class Artist(BaseModel):
    """Artist model"""
    __tablename__ = "artists"
    
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    bio = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    social_links = Column(JSON, nullable=True)  # {"twitter": "...", "instagram": "..."}
    genre = Column(String(100), nullable=True, index=True)
    label = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    is_verified = Column(Boolean, default=False)
    
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="artists", foreign_keys=[user_id])
    
    # Relationships
    tracks = relationship("Track", back_populates="artist")
    albums = relationship("Album", back_populates="artist")


class Album(BaseModel):
    """Album model"""
    __tablename__ = "albums"
    
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    cover_url = Column(String(500), nullable=True)
    release_date = Column(DateTime, nullable=True)
    genre = Column(String(100), nullable=True, index=True)
    label = Column(String(255), nullable=True)
    total_tracks = Column(Integer, default=0)
    total_duration = Column(Integer, default=0)  # seconds
    is_single = Column(Boolean, default=False)
    
    artist_id = Column(PGUUID(as_uuid=True), ForeignKey("artists.id"), nullable=True)
    artist = relationship("Artist", back_populates="albums")
    
    # Relationships
    tracks = relationship("Track", back_populates="album")


class Track(BaseModel):
    """Track/Song model"""
    __tablename__ = "tracks"
    
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)  # seconds
    track_number = Column(Integer, nullable=True)
    bpm = Column(Integer, nullable=True)
    key_signature = Column(String(20), nullable=True)
    explicit = Column(Boolean, default=False)
    
    audio_url = Column(String(500), nullable=True)
    waveform_url = Column(String(500), nullable=True)
    
    genre = Column(String(100), nullable=True, index=True)
    mood = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)  # ["pop", "upbeat", "summer"]
    
    play_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    
    artist_id = Column(PGUUID(as_uuid=True), ForeignKey("artists.id"), nullable=True)
    artist = relationship("Artist", back_populates="tracks")
    
    album_id = Column(PGUUID(as_uuid=True), ForeignKey("albums.id"), nullable=True)
    album = relationship("Album", back_populates="tracks")
    
    # Relationships
    media_assets = relationship("MediaAsset", back_populates="track")


class Project(BaseModel):
    """Project model for organizing creative work"""
    __tablename__ = "projects"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="draft", index=True)  # draft, in_progress, completed, archived
    project_type = Column(String(50), nullable=True)  # album, single, campaign, remix, etc.
    
    cover_url = Column(String(500), nullable=True)
    metadata_dict = Column("metadata", JSON, nullable=True)
    
    owner_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="projects")
    
    artist_id = Column(PGUUID(as_uuid=True), ForeignKey("artists.id"), nullable=True)
    artist = relationship("Artist")
    
    # Relationships
    media_assets = relationship("MediaAsset", back_populates="project")
    generated_assets = relationship("GeneratedAsset", back_populates="project")
    workflows = relationship("Workflow", back_populates="project")