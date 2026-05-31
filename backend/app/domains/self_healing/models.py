"""
Self-Healing Orchestration Models - Runtime stabilization and recovery.

Provides:
- Orchestration recovery engine
- Predictive anomaly prevention
- Execution resilience systems
- Adaptive stabilization loops
- Runtime recovery intelligence
- Orchestration balancing systems
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class RecoveryState(str, Enum):
    """Recovery state"""
    IDLE = "idle"
    DETECTING = "detecting"
    DIAGNOSING = "diagnosing"
    RECOVERING = "recovering"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


class AnomalySeverity(str, Enum):
    """Anomaly severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ResilienceState(str, Enum):
    """Resilience state"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    RECOVERING = "recovering"
    FAILOVER = "failover"


class StabilizationMode(str, Enum):
    """Stabilization mode"""
    ACTIVE = "active"
    PASSIVE = "passive"
    PREDICTIVE = "predictive"


class OrchestrationResilienceMetric(BaseModel):
    """Orchestration resilience metrics - tracks system health"""
    __tablename__ = "orchestration_resilience_metrics"
    
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
    
    # State
    state: Mapped[str] = mapped_column(String(20), default=ResilienceState.HEALTHY.value)
    
    # Trend
    trend: Mapped[str] = mapped_column(String(20), default="stable")
    change_rate: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Timing
    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


# DEPRECATED: anomaly_detections has moved. Import from authoritative location.
class AnomalyDetection:
    """DEPRECATED: Move to original location. This is a stub to prevent import errors."""
    __table__ = None
    
    def __init__(self, *args, **kwargs):
        raise RuntimeError(
            f"AnomalyDetection is no longer in {filepath}. "
            f"Import from the authoritative location instead."
        )
    
    @classmethod
    def __table__(cls):
        return None


class RecoveryAction(BaseModel):
    """Recovery action - tracked recovery operations"""
    __tablename__ = "recovery_actions"
    
    # Action identification
    action_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Related anomaly
    anomaly_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Action details
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action_description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Target
    target_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Configuration
    action_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # State
    state: Mapped[str] = mapped_column(String(20), default=RecoveryState.IDLE.value, index=True)
    
    # Execution
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Result
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class StabilizationLoop(BaseModel):
    """Stabilization loop - adaptive stabilization cycles"""
    __tablename__ = "stabilization_loops"
    
    # Loop identification
    loop_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    loop_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Target
    target_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Configuration
    mode: Mapped[str] = mapped_column(String(20), default=StabilizationMode.ACTIVE.value)
    interval_seconds: Mapped[int] = mapped_column(Integer, default=60)
    
    # Metrics
    target_metric: Mapped[str] = mapped_column(String(50), nullable=False)
    target_value: Mapped[float] = mapped_column(Float, default=0.9)
    current_value: Mapped[float] = mapped_column(Float, default=0.0)
    
    # State
    state: Mapped[str] = mapped_column(String(20), default="running", index=True)
    
    # Iteration tracking
    iteration_count: Mapped[int] = mapped_column(Integer, default=0)
    max_iterations: Mapped[int] = mapped_column(Integer, default=10)
    
    # History
    iteration_history: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    last_iteration: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class FailurePrediction(BaseModel):
    """Failure prediction - predicted failures"""
    __tablename__ = "failure_predictions"
    
    # Prediction identification
    prediction_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Target
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Prediction
    predicted_failure: Mapped[str] = mapped_column(String(100), nullable=False)
    failure_probability: Mapped[float] = mapped_column(Float, default=0.0)
    severity: Mapped[str] = mapped_column(String(20), default=AnomalySeverity.WARNING.value)
    
    # Timeline
    predicted_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    time_horizon_minutes: Mapped[int] = mapped_column(Integer, default=60)
    
    # Evidence
    evidence: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Status
    is_acted_upon: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    mitigation_action: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Validation
    actual_occurred: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ResiliencePolicy(BaseModel):
    """Resilience policy - rules for resilience behavior"""
    __tablename__ = "resilience_policies"
    
    # Policy identification
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Scope
    policy_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Trigger conditions
    trigger_conditions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Actions
    actions: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    action_order: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Configuration
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=5)
    
    # Metrics
    trigger_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


# DEPRECATED: health_checks has moved. Import from authoritative location.
class HealthCheck:
    """DEPRECATED: Move to original location. This is a stub to prevent import errors."""
    __table__ = None
    
    def __init__(self, *args, **kwargs):
        raise RuntimeError(
            f"HealthCheck is no longer in {filepath}. "
            f"Import from the authoritative location instead."
        )
    
    @classmethod
    def __table__(cls):
        return None


class FailoverRecord(BaseModel):
    """Failover record - tracks failover events"""
    __tablename__ = "failover_records"
    
    # Record identification
    record_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    failover_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Source and target
    source_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Reason
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    reason_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # State
    state: Mapped[str] = mapped_column(String(20), default="initiated", index=True)
    
    # Timing
    initiated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Result
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class RecoveryCheckpoint(BaseModel):
    """Recovery checkpoint - point-in-time recovery state"""
    __tablename__ = "recovery_checkpoints"
    
    # Checkpoint identification
    checkpoint_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Reference
    execution_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # State data
    state_snapshot: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    node_states: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    context_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Checkpoint metadata
    checkpoint_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Sequence
    sequence_number: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)