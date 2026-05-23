"""
Timeline Domain - Video composition and editing engine.

Contains:
- models: Timeline, TimelineTrack, TimelineClip
- services: TimelineService
- events: Timeline events
- handlers: Timeline event handlers
"""
from .models import (
    Timeline,
    TimelineTrack,
    TimelineClip,
    TimelineStatus,
    TrackType,
    TransitionType,
    TimelineRepository,
)
from .services import TimelineService, TimelineCompositionEngine

__all__ = [
    "Timeline",
    "TimelineTrack",
    "TimelineClip",
    "TimelineStatus",
    "TrackType",
    "TransitionType",
    "TimelineRepository",
    "TimelineService",
    "TimelineCompositionEngine",
]