"""
Media-related models: Artist, Album, Track, Project
"""
from sqlalchemy import JSON, Column, String, Integer, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Artist(BaseModel):
    """Artist model for music creators"""
    
    __tablename__ = "artists"
    
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    bio = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    social_links = Column(JSON, nullable=True)  # {twitter, instagram, spotify, etc.}
    
    # Music metadata
    genre = Column(String(100), nullable=True, index=True)
    label = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    
    # Ownership
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", lazy="selectin")
    albums = relationship("Album", back_populates="artist", lazy="selectin")
    tracks = relationship("Track", back_populates="artist", lazy="selectin")
    projects = relationship("Project", back_populates="artist", lazy="selectin")
    brand_profile = relationship("BrandProfile", back_populates="artist", uselist=False, lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<Artist(id={self.id}, name={self.name})>"


class Album(BaseModel):
    """Album model for music releases"""
    
    __tablename__ = "albums"
    
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    cover_url = Column(String(500), nullable=True)
    release_date = Column(DateTime, nullable=True)
    
    # Metadata
    genre = Column(String(100), nullable=True, index=True)
    label = Column(String(255), nullable=True)
    total_tracks = Column(Integer, default=0)
    total_duration = Column(Integer, default=0)  # in seconds
    
    # Type
    is_single = Column(Boolean, default=False)
    
    # Ownership
    artist_id = Column(UUID(as_uuid=True), ForeignKey("artists.id"), nullable=True)
    
    # Relationships
    artist = relationship("Artist", back_populates="albums", lazy="selectin")
    tracks = relationship("Track", back_populates="album", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<Album(id={self.id}, title={self.title})>"


class Track(BaseModel):
    """Track model for individual songs"""
    
    __tablename__ = "tracks"
    
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Audio properties
    duration = Column(Integer, nullable=True)  # in seconds
    track_number = Column(Integer, nullable=True)
    bpm = Column(Integer, nullable=True)
    key_signature = Column(String(20), nullable=True)
    
    # Content flags
    explicit = Column(Boolean, default=False)
    
    # Audio files
    audio_url = Column(String(500), nullable=True)
    waveform_url = Column(String(500), nullable=True)
    
    # Metadata
    genre = Column(String(100), nullable=True, index=True)
    mood = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Statistics
    play_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    
    # Ownership
    artist_id = Column(UUID(as_uuid=True), ForeignKey("artists.id"), nullable=True)
    album_id = Column(UUID(as_uuid=True), ForeignKey("albums.id"), nullable=True)
    
    # Relationships
    artist = relationship("Artist", back_populates="tracks", lazy="selectin")
    album = relationship("Album", back_populates="tracks", lazy="selectin")
    media_assets = relationship("MediaAsset", back_populates="track", lazy="selectin")
    social_posts = relationship("SocialPost", back_populates="track", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<Track(id={self.id}, title={self.title})>"


class Project(BaseModel):
    """Project model for creative work organization"""
    
    __tablename__ = "projects"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="draft", index=True)  # draft, in_progress, completed, archived
    
    # Project type (album, single, video, campaign, etc.)
    project_type = Column(String(50), nullable=True)
    
    # Visual
    cover_url = Column(String(500), nullable=True)
    
    # Additional metadata
    meta_info = Column("metadata", JSON, nullable=True)
    
    # Ownership
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    artist_id = Column(UUID(as_uuid=True), ForeignKey("artists.id"), nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="projects", lazy="selectin")
    artist = relationship("Artist", back_populates="projects", lazy="selectin")
    media_assets = relationship("MediaAsset", back_populates="project", lazy="selectin")
    generated_assets = relationship("GeneratedAsset", back_populates="project", lazy="selectin")
    workflows = relationship("Workflow", back_populates="project", lazy="selectin")
    render_jobs = relationship("RenderJob", back_populates="project", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name})>"