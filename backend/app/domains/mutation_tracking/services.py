"""
Mutation Tracking Services - Production-grade mutation lineage infrastructure

Provides:
- Mutation lineage tracking
- Cognition evolution tracing
- Semantic adaptation history
- Runtime behavior evolution tracking
- Recursive adaptation telemetry
- Distributed mutation coordination
- Mutation lineage graph building

All services support:
- Async operation
- Indexed lineage tracking
- Temporal tracking
- Lifecycle versioning
- Distributed mutation traceability
"""
from __future__ import annotations

import logging
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from .models import (
    MutationSeverity,
    MutationStatus,
    AdaptationPhase,
    EvolutionTrajectory,
    OrchestrationMutation,
    CognitionEvolutionTrace,
    SemanticAdaptationEvent,
    RuntimeBehaviorEvolution,
    RecursiveAdaptationTelemetry,
    DistributedMutationCoordination,
    MutationLineageGraph,
    MutationNode,
    MutationEdge,
)

logger = logging.getLogger(__name__)


# =====================================================================
# Data Transfer Objects
# =====================================================================

@dataclass
class MutationRecord:
    """Record for a mutation event"""
    mutation_id: str
    lineage_id: str
    subject_kind: str
    subject_key: str
    mutation_type: str
    changes: Dict[str, Any]
    severity: MutationSeverity
    status: MutationStatus
    pre_hash: Optional[str] = None
    post_hash: Optional[str] = None


@dataclass
class EvolutionPath:
    """Evolution path through lineage"""
    path: List[str]  # List of mutation IDs
    total_impact: float
    trajectory: EvolutionTrajectory
    depth: int


@dataclass
class TelemetrySnapshot:
    """Telemetry snapshot for recursive adaptation"""
    metrics: Dict[str, float]
    coherence: float
    efficiency: float
    timestamp: datetime


# =====================================================================
# Mutation Lineage Tracker
# =====================================================================

class MutationLineageTracker:
    """
    Tracks orchestration mutation lineage.
    Maintains complete evolution history.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._active_mutations: Dict[str, OrchestrationMutation] = {}

    async def initialize(self) -> None:
        """Initialize the tracker"""
        await self._load_active_mutations()
        logger.info("MutationLineageTracker initialized")

    async def _load_active_mutations(self) -> None:
        """Load active mutations into cache"""
        result = await self.db.execute(
            select(OrchestrationMutation).where(
                OrchestrationMutation.mutation_status.in_([
                    MutationStatus.APPROVED.value,
                    MutationStatus.APPLYING.value,
                    MutationStatus.PENDING.value,
                ])
            )
        )
        for mutation in result.scalars().all():
            self._active_mutations[mutation.mutation_id] = mutation

    async def record_mutation(
        self,
        lineage_id: str,
        subject_kind: str,
        subject_key: str,
        mutation_type: str,
        pre_state: Dict[str, Any],
        post_state: Dict[str, Any],
        severity: MutationSeverity = MutationSeverity.MINOR,
        parent_mutation_id: Optional[str] = None,
        can_revert: bool = True,
        **kwargs,
    ) -> OrchestrationMutation:
        """Record a mutation event"""
        mutation_id = f"mut_{uuid4()}"

        # Calculate changes
        changes = self._compute_changes(pre_state, post_state)

        # Compute state hashes
        pre_hash = hashlib.sha256(str(pre_state).encode()).hexdigest()
        post_hash = hashlib.sha256(str(post_state).encode()).hexdigest()

        # Calculate depth
        lineage_depth = 0
        root_id = None
        if parent_mutation_id:
            parent = await self._get_mutation(parent_mutation_id)
            if parent:
                lineage_depth = parent.lineage_depth + 1
                root_id = parent.root_mutation_id or parent.mutation_id

        # Calculate impact and risk scores
        impact = self._calculate_impact(changes)
        risk = self._calculate_risk(pre_state, post_state, severity)

        mutation = OrchestrationMutation(
            mutation_id=mutation_id,
            lineage_id=lineage_id,
            subject_kind=subject_kind,
            subject_key=subject_key,
            subject_version=kwargs.get("subject_version", 1),
            mutation_type=mutation_type,
            mutation_category=kwargs.get("mutation_category", "runtime"),
            description=kwargs.get("description"),
            pre_mutation_snapshot=pre_state,
            pre_mutation_hash=pre_hash,
            post_mutation_snapshot=post_state,
            post_mutation_hash=post_hash,
            changes=changes,
            severity=severity.value,
            impact_score=impact,
            risk_score=risk,
            can_revert=can_revert,
            revert_snapshot=pre_state if can_revert else None,
            mutation_status=MutationStatus.PROPOSED.value,
            parent_mutation_id=parent_mutation_id,
            root_mutation_id=root_id,
            lineage_depth=lineage_depth,
            proposed_at=datetime.utcnow(),
            correlation_id=kwargs.get("correlation_id"),
        )

        self.db.add(mutation)
        await self.db.commit()
        await self.db.refresh(mutation)

        # Update parent child list
        if parent_mutation_id:
            parent = await self._get_mutation(parent_mutation_id)
            if parent:
                child_ids = parent.child_mutation_ids or []
                child_ids.append(mutation_id)
                parent.child_mutation_ids = child_ids
                await self.db.commit()

        self._active_mutations[mutation_id] = mutation
        return mutation

    def _compute_changes(self, pre: Dict[str, Any], post: Dict[str, Any]) -> Dict[str, Any]:
        """Compute the changes between pre and post state"""
        changes = {}
        all_keys = set(pre.keys()) | set(post.keys())
        for k in all_keys:
            if pre.get(k) != post.get(k):
                changes[k] = {
                    "changed": True,
                    "pre": pre.get(k),
                    "post": post.get(k),
                }
        return changes

    def _calculate_impact(self, changes: Dict[str, Any]) -> float:
        """Calculate impact score for changes"""
        if not changes:
            return 0.0
        # Weighted impact - larger changes have more impact
        impact = 0.0
        critical_keys = ["governance", "core", "primary", "essential"]
        for k, v in changes.items():
            key_lower = k.lower()
            if any(ck in key_lower for ck in critical_keys):
                impact += 0.8
            elif isinstance(v.get("post"), dict):
                impact += 0.3 * len(v["post"])
            else:
                impact += 0.1
        return min(1.0, impact)

    def _calculate_risk(
        self,
        pre: Dict[str, Any],
        post: Dict[str, Any],
        severity: MutationSeverity,
    ) -> float:
        """Calculate risk score"""
        base_risk = [
            MutationSeverity.TRIVIAL,
            MutationSeverity.MINOR,
            MutationSeverity.MODERATE,
            MutationSeverity.MAJOR,
            MutationSeverity.CRITICAL,
            MutationSeverity.CATASTROPHIC,
        ].index(severity) / (len(MutationSeverity) - 1)

        # Additional risk factors
        if len(post) > len(pre):
            base_risk += 0.1  # Added keys increase risk
        if pre.get("locked") and not post.get("locked"):
            base_risk += 0.3  # Unlocking increases risk

        return min(1.0, base_risk)

    async def _get_mutation(self, mutation_id: str) -> Optional[OrchestrationMutation]:
        """Get mutation from cache or DB"""
        return self._active_mutations.get(mutation_id) or await self.db.execute(
            select(OrchestrationMutation).where(
                OrchestrationMutation.mutation_id == mutation_id)
        ).scalar_one_or_none()

    async def update_status(
        self,
        mutation_id: str,
        status: MutationStatus,
        **kwargs,
    ) -> OrchestrationMutation:
        """Update mutation status"""
        mutation = await self._get_mutation(mutation_id)
        if not mutation:
            raise ValueError(f"Mutation not found: {mutation_id}")

        mutation.mutation_status = status.value

        # Set timestamps based on status
        if status == MutationStatus.APPROVED:
            mutation.approved_at = datetime.utcnow()
        elif status == MutationStatus.APPLIED:
            mutation.applied_at = datetime.utcnow()
        elif status == MutationStatus.COMPLETED or status == MutationStatus.VERIFIED:
            mutation.completed_at = datetime.utcnow()
        elif status == MutationStatus.REVERTED:
            mutation.reverted_at = datetime.utcnow()
            mutation.is_reverted = True

        # Update validation
        if "validation_passed" in kwargs:
            mutation.validation_passed = kwargs["validation_passed"]
            mutation.verification_timestamp = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(mutation)
        return mutation

    async def revert_mutation(
        self,
        mutation_id: str,
    ) -> OrchestrationMutation:
        """Revert a mutation to pre-mutation state"""
        mutation = await self._get_mutation(mutation_id)
        if not mutation:
            raise ValueError(f"Mutation not found: {mutation_id}")

        if not mutation.can_revert:
            raise ValueError(f"Mutation cannot be reverted: {mutation_id}")

        mutation.mutation_status = MutationStatus.REVERTING.value
        await self.db.commit()

        mutation.mutation_status = MutationStatus.REVERTED.value
        mutation.reverted_at = datetime.utcnow()
        mutation.is_reverted = True

        await self.db.commit()
        await self.db.refresh(mutation)
        return mutation

    async def get_lineage(
        self,
        lineage_id: str,
        include_reverted: bool = False,
    ) -> List[OrchestrationMutation]:
        """Get all mutations in a lineage"""
        query = select(OrchestrationMutation).where(
            OrchestrationMutation.lineage_id == lineage_id
        )

        if not include_reverted:
            query = query.where(OrchestrationMutation.is_reverted.is_(False))

        result = await self.db.execute(query.order_by(
            OrchestrationMutation.proposed_at.asc()))

        return list(result.scalars().all())

    async def get_mutation_chain(
        self,
        mutation_id: str,
    ) -> List[OrchestrationMutation]:
        """Get the parent chain for a mutation"""
        chain = []
        current_id = mutation_id

        for _ in range(100):  # Max depth limit
            mutation = await self._get_mutation(current_id)
            if not mutation:
                break
            chain.append(mutation)
            current_id = mutation.parent_mutation_id
            if not current_id:
                break

        return list(reversed(chain))


# =====================================================================
# Cognition Evolution Tracer
# =====================================================================

class CognitionEvolutionTracer:
    """
    Traces cognition evolution over time.
    Tracks cognitive process adaptations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self) -> None:
        """Initialize the tracer"""
        logger.info("CognitionEvolutionTracer initialized")

    async def record_cognition_trace(
        self,
        lineage_id: str,
        reasoning_type: str,
        domain: str,
        cognition_state: Dict[str, Any],
        reasoning_context: Dict[str, Any],
        coherence_before: float = 1.0,
        coherence_after: float = 1.0,
        phase: AdaptationPhase = AdaptationPhase.OBSERVATION,
        **kwargs,
    ) -> CognitionEvolutionTrace:
        """Record a cognition evolution trace"""
        trace_id = f"cog_trace_{uuid4()}"

        coherence_delta = coherence_after - coherence_before

        # Determine trajectory
        if coherence_delta > 0.1:
            trajectory = EvolutionTrajectory.EMERGENT
        elif coherence_delta < -0.1:
            trajectory = EvolutionTrajectory.DECLINING
        elif kwargs.get("rapid"):
            trajectory = EvolutionTrajectory.RAPID
        else:
            trajectory = EvolutionTrajectory.GRADUAL

        trace = CognitionEvolutionTrace(
            trace_id=trace_id,
            lineage_id=lineage_id,
            reasoning_type=reasoning_type,
            reasoning_phase=kwargs.get("reasoning_phase", "analysis"),
            domain=domain,
            cognition_snapshot=cognition_state,
            reasoning_context=reasoning_context,
            adaptation_phase=phase.value,
            adaptation_trigger=kwargs.get("trigger"),
            trigger_conditions=kwargs.get("trigger_conditions"),
            coherence_before=coherence_before,
            coherence_after=coherence_after,
            coherence_delta=coherence_delta,
            insight_gain=kwargs.get("insight_gain", 0.0),
            reasoning_efficiency=kwargs.get("efficiency", 0.5),
            adaptation_quality=kwargs.get("quality", 0.5),
            trajectory=trajectory.value,
            trajectory_confidence=kwargs.get("trajectory_confidence", 0.5),
            parent_trace_id=kwargs.get("parent_trace_id"),
            session_id=kwargs.get("session_id"),
            traced_at=datetime.utcnow(),
            correlation_id=kwargs.get("correlation_id"),
        )

        self.db.add(trace)
        await self.db.commit()
        await self.db.refresh(trace)
        return trace

    async def get_traces_for_session(
        self,
        session_id: str,
        reasoning_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[CognitionEvolutionTrace]:
        """Get cognition traces for a session"""
        query = select(CognitionEvolutionTrace).where(
            CognitionEvolutionTrace.session_id == session_id
        )
        if reasoning_type:
            query = query.where(
                CognitionEvolutionTrace.reasoning_type == reasoning_type)

        result = await self.db.execute(
            query.order_by(CognitionEvolutionTrace.traced_at.desc()).limit(limit))

        return list(result.scalars().all())

    async def calculate_evolution_trend(
        self,
        lineage_id: str,
        window_minutes: int = 60,
    ) -> Dict[str, Any]:
        """Calculate evolution trend for a lineage"""
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)

        result = await self.db.execute(
            select(CognitionEvolutionTrace).where(
                and_(
                    CognitionEvolutionTrace.lineage_id == lineage_id,
                    CognitionEvolutionTrace.traced_at >= cutoff,
                )
            ).order_by(CognitionEvolutionTrace.traced_at.asc())
        )
        traces = list(result.scalars().all())

        if not traces:
            return {"trend": "unknown", "stability": 1.0, "count": 0}

        coherence_values = [t.coherence_after for t in traces]
        avg_coherence = sum(coherence_values) / len(coherence_values)

        # Calculate stability (inverse of variance)
        if len(coherence_values) > 1:
            variance = sum((c - avg_coherence) ** 2 for c in coherence_values) / len(coherence_values)
            stability = max(0.0, 1.0 - variance)
        else:
            stability = 1.0

        # Determine trend
        if len(traces) >= 3:
            first_third = coherence_values[:len(coherence_values) // 3]
            last_third = coherence_values[-len(coherence_values) // 3:]
            avg_first = sum(first_third) / len(first_third)
            avg_last = sum(last_third) / len(last_third)
            delta = avg_last - avg_first

            if delta > 0.1:
                trend = "improving"
            elif delta < -0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "trend": trend,
            "stability": stability,
            "count": len(traces),
            "avg_coherence": avg_coherence,
        }


# =====================================================================
# Semantic Adaptation History
# =====================================================================

class SemanticAdaptationHistory:
    """
    Records semantic adaptation history.
    Tracks semantic changes across evolution.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self) -> None:
        """Initialize the history recorder"""
        logger.info("SemanticAdaptationHistory initialized")

    async def record_adaptation(
        self,
        lineage_id: str,
        adaptation_scope: str,
        subject_kind: str,
        subject_key: str,
        semantic_type: str,
        change_type: str,
        pre_semantic: Dict[str, Any],
        post_semantic: Dict[str, Any],
        pre_predicates: Optional[List[Dict[str, Any]]] = None,
        post_predicates: Optional[List[Dict[str, Any]]] = None,
        contract_id: Optional[str] = None,
        **kwargs,
    ) -> SemanticAdaptationEvent:
        """Record a semantic adaptation event"""
        event_id = f"sem_adapt_{uuid4()}"

        # Calculate semantic distance
        semantic_distance = self._calculate_semantic_distance(pre_semantic, post_semantic)

        # Calculate preservation score
        preservation = self._calculate_preservation(pre_semantic, post_semantic)

        # Check for invariant violations
        invariants = kwargs.get("invariants", [])
        violations = self._check_invariant_violations(post_semantic, invariants)

        event = SemanticAdaptationEvent(
            event_id=event_id,
            lineage_id=lineage_id,
            adaptation_scope=adaptation_scope,
            subject_kind=subject_kind,
            subject_key=subject_key,
            subject_version=kwargs.get("subject_version", 1),
            semantic_type=semantic_type,
            change_type=change_type,
            description=kwargs.get("description"),
            pre_semantic_state=pre_semantic,
            pre_predicates=pre_predicates,
            post_semantic_state=post_semantic,
            post_predicates=post_predicates,
            semantic_distance=semantic_distance,
            semantic_preservation=preservation,
            invariant_violations=violations if violations else None,
            contract_id=contract_id,
            occurred_at=datetime.utcnow(),
            correlation_id=kwargs.get("correlation_id"),
            mutation_id=kwargs.get("mutation_id"),
        )

        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    def _calculate_semantic_distance(
        self,
        pre: Dict[str, Any],
        post: Dict[str, Any],
    ) -> float:
        """Calculate semantic distance between states"""
        if not pre and not post:
            return 0.0
        if not pre:
            return 1.0
        if not post:
            return 1.0

        # Simple Jaccard-like distance on keys
        pre_keys = set(pre.keys())
        post_keys = set(post.keys())

        if not pre_keys and not post_keys:
            return 0.0

        intersection = len(pre_keys & post_keys)
        union = len(pre_keys | post_keys)

        return 1.0 - (intersection / union if union > 0 else 0.0)

    def _calculate_preservation(
        self,
        pre: Dict[str, Any],
        post: Dict[str, Any],
    ) -> float:
        """Calculate semantic preservation score"""
        if not pre:
            return 1.0

        common_keys = set(pre.keys()) & set(post.keys())
        if not common_keys:
            return 0.0

        preserved = sum(
            1 for k in common_keys if pre[k] == post[k]
        )

        return preserved / len(pre.keys())

    def _check_invariant_violations(
        self,
        state: Dict[str, Any],
        invariants: List[str],
    ) -> List[str]:
        """Check for invariant violations"""
        violations = []
        for invariant in invariants:
            if invariant == "required_keys":
                required = state.get("_required_keys", [])
                for key in required:
                    if key not in state:
                        violations.append(f"missing required key: {key}")
            elif invariant == "min_version":
                min_ver = state.get("_min_version", 1)
                if state.get("version", 1) < min_ver:
                    violations.append(f"version below minimum: {state.get('version')} < {min_ver}")
        return violations


# =====================================================================
# Runtime Behavior Evolution Tracker
# =====================================================================

class RuntimeBehaviorEvolutionTracker:
    """
    Tracks runtime behavior evolution.
    Monitors behavioral changes in runtime environments.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self) -> None:
        """Initialize the tracker"""
        logger.info("RuntimeBehaviorEvolutionTracker initialized")

    async def record_evolution(
        self,
        runtime_instance_id: str,
        lineage_id: str,
        behavior_kind: str,
        behavior_scope: str,
        pre_behavior: Dict[str, Any],
        post_behavior: Dict[str, Any],
        pre_metrics: Optional[Dict[str, float]] = None,
        post_metrics: Optional[Dict[str, float]] = None,
        **kwargs,
    ) -> RuntimeBehaviorEvolution:
        """Record runtime behavior evolution"""
        evolution_id = f"rt_evo_{uuid4()}"

        # Calculate metrics
        behavioral_drift = self._calculate_drift(pre_behavior, post_behavior)
        performance_impact = self._calculate_performance_impact(
            pre_metrics or {}, post_metrics or {})
        stability_change = self._calculate_stability_change(
            pre_metrics or {}, post_metrics or {})

        # Detect anomalies
        anomalies = self._detect_anomalies(
            pre_behavior, post_behavior, pre_metrics or {}, post_metrics or {})
        anomaly_score = len(anomalies) * 0.2

        evolution = RuntimeBehaviorEvolution(
            evolution_id=evolution_id,
            runtime_instance_id=runtime_instance_id,
            lineage_id=lineage_id,
            behavior_kind=behavior_kind,
            behavior_category=kwargs.get("behavior_category", "runtime"),
            behavior_scope=behavior_scope,
            pre_evolution_behavior=pre_behavior,
            pre_metrics=pre_metrics or {},
            post_evolution_behavior=post_behavior,
            post_metrics=post_metrics or {},
            behavioral_drift=behavioral_drift,
            performance_impact=performance_impact,
            stability_change=stability_change,
            anomalies_detected=anomalies if anomalies else None,
            anomaly_score=min(1.0, anomaly_score),
            trigger_type=kwargs.get("trigger_type"),
            trigger_evidence=kwargs.get("trigger_evidence"),
            observed_at=datetime.utcnow(),
            correlation_id=kwargs.get("correlation_id"),
        )

        self.db.add(evolution)
        await self.db.commit()
        await self.db.refresh(evolution)
        return evolution

    def _calculate_drift(
        self,
        pre: Dict[str, Any],
        post: Dict[str, Any],
    ) -> float:
        """Calculate behavioral drift"""
        pre_keys = set(pre.keys())
        post_keys = set(post.keys())

        # Key change drift
        key_drift = len(pre_keys ^ post_keys) / max(len(pre_keys | post_keys), 1)

        # Value change drift
        common_keys = pre_keys & post_keys
        if common_keys:
            value_drift = sum(
                1 for k in common_keys if pre[k] != post[k]
            ) / len(common_keys)
        else:
            value_drift = 1.0

        return (key_drift + value_drift) / 2

    def _calculate_performance_impact(
        self,
        pre: Dict[str, float],
        post: Dict[str, float],
    ) -> float:
        """Calculate performance impact"""
        if not pre:
            return 0.0

        perf_keys = ["latency", "cpu", "memory", "throughput"]
        impacts = []

        for key in perf_keys:
            if key in pre and key in post:
                if key == "latency":  # Lower is better
                    if pre[key] > 0:
                        impacts.append((pre[key] - post[key]) / pre[key])
                elif key == "cpu":  # Lower is better
                    if pre[key] > 0:
                        impacts.append((pre[key] - post[key]) / pre[key])
                else:  # Higher is better
                    if pre[key] > 0:
                        impacts.append((post[key] - pre[key]) / pre[key])

        return sum(impacts) / len(impacts) if impacts else 0.0

    def _calculate_stability_change(
        self,
        pre: Dict[str, float],
        post: Dict[str, float],
    ) -> float:
        """Calculate stability change"""
        # Compare variance indicators if available
        pre_stability = pre.get("stability", 1.0)
        post_stability = post.get("stability", 1.0)
        return post_stability - pre_stability

    def _detect_anomalies(
        self,
        pre_behavior: Dict[str, Any],
        post_behavior: Dict[str, Any],
        pre_metrics: Dict[str, float],
        post_metrics: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in behavioral evolution"""
        anomalies = []

        # Check for sudden large changes
        for key in set(pre_behavior.keys()) & set(post_behavior.keys()):
            if isinstance(pre_behavior[key], (int, float)) and isinstance(post_behavior[key], (int, float)):
                if pre_behavior[key] != 0:
                    change_pct = abs(post_behavior[key] - pre_behavior[key]) / abs(pre_behavior[key])
                    if change_pct > 0.5:
                        anomalies({
                            "type": "large_change",
                            "key": key,
                            "change_pct": change_pct,
                        })

        # Check for metric thresholds
        metric_thresholds = {
            "cpu": 0.9,
            "memory": 0.9,
            "error_rate": 0.1,
        }
        for metric, threshold in metric_thresholds.items():
            if metric in post_metrics and post_metrics[metric] > threshold:
                anomalies.append({
                    "type": "threshold_exceeded",
                    "metric": metric,
                    "value": post_metrics[metric],
                    "threshold": threshold,
                })

        return anomalies


# =====================================================================
# Recursive Adaptation Telemetry Service
# =====================================================================

class RecursiveAdaptationTelemetryService:
    """
    Manages recursive adaptation telemetry.
    Tracks nested adaptation cycles.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self) -> None:
        """Initialize the telemetry service"""
        logger.info("RecursiveAdaptationTelemetryService initialized")

    async def capture_telemetry(
        self,
        session_id: str,
        recursion_depth: int,
        adaptation_level: str,
        metrics: Dict[str, float],
        coherence: float = 1.0,
        efficiency: float = 0.5,
        parent_telemetry_id: Optional[str] = None,
        **kwargs,
    ) -> RecursiveAdaptationTelemetry:
        """Capture telemetry snapshot for recursive adaptation"""
        telemetry_id = f"telem_{uuid4()}"

        # Aggregate child metrics if any
        aggregate = self._aggregate_metrics(metrics)

        telemetry = RecursiveAdaptationTelemetry(
            telemetry_id=telemetry_id,
            session_id=session_id,
            recursion_depth=recursion_depth,
            max_recursion_depth=kwargs.get("max_depth", 10),
            parent_telemetry_id=parent_telemetry_id,
            root_telemetry_id=kwargs.get("root_telemetry_id"),
            adaptation_level=adaptation_level,
            adaptation_state=kwargs.get("adaptation_state", "active"),
            adaptation_progress=kwargs.get("progress", 0.0),
            metrics_snapshot=metrics,
            coherence_snapshot=coherence,
            efficiency_snapshot=efficiency,
            child_metrics=kwargs.get("child_metrics"),
            aggregate_metrics=aggregate,
            captured_at=datetime.utcnow(),
            correlation_id=kwargs.get("correlation_id"),
        )

        self.db.add(telemetry)
        await self.db.commit()
        await self.db.refresh(telemetry)

        # Update parent's child list if applicable
        if parent_telemetry_id:
            parent = await self.db.execute(
                select(RecursiveAdaptationTelemetry).where(
                    RecursiveAdaptationTelemetry.telemetry_id == parent_telemetry_id)
            ).scalar_one_or_none()
            if parent:
                child_ids = parent.child_telemetry_ids or []
                child_ids.append(telemetry_id)
                parent.child_telemetry_ids = child_ids
                await self.db.commit()

        return telemetry

    def _aggregate_metrics(
        self,
        metrics: Dict[str, float],
    ) -> Dict[str, float]:
        """Aggregate metrics across levels"""
        if not metrics:
            return {}

        return {
            "count": float(len(metrics)),
            "sum": sum(metrics.values()),
            "avg": sum(metrics.values()) / len(metrics),
            "max": max(metrics.values()),
            "min": min(metrics.values()),
        }

    async def get_telemetry_chain(
        self,
        telemetry_id: str,
    ) -> List[RecursiveAdaptationTelemetry]:
        """Get the telemetry chain from root to this node"""
        chain = []
        current_id = telemetry_id

        for _ in range(100):
            result = await self.db.execute(
                select(RecursiveAdaptationTelemetry).where(
                    RecursiveAdaptationTelemetry.telemetry_id == current_id)
            )
            telemetry = result.scalar_one_or_none()
            if not telemetry:
                break
            chain.append(telemetry)
            current_id = telemetry.parent_telemetry_id
            if not current_id:
                break

        return list(reversed(chain))


# =====================================================================
# Distributed Mutation Coordinator
# =====================================================================

class DistributedMutationCoordinator:
    """
    Coordinates mutations across distributed systems.
    Ensures consistent mutation application.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self) -> None:
        """Initialize the coordinator"""
        logger.info("DistributedMutationCoordinator initialized")

    async def coordinate_mutation(
        self,
        batch_id: str,
        lineage_id: str,
        node_id: str,
        node_kind: str,
        node_role: str,
        mutations: List[str],
        node_state_before: Dict[str, Any],
        coordination_type: str = "synchronous",
        **kwargs,
    ) -> DistributedMutationCoordination:
        """Coordinate mutation application on a node"""
        coordination_id = f"coord_{uuid4()}"

        coordination = DistributedMutationCoordination(
            coordination_id=coordination_id,
            batch_id=batch_id,
            lineage_id=lineage_id,
            node_id=node_id,
            node_kind=node_kind,
            node_role=node_role,
            coordination_type=coordination_type,
            coordination_strategy=kwargs.get("strategy", "paxos"),
            consensus_algorithm=kwargs.get("consensus_algorithm"),
            mutations_assigned=mutations,
            mutations_applied=kwargs.get("applied_mutations", []),
            mutations_pending=kwargs.get("pending_mutations", mutations),
            node_state_before=node_state_before,
            node_state_after=kwargs.get("node_state_after", {}),
            coordination_success=kwargs.get("success", True),
            consensus_reached=kwargs.get("consensus_reached", True),
            final_state_hash=kwargs.get("final_hash"),
            initiated_at=datetime.utcnow(),
            coordinated_at=datetime.utcnow(),
            correlation_id=kwargs.get("correlation_id"),
        )

        self.db.add(coordination)
        await self.db.commit()
        await self.db.refresh(coordination)
        return coordination

    async def get_batch_coordinations(
        self,
        batch_id: str,
    ) -> List[DistributedMutationCoordination]:
        """Get all coordinations for a batch"""
        result = await self.db.execute(
            select(DistributedMutationCoordination).where(
                DistributedMutationCoordination.batch_id == batch_id
            ).order_by(DistributedMutationCoordination.coordinated_at)
        )
        return list(result.scalars().all())


# =====================================================================
# Mutation Lineage Graph Builder
# =====================================================================

class MutationLineageGraphBuilder:
    """
    Builds mutation lineage graphs.
    Constructs visualizable evolution trees.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self) -> None:
        """Initialize the graph builder"""
        logger.info("MutationLineageGraphBuilder initialized")

    async def build_graph(
        self,
        lineage_id: str,
        subject_kind: str,
        subject_key: str,
    ) -> MutationLineageGraph:
        """Build a complete lineage graph"""
        graph_id = f"graph_{uuid4()}"

        # Get all mutations in lineage
        result = await self.db.execute(
            select(OrchestrationMutation).where(
                and_(
                    OrchestrationMutation.lineage_id == lineage_id,
                    OrchestrationMutation.is_reverted.is_(False),
                )
            ).order_by(OrchestrationMutation.proposed_at)
        )
        mutations = list(result.scalars().all())

        if not mutations:
            raise ValueError(f"No mutations found for lineage: {lineage_id}")

        # Calculate graph metrics
        node_count = len(mutations)
        edge_count = sum(1 for m in mutations if m.parent_mutation_id)

        # Calculate max depth
        max_depth = max(m.lineage_depth for m in mutations)

        # Calculate graph diameter (simplified)
        graph_diameter = max_depth * 2

        # Calculate average branching factor
        branching_factor = edge_count / node_count if node_count > 0 else 0.0

        # Calculate coherence score
        coherence_score = sum(
            1 - m.risk_score for m in mutations
        ) / node_count if node_count > 0 else 1.0

        graph = MutationLineageGraph(
            graph_id=graph_id,
            lineage_id=lineage_id,
            subject_kind=subject_kind,
            subject_key=subject_key,
            root_mutation_id=mutations[0].mutation_id,
            node_count=node_count,
            edge_count=edge_count,
            max_depth=max_depth,
            graph_diameter=graph_diameter,
            branching_factor=branching_factor,
            coherence_score=coherence_score,
            created_at=datetime.utcnow(),
            last_updated_at=datetime.utcnow(),
        )

        self.db.add(graph)
        await self.db.commit()
        await self.db.refresh(graph)

        # Build nodes
        for i, mutation in enumerate(mutations):
            node = MutationNode(
                node_id=f"node_{mutation.mutation_id}",
                graph_id=graph_id,
                mutation_id=mutation.mutation_id,
                depth=mutation.lineage_depth,
                position_index=i,
                node_type="mutation",
                label=f"{mutation.mutation_type}@{mutation.proposed_at.strftime('%H:%M:%S')}",
                data={
                    "mutation_type": mutation.mutation_type,
                    "severity": mutation.severity,
                    "status": mutation.mutation_status,
                    "impact": mutation.impact_score,
                },
                impact_score=mutation.impact_score,
            )
            self.db.add(node)

            # Build edges for parent relationships
            if mutation.parent_mutation_id:
                edge = MutationEdge(
                    edge_id=f"edge_{mutation.mutation_id}",
                    graph_id=graph_id,
                    source_node_id=f"node_{mutation.parent_mutation_id}",
                    target_node_id=f"node_{mutation.mutation_id}",
                    edge_type="parent_child",
                    relationship="derived_from",
                )
                self.db.add(edge)

        await self.db.commit()
        await self.db.refresh(graph)
        return graph

    async def get_graph_nodes(
        self,
        graph_id: str,
    ) -> List[MutationNode]:
        """Get all nodes in a graph"""
        result = await self.db.execute(
            select(MutationNode).where(
                MutationMuteNode.graph_id == graph_id
            ).order_by(MutationNode.depth, MutationNode.position_index)
        )
        return list(result.scalars().all())


__all__ = [
    "MutationLineageTracker",
    "CognitionEvolutionTracer",
    "SemanticAdaptationHistory",
    "RuntimeBehaviorEvolutionTracker",
    "RecursiveAdaptationTelemetryService",
    "DistributedMutationCoordinator",
    "MutationLineageGraphBuilder",
    "MutationRecord",
    "EvolutionPath",
    "TelemetrySnapshot",
]
