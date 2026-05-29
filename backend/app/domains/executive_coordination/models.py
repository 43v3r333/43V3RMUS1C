"""
Executive Coordination Domain - Recursive Executive Coordination Layer.

This module implements the EXECUTIVE NERVOUS SYSTEM of the platform:

RECURSIVE SUPERVISION ENGINE:
- Recursive cognition supervisors
- Orchestration oversight runtime
- Governance coordination engine
- Adaptive hierarchy management

ORCHESTRATION ARBITRATION SYSTEM:
- Orchestration arbitration engine
- Cognition conflict resolution
- Semantic policy reconciliation
- Adaptive governance balancing

HIERARCHICAL STABILIZATION SYSTEMS:
- Stabilization priority hierarchies
- Orchestration recovery governance
- Adaptive escalation systems
- Runtime coherence balancing

EXECUTIVE COORDINATION FABRIC:
- Executive cognition fabric
- Orchestration hierarchy mapping
- Distributed governance coordination
- Adaptive reasoning synchronization

PREDICTIVE RECURSIVE DIAGNOSTICS:
- Recursive instability forecasting
- Governance cascade detection
- Semantic collapse prediction
- Orchestration coherence forecasting

Every record is UUID-keyed, indexed, and lifecycle-stamped via BaseModel.
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
    ForeignKey,
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


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class SupervisionLevel(int, Enum):
    """Recursive supervision depth levels - higher = deeper oversight."""
    SURFACE = 0      # Surface-level observation
    OBSERVER = 1     # Passive monitoring
    ADVISOR = 2      # Advisory supervision
    REVIEWER = 3      # Active review
    COORDINATOR = 4  # Orchestration coordination
    GOVERNOR = 5     # Governance oversight
    MASTER = 6       # Full recursive control


class SupervisionState(str, Enum):
    """Supervision session state."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    RECOVERING = "recovering"
    STABILIZED = "stabilized"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"


class ArbitrationScope(str, Enum):
    """Arbitration scope types."""
    ATOMIC = "atomic"                    # Single resource contention
    COMPOSITE = "composite"             # Multi-resource conflicts
    SEMANTIC = "semantic"                # Meaning-level conflicts
    GOVERNOR = "governor"                # Governance-level conflicts
    SYSTEMIC = "systemic"               # System-wide conflicts


class ArbitrationState(str, Enum):
    """Arbitration state."""
    DETECTED = "detected"
    EVALUATING = "evaluating"
    ARBITRATING = "arbitrating"
    RESOLVING = "resolving"
    RECONCILED = "reconciled"
    ESCALATED = "escalated"
    DISMISSED = "dismissed"


class StabilizationTier(str, Enum):
    """Stabilization hierarchy tiers."""
    TIER_0_HEALTHY = "tier_0_healthy"     # Optimal operation
    TIER_1_MARGINAL = "tier_1_marginal"  # Minor fluctuations
    TIER_2_DEGRADING = "tier_2_degrading" # Visible degradation
    TIER_3_UNSTABLE = "tier_3_unstable" # Instability detected
    TIER_4_CRITICAL = "tier_4_critical"  # System intervention required
    TIER_5_COLLAPSE = "tier_5_collapse"  # Emergency protocols


class StabilizationAction(str, Enum):
    """Stabilization action types."""
    MONITOR = "monitor"
    BALANCE = "balance"
    RESTRICT = "restrict"
    ISOLATE = "isolate"
    ROLLBACK = "rollback"
    RESET = "reset"
    EMERGENCY = "emergency"


class CoordinationTopology(str, Enum):
    """Executive coordination topology types."""
    HIERARCHICAL = "hierarchical"
    MESH = "mesh"
    FEDERATED = "federated"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"


class CoordinationState(str, Enum):
    """Coordination state."""
    DISCONNECTED = "disconnected"
    SYNCING = "syncing"
    SYNCHRONIZED = "synchronized"
    CONFLICTING = "conflicting"
    COHERENT = "coherent"


class CoherenceMetric(str, Enum):
    """Systemic coherence metric types."""
    SEMANTIC = "semantic"
    EXECUTION = "execution"
    GOVERNANCE = "governance"
    ORCHESTRATION = "orchestration"
    DISTRIBUTION = "distribution"
    TEMPORAL = "temporal"


class BalanceStrategy(str, Enum):
    """Hierarchy balancing strategies."""
    EQUALIZE = "equalize"
    PRIORITIZE = "prioritize"
    WEIGHT = "weight"
    DISTRIBUTE = "distribute"
    CONSOLIDATE = "consolidate"


class DiagnosticsHorizon(str, Enum):
    """Diagnostics forecast horizon."""
    INSTANTANEOUS = "instantaneous"     # 0-1 minute
    NEAR = "near"                      # 1-15 minutes
    SHORT = "short"                    # 15-60 minutes
    MEDIUM = "medium"                  # 1-4 hours
    LONG = "long"                      # 4+ hours


class AnomalySeverity(str, Enum):
    """Anomaly severity classification."""
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ReconciliationState(str, Enum):
    """Governance reconciliation state."""
    ALIGNED = "aligned"
    DEVIATING = "deviating"
    CONFLICTING = "conflicting"
    RECONCILING = "reconciling"
    BALANCED = "balanced"


# ---------------------------------------------------------------------------
# Recursive Supervision Sessions
# ---------------------------------------------------------------------------


class RecursiveSupervisionSession(BaseModel):
    """
    Recursive supervision session - tracks active cognition supervision.

    Implements recursive cognition supervisors with multiple oversight levels,
    enabling deep introspection and self-correction capabilities.
    """
    __tablename__ = "recursive_supervision_sessions"
    __table_args__ = (
        UniqueConstraint("session_key", name="uq_supervision_session_key"),
        Index("ix_supervision_session_state", "supervision_state"),
        Index("ix_supervision_session_supervisor", "supervisor_id"),
        Index("ix_supervision_session_scope", "scope"),
        Index("ix_supervision_session_started", "started_at"),
    )

    # Session identification
    session_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    supervisor_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Supervision hierarchy
    supervision_level: Mapped[int] = mapped_column(Integer, nullable=False, default=SupervisionLevel.ADVISOR.value)
    parent_session_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    root_session_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    recursion_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Target
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_snapshot: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # State
    supervision_state: Mapped[str] = mapped_column(String(20), nullable=False, default=SupervisionState.PENDING.value, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Findings
    findings: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    violations: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # Metrics
    metrics_evaluated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    issues_detected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    remediation_cycles: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Escalation
    escalated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    escalated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    escalated_to: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class SupervisionArtifact(BaseModel):
    """
    Supervision artifact - captures supervision session outputs.

    Stores knowledge artifacts generated during recursive supervision
    for future reference and consistency.
    """
    __tablename__ = "supervision_artifacts"
    __table_args__ = (
        Index("ix_artifact_session", "session_id"),
        Index("ix_artifact_type", "artifact_type"),
        Index("ix_artifact_scope", "scope"),
    )

    # Session reference
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("recursive_supervision_sessions.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    # Artifact identification
    artifact_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Importance
    importance: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    applicability: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Lifecycle
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Usage tracking
    access_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_accessed: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Expiry
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)


# ---------------------------------------------------------------------------
# Orchestration Arbitration States
# ---------------------------------------------------------------------------


class OrchestrationArbitrationState(BaseModel):
    """
    Orchestration arbitration state - tracks active arbitration processes.

    Implements an orchestration arbitration engine for cognition conflicts,
    semantic policy reconciliation, and adaptive governance balancing.
    """
    __tablename__ = "orchestration_arbitration_states"
    __table_args__ = (
        UniqueConstraint("arbitration_key", name="uq_arbitration_key"),
        Index("ix_arbitration_state", "arbitration_state"),
        Index("ix_arbitration_scope", "scope"),
        Index("ix_arbitration_priority", "priority"),
        Index("ix_arbitration_detected", "detected_at"),
    )

    # Arbitration identification
    arbitration_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)

    # Arbitration scope type
    arbitration_scope: Mapped[str] = mapped_column(String(20), nullable=False, default=ArbitrationScope.ATOMIC.value)

    # State
    arbitration_state: Mapped[str] = mapped_column(String(20), nullable=False, default=ArbitrationState.DETECTED.value, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Conflict parties
    parties: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    party_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Conflict details
    conflict_type: Mapped[str] = mapped_column(String(50), nullable=False)
    conflict_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    conflicting_claims: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)

    # Resolution
    resolution_strategy: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    resolution_output: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    winning_party: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    merge_output: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Metrics
    negotiation_rounds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    proposals_evaluated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Escalation
    escalation_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    escalated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    escalated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timing
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolution_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    lineage_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)


class ArbitrationPolicy(BaseModel):
    """
    Arbitration policy - configurable conflict resolution policies.

    Defines how different types of conflicts are resolved based on
    scope, priority, and strategic configuration.
    """
    __tablename__ = "arbitration_policies"
    __table_args__ = (
        UniqueConstraint("policy_key", name="uq_arbitration_policy_key"),
        Index("ix_arb_policy_scope", "scope"),
        Index("ix_arb_policy_active", "is_active"),
        Index("ix_arb_policy_priority", "priority"),
    )

    # Policy identification
    policy_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Scope
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    scope_type: Mapped[str] = mapped_column(String(20), nullable=False, default=ArbitrationScope.ATOMIC.value)

    # Configuration
    strategy: Mapped[str] = mapped_column(String(50), nullable=False)
    strategy_config: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Constraints
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    max_rounds: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    timeout_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=30000)
    escalation_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    # Fallback
    fallback_strategy: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fallback_policy_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Activation
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Usage metrics
    invocation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


# ---------------------------------------------------------------------------
# Stabilization Hierarchy Profiles
# ---------------------------------------------------------------------------


class StabilizationHierarchyProfile(BaseModel):
    """
    Stabilization hierarchy profile - layered stabilization infrastructure.

    Implements stabilization priority hierarchies with adaptive escalation
    for runtime coherence balancing.
    """
    __tablename__ = "stabilization_hierarchy_profiles"
    __table_args__ = (
        UniqueConstraint("profile_key", name="uq_stabilization_profile_key"),
        Index("ix_stab_profile_tier", "tier"),
        Index("ix_stab_profile_scope", "scope"),
        Index("ix_stab_profile_state", "state"),
    )

    # Profile identification
    profile_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Tier configuration
    tier: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)

    # Hierarchy chain
    parent_profile_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    child_profile_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    hierarchy_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # State
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    # Thresholds
    thresholds: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    action_thresholds: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Recovery configuration
    recovery_strategy: Mapped[str] = mapped_column(String(50), nullable=False, default=StabilizationAction.MONITOR.value)
    recovery_window_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=60000)
    max_retry_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    # Metrics
    activation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_activated: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class StabilizationEvent(BaseModel):
    """
    Stabilization event - tracks stabilization actions.

    Records each stabilization action taken with detailed metrics
    for recovery governance and adaptive escalation.
    """
    __tablename__ = "stabilization_events"
    __table_args__ = (
        UniqueConstraint("event_key", name="uq_stabilization_event_key"),
        Index("ix_stab_event_profile", "profile_id"),
        Index("ix_stab_event_action", "action"),
        Index("ix_stab_event_target", "target_id"),
        Index("ix_stab_event_detected", "detected_at"),
    )

    # Profile reference
    profile_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("stabilization_hierarchy_profiles.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    # Event identification
    event_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    # Target
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Action
    tier_before: Mapped[str] = mapped_column(String(20), nullable=False)
    tier_after: Mapped[str] = mapped_column(String(20), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # State
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="triggered")
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Context
    drift_detected: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    drift_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    coherence_score_before: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    coherence_score_after: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Timing
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    action_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    lineage_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)


# ---------------------------------------------------------------------------
# Executive Coordination Topology
# ---------------------------------------------------------------------------


class ExecutiveCoordinationTopology(BaseModel):
    """
    Executive coordination topology - centralizes executive orchestration.

    Defines the topology for distributed governance coordination with
    adaptive reasoning synchronization.
    """
    __tablename__ = "executive_coordination_topology"
    __table_args__ = (
        UniqueConstraint("topology_key", name="uq_topology_key"),
        Index("ix_coord_topology_state", "topology_state"),
        Index("ix_coord_topology_scope", "scope"),
    )

    # Topology identification
    topology_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Topology configuration
    topology_type: Mapped[str] = mapped_column(String(20), nullable=False, default=CoordinationTopology.HIERARCHICAL.value)
    
    # Nodes and edges
    nodes: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    edges: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    node_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    edge_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Coordinators
    coordinator_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    primary_coordinator_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # State
    topology_state: Mapped[str] = mapped_column(String(20), nullable=False, default=CoordinationState.SYNCHRONIZED.value, index=True)
    coherence_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Metrics
    message_throughput: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    sync_latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    conflict_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    last_sync: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class CoordinationEdge(BaseModel):
    """
    Coordination edge - connections between coordination nodes.

    Represents communication channels, authority flows, and
    synchronization links between executive components.
    """
    __tablename__ = "coordination_edges"
    __table_args__ = (
        UniqueConstraint("edge_key", name="uq_coord_edge_key"),
        Index("ix_coord_edge_topology", "topology_id"),
        Index("ix_coord_edge_source", "source_id"),
        Index("ix_coord_edge_target", "target_id"),
        Index("ix_coord_edge_state", "state"),
    )

    # Topology reference
    topology_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("executive_coordination_topology.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    # Edge identification
    edge_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    # Connection
    source_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Edge properties
    edge_type: Mapped[str] = mapped_column(String(50), nullable=False)
    bandwidth: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    latency: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # State
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Metrics
    message_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


# ---------------------------------------------------------------------------
# Governance Reconciliation Metrics
# ---------------------------------------------------------------------------


class GovernanceReconciliationMetrics(BaseModel):
    """
    Governance reconciliation metrics - tracks reconciliation processes.

    Monitors governance alignment, conflict detection, and
    policy consistency enforcement.
    """
    __tablename__ = "governance_reconciliation_metrics"
    __table_args__ = (
        UniqueConstraint("metrics_key", name="uq_reconciliation_metrics_key"),
        Index("ix_gov_recon_state", "reconciliation_state"),
        Index("ix_gov_recon_scope", "scope"),
        Index("ix_gov_recon_timestamp", "timestamp"),
    )

    # Metrics identification
    metrics_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Reconciliation state
    reconciliation_state: Mapped[str] = mapped_column(String(20), nullable=False, default=ReconciliationState.ALIGNED.value, index=True)

    # Alignment metrics
    policy_alignment_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    semantic_alignment_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    execution_alignment_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Deviation metrics
    deviation_detected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deviation_magnitude: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    deviation_direction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Conflict metrics
    conflicts_detected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    conflicts_resolved: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    conflicts_escalated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Policy metrics
    policies_evaluated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    policies_violated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    policies_corrected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timing
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


# ---------------------------------------------------------------------------
# Recursive Diagnostics Forecasts
# ---------------------------------------------------------------------------


class RecursiveDiagnosticsForecast(BaseModel):
    """
    Recursive diagnostics forecast - predictive stability analytics.

    Provides foresight into potential instability, governance cascades,
    and semantic collapse before they occur.
    """
    __tablename__ = "recursive_diagnostics_forecasts"
    __table_args__ = (
        UniqueConstraint("forecast_key", name="uq_diagnostics_forecast_key"),
        Index("ix_diag_forecast_target", "target_id"),
        Index("ix_diag_forecast_horizon", "horizon"),
        Index("ix_diag_forecast_kind", "forecast_kind"),
        Index("ix_diag_forecast_validated", "validated_at"),
    )

    # Forecast identification
    forecast_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Forecast type
    forecast_kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    horizon: Mapped[str] = mapped_column(String(20), nullable=False, default=DiagnosticsHorizon.NEAR.value, index=True)

    # Prediction
    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    probability: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Range
    min_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    expected_range: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)

    # Evidence
    indicators: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    risk_factors: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    supporting_evidence: Mapped[List[str]] = mapped_column(JSON, nullable=True)

    # Severity and risk
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default=AnomalySeverity.INFO.value)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="low")

    # Recommended actions
    recommended_actions: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    escalation_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Validation
    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    validated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timing
    predicted_for: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class SystemicAnomalyDetection(BaseModel):
    """
    Systemic anomaly detection - detects system-wide anomalies.

    Monitors for anomalies across orchestration, cognition, and
    governance layers with correlation tracking.
    """
    __tablename__ = "systemic_anomaly_detections"
    __table_args__ = (
        UniqueConstraint("anomaly_key", name="uq_systemic_anomaly_key"),
        Index("ix_sys_anomaly_target", "target_id"),
        Index("ix_sys_anomaly_severity", "severity"),
        Index("ix_sys_anomaly_type", "anomaly_type"),
        Index("ix_sys_anomaly_detected", "detected_at"),
    )

    # Anomaly identification
    anomaly_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Anomaly details
    anomaly_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default=AnomalySeverity.WARNING.value, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Scope
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    affected_components: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    cascade_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Detection
    detection_method: Mapped[str] = mapped_column(String(50), nullable=False)
    detection_signals: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    baseline: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    observed: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    deviation: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Context
    impact_assessment: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Remediation
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="detected")
    remediation_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timing
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


# ---------------------------------------------------------------------------
# Adaptive Hierarchy Balancing
# ---------------------------------------------------------------------------


class AdaptiveHierarchyBalancing(BaseModel):
    """
    Adaptive hierarchy balancing - manages hierarchy rebalancing.

    Implements adaptive hierarchy reconciliation with balance
    strategies for optimal resource distribution.
    """
    __tablename__ = "adaptive_hierarchy_balancing"
    __table_args__ = (
        UniqueConstraint("balancing_key", name="uq_hierarchy_balancing_key"),
        Index("ix_adapt_bal_scope", "scope"),
        Index("ix_adapt_bal_state", "state"),
        Index("ix_adapt_bal_timestamp", "timestamp"),
    )

    # Balancing identification
    balancing_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Strategy
    balance_strategy: Mapped[str] = mapped_column(String(20), nullable=False, default=BalanceStrategy.EQUALIZE.value)
    balance_config: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # State
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    balance_score_before: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    balance_score_after: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Hierarchy components
    hierarchies: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    hierarchy_weights: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    balance_distribution: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Nodes involved
    nodes: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    node_weights: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)

    # Implementation
    changes_required: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    changes_applied: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    rollback_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Metrics
    improvement_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    metrics_evaluated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timing
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


# ---------------------------------------------------------------------------
# Systemic Coherence Lineage
# ---------------------------------------------------------------------------


class SystemicCoherenceLineage(BaseModel):
    """
    Systemic coherence lineage - tracks coherence evolution.

    Records the lineage of systemic coherence events across
    all platform layers for audit and analysis.
    """
    __tablename__ = "systemic_coherence_lineage"
    __table_args__ = (
        UniqueConstraint("lineage_key", name="uq_coherence_lineage_key"),
        Index("ix_coh_lineage_scope", "scope"),
        Index("ix_coh_lineage_composite", "coherence_metric", "timestamp"),
        Index("ix_coh_lineage_timestamp", "timestamp"),
    )

    # Lineage identification
    lineage_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Coherence metric
    coherence_metric: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Values
    coherence_value: Mapped[float] = mapped_column(Float, nullable=False)
    coherence_delta: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    coherence_trend: Mapped[str] = mapped_column(String(20), nullable=False, default="stable")

    # State
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="recorded")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="healthy")

    # Event
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    event_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Correlation
    parent_lineage_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Chain tracking
    chain_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    chain_position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Context
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    tags: Mapped[List[str]] = mapped_column(JSON, nullable=True)

    # Timing
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

__all__ = [
    # Enumerations
    "SupervisionLevel",
    "SupervisionState",
    "ArbitrationScope",
    "ArbitrationState",
    "StabilizationTier",
    "StabilizationAction",
    "CoordinationTopology",
    "CoordinationState",
    "CoherenceMetric",
    "BalanceStrategy",
    "DiagnosticsHorizon",
    "AnomalySeverity",
    "ReconciliationState",

    # Recursive Supervision
    "RecursiveSupervisionSession",
    "SupervisionArtifact",

    # Orchestration Arbitration
    "OrchestrationArbitrationState",
    "ArbitrationPolicy",

    # Stabilization Hierarchy
    "StabilizationHierarchyProfile",
    "StabilizationEvent",

    # Executive Coordination Topology
    "ExecutiveCoordinationTopology",
    "CoordinationEdge",

    # Governance Reconciliation
    "GovernanceReconciliationMetrics",

    # Recursive Diagnostics
    "RecursiveDiagnosticsForecast",
    "SystemicAnomalyDetection",

    # Adaptive Hierarchy
    "AdaptiveHierarchyBalancing",

    # Coherence Lineage
    "SystemicCoherenceLineage",
]
