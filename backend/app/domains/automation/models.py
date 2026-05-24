"""
Automation Models - Rule-based automation
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class TriggerType(str, Enum):
    """Trigger types"""
    EVENT = "event"
    SCHEDULE = "schedule"
    CONDITION = "condition"
    WEBHOOK = "webhook"


class RuleStatus(str, Enum):
    """Automation rule status"""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class AutomationTrigger(BaseModel):
    """Automation trigger model"""
    __tablename__ = "automation_triggers"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Configuration
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Filters
    event_filters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    conditions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)


class AutomationRule(BaseModel):
    """Automation rule model"""
    __tablename__ = "automation_rules"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=RuleStatus.ACTIVE.value, index=True)
    
    # Trigger
    trigger_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("automation_triggers.id"),
        nullable=True
    )
    
    # Actions
    actions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=False)
    
    # Configuration
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    max_executions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Error handling
    retry_on_failure: Mapped[bool] = mapped_column(Boolean, default=True)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    
    # Last execution
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)