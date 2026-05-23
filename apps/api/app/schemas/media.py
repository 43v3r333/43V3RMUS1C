"""
Media-related Pydantic schemas (Artist, Album, Track, Project)
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, TimestampSchema


# ============ Artist Schemas ============

class ArtistBase(BaseSchema):
    """Base artist schema"""
    
    name: str = Field(min_length=1, max_length=255)
    slug: Optional[str] = None
    bio: Optional[str] = None
    image_url: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    genre: Optional[str] = None
    label: Optional[str] = None
    website: Optional[str] = None
    is_verified: bool = False


class ArtistCreate(ArtistBase):
    """Artist creation schema"""
    
    pass


class ArtistUpdate(BaseSchema):
    """Artist update schema"""
    
    name: Optional[str] = Field(default=None, max_length=255)
    bio: Optional[str] = None
    image_url: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    genre: Optional[str] = None
    label: Optional[str] = None
    website: Optional[str] = None


class ArtistResponse(TimestampSchema):
    """Artist response schema"""
    
    name: str
    slug: str
    bio: Optional[str] = None
    image_url: Optional[str] = None
    social_links: Optional[Dict[str, Any]] = None
    genre: Optional[str] = None
    label: Optional[str] = None
    website: Optional[str] = None
    is_verified: bool
    user_id: Optional[UUID] = None


# ============ Album Schemas ============

class AlbumBase(BaseSchema):
    """Base album schema"""
    
    title: str = Field(min_length=1, max_length=255)
    slug: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    release_date: Optional[datetime] = None
    genre: Optional[str] = None
    label: Optional[str] = None
    total_tracks: int = 0
    total_duration: int = 0
    is_single: bool = False


class AlbumCreate(AlbumBase):
    """Album creation schema"""
    
    artist_id: Optional[UUID] = None


class AlbumUpdate(BaseSchema):
    """Album update schema"""
    
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    cover_url: Optional[str] = None
    release_date: Optional[datetime] = None
    genre: Optional[str] = None
    label: Optional[str] = None
    is_single: Optional[bool] = None


class AlbumResponse(TimestampSchema):
    """Album response schema"""
    
    title: str
    slug: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    release_date: Optional[datetime] = None
    genre: Optional[str] = None
    label: Optional[str] = None
    total_tracks: int
    total_duration: int
    is_single: bool
    artist_id: Optional[UUID] = None


# ============ Track Schemas ============

class TrackBase(BaseSchema):
    """Base track schema"""
    
    title: str = Field(min_length=1, max_length=255)
    slug: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    track_number: Optional[int] = None
    bpm: Optional[int] = None
    key_signature: Optional[str] = None
    explicit: bool = False
    audio_url: Optional[str] = None
    waveform_url: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None
    tags: Optional[List[str]] = None


class TrackCreate(TrackBase):
    """Track creation schema"""
    
    artist_id: Optional[UUID] = None
    album_id: Optional[UUID] = None


class TrackUpdate(BaseSchema):
    """Track update schema"""
    
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    duration: Optional[int] = None
    track_number: Optional[int] = None
    bpm: Optional[int] = None
    key_signature: Optional[str] = None
    explicit: Optional[bool] = None
    audio_url: Optional[str] = None
    waveform_url: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None
    tags: Optional[List[str]] = None


class TrackResponse(TimestampSchema):
    """Track response schema"""
    
    title: str
    slug: str
    description: Optional[str] = None
    duration: Optional[int] = None
    track_number: Optional[int] = None
    bpm: Optional[int] = None
    key_signature: Optional[str] = None
    explicit: bool
    audio_url: Optional[str] = None
    waveform_url: Optional[str] = None
    genre: Optional[str] = None
    mood: Optional[str] = None
    tags: Optional[List[str]] = None
    play_count: int
    like_count: int
    artist_id: Optional[UUID] = None
    album_id: Optional[UUID] = None


# ============ Project Schemas ============

class ProjectBase(BaseSchema):
    """Base project schema"""
    
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = "draft"
    project_type: Optional[str] = None
    cover_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ProjectCreate(ProjectBase):
    """Project creation schema"""
    
    artist_id: Optional[UUID] = None


class ProjectUpdate(BaseSchema):
    """Project update schema"""
    
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    project_type: Optional[str] = None
    cover_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ProjectResponse(TimestampSchema):
    """Project response schema"""
    
    name: str
    description: Optional[str] = None
    status: str
    project_type: Optional[str] = None
    cover_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    owner_id: UUID
    artist_id: Optional[UUID] = None