"""
Render queue service for managing render jobs.
Handles job creation, prioritization, and execution monitoring.
"""
import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

from app.core.ffmpeg_engine import get_ffmpeg_engine, FFmpegOutput, FFmpegInput, RenderRequest
from app.core.storage import get_storage_manager
from app.models.workflow import RenderJob
from app.models.media_execution import RenderOutput, ExportPreset, ExportPresetModel

logger = logging.getLogger(__name__)


class RenderQueueService:
    """
    Service for managing the render queue.
    Handles job creation, prioritization, and monitoring.
    """
    
    PRIORITY_MAP = {
        "low": 1,
        "normal": 5,
        "high": 10,
        "urgent": 20
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.ffmpeg = get_ffmpeg_engine()
        self.storage = get_storage_manager()
    
    def create_render_job(
        self,
        name: str,
        job_type: str,
        input_path: str,
        output_path: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        priority: str = "normal",
        project_id: Optional[uuid.UUID] = None,
        estimated_duration: Optional[int] = None
    ) -> RenderJob:
        """
        Create a new render job.
        
        Args:
            name: Job name
            job_type: Type of render (video, audio, image, export)
            input_path: Source file path
            output_path: Target output path
            parameters: FFmpeg parameters
            priority: Job priority (low, normal, high, urgent)
            project_id: Associated project
            estimated_duration: Estimated time in seconds
            
        Returns:
            Created RenderJob
        """
        # Generate output path if not provided
        if not output_path:
            output_path = self._generate_output_path(input_path, parameters)
        
        job = RenderJob(
            name=name,
            job_type=job_type,
            status="queued",
            priority=priority,
            input_path=input_path,
            output_path=output_path,
            parameters=parameters or {},
            project_id=project_id,
            estimated_duration=estimated_duration
        )
        
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        logger.info(f"Created render job {job.id}: {name}")
        
        return job
    
    def get_job(self, job_id: uuid.UUID) -> Optional[RenderJob]:
        """Get render job by ID"""
        return self.db.query(RenderJob).filter(RenderJob.id == job_id).first()
    
    def get_next_job(self, worker_id: str) -> Optional[RenderJob]:
        """
        Get next job from queue for processing.
        
        Args:
            worker_id: Worker identifier
            
        Returns:
            Next RenderJob or None if queue is empty
        """
        # Get highest priority queued job
        job = (
            self.db.query(RenderJob)
            .filter(RenderJob.status == "queued")
            .order_by(RenderJob.priority.desc(), RenderJob.created_at.asc())
            .first()
        )
        
        if job:
            job.status = "processing"
            job.worker_id = worker_id
            job.started_at = datetime.utcnow()
            self.db.commit()
        
        return job
    
    def complete_job(
        self,
        job_id: uuid.UUID,
        output_path: Optional[str] = None,
        error: Optional[str] = None
    ) -> RenderJob:
        """
        Mark job as completed or failed.
        
        Args:
            job_id: Job ID
            output_path: Final output path
            error: Error message if failed
            
        Returns:
            Updated RenderJob
        """
        job = self.get_job(job_id)
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        if error:
            job.status = "failed"
            job.error_message = error
            job.completed_at = datetime.utcnow()
            
            # Calculate actual duration
            if job.started_at:
                job.actual_duration = int(
                    (datetime.utcnow() - job.started_at).total_seconds()
                )
        else:
            job.status = "completed"
            job.progress = 100.0
            job.completed_at = datetime.utcnow()
            
            if output_path:
                job.output_path = output_path
            
            # Calculate actual duration
            if job.started_at:
                job.actual_duration = int(
                    (datetime.utcnow() - job.started_at).total_seconds()
                )
            
            # Create render output record
            self._create_render_output(job)
        
        self.db.commit()
        logger.info(f"Job {job_id} completed: {job.status}")
        
        return job
    
    def update_progress(self, job_id: uuid.UUID, progress: float) -> RenderJob:
        """Update job progress"""
        job = self.get_job(job_id)
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.progress = min(progress, 100.0)
        self.db.commit()
        
        return job
    
    def cancel_job(self, job_id: uuid.UUID) -> RenderJob:
        """Cancel a queued or processing job"""
        job = self.get_job(job_id)
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        if job.status in ["queued", "processing"]:
            job.status = "cancelled"
            job.completed_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Job {job_id} cancelled")
        else:
            raise ValueError(f"Cannot cancel job in status: {job.status}")
        
        return job
    
    def retry_job(self, job_id: uuid.UUID) -> RenderJob:
        """Retry a failed job"""
        job = self.get_job(job_id)
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        if job.status == "failed" and job.retry_count < job.max_retries:
            job.status = "queued"
            job.retry_count += 1
            job.error_message = None
            job.completed_at = None
            self.db.commit()
            
            logger.info(f"Job {job_id} queued for retry (attempt {job.retry_count})")
        else:
            raise ValueError(f"Cannot retry job: status={job.status}, retries={job.retry_count}")
        
        return job
    
    def list_jobs(
        self,
        status: Optional[str] = None,
        job_type: Optional[str] = None,
        project_id: Optional[uuid.UUID] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[RenderJob]:
        """List render jobs with filters"""
        query = self.db.query(RenderJob)
        
        if status:
            query = query.filter(RenderJob.status == status)
        if job_type:
            query = query.filter(RenderJob.job_type == job_type)
        if project_id:
            query = query.filter(RenderJob.project_id == project_id)
        
        return query.order_by(
            RenderJob.priority.desc(),
            RenderJob.created_at.asc()
        ).offset(offset).limit(limit).all()
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get render queue statistics"""
        jobs = self.db.query(RenderJob).all()
        
        stats = {
            "total": len(jobs),
            "queued": sum(1 for j in jobs if j.status == "queued"),
            "processing": sum(1 for j in jobs if j.status == "processing"),
            "completed": sum(1 for j in jobs if j.status == "completed"),
            "failed": sum(1 for j in jobs if j.status == "failed"),
            "cancelled": sum(1 for j in jobs if j.status == "cancelled"),
        }
        
        # Calculate average processing time
        completed_jobs = [j for j in jobs if j.actual_duration]
        if completed_jobs:
            stats["avg_duration"] = sum(j.actual_duration for j in completed_jobs) / len(completed_jobs)
        else:
            stats["avg_duration"] = 0
        
        return stats
    
    def _create_render_output(self, job: RenderJob):
        """Create render output record for completed job"""
        if not job.output_path:
            return
        
        try:
            output = RenderOutput(
                render_job_id=job.id,
                name=job.name,
                output_path=job.output_path
            )
            
            # Get output file info
            info = self.ffmpeg.get_video_info(job.output_path)
            output.width = info.get("width")
            output.height = info.get("height")
            output.duration = info.get("duration")
            output.codec = info.get("video_codec") or info.get("audio_codec")
            output.bit_rate = info.get("bit_rate")
            
            self.db.add(output)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to create render output: {e}")
    
    def _generate_output_path(self, input_path: str, parameters: Optional[Dict]) -> str:
        """Generate output path for render"""
        from pathlib import Path
        
        input_name = Path(input_path).stem
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Determine format from parameters
        format_ext = parameters.get("format", "mp4") if parameters else "mp4"
        
        return f"renders/{input_name}_{timestamp}.{format_ext}"


class ExportService:
    """
    Service for exporting renders to social media platforms.
    Handles preset management and platform-specific exports.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ffmpeg = get_ffmpeg_engine()
        self.storage = get_storage_manager()
    
    def get_preset(self, preset_id: uuid.UUID) -> Optional[ExportPresetModel]:
        """Get export preset by ID"""
        return self.db.query(ExportPresetModel).filter(ExportPresetModel.id == preset_id).first()
    
    def get_preset_by_platform(self, platform: str) -> Optional[ExportPresetModel]:
        """Get default export preset for a platform"""
        return (
            self.db.query(ExportPresetModel)
            .filter(
                ExportPresetModel.platform == platform,
                ExportPresetModel.is_active == True,
                ExportPresetModel.is_default == True
            )
            .first()
        )
    
    def list_presets(
        self,
        platform: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[ExportPresetModel]:
        """List export presets"""
        query = self.db.query(ExportPresetModel).filter(ExportPresetModel.is_active == True)
        
        if platform:
            query = query.filter(ExportPresetModel.platform == platform)
        if category:
            query = query.filter(ExportPresetModel.category == category)
        
        return query.all()
    
    def create_preset(
        self,
        name: str,
        display_name: str,
        platform: str,
        width: int,
        height: int,
        frame_rate: float = 30.0,
        video_codec: str = "libx264",
        video_bitrate: Optional[str] = None,
        audio_codec: str = "aac",
        audio_bitrate: str = "192k",
        **kwargs
    ) -> ExportPresetModel:
        """Create a new export preset"""
        preset = ExportPresetModel(
            name=name,
            display_name=display_name,
            platform=platform,
            width=width,
            height=height,
            frame_rate=frame_rate,
            video_codec=video_codec,
            video_bitrate=video_bitrate,
            audio_codec=audio_codec,
            audio_bitrate=audio_bitrate,
            **kwargs
        )
        
        self.db.add(preset)
        self.db.commit()
        self.db.refresh(preset)
        
        return preset
    
    def export_to_platform(
        self,
        input_path: str,
        platform: str,
        output_name: Optional[str] = None
    ) -> str:
        """
        Export media to a specific platform using its preset.
        
        Args:
            input_path: Source file path
            platform: Target platform (tiktok, youtube, instagram)
            output_name: Optional output filename
            
        Returns:
            Output file path
        """
        preset = self.get_preset_by_platform(platform)
        
        if not preset:
            raise ValueError(f"No default preset found for platform: {platform}")
        
        # Generate output path
        if not output_name:
            from pathlib import Path
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_name = f"{Path(input_path).stem}_{platform}_{timestamp}.mp4"
        
        output_path = f"exports/{platform}/{output_name}"
        full_output_path = Path(self.storage.storage.config.base_path) / output_path
        full_output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build FFmpeg command
        cmd = self._build_export_command(preset, input_path, str(full_output_path))
        
        # Execute
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        
        if result.returncode != 0:
            raise RuntimeError(f"Export failed: {result.stderr}")
        
        return str(full_output_path)
    
    def _build_export_command(
        self,
        preset: ExportPresetModel,
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
        
        # Add platform-specific watermark if required
        if preset.requires_watermark:
            # Would add watermark filter here
            pass
        
        # Add additional args
        if preset.additional_args:
            for arg in preset.additional_args:
                cmd.extend(arg)
        
        cmd.append(output_path)
        
        return cmd
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        return [
            "tiktok",
            "youtube_shorts",
            "instagram_reels",
            "twitter",
            "facebook",
            "linkedin"
        ]