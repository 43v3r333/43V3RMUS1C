"""
Campaign-related Pydantic schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, TimestampSchema


# ============ Campaign Schemas ============

class CampaignBase(BaseSchema):
    """Base campaign schema"""
    
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    campaign_type: str
    status: str = "draft"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[int] = None
    target_platforms: Optional[List[str]] = None
    target_audience: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class CampaignCreate(CampaignBase):
    """Campaign creation schema"""
    
    artist_id: Optional[UUID] = None


class CampaignUpdate(BaseSchema):
    """Campaign update schema"""
    
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[int] = None
    target_platforms: Optional[List[str]] = None
    target_audience: Optional[Dict[str, Any]] = None


class CampaignResponse(TimestampSchema):
    """Campaign response schema"""
    
    name: str
    description: Optional[str] = None
    campaign_type: str
    status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[int] = None
    target_platforms: Optional[List[str]] = None
    target_audience: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_by_id: UUID
    artist_id: Optional[UUID] = None


# ============ Social Account Schemas ============

class SocialAccountBase(BaseSchema):
    """Base social account schema"""
    
    platform: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    profile_url: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_active: bool = True
    is_primary: bool = False


class SocialAccountCreate(SocialAccountBase):
    """Social account creation schema"""
    
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None


class SocialAccountUpdate(BaseSchema):
    """Social account update schema"""
    
    username: Optional[str] = None
    display_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_primary: Optional[bool] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None


class SocialAccountResponse(TimestampSchema):
    """Social account response schema"""
    
    platform: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    profile_url: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_active: bool
    is_primary: bool
    stats: Optional[Dict[str, Any]] = None
    user_id: Optional[UUID] = None
    artist_id: Optional[UUID] = None


# ============ Social Post Schemas ============

class SocialPostBase(BaseSchema):
    """Base social post schema"""
    
    content: Optional[str] = None
    caption: Optional[str] = None
    media_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    platform: str
    post_type: str = "post"
    status: str = "draft"
    scheduled_at: Optional[datetime] = None


class SocialPostCreate(SocialPostBase):
    """Social post creation schema"""
    
    account_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    track_id: Optional[UUID] = None


class SocialPostUpdate(BaseSchema):
    """Social post update schema"""
    
    content: Optional[str] = None
    caption: Optional[str] = None
    media_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class SocialPostResponse(TimestampSchema):
    """Social post response schema"""
    
    content: Optional[str] = None
    caption: Optional[str] = None
    media_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    platform: str
    post_type: str
    status: str
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    external_id: Optional[str] = None
    external_url: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    account_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    track_id: Optional[UUID] = None