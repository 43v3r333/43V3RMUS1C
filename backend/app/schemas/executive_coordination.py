"""
Executive Coordination Schemas - Pydantic models for API serialization.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Supervision Schemas
# ---------------------------------------------------------------------------


class SupervisionArtifactCreate(BaseModel):
    session_id: UUID
    artifact_type: str
    scope: str
    title: str
    content: Dict[str, Any]
    importance: float = 0.5
    summary: Optional[str] = None


class SupervisionArtifactResponse(BaseModel):
    id: UUID
    session_id: UUID
    artifact_key: str
    artifact_type: str
    scope: str
    title: str
    content: Dict[str, Any]
    summary: Optional[str]
    importance: float
    confidence: float
    applicability: Optional[Dict[str, Any]]
    state: str
    version: int
    access_count: int
    last_accessed: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class SupervisionMetricInput(BaseModel):
    category: str = "general"
    value: float
    threshold: float = 0.5
    severity: str = "warning"
    description: Optional[str] = None
    recommendation: Optional[str] = None
    confidence: float = 0.5
    is_violation: bool = False


class SupervisionSessionCreate(BaseModel):
    supervisor_id: str
    scope: str
    target_id: str
    target_type: str
    supervision_level: int = 2
    parent_session_id: Optional[UUID] = None
    target_snapshot: Optional[Dict[str, Any]] = None


class SupervisionSessionResponse(BaseModel):
    id: UUID
    session_key: str
    supervisor_id: str
    scope: str
    supervision_level: int
    parent_session_id: Optional[UUID]
    root_session_id: Optional[UUID]
    recursion_depth: int
    target_id: str
    target_type: str
    target_snapshot: Dict[str, Any]
    supervision_state: str
    confidence_score: float
    findings: Optional[List[Dict[str, Any]]]
    recommendations: Optional[List[str]]
    violations: Optional[List[Dict[str, Any]]]
    metrics_evaluated: int
    issues_detected: int
    remediation_cycles: int
    escalated: bool
    escalated_at: Optional[datetime]
    escalated_to: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: Optional[float]
    correlation_id: Optional[str]
    trace_id: Optional[str]

    model_config = {"from_attributes": True}


class SupervisionEvaluationRequest(BaseModel):
    session_id: UUID
    metrics: List[SupervisionMetricInput]


class SupervisionEvaluationResponse(BaseModel):
    session_id: str
    state: str
    confidence_score: float
    findings: List[Dict[str, Any]]
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    escalated: bool
    escalated_to: Optional[str]
    duration_ms: Optional[float]


# ---------------------------------------------------------------------------
# Arbitration Schemas
# ---------------------------------------------------------------------------


class ArbitrationPolicyCreate(BaseModel):
    policy_key: str
    name: str
    scope: str
    scope_type: str = "atomic"
    strategy: str = "priority_weighted"
    strategy_config: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 5
    max_rounds: int = 10
    timeout_ms: int = 30000
    escalation_threshold: int = 3
    fallback_strategy: Optional[str] = None
    is_active: bool = True


class ArbitrationPolicyResponse(BaseModel):
    id: UUID
    policy_key: str
    name: str
    description: Optional[str]
    scope: str
    scope_type: str
    strategy: str
    strategy_config: Dict[str, Any]
    priority: int
    max_rounds: int
    timeout_ms: int
    escalation_threshold: int
    fallback_strategy: Optional[str]
    is_active: bool
    version: int
    invocation_count: int
    success_count: int
    failure_count: int

    model_config = {"from_attributes": True}


class ConflictingClaimInput(BaseModel):
    party: str
    priority: int = 5
    score: float = 0.5
    data: Dict[str, Any] = Field(default_factory=dict)


class ArbitrationCreate(BaseModel):
    scope: str
    conflict_type: str
    parties: List[str]
    conflicting_claims: List[ConflictingClaimInput]
    priority: int = 5
    description: Optional[str] = None


class ArbitrationResponse(BaseModel):
    id: UUID
    arbitration_key: str
    scope: str
    arbitration_scope: str
    priority: int
    arbitration_state: str
    confidence_score: float
    parties: List[str]
    party_count: int
    conflict_type: str
    conflict_description: Optional[str]
    conflicting_claims: List[Dict[str, Any]]
    resolution_strategy: Optional[str]
    resolution_output: Optional[Dict[str, Any]]
    winning_party: Optional[str]
    merge_output: Optional[Dict[str, Any]]
    negotiation_rounds: int
    proposals_evaluated: int
    escalation_required: bool
    escalated: bool
    escalated_at: Optional[datetime]
    detected_at: datetime
    resolved_at: Optional[datetime]
    resolution_time_ms: Optional[float]
    correlation_id: Optional[str]

    model_config = {"from_attributes": True}


class ArbitrationResolveRequest(BaseModel):
    arbitration_id: UUID
    strategy: Optional[str] = None


# ---------------------------------------------------------------------------
# Stabilization Schemas
# ---------------------------------------------------------------------------


class StabilizationProfileCreate(BaseModel):
    name: str
    scope: str
    tier: str = "tier_1_marginal"
    thresholds: Dict[str, float] = Field(default_factory=dict)
    action_thresholds: Dict[str, Any] = Field(default_factory=dict)
    parent_profile_id: Optional[UUID] = None


class StabilizationProfileResponse(BaseModel):
    id: UUID
    profile_key: str
    name: str
    scope: str
    description: Optional[str]
    tier: str
    priority: int
    parent_profile_id: Optional[UUID]
    child_profile_ids: List[str]
    hierarchy_depth: int
    state: str
    thresholds: Dict[str, float]
    action_thresholds: Dict[str, Any]
    recovery_strategy: str
    recovery_window_ms: int
    max_retry_attempts: int
    activation_count: int
    last_activated: Optional[datetime]
    success_count: int

    model_config = {"from_attributes": True}


class StabilizationExecuteRequest(BaseModel):
    profile_id: UUID
    target_id: str
    target_type: str
    coherence_score_before: float
    action: Optional[str] = None


class StabilizationEventResponse(BaseModel):
    id: UUID
    event_key: str
    profile_id: UUID
    target_id: str
    target_type: str
    tier_before: str
    tier_after: str
    action: str
    state: str
    success: bool
    drift_detected: float
    drift_threshold: float
    coherence_score_before: float
    coherence_score_after: float
    detected_at: datetime
    action_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_ms: Optional[float]
    correlation_id: Optional[str]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Coordination Topology Schemas
# ---------------------------------------------------------------------------


class TopologyNodeInput(BaseModel):
    node_id: str
    node_type: str
    capabilities: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TopologyEdgeInput(BaseModel):
    source_id: str
    target_id: str
    edge_type: str = "communication"
    bandwidth: float = 1.0


class CoordinationTopologyCreate(BaseModel):
    name: str
    scope: str
    topology_type: str = "hierarchical"
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    coordinator_ids: List[str] = Field(default_factory=list)


class CoordinationTopologyResponse(BaseModel):
    id: UUID
    topology_key: str
    name: str
    scope: str
    topology_type: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    node_count: int
    edge_count: int
    coordinator_ids: List[str]
    primary_coordinator_id: Optional[str]
    topology_state: str
    coherence_score: float
    message_throughput: float
    sync_latency_ms: float
    conflict_rate: float
    version: int
    created_at: datetime
    last_sync: Optional[datetime]

    model_config = {"from_attributes": True}


class CoordinationEdgeCreate(BaseModel):
    topology_id: UUID
    source_id: str
    target_id: str
    edge_type: str = "communication"
    bandwidth: float = 1.0


class CoordinationEdgeResponse(BaseModel):
    id: UUID
    edge_key: str
    topology_id: UUID
    source_id: str
    target_id: str
    edge_type: str
    bandwidth: float
    latency: float
    state: str
    is_active: bool
    message_count: int
    last_message_at: Optional[datetime]
    error_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TopologySyncRequest(BaseModel):
    topology_id: UUID
    message_throughput: float = 0.0
    sync_latency_ms: float = 0.0
    conflict_rate: float = 0.0


# ---------------------------------------------------------------------------
# Diagnostics Schemas
# ---------------------------------------------------------------------------


class ForecastIndicatorInput(BaseModel):
    value: float
    weight: float = 0.1
    confidence: float = 0.5
    source: Optional[str] = None


class DiagnosticsForecastCreate(BaseModel):
    target_id: str
    target_type: str
    scope: str
    forecast_kind: str
    horizon: str = "near"
    indicators: List[Dict[str, Any]] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)


class DiagnosticsForecastResponse(BaseModel):
    id: UUID
    forecast_key: str
    target_id: str
    target_type: str
    scope: str
    forecast_kind: str
    horizon: str
    predicted_value: float
    confidence: float
    probability: float
    min_value: Optional[float]
    max_value: Optional[float]
    expected_range: Optional[Dict[str, float]]
    indicators: Optional[List[Dict[str, Any]]]
    risk_factors: Optional[List[str]]
    supporting_evidence: Optional[List[str]]
    severity: str
    risk_level: str
    recommended_actions: Optional[List[str]]
    escalation_required: bool
    actual_value: Optional[float]
    accuracy: Optional[float]
    validated: bool
    validated_at: Optional[datetime]
    predicted_for: datetime
    generated_at: datetime

    model_config = {"from_attributes": True}


class AnomalyDetectionInput(BaseModel):
    baseline: Dict[str, float]
    observed: Dict[str, float]
    detection_method: str = "statistical"


class AnomalyDetectionCreate(BaseModel):
    target_id: str
    target_type: str
    scope: str
    anomaly_type: str
    baseline: Dict[str, float]
    observed: Dict[str, float]
    detection_method: str = "statistical"


class AnomalyDetectionResponse(BaseModel):
    id: UUID
    anomaly_key: str
    target_id: str
    target_type: str
    anomaly_type: str
    severity: str
    description: Optional[str]
    scope: str
    affected_components: List[str]
    cascade_risk: float
    detection_method: str
    detection_signals: Optional[List[Dict[str, Any]]]
    baseline: Dict[str, float]
    observed: Dict[str, float]
    deviation: float
    impact_assessment: Optional[Dict[str, Any]]
    correlation_id: Optional[str]
    status: str
    remediation_action: Optional[str]
    resolved: bool
    resolved_at: Optional[datetime]
    detected_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Balancing Schemas
# ---------------------------------------------------------------------------


class BalancingCalculateRequest(BaseModel):
    scope: str
    nodes: List[str]
    weights: Optional[Dict[str, float]] = None


class BalancingResponse(BaseModel):
    id: UUID
    balancing_key: str
    scope: str
    balance_strategy: str
    balance_config: Dict[str, Any]
    state: str
    balance_score_before: float
    balance_score_after: float
    hierarchies: List[str]
    hierarchy_weights: Optional[Dict[str, float]]
    balance_distribution: Optional[Dict[str, Any]]
    nodes: List[str]
    node_weights: Optional[Dict[str, float]]
    changes_required: List[Dict[str, Any]]
    changes_applied: List[Dict[str, Any]]
    rollback_available: bool
    improvement_score: float
    metrics_evaluated: int
    timestamp: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Reconciliation Schemas
# ---------------------------------------------------------------------------


class ReconciliationMetricsCreate(BaseModel):
    scope: str
    policy_alignment_score: float = 1.0
    semantic_alignment_score: float = 1.0
    execution_alignment_score: float = 1.0
    conflicts_detected: int = 0
    policies_evaluated: int = 0
    policies_violated: int = 0


class ReconciliationMetricsResponse(BaseModel):
    id: UUID
    metrics_key: str
    scope: str
    reconciliation_state: str
    policy_alignment_score: float
    semantic_alignment_score: float
    execution_alignment_score: float
    deviation_detected: bool
    deviation_magnitude: float
    deviation_direction: Optional[str]
    conflicts_detected: int
    conflicts_resolved: int
    conflicts_escalated: int
    policies_evaluated: int
    policies_violated: int
    policies_corrected: int
    timestamp: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_ms: Optional[float]
    correlation_id: Optional[str]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Coherence Lineage Schemas
# ---------------------------------------------------------------------------


class CoherenceLineageCreate(BaseModel):
    scope: str
    source_id: str
    source_type: str
    coherence_metric: str
    coherence_value: float
    event_type: str
    event_description: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None
    parent_lineage_id: Optional[UUID] = None


class CoherenceLineageResponse(BaseModel):
    id: UUID
    lineage_key: str
    scope: str
    coherence_metric: str
    source_id: str
    source_type: str
    coherence_value: float
    coherence_delta: float
    coherence_trend: str
    state: str
    status: str
    event_type: str
    event_description: Optional[str]
    event_data: Optional[Dict[str, Any]]
    parent_lineage_id: Optional[UUID]
    correlation_id: Optional[str]
    trace_id: Optional[str]
    chain_id: str
    chain_position: int
    context: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    timestamp: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Dashboard / Overview Schemas
# ---------------------------------------------------------------------------


class ExecutiveOverview(BaseModel):
    active_supervision_sessions: int
    active_arbitrations: int
    stabilization_profiles: int
    coordination_topologies: int
    active_forecasts: int
    active_anomalies: int
    overall_coherence_score: float
    system_health: str


__all__ = [
    # Supervision
    "SupervisionArtifactCreate",
    "SupervisionArtifactResponse",
    "SupervisionMetricInput",
    "SupervisionSessionCreate",
    "SupervisionSessionResponse",
    "SupervisionEvaluationRequest",
    "SupervisionEvaluationResponse",

    # Arbitration
    "ArbitrationPolicyCreate",
    "ArbitrationPolicyResponse",
    "ConflictingClaimInput",
    "ArbitrationCreate",
    "ArbitrationResponse",
    "ArbitrationResolveRequest",

    # Stabilization
    "StabilizationProfileCreate",
    "StabilizationProfileResponse",
    "StabilizationExecuteRequest",
    "StabilizationEventResponse",

    # Topology
    "TopologyNodeInput",
    "TopologyEdgeInput",
    "CoordinationTopologyCreate",
    "CoordinationTopologyResponse",
    "CoordinationEdgeCreate",
    "CoordinationEdgeResponse",
    "TopologySyncRequest",

    # Diagnostics
    "ForecastIndicatorInput",
    "DiagnosticsForecastCreate",
    "DiagnosticsForecastResponse",
    "AnomalyDetectionInput",
    "AnomalyDetectionCreate",
    "AnomalyDetectionResponse",

    # Balancing
    "BalancingCalculateRequest",
    "BalancingResponse",

    # Reconciliation
    "ReconciliationMetricsCreate",
    "ReconciliationMetricsResponse",

    # Lineage
    "CoherenceLineageCreate",
    "CoherenceLineageResponse",

    # Overview
    "ExecutiveOverview",
]
