"""
Evolution Governance Services - Production-grade evolutionary governance infrastructure

Provides:
- Evolution governance engine
- Mutation policy management
- Cognition adaptation control
- Semantic continuity validation
- Recursive evolution coordination
- Systemic coherence supervision
- Evolution audit service

All services support:
- Async operation
- Typed evolution contracts
- Adaptation lineage tracking
- Distributed governance visibility
- Recursive evolution traceability
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, update, func

from .models import (
    EvolutionStage,
    CoherenceState,
    AdaptationStrategy,
    MutationSeverity,
    GovernanceLevel,
    EvolutionProfile,
    MutationPolicy,
    CognitionAdaptationRule,
    SemanticContinuityContract,
    RecursiveEvolutionSession,
    SystemicCoherenceSnapshot,
    EvolutionGovernanceAudit,
    AdaptationLineage,
)

logger = logging.getLogger(__name__)


# =====================================================================
# Data Transfer Objects
# =====================================================================

@dataclass
class EvolutionDecision:
    """Result of an evolution governance decision"""
    approved: bool
    action: str
    reason: str
    severity: str
    governance_level: str
    required_approvals: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    mutations_suggested: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class MutationEvaluation:
    """Evaluation result for a mutation"""
    mutation_id: str
    policy_applied: Optional[MutationPolicy]
    approved: bool
    severity: MutationSeverity
    risk_score: float
    required_preconditions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    conditions_met: bool = True


@dataclass
class CoherenceAssessment:
    """Systemic coherence assessment result"""
    is_coherent: bool
    coherence_score: float
    coherence_state: CoherenceState
    drift_sources: List[Dict[str, Any]] = field(default_factory=list)
    contract_violations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class AdaptationResult:
    """Result of an adaptation operation"""
    adaptation_id: str
    lineage_id: str
    approved: bool
    changes: Dict[str, Any] = field(default_factory=dict)
    rollback_required: bool
    coherence_impact: float


# =====================================================================
# Evolution Governance Engine
# =====================================================================

class EvolutionGovernanceEngine:
    """
    Central evolution governance engine.
    Coordinates evolutionary processes, policies, and coherence systems.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._profiles: Dict[str, EvolutionProfile] = {}
        self._running = False

    async def initialize(self) -> None:
        """Initialize the governance engine"""
        await self._load_profiles()
        self._running = True
        logger.info("EvolutionGovernanceEngine initialized")

    async def shutdown(self) -> None:
        """Shutdown the engine"""
        self._running = False
        logger.info("EvolutionGovernanceEngine shutdown")

    async def _load_profiles(self) -> None:
        """Load active profiles into cache"""
        result = await self.db.execute(
            select(EvolutionProfile).where(EvolutionProfile.is_active.is_(True))
        )
        for profile in result.scalars().all():
            self._profiles[profile.profile_id] = profile

    # ---- Profile Management ----

    async def create_profile(
        self,
        profile_scope: str,
        profile_key: str,
        governance_level: GovernanceLevel = GovernanceLevel.INTERVENTION,
        adaptation_strategy: AdaptationStrategy = AdaptationStrategy.BALANCED,
        coherence_target: float = 0.85,
        mutation_severity_cap: MutationSeverity = MutationSeverity.MODERATE,
        **kwargs,
    ) -> EvolutionProfile:
        """Create a new evolution profile"""
        profile = EvolutionProfile(
            profile_id=f"evo_profile_{uuid4()}",
            profile_scope=profile_scope,
            profile_key=profile_key,
            governance_level=governance_level.value,
            adaptation_strategy=adaptation_strategy.value,
            coherence_target=coherence_target,
            mutation_severity_cap=mutation_severity_cap.value,
            **kwargs,
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        self._profiles[profile.profile_id] = profile
        return profile

    async def get_profile(self, profile_id: str) -> Optional[EvolutionProfile]:
        """Get a profile by ID"""
        return self._profiles.get(profile_id) or await self.db.execute(
            select(EvolutionProfile).where(EvolutionProfile.profile_id == profile_id)
        ).scalar_one_or_none()

    async def update_profile_metrics(
        self,
        profile_id: str,
        cycle_delta: int = 0,
        mutation_delta: int = 0,
        success_delta: int = 0,
        failure_delta: int = 0,
    ) -> None:
        """Update profile metrics"""
        profile = await self.get_profile(profile_id)
        if profile:
            profile.cycle_count += cycle_delta
            profile.total_mutations += mutation_delta
            profile.successful_adaptations += success_delta
            profile.failed_adaptations += failure_delta
            await self.db.commit()

    # ---- Evolution Decision ----

    async def evaluate_evolution(
        self,
        scope: str,
        mutations: List[Dict[str, Any]],
        actor_ctx: Dict[str, Any],
        coherence_snapshot: Optional[Dict[str, Any]] = None,
    ) -> EvolutionDecision:
        """Evaluate whether evolution is permitted under current governance"""
        # Get applicable profile
        profile_result = await self.db.execute(
            select(EvolutionProfile).where(
                and_(
                    EvolutionProfile.profile_scope == scope,
                    EvolutionProfile.is_active.is_(True),
                )
            )
        )
        profile = profile_result.scalar_one_or_none()

        if not profile:
            # Default permissive decision
            return EvolutionDecision(
                approved=True,
                action="allow",
                reason="no profile found, default allow",
                severity=MutationSeverity.TRIVIAL.value,
                governance_level=GovernanceLevel.OBSERVATION.value,
            )

        # Evaluate against cooldown
        if profile.mutation_cooldown_seconds > 0:
            time_since_last = 0.0  # Would calculate from last mutation
            if time_since_last < profile.mutation_cooldown_seconds:
                return EvolutionDecision(
                    approved=False,
                    action="deny_cooldown",
                    reason=f"mutation cooldown active ({profile.mutation_cooldown_seconds}s)",
                    severity=MutationSeverity.TRIVIAL.value,
                    governance_level=profile.governance_level,
                    warnings=["cooldown period active"],
                )

        # Check mutation count limit
        if len(mutations) > profile.max_mutations_per_cycle:
            return EvolutionDecision(
                approved=False,
                action="deny_count",
                reason=f"exceeds max mutations per cycle ({profile.max_mutations_per_cycle})",
                severity=MutationSeverity.MINOR.value,
                governance_level=profile.governance_level,
                warnings=["mutation count limit exceeded"],
            )

        # Evaluate severity
        severity_order = list(MutationSeverity)
        cap_severity = MutationSeverity(profile.mutation_severity_cap)
        max_requested = max(
            (MutationSeverity(m.get("severity", MutationSeverity.TRIVIAL.value)) for m in mutations),
            default=cap_severity,
        )
        if severity_order.index(max_requested) > severity_order.index(cap_severity):
            return EvolutionDecision(
                approved=False,
                action="deny_severity",
                reason=f"severity {max_requested.value} exceeds cap {cap_severity.value}",
                severity=max_requested.value,
                governance_level=profile.governance_level,
                warnings=[f"severity cap exceeded: {max_requested.value} > {cap_severity.value}"],
            )

        # Check coherence constraints
        if coherence_snapshot and profile.coherence_threshold > 0:
            coherence_score = coherence_snapshot.get("coherence_score", 1.0)
            if coherence_score < profile.coherence_threshold:
                return EvolutionDecision(
                    approved=False,
                    action="deny_coherence",
                    reason=f"coherence {coherence_score:.2f} below threshold {profile.coherence_threshold}",
                    severity=MutationSeverity.MODERATE.value,
                    governance_level=profile.governance_level,
                    warnings=["coherence below safe threshold"],
                )

        # Approve with possible suggestions
        suggested_mutations = self._suggest_mutations(profile, mutations)

        return EvolutionDecision(
            approved=True,
            action="allow",
            reason="passed governance evaluation",
            severity=max_requested.value,
            governance_level=profile.governance_level,
            mutations_suggested=suggested_mutations,
        )

    def _suggest_mutations(
        self,
        profile: EvolutionProfile,
        mutations: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Suggest modifications to mutations based on profile"""
        suggestions = []
        # Example: suggest lower severity if close to cap
        cap_idx = list(MutationSeverity).index(MutationSeverity(profile.mutation_severity_cap))
        for m in mutations:
            sev_idx = list(MutationSeverity).index(
                MutationSeverity(m.get("severity", MutationSeverity.TRIVIAL.value)))
            if sev_idx >= cap_idx - 1 and sev_idx > 0:
                suggestions.append({
                    "type": "severity_reduction",
                    "mutation_id": m.get("id"),
                    "from": m.get("severity"),
                    "to": list(MutationSeverity)[sev_idx - 1].value,
                    "reason": "approaching severity cap",
                })
        return suggestions


# =====================================================================
# Mutation Policy Manager
# =====================================================================

class MutationPolicyManager:
    """
    Manages orchestration mutation policies.
    Evaluates and enforces mutation constraints.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._policies: Dict[str, MutationPolicy] = {}

    async def initialize(self) -> None:
        """Initialize the policy manager"""
        result = await self.db.execute(
            select(MutationPolicy).where(MutationPolicy.is_active.is_(True))
        )
        for policy in result.scalars().all():
            self._policies[policy.policy_id] = policy
        logger.info("MutationPolicyManager initialized with %d policies", len(self._policies))

    async def create_policy(
        self,
        policy_domain: str,
        policy_key: str,
        allowed_mutations: List[str],
        min_severity: MutationSeverity = MutationSeverity.TRIVIAL,
        max_severity: MutationSeverity = MutationSeverity.CRITICAL,
        requires_approval: bool = False,
        **kwargs,
    ) -> MutationPolicy:
        """Create a new mutation policy"""
        policy = MutationPolicy(
            policy_id=f"mut_policy_{uuid4()}",
            policy_domain=policy_domain,
            policy_key=policy_key,
            allowed_mutations=allowed_mutations,
            min_severity_threshold=min_severity.value,
            max_severity_threshold=max_severity.value,
            requires_approval=requires_approval,
            **kwargs,
        )
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        self._policies[policy.policy_id] = policy
        return policy

    async def evaluate_mutation(
        self,
        mutation: Dict[str, Any],
        domain: str,
        kind: Optional[str] = None,
    ) -> MutationEvaluation:
        """Evaluate a mutation against applicable policies"""
        # Find applicable policy
        query = select(MutationPolicy).where(
            and_(
                MutationPolicy.policy_domain == domain,
                MutationPolicy.is_active.is_(True),
            )
        )
        if kind:
            query = query.where(
                or_(
                    MutationPolicy.applies_to_kinds.is_(None),
                    MutationPolicy.applies_to_kinds.contains([kind]),
                )
            )

        result = await self.db.execute(query.order_by(MutationPolicy.priority.desc()))
        policies = list(result.scalars().all())

        if not policies:
            # Default permissive
            return MutationEvaluation(
                mutation_id=mutation.get("id", str(uuid4())),
                policy_applied=None,
                approved=True,
                severity=MutationSeverity.TRIVIAL,
                risk_score=0.0,
            )

        policy = policies[0]  # Use highest priority policy

        # Check severity threshold
        mutation_severity = MutationSeverity(
            mutation.get("severity", MutationSeverity.TRIVIAL.value))
        min_sev = MutationSeverity(policy.min_severity_threshold)
        max_sev = MutationSeverity(policy.max_severity_threshold)

        if list(MutationSeverity).index(mutation_severity) < list(MutationSeverity).index(min_sev):
            return MutationEvaluation(
                mutation_id=mutation.get("id", str(uuid4())),
                policy_applied=policy,
                approved=False,
                severity=mutation_severity,
                risk_score=1.0,
                warnings=["severity below minimum threshold"],
            )

        if list(MutationSeverity).index(mutation_severity) > list(MutationSeverity).index(max_sev):
            return MutationEvaluation(
                mutation_id=mutation.get("id", str(uuid4())),
                policy_applied=policy,
                approved=False,
                severity=mutation_severity,
                risk_score=1.0,
                warnings=["severity exceeds maximum threshold"],
            )

        # Check mutation type is allowed
        mutation_type = mutation.get("type", "")
        if mutation_type not in policy.allowed_mutations:
            return MutationEvaluation(
                mutation_id=mutation.get("id", str(uuid4())),
                policy_applied=policy,
                approved=False,
                severity=mutation_severity,
                risk_score=0.9,
                warnings=[f"To perform {mutation_type}, you need proper authorization"],
            )

        # Calculate risk score based on severity and conditions
        severity_idx = list(MutationSeverity).index(mutation_severity)
        risk_score = (severity_idx + 1) / len(MutationSeverity)

        # Update policy stats
        policy.trigger_count += 1
        await self.db.commit()

        return MutationEvaluation(
            mutation_id=mutation.get("id", str(uuid4())),
            policy_applied=policy,
            approved=True,
            severity=mutation_severity,
            risk_score=risk_score,
        )


# =====================================================================
# Cognition Adaptation Controller
# =====================================================================

class CognitionAdaptationController:
    """
    Controls cognition adaptation processes.
    Manages adaptation rules and convergence validation.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._rules: Dict[str, CognitionAdaptationRule] = {}

    async def initialize(self) -> None:
        """Initialize the controller"""
        result = await self.db.execute(
            select(CognitionAdaptationRule).where(
                CognitionAdaptationRule.is_active.is_(True))
        )
        for rule in result.scalars().all():
            self._rules[rule.rule_id] = rule
        logger.info("CognitionAdaptationController initialized with %d rules", len(self._rules))

    async def evaluate_adaptation(
        self,
        reasoning_type: str,
        domain: str,
        current_state: Dict[str, Any],
        target_state: Dict[str, Any],
    ) -> AdaptationResult:
        """Evaluate an adaptation for cognition"""
        # Find applicable rule
        result = await self.db.execute(
            select(CognitionAdaptationRule).where(
                and_(
                    CognitionAdaptationRule.applies_to_reasoning_types.contains([reasoning_type]),
                    CognitionAdaptationRule.is_active.is_(True),
                )
            )
        )
        rule = result.scalar_one_or_none()

        if not rule:
            # Default adaptation
            adaptation_id = f"cog_adapt_{uuid4()}"
            return AdaptationResult(
                adaptation_id=adaptation_id,
                lineage_id=f"lineage_{adaptation_id}",
                approved=True,
                changes={"delta": {}},
                rollback_required=False,
                coherence_impact=0.0,
            )

        # Calculate magnitude of adaptation
        magnitude = self._calculate_magnitude(current_state, target_state)
        
        if magnitude < rule.adaptation_magnitude_min:
            return AdaptationResult(
                adaptation_id=f"cog_adapt_{uuid4()}",
                lineage_id=f"lineage_{uuid4()}",
                approved=False,
                changes={},
                rollback_required=False,
                coherence_impact=0.0,
            )

        if magnitude > rule.adaptation_magnitude_max:
            return AdaptationResult(
                adaptation_id=f"cog_adapt_{uuid4()}",
                lineage_id=f"lineage_{uuid4()}",
                approved=False,
                changes={},
                rollback_required=True,
                coherence_impact=0.5,
            )

        # Check divergence threshold
        divergence = self._calculate_divergence(current_state, target_state, rule)
        if divergence > rule.divergence_threshold:
            rule.divergence_count += 1
            await self.db.commit()
            return AdaptationResult(
                adaptation_id=f"cog_adapt_{uuid4()}",
                lineage_id=f"lineage_{uuid4()}",
                approved=False,
                changes={},
                rollback_required=rule.rollback_on_divergence,
                coherence_impact=divergence,
            )

        # Approve adaptation
        rule.adaptation_count += 1
        await self.db.commit()

        return AdaptationResult(
            adaptation_id=f"cog_adapt_{uuid4()}",
            lineage_id=f"lineage_{uuid4()}",
            approved=True,
            changes={"delta": {k: target_state.get(k) - current_state.get(k, 0) 
                               for k in target_state if k in current_state}},
            rollback_required=False,
            coherence_impact=magnitude * 0.1,
        )

    def _calculate_magnitude(
        self,
        current: Dict[str, Any],
        target: Dict[str, Any],
    ) -> float:
        """Calculate the magnitude of adaptation"""
        if not current or not target:
            return 0.0
        # Simple Euclidean-like magnitude
        delta_sum = sum(
            (target.get(k, 0) - current.get(k, 0)) ** 2
            for k in set(current.keys()) | set(target.keys())
        )
        return delta_sum ** 0.5

    def _calculate_divergence(
        self,
        current: Dict[str, Any],
        target: Dict[str, Any],
        rule: CognitionAdaptationRule,
    ) -> float:
        """Calculate divergence score"""
        magnitude = self._calculate_magnitude(current, target)
        # Normalized by target scale factor
        return magnitude / rule.adaptation_magnitude_max if rule.adaptation_magnitude_max > 0 else 0.0


# =====================================================================
# Semantic Continuity Validator
# =====================================================================

class SemanticContinuityValidator:
    """
    Validates semantic continuity across evolution.
    Enforces invariants and detects violations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._contracts: Dict[str, SemanticContinuityContract] = {}

    async def initialize(self) -> None:
        """Initialize the validator"""
        await self._load_contracts()
        logger.info("SemanticContinuityValidator initialized")

    async def _load_contracts(self) -> None:
        """Load active contracts"""
        result = await self.db.execute(
            select(SemanticContinuityContract).where(
                SemanticContinuityContract.is_active.is_(True))
        )
        for contract in result.scalars().all():
            self._contracts[contract.contract_id] = contract

    async def validate_invariants(
        self,
        scope: str,
        state: Dict[str, Any],
        contracts: Optional[List[str]] = None,
    ) -> CoherenceAssessment:
        """Validate semantic invariants for a scope"""
        violations: List[str] = []
        drift_sources: List[Dict[str, Any]] = []

        # Find applicable contracts
        query = select(SemanticContinuityContract).where(
            and_(
                SemanticContinuityContract.contract_scope == scope,
                SemanticContinuityContract.is_active.is_(True),
            )
        )
        if contracts:
            query = query.where(
                SemanticContinuityContract.contract_id.in_(contracts))
        
        result = await self.db.execute(query)
        applicable_contracts = list(result.scalars().all())

        if not applicable_contracts:
            return CoherenceAssessment(
                is_coherent=True,
                coherence_score=1.0,
                coherence_state=CoherenceState.ALIGNED,
                recommendations=[],
            )

        for contract in applicable_contracts:
            contract.validation_count += 1

            # Check each invariant
            for invariant in contract.invariants:
                invariant_type = invariant.get("type")
                invariant_params = invariant.get("params", {})

                if invariant_type == "property_exists":
                    prop_name = invariant_params.get("property")
                    if prop_name and prop_name not in state:
                        violations.append(f"{contract.contract_id}: missing {prop_name}")
                        contract.violation_count += 1

                elif invariant_type == "property_range":
                    prop_name = invariant_params.get("property")
                    min_val = invariant_params.get("min")
                    max_val = invariant_params.get("max")
                    if prop_name in state:
                        val = state[prop_name]
                        if min_val is not None and val < min_val:
                            violations.append(f"{contract.contract_id}: {prop_name} below min")
                            contract.violation_count += 1
                        if max_val is not None and val > max_val:
                            violations.append(f"{contract.contract_id}: {prop_name} above max")
                            contract.violation_count += 1

                elif invariant_type == "property_comparison":
                    prop_a = invariant_params.get("property_a")
                    prop_b = invariant_params.get("property_b")
                    operator = invariant_params.get("operator", "eq")
                    expected = invariant_params.get("expected")
                    if prop_a in state and prop_b in state:
                        actual = state[prop_a] - state[prop_b]  # Simplified
                        if operator == "eq" and abs(actual - expected) > 0.001:
                            violations.append(f"{contract.contract_id}: comparison failed")
                            contract.violation_count += 1

            contract.last_validated_at = datetime.utcnow()

        await self.db.commit()

        # Calculate coherence score
        violation_penalty = len(violations) * 0.1
        coherence_score = max(0.0, 1.0 - violation_penalty)

        # Determine coherence state
        if coherence_score >= 0.9:
            coherence_state = CoherenceState.ALIGNED
        elif coherence_score >= 0.7:
            coherence_state = CoherenceState.DRIFTING
        elif coherence_score >= 0.5:
            coherence_state = CoherenceState.RECOVERING
        else:
            coherence_state = CoherenceState.FRAGMENTED

        return CoherenceAssessment(
            is_coherent=len(violations) == 0,
            coherence_score=coherence_score,
            coherence_state=coherence_state,
            contract_violations=violations,
            recommendations=self._generate_recommendations(violations),
        )

    def _generate_recommendations(self, violations: List[str]) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []
        for v in violations:
            if "missing" in v:
                recommendations.append(f"Add missing property identified in: {v}")
            elif "below" in v or "above" in v:
                recommendations.append(f"Adjust property value identified in: {v}")
            else:
                recommendations.append(f"Review semantic invariant: {v}")
        return recommendations


# =====================================================================
# Recursive Evolution Coordinator
# =====================================================================

class RecursiveEvolutionCoordinator:
    """
    Coordinates recursive evolution sessions.
    Manages nested evolution hierarchies.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._active_sessions: Dict[str, RecursiveEvolutionSession] = {}

    async def initialize(self) -> None:
        """Initialize the coordinator"""
        await self._load_active_sessions()
        logger.info("RecursiveEvolutionCoordinator initialized")

    async def _load_active_sessions(self) -> None:
        """Load active sessions"""
        result = await self.db.execute(
            select(RecursiveEvolutionSession).where(
                RecursiveEvolutionSession.session_state.in_(["init", "running", "paused"])
            )
        )
        for session in result.scalars().all():
            self._active_sessions[session.session_id] = session

    async def create_session(
        self,
        session_scope: str,
        governance_level: GovernanceLevel = GovernanceLevel.INTERVENTION,
        strategy: AdaptationStrategy = AdaptationStrategy.RECURSIVE,
        max_depth: int = 10,
        parent_session_id: Optional[UUID] = None,
        scope_kind: Optional[str] = None,
        scope_id: Optional[str] = None,
    ) -> RecursiveEvolutionSession:
        """Create a new recursive evolution session"""
        # Calculate depth if parent exists
        recursion_depth = 0
        root_session_id = None
        if parent_session_id:
            parent = await self.db.get(RecursiveEvolutionSession, parent_session_id)
            if parent:
                recursion_depth = parent.recursion_depth + 1
                root_session_id = parent.root_session_id or parent.id
        
        if recursion_depth >= max_depth:
            raise ValueError(f"max recursion depth {max_depth} exceeded")

        session = RecursiveEvolutionSession(
            session_id=f"rec_evo_{uuid4()}",
            session_scope=session_scope,
            governance_level=governance_level.value,
            strategy=strategy.value,
            max_recursion_depth=max_depth,
            recursion_depth=recursion_depth,
            parent_session_id=parent_session_id,
            root_session_id=root_session_id,
            scope_kind=scope_kind,
            scope_id=scope_id,
            started_at=datetime.utcnow(),
            session_state="init",
            coherence_state=CoherenceState.ALIGNED.value,
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        self._active_sessions[session.session_id] = session

        # Update parent if exists
        if parent_session_id:
            parent = await self.db.get(RecursiveEvolutionSession, parent_session_id)
            if parent:
                child_ids = parent.child_session_ids or []
                child_ids.append(session.session_id)
                parent.child_session_ids = child_ids
                await self.db.commit()

        return session

    async def advance_session(
        self,
        session_id: str,
        mutations: List[Dict[str, Any]],
        metrics: Optional[Dict[str, float]] = None,
    ) -> RecursiveEvolutionSession:
        """Advance a session by applying mutations"""
        session = self._active_sessions.get(session_id) or await self.db.execute(
            select(RecursiveEvolutionSession).where(
                RecursiveEvolutionSession.session_id == session_id)
        ).scalar_one_or_none()

        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if session.session_state == "completed":
            raise ValueError(f"Session already completed: {session_id}")

        # Apply state
        session.session_state = "running"
        session.cycle_count += 1
        session.mutations_applied += len(mutations)
        session.mutations_successful += len([m for m in mutations if m.get("success", True)])

        if metrics:
            session.evolution_metrics = metrics
            session.coherence_score = metrics.get("coherence_score", session.coherence_score)
            session.adaptation_efficiency = metrics.get("efficiency", session.adaptation_efficiency)

        await self.db.commit()
        return session

    async def complete_session(
        self,
        session_id: str,
        final_metrics: Optional[Dict[str, float]] = None,
    ) -> RecursiveEvolutionSession:
        """Complete a session"""
        session = self._active_sessions.get(session_id) or await self.db.execute(
            select(RecursiveEvolutionSession).where(
                RecursiveEvolutionSession.session_id == session_id)
        ).scalar_one_or_none()

        if not session:
            raise ValueError(f"Session not found: {session_id}")

        session.session_state = "completed"
        session.completed_at = datetime.utcnow()
        session.duration_seconds = (
            session.completed_at - session.started_at
        ).total_seconds()

        if final_metrics:
            session.evolution_metrics = final_metrics

        # Remove from active
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]

        await self.db.commit()
        return session


# =====================================================================
# Systemic Coherence Supervisor
# =====================================================================

class SystemicCoherenceSupervisor:
    """
    Supervises systemic coherence.
    Monitors and maintains platform-wide coherence.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def capture_snapshot(
        self,
        snapshot_key: str,
        coherence_metrics: Dict[str, float],
        component_states: Dict[str, str],
        pending_mutations: Optional[List[Dict[str, Any]]] = None,
        session_id: Optional[str] = None,
    ) -> SystemicCoherenceSnapshot:
        """Capture a coherence snapshot"""
        coherence_score = coherence_metrics.get("overall", 0.9)
        drift_score = coherence_metrics.get("drift", 0.0)

        # Determine coherence state
        if coherence_score >= 0.9:
            coherence_state = CoherenceState.ALIGNED.value
        elif coherence_score >= 0.7:
            coherence_state = CoherenceState.DRIFTING.value
        elif coherence_score >= 0.5:
            coherence_state = CoherenceState.RECOVERING.value
        else:
            coherence_state = CoherenceState.FRAGMENTED.value

        snapshot = SystemicCoherenceSnapshot(
            snapshot_id=f"coh_snap_{uuid4()}",
            session_id=session_id,
            snapshot_key=snapshot_key,
            coherence_state=coherence_state,
            coherence_score=coherence_score,
            drift_score=drift_score,
            component_states=component_states,
            component_coherence_scores={
                k: v for k, v in coherence_metrics.items()
                if k not in ["overall", "drift"]
            },
            orchestration_health=coherence_metrics.get("orchestration", 1.0),
            cognition_alignment=coherence_metrics.get("cognition", 1.0),
            semantic_stability=coherence_metrics.get("semantic", 1.0),
            distributed_sync=coherence_metrics.get("distributed", 1.0),
            pending_mutations=pending_mutations,
            captured_at=datetime.utcnow(),
        )

        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)
        return snapshot

    async def assess_systemic_coherence(
        self,
        scope: Optional[str] = None,
        window_seconds: int = 300,
    ) -> CoherenceAssessment:
        """Assess current systemic coherence"""
        # Get recent snapshots
        query = select(SystemicCoherenceSnapshot)
        if scope:
            query = query.where(SystemicCoherenceSnapshot.session_id.like(f"%{scope}%"))
        
        query = query.order_by(SystemicCoherenceSnapshot.captured_at.desc()).limit(10)
        result = await self.db.execute(query)
        snapshots = list(result.scalars().all())

        if not snapshots:
            return CoherenceAssessment(
                is_coherent=True,
                coherence_score=1.0,
                coherence_state=CoherenceState.ALIGNED,
                recommendations=["no snapshots available"],
            )

        # Aggregate metrics
        avg_score = sum(s.coherence_score for s in snapshots) / len(snapshots)
        avg_drift = sum(s.drift_score for s in snapshots) / len(snapshots)
        total_violations = sum(s.violation_count for s in snapshots)

        # Determine state
        if avg_score >= 0.9:
            state = CoherenceState.ALIGNED
        elif avg_score >= 0.7:
            state = CoherenceState.DRIFTING
        elif avg_score >= 0.5:
            state = CoherenceState.RECOVERING
        else:
            state = CoherenceState.FRAGMENTED

        return CoherenceAssessment(
            is_coherent=total_violations == 0 and avg_score >= 0.7,
            coherence_score=avg_score,
            coherence_state=state,
            drift_sources=[{"snapshot": s.snapshot_id, "drift": s.drift_score} 
                          for s in snapshots if s.drift_score > 0.2],
            recommendations=self._generate_coherence_recommendations(
                avg_score, avg_drift, total_violations),
        )

    def _generate_coherence_recommendations(
        self,
        score: float,
        drift: float,
        violations: int,
    ) -> List[str]:
        """Generate coherence recommendations"""
        recs = []
        if score < 0.7:
            recs.append("coherence_score_low: review recent mutations for stability")
        if drift > 0.2:
            recs.append("drift_detected: evaluate semantic alignment across components")
        if violations > 0:
            recs.append(f"contract_violations: address {violations} active contract violations")
        if score >= 0.9:
            recs.append("system_healthy: coherence targets met")
        return recs


# =====================================================================
# Evolution Audit Service
# =====================================================================

class EvolutionAuditService:
    """
    Tracks all evolution governance actions.
    Maintains audit trail for compliance.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self,
        action_type: str,
        action_target: str,
        actor_type: str,
        governance_level: GovernanceLevel,
        outcome_type: str,
        success: bool = True,
        pre_state: Optional[Dict[str, Any]] = None,
        post_state: Optional[Dict[str, Any]] = None,
        action_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        profile_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> EvolutionGovernanceAudit:
        """Log a governance action"""
        audit = EvolutionGovernanceAudit(
            audit_id=f"evo_audit_{uuid4()}",
            action_type=action_type,
            action_target=action_target,
            actor_type=actor_type,
            actor_id=actor_id,
            governance_level_used=governance_level.value,
            outcome_type=outcome_type,
            success=success,
            pre_state=pre_state,
            post_state=post_state,
            action_context=action_context or {},
            logged_at=datetime.utcnow(),
            session_id=session_id,
            profile_id=profile_id,
            correlation_id=correlation_id,
        )

        self.db.add(audit)
        await self.db.commit()
        await self.db.refresh(audit)
        return audit

    async def get_audit_trail(
        self,
        session_id: Optional[str] = None,
        action_type: Optional[str] = None,
        actor_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[EvolutionGovernanceAudit]:
        """Get audit trail entries"""
        query = select(EvolutionGovernanceAudit)
        
        if session_id:
            query = query.where(EvolutionGovernanceAudit.session_id == session_id)
        if action_type:
            query = query.where(EvolutionGovernanceAudit.action_type == action_type)
        if actor_type:
            query = query.where(EvolutionGovernanceAudit.actor_type == actor_type)

        result = await self.db.execute(
            query.order_by(EvolutionGovernanceAudit.logged_at.desc()).limit(limit))
        return list(result.scalars().all())


# =====================================================================
# Adaptation Lineage Tracker
# =====================================================================

class AdaptationLineageTracker:
    """
    Tracks adaptation lineage for traceability.
    Records evolution history of orchestrations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_adaptation(
        self,
        subject_kind: str,
        subject_key: str,
        adaptation_type: str,
        adaptation_trigger: str,
        pre_state: Dict[str, Any],
        post_state: Dict[str, Any],
        parent_adaptation_id: Optional[UUID] = None,
        lineage_id: Optional[str] = None,
        **kwargs,
    ) -> AdaptationLineage:
        """Record an adaptation event"""
        adaptation_id = f"adapt_{uuid4()}"
        if not lineage_id:
            lineage_id = f"lineage_{uuid4()}"

        # Calculate lineage depth
        lineage_depth = 0
        root_id = None
        if parent_adaptation_id:
            parent = await self.db.get(AdaptationLineage, parent_adaptation_id)
            if parent:
                lineage_depth = parent.lineage_depth + 1
                root_id = parent.root_adaptation_id or parent.id

        # Calculate changes
        changes = {}
        for k in set(pre_state.keys()) | set(post_state.keys()):
            if pre_state.get(k) != post_state.get(k):
                changes[k] = {
                    "from": pre_state.get(k),
                    "to": post_state.get(k),
                }

        # Calculate impact scores
        impact = len(changes) * 0.1
        risk = self._calculate_risk(pre_state, post_state)
        benefit = self._calculate_benefit(pre_state, post_state)

        adaptation = AdaptationLineage(
            adaptation_id=adaptation_id,
            lineage_id=lineage_id,
            subject_kind=subject_kind,
            subject_key=subject_key,
            adaptation_type=adaptation_type,
            adaptation_trigger=adaptation_trigger,
            pre_adaptation_state=pre_state,
            post_adaptation_state=post_state,
            changes_delta=changes,
            impact_score=impact,
            risk_score=risk,
            benefit_score=benefit,
            outcome="completed",
            lineage_depth=lineage_depth,
            parent_adaptation_id=parent_adaptation_id,
            root_adaptation_id=root_id,
            started_at=datetime.utcnow(),
            **kwargs,
        )

        self.db.add(adaptation)
        await self.db.commit()
        await self.db.refresh(adaptation)
        return adaptation

    def _calculate_risk(
        self,
        pre: Dict[str, Any],
        post: Dict[str, Any],
    ) -> float:
        """Calculate risk score for adaptation"""
        # Simplified risk calculation
        critical_keys = ["governance", "security", "core", "primary"]
        risk = 0.0
        for k in post.keys():
            if any(ck in k.lower() for ck in critical_keys):
                risk += 0.7
            elif post[k] != pre.get(k):
                risk += 0.1
        return min(1.0, risk)

    def _calculate_benefit(
        self,
        pre: Dict[str, Any],
        post: Dict[str, Any],
    ) -> float:
        """Calculate benefit score for adaptation"""
        # Simplified benefit calculation
        improvement_keys = ["performance", "efficiency", "quality", "reliability"]
        benefit = 0.0
        for k in post.keys():
            if any(ik in k.lower() for ik in improvement_keys):
                if isinstance(post[k], (int, float)) and isinstance(pre.get(k), (int, float)):
                    if post[k] > pre[k]:
                        benefit += 0.5
        return min(1.0, benefit)


__all__ = [
    "EvolutionGovernanceEngine",
    "MutationPolicyManager",
    "CognitionAdaptationController",
    "SemanticContinuityValidator",
    "RecursiveEvolutionCoordinator",
    "SystemicCoherenceSupervisor",
    "EvolutionAuditService",
    "AdaptationLineageTracker",
    "EvolutionDecision",
    "MutationEvaluation",
    "CoherenceAssessment",
    "AdaptationResult",
]
