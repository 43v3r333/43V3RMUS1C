"""
Media asset API endpoints.
Handles upload, retrieval, and management of media assets.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Path
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_async_db
from app.core.storage import get_storage_manager
from app.schemas.media_schema import (
    MediaAssetCreate,
    MediaAssetUpdate,
    MediaAssetResponse,
    MediaAssetListResponse,
    UploadResponse
)
from app.services.media_service import MediaAssetService, TranscodingService
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/assets", tags=["media_assets"])


@router.post("/upload", response_model=UploadResponse)
async def upload_asset(
    file: UploadFile = File(...),
    project_id: Optional[str] = Query(None),
    artist_id: Optional[str] = Query(None),
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a new media asset.
    Supports chunked uploads for large files.
    """
    # Validate file size (500MB max)
    MAX_SIZE = 500 * 1024 * 1024
    
    # Read file content
    content = await file.read()
    
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 500MB.")
    
    # Reset file position
    await file.seek(0)
    
    # Create service
    service = MediaAssetService(db)
    
    # Convert UUIDs
    project_uuid = uuid.UUID(project_id) if project_id else None
    artist_uuid = uuid.UUID(artist_id) if artist_id else None
    
    try:
        asset = await service.create_asset_from_upload(
            file_data=file.file,
            filename=file.filename,
            content_type=file.content_type,
            created_by_id=current_user.id,
            project_id=project_uuid,
            artist_id=artist_uuid
        )
        
        return UploadResponse(
            asset_id=str(asset.id),
            name=asset.name,
            status=asset.status,
            message="Asset uploaded successfully. Processing in background."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/chunked")
async def initiate_chunked_upload(
    filename: str = Query(...),
    total_chunks: int = Query(...),
    content_type: str = Query(...),
    project_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """
    Initiate a chunked upload session.
    Returns upload ID for subsequent chunk uploads.
    """
    import secrets
    
    # Generate upload session ID
    upload_id = secrets.token_urlsafe(32)
    
    # Store upload metadata in Redis (would need Redis setup)
    # For now, return upload ID
    
    return {
        "upload_id": upload_id,
        "filename": filename,
        "total_chunks": total_chunks,
        "status": "initiated"
    }


@router.post("/upload/chunked/{upload_id}")
async def upload_chunk(
    upload_id: str,
    chunk_number: int = Query(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a chunk of a file.
    """
    # This would handle storing chunks in temp storage
    
    return {
        "upload_id": upload_id,
        "chunk_number": chunk_number,
        "status": "received"
    }


@router.post("/upload/chunked/{upload_id}/complete")
async def complete_chunked_upload(
    upload_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Complete a chunked upload by merging all chunks.
    """
    # This would merge chunks and create the final asset
    
    return {
        "upload_id": upload_id,
        "status": "completed"
    }


@router.get("", response_model=MediaAssetListResponse)
async def list_assets(
    project_id: Optional[str] = Query(None),
    asset_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    List media assets with filters.
    """
    service = MediaAssetService(db)
    
    project_uuid = uuid.UUID(project_id) if project_id else None
    
    assets = service.list_assets(
        project_id=project_uuid,
        asset_type=asset_type,
        status=status,
        limit=limit,
        offset=offset
    )
    
    total = service.repository.count_assets(
        project_id=project_uuid,
        asset_type=asset_type,
        status=status
    )
    
    return MediaAssetListResponse(
        items=[MediaAssetResponse.model_validate(a) for a in assets],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{asset_id}", response_model=MediaAssetResponse)
async def get_asset(
    asset_id: str = Path(...),
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a single media asset by ID.
    """
    service = MediaAssetService(db)
    
    try:
        asset_uuid = uuid.UUID(asset_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid asset ID format")
    
    asset = service.get_asset(asset_uuid)
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return MediaAssetResponse.model_validate(asset)


@router.patch("/{asset_id}", response_model=MediaAssetResponse)
async def update_asset(
    asset_id: str,
    updates: MediaAssetUpdate,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update asset metadata.
    """
    service = MediaAssetService(db)
    
    try:
        asset_uuid = uuid.UUID(asset_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid asset ID format")
    
    try:
        asset = service.update_asset(asset_uuid, updates.model_dump(exclude_unset=True))
        return MediaAssetResponse.model_validate(asset)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: str,
    permanent: bool = Query(False),
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an asset. Use permanent=true for hard delete.
    """
    service = MediaAssetService(db)
    
    try:
        asset_uuid = uuid.UUID(asset_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid asset ID format")
    
    if permanent:
        success = service.delete_asset(asset_uuid)
    else:
        service.archive_asset(asset_uuid)
        success = True
    
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return {"status": "deleted", "permanent": permanent}


@router.get("/{asset_id}/download")
async def download_asset(
    asset_id: str,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download asset file.
    """
    service = MediaAssetService(db)
    storage = get_storage_manager()
    
    try:
        asset_uuid = uuid.UUID(asset_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid asset ID format")
    
    asset = service.get_asset(asset_uuid)
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    try:
        content = await storage.backend.download(asset.file_path)
        
        return StreamingResponse(
            iter([content]),
            media_type=asset.mime_type or "application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{asset.original_filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/{asset_id}/thumbnail")
async def get_asset_thumbnail(
    asset_id: str,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get asset thumbnail image.
    """
    service = MediaAssetService(db)
    storage = get_storage_manager()
    
    try:
        asset_uuid = uuid.UUID(asset_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid asset ID format")
    
    asset = service.get_asset(asset_uuid)
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    if not asset.thumbnail_path:
        raise HTTPException(status_code=404, detail="No thumbnail available")
    
    try:
        content = await storage.backend.download(asset.thumbnail_path)
        
        return StreamingResponse(
            iter([content]),
            media_type="image/jpeg"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Thumbnail not found: {str(e)}")


@router.post("/{asset_id}/reprocess")
async def reprocess_asset(
    asset_id: str,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger reprocessing of an asset to regenerate thumbnails and metadata.
    """
    service = MediaAssetService(db)
    
    try:
        asset_uuid = uuid.UUID(asset_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid asset ID format")
    
    try:
        # Process asset synchronously (or trigger background job)
        asset = service.process_asset(asset_uuid)
        return {
            "status": "completed",
            "asset_id": str(asset.id),
            "message": "Asset reprocessed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{asset_id}/transcode")
async def transcode_asset(
    asset_id: str,
    target_format: str = Query(...),
    target_codec: Optional[str] = Query(None),
    target_resolution: Optional[str] = Query(None),
    target_bitrate: Optional[str] = Query(None),
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a transcoding job for an asset.
    """
    transcoding_service = TranscodingService(db)
    asset_service = MediaAssetService(db)
    
    try:
        asset_uuid = uuid.UUID(asset_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid asset ID format")
    
    asset = asset_service.get_asset(asset_uuid)
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    job = transcoding_service.create_transcoding_job(
        name=f"Transcode {asset.name} to {target_format}",
        asset_id=asset_uuid,
        input_path=asset.file_path,
        target_format=target_format,
        target_codec=target_codec,
        target_resolution=target_resolution,
        target_bitrate=target_bitrate
    )
    
    return {
        "job_id": str(job.id),
        "status": job.status,
        "message": "Transcoding job created"
    }