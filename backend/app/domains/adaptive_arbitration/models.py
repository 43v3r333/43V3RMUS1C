"""
Adaptive Arbitration Models - Production-grade arbitration infrastructure

Provides:
- Adaptation arbitration engine
- Recursive balancing systems
- Semantic evolution reconciliation
- Orchestration adaptation governance
- Distributed mutation coordination
- Systemic evolution stabilization

All models support:
- UUID primary keys
- Indexed arbitration tracking
- Temporal governance tracking
- Lifecycle versioning
- Distributed coordination traceability
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


class BalanceStrategy(str, Enum):
    """Balance strategies for adaptation"""
    CONSERVATIVE = "conservative"      # Minimal changes for stability
    EQUALIZING = "equalizing"         # Balance all components equally
    PRIORITIZED = "prioritized"       # Priority-based distribution
    WEIGHTED = "weighted"             # Weighted by impact
    RECURSIVE = "recursive"           # Self-balancing hierarchy
    ADAPTIVE = "adaptive"             # Dynamic strategy selection


class ArbitrationScope(str, Enum):
    """Arbitration scope levels"""
    LOCAL = "local"                   # Single component
    ORCHESTRATION = "orchestration"    # Orchestration level
    SESSION = "session"               # Session level
    DOMAIN = "domain"                 # Domain level
    SYSTEMIC = "systemic"             # System-wide
    GLOBAL = "global"                 # Complete platform


class ReconciliationState(str, Enum):
    """Semantic reconciliation states"""
    PENDING = "pending"              # Awaiting reconciliation
    IN_PROGRESS = "in_progress"     # Currently reconciling
    RECONCILED = "reconciled"        # Successfully reconciled
    FAILED = "failed"               # Reconciliation failed
    DEADLOCKED = "deadlocked"        # Cannot reconcile


class AdaptationPhase(str, Enum):
    """Adaptation lifecycle phases"""
    DETECTION = "detection"          # Detecting need for adaptation
    EVALUATION = "evaluation"        # Evaluating options
    PROPOSAL = "proposal"            # Proposing adaptations
    ARBITRATION = "arbitration"      # Arbitrating conflicts
    DECISION = "decision"            # Making final decision
    APPLICATION = "application"       # Applying adaptations
    VALIDATION = "validation"        # Validating results
    STABILIZATION = "stabilization"  # Stabilizing new state


class ArbitrationSession(BaseModel):
    """
    Adaptation arbitration session.
    Manages conflict resolution and balance arbitration.
    """
    __tablename__ = "arbitration_sessions"
    __table_args__ = (
        Index("ix_arb_session_scope", "arbitration_scope"),
        Index("ix_arb_session_state", "session_state"),
        Index("ix_arb_session_parent", "parent_session_id"),
    )

    session_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_key: Mapped[str] = mapped_column(String(255), nullable=False)

    # Scope
    arbitration_scope: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    scope_kind: Mapped[str] = mapped_column(String(50), nullable=False)
    scope_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Strategy
    balance_strategy: Mapped[str] = mapped_column(String(20), nullable=False, default=BalanceStrategy.ADAPTIVE.value)
    strategy_config: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Hierarchy
    recursion_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_recursion_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    parent_session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    child_session_ids: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Conflict tracking
    conflicting_adaptations: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    resolution_paths: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    selected_path: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # State
    session_state: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    reconciliation_state: Mapped[str] = mapped_column(String(20), nullable=False, default=ReconciliationState.PENDING.value)

    # Phase
    current_phase: Mapped[str] = mapped_column(String(20), nullable=False, default=AdaptationPhase.DETECTION.value)
    phase_history: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # Results
    balance_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    adaptation_assignments: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    success: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Metrics
    coherence_impact: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    balance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    arbitration_duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class AdaptationBalance(BaseModel):
    """
    Adaptation balance tracking.
    Tracks the balance state across adaptation cycles.
    """
    __tablename__ = "adaptation_balances"
    __table_args__ = (
        Index("ix_adapt_balance_scope", "balance_scope"),
        Index("ix_adapt_balance_timestamp", "captured_at"),
    )

    balance_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Balance scope
    balance_scope: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    scope_components: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    # Balance state
    component_states: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    balance_vector: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    imbalance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Strategy
    strategy_used: Mapped[str] = mapped_column(String(20), nullable=False)
    strategy_params: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Target balance
    target_balance: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    tolerance_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.05)

    # Redistribution
    redistribution_plan: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    redistribution_applied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Timing
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class SemanticReconciliation(BaseModel):
    """
    Semantic reconciliation tracking.
    Tracks semantic alignment across adaptations.
    """
    __tablename__ = "semantic_reconciliations"
    __table_args__ = (
        Index("ix_semantic_recon_scope", "reconciliation_scope"),
        Index("ix_semantic_recon_state", "reconciliation_state"),
        Index("ix_semantic_recon_timestamp", "reconciled_at"),
    )

    reconciliation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Scope
    reconciliation_scope: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    subject_kind: Mapped[str] = mapped_column(String(50), nullable=False)
    subject_key: Mapped[str] = mapped_column(String(255), nullable=False)

    # Pre-reconciliation state
    pre_reconciliation_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    pre_semantic_distance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Post-reconciliation state
    post_reconciliation_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    post_semantic_distance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Reconciliation strategy
    reconciliation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reconciliation_approach: Mapped[str] = mapped_column(String(50), nullable=False)

    # State
    reconciliation_state: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    convergence_achieved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Semantic invariants
    invariants_maintained: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    invariant_violations: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Conflict resolution
    conflicts_resolved: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    conflicts_remaining: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # Timing
    reconciled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, index=True)
    reconciliation_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class OrchestrationAdaptation(BaseModel):
    """
    Orchestration adaptation tracking.
    Tracks adaptation governance for orchestrations.
    """
    __tablename__ = "orchestration_adaptations"
    __table_args__ = (
        Index("ix_orch_adapt_subject", "subject_kind", "subject_key"),
        Index("ix_orch_adapt_state", "adaptation_state"),
        Index("ix_orch_adapt_timestamp", "adapted_at"),
    )

    adaptation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Subject
    subject_kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subject_key: Mapped[str] = mapped_column(String(255), nullable=False)
    subject_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Adaptation details
    adaptation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    adaptation_category: Mapped[str] = mapped_column(String(50), nullable=False)
    adaptation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Pre-adaptation
    pre_adaptation_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    pre_coherence_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Post-adaptation
    post_adaptation_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    post_coherence_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Governance
    governance_level: Mapped[str] = mapped_column(String(20), nullable=False, default="intervention")
    approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    approved_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # State
    adaptation_state: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    is_reverted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Impact
    impact_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    coherence_impact: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Timing
    adapted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class DistributedAdaptationCoordination(BaseModel):
    """
    Distributed adaptation coordination.
    Coordinates adaptations across distributed nodes.
    """
    __tablename__ = "distributed_adaptation_coordinations"
    __table_args__ = (
        Index("ix_dist_coordination_batch", "batch_id"),
        Index("ix_dist_coordination_node", "node_id"),
        Index("ix_dist_coordination_timestamp", "coordinated_at"),
    )

    coordination_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    batch_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Node tracking
    node_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    node_kind: Mapped[str] = mapped_column(String(50), nullable=False)
    node_role: Mapped[str] = mapped_column(String(50), nullable=False)

    # Coordination strategy
    coordination_type: Mapped[str] = mapped_column(String(50), nullable=False)
    consensus_algorithm: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    coordination_phase: Mapped[str] = mapped_column(String(20), nullable=False)

    # Adaptation distribution
    adaptations_assigned: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    adaptations_applied: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    adaptations_pending: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    # State synchronization
    local_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    synchronized_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    state_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Results
    coordination_success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    consensus_reached: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    final_state_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Timing
    initiated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    coordinated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completion_duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class SystemicEvolutionStabilization(BaseModel):
    """
    Systemic evolution stabilization.
    Tracks platform-wide stabilization efforts.
    """
    __tablename__ = "systemic_evolution_stabilizations"
    __table_args__ = (
        Index("ix_sys_stabilization_cycle", "stabilization_cycle"),
        Index("ix_sys_stabilization_state", "stabilization_state"),
        Index("ix_sys_stabilization_timestamp", "started_at"),
    )

    stabilization_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Cycle information
    stabilization_cycle: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    iteration: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_iterations: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

    # Scope
    stabilization_scope: Mapped[str] = mapped_column(String(20), nullable=False)
    affected_components: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    # Systemic state
    pre_stabilization_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    post_stabilization_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Metrics
    coherence_before: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    coherence_after: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    stability_delta: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # State
    stabilization_state: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    stabilization_complete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Interventions
    interventions_applied: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    interventions_planned: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # Convergence
    convergence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    convergence_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.95)

    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


__all__ = [
    "BalanceStrategy",
    "ArbitrationScope",
    "ReconciliationState",
    "AdaptationPhase",
    "ArbitrationSession",
    "AdaptationBalance",
    "SemanticReconciliation",
    "OrchestrationAdaptation",
    "DistributedAdaptationCoordination",
    "SystemicEvolutionStabilization",
]
