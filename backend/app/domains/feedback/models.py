"""
Feedback Models - Self-optimizing runtime systems and adaptive learning.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from ...models.base import BaseModel


class FeedbackType(str, Enum):
    DURATION = "duration"
    QUALITY = "quality"
    COST = "cost"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    SATISFACTION = "satisfaction"
    RESOURCE_EFFICIENCY = "resource_efficiency"
    CUSTOM = "custom"


class TuningAction(str, Enum):
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    RETRY_STRATEGY = "retry_strategy"
    RESOURCE_REBALANCE = "resource_rebalance"
    BATCH_SIZE_ADJUST = "batch_size_adjust"
    CACHE_BYPASS = "cache_bypass"
    MODEL_SWITCH = "model_switch"
    PARAMETER_TUNE = "parameter_tune"
    POLICY_UPDATE = "policy_update"
    THRESHOLD_ADJUST = "threshold_adjust"


class OrchestrationFeedback(BaseModel):
    """Execution outcome feedback from the runtime.

    Captures what happened during an orchestration run so the adaptive layer
    can close the feedback loop.
    """

    __tablename__ = "orchestration_feedback"
    __table_args__ = (
        Index("ix_feedback_subject", "subject_kind", "subject_key"),
        Index("ix_feedback_type", "feedback_type"),
        Index("ix_feedback_correlation", "correlation_id"),
    )

    subject_kind: Mapped[str] = mapped_column(String(50), nullable=False)
    subject_key: Mapped[str] = mapped_column(String(255), nullable=False)

    feedback_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Signal values
    expected_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    delta_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Quality signals
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Context
    context: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Attribution
    workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    agent_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    policy_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    heuristic_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Temporal
    execution_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    execution_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class AdaptiveLearningState(BaseModel):
    """Current learned parameters per context.

    The learning engine updates these after each tuning cycle. They act as
    the "memory" of the adaptive system.
    """

    __tablename__ = "adaptive_learning_states"
    __table_args__ = (
        UniqueConstraint("context_key", "parameter_name", name="uq_learning_state_key_param"),
        Index("ix_learning_state_context", "context_key"),
    )

    context_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    parameter_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Learned value
    current_value: Mapped[float] = mapped_column(Float, nullable=False)
    min_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Learning metadata
    value_source: Mapped[str] = mapped_column(String(32), nullable=False, default="initial")  # initial / heuristic / learned
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    sample_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # History (rolling window as JSON)
    history: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)

    # Decay / expiry
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class AutonomousTuningRecord(BaseModel):
    """Record of an autonomous parameter adjustment and its outcome."""

    __tablename__ = "autonomous_tuning_records"
    __table_args__ = (
        Index("ix_tuning_record_cycle", "cycle_id"),
        Index("ix_tuning_record_param", "parameter_name"),
        Index("ix_tuning_record_state", "tuning_state"),
    )

    cycle_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    parameter_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Before/after
    before_value: Mapped[float] = mapped_column(Float, nullable=False)
    after_value: Mapped[float] = mapped_column(Float, nullable=False)
    delta: Mapped[float] = mapped_column(Float, nullable=False)

    # Action taken
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    action_config: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Reasoning
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    triggered_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    heuristic_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Outcome
    outcome_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    improvement_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tuning_state: Mapped[str] = mapped_column(
        String(32), nullable=False, default="applied", index=True
    )

    # Confidence
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    evaluated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class TuningCycle(BaseModel):
    """Groups a batch of tuning actions into a single adaptive cycle."""

    __tablename__ = "tuning_cycles"
    __table_args__ = (
        Index("ix_tuning_cycle_state", "cycle_state"),
        Index("ix_tuning_cycle_context", "context_key"),
    )

    cycle_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)

    context_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Cycle configuration
    target_metric: Mapped[str] = mapped_column(String(50), nullable=False)
    target_improvement: Mapped[float] = mapped_column(Float, nullable=False, default=0.1)
    max_iterations: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

    # Progress
    iteration: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cycle_state: Mapped[str] = mapped_column(String(32), nullable=False, default="running", index=True)

    # Results
    best_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    best_parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Tuning actions in this cycle
    tuning_records: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


__all__ = [
    "FeedbackType",
    "TuningAction",
    "OrchestrationFeedback",
    "AdaptiveLearningState",
    "AutonomousTuningRecord",
    "TuningCycle",
]