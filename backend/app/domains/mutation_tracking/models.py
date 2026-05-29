"""
Mutation Tracking Models - Production-grade mutation lineage infrastructure

Provides:
- Orchestration mutation lineage tracking
- Cognition evolution tracing
- Semantic adaptation history
- Runtime behavior evolution tracking
- Recursive adaptation telemetry
- Distributed evolution coordination

All models support:
- UUID primary keys
- Indexed evolution lineage
- Temporal tracking
- Lifecycle versioning
- Distributed mutation traceability
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
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from ...models.base import BaseModel


class MutationSeverity(str, Enum):
    """Mutation severity classification"""
    TRIVIAL = "trivial"      # No functional impact
    MINOR = "minor"          # Minor behavioral change
    MODERATE = "moderate"    # Significant modification
    MAJOR = "major"         # Core functionality change
    CRITICAL = "critical"    # System-breaking mutation
    CATASTROPHIC = "catastrophic"  # Complete system failure


class MutationStatus(str, Enum):
    """Mutation lifecycle status"""
    PROPOSED = "proposed"        # Mutation suggested
    PENDING = "pending"         # Awaiting approval
    APPROVED = "approved"        # Approved for application
    APPLYING = "applying"        # Currently applying
    APPLIED = "applied"          # Successfully applied
    VERIFIED = "verified"        # Verified and stable
    REVERTING = "reverting"      # Rolling back
    REVERTED = "reverted"       # Rolled back to previous state
    REJECTED = "rejected"        # Rejected by policy
    FAILED = "failed"           # Application failed


class AdaptationPhase(str, Enum):
    """Cognition adaptation phases"""
    OBSERVATION = "observation"   # Monitoring for changes
    DETECTION = "detection"      # Change detected
    EVALUATION = "evaluation"    # Evaluating impact
    DECISION = "decision"        # Making adaptation decision
    APPLICATION = "application"  # Applying adaptation
    VALIDATION = "validation"   # Validating results
    INTEGRATION = "integration"  # Integrating into runtime
    STABILIZATION = "stabilization"  # Stabilizing new state


class EvolutionTrajectory(str, Enum):
    """Evolution direction classification"""
    EMERGENT = "emergent"         # Self-organizing evolution
    DIRECTED = "directed"         # Goal-directed evolution
    GRADUAL = "gradual"           # Incremental changes
    RAPID = "rapid"              # Rapid adaptation
    STAGNANT = "stagnant"         # Minimal evolution
    DECLINING = "declining"       # Negative evolution


class OrchestrationMutation(BaseModel):
    """
    Orchestration mutation lineage.
    Tracks the complete evolution history of orchestrations.
    """
    __tablename__ = "orchestration_mutations"
    __table_args__ = (
        Index("ix_orch_mutation_lineage", "lineage_id"),
        Index("ix_orch_mutation_subject", "subject_kind", "subject_key"),
        Index("ix_orch_mutation_status", "mutation_status"),
    )

    mutation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Subject being mutated
    subject_kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subject_key: Mapped[str] = mapped_column(String(255), nullable=False)
    subject_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Mutation details
    mutation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    mutation_category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Pre-mutation state
    pre_mutation_snapshot: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    pre_mutation_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Post-mutation state
    post_mutation_snapshot: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    post_mutation_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Changes
    changes: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    change_scope: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Severity and risk
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default=MutationSeverity.MINOR.value)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    impact_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Rollback capability
    can_revert: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    revert_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    is_reverted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Status and lifecycle
    mutation_status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    lifecycle_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    # Parent lineage
    parent_mutation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    root_mutation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    child_mutation_ids: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    lineage_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Validation
    validation_checks: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    validation_passed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    verification_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timing
    proposed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reverted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Metadata
    actor_type: Mapped[str] = mapped_column(String(50), nullable=False, default="system")
    actor_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    policy_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class CognitionEvolutionTrace(BaseModel):
    """
    Cognition evolution tracing.
    Tracks cognitive process adaptations over time.
    """
    __tablename__ = "cognition_evolution_traces"
    __table_args__ = (
        Index("ix_cog_evolution_reasoning", "reasoning_type"),
        Index("ix_cog_evolution_session", "session_id"),
        Index("ix_cog_evolution_timestamp", "traced_at"),
    )

    trace_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Reasoning context
    reasoning_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    reasoning_phase: Mapped[str] = mapped_column(String(20), nullable=False)
    domain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Trace data
    cognition_snapshot: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    reasoning_context: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Adaptation tracking
    adaptation_phase: Mapped[str] = mapped_column(String(20), nullable=False, default=AdaptationPhase.OBSERVATION.value)
    adaptation_trigger: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    trigger_conditions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Evolution metrics
    coherence_before: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    coherence_after: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    coherence_delta: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    insight_gain: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reasoning_efficiency: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    adaptation_quality: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Trajectory
    trajectory: Mapped[str] = mapped_column(String(20), nullable=False, default=EvolutionTrajectory.GRADUAL.value)
    trajectory_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Parent trace
    parent_trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Timing
    traced_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class SemanticAdaptationEvent(BaseModel):
    """
    Semantic adaptation history.
    Records semantic changes across evolution cycles.
    """
    __tablename__ = "semantic_adaptation_events"
    __table_args__ = (
        Index("ix_semantic_adaptation_subject", "subject_kind", "subject_key"),
        Index("ix_semantic_adaptation_scope", "adaptation_scope"),
        Index("ix_semantic_adaptation_timestamp", "occurred_at"),
    )

    event_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True) 
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Adaptation scope
    adaptation_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subject_kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subject_key: Mapped[str] = mapped_column(String(255), nullable=False)
    subject_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Semantic change
    semantic_type: Mapped[str] = mapped_column(String(50), nullable=False)
    change_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Pre-change
    pre_semantic_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    pre_predicates: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # Post-change
    post_semantic_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    post_predicates: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # Semantic impact
    semantic_distance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    semantic_preservation: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    invariant_violations: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Contract tracking
    contract_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    contract_version_before: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    contract_version_after: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Timing
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    mutation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class RuntimeBehaviorEvolution(BaseModel):
    """
    Runtime behavior evolution tracking.
    Monitors behavioral changes in runtime environments.
    """
    __tablename__ = "runtime_behavior_evolutions"
    __table_args__ = (
        Index("ix_runtime_evolution_instance", "runtime_instance_id"),
        Index("ix_runtime_evolution_behavior", "behavior_kind"),
        Index("ix_runtime_evolution_timestamp", "observed_at"),
    )

    evolution_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    runtime_instance_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Behavior context
    behavior_kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    behavior_category: Mapped[str] = mapped_column(String(50), nullable=False)
    behavior_scope: Mapped[str] = aColumn(String(50), nullable=False, index=True)

    # Pre-evolution behavior
    pre_evolution_behavior: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    pre_metrics: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)

    # Post-evolution behavior
    post_evolution_behavior: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    post_metrics: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)

    # Evolution metrics
    behavioral_drift: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    performance_impact: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    stability_change: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Anomaly detection
    anomalies_detected: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Trigger and cause
    trigger_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    trigger_evidence: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Timing
    observed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    evolution_duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class RecursiveAdaptationTelemetry(BaseModel):
    """
    Recursive adaptation telemetry.
    Tracks nested adaptation cycles for complex orchestrations.
    """
    __tablename__ = "recursive_adaptation_telemetry"
    __table_args__ = (
        Index("ix_recursive_telemetry_session", "session_id"),
        Index("ix_recursive_telemetry_parent", "parent_telemetry_id"),
        Index("ix_recursive_telemetry_timestamp", "captured_at"),
    )

    telemetry_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Recursion tracking
    recursion_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_recursion_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    parent_telemetry_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    root_telemetry_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    child_telemetry_ids: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Adaptation metrics
    adaptation_level: Mapped[str] = mapped_column(String(20), nullable=False)
    adaptation_state: Mapped[str] = mapped_column(String(20), nullable=False)
    adaptation_progress: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Telemetry data
    metrics_snapshot: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    coherence_snapshot: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    efficiency_snapshot: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Nested metrics
    child_metrics: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    aggregate_metrics: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)

    # Timing
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    capture_duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class DistributedMutationCoordination(BaseModel):
    """
    Distributed mutation coordination.
    Coordinates mutations across distributed systems.
    """
    __tablename__ = "distributed_mutation_coordinations"
    __table_args__ = (
        Index("ix_distributed_coordination_batch", "batch_id"),
        Index("ix_distributed_coordination_node", "node_id"),
        Index("ix_distributed_coordination_timestamp", "coordinated_at"),
    )

    coordination_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    batch_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Node tracking
    node_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    node_kind: Mapped[str] = mapped_column(String(50), nullable=False)
    node_role: Mapped[str] = mapped_column(String(50), nullable=False)

    # Coordination metadata
    coordination_type: Mapped[str] = mapped_column(String(50), nullable=False)
    coordination_strategy: Mapped[str] = mapped_column(String(50), nullable=False)
    consensus_algorithm: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Mutation distribution
    mutations_assigned: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    mutations_applied: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    mutations_pending: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    # Node state
    node_state_before: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    node_state_after: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Coordination results
    coordination_success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    consensus_reached: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    final_state_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Timing
    initiated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    coordinated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completion_duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class MutationLineageGraph(BaseModel):
    """
    Mutation lineage graph.
    Represents the complete evolutionary graph of mutations.
    """
    __tablename__ = "mutation_lineage_graphs"
    __table_args__ = (
        Index("ix_lineage_graph_root", "root_mutation_id"),
        Index("ix_lineage_graph_subject", "subject_kind", "subject_key"),
    )

    graph_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Subject
    subject_kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subject_key: Mapped[str] = mapped_column(String(255), nullable=False)

    # Graph structure
    root_mutation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    node_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    edge_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Graph metrics
    graph_diameter: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    branching_factor: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    coherence_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class MutationNode(BaseModel):
    """
    Mutation node in lineage graph.
    Represents a single mutation event.
    """
    __tablename__ = "mutation_nodes"
    __table_args__ = (
        Index("ix_mutation_node_graph", "graph_id"),
        Index("ix_mutation_node_mutation", "mutation_id"),
    )

    node_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    graph_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    mutation_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Node position
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    position_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Node data
    node_type: Mapped[str] = mapped_column(String(50), nullable=False, default="mutation")
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Metrics
    impact_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


class MutationEdge(BaseModel):
    """
    Mutation edge in lineage graph.
    Represents relationships between mutations.
    """
    __tablename__ = "mutation_edges"
    __table_args__ = (
        Index("ix_mutation_edge_graph", "graph_id"),
        Index("ix_mutation_edge_source", "source_node_id"),
        Index("ix_mutation_edge_target", "target_node_id"),
    )

    edge_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    graph_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    source_node_id: Mapped[str] = mapped_column(String(100), nullable=False)
    target_node_id: Mapped[str] = mapped_column(String(100), nullable=False)

    # Edge data
    edge_type: Mapped[str] = mapped_column(String(50), nullable=False)
    relationship: Mapped[str] = mapped_column(String(50), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Path information
    path_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    path_length: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


__all__ = [
    "MutationSeverity",
    "MutationStatus",
    "AdaptationPhase",
    "EvolutionTrajectory",
    "OrchestrationMutation",
    "CognitionEvolutionTrace",
    "SemanticAdaptationEvent",
    "RuntimeBehaviorEvolution",
    "RecursiveAdaptationTelemetry",
    "DistributedMutationCoordination",
    "MutationLineageGraph",
    "MutationNode",
    "MutationEdge",
]
