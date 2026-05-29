"""
Constitutional Governance API Endpoints

Production-grade constitutional governance, invariant enforcement, and safety
system endpoints for the 43V3R CORE platform.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.deps import get_current_user, get_optional_user

from app.domains.constitutional_governance import (
    ConstitutionalGovernanceEngine,
    InvariantPolicyManager,
    CognitionBoundaryEnforcer,
    RecursiveSafetyGovernance,
    SystemicConstraintSupervisor,
    ConstitutionalAuditService,
    GovernanceBoundaryValidator,
)
from app.domains.constitutional_governance.models import (
    ConstraintSeverity,
    GovernanceScope,
    SafetyState,
)
from app.domains.invariant_enforcement import (
    InvariantEnforcementRuntime,
    ConstraintLineageTracker,
    ConsistencyValidator,
    IntegrityMonitor,
)
from app.domains.invariant_enforcement.models import (
    InvariantType,
    ViolationSeverity,
)
from app.domains.recursive_safety import (
    RecursiveSafetyEngine,
    SafetyBoundaryManager,
    CollapsePreventionSystem,
    GovernanceConflictResolver,
    StabilityCoordinator,
)
from app.domains.recursive_safety.models import (
    SafetyState as RecursiveSafetyState,
    ProtectionLevel,
)
from app.domains.constitutional_arbitration import (
    ConstitutionalArbitrationEngine,
    ReconciliationPolicyManager,
    ConstitutionalLineageTracker,
    EcosystemCoherenceValidator,
)
from app.domains.constitutional_arbitration.models import (
    ArbitrationStrategy,
    ReconciliationState,
)

router = APIRouter(prefix="/constitutional", tags=["constitutional"])


# =====================================================================
# CONSTITUTIONAL GOVERNANCE ENDPOINTS
# =====================================================================

@router.post("/profiles")
async def create_constitutional_profile(
    profile_scope: str,
    profile_key: str,
    governance_scope: str = "ecosystem",
    max_violations: int = 3,
    severity_cap: str = "high",
    db: AsyncSession = Depends(get_async_db),
):
    """Create a constitutional profile"""
    engine = ConstitutionalGovernanceEngine(db)
    profile = await engine.create_profile(
        profile_scope=profile_scope,
        profile_key=profile_key,
        governance_scope=GovernanceScope(governance_scope),
        max_violations=max_violations,
        severity_cap=ConstraintSeverity(severity_cap),
    )
    await db.commit()
    return {"profile_id": profile.profile_id, "status": "created"}


@router.get("/profiles/{profile_id}")
async def get_constitutional_profile(
    profile_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a constitutional profile"""
    engine = ConstitutionalGovernanceEngine(db)
    profile = await engine.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "profile_id": profile.profile_id,
        "profile_scope": profile.profile_scope,
        "governance_scope": profile.governance_scope,
        "cycle_count": profile.cycle_count,
        "total_violations": profile.total_violations,
    }


@router.post("/evaluate")
async def evaluate_constitutional_action(
    scope: str,
    action: Dict[str, Any],
    current_state: Dict[str, Any],
    profile_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Evaluate a constitutionally action"""
    engine = ConstitutionalGovernanceEngine(db)
    decision = await engine.evaluate_constitutional_action(
        scope=scope,
        action=action,
        current_state=current_state,
        profile_id=profile_id,
    )
    return {
        "approved": decision.approved,
        "action": decision.action,
        "reason": decision.reason,
        "severity": decision.severity.value,
        "violations": decision.violations,
        "safety_state": decision.safety_state.value,
    }


@router.post("/invariant-policies")
async def create_invariant_policy(
    policy_scope: str,
    invariant_type: str,
    invariant_name: str,
    invariant_expression: str,
    constraint_type: str = "safety",
    severity: str = "moderate",
    db: AsyncSession = Depends(get_async_db),
):
    """Create an invariant policy"""
    manager = InvariantPolicyManager(db)
    policy = await manager.create_policy(
        policy_scope=policy_scope,
        invariant_type=InvariantType(invariant_type),
        invariant_name=invariant_name,
        invariant_expression=invariant_expression,
        constraint_type=constraint_type,
        severity=ViolationSeverity(severity),
    )
    await db.commit()
    return {"policy_id": policy.policy_id, "status": "created"}


@router.post("/validate-invariant")
async def validate_invariant(
    scope: str,
    state: Dict[str, Any],
    policy_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Validate an invariant"""
    manager = InvariantPolicyManager(db)
    result = await manager.validate_invariant(scope, state, policy_id)
    return {
        "is_valid": result.is_valid,
        "constraint_id": result.constraint_id,
        "violations": result.violations,
        "confidence": result.confidence,
    }


@router.post("/cognition-boundaries")
async def create_cognition_boundary(
    boundary_scope: str,
    boundary_type: str,
    boundary_key: str,
    boundary_limits: Dict[str, float],
    soft_limit: float = 0.8,
    hard_limit: float = 0.95,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a cognition boundary"""
    enforcer = CognitionBoundaryEnforcer(db)
    boundary = await enforcer.create_boundary(
        boundary_scope=boundary_scope,
        boundary_type=boundary_type,
        boundary_key=boundary_key,
        boundary_limits=boundary_limits,
        soft_limit=soft_limit,
        hard_limit=hard_limit,
    )
    await db.commit()
    return {"boundary_id": boundary.boundary_id, "status": "created"}


@router.post("/validate-boundary/{boundary_id}")
async def validate_cognition_boundary(
    boundary_id: str,
    current_value: float,
    db: AsyncSession = Depends(get_async_db),
):
    """Validate against a cognition boundary"""
    enforcer = CognitionBoundaryEnforcer(db)
    result = await enforcer.validate_boundary(boundary_id, current_value)
    return {
        "within_bounds": result.within_bounds,
        "limit_type": result.limit_type,
        "distance_from_limit": result.distance_from_limit,
        "violations": result.violations,
    }


@router.post("/safety-assessment")
async def assess_recursive_safety(
    scope: str,
    recursion_depth: int,
    current_metrics: Dict[str, float],
    db: AsyncSession = Depends(get_async_db),
):
    """Assess recursive safety state"""
    governance = RecursiveSafetyGovernance(db)
    assessment = await governance.assess_safety(scope, recursion_depth, current_metrics)
    return {
        "safety_state": assessment.safety_state.value,
        "risk_score": assessment.risk_score,
        "collapse_probability": assessment.collapse_probability,
        "contributing_factors": assessment.contributing_factors,
        "recommendations": assessment.recommendations,
        "interventions_needed": assessment.interventions_needed,
    }


@router.post("/prevent-collapse")
async def prevent_collapse(
    scope: str,
    current_state: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db),
):
    """Execute collapse prevention"""
    governance = RecursiveSafetyGovernance(db)
    result = await governance.prevent_collapse(scope, current_state)
    return result


@router.post("/systemic-constraints")
async def create_systemic_constraint(
    constraint_scope: str,
    constraint_type: str,
    constraint_key: str,
    constraint_definition: Dict[str, Any],
    components: List[str],
    severity: str = "high",
    db: AsyncSession = Depends(get_async_db),
):
    """Create a systemic constraint"""
    supervisor = SystemicConstraintSupervisor(db)
    constraint = await supervisor.create_constraint(
        constraint_scope=constraint_scope,
        constraint_type=constraint_type,
        constraint_key=constraint_key,
        constraint_definition=constraint_definition,
        components=components,
        severity=ConstraintSeverity(severity),
    )
    await db.commit()
    return {"constraint_id": constraint.constraint_id, "status": "created"}


@router.get("/audit-trail")
async def get_constitutional_audit_trail(
    session_id: Optional[str] = None,
    action_type: Optional[str] = None,
    constraint_id: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
):
    """Get constitutional audit trail"""
    service = ConstitutionalAuditService(db)
    audits = await service.get_audit_trail(session_id, action_type, constraint_id, limit)
    return {
        "audits": [
            {
                "audit_id": a.audit_id,
                "action_type": a.action_type,
                "success": a.success,
                "logged_at": a.logged_at.isoformat(),
            }
            for a in audits
        ],
        "count": len(audits),
    }


# =====================================================================
# INVARIANT ENFORCEMENT ENDPOINTS
# =====================================================================

@router.post("/invariants")
async def register_invariant(
    invariant_scope: str,
    invariant_type: str,
    invariant_name: str,
    expression: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Register an invariant"""
    runtime = InvariantEnforcementRuntime(db)
    invariant = await runtime.register_invariant(
        invariant_scope=invariant_scope,
        invariant_type=InvariantType(invariant_type),
        invariant_name=invariant_name,
        expression=expression,
    )
    await db.commit()
    return {"invariant_id": invariant.invariant_id, "status": "registered"}


@router.post("/invariants/{invariant_id}/validate")
async def validate_invariant_runtime(
    invariant_id: str,
    state: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db),
):
    """Validate invariant against state"""
    runtime = InvariantEnforcementRuntime(db)
    result = await runtime.validate_invariant(invariant_id, state)
    return {
        "is_valid": result.is_valid,
        "violations": result.violations,
        "confidence": result.confidence,
    }


@router.post("/consistency-assessment")
async def assess_consistency(
    session_id: str,
    lineage_id: str,
    component_states: Dict[str, Any],
    invariants: List[str],
    db: AsyncSession = Depends(get_async_db),
):
    """Assess consistency across components"""
    validator = ConsistencyValidator(db)
    assessment = await validator.assess_consistency(
        session_id, lineage_id, component_states, invariants
    )
    return {
        "is_consistent": assessment.is_consistent,
        "consistency_score": assessment.consistency_score,
        "violations": assessment.violations,
        "recommendations": assessment.recommendations,
    }


# =====================================================================
# RECURSIVE SAFETY ENDPOINTS
# =====================================================================

@router.post("/safety-profiles")
async def create_safety_profile(
    profile_scope: str,
    profile_key: str,
    protection_level: str = "standard",
    db: AsyncSession = Depends(get_async_db),
):
    """Create a safety profile"""
    engine = RecursiveSafetyEngine(db)
    profile = await engine.create_profile(
        profile_scope=profile_scope,
        profile_key=profile_key,
        protection_level=ProtectionLevel(protection_level),
    )
    await db.commit()
    return {"profile_id": profile.profile_id, "status": "created"}


@router.post("/safety-assessment")
async def assess_safety_state(
    scope: str,
    recursion_depth: int,
    current_metrics: Dict[str, float],
    db: AsyncSession = Depends(get_async_db),
):
    """Assess safety state"""
    engine = RecursiveSafetyEngine(db)
    assessment = await engine.assess_safety(scope, recursion_depth, current_metrics)
    return {
        "safety_state": assessment.safety_state.value,
        "risk_score": assessment.risk_score,
        "recommendations": assessment.recommendations,
        "interventions_needed": assessment.interventions_needed,
    }


@router.post("/stability-sessions")
async def create_stability_session(
    session_scope: str,
    scope_kind: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a stability session"""
    coordinator = StabilityCoordinator(db)
    session = await coordinator.create_session(session_scope, scope_kind)
    await db.commit()
    return {"session_id": session.session_id, "started_at": session.started_at.isoformat()}


@router.post("/governance-conflicts")
async def detect_governance_conflict(
    session_id: str,
    lineage_id: str,
    conflict_type: str,
    conflicting_rules: List[str],
    rule_priorities: Optional[Dict[str, int]] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Detect a governance conflict"""
    resolver = GovernanceConflictResolver(db)
    conflict = await resolver.detect_conflict(
        session_id=session_id,
        lineage_id=lineage_id,
        conflict_type=conflict_type,
        conflicting_rules=conflicting_rules,
        rule_priorities=rule_priorities,
    )
    await db.commit()
    return {"conflict_id": conflict.conflict_id, "status": "detected"}


# =====================================================================
# CONSTITUTIONAL ARBITRATION ENDPOINTS
# =====================================================================

@router.post("/arbitration-sessions")
async def create_arbitration_session(
    session_scope: str,
    scope_kind: str,
    strategy: str = "recursive",
    max_depth: int = 10,
    db: AsyncSession = Depends(get_async_db),
):
    """Create an arbitration session"""
    engine = ConstitutionalArbitrationEngine(db)
    session = await engine.create_session(
        session_scope=session_scope,
        scope_kind=scope_kind,
        strategy=ArbitrationStrategy(strategy),
        max_depth=max_depth,
    )
    await db.commit()
    return {"session_id": session.session_id, "started_at": session.started_at.isoformat()}


@router.post("/arbitration-sessions/{session_id}/arbitrate")
async def arbitrate_policies(
    session_id: str,
    conflicting_policies: List[str],
    policy_scores: Dict[str, float],
    db: AsyncSession = Depends(get_async_db),
):
    """Arbitrate between conflicting policies"""
    engine = ConstitutionalArbitrationEngine(db)
    result = await engine.arbitrate(session_id, conflicting_policies, policy_scores)
    return {
        "decision_type": result.decision_type,
        "selected_policy": result.selected_policy,
        "rejected_policies": result.rejected_policies,
        "coherence_impact": result.coherence_impact,
        "success": result.success,
    }


@router.post("/ecosystem-coherence")
async def assess_ecosystem_coherence(
    component_states: Dict[str, str],
    policy_states: Dict[str, bool],
    db: AsyncSession = Depends(get_async_db),
):
    """Assess ecosystem coherence"""
    validator = EcosystemCoherenceValidator(db)
    assessment = await validator.assess_coherence(component_states, policy_states)
    return {
        "is_coherent": assessment.is_coherent,
        "coherence_score": assessment.coherence_score,
        "stability_score": assessment.stability_score,
        "balance_score": assessment.balance_score,
        "violations": assessment.violations,
    }


@router.post("/reconciliation-policies")
async def create_reconciliation_policy(
    policy_scope: str,
    policy_type: str,
    policy_key: str,
    default_strategy: str = "priority",
    db: AsyncSession = Depends(get_async_db),
):
    """Create a reconciliation policy"""
    manager = ReconciliationPolicyManager(db)
    policy = await manager.create_policy(
        policy_scope=policy_scope,
        policy_type=policy_type,
        policy_key=policy_key,
        default_strategy=ArbitrationStrategy(default_strategy),
    )
    await db.commit()
    return {"policy_id": policy.policy_id, "status": "created"}


__all__ = ["router"]
