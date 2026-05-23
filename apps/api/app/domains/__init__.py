"""
Domain-Driven Architecture for 43V3R CORE

This module contains bounded contexts for different domains:

/media - Asset lifecycle and processing
/rendering - Distributed render orchestration
/audio - Music intelligence and analysis
/timelines - Video composition and editing
/workflows - Automation and execution
/analytics - Data and metrics
/ai - AI orchestration
/automation - System automation
"""
from .media import (
    MediaAsset,
    TranscodingJob,
    WaveformData,
    AudioAnalysis,
    MediaAssetService,
    TranscodingService,
    MediaStatus,
    AssetType,
)
from .rendering import (
    RenderJob,
    RenderOutput,
    ExportPreset,
    RenderWorker,
    RenderQueueService,
    RenderOrchestrator,
    RenderStatus,
    RenderPriority,
)
from .audio import (
    AudioAnalysisService,
    AudioProcessingService,
    AudioSegment,
)
from .timelines import (
    Timeline,
    TimelineTrack,
    TimelineClip,
    TimelineService,
    TimelineCompositionEngine,
    TimelineStatus,
    TrackType,
)
from .workflows import (
    Workflow,
    WorkflowExecution,
    WorkflowStep,
    WorkflowService,
    WorkflowExecutor,
    WorkflowStatus,
    ExecutionStatus,
)

__all__ = [
    # Media
    "MediaAsset",
    "TranscodingJob",
    "WaveformData",
    "AudioAnalysis",
    "MediaAssetService",
    "TranscodingService",
    "MediaStatus",
    "AssetType",
    
    # Rendering
    "RenderJob",
    "RenderOutput",
    "ExportPreset",
    "RenderWorker",
    "RenderQueueService",
    "RenderOrchestrator",
    "RenderStatus",
    "RenderPriority",
    
    # Audio
    "AudioAnalysisService",
    "AudioProcessingService",
    "AudioSegment",
    
    # Timelines
    "Timeline",
    "TimelineTrack",
    "TimelineClip",
    "TimelineService",
    "TimelineCompositionEngine",
    "TimelineStatus",
    "TrackType",
    
    # Workflows
    "Workflow",
    "WorkflowExecution",
    "WorkflowStep",
    "WorkflowService",
    "WorkflowExecutor",
    "WorkflowStatus",
    "ExecutionStatus",
]