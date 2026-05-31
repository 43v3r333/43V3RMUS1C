"""
Media-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID

from pydantic import BaseModel, Field


class MediaAssetBase(BaseModel):
    """Base media asset schema"""
    name: str
    asset_type: str
    original_filename: Optional[str] = None
    mime_type: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None


class MediaAssetCreate(MediaAssetBase):
    """Schema for creating media asset"""
    project_id: Optional[UUID] = None
    artist_id: Optional[UUID] = None


class MediaAssetUpdate(BaseModel):
    """Schema for updating media asset"""
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    metadata: Optional[dict] = None
    processing_notes: Optional[str] = None


class MediaAssetResponse(BaseModel):
    """Schema for media asset response"""
    id: UUID
    name: str
    slug: str
    original_filename: str
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    md5_hash: Optional[str] = None
    asset_type: str
    status: str
    
    # Media properties
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    frame_rate: Optional[float] = None
    bit_rate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    codec: Optional[str] = None
    
    # File paths
    thumbnail_path: Optional[str] = None
    preview_path: Optional[str] = None
    waveform_path: Optional[str] = None
    
    # Metadata
    metadata: Optional[dict] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    
    # Relationships
    project_id: Optional[UUID] = None
    artist_id: Optional[UUID] = None
    created_by_id: UUID
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MediaAssetListResponse(BaseModel):
    """Paginated list of media assets"""
    items: List[MediaAssetResponse]
    total: int
    limit: int
    offset: int


class UploadResponse(BaseModel):
    """Response for upload operation"""
    asset_id: str
    name: str
    status: str
    message: str


class TranscodingJobResponse(BaseModel):
    """Schema for transcoding job response"""
    id: UUID
    name: str
    asset_id: UUID
    target_format: str
    status: str
    progress: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class WaveformDataResponse(BaseModel):
    """Schema for waveform data"""
    peaks: List[float]
    duration: float
    samples_per_second: int


class AudioAnalysisResponse(BaseModel):
    """Schema for audio analysis results"""
    bpm: Optional[float] = None
    bpm_confidence: Optional[float] = None
    key: Optional[str] = None
    key_confidence: Optional[float] = None
    energy: Optional[float] = None
    valence: Optional[float] = None
    danceability: Optional[float] = None
    
    intro_start: Optional[float] = None
    intro_end: Optional[float] = None
    hook_start: Optional[float] = None
    hook_end: Optional[float] = None
    outro_start: Optional[float] = None
    outro_end: Optional[float] = None
    
    spectral_centroid: Optional[float] = None
    loudness: Optional[float] = None
    
    class Config:
        from_attributes = True


# Timeline schemas

class TimelineTrackResponse(BaseModel):
    """Schema for timeline track"""
    id: UUID
    name: str
    track_type: str
    order: int
    is_muted: bool
    is_solo: bool
    is_locked: bool
    volume: float
    opacity: float
    height: int
    
    class Config:
        from_attributes = True


class TimelineClipResponse(BaseModel):
    """Schema for timeline clip"""
    id: UUID
    asset_id: Optional[UUID] = None
    track_id: UUID
    timeline_start: float
    timeline_end: float
    source_start: float
    source_end: float
    name: Optional[str] = None
    
    # Visual properties
    x_position: float
    y_position: float
    scale: float
    rotation: float
    
    # Effects
    effects: Optional[List[dict]] = None
    filters: Optional[List[str]] = None
    
    # Transitions
    transition_in: Optional[str] = None
    transition_out: Optional[str] = None
    transition_duration: float
    
    class Config:
        from_attributes = True
    
    @property
    def duration(self) -> float:
        return self.timeline_end - self.timeline_start


class TimelineResponse(BaseModel):
    """Schema for timeline response"""
    id: UUID
    name: str
    description: Optional[str] = None
    duration: Optional[float] = None
    frame_rate: float
    resolution_width: int
    resolution_height: int
    aspect_ratio: str
    
    is_locked: bool
    is_published: bool
    
    project_id: Optional[UUID] = None
    created_by_id: UUID
    
    tracks: List[TimelineTrackResponse] = []
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TimelineCreate(BaseModel):
    """Schema for creating timeline"""
    name: str
    description: Optional[str] = None
    project_id: Optional[UUID] = None
    frame_rate: float = 30.0
    resolution_width: int = 1080
    resolution_height: int = 1920
    aspect_ratio: str = "9:16"


class TimelineUpdate(BaseModel):
    """Schema for updating timeline"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_locked: Optional[bool] = None
    is_published: Optional[bool] = None
    export_preset: Optional[str] = None
    export_settings: Optional[dict] = None


class TimelineClipCreate(BaseModel):
    """Schema for creating timeline clip"""
    track_id: UUID
    asset_id: UUID
    timeline_start: float
    timeline_end: float
    source_start: float = 0
    source_end: Optional[float] = None
    name: Optional[str] = None


class TimelineClipUpdate(BaseModel):
    """Schema for updating timeline clip"""
    timeline_start: Optional[float] = None
    timeline_end: Optional[float] = None
    source_start: Optional[float] = None
    source_end: Optional[float] = None
    name: Optional[str] = None
    x_position: Optional[float] = None
    y_position: Optional[float] = None
    scale: Optional[float] = None
    rotation: Optional[float] = None


# Export presets

class ExportPresetResponse(BaseModel):
    """Schema for export preset"""
    id: UUID
    name: str
    display_name: str
    platform: str
    width: int
    height: int
    frame_rate: float
    video_codec: str
    video_bitrate: Optional[str] = None
    audio_codec: str
    audio_bitrate: str
    audio_sample_rate: int
    
    ffmpeg_preset: str
    crf: int
    
    max_duration: Optional[int] = None
    max_file_size: Optional[int] = None
    requires_watermark: bool
    
    is_active: bool
    is_default: bool
    category: Optional[str] = None
    
    class Config:
        from_attributes = True


# Render job schemas

class RenderJobResponse(BaseModel):
    """Schema for render job"""
    id: UUID
    name: str
    job_type: str
    status: str
    priority: str
    
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    
    progress: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    worker_id: Optional[str] = None
    error_message: Optional[str] = None
    
    retry_count: int
    max_retries: int
    
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    
    project_id: Optional[UUID] = None
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class RenderJobCreate(BaseModel):
    """Schema for creating render job"""
    name: str
    job_type: str
    input_path: str
    output_path: Optional[str] = None
    parameters: Optional[dict] = None
    priority: str = "normal"
    project_id: Optional[UUID] = None


class RenderQueueStats(BaseModel):
    """Render queue statistics"""
    total: int
    queued: int
    processing: int
    completed: int
    failed: int
    cancelled: int
    avg_duration: float