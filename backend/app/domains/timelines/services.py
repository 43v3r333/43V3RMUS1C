"""
Timeline Engine Services - Professional timeline operations
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import (
    TimelineStatus,
    TrackType,
    TransitionType,
    TimeRange,
    ClipData,
    TransitionData,
    MarkerData,
    Timeline,
    TimelineTrack,
    TimelineClip,
    TimelineMarker,
)

logger = logging.getLogger(__name__)


class TimelineEngine:
    """
    Professional timeline engine for media sequencing and editing.
    Handles timing calculations, clip sequencing, synchronization,
    transition orchestration, beat alignment, and export preparation.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== Timeline Operations ====================
    
    async def create_timeline(
        self,
        name: str,
        project_id: Optional[UUID] = None,
        duration: float = 0.0,
        frame_rate: float = 30.0,
        resolution: Tuple[int, int] = (1920, 1080),
        sample_rate: int = 48000,
    ) -> Timeline:
        """Create a new timeline"""
        timeline = Timeline(
            name=name,
            project_id=project_id,
            duration=duration,
            frame_rate=frame_rate,
            resolution_width=resolution[0],
            resolution_height=resolution[1],
            sample_rate=sample_rate,
            status=TimelineStatus.DRAFT.value,
        )
        
        self.db.add(timeline)
        await self.db.commit()
        await self.db.refresh(timeline)
        
        return timeline
    
    async def get_timeline(self, timeline_id: UUID) -> Optional[Timeline]:
        """Get timeline by ID"""
        result = await self.db.execute(
            select(Timeline).where(Timeline.id == timeline_id)
        )
        return result.scalar_one_or_none()
    
    async def update_timeline(
        self,
        timeline: Timeline,
        **kwargs,
    ) -> Timeline:
        """Update timeline properties"""
        for key, value in kwargs.items():
            if hasattr(timeline, key):
                setattr(timeline, key, value)
        
        self.db.add(timeline)
        await self.db.commit()
        await self.db.refresh(timeline)
        
        return timeline
    
    async def delete_timeline(self, timeline: Timeline) -> None:
        """Delete timeline"""
        await self.db.delete(timeline)
        await self.db.commit()
    
    # ==================== Track Operations ====================
    
    async def add_track(
        self,
        timeline: Timeline,
        name: str,
        track_type: TrackType,
        order: Optional[int] = None,
        height: int = 60,
    ) -> TimelineTrack:
        """Add a track to timeline"""
        if order is None:
            order = len(timeline.tracks)
        
        track = TimelineTrack(
            timeline_id=timeline.id,
            name=name,
            track_type=track_type.value,
            order=order,
            height=height,
        )
        
        self.db.add(track)
        await self.db.commit()
        await self.db.refresh(track)
        
        return track
    
    async def remove_track(self, track: TimelineTrack) -> None:
        """Remove track from timeline"""
        await self.db.delete(track)
        await self.db.commit()
    
    async def reorder_tracks(
        self,
        timeline: Timeline,
        track_order: List[UUID],
    ) -> List[TimelineTrack]:
        """Reorder tracks in timeline"""
        for idx, track_id in enumerate(track_order):
            result = await self.db.execute(
                select(TimelineTrack).where(TimelineTrack.id == track_id)
            )
            track = result.scalar_one_or_none()
            if track and track.timeline_id == timeline.id:
                track.order = idx
        
        await self.db.commit()
        
        # Return updated tracks
        result = await self.db.execute(
            select(TimelineTrack)
            .where(TimelineTrack.timeline_id == timeline.id)
            .order_by(TimelineTrack.order)
        )
        return list(result.scalars().all())
    
    # ==================== Clip Operations ====================
    
    async def add_clip(
        self,
        track: TimelineTrack,
        name: str,
        source_asset_id: Optional[UUID] = None,
        source_start: float = 0.0,
        source_end: float = 0.0,
        timeline_start: float = 0.0,
        duration: Optional[float] = None,
        gain: float = 1.0,
        pan: float = 0.0,
        opacity: float = 1.0,
        speed: float = 1.0,
    ) -> TimelineClip:
        """Add clip to track"""
        if duration is None:
            duration = source_end - source_start
        
        clip = TimelineClip(
            track_id=track.id,
            name=name,
            source_asset_id=source_asset_id,
            source_start=source_start,
            source_end=source_end,
            timeline_start=timeline_start,
            duration=duration,
            gain=gain,
            pan=pan,
            opacity=opacity,
            speed=speed,
        )
        
        self.db.add(clip)
        await self.db.commit()
        await self.db.refresh(clip)
        
        # Update timeline duration if needed
        timeline_end = timeline_start + duration
        if timeline_end > track.timeline.duration:
            track.timeline.duration = timeline_end
            await self.db.commit()
        
        return clip
    
    async def remove_clip(self, clip: TimelineClip) -> None:
        """Remove clip from track"""
        await self.db.delete(clip)
        await self.db.commit()
    
    async def update_clip(
        self,
        clip: TimelineClip,
        **kwargs,
    ) -> TimelineClip:
        """Update clip properties"""
        for key, value in kwargs.items():
            if hasattr(clip, key):
                setattr(clip, key, value)
        
        self.db.add(clip)
        await self.db.commit()
        await self.db.refresh(clip)
        
        return clip
    
    async def move_clip(
        self,
        clip: TimelineClip,
        new_timeline_start: float,
        new_track_id: Optional[UUID] = None,
    ) -> TimelineClip:
        """Move clip to new position"""
        clip.timeline_start = new_timeline_start
        
        if new_track_id:
            clip.track_id = new_track_id
        
        self.db.add(clip)
        await self.db.commit()
        await self.db.refresh(clip)
        
        return clip
    
    async def split_clip(
        self,
        clip: TimelineClip,
        split_time: float,
    ) -> Tuple[TimelineClip, TimelineClip]:
        """Split clip at given time, returning two clips"""
        # Calculate relative position
        relative_time = split_time - clip.timeline_start
        
        if relative_time <= 0 or relative_time >= clip.duration:
            raise ValueError("Split time must be within clip duration")
        
        # Create first clip (before split)
        clip1 = TimelineClip(
            track_id=clip.track_id,
            name=f"{clip.name} (1)",
            source_asset_id=clip.source_asset_id,
            source_start=clip.source_start,
            source_end=clip.source_start + relative_time * clip.speed,
            timeline_start=clip.timeline_start,
            duration=relative_time,
            gain=clip.gain,
            pan=clip.pan,
            opacity=clip.opacity,
            speed=clip.speed,
        )
        
        # Create second clip (after split)
        clip2 = TimelineClip(
            track_id=clip.track_id,
            name=f"{clip.name} (2)",
            source_asset_id=clip.source_asset_id,
            source_start=clip.source_start + relative_time * clip.speed,
            source_end=clip.source_end,
            timeline_start=split_time,
            duration=clip.duration - relative_time,
            gain=clip.gain,
            pan=clip.pan,
            opacity=clip.opacity,
            speed=clip.speed,
        )
        
        self.db.add(clip1)
        self.db.add(clip2)
        await self.db.delete(clip)
        await self.db.commit()
        await self.db.refresh(clip1)
        await self.db.refresh(clip2)
        
        return clip1, clip2
    
    # ==================== Timing Calculations ====================
    
    def frame_to_time(self, frame: int, frame_rate: float = 30.0) -> float:
        """Convert frame number to time in seconds"""
        return frame / frame_rate
    
    def time_to_frame(self, time: float, frame_rate: float = 30.0) -> int:
        """Convert time in seconds to frame number"""
        return int(time * frame_rate)
    
    def time_to_smpte(self, time: float, frame_rate: float = 30.0) -> str:
        """Convert time to SMPTE timecode format"""
        total_frames = int(time * frame_rate)
        hours = total_frames // (3600 * frame_rate)
        minutes = (total_frames % (3600 * frame_rate)) // (60 * frame_rate)
        seconds = (total_frames % (60 * frame_rate)) // frame_rate
        frames = total_frames % frame_rate
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"
    
    def smpte_to_time(self, timecode: str, frame_rate: float = 30.0) -> float:
        """Convert SMPTE timecode to time in seconds"""
        parts = timecode.split(":")
        if len(parts) != 4:
            raise ValueError("Invalid SMPTE format")
        
        hours, minutes, seconds, frames = map(int, parts)
        total_frames = (
            hours * 3600 * frame_rate +
            minutes * 60 * frame_rate +
            seconds * frame_rate +
            frames
        )
        
        return total_frames / frame_rate
    
    def calculate_duration(
        self,
        timeline: Timeline,
        include_overflows: bool = True,
    ) -> float:
        """Calculate timeline duration based on clips"""
        max_end = 0.0
        
        for track in timeline.tracks:
            for clip in track.clips:
                clip_end = clip.timeline_start + clip.duration
                if clip_end > max_end:
                    max_end = clip_end
        
        return max_end if include_overflows else timeline.duration
    
    # ==================== Synchronization ====================
    
    async def sync_to_beat(
        self,
        clip: TimelineClip,
        beat_markers: List[float],
        tolerance: float = 0.1,
    ) -> TimelineClip:
        """Snap clip start to nearest beat marker"""
        if not beat_markers:
            return clip
        
        # Find nearest beat to clip start
        nearest_beat = min(
            beat_markers,
            key=lambda b: abs(b - clip.timeline_start)
        )
        
        # Check if within tolerance
        if abs(nearest_beat - clip.timeline_start) <= tolerance:
            clip.timeline_start = nearest_beat
        
        self.db.add(clip)
        await self.db.commit()
        await self.db.refresh(clip)
        
        return clip
    
    async def align_clips_to_beat(
        self,
        clips: List[TimelineClip],
        beat_markers: List[float],
        tolerance: float = 0.1,
    ) -> List[TimelineClip]:
        """Align multiple clips to beat markers"""
        aligned = []
        
        for clip in clips:
            aligned_clip = await self.sync_to_beat(clip, beat_markers, tolerance)
            aligned.append(aligned_clip)
        
        return aligned
    
    def find_sync_points(
        self,
        track1_clips: List[TimelineClip],
        track2_clips: List[TimelineClip],
        tolerance: float = 0.05,
    ) -> List[Tuple[float, TimelineClip, TimelineClip]]:
        """Find synchronization points between two clip lists"""
        sync_points = []
        
        for clip1 in track1_clips:
            for clip2 in track2_clips:
                # Check if start times are within tolerance
                if abs(clip1.timeline_start - clip2.timeline_start) <= tolerance:
                    sync_points.append((
                        clip1.timeline_start,
                        clip1,
                        clip2,
                    ))
                # Check if clip1 start aligns with clip2 end
                if abs(clip1.timeline_start - (clip2.timeline_start + clip2.duration)) <= tolerance:
                    sync_points.append((
                        clip1.timeline_start,
                        clip1,
                        clip2,
                    ))
        
        return sync_points
    
    # ==================== Transition Operations ====================
    
    async def set_transition(
        self,
        clip: TimelineClip,
        transition_type: TransitionType,
        duration: float,
        direction: str = "in",  # "in" or "out"
        parameters: Optional[Dict[str, Any]] = None,
    ) -> TimelineClip:
        """Set transition on clip"""
        transition_data = {
            "type": transition_type.value,
            "duration": duration,
            "parameters": parameters or {},
        }
        
        if direction == "in":
            clip.transition_in = transition_data
        else:
            clip.transition_out = transition_data
        
        self.db.add(clip)
        await self.db.commit()
        await self.db.refresh(clip)
        
        return clip
    
    async def calculate_crossfade(
        self,
        clip_out: TimelineClip,
        clip_in: TimelineClip,
        overlap_duration: float,
    ) -> Tuple[List[Dict], List[Dict]]:
        """Calculate crossfade parameters for two clips"""
        # Calculate gain curves for crossfade
        gain_out = []
        gain_in = []
        
        steps = 100
        for i in range(steps):
            progress = i / steps
            gain_out.append({"time": i / steps, "gain": 1.0 - progress})
            gain_in.append({"time": i / steps, "gain": progress})
        
        return gain_out, gain_in
    
    # ==================== Export Preparation ====================
    
    async def prepare_for_export(
        self,
        timeline: Timeline,
        output_format: str = "mp4",
        codec: str = "libx264",
    ) -> Dict[str, Any]:
        """Prepare timeline for export"""
        # Calculate total duration
        duration = self.calculate_duration(timeline)
        
        # Build render list
        render_list = []
        
        for track in sorted(timeline.tracks, key=lambda t: t.order):
            if track.muted:
                continue
            
            for clip in track.clips:
                render_item = {
                    "track_type": track.track_type,
                    "clip_id": str(clip.id),
                    "source_asset_id": str(clip.source_asset_id) if clip.source_asset_id else None,
                    "start_time": clip.timeline_start,
                    "duration": clip.duration,
                    "source_start": clip.source_start,
                    "source_end": clip.source_end,
                    "gain": clip.gain,
                    "pan": clip.pan,
                    "opacity": clip.opacity,
                    "speed": clip.speed,
                    "effects": clip.effects or [],
                }
                render_list.append(render_item)
        
        return {
            "timeline_id": str(timeline.id),
            "output_format": output_format,
            "codec": codec,
            "frame_rate": timeline.frame_rate,
            "resolution": f"{timeline.resolution_width}x{timeline.resolution_height}",
            "duration": duration,
            "sample_rate": timeline.sample_rate,
            "render_list": render_list,
        }
    
    # ==================== Marker Operations ====================
    
    async def add_marker(
        self,
        timeline: Timeline,
        name: str,
        time: float,
        color: str = "#FFFF00",
        description: Optional[str] = None,
    ) -> TimelineMarker:
        """Add marker to timeline"""
        marker = TimelineMarker(
            timeline_id=timeline.id,
            name=name,
            time=time,
            color=color,
            description=description,
        )
        
        self.db.add(marker)
        await self.db.commit()
        await self.db.refresh(marker)
        
        return marker
    
    async def remove_marker(self, marker: TimelineMarker) -> None:
        """Remove marker from timeline"""
        await self.db.delete(marker)
        await self.db.commit()
    
    async def get_markers_in_range(
        self,
        timeline: Timeline,
        start_time: float,
        end_time: float,
    ) -> List[TimelineMarker]:
        """Get markers within time range"""
        result = await self.db.execute(
            select(TimelineMarker)
            .where(
                TimelineMarker.timeline_id == timeline.id,
                TimelineMarker.time >= start_time,
                TimelineMarker.time <= end_time,
            )
            .order_by(TimelineMarker.time)
        )
        return list(result.scalars().all())
    
    # ==================== Composition ====================
    
    async def build_composition(
        self,
        timeline: Timeline,
    ) -> Dict[str, Any]:
        """Build complete timeline composition"""
        # Load tracks and markers
        result = await self.db.execute(
            select(TimelineTrack)
            .where(TimelineTrack.timeline_id == timeline.id)
            .order_by(TimelineTrack.order)
        )
        tracks = list(result.scalars().all())
        
        result = await self.db.execute(
            select(TimelineMarker)
            .where(TimelineMarker.timeline_id == timeline.id)
            .order_by(TimelineMarker.time)
        )
        markers = list(result.scalars().all())
        
        # Build composition structure
        composition = {
            "id": str(timeline.id),
            "name": timeline.name,
            "duration": timeline.duration,
            "frame_rate": timeline.frame_rate,
            "resolution": (timeline.resolution_width, timeline.resolution_height),
            "tracks": [],
            "markers": [
                {
                    "id": str(m.id),
                    "name": m.name,
                    "time": m.time,
                    "color": m.color,
                    "description": m.description,
                }
                for m in markers
            ],
        }
        
        for track in tracks:
            track_data = {
                "id": str(track.id),
                "name": track.name,
                "track_type": track.track_type,
                "order": track.order,
                "muted": track.muted,
                "solo": track.solo,
                "locked": track.locked,
                "volume": track.volume,
                "pan": track.pan,
                "height": track.height,
                "clips": [],
            }
            
            for clip in track.clips:
                clip_data = ClipData(
                    id=clip.id,
                    track_id=clip.track_id,
                    name=clip.name,
                    source_asset_id=clip.source_asset_id,
                    source_start=clip.source_start,
                    source_end=clip.source_end,
                    timeline_start=clip.timeline_start,
                    timeline_end=clip.timeline_start + clip.duration,
                    duration=clip.duration,
                    gain=clip.gain,
                    pan=clip.pan,
                    opacity=clip.opacity,
                    speed=clip.speed,
                    effects=clip.effects or [],
                )
                track_data["clips"].append(clip_data.__dict__)
            
            composition["tracks"].append(track_data)
        
        return composition