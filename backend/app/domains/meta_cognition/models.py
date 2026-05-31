"""
Meta-Cognition Domain Models - Runtime self-awareness and orchestration introspection.

Provides:
- Orchestration introspection engine
- Cognition diagnostics runtime
- Execution reasoning analyzer
- Semantic consistency validator
- Adaptive cognition auditing
- Runtime self-analysissystems

This is the EXECUTIVE INTELLIGENCE LAYER of the platform.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from ...models.base import BaseModel


# ---- Enums ----

class IntrospectionPhase(str, Enum):
    """Introspection phase"""
    INITIALIZING = "initializing"
    OBSERVING = "observing"
    ANALYZING = "analyzing"
    SYNTHESIZING = "synthesizing"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"


class CognitionState(str, Enum):
    """Cognition state"""
    HEALTHY = "healthy"
    DRIFTING = "drifting"
    CONFLICTED = "conflicted"
    DEGRADED = "degraded"
    RECOVERING = "recovering"
    UNKNOWN = "unknown"


class AuditSeverity(str, Enum):
    """Audit severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class DiagnosticType(str, Enum):
    """Diagnostic types"""
    REASONING = "reasoning"
    COHERENCE = "coherence"
    SEMANTIC = "semantic"
    EXECUTION = "execution"
    DISTRIBUTION = "distribution"
    ADAPTATION = "adaptation"


class ReconciliationStatus(str, Enum):
    """Reconciliation status"""
    SYNCED = "synced"
    PENDING = "pending"
    CONFLICTING = "conflicting"
    RESOLVING = "resolving"


class PredictionHorizon(str, Enum):
    """Prediction horizon for cognition forecasting"""
    IMMEDIATE = "immediate"      # < 5 minutes
    NEAR_TERM = "near_term"      # 5-30 minutes
    SHORT = "short"             # 30min - 2h
    MEDIUM = "medium"           # 2-8h


class GovernanceAlignment(str, Enum):
    """Governance alignment status"""
    ALIGNED = "aligned"
    MISALIGNED = "misaligned"
    DEVIATING = "deviating"
    PENDING_REVIEW = "pending_review"


# ---- Meta-Cognition Diagnostics ----

class CognitionDiagnostics(BaseModel):
    """
    Runtime cognition diagnostics - tracks cognitive health metrics.
    
    Provides insight into the current state of cognitive processes
    including reasoning quality, coherence, and adaptation effectiveness.
    """
    __tablename__ = "cognition_diagnostics"
    __table_args__ = (
        Index("ix_cog_diag_scope_time", "scope", "assessed_at"),
        Index("ix_cog_diag_state", "cognition_state"),
    )

    # Diagnostics identification
    diagnostic_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Scope and domain
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Cognitive state
    cognition_state: Mapped[str] = mapped_column(String(20), default=CognitionState.HEALTHY.value, index=True)
    
    # Diagnostic metrics
    reasoning_quality: Mapped[float] = mapped_column(Float, default=1.0)
    coherence_score: Mapped[float] = mapped_column(Float, default=1.0)
    consistency_score: Mapped[float] = mapped_column(Float, default=1.0)
    adaptation_efficiency: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Distribution metrics
    distribution_alignment: Mapped[float] = mapped_column(Float, default=1.0)
    sync_health: Mapped[float] = mapped_column(Float, default=1.0)
    conflict_rate: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Anomaly detection
    detected_anomalies: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    anomaly_severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Recommendations
    recommendations: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    assessed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


# ---- Orchestration Introspection Sessions ----

class IntrospectionSession(BaseModel):
    """
    Orchestration introspection session - runtime self-analysis tracking.
    
    Tracks self-analysis processes that enable the system to understand
    its own reasoning patterns, decision quality, and execution efficiency.
    """
    __tablename__ = "orchestration_introspection_sessions"
    __table_args__ = (
        Index("ix_introspect_session_phase", "phase"),
        Index("ix_introspect_session_exec", "execution_id"),
    )

    # Session identification
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Target context
    execution_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Introspection phase
    phase: Mapped[str] = mapped_column(String(20), default=IntrospectionPhase.INITIALIZING.value, index=True)
    
    # Introspection type
    introspection_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    focus_areas: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    
    # Analysis results
    findings: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    insights: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Performance metrics
    depth_achieved: Mapped[int] = mapped_column(Integer, default=0)
    breadth_achieved: Mapped[int] = mapped_column(Integer, default=0)
    
    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


# ---- Semantic Consistency Audits ----

class SemanticConsistencyAudit(BaseModel):
    """
    Semantic consistency audit - validates semantic coherence across cognition.
    
    Ensures that semantic meaning is preserved and consistently interpreted
    throughout distributed execution contexts.
    """
    __tablename__ = "semantic_consistency_audits"
    __table_args__ = (
        Index("ix_sem_audit_time_kind", "audit_kind", "audited_at"),
        Index("ix_sem_audit_status", "audit_status"),
    )

    # Audit identification
    audit_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Audit type
    audit_kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Audit status
    audit_status: Mapped[str] = mapped_column(String(20), default="passed", index=True)
    severity: Mapped[str] = mapped_column(String(20), default=AuditSeverity.INFO.value, index=True)
    
    # Validation results
    consistency_score: Mapped[float] = mapped_column(Float, default=1.0)
    divergence_detected: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Findings
    violations: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    warnings: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Context
    target_entities: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    validation_rules: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Resolution
    resolution_required: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution_applied: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing
    audited_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


# ---- Adaptive Governance Profiles ----

class AdaptiveGovernanceProfile(BaseModel):
    """
    Adaptive governance profile - cognitive governance rules and policies.
    
    Defines how cognitive processes should be governed, including
    validation thresholds, alignment requirements, and enforcement rules.
    """
    __tablename__ = "adaptive_governance_profiles"
    __table_args__ = (
        Index("ix_gov_profile_scope", "scope"),
        UniqueConstraint("scope", "profile_key", name="uq_gov_profile_scope_key"),
    )

    # Profile identification
    profile_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    profile_key: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Scope and domain
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Governance rules
    validation_thresholds: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    alignment_requirements: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    enforcement_rules: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    
    # Policy configuration
    policy_mode: Mapped[str] = mapped_column(String(20), default="active")
    intervention_level: Mapped[str] = mapped_column(String(20), default="advisory")
    
    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    alignment_status: Mapped[str] = mapped_column(String(20), default=GovernanceAlignment.ALIGNED.value)
    
    # Metrics
    trigger_count: Mapped[int] = mapped_column(Integer, default=0)
    violation_count: Mapped[int] = mapped_column(Integer, default=0)
    last_triggered: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Version
    version: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


# ---- Cognition Reconciliation States ----

class CognitionReconciliationState(BaseModel):
    """
    Cognition reconciliation state - distributed cognition synchronization state.
    
    Tracks the synchronization state of distributed cognition nodes,
    including pending conflicts, reconciliation progress, and sync health.
    """
    __tablename__ = "cognition_reconciliation_states"
    __table_args__ = (
        Index("ix_reconcile_node_scope", "node_id", "scope"),
        Index("ix_reconcile_status", "reconciliation_status"),
    )

    # State identification
    state_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Node context
    node_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Reconciliation status
    reconciliation_status: Mapped[str] = mapped_column(String(20), default=ReconciliationStatus.SYNCED.value, index=True)
    
    # Sync metrics
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sync_version: Mapped[int] = mapped_column(Integer, default=1)
    pending_updates: Mapped[int] = mapped_column(Integer, default=0)
    
    # Conflict tracking
    active_conflicts: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    resolved_conflicts: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Health metrics
    sync_health_score: Mapped[float] = mapped_column(Float, default=1.0)
    latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


# ---- Runtime Self-Awareness Metrics ----

class RuntimeSelfAwarenessMetrics(BaseModel):
    """
    Runtime self-awareness metrics - introspection performance tracking.
    
    Records metrics about the effectiveness and efficiency of
    self-reflection and introspection processes.
    """
    __tablename__ = "runtime_self_awareness_metrics"
    __table_args__ = (
        Index("ix_self_aware_time_scope", "timestamp", "scope"),
        Index("ix_self_aware_session", "session_id"),
    )

    # Metric identification
    metric_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Session context
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    execution_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Introspection metrics
    introspection_depth: Mapped[float] = mapped_column(Float, default=0.0)
    reflection_accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    self_model_accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Performance metrics
    introspection_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    processing_overhead: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Quality metrics
    insight_relevance: Mapped[float] = mapped_column(Float, default=0.0)
    finding_accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Context
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    metadata_: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)
    
    # Timing
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


# ---- Predictive Cognition Forecasts ----

class PredictiveCognitionForecast(BaseModel):
    """
    Predictive cognition forecasts - anticipatory cognition health predictions.
    
    Provides foresight into potential cognition drift, conflicts, and
    misalignment before they occur.
    """
    __tablename__ = "predictive_cognition_forecasts"
    __table_args__ = (
        Index("ix_pred_cog_forecast_time", "predicted_for", "horizon"),
        Index("ix_pred_cog_forecast_kind", "forecast_kind"),
    )

    # Forecast identification
    forecast_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Target
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Forecast type
    forecast_kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    horizon: Mapped[str] = mapped_column(String(20), default=PredictionHorizon.NEAR_TERM.value, index=True)
    
    # Prediction
    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Range
    min_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Evidence
    indicators: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    risk_factors: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Mitigation
    recommended_actions: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), default="low")
    
    # Validation
    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    predicted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timing
    predicted_for: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


# ---- Orchestration Reasoning Lineage ----

class OrchestrationReasoningLineage(BaseModel):
    """
    Orchestration reasoning lineage - traceable reasoning chains.
    
    Records the chain of reasoning decisions made during orchestration,
    enabling analysis, auditing, and improvement of reasoning processes.
    """
    __tablename__ = "orchestration_reasoning_lineage"
    __table_args__ = (
        Index("ix_reasoning_lineage_exec", "execution_id"),
        Index("ix_reasoning_lineage_chain", "lineage_chain"),
    )

    # Lineage identification
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Execution context
    execution_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Reasoning chain
    reasoning_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    inference_pattern: Mapped[str] = mapped_column(String(50), nullable=False)
    lineage_chain: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    chain_position: Mapped[int] = mapped_column(Integer, default=0)
    
    # Reasoning content
    premise: Mapped[str] = mapped_column(Text, nullable=False)
    inference: Mapped[str] = mapped_column(Text, nullable=False)
    conclusion: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Evidence and confidence
    evidence: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    reasoning_depth: Mapped[int] = mapped_column(Integer, default=1)
    
    # Context
    decision_context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    metadata_: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)
    
    # Validation
    validation_result: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Parent lineage (for chain relationships)
    parent_lineage_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


# ---- Cognition Anomaly Registry ----

class CognitionAnomalyRegistry(BaseModel):
    """
    Cognition anomaly registry - detected cognitive anomalies.
    
    Centralized registry of all detected cognitive anomalies,
    their severity, status, and remediation actions.
    """
    __tablename__ = "cognition_anomaly_registry"
    __table_args__ = (
        Index("ix_anomaly_registry_time_type", "detected_at", "anomaly_type"),
        Index("ix_anomaly_registry_status", "status"),
    )

    # Anomaly identification
    anomaly_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Anomaly type
    anomaly_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), default=AuditSeverity.WARNING.value, index=True)
    
    # Target
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Detection data
    detection_method: Mapped[str] = mapped_column(String(50), nullable=False)
    detection_signals: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    expected_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    deviation: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Impact assessment
    impact_scope: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    impact_severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Remediation
    status: Mapped[str] = mapped_column(String(20), default="detected", index=True)
    remediation_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Timing
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


__all__ = [
    "IntrospectionPhase",
    "CognitionState",
    "AuditSeverity",
    "DiagnosticType",
    "ReconciliationStatus",
    "PredictionHorizon",
    "GovernanceAlignment",
    "CognitionDiagnostics",
    "IntrospectionSession",
    "SemanticConsistencyAudit",
    "AdaptiveGovernanceProfile",
    "CognitionReconciliationState",
    "RuntimeSelfAwarenessMetrics",
    "PredictiveCognitionForecast",
    "OrchestrationReasoningLineage",
    "CognitionAnomalyRegistry",
]
