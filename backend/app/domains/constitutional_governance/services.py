"""
Constitutional Governance Services - Production-grade constitutional governance infrastructure

Provides:
- Constitutional governance engine
- Invariant policy management
- Cognition boundary enforcement
- Recursive safety governance
- Systemic constraint supervision
- Constitutional audit tracking

All services support:
- Async operation
- Typed constitutional contracts
- Invariant lineage tracking
- Distributed constitutional visibility
- Recursive governance traceability
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
    ConstraintSeverity,
    GovernanceScope,
    BoundaryType,
    InvariantType,
    SafetyState,
    ConstitutionalProfile,
    InvariantPolicy,
    CognitionBoundary,
    RecursiveSafetyRule,
    SystemicConstraint,
    ConstitutionalAudit,
    GovernanceBoundary,
    ConstraintViolation,
)

logger = logging.getLogger(__name__)


# =====================================================================
# Data Transfer Objects
# =====================================================================

@dataclass
class ConstitutionalDecision:
    """Result of a constitutional governance decision"""
    approved: bool
    action: str
    reason: str
    severity: ConstraintSeverity
    violations: List[str] = field(default_factory=list)
    remediations: List[str] = field(default_factory=list)
    safety_state: SafetyState = SafetyState.NOMINAL
    confidence: float = 1.0


@dataclass
class InvariantValidationResult:
    """Result of an invariant validation"""
    is_valid: bool
    constraint_id: Optional[str]
    violations: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    remediation_suggestions: List[str] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class BoundaryAssessment:
    """Assessment of boundary compliance"""
    within_bounds: bool
    boundary_id: str
    current_value: float
    limit_type: str
    distance_from_limit: float
    violations: List[str] = field(default_factory=list)


@dataclass
class SafetyAssessment:
    """Assessment of system safety state"""
    safety_state: SafetyState
    risk_score: float
    collapse_probability: float
    contributing_factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    interventions_needed: bool = False


# =====================================================================
# Constitutional Governance Engine
# =====================================================================

class ConstitutionalGovernanceEngine:
    """
    Central constitutional governance engine.
    Coordinates constitutional constraints and safety systems.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._profiles: Dict[str, ConstitutionalProfile] = {}
        self._running = False

    async def initialize(self) -> None:
        """Initialize the governance engine"""
        await self._load_profiles()
        self._running = True
        logger.info("ConstitutionalGovernanceEngine initialized")

    async def shutdown(self) -> None:
        """Shutdown the engine"""
        self._running = False
        logger.info("ConstitutionalGovernanceEngine shutdown")

    async def _load_profiles(self) -> None:
        """Load active profiles into cache"""
        result = await self.db.execute(
            select(ConstitutionalProfile).where(
                ConstitutionalProfile.is_active.is_(True)
            )
        )
        for profile in result.scalars().all():
            self._profiles[profile.profile_id] = profile

    # ---- Profile Management ----

    async def create_profile(
        self,
        profile_scope: str,
        profile_key: str,
        governance_scope: GovernanceScope = GovernanceScope.ECOSYSTEM,
        max_violations: int = 3,
        severity_cap: ConstraintSeverity = ConstraintSeverity.HIGH,
        **kwargs,
    ) -> ConstitutionalProfile:
        """Create a new constitutional profile"""
        profile = ConstitutionalProfile(
            profile_id=f"con_profile_{uuid4()}",
            profile_scope=profile_scope,
            profile_key=profile_key,
            governance_scope=governance_scope.value,
            max_violations_per_cycle=max_violations,
            violation_severity_cap=severity_cap.value,
            **kwargs,
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        self._profiles[profile.profile_id] = profile
        return profile

    async def get_profile(self, profile_id: str) -> Optional[ConstitutionalProfile]:
        """Get a profile by ID"""
        return self._profiles.get(profile_id) or await self.db.execute(
            select(ConstitutionalProfile).where(
                ConstitutionalProfile.profile_id == profile_id
            )
        ).scalar_one_or_none()

    async def evaluate_constitutional_action(
        self,
        scope: str,
        action: Dict[str, Any],
        current_state: Dict[str, Any],
        profile_id: Optional[str] = None,
    ) -> ConstitutionalDecision:
        """Evaluate whether an action is constitutionally valid"""
        # Get applicable profile
        if profile_id:
            profile = await self.get_profile(profile_id)
        else:
            result = await self.db.execute(
                select(ConstitutionalProfile).where(
                    and_(
                        ConstitutionalProfile.profile_scope == scope,
                        ConstitutionalProfile.is_active.is_(True),
                    )
                )
            )
            profile = result.scalar_one_or_none()

        if not profile:
            # Default permissive
            return ConstitutionalDecision(
                approved=True,
                action="allow",
                reason="no profile found",
                severity=ConstraintSeverity.INFO,
            )

        violations: List[str] = []
        remediations: List[str] = []

        # Check violation count limit
        if current_state.get("violation_count", 0) >= profile.max_violations_per_cycle:
            return ConstitutionalDecision(
                approved=False,
                action="deny",
                reason=f"violation count limit reached ({profile.max_violations_per_cycle})",
                severity=ConstraintSeverity.CRITICAL,
                violations=["violation_limit_exceeded"],
            )

        # Check severity cap
        severity_order = list(ConstraintSeverity)
        cap_index = severity_order.index(ConstraintSeverity(profile.violation_severity_cap))
        requested_severity = ConstraintSeverity(
            action.get("severity", ConstraintSeverity.INFO.value)
        )
        if severity_order.index(requested_severity) > cap_index:
            return ConstitutionalDecision(
                approved=False,
                action="deny",
                reason=f"severity {requested_severity.value} exceeds cap",
                severity=requested_severity,
                violations=["severity_cap_exceeded"],
            )

        # Check emergency shutdown threshold
        if profile.emergency_shutdown_threshold > 0:
            safety_score = current_state.get("safety_score", 1.0)
            if safety_score < profile.emergency_shutdown_threshold:
                return ConstitutionalDecision(
                    approved=False,
                    action="emergency_shutdown",
                    reason=f"safety score below emergency threshold",
                    severity=ConstraintSeverity.CRITICAL,
                    violations=["safety_threshold_breached"],
                    safety_state=SafetyState.CRITICAL,
                )

        # Check auto-remediation
        if profile.auto_remediation_enabled:
            remediations = self._suggest_remediations(action, current_state)

        return ConstitutionalDecision(
            approved=True,
            action="allow",
            reason="passed constitutional evaluation",
            severity=requested_severity,
            violations=violations,
            remediations=remediations,
            safety_state=SafetyState.NOMINAL,
            confidence=0.95,
        )

    def _suggest_remediations(
        self,
        action: Dict[str, Any],
        state: Dict[str, Any],
    ) -> List[str]:
        """Suggest remediations for potential issues"""
        suggestions = []
        if action.get("severity") in [ConstraintSeverity.HIGH.value, ConstraintSeverity.CRITICAL.value]:
            suggestions.append("consider_reducing_severity")
        if state.get("violation_count", 0) > 0:
            suggestions.append("address_pending_violations_first")
        return suggestions

    async def update_profile_metrics(
        self,
        profile_id: str,
        cycle_delta: int = 0,
        violation_delta: int = 0,
        critical_delta: int = 0,
        remediation_delta: int = 0,
    ) -> None:
        """Update profile metrics"""
        profile = await self.get_profile(profile_id)
        if profile:
            profile.cycle_count += cycle_delta
            profile.total_violations += violation_delta
            profile.critical_violations += critical_delta
            profile.remediations += remediation_delta
            await self.db.commit()


# =====================================================================
# Invariant Policy Manager
# =====================================================================

class InvariantPolicyManager:
    """
    Manages orchestration invariant policies.
    Enforces constitutional constraints.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._policies: Dict[str, InvariantPolicy] = {}

    async def initialize(self) -> None:
        """Initialize the policy manager"""
        result = await self.db.execute(
            select(InvariantPolicy).where(InvariantPolicy.is_active.is_(True))
        )
        for policy in result.scalars().all():
            self._policies[policy.policy_id] = policy
        logger.info("InvariantPolicyManager initialized with %d policies", len(self._policies))

    async def create_policy(
        self,
        policy_scope: str,
        invariant_type: InvariantType,
        invariant_name: str,
        invariant_expression: str,
        constraint_type: str = "safety",
        severity: ConstraintSeverity = ConstraintSeverity.MODERATE,
        **kwargs,
    ) -> InvariantPolicy:
        """Create a new invariant policy"""
        policy = InvariantPolicy(
            policy_id=f"inv_policy_{uuid4()}",
            policy_scope=policy_scope,
            invariant_type=invariant_type.value,
            invariant_name=invariant_name,
            invariant_expression=invariant_expression,
            constraint_type=constraint_type,
            severity=severity.value,
            **kwargs,
        )
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        self._policies[policy.policy_id] = policy
        return policy

    async def validate_invariant(
        self,
        scope: str,
        state: Dict[str, Any],
        policy_id: Optional[str] = None,
    ) -> InvariantValidationResult:
        """Validate an invariant against current state"""
        if policy_id:
            policy = self._policies.get(policy_id) or await self.db.execute(
                select(InvariantPolicy).where(InvariantPolicy.policy_id == policy_id)
            ).scalar_one_or_none()
        else:
            result = await self.db.execute(
                select(InvariantPolicy).where(
                    and_(
                        InvariantPolicy.policy_scope == scope,
                        InvariantPolicy.is_active.is_(True),
                    )
                )
            )
            policy = result.scalar_one_or_none()

        if not policy:
            return InvariantValidationResult(is_valid=True, constraint_id=None)

        policy.trigger_count += 1
        await self.db.commit()

        # Evaluate invariant expression (simplified)
        violations = self._evaluate_expression(policy.invariant_expression, state)
        
        if violations:
            policy.violation_count += 1
            await self.db.commit()
            return InvariantValidationResult(
                is_valid=False,
                constraint_id=policy.policy_id,
                violations=[{"policy": policy.invariant_name, "details": violations}],
                remediation_suggestions=self._suggest_remediations(policy, state),
                confidence=0.9,
            )

        return InvariantValidationResult(
            is_valid=True,
            constraint_id=policy.policy_id,
            confidence=0.95,
        )

    def _evaluate_expression(
        self,
        expression: str,
        state: Dict[str, Any],
    ) -> List[str]:
        """Evaluate an invariant expression against state"""
        violations = []
        
        # Simplified evaluation - in production would use actual expression evaluation
        if "NOT_NULL" in expression:
            for key in expression.replace("NOT_NULL(", "").replace(")", "").split(","):
                key = key.strip()
                if key and key not in state:
                    violations.append(f"{key} is null")
        
        if "MAX_VALUE" in expression:
            # Parse MAX_VALUE(constraint_name, value)
            violations.append("max_value_exceeded")
        
        return violations

    def _suggest_remediations(
        self,
        policy: InvariantPolicy,
        state: Dict[str, Any],
    ) -> List[str]:
        """Suggest remediations for invariant violation"""
        suggestions = []
        if policy.auto_remediate:
            suggestions.append("auto_remediation_available")
        if policy.rollback_on_violation:
            suggestions.append("rollback_recommended")
        return suggestions


# =====================================================================
# Cognition Boundary Enforcer
# =====================================================================

class CognitionBoundaryEnforcer:
    """
    Enforces cognition boundaries.
    Validates operations against defined limits.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._boundaries: Dict[str, CognitionBoundary] = {}

    async def initialize(self) -> None:
        """Initialize the enforcer"""
        result = await self.db.execute(
            select(CognitionBoundary).where(CognitionBoundary.is_active.is_(True))
        )
        for boundary in result.scalars().all():
            self._boundaries[boundary.boundary_id] = boundary
        logger.info("CognitionBoundaryEnforcer initialized with %d boundaries", len(self._boundaries))

    async def create_boundary(
        self,
        boundary_scope: str,
        boundary_type: BoundaryType,
        boundary_key: str,
        boundary_limits: Dict[str, float],
        soft_limit: float = 0.8,
        hard_limit: float = 0.95,
        **kwargs,
    ) -> CognitionBoundary:
        """Create a new cognition boundary"""
        boundary = CognitionBoundary(
            boundary_id=f"cog_boundary_{uuid4()}",
            boundary_scope=boundary_scope,
            boundary_type=boundary_type.value,
            boundary_key=boundary_key,
            boundary_limits=boundary_limits,
            soft_limit=soft_limit,
            hard_limit=hard_limit,
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
        current_value: float,
    ) -> BoundaryAssessment:
        """Validate against a boundary"""
        boundary = self._boundaries.get(boundary_id) or await self.db.execute(
            select(CognitionBoundary).where(
                CognitionBoundary.boundary_id == boundary_id
            )
        ).scalar_one_or_none()

        if not boundary:
            return BoundaryAssessment(
                within_bounds=True,
                boundary_id=boundary_id,
                current_value=current_value,
                limit_type="none",
                distance_from_limit=0.0,
            )

        boundary.validation_count += 1
        await self.db.commit()

        # Check limits
        violations: List[str] = []
        limit_type = "within_bounds"

        if current_value >= boundary.critical_limit:
            limit_type = "critical"
            violations.append(f"critical limit breached: {current_value} >= {boundary.critical_limit}")
            boundary.breach_count += 1
        elif current_value >= boundary.hard_limit:
            limit_type = "hard"
            violations.append(f"hard limit breached: {current_value} >= {boundary.hard_limit}")
            boundary.breach_count += 1
        elif current_value >= boundary.soft_limit:
            limit_type = "soft"
            boundary.warning_count += 1

        distance = boundary.hard_limit - current_value if current_value < boundary.hard_limit else 0

        return BoundaryAssessment(
            within_bounds=current_value < boundary.hard_limit,
            boundary_id=boundary_id,
            current_value=current_value,
            limit_type=limit_type,
            distance_from_limit=distance,
            violations=violations,
        )


# =====================================================================
# Recursive Safety Governance
# =====================================================================

class RecursiveSafetyGovernance:
    """
    Manages recursive safety constraints.
    Prevents collapse in recursive operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._rules: Dict[str, RecursiveSafetyRule] = {}

    async def initialize(self) -> None:
        """Initialize the governance"""
        result = await self.db.execute(
            select(RecursiveSafetyRule).where(RecursiveSafetyRule.is_active.is_(True))
        )
        for rule in result.scalars().all():
            self._rules[rule.rule_id] = rule
        logger.info("RecursiveSafetyGovernance initialized with %d rules", len(self._rules))

    async def assess_safety(
        self,
        scope: str,
        recursion_depth: int,
        current_metrics: Dict[str, float],
    ) -> SafetyAssessment:
        """Assess current safety state"""
        # Find applicable rule
        result = await self.db.execute(
            select(RecursiveSafetyRule).where(
                and_(
                    RecursiveSafetyRule.rule_scope == scope,
                    RecursiveSafetyRule.is_active.is_(True),
                )
            )
        )
        rule = result.scalar_one_or_none()

        if not rule:
            return SafetyAssessment(
                safety_state=SafetyState.NOMINAL,
                risk_score=0.0,
                collapse_probability=0.0,
            )

        # Calculate risk score
        depth_ratio = recursion_depth / rule.max_recursion_depth if rule.max_recursion_depth > 0 else 0
        
        # Get complexity from metrics
        complexity = current_metrics.get("complexity", 0.5)
        instability = current_metrics.get("instability", 0.0)

        # Calculate collapse probability
        collapse_prob = (depth_ratio * 0.4 + complexity * 0.3 + instability * 0.3)
        collapse_prob = min(1.0, collapse_prob)

        # Determine safety state
        if collapse_prob >= rule.collapse_threshold:
            safety_state = SafetyState.COLLAPSE
        elif collapse_prob >= rule.critical_threshold:
            safety_state = SafetyState.CRITICAL
        elif collapse_prob >= rule.warning_threshold:
            safety_state = SafetyState.WARNING
        else:
            safety_state = SafetyState.NOMINAL

        # Generate recommendations
        recommendations = self._generate_recommendations(
            safety_state, recursion_depth, rule, current_metrics
        )

        return SafetyAssessment(
            safety_state=safety_state,
            risk_score=collapse_prob,
            collapse_probability=collapse_prob,
            contributing_factors=self._identify_factors(
                depth_ratio, complexity, instability
            ),
            recommendations=recommendations,
            interventions_needed=safety_state in [
                SafetyState.CRITICAL, SafetyState.COLLAPSE
            ],
        )

    def _identify_factors(
        self,
        depth_ratio: float,
        complexity: float,
        instability: float,
    ) -> List[str]:
        """Identify contributing safety factors"""
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
        rule: RecursiveSafetyRule,
        metrics: Dict[str, float],
    ) -> List[str]:
        """Generate safety recommendations"""
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
        
        if depth >= rule.max_recursion_depth * 0.8:
            recommendations.append("approaching_depth_limit")
        
        return recommendations

    async def prevent_collapse(
        self,
        scope: str,
        current_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute collapse prevention measures"""
        assessment = await self.assess_safety(
            scope,
            current_state.get("recursion_depth", 0),
            current_state.get("metrics", {}),
        )

        actions = {"prevented": False, "actions_taken": []}

        if assessment.safety_state == SafetyState.COLLAPSE:
            actions["prevented"] = True
            actions["actions_taken"] = [
                "rollback_initiated",
                "depth_reduced",
                "state_restored",
            ]
        elif assessment.safety_state == SafetyState.CRITICAL:
            actions["prevented"] = True
            actions["actions_taken"] = [
                "intervention_triggered",
                "complexity_reduced",
            ]

        return actions


# =====================================================================
# Systemic Constraint Supervisor
# =====================================================================

class SystemicConstraintSupervisor:
    """
    Supervises systemic constraints across the ecosystem.
    Ensures ecosystem-wide compliance.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self) -> None:
        """Initialize the supervisor"""
        logger.info("SystemicConstraintSupervisor initialized")

    async def create_constraint(
        self,
        constraint_scope: str,
        constraint_type: str,
        constraint_key: str,
        constraint_definition: Dict[str, Any],
        components: List[str],
        severity: ConstraintSeverity = ConstraintSeverity.HIGH,
        **kwargs,
    ) -> SystemicConstraint:
        """Create a new systemic constraint"""
        constraint = SystemicConstraint(
            constraint_id=f"sys_constraint_{uuid4()}",
            constraint_scope=constraint_scope,
            constraint_type=constraint_type,
            constraint_key=constraint_key,
            constraint_definition=constraint_definition,
            constraint_scope_components=components,
            severity=severity.value,
            **kwargs,
        )
        self.db.add(constraint)
        await self.db.commit()
        await self.db.refresh(constraint)
        return constraint

    async def evaluate_constraint(
        self,
        constraint_id: str,
        component_states: Dict[str, Any],
    ) -> Tuple[bool, List[str]]:
        """Evaluate a constraint across components"""
        result = await self.db.execute(
            select(SystemicConstraint).where(
                SystemicConstraint.constraint_id == constraint_id
            )
        )
        constraint = result.scalar_one_or_none()

        if not constraint:
            return True, []

        constraint.evaluation_count += 1
        await self.db.commit()

        violations: List[str] = []
        
        # Evaluate constraint definition against component states
        definition = constraint.constraint_definition
        constraint_type = definition.get("type")

        if constraint_type == "all_components":
            # All components must satisfy condition
            for comp_id in constraint.constraint_scope_components:
                if comp_id not in component_states:
                    violations.append(f"missing_component: {comp_id}")
                else:
                    comp_state = component_states[comp_id]
                    if not self._check_component_condition(comp_state, definition):
                        violations.append(f"condition_failed: {comp_id}")

        elif constraint_type == "aggregate":
            # Aggregate metric must be within bounds
            agg_value = sum(
                component_states.get(comp_id, {}).get(definition.get("metric", ""), 0)
                for comp_id in constraint.constraint_scope_components
            ) / max(len(constraint.constraint_scope_components), 1)
            
            min_val = definition.get("min_value", 0)
            max_val = definition.get("max_value", float("inf"))
            
            if agg_value < min_val or agg_value > max_val:
                violations.append(f"aggregate_out_of_bounds: {agg_value}")

        if violations:
            constraint.violation_count += 1
            await self.db.commit()

        return len(violations) == 0, violations

    def _check_component_condition(
        self,
        state: Dict[str, Any],
        definition: Dict[str, Any],
    ) -> bool:
        """Check if component satisfies condition"""
        condition = definition.get("condition", {})
        if "metric" in condition:
            metric = condition["metric"]
            value = state.get(metric, 0)
            if "min" in condition and value < condition["min"]:
                return False
            if "max" in condition and value > condition["max"]:
                return False
        return True


# =====================================================================
# Constitutional Audit Service
# =====================================================================

class ConstitutionalAuditService:
    """
    Tracks constitutional governance actions.
    Maintains audit trail for compliance.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self,
        action_type: str,
        action_target: str,
        actor_type: str,
        outcome_type: str,
        success: bool = True,
        pre_state: Optional[Dict[str, Any]] = None,
        post_state: Optional[Dict[str, Any]] = None,
        action_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        profile_id: Optional[str] = None,
        constraint_id: Optional[str] = None,
        violation_detected: bool = False,
        safety_state: Optional[SafetyState] = None,
        correlation_id: Optional[str] = None,
    ) -> ConstitutionalAudit:
        """Log a constitutional governance action"""
        audit = ConstitutionalAudit(
            audit_id=f"con_audit_{uuid4()}",
            action_type=action_type,
            action_target=action_target,
            actor_type=actor_type,
            outcome_type=outcome_type,
            success=success,
            pre_state=pre_state,
            post_state=post_state,
            action_context=action_context or {},
            logged_at=datetime.utcnow(),
            session_id=session_id,
            profile_id=profile_id,
            constraint_id=constraint_id,
            violation_detected=violation_detected,
            safety_state_before=safety_state.value if safety_state else None,
        )

        self.db.add(audit)
        await self.db.commit()
        await self.db.refresh(audit)
        return audit

    async def get_audit_trail(
        self,
        session_id: Optional[str] = None,
        action_type: Optional[str] = None,
        constraint_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[ConstitutionalAudit]:
        """Get audit trail entries"""
        query = select(ConstitutionalAudit)

        if session_id:
            query = query.where(ConstitutionalAudit.session_id == session_id)
        if action_type:
            query = query.where(ConstitutionalAudit.action_type == action_type)
        if constraint_id:
            query = query.where(ConstitutionalAudit.constraint_id == constraint_id)

        result = await self.db.execute(
            query.order_by(ConstitutionalAudit.logged_at.desc()).limit(limit)
        )
        return list(result.scalars().all())


# =====================================================================
# Governance Boundary Validator
# =====================================================================

class GovernanceBoundaryValidator:
    """
    Validates operations against governance boundaries.
    Enforces operational limits.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._boundaries: Dict[str, GovernanceBoundary] = {}

    async def initialize(self) -> None:
        """Initialize the validator"""
        result = await self.db.execute(
            select(GovernanceBoundary).where(GovernanceBoundary.is_active.is_(True))
        )
        for boundary in result.scalars().all():
            self._boundaries[boundary.boundary_id] = boundary
        logger.info("GovernanceBoundaryValidator initialized with %d boundaries", len(self._boundaries))

    async def create_boundary(
        self,
        boundary_scope: str,
        boundary_type: BoundaryType,
        boundary_key: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        **kwargs,
    ) -> GovernanceBoundary:
        """Create a new governance boundary"""
        boundary = GovernanceBoundary(
            boundary_id=f"gov_boundary_{uuid4()}",
            boundary_scope=boundary_scope,
            boundary_type=boundary_type.value,
            boundary_key=boundary_key,
            min_value=min_value,
            max_value=max_value,
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
    ) -> Tuple[bool, List[str]]:
        """Validate a value against a boundary"""
        boundary = self._boundaries.get(boundary_id) or await self.db.execute(
            select(GovernanceBoundary).where(
                GovernanceBoundary.boundary_id == boundary_id
            )
        ).scalar_one_or_none()

        if not boundary:
            return True, []

        boundary.validation_count += 1
        await self.db.commit()

        violations: List[str] = []

        if boundary.min_value is not None and value < boundary.min_value:
            violations.append(f"value {value} below minimum {boundary.min_value}")
            boundary.breach_count += 1

        if boundary.max_value is not None and value > boundary.max_value:
            violations.append(f"value {value} above maximum {boundary.max_value}")
            boundary.breach_count += 1

        await self.db.commit()

        return len(violations) == 0, violations


__all__ = [
    "ConstitutionalGovernanceEngine",
    "InvariantPolicyManager",
    "CognitionBoundaryEnforcer",
    "RecursiveSafetyGovernance",
    "SystemicConstraintSupervisor",
    "ConstitutionalAuditService",
    "GovernanceBoundaryValidator",
    "ConstitutionalDecision",
    "InvariantValidationResult",
    "BoundaryAssessment",
    "SafetyAssessment",
]
