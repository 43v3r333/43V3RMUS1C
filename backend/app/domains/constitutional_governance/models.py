"""
Constitutional Governance Models - Production-grade constitutional governance infrastructure

Provides:
- Constitutional governance engine
- Orchestration invariant policies
- Cognition boundary enforcement
- Recursive safety governance
- Systemic constraint supervision
- Adaptive constitutional coordination

All models support:
- UUID primary keys
- Indexed constitutional lineage
- Temporal governance tracking
- Lifecycle versioning
- Distributed invariant traceability
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


class ConstraintSeverity(str, Enum):
    """Constraint severity levels"""
    INFO = "info"           # Informational violation
    WARNING = "warning"     # Minor violation
    MODERATE = "moderate"   # Significant violation
    HIGH = "high"          # Major violation
    CRITICAL = "critical"   # Critical violation
    BLOCKING = "blocking"   # Must be fixed before proceeding


class GovernanceScope(str, Enum):
    """Constitutional governance scope levels"""
    LOCAL = "local"                 # Single component
    ORCHESTRATION = "orchestration"   # Orchestration level
    SESSION = "session"             # Session level
    DOMAIN = "domain"             # Domain level
    ECOSYSTEM = "ecosystem"       # Ecosystem level
    GLOBAL = "global"             # Platform-wide


class BoundaryType(str, Enum):
    """Boundary types for governance"""
    HARD_LIMIT = "hard_limit"       # Absolute boundary
    SOFT_LIMIT = "soft_limit"       # Warning boundary
    THRESHOLD = "threshold"         # Threshold boundary
    RATE_LIMIT = "rate_limit"       # Rate boundary
    RESOURCE = "resource"           # Resource boundary
    SEMANTIC = "semantic"          # Semantic boundary


class InvariantType(str, Enum):
    """Invariant types for constitutional constraints"""
    SAFETY = "safety"           # Safety invariant
    CONSISTENCY = "consistency"   # Consistency invariant
    INTEGRITY = "integrity"       # Integrity invariant
    COHERENCE = "coherence"      # Coherence invariant
    TERMINATION = "termination"   # Termination invariant
    RESOURCE = "resource"        # Resource invariant
    SECURITY = "security"        # Security invariant


class SafetyState(str, Enum):
    """Safety state for recursive safety tracking"""
    NOMINAL = "nominal"         # System is safe
    CAUTION = "caution"        # Minor safety concerns
    WARNING = "warning"         # Safety warning
    CRITICAL = "critical"      # Critical safety issue
    COLLAPSE = "collapse"       # Potential collapse


class ConstitutionalProfile(BaseModel):
    """
    Constitutional governance profile.
    Defines governance parameters for constitutional operations.
    """
    __tablename__ = "constitutional_profiles"
    __table_args__ = (
        Index("ix_con_profile_scope", "profile_scope"),
        Index("ix_con_profile_state", "profile_state"),
        Index("ix_con_profile_active", "is_active"),
    )

    profile_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    profile_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    profile_key: Mapped[str] = mapped_column(String(255), nullable=False)

    # Governance configuration
    governance_scope: Mapped[str] = mapped_column(String(20), nullable=False, default=GovernanceScope.ECOSYSTEM.value)
    
    # Constitutional parameters
    max_violations_per_cycle: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    violation_severity_cap: Mapped[str] = mapped_column(String(20), nullable=False, default=ConstraintSeverity.HIGH.value)
    auto_remediation_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    escalation_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=5)

    # Boundary parameters
    hard_limit_multiplier: Mapped[float] = mapped_column(Float, nullable=False, default=0.95)
    soft_limit_multiplier: Mapped[float] = mapped_column(Float, nullable=False, default=0.8)
    warning_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.6)

    # Safety parameters
    safety_margin: Mapped[float] = mapped_column(Float, nullable=False, default=0.1)
    collapse_prevention_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    emergency_shutdown_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.1)

    # Invariant constraints
    invariant_policies: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    critical_invariants: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # State tracking
    profile_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Metrics
    cycle_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_violations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    critical_violations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    remediations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_profile_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class InvariantPolicy(BaseModel):
    """
    Orchestration invariant policy.
    Defines constraints and invariants for orchestration.
    """
    __tablename__ = "invariant_policies"
    __table_args__ = (
        Index("ix_invariant_policy_scope", "policy_scope"),
        Index("ix_invariant_policy_type", "invariant_type"),
        Index("ix_invariant_policy_active", "is_active"),
    )

    policy_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    policy_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    policy_key: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Invariant definition
    invariant_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    invariant_name: Mapped[str] = mapped_column(String(255), nullable=False)
    invariant_expression: Mapped[str] = mapped_column(Text, nullable=False)

    # Constraint parameters
    constraint_type: Mapped[str] = mapped_column(String(50), nullable=False)
    constraint_parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Severity and scope
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default=ConstraintSeverity.MODERATE.value)
    governance_scope: Mapped[str] = mapped_column(String(20), nullable=False, default=GovernanceScope.ECOSYSTEM.value)

    # Preconditions and postconditions
    preconditions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    postconditions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Enforcement
    enforcement_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="strict")  # strict, lenient, audit
    auto_remediate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rollback_on_violation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # State
    policy_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Audit
    trigger_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    violation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    remediation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class CognitionBoundary(BaseModel):
    """
    Cognition boundary definition.
    Defines boundaries for cognitive operations.
    """
    __tablename__ = "cognition_boundaries"
    __table_args__ = (
        Index("ix_cognition_boundary_scope", "boundary_scope"),
        Index("ix_cognition_boundary_type", "boundary_type"),
        Index("ix_cognition_boundary_active", "is_active"),
    )

    boundary_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    boundary_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    boundary_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    boundary_key: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Boundary definition
    boundary_limits: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    boundary_expressions: Mapped[Dict[str, str]] = mapped_column(JSON, nullable=False, default=dict)

    # Thresholds
    soft_limit: Mapped[float] = mapped_column(Float, nullable=False, default=0.8)
    hard_limit: Mapped[float] = mapped_column(Float, nullable=False, default=0.95)
    critical_limit: Mapped[float] = mapped_column(Float, nullable=False, default=0.99)

    # Enforcement
    enforcement_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="strict")
    allows_override: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    override_requires_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # State
    boundary_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Metrics
    breach_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class RecursiveSafetyRule(BaseModel):
    """
    Recursive safety rule.
    Defines safety constraints for recursive operations.
    """
    __tablename__ = "recursive_safety_rules"
    __table_args__ = (
        Index("ix_recursive_safety_scope", "rule_scope"),
        Index("ix_recursive_safety_type", "safety_type"),
        Index("ix_recursive_safety_active", "is_active"),
    )

    rule_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    rule_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    safety_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    rule_key: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Safety parameters
    max_recursion_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    max_stack_size: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    max_iteration_count: Mapped[int] = mapped_column(Integer, nullable=False, default=10000)

    # Safety thresholds
    collapse_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.1)
    warning_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.3)
    critical_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Safety actions
    on_collapse_action: Mapped[str] = mapped_column(String(50), nullable=False, default="rollback")
    on_warning_action: Mapped[str] = mapped_column(String(50), nullable=False, default="notify")
    on_critical_action: Mapped[str] = mapped_column(String(50), nullable=False, default="escalate")

    # State
    rule_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Metrics
    trigger_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    collapse_preventions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    safety_interventions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class SystemicConstraint(BaseModel):
    """
    Systemic constraint definition.
    Defines constraints across the ecosystem.
    """
    __tablename__ = "systemic_constraints"
    __table_args__ = (
        Index("ix_systemic_constraint_scope", "constraint_scope"),
        Index("ix_systemic_constraint_type", "constraint_type"),
        Index("ix_systemic_constraint_active", "is_active"),
    )

    constraint_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    constraint_scope: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    constraint_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    constraint_key: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Constraint definition
    constraint_definition: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    constraint_scope_components: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    # Severity and priority
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default=ConstraintSeverity.HIGH.value)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)

    # Enforcement
    enforcement_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    auto_enforce: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    enforcement_scope: Mapped[str] = mapped_column(String(20), nullable=False, default=GovernanceScope.GLOBAL.value)

    # State
    constraint_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Metrics
    evaluation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    violation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Dependencies
    depends_on_constraints: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    constrains_components: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class ConstitutionalAudit(BaseModel):
    """
    Constitutional governance audit trail.
    Records all constitutional decisions and actions.
    """
    __tablename__ = "constitutional_audits"
    __table_args__ = (
        Index("ix_con_audit_session", "session_id"),
        Index("ix_con_audit_action", "action_type"),
        Index("ix_con_audit_timestamp", "logged_at"),
    )

    audit_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    profile_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Actor info
    actor_type: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    actor_kind: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Action
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action_target: Mapped[str] = mapped_column(String(100), nullable=False)

    # Context
    action_context: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    pre_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    post_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Outcome
    outcome_type: Mapped[str] = mapped_column(String(50), nullable=False)
    outcome_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Constraint info
    constraint_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    violation_detected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    remediation_applied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Safety
    safety_state_before: Mapped[str] = mapped_column(String(20), nullable=True)
    safety_state_after: Mapped[str] = mapped_column(String(20), nullable=True)

    # Timing
    logged_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    execution_duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class GovernanceBoundary(BaseModel):
    """
    Governance boundary definition.
    Defines operational boundaries for governance.
    """
    __tablename__ = "governance_boundaries"
    __table_args__ = (
        Index("ix_gov_boundary_scope", "boundary_scope"),
        Index("ix_gov_boundary_type", "boundary_type"),
        Index("ix_gov_boundary_active", "is_active"),
    )

    boundary_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    boundary_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    boundary_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    boundary_key: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Boundary definition
    min_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    boundary_expression: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Validation
    validation_function: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    validation_parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # State
    boundary_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Metrics
    validation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    breach_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class ConstraintViolation(BaseModel):
    """
    Constraint violation record.
    Tracks all constraint violations.
    """
    __tablename__ = "constraint_violations"
    __table_args__ = (
        Index("ix_constraint_violation_constraint", "constraint_id"),
        Index("ix_constraint_violation_session", "session_id"),
        Index("ix_constraint_violation_severity", "severity"),
        Index("ix_constraint_violation_timestamp", "occurred_at"),
    )

    violation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    constraint_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    lineage_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Violation details
    violation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Context
    violating_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    expected_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    deviation: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Resolution
    resolution_state: Mapped[str] = mapped_column(String(20), nullable=False, default="detected", index=True)
    remediation_applied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    remediation_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rollback_triggered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Escalation
    escalated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    escalation_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Safety impact
    safety_impact: Mapped[str] = mapped_column(String(20), nullable=False, default=SafetyState.NOMINAL.value)

    # Timing
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


__all__ = [
    "ConstraintSeverity",
    "GovernanceScope",
    "BoundaryType",
    "InvariantType",
    "SafetyState",
    "ConstitutionalProfile",
    "InvariantPolicy",
    "CognitionBoundary",
    "RecursiveSafetyRule",
    "SystemicConstraint",
    "ConstitutionalAudit",
    "GovernanceBoundary",
    "ConstraintViolation",
]
