"""
Constitutional Arbitration Models - Production-grade constitutional arbitration infrastructure

Provides:
- Constitutional arbitration engine
- Recursive governance balancing
- Orchestration policy reconciliation
- Adaptive constitutional alignment
- Distributed safety coordination
- Systemic integrity stabilization

All models support:
- UUID primary keys
- Indexed arbitration lineage
- Temporal reconciliation tracking
- Lifecycle versioning
- Distributed arbitration traceability
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
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from ...models.base import BaseModel


class ArbitrationStrategy(str, Enum):
    """Arbitration strategies"""
    PRIORITY = "priority"
    WEIGHTED = "weighted"
    ROLLBACK = "rollback"
    ESCALATION = "escalation"
    MERGE = "merge"
    RECURSIVE = "recursive"


class ReconciliationState(str, Enum):
    """Reconciliation states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RECONCILED = "reconciled"
    FAILED = "failed"
    DEADLOCKED = "deadlocked"


class ArbitrationSession(BaseModel):
    """
    Arbitration session.
    Tracks arbitration for constitutional decisions.
    """
    __tablename__ = "arbitration_sessions"
    __table_args__ = (
        Index("ix_arb_session_scope", "session_scope"),
        Index("ix_arb_session_state", "session_state"),
        Index("ix_arb_session_parent", "parent_session_id"),
    )

    session_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_key: Mapped[str] = mapped_column(String(255), nullable=False)

    # Scope
    session_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    scope_kind: Mapped[str] = mapped_column(String(50), nullable=False)

    # Hierarchy
    recursion_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_recursion_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    parent_session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Strategy
    strategy: Mapped[str] = mapped_column(String(20), nullable=False, default=ArbitrationStrategy.RECURSIVE.value)
    strategy_config: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Conflicts
    conflicting_policies: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    resolution_path: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # State
    session_state: Mapped[str] = mapped_column(String(20), nullable=False, default=ReconciliationState.PENDING.value, index=True)

    # Results
    coherence_impact: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    success: Mapped[bool] = mapped_column(Boolean, nullable=True)

    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class ReconciliationPolicy(BaseModel):
    """
    Reconciliation policy.
    Defines how conflicts are reconciled.
    """
    __tablename__ = "reconciliation_policies"
    __table_args__ = (
        Index("ix_recon_policy_scope", "policy_scope"),
        Index("ix_recon_policy_type", "policy_type"),
        Index("ix_recon_policy_active", "is_active"),
    )

    policy_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    policy_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    policy_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    policy_key: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Strategy
    default_strategy: Mapped[str] = mapped_column(String(20), nullable=False, default=ArbitrationStrategy.PRIORITY.value)
    strategy_mapping: Mapped[Dict[str, str]] = mapped_column(JSON, nullable=False, default=dict)

    # Rules
    priority_rules: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    weight_mapping: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)

    # State
    policy_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Metrics
    reconciliation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class ConstitutionalLineage(BaseModel):
    """
    Constitutional lineage.
    Tracks evolution of constitutional decisions.
    """
    __tablename__ = "constitutional_lineages"
    __table_args__ = (
        Index("ix_con_lineage_scope", "lineage_scope"),
        Index("ix_con_lineage_parent", "parent_decision_id"),
        Index("ix_con_lineage_timestamp", "created_at"),
    )

    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    lineage_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Decision info
    decision_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    decision_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Parent lineage
    parent_decision_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    root_decision_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Change
    change_type: Mapped[str] = mapped_column(String(50), nullable=False)
    pre_decision: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    post_decision: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Impact
    impact_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class EcosystemSnapshot(BaseModel):
    """
    Ecosystem snapshot.
    Captures ecosystem state at checkpoints.
    """
    __tablename__ = "ecosystem_snapshots"
    __table_args__ = (
        Index("ix_eco_snapshot_session", "session_id"),
        Index("ix_eco_snapshot_timestamp", "captured_at"),
    )

    snapshot_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Snapshot data
    snapshot_key: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Metrics
    coherence_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    stability_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    balance_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Component states
    component_states: Mapped[Dict[str, str]] = mapped_column(JSON, nullable=False, default=dict)
    policy_states: Mapped[Dict[str, bool]] = mapped_column(JSON, nullable=False, default=dict)

    # Violations
    violations_detected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timing
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class BalanceMetric(BaseModel):
    """
    Balance metric.
    Records balance measurements.
    """
    __tablename__ = "balance_metrics"
    __table_args__ = (
        Index("ix_balance_metric_scope", "metric_scope"),
        Index("ix_balance_metric_type", "metric_type"),
        Index("ix_balance_metric_timestamp", "captured_at"),
    )

    metric_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    metric_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Value
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Context
    target_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Assessment
    is_balanced: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timing
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class ArbitrationResult(BaseModel):
    """
    Arbitration result.
    Records arbitration outcomes.
    """
    __tablename__ = "arbitration_results"
    __table_args__ = (
        Index("ix_arb_result_session", "session_id"),
        Index("ix_arb_result_timestamp", "created_at"),
    )

    result_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Decision
    decision_type: Mapped[str] = mapped_column(String(50), nullable=False)
    selected_policy: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rejected_policies: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    # Outcome
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    coherence_impact: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # Details
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


__all__ = [
    "ArbitrationStrategy",
    "ReconciliationState",
    "ArbitrationSession",
    "ReconciliationPolicy",
    "ConstitutionalLineage",
    "EcosystemSnapshot",
    "BalanceMetric",
    "ArbitrationResult",
]
