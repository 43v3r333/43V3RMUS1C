"""
Invariant Enforcement Models - Production-grade invariant enforcement infrastructure

Provides:
- Invariant validation runtime
- Orchestration boundary systems
- Semantic integrity constraints
- Recursive consistency enforcement
- Cognition stability guarantees
- Distributed constraint coordination

All models support:
- UUID primary keys
- Indexed invariant lineage
- Temporal constraint tracking
- Lifecycle versioning
- Distributed constraint traceability
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


class InvariantType(str, Enum):
    """Invariant types"""
    SAFETY = "safety"
    CONSISTENCY = "consistency"
    INTEGRITY = "integrity"
    COHERENCE = "coherence"
    TERMINATION = "termination"
    RESOURCE = "resource"
    SEMANTIC = "semantic"
    GOVERNANCE = "governance"


class ViolationSeverity(str, Enum):
    """Violation severity levels"""
    INFO = "info"
    WARNING = "warning"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    BLOCKING = "blocking"


class EnforcementMode(str, Enum):
    """Enforcement modes"""
    STRICT = "strict"
    LENIENT = "lenient"
    AUDIT = "audit"
    DISABLED = "disabled"


class InvariantRegistry(BaseModel):
    """
    Invariant registry.
    Central registry for all invariants.
    """
    __tablename__ = "invariant_registry"
    __table_args__ = (
        Index("ix_invariant_registry_type", "invariant_type"),
        Index("ix_invariant_registry_scope", "invariant_scope"),
        Index("ix_invariant_registry_active", "is_active"),
    )

    invariant_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    invariant_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    invariant_key: Mapped[str] = mapped_column(String(255), nullable=False)
    invariant_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    invariant_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Invariant definition
    invariant_expression: Mapped[str] = mapped_column(Text, nullable=False)
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Enforcement
    enforcement_mode: Mapped[str] = mapped_column(String(20), nullable=False, default=EnforcementMode.STRICT.value)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default=ViolationSeverity.HIGH.value)

    # State
    invariant_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Metrics
    validation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    violation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class InvariantViolation(BaseModel):
    """
    Invariant violation record.
    Tracks all invariant violations.
    """
    __tablename__ = "invariant_violations"
    __table_args__ = (
        Index("ix_invariant_violation_invariant", "invariant_id"),
        Index("ix_invariant_violation_session", "session_id"),
        Index("ix_invariant_violation_severity", "severity"),
        Index("ix_invariant_violation_timestamp", "occurred_at"),
    )

    violation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    invariant_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Violation details
    violation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Context
    violating_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    expected_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    expression: Mapped[str] = mapped_column(Text, nullable=False)

    # Resolution
    resolution_state: Mapped[str] = mapped_column(String(20), nullable=False, default="detected")
    remediation_applied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    remediation_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Impact
    safety_impact: Mapped[str] = mapped_column(String(20), nullable=False, default="low")
    coherence_impact: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Timing
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class ConstraintLineage(BaseModel):
    """
    Constraint lineage tracking.
    Records the evolution of constraints.
    """
    __tablename__ = "constraint_lineages"
    __table_args__ = (
        Index("ix_constraint_lineage_scope", "constraint_scope"),
        Index("ix_constraint_lineage_parent", "parent_constraint_id"),
        Index("ix_constraint_lineage_timestamp", "created_at"),
    )

    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    constraint_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Constraint info
    invariant_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    constraint_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Parent lineage
    parent_constraint_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    root_constraint_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Evolution
    change_type: Mapped[str] = mapped_column(String(50), nullable=False)
    change_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pre_constraint: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    post_constraint: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Impact
    impact_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class ConsistencySnapshot(BaseModel):
    """
    Consistency snapshot.
    Captures consistency state at checkpoints.
    """
    __tablename__ = "consistency_snapshots"
    __table_args__ = (
        Index("ix_consistency_snapshot_session", "session_id"),
        Index("ix_consistency_snapshot_timestamp", "captured_at"),
    )

    snapshot_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Snapshot data
    snapshot_key: Mapped[str] = mapped_column(String(255), nullable=False)
    consistency_score: Mapped[float] = mapped_column(Float, nullable=False)
    coherence_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Component states
    component_states: Mapped[Dict[str, str]] = mapped_column(JSON, nullable=False, default=dict)
    invariant_states: Mapped[Dict[str, bool]] = mapped_column(JSON, nullable=False, default=dict)

    # Violations
    violations_detected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    critical_violations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timing
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class IntegrityMetric(BaseModel):
    """
    Integrity metric.
    Tracks integrity measurements over time.
    """
    __tablename__ = "integrity_metrics"
    __table_args__ = (
        Index("ix_integrity_metric_scope", "metric_scope"),
        Index("ix_integrity_metric_type", "metric_type"),
        Index("ix_integrity_metric_timestamp", "captured_at"),
    )

    metric_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    metric_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Value
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Context
    target_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Thresholds
    min_threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Assessment
    is_compliant: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    deviation: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Timing
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class EnforcementPolicy(BaseModel):
    """
    Enforcement policy.
    Defines how invariants are enforced.
    """
    __tablename__ = "enforcement_policies"
    __table_args__ = (
        Index("ix_enforcement_policy_scope", "policy_scope"),
        Index("ix_enforcement_policy_type", "policy_type"),
        Index("ix_enforcement_policy_active", "is_active"),
    )

    policy_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    policy_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    policy_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    policy_key: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Policy rules
    enforcement_mode: Mapped[str] = mapped_column(String(20), nullable=False, default=EnforcementMode.STRICT.value)
    severity_mapping: Mapped[Dict[str, str]] = mapped_column(JSON, nullable=False, default=dict)

    # Actions
    on_violation_actions: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    escalation_policy: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # State
    policy_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Metrics
    enforcement_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    violation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class ValidationRule(BaseModel):
    """
    Validation rule.
    Defines validation logic for invariants.
    """
    __tablename__ = "validation_rules"
    __table_args__ = (
        Index("ix_validation_rule_scope", "rule_scope"),
        Index("ix_validation_rule_type", "rule_type"),
        Index("ix_validation_rule_active", "is_active"),
    )

    rule_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    rule_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    rule_key: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Rule definition
    validation_expression: Mapped[str] = mapped_column(Text, nullable=False)
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Matching
    applies_to: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # State
    rule_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Metrics
    trigger_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


__all__ = [
    "InvariantType",
    "ViolationSeverity",
    "EnforcementMode",
    "InvariantRegistry",
    "InvariantViolation",
    "ConstraintLineage",
    "ConsistencySnapshot",
    "IntegrityMetric",
    "EnforcementPolicy",
    "ValidationRule",
]
