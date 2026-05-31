"""
Timeline Domain Models - Professional timeline architecture
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, JSON, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class TimelineStatus(str, Enum):
    """Timeline status"""
    DRAFT = "draft"
    EDITING = "editing"
    RENDERING = "rendering"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TrackType(str, Enum):
    """Track types"""
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    EFFECT = "effect"
    CAPTION = "caption"


class TransitionType(str, Enum):
    """Transition types between clips"""
    CUT = "cut"
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE = "wipe"
    SLIDE = "slide"
    ZOOM = "zoom"


@dataclass
class TimeRange:
    """Time range with start and duration"""
    start: float = 0.0
    duration: float = 0.0
    
    @property
    def end(self) -> float:
        return self.start + self.duration
    
    def overlaps(self, other: "TimeRange") -> bool:
        """Check if two ranges overlap"""
        return self.start < other.end and other.start < self.end
    
    def contains(self, time: float) -> bool:
        """Check if time is within range"""
        return self.start <= time < self.end


@dataclass
class ClipData:
    """Clip data structure for API"""
    id: UUID
    track_id: UUID
    name: str
    source_asset_id: Optional[UUID]
    source_start: float
    source_end: float
    timeline_start: float
    timeline_end: float
    duration: float
    gain: float = 1.0
    pan: float = 0.0
    opacity: float = 1.0
    speed: float = 1.0
    effects: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TransitionData:
    """Transition data structure"""
    type: TransitionType
    duration: float
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MarkerData:
    """Timeline marker data"""
    id: UUID
    name: str
    time: float
    color: str = "#FFFF00"
    description: Optional[str] = None


@dataclass
class TimelineComposition:
    """Complete timeline composition"""
    id: UUID
    name: str
    duration: float
    frame_rate: float
    resolution: Tuple[int, int]
    tracks: List["TrackData"] = field(default_factory=list)
    markers: List[MarkerData] = field(default_factory=list)


@dataclass
class TrackData:
    """Track data structure"""
    id: UUID
    name: str
    track_type: TrackType
    order: int
    muted: bool = False
    solo: bool = False
    locked: bool = False
    volume: float = 1.0
    clips: List[ClipData] = field(default_factory=list)


class Timeline(BaseModel):
    """Timeline model"""
    __tablename__ = "timelines"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=TimelineStatus.DRAFT.value, index=True)
    
    # Project reference
    project_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("projects.id"), 
        nullable=True,
        index=True
    )
    
    # Timeline settings
    duration: Mapped[float] = mapped_column(Float, default=0.0)
    frame_rate: Mapped[float] = mapped_column(Float, default=30.0)
    resolution_width: Mapped[int] = mapped_column(Integer, default=1920)
    resolution_height: Mapped[int] = mapped_column(Integer, default=1080)
    sample_rate: Mapped[int] = mapped_column(Integer, default=48000)
    
    # Render settings
    output_format: Mapped[str] = mapped_column(String(20), default="mp4")
    output_codec: Mapped[str] = mapped_column(String(50), default="h264")
    output_bitrate: Mapped[str] = mapped_column(String(20), default="10M")
    
    # Timeline data (clips, markers, etc.)
    timeline_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    meta_info: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)
    
    # Relationships
    tracks: Mapped[List["TimelineTrack"]] = relationship(
        "TimelineTrack", 
        back_populates="timeline",
        cascade="all, delete-orphan",
        order_by="TimelineTrack.order"
    )
    markers: Mapped[List["TimelineMarker"]] = relationship(
        "TimelineMarker",
        back_populates="timeline",
        cascade="all, delete-orphan"
    )


class TimelineTrack(BaseModel):
    """Timeline track model"""
    __tablename__ = "timeline_tracks"
    
    timeline_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("timelines.id"), 
        nullable=False,
        index=True
    )
    timeline: Mapped[Timeline] = relationship("Timeline", back_populates="tracks")
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    track_type: Mapped[str] = mapped_column(String(50), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)
    
    muted: Mapped[bool] = mapped_column(Boolean, default=False)
    solo: Mapped[bool] = mapped_column(Boolean, default=False)
    locked: Mapped[bool] = mapped_column(Boolean, default=False)
    volume: Mapped[float] = mapped_column(Float, default=1.0)
    pan: Mapped[float] = mapped_column(Float, default=0.0)
    height: Mapped[int] = mapped_column(Integer, default=60)  # Pixel height
    
    # Relationship
    clips: Mapped[List["TimelineClip"]] = relationship(
        "TimelineClip",
        back_populates="track",
        cascade="all, delete-orphan"
    )


class TimelineClip(BaseModel):
    """Timeline clip model"""
    __tablename__ = "timeline_clips"
    
    track_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("timeline_tracks.id"), 
        nullable=False,
        index=True
    )
    track: Mapped[TimelineTrack] = relationship("TimelineTrack", back_populates="clips")
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Source reference
    source_asset_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("media_assets.id"), 
        nullable=True
    )
    
    # Timing
    source_start: Mapped[float] = mapped_column(Float, default=0.0)
    source_end: Mapped[float] = mapped_column(Float, default=0.0)
    timeline_start: Mapped[float] = mapped_column(Float, default=0.0)
    duration: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Properties
    gain: Mapped[float] = mapped_column(Float, default=1.0)
    pan: Mapped[float] = mapped_column(Float, default=0.0)
    opacity: Mapped[float] = mapped_column(Float, default=1.0)
    speed: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Effects
    effects: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Transitions
    transition_in: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    transition_out: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)


class TimelineMarker(BaseModel):
    """Timeline marker model"""
    __tablename__ = "timeline_markers"
    
    timeline_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("timelines.id"), 
        nullable=False,
        index=True
    )
    timeline: Mapped[Timeline] = relationship("Timeline", back_populates="markers")
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    time: Mapped[float] = mapped_column(Float, nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#FFFF00")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


# Import for relationship
from ...models.media import Project
from typing import List