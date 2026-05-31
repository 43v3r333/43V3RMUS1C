"""
Analytics-related Pydantic schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, TimestampSchema


# ============ Analytics Event Schemas ============

class AnalyticsEventResponse(BaseSchema):
    """Analytics event response schema"""
    
    id: UUID
    created_at: datetime
    event_type: str
    event_name: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    traits: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime


# ============ Trend Data Schemas ============

class TrendDataResponse(BaseSchema):
    """Trend data response schema"""
    
    id: UUID
    created_at: datetime
    source: str
    trend_type: str
    name: str
    external_id: Optional[str] = None
    rank: Optional[int] = None
    change: Optional[str] = None
    change_value: Optional[int] = None
    metrics: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    region: Optional[str] = None
    date: datetime


# ============ Platform Metric Schemas ============

class PlatformMetricResponse(BaseSchema):
    """Platform metric response schema"""
    
    id: UUID
    created_at: datetime
    metric_name: str
    metric_type: str
    value: float
    unit: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime


# ============ Brand Profile Schemas ============

class BrandProfileBase(BaseSchema):
    """Base brand profile schema"""
    
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    colors: Optional[List[Dict[str, str]]] = None
    fonts: Optional[List[Dict[str, str]]] = None
    visual_style: Optional[Dict[str, Any]] = None
    tone_of_voice: Optional[Dict[str, Any]] = None
    content_guidelines: Optional[Dict[str, Any]] = None
    logo_url: Optional[str] = None
    assets: Optional[List[Dict[str, Any]]] = None
    is_active: bool = True


class BrandProfileCreate(BrandProfileBase):
    """Brand profile creation schema"""
    
    pass


class BrandProfileUpdate(BaseSchema):
    """Brand profile update schema"""
    
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    colors: Optional[List[Dict[str, str]]] = None
    fonts: Optional[List[Dict[str, str]]] = None
    visual_style: Optional[Dict[str, Any]] = None
    tone_of_voice: Optional[Dict[str, Any]] = None
    content_guidelines: Optional[Dict[str, Any]] = None
    logo_url: Optional[str] = None
    assets: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None


class BrandProfileResponse(TimestampSchema):
    """Brand profile response schema"""
    
    name: str
    description: Optional[str] = None
    colors: Optional[List[Dict[str, str]]] = None
    fonts: Optional[List[Dict[str, str]]] = None
    visual_style: Optional[Dict[str, Any]] = None
    tone_of_voice: Optional[Dict[str, Any]] = None
    content_guidelines: Optional[Dict[str, Any]] = None
    logo_url: Optional[str] = None
    assets: Optional[List[Dict[str, Any]]] = None
    is_active: bool
    artist_id: Optional[UUID] = None