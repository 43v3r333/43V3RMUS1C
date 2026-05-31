"""
Asset schemas for media and generated assets
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class MediaAssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    asset_type: str
    mime_type: Optional[str] = None
    tags: Optional[List[str]] = None


class MediaAssetCreate(MediaAssetBase):
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    duration: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    project_id: Optional[UUID] = None
    track_id: Optional[UUID] = None


class MediaAssetUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class MediaAssetResponse(MediaAssetBase):
    id: UUID
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    status: str
    duration: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    project_id: Optional[UUID] = None
    track_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GeneratedAssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    asset_type: str
    generation_type: str
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None


class GeneratedAssetCreate(GeneratedAssetBase):
    parameters: Optional[Dict[str, Any]] = None
    project_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None


class GeneratedAssetUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    output_path: Optional[str] = None
    output_url: Optional[str] = None
    preview_url: Optional[str] = None
    error_message: Optional[str] = None


class GeneratedAssetResponse(GeneratedAssetBase):
    id: UUID
    parameters: Optional[Dict[str, Any]] = None
    output_path: Optional[str] = None
    output_url: Optional[str] = None
    preview_url: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    generation_time: Optional[int] = None
    project_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssetUploadResponse(BaseModel):
    id: UUID
    name: str
    file_path: str
    file_size: int
    mime_type: str
    status: str