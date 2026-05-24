"""
Timeline Domain Models
"""
import enum
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, Session

from app.models.base import BaseModel


class TimelineStatus(str, enum.Enum):
    """Timeline status"""
    DRAFT = "draft"
    EDITING = "editing"
    RENDERING = "rendering"
    COMPLETED = "completed"
    PUBLISHED = "published"


class TrackType(str, enum.Enum):
    """Track type classification"""
    VIDEO = "video"
    AUDIO = "audio"
    OVERLAY = "overlay"
    CAPTION = "caption"


class TransitionType(str, enum.Enum):
    """Transition types for clip connections"""
    NONE = "none"
    CUT = "cut"
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE = "wipe"
    SLIDE = "slide"


class Timeline(BaseModel):
    """
    Timeline model for video composition.
    Contains tracks with clips for multi-layer editing.
    """
    __tablename__ = "timelines"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Timeline properties
    duration = Column(Float, nullable=True)
    frame_rate = Column(Float, default=30.0)
    resolution_width = Column(Integer, default=1080)
    resolution_height = Column(Integer, default=1920)
    
    # Configuration
    aspect_ratio = Column(String(20), default="9:16")
    background_color = Column(String(7), default="#000000")
    
    # Status
    status = Column(String(20), default=TimelineStatus.DRAFT.value, index=True)
    is_locked = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)
    
    # Export settings
    export_preset = Column(String(50), nullable=True)
    export_settings = Column(JSON, nullable=True)
    
    # Relationships
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    created_by_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="timelines")
    tracks = relationship(
        "TimelineTrack",
        back_populates="timeline",
        lazy="selectin",
        order_by="TimelineTrack.order",
        cascade="all, delete-orphan"
    )
    creator = relationship("User")
    
    def __repr__(self) -> str:
        return f"<Timeline(id={self.id}, name={self.name}, duration={self.duration})>"
    
    @property
    def video_tracks(self) -> List["TimelineTrack"]:
        return [t for t in self.tracks if t.track_type == TrackType.VIDEO.value]
    
    @property
    def audio_tracks(self) -> List["TimelineTrack"]:
        return [t for t in self.tracks if t.track_type == TrackType.AUDIO.value]


class TimelineTrack(BaseModel):
    """
    Timeline track for organizing clips.
    Represents a horizontal lane in the timeline.
    """
    __tablename__ = "timeline_tracks"
    
    timeline_id = Column(PGUUID(as_uuid=True), ForeignKey("timelines.id"), nullable=False)
    name = Column(String(255), nullable=False)
    
    # Track configuration
    track_type = Column(String(20), nullable=False)
    order = Column(Integer, nullable=False, default=0)
    
    # Track properties
    is_muted = Column(Boolean, default=False)
    is_solo = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    volume = Column(Float, default=1.0)
    opacity = Column(Float, default=1.0)
    height = Column(Integer, default=60)
    
    # Visual settings
    color = Column(String(7), nullable=True)
    
    # Relationships
    timeline = relationship("Timeline", back_populates="tracks")
    clips = relationship(
        "TimelineClip",
        back_populates="track",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<TimelineTrack(id={self.id}, name={self.name}, type={self.track_type})>"
    
    @property
    def clip_count(self) -> int:
        return len(self.clips)
    
    @property
    def duration(self) -> float:
        if not self.clips:
            return 0.0
        return max(clip.timeline_end for clip in self.clips)


class TimelineClip(BaseModel):
    """
    Timeline clip for individual media segments.
    Represents a portion of media placed on the timeline.
    """
    __tablename__ = "timeline_clips"
    
    track_id = Column(PGUUID(as_uuid=True), ForeignKey("timeline_tracks.id"), nullable=False)
    asset_id = Column(PGUUID(as_uuid=True), ForeignKey("media_assets.id"), nullable=True)
    
    # Timing (all in seconds)
    timeline_start = Column(Float, nullable=False, default=0)
    timeline_end = Column(Float, nullable=False)
    source_start = Column(Float, nullable=False, default=0)
    source_end = Column(Float, nullable=False)
    
    # Clip properties
    name = Column(String(255), nullable=True)
    
    # Visual properties (for video clips)
    x_position = Column(Float, default=0)
    y_position = Column(Float, default=0)
    scale = Column(Float, default=1.0)
    rotation = Column(Float, default=0)
    
    # Effects
    effects = Column(JSON, nullable=True)
    filters = Column(JSON, nullable=True)
    
    # Transitions
    transition_in = Column(String(50), nullable=True)
    transition_out = Column(String(50), nullable=True)
    transition_duration = Column(Float, default=0.5)
    
    # Volume/Audio
    volume = Column(Float, default=1.0)
    
    # Relationships
    track = relationship("TimelineTrack", back_populates="clips")
    asset = relationship("MediaAsset")
    
    def __repr__(self) -> str:
        return f"<TimelineClip(id={self.id}, start={self.timeline_start}, end={self.timeline_end})>"
    
    @property
    def duration(self) -> float:
        return self.timeline_end - self.timeline_start
    
    @property
    def source_duration(self) -> float:
        return self.source_end - self.source_start
    
    @property
    def effective_duration(self) -> float:
        """Duration considering transitions"""
        in_trans = self.transition_duration if self.transition_in else 0
        out_trans = self.transition_duration if self.transition_out else 0
        return self.duration - in_trans - out_trans


class TimelineMarker(BaseModel):
    """
    Timeline marker for marking important positions.
    Used for beat markers, chapter markers, etc.
    """
    __tablename__ = "timeline_markers"
    
    timeline_id = Column(PGUUID(as_uuid=True), ForeignKey("timelines.id"), nullable=False)
    
    # Marker properties
    time = Column(Float, nullable=False)
    label = Column(String(255), nullable=True)
    color = Column(String(7), nullable=True)
    marker_type = Column(String(50), default="custom")
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f"<TimelineMarker(time={self.time}, label={self.label})>"


class TimelineRepository:
    """Repository for timeline data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, timeline_id: UUID) -> Optional[Timeline]:
        return self.db.query(Timeline).filter(Timeline.id == timeline_id).first()
    
    def get_with_tracks(self, timeline_id: UUID) -> Optional[Timeline]:
        return (
            self.db.query(Timeline)
            .filter(Timeline.id == timeline_id)
            .first()
        )
    
    def list_timelines(
        self,
        project_id: Optional[UUID] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Timeline]:
        query = self.db.query(Timeline)
        
        if project_id:
            query = query.filter(Timeline.project_id == project_id)
        if status:
            query = query.filter(Timeline.status == status)
        
        return query.order_by(Timeline.created_at.desc()).offset(offset).limit(limit).all()
    
    def create(self, timeline: Timeline) -> Timeline:
        self.db.add(timeline)
        self.db.commit()
        self.db.refresh(timeline)
        return timeline
    
    def update(self, timeline_id: UUID, updates: dict) -> Timeline:
        timeline = self.get_by_id(timeline_id)
        if not timeline:
            raise ValueError(f"Timeline {timeline_id} not found")
        
        for key, value in updates.items():
            if hasattr(timeline, key):
                setattr(timeline, key, value)
        
        timeline.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(timeline)
        return timeline
    
    def delete(self, timeline_id: UUID) -> bool:
        timeline = self.get_by_id(timeline_id)
        if not timeline:
            return False
        
        self.db.delete(timeline)
        self.db.commit()
        return True
    
    # Track operations
    def add_track(self, track: TimelineTrack) -> TimelineTrack:
        self.db.add(track)
        self.db.commit()
        self.db.refresh(track)
        return track
    
    def update_track(self, track_id: UUID, updates: dict) -> TimelineTrack:
        track = self.db.query(TimelineTrack).filter(TimelineTrack.id == track_id).first()
        if not track:
            raise ValueError(f"Track {track_id} not found")
        
        for key, value in updates.items():
            if hasattr(track, key):
                setattr(track, key, value)
        
        self.db.commit()
        self.db.refresh(track)
        return track
    
    def delete_track(self, track_id: UUID) -> bool:
        track = self.db.query(TimelineTrack).filter(TimelineTrack.id == track_id).first()
        if not track:
            return False
        
        self.db.delete(track)
        self.db.commit()
        return True
    
    # Clip operations
    def add_clip(self, clip: TimelineClip) -> TimelineClip:
        self.db.add(clip)
        self.db.commit()
        self.db.refresh(clip)
        return clip
    
    def update_clip(self, clip_id: UUID, updates: dict) -> TimelineClip:
        clip = self.db.query(TimelineClip).filter(TimelineClip.id == clip_id).first()
        if not clip:
            raise ValueError(f"Clip {clip_id} not found")
        
        for key, value in updates.items():
            if hasattr(clip, key):
                setattr(clip, key, value)
        
        self.db.commit()
        self.db.refresh(clip)
        return clip
    
    def delete_clip(self, clip_id: UUID) -> bool:
        clip = self.db.query(TimelineClip).filter(TimelineClip.id == clip_id).first()
        if not clip:
            return False
        
        self.db.delete(clip)
        self.db.commit()
        return True
    
    def move_clip(
        self,
        clip_id: UUID,
        new_track_id: UUID,
        new_start: Optional[float] = None
    ) -> TimelineClip:
        clip = self.db.query(TimelineClip).filter(TimelineClip.id == clip_id).first()
        if not clip:
            raise ValueError(f"Clip {clip_id} not found")
        
        clip.track_id = new_track_id
        
        if new_start is not None:
            duration = clip.duration
            clip.timeline_start = new_start
            clip.timeline_end = new_start + duration
        
        self.db.commit()
        self.db.refresh(clip)
        return clip