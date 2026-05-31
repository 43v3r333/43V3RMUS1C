"""
Asset-related Pydantic schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, TimestampSchema


# ============ Media Asset Schemas ============

class MediaAssetBase(BaseSchema):
    """Base media asset schema"""
    
    name: str = Field(min_length=1, max_length=255)
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    asset_type: str
    status: str = "pending"
    duration: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class MediaAssetCreate(MediaAssetBase):
    """Media asset creation schema"""
    
    project_id: Optional[UUID] = None
    track_id: Optional[UUID] = None


class MediaAssetUpdate(BaseSchema):
    """Media asset update schema"""
    
    name: Optional[str] = Field(default=None, max_length=255)
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class MediaAssetResponse(TimestampSchema):
    """Media asset response schema"""
    
    name: str
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    asset_type: str
    status: str
    duration: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    project_id: Optional[UUID] = None
    track_id: Optional[UUID] = None


# ============ Generated Asset Schemas ============

class GeneratedAssetBase(BaseSchema):
    """Base generated asset schema"""
    
    name: str = Field(min_length=1, max_length=255)
    asset_type: str
    generation_type: str
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    output_path: Optional[str] = None
    output_url: Optional[str] = None
    preview_url: Optional[str] = None
    status: str = "pending"
    error_message: Optional[str] = None
    generation_time: Optional[int] = None


class GeneratedAssetCreate(GeneratedAssetBase):
    """Generated asset creation schema"""
    
    project_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None


class GeneratedAssetUpdate(BaseSchema):
    """Generated asset update schema"""
    
    name: Optional[str] = Field(default=None, max_length=255)
    status: Optional[str] = None
    output_path: Optional[str] = None
    output_url: Optional[str] = None
    preview_url: Optional[str] = None
    error_message: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class GeneratedAssetResponse(TimestampSchema):
    """Generated asset response schema"""
    
    name: str
    asset_type: str
    generation_type: str
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    output_path: Optional[str] = None
    output_url: Optional[str] = None
    preview_url: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    generation_time: Optional[int] = None
    project_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None