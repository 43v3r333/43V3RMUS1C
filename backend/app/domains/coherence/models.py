"""
Coherence Domain Models - Unified Runtime Identity and Cognitive Continuity.

These models implement the UNIFIED COGNITIVE COHERENCE LAYER:
- Centralized runtime identity architecture
- Persistent orchestration cognition
- Semantic execution graphs
- Autonomous governance infrastructure
- Distributed agent coordination
- Predictive observability

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


class IdentityScope(str, Enum):
    """Runtime identity scope"""
    SYSTEM = "system"
    ORCHESTRATION = "orchestration"
    EXECUTION = "execution"
    AGENT = "agent"
    WORKFLOW = "workflow"
    SESSION = "session"


class LineageEventType(str, Enum):
    """Lineage event types"""
    CREATED = "created"
    STARTED = "started"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ADAPTED = "adapted"
    OPTIMIZED = "optimized"
    GOVERNED = "governed"


class MemoryRetrievalMode(str, Enum):
    """Memory retrieval modes"""
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"
    MIXED = "mixed"
    CONTEXTUAL = "contextual"


class SemanticRelationType(str, Enum):
    """Semantic relation types"""
    DEPENDS_ON = "depends_on"
    PRODUCES = "produces"
    CONSUMES = "consumes"
    TRIGGERS = "triggers"
    GOVERNS = "governs"
    PRECEDES = "precedes"
    SUCCEEDS = "succeeds"
    SIMILAR_TO = "similar_to"
    CONFLICTS_WITH = "conflicts_with"


class TuningStrategy(str, Enum):
    """Tuning strategies"""
    GRADIENT_ASCENT = "gradient_ascent"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    HEURISTIC_SEARCH = "heuristic_search"
    GENETIC_ALGORITHM = "genetic_algorithm"


class PolicySeverity(str, Enum):
    """Policy violation severity"""
    INFO = "info"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"
    BLOCKING = "blocking"


class StabilityStatus(str, Enum):
    """Orchestration stability status"""
    STABLE = "stable"
    MARGINAL = "marginal"
    DEGRADING = "degrading"
    UNSTABLE = "unstable"
    CRITICAL = "critical"


class ConsensusState(str, Enum):
    """Agent consensus state"""
    PENDING = "pending"
    VOTING = "voting"
    CONSENSUS_REACHED = "consensus_reached"
    CONFLICT = "conflict"
    DISSOLVED = "dissolved"


class ExecutionHorizon(str, Enum):
    """Execution forecast horizon"""
    IMMEDIATE = "immediate"
    NEAR_TERM = "near_term"
    SHORT = "short"
    MEDIUM = "medium"
    EXTENDED = "extended"


# ---------------------------------------------------------------------------
# Identity & Lineage
# ---------------------------------------------------------------------------


class RuntimeIdentity(BaseModel):
    """Unified runtime identity model.
    
    Centralizes execution identity across the platform. Every workflow,
    execution, agent, and session has a consistent UUID-based identity
    that propagates through the entire orchestration fabric.
    """
    __tablename__ = "runtime_identities"
    __table_args__ = (
        UniqueConstraint("identity_scope", "identity_key", name="uq_runtime_identity_scope_key"),
        Index("ix_runtime_identity_scope_status", "identity_scope", "lifecycle_state"),
        Index("ix_runtime_identity_parent", "parent_id"),
        Index("ix_runtime_identity_correlation", "correlation_id"),
    )

    identity_scope: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    identity_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Hierarchy
    parent_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    root_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    
    # Metadata
    properties: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    capabilities: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    
    # Lifecycle
    lifecycle_state: Mapped[str] = mapped_column(String(32), nullable=False, default="active", index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    # Auditing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class OrchestrationLineage(BaseModel):
    """Orchestration lineage model.
    
    Tracks the complete execution lineage of workflows, preserving
    the chain of decisions, adaptations, and outcomes for audit
    and continuity.
    """
    __tablename__ = "orchestration_lineages"
    __table_args__ = (
        Index("ix_lineage_root", "root_identity_id"),
        Index("ix_lineage_correlation", "correlation_id"),
        Index("ix_lineage_status", "status"),
    )

    root_identity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Lineage info
    lineage_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    
    # Nodes and edges stored as JSON for flexibility
    nodes: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    edges: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    
    # Metrics
    total_nodes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class ExecutionLineageNode(BaseModel):
    """Execution lineage node model.
    
    Individual nodes in the execution lineage representing
    specific events, decisions, or states.
    """
    __tablename__ = "execution_lineage_nodes"
    __table_args__ = (
        Index("ix_lineage_node_identity", "identity_id"),
        Index("ix_lineage_node_event_type", "event_type"),
        Index("ix_lineage_node_timestamp", "timestamp"),
    )

    lineage_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("orchestration_lineages.id", ondelete="CASCADE"), nullable=False, index=True)
    identity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("runtime_identities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Node info
    node_id: Mapped[str] = mapped_column(String(100), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Data
    event_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    state_before: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    state_after: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Context
    parent_node_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Timing
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class RuntimeContext(BaseModel):
    """Runtime context propagation model.
    
    Tracks distributed context propagation across the platform,
    enabling coherent state sharing between services and agents.
    """
    __tablename__ = "runtime_contexts"
    __table_args__ = (
        UniqueConstraint("context_key", "context_scope", name="uq_runtime_context_key_scope"),
        Index("ix_runtime_context_identity", "identity_id"),
        Index("ix_runtime_context_expiry", "expires_at"),
    )

    identity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("runtime_identities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    context_key: Mapped[str] = mapped_column(String(255), nullable=False)
    context_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Value
    value: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    value_type: Mapped[str] = mapped_column(String(50), nullable=False, default="json")
    
    # Propagation
    propagation_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sources: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    
    # Lifecycle
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_mutable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Expiry
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


# ---------------------------------------------------------------------------
# Cognitive Memory
# ---------------------------------------------------------------------------


class CognitiveMemoryItem(BaseModel):
    """Cognitive memory item model.
    
    Persistent orchestration cognition with importance, recency,
    and confidence scoring for intelligent retrieval.
    """
    __tablename__ = "cognitive_memory_items"
    __table_args__ = (
        Index("ix_cog_memory_scope_kind", "scope", "memory_kind"),
        Index("ix_cog_memory_importance", "importance"),
        Index("ix_cog_memory_identity", "identity_id"),
        Index("ix_cog_memory_correlation", "correlation_id"),
    )

    identity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("runtime_identities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Classification
    scope: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # episodic, semantic, procedural, evaluative, strategic
    memory_kind: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    
    # Content
    subject: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Ranking
    importance: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    recency: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    
    # Access
    access_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Lifecycle
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    agent_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class MemoryFragment(BaseModel):
    """Memory fragment model.
    
    Granular memory fragments that can be assembled into
    coherent context for agent reasoning.
    """
    __tablename__ = "memory_fragments"
    __table_args__ = (
        Index("ix_mem_fragment_memory", "memory_id"),
        Index("ix_mem_fragment_order", "fragment_order"),
    )

    memory_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("cognitive_memory_items.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Fragment
    fragment_id: Mapped[str] = mapped_column(String(100), nullable=False)
    fragment_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Content
    fragment_type: Mapped[str] = mapped_column(String(50), nullable=False)  # observation, decision, action, result, insight
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    
    # Context
    context_tags: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)


class ContextSnapshot(BaseModel):
    """Context snapshot model.
    
    Captured snapshots of runtime context for replay,
    analysis, and continuity restoration.
    """
    __tablename__ = "context_snapshots"
    __table_args__ = (
        Index("ix_ctx_snapshot_identity", "identity_id"),
        Index("ix_ctx_snapshot_purpose", "purpose"),
        Index("ix_ctx_snapshot_created", "created_at"),
    )

    identity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("runtime_identities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Snapshot info
    snapshot_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    purpose: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Content
    context_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    memory_items: Mapped[List[UUID]] = mapped_column(JSON, nullable=False, default=list)
    active_identities: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    
    # Metrics
    item_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    data_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


# ---------------------------------------------------------------------------
# Semantic Execution
# ---------------------------------------------------------------------------


class SemanticExecutionGraph(BaseModel):
    """Semantic execution graph model.
    
    Platform-wide semantic coordination of execution relationships,
    enabling intelligent dependency mapping and workflow cognition.
    """
    __tablename__ = "semantic_execution_graphs"
    __table_args__ = (
        Index("ix_sem_graph_identity", "identity_id"),
        Index("ix_sem_graph_status", "lifecycle_state"),
    )

    identity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("runtime_identities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Graph info
    graph_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Structure
    nodes: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    edges: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    
    # Metrics
    node_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    edge_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    semantic_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Lifecycle
    lifecycle_state: Mapped[str] = mapped_column(String(32), nullable=False, default="active", index=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class SemanticNode(BaseModel):
    """Semantic node model.
    
    Individual nodes in semantic execution graphs with
    relationship metadata and semantic properties.
    """
    __tablename__ = "semantic_nodes"
    __table_args__ = (
        Index("ix_sem_node_graph", "graph_id"),
        Index("ix_sem_node_type", "node_type"),
        Index("ix_sem_node_semantic_key", "semantic_key"),
    )

    graph_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("semantic_execution_graphs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Node info
    node_key: Mapped[str] = mapped_column(String(255), nullable=False)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    semantic_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Properties
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    properties: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    tags: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    
    # Semantics
    semantic_type: Mapped[str] = mapped_column(String(50), nullable=False, default="execution")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    
    # Position
    position_x: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


class SemanticEdge(BaseModel):
    """Semantic edge model.
    
    Semantic relationships between execution nodes with
    confidence, weight, and evidence tracking.
    """
    __tablename__ = "semantic_edges"
    __table_args__ = (
        UniqueConstraint("source_id", "target_id", "relation_type", name="uq_semantic_edge_triplet"),
        Index("ix_sem_edge_graph", "graph_id"),
        Index("ix_sem_edge_relation", "relation_type"),
    )

    graph_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("semantic_execution_graphs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    source_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("semantic_nodes.id", ondelete="CASCADE"), nullable=False)
    target_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("semantic_nodes.id", ondelete="CASCADE"), nullable=False)
    
    # Edge info
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Weight and confidence
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    
    # Evidence
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    attributes: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    
    # Lifecycle
    lifecycle_state: Mapped[str] = mapped_column(String(32), nullable=False, default="active", index=True)
    last_reinforced_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# Adaptive Runtime
# ---------------------------------------------------------------------------


class AdaptiveProfile(BaseModel):
    """Adaptive runtime profile model.
    
    Self-optimizing execution profiles that track performance,
    tuning history, and optimization outcomes.
    """
    __tablename__ = "adaptive_profiles"
    __table_args__ = (
        UniqueConstraint("profile_key", "context_key", name="uq_adaptive_profile_key_context"),
        Index("ix_adaptive_profile_identity", "identity_id"),
        Index("ix_adaptive_profile_state", "profile_state"),
    )

    identity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("runtime_identities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Profile info
    profile_key: Mapped[str] = mapped_column(String(255), nullable=False)
    context_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Parameters
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    baseline_metrics: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    current_metrics: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    
    # Optimization
    tuning_strategy: Mapped[str] = mapped_column(String(50), nullable=False, default=TuningStrategy.GRADIENT_ASCENT.value)
    optimization_iterations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    best_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # State
    profile_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    last_tuned_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class OptimizationMetric(BaseModel):
    """Optimization metric model.
    
    Tracks optimization metrics and improvement trends
    for self-tuning execution systems.
    """
    __tablename__ = "optimization_metrics"
    __table_args__ = (
        Index("ix_opt_metric_profile", "profile_id"),
        Index("ix_opt_metric_type", "metric_type"),
        Index("ix_opt_metric_timestamp", "timestamp"),
    )

    profile_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("adaptive_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Metric info
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Value
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    delta: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Context
    iteration: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Tags
    tags: Mapped[Dict[str, str]] = mapped_column(JSON, nullable=False, default=dict)


class ExecutionTuningHistory(BaseModel):
    """Execution tuning history model.
    
    Records of all tuning operations and their outcomes
    for continuous optimization improvement.
    """
    __tablename__ = "execution_tuning_history"
    __table_args__ = (
        Index("ix_tune_history_profile", "profile_id"),
        Index("ix_tune_history_strategy", "strategy"),
        Index("ix_tune_history_timestamp", "timestamp"),
    )

    profile_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("adaptive_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Tuning info
    tuning_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    strategy: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Parameters
    parameters_before: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    parameters_after: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Results
    score_before: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    score_after: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    improvement_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Context
    trigger_reason: Mapped[str] = mapped_column(String(255), nullable=False)
    is_applied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


# ---------------------------------------------------------------------------
# Governance
# ---------------------------------------------------------------------------


class GovernancePolicy(BaseModel):
    """Governance policy model.
    
    Autonomous governance policies with enforcement rules,
    severity levels, and violation tracking.
    """
    __tablename__ = "governance_policies"
    __table_args__ = (
        UniqueConstraint("policy_key", "version", name="uq_governance_policy_key_version"),
        Index("ix_gov_policy_scope", "policy_scope"),
        Index("ix_gov_policy_state", "lifecycle_state"),
    )

    policy_key: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Policy info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    policy_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Rules
    conditions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    enforcement_action: Mapped[str] = mapped_column(String(50), nullable=False)
    action_config: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    
    # Severity
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default=PolicySeverity.WARNING.value)
    
    # Lifecycle
    lifecycle_state: Mapped[str] = mapped_column(String(32), nullable=False, default="active", index=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Usage
    trigger_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    violation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class PolicyViolation(BaseModel):
    """Policy violation model.
    
    Tracks policy violations for audit, analysis,
    and adaptive governance improvement.
    """
    __tablename__ = "policy_violations"
    __table_args__ = (
        Index("ix_policy_violation_policy", "policy_id"),
        Index("ix_policy_violation_severity", "severity"),
        Index("ix_policy_violation_identity", "identity_id"),
        Index("ix_policy_violation_timestamp", "detected_at"),
    )

    policy_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("governance_policies.id", ondelete="CASCADE"), nullable=False, index=True)
    identity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("runtime_identities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Violation info
    violation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Details
    violation_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    
    # Resolution
    enforcement_action: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Detection
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class ArbitrationRecord(BaseModel):
    """Arbitration record model.
    
    Records of orchestration arbitration decisions
    for conflict resolution and governance.
    """
    __tablename__ = "arbitration_records"
    __table_args__ = (
        Index("ix_arb_record_identity", "identity_id"),
        Index("ix_arb_record_type", "arbitration_type"),
        Index("ix_arb_record_timestamp", "decided_at"),
    )

    identity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("runtime_identities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Arbitration info
    record_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    arbitration_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Parties
    parties: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    decision: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Reasoning
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    
    # Execution
    enforcement_actions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    executed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Timing
    decided_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


# ---------------------------------------------------------------------------
# Stability & Prediction
# ---------------------------------------------------------------------------


class OrchestrationStabilityMetrics(BaseModel):
    """Orchestration stability metrics model.
    
    Real-time stability metrics for predictive governance
    and self-healing orchestration.
    """
    __tablename__ = "orchestration_stability_metrics"
    __table_args__ = (
        Index("ix_stability_identity", "identity_id"),
        Index("ix_stability_status", "stability_status"),
        Index("ix_stability_timestamp", "recorded_at"),
    )

    identity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("runtime_identities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Metrics
    stability_status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Performance metrics
    throughput: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    latency_p50: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    latency_p95: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    latency_p99: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Error metrics
    error_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Resource metrics
    cpu_usage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    memory_usage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Stability score
    stability_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    health_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    
    # Timing
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    window_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class ExecutionForecast(BaseModel):
    """Execution forecast model.
    
    Predictive execution forecasts for resource planning,
    anomaly prevention, and optimization.
    """
    __tablename__ = "execution_forecasts"
    __table_args__ = (
        Index("ix_forecast_subject", "subject_kind", "subject_key"),
        Index("ix_forecast_horizon", "horizon"),
        Index("ix_forecast_state", "forecast_state"),
    )

    forecast_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    
    # Subject
    subject_kind: Mapped[str] = mapped_column(String(50), nullable=False)
    subject_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Forecast
    forecast_kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # duration, resource_need, failure_probability, queue_time
    horizon: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Values
    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    
    # Range
    min_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Model
    features: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Validation
    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    prediction_error: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timing
    predicted_for: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Lifecycle
    forecast_state: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")


class AnomalyDetection(BaseModel):
    """Anomaly detection model.
    
    Tracks detected anomalies for pattern analysis
    and predictive prevention.
    """
    __tablename__ = "anomaly_detections"
    __table_args__ = (
        Index("ix_anomaly_identity", "identity_id"),
        Index("ix_anomaly_type", "anomaly_type"),
        Index("ix_anomaly_severity", "severity"),
        Index("ix_anomaly_timestamp", "detected_at"),
    )

    identity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("runtime_identities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Anomaly info
    anomaly_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    anomaly_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    baseline: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False)
    observed: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False)
    deviation: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Context
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Resolution
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Detection
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


# ---------------------------------------------------------------------------
# Distributed Coordination
# ---------------------------------------------------------------------------


class DistributedContextState(BaseModel):
    """Distributed context state model.
    
    Tracks distributed context synchronization across
    agents and services for coherent coordination.
    """
    __tablename__ = "distributed_context_states"
    __table_args__ = (
        UniqueConstraint("context_key", "partition_key", name="uq_distributed_context_key_partition"),
        Index("ix_dist_ctx_identity", "identity_id"),
        Index("ix_dist_ctx_state", "consensus_state"),
    )

    identity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("runtime_identities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Context key
    context_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    partition_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # State
    state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Nodes
    participating_nodes: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    node_versions: Mapped[Dict[str, int]] = mapped_column(JSON, nullable=False, default=dict)
    
    # Consensus
    consensus_state: Mapped[str] = mapped_column(String(20), nullable=False, default=ConsensusState.PENDING.value)
    consensus_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Lifecycle
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class AgentConsensus(BaseModel):
    """Agent consensus model.
    
    Tracks agent consensus decisions for coordinated
    reasoning and execution.
    """
    __tablename__ = "agent_consensus"
    __table_args__ = (
        Index("ix_consensus_topic", "topic_kind", "topic_key"),
        Index("ix_consensus_state", "consensus_state"),
        Index("ix_consensus_timestamp", "created_at"),
    )

    consensus_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    
    # Topic
    topic_kind: Mapped[str] = mapped_column(String(50), nullable=False)
    topic_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Decision
    decision: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Voting
    votes: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    required_votes: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    gathered_votes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # State
    consensus_state: Mapped[str] = mapped_column(String(20), nullable=False, default=ConsensusState.PENDING.value)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    
    # Expiry
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class AuthorityDelegation(BaseModel):
    """Authority delegation model.
    
    Manages authority delegation between agents for
    execution diplomacy and coordinated planning.
    """
    __tablename__ = "authority_delegations"
    __table_args__ = (
        UniqueConstraint("delegator_id", "delegate_id", "authority_type", name="uq_authority_delegation_triplet"),
        Index("ix_delegation_delegator", "delegator_id"),
        Index("ix_delegation_delegate", "delegate_id"),
        Index("ix_delegation_state", "delegation_state"),
    )

    delegation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    
    # Parties
    delegator_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    delegate_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Authority
    authority_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    scope: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    
    # Constraints
    constraints: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    max_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    current_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # State
    delegation_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    revocation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Usage
    invocation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


__all__ = [
    # Enums
    "IdentityScope",
    "LineageEventType",
    "MemoryRetrievalMode",
    "SemanticRelationType",
    "TuningStrategy",
    "PolicySeverity",
    "StabilityStatus",
    "ConsensusState",
    "ExecutionHorizon",
    
    # Identity & Lineage
    "RuntimeIdentity",
    "OrchestrationLineage",
    "ExecutionLineageNode",
    "RuntimeContext",
    
    # Cognitive Memory
    "CognitiveMemoryItem",
    "MemoryFragment",
    "ContextSnapshot",
    
    # Semantic Execution
    "SemanticExecutionGraph",
    "SemanticNode",
    "SemanticEdge",
    
    # Adaptive Runtime
    "AdaptiveProfile",
    "OptimizationMetric",
    "ExecutionTuningHistory",
    
    # Governance
    "GovernancePolicy",
    "PolicyViolation",
    "ArbitrationRecord",
    
    # Stability & Prediction
    "OrchestrationStabilityMetrics",
    "ExecutionForecast",
    "AnomalyDetection",
    
    # Distributed Coordination
    "DistributedContextState",
    "AgentConsensus",
    "AuthorityDelegation",
]