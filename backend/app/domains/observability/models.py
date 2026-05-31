"""
Observability Domain Models - Monitoring, metrics, and health checks

NOTE: RuntimeMetric is defined in runtime/models.py to avoid duplicate registration.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from enum import Enum

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, JSON, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


# Enum stubs
class TraceStatus(str, Enum):
    STARTED = "started"
    OK = "ok"
    ERROR = "error"
    UNSET = "unset"
    COMPLETED = "completed"


class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


class AlertSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    WARNING = "warning"


# Stub classes - all else moved or deprecated
class ExecutionTrace:
    __table__ = None
    def __init__(self, *args, **kwargs):
        raise RuntimeError("ExecutionTrace stub - import from original location")


class TelemetryEvent:
    __table__ = None
    def __init__(self, *args, **kwargs):
        raise RuntimeError("TelemetryEvent stub - import from original location")


class OrchestrationMetric:
    __table__ = None
    def __init__(self, *args, **kwargs):
        raise RuntimeError("OrchestrationMetric stub - import from original location")


class RuntimeMetric:
    __table__ = None
    def __init__(self, *args, **kwargs):
        raise RuntimeError("RuntimeMetric is in runtime/models.py")


class Alert(BaseModel):
    __tablename__ = "alerts"
    name = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(Text, nullable=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)


class LogEntry(BaseModel):
    __tablename__ = "log_entries"
    level = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    logger = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_ = Column("metadata", JSON, nullable=True)


class HealthCheck(BaseModel):
    """Health check model"""
    __tablename__ = "health_checks"
    
    service_name = Column(String(100), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    detail = Column(Text, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow, index=True)
    response_time_ms = Column(Float, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)