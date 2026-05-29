"""
Recursive Safety Services - Production-grade recursive safety infrastructure

Provides:
- Recursive safety engine
- Safety boundary management
- Collapse prevention system
- Governance conflict resolution
- Stability coordination
- Safety telemetry

All services support:
- Async operation
- Typed safety governance
- Protection lineage tracking
- Distributed safety enforcement
- Recursive collapse prevention
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
    SafetyState,
    ProtectionLevel,
    ConflictResolution,
    SafetyProfile,
    SafetyBoundary,
    CollapsePrevention,
    GovernanceConflict,
    StabilitySession,
    SafetyMetric,
)

logger = logging.getLogger(__name__)


@dataclass
class SafetyAssessment:
    """Assessment of system safety"""
    safety_state: SafetyState
    risk_score: float
    collapse_probability: float
    contributing_factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    interventions_needed: bool = False


@dataclass
class BoundaryValidation:
    """Boundary validation result"""
    within_bounds: bool
    boundary_id: str
    current_value: float
    limit_type: str
    distance_from_limit: float


# =====================================================================
# Recursive Safety Engine
# =====================================================================

class RecursiveSafetyEngine:
    """
    Core recursive safety engine.
    Manages safety for recursive operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._profiles: Dict[str, SafetyProfile] = {}
        self._running = False

    async def initialize(self) -> None:
        """Initialize the engine"""
        await self._load_profiles()
        self._running = True
        logger.info("RecursiveSafetyEngine initialized")

    async def shutdown(self) -> None:
        """Shutdown the engine"""
        self._running = False
        logger.info("RecursiveSafetyEngine shutdown")

    async def _load_profiles(self) -> None:
        """Load active profiles"""
        result = await self.db.execute(
            select(SafetyProfile).where(SafetyProfile.is_active.is_(True))
        )
        for profile in result.scalars().all():
            self._profiles[profile.profile_id] = profile

    async def assess_safety(
        self,
        scope: str,
        recursion_depth: int,
        current_metrics: Dict[str, float],
    ) -> SafetyAssessment:
        """Assess current safety state"""
        # Find applicable profile
        result = await self.db.execute(
            select(SafetyProfile).where(
                and_(
                    SafetyProfile.profile_scope == scope,
                    SafetyProfile.is_active.is_(True),
                )
            )
        )
        profile = result.scalar_one_or_none()

        if not profile:
            return SafetyAssessment(
                safety_state=SafetyState.NOMINAL,
                risk_score=0.0,
                collapse_probability=0.0,
            )

        # Calculate risk score
        depth_ratio = recursion_depth / profile.max_recursion_depth if profile.max_recursion_depth > 0 else 0
        complexity = current_metrics.get("complexity", 0.5)
        instability = current_metrics.get("instability", 0.0)

        collapse_prob = (
            depth_ratio * 0.4 +
            complexity * 0.3 +
            instability * 0.3
        )
        collapse_prob = min(1.0, collapse_prob)

        # Determine safety state
        if collapse_prob >= profile.collapse_threshold:
            safety_state = SafetyState.COLLAPSE
        elif collapse_prob >= profile.critical_threshold:
            safety_state = SafetyState.CRITICAL
        elif collapse_prob >= profile.warning_threshold:
            safety_state = SafetyState.WARNING
        else:
            safety_state = SafetyState.NOMINAL

        # Generate recommendations
        recommendations = self._generate_recommendations(
            safety_state, recursion_depth, profile, current_metrics
        )

        return SafetyAssessment(
            safety_state=safety_state,
            risk_score=collapse_prob,
            collapse_probability=collapse_prob,
            contributing_factors=self._identify_factors(depth_ratio, complexity, instability),
            recommendations=recommendations,
            interventions_needed=safety_state in [SafetyState.CRITICAL, SafetyState.COLLAPSE],
        )

    def _identify_factors(
        self,
        depth_ratio: float,
        complexity: float,
        instability: float,
    ) -> List[str]:
        """Identify contributing factors"""
        factors = []
        if depth_ratio > 0.7:
            factors.append("high_recursion_depth")
        if complexity > 0.8:
            factors.append("high_complexity")
        if instability > 0.5:
            factors.append("high_instability")
        return factors

    def _generate_recommendations(
        self,
        state: SafetyState,
        depth: int,
        profile: SafetyProfile,
        metrics: Dict[str, float],
    ) -> List[str]:
        """Generate recommendations"""
        recommendations = []
        
        if state == SafetyState.COLLAPSE:
            recommendations.append("immediate_rollback")
            recommendations.append("reduce_recursion_depth")
        elif state == SafetyState.CRITICAL:
            recommendations.append("consider_early_termination")
            recommendations.append("stabilize_metrics")
        elif state == SafetyState.WARNING:
            recommendations.append("monitor_closely")
            recommendations.append("prepare_contingency")
        
        if depth >= profile.max_recursion_depth * 0.8:
            recommendations.append("approaching_depth_limit")
        
        return recommendations

    async def create_profile(
        self,
        profile_scope: str,
        profile_key: str,
        protection_level: ProtectionLevel = ProtectionLevel.STANDARD,
        **kwargs,
    ) -> SafetyProfile:
        """Create a new safety profile"""
        profile = SafetyProfile(
            profile_id=f"safety_profile_{uuid4()}",
            profile_scope=profile_scope,
            profile_key=profile_key,
            protection_level=protection_level.value,
            **kwargs,
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        self._profiles[profile.profile_id] = profile
        return profile


# =====================================================================
# Safety Boundary Manager
# =====================================================================

class SafetyBoundaryManager:
    """
    Manages safety boundaries.
    Validates against operational limits.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._boundaries: Dict[str, SafetyBoundary] = {}

    async def initialize(self) -> None:
        """Initialize the manager"""
        result = await self.db.execute(
            select(SafetyBoundary).where(SafetyBoundary.is_active.is_(True))
        )
        for boundary in result.scalars().all():
            self._boundaries[boundary.boundary_id] = boundary
        logger.info("SafetyBoundaryManager initialized with %d boundaries", len(self._boundaries))

    async def create_boundary(
        self,
        boundary_scope: str,
        boundary_type: str,
        boundary_key: str,
        **kwargs,
    ) -> SafetyBoundary:
        """Create a new boundary"""
        boundary = SafetyBoundary(
            boundary_id=f"safety_boundary_{uuid4()}",
            boundary_scope=boundary_scope,
            boundary_type=boundary_type,
            boundary_key=boundary_key,
            **kwargs,
        )
        self.db.add(boundary)
        await self.db.commit()
        await self.db.refresh(boundary)
        self._boundaries[boundary.boundary_id] = boundary
        return boundary

    async def validate_boundary(
        self,
        boundary_id: str,
        value: float,
    ) -> BoundaryValidation:
        """Validate against a boundary"""
        boundary = self._boundaries.get(boundary_id) or await self.db.execute(
            select(SafetyBoundary).where(SafetyBoundary.boundary_id == boundary_id)
        ).scalar_one_or_none()

        if not boundary:
            return BoundaryValidation(
                within_bounds=True,
                boundary_id=boundary_id,
                current_value=value,
                limit_type="none",
                distance_from_limit=0.0,
            )

        boundary.validation_count += 1
        await self.db.commit()

        violations = []
        limit_type = "within_bounds"
        distance = 0.0

        if boundary.hard_limit is not None and value >= boundary.hard_limit:
            limit_type = "hard"
            violations.append(f"hard limit breached: {value} >= {boundary.hard_limit}")
            boundary.breach_count += 1
            distance = value - boundary.hard_limit
        elif boundary.soft_limit is not None and value >= boundary.soft_limit:
            limit_type = "soft"

        return BoundaryValidation(
            within_bounds=limit_type == "within_bounds",
            boundary_id=boundary_id,
            current_value=value,
            limit_type=limit_type,
            distance_from_limit=distance,
        )


# =====================================================================
# Collapse Prevention System
# =====================================================================

class CollapsePreventionSystem:
    """
    System for preventing collapse.
    Manages collapse prevention measures.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self) -> None:
        """Initialize the system"""
        logger.info("CollapsePreventionSystem initialized")

    async def prevent_collapse(
        self,
        session_id: str,
        lineage_id: str,
        prevention_type: str,
        severity: str,
        pre_state: Dict[str, Any],
        actions: List[str],
    ) -> CollapsePrevention:
        """Execute collapse prevention"""
        prevention = CollapsePrevention(
            prevention_id=f"collapse_prev_{uuid4()}",
            session_id=session_id,
            lineage_id=lineage_id,
            prevention_type=prevention_type,
            severity=severity,
            pre_prevention_state=pre_state,
            post_prevention_state={},  # Will be updated
            actions_taken=actions,
            rollback_triggered="rollback" in actions,
            occurred_at=datetime.utcnow(),
        )

        self.db.add(prevention)
        await self.db.commit()
        await self.db.refresh(prevention)
        return prevention

    async def complete_prevention(
        self,
        prevention_id: str,
        post_state: Dict[str, Any],
        effectiveness: float = 1.0,
    ) -> CollapsePrevention:
        """Complete a prevention"""
        result = await self.db.execute(
            select(CollapsePrevention).where(
                CollapsePrevention.prevention_id == prevention_id)
        )
        prevention = result.scalar_one_or_none()

        if not prevention:
            raise ValueError(f"Prevention not found: {prevention_id}")

        prevention.post_prevention_state = post_state
        prevention.effectiveness = effectiveness
        prevention.completed_at = datetime.utcnow()
        prevention.recovery_time_ms = (
            prevention.completed_at - prevention.occurred_at
        ).total_seconds() * 1000

        await self.db.commit()
        await self.db.refresh(prevention)
        return prevention


# =====================================================================
# Governance Conflict Resolver
# =====================================================================

class GovernanceConflictResolver:
    """
    Resolves conflicts between governance rules.
    Manages conflict resolution strategies.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._conflicts: Dict[str, GovernanceConflict] = {}

    async def initialize(self) -> None:
        """Initialize the resolver"""
        logger.info("GovernanceConflictResolver initialized")

    async def detect_conflict(
        self,
        session_id: str,
        lineage_id: str,
        conflict_type: str,
        conflicting_rules: List[str],
        rule_priorities: Optional[Dict[str, int]] = None,
    ) -> GovernanceConflict:
        """Detect and record a conflict"""
        conflict = GovernanceConflict(
            conflict_id=f"gov_conflict_{uuid4()}",
            session_id=session_id,
            lineage_id=lineage_id,
            conflict_type=conflict_type,
            conflicting_rules=conflicting_rules,
            rule_priorities=rule_priorities,
            occurred_at=datetime.utcnow(),
        )

        self.db.add(conflict)
        await self.db.commit()
        await self.db.refresh(conflict)
        self._conflicts[conflict.conflict_id] = conflict
        return conflict

    async def resolve_conflict(
        self,
        conflict_id: str,
        strategy: ConflictResolution,
    ) -> GovernanceConflict:
        """Resolve a conflict"""
        conflict = self._conflicts.get(conflict_id) or await self.db.execute(
            select(GovernanceConflict).where(
                GovernanceConflict.conflict_id == conflict_id)
        ).scalar_one_or_none()

        if not conflict:
            raise ValueError(f"Conflict not found: {conflict_id}")

        conflict.conflict_state = "resolved"
        conflict.resolution_strategy = strategy.value

        # Determine winning rule based on strategy
        if strategy == ConflictResolution.PRIORITY and conflict.rule_priorities:
            winning = max(conflict.rule_priorities.items(), key=lambda x: x[1])
            conflict.winning_rule = winning[0]
        elif strategy == ConflictResolution.ROLLBACK:
            conflict.winning_rule = None  # No winner, rollback
        else:
            conflict.winning_rule = conflict.conflicting_rules[0] if conflict.conflicting_rules else None

        conflict.resolution_applied = True
        conflict.resolved_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(conflict)
        return conflict


# =====================================================================
# Stability Coordinator
# =====================================================================

class StabilityCoordinator:
    """
    Coordinates stability across the ecosystem.
    Manages stability sessions.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._sessions: Dict[str, StabilitySession] = {}

    async def initialize(self) -> None:
        """Initialize the coordinator"""
        logger.info("StabilityCoordinator initialized")

    async def create_session(
        self,
        session_scope: str,
        scope_kind: str,
    ) -> StabilitySession:
        """Create a new stability session"""
        session = StabilitySession(
            session_id=f"stability_{uuid4()}",
            session_scope=session_scope,
            scope_kind=scope_kind,
            started_at=datetime.utcnow(),
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        self._sessions[session.session_id] = session
        return session

    async def update_session(
        self,
        session_id: str,
        stability_score: Optional[float] = None,
        safety_score: Optional[float] = None,
        safety_state: Optional[SafetyState] = None,
    ) -> StabilitySession:
        """Update session metrics"""
        session = self._sessions.get(session_id) or await self.db.execute(
            select(StabilitySession).where(
                StabilitySession.session_id == session_id)
        ).scalar_one_or_none()

        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if stability_score is not None:
            session.stability_score = stability_score
        if safety_score is not None:
            session.safety_score = safety_score
        if safety_state is not None:
            session.safety_state = safety_state.value

        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def complete_session(
        self,
        session_id: str,
    ) -> StabilitySession:
        """Complete a session"""
        session = self._sessions.get(session_id) or await self.db.execute(
            select(StabilitySession).where(
                StabilitySession.session_id == session_id)
        ).scalar_one_or_none()

        if not session:
            raise ValueError(f"Session not found: {session_id}")

        session.session_state = "completed"
        session.completed_at = datetime.utcnow()
        session.duration_seconds = (
            session.completed_at - session.started_at
        ).total_seconds()

        await self.db.commit()
        await self.db.refresh(session)

        if session_id in self._sessions:
            del self._sessions[session_id]

        return session


# =====================================================================
# Safety Telemetry
# =====================================================================

class SafetyTelemetry:
    """
    Records safety telemetry.
    Monitors safety metrics over time.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self) -> None:
        """Initialize telemetry"""
        logger.info("SafetyTelemetry initialized")

    async def record_metric(
        self,
        metric_scope: str,
        metric_type: str,
        metric_name: str,
        value: float,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> SafetyMetric:
        """Record a safety metric"""
        metric = SafetyMetric(
            metric_id=f"safety_metric_{uuid4()}",
            session_id=session_id,
            metric_scope=metric_scope,
            metric_type=metric_type,
            metric_name=metric_name,
            value=value,
            unit=kwargs.get("unit"),
            target_id=kwargs.get("target_id"),
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
    ) -> List[SafetyMetric]:
        """Get metrics over time"""
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)

        result = await self.db.execute(
            select(SafetyMetric).where(
                and_(
                    SafetyMetric.metric_name == metric_name,
                    SafetyMetric.captured_at >= cutoff,
                )
            ).order_by(SafetyMetric.captured_at.desc())
        )
        return list(result.scalars().all())


__all__ = [
    "RecursiveSafetyEngine",
    "SafetyBoundaryManager",
    "CollapsePreventionSystem",
    "GovernanceConflictResolver",
    "StabilityCoordinator",
    "SafetyTelemetry",
    "SafetyAssessment",
    "BoundaryValidation",
]
