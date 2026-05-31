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
                job.progress = 100.0
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
                job.progress = 100.0
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
                job.progress = 100.0
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


@celery_app.task(bind=True, name="process_media_asset")
def process_media_asset(
    self: Task,
    asset_id: str
) -> dict:
    """
    Process a media asset to extract metadata and generate thumbnails.
    
    This is the main entry point for the media ingestion pipeline.
    """
    from app.core.database import get_db_session
    from app.core.ffmpeg_engine import get_ffmpeg_engine
    from app.models.media_execution import MediaAsset, AssetStatus
    
    engine = get_ffmpeg_engine()
    
    with get_db_session() as db:
        try:
            asset = db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
            if not asset:
                logger.error(f"Asset {asset_id} not found")
                return {"status": "error", "message": "Asset not found"}
            
            asset.status = AssetStatus.PROCESSING.value
            db.commit()
            
            # Get full path
            from pathlib import Path
            storage_base = Path("./storage")
            full_path = storage_base / asset.file_path
            
            # Probe media
            logger.info(f"Probing media: {full_path}")
            probe = engine.probe(str(full_path))
            
            # Update asset metadata
            asset.duration = probe.duration
            asset.width = probe.width
            asset.height = probe.height
            asset.frame_rate = probe.frame_rate
            asset.bit_rate = probe.bit_rate
            
            if probe.audio_stream:
                asset.sample_rate = probe.audio_sample_rate
                asset.channels = probe.audio_channels
            
            asset.codec = probe.video_codec or probe.audio_codec
            
            # Store technical specs
            asset.metadata = {
                "format": probe.format,
                "streams": probe.streams,
                "probe_time": self.request.hostname
            }
            
            # Generate thumbnail if video
            if asset.asset_type == "video" and probe.video_stream:
                thumb_path = storage_base / f"thumbnails/{asset.id}.jpg"
                thumb_path.parent.mkdir(parents=True, exist_ok=True)
                
                success = engine.create_thumbnail(
                    str(full_path),
                    str(thumb_path),
                    timestamp="00:00:01"
                )
                
                if success:
                    asset.thumbnail_path = f"thumbnails/{asset.id}.jpg"
                    logger.info(f"Generated thumbnail: {thumb_path}")
            
            asset.status = AssetStatus.READY.value
            db.commit()
            
            logger.info(f"Asset {asset_id} processed successfully")
            return {"status": "completed", "asset_id": asset_id}
            
        except Exception as e:
            logger.error(f"Asset processing failed: {e}")
            if 'asset' in locals():
                asset.status = AssetStatus.FAILED.value
                asset.error_message = str(e)
                db.commit()
            return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="analyze_audio")
def analyze_audio(
    self: Task,
    asset_id: str
) -> dict:
    """
    Perform audio analysis on a media asset.
    Extracts BPM, beats, waveform, and other audio features.
    """
    from app.core.database import get_db_session
    from app.core.audio_analyzer import get_audio_analyzer
    from app.models.media_execution import MediaAsset, AudioAnalysis, WaveformData, AssetStatus
    
    analyzer = get_audio_analyzer()
    
    with get_db_session() as db:
        try:
            asset = db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
            if not asset:
                return {"status": "error", "message": "Asset not found"}
            
            if asset.asset_type != "audio":
                return {"status": "skipped", "message": "Not an audio asset"}
            
            # Get full path
            from pathlib import Path
            storage_base = Path("./storage")
            full_path = storage_base / asset.file_path
            
            logger.info(f"Analyzing audio: {full_path}")
            
            # Perform analysis
            features = analyzer.analyze(str(full_path))
            
            # Store analysis results
            analysis = AudioAnalysis(
                asset_id=asset.id,
                bpm=features.bpm,
                bpm_confidence=features.bpm_confidence,
                beats=features.beats,
                beat_confidence=features.beat_confidence,
                key=features.key,
                key_confidence=features.key_confidence,
                energy=features.energy,
                valence=features.valence,
                danceability=features.danceability,
                intro_start=features.intro_start,
                intro_end=features.intro_end,
                hook_start=features.hook_start,
                hook_end=features.hook_end,
                outro_start=features.outro_start,
                outro_end=features.outro_end,
                silent_regions=features.silent_regions,
                spectral_centroid=features.spectral_centroid,
                spectral_rolloff=features.spectral_rolloff,
                loudness=features.loudness,
                dynamic_range=features.dynamic_range,
                confidence_score=features.confidence_score
            )
            
            db.add(analysis)
            
            # Generate waveform
            waveform = analyzer.generate_waveform(str(full_path))
            
            waveform_data = WaveformData(
                asset_id=asset.id,
                peaks_left=waveform.peaks,
                peaks_mono=waveform.peaks,
                peaks_right=waveform.peaks,
                duration=waveform.duration,
                samples_per_second=waveform.samples_per_second,
                peak_amplitude=max(waveform.peaks) if waveform.peaks else 0
            )
            
            db.add(waveform_data)
            
            # Update asset with waveform path
            asset.waveform_path = f"waveforms/{asset.id}.json"
            db.commit()
            
            logger.info(f"Audio analysis completed for {asset_id}: BPM={features.bpm}")
            return {
                "status": "completed",
                "asset_id": asset_id,
                "bpm": features.bpm,
                "key": features.key
            }
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="transcode_media")
def transcode_media(
    self: Task,
    job_id: str
) -> dict:
    """
    Transcode media file using transcoding job configuration.
    """
    from app.core.database import get_db_session
    from app.core.ffmpeg_engine import get_ffmpeg_engine
    from app.models.media_execution import TranscodingJob, TranscodingStatus
    
    engine = get_ffmpeg_engine()
    
    with get_db_session() as db:
        try:
            job = db.query(TranscodingJob).filter(TranscodingJob.id == job_id).first()
            if not job:
                return {"status": "error", "message": "Transcoding job not found"}
            
            job.status = TranscodingStatus.IN_PROGRESS.value
            job.started_at = self.request.id
            job.worker_id = self.request.hostname
            db.commit()
            
            from pathlib import Path
            storage_base = Path("./storage")
            
            input_path = storage_base / job.input_path
            output_path = storage_base / f"transcoded/{job.asset_id}/{Path(job.input_path).stem}.{job.target_format}"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Build FFmpeg command
            cmd = ["ffmpeg", "-y", "-i", str(input_path)]
            
            if job.target_codec:
                cmd.extend(["-c:v", job.target_codec])
            
            if job.target_resolution:
                cmd.extend(["-s", job.target_resolution])
            
            if job.target_bitrate:
                cmd.extend(["-b:v", job.target_bitrate])
            
            cmd.append(str(output_path))
            
            logger.info(f"Transcoding: {' '.join(cmd[:5])}...")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0:
                job.status = TranscodingStatus.COMPLETED.value
                job.output_path = str(output_path)
                job.completed_at = self.request.id
                
                # Get output info
                output_info = engine.get_video_info(str(output_path))
                job.output_size = output_info.get("size")
                job.output_codec = output_info.get("video_codec")
                
                logger.info(f"Transcoding completed: {output_path}")
            else:
                job.status = TranscodingStatus.FAILED.value
                job.error_message = result.stderr
            
            db.commit()
            return {"status": job.status, "job_id": job_id}
            
        except Exception as e:
            logger.error(f"Transcoding failed: {e}")
            if 'job' in locals():
                job.status = TranscodingStatus.FAILED.value
                job.error_message = str(e)
                db.commit()
            return {"status": "error", "message": str(e)}


@celery_app.task(bind=True, name="generate_waveform")
def generate_waveform(
    self: Task,
    asset_id: str,
    output_format: str = "json"
) -> dict:
    """
    Generate waveform data for an audio asset.
    """
    from app.core.database import get_db_session
    from app.core.audio_analyzer import get_audio_analyzer
    from app.core.storage import get_storage_manager
    from app.models.media_execution import MediaAsset, WaveformData
    import json
    
    analyzer = get_audio_analyzer()
    storage = get_storage_manager()
    
    with get_db_session() as db:
        try:
            asset = db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
            if not asset:
                return {"status": "error", "message": "Asset not found"}
            
            from pathlib import Path
            storage_base = Path("./storage")
            full_path = storage_base / asset.file_path
            
            # Generate waveform
            waveform = analyzer.generate_waveform(str(full_path))
            
            # Store waveform data
            waveform_data = WaveformData(
                asset_id=asset.id,
                peaks_left=waveform.peaks,
                peaks_mono=waveform.peaks,
                duration=waveform.duration,
                samples_per_second=waveform.samples_per_second
            )
            
            db.add(waveform_data)
            
            # Save waveform JSON
            waveform_path = storage_base / f"waveforms/{asset.id}.json"
            waveform_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(waveform_path, "w") as f:
                f.write(waveform.to_json())
            
            # Update asset
            asset.waveform_path = f"waveforms/{asset.id}.json"
            db.commit()
            
            logger.info(f"Waveform generated for {asset_id}")
            return {"status": "completed", "asset_id": asset_id}
            
        except Exception as e:
            logger.error(f"Waveform generation failed: {e}")
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