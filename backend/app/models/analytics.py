"""
Analytics and monitoring models
"""
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, JSON, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import BaseModel


class AnalyticsEvent(BaseModel):
    """Analytics event model"""
    __tablename__ = "analytics_events"
    
    event_type = Column(String(100), nullable=False, index=True)
    event_name = Column(String(255), nullable=False, index=True)
    
    user_id = Column(String(100), nullable=True, index=True)  # Can be anonymous
    session_id = Column(String(100), nullable=True, index=True)
    
    properties = Column(JSON, nullable=True)
    traits = Column(JSON, nullable=True)
    
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    referrer = Column(String(500), nullable=True)
    
    # Timestamp already in base model, rename for clarity
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


class TrendData(BaseModel):
    """Trend data model for market analytics"""
    __tablename__ = "trend_data"
    
    source = Column(String(50), nullable=False, index=True)  # spotify, tiktok, youtube
    trend_type = Column(String(50), nullable=False, index=True)  # track, artist, genre, mood
    
    name = Column(String(255), nullable=False, index=True)
    external_id = Column(String(255), nullable=True)
    
    rank = Column(Integer, nullable=True)
    change = Column(String(50), nullable=True)  # "up", "down", "stable"
    change_value = Column(Integer, nullable=True)
    
    metrics = Column(JSON, nullable=True)  # {"streams": 1000000, "growth_rate": 0.15}
    metadata_dict = Column("metadata", JSON, nullable=True)
    
    region = Column(String(50), nullable=True, index=True)
    date = Column(DateTime, nullable=False, index=True)


class PlatformMetric(BaseModel):
    """Platform metrics model for performance monitoring"""
    __tablename__ = "platform_metrics"
    
    metric_name = Column(String(100), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)  # gauge, counter, histogram
    
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)
    
    tags = Column(JSON, nullable=True)  # {"service": "api", "region": "us-east"}
    metadata_dict = Column("metadata", JSON, nullable=True)
    
    timestamp = Column(DateTime, nullable=False, index=True)


class BrandProfile(BaseModel):
    """Brand DNA profile model"""
    __tablename__ = "brand_profiles"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    colors = Column(JSON, nullable=True)  # [{"primary": "#000000"}, {"secondary": "#ffffff"}]
    fonts = Column(JSON, nullable=True)
    visual_style = Column(JSON, nullable=True)
    
    tone_of_voice = Column(JSON, nullable=True)
    content_guidelines = Column(JSON, nullable=True)
    
    logo_url = Column(String(500), nullable=True)
    assets = Column(JSON, nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    artist_id = Column(PGUUID(as_uuid=True), ForeignKey("artists.id"), nullable=True)
    artist = relationship("Artist")


class SystemLog(BaseModel):
    """System log model for audit trail"""
    __tablename__ = "system_logs"
    
    level = Column(String(20), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    
    logger_name = Column(String(100), nullable=True)
    
    module = Column(String(100), nullable=True)
    function = Column(String(100), nullable=True)
    line_number = Column(Integer, nullable=True)
    
    request_id = Column(String(100), nullable=True, index=True)
    user_id = Column(String(100), nullable=True, index=True)
    
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    extra_data = Column(JSON, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    timestamp = Column(DateTime, nullable=False, index=True)