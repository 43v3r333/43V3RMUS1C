"""
Render Domain Services
"""
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.ffmpeg_engine import get_ffmpeg_engine
from app.core.storage import get_storage_manager
from app.core.event_bus import EventType, EventDrivenService
from app.domains.rendering.models import (
    RenderJob,
    RenderOutput,
    RenderWorker,
    ExportPreset,
    RenderStatus,
    RenderPriority,
    RenderJobRepository,
    ExportPresetRepository,
)

logger = logging.getLogger(__name__)


class RenderQueueService(EventDrivenService):
    """
    Service for managing the distributed render queue.
    Handles job creation, prioritization, and worker assignment.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = RenderJobRepository(db)
        self.ffmpeg = get_ffmpeg_engine()
        self.storage = get_storage_manager()
        super().__init__()
    
    def create_render_job(
        self,
        name: str,
        job_type: str,
        input_path: str,
        output_path: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        priority: str = "normal",
        project_id: Optional[UUID] = None,
        timeline_id: Optional[UUID] = None,
        preset_id: Optional[UUID] = None,
        estimated_duration: Optional[int] = None
    ) -> RenderJob:
        """Create a new render job"""
        if not output_path:
            output_path = self._generate_output_path(input_path, parameters)
        
        job = RenderJob(
            name=name,
            job_type=job_type,
            status=RenderStatus.QUEUED.value,
            priority=priority,
            input_path=input_path,
            output_path=output_path,
            parameters=parameters or {},
            project_id=project_id,
            timeline_id=timeline_id,
            preset_id=preset_id,
            estimated_duration=estimated_duration
        )
        
        created = self.repository.create(job)
        
        # Emit event
        # Note: Need to make this async
        
        logger.info(f"Created render job {created.id}: {name}")
        
        return created
    
    def get_job(self, job_id: UUID) -> Optional[RenderJob]:
        return self.repository.get_by_id(job_id)
    
    def get_next_job(self, worker_id: str) -> Optional[RenderJob]:
        """Get next job for worker and mark as processing"""
        job = self.repository.get_next_job()
        
        if job:
            job.status = RenderStatus.PROCESSING.value
            job.worker_id = worker_id
            job.started_at = datetime.utcnow()
            self.db.commit()
            
            # Emit render started event
            # await self.emit(EventType.RENDER_STARTED, {...})
        
        return job
    
    def complete_job(
        self,
        job_id: UUID,
        output_path: Optional[str] = None,
        error: Optional[str] = None
    ) -> RenderJob:
        """Mark job as completed or failed"""
        job = self.get_job(job_id)
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        if error:
            job.status = RenderStatus.FAILED.value
            job.error_message = error
            job.completed_at = datetime.utcnow()
            
            if job.started_at:
                job.actual_duration = int((datetime.utcnow() - job.started_at).total_seconds())
        else:
            job.status = RenderStatus.COMPLETED.value
            job.progress = 100.0
            job.completed_at = datetime.utcnow()
            
            if output_path:
                job.output_path = output_path
            
            if job.started_at:
                job.actual_duration = int((datetime.utcnow() - job.started_at).total_seconds())
            
            # Create render output record
            self._create_render_output(job)
        
        self.db.commit()
        
        # Emit render completed/failed event
        # if error:
        #     await self.emit(EventType.RENDER_FAILED, {...})
        # else:
        #     await self.emit(EventType.RENDER_COMPLETED, {...})
        
        return job
    
    def update_progress(self, job_id: UUID, progress: float) -> RenderJob:
        """Update job progress"""
        job = self.get_job(job_id)
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.progress = min(progress, 100.0)
        self.db.commit()
        
        # Emit progress event
        # await self.emit(EventType.RENDER_PROGRESS, {...})
        
        return job
    
    def cancel_job(self, job_id: UUID) -> RenderJob:
        """Cancel a queued or processing job"""
        job = self.get_job(job_id)
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        if job.status in [RenderStatus.QUEUED.value, RenderStatus.PROCESSING.value, RenderStatus.RENDERING.value]:
            job.status = RenderStatus.CANCELLED.value
            job.completed_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Job {job_id} cancelled")
        
        return job
    
    def retry_job(self, job_id: UUID) -> RenderJob:
        """Retry a failed job"""
        job = self.get_job(job_id)
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        if job.status == RenderStatus.FAILED.value and job.retry_count < job.max_retries:
            job.status = RenderStatus.QUEUED.value
            job.retry_count += 1
            job.error_message = None
            job.completed_at = None
            job.progress = 0.0
            self.db.commit()
            
            logger.info(f"Job {job_id} queued for retry (attempt {job.retry_count})")
        
        return job
    
    def list_jobs(
        self,
        status: Optional[str] = None,
        job_type: Optional[str] = None,
        project_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[RenderJob]:
        return self.repository.list_jobs(status, job_type, project_id, limit, offset)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        return self.repository.get_queue_stats()
    
    def _create_render_output(self, job: RenderJob) -> None:
        """Create render output record for completed job"""
        if not job.output_path:
            return
        
        try:
            output = RenderOutput(
                render_job_id=job.id,
                name=job.name,
                output_path=job.output_path,
                is_primary=True
            )
            
            # Get output info
            info = self.ffmpeg.get_video_info(job.output_path)
            output.width = info.get("width")
            output.height = info.get("height")
            output.duration = info.get("duration")
            output.codec = info.get("video_codec") or info.get("audio_codec")
            output.bit_rate = info.get("bit_rate")
            output.file_size = info.get("size")
            
            self.db.add(output)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to create render output: {e}")
    
    def _generate_output_path(self, input_path: str, parameters: Optional[Dict]) -> str:
        """Generate output path for render"""
        input_name = Path(input_path).stem
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        format_ext = parameters.get("format", "mp4") if parameters else "mp4"
        
        return f"renders/{input_name}_{timestamp}.{format_ext}"


class RenderOrchestrator:
    """
    Orchestrator for distributed render execution.
    Manages worker assignment, job dependencies, and render graphs.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.queue_service = RenderQueueService(db)
        self.ffmpeg = get_ffmpeg_engine()
        self.storage = get_storage_manager()
    
    def execute_render(self, job_id: UUID, worker_id: str) -> Dict[str, Any]:
        """
        Execute a render job.
        Called by Celery worker.
        """
        job = self.queue_service.get_job(job_id)
        
        if not job:
            return {"status": "error", "message": "Job not found"}
        
        try:
            job.status = RenderStatus.RENDERING.value
            job.worker_id = worker_id
            self.db.commit()
            
            # Build FFmpeg command
            cmd = self._build_ffmpeg_command(job)
            
            # Execute
            logger.info(f"Executing render: {' '.join(cmd[:5])}...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            if result.returncode == 0:
                return self.queue_service.complete_job(job_id, job.output_path)
            else:
                return self.queue_service.complete_job(job_id, error=result.stderr)
            
        except Exception as e:
            logger.error(f"Render execution failed: {e}")
            return self.queue_service.complete_job(job_id, error=str(e))
    
    def _build_ffmpeg_command(self, job: RenderJob) -> List[str]:
        """Build FFmpeg command from job parameters"""
        cmd = ["ffmpeg", "-y", "-i", job.input_path]
        
        if parameters := job.parameters:
            # Resolution
            if resolution := parameters.get("resolution"):
                cmd.extend(["-s", resolution])
            
            # Video codec
            if video_codec := parameters.get("video_codec"):
                cmd.extend(["-c:v", video_codec])
            
            # Audio codec
            if audio_codec := parameters.get("audio_codec"):
                cmd.extend(["-c:a", audio_codec])
            
            # Bitrate
            if bitrate := parameters.get("bitrate"):
                cmd.extend(["-b:v", bitrate])
            
            # Frame rate
            if fps := parameters.get("fps"):
                cmd.extend(["-r", str(fps)])
            
            # Custom args
            if custom_args := parameters.get("custom_args"):
                cmd.extend(custom_args)
        
        # Get preset settings if available
        if job.preset:
            cmd.extend(["-preset", job.preset.ffmpeg_preset])
            cmd.extend(["-crf", str(job.preset.crf)])
            if job.preset.video_bitrate:
                cmd.extend(["-b:v", job.preset.video_bitrate])
        
        cmd.append(job.output_path)
        
        return cmd
    
    def get_worker_status(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """Get worker status"""
        worker = self.db.query(RenderWorker).filter(
            RenderWorker.worker_id == worker_id
        ).first()
        
        if not worker:
            return None
        
        return {
            "worker_id": worker.worker_id,
            "status": worker.status,
            "current_jobs": worker.current_jobs,
            "max_concurrent_jobs": worker.max_concurrent_jobs,
            "cpu_usage": worker.cpu_usage,
            "memory_usage": worker.memory_usage,
            "jobs_completed": worker.jobs_completed,
            "last_heartbeat": worker.last_heartbeat.isoformat() if worker.last_heartbeat else None
        }
    
    def update_worker_heartbeat(self, worker_id: str, metrics: Dict[str, Any]) -> None:
        """Update worker heartbeat and metrics"""
        worker = self.db.query(RenderWorker).filter(
            RenderWorker.worker_id == worker_id
        ).first()
        
        if worker:
            worker.last_heartbeat = datetime.utcnow()
            worker.cpu_usage = metrics.get("cpu_usage")
            worker.memory_usage = metrics.get("memory_usage")
            self.db.commit()
    
    def register_worker(
        self,
        worker_id: str,
        name: str,
        capabilities: Optional[Dict[str, Any]] = None,
        max_concurrent_jobs: int = 1
    ) -> RenderWorker:
        """Register a new render worker"""
        worker = RenderWorker(
            worker_id=worker_id,
            name=name,
            capabilities=capabilities,
            max_concurrent_jobs=max_concurrent_jobs,
            last_heartbeat=datetime.utcnow()
        )
        
        self.db.add(worker)
        self.db.commit()
        self.db.refresh(worker)
        
        return worker


class ExportService:
    """
    Service for managing export presets and platform-specific exports.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = ExportPresetRepository(db)
        self.ffmpeg = get_ffmpeg_engine()
    
    def get_preset(self, preset_id: UUID) -> Optional[ExportPreset]:
        return self.repository.get_by_id(preset_id)
    
    def get_preset_by_platform(self, platform: str) -> Optional[ExportPreset]:
        return self.repository.get_by_platform(platform)
    
    def list_presets(
        self,
        platform: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[ExportPreset]:
        return self.repository.list_presets(platform, category)
    
    def create_preset(
        self,
        name: str,
        display_name: str,
        platform: str,
        width: int,
        height: int,
        frame_rate: float = 30.0,
        video_codec: str = "libx264",
        audio_codec: str = "aac",
        **kwargs
    ) -> ExportPreset:
        """Create a new export preset"""
        preset = ExportPreset(
            name=name,
            display_name=display_name,
            platform=platform,
            width=width,
            height=height,
            frame_rate=frame_rate,
            video_codec=video_codec,
            audio_codec=audio_codec,
            **kwargs
        )
        
        return self.repository.create(preset)
    
    def export_to_platform(
        self,
        input_path: str,
        platform: str,
        output_name: Optional[str] = None
    ) -> str:
        """Export media to a specific platform using its preset"""
        preset = self.get_preset_by_platform(platform)
        
        if not preset:
            raise ValueError(f"No default preset found for platform: {platform}")
        
        if not output_name:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_name = f"{Path(input_path).stem}_{platform}_{timestamp}.mp4"
        
        output_path = f"exports/{platform}/{output_name}"
        full_output = Path(self.storage.storage.config.base_path) / output_path
        full_output.parent.mkdir(parents=True, exist_ok=True)
        
        # Build FFmpeg command
        cmd = self._build_export_command(preset, input_path, str(full_output))
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        
        if result.returncode != 0:
            raise RuntimeError(f"Export failed: {result.stderr}")
        
        return str(full_output)
    
    def _build_export_command(
        self,
        preset: ExportPreset,
        input_path: str,
        output_path: str
    ) -> List[str]:
        """Build FFmpeg command for export"""
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", f"scale={preset.width}:{preset.height}:force_original_aspect_ratio=decrease,pad={preset.width}:{preset.height}:(ow-iw)/2:(oh-ih)/2",
            "-r", str(preset.frame_rate),
            "-c:v", preset.video_codec,
        ]
        
        if preset.video_bitrate:
            cmd.extend(["-b:v", preset.video_bitrate])
        
        cmd.extend([
            "-preset", preset.ffmpeg_preset,
            "-crf", str(preset.crf),
            "-c:a", preset.audio_codec,
            "-b:a", preset.audio_bitrate,
            "-ar", str(preset.audio_sample_rate),
        ])
        
        if preset.additional_args:
            for arg in preset.additional_args:
                cmd.extend(arg)
        
        cmd.append(output_path)
        
        return cmd
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        return [p.value for p in ExportPlatform]