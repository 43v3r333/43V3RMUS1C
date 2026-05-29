"""
Constitutional Arbitration Services - Production-grade constitutional arbitration infrastructure

Provides:
- Constitutional arbitration engine
- Reconciliation policy management
- Constitutional lineage tracking
- Ecosystem coherence validation
- Balance metric collection

All services support:
- Async operation
- Typed arbitration governance
- Reconciliation lineage tracking
- Distributed arbitration
- Recursive governance balancing
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from .models import (
    ArbitrationStrategy,
    ReconciliationState,
    ArbitrationSession,
    ReconciliationPolicy,
    ConstitutionalLineage,
    EcosystemSnapshot,
    BalanceMetric,
    ArbitrationResult,
)

logger = logging.getLogger(__name__)


@dataclass
class ArbitrationDecision:
    """Result of an arbitration decision"""
    decision_type: str
    selected_policy: Optional[str]
    rejected_policies: List[str] = field(default_factory=list)
    coherence_impact: float = 0.0
    success: bool = True


@dataclass
class EcosystemAssessment:
    """Assessment of ecosystem coherence"""
    is_coherent: bool
    coherence_score: float
    stability_score: float
    balance_score: float
    violations: List[str] = field(default_factory=list)


# =====================================================================
# Constitutional Arbitration Engine
# =====================================================================

class ConstitutionalArbitrationEngine:
    """
    Core constitutional arbitration engine.
    Resolves conflicts between constitutional policies.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._sessions: Dict[str, ArbitrationSession] = {}

    async def initialize(self) -> None:
        """Initialize the engine"""
        logger.info("ConstitutionalArbitrationEngine initialized")

    async def create_session(
        self,
        session_scope: str,
        scope_kind: str,
        strategy: ArbitrationStrategy = ArbitrationStrategy.RECURSIVE,
        max_depth: int = 10,
        parent_session_id: Optional[str] = None,
    ) -> ArbitrationSession:
        """Create an arbitration session"""
        # Calculate depth
        recursion_depth = 0
        if parent_session_id:
            parent = await self._get_session(parent_session_id)
            if parent:
                recursion_depth = parent.recursion_depth + 1

        if recursion_depth >= max_depth:
            raise ValueError(f"max recursion depth {max_depth} exceeded")

        session = ArbitrationSession(
            session_id=f"arb_session_{uuid4()}",
            session_scope=session_scope,
            scope_kind=scope_kind,
            recursion_depth=recursion_depth,
            max_recursion_depth=max_depth,
            parent_session_id=parent_session_id,
            strategy=strategy.value,
            started_at=datetime.utcnow(),
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        self._sessions[session.session_id] = session
        return session

    async def _get_session(self, session_id: str) -> Optional[ArbitrationSession]:
        """Get session by ID"""
        return self._sessions.get(session_id) or await self.db.execute(
            select(ArbitrationSession).where(
                ArbitrationSession.session_id == session_id
            )
        ).scalar_one_or_none()

    async def arbitrate(
        self,
        session_id: str,
        conflicting_policies: List[str],
        policy_scores: Dict[str, float],
    ) -> ArbitrationDecision:
        """Arbitrate between conflicting policies"""
        session = await self._get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        session.session_state = ReconciliationState.IN_PROGRESS.value
        session.conflicting_policies = conflicting_policies
        await self.db.commit()

        # Apply strategy
        strategy = ArbitrationStrategy(session.strategy)

        if strategy == ArbitrationStrategy.PRIORITY:
            selected = self._apply_priority_strategy(conflicting_policies, policy_scores)
        elif strategy == ArbitrationStrategy.WEIGHTED:
            selected = self._apply_weighted_strategy(conflicting_policies, policy_scores)
        elif strategy == ArbitrationStrategy.ROLLBACK:
            selected = None  # Rollback scenario
        elif strategy == ArbitrationStrategy.MERGE:
            selected = self._apply_merge_strategy(conflicting_policies)
        else:
            selected = conflicting_policies[0] if conflicting_policies else None

        rejected = [p for p in conflicting_policies if p != selected]

        # Calculate coherence impact
        impact = len(rejected) * 0.05

        session.session_state = ReconciliationState.RECINCILED.value
        session.coherence_impact = impact
        session.success = selected is not None
        await self.db.commit()

        return ArbitrationDecision(
            decision_type=strategy.value,
            selected_policy=selected,
            rejected_policies=rejected,
            coherence_impact=impact,
            success=selected is not None,
        )

    def _apply_priority_strategy(
        self,
        policies: List[str],
        scores: Dict[str, float],
    ) -> Optional[str]:
        """Apply priority-based selection"""
        if not policies:
            return None
        return max(policies, key=lambda p: scores.get(p, 0))

    def _apply_weighted_strategy(
        self,
        policies: List[str],
        scores: Dict[str, float],
    ) -> Optional[str]:
        """Apply weighted selection"""
        if not policies:
            return None
        total = sum(scores.get(p, 0) for p in policies)
        if total == 0:
            return policies[0]
        weights = [scores.get(p, 0) / total for p in policies]
        return policies[weights.index(max(weights))]

    def _apply_merge_strategy(
        self,
        policies: List[str],
    ) -> Optional[str]:
        """Apply merge strategy"""
        # Return first policy as representative
        return policies[0] if policies else None

    async def complete_session(
        self,
        session_id: str,
    ) -> ArbitrationSession:
        """Complete an arbitration session"""
        session = await self._get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        session.session_state = ReconciliationState.RECINCILED.value
        session.completed_at = datetime.utcnow()
        session.duration_ms = (
            session.completed_at - session.started_at
        ).total_seconds() * 1000

        await self.db.commit()
        await self.db.refresh(session)

        if session_id in self._sessions:
            del self._sessions[session_id]

        return session


# =====================================================================
# Reconciliation Policy Manager
# =====================================================================

class ReconciliationPolicyManager:
    """
    Manages reconciliation policies.
    Defines how conflicts are reconciled.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._policies: Dict[str, ReconciliationPolicy] = {}

    async def initialize(self) -> None:
        """Initialize the manager"""
        result = await self.db.execute(
            select(ReconciliationPolicy).where(
                ReconciliationPolicy.is_active.is_(True)
            )
        )
        for policy in result.scalars().all():
            self._policies[policy.policy_id] = policy
        logger.info("ReconciliationPolicyManager initialized with %d policies", len(self._policies))

    async def create_policy(
        self,
        policy_scope: str,
        policy_type: str,
        policy_key: str,
        default_strategy: ArbitrationStrategy = ArbitrationStrategy.PRIORITY,
        **kwargs,
    ) -> ReconciliationPolicy:
        """Create a new policy"""
        policy = ReconciliationPolicy(
            policy_id=f"recon_policy_{uuid4()}",
            policy_scope=policy_scope,
            policy_type=policy_type,
            policy_key=policy_key,
            default_strategy=default_strategy.value,
            **kwargs,
        )
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        self._policies[policy.policy_id] = policy
        return policy

    async def get_policy(
        self,
        policy_id: str,
    ) -> Optional[ReconciliationPolicy]:
        """Get a policy by ID"""
        return self._policies.get(policy_id) or await self.db.execute(
            select(ReconciliationPolicy).where(
                ReconciliationPolicy.policy_id == policy_id
            )
        ).scalar_one_or_none()


# =====================================================================
# Constitutional Lineage Tracker
# =====================================================================

class ConstitutionalLineageTracker:
    """
    Tracks constitutional lineage.
    Records evolution of constitutional decisions.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self) -> None:
        """Initialize the tracker"""
        logger.info("ConstitutionalLineageTracker initialized")

    async def record_decision(
        self,
        lineage_scope: str,
        decision_id: str,
        decision_type: str,
        pre_decision: Dict[str, Any],
        post_decision: Dict[str, Any],
        parent_decision_id: Optional[str] = None,
    ) -> ConstitutionalLineage:
        """Record a constitutional decision"""
        lineage_id = f"con_lineage_{uuid4()}"

        # Calculate impact
        impact = self._calculate_impact(pre_decision, post_decision)

        # Get root
        root_id = None
        if parent_decision_id:
            parent = await self._get_decision(parent_decision_id)
            if parent:
                root_id = parent.root_decision_id

        lineage = ConstitutionalLineage(
            lineage_id=lineage_id,
            lineage_scope=lineage_scope,
            decision_id=decision_id,
            decision_type=decision_type,
            parent_decision_id=parent_decision_id,
            root_decision_id=root_id,
            change_type="constitutional_decision",
            pre_decision=pre_decision,
            post_decision=post_decision,
            impact_score=impact,
            created_at=datetime.utcnow(),
        )

        self.db.add(lineage)
        await self.db.commit()
        await self.db.refresh(lineage)
        return lineage

    def _calculate_impact(
        self,
        pre: Dict[str, Any],
        post: Dict[str, Any],
    ) -> float:
        """Calculate impact of decision"""
        if not pre:
            return 1.0
        changes = sum(
            1 for k in set(pre.keys()) | set(post.keys())
            if pre.get(k) != post.get(k)
        )
        return min(1.0, changes / 50)

    async def _get_decision(
        self,
        decision_id: str,
    ) -> Optional[ConstitutionalLineage]:
        """Get a decision by ID"""
        return await self.db.execute(
            select(ConstitutionalLineage).where(
                ConstitutionalLineage.decision_id == decision_id
            )
        ).scalar_one_or_none()


# =====================================================================
# Ecosystem Coherence Validator
# =====================================================================

class EcosystemCoherenceValidator:
    """
    Validates ecosystem coherence.
    Ensures ecosystem-wide consistency.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self) -> None:
        """Initialize the validator"""
        logger.info("EcosystemCoherenceValidator initialized")

    async def assess_coherence(
        self,
        component_states: Dict[str, str],
        policy_states: Dict[str, bool],
    ) -> EcosystemAssessment:
        """Assess ecosystem coherence"""
        violations: List[str] = []

        # Check for incoherent components
        for comp_id, state in component_states.items():
            if state == "failed":
                violations.append(f"component_failed: {comp_id}")
            elif state == "degraded":
                violations.append(f"component_degraded: {comp_id}")

        # Check for policy violations
        for policy_id, is_valid in policy_states.items():
            if not is_valid:
                violations.append(f"policy_violated: {policy_id}")

        # Calculate scores
        total_comps = len(component_states) if component_states else 1
        coherent_comps = sum(
            1 for s in component_states.values() if s in ["healthy", "nominal"]
        )
        coherence_score = coherent_comps / total_comps

        valid_policies = sum(1 for v in policy_states.values() if v)
        total_policies = len(policy_states) if policy_states else 1
        balance_score = valid_policies / total_policies

        stability_score = (coherence_score + balance_score) / 2

        return EcosystemAssessment(
            is_coherent=len(violations) == 0,
            coherence_score=coherence_score,
            stability_score=stability_score,
            balance_score=balance_score,
            violations=violations,
        )

    async def capture_snapshot(
        self,
        lineage_id: str,
        snapshot_key: str,
        coherence_score: float,
        stability_score: float,
        balance_score: float,
        component_states: Dict[str, str],
        policy_states: Dict[str, bool],
        session_id: Optional[str] = None,
    ) -> EcosystemSnapshot:
        """Capture an ecosystem snapshot"""
        snapshot = EcosystemSnapshot(
            snapshot_id=f"eco_snap_{uuid4()}",
            session_id=session_id,
            lineage_id=lineage_id,
            snapshot_key=snapshot_key,
            coherence_score=coherence_score,
            stability_score=stability_score,
            balance_score=balance_score,
            component_states=component_states,
            policy_states=policy_states,
            violations_detected=sum(1 for v in policy_states.values() if not v),
            captured_at=datetime.utcnow(),
        )

        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)
        return snapshot


# =====================================================================
# Balance Metric Collector
# =====================================================================

class BalanceMetricCollector:
    """
    Collects balance metrics.
    Monitors balance over time.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self) -> None:
        """Initialize the collector"""
        logger.info("BalanceMetricCollector initialized")

    async def record_metric(
        self,
        metric_scope: str,
        metric_type: str,
        metric_name: str,
        value: float,
        is_balanced: bool = True,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> BalanceMetric:
        """Record a balance metric"""
        metric = BalanceMetric(
            metric_id=f"balance_metric_{uuid4()}",
            session_id=session_id,
            metric_scope=metric_scope,
            metric_type=metric_type,
            metric_name=metric_name,
            value=value,
            unit=kwargs.get("unit"),
            target_id=kwargs.get("target_id"),
            is_balanced=is_balanced,
            captured_at=datetime.utcnow(),
        )

        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        return metric

    async def get_metrics(
        self,
        metric_name: str,
        window_minutes: int = 60,
    ) -> List[BalanceMetric]:
        """Get metrics over time"""
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)

        result = await self.db.execute(
            select(BalanceMetric).where(
                and_(
                    BalanceMetric.metric_name == metric_name,
                    BalanceMetric.captured_at >= cutoff,
                )
            ).order_by(BalanceMetric.captured_at.desc())
        )
        return list(result.scalars().all())


__all__ = [
    "ConstitutionalArbitrationEngine",
    "ReconciliationPolicyManager",
    "ConstitutionalLineageTracker",
    "EcosystemCoherenceValidator",
    "BalanceMetricCollector",
    "ArbitrationDecision",
    "EcosystemAssessment",
]
