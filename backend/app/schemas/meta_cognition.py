"""
Meta-Cognition Schemas - API request/response models for executive intelligence layer.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ---- Cognition Diagnostics ----

class CognitionDiagnosticsCreate(BaseModel):
    """Create cognition diagnostics request"""
    scope: str = Field(..., description="Diagnostics scope")
    domain: str = Field(..., description="Domain context")
    diagnostic_types: Optional[List[str]] = Field(None, description="Specific diagnostic types")


class CognitionDiagnosticsResponse(BaseModel):
    """Cognition diagnostics response"""
    diagnostic_id: str
    scope: str
    domain: str
    cognition_state: str
    reasoning_quality: float
    coherence_score: float
    consistency_score: float
    adaptation_efficiency: float
    distribution_alignment: float
    sync_health: float
    conflict_rate: float
    detected_anomalies: Optional[List[Dict[str, Any]]]
    anomaly_severity: Optional[str]
    recommendations: Optional[List[Dict[str, Any]]]
    assessed_at: datetime
    correlation_id: Optional[str]


# ---- Introspection Session ----

class IntrospectionSessionCreate(BaseModel):
    """Create introspection session request"""
    scope: str = Field(..., description="Introspection scope")
    introspection_type: str = Field(..., description="Type of introspection")
    execution_id: Optional[str] = Field(None, description="Execution context")
    workflow_id: Optional[str] = Field(None, description="Workflow context")
    focus_areas: Optional[List[str]] = Field(None, description="Focus areas to investigate")


class IntrospectionSessionResponse(BaseModel):
    """Introspection session response"""
    session_id: str
    execution_id: Optional[str]
    workflow_id: Optional[str]
    scope: str
    phase: str
    introspection_type: str
    focus_areas: List[str]
    findings: Optional[List[Dict[str, Any]]]
    insights: Optional[List[str]]
    confidence: float
    depth_achieved: int
    breadth_achieved: int
    is_active: bool
    error: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: Optional[float]


# ---- Semantic Consistency Audit ----

class SemanticAuditCreate(BaseModel):
    """Create semantic audit request"""
    audit_kind: str = Field(..., description="Audit type")
    scope: str = Field(..., description="Scope context")
    target_entities: Optional[List[str]] = Field(None, description="Entities to audit")


class SemanticAuditResponse(BaseModel):
    """Semantic audit response"""
    audit_id: str
    audit_kind: str
    scope: str
    audit_status: str
    severity: str
    consistency_score: float
    divergence_detected: Optional[float]
    violations: Optional[List[Dict[str, Any]]]
    warnings: Optional[List[str]]
    target_entities: Optional[List[str]]
    resolution_required: bool
    resolution_applied: Optional[str]
    audited_at: datetime
    correlation_id: Optional[str]


# ---- Adaptive Governance Profile ----

class GovernanceProfileCreate(BaseModel):
    """Create governance profile request"""
    profile_key: str = Field(..., description="Profile key")
    scope: str = Field(..., description="Scope context")
    domain: str = Field(..., description="Domain context")
    validation_thresholds: Optional[Dict[str, float]] = Field(None, description="Validation thresholds")
    enforcement_rules: Optional[List[Dict[str, Any]]] = Field(None, description="Enforcement rules")


class GovernanceProfileUpdate(BaseModel):
    """Update governance profile"""
    validation_thresholds: Optional[Dict[str, float]] = None
    enforcement_rules: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None


class GovernanceProfileResponse(BaseModel):
    """Governance profile response"""
    profile_id: str
    profile_key: str
    scope: str
    domain: str
    validation_thresholds: Dict[str, float]
    alignment_requirements: Dict[str, Any]
    enforcement_rules: List[Dict[str, Any]]
    policy_mode: str
    intervention_level: str
    is_active: bool
    alignment_status: str
    trigger_count: int
    violation_count: int
    last_triggered: Optional[datetime]
    version: int
    updated_at: Optional[datetime]


# ---- Cognition Reconciliation State ----

class ReconciliationRequest(BaseModel):
    """Reconciliation request"""
    node_id: str = Field(..., description="Node identifier")
    scope: str = Field(..., description="Scope context")
    sync_version: Optional[int] = Field(None, description="Expected sync version")


class ReconciliationStateResponse(BaseModel):
    """Reconciliation state response"""
    state_id: str
    node_id: str
    scope: str
    reconciliation_status: str
    last_sync_at: Optional[datetime]
    sync_version: int
    pending_updates: int
    active_conflicts: Optional[List[Dict[str, Any]]]
    resolved_conflicts: Optional[int]
    sync_health_score: float
    latency_ms: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]


# ---- Predictive Cognition Forecast ----

class ForecastRequest(BaseModel):
    """Forecast request"""
    target_id: str = Field(..., description="Target identifier")
    target_type: str = Field(..., description="Target type")
    scope: str = Field(..., description="Scope context")
    horizon: str = Field("near_term", description="Prediction horizon")


class ForecastResponse(BaseModel):
    """Forecast response"""
    forecast_id: str
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
    indicators: Optional[List[Dict[str, Any]]]
    risk_factors: Optional[List[str]]
    recommended_actions: Optional[List[str]]
    risk_level: str
    actual_value: Optional[float]
    predicted: bool
    predicted_for: datetime
    generated_at: datetime


# ---- Reasoning Lineage ----

class ReasoningStepCreate(BaseModel):
    """Create reasoning step request"""
    execution_id: str = Field(..., description="Execution identifier")
    reasoning_type: str = Field(..., description="Type of reasoning")
    premise: str = Field(..., description="Reasoning premise")
    inference: str = Field(..., description="Inference step")
    conclusion: str = Field(..., description="Conclusion")
    evidence: Optional[List[Dict[str, Any]]] = Field(None, description="Supporting evidence")
    parent_lineage_id: Optional[str] = Field(None, description="Parent lineage reference")
    session_id: Optional[str] = Field(None, description="Session context")


class ReasoningLineageResponse(BaseModel):
    """Reasoning lineage response"""
    lineage_id: str
    execution_id: str
    session_id: Optional[str]
    reasoning_type: str
    inference_pattern: str
    lineage_chain: str
    chain_position: int
    premise: str
    inference: str
    conclusion: str
    evidence: Optional[List[Dict[str, Any]]]
    confidence: float
    reasoning_depth: int
    decision_context: Optional[Dict[str, Any]]
    validation_result: Optional[str]
    verified: bool
    parent_lineage_id: Optional[str]
    created_at: datetime


# ---- Anomaly Registry ----

class AnomalyCreate(BaseModel):
    """Create anomaly request"""
    anomaly_type: str = Field(..., description="Anomaly type")
    target_id: str = Field(..., description="Target identifier")
    target_type: str = Field(..., description="Target type")
    scope: str = Field(..., description="Scope context")
    detection_method: str = Field(..., description="Detection method")
    detection_signals: Optional[List[Dict[str, Any]]] = Field(None, description="Detection signals")
    severity: str = Field("warning", description="Severity level")
    expected_value: Optional[float] = Field(None, description="Expected value")
    actual_value: Optional[float] = Field(None, description="Actual value")
    correlation_id: Optional[str] = Field(None, description="Correlation identifier")


class AnomalyResponse(BaseModel):
    """Anomaly response"""
    anomaly_id: str
    anomaly_type: str
    severity: str
    target_id: str
    target_type: str
    scope: str
    detection_method: str
    detection_signals: Optional[List[Dict[str, Any]]]
    expected_value: Optional[float]
    actual_value: Optional[float]
    deviation: Optional[float]
    impact_scope: Optional[str]
    impact_severity: Optional[str]
    status: str
    remediation_action: Optional[str]
    resolved_at: Optional[datetime]
    correlation_id: Optional[str]
    detected_at: datetime


# ---- Self-Awareness Metrics ----

class SelfAwarenessMetricsResponse(BaseModel):
    """Self-awareness metrics response"""
    metric_id: str
    session_id: Optional[str]
    execution_id: Optional[str]
    scope: str
    introspection_depth: float
    reflection_accuracy: float
    self_model_accuracy: float
    introspection_latency_ms: float
    processing_overhead: float
    insight_relevance: float
    finding_accuracy: float
    metric_type: str
    metadata: Optional[Dict[str, Any]]
    timestamp: datetime


# ---- Meta-Cognition Dashboard ----

class MetaCognitionSummary(BaseModel):
    """Summary of meta-cognition state"""
    cognition_state: str
    active_sessions: int
    active_anomalies: int
    pending_reconciliations: int
    active_forecasts: int
    governance_alignment: str
    last_diagnostics: Optional[CognitionDiagnosticsResponse]


class MetaCognitionHealth(BaseModel):
    """Health status of meta-cognition systems"""
    engine_status: str
    active_sessions: int
    queued_processes: int
    cache_size: int
    uptime_seconds: float


__all__ = [
    "CognitionDiagnosticsCreate",
    "CognitionDiagnosticsResponse",
    "IntrospectionSessionCreate",
    "IntrospectionSessionResponse",
    "SemanticAuditCreate",
    "SemanticAuditResponse",
    "GovernanceProfileCreate",
    "GovernanceProfileUpdate",
    "GovernanceProfileResponse",
    "ReconciliationRequest",
    "ReconciliationStateResponse",
    "ForecastRequest",
    "ForecastResponse",
    "ReasoningStepCreate",
    "ReasoningLineageResponse",
    "AnomalyCreate",
    "AnomalyResponse",
    "SelfAwarenessMetricsResponse",
    "MetaCognitionSummary",
    "MetaCognitionHealth",
]
