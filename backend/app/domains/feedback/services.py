"""
Feedback Services - Self-optimizing runtime systems and adaptive tuning loops.
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from .models import (
    AdaptiveLearningState,
    AutonomousTuningRecord,
    FeedbackType,
    OrchestrationFeedback,
    TuningAction,
    TuningCycle,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data transfer types
# ---------------------------------------------------------------------------

@dataclass
class FeedbackSnapshot:
    feedback_id: str
    subject_key: str
    feedback_type: str
    actual_value: float
    expected_value: float
    delta_pct: float
    quality_score: float
    observed_at: datetime


@dataclass
class TuningRecommendation:
    parameter_name: str
    current_value: float
    recommended_value: float
    action: TuningAction
    reason: str
    expected_improvement: float
    confidence: float


# ---------------------------------------------------------------------------
# Feedback loop service
# ---------------------------------------------------------------------------

class FeedbackLoopService:
    """Collects, stores, and analyzes execution feedback for closed-loop optimization.

    This service is the ingestion point for all runtime feedback signals. It
    normalizes feedback, feeds it into the learning engine, and surfaces
    actionable insights to the adaptive scheduler.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def ingest(
        self,
        *,
        subject_kind: str,
        subject_key: str,
        feedback_type: FeedbackType,
        actual_value: float,
        expected_value: Optional[float] = None,
        quality_score: Optional[float] = None,
        error_rate: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        policy_id: Optional[UUID] = None,
        heuristic_id: Optional[UUID] = None,
        execution_start: datetime,
        execution_end: Optional[datetime] = None,
        correlation_id: Optional[str] = None,
    ) -> OrchestrationFeedback:
        """Ingest a feedback signal from the runtime."""
        delta_pct = None
        if expected_value is not None and expected_value != 0:
            delta_pct = (actual_value - expected_value) / abs(expected_value)

        feedback = OrchestrationFeedback(
            subject_kind=subject_kind,
            subject_key=subject_key,
            feedback_type=feedback_type.value,
            expected_value=expected_value,
            actual_value=actual_value,
            delta_pct=delta_pct,
            quality_score=quality_score,
            error_rate=error_rate,
            context=dict(context or {}),
            workflow_id=workflow_id,
            agent_id=agent_id,
            policy_id=policy_id,
            heuristic_id=heuristic_id,
            execution_start=execution_start,
            execution_end=execution_end,
            observed_at=datetime.utcnow(),
            correlation_id=correlation_id,
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def get_recent_feedback(
        self,
        *,
        subject_key: Optional[str] = None,
        feedback_type: Optional[FeedbackType] = None,
        since: Optional[datetime] = None,
        limit: int = 50,
    ) -> List[OrchestrationFeedback]:
        query = self.db.query(OrchestrationFeedback)
        if subject_key:
            query = query.filter(OrchestrationFeedback.subject_key == subject_key)
        if feedback_type:
            query = query.filter(OrchestrationFeedback.feedback_type == feedback_type.value)
        if since:
            query = query.filter(OrchestrationFeedback.observed_at >= since)
        return query.order_by(OrchestrationFeedback.observed_at.desc()).limit(limit).all()

    def analyze_outcomes(
        self,
        *,
        subject_kind: Optional[str] = None,
        feedback_type: Optional[FeedbackType] = None,
        since: Optional[datetime] = None,
    ) -> Dict[str, float]:
        """Compute aggregate outcome statistics."""
        query = self.db.query(OrchestrationFeedback).filter(
            OrchestrationFeedback.actual_value.isnot(None)
        )
        if subject_kind:
            query = query.filter(OrchestrationFeedback.subject_kind == subject_kind)
        if feedback_type:
            query = query.filter(OrchestrationFeedback.feedback_type == feedback_type.value)
        if since:
            query = query.filter(OrchestrationFeedback.observed_at >= since)

        rows = query.all()
        if not rows:
            return {"count": 0.0, "mean_actual": 0.0, "mean_delta_pct": 0.0}

        actuals = [r.actual_value for r in rows if r.actual_value is not None]
        deltas = [r.delta_pct for r in rows if r.delta_pct is not None]
        quality_scores = [r.quality_score for r in rows if r.quality_score is not None]

        return {
            "count": float(len(rows)),
            "mean_actual": sum(actuals) / len(actuals) if actuals else 0.0,
            "mean_delta_pct": sum(deltas) / len(deltas) if deltas else 0.0,
            "mean_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0.0,
            "error_count": sum(1 for r in rows if r.error_rate and r.error_rate > 0.1),
        }

    def get_feedback_by_workflow(
        self,
        *,
        workflow_id: str,
        limit: int = 100,
    ) -> List[OrchestrationFeedback]:
        return (
            self.db.query(OrchestrationFeedback)
            .filter(OrchestrationFeedback.workflow_id == workflow_id)
            .order_by(OrchestrationFeedback.observed_at.desc())
            .limit(limit)
            .all()
        )


# ---------------------------------------------------------------------------
# Adaptive tuning service
# ---------------------------------------------------------------------------

class AdaptiveTuningService:
    """Closed-loop autonomous parameter tuning.

    Implements a hill-climbing style tuning loop that observes feedback,
    computes gradients, and adjusts parameters within configured bounds.
    """

    STEP_SIZE = 0.05  # fraction of range per step
    MIN_CONFIDENCE = 0.3

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_tuning_cycle(
        self,
        *,
        context_key: str,
        target_metric: str,
        target_improvement: float = 0.1,
        max_iterations: int = 10,
        description: Optional[str] = None,
    ) -> TuningCycle:
        cycle = TuningCycle(
            cycle_id=f"cycle_{uuid4()}",
            context_key=context_key,
            description=description,
            target_metric=target_metric,
            target_improvement=target_improvement,
            max_iterations=max_iterations,
            started_at=datetime.utcnow(),
        )
        self.db.add(cycle)
        self.db.commit()
        self.db.refresh(cycle)
        return cycle

    def tune_parameter(
        self,
        *,
        parameter_name: str,
        context_key: str,
        current_value: float,
        outcome_score: Optional[float],
        action: TuningAction = TuningAction.PARAMETER_TUNE,
        reason: str = "",
        triggered_by: Optional[str] = None,
        heuristic_id: Optional[UUID] = None,
        confidence: float = 0.5,
        cycle_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> AutonomousTuningRecord:
        """Apply a single parameter tuning step."""
        before = current_value

        # Compute new value based on gradient direction
        if outcome_score is not None and outcome_score > 0.5:
            # Good outcome: step in the same direction
            delta = self.STEP_SIZE * current_value * 0.1
            after = before + delta
        elif outcome_score is not None:
            # Bad outcome: step in opposite direction
            delta = self.STEP_SIZE * current_value * 0.1
            after = before - delta
        else:
            # Neutral: keep as is
            delta = 0.0
            after = before

        # Apply bounds from learning state if available
        state = self.get_learning_state(context_key, parameter_name)
        if state:
            if state.min_value is not None:
                after = max(state.min_value, after)
            if state.max_value is not None:
                after = min(state.max_value, after)

        # Update learning state
        self._update_learning_state(
            context_key=context_key,
            parameter_name=parameter_name,
            new_value=after,
            confidence=confidence,
        )

        record = AutonomousTuningRecord(
            cycle_id=cycle_id or f"standalone_{uuid4()}",
            parameter_name=parameter_name,
            before_value=before,
            after_value=after,
            delta=after - before,
            action=action.value,
            reason=reason,
            triggered_by=triggered_by,
            heuristic_id=heuristic_id,
            outcome_score=outcome_score,
            improvement_pct=((after - before) / max(before, 0.001)) if before else 0.0,
            tuning_state="applied",
            confidence=confidence,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            correlation_id=correlation_id,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        # Attach to cycle if provided
        if cycle_id:
            cycle = (
                self.db.query(TuningCycle)
                .filter(TuningCycle.cycle_id == cycle_id)
                .first()
            )
            if cycle:
                cycle.tuning_records = list(cycle.tuning_records or []) + [str(record.id)]
                cycle.iteration += 1

                # Update best if improved
                if outcome_score is not None:
                    if cycle.best_score is None or outcome_score > cycle.best_score:
                        cycle.best_score = outcome_score

                self.db.commit()

        return record

    def get_learning_state(
        self, context_key: str, parameter_name: str
    ) -> Optional[AdaptiveLearningState]:
        return (
            self.db.query(AdaptiveLearningState)
            .filter(
                AdaptiveLearningState.context_key == context_key,
                AdaptiveLearningState.parameter_name == parameter_name,
                or_(
                    AdaptiveLearningState.expires_at.is_(None),
                    AdaptiveLearningState.expires_at > datetime.utcnow(),
                ),
            )
            .first()
        )

    def _update_learning_state(
        self,
        *,
        context_key: str,
        parameter_name: str,
        new_value: float,
        confidence: float,
    ) -> None:
        existing = self.get_learning_state(context_key, parameter_name)
        if existing is None:
            state = AdaptiveLearningState(
                context_key=context_key,
                parameter_name=parameter_name,
                current_value=new_value,
                value_source="learned",
                confidence=confidence,
                sample_count=1,
                history=[],
                last_updated=datetime.utcnow(),
            )
            self.db.add(state)
        else:
            # Update
            existing.current_value = new_value
            existing.confidence = min(1.0, existing.confidence + 0.01)
            existing.sample_count += 1
            existing.last_updated = datetime.utcnow()

            # Rolling history (keep last 20)
            history = list(existing.history or [])
            history.append({
                "value": new_value,
                "timestamp": datetime.utcnow().isoformat(),
                "confidence": confidence,
            })
            existing.history = history[-20:]

        self.db.commit()

    def get_tuning_recommendations(
        self,
        *,
        context_key: str,
        parameters: List[str],
        current_values: Dict[str, float],
        recent_outcomes: List[float],
        limit: int = 5,
    ) -> List[TuningRecommendation]:
        """Suggest parameter adjustments based on recent outcomes."""
        recommendations: List[TuningRecommendation] = []

        if not recent_outcomes:
            return recommendations

        avg_outcome = sum(recent_outcomes) / len(recent_outcomes)
        outcome_trend = (
            (recent_outcomes[-1] - recent_outcomes[0]) / max(recent_outcomes[0], 0.001)
            if len(recent_outcomes) > 1
            else 0.0
        )

        for param in parameters[:limit]:
            current = current_values.get(param, 0.0)
            state = self.get_learning_state(context_key, param)

            # Compute gradient direction
            if outcome_trend > 0:
                direction = 1.0
            elif outcome_trend < 0:
                direction = -1.0
            else:
                direction = 0.0

            step = self.STEP_SIZE * (state.max_value - state.min_value if state and state.max_value and state.min_value else current * 0.1 + 1.0)
            recommended = current + (direction * step)

            # Clamp to bounds
            if state:
                if state.min_value is not None:
                    recommended = max(state.min_value, recommended)
                if state.max_value is not None:
                    recommended = min(state.max_value, recommended)

            action = TuningAction.PARAMETER_TUNE
            if direction > 0:
                action = TuningAction.SCALE_UP
            elif direction < 0:
                action = TuningAction.SCALE_DOWN

            recommendations.append(TuningRecommendation(
                parameter_name=param,
                current_value=current,
                recommended_value=recommended,
                action=action,
                reason=f"trend={'up' if direction > 0 else 'down' if direction < 0 else 'flat'}; avg_outcome={avg_outcome:.2f}",
                expected_improvement=abs(outcome_trend),
                confidence=min(state.confidence if state else 0.5, 0.9),
            ))

        return recommendations

    def get_active_cycle(
        self, context_key: str
    ) -> Optional[TuningCycle]:
        return (
            self.db.query(TuningCycle)
            .filter(
                TuningCycle.context_key == context_key,
                TuningCycle.cycle_state == "running",
            )
            .first()
        )

    def complete_cycle(self, cycle_id: str) -> Optional[TuningCycle]:
        cycle = (
            self.db.query(TuningCycle)
            .filter(TuningCycle.cycle_id == cycle_id)
            .first()
        )
        if cycle is None:
            return None
        cycle.cycle_state = "completed"
        cycle.completed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(cycle)
        return cycle

    def get_tuning_history(
        self,
        *,
        parameter_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[AutonomousTuningRecord]:
        query = self.db.query(AutonomousTuningRecord)
        if parameter_name:
            query = query.filter(AutonomousTuningRecord.parameter_name == parameter_name)
        return query.order_by(AutonomousTuningRecord.started_at.desc()).limit(limit).all()


__all__ = [
    "FeedbackLoopService",
    "AdaptiveTuningService",
    "FeedbackSnapshot",
    "TuningRecommendation",
]