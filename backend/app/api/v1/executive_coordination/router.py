"""
Executive Coordination API Router - Recursive Executive Coordination Layer.

Provides RESTful endpoints for:
- Recursive Cognition Supervision Engine
- Orchestration Arbitration System
- Hierarchical Stabilization Systems
- Executive Coordination Fabric
- Predictive Recursive Diagnostics
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.deps import get_db
from app.domains.executive_coordination.services import (
    RecursiveSupervisionEngine,
    OrchestrationArbitrationEngine,
    HierarchicalStabilizationSystem,
    ExecutiveCoordinationFabric,
    PredictiveRecursiveDiagnostics,
    AdaptiveHierarchyBalancing,
    GovernanceReconciliationService,
    SystemicCoherenceLineageService,
)
from app.domains.executive_coordination.models import (
    SupervisionLevel,
    SupervisionState,
    ArbitrationScope,
    ArbitrationState,
    StabilizationTier,
    StabilizationAction,
    CoordinationTopology,
    CoordinationState,
    CoherenceMetric,
    BalanceStrategy,
    DiagnosticsHorizon,
    AnomalySeverity,
    ReconciliationState,
)
from ....schemas.executive_coordination import (
    SupervisionSessionCreate,
    SupervisionSessionResponse,
    SupervisionEvaluationRequest,
    SupervisionEvaluationResponse,
    SupervisionArtifactCreate,
    SupervisionArtifactResponse,
    ArbitrationPolicyCreate,
    ArbitrationPolicyResponse,
    ConflictingClaimInput,
    ArbitrationCreate,
    ArbitrationResponse,
    ArbitrationResolveRequest,
    StabilizationProfileCreate,
    StabilizationProfileResponse,
    StabilizationExecuteRequest,
    StabilizationEventResponse,
    TopologyNodeInput,
    CoordinationTopologyCreate,
    CoordinationTopologyResponse,
    CoordinationEdgeCreate,
    CoordinationEdgeResponse,
    TopologySyncRequest,
    DiagnosticsForecastCreate,
    DiagnosticsForecastResponse,
    AnomalyDetectionCreate,
    AnomalyDetectionResponse,
    BalancingCalculateRequest,
    BalancingResponse,
    ReconciliationMetricsCreate,
    ReconciliationMetricsResponse,
    CoherenceLineageCreate,
    CoherenceLineageResponse,
    ExecutiveOverview,
)

router = APIRouter(prefix="/executive", tags=["executive-coordination"])


# ============================================================================
# Service Dependency
# ============================================================================


def get_executive_services(db=Depends(get_db)):
    """Get all executive coordination services."""
    return {
        "supervision": RecursiveSupervisionEngine(db),
        "arbitration": OrchestrationArbitrationEngine(db),
        "stabilization": HierarchicalStabilizationSystem(db),
        "coordination": ExecutiveCoordinationFabric(db),
        "diagnostics": PredictiveRecursiveDiagnostics(db),
        "balancing": AdaptiveHierarchyBalancing(db),
        "reconciliation": GovernanceReconciliationService(db),
        "lineage": SystemicCoherenceLineageService(db),
    }


# ============================================================================
# System Overview
# ============================================================================


@router.get("/overview", response_model=ExecutiveOverview)
async def get_executive_overview(
    services: Dict = Depends(get_executive_services),
):
    """Get executive coordination system overview."""
    supervision = services["supervision"]
    arbitration = services["arbitration"]
    stabilization = services["stabilization"]
    coordination = services["coordination"]
    diagnostics = services["diagnostics"]

    active_sessions = supervision.get_active_sessions(limit=100)
    active_arbs = arbitration.get_active_arbitrations(limit=100)
    active_profiles = stabilization.get_active_profiles(limit=100)
    topologies = coordination.get_topologies(limit=100)
    forecasts = diagnostics.get_forecasts(not_validated=True, limit=100)
    anomalies = diagnostics.get_active_anomalies(limit=100)

    total_coherence = 1.0
    if topologies:
        total_coherence = sum(t.coherence_score for t in topologies) / len(topologies)

    # Assess system health
    if total_coherence >= 0.9 and not anomalies:
        health = "healthy"
    elif total_coherence >= 0.7:
        health = "stable"
    elif total_coherence >= 0.5:
        health = "degraded"
    elif total_coherence >= 0.3:
        health = "unstable"
    else:
        health = "critical"

    return ExecutiveOverview(
        active_supervision_sessions=len(active_sessions),
        active_arbitrations=len(active_arbs),
        stabilization_profiles=len(active_profiles),
        coordination_topologies=len(topologies),
        active_forecasts=len(forecasts),
        active_anomalies=len(anomalies),
        overall_coherence_score=total_coherence,
        system_health=health,
    )


# ============================================================================
# Recursive Supervision Endpoints
# ============================================================================


@router.post("/supervision/sessions", response_model=dict)
async def create_supervision_session(
    request: SupervisionSessionCreate,
    services: Dict = Depends(get_executive_services),
):
    """Create a new recursive supervision session."""
    supervision = services["supervision"]

    session = supervision.create_session(
        supervisor_id=request.supervisor_id,
        scope=request.scope,
        target_id=request.target_id,
        target_type=request.target_type,
        supervision_level=SupervisionLevel(request.supervision_level),
        parent_session_id=request.parent_session_id,
        target_snapshot=request.target_snapshot,
    )

    return {
        "session_id": str(session.id),
        "session_key": session.session_key,
        "supervision_state": session.supervision_state,
        "recursion_depth": session.recursion_depth,
    }


@router.get("/supervision/sessions", response_model=List[dict])
async def list_supervision_sessions(
    scope: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    services: Dict = Depends(get_executive_services),
):
    """List supervision sessions."""
    supervision = services["supervision"]
    sessions = supervision.get_active_sessions(scope=scope, limit=limit)

    if state:
        sessions = [s for s in sessions if s.supervision_state == state]

    return [
        {
            "session_id": str(s.id),
            "session_key": s.session_key,
            "supervisor_id": s.supervisor_id,
            "scope": s.scope,
            "target_id": s.target_id,
            "supervision_state": s.supervision_state,
            "confidence_score": s.confidence_score,
            "recrospection_depth": s.recursion_depth,
            "started_at": s.started_at.isoformat() if s.started_at else None,
        }
        for s in sessions
    ]


@router.get("/supervision/sessions/{session_id}", response_model=dict)
async def get_supervision_session(
    session_id: UUID,
    services: Dict = Depends(get_executive_services),
):
    """Get a supervision session by ID."""
    supervision = services["supervision"]
    session = supervision.db.get(RecursiveSupervisionSession, session_id)
    if not session:
        # Try to get directly
        from app.domains.executive_coordination.models import RecursiveSupervisionSession
        session = supervision.db.get(RecursiveSupervisionSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": str(session.id),
        "session_key": session.session_key,
        "supervisor_id": session.supervisor_id,
        "scope": session.scope,
        "target_id": session.target_id,
        "target_type": session.target_type,
        "supervision_state": session.supervision_state,
        "confidence_score": session.confidence_score,
        "findings": session.findings,
        "recommendations": session.recommendations,
        "violations": session.violations,
        "escalated": session.escalated,
        "escalated_to": session.escalated_to,
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
    }


@router.post("/supervision/sessions/{session_id}/evaluate", response_model=SupervisionEvaluationResponse)
async def evaluate_supervision_session(
    session_id: UUID,
    request: SupervisionEvaluationRequest,
    services: Dict = Depends(get_executive_services),
):
    """Evaluate a supervision session with metrics."""
    supervision = services["supervision"]

    metrics_data = [
        {
            "category": m.category,
            "value": m.value,
            "threshold": m.threshold,
            "severity": m.severity,
            "description": m.description,
            "recommendation": m.recommendation,
            "confidence": m.confidence,
            "is_violation": m.is_violation,
        }
        for m in request.metrics
    ]

    result = supervision.evaluate_session(session_id, metrics_data)

    return SupervisionEvaluationResponse(
        session_id=result.session_id,
        state=result.state,
        confidence_score=result.confidence_score,
        findings=[{"category": f.category, "severity": f.severity, "description": f.description} for f in result.findings],
        violations=result.violations,
        recommendations=result.recommendations,
        escalated=result.escalated,
        escalated_to=result.escalated_to,
        duration_ms=result.duration_ms,
    )


@router.post("/supervision/artifacts", response_model=dict)
async def create_supervision_artifact(
    request: SupervisionArtifactCreate,
    services: Dict = Depends(get_executive_services),
):
    """Store a supervision artifact."""
    supervision = services["supervision"]

    artifact = supervision.store_artifact(
        session_id=request.session_id,
        artifact_type=request.artifact_type,
        scope=request.scope,
        title=request.title,
        content=request.content,
        importance=request.importance,
        summary=request.summary,
    )

    return {
        "artifact_id": str(artifact.id),
        "artifact_key": artifact.artifact_key,
        "artifact_type": artifact.artifact_type,
    }


# ============================================================================
# Arbitration Endpoints
# ============================================================================


@router.post("/arbitration/policies", response_model=dict)
async def create_arbitration_policy(
    request: ArbitrationPolicyCreate,
    services: Dict = Depends(get_executive_services),
):
    """Create an arbitration policy."""
    arbitration = services["arbitration"]

    from app.domains.executive_coordination.models import ArbitrationPolicy

    policy = ArbitrationPolicy(
        policy_key=request.policy_key,
        name=request.name,
        scope=request.scope,
        scope_type=request.scope_type,
        strategy=request.strategy,
        strategy_config=request.strategy_config,
        priority=request.priority,
        max_rounds=request.max_rounds,
        timeout_ms=request.timeout_ms,
        escalation_threshold=request.escalation_threshold,
        fallback_strategy=request.fallback_strategy,
        is_active=request.is_active,
    )
    arbitration.db.add(policy)
    arbitration.db.commit()
    arbitration.db.refresh(policy)

    return {
        "policy_id": str(policy.id),
        "policy_key": policy.policy_key,
        "name": policy.name,
    }


@router.post("/arbitration", response_model=dict)
async def create_arbitration(
    request: ArbitrationCreate,
    services: Dict = Depends(get_executive_services),
):
    """Create a new arbitration process."""
    arbitration = services["arbitration"]

    claims = [
        {
            "party": c.party,
            "priority": c.priority,
            "score": c.score,
            "data": c.data,
        }
        for c in request.conflicting_claims
    ]

    arb = arbitration.create_arbitration(
        scope=request.scope,
        conflict_type=request.conflict_type,
        parties=request.parties,
        conflicting_claims=claims,
        priority=request.priority,
        description=request.description,
    )

    return {
        "arbitration_id": str(arb.id),
        "arbitration_key": arb.arbitration_key,
        "arbitration_state": arb.arbitration_state,
    }


@router.get("/arbitration", response_model=List[dict])
async def list_arbitrations(
    scope: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    services: Dict = Depends(get_executive_services),
):
    """List active arbitration processes."""
    arbitration = services["arbitration"]
    arbs = arbitration.get_active_arbitrations(scope=scope, limit=limit)

    if state:
        arbs = [a for a in arbs if a.arbitration_state == state]

    return [
        {
            "arbitration_id": str(a.id),
            "arbitration_key": a.arbitration_key,
            "scope": a.scope,
            "conflict_type": a.conflict_type,
            "parties": a.parties,
            "party_count": a.party_count,
            "arbitration_state": a.arbitration_state,
            "priority": a.priority,
            "negotiation_rounds": a.negotiation_rounds,
            "escalation_required": a.escalation_required,
        }
        for a in arbs
    ]


@router.post("/arbitration/{arbitration_id}/resolve", response_model=dict)
async def resolve_arbitration(
    arbitration_id: UUID,
    request: ArbitrationResolveRequest,
    services: Dict = Depends(get_executive_services),
):
    """Resolve an arbitration process."""
    arbitration = services["arbitration"]

    result = arbitration.resolve_arbitration(
        arbitration_id=arbitration_id,
        strategy=request.strategy,
    )

    return {
        "arbitration_id": result.arbitration_id,
        "state": result.state,
        "confidence_score": result.confidence_score,
        "winning_party": result.winning_party,
        "resolution_strategy": result.resolution_strategy,
        "negotiation_rounds": result.negotiation_rounds,
        "escalation_required": result.escalation_required,
        "resolution_time_ms": result.resolution_time_ms,
    }


# ============================================================================
# Stabilization Endpoints
# ============================================================================


@router.post("/stabilization/profiles", response_model=dict)
async def create_stabilization_profile(
    request: StabilizationProfileCreate,
    services: Dict = Depends(get_executive_services),
):
    """Create a stabilization profile."""
    stabilization = services["stabilization"]

    profile = stabilization.create_profile(
        name=request.name,
        scope=request.scope,
        tier=StabilizationTier(request.tier),
        thresholds=request.thresholds,
        action_thresholds=request.action_thresholds,
        parent_profile_id=request.parent_profile_id,
    )

    return {
        "profile_id": str(profile.id),
        "profile_key": profile.profile_key,
        "name": profile.name,
        "tier": profile.tier,
    }


@router.get("/stabilization/profiles", response_model=List[dict])
async def list_stabilization_profiles(
    scope: Optional[str] = Query(None),
    tier: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    services: Dict = Depends(get_executive_services),
):
    """List stabilization profiles."""
    stabilization = services["stabilization"]
    profiles = stabilization.get_active_profiles(scope=scope, limit=limit)

    if tier:
        profiles = [p for p in profiles if p.tier == tier]

    return [
        {
            "profile_id": str(p.id),
            "profile_key": p.profile_key,
            "name": p.name,
            "scope": p.scope,
            "tier": p.tier,
            "priority": p.priority,
            "state": p.state,
            "activation_count": p.activation_count,
            "success_count": p.success_count,
        }
        for p in profiles
    ]


@router.post("/stabilization/execute", response_model=dict)
async def execute_stabilization(
    request: StabilizationExecuteRequest,
    services: Dict = Depends(get_executive_services),
):
    """Execute a stabilization action."""
    stabilization = services["stabilization"]

    action = StabilizationAction(request.action) if request.action else None

    result = stabilization.execute_stabilization(
        profile_id=request.profile_id,
        target_id=request.target_id,
        target_type=request.target_type,
        coherence_score_before=request.coherence_score_before,
        action=action,
    )

    return {
        "event_id": result.event_id,
        "action": result.action,
        "tier_before": result.tier_before,
        "tier_after": result.tier_after,
        "success": result.success,
        "coherence_delta": result.coherence_delta,
        "duration_ms": result.duration_ms,
    }


# ============================================================================
# Coordination Topology Endpoints
# ============================================================================


@router.post("/coordination/topology", response_model=dict)
async def create_topology(
    request: CoordinationTopologyCreate,
    services: Dict = Depends(get_executive_services),
):
    """Create a coordination topology."""
    coordination = services["coordination"]

    topology = coordination.create_topology(
        name=request.name,
        scope=request.scope,
        topology_type=CoordinationTopology(request.topology_type),
        nodes=request.nodes,
        coordinator_ids=request.coordinator_ids,
    )

    return {
        "topology_id": str(topology.id),
        "topology_key": topology.topology_key,
        "name": topology.name,
        "topology_type": topology.topology_type,
        "node_count": topology.node_count,
    }


@router.get("/coordination/topology", response_model=List[dict])
async def list_topologies(
    scope: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    services: Dict = Depends(get_executive_services),
):
    """List coordination topologies."""
    coordination = services["coordination"]
    topologies = coordination.get_topologies(scope=scope, limit=limit)

    return [
        {
            "topology_id": str(t.id),
            "topology_key": t.topology_key,
            "name": t.name,
            "scope": t.scope,
            "topology_type": t.topology_type,
            "node_count": t.node_count,
            "edge_count": t.edge_count,
            "topology_state": t.topology_state,
            "coherence_score": t.coherence_score,
            "sync_latency_ms": t.sync_latency_ms,
        }
        for t in topologies
    ]


@router.post("/coordination/topology/{topology_id}/edges", response_model=dict)
async def add_topology_edge(
    topology_id: UUID,
    request: CoordinationEdgeCreate,
    services: Dict = Depends(get_executive_services),
):
    """Add an edge to a topology."""
    coordination = services["coordination"]

    edge = coordination.add_edge(
        topology_id=topology_id,
        source_id=request.source_id,
        target_id=request.target_id,
        edge_type=request.edge_type,
        bandwidth=request.bandwidth,
    )

    return {
        "edge_id": str(edge.id),
        "edge_key": edge.edge_key,
        "source_id": edge.source_id,
        "target_id": edge.target_id,
    }


@router.post("/coordination/topology/{topology_id}/sync", response_model=dict)
async def sync_topology(
    topology_id: UUID,
    request: TopologySyncRequest,
    services: Dict = Depends(get_executive_services),
):
    """Synchronize a topology."""
    coordination = services["coordination"]

    topology = coordination.sync_topology(
        topology_id=topology_id,
        message_throughput=request.message_throughput,
        sync_latency_ms=request.sync_latency_ms,
        conflict_rate=request.conflict_rate,
    )

    return {
        "topology_id": str(topology.id),
        "topology_state": topology.topology_state,
        "coherence_score": topology.coherence_score,
        "conflict_rate": topology.conflict_rate,
    }


# ============================================================================
# Diagnostics Endpoints
# ============================================================================


@router.post("/diagnostics/forecasts", response_model=dict)
async def create_forecast(
    request: DiagnosticsForecastCreate,
    services: Dict = Depends(get_executive_services),
):
    """Generate a diagnostic forecast."""
    diagnostics = services["diagnostics"]

    forecast = diagnostics.generate_forecast(
        target_id=request.target_id,
        target_type=request.target_type,
        scope=request.scope,
        forecast_kind=request.forecast_kind,
        horizon=DiagnosticsHorizon(request.horizon),
        indicators=request.indicators,
        risk_factors=request.risk_factors,
    )

    return {
        "forecast_id": str(forecast.id),
        "forecast_key": forecast.forecast_key,
        "target_id": forecast.target_id,
        "forecast_kind": forecast.forecast_kind,
        "horizon": forecast.horizon,
        "predicted_value": forecast.predicted_value,
        "confidence": forecast.confidence,
        "probability": forecast.probability,
        "severity": forecast.severity,
        "risk_level": forecast.risk_level,
    }


@router.get("/diagnostics/forecasts", response_model=List[dict])
async def list_forecasts(
    target_id: Optional[str] = Query(None),
    scope: Optional[str] = Query(None),
    horizon: Optional[str] = Query(None),
    not_validated: bool = Query(True),
    limit: int = Query(50, le=100),
    services: Dict = Depends(get_executive_services),
):
    """List diagnostic forecasts."""
    diagnostics = services["diagnostics"]

    h = DiagnosticsHorizon(horizon) if horizon else None

    forecasts = diagnostics.get_forecasts(
        target_id=target_id,
        scope=scope,
        horizon=h,
        not_validated=not_validated,
        limit=limit,
    )

    return [
        {
            "forecast_id": str(f.id),
            "forecast_key": f.forecast_key,
            "target_id": f.target_id,
            "target_type": f.target_type,
            "forecast_kind": f.forecast_kind,
            "horizon": f.horizon,
            "predicted_value": f.predicted_value,
            "confidence": f.confidence,
            "probability": f.probability,
            "severity": f.severity,
            "risk_level": f.risk_level,
            "validated": f.validated,
            "generated_at": f.generated_at.isoformat() if f.generated_at else None,
        }
        for f in forecasts
    ]


@router.post("/diagnostics/anomalies", response_model=dict)
async def create_anomaly_detection(
    request: AnomalyDetectionCreate,
    services: Dict = Depends(get_executive_services),
):
    """Detect a systemic anomaly."""
    diagnostics = services["diagnostics"]

    anomaly = diagnostics.detect_anomaly(
        target_id=request.target_id,
        target_type=request.target_type,
        scope=request.scope,
        anomaly_type=request.anomaly_type,
        baseline=request.baseline,
        observed=request.observed,
        detection_method=request.detection_method,
    )

    return {
        "anomaly_id": str(anomaly.id),
        "anomaly_key": anomaly.anomaly_key,
        "target_id": anomaly.target_id,
        "anomaly_type": anomaly.anomaly_type,
        "severity": anomaly.severity,
        "deviation": anomaly.deviation,
        "status": anomaly.status,
        "detected_at": anomaly.detected_at.isoformat() if anomaly.detected_at else None,
    }


@router.get("/diagnostics/anomalies", response_model=List[dict])
async def list_anomalies(
    scope: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    services: Dict = Depends(get_executive_services),
):
    """List active anomaly detections."""
    diagnostics = services["diagnostics"]

    anomalies = diagnostics.get_active_anomalies(
        scope=scope,
        severity_filter=severity,
        limit=limit,
    )

    return [
        {
            "anomaly_id": str(a.id),
            "anomaly_key": a.anomaly_key,
            "target_id": a.target_id,
            "target_type": a.target_type,
            "anomaly_type": a.anomaly_type,
            "severity": a.severity,
            "scope": a.scope,
            "deviation": a.deviation,
            "cascade_risk": a.cascade_risk,
            "status": a.status,
            "detected_at": a.detected_at.isoformat() if a.detected_at else None,
        }
        for a in anomalies
    ]


# ============================================================================
# Balancing Endpoints
# ============================================================================


@router.post("/balancing/calculate", response_model=dict)
async def calculate_balance(
    request: BalancingCalculateRequest,
    services: Dict = Depends(get_executive_services),
):
    """Calculate hierarchy balance."""
    balancing = services["balancing"]

    result = balancing.calculate_balance(
        scope=request.scope,
        nodes=request.nodes,
        weights=request.weights,
    )

    return {
        "balancing_id": str(result.id),
        "balancing_key": result.balancing_key,
        "scope": result.scope,
        "balance_strategy": result.balance_strategy,
        "balance_score_before": result.balance_score_before,
        "balance_score_after": result.balance_score_after,
    }


# ============================================================================
# Reconciliation Endpoints
# ============================================================================


@router.post("/reconciliation/metrics", response_model=dict)
async def record_reconciliation_metrics(
    request: ReconciliationMetricsCreate,
    services: Dict = Depends(get_executive_services),
):
    """Record governance reconciliation metrics."""
    reconciliation = services["reconciliation"]

    metrics = reconciliation.record_metrics(
        scope=request.scope,
        policy_alignment_score=request.policy_alignment_score,
        semantic_alignment_score=request.semantic_alignment_score,
        execution_alignment_score=request.execution_alignment_score,
        conflicts_detected=request.conflicts_detected,
        policies_evaluated=request.policies_evaluated,
        policies_violated=request.policies_violated,
    )

    return {
        "metrics_id": str(metrics.id),
        "metrics_key": metrics.metrics_key,
        "scope": metrics.scope,
        "reconciliation_state": metrics.reconciliation_state,
        "policy_alignment_score": metrics.policy_alignment_score,
    }


@router.get("/reconciliation/metrics", response_model=List[dict])
async def get_reconciliation_metrics(
    scope: Optional[str] = Query(None),
    limit: int = Query(1),
    services: Dict = Depends(get_executive_services),
):
    """Get the latest reconciliation metrics."""
    reconciliation = services["reconciliation"]

    metrics_list = reconciliation.get_latest_metrics(scope=scope, limit=limit)

    return [
        {
            "metrics_id": str(m.id),
            "metrics_key": m.metrics_key,
            "scope": m.scope,
            "reconciliation_state": m.reconciliation_state,
            "policy_alignment_score": m.policy_alignment_score,
            "semantic_alignment_score": m.semantic_alignment_score,
            "execution_alignment_score": m.execution_alignment_score,
            "deviation_detected": m.deviation_detected,
            "conflicts_detected": m.conflicts_detected,
            "policies_violated": m.policies_violated,
        }
        for m in metrics_list
    ]


# ============================================================================
# Coherence Lineage Endpoints
# ============================================================================


@router.post("/coherence/lineage", response_model=dict)
async def record_coherence_lineage(
    request: CoherenceLineageCreate,
    services: Dict = Depends(get_executive_services),
):
    """Record a coherence lineage event."""
    lineage = services["lineage"]

    event = lineage.record_event(
        scope=request.scope,
        source_id=request.source_id,
        source_type=request.source_type,
        coherence_metric=CoherenceMetric(request.coherence_metric),
        coherence_value=request.coherence_value,
        event_type=request.event_type,
        event_description=request.event_description,
        event_data=request.event_data,
        parent_lineage_id=request.parent_lineage_id,
    )

    return {
        "lineage_id": str(event.id),
        "lineage_key": event.lineage_key,
        "coherence_metric": event.coherence_metric,
        "coherence_value": event.coherence_value,
        "coherence_trend": event.coherence_trend,
        "chain_id": event.chain_id,
        "chain_position": event.chain_position,
    }


@router.get("/coherence/lineage", response_model=List[dict])
async def get_coherence_lineage(
    chain_id: Optional[str] = Query(None),
    source_id: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    services: Dict = Depends(get_executive_services),
):
    """Get coherence lineage chain."""
    lineage = services["lineage"]

    events = lineage.get_lineage_chain(
        chain_id=chain_id,
        source_id=source_id,
        limit=limit,
    )

    return [
        {
            "lineage_id": str(e.id),
            "lineage_key": e.lineage_key,
            "scope": e.scope,
            "coherence_metric": e.coherence_metric,
            "source_id": e.source_id,
            "coherence_value": e.coherence_value,
            "coherence_trend": e.coherence_trend,
            "event_type": e.event_type,
            "chain_id": e.chain_id,
            "chain_position": e.chain_position,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        }
        for e in events
    ]


# ============================================================================
# Status Endpoint
# ============================================================================


@router.get("/status", response_model=Dict[str, Any])
async def get_executive_status(
    services: Dict = Depends(get_executive_services),
):
    """Get executive coordination system status."""
    return {
        "service": "executive_coordination",
        "status": "operational",
        "capabilities": [
            "recursive_supervision",
            "orchestration_arbitration",
            "hierarchical_stabilization",
            "executive_coordination_fabric",
            "predictive_diagnostics",
            "adaptive_hierarchy_balancing",
            "governance_reconciliation",
            "systemic_coherence_lineage",
        ],
        "timestamp": datetime.utcnow().isoformat(),
    }
