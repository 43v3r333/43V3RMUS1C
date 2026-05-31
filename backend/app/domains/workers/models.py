"""
Worker Domain Models - Worker orchestration and telemetry
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class WorkerStatus(str, Enum):
    """Worker status"""
    ONLINE = "online"
    BUSY = "busy"
    IDLE = "idle"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class WorkerType(str, Enum):
    """Worker types"""
    MEDIA = "media"
    RENDER = "render"
    AUDIO = "audio"
    ANALYSIS = "analysis"
    TRANSCODE = "transcode"
    GENERAL = "general"


@dataclass
class WorkerMetrics:
    """Worker metrics snapshot"""
    worker_id: str
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: int
    memory_available_mb: int
    disk_used_mb: int
    disk_available_mb: int
    jobs_processed: int
    jobs_failed: int
    average_job_duration: float
    current_jobs: List[str] = field(default_factory=list)


@dataclass
class WorkerHealth:
    """Worker health status"""
    worker_id: str
    status: WorkerStatus
    last_heartbeat: datetime
    healthy: bool
    error_count: int
    uptime_seconds: int
    capabilities: List[str]


class Worker(BaseModel):
    """Worker model"""
    __tablename__ = "workers"
    
    worker_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    worker_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=WorkerStatus.OFFLINE.value, index=True)
    
    # Host info
    hostname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Capabilities
    capabilities: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    max_concurrent_jobs: Mapped[int] = mapped_column(Integer, default=1)
    
    # Heartbeat
    last_heartbeat: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    heartbeat_interval: Mapped[int] = mapped_column(Integer, default=30)
    
    # Stats
    total_jobs: Mapped[int] = mapped_column(Integer, default=0)
    completed_jobs: Mapped[int] = mapped_column(Integer, default=0)
    failed_jobs: Mapped[int] = mapped_column(Integer, default=0)
    avg_job_duration: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Error tracking
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Start time
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    @property
    def uptime(self) -> int:
        """Calculate uptime in seconds"""
        if self.started_at:
            return int((datetime.utcnow() - self.started_at).total_seconds())
        return 0
    
    @property
    def is_healthy(self) -> bool:
        """Check if worker is healthy"""
        return (
            self.status != WorkerStatus.ERROR and 
            self.error_count < 10 and
            self.last_heartbeat is not None and
            (datetime.utcnow() - self.last_heartbeat).total_seconds() < 120
        )


class WorkerMetric(BaseModel):
    """Worker metrics model for historical tracking"""
    __tablename__ = "worker_metrics"
    
    worker_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # CPU metrics
    cpu_percent: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Memory metrics
    memory_percent: Mapped[float] = mapped_column(Float, default=0.0)
    memory_used_mb: Mapped[int] = mapped_column(Integer, default=0)
    memory_available_mb: Mapped[int] = mapped_column(Integer, default=0)
    
    # Disk metrics
    disk_used_mb: Mapped[int] = mapped_column(Integer, default=0)
    disk_available_mb: Mapped[int] = mapped_column(Integer, default=0)
    
    # Job metrics
    jobs_processed: Mapped[int] = mapped_column(Integer, default=0)
    jobs_failed: Mapped[int] = mapped_column(Integer, default=0)
    current_jobs: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Network metrics (if available)
    network_rx_mb: Mapped[float] = mapped_column(Float, default=0.0)
    network_tx_mb: Mapped[float] = mapped_column(Float, default=0.0)


class WorkerEvent(BaseModel):
    """Worker event log model"""
    __tablename__ = "worker_events"
    
    worker_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), default="info")
    
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)
    
    job_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class ProcessingState(BaseModel):
    """Processing state model for resume capability"""
    __tablename__ = "processing_states"
    
    job_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    worker_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # State data
    state_type: Mapped[str] = mapped_column(String(50), nullable=False)
    state_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Progress
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    processed_items: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    @property
    def is_expired(self) -> bool:
        """Check if state has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False


class RuntimeLog(BaseModel):
    """Runtime log model"""
    __tablename__ = "runtime_logs"
    
    worker_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    log_level: Mapped[str] = mapped_column(String(20), default="info", index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Context
    job_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    task_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Extra data
    metadata_: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)