"""
Evolution API Endpoints

Production-grade evolution governance, mutation tracking, and adaptive
arbitration endpoints for the 43V3R CORE platform.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.deps import get_current_user, get_current_user_optional as get_optional_user

from app.domains.evolution_governance import (
    EvolutionGovernanceEngine,
    MutationPolicyManager,
    CognitionAdaptationController,
    SemanticContinuityValidator,
    RecursiveEvolutionCoordinator,
    SystemicCoherenceSupervisor,
    EvolutionAuditService,
    AdaptationLineageTracker,
)
from app.domains.evolution_governance.models import (
    EvolutionStage,
    CoherenceState,
    AdaptationStrategy,
    MutationSeverity,
    GovernanceLevel,
)
from app.domains.mutation_tracking import (
    MutationLineageTracker,
    CognitionEvolutionTracer,
    SemanticAdaptationHistory,
    RuntimeBehaviorEvolutionTracker,
    RecursiveAdaptationTelemetryService,
    DistributedMutationCoordinator,
    MutationLineageGraphBuilder,
)
from app.domains.mutation_tracking.models import (
    MutationStatus,
    AdaptationPhase,
    EvolutionTrajectory,
)
from app.domains.adaptive_arbitration import (
    AdaptationArbitrationEngine,
    RecursiveBalancingSystem,
    SemanticEvolutionReconciler,
    OrchestrationAdaptationGovernor,
    SystemicEvolutionStabilizer,
)
from app.domains.adaptive_arbitration.models import (
    BalanceStrategy,
    ArbitrationScope,
    ReconciliationState,
)

router = APIRouter(prefix="/evolution", tags=["evolution"])


# =====================================================================
# EVOLUTION GOVERNANCE ENDPOINTS
# =====================================================================

@router.post("/profiles")
async def create_evolution_profile(
    profile_scope: str,
    profile_key: str,
    governance_level: str = "intervention",
    adaptation_strategy: str = "balanced",
    coherence_target: float = 0.85,
    mutation_severity_cap: str = "moderate",
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_optional_user),
):
    """Create a new evolution profile"""
    engine = EvolutionGovernanceEngine(db)
    profile = await engine.create_profile(
        profile_scope=profile_scope,
        profile_key=profile_key,
        governance_level=GovernanceLevel(governance_level),
        adaptation_strategy=AdaptationStrategy(adaptation_strategy),
        coherence_target=coherence_target,
        mutation_severity_cap=MutationSeverity(mutation_severity_cap),
    )
    await db.commit()
    return {"profile_id": profile.profile_id, "status": "created"}


@router.get("/profiles/{profile_id}")
async def get_evolution_profile(
    profile_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Get an evolution profile"""
    engine = EvolutionGovernanceEngine(db)
    profile = await engine.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "profile_id": profile.profile_id,
        "profile_scope": profile.profile_scope,
        "governance_level": profile.governance_level,
        "adaptation_strategy": profile.adaptation_strategy,
        "coherence_target": profile.coherence_target,
        "cycle_count": profile.cycle_count,
        "is_active": profile.is_active,
    }


@router.post("/evaluate")
async def evaluate_evolution(
    scope: str,
    mutations: List[Dict[str, Any]],
    coherence_snapshot: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Evaluate whether evolution is permitted"""
    engine = EvolutionGovernanceEngine(db)
    decision = await engine.evaluate_evolution(
        scope=scope,
        mutations=mutations,
        actor_ctx={},
        coherence_snapshot=coherence_snapshot,
    )
    return {
        "approved": decision.approved,
        "action": decision.action,
        "reason": decision.reason,
        "severity": decision.severity,
        "warnings": decision.warnings,
        "mutations_suggested": decision.mutations_suggested,
    }


@router.post("/mutation-policies")
async def create_mutation_policy(
    policy_domain: str,
    policy_key: str,
    allowed_mutations: List[str],
    min_severity: str = "trivial",
    max_severity: str = "critical",
    requires_approval: bool = False,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a mutation policy"""
    manager = MutationPolicyManager(db)
    policy = await manager.create_policy(
        policy_domain=policy_domain,
        policy_key=policy_key,
        allowed_mutations=allowed_mutations,
        min_severity=MutationSeverity(min_severity),
        max_severity=MutationSeverity(max_severity),
        requires_approval=requires_approval,
    )
    await db.commit()
    return {"policy_id": policy.policy_id, "status": "created"}


@router.post("/mutation-policies/evaluate")
async def evaluate_mutation(
    mutation: Dict[str, Any],
    domain: str,
    kind: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Evaluate a mutation against policies"""
    manager = MutationPolicyManager(db)
    result = await manager.evaluate_mutation(mutation, domain, kind)
    return {
        "mutation_id": result.mutation_id,
        "approved": result.approved,
        "severity": result.severity.value,
        "risk_score": result.risk_score,
        "warnings": result.warnings,
    }


@router.post("/cognition-adaptation/evaluate")
async def evaluate_cognition_adaptation(
    reasoning_type: str,
    domain: str,
    current_state: Dict[str, Any],
    target_state: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db),
):
    """Evaluate a cognition adaptation"""
    controller = CognitionAdaptationController(db)
    result = await controller.evaluate_adaptation(
        reasoning_type=reasoning_type,
        domain=domain,
        current_state=current_state,
        target_state=target_state,
    )
    return {
        "adaptation_id": result.adaptation_id,
        "approved": result.approved,
        "rollback_required": result.rollback_required,
        "coherence_impact": result.coherence_impact,
    }


@router.post("/semantic-continuity/validate")
async def validate_semantic_continuity(
    scope: str,
    state: Dict[str, Any],
    contracts: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Validate semantic continuity for a scope"""
    validator = SemanticContinuityValidator(db)
    assessment = await validator.validate_invariants(scope, state, contracts)
    return {
        "is_coherent": assessment.is_coherent,
        "coherence_score": assessment.coherence_score,
        "coherence_state": assessment.coherence_state.value,
        "contract_violations": assessment.contract_violations,
        "recommendations": assessment.recommendations,
    }


@router.post("/recursive-sessions")
async def create_recursive_session(
    session_scope: str,
    governance_level: str = "intervention",
    strategy: str = "recursive",
    max_depth: int = 10,
    parent_session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a recursive evolution session"""
    coordinator = RecursiveEvolutionCoordinator(db)
    session = await coordinator.create_session(
        session_scope=session_scope,
        governance_level=GovernanceLevel(governance_level),
        strategy=AdaptationStrategy(strategy),
        max_depth=max_depth,
        parent_session_id=UUID(parent_session_id) if parent_session_id else None,
    )
    await db.commit()
    return {
        "session_id": session.session_id,
        "recursion_depth": session.recursion_depth,
        "session_state": session.session_state,
    }


@router.post("/recursive-sessions/{session_id}/advance")
async def advance_recursive_session(
    session_id: str,
    mutations: List[Dict[str, Any]],
    metrics: Optional[Dict[str, float]] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Advance a recursive session"""
    coordinator = RecursiveEvolutionCoordinator(db)
    session = await coordinator.advance_session(session_id, mutations, metrics)
    await db.commit()
    return {
        "session_id": session.session_id,
        "cycle_count": session.cycle_count,
        "mutations_applied": session.mutations_applied,
        "coherence_score": session.coherence_score,
    }


@router.post("/recursive-sessions/{session_id}/complete")
async def complete_recursive_session(
    session_id: str,
    final_metrics: Optional[Dict[str, float]] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Complete a recursive session"""
    coordinator = RecursiveEvolutionCoordinator(db)
    session = await coordinator.complete_session(session_id, final_metrics)
    await db.commit()
    return {
        "session_id": session.session_id,
        "session_state": session.session_state,
        "duration_seconds": session.duration_seconds,
        "mutations_successful": session.mutations_successful,
    }


@router.post("/coherence-snapshots")
async def capture_coherence_snapshot(
    snapshot_key: str,
    coherence_metrics: Dict[str, float],
    component_states: Dict[str, str],
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Capture a coherence snapshot"""
    supervisor = SystemicCoherenceSupervisor(db)
    snapshot = await supervisor.capture_snapshot(
        snapshot_key=snapshot_key,
        coherence_metrics=coherence_metrics,
        component_states=component_states,
        session_id=session_id,
    )
    await db.commit()
    return {"snapshot_id": snapshot.snapshot_id, "coherence_score": snapshot.coherence_score}


@router.get("/coherence-assessment")
async def assess_systemic_coherence(
    scope: Optional[str] = None,
    window_seconds: int = 300,
    db: AsyncSession = Depends(get_async_db),
):
    """Assess current systemic coherence"""
    supervisor = SystemicCoherenceSupervisor(db)
    assessment = await supervisor.assess_systemic_coherence(scope, window_seconds)
    return {
        "is_coherent": assessment.is_coherent,
        "coherence_score": assessment.coherence_score,
        "coherence_state": assessment.coherence_state.value,
        "drift_sources": assessment.drift_sources,
        "recommendations": assessment.recommendations,
    }


# =====================================================================
# MUTATION TRACKING ENDPOINTS
# =====================================================================

@router.post("/mutations")
async def record_mutation(
    lineage_id: str,
    subject_kind: str,
    subject_key: str,
    mutation_type: str,
    pre_state: Dict[str, Any],
    post_state: Dict[str, Any],
    severity: str = "minor",
    parent_mutation_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Record a mutation event"""
    tracker = MutationLineageTracker(db)
    mutation = await tracker.record_mutation(
        lineage_id=lineage_id,
        subject_kind=subject_kind,
        subject_key=subject_key,
        mutation_type=mutation_type,
        pre_state=pre_state,
        post_state=post_state,
        severity=MutationSeverity(severity),
        parent_mutation_id=parent_mutation_id,
    )
    await db.commit()
    return {"mutation_id": mutation.mutation_id, "status": mutation.mutation_status}


@router.get("/mutations/{mutation_id}")
async def get_mutation(
    mutation_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Get mutation details"""
    tracker = MutationLineageTracker(db)
    mutation = await tracker._get_mutation(mutation_id)
    if not mutation:
        raise HTTPException(status_code=404, detail="Mutation not found")
    return {
        "mutation_id": mutation.mutation_id,
        "lineage_id": mutation.lineage_id,
        "mutation_type": mutation.mutation_type,
        "severity": mutation.severity,
        "status": mutation.mutation_status,
        "impact_score": mutation.impact_score,
        "risk_score": mutation.risk_score,
        "lineage_depth": mutation.lineage_depth,
    }


@router.get("/lineages/{lineage_id}")
async def get_lineage(
    lineage_id: str,
    include_reverted: bool = False,
    db: AsyncSession = Depends(get_async_db),
):
    """Get all mutations in a lineage"""
    tracker = MutationLineageTracker(db)
    mutations = await tracker.get_lineage(lineage_id, include_reverted)
    return {
        "lineage_id": lineage_id,
        "mutations": [
            {
                "mutation_id": m.mutation_id,
                "mutation_type": m.mutation_type,
                "severity": m.severity,
                "status": m.mutation_status,
                "proposed_at": m.proposed_at.isoformat(),
            }
            for m in mutations
        ],
        "count": len(mutations),
    }


@router.post("/mutations/{mutation_id}/update-status")
async def update_mutation_status(
    mutation_id: str,
    status: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Update mutation status"""
    tracker = MutationLineageTracker(db)
    mutation = await tracker.update_status(mutation_id, MutationStatus(status))
    await db.commit()
    return {"mutation_id": mutation.mutation_id, "status": mutation.mutation_status}


@router.post("/mutations/{mutation_id}/revert")
async def revert_mutation(
    mutation_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Revert a mutation"""
    tracker = MutationLineageTracker(db)
    mutation = await tracker.revert_mutation(mutation_id)
    await db.commit()
    return {"mutation_id": mutation.mutation_id, "is_reverted": mutation.is_reverted}


@router.post("/cognition-traces")
async def record_cognition_trace(
    lineage_id: str,
    reasoning_type: str,
    domain: str,
    cognition_state: Dict[str, Any],
    reasoning_context: Dict[str, Any],
    coherence_before: float = 1.0,
    coherence_after: float = 1.0,
    phase: str = "observation",
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Record a cognition trace"""
    tracer = CognitionEvolutionTracer(db)
    trace = await tracer.record_cognition_trace(
        lineage_id=lineage_id,
        reasoning_type=reasoning_type,
        domain=domain,
        cognition_state=cognition_state,
        reasoning_context=reasoning_context,
        coherence_before=coherence_before,
        coherence_after=coherence_after,
        phase=AdaptationPhase(phase),
        session_id=session_id,
    )
    await db.commit()
    return {"trace_id": trace.trace_id, "trajectory": trace.trajectory}


@router.get("/cognition-traces/session/{session_id}/trend")
async def get_cognition_trend(
    session_id: str,
    window_minutes: int = 60,
    db: AsyncSession = Depends(get_async_db),
):
    """Get cognition evolution trend"""
    tracer = CognitionEvolutionTracer(db)
    trend = await tracer.calculate_evolution_trend(session_id, window_minutes)
    return trend


@router.post("/lineage-graphs")
async def build_lineage_graph(
    lineage_id: str,
    subject_kind: str,
    subject_key: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Build a lineage graph"""
    builder = MutationLineageGraphBuilder(db)
    try:
        graph = await builder.build_graph(lineage_id, subject_kind, subject_key)
        await db.commit()
        return {
            "graph_id": graph.graph_id,
            "node_count": graph.node_count,
            "edge_count": graph.edge_count,
            "max_depth": graph.max_depth,
            "coherence_score": graph.coherence_score,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# =====================================================================
# ADAPTIVE ARBITRATION ENDPOINTS
# =====================================================================

@router.post("/arbitration-sessions")
async def create_arbitration_session(
    scope_kind: str,
    scope_id: Optional[str] = None,
    strategy: str = "adaptive",
    max_depth: int = 10,
    parent_session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Create an arbitration session"""
    engine = AdaptationArbitrationEngine(db)
    session = await engine.create_session(
        scope_kind=scope_kind,
        scope_id=scope_id,
        strategy=BalanceStrategy(strategy),
        max_depth=max_depth,
        parent_session_id=parent_session_id,
    )
    await db.commit()
    return {
        "session_id": session.session_id,
        "recursion_depth": session.recursion_depth,
        "balance_strategy": session.balance_strategy,
    }


@router.post("/arbitration-sessions/{session_id}/arbitrate")
async def arbitrate(
    session_id: str,
    conflicting_adaptations: List[str],
    session_state: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db),
):
    """Arbitrate between conflicting adaptations"""
    engine = AdaptationArbitrationEngine(db)
    result = await engine.arbitrate(session_id, conflicting_adaptations, session_state)
    await db.commit()
    return {
        "session_id": result.session_id,
        "decision": result.decision,
        "selected_adaptations": result.selected_adaptations,
        "rejected_adaptations": result.rejected_adaptations,
        "coherence_impact": result.coherence_impact,
        "confidence": result.confidence,
    }


@router.post("/balance-snapshots")
async def capture_balance_snapshot(
    session_id: str,
    lineage_id: str,
    balance_scope: str,
    component_states: Dict[str, float],
    strategy: str = "adaptive",
    target_balance: Optional[Dict[str, float]] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Capture a balance snapshot"""
    balancer = RecursiveBalancingSystem(db)
    balance = await balancer.capture_balance(
        session_id=session_id,
        lineage_id=lineage_id,
        balance_scope=balance_scope,
        component_states=component_states,
        strategy=BalanceStrategy(strategy),
        target_balance=target_balance,
    )
    await db.commit()
    return {"balance_id": balance.balance_id, "imbalance_score": balance.imbalance_score}


@router.get("/balance-assessment/{session_id}")
async def assess_balance(
    session_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Assess current balance state"""
    balancer = RecursiveBalancingSystem(db)
    assessment = await balancer.assess_balance(session_id)
    return {
        "is_balanced": assessment.is_balanced,
        "imbalance_score": assessment.imbalance_score,
        "deviation_sources": assessment.deviation_sources,
        "redistribution_plan": assessment.redistribution_plan,
        "tolerance_met": assessment.tolerance_met,
    }


@router.post("/semantic-reconciliation")
async def reconcile_semantic(
    session_id: str,
    lineage_id: str,
    subject_kind: str,
    subject_key: str,
    pre_state: Dict[str, Any],
    post_state: Dict[str, Any],
    reconciliation_type: str = "merge",
    db: AsyncSession = Depends(get_async_db),
):
    """Reconcile semantic states"""
    reconciler = SemanticEvolutionReconciler(db)
    reconciliation = await reconciler.reconcile(
        session_id=session_id,
        lineage_id=lineage_id,
        subject_kind=subject_kind,
        subject_key=subject_key,
        pre_state=pre_state,
        post_state=post_state,
        reconciliation_type=reconciliation_type,
    )
    await db.commit()
    return {
        "reconciliation_id": reconciliation.reconciliation_id,
        "convergence_achieved": reconciliation.convergence_achieved,
        "conflicts_resolved": reconciliation.conflicts_resolved,
        "reconciliation_state": reconciliation.reconciliation_state,
    }


@router.post("/orchestration-adaptations")
async def create_orchestration_adaptation(
    session_id: str,
    lineage_id: str,
    subject_kind: str,
    subject_key: str,
    adaptation_type: str,
    pre_state: Dict[str, Any],
    post_state: Dict[str, Any],
    governance_level: str = "intervention",
    requires_approval: bool = True,
    db: AsyncSession = Depends(get_async_db),
):
    """Create an orchestrated adaptation"""
    governor = OrchestrationAdaptationGovernor(db)
    adaptation = await governor.create_adaptation(
        session_id=session_id,
        lineage_id=lineage_id,
        subject_kind=subject_kind,
        subject_key=subject_key,
        adaptation_type=adaptation_type,
        pre_state=pre_state,
        post_state=post_state,
        governance_level=governance_level,
        requires_approval=requires_approval,
    )
    await db.commit()
    return {
        "adaptation_id": adaptation.adaptation_id,
        "impact_score": adaptation.impact_score,
        "approval_required": adaptation.approval_required,
    }


@router.post("/stabilization")
async def begin_stabilization(
    session_scope: str,
    lineage_id: str,
    stabilization_scope: str,
    affected_components: List[str],
    pre_state: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db),
):
    """Begin a stabilization effort"""
    stabilizer = SystemicEvolutionStabilizer(db)
    stabilization = await stabilizer.begin_stabilization(
        session_id="stabilization_" + session_scope,
        lineage_id=lineage_id,
        stabilization_scope=stabilization_scope,
        affected_components=affected_components,
        pre_state=pre_state,
    )
    await db.commit()
    return {"stabilization_id": stabilization.stabilization_id, "iteration": stabilization.iteration}


@router.post("/stabilization/{stabilization_id}/intervention")
async def apply_stabilization_intervention(
    stabilization_id: str,
    intervention: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db),
):
    """Apply a stabilization intervention"""
    stabilizer = SystemicEvolutionStabilizer(db)
    stabilization = await stabilizer.apply_intervention(stabilization_id, intervention)
    await db.commit()
    return {
        "stabilization_id": stabilization.stabilization_id,
        "iteration": stabilization.iteration,
        "convergence_score": stabilization.convergence_score,
        "stabilization_complete": stabilization.stabilization_complete,
    }


@router.post("/stabilization/{stabilization_id}/complete")
async def complete_stabilization(
    stabilization_id: str,
    post_state: Dict[str, Any],
    success: bool = True,
    db: AsyncSession = Depends(get_async_db),
):
    """Complete stabilization"""
    stabilizer = SystemicEvolutionStabilizer(db)
    stabilization = await stabilizer.complete_stabilization(
        stabilization_id, post_state, success)
    await db.commit()
    return {
        "stabilization_id": stabilization.stabilization_id,
        "stabilization_state": stabilization.stabilization_state,
        "duration_seconds": stabilization.duration_seconds,
    }


__all__ = ["router"]
