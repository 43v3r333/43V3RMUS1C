"""
Analytics Domain Models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, JSON, Text, DateTime
from sqlalchemy.orm import relationship

from ...models.base import BaseModel

# AnalyticsEvent is moved to app.models.analytics to avoid duplicate table registration
# This is a stub to prevent import errors
class AnalyticsEvent:
    """DEPRECATED: AnalyticsEvent has moved to app.models.analytics.
    
    This class exists only to prevent ImportErrors during migration.
    Use: from app.models.analytics import AnalyticsEvent
    """
    __table__ = None
    
    def __init__(self, *args, **kwargs):
        raise RuntimeError(
            "AnalyticsEvent is no longer in domains/analytics/models.py. "
            "Import from app.models.analytics instead."
        )


class Report(BaseModel):
    """Analytics report model"""
    __tablename__ = "analytics_reports"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False)
    config = Column(JSON, nullable=False)
    status = Column(String(50), default="draft")
    last_generated = Column(DateTime, nullable=True)
    
    # Scheduled settings
    is_scheduled = Column(Boolean, default=False)
    schedule_cron = Column(String(100), nullable=True)
    
    # Output settings
    output_format = Column(String(20), default="json")
    destination_path = Column(String(500), nullable=True)


class AnalyticsEngine:
    """Stub for AnalyticsEngine - import from services"""
    pass