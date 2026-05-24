"""
Analytics Models - Analytics event tracking
"""
from datetime import datetime
from typing import Dict, Optional, Any
from uuid import UUID

from sqlalchemy import Column, String, Text, Integer, Float, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class AnalyticsEvent(BaseModel):
    """Analytics event model"""
    __tablename__ = "analytics_events"
    
    # Event identification
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Actor info
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Object info
    object_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    object_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Event data
    properties: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Context
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    referrer: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamp is inherited from BaseModel


class Report(BaseModel):
    """Analytics report model"""
    __tablename__ = "analytics_reports"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Report configuration
    filters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    metrics: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    dimensions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Results
    data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Schedule
    is_scheduled: Mapped[bool] = mapped_column(default=False)
    schedule_interval: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)