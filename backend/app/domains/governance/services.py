"""
Governance Services - Multi-agent authority hierarchy, arbitration, and conflict resolution.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from .models import (
    AgentGovernanceRule,
    AgentPolicyViolation,
    ArbitrationPolicy,
    ArbitrationStrategy,
    AuthorityHierarchy,
    AuthorityLevel,
    ConflictResolution,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data transfer types
# ---------------------------------------------------------------------------

@dataclass
class RuleEvaluation:
    rule: AgentGovernanceRule
    triggered: bool
    action: str
    reason: str


@dataclass
class GovernanceDecision:
    action: str  # allow / deny / escalate
    reason: str
    triggered_rules: List[RuleEvaluation] = field(default_factory=list)
    escalation_agent: Optional[str] = None
    confidence: float = 1.0


# ---------------------------------------------------------------------------
# Authority registry
# ---------------------------------------------------------------------------

class AuthorityRegistry:
    """Maintains the current authority hierarchy for all agent kinds."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self._cache: Dict[str, int] = {}
        self._loaded = False

    def load(self) -> None:
        rows = self.db.query(AuthorityHierarchy).filter(
            AuthorityHierarchy.is_active.is_(True)
        ).all()
        self._cache = {row.agent_kind: row.authority_level for row in rows}
        self._loaded = True

    def get_authority_level(self, agent_kind: str) -> int:
        if not self._loaded:
            self.load()
        return self._cache.get(agent_kind, AuthorityLevel.EXECUTOR.value)

    def get_parent(self, agent_kind: str) -> Optional[AuthorityHierarchy]:
        hierarchy = (
            self.db.query(AuthorityHierarchy)
            .filter(
                AuthorityHierarchy.agent_kind == agent_kind,
                AuthorityHierarchy.is_active.is_(True),
            )
            .first()
        )
        if hierarchy and hierarchy.parent_authority_id:
            return self.db.get(AuthorityHierarchy, hierarchy.parent_authority_id)
        return None

    def can_delegate(self, agent_kind: str) -> bool:
        hierarchy = (
            self.db.query(AuthorityHierarchy)
            .filter(
                AuthorityHierarchy.agent_kind == agent_kind,
                AuthorityHierarchy.is_active.is_(True),
            )
            .first()
        )
        return hierarchy.can_delegate if hierarchy else False

    def can_escalate(self, agent_kind: str) -> bool:
        hierarchy = (
            self.db.query(AuthorityHierarchy)
            .filter(
                AuthorityHierarchy.agent_kind == agent_kind,
                AuthorityHierarchy.is_active.is_(True),
            )
            .first()
        )
        return hierarchy.can_escalate if hierarchy else True

    def register_authority(
        self,
        *,
        agent_kind: str,
        role_name: str,
        authority_level: AuthorityLevel,
        can_delegate: bool = False,
        can_escalate: bool = True,
        parent_kind: Optional[str] = None,
        owner_id: Optional[UUID] = None,
    ) -> AuthorityHierarchy:
        parent_id = None
        if parent_kind:
            parent = (
                self.db.query(AuthorityHierarchy)
                .filter(
                    AuthorityHierarchy.agent_kind == parent_kind,
                    AuthorityHierarchy.is_active.is_(True),
                )
                .first()
            )
            if parent:
                parent_id = parent.id

        hierarchy = AuthorityHierarchy(
            agent_kind=agent_kind,
            role_name=role_name,
            authority_level=authority_level.value,
            can_delegate=can_delegate,
            can_escalate=can_escalate,
            parent_authority_id=parent_id,
            owner_id=owner_id,
        )
        self.db.add(hierarchy)
        self.db.commit()
        self.db.refresh(hierarchy)
        self._cache[agent_kind] = authority_level.value
        return hierarchy


# ---------------------------------------------------------------------------
# Arbitration engine
# ---------------------------------------------------------------------------

class ArbitrationEngine:
    """Resolves conflicts between agents using configurable policies."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def resolve(
        self,
        *,
        conflict_id: str,
        domain: str,
        agents: List[Dict[str, Any]],
        conflicting_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> ConflictResolution:
        """Resolve a conflict between agents, returning a resolution record."""
        authority_levels = [a.get("authority_level", 0) for a in agents]
        agent_ids = [a.get("agent_id", "?") for a in agents]

        # Find applicable policy
        policy = self._get_policy(domain)
        strategy = ArbitrationStrategy(policy.strategy if policy else ArbitrationStrategy.PRIORITY)

        outcome, winning_agent = self._apply_strategy(
            strategy=strategy,
            agents=agents,
            actions=conflicting_actions,
            policy=policy,
        )

        resolution = ConflictResolution(
            conflict_id=conflict_id,
            domain=domain,
            agent_ids=agent_ids,
            authority_levels=authority_levels,
            conflict_type=context.get("conflict_type", "resource_contention") if context else "resource_contention",
            description=context.get("description") if context else None,
            conflicting_actions=conflicting_actions,
            strategy_used=strategy.value,
            resolution_outcome=outcome,
            winning_agent_id=winning_agent,
            resolution_state="resolved",
            escalation_required=(strategy == ArbitrationStrategy.MEDIATED),
            detected_at=datetime.utcnow(),
        )
        self.db.add(resolution)
        self.db.commit()
        self.db.refresh(resolution)
        return resolution

    def _get_policy(self, domain: str) -> Optional[ArbitrationPolicy]:
        return (
            self.db.query(ArbitrationPolicy)
            .filter(
                ArbitrationPolicy.domain == domain,
                ArbitrationPolicy.is_active.is_(True),
            )
            .order_by(ArbitrationPolicy.priority.desc())
            .first()
        )

    def _apply_strategy(
        self,
        *,
        strategy: ArbitrationStrategy,
        agents: List[Dict[str, Any]],
        actions: List[Dict[str, Any]],
        policy: Optional[ArbitrationPolicy],
    ) -> tuple[str, Optional[str]]:
        if strategy == ArbitrationStrategy.PRIORITY:
            max_auth = max((a.get("authority_level", 0) for a in agents), default=0)
            winner = next((a.get("agent_id") for a in agents if a.get("authority_level", 0) == max_auth), None)
            return "priority_wins", winner

        elif strategy == ArbitrationStrategy.WEIGHTED_VOTE:
            weights = [a.get("authority_level", 0) * a.get("reliability_score", 0.8) for a in agents]
            max_idx = weights.index(max(weights)) if weights else 0
            return "weighted_vote", agents[max_idx].get("agent_id")

        elif strategy == ArbitrationStrategy.FIRST_COMMIT:
            # First agent by creation time wins
            winner = agents[0].get("agent_id") if agents else None
            return "first_commit", winner

        elif strategy == ArbitrationStrategy.ROUND_ROBIN:
            # Alternating is not deterministic in a single-shot; pick based on time
            winner = agents[hash(str(datetime.utcnow().second)) % len(agents)].get("agent_id") if agents else None
            return "round_robin", winner

        elif strategy == ArbitrationStrategy.MEDIATED:
            return "escalated_to_human", None

        elif strategy == ArbitrationStrategy.MERGE:
            return "merged", None

        else:  # RETRY
            return "retry_scheduled", None

    def get_active_conflicts(self, domain: Optional[str] = None) -> List[ConflictResolution]:
        query = self.db.query(ConflictResolution).filter(
            ConflictResolution.resolution_state.in_(["detected", "resolving"])
        )
        if domain:
            query = query.filter(ConflictResolution.domain == domain)
        return query.order_by(ConflictResolution.detected_at.desc()).limit(50).all()


# ---------------------------------------------------------------------------
# Governance service
# ---------------------------------------------------------------------------

class GovernanceService:
    """Top-level governance service coordinating rules, authority, and arbitration."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self._authority = AuthorityRegistry(db)
        self._arbitration = ArbitrationEngine(db)

    # ---- Rule evaluation -------------------------------------------------

    def evaluate_action(
        self,
        *,
        agent_id: str,
        agent_kind: str,
        action_type: str,
        action_params: Dict[str, Any],
    ) -> GovernanceDecision:
        """Evaluate whether an agent action is permitted under current governance rules."""
        triggered: List[RuleEvaluation] = []

        rules = (
            self.db.query(AgentGovernanceRule)
            .filter(
                AgentGovernanceRule.is_active.is_(True),
                or_(
                    AgentGovernanceRule.agent_kind == agent_kind,
                    AgentGovernanceRule.agent_kind.is_(None),
                ),
            )
            .order_by(AgentGovernanceRule.priority.desc())
            .all()
        )

        final_action = "allow"
        reason = "no rule matched"

        for rule in rules:
            if not self._matches_conditions(rule.conditions, action_type, action_params):
                continue

            eval_result = RuleEvaluation(
                rule=rule,
                triggered=True,
                action=rule.action,
                reason=f"matched rule '{rule.name}'",
            )
            triggered.append(eval_result)

            if rule.action == "deny":
                final_action = "deny"
                reason = f"denied by rule '{rule.name}'"
                break
            elif rule.action == "escalate":
                final_action = "escalate"
                reason = f"escalated by rule '{rule.name}'"

        # Record violations
        for eval_r in triggered:
            if eval_r.action == "deny":
                self.record_violation(
                    agent_id=agent_id,
                    agent_kind=agent_kind,
                    rule=eval_r.rule,
                    description=reason,
                )

        # Determine confidence
        confidence = 1.0 if final_action == "allow" else 0.9

        # Check escalation
        escalate_to = None
        if final_action == "escalate":
            parent = self._authority.get_parent(agent_kind)
            if parent:
                escalate_to = parent.agent_kind

        return GovernanceDecision(
            action=final_action,
            reason=reason,
            triggered_rules=triggered,
            escalation_agent=escalate_to,
            confidence=confidence,
        )

    def _matches_conditions(
        self,
        conditions: Dict[str, Any],
        action_type: str,
        action_params: Dict[str, Any],
    ) -> bool:
        if not conditions:
            return True

        # Rule type matching
        if "action_types" in conditions:
            if action_type not in conditions["action_types"]:
                return False

        # Parameter constraints
        for key, expected in conditions.get("params", {}).items():
            if key in action_params:
                if isinstance(expected, dict):
                    # Range constraint
                    val = action_params[key]
                    if "min" in expected and val < expected["min"]:
                        return False
                    if "max" in expected and val > expected["max"]:
                        return False
                elif action_params[key] != expected:
                    return False

        return True

    # ---- Policy management ----------------------------------------------

    def create_rule(
        self,
        *,
        name: str,
        rule_type: str,
        conditions: Dict[str, Any],
        action: str,
        agent_kind: Optional[str] = None,
        priority: int = 0,
        owner_id: Optional[UUID] = None,
    ) -> AgentGovernanceRule:
        rule = AgentGovernanceRule(
            name=name,
            rule_type=rule_type,
            conditions=dict(conditions),
            action=action,
            agent_kind=agent_kind,
            priority=priority,
            owner_id=owner_id,
        )
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def get_rules(
        self,
        *,
        agent_kind: Optional[str] = None,
        is_active: bool = True,
        limit: int = 50,
    ) -> List[AgentGovernanceRule]:
        query = self.db.query(AgentGovernanceRule)
        if agent_kind:
            query = query.filter(AgentGovernanceRule.agent_kind == agent_kind)
        if is_active:
            query = query.filter(AgentGovernanceRule.is_active.is_(True))
        return query.order_by(AgentGovernanceRule.priority.desc()).limit(limit).all()

    def create_arbitration_policy(
        self,
        *,
        name: str,
        domain: str,
        strategy: ArbitrationStrategy,
        fallback_strategy: Optional[ArbitrationStrategy] = None,
        escalation_threshold: int = 3,
        priority: int = 0,
    ) -> ArbitrationPolicy:
        policy = ArbitrationPolicy(
            name=name,
            domain=domain,
            strategy=strategy.value,
            fallback_strategy=fallback_strategy.value if fallback_strategy else None,
            escalation_threshold=escalation_threshold,
            priority=priority,
        )
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        return policy

    # ---- Conflict management ---------------------------------------------

    def register_conflict(
        self,
        *,
        domain: str,
        agents: List[Dict[str, Any]],
        conflicting_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> ConflictResolution:
        conflict_id = f"conflict_{uuid4()}"
        return self._arbitration.resolve(
            conflict_id=conflict_id,
            domain=domain,
            agents=agents,
            conflicting_actions=conflicting_actions,
            context=context,
        )

    def get_authority_level(self, agent_kind: str) -> int:
        return self._authority.get_authority_level(agent_kind)

    # ---- Violation tracking ----------------------------------------------

    def record_violation(
        self,
        *,
        agent_id: str,
        agent_kind: str,
        rule: AgentGovernanceRule,
        description: str,
        severity: str = "warning",
    ) -> AgentPolicyViolation:
        violation = AgentPolicyViolation(
            violation_id=f"viol_{uuid4()}",
            agent_id=agent_id,
            agent_kind=agent_kind,
            rule_id=rule.id if rule else None,
            rule_name=rule.name if rule else "unknown",
            violation_type="policy_denied",
            severity=severity,
            description=description,
            detected_at=datetime.utcnow(),
        )
        self.db.add(violation)

        # Update rule stats
        if rule:
            rule.trigger_count += 1
            rule.failure_count += 1

        self.db.commit()
        return violation

    def list_violations(
        self,
        *,
        agent_id: Optional[str] = None,
        resolved: Optional[bool] = None,
        limit: int = 50,
    ) -> List[AgentPolicyViolation]:
        query = self.db.query(AgentPolicyViolation)
        if agent_id:
            query = query.filter(AgentPolicyViolation.agent_id == agent_id)
        if resolved is not None:
            query = query.filter(AgentPolicyViolation.resolved == resolved)
        return query.order_by(AgentPolicyViolation.detected_at.desc()).limit(limit).all()


__all__ = [
    "GovernanceService",
    "ArbitrationEngine",
    "AuthorityRegistry",
    "RuleEvaluation",
    "GovernanceDecision",
]