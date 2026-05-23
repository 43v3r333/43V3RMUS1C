"""
Analytics schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel


class AnalyticsEventCreate(BaseModel):
    event_type: str
    event_name: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    traits: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None


class AnalyticsEventResponse(AnalyticsEventCreate):
    id: UUID
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TrendDataBase(BaseModel):
    source: str
    trend_type: str
    name: str
    external_id: Optional[str] = None
    region: Optional[str] = None


class TrendDataCreate(TrendDataBase):
    rank: Optional[int] = None
    change: Optional[str] = None
    change_value: Optional[int] = None
    metrics: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    date: datetime


class TrendDataResponse(TrendDataBase):
    id: UUID
    rank: Optional[int] = None
    change: Optional[str] = None
    change_value: Optional[int] = None
    metrics: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PlatformMetricBase(BaseModel):
    metric_name: str
    metric_type: str
    value: float
    unit: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None


class PlatformMetricCreate(PlatformMetricBase):
    timestamp: datetime


class PlatformMetricResponse(PlatformMetricBase):
    id: UUID
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BrandProfileBase(BaseModel):
    name: str
    description: Optional[str] = None
    colors: Optional[List[Dict[str, str]]] = None
    fonts: Optional[List[str]] = None
    visual_style: Optional[Dict[str, Any]] = None
    tone_of_voice: Optional[Dict[str, Any]] = None
    content_guidelines: Optional[Dict[str, Any]] = None


class BrandProfileCreate(BrandProfileBase):
    logo_url: Optional[str] = None
    assets: Optional[Dict[str, Any]] = None
    artist_id: Optional[UUID] = None


class BrandProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    colors: Optional[List[Dict[str, str]]] = None
    fonts: Optional[List[str]] = None
    visual_style: Optional[Dict[str, Any]] = None
    tone_of_voice: Optional[Dict[str, Any]] = None
    content_guidelines: Optional[Dict[str, Any]] = None
    logo_url: Optional[str] = None
    assets: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class BrandProfileResponse(BrandProfileBase):
    id: UUID
    logo_url: Optional[str] = None
    assets: Optional[Dict[str, Any]] = None
    is_active: bool
    artist_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SystemLogCreate(BaseModel):
    level: str
    message: str
    logger_name: Optional[str] = None
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None


class SystemLogResponse(SystemLogCreate):
    id: UUID
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}