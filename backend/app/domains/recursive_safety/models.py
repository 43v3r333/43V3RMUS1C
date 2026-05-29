"""
Recursive Safety Models - Production-grade recursive safety infrastructure

Provides:
- Recursive safety engine
- Orchestration safeguard systems
- Adaptive boundary protection
- Cognition collapse prevention
- Governance conflict mitigation
- Ecosystem stability balancing

All models support:
- UUID primary keys
- Indexed safety lineage
- Temporal protection tracking
- Lifecycle versioning
- Distributed safety traceability
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


class SafetyState(str, Enum):
    """Safety state levels"""
    NOMINAL = "nominal"
    CAUTION = "caution"
    WARNING = "warning"
    CRITICAL = "critical"
    COLLAPSE = "collapse"


class ProtectionLevel(str, Enum):
    """Protection levels"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"
    EMERGENCY = "emergency"


class ConflictResolution(str, Enum):
    """Conflict resolution strategies"""
    PRIORITY = "priority"
    WEIGHTED = "weighted"
    ROLLBACK = "rollback"
    ESCALATION = "escalation"
    MERGE = "merge"


class SafetyProfile(BaseModel):
    """
    Safety profile.
    Defines safety parameters for recursive operations.
    """
    __tablename__ = "safety_profiles"
    __table_args__ = (
        Index("ix_safety_profile_scope", "profile_scope"),
        Index("ix_safety_profile_state", "profile_state"),
        Index("ix_safety_profile_active", "is_active"),
    )

    profile_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    profile_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    profile_key: Mapped[str] = mapped_column(String(255), nullable=False)

    # Safety parameters
    protection_level: Mapped[str] = mapped_column(String(20), nullable=False, default=ProtectionLevel.STANDARD.value)
    
    # Thresholds
    collapse_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.1)
    warning_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.3)
    critical_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    max_recursion_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    max_stack_size: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)

    # Safety margins
    safety_margin: Mapped[float] = mapped_column(Float, nullable=False, default=0.1)
    emergency_shutdown_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.05)

    # State
    profile_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Metrics
    protection_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    collapse_preventions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    safety_interventions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class SafetyBoundary(BaseModel):
    """
    Safety boundary.
    Defines operational boundaries for safety.
    """
    __tablename__ = "safety_boundaries"
    __table_args__ = (
        Index("ix_safety_boundary_scope", "boundary_scope"),
        Index("ix_safety_boundary_type", "boundary_type"),
        Index("ix_safety_boundary_active", "is_active"),
    )

    boundary_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    boundary_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    boundary_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    boundary_key: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Boundary definition
    min_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hard_limit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    soft_limit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Enforcement
    enforcement_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="strict")
    allows_override: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # State
    boundary_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Metrics
    breach_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    validation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class CollapsePrevention(BaseModel):
    """
    Collapse prevention record.
    Tracks collapse prevention measures.
    """
    __tablename__ = "collapse_preventions"
    __table_args__ = (
        Index("ix_collapse_prevention_session", "session_id"),
        Index("ix_collapse_prevention_timestamp", "occurred_at"),
    )

    prevention_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Prevention details
    prevention_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # State
    pre_prevention_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    post_prevention_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Actions taken
    actions_taken: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    rollback_triggered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Effectiveness
    effectiveness: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    recovery_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Timing
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class GovernanceConflict(BaseModel):
    """
    Governance conflict.
    Tracks conflicts between governance rules.
    """
    __tablename__ = "governance_conflicts"
    __table_args__ = (
        Index("ix_gov_conflict_session", "session_id"),
        Index("ix_gov_conflict_state", "conflict_state"),
        Index("ix_gov_conflict_timestamp", "occurred_at"),
    )

    conflict_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Conflict details
    conflict_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Rules in conflict
    conflicting_rules: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    rule_priorities: Mapped[Optional[Dict[str, int]]] = mapped_column(JSON, nullable=True)

    # State
    conflict_state: Mapped[str] = mapped_column(String(20), nullable=False, default="detected", index=True)
    resolution_strategy: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Resolution
    resolution_applied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resolution_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    winning_rule: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Timing
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class StabilitySession(BaseModel):
    """
    Stability session.
    Tracks stability monitoring sessions.
    """
    __tablename__ = "stability_sessions"
    __table_args__ = (
        Index("ix_stability_session_state", "session_state"),
        Index("ix_stability_session_timestamp", "started_at"),
    )

    session_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_key: Mapped[str] = mapped_column(String(255), nullable=False)

    # Scope
    session_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    scope_kind: Mapped[str] = mapped_column(String(50), nullable=False)

    # State
    session_state: Mapped[str] = mapped_column(String(20), nullable=False, default="init", index=True)
    safety_state: Mapped[str] = mapped_column(String(20), nullable=False, default=SafetyState.NOMINAL.value)

    # Metrics
    stability_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    safety_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    conflict_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Interventions
    interventions_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    collapse_preventions_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class SafetyMetric(BaseModel):
    """
    Safety metric.
    Records safety measurements.
    """
    __tablename__ = "safety_metrics"
    __table_args__ = (
        Index("ix_safety_metric_scope", "metric_scope"),
        Index("ix_safety_metric_type", "metric_type"),
        Index("ix_safety_metric_timestamp", "captured_at"),
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
    is_compliant: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timing
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


__all__ = [
    "SafetyState",
    "ProtectionLevel",
    "ConflictResolution",
    "SafetyProfile",
    "SafetyBoundary",
    "CollapsePrevention",
    "GovernanceConflict",
    "StabilitySession",
    "SafetyMetric",
]
