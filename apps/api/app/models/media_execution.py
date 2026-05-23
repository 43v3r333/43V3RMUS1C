"""
Media Execution models for the core media pipeline
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, DateTime, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class AssetStatus(str, enum.Enum):
    """Asset lifecycle status"""
    UPLOADING = "uploading"
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    ARCHIVED = "archived"


class AssetType(str, enum.Enum):
    """Media asset types"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"


class RenderJobStatus(str, enum.Enum):
    """Render job status states"""
    QUEUED = "queued"
    PROCESSING = "processing"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RenderJobPriority(str, enum.Enum):
    """Render job priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ExportPreset(str, enum.Enum):
    """Social media export presets"""
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM_REELS = "instagram_reels"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    CUSTOM = "custom"


class TimelineTrackType(str, enum.Enum):
    """Timeline track types"""
    VIDEO = "video"
    AUDIO = "audio"
    OVERLAY = "overlay"
    CAPTION = "caption"


class TranscodingStatus(str, enum.Enum):
    """Transcoding job status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class MediaAsset(BaseModel):
    """
    Enhanced media asset model for comprehensive asset management.
    Stores metadata for all media types with versioning support.
    """
    __tablename__ = "media_assets"
    
    # Basic identification
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, index=True)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(700), nullable=False)
    file_size = Column(Integer, nullable=True)  # bytes
    mime_type = Column(String(100), nullable=True, index=True)
    md5_hash = Column(String(32), nullable=True, index=True)  # Content fingerprint
    
    # Asset classification
    asset_type = Column(String(20), nullable=False, index=True)  # audio, video, image, document
    status = Column(String(20), default=AssetStatus.PENDING.value, index=True)
    
    # Media properties (extracted via ffprobe/analysis)
    duration = Column(Float, nullable=True)  # seconds
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    frame_rate = Column(Float, nullable=True)
    bit_rate = Column(Integer, nullable=True)
    sample_rate = Column(Integer, nullable=True)  # for audio
    channels = Column(Integer, nullable=True)  # for audio
    codec = Column(String(50), nullable=True)
    
    # Technical metadata
    metadata = Column(JSON, nullable=True)  # Full ffprobe output
    technical_specs = Column(JSON, nullable=True)  # Detailed specs
    
    # Thumbnail and preview
    thumbnail_path = Column(String(700), nullable=True)
    preview_path = Column(String(700), nullable=True)
    waveform_path = Column(String(700), nullable=True)
    
    # Versioning
    version = Column(Integer, default=1)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("media_assets.id"), nullable=True)
    
    # Organization
    tags = Column(JSON, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    
    # Ownership and project
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    artist_id = Column(UUID(as_uuid=True), ForeignKey("artists.id"), nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Processing metadata
    processing_notes = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="media_assets")
    artist = relationship("Artist", back_populates="media_assets")
    creator = relationship("User", back_populates="media_assets")
    parent = relationship("MediaAsset", remote_side="MediaAsset.id", backref="versions")
    transcoding_jobs = relationship("TranscodingJob", back_populates="asset", lazy="selectin")
    waveform_data = relationship("WaveformData", back_populates="asset", uselist=False, lazy="selectin")
    audio_analysis = relationship("AudioAnalysis", back_populates="asset", uselist=False, lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<MediaAsset(id={self.id}, name={self.name}, type={self.asset_type})>"


class TranscodingJob(BaseModel):
    """
    Transcoding job model for asset processing pipeline.
    Tracks the lifecycle of media format conversions.
    """
    __tablename__ = "transcoding_jobs"
    
    # Job identification
    name = Column(String(255), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("media_assets.id"), nullable=False)
    
    # Input/Output
    input_path = Column(String(700), nullable=False)
    output_path = Column(String(700), nullable=True)
    
    # Configuration
    target_format = Column(String(20), nullable=False)  # mp4, mp3, webm, etc.
    target_codec = Column(String(50), nullable=True)
    target_resolution = Column(String(20), nullable=True)  # 1080p, 720p, etc.
    target_bitrate = Column(String(20), nullable=True)  # 5M, 10M, etc.
    
    # Status and progress
    status = Column(String(20), default=TranscodingStatus.PENDING.value, index=True)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # seconds
    actual_duration = Column(Integer, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Worker
    worker_id = Column(String(100), nullable=True)
    
    # Results
    output_size = Column(Integer, nullable=True)
    output_codec = Column(String(50), nullable=True)
    
    # Relationships
    asset = relationship("MediaAsset", back_populates="transcoding_jobs")
    
    def __repr__(self) -> str:
        return f"<TranscodingJob(id={self.id}, name={self.name}, status={self.status})>"


class WaveformData(BaseModel):
    """
    Waveform data model for audio visualization.
    Stores pre-computed waveform peaks for real-time display.
    """
    __tablename__ = "waveform_data"
    
    asset_id = Column(UUID(as_uuid=True), ForeignKey("media_assets.id"), nullable=False, unique=True)
    
    # Waveform configuration
    sample_rate = Column(Integer, nullable=False)  # Samples per second of waveform
    samples_per_second = Column(Integer, default=100)  # Display resolution
    channel_mode = Column(String(20), default="stereo")  # stereo, mono, dual
    
    # Data storage (peaks as JSON array for fast loading)
    peaks_left = Column(JSON, nullable=True)  # Left channel peaks
    peaks_right = Column(JSON, nullable=True)  # Right channel peaks (for stereo)
    peaks_mono = Column(JSON, nullable=True)  # Combined peaks (for mono)
    
    # Statistics
    duration = Column(Float, nullable=True)
    peak_amplitude = Column(Float, nullable=True)
    rms_level = Column(Float, nullable=True)
    
    # Processing info
    processing_version = Column(String(20), default="1.0")
    
    # Relationships
    asset = relationship("MediaAsset", back_populates="waveform_data")
    
    def __repr__(self) -> str:
        return f"<WaveformData(asset_id={self.asset_id})>"


class AudioAnalysis(BaseModel):
    """
    Audio analysis model for music intelligence.
    Stores beat detection, BPM, key, and other audio features.
    """
    __tablename__ = "audio_analysis"
    
    asset_id = Column(UUID(as_uuid=True), ForeignKey("media_assets.id"), nullable=False, unique=True)
    
    # Tempo analysis
    bpm = Column(Float, nullable=True, index=True)
    bpm_confidence = Column(Float, nullable=True)
    
    # Beat tracking
    beats = Column(JSON, nullable=True)  # Beat timestamps in seconds
    beat_confidence = Column(Float, nullable=True)
    
    # Musical key
    key = Column(String(10), nullable=True, index=True)  # e.g., "C major", "A minor"
    key_confidence = Column(Float, nullable=True)
    
    # Energy and mood
    energy = Column(Float, nullable=True)  # 0.0 to 1.0
    valence = Column(Float, nullable=True)  # 0.0 to 1.0 (positive/negative)
    danceability = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Time markers
    intro_start = Column(Float, nullable=True)
    intro_end = Column(Float, nullable=True)
    hook_start = Column(Float, nullable=True)
    hook_end = Column(Float, nullable=True)
    outro_start = Column(Float, nullable=True)
    outro_end = Column(Float, nullable=True)
    
    # Silence detection
    silent_regions = Column(JSON, nullable=True)  # List of (start, end) tuples
    
    # Spectral features
    spectral_centroid = Column(Float, nullable=True)
    spectral_rolloff = Column(Float, nullable=True)
    
    # Loudness
    loudness = Column(Float, nullable=True)  # LUFS
    dynamic_range = Column(Float, nullable=True)
    
    # Analysis metadata
    analysis_version = Column(String(20), default="1.0")
    confidence_score = Column(Float, nullable=True)
    
    # Relationships
    asset = relationship("MediaAsset", back_populates="audio_analysis")
    
    def __repr__(self) -> str:
        return f"<AudioAnalysis(asset_id={self.asset_id}, bpm={self.bpm})>"


class Timeline(BaseModel):
    """
    Timeline model for video composition and editing.
    Represents a sequence of media clips with timing information.
    """
    __tablename__ = "timelines"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Timeline properties
    duration = Column(Float, nullable=True)  # Total duration in seconds
    frame_rate = Column(Float, default=30.0)  # Frames per second
    resolution_width = Column(Integer, default=1080)
    resolution_height = Column(Integer, default=1920)
    
    # Configuration
    aspect_ratio = Column(String(20), default="9:16")  # 9:16 for social, 16:9 for YouTube
    background_color = Column(String(7), default="#000000")  # Hex color
    
    # Status
    is_locked = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)
    
    # Export settings
    export_preset = Column(String(50), nullable=True)
    export_settings = Column(JSON, nullable=True)
    
    # Project link
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="timelines")
    creator = relationship("User")
    tracks = relationship("TimelineTrack", back_populates="timeline", lazy="selectin", order_by="TimelineTrack.order")
    
    def __repr__(self) -> str:
        return f"<Timeline(id={self.id}, name={self.name})>"


class TimelineTrack(BaseModel):
    """
    Timeline track model for organizing media clips.
    Represents a horizontal lane in the timeline.
    """
    __tablename__ = "timeline_tracks"
    
    timeline_id = Column(UUID(as_uuid=True), ForeignKey("timelines.id"), nullable=False)
    name = Column(String(255), nullable=False)
    
    # Track configuration
    track_type = Column(String(20), nullable=False)  # video, audio, overlay, caption
    order = Column(Integer, nullable=False, default=0)
    
    # Track properties
    is_muted = Column(Boolean, default=False)
    is_solo = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    volume = Column(Float, default=1.0)  # 0.0 to 2.0
    opacity = Column(Float, default=1.0)  # 0.0 to 1.0
    
    # Visual settings
    height = Column(Integer, default=60)  # Track height in pixels
    
    # Relationships
    timeline = relationship("Timeline", back_populates="tracks")
    clips = relationship("TimelineClip", back_populates="track", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<TimelineTrack(id={self.id}, name={self.name})>"


class TimelineClip(BaseModel):
    """
    Timeline clip model for individual media segments.
    Represents a portion of media placed on the timeline.
    """
    __tablename__ = "timeline_clips"
    
    track_id = Column(UUID(as_uuid=True), ForeignKey("timeline_tracks.id"), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("media_assets.id"), nullable=True)
    
    # Timing (all in seconds)
    timeline_start = Column(Float, nullable=False, default=0)
    timeline_end = Column(Float, nullable=False)
    source_start = Column(Float, nullable=False, default=0)  # In-point in source
    source_end = Column(Float, nullable=False)  # Out-point in source
    
    # Clip properties
    name = Column(String(255), nullable=True)
    
    # Visual (for video clips)
    x_position = Column(Float, default=0)
    y_position = Column(Float, default=0)
    scale = Column(Float, default=1.0)
    rotation = Column(Float, default=0)
    
    # Effects
    effects = Column(JSON, nullable=True)  # List of applied effects
    filters = Column(JSON, nullable=True)  # FFmpeg filters
    
    # Transitions
    transition_in = Column(String(50), nullable=True)  # Transition type at start
    transition_out = Column(String(50), nullable=True)  # Transition type at end
    transition_duration = Column(Float, default=0.5)
    
    # Relationships
    track = relationship("TimelineTrack", back_populates="clips")
    asset = relationship("MediaAsset")
    
    def __repr__(self) -> str:
        return f"<TimelineClip(id={self.id}, start={self.timeline_start})>"
    
    @property
    def duration(self) -> float:
        return self.timeline_end - self.timeline_start


class ExportPresetModel(BaseModel):
    """
    Export preset model for social media export configurations.
    Stores platform-specific export settings.
    """
    __tablename__ = "export_presets"
    
    name = Column(String(255), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False, index=True)  # tiktok, youtube, instagram, etc.
    
    # Video settings
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    frame_rate = Column(Float, default=30.0)
    video_codec = Column(String(50), default="libx264")
    video_bitrate = Column(String(20), nullable=True)  # e.g., "8M"
    
    # Audio settings
    audio_codec = Column(String(50), default="aac")
    audio_bitrate = Column(String(20), default="192k")
    audio_sample_rate = Column(Integer, default=44100)
    
    # FFmpeg parameters
    ffmpeg_preset = Column(String(20), default="medium")  # ultrafast to slow
    crf = Column(Integer, default=23)  # Constant Rate Factor
    
    # Platform specific
    max_duration = Column(Integer, nullable=True)  # seconds
    max_file_size = Column(Integer, nullable=True)  # bytes
    requires_watermark = Column(Boolean, default=False)
    
    # Custom arguments
    additional_args = Column(JSON, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Organization
    category = Column(String(50), nullable=True, index=True)
    tags = Column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f"<ExportPreset(id={self.id}, name={self.name}, platform={self.platform})>"


class RenderOutput(BaseModel):
    """
    Render output model for tracking completed renders.
    Stores output file information and metadata.
    """
    __tablename__ = "render_outputs"
    
    # Job reference
    render_job_id = Column(UUID(as_uuid=True), ForeignKey("render_jobs.id"), nullable=False)
    
    # Output file
    name = Column(String(255), nullable=False)
    output_path = Column(String(700), nullable=False)
    output_url = Column(String(700), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Format details
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration = Column(Float, nullable=True)
    codec = Column(String(50), nullable=True)
    bit_rate = Column(Integer, nullable=True)
    
    # Thumbnail
    thumbnail_path = Column(String(700), nullable=True)
    preview_path = Column(String(700), nullable=True)
    
    # Export info
    export_preset = Column(String(50), nullable=True)
    platform = Column(String(50), nullable=True)
    
    # Status
    is_primary = Column(Boolean, default=False)  # Primary output vs. alternate
    status = Column(String(20), default="ready")  # ready, uploading, uploaded, failed
    
    # Relationships
    render_job = relationship("RenderJob")
    
    def __repr__(self) -> str:
        return f"<RenderOutput(id={self.id}, name={self.name})>"


# Update existing models with new relationships
# This is done via imports in the models/__init__.py