"""
Render Domain Models
"""
import enum
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, Session

from app.models.base import BaseModel


class RenderStatus(str, enum.Enum):
    """Render job status states"""
    QUEUED = "queued"
    PROCESSING = "processing"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class RenderPriority(str, enum.Enum):
    """Render job priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ExportPlatform(str, enum.Enum):
    """Social media export platforms"""
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM_REELS = "instagram_reels"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    CUSTOM = "custom"


class WorkerStatus(str, enum.Enum):
    """Render worker status"""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


class RenderJob(BaseModel):
    """
    Render job model for distributed media rendering.
    Supports prioritization, retries, and progress tracking.
    """
    __tablename__ = "render_jobs"
    
    # Identification
    name = Column(String(255), nullable=False, index=True)
    job_type = Column(String(50), nullable=False, index=True)
    
    # Status and priority
    status = Column(String(20), default=RenderStatus.QUEUED.value, index=True)
    priority = Column(String(20), default=RenderPriority.NORMAL.value, index=True)
    
    # File paths
    input_path = Column(String(700), nullable=True)
    output_path = Column(String(700), nullable=True)
    
    # Processing parameters
    parameters = Column(JSON, nullable=True)
    preset_id = Column(PGUUID(as_uuid=True), ForeignKey("export_presets.id"), nullable=True)
    
    # Progress tracking
    progress = Column(Float, default=0.0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Worker info
    worker_id = Column(String(100), nullable=True)
    estimated_duration = Column(Integer, nullable=True)
    actual_duration = Column(Integer, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Render graph
    render_graph = Column(JSON, nullable=True)
    dependencies = Column(JSON, nullable=True)
    
    # Output info
    output_size = Column(Integer, nullable=True)
    output_format = Column(String(50), nullable=True)
    
    # Relationships
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    timeline_id = Column(PGUUID(as_uuid=True), ForeignKey("timelines.id"), nullable=True)
    
    outputs = relationship("RenderOutput", back_populates="render_job", lazy="selectin")
    preset = relationship("ExportPreset", back_populates="jobs")
    project = relationship("Project", back_populates="render_jobs")
    
    def __repr__(self) -> str:
        return f"<RenderJob(id={self.id}, name={self.name}, status={self.status})>"
    
    @property
    def is_active(self) -> bool:
        return self.status in [RenderStatus.QUEUED.value, RenderStatus.PROCESSING.value, RenderStatus.RENDERING.value]
    
    @property
    def can_retry(self) -> bool:
        return self.status == RenderStatus.FAILED.value and self.retry_count < self.max_retries


class RenderOutput(BaseModel):
    """
    Render output model for tracking completed renders.
    """
    __tablename__ = "render_outputs"
    
    render_job_id = Column(PGUUID(as_uuid=True), ForeignKey("render_jobs.id"), nullable=False)
    
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
    is_primary = Column(Boolean, default=False)
    status = Column(String(20), default="ready")
    
    render_job = relationship("RenderJob", back_populates="outputs")
    
    def __repr__(self) -> str:
        return f"<RenderOutput(id={self.id}, name={self.name})>"


class ExportPreset(BaseModel):
    """
    Export preset model for platform-specific exports.
    """
    __tablename__ = "export_presets"
    
    name = Column(String(255), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False, index=True)
    
    # Video settings
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    frame_rate = Column(Float, default=30.0)
    video_codec = Column(String(50), default="libx264")
    video_bitrate = Column(String(20), nullable=True)
    
    # Audio settings
    audio_codec = Column(String(50), default="aac")
    audio_bitrate = Column(String(20), default="192k")
    audio_sample_rate = Column(Integer, default=44100)
    
    # FFmpeg settings
    ffmpeg_preset = Column(String(20), default="medium")
    crf = Column(Integer, default=23)
    
    # Platform limits
    max_duration = Column(Integer, nullable=True)
    max_file_size = Column(Integer, nullable=True)
    requires_watermark = Column(Boolean, default=False)
    
    # Custom args
    additional_args = Column(JSON, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Organization
    category = Column(String(50), nullable=True, index=True)
    tags = Column(JSON, nullable=True)
    
    jobs = relationship("RenderJob", back_populates="preset")
    
    def __repr__(self) -> str:
        return f"<ExportPreset(id={self.id}, name={self.name}, platform={self.platform})>"


class RenderWorker(BaseModel):
    """
    Render worker model for distributed rendering.
    Tracks worker health and capacity.
    """
    __tablename__ = "render_workers"
    
    worker_id = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    
    # Status
    status = Column(String(20), default=WorkerStatus.IDLE.value, index=True)
    
    # Capabilities
    capabilities = Column(JSON, nullable=True)
    max_concurrent_jobs = Column(Integer, default=1)
    current_jobs = Column(Integer, default=0)
    
    # Resource usage
    cpu_usage = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    gpu_available = Column(Boolean, default=False)
    
    # Health
    last_heartbeat = Column(DateTime, nullable=True)
    jobs_completed = Column(Integer, default=0)
    jobs_failed = Column(Integer, default=0)
    
    # Stats
    avg_job_duration = Column(Integer, nullable=True)
    
    def __repr__(self) -> str:
        return f"<RenderWorker(id={self.worker_id}, status={self.status})>"
    
    @property
    def is_available(self) -> bool:
        return self.status == WorkerStatus.IDLE.value and self.current_jobs < self.max_concurrent_jobs


class RenderJobRepository:
    """Repository for render job data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, job_id: UUID) -> Optional[RenderJob]:
        return self.db.query(RenderJob).filter(RenderJob.id == job_id).first()
    
    def get_next_job(self) -> Optional[RenderJob]:
        """Get highest priority queued job"""
        return (
            self.db.query(RenderJob)
            .filter(RenderJob.status == RenderStatus.QUEUED.value)
            .order_by(RenderJob.priority.desc(), RenderJob.created_at.asc())
            .first()
        )
    
    def list_jobs(
        self,
        status: Optional[str] = None,
        job_type: Optional[str] = None,
        project_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[RenderJob]:
        query = self.db.query(RenderJob)
        
        if status:
            query = query.filter(RenderJob.status == status)
        if job_type:
            query = query.filter(RenderJob.job_type == job_type)
        if project_id:
            query = query.filter(RenderJob.project_id == project_id)
        
        return query.order_by(
            RenderJob.priority.desc(),
            RenderJob.created_at.asc()
        ).offset(offset).limit(limit).all()
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        jobs = self.db.query(RenderJob).all()
        
        return {
            "total": len(jobs),
            "queued": sum(1 for j in jobs if j.status == RenderStatus.QUEUED.value),
            "processing": sum(1 for j in jobs if j.status == RenderStatus.PROCESSING.value),
            "rendering": sum(1 for j in jobs if j.status == RenderStatus.RENDERING.value),
            "completed": sum(1 for j in jobs if j.status == RenderStatus.COMPLETED.value),
            "failed": sum(1 for j in jobs if j.status == RenderStatus.FAILED.value),
            "cancelled": sum(1 for j in jobs if j.status == RenderStatus.CANCELLED.value),
        }
    
    def create(self, job: RenderJob) -> RenderJob:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def update(self, job_id: UUID, updates: dict) -> RenderJob:
        job = self.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        for key, value in updates.items():
            if hasattr(job, key):
                setattr(job, key, value)
        
        job.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(job)
        return job


class ExportPresetRepository:
    """Repository for export preset data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, preset_id: UUID) -> Optional[ExportPreset]:
        return self.db.query(ExportPreset).filter(ExportPreset.id == preset_id).first()
    
    def get_by_platform(self, platform: str) -> Optional[ExportPreset]:
        return (
            self.db.query(ExportPreset)
            .filter(
                ExportPreset.platform == platform,
                ExportPreset.is_active == True,
                ExportPreset.is_default == True
            )
            .first()
        )
    
    def list_presets(
        self,
        platform: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[ExportPreset]:
        query = self.db.query(ExportPreset).filter(ExportPreset.is_active == True)
        
        if platform:
            query = query.filter(ExportPreset.platform == platform)
        if category:
            query = query.filter(ExportPreset.category == category)
        
        return query.all()
    
    def create(self, preset: ExportPreset) -> ExportPreset:
        self.db.add(preset)
        self.db.commit()
        self.db.refresh(preset)
        return preset