"""
Storage abstraction layer for media assets.
Supports local filesystem, S3, and future cloud storage backends.
"""
import os
import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List, BinaryIO, Tuple
from uuid import UUID

logger = logging.getLogger(__name__)


@dataclass
class StorageConfig:
    """Storage configuration"""
    storage_type: str = "local"  # local, s3, gcs, azure
    base_path: str = "./storage"
    temp_path: str = "./storage/temp"
    cdn_url: Optional[str] = None
    max_file_size: int = 500 * 1024 * 1024  # 500MB default
    
    # S3 specific (if using S3)
    s3_bucket: Optional[str] = None
    s3_region: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None


@dataclass
class StorageFile:
    """Represents a stored file"""
    path: str
    url: Optional[str] = None
    size: int = 0
    checksum: Optional[str] = None
    mime_type: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class UploadProgress:
    """Upload progress tracking"""
    upload_id: str
    file_name: str
    total_bytes: int
    uploaded_bytes: int
    status: str  # pending, uploading, completed, failed
    error: Optional[str] = None


class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    async def upload(
        self,
        file_data: BinaryIO,
        filename: str,
        content_type: Optional[str] = None,
        path: Optional[str] = None
    ) -> StorageFile:
        """Upload a file"""
        pass
    
    @abstractmethod
    async def download(self, path: str) -> bytes:
        """Download a file"""
        pass
    
    @abstractmethod
    async def delete(self, path: str) -> bool:
        """Delete a file"""
        pass
    
    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if file exists"""
        pass
    
    @abstractmethod
    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Get public/presigned URL for file"""
        pass
    
    @abstractmethod
    async def list_files(self, path: str, pattern: str = "*") -> List[StorageFile]:
        """List files in directory"""
        pass


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend"""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.base_path = Path(config.base_path)
        self.temp_path = Path(config.temp_path)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories"""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.base_path / "media").mkdir(exist_ok=True)
        (self.base_path / "assets").mkdir(exist_ok=True)
        (self.base_path / "renders").mkdir(exist_ok=True)
        (self.base_path / "thumbnails").mkdir(exist_ok=True)
        (self.base_path / "waveforms").mkdir(exist_ok=True)
    
    async def upload(
        self,
        file_data: BinaryIO,
        filename: str,
        content_type: Optional[str] = None,
        path: Optional[str] = None
    ) -> StorageFile:
        """Upload file to local storage"""
        # Determine target path
        if path:
            target_dir = self.base_path / path
            target_dir.mkdir(parents=True, exist_ok=True)
        else:
            target_dir = self.base_path / "media"
        
        target_path = target_dir / filename
        
        # Read and save file
        content = file_data.read()
        with open(target_path, "wb") as f:
            f.write(content)
        
        # Calculate checksum
        checksum = hashlib.md5(content).hexdigest()
        
        # Determine URL
        url = None
        if self.config.cdn_url:
            url = f"{self.config.cdn_url}/{path or 'media'}/{filename}"
        
        return StorageFile(
            path=str(target_path),
            url=url,
            size=len(content),
            checksum=checksum,
            mime_type=content_type,
            created_at=datetime.utcnow()
        )
    
    async def download(self, path: str) -> bytes:
        """Download file from local storage"""
        file_path = self.base_path / path if not Path(path).is_absolute() else Path(path)
        with open(file_path, "rb") as f:
            return f.read()
    
    async def delete(self, path: str) -> bool:
        """Delete file from local storage"""
        try:
            file_path = self.base_path / path if not Path(path).is_absolute() else Path(path)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    async def exists(self, path: str) -> bool:
        """Check if file exists"""
        file_path = self.base_path / path if not Path(path).is_absolute() else Path(path)
        return file_path.exists()
    
    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Get file URL (local files just return path)"""
        if self.config.cdn_url:
            return f"{self.config.cdn_url}/{path}"
        return f"/storage/{path}"
    
    async def list_files(self, path: str, pattern: str = "*") -> List[StorageFile]:
        """List files in directory"""
        dir_path = self.base_path / path if not Path(path).is_absolute() else Path(path)
        files = []
        
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                files.append(StorageFile(
                    path=str(file_path.relative_to(self.base_path)),
                    size=file_path.stat().st_size,
                    created_at=datetime.fromtimestamp(file_path.stat().st_ctime)
                ))
        
        return files


class S3StorageBackend(StorageBackend):
    """AWS S3 storage backend"""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.bucket = config.s3_bucket
        # Lazy import boto3 to avoid dependency when not using S3
        self._s3 = None
    
    @property
    def s3(self):
        """Lazy load boto3"""
        if self._s3 is None:
            import boto3
            self._s3 = boto3.client(
                's3',
                region_name=self.config.s3_region or 'us-east-1',
                aws_access_key_id=self.config.s3_access_key,
                aws_secret_access_key=self.config.s3_secret_key
            )
        return self._s3
    
    async def upload(
        self,
        file_data: BinaryIO,
        filename: str,
        content_type: Optional[str] = None,
        path: Optional[str] = None
    ) -> StorageFile:
        """Upload file to S3"""
        content = file_data.read()
        key = f"{path or 'media'}/{filename}" if path else f"media/{filename}"
        
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=content,
            **extra_args
        )
        
        checksum = hashlib.md5(content).hexdigest()
        
        return StorageFile(
            path=key,
            url=f"https://{self.bucket}.s3.amazonaws.com/{key}",
            size=len(content),
            checksum=checksum,
            mime_type=content_type,
            created_at=datetime.utcnow()
        )
    
    async def download(self, path: str) -> bytes:
        """Download file from S3"""
        response = self.s3.get_object(Bucket=self.bucket, Key=path)
        return response['Body'].read()
    
    async def delete(self, path: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=path)
            return True
        except Exception as e:
            logger.error(f"Failed to delete file from S3: {e}")
            return False
    
    async def exists(self, path: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.s3.head_object(Bucket=self.bucket, Key=path)
            return True
        except:
            return False
    
    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Get presigned URL for S3 file"""
        return self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': path},
            ExpiresIn=expires_in
        )
    
    async def list_files(self, path: str, pattern: str = "*") -> List[StorageFile]:
        """List files in S3 prefix"""
        prefix = f"{path}/" if path else ""
        response = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        files = []
        
        for obj in response.get('Contents', []):
            files.append(StorageFile(
                path=obj['Key'],
                size=obj['Size'],
                created_at=obj['LastModified']
            ))
        
        return files


class StorageManager:
    """Main storage manager with factory pattern"""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self._backend: Optional[StorageBackend] = None
        self._initialize_backend()
    
    def _initialize_backend(self):
        """Initialize the appropriate storage backend"""
        storage_type = self.config.storage_type.lower()
        
        if storage_type == "local":
            self._backend = LocalStorageBackend(self.config)
        elif storage_type == "s3":
            self._backend = S3StorageBackend(self.config)
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
        
        logger.info(f"Storage initialized: {storage_type} at {self.config.base_path}")
    
    @property
    def backend(self) -> StorageBackend:
        """Get current backend"""
        return self._backend
    
    async def save_upload(
        self,
        file_data: BinaryIO,
        filename: str,
        content_type: Optional[str] = None,
        subdirectory: str = "media"
    ) -> StorageFile:
        """Save uploaded file"""
        return await self._backend.upload(file_data, filename, content_type, subdirectory)
    
    async def save_render_output(
        self,
        file_data: BinaryIO,
        filename: str,
        content_type: Optional[str] = None
    ) -> StorageFile:
        """Save render output"""
        return await self._backend.upload(file_data, filename, content_type, "renders")
    
    async def save_thumbnail(
        self,
        file_data: BinaryIO,
        filename: str
    ) -> StorageFile:
        """Save thumbnail"""
        return await self._backend.upload(file_data, filename, "image/jpeg", "thumbnails")
    
    async def save_waveform(
        self,
        file_data: BinaryIO,
        filename: str
    ) -> StorageFile:
        """Save waveform data"""
        return await self._backend.upload(file_data, filename, "application/json", "waveforms")
    
    def generate_storage_path(self, asset_type: str, file_ext: str) -> str:
        """Generate a unique storage path for an asset"""
        timestamp = datetime.utcnow().strftime("%Y/%m/%d")
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return f"{asset_type}/{timestamp}/{unique_id}.{file_ext}"
    
    def get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename"""
        return Path(filename).suffix.lstrip('.')


# Global storage manager instance
_storage_manager: Optional[StorageManager] = None


def get_storage_manager() -> StorageManager:
    """Get or create global storage manager"""
    global _storage_manager
    
    if _storage_manager is None:
        from app.core.config import settings
        
        config = StorageConfig(
            storage_type=settings.storage_type,
            base_path=settings.storage_path,
            temp_path=f"{settings.storage_path}/temp",
            cdn_url=getattr(settings, 'cdn_url', None),
            max_file_size=500 * 1024 * 1024
        )
        
        _storage_manager = StorageManager(config)
    
    return _storage_manager