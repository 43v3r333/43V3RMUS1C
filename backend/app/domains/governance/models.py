"""
Governance Models - Multi-agent authority hierarchy, arbitration, and conflict resolution.
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


class AuthorityLevel(int, Enum):
    """Agent authority levels - higher number = more authority."""

    OBSERVER = 0
    EXECUTOR = 10
    COORDINATOR = 20
    SUPERVISOR = 30
    ADMINISTRATOR = 50
    MASTER = 100


class ArbitrationStrategy(str, Enum):
    """Conflict resolution strategies."""

    PRIORITY = "priority"          # higher authority wins
    ROUND_ROBIN = "round_robin"    # alternate between agents
    FIRST_COMMIT = "first_commit"  # first to act wins
    WEIGHTED_VOTE = "weighted_vote"  # weighted by authority
    MEDIATED = "mediated"          # escalate to human
    RETRY = "retry"                # retry with backoff
    MERGE = "merge"                # combine outputs


class AgentGovernanceRule(BaseModel):
    """Configurable governance rules per agent class / type.

    Defines what actions an agent is allowed to take, which actions need
    approval, and which trigger automatic escalation.
    """

    __tablename__ = "agent_governance_rules"
    __table_args__ = (
        Index("ix_gov_rule_agent_kind", "agent_kind"),
        Index("ix_gov_rule_active", "is_active"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    agent_kind: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    agent_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Rule definition
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    conditions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # allow / deny / escalate
    action_config: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Scope
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    # Audit
    trigger_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class AuthorityHierarchy(BaseModel):
    """Static authority relationships between agent types.

    Establishes a baseline authority chain that the governance service uses
    for priority-based conflict resolution.
    """

    __tablename__ = "authority_hierarchies"
    __table_args__ = (
        UniqueConstraint("agent_kind", "role_name", name="uq_auth_hierarchy_kind_role"),
        Index("ix_auth_hierarchy_parent", "parent_authority_id"),
    )

    agent_kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    role_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    authority_level: Mapped[int] = mapped_column(Integer, nullable=False)
    can_delegate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    can_escalate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    parent_authority_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class ArbitrationPolicy(BaseModel):
    """Active arbitration configuration for a domain / workflow class.

    Controls how conflicts are resolved when multiple agents attempt the
    same action or produce conflicting outputs.
    """

    __tablename__ = "arbitration_policies"
    __table_args__ = (
        Index("ix_arb_policy_domain", "domain"),
        Index("ix_arb_policy_active", "is_active"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    domain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    workflow_class: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Strategy
    strategy: Mapped[str] = mapped_column(String(32), nullable=False)
    strategy_config: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Fallback
    escalation_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    fallback_strategy: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class ConflictResolution(BaseModel):
    """Recorded conflict outcomes for audit and learning."""

    __tablename__ = "conflict_resolutions"
    __table_args__ = (
        Index("ix_conflict_resolution_domain", "domain"),
        Index("ix_conflict_resolution_state", "resolution_state"),
    )

    conflict_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    domain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Involved agents
    agent_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    authority_levels: Mapped[List[int]] = mapped_column(JSON, nullable=False, default=list)

    # Conflict details
    conflict_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    conflicting_actions: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )

    # Resolution
    strategy_used: Mapped[str] = mapped_column(String(32), nullable=False)
    resolution_outcome: Mapped[str] = mapped_column(String(32), nullable=False)
    winning_agent_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    merge_output: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Resolution state
    resolution_state: Mapped[str] = mapped_column(
        String(32), nullable=False, default="resolved", index=True
    )
    escalation_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    human_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Timing
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolution_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class AgentPolicyViolation(BaseModel):
    """Record of policy violations detected at runtime."""

    __tablename__ = "agent_policy_violations"
    __table_args__ = (
        Index("ix_violation_agent", "agent_id"),
        Index("ix_violation_rule", "rule_id"),
    )

    violation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)

    agent_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    agent_kind: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    rule_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("agent_governance_rules.id"), nullable=True
    )
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Violation details
    violation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="warning")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    context: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Handling
    action_taken: Mapped[str] = mapped_column(String(50), nullable=False, default="logged")
    escalated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Timing
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


__all__ = [
    "AuthorityLevel",
    "ArbitrationStrategy",
    "AgentGovernanceRule",
    "AuthorityHierarchy",
    "ArbitrationPolicy",
    "ConflictResolution",
    "AgentPolicyViolation",
]