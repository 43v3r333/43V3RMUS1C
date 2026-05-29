"""
Evolution Governance Models - Production-grade evolutionary governance infrastructure

Provides:
- Evolution profiles for adaptive supervision
- Mutation policies for orchestration evolution
- Cognition adaptation rules
- Semantic continuity contracts
- Recursive evolution sessions
- Systemic coherence snapshots
- Governance audit trails
- Adaptation lineage tracking

All models support:
- UUID primary keys
- Indexed evolution lineage
- Temporal governance tracking
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


class EvolutionStage(str, Enum):
    """Evolution lifecycle stages"""
    EMBRYONIC = "embryonic"
    EMERGING = "emerging"
    GROWING = "growing"
    MATURING = "maturing"
    STABLE = "stable"
    DECLINING = "declining"
    TERMINATED = "terminated"


class CoherenceState(str, Enum):
    """Systemic coherence states"""
    ALIGNED = "aligned"
    DRIFTING = "drifting"
    FRAGMENTED = "fragmented"
    RECOVERING = "recovering"
    COLLAPSED = "collapsed"


class AdaptationStrategy(str, Enum):
    """Adaptation strategies for evolution"""
    CONSERVATIVE = "conservative"       # Minimal changes, high safety
    BALANCED = "balanced"               # Moderate changes, balanced approach
    AGGRESSIVE = "aggressive"           # Rapid changes, high risk/reward
    EMERGENT = "emergent"               # Self-organizing adaptation
    RECURSIVE = "recursive"             # Self-referential evolution
    HIERARCHICAL = "hierarchical"       # Multi-level adaptation


class MutationSeverity(str, Enum):
    """Severity levels for mutations"""
    TRIVIAL = "trivial"     # No functional impact
    MINOR = "minor"         # Minor behavioral change
    MODERATE = "moderate"   # Significant behavioral modification
    MAJOR = "major"         # Core functionality change
    CRITICAL = "critical"   # System-breaking mutation
    CATASTROPHIC = "catastrophic"  # Platform failure


class GovernanceLevel(str, Enum):
    """Governance authority levels"""
    OBSERVATION = "observation"       # Monitor only
    RECOMMENDATION = "recommendation" # Can suggest changes
    INTERVENTION = "intervention"     # Can intervene in processes
    ENFORCEMENT = "enforcement"       # Can enforce policies
    ABSOLUTE = "absolute"             # Unlimited authority


class EvolutionProfile(BaseModel):
    """
    Adaptive evolution governance profile.
    Defines supervisory parameters for orchestrations and agents.
    """
    __tablename__ = "evolution_profiles"
    __table_args__ = (
        Index("ix_evo_profile_scope", "profile_scope"),
        Index("ix_evo_profile_state", "profile_state"),
        Index("ix_evo_profile_active", "is_active"),
    )

    profile_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    profile_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    profile_key: Mapped[str] = mapped_column(String(255), nullable=False)

    # Governance configuration
    governance_level: Mapped[str] = mapped_column(String(20), nullable=False, default=GovernanceLevel.INTERVENTION.value)
    adaptation_strategy: Mapped[str] = mapped_column(String(20), nullable=False, default=AdaptationStrategy.BALANCED.value)

    # Evolution parameters
    evolution_stage: Mapped[str] = mapped_column(String(20), nullable=False, default=EvolutionStage.EMERGING.value)
    evolution_velocity: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    adaptation_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Coherence thresholds
    coherence_target: Mapped[float] = mapped_column(Float, nullable=False, default=0.85)
    coherence_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.6)
    coherence_drift_limit: Mapped[float] = mapped_column(Float, nullable=False, default=0.15)

    # Mutation constraints
    max_mutations_per_cycle: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    mutation_severity_cap: Mapped[str] = mapped_column(String(20), nullable=False, default=MutationSeverity.MODERATE.value)
    mutation_cooldown_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=300)

    # Semantic constraints
    semantic_invariants: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    continuity_score_min: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)

    # Observability
    lineage_depth_max: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    audit_retention_days: Mapped[int] = mapped_column(Integer, nullable=False, default=90)

    # State tracking
    profile_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Metrics
    cycle_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_mutations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    successful_adaptations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_adaptations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_profile_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class MutationPolicy(BaseModel):
    """
    Orchestration mutation policy.
    Defines rules and constraints for runtime evolution.
    """
    __tablename__ = "mutation_policies"
    __table_args__ = (
        Index("ix_mutation_policy_domain", "policy_domain"),
        Index("ix_mutation_policy_active", "is_active"),
    )

    policy_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    policy_domain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    policy_key: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Policy scope
    applies_to_kinds: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    excludes_kinds: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Mutation rules
    allowed_mutations: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    denied_mutations: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    mutation_conditions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Severity constraints
    min_severity_threshold: Mapped[str] = mapped_column(String(20), nullable=False, default=MutationSeverity.TRIVIAL.value)
    max_severity_threshold: Mapped[str] = mapped_column(String(20), nullable=False, default=MutationSeverity.CRITICAL.value)
    breakglass_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Preconditions
    preconditions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    rollback_on_failure: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Governance
    requires_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    approval_threshold: Mapped[str] = mapped_column(String(20), nullable=False, default=GovernanceLevel.RECOMMENDATION.value)
    escalation_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # State
    policy_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Audit
    trigger_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_policy_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class CognitionAdaptationRule(BaseModel):
    """
    Cognition adaptation governance rule.
    Controls how cognitive processes evolve over time.
    """
    __tablename__ = "cognition_adaptation_rules"
    __table_args__ = (
        Index("ix_cog_adaptation_rule_kind", "rule_kind"),
        Index("ix_cog_adaptation_rule_active", "is_active"),
    )

    rule_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    rule_kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    rule_key: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Rule scope
    applies_to_reasoning_types: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    applies_to_domains: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Adaptation parameters
    adaptation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    adaptation_conditions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    adaptation_targets: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Thresholds
    trigger_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    adaptation_magnitude_min: Mapped[float] = mapped_column(Float, nullable=False, default=0.01)
    adaptation_magnitude_max: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    convergence_criteria: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Safety constraints
    requires_validation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    validation_timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    rollback_on_divergence: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    divergence_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.2)

    # State
    rule_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Audit
    trigger_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    adaptation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    divergence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class SemanticContinuityContract(BaseModel):
    """
    Semantic continuity enforcement contract.
    Maintains semantic invariants across evolution cycles.
    """
    __tablename__ = "semantic_continuity_contracts"
    __table_args__ = (
        Index("ix_semantic_contract_scope", "contract_scope"),
        Index("ix_semantic_contract_active", "is_active"),
    )

    contract_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    contract_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    contract_key: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Semantic invariants
    invariants: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    semantic_constraints: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    breaking_conditions: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    # Violation handling
    violation_severity_cap: Mapped[str] = mapped_column(String(20), nullable=False, default=MutationSeverity.MAJOR.value)
    auto_repair_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, value=False)
    repair_strategy: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # State
    contract_state: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Compliance tracking
    last_validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    validation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    violation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    repair_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Dependencies
    depends_on_contracts: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    dependents: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class RecursiveEvolutionSession(BaseModel):
    """
    Recursive evolution supervision session.
    Tracks nested evolution cycles for complex orchestrations.
    """
    __tablename__ = "recursive_evolution_sessions"
    __table_args__ = (
        Index("ix_recursive_session_state", "session_state"),
        Index("ix_recursive_session_parent", "parent_session_id"),
        Index("ix_recursive_session_root", "root_session_id"),
    )

    session_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_key: Mapped[str] = mapped_column(String(255), nullable=False)

    # Hierarchy
    recursion_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_recursion_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    parent_session_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    root_session_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    child_session_ids: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Scope
    session_scope: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    scope_kind: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    scope_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Governance
    governance_level: Mapped[str] = mapped_column(String(20), nullable=False, default=GovernanceLevel.INTERVENTION.value)
    strategy: Mapped[str] = mapped_column(String(20), nullable=False, default=AdaptationStrategy.RECURSIVE.value)

    # State
    session_state: Mapped[str] = mapped_column(String(20), nullable=False, default="init", index=True)
    coherence_state: Mapped[str] = mapped_column(String(20), nullable=False, default=CoherenceState.ALIGNED.value)

    # Metrics
    evolution_metrics: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    coherence_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    adaptation_efficiency: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cycle_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Mutations
    mutations_applied: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mutations_successful: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mutations_reverted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

 # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class SystemicCoherenceSnapshot(BaseModel):
    """
    Systemic coherence metrics snapshot.
    Captures systemic state at evolution checkpoints.
    """
    __tablename__ = "systemic_coherence_snapshots"
    __table_args__ = (
        Index("ix_coherence_snapshot_session", "session_id"),
        Index("ix_coherence_snapshot_timestamp", "captured_at"),
    )

    snapshot_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    snapshot_key: Mapped[str] = mapped_column(String(255), nullable=False)

    # Coherence metrics
    coherence_state: Mapped[str] = mapped_column(String(20), nullable=False, default=CoherenceState.ALIGNED.value)
    coherence_score: Mapped[float] = mapped_column(Float, nullable=False)
    drift_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Component health
    component_states: Mapped[Dict[str, str]] = mapped_column(JSON, nullable=False, default=dict)
    component_coherence_scores: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    failing_components: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Systemic metrics
    orchestration_health: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    cognition_alignment: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    semantic_stability: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    distributed_sync: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Mutations at snapshot
    pending_mutations: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    applied_mutations: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    reverted_mutations: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Dependencies
    contract_ids_validated: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    violation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timing
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    capture_type: Mapped[str] = mapped_column(String(20), nullable=False, default="scheduled")

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class EvolutionGovernanceAudit(BaseModel):
    """
    Evolution governance audit trail.
    Records all governance decisions and actions.
    """
    __tablename__ = "evolution_governance_audits"
    __table_args__ = (
        Index("ix_evolution_audit_session", "session_id"),
        Index("ix_evolution_audit_action", "action_type"),
        Index("ix_evolution_audit_timestamp", "logged_at"),
    )

    audit_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    profile_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Actor info
    actor_type: Mapped[str] = mapped_column(String(50), nullable=False)  # agent, system, human
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

    # Governance
    governance_level_used: Mapped[str] = mapped_column(String(20), nullable=False)
    violation_detected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    escalation_triggered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Timing
    logged_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    execution_duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class AdaptationLineage(BaseModel):
    """
    Adaptation lineage tracking.
    Records the evolution history of orchestrations and agents.
    """
    __tablename__ = "adaptation_lineages"
    __table_args__ = (
        Index("ix_adaptation_lineage_subject", "subject_kind", "subject_key"),
        Index("ix_adaptation_lineage_parent", "parent_adaptation_id"),
    )

    adaptation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    lineage_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Subject
    subject_kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subject_key: Mapped[str] = mapped_column(String(255), nullable=False)
    subject_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Parent lineage
    parent_adaptation_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    root_adaptation_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Adaptation details
    adaptation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    adaptation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    adaptation_trigger: Mapped[str] = mapped_column(String(50), nullable=False)

    # Changes
    pre_adaptation_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    post_adaptation_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    changes_delta: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Impact assessment
    impact_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    benefit_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    rollback_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Outcome
    outcome: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    outcome_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    was_reverted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Timing
    lineage_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


__all__ = [
    "EvolutionStage",
    "CoherenceState",
    "AdaptationStrategy",
    "MutationSeverity",
    "GovernanceLevel",
    "EvolutionProfile",
    "MutationPolicy",
    "CognitionAdaptationRule",
    "SemanticContinuityContract",
    "RecursiveEvolutionSession",
    "SystemicCoherenceSnapshot",
    "EvolutionGovernanceAudit",
    "AdaptationLineage",
]
