"""
Forecasting Services - Long-horizon execution planning and prediction.
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence
from uuid import UUID, uuid4

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from .models import (
    ExecutionForecast,
    ForecastHorizon,
    ForecastKind,
    MultiStageExecutionGraph,
    OrchestrationStrategy,
    PredictiveRuntimeMetric,
    StrategyKind,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data transfer types
# ---------------------------------------------------------------------------


@dataclass
class ForecastSnapshot:
    subject_key: str
    forecast_kind: ForecastKind
    predicted: float
    confidence: float
    horizon: str
    lower: Optional[float] = None
    upper: Optional[float] = None
    features: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StagePlanResult:
    stage_id: str
    label: str
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: float = 0.0
    resource_requirements: Dict[str, float] = field(default_factory=dict)
    can_parallelize: bool = True
    risk_score: float = 0.0


@dataclass
class StrategyDecision:
    strategy: StrategyKind
    rationale: str
    expected_improvement: float
    confidence: float
    scores: Dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Forecasting service
# ---------------------------------------------------------------------------


class ForecastingService:
    """Predictive execution engine.

    Maintains a lightweight adaptive model per ``(subject_kind, subject_key,
    forecast_kind)`` using an exponential moving average of historical outcomes.
    Stores results as ``ExecutionForecast`` and ``PredictiveRuntimeMetric`` rows.
    """

    ALPHA = 0.3  # EMA smoothing factor

    def __init__(self, db: Session) -> None:
        self.db = db

    # ---- single forecasts -----------------------------------------------

    def forecast(
        self,
        *,
        subject_kind: str,
        subject_key: str,
        forecast_kind: ForecastKind,
        features: Optional[Dict[str, Any]] = None,
        horizon: Optional[ForecastHorizon] = None,
    ) -> ExecutionForecast:
        """Produce an execution forecast for the given subject.

        Uses a simple EMA baseline; in production this would delegate to the
        predictive-model service loaded from the learning domain.
        """
        horizon_value = (horizon or ForecastHorizon.NEAR_TERM).value

        # Load recent realized forecasts for the subject
        recent = (
            self.db.query(ExecutionForecast)
            .filter(
                ExecutionForecast.subject_kind == subject_kind,
                ExecutionForecast.subject_key == subject_key,
                ExecutionForecast.forecast_kind == forecast_kind.value,
                ExecutionForecast.actual_value.isnot(None),
            )
            .order_by(ExecutionForecast.realized_at.desc())
            .limit(20)
            .all()
        )

        if recent:
            # EMA of realized values
            values = [r.actual_value for r in recent if r.actual_value is not None]
            predicted = values[0]
            alpha = self.ALPHA
            for v in values[1:]:
                predicted = alpha * v + (1 - alpha) * predicted
            # Width based on recent error
            errors = [
                abs(r.actual_value - r.predicted_value) / max(r.predicted_value, 1e-6)
                for r in recent
                if r.actual_value and r.predicted_value
            ]
            error_margin = (sum(errors) / len(errors)) if errors else 0.1
            lower = predicted * (1 - error_margin)
            upper = predicted * (1 + error_margin)
            confidence = max(0.3, 1.0 - error_margin)
        else:
            # No history — return conservative defaults by kind
            defaults = {
                ForecastKind.DURATION: (120.0, 60.0, 240.0),
                ForecastKind.QUEUE_TIME: (30.0, 5.0, 120.0),
                ForecastKind.FAILURE_PROBABILITY: (0.05, 0.0, 0.2),
                ForecastKind.RESOURCE_NEED: (1024.0, 512.0, 2048.0),
                ForecastKind.COST: (0.5, 0.1, 2.0),
                ForecastKind.QUALITY: (0.8, 0.5, 1.0),
            }
            vals = defaults.get(forecast_kind, (100.0, 50.0, 200.0))
            predicted, lower, upper = vals
            confidence = 0.4

        predicted_for = self._predict_for(horizon_value)
        method = "ema_adaptive"

        forecast_row = ExecutionForecast(
            subject_kind=subject_kind,
            subject_key=subject_key,
            forecast_kind=forecast_kind.value,
            horizon=horizon_value,
            predicted_value=predicted,
            lower_bound=lower,
            upper_bound=upper,
            confidence=confidence,
            features=dict(features or {}),
            method=method,
            predicted_for=predicted_for,
        )
        self.db.add(forecast_row)
        self.db.commit()
        self.db.refresh(forecast_row)
        return forecast_row

    def realize(self, forecast_id: UUID, actual: float) -> Optional[ExecutionForecast]:
        """Record the realized outcome against a pending forecast."""
        forecast = self.db.get(ExecutionForecast, forecast_id)
        if forecast is None:
            return None
        forecast.actual_value = actual
        forecast.realized_at = datetime.utcnow()
        forecast.error_pct = (
            abs(actual - forecast.predicted_value) / max(abs(forecast.predicted_value), 1e-6)
        )
        forecast.lifecycle_state = "realized"
        self.db.commit()
        self.db.refresh(forecast)
        return forecast

    def realize_latest(
        self,
        *,
        subject_kind: str,
        subject_key: str,
        forecast_kind: ForecastKind,
        actual: float,
    ) -> Optional[ExecutionForecast]:
        """Find the latest pending forecast for the subject and realize it."""
        pending = (
            self.db.query(ExecutionForecast)
            .filter(
                ExecutionForecast.subject_kind == subject_kind,
                ExecutionForecast.subject_key == subject_key,
                ExecutionForecast.forecast_kind == forecast_kind.value,
                ExecutionForecast.lifecycle_state == "pending",
            )
            .order_by(ExecutionForecast.predicted_for.asc())
            .first()
        )
        if pending is None:
            return None
        return self.realize(pending.id, actual)

    def get_active_forecasts(
        self,
        *,
        subject_kind: Optional[str] = None,
        subject_key: Optional[str] = None,
        horizon: Optional[str] = None,
        limit: int = 50,
    ) -> List[ExecutionForecast]:
        query = self.db.query(ExecutionForecast).filter(
            ExecutionForecast.lifecycle_state == "pending",
            ExecutionForecast.predicted_for >= datetime.utcnow() - timedelta(hours=1),
        )
        if subject_kind:
            query = query.filter(ExecutionForecast.subject_kind == subject_kind)
        if subject_key:
            query = query.filter(ExecutionForecast.subject_key == subject_key)
        if horizon:
            query = query.filter(ExecutionForecast.horizon == horizon)
        return query.order_by(ExecutionForecast.predicted_for.asc()).limit(limit).all()

    def get_forecast_accuracy(
        self,
        *,
        subject_kind: Optional[str] = None,
        forecast_kind: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> Dict[str, float]:
        query = self.db.query(ExecutionForecast).filter(
            ExecutionForecast.actual_value.isnot(None),
            ExecutionForecast.error_pct.isnot(None),
        )
        if subject_kind:
            query = query.filter(ExecutionForecast.subject_kind == subject_kind)
        if forecast_kind:
            query = query.filter(ExecutionForecast.forecast_kind == forecast_kind)
        if since:
            query = query.filter(ExecutionForecast.realized_at >= since)

        realized = query.all()
        if not realized:
            return {"count": 0.0, "mean_error_pct": 0.0, "mae": 0.0}

        errors = [abs(f.error_pct) for f in realized if f.error_pct is not None]
        maes = [
            abs(f.actual_value - f.predicted_value)
            for f in realized
            if f.actual_value is not None
        ]
        return {
            "count": float(len(realized)),
            "mean_error_pct": sum(errors) / len(errors) if errors else 0.0,
            "mae": sum(maes) / len(maes) if maes else 0.0,
        }

    # ---- runtime metric forecasts ---------------------------------------

    def forecast_runtime_metric(
        self,
        *,
        metric_name: str,
        metric_kind: str,
        scope_key: str,
        window_start: datetime,
        window_seconds: int,
        confidence: float = 0.7,
    ) -> PredictiveRuntimeMetric:
        """Predict a runtime metric over a time window.

        A simple rolling mean; extend via learning domain for heavier models.
        """
        # Load last 5 observed values for the same metric
        recent = (
            self.db.query(PredictiveRuntimeMetric)
            .filter(
                PredictiveRuntimeMetric.metric_name == metric_name,
                PredictiveRuntimeMetric.scope_key == scope_key,
                PredictiveRuntimeMetric.observed_value.isnot(None),
            )
            .order_by(PredictiveRuntimeMetric.window_start.desc())
            .limit(5)
            .all()
        )
        if recent:
            vals = [r.observed_value for r in recent if r.observed_value is not None]
            pred = sum(vals) / len(vals)
            error_half = 0.1 * pred
        else:
            pred = 0.0
            error_half = 0.0

        window_end = window_start + timedelta(seconds=window_seconds)
        metric = PredictiveRuntimeMetric(
            metric_name=metric_name,
            metric_kind=metric_kind,
            scope_key=scope_key,
            window_start=window_start,
            window_end=window_end,
            bucket_seconds=window_seconds,
            predicted_value=pred,
            lower_bound=max(0.0, pred - error_half),
            upper_bound=pred + error_half,
            confidence=confidence,
            method="rolling_mean",
        )
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        return metric

    def get_runtime_forecast_series(
        self,
        *,
        metric_name: str,
        scope_key: str,
        from_time: datetime,
        to_time: datetime,
        bucket_seconds: int = 300,
    ) -> List[PredictiveRuntimeMetric]:
        return (
            self.db.query(PredictiveRuntimeMetric)
            .filter(
                PredictiveRuntimeMetric.metric_name == metric_name,
                PredictiveRuntimeMetric.scope_key == scope_key,
                PredictiveRuntimeMetric.window_start >= from_time,
                PredictiveRuntimeMetric.window_start <= to_time,
            )
            .order_by(PredictiveRuntimeMetric.window_start.asc())
            .all()
        )

    # ---- helper --------------------------------------------------------

    def _predict_for(self, horizon_value: str) -> datetime:
        offsets = {
            ForecastHorizon.IMMEDIATE.value: timedelta(seconds=30),
            ForecastHorizon.NEAR_TERM.value: timedelta(minutes=5),
            ForecastHorizon.SHORT.value: timedelta(hours=2),
            ForecastHorizon.LONG.value: timedelta(hours=12),
            ForecastHorizon.EXTENDED.value: timedelta(days=1),
        }
        return datetime.utcnow() + offsets.get(horizon_value, timedelta(minutes=15))


# ---------------------------------------------------------------------------
# Multi-stage planner
# ---------------------------------------------------------------------------


class MultiStagePlanner:
    """Builds multi-stage execution DAGs from workflow definitions.

    Takes a list of step descriptors and produces an ordered, dependency-aware
    plan with estimated durations, risk scores and parallelism factors.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def plan(
        self,
        *,
        subject_kind: str,
        subject_key: str,
        plan_label: str,
        steps: List[Dict[str, Any]],
        selected_strategy: Optional[StrategyKind] = None,
        correlation_id: Optional[str] = None,
        owner_id: Optional[UUID] = None,
    ) -> MultiStageExecutionGraph:
        """Convert a list of step descriptors into a staged execution graph."""
        stages: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []
        total_duration = 0.0
        max_parallelism = 1.0

        for i, step in enumerate(steps):
            stage_id = step.get("id", f"stage_{i}")
            deps = step.get("depends_on", [])

            for dep in deps:
                edges.append({
                    "from": str(dep),
                    "to": stage_id,
                    "kind": "depends_on",
                })

            est = float(step.get("estimated_duration", 60.0))
            risk = float(step.get("risk_score", 0.1))
            parallel = bool(step.get("can_parallelize", False))

            stages.append({
                "stage_id": stage_id,
                "label": step.get("label", f"Step {i+1}"),
                "dependencies": [str(d) for d in deps],
                "estimated_duration": est,
                "resource_requirements": step.get("resources", {}),
                "can_parallelize": parallel,
                "risk_score": risk,
                "index": i,
            })
            total_duration += est
            if parallel:
                max_parallelism = max(max_parallelism, len(steps) - i)

        # Compute risk score for the whole graph
        overall_risk = 1.0 - math.prod(1.0 - s["risk_score"] for s in stages)

        graph = MultiStageExecutionGraph(
            subject_kind=subject_kind,
            subject_key=subject_key,
            plan_label=plan_label,
            stages=stages,
            edges=edges,
            stage_count=len(stages),
            parallelism_factor=max_parallelism,
            estimated_duration=total_duration,
            estimated_cost=total_duration * 0.01,
            risk_score=overall_risk,
            selected_strategy=(selected_strategy.value if selected_strategy else None),
            correlation_id=correlation_id,
            owner_id=owner_id,
        )
        self.db.add(graph)
        self.db.commit()
        self.db.refresh(graph)
        return graph

    def get_active_graphs(
        self,
        *,
        subject_kind: Optional[str] = None,
        subject_key: Optional[str] = None,
        limit: int = 20,
    ) -> List[MultiStageExecutionGraph]:
        query = self.db.query(MultiStageExecutionGraph).filter(
            MultiStageExecutionGraph.lifecycle_state.in_(["planned", "scheduled"])
        )
        if subject_kind:
            query = query.filter(MultiStageExecutionGraph.subject_kind == subject_kind)
        if subject_key:
            query = query.filter(MultiStageExecutionGraph.subject_key == subject_key)
        return query.order_by(MultiStageExecutionGraph.created_at.desc()).limit(limit).all()


# ---------------------------------------------------------------------------
# Strategy engine
# ---------------------------------------------------------------------------


class OrchestrationStrategyEngine:
    """Selects and records the best orchestration strategy for a given context."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def select(
        self,
        *,
        subject_kind: str,
        subject_key: str,
        context: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> StrategyDecision:
        """Score all strategies and record the winner."""
        # Heuristic scoring based on context signals
        scores: Dict[str, float] = {}
        priority = context.get("priority", "normal")
        estimated_duration = float(context.get("estimated_duration", 300))
        has_dependencies = bool(context.get("dependencies", []))

        # Cost-aware: penalize latency-first when cost matters
        if context.get("cost_sensitive", False):
            scores[StrategyKind.LATENCY_FIRST.value] = 0.3
            scores[StrategyKind.COST_AWARE.value] = 0.9
            scores[StrategyKind.THROUGHPUT_FIRST.value] = 0.6
        else:
            scores[StrategyKind.LATENCY_FIRST.value] = 0.85
            scores[StrategyKind.THROUGHPUT_FIRST.value] = 0.7
            scores[StrategyKind.COST_AWARE.value] = 0.4

        # Duration-based
        if estimated_duration < 60:
            scores[StrategyKind.LATENCY_FIRST.value] = max(
                scores.get(StrategyKind.LATENCY_FIRST.value, 0), 0.95
            )
        elif estimated_duration > 3600:
            scores[StrategyKind.THROUGHPUT_FIRST.value] = max(
                scores.get(StrategyKind.THROUGHPUT_FIRST.value, 0), 0.85
            )
            scores[StrategyKind.BALANCED.value] = 0.8

        # Dependency complexity
        if has_dependencies:
            scores[StrategyKind.CONSERVATIVE.value] = 0.75
        else:
            scores[StrategyKind.AGGRESSIVE_SCALE.value] = 0.7

        # Priority override
        if priority == "urgent":
            scores[StrategyKind.LATENCY_FIRST.value] = max(
                scores.get(StrategyKind.LATENCY_FIRST.value, 0), 1.0
            )

        # Normalize and pick winner
        if not scores:
            winner_kind = StrategyKind.BALANCED
        else:
            winner_kind = StrategyKind(
                max(scores.items(), key=lambda kv: kv[1])[0]
            )

        # Record in DB
        winner_score = scores.get(winner_kind.value, 0.5)
        rationale = f"score={winner_score:.2f}; context={context.get('reason', 'heuristic')}"
        self._record(subject_kind, subject_key, winner_kind, rationale, scores, correlation_id)

        improvement = winner_score * 0.1
        return StrategyDecision(
            strategy=winner_kind,
            rationale=rationale,
            expected_improvement=improvement,
            confidence=winner_score,
            scores=scores,
        )

    def get_active(self, subject_kind: str, subject_key: str) -> Optional[OrchestrationStrategy]:
        return (
            self.db.query(OrchestrationStrategy)
            .filter(
                OrchestrationStrategy.subject_kind == subject_kind,
                OrchestrationStrategy.subject_key == subject_key,
                OrchestrationStrategy.is_active.is_(True),
            )
            .first()
        )

    def get_history(
        self,
        *,
        subject_kind: Optional[str] = None,
        limit: int = 50,
    ) -> List[OrchestrationStrategy]:
        query = self.db.query(OrchestrationStrategy).filter(
            OrchestrationStrategy.is_active.is_(False)
        )
        if subject_kind:
            query = query.filter(OrchestrationStrategy.subject_kind == subject_kind)
        return query.order_by(OrchestrationStrategy.created_at.desc()).limit(limit).all()

    def _record(
        self,
        subject_kind: str,
        subject_key: str,
        strategy: StrategyKind,
        rationale: str,
        scores: Dict[str, float],
        correlation_id: Optional[str],
    ) -> None:
        # Supersede previous active strategy for this subject
        active = (
            self.db.query(OrchestrationStrategy)
            .filter(
                OrchestrationStrategy.subject_kind == subject_kind,
                OrchestrationStrategy.subject_key == subject_key,
                OrchestrationStrategy.is_active.is_(True),
            )
            .all()
        )
        for old in active:
            old.is_active = False
            old.superseded_at = datetime.utcnow()

        new_row = OrchestrationStrategy(
            subject_kind=subject_kind,
            subject_key=subject_key,
            strategy_kind=strategy.value,
            rationale=rationale,
            scores=dict(scores),
            expected_improvement=scores.get(strategy.value, 0.5) * 0.1,
            confidence=scores.get(strategy.value, 0.5),
            is_active=True,
            activated_at=datetime.utcnow(),
            correlation_id=correlation_id,
        )
        self.db.add(new_row)
        self.db.commit()


__all__ = [
    "ForecastingService",
    "MultiStagePlanner",
    "OrchestrationStrategyEngine",
    "ForecastSnapshot",
    "StagePlanResult",
    "StrategyDecision",
]
