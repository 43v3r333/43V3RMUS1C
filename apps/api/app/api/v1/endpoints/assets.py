"""
Asset endpoints (Media Assets, Generated Assets)
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_async_db, get_current_user
from app.models.user import User
from app.schemas.asset import (
    MediaAssetCreate, MediaAssetUpdate, MediaAssetResponse,
    GeneratedAssetCreate, GeneratedAssetUpdate, GeneratedAssetResponse,
)
from app.schemas.base import PaginatedResponse
from app.models.asset import MediaAsset, GeneratedAsset
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)

router = APIRouter()

# ============ Media Asset Endpoints ============

@router.get("/media", response_model=PaginatedResponse[MediaAssetResponse])
async def list_media_assets(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    asset_type: Optional[str] = None,
    status: Optional[str] = None,
    project_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """List all media assets"""
    repo = BaseRepository(MediaAsset, db)
    filters = {}
    if asset_type:
        filters["asset_type"] = asset_type
    if status:
        filters["status"] = status
    if project_id:
        filters["project_id"] = project_id
    assets, total = await repo.paginate(page, per_page, filters=filters if filters else None)
    return PaginatedResponse.create(assets, total, page, per_page)


@router.post("/media", response_model=MediaAssetResponse, status_code=status.HTTP_201_CREATED)
async def create_media_asset(
    data: MediaAssetCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Create new media asset"""
    asset = MediaAsset(**data.model_dump())
    repo = BaseRepository(MediaAsset, db)
    asset = await repo.create(asset)
    logger.info(f"Media asset created: {asset.name}")
    return asset


@router.get("/media/{asset_id}", response_model=MediaAssetResponse)
async def get_media_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Get media asset by ID"""
    repo = BaseRepository(MediaAsset, db)
    asset = await repo.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Media asset not found")
    return asset


@router.patch("/media/{asset_id}", response_model=MediaAssetResponse)
async def update_media_asset(
    asset_id: str,
    data: MediaAssetUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Update media asset"""
    repo = BaseRepository(MediaAsset, db)
    asset = await repo.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Media asset not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(asset, key, value)
    
    asset = await repo.update(asset)
    return asset


@router.delete("/media/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Delete media asset"""
    repo = BaseRepository(MediaAsset, db)
    asset = await repo.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Media asset not found")
    
    await repo.delete(asset)
    return None


# ============ Generated Asset Endpoints ============

@router.get("/generated", response_model=PaginatedResponse[GeneratedAssetResponse])
async def list_generated_assets(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    asset_type: Optional[str] = None,
    status: Optional[str] = None,
    generation_type: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """List all generated assets"""
    repo = BaseRepository(GeneratedAsset, db)
    filters = {}
    if asset_type:
        filters["asset_type"] = asset_type
    if status:
        filters["status"] = status
    if generation_type:
        filters["generation_type"] = generation_type
    assets, total = await repo.paginate(page, per_page, filters=filters if filters else None)
    return PaginatedResponse.create(assets, total, page, per_page)


@router.post("/generated", response_model=GeneratedAssetResponse, status_code=status.HTTP_201_CREATED)
async def create_generated_asset(
    data: GeneratedAssetCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Create new generated asset (job request)"""
    asset = GeneratedAsset(**data.model_dump())
    repo = BaseRepository(GeneratedAsset, db)
    asset = await repo.create(asset)
    logger.info(f"Generated asset job created: {asset.name}")
    return asset


@router.get("/generated/{asset_id}", response_model=GeneratedAssetResponse)
async def get_generated_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Get generated asset by ID"""
    repo = BaseRepository(GeneratedAsset, db)
    asset = await repo.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Generated asset not found")
    return asset


@router.patch("/generated/{asset_id}", response_model=GeneratedAssetResponse)
async def update_generated_asset(
    asset_id: str,
    data: GeneratedAssetUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Update generated asset"""
    repo = BaseRepository(GeneratedAsset, db)
    asset = await repo.get_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Generated asset not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(asset, key, value)
    
    asset = await repo.update(asset)
    return asset