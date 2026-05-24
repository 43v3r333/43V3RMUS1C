"""
Forecasting Models - Persistent long-horizon orchestration forecasts.

Three persistent tables:

  - ``execution_forecasts``         predicted outcome for a specific subject
  - ``predictive_runtime_metrics``  rolling timeseries of predicted system metrics
  - ``multi_stage_execution_graphs`` materialized DAGs ahead of dispatch
  - ``orchestration_strategies``    selected strategy + score history
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
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from ...models.base import BaseModel


class ForecastKind(str, Enum):
    """Type of forecasted quantity."""

    DURATION = "duration"
    QUEUE_TIME = "queue_time"
    FAILURE_PROBABILITY = "failure_probability"
    RESOURCE_NEED = "resource_need"
    THROUGHPUT = "throughput"
    SATURATION = "saturation"
    COST = "cost"
    QUALITY = "quality"


class ForecastHorizon(str, Enum):
    """Horizon classification used by the planner."""

    IMMEDIATE = "immediate"  # < 60s
    NEAR_TERM = "near_term"  # 1m - 30m
    SHORT = "short"  # 30m - 6h
    LONG = "long"  # 6h - 24h
    EXTENDED = "extended"  # > 24h


class StrategyKind(str, Enum):
    """Available orchestration strategies."""

    LATENCY_FIRST = "latency_first"
    THROUGHPUT_FIRST = "throughput_first"
    COST_AWARE = "cost_aware"
    QUALITY_FIRST = "quality_first"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"
    AGGRESSIVE_SCALE = "aggressive_scale"


class ExecutionForecast(BaseModel):
    """A predicted outcome for a specific subject (job, workflow, batch)."""

    __tablename__ = "execution_forecasts"
    __table_args__ = (
        Index("ix_forecast_subject", "subject_kind", "subject_key"),
        Index("ix_forecast_kind_horizon", "forecast_kind", "horizon"),
        Index("ix_forecast_predicted_for", "predicted_for"),
    )

    subject_kind: Mapped[str] = mapped_column(String(50), nullable=False)
    subject_key: Mapped[str] = mapped_column(String(255), nullable=False)

    forecast_kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    horizon: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    lower_bound: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    upper_bound: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    features: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    predicted_for: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )

    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    realized_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    lifecycle_state: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending", index=True
    )
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class PredictiveRuntimeMetric(BaseModel):
    """Rolling timeseries of predicted runtime metrics.

    These are operator-facing predictions (predicted CPU, predicted queue depth,
    predicted failure rate over the next window) used to drive autoscaling and
    visibility dashboards.
    """

    __tablename__ = "predictive_runtime_metrics"
    __table_args__ = (
        Index("ix_pred_metric_name_window", "metric_name", "window_start"),
        Index("ix_pred_metric_kind", "metric_kind"),
        UniqueConstraint(
            "metric_name", "window_start", "scope_key",
            name="uq_pred_metric_window",
        ),
    )

    metric_name: Mapped[str] = mapped_column(String(120), nullable=False)
    metric_kind: Mapped[str] = mapped_column(String(50), nullable=False, default="gauge")
    scope_key: Mapped[str] = mapped_column(String(120), nullable=False, default="global")

    window_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    bucket_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=60)

    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    lower_bound: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    upper_bound: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    baseline_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    observed_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    features: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    is_anomalous: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class MultiStageExecutionGraph(BaseModel):
    """A materialized multi-stage execution DAG produced by the planner.

    Captures the planned shape of an execution: stages, nodes, edges, expected
    durations, parallelism factor and resource footprint. The runtime engine
    converts this into actual dispatch.
    """

    __tablename__ = "multi_stage_execution_graphs"
    __table_args__ = (
        Index("ix_msx_graph_subject", "subject_kind", "subject_key"),
        Index("ix_msx_graph_state", "lifecycle_state"),
    )

    subject_kind: Mapped[str] = mapped_column(String(50), nullable=False)
    subject_key: Mapped[str] = mapped_column(String(255), nullable=False)
    plan_label: Mapped[str] = mapped_column(String(255), nullable=False)

    stages: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    edges: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)

    stage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    parallelism_factor: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    estimated_duration: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estimated_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    selected_strategy: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)

    lifecycle_state: Mapped[str] = mapped_column(
        String(32), nullable=False, default="planned", index=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class OrchestrationStrategy(BaseModel):
    """Selected orchestration strategy with explanatory metadata."""

    __tablename__ = "orchestration_strategies"
    __table_args__ = (
        Index("ix_strategy_subject", "subject_kind", "subject_key"),
        Index("ix_strategy_kind", "strategy_kind"),
    )

    subject_kind: Mapped[str] = mapped_column(String(50), nullable=False)
    subject_key: Mapped[str] = mapped_column(String(255), nullable=False)

    strategy_kind: Mapped[str] = mapped_column(String(50), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)

    scores: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    expected_improvement: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    superseded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


__all__ = [
    "ForecastKind",
    "ForecastHorizon",
    "StrategyKind",
    "ExecutionForecast",
    "PredictiveRuntimeMetric",
    "MultiStageExecutionGraph",
    "OrchestrationStrategy",
]
