"""
Analytics models: AnalyticsEvent, TrendData, PlatformMetric, BrandProfile
"""
from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AnalyticsEvent(BaseModel):
    """Analytics event model for user behavior tracking"""
    
    __tablename__ = "analytics_events"
    
    event_type = Column(String(100), nullable=False, index=True)  # page_view, button_click, etc.
    event_name = Column(String(255), nullable=False, index=True)
    
    # User context
    user_id = Column(String(100), nullable=True, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    
    # Event properties
    properties = Column(JSON, nullable=True)
    traits = Column(JSON, nullable=True)
    
    # Context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    referrer = Column(String(500), nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<AnalyticsEvent(id={self.id}, event_name={self.event_name})>"


class TrendData(BaseModel):
    """Trend data model for market analytics"""
    
    __tablename__ = "trend_data"
    
    source = Column(String(50), nullable=False, index=True)  # spotify, twitter, google
    trend_type = Column(String(50), nullable=False, index=True)  # track, genre, artist
    name = Column(String(255), nullable=False, index=True)
    
    # External reference
    external_id = Column(String(255), nullable=True)
    
    # Metrics
    rank = Column(Integer, nullable=True)
    change = Column(String(50), nullable=True)  # up, down, stable
    change_value = Column(Integer, nullable=True)
    metrics = Column(JSON, nullable=True)
    
    # Additional data
    metadata = Column(JSON, nullable=True)
    region = Column(String(50), nullable=True, index=True)
    
    # Time reference
    date = Column(DateTime, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<TrendData(id={self.id}, name={self.name}, source={self.source})>"


class PlatformMetric(BaseModel):
    """Platform metric model for system monitoring"""
    
    __tablename__ = "platform_metrics"
    
    metric_name = Column(String(100), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)  # counter, gauge, histogram
    
    # Value
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)
    
    # Tags for categorization
    tags = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<PlatformMetric(id={self.id}, name={self.metric_name}, value={self.value})>"


class BrandProfile(BaseModel):
    """Brand profile model for visual identity management"""
    
    __tablename__ = "brand_profiles"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Visual elements
    colors = Column(JSON, nullable=True)  # [{name, hex, rgb}]
    fonts = Column(JSON, nullable=True)  # [{name, weight, style}]
    visual_style = Column(JSON, nullable=True)  # {mood, theme, references}
    
    # Content guidelines
    tone_of_voice = Column(JSON, nullable=True)  # {personality, words, examples}
    content_guidelines = Column(JSON, nullable=True)
    
    # Assets
    logo_url = Column(String(500), nullable=True)
    assets = Column(JSON, nullable=True)  # asset references
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Ownership
    artist_id = Column(UUID(as_uuid=True), ForeignKey("artists.id"), nullable=True)
    
    # Relationships
    artist = relationship("Artist", back_populates="brand_profile", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<BrandProfile(id={self.id}, name={self.name})>"


# Additional imports
from sqlalchemy import Boolean, DateTime