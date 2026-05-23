"""
Media schemas for artists, albums, tracks, projects
"""
from datetime import datetime
from typing import Optional, List, Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class ArtistBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    bio: Optional[str] = None
    image_url: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    genre: Optional[str] = None
    label: Optional[str] = None
    website: Optional[str] = None


class ArtistCreate(ArtistBase):
    slug: str
    user_id: Optional[UUID] = None


class ArtistUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    bio: Optional[str] = None
    image_url: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    genre: Optional[str] = None
    label: Optional[str] = None
    website: Optional[str] = None
    is_verified: Optional[bool] = None


class ArtistResponse(ArtistBase):
    id: UUID
    slug: str
    is_verified: bool
    user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlbumBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    cover_url: Optional[str] = None
    release_date: Optional[datetime] = None
    genre: Optional[str] = None
    label: Optional[str] = None
    total_tracks: int = 0
    total_duration: int = 0
    is_single: bool = False


class AlbumCreate(AlbumBase):
    slug: str
    artist_id: UUID


class AlbumUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    release_date: Optional[datetime] = None
    genre: Optional[str] = None
    label: Optional[str] = None
    total_tracks: Optional[int] = None
    total_duration: Optional[int] = None
    is_single: Optional[bool] = None


class AlbumResponse(AlbumBase):
    id: UUID
    slug: str
    artist_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TrackBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
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
    slug: str
    artist_id: UUID
    album_id: Optional[UUID] = None


class TrackUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
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


class TrackResponse(TrackBase):
    id: UUID
    slug: str
    play_count: int = 0
    like_count: int = 0
    artist_id: Optional[UUID] = None
    album_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = "draft"
    project_type: Optional[str] = None
    cover_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ProjectCreate(ProjectBase):
    owner_id: UUID
    artist_id: Optional[UUID] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    project_type: Optional[str] = None
    cover_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ProjectResponse(ProjectBase):
    id: UUID
    owner_id: UUID
    artist_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}