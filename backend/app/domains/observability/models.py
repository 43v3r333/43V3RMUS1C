"""
Observability Domain Models - Production-grade telemetry
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum
from dataclasses import dataclass, field

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class TraceStatus(str, Enum):
    """Trace status"""
    STARTED = "started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MetricType(str, Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ExecutionTrace(BaseModel):
    """Distributed execution trace model"""
    __tablename__ = "execution_traces"
    
    # Trace identification
    trace_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    span_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    parent_span_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Service info
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    service_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Operation info
    operation_name: Mapped[str] = mapped_column(String(255), nullable=False)
    operation_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    
    # Timing
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=TraceStatus.STARTED.value, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Context
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    execution_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Metadata
    attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # User context
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class TelemetryEvent(BaseModel):
    """Telemetry event model for observability"""
    __tablename__ = "telemetry_events"
    
    # Event identification
    event_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Source info
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Event type
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Severity
    severity: Mapped[str] = mapped_column(String(20), default=AlertSeverity.INFO.value, index=True)
    
    # Timing
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Data
    data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    metrics: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # User
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class RuntimeMetric(BaseModel):
    """Runtime metric model for performance tracking"""
    __tablename__ = "runtime_metrics"
    
    # Metric identification
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    metric_type: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Value
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Source
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Context
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Tags
    tags: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON, nullable=True)
    labels: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON, nullable=True)
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Aggregation
    aggregation_window: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    aggregation_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)


class OrchestrationMetric(BaseModel):
    """Orchestration metrics model"""
    __tablename__ = "orchestration_metrics"
    
    # Metric identification
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Value
    value: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Category
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Context
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    execution_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Tags
    tags: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON, nullable=True)
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class HealthCheck(BaseModel):
    """Health check model"""
    __tablename__ = "health_checks"
    
    # Service info
    service_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    service_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="healthy", index=True)
    is_healthy: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Health details
    checks: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    dependencies: Mapped[Optional[Dict[str, bool]]] = mapped_column(JSON, nullable=True)
    
    # Metrics
    response_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    uptime_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timestamp
    checked_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class Alert(BaseModel):
    """Alert model for observability"""
    __tablename__ = "alerts"
    
    # Alert identification
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Severity
    severity: Mapped[str] = mapped_column(String(20), default=AlertSeverity.WARNING.value, index=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Source
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Description
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Data
    metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Context
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    execution_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timing
    triggered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Acknowledgement
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class LogEntry(BaseModel):
    """Structured log entry model"""
    __tablename__ = "log_entries"
    
    # Log identification
    log_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Source
    logger: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Level
    level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Message
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Context
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Trace info
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    span_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timing
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # User
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Resource
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)