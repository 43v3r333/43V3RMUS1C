"""
Campaign and social schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    campaign_type: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[int] = None
    target_platforms: Optional[List[str]] = None
    target_audience: Optional[Dict[str, Any]] = None


class CampaignCreate(CampaignBase):
    created_by_id: UUID
    artist_id: Optional[UUID] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    campaign_type: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[int] = None
    target_platforms: Optional[List[str]] = None
    target_audience: Optional[Dict[str, Any]] = None


class CampaignResponse(CampaignBase):
    id: UUID
    status: str
    metadata: Optional[Dict[str, Any]] = None
    created_by_id: UUID
    artist_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SocialAccountBase(BaseModel):
    platform: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    profile_url: Optional[str] = None


class SocialAccountCreate(SocialAccountBase):
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    user_id: Optional[UUID] = None
    artist_id: Optional[UUID] = None


class SocialAccountUpdate(BaseModel):
    username: Optional[str] = None
    display_name: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_primary: Optional[bool] = None


class SocialAccountResponse(SocialAccountBase):
    id: UUID
    profile_image_url: Optional[str] = None
    is_active: bool
    is_primary: bool
    stats: Optional[Dict[str, Any]] = None
    user_id: Optional[UUID] = None
    artist_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SocialPostBase(BaseModel):
    content: Optional[str] = None
    caption: Optional[str] = None
    media_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    post_type: str = "post"


class SocialPostCreate(SocialPostBase):
    platform: str
    account_id: UUID
    campaign_id: Optional[UUID] = None
    track_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None


class SocialPostUpdate(BaseModel):
    content: Optional[str] = None
    caption: Optional[str] = None
    media_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class SocialPostResponse(SocialPostBase):
    id: UUID
    platform: str
    status: str
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    external_id: Optional[str] = None
    external_url: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    account_id: UUID
    campaign_id: Optional[UUID] = None
    track_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}