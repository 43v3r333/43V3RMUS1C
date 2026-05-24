"""
Media Runtime Services - Operational media lifecycle management
"""
import os
import hashlib
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass

import subprocess
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...core.config import settings
from ...models.base import BaseModel
from .models import (
    MediaType,
    MediaStatus,
    MediaAsset,
    MediaFile,
    ProcessingResult,
    MediaValidationRule,
)
from ..events import EventBus, DomainEvent, EventType

logger = logging.getLogger(__name__)


class MediaRuntime:
    """
    Operational media runtime for media lifecycle management.
    Handles ingest, validation, metadata extraction, transcoding,
    preview generation, waveform generation, and asset fingerprinting.
    """
    
    SUPPORTED_AUDIO = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".aiff"}
    SUPPORTED_VIDEO = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}
    SUPPORTED_IMAGE = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}
    
    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        storage_path: Optional[str] = None,
    ):
        self.event_bus = event_bus
        self.storage_path = Path(storage_path or settings.media_storage_path)
        self._processing_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        
    async def initialize(self) -> None:
        """Initialize media runtime"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._running = True
        logger.info(f"MediaRuntime initialized at {self.storage_path}")
    
    async def shutdown(self) -> None:
        """Shutdown media runtime"""
        self._running = False
        logger.info("MediaRuntime shutdown")
    
    def detect_media_type(self, file_path: str) -> MediaType:
        """Detect media type from file extension"""
        ext = Path(file_path).suffix.lower()
        if ext in self.SUPPORTED_AUDIO:
            return MediaType.AUDIO
        elif ext in self.SUPPORTED_VIDEO:
            return MediaType.VIDEO
        elif ext in self.SUPPORTED_IMAGE:
            return MediaType.IMAGE
        return MediaType.OTHER
    
    def calculate_fingerprint(self, file_path: str) -> str:
        """Calculate file fingerprint (MD5 of first/last chunks + metadata)"""
        hasher = hashlib.md5()
        
        with open(file_path, "rb") as f:
            # First 64KB
            chunk = f.read(65536)
            hasher.update(chunk)
            
            # File size
            f.seek(0, 2)
            hasher.update(str(f.tell()).encode())
            
            # Last 64KB
            f.seek(-65536, 2)
            hasher.update(f.read())
        
        return hasher.hexdigest()
    
    async def validate_media(
        self,
        file_path: str,
        validation_rules: Optional[List[MediaValidationRule]] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Validate media file using FFprobe.
        Returns (is_valid, error_message).
        """
        if not os.path.exists(file_path):
            return False, "File not found"
        
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path,
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                return False, f"FFprobe error: {stderr.decode()}"
            
            return True, None
            
        except FileNotFoundError:
            return False, "FFprobe not available"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    async def extract_metadata(
        self,
        file_path: str,
        media_type: MediaType,
    ) -> Dict[str, Any]:
        """Extract metadata from media file using FFprobe"""
        metadata = {
            "format": None,
            "streams": [],
            "duration": None,
            "size": os.path.getsize(file_path),
        }
        
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path,
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                import json
                probe_data = json.loads(stdout.decode())
                metadata["format"] = probe_data.get("format", {})
                metadata["streams"] = probe_data.get("streams", [])
                metadata["duration"] = float(probe_data.get("format", {}).get("duration", 0))
                
                # Extract type-specific metadata
                for stream in metadata["streams"]:
                    if stream.get("codec_type") == "video":
                        metadata["width"] = stream.get("width")
                        metadata["height"] = stream.get("height")
                        metadata["frame_rate"] = self._parse_frame_rate(stream.get("r_frame_rate", ""))
                    elif stream.get("codec_type") == "audio":
                        metadata["sample_rate"] = stream.get("sample_rate")
                        metadata["channels"] = stream.get("channels")
                        metadata["bitrate"] = stream.get("bit_rate")
                    elif stream.get("codec_type") == "image":
                        metadata["width"] = stream.get("width")
                        metadata["height"] = stream.get("height")
                
        except Exception as e:
            logger.error(f"Metadata extraction error: {e}")
        
        return metadata
    
    def _parse_frame_rate(self, fr_str: str) -> float:
        """Parse FFmpeg frame rate format (e.g., '30000/1001')"""
        try:
            if "/" in fr_str:
                num, den = fr_str.split("/")
                return float(num) / float(den)
            return float(fr_str)
        except:
            return 30.0
    
    async def generate_thumbnail(
        self,
        file_path: str,
        media_type: MediaType,
        output_path: Optional[str] = None,
        timestamp: float = 0,
    ) -> Optional[str]:
        """Generate thumbnail from media file"""
        if media_type == MediaType.IMAGE:
            # For images, just copy as thumbnail
            output_path = output_path or str(Path(self.storage_path) / "thumbnails" / f"{Path(file_path).stem}_thumb.jpg")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            os.link(file_path, output_path)
            return output_path
        
        if media_type != MediaType.VIDEO:
            return None
        
        output_path = output_path or str(Path(self.storage_path) / "thumbnails" / f"{Path(file_path).stem}_thumb.jpg")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            cmd = [
                "ffmpeg",
                "-y",
                "-ss", str(timestamp),
                "-i", file_path,
                "-vframes", "1",
                "-q:v", "2",
                output_path,
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await result.communicate()
            
            if result.returncode == 0 and os.path.exists(output_path):
                return output_path
                
        except Exception as e:
            logger.error(f"Thumbnail generation error: {e}")
        
        return None
    
    async def transcode_media(
        self,
        input_path: str,
        output_path: str,
        codec: str = "libx264",
        bitrate: str = "5M",
        resolution: Optional[str] = None,
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> ProcessingResult:
        """Transcode media file"""
        start_time = datetime.utcnow()
        
        try:
            cmd = [
                "ffmpeg",
                "-y",
                "-i", input_path,
                "-c:v", codec,
                "-b:v", bitrate,
            ]
            
            if resolution:
                cmd.extend(["-vf", f"scale={resolution}"])
            
            # Get input duration for progress
            duration = await self._get_duration(input_path)
            if duration:
                cmd.extend(["-progress", "pipe:1"])
            
            cmd.append(output_path)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            # Monitor progress
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                
                if progress_callback and duration:
                    line_str = line.decode().strip()
                    if line_str.startswith("out_time_ms="):
                        try:
                            time_ms = int(line_str.split("=")[1])
                            progress = min(100, (time_ms / 1000 / duration) * 100)
                            await progress_callback(progress)
                        except:
                            pass
                
                if progress_callback:
                    await asyncio.sleep(0.1)
            
            await process.wait()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            if process.returncode == 0:
                return ProcessingResult(
                    success=True,
                    file_path=output_path,
                    processing_time=processing_time,
                )
            else:
                stderr = await process.stderr.read()
                return ProcessingResult(
                    success=False,
                    error=f"Transcode failed: {stderr.decode()}",
                    processing_time=processing_time,
                )
                
        except Exception as e:
            return ProcessingResult(
                success=False,
                error=str(e),
                processing_time=(datetime.utcnow() - start_time).total_seconds(),
            )
    
    async def _get_duration(self, file_path: str) -> Optional[float]:
        """Get media duration in seconds"""
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "csv=p=0",
                file_path,
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await result.communicate()
            
            if result.returncode == 0:
                return float(stdout.decode().strip())
                
        except:
            pass
        
        return None
    
    async def ingest_media(
        self,
        file_path: str,
        name: str,
        project_id: Optional[UUID] = None,
        track_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
    ) -> ProcessingResult:
        """
        Main ingest pipeline: validate, extract metadata, fingerprint, generate thumbnail.
        """
        start_time = datetime.utcnow()
        
        # Create media file descriptor
        media_file = MediaFile(
            path=file_path,
            name=name,
            size=os.path.getsize(file_path),
            mime_type=self._get_mime_type(file_path),
            media_type=self.detect_media_type(file_path),
        )
        
        # Validate
        is_valid, error = await self.validate_media(file_path)
        if not is_valid:
            return ProcessingResult(success=False, error=error)
        
        # Extract metadata
        metadata = await self.extract_metadata(file_path, media_file.media_type)
        
        # Calculate fingerprint
        fingerprint = self.calculate_fingerprint(file_path)
        
        # Generate thumbnail
        thumbnail_path = await self.generate_thumbnail(
            file_path, 
            media_file.media_type
        )
        
        # Update metadata with additional fields
        metadata["fingerprint"] = fingerprint
        metadata["thumbnail"] = thumbnail_path
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ProcessingResult(
            success=True,
            file_path=file_path,
            metadata=metadata,
            duration=int(metadata.get("duration", 0)) if metadata.get("duration") else None,
            dimensions=(metadata.get("width"), metadata.get("height")),
            processing_time=processing_time,
        )
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type from file extension"""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "application/octet-stream"


class MediaLifecycleManager:
    """
    Manages media asset lifecycle through status transitions.
    """
    
    VALID_TRANSITIONS = {
        MediaStatus.UPLOADED: [MediaStatus.VALIDATING],
        MediaStatus.VALIDATING: [MediaStatus.VALIDATED, MediaStatus.FAILED],
        MediaStatus.VALIDATED: [MediaStatus.ANALYZING],
        MediaStatus.ANALYZING: [MediaStatus.ANALYZED, MediaStatus.FAILED],
        MediaStatus.ANALYZED: [MediaStatus.TRANSFORMING],
        MediaStatus.TRANSFORMING: [MediaStatus.READY, MediaStatus.FAILED],
        MediaStatus.READY: [],  # Terminal state
        MediaStatus.FAILED: [],  # Terminal state (retryable)
    }
    
    def __init__(
        self,
        db: AsyncSession,
        event_bus: Optional[EventBus] = None,
    ):
        self.db = db
        self.event_bus = event_bus
    
    def can_transition(self, current: MediaStatus, target: MediaStatus) -> bool:
        """Check if status transition is valid"""
        return target in self.VALID_TRANSITIONS.get(current, [])
    
    async def transition(
        self,
        asset: MediaAsset,
        target_status: MediaStatus,
        error_message: Optional[str] = None,
    ) -> MediaAsset:
        """Transition asset to new status"""
        if not self.can_transition(MediaStatus(asset.status), target_status):
            raise ValueError(
                f"Invalid transition from {asset.status} to {target_status.value}"
            )
        
        asset.status = target_status.value
        
        if target_status == MediaStatus.FAILED and error_message:
            asset.processing_error = error_message
            asset.retry_count += 1
        
        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)
        
        # Emit event
        if self.event_bus:
            event = DomainEvent(
                event_type=EventType.MEDIA_TRANSFORMED if target_status != MediaStatus.FAILED else EventType.ERROR_OCCURRED,
                aggregate_id=asset.id,
                metadata={
                    "previous_status": asset.status,
                    "new_status": target_status.value,
                    "error": error_message,
                },
            )
            await self.event_bus.publish(event)
        
        return asset
    
    async def get_asset_status(self, asset_id: UUID) -> Optional[str]:
        """Get current status of asset"""
        result = await self.db.execute(
            select(MediaAsset).where(MediaAsset.id == asset_id)
        )
        asset = result.scalar_one_or_none()
        return asset.status if asset else None