"""
Governance Domain - Multi-agent authority hierarchy, orchestration arbitration, and conflict resolution.

Implements the governance layer for distributed agent coordination:

  - AuthorityHierarchy   : role-based authority levels between agents
  - ArbitrationPolicy    : conflict resolution strategies
  - AgentGovernanceRule  : configurable rules per agent class
  - ConflictResolution   : recorded conflict outcomes and resolutions
"""
from .models import (
    AuthorityLevel,
    ArbitrationStrategy,
    AgentGovernanceRule,
    AuthorityHierarchy,
    ArbitrationPolicy,
    ConflictResolution,
    AgentPolicyViolation,
)
from .services import (
    GovernanceService,
    ArbitrationEngine,
    AuthorityRegistry,
    RuleEvaluation,
    GovernanceDecision,
)

__all__ = [
    # Enums
    "AuthorityLevel",
    "ArbitrationStrategy",
    # Models
    "AgentGovernanceRule",
    "AuthorityHierarchy",
    "ArbitrationPolicy",
    "ConflictResolution",
    "AgentPolicyViolation",
    # Services
    "GovernanceService",
    "ArbitrationEngine",
    "AuthorityRegistry",
    # Data
    "RuleEvaluation",
    "GovernanceDecision",
]