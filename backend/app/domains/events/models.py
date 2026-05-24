"""
Event Persistence Models - Database models for event storage
"""
from datetime import datetime
from typing import Dict, Optional, Any
from uuid import UUID

from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class DomainEventRecord(BaseModel):
    """Persisted domain event record"""
    __tablename__ = "domain_events"
    
    # Event identification
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Aggregate info
    aggregate_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    aggregate_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Causality
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    causation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # User context
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Event data
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Processing state
    processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    processor: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Error handling
    failed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)