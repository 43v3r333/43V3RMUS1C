"""
Render job tasks
"""
import subprocess
import logging
from typing import Optional

from ..celery_app import celery_app
from ..core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="render_media")
def render_media(
    self,
    job_id: str,
    input_path: str,
    output_path: str,
    parameters: Optional[dict] = None
):
    """Render media file using FFmpeg"""
    from ..core.database import SessionLocal
    from ..models.workflow import RenderJob
    
    db = SessionLocal()
    try:
        # Update job status
        job = db.query(RenderJob).filter(RenderJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return {"status": "error", "message": "Job not found"}
        
        job.status = "processing"
        job.worker_id = self.request.hostname
        db.commit()
        
        # Build FFmpeg command
        cmd = [
            settings.ffmpeg_path,
            "-i", input_path,
            "-y"  # Overwrite output
        ]
        
        # Add parameters
        if parameters:
            resolution = parameters.get("resolution")
            if resolution:
                cmd.extend(["-s", resolution])
            
            codec = parameters.get("codec")
            if codec:
                cmd.extend(["-c:v", codec])
            
            bitrate = parameters.get("bitrate")
            if bitrate:
                cmd.extend(["-b:v", bitrate])
        
        cmd.append(output_path)
        
        # Execute
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=settings.ffmpeg_timeout
        )
        
        if result.returncode == 0:
            job.status = "completed"
            job.progress = 1.0
            logger.info(f"Job {job_id} completed successfully")
        else:
            job.status = "failed"
            job.error_message = result.stderr
            logger.error(f"Job {job_id} failed: {result.stderr}")
        
        db.commit()
        return {"status": job.status, "job_id": job_id}
    
    except Exception as e:
        logger.error(f"Job {job_id} error: {str(e)}")
        job.status = "failed"
        job.error_message = str(e)
        db.commit()
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()


@celery_app.task(bind=True, name="transcode_audio")
def transcode_audio(
    self,
    job_id: str,
    input_path: str,
    output_path: str,
    format: str = "mp3",
    bitrate: str = "320k"
):
    """Transcode audio file"""
    from ..core.database import SessionLocal
    from ..models.workflow import RenderJob
    
    db = SessionLocal()
    try:
        job = db.query(RenderJob).filter(RenderJob.id == job_id).first()
        if not job:
            return {"status": "error", "message": "Job not found"}
        
        job.status = "processing"
        job.worker_id = self.request.hostname
        db.commit()
        
        cmd = [
            settings.ffmpeg_path,
            "-i", input_path,
            "-y",
            "-b:a", bitrate,
        ]
        
        if format == "mp3":
            cmd.extend(["-codec:a", "libmp3lame"])
        elif format == "aac":
            cmd.extend(["-codec:a", "aac"])
        elif format == "flac":
            cmd.extend(["-codec:a", "flac"])
        
        cmd.append(output_path)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        
        if result.returncode == 0:
            job.status = "completed"
            job.progress = 1.0
        else:
            job.status = "failed"
            job.error_message = result.stderr
        
        db.commit()
        return {"status": job.status, "job_id": job_id}
    
    finally:
        db.close()