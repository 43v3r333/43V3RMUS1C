"""
Render job tasks for media processing
"""
import logging
import subprocess
from typing import Optional

from celery import Task

from .celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="render_media")
def render_media(
    self: Task,
    job_id: str,
    input_path: str,
    output_path: str,
    parameters: Optional[dict] = None
) -> dict:
    """
    Render media file using FFmpeg with specified parameters.
    
    Args:
        job_id: UUID of the render job record
        input_path: Path to source media file
        output_path: Path for rendered output
        parameters: Optional FFmpeg parameters (resolution, codec, bitrate)
    """
    from app.core.database import get_db_session
    from app.models.workflow import RenderJob
    
    with get_db_session() as db:
        try:
            job = db.query(RenderJob).filter(RenderJob.id == job_id).first()
            if not job:
                logger.error(f"Job {job_id} not found")
                return {"status": "error", "message": "Job not found"}
            
            job.status = "processing"
            job.worker_id = self.request.hostname
            db.commit()
            
            # Build FFmpeg command
            cmd = _build_ffmpeg_command(input_path, output_path, parameters)
            
            # Execute with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour max
            )
            
            if result.returncode == 0:
                job.status = "completed"
                job.progress = 1.0
                job.output_path = output_path
                logger.info(f"Job {job_id} completed successfully")
                return {"status": "completed", "job_id": job_id}
            else:
                job.status = "failed"
                job.error_message = result.stderr
                logger.error(f"Job {job_id} failed: {result.stderr}")
                return {"status": "failed", "job_id": job_id, "error": result.stderr}
        
        except Exception as e:
            logger.error(f"Job {job_id} error: {e}")
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
            return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="transcode_audio")
def transcode_audio(
    self: Task,
    job_id: str,
    input_path: str,
    output_path: str,
    format: str = "mp3",
    bitrate: str = "320k"
) -> dict:
    """
    Transcode audio file to specified format and bitrate.
    """
    from app.core.database import get_db_session
    from app.models.workflow import RenderJob
    
    with get_db_session() as db:
        try:
            job = db.query(RenderJob).filter(RenderJob.id == job_id).first()
            if not job:
                return {"status": "error", "message": "Job not found"}
            
            job.status = "processing"
            job.worker_id = self.request.hostname
            db.commit()
            
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-y",
                "-b:a", bitrate,
            ]
            
            # Set codec based on format
            codec_map = {"mp3": "libmp3lame", "aac": "aac", "flac": "flac", "ogg": "libvorbis"}
            if format in codec_map:
                cmd.extend(["-codec:a", codec_map[format]])
            
            cmd.append(output_path)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            
            if result.returncode == 0:
                job.status = "completed"
                job.progress = 1.0
                job.output_path = output_path
            else:
                job.status = "failed"
                job.error_message = result.stderr
            
            db.commit()
            return {"status": job.status, "job_id": job_id}
        
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
            return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="generate_preview")
def generate_preview(
    self: Task,
    job_id: str,
    input_path: str,
    output_path: str,
    timestamp: str = "00:00:05",
    duration: int = 5
) -> dict:
    """
    Generate a short preview clip from media file.
    """
    from app.core.database import get_db_session
    from app.models.workflow import RenderJob
    
    with get_db_session() as db:
        try:
            job = db.query(RenderJob).filter(RenderJob.id == job_id).first()
            if not job:
                return {"status": "error", "message": "Job not found"}
            
            job.status = "processing"
            job.worker_id = self.request.hostname
            db.commit()
            
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-ss", timestamp,
                "-t", str(duration),
                "-y",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                job.status = "completed"
                job.progress = 1.0
                job.output_path = output_path
            else:
                job.status = "failed"
                job.error_message = result.stderr
            
            db.commit()
            return {"status": job.status, "job_id": job_id}
        
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
            return {"status": "error", "message": str(e)}


def _build_ffmpeg_command(input_path: str, output_path: str, parameters: Optional[dict]) -> list:
    """Build FFmpeg command from parameters"""
    cmd = ["ffmpeg", "-i", input_path, "-y"]
    
    if not parameters:
        cmd.append(output_path)
        return cmd
    
    # Resolution
    if resolution := parameters.get("resolution"):
        cmd.extend(["-s", resolution])
    
    # Video codec
    if codec := parameters.get("codec"):
        cmd.extend(["-c:v", codec])
    
    # Audio codec
    if audio_codec := parameters.get("audio_codec"):
        cmd.extend(["-c:a", audio_codec])
    
    # Bitrate
    if bitrate := parameters.get("bitrate"):
        cmd.extend(["-b:v", bitrate])
    
    # Audio bitrate
    if audio_bitrate := parameters.get("audio_bitrate"):
        cmd.extend(["-b:a", audio_bitrate])
    
    # Frame rate
    if fps := parameters.get("fps"):
        cmd.extend(["-r", str(fps)])
    
    # Custom FFmpeg args
    if custom_args := parameters.get("custom_args"):
        cmd.extend(custom_args)
    
    cmd.append(output_path)
    return cmd