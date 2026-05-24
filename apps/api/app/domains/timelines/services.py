"""
Timeline Domain Services
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.ffmpeg_engine import get_ffmpeg_engine, FFmpegInput, FFmpegOutput, FFmpegFilter, RenderRequest
from app.core.storage import get_storage_manager
from app.domains.timelines.models import (
    Timeline,
    TimelineTrack,
    TimelineClip,
    TimelineMarker,
    TimelineStatus,
    TrackType,
    TransitionType,
    TimelineRepository,
)

logger = logging.getLogger(__name__)


class TimelineService:
    """
    Service for managing timelines and video composition.
    Handles timeline CRUD, track management, and clip operations.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = TimelineRepository(db)
        self.ffmpeg = get_ffmpeg_engine()
        self.storage = get_storage_manager()
    
    def create_timeline(
        self,
        name: str,
        created_by_id: UUID,
        project_id: Optional[UUID] = None,
        description: Optional[str] = None,
        frame_rate: float = 30.0,
        resolution_width: int = 1080,
        resolution_height: int = 1920,
        aspect_ratio: str = "9:16"
    ) -> Timeline:
        """Create a new timeline with default tracks"""
        timeline = Timeline(
            name=name,
            description=description,
            frame_rate=frame_rate,
            resolution_width=resolution_width,
            resolution_height=resolution_height,
            aspect_ratio=aspect_ratio,
            project_id=project_id,
            created_by_id=created_by_id
        )
        
        self.db.add(timeline)
        self.db.commit()
        self.db.refresh(timeline)
        
        # Create default tracks
        self._create_default_tracks(timeline.id)
        
        return timeline
    
    def _create_default_tracks(self, timeline_id: UUID) -> None:
        """Create default tracks for a timeline"""
        default_tracks = [
            {"name": "Video", "track_type": TrackType.VIDEO.value, "order": 0, "height": 80},
            {"name": "Audio", "track_type": TrackType.AUDIO.value, "order": 1, "height": 60},
            {"name": "Overlay", "track_type": TrackType.OVERLAY.value, "order": 2, "height": 40},
            {"name": "Captions", "track_type": TrackType.CAPTION.value, "order": 3, "height": 40},
        ]
        
        for track_data in default_tracks:
            track = TimelineTrack(
                timeline_id=timeline_id,
                **track_data
            )
            self.db.add(track)
        
        self.db.commit()
    
    def get_timeline(self, timeline_id: UUID) -> Optional[Timeline]:
        """Get timeline by ID with all tracks and clips"""
        return self.repository.get_with_tracks(timeline_id)
    
    def list_timelines(
        self,
        project_id: Optional[UUID] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Timeline]:
        return self.repository.list_timelines(project_id, status, limit)
    
    def update_timeline(self, timeline_id: UUID, updates: Dict[str, Any]) -> Timeline:
        """Update timeline properties"""
        timeline = self.repository.update(timeline_id, updates)
        
        # Update duration if needed
        if any(k in updates for k in ["duration"]):
            self._update_timeline_duration(timeline_id)
        
        return timeline
    
    def delete_timeline(self, timeline_id: UUID) -> bool:
        """Delete timeline and all associated tracks/clips"""
        return self.repository.delete(timeline_id)
    
    # Track operations
    
    def add_track(
        self,
        timeline_id: UUID,
        name: str,
        track_type: str,
        order: Optional[int] = None,
        height: int = 60
    ) -> TimelineTrack:
        """Add a new track to timeline"""
        timeline = self.get_timeline(timeline_id)
        if not timeline:
            raise ValueError(f"Timeline {timeline_id} not found")
        
        if order is None:
            max_order = max((t.order for t in timeline.tracks), default=-1)
            order = max_order + 1
        
        track = TimelineTrack(
            timeline_id=timeline_id,
            name=name,
            track_type=track_type,
            order=order,
            height=height
        )
        
        return self.repository.add_track(track)
    
    def update_track(self, track_id: UUID, updates: Dict[str, Any]) -> TimelineTrack:
        """Update track properties"""
        return self.repository.update_track(track_id, updates)
    
    def delete_track(self, track_id: UUID) -> bool:
        """Delete track and all clips"""
        return self.repository.delete_track(track_id)
    
    # Clip operations
    
    def add_clip(
        self,
        track_id: UUID,
        asset_id: UUID,
        timeline_start: float,
        timeline_end: float,
        source_start: float = 0,
        source_end: Optional[float] = None,
        name: Optional[str] = None,
        **kwargs
    ) -> TimelineClip:
        """Add a clip to a track"""
        # Get source duration if not specified
        if source_end is None:
            from app.domains.media.models import MediaAsset
            asset = self.db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
            if asset and asset.duration:
                source_end = asset.duration
        
        clip = TimelineClip(
            track_id=track_id,
            asset_id=asset_id,
            timeline_start=timeline_start,
            timeline_end=timeline_end,
            source_start=source_start,
            source_end=source_end or timeline_end,
            name=name,
            **kwargs
        )
        
        created = self.repository.add_clip(clip)
        
        # Update timeline duration
        track = self.db.query(TimelineTrack).filter(TimelineTrack.id == track_id).first()
        if track:
            self._update_timeline_duration(track.timeline_id)
        
        return created
    
    def update_clip(self, clip_id: UUID, updates: Dict[str, Any]) -> TimelineClip:
        """Update clip properties"""
        clip = self.repository.update_clip(clip_id, updates)
        
        # Update timeline duration
        if clip.track:
            self._update_timeline_duration(clip.track.timeline_id)
        
        return clip
    
    def delete_clip(self, clip_id: UUID) -> bool:
        """Delete a clip"""
        clip = self.db.query(TimelineClip).filter(TimelineClip.id == clip_id).first()
        if not clip:
            return False
        
        timeline_id = clip.track.timeline_id if clip.track else None
        
        success = self.repository.delete_clip(clip_id)
        
        if success and timeline_id:
            self._update_timeline_duration(timeline_id)
        
        return success
    
    def move_clip(
        self,
        clip_id: UUID,
        new_track_id: UUID,
        new_start: Optional[float] = None
    ) -> TimelineClip:
        """Move clip to different track or position"""
        return self.repository.move_clip(clip_id, new_track_id, new_start)
    
    def _update_timeline_duration(self, timeline_id: UUID) -> None:
        """Update timeline duration based on clips"""
        timeline = self.get_timeline(timeline_id)
        if not timeline:
            return
        
        max_end = 0.0
        for track in timeline.tracks:
            for clip in track.clips:
                if clip.timeline_end > max_end:
                    max_end = clip.timeline_end
        
        timeline.duration = max_end if max_end > 0 else None
        self.db.commit()
    
    # Marker operations
    
    def add_marker(
        self,
        timeline_id: UUID,
        time: float,
        label: Optional[str] = None,
        marker_type: str = "custom",
        color: Optional[str] = None
    ) -> TimelineMarker:
        """Add a marker to timeline"""
        marker = TimelineMarker(
            timeline_id=timeline_id,
            time=time,
            label=label,
            marker_type=marker_type,
            color=color
        )
        
        self.db.add(marker)
        self.db.commit()
        self.db.refresh(marker)
        
        return marker
    
    def sync_to_beats(self, timeline_id: UUID, beats: List[float]) -> List[TimelineClip]:
        """Sync all clips to beat markers"""
        timeline = self.get_timeline(timeline_id)
        if not timeline:
            return []
        
        updated_clips = []
        
        for track in timeline.tracks:
            for clip in track.clips:
                if beats:
                    nearest_beat = min(beats, key=lambda b: abs(b - clip.timeline_start))
                    if abs(nearest_beat - clip.timeline_start) < 0.2:
                        duration = clip.duration
                        clip.timeline_start = nearest_beat
                        clip.timeline_end = nearest_beat + duration
                        updated_clips.append(clip)
        
        self.db.commit()
        return updated_clips


class TimelineCompositionEngine:
    """
    Engine for composing and rendering timelines.
    Converts timeline structure to FFmpeg render commands.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ffmpeg = get_ffmpeg_engine()
        self.storage = get_storage_manager()
    
    def build_render_request(
        self,
        timeline_id: UUID,
        output_path: str,
        preset: Optional[Dict[str, Any]] = None
    ) -> RenderRequest:
        """
        Build FFmpeg render request from timeline structure.
        """
        from app.domains.timelines.models import Timeline
        
        timeline = self.db.query(Timeline).filter(Timeline.id == timeline_id).first()
        if not timeline:
            raise ValueError(f"Timeline {timeline_id} not found")
        
        inputs = []
        filters = []
        
        # Process video tracks
        for track in timeline.tracks:
            if track.track_type != TrackType.VIDEO.value:
                continue
            
            for clip in track.clips:
                if not clip.asset:
                    continue
                
                asset_path = self.storage.storage.config.base_path / clip.asset.file_path
                
                clip_input = FFmpegInput(
                    path=str(asset_path),
                    start_time=clip.source_start,
                    duration=clip.duration,
                    volume=clip.volume if track.track_type == TrackType.AUDIO.value else None
                )
                inputs.append(clip_input)
                
                # Add video effects filters
                if clip.filters:
                    for f in clip.filters:
                        filters.append(FFmpegFilter(name=f["name"], params=f.get("params", {})))
        
        # Build output configuration
        if preset:
            output = FFmpegOutput(
                path=output_path,
                width=preset.get("width", timeline.resolution_width),
                height=preset.get("height", timeline.resolution_height),
                frame_rate=preset.get("frame_rate", timeline.frame_rate),
                video_codec=preset.get("video_codec", "libx264"),
                preset=preset.get("ffmpeg_preset", "medium"),
                crf=preset.get("crf", 23)
            )
        else:
            output = FFmpegOutput(
                path=output_path,
                width=timeline.resolution_width,
                height=timeline.resolution_height,
                frame_rate=timeline.frame_rate
            )
        
        return RenderRequest(inputs=inputs, output=output, filters=filters)
    
    def calculate_clip_timeline(
        self,
        timeline: Timeline,
        clip_id: UUID,
        target_time: float
    ) -> Dict[str, float]:
        """
        Calculate new clip position for timeline editing.
        Returns adjusted start/end times.
        """
        clip = self.db.query(TimelineClip).filter(TimelineClip.id == clip_id).first()
        if not clip:
            raise ValueError(f"Clip {clip_id} not found")
        
        duration = clip.duration
        
        return {
            "timeline_start": target_time,
            "timeline_end": target_time + duration,
            "source_start": clip.source_start,
            "source_end": clip.source_end
        }
    
    def snap_to_grid(
        self,
        timeline_id: UUID,
        grid_size: float = 0.1
    ) -> List[TimelineClip]:
        """
        Snap all clips to a time grid.
        Useful for beat-aligned editing.
        """
        timeline = self.db.query(Timeline).filter(Timeline.id == timeline_id).first()
        if not timeline:
            return []
        
        updated = []
        
        for track in timeline.tracks:
            for clip in track.clips:
                # Snap start
                snapped_start = round(clip.timeline_start / grid_size) * grid_size
                duration = clip.duration
                
                clip.timeline_start = snapped_start
                clip.timeline_end = snapped_start + duration
                updated.append(clip)
        
        self.db.commit()
        return updated
    
    def get_edit_preview(
        self,
        timeline_id: UUID,
        time: float,
        window_size: float = 1.0
    ) -> Dict[str, Any]:
        """
        Get preview of what's happening at a specific time.
        Returns visible clips and their properties.
        """
        timeline = self.get_timeline(timeline_id)
        if not timeline:
            return {}
        
        visible_clips = []
        
        for track in timeline.tracks:
            for clip in track.clips:
                if clip.timeline_start <= time <= clip.timeline_end:
                    visible_clips.append({
                        "clip_id": str(clip.id),
                        "track_id": str(clip.track_id),
                        "track_type": track.track_type,
                        "name": clip.name,
                        "source_time": clip.source_start + (time - clip.timeline_start),
                        "volume": clip.volume,
                        "opacity": clip.opacity if hasattr(track, 'opacity') else 1.0
                    })
        
        return {
            "time": time,
            "clips": visible_clips,
            "duration": timeline.duration
        }