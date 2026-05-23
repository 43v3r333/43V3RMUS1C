"""
Asset endpoints for media and generated assets
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.deps import get_current_active_user
from ....schemas.asset import (
    MediaAssetCreate, MediaAssetUpdate, MediaAssetResponse,
    GeneratedAssetCreate, GeneratedAssetUpdate, GeneratedAssetResponse,
)
from ....services.asset_service import MediaAssetService, GeneratedAssetService
from ....repositories.asset_repository import MediaAssetRepository, GeneratedAssetRepository

router = APIRouter(prefix="/assets", tags=["assets"])


# Media Assets
@router.get("/media", response_model=List[MediaAssetResponse])
async def list_media_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    asset_type: Optional[str] = None,
    project_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List media assets with optional filters"""
    repo = MediaAssetRepository(db)
    service = MediaAssetService(repo)
    
    if asset_type:
        return repo.get_by_type(asset_type, skip, limit)
    if project_id:
        return repo.get_by_project(project_id, skip, limit)
    return service.get_all(skip, limit)


@router.post("/media", response_model=MediaAssetResponse)
async def create_media_asset(
    asset_data: MediaAssetCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create media asset metadata"""
    repo = MediaAssetRepository(db)
    service = MediaAssetService(repo)
    
    return service.create(asset_data)


@router.get("/media/{asset_id}", response_model=MediaAssetResponse)
async def get_media_asset(
    asset_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get media asset by ID"""
    repo = MediaAssetRepository(db)
    service = MediaAssetService(repo)
    
    asset = service.get_by_id(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    return asset


@router.put("/media/{asset_id}", response_model=MediaAssetResponse)
async def update_media_asset(
    asset_id: UUID,
    asset_data: MediaAssetUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update media asset"""
    repo = MediaAssetRepository(db)
    service = MediaAssetService(repo)
    
    asset = service.get_by_id(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    return service.update(asset, asset_data)


@router.post("/media/upload")
async def upload_media_asset(
    file: UploadFile = File(...),
    project_id: Optional[UUID] = None,
    track_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Upload media asset file"""
    # TODO: Implement file upload to storage
    # For now, return placeholder response
    return {
        "message": "Upload endpoint - implement storage integration",
        "file_name": file.filename,
        "content_type": file.content_type
    }


# Generated Assets
@router.get("/generated", response_model=List[GeneratedAssetResponse])
async def list_generated_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    asset_type: Optional[str] = None,
    generation_type: Optional[str] = None,
    project_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List generated assets with optional filters"""
    repo = GeneratedAssetRepository(db)
    service = GeneratedAssetService(repo)
    
    if asset_type:
        return repo.get_by_type(asset_type, skip, limit)
    if generation_type:
        return repo.get_by_generation_type(generation_type, skip, limit)
    if project_id:
        return repo.get_by_project(project_id, skip, limit)
    return service.get_all(skip, limit)


@router.post("/generated", response_model=GeneratedAssetResponse)
async def create_generated_asset(
    asset_data: GeneratedAssetCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create new generated asset"""
    repo = GeneratedAssetRepository(db)
    service = GeneratedAssetService(repo)
    
    return service.create(asset_data)


@router.get("/generated/{asset_id}", response_model=GeneratedAssetResponse)
async def get_generated_asset(
    asset_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get generated asset by ID"""
    repo = GeneratedAssetRepository(db)
    service = GeneratedAssetService(repo)
    
    asset = service.get_by_id(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    return asset


@router.put("/generated/{asset_id}", response_model=GeneratedAssetResponse)
async def update_generated_asset(
    asset_id: UUID,
    asset_data: GeneratedAssetUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update generated asset"""
    repo = GeneratedAssetRepository(db)
    service = GeneratedAssetService(repo)
    
    asset = service.get_by_id(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    return service.update(asset, asset_data)


@router.get("/generated/recent", response_model=List[GeneratedAssetResponse])
async def get_recent_generated_assets(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get recently generated assets"""
    repo = GeneratedAssetRepository(db)
    service = GeneratedAssetService(repo)
    
    return repo.get_recent(limit)