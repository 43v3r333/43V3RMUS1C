"""
Rendering Domain Models - Distributed render graph orchestration
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, JSON, Text, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class RenderStatus(str, Enum):
    """Render job status"""
    QUEUED = "queued"
    PREPARING = "preparing"
    RENDERING = "rendering"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class RenderPriority(str, Enum):
    """Render job priority"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class RenderNodeType(str, Enum):
    """Render node operation types"""
    SOURCE = "source"
    TRANSFORM = "transform"
    EFFECT = "effect"
    COMPOSITE = "composite"
    EXPORT = "export"


@dataclass
class RenderPort:
    """Input/output port for render node"""
    name: str
    data_type: str
    default_value: Any = None
    required: bool = True


@dataclass
class RenderNodeConfig:
    """Configuration for a render node"""
    node_type: RenderNodeType
    operation: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    inputs: List[RenderPort] = field(default_factory=list)
    outputs: List[RenderPort] = field(default_factory=list)


class RenderGraph(BaseModel):
    """Render graph model"""
    __tablename__ = "render_graphs"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Graph structure (nodes and edges as JSON)
    nodes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    edges: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=False)
    
    # Render settings
    output_format: Mapped[str] = mapped_column(String(20), default="mp4")
    output_resolution: Mapped[str] = mapped_column(String(20), default="1920x1080")
    frame_rate: Mapped[float] = mapped_column(Float, default=30.0)
    bitrate: Mapped[int] = mapped_column(Integer, default=10_000_000)
    
    # Presets
    preset_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    preset_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Versioning
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_graph_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("render_graphs.id"), 
        nullable=True
    )


class RenderNode(BaseModel):
    """Render node in a graph"""
    __tablename__ = "render_nodes"
    
    graph_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("render_graphs.id"), 
        nullable=False,
        index=True
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    operation: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Position in graph (for UI)
    position_x: Mapped[float] = mapped_column(Float, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Configuration
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    input_ports: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    output_ports: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Execution state
    dependencies: Mapped[Optional[List[UUID]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=RenderStatus.QUEUED.value)
    
    # Execution metrics
    execution_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    memory_usage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class RenderJob(BaseModel):
    """Render job model"""
    __tablename__ = "render_jobs"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    job_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Graph reference
    graph_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("render_graphs.id"), 
        nullable=True
    )
    timeline_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("timelines.id"), 
        nullable=True,
        index=True
    )
    
    # Status and priority
    status: Mapped[str] = mapped_column(String(50), default=RenderStatus.QUEUED.value, index=True)
    priority: Mapped[str] = mapped_column(String(20), default=RenderPriority.NORMAL.value, index=True)
    
    # Progress tracking
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    total_frames: Mapped[int] = mapped_column(Integer, default=0)
    processed_frames: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    queued_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Worker assignment
    worker_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    worker_node: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Results
    output_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    output_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    
    # Render settings overrides
    settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    graph: Mapped[Optional[RenderGraph]] = relationship("RenderGraph")
    timeline: Mapped[Optional["Timeline"]] = relationship("Timeline")
    
    # Event trace
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class RenderPreset(BaseModel):
    """Render preset model"""
    __tablename__ = "render_presets"
    
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Format settings
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    codec: Mapped[str] = mapped_column(String(50), nullable=False)
    container: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Quality settings
    resolution: Mapped[str] = mapped_column(String(20), nullable=False)
    frame_rate: Mapped[float] = mapped_column(Float, nullable=False)
    bitrate: Mapped[int] = mapped_column(Integer, nullable=True)
    bitrate_mode: Mapped[str] = mapped_column(String(20), default="auto")
    
    # Audio settings
    audio_codec: Mapped[str] = mapped_column(String(50), default="aac")
    audio_bitrate: Mapped[int] = mapped_column(Integer, default=192_000)
    audio_sample_rate: Mapped[int] = mapped_column(Integer, default=48000)
    
    # Extra parameters
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # UI metadata
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False)
    
    usage_count: Mapped[int] = mapped_column(Integer, default=0)


# Import for relationship
from .timelines.models import Timeline