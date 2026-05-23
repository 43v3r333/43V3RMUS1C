"""
Timeline composition service for video editing.
Handles timeline creation, clip management, and composition rendering.
"""
import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy.orm import Session

from app.core.ffmpeg_engine import get_ffmpeg_engine, FFmpegInput, FFmpegOutput, FFmpegFilter, RenderRequest
from app.core.storage import get_storage_manager
from app.models.media_execution import (
    Timeline,
    TimelineTrack,
    TimelineClip,
    ExportPresetModel
)

logger = logging.getLogger(__name__)


class TimelineService:
    """
    Service for managing timelines and video composition.
    Handles timeline CRUD, clip manipulation, and render composition.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ffmpeg = get_ffmpeg_engine()
        self.storage = get_storage_manager()
    
    def create_timeline(
        self,
        name: str,
        created_by_id: uuid.UUID,
        project_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        frame_rate: float = 30.0,
        resolution_width: int = 1080,
        resolution_height: int = 1920,
        aspect_ratio: str = "9:16"
    ) -> Timeline:
        """
        Create a new timeline.
        
        Args:
            name: Timeline name
            created_by_id: User creating the timeline
            project_id: Optional project association
            description: Timeline description
            frame_rate: Frames per second
            resolution_width: Video width
            resolution_height: Video height
            aspect_ratio: Aspect ratio (9:16, 16:9, 1:1)
            
        Returns:
            Created Timeline with default tracks
        """
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
    
    def _create_default_tracks(self, timeline_id: uuid.UUID):
        """Create default tracks for a timeline"""
        default_tracks = [
            {"name": "Video", "track_type": "video", "order": 0, "height": 80},
            {"name": "Audio", "track_type": "audio", "order": 1, "height": 60},
            {"name": "Overlay", "track_type": "overlay", "order": 2, "height": 40},
            {"name": "Captions", "track_type": "caption", "order": 3, "height": 40},
        ]
        
        for track_data in default_tracks:
            track = TimelineTrack(
                timeline_id=timeline_id,
                **track_data
            )
            self.db.add(track)
        
        self.db.commit()
    
    def get_timeline(self, timeline_id: uuid.UUID) -> Optional[Timeline]:
        """Get timeline by ID with all tracks and clips"""
        return (
            self.db.query(Timeline)
            .filter(Timeline.id == timeline_id)
            .first()
        )
    
    def list_timelines(
        self,
        project_id: Optional[uuid.UUID] = None,
        is_published: Optional[bool] = None,
        limit: int = 50
    ) -> List[Timeline]:
        """List timelines"""
        query = self.db.query(Timeline)
        
        if project_id:
            query = query.filter(Timeline.project_id == project_id)
        if is_published is not None:
            query = query.filter(Timeline.is_published == is_published)
        
        return query.order_by(Timeline.created_at.desc()).limit(limit).all()
    
    def update_timeline(
        self,
        timeline_id: uuid.UUID,
        updates: Dict[str, Any]
    ) -> Timeline:
        """Update timeline properties"""
        timeline = self.get_timeline(timeline_id)
        
        if not timeline:
            raise ValueError(f"Timeline {timeline_id} not found")
        
        for key, value in updates.items():
            if hasattr(timeline, key):
                setattr(timeline, key, value)
        
        timeline.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(timeline)
        
        return timeline
    
    def delete_timeline(self, timeline_id: uuid.UUID) -> bool:
        """Delete timeline and all associated clips"""
        timeline = self.get_timeline(timeline_id)
        
        if not timeline:
            return False
        
        # Delete associated tracks and clips (cascade)
        self.db.query(TimelineClip).filter(
            TimelineClip.track_id.in_(
                self.db.query(TimelineTrack.id).filter(TimelineTrack.timeline_id == timeline_id)
            )
        ).delete(synchronize_session=False)
        
        self.db.query(TimelineTrack).filter(
            TimelineTrack.timeline_id == timeline_id
        ).delete(synchronize_session=False)
        
        self.db.delete(timeline)
        self.db.commit()
        
        return True
    
    # Track management
    
    def add_track(
        self,
        timeline_id: uuid.UUID,
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
            max_order = self.db.query(TimelineTrack).filter(
                TimelineTrack.timeline_id == timeline_id
            ).func.max(TimelineTrack.order).scalar() or -1
            order = max_order + 1
        
        track = TimelineTrack(
            timeline_id=timeline_id,
            name=name,
            track_type=track_type,
            order=order,
            height=height
        )
        
        self.db.add(track)
        self.db.commit()
        self.db.refresh(track)
        
        return track
    
    def update_track(
        self,
        track_id: uuid.UUID,
        updates: Dict[str, Any]
    ) -> TimelineTrack:
        """Update track properties"""
        track = self.db.query(TimelineTrack).filter(TimelineTrack.id == track_id).first()
        
        if not track:
            raise ValueError(f"Track {track_id} not found")
        
        for key, value in updates.items():
            if hasattr(track, key):
                setattr(track, key, value)
        
        self.db.commit()
        self.db.refresh(track)
        
        return track
    
    def delete_track(self, track_id: uuid.UUID) -> bool:
        """Delete track and all clips"""
        track = self.db.query(TimelineTrack).filter(TimelineTrack.id == track_id).first()
        
        if not track:
            return False
        
        # Delete clips
        self.db.query(TimelineClip).filter(TimelineClip.track_id == track_id).delete()
        
        self.db.delete(track)
        self.db.commit()
        
        return True
    
    # Clip management
    
    def add_clip(
        self,
        track_id: uuid.UUID,
        asset_id: uuid.UUID,
        timeline_start: float,
        timeline_end: float,
        source_start: float = 0,
        source_end: Optional[float] = None,
        name: Optional[str] = None,
        **kwargs
    ) -> TimelineClip:
        """
        Add a clip to a track.
        
        Args:
            track_id: Target track
            asset_id: Media asset to add
            timeline_start: Start position on timeline (seconds)
            timeline_end: End position on timeline (seconds)
            source_start: In-point in source asset (seconds)
            source_end: Out-point in source asset (seconds)
            name: Optional clip name
            
        Returns:
            Created TimelineClip
        """
        track = self.db.query(TimelineTrack).filter(TimelineTrack.id == track_id).first()
        
        if not track:
            raise ValueError(f"Track {track_id} not found")
        
        # If source_end not specified, use duration from asset
        if source_end is None:
            from app.models.media_execution import MediaAsset
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
            name=name or f"Clip {timeline_start}s"
        )
        
        # Apply additional clip properties
        for key, value in kwargs.items():
            if hasattr(clip, key):
                setattr(clip, key, value)
        
        self.db.add(clip)
        self.db.commit()
        self.db.refresh(clip)
        
        # Update timeline duration if needed
        self._update_timeline_duration(track.timeline_id)
        
        return clip
    
    def update_clip(
        self,
        clip_id: uuid.UUID,
        updates: Dict[str, Any]
    ) -> TimelineClip:
        """Update clip properties"""
        clip = self.db.query(TimelineClip).filter(TimelineClip.id == clip_id).first()
        
        if not clip:
            raise ValueError(f"Clip {clip_id} not found")
        
        for key, value in updates.items():
            if hasattr(clip, key):
                setattr(clip, key, value)
        
        self.db.commit()
        self.db.refresh(clip)
        
        # Update timeline duration
        self._update_timeline_duration(clip.track.timeline_id)
        
        return clip
    
    def delete_clip(self, clip_id: uuid.UUID) -> bool:
        """Delete a clip"""
        clip = self.db.query(TimelineClip).filter(TimelineClip.id == clip_id).first()
        
        if not clip:
            return False
        
        timeline_id = clip.track.timeline_id
        self.db.delete(clip)
        self.db.commit()
        
        # Update timeline duration
        self._update_timeline_duration(timeline_id)
        
        return True
    
    def move_clip(
        self,
        clip_id: uuid.UUID,
        new_track_id: uuid.UUID,
        new_start: Optional[float] = None
    ) -> TimelineClip:
        """Move clip to different track or position"""
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
    
    def _update_timeline_duration(self, timeline_id: uuid.UUID):
        """Update timeline duration based on clips"""
        timeline = self.get_timeline(timeline_id)
        
        if not timeline:
            return
        
        # Find the maximum end time across all clips
        max_end = 0.0
        for track in timeline.tracks:
            for clip in track.clips:
                if clip.timeline_end > max_end:
                    max_end = clip.timeline_end
        
        timeline.duration = max_end if max_end > 0 else None
        self.db.commit()
    
    # Rendering
    
    def render_timeline(
        self,
        timeline_id: uuid.UUID,
        preset: Optional[ExportPresetModel] = None
    ) -> Tuple[bool, str]:
        """
        Render timeline to video file.
        
        Args:
            timeline_id: Timeline to render
            preset: Optional export preset
            
        Returns:
            Tuple of (success, output_path or error_message)
        """
        timeline = self.get_timeline(timeline_id)
        
        if not timeline:
            raise ValueError(f"Timeline {timeline_id} not found")
        
        if not timeline.tracks:
            return False, "No tracks in timeline"
        
        # Generate output path
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_name = f"{timeline.name}_{timestamp}.mp4"
        output_path = f"renders/{output_name}"
        full_output = self.storage.storage.config.base_path / output_path
        full_output.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Build render request
            render_request = self._build_render_request(timeline, str(full_output), preset)
            
            # Execute render
            returncode, stdout, stderr = self.ffmpeg.execute(render_request)
            
            if returncode == 0:
                return True, str(full_output)
            else:
                return False, stderr
                
        except Exception as e:
            logger.error(f"Timeline render failed: {e}")
            return False, str(e)
    
    def _build_render_request(
        self,
        timeline: Timeline,
        output_path: str,
        preset: Optional[ExportPresetModel]
    ) -> RenderRequest:
        """Build FFmpeg render request from timeline"""
        # Collect all clips grouped by track
        video_clips = []
        audio_clips = []
        
        for track in timeline.tracks:
            for clip in track.clips:
                if not clip.asset:
                    continue
                
                # Get asset path
                asset_path = self.storage.storage.config.base_path / clip.asset.file_path
                
                clip_input = FFmpegInput(
                    path=str(asset_path),
                    start_time=clip.source_start,
                    duration=clip.duration,
                    volume=track.volume if track.track_type == "audio" else None
                )
                
                if track.track_type == "video":
                    video_clips.append((clip, clip_input))
                elif track.track_type == "audio":
                    audio_clips.append((clip, clip_input))
        
        # Build output configuration
        if preset:
            output = FFmpegOutput(
                path=output_path,
                width=preset.width,
                height=preset.height,
                frame_rate=preset.frame_rate,
                video_codec=preset.video_codec,
                video_bitrate=preset.video_bitrate,
                audio_codec=preset.audio_codec,
                audio_bitrate=preset.audio_bitrate,
                preset=preset.ffmpeg_preset,
                crf=preset.crf
            )
        else:
            output = FFmpegOutput(
                path=output_path,
                width=timeline.resolution_width,
                height=timeline.resolution_height,
                frame_rate=timeline.frame_rate
            )
        
        # Build inputs list
        inputs = []
        filters = []
        
        # For simple single-clip render
        if video_clips:
            clip, clip_input = video_clips[0]
            inputs.append(clip_input)
        
        if audio_clips:
            clip, clip_input = audio_clips[0]
            inputs.append(clip_input)
        
        return RenderRequest(
            inputs=inputs,
            output=output,
            filters=filters
        )
    
    # Beat synchronization
    
    def sync_to_beat(
        self,
        timeline_id: uuid.UUID,
        beats: List[float],
        clip_id: uuid.UUID
    ) -> TimelineClip:
        """
        Align clip to beat grid.
        
        Args:
            timeline_id: Timeline containing the clip
            beats: List of beat timestamps
            clip_id: Clip to sync
            
        Returns:
            Updated clip
        """
        clip = self.db.query(TimelineClip).filter(TimelineClip.id == clip_id).first()
        
        if not clip:
            raise ValueError(f"Clip {clip_id} not found")
        
        # Find nearest beat to current start
        if beats:
            nearest_beat = min(beats, key=lambda b: abs(b - clip.timeline_start))
            
            # Only snap if within 0.2 seconds
            if abs(nearest_beat - clip.timeline_start) < 0.2:
                duration = clip.duration
                clip.timeline_start = nearest_beat
                clip.timeline_end = nearest_beat + duration
        
        self.db.commit()
        self.db.refresh(clip)
        
        return clip
    
    def auto_trim_to_beat(
        self,
        timeline_id: uuid.UUID,
        beats: List[float],
        silence_threshold: float = -40.0
    ) -> List[TimelineClip]:
        """
        Automatically trim clips to avoid silence at boundaries.
        
        Args:
            timeline_id: Timeline to process
            beats: Beat timestamps
            silence_threshold: Silence threshold in dB
            
        Returns:
            List of updated clips
        """
        timeline = self.get_timeline(timeline_id)
        
        if not timeline:
            return []
        
        updated_clips = []
        
        for track in timeline.tracks:
            if track.track_type != "audio":
                continue
            
            for clip in track.clips:
                # This would involve audio analysis
                # For now, just sync to nearest beat
                if beats:
                    nearest_beat = min(beats, key=lambda b: abs(b - clip.timeline_start))
                    if abs(nearest_beat - clip.timeline_start) < 0.1:
                        duration = clip.duration
                        clip.timeline_start = nearest_beat
                        clip.timeline_end = nearest_beat + duration
                        
                        self.db.commit()
                        updated_clips.append(clip)
        
        return updated_clips