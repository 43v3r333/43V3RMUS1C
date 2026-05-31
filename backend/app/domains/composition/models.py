"""
Composition Domain Models - Cinematic composition architecture
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum
from dataclasses import dataclass, field

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class CompositionStatus(str, Enum):
    """Composition status"""
    DRAFT = "draft"
    COMPOSING = "composing"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


class SceneType(str, Enum):
    """Scene types"""
    INTRO = "intro"
    VERSE = "verse"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    OUTRO = "outro"
    TRANSITION = "transition"
    INTERLUDE = "interlude"


class TransitionType(str, Enum):
    """Transition types"""
    CUT = "cut"
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE = "wipe"
    ZOOM = "zoom"
    SLIDE = "slide"


@dataclass
class TimingPosition:
    """Timing position in composition"""
    start_time: float  # seconds
    end_time: float  # seconds
    duration: float  # seconds


@dataclass
class BeatInfo:
    """Beat information for alignment"""
    timestamp: float
    strength: float  # 0-1
    beat_type: str  # downbeat, upbeat, accent


@dataclass
class TransitionConfig:
    """Transition configuration"""
    type: TransitionType
    duration: float  # seconds
    easing: str = "ease-in-out"
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClipReference:
    """Reference to a media clip"""
    clip_id: str
    start_time: float  # in source
    duration: float
    effects: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class OverlayElement:
    """Overlay element configuration"""
    element_type: str  # text, image, shape
    content: str
    position_x: float
    position_y: float
    width: float
    height: float
    opacity: float = 1.0
    effects: List[Dict[str, Any]] = field(default_factory=list)


class CompositionGraph(BaseModel):
    """Composition graph model - defines cinematic composition structure"""
    __tablename__ = "composition_graphs"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Structure
    scenes: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=False)
    clips: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=False)
    transitions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    overlays: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Configuration
    frame_rate: Mapped[float] = mapped_column(Float, default=30.0)
    resolution_width: Mapped[int] = mapped_column(Integer, default=1920)
    resolution_height: Mapped[int] = mapped_column(Integer, default=1080)
    
    # Timing
    total_duration: Mapped[float] = mapped_column(Float, default=0.0)
    tempo: Mapped[float] = mapped_column(Float, default=120.0)
    
    # Audio
    audio_tracks: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    background_music: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=CompositionStatus.DRAFT.value, index=True)
    
    # Metadata
    genre: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    mood: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    style: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Usage
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    project_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)


class CompositionScene(BaseModel):
    """Composition scene model - individual scene in composition"""
    __tablename__ = "composition_scenes"
    
    graph_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("composition_graphs.id"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scene_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Timing
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Beat alignment
    start_beat: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    end_beat: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    beat_markers: Mapped[Optional[List[Dict[str, float]]]] = mapped_column(JSON, nullable=True)
    
    # Configuration
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Order
    order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)


class CompositionClip(BaseModel):
    """Composition clip model - media clip in composition"""
    __tablename__ = "composition_clips"
    
    graph_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("composition_graphs.id"), nullable=False, index=True)
    scene_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("composition_scenes.id"), nullable=True, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    clip_type: Mapped[str] = mapped_column(String(20), nullable=False)  # video, audio, image
    
    # Source reference
    source_asset_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    source_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timing in composition
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Source timing
    source_start: Mapped[float] = mapped_column(Float, default=0.0)
    source_end: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Position and scale
    position_x: Mapped[float] = mapped_column(Float, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, default=0.0)
    width: Mapped[float] = mapped_column(Float, nullable=True)
    height: Mapped[float] = mapped_column(Float, nullable=True)
    scale: Mapped[float] = mapped_column(Float, default=1.0)
    rotation: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Opacity and effects
    opacity: Mapped[float] = mapped_column(Float, default=1.0)
    effects: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Track
    track_index: Mapped[int] = mapped_column(Integer, default=0)
    
    # Order within scene
    order: Mapped[int] = mapped_column(Integer, default=0)


class CompositionTransition(BaseModel):
    """Composition transition model - transitions between scenes/clips"""
    __tablename__ = "composition_transitions"
    
    graph_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("composition_graphs.id"), nullable=False, index=True)
    
    # Transition endpoints
    from_scene_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    to_scene_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    from_clip_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    to_clip_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    # Transition config
    transition_type: Mapped[str] = mapped_column(String(20), nullable=False)
    duration: Mapped[float] = mapped_column(Float, default=0.5)
    easing: Mapped[str] = mapped_column(String(50), default="ease-in-out")
    
    # Parameters
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)


class CompositionOverlay(BaseModel):
    """Composition overlay model - text/graphics overlays"""
    __tablename__ = "composition_overlays"
    
    graph_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("composition_graphs.id"), nullable=False, index=True)
    scene_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    overlay_type: Mapped[str] = mapped_column(String(20), nullable=False)  # text, image, shape
    
    # Content
    content: Mapped[str] = mapped_column(Text, nullable=True)
    source_asset_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Position and size
    position_x: Mapped[float] = mapped_column(Float, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, default=0.0)
    width: Mapped[float] = mapped_column(Float, nullable=True)
    height: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Styling
    font_family: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    font_size: Mapped[float] = mapped_column(Float, nullable=True)
    font_color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    text_align: Mapped[str] = mapped_column(String(20), default="center")
    
    # Timing
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Effects
    opacity: Mapped[float] = mapped_column(Float, default=1.0)
    effects: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Z-index
    z_index: Mapped[int] = mapped_column(Integer, default=0)


class CompositionExecution(BaseModel):
    """Composition execution model - tracks render jobs"""
    __tablename__ = "composition_executions"
    
    graph_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("composition_graphs.id"), nullable=False, index=True)
    
    # Execution info
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    
    # Output
    output_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    output_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Format
    format: Mapped[str] = mapped_column(String(20), default="mp4")
    quality: Mapped[str] = mapped_column(String(20), default="high")
    codec: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Progress
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    current_scene: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_scenes: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    queued_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Worker
    worker_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)