"""
Media service layer for asset management and processing.
Handles asset lifecycle, metadata extraction, and asset operations.
"""
import hashlib
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO

from sqlalchemy.orm import Session

from app.core.ffmpeg_engine import get_ffmpeg_engine, MediaProbeResult
from app.core.storage import get_storage_manager, StorageFile
from app.models.media_execution import (
    MediaAsset,
    AssetStatus,
    AssetType,
    TranscodingJob,
    TranscodingStatus,
    WaveformData,
    AudioAnalysis
)
from app.repositories.media_asset_repository import MediaAssetRepository

logger = logging.getLogger(__name__)


class MediaAssetService:
    """
    Service for managing media assets.
    Handles upload, processing, and asset lifecycle.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = MediaAssetRepository(db)
        self.ffmpeg = get_ffmpeg_engine()
        self.storage = get_storage_manager()
    
    async def create_asset_from_upload(
        self,
        file_data: BinaryIO,
        filename: str,
        content_type: str,
        created_by_id: uuid.UUID,
        project_id: Optional[uuid.UUID] = None,
        artist_id: Optional[uuid.UUID] = None
    ) -> MediaAsset:
        """
        Create a new media asset from an uploaded file.
        
        Args:
            file_data: File data stream
            filename: Original filename
            content_type: MIME type
            created_by_id: User who uploaded the file
            project_id: Optional project association
            artist_id: Optional artist association
            
        Returns:
            Created MediaAsset
        """
        # Read file for checksum
        content = file_data.read()
        file_data.seek(0)  # Reset for storage
        
        # Calculate checksum
        checksum = hashlib.md5(content).hexdigest()
        
        # Determine asset type
        asset_type = self._determine_asset_type(content_type, filename)
        
        # Generate storage path
        storage_path = self.storage.generate_storage_path(asset_type, Path(filename).suffix)
        
        # Upload to storage
        storage_file = await self.storage.save_upload(
            file_data,
            filename,
            content_type,
            storage_path
        )
        
        # Create asset record
        asset = MediaAsset(
            name=Path(filename).stem,
            slug=self._generate_slug(Path(filename).stem),
            original_filename=filename,
            file_path=storage_file.path,
            file_size=storage_file.size,
            mime_type=content_type,
            md5_hash=checksum,
            asset_type=asset_type,
            status=AssetStatus.UPLOADING.value,
            project_id=project_id,
            artist_id=artist_id,
            created_by_id=created_by_id
        )
        
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        
        # Start background processing
        await self._process_asset_async(asset.id)
        
        return asset
    
    async def _process_asset_async(self, asset_id: uuid.UUID):
        """Process asset in background (called by Celery task)"""
        # This would trigger a Celery task to extract metadata
        pass
    
    def process_asset(self, asset_id: uuid.UUID) -> MediaAsset:
        """
        Process asset to extract metadata and generate thumbnails.
        Called by Celery worker.
        
        Args:
            asset_id: Asset to process
            
        Returns:
            Updated MediaAsset
        """
        asset = self.db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
        
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")
        
        try:
            asset.status = AssetStatus.PROCESSING.value
            self.db.commit()
            
            # Get full path
            full_path = Path(self.storage.storage.config.base_path) / asset.file_path
            
            # Probe media
            probe = self.ffmpeg.probe(str(full_path))
            
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
                "probe_time": datetime.utcnow().isoformat()
            }
            
            # Generate thumbnail if video
            if asset.asset_type == AssetType.VIDEO.value:
                self._generate_thumbnail(asset, probe)
            
            # Generate waveform if audio
            if asset.asset_type == AssetType.AUDIO.value:
                self._generate_waveform(asset)
            
            asset.status = AssetStatus.READY.value
            self.db.commit()
            
            return asset
            
        except Exception as e:
            logger.error(f"Asset processing failed: {e}")
            asset.status = AssetStatus.FAILED.value
            asset.error_message = str(e)
            self.db.commit()
            raise
    
    def _generate_thumbnail(self, asset: MediaAsset, probe: MediaProbeResult):
        """Generate thumbnail for video asset"""
        full_path = Path(self.storage.storage.config.base_path) / asset.file_path
        thumbnail_name = f"{asset.id}_thumb.jpg"
        thumbnail_path = f"thumbnails/{asset.id}"
        
        thumbnail_full = Path(self.storage.storage.config.base_path) / thumbnail_path
        thumbnail_full.mkdir(parents=True, exist_ok=True)
        
        output_path = thumbnail_full / thumbnail_name
        
        success = self.ffmpeg.create_thumbnail(
            str(full_path),
            str(output_path),
            timestamp="00:00:01"
        )
        
        if success:
            asset.thumbnail_path = f"{thumbnail_path}/{thumbnail_name}"
    
    def _generate_waveform(self, asset: MediaAsset):
        """Generate waveform data for audio asset"""
        from app.core.audio_analyzer import get_audio_analyzer
        
        full_path = Path(self.storage.storage.config.base_path) / asset.file_path
        analyzer = get_audio_analyzer()
        
        # Generate waveform peaks
        waveform = analyzer.generate_waveform(str(full_path))
        
        # Store waveform data
        waveform_record = WaveformData(
            asset_id=asset.id,
            peaks_left=waveform.peaks,
            peaks_mono=waveform.peaks,
            duration=waveform.duration,
            samples_per_second=waveform.samples_per_second
        )
        
        self.db.add(waveform_record)
        
        # Update asset with waveform path
        asset.waveform_path = f"waveforms/{asset.id}.json"
    
    def get_asset(self, asset_id: uuid.UUID) -> Optional[MediaAsset]:
        """Get asset by ID"""
        return self.repository.get_by_id(asset_id)
    
    def get_asset_by_slug(self, slug: str) -> Optional[MediaAsset]:
        """Get asset by slug"""
        return self.repository.get_by_slug(slug)
    
    def list_assets(
        self,
        project_id: Optional[uuid.UUID] = None,
        asset_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[MediaAsset]:
        """List assets with filters"""
        return self.repository.list_assets(
            project_id=project_id,
            asset_type=asset_type,
            status=status,
            limit=limit,
            offset=offset
        )
    
    def update_asset(self, asset_id: uuid.UUID, updates: Dict[str, Any]) -> MediaAsset:
        """Update asset metadata"""
        return self.repository.update(asset_id, updates)
    
    def archive_asset(self, asset_id: uuid.UUID) -> MediaAsset:
        """Archive an asset (soft delete)"""
        return self.repository.update(asset_id, {
            "status": AssetStatus.ARCHIVED.value
        })
    
    def delete_asset(self, asset_id: uuid.UUID) -> bool:
        """Permanently delete an asset and its files"""
        asset = self.get_asset(asset_id)
        
        if not asset:
            return False
        
        # Delete from storage
        import asyncio
        asyncio.run(self.storage.backend.delete(asset.file_path))
        
        # Delete thumbnail if exists
        if asset.thumbnail_path:
            asyncio.run(self.storage.backend.delete(asset.thumbnail_path))
        
        # Delete from database
        self.db.delete(asset)
        self.db.commit()
        
        return True
    
    def _determine_asset_type(self, content_type: str, filename: str) -> str:
        """Determine asset type from content type and filename"""
        if content_type.startswith("audio/"):
            return AssetType.AUDIO.value
        elif content_type.startswith("video/"):
            return AssetType.VIDEO.value
        elif content_type.startswith("image/"):
            return AssetType.IMAGE.value
        else:
            return AssetType.DOCUMENT.value
    
    def _generate_slug(self, name: str) -> str:
        """Generate URL-safe slug from name"""
        import re
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        
        # Ensure uniqueness
        base_slug = slug
        counter = 1
        while self.repository.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug


class TranscodingService:
    """Service for transcoding media files"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ffmpeg = get_ffmpeg_engine()
        self.storage = get_storage_manager()
    
    def create_transcoding_job(
        self,
        name: str,
        asset_id: uuid.UUID,
        input_path: str,
        target_format: str,
        target_codec: Optional[str] = None,
        target_resolution: Optional[str] = None,
        target_bitrate: Optional[str] = None
    ) -> TranscodingJob:
        """Create a new transcoding job"""
        job = TranscodingJob(
            name=name,
            asset_id=asset_id,
            input_path=input_path,
            target_format=target_format,
            target_codec=target_codec,
            target_resolution=target_resolution,
            target_bitrate=target_bitrate,
            status=TranscodingStatus.PENDING.value
        )
        
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        return job
    
    def execute_transcoding(self, job_id: uuid.UUID) -> TranscodingJob:
        """
        Execute transcoding job.
        Called by Celery worker.
        
        Args:
            job_id: Transcoding job ID
            
        Returns:
            Updated TranscodingJob
        """
        job = self.db.query(TranscodingJob).filter(TranscodingJob.id == job_id).first()
        
        if not job:
            raise ValueError(f"Transcoding job {job_id} not found")
        
        try:
            job.status = TranscodingStatus.IN_PROGRESS.value
            job.started_at = datetime.utcnow()
            self.db.commit()
            
            # Generate output path
            output_filename = f"{Path(job.input_path).stem}_{job.target_format}"
            output_path = f"transcoded/{job.asset_id}/{output_filename}"
            full_output_path = Path(self.storage.storage.config.base_path) / output_path
            full_output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Build FFmpeg command
            cmd = ["ffmpeg", "-y", "-i", job.input_path]
            
            # Video codec
            if job.target_codec:
                cmd.extend(["-c:v", job.target_codec])
            
            # Resolution
            if job.target_resolution:
                cmd.extend(["-s", job.target_resolution])
            
            # Bitrate
            if job.target_bitrate:
                cmd.extend(["-b:v", job.target_bitrate])
            
            cmd.append(str(full_output_path))
            
            # Execute
            import subprocess
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            if result.returncode == 0:
                job.status = TranscodingStatus.COMPLETED.value
                job.output_path = str(full_output_path)
                job.completed_at = datetime.utcnow()
                
                # Get output info
                output_info = self.ffmpeg.get_video_info(str(full_output_path))
                job.output_size = output_info.get("size")
                job.output_codec = output_info.get("video_codec")
                
            else:
                job.status = TranscodingStatus.FAILED.value
                job.error_message = result.stderr
            
            self.db.commit()
            return job
            
        except Exception as e:
            logger.error(f"Transcoding failed: {e}")
            job.status = TranscodingStatus.FAILED.value
            job.error_message = str(e)
            self.db.commit()
            raise
    
    def get_job(self, job_id: uuid.UUID) -> Optional[TranscodingJob]:
        """Get transcoding job by ID"""
        return self.db.query(TranscodingJob).filter(TranscodingJob.id == job_id).first()
    
    def list_jobs(
        self,
        asset_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[TranscodingJob]:
        """List transcoding jobs"""
        query = self.db.query(TranscodingJob)
        
        if asset_id:
            query = query.filter(TranscodingJob.asset_id == asset_id)
        if status:
            query = query.filter(TranscodingJob.status == status)
        
        return query.order_by(TranscodingJob.created_at.desc()).limit(limit).all()