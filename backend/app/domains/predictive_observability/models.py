"""
Predictive Observability Models - Runtime forecasting and predictive analytics.

Provides:
- Predictive runtime analytics
- Orchestration stability forecasting
- Execution anomaly detection
- Adaptive telemetry cognition
- Distributed diagnostics systems
- Runtime forecasting infrastructure
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class ForecastType(str, Enum):
    """Forecast type"""
    DURATION = "duration"
    RESOURCE_USAGE = "resource_usage"
    FAILURE = "failure"
    QUEUE_TIME = "queue_time"
    PERFORMANCE = "performance"
    CAPACITY = "capacity"


class ForecastHorizon(str, Enum):
    """Forecast horizon"""
    SHORT = "short"  # < 15 min
    MEDIUM = "medium"  # 15-60 min
    LONG = "long"  # > 60 min


class ForecastStatus(str, Enum):
    """Forecast status"""
    PENDING = "pending"
    ACTIVE = "active"
    VALIDATED = "validated"
    EXPIRED = "expired"


class MetricGranularity(str, Enum):
    """Metric granularity"""
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"


class PredictiveRuntimeForecast(BaseModel):
    """Predictive runtime forecasts - execution forecasting"""
    __tablename__ = "predictive_runtime_forecasts"
    
    # Forecast identification
    forecast_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type and horizon
    forecast_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    horizon: Mapped[str] = mapped_column(String(20), default=ForecastHorizon.SHORT.value, index=True)
    
    # Target
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Prediction
    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Confidence
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Range
    min_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Model info
    model_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Features
    features: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    
    # Validation
    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    prediction_error: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=ForecastStatus.PENDING.value, index=True)
    
    # Timing
    predicted_for: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Index for forecast queries
    __table_args__ = (
        Index('ix_forecasts_target_type', 'target_id', 'target_type'),
        Index('ix_forecasts_type_horizon', 'forecast_type', 'horizon'),
    )


class OrchestrationStabilityMetric(BaseModel):
    """Orchestration stability metrics - stability tracking"""
    __tablename__ = "orchestration_stability_metrics"
    
    # Metric identification
    metric_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Target
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Values
    current_value: Mapped[float] = mapped_column(Float, default=0.0)
    previous_value: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Thresholds
    healthy_threshold: Mapped[float] = mapped_column(Float, default=0.9)
    warning_threshold: Mapped[float] = mapped_column(Float, default=0.7)
    critical_threshold: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Trend
    trend: Mapped[str] = mapped_column(String(20), default="stable")
    volatility: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Timing
    measured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class AdaptiveTelemetryDataPoint(BaseModel):
    """Adaptive telemetry data points - collected metrics"""
    __tablename__ = "adaptive_telemetry_data_points"
    
    # Data point identification
    point_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Target
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Value
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Tags
    tags: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON, nullable=True)
    
    # Granularity
    granularity: Mapped[str] = mapped_column(String(20), default=MetricGranularity.MINUTE.value)
    
    # Timing
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Index for time-series queries
    __table_args__ = (
        Index('ix_telemetry_target_metric', 'target_id', 'metric_name', 'timestamp'),
    )


class DistributedDiagnosticsResult(BaseModel):
    """Distributed diagnostics results - diagnostic outputs"""
    __tablename__ = "distributed_diagnostics_results"
    
    # Diagnostics identification
    diagnostics_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    diagnostics_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Target
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Results
    health_score: Mapped[float] = mapped_column(Float, default=1.0)
    issues_found: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Details
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    executed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class AnomalyForecast(BaseModel):
    """Anomaly forecast - predicted anomalies"""
    __tablename__ = "anomaly_forecasts"
    
    # Forecast identification
    forecast_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    anomaly_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Target
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Prediction
    predicted_occurrence: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    probability: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Severity
    severity: Mapped[str] = mapped_column(String(20), default="warning")
    
    # Evidence
    evidence: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Status
    is_mitigated: Mapped[bool] = mapped_column(Boolean, default=False)
    mitigation_action: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Validation
    actual_occurred: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class TelemetryAggregation(BaseModel):
    """Telemetry aggregation - aggregated metrics"""
    __tablename__ = "telemetry_aggregations"
    
    # Aggregation identification
    aggregation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Scope
    target_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Aggregation
    aggregation_type: Mapped[str] = mapped_column(String(20), nullable=False)  # avg, sum, min, max, count
    
    # Values
    value: Mapped[float] = mapped_column(Float, nullable=False)
    min_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Granularity
    granularity: Mapped[str] = mapped_column(String(20), nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Tags
    tags: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON, nullable=True)
    
    # Index for aggregation queries
    __table_args__ = (
        Index('ix_aggregations_metric_granularity', 'metric_name', 'granularity', 'period_start'),
    )


class ForecastModel(BaseModel):
    """Forecast model - tracking prediction models"""
    __tablename__ = "forecast_models"
    
    # Model identification
    model_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    model_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    forecast_target: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Configuration
    hyperparameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    features: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    
    # Performance
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    precision: Mapped[float] = mapped_column(Float, default=0.0)
    recall: Mapped[float] = mapped_column(Float, default=0.0)
    f1_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Training
    training_samples: Mapped[int] = mapped_column(Integer, default=0)
    validation_samples: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    trained_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class RuntimeAnomalyEvent(BaseModel):
    """Runtime anomaly event - detected anomalies"""
    __tablename__ = "runtime_anomaly_events"
    
    # Event identification
    event_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    anomaly_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Severity
    severity: Mapped[str] = mapped_column(String(20), default="warning")
    
    # Target
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Detection
    detection_method: Mapped[str] = mapped_column(String(50), nullable=False)
    detection_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Values
    expected_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    deviation: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Context
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Resolution
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)