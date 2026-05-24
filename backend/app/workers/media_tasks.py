"""
Media Worker Tasks - Dedicated media processing workers
"""
import logging
from typing import Dict, List, Optional, Any
from uuid import UUID

from celery import Task
from celery.utils.log import get_task_logger

from .celery_app import celery_app
from ..core.config import settings
from ..core.database import AsyncSessionLocal
from ..domains.media import MediaRuntime, MediaLifecycleManager
from ..domains.media.models import MediaType, MediaStatus
from ..domains.audio import AudioIntelligenceEngine
from ..domains.workers import WorkerOrchestrator, WorkerRegistry, WorkerMetrics, WorkerStatus, WorkerType
from ..domains.events import EventBus, DomainEvent, EventType

logger = get_task_logger(__name__)


class MediaProcessingTask(Task):
    """Base task for media processing"""
    _media_runtime: Optional[MediaRuntime] = None
    _audio_engine: Optional[AudioIntelligenceEngine] = None
    _worker_registry: Optional[WorkerRegistry] = None
    
    @property
    def media_runtime(self) -> MediaRuntime:
        if self._media_runtime is None:
            self._media_runtime = MediaRuntime(storage_path=settings.media_storage_path)
        return self._media_runtime
    
    @property
    def audio_engine(self) -> AudioIntelligenceEngine:
        if self._audio_engine is None:
            self._audio_engine = AudioIntelligenceEngine(storage_path=settings.media_storage_path)
        return self._audio_engine
    
    @property
    def worker_registry(self) -> WorkerRegistry:
        if self._worker_registry is None:
            self._worker_registry = WorkerRegistry()
        return self._worker_registry


@celery_app.task(bind=True, base=MediaProcessingTask, name="media.ingest")
async def ingest_media(
    self,
    file_path: str,
    name: str,
    media_type: str,
    project_id: Optional[str] = None,
    track_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Ingest media file: validate, extract metadata, fingerprint, generate thumbnail.
    """
    from uuid import UUID as UUIDParser
    
    logger.info(f"Starting media ingest: {name}")
    
    try:
        runtime = self.media_runtime
        
        # Run ingest pipeline
        result = await runtime.ingest_media(
            file_path=file_path,
            name=name,
            project_id=UUIDParser(project_id) if project_id else None,
            track_id=UUIDParser(track_id) if track_id else None,
            user_id=UUIDParser(user_id) if user_id else None,
        )
        
        if result.success:
            logger.info(f"Media ingested successfully: {result.file_path}")
            return {
                "success": True,
                "file_path": result.file_path,
                "metadata": result.metadata,
                "duration": result.duration,
                "dimensions": result.dimensions,
            }
        else:
            logger.error(f"Media ingest failed: {result.error}")
            return {
                "success": False,
                "error": result.error,
            }
            
    except Exception as e:
        logger.error(f"Media ingest error: {e}")
        return {
            "success": False,
            "error": str(e),
        }


@celery_app.task(bind=True, base=MediaProcessingTask, name="media.transcode")
async def transcode_media(
    self,
    input_path: str,
    output_path: str,
    codec: str = "libx264",
    bitrate: str = "5M",
    resolution: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Transcode media file.
    """
    logger.info(f"Starting transcode: {input_path} -> {output_path}")
    
    try:
        runtime = self.media_runtime
        
        # Run transcode with progress callback
        async def progress_callback(progress: float):
            self.update_state(
                state="PROGRESS",
                meta={"progress": progress}
            )
        
        result = await runtime.transcode_media(
            input_path=input_path,
            output_path=output_path,
            codec=codec,
            bitrate=bitrate,
            resolution=resolution,
            progress_callback=progress_callback,
        )
        
        return {
            "success": result.success,
            "output_path": result.file_path,
            "processing_time": result.processing_time,
            "error": result.error,
        }
        
    except Exception as e:
        logger.error(f"Transcode error: {e}")
        return {
            "success": False,
            "error": str(e),
        }


@celery_app.task(bind=True, base=MediaProcessingTask, name="media.analyze")
async def analyze_media(
    self,
    file_path: str,
    media_type: str,
    asset_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze media file - extract metadata, generate waveforms.
    """
    from uuid import UUID as UUIDParser
    
    logger.info(f"Starting media analysis: {file_path}")
    
    try:
        runtime = self.media_runtime
        audio_engine = self.audio_engine
        
        metadata = await runtime.extract_metadata(
            file_path, 
            MediaType(media_type)
        )
        
        # Generate waveform for audio
        waveform_data = {}
        if media_type == "audio":
            waveform_data = await audio_engine.generate_waveform(file_path)
        
        return {
            "success": True,
            "metadata": metadata,
            "waveform": waveform_data,
        }
        
    except Exception as e:
        logger.error(f"Media analysis error: {e}")
        return {
            "success": False,
            "error": str(e),
        }


@celery_app.task(bind=True, base=MediaProcessingTask, name="media.generate_thumbnail")
async def generate_thumbnail(
    self,
    file_path: str,
    media_type: str,
    output_path: Optional[str] = None,
    timestamp: float = 0,
) -> Dict[str, Any]:
    """
    Generate thumbnail from media file.
    """
    logger.info(f"Generating thumbnail for: {file_path}")
    
    try:
        runtime = self.media_runtime
        
        thumbnail_path = await runtime.generate_thumbnail(
            file_path,
            MediaType(media_type),
            output_path,
            timestamp,
        )
        
        if thumbnail_path:
            return {
                "success": True,
                "thumbnail_path": thumbnail_path,
            }
        else:
            return {
                "success": False,
                "error": "Thumbnail generation failed",
            }
            
    except Exception as e:
        logger.error(f"Thumbnail generation error: {e}")
        return {
            "success": False,
            "error": str(e),
        }


@celery_app.task(bind=True, base=MediaProcessingTask, name="audio.analyze")
async def analyze_audio(
    self,
    file_path: str,
    asset_id: str,
) -> Dict[str, Any]:
    """
    Full audio analysis using Librosa.
    """
    from uuid import UUID as UUIDParser
    
    logger.info(f"Starting audio analysis: {file_path}")
    
    try:
        audio_engine = self.audio_engine
        
        analysis = await audio_engine.analyze_audio(
            file_path=file_path,
            media_asset_id=UUIDParser(asset_id),
        )
        
        return {
            "success": True,
            "analysis": {
                "bpm": analysis.bpm,
                "bpm_confidence": analysis.bpm_confidence,
                "beat_markers": analysis.beat_markers,
                "transient_markers": analysis.transient_markers,
                "silence_regions": analysis.silence_regions,
                "key_signature": analysis.key_signature,
                "mode": analysis.mode,
            },
        }
        
    except Exception as e:
        logger.error(f"Audio analysis error: {e}")
        return {
            "success": False,
            "error": str(e),
        }


@celery_app.task(bind=True, base=MediaProcessingTask, name="audio.waveform")
async def generate_waveform(
    self,
    file_path: str,
    samples_per_pixel: int = 512,
    display_width: int = 1000,
) -> Dict[str, Any]:
    """
    Generate waveform data for visualization.
    """
    logger.info(f"Generating waveform for: {file_path}")
    
    try:
        audio_engine = self.audio_engine
        
        waveform_data = await audio_engine.generate_waveform(
            file_path=file_path,
            samples_per_pixel=samples_per_pixel,
            display_width=display_width,
        )
        
        return {
            "success": True,
            "waveform": waveform_data,
        }
        
    except Exception as e:
        logger.error(f"Waveform generation error: {e}")
        return {
            "success": False,
            "error": str(e),
        }


@celery_app.task(bind=True, base=MediaProcessingTask, name="worker.heartbeat")
async def worker_heartbeat(
    self,
    worker_id: str,
    worker_type: str = "media",
) -> Dict[str, Any]:
    """
    Process worker heartbeat and update worker status.
    """
    logger.debug(f"Processing heartbeat for worker: {worker_id}")
    
    try:
        registry = self.worker_registry
        
        # Update heartbeat
        registry.update_heartbeat(worker_id)
        
        return {
            "success": True,
            "worker_id": worker_id,
            "timestamp": None,
        }
        
    except Exception as e:
        logger.error(f"Heartbeat error: {e}")
        return {
            "success": False,
            "error": str(e),
        }


@celery_app.task(bind=True, base=MediaProcessingTask, name="health_check")
async def health_check(self) -> Dict[str, Any]:
    """
    Health check task for media workers.
    """
    return {
        "status": "healthy",
        "worker_type": "media",
    }