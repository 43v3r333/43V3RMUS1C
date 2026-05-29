"""
Adaptive Arbitration Services - Production-grade arbitration infrastructure

Provides:
- Adaptation arbitration engine
- Recursive balancing systems
- Semantic evolution reconciliation
- Orchestration adaptation governance
- Distributed mutation coordination
- Systemic evolution stabilization

All services support:
- Async operation
- Typed arbitration contracts
- Balance lineage tracking
- Distributed coordination visibility
- Recursive stabilization traceability
"""
from __future__ import annotations

import logging
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from .models import (
    BalanceStrategy,
    ArbitrationScope,
    ReconciliationState,
    AdaptationPhase,
    ArbitrationSession,
    AdaptationBalance,
    SemanticReconciliation,
    OrchestrationAdaptation,
    DistributedAdaptationCoordination,
    SystemicEvolutionStabilization,
)

logger = logging.getLogger(__name__)


# =====================================================================
# Data Transfer Objects
# =====================================================================

@dataclass
class ArbitrationResult:
    """Result of an arbitration decision"""
    session_id: str
    decision: str
    selected_adaptations: List[str] = field(default_factory=list)
    rejected_adaptations: List[str] = field(default_factory=list)
    balance_assignments: Dict[str, Any] = field(default_factory=dict)
    coherence_impact: float = 0.0
    confidence: float = 1.0


@dataclass
class BalanceAssessment:
    """Assessment of balance state"""
    is_balanced: bool
    imbalance_score: float
    deviation_sources: List[Dict[str, Any]] = field(default_factory=list)
    redistribution_plan: Optional[List[Dict[str, Any]]] = None
    tolerance_met: bool = False


@dataclass
class ReconciliationResult:
    """Result of semantic reconciliation"""
    reconciliation_id: str
    is_reconciled: bool
    convergence_score: float
    conflicts_resolved: int
    remaining_conflicts: List[Dict[str, Any]] = field(default_factory=list)


# =====================================================================
# Adaptation Arbitration Engine
# =====================================================================

class AdaptationArbitrationEngine:
    """
    Central adaptation arbitration engine.
    Coordinates conflict resolution and balance arbitration.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._active_sessions: Dict[str, ArbitrationSession] = {}

    async def initialize(self) -> None:
        """Initialize the arbitration engine"""
        await self._load_active_sessions()
        logger.info("AdaptationArbitrationEngine initialized")

    async def _load_active_sessions(self) -> None:
        """Load active sessions"""
        result = await self.db.execute(
            select(ArbitrationSession).where(
                ArbitrationSession.session_state.in_(["init", "running", "arbitrating"])
            )
        )
        for session in result.scalars().all():
            self._active_sessions[session.session_id] = session

    async def create_session(
        self,
        scope_kind: str,
        scope_id: Optional[str] = None,
        strategy: BalanceStrategy = BalanceStrategy.ADAPTIVE,
        max_depth: int = 10,
        parent_session_id: Optional[str] = None,
        **kwargs,
    ) -> ArbitrationSession:
        """Create a new arbitration session"""
        session_id = f"arb_session_{uuid4()}"

        # Calculate depth
        recursion_depth = 0
        if parent_session_id:
            parent = await self._get_session(parent_session_id)
            if parent:
                recursion_depth = parent.recursion_depth + 1

        if recursion_depth >= max_depth:
            raise ValueError(f"max recursion depth {max_depth} exceeded")

        session = ArbitrationSession(
            session_id=session_id,
            session_key=kwargs.get("session_key", f"arb_{session_id}"),
            arbitration_scope=kwargs.get("arbitration_scope", ArbitrationScope.ORCHESTRATION.value),
            scope_kind=scope_kind,
            scope_id=scope_id,
            balance_strategy=strategy.value,
            strategy_config=kwargs.get("strategy_config", {}),
            recursion_depth=recursion_depth,
            max_recursion_depth=max_depth,
            parent_session_id=parent_session_id,
            session_state="init",
            started_at=datetime.utcnow(),
            correlation_id=kwargs.get("correlation_id"),
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        self._active_sessions[session_id] = session

        # Update parent's child list
        if parent_session_id:
            parent = await self._get_session(parent_session_id)
            if parent:
                child_ids = parent.child_session_ids or []
                child_ids.append(session_id)
                parent.child_session_ids = child_ids
                await self.db.commit()

        return session

    async def _get_session(self, session_id: str) -> Optional[ArbitrationSession]:
        """Get session from cache or DB"""
        return self._active_sessions.get(session_id) or await self.db.execute(
            select(ArbitrationSession).where(
                ArbitrationSession.session_id == session_id)
        ).scalar_one_or_none()

    async def arbitrate(
        self,
        session_id: str,
        conflicting_adaptations: List[str],
        session_state: Dict[str, Any],
    ) -> ArbitrationResult:
        """Arbitrate between conflicting adaptations"""
        session = await self._get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Update state
        session.session_state = "arbitrating"
        session.conflicting_adaptations = conflicting_adaptations
        session.current_phase = AdaptationPhase.ARBITRATION.value
        await self.db.commit()

        # Apply arbitration strategy
        strategy = BalanceStrategy(session.balance_strategy)
        
        if strategy == BalanceStrategy.CONSERVATIVE:
            selected = self._apply_conservative_selection(conflicting_adaptations, session_state)
        elif strategy == BalanceStrategy.EQUALIZING:
            selected = self._apply_equalizing_selection(conflicting_adaptations, session_state)
        elif strategy == BalanceStrategy.PRIORITIZED:
            selected = self._apply_prioritized_selection(conflicting_adaptations, session_state)
        elif strategy == BalanceStrategy.WEIGHTED:
            selected = self._apply_weighted_selection(conflicting_adaptations, session_state)
        elif strategy == BalanceStrategy.RECURSIVE:
            selected = await self._apply_recursive_selection(
                conflicting_adaptations, session_state, strategy_config=session.strategy_config)
        else:
            selected = self._apply_adaptive_selection(conflicting_adaptations, session_state)

        rejected = [a for a in conflicting_adaptations if a not in selected]

        # Calculate coherence impact
        coherence_impact = len(selected) * 0.05

        session.session_state = "completed"
        session.phase_history = session.phase_history or []
        session.phase_history.append({
            "phase": AdaptationPhase.DECISION.value,
            "selected": selected,
            "rejected": rejected,
            "timestamp": datetime.utcnow().isoformat(),
        })
        session.balance_score = 1.0 - (len(rejected) / max(len(conflicting_adaptations), 1))
        await self.db.commit()

        return ArbitrationResult(
            session_id=session_id,
            decision="arbitrated",
            selected_adaptations=selected,
            rejected_adaptations=rejected,
            coherence_impact=coherence_impact,
            confidence=session.balance_score,
        )

    def _apply_conservative_selection(
        self,
        adaptations: List[str],
        state: Dict[str, Any],
    ) -> List[str]:
        """Apply conservative selection - prefer fewer changes"""
        # Select the adaptation with lowest impact
        impacts = [(a, state.get(f"{a}_impact", 0)) for a in adaptations]
        impacts.sort(key=lambda x: x[1])
        return [impacts[0][0]] if impacts else []

    def _apply_equalizing_selection(
        self,
        adaptations: List[str],
        state: Dict[str, Any],
    ) -> List[str]:
        """Apply equalizing selection - balance across components"""
        # Select adaptations that equalize across different scopes
        return adaptations[:len(adaptations) // 2 + 1]

    def _apply_prioritized_selection(
        self,
        adaptations: List[str],
        state: Dict[str, Any],
    ) -> List[str]:
        """Apply prioritized selection by priority"""
        # Sort by priority and select top
        priorities = [(a, state.get(f"{a}_priority", 5)) for a in adaptations]
        priorities.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in priorities[:3]]

    def _apply_weighted_selection(
        self,
        adaptations: List[str],
        state: Dict[str, Any],
    ) -> List[str]:
        """Apply weighted selection by impact/benefit"""
        scores = []
        for a in adaptations:
            impact = state.get(f"{a}_impact", 0.5)
            benefit = state.get(f"{a}_benefit", 0.5)
            score = benefit - impact * 0.5  # Higher benefit, lower impact is better
            scores.append((a, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scores[:3]]

    def _apply_adaptive_selection(
        self,
        adaptations: List[str],
        state: Dict[str, Any],
    ) -> List[str]:
        """Apply adaptive selection based on context"""
        # Use a combination of factors
        scores = []
        for a in adaptations:
            priority = state.get(f"{a}_priority", 5)
            impact = state.get(f"{a}_impact", 0.5)
            urgency = state.get(f"{a}_urgency", 5)
            score = (priority * 0.4 + urgency * 0.3 + (1 - impact) * 0.3)
            scores.append((a, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scores[:4]]

    async def _apply_recursive_selection(
        self,
        adaptations: List[str],
        state: Dict[str, Any],
        strategy_config: Dict[str, Any],
    ) -> List[str]:
        """Apply recursive selection for complex conflicts"""
        # Recursive balancing - delegate to parent if available
        recursion_limit = strategy_config.get("recursion_limit", 3)
        current_depth = strategy_config.get("current_depth", 0)

        if current_depth >= recursion_limit:
            return self._apply_adaptive_selection(adaptations, state)

        # Split adaptations by scope and recursively arbitrate
        by_scope: Dict[str, List[str]] = {}
        for a in adaptations:
            scope = state.get(f"{a}_scope", "default")
            if scope not in by_scope:
                by_scope[scope] = []
            by_scope[scope].append(a)

        results = []
        for scope, scope_adaptations in by_scope.items():
            if len(scope_adaptations) > 1:
                # Create child session for this scope
                child_session = await self.create_session(
                    scope_kind=scope,
                    parent_session_id=strategy_config.get("parent_session_id"),
                )
                child_adaptations = await self._apply_recursive_selection(
                    scope_adaptations,
                    state,
                    {**strategy_config, "current_depth": current_depth + 1,
                     "parent_session_id": child_session.session_id},
                )
                results.extend(child_adaptations)
            else:
                results.extend(scope_adaptations)

        return results

    async def complete_session(
        self,
        session_id: str,
        success: bool = True,
    ) -> ArbitrationSession:
        """Complete an arbitration session"""
        session = await self._get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        session.session_state = "completed"
        session.completed_at = datetime.utcnow()
        session.arbitration_duration_ms = (
            session.completed_at - session.started_at
        ).total_seconds() * 1000
        session.success = success

        if session_id in self._active_sessions:
            del self._active_sessions[session_id]

        await self.db.commit()
        await self.db.refresh(session)
        return session


# =====================================================================
# Recursive Balancing System
# =====================================================================

class RecursiveBalancingSystem:
    """
    Recursive balancing system.
    Manages balance state across adaptation hierarchies.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self) -> None:
        """Initialize the system"""
        logger.info("RecursiveBalancingSystem initialized")

    async def capture_balance(
        self,
        session_id: str,
        lineage_id: str,
        balance_scope: str,
        component_states: Dict[str, float],
        strategy: BalanceStrategy,
        target_balance: Optional[Dict[str, float]] = None,
        **kwargs,
    ) -> AdaptationBalance:
        """Capture a balance state snapshot"""
        balance_id = f"balance_{uuid4()}"

        # Calculate balance vector
        balance_vector = self._calculate_balance_vector(component_states)

        # Calculate imbalance
        imbalance = self._calculate_imbalance(component_states, target_balance)

        balance = AdaptationBalance(
            balance_id=balance_id,
            session_id=session_id,
            lineage_id=lineage_id,
            balance_scope=balance_scope,
            scope_components=list(component_states.keys()),
            component_states=component_states,
            balance_vector=balance_vector,
            imbalance_score=imbalance,
            strategy_used=strategy.value,
            strategy_params=kwargs.get("strategy_params", {}),
            target_balance=target_balance,
            tolerance_threshold=kwargs.get("tolerance", 0.05),
            captured_at=datetime.utcnow(),
            correlation_id=kwargs.get("correlation_id"),
        )

        self.db.add(balance)
        await self.db.commit()
        await self.db.refresh(balance)
        return balance

    def _calculate_balance_vector(
        self,
        states: Dict[str, float],
    ) -> Dict[str, float]:
        """Calculate balance vector for components"""
        if not states:
            return {}
        total = sum(states.values())
        count = len(states)
        mean = total / count if count > 0 else 0

        return {
            k: (v - mean) / mean if mean != 0 else 0
            for k, v in states.items()
        }

    def _calculate_imbalance(
        self,
        states: Dict[str, float],
        target: Optional[Dict[str, float]],
    ) -> float:
        """Calculate imbalance score"""
        if not states:
            return 0.0

        if target:
            # Compare against target
            deviations = sum(
                (states.get(k, 0) - v) ** 2
                for k, v in target.items()
            )
            return (deviations / len(target)) ** 0.5
        else:
            # Use variance as imbalance
            values = list(states.values())
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            return variance ** 0.5

    async def assess_balance(
        self,
        session_id: str,
    ) -> BalanceAssessment:
        """Assess current balance state"""
        result = await self.db.execute(
            select(AdaptationBalance).where(
                AdaptationBalance.session_id == session_id
            ).order_by(AdaptationBalance.captured_at.desc()).limit(1)
        )
        balance = result.scalar_one_or_none()

        if not balance:
            return BalanceAssessment(
                is_balanced=True,
                imbalance_score=0.0,
            )

        # Check tolerance
        tolerance_met = balance.imbalance_score <= balance.tolerance_threshold

        # Find deviation sources
        deviations = self._find_deviation_sources(balance)

        # Generate redistribution plan
        plan = self._generate_redistribution_plan(balance) if not tolerance_met else None

        return BalanceAssessment(
            is_balanced=tolerance_met,
            imbalance_score=balance.imbalance_score,
            deviation_sources=deviations,
            redistribution_plan=plan,
            tolerance_met=tolerance_met,
        )

    def _find_deviation_sources(
        self,
        balance: AdaptationBalance,
    ) -> List[Dict[str, Any]]:
        """Find components driving deviation"""
        sources = []
        for k, v in balance.balance_vector.items():
            if abs(v) > balance.tolerance_threshold:
                sources.append({
                    "component": k,
                    "deviation": v,
                    "state": balance.component_states.get(k),
                })
        return sources

    def _generate_redistribution_plan(
        self,
        balance: AdaptationBalance,
    ) -> List[Dict[str, Any]]:
        """Generate redistribution plan to restore balance"""
        plan = []
        vector = balance.balance_vector

        # Sort by deviation
        high = [(k, v) for k, v in vector.items() if v > 0]
        low = [(k, v) for k, v in vector.items() if v < 0]

        for i in range(min(len(high), len(low))):
            if high[i][1] > abs(low[i][1]):
                amount = abs(low[i][1]) * 0.5
            else:
                amount = high[i][1] * 0.5

            plan.append({
                "from": high[i][0],
                "to": low[i][0],
                "amount": amount,
                "rationale": "balance redistribution",
            })

        return plan


# =====================================================================
# Semantic Evolution Reconciler
# =====================================================================

class SemanticEvolutionReconciler:
    """
    Semantic evolution reconciler.
    Reconciles semantic states across adaptations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self) -> None:
        """Initialize the reconciler"""
        logger.info("SemanticEvolutionReconciler initialized")

    async def reconcile(
        self,
        session_id: str,
        lineage_id: str,
        subject_kind: str,
        subject_key: str,
        pre_state: Dict[str, Any],
        post_state: Dict[str, Any],
        reconciliation_type: str = "merge",
        **kwargs,
    ) -> SemanticReconciliation:
        """Reconcile semantic states"""
        reconciliation_id = f"recon_{uuid4()}"

        # Calculate semantic distances
        pre_distance = self._calculate_semantic_distance(pre_state)
        post_distance = self._calculate_semantic_distance(post_state)

        # Determine reconciliation approach
        if reconciliation_type == "merge":
            approach = self._determine_merge_approach(pre_state, post_state)
        elif reconciliation_type == "override":
            approach = "later_wins"
        else:
            approach = "weighted_merge"

        # Perform reconciliation
        conflicts = self._detect_conflicts(pre_state, post_state)
        violations = self._check_invariants(post_state, kwargs.get("invariants", []))

        reconciliation = SemanticReconciliation(
            reconciliation_id=reconciliation_id,
            session_id=session_id,
            lineage_id=lineage_id,
            reconciliation_scope=kwargs.get("scope", "local"),
            subject_kind=subject_kind,
            subject_key=subject_key,
            pre_reconciliation_state=pre_state,
            pre_semantic_distance=pre_distance,
            post_reconciliation_state=post_state,
            post_semantic_distance=post_distance,
            reconciliation_type=reconciliation_type,
            reconciliation_approach=approach,
            reconciliation_state=ReconciliationState.RECINCILED.value if not conflicts else ReconciliationState.IN_PROGRESS.value,
            convergence_achieved=len(conflicts) == 0,
            invariants_maintained=len(violations) == 0,
            invariant_violations=violations if violations else None,
            conflicts_resolved=len([c for c in conflicts if c.get("resolved")]),
            conflicts_remaining=conflicts if conflicts else None,
            reconciled_at=datetime.utcnow(),
            correlation_id=kwargs.get("correlation_id"),
        )

        self.db.add(reconciliation)
        await self.db.commit()
        await self.db.refresh(reconciliation)
        return reconciliation

    def _calculate_semantic_distance(self, state: Dict[str, Any]) -> float:
        """Calculate semantic distance for a state"""
        if not state:
            return 0.0
        # Simple measure based on number of changed keys
        return min(1.0, len(state) / 100)

    def _determine_merge_approach(
        self,
        pre: Dict[str, Any],
        post: Dict[str, Any],
    ) -> str:
        """Determine best merge approach"""
        if len(post) > len(pre):
            return "additive_merge"
        elif len(post) > len(pre) * 2:
            return "replacement"
        else:
            return "weighted_merge"

    def _detect_conflicts(
        self,
        pre: Dict[str, Any],
        post: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Detect semantic conflicts"""
        conflicts = []
        for key in set(pre.keys()) & set(post.keys()):
            if pre[key] != post[key]:
                conflicts.append({
                    "key": key,
                    "pre": pre[key],
                    "post": post[key],
                    "resolved": False,
                })
        return conflicts

    def _check_invariants(
        self,
        state: Dict[str, Any],
        invariants: List[str],
    ) -> List[str]:
        """Check for invariant violations"""
        violations = []
        for invariant in invariants:
            if invariant == "coherence":
                if state.get("coherence", 1.0) < 0.5:
                    violations.append("coherence invariant violated")
            elif invariant == "version":
                if state.get("version", 1) < 1:
                    violations.append("version invariant violated")
        return violations


# =====================================================================
# Orchestration Adaptation Governor
# =====================================================================

class OrchestrationAdaptationGovernor:
    """
    Orchestration adaptation governor.
    Governs adaptation approval and execution.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self) -> None:
        """Initialize the governor"""
        logger.info("OrchestrationAdaptationGovernor initialized")

    async def create_adaptation(
        self,
        session_id: str,
        lineage_id: str,
        subject_kind: str,
        subject_key: str,
        adaptation_type: str,
        pre_state: Dict[str, Any],
        post_state: Dict[str, Any],
        governance_level: str = "intervention",
        **kwargs,
    ) -> OrchestrationAdaptation:
        """Create an orchestrated adaptation"""
        adaptation_id = f"orch_adapt_{uuid4()}"

        # Calculate impact
        impact = self._calculate_impact(pre_state, post_state)

        adaptation = OrchestrationAdaptation(
            adaptation_id=adaptation_id,
            session_id=session_id,
            lineage_id=lineage_id,
            subject_kind=subject_kind,
            subject_key=subject_key,
            subject_version=kwargs.get("subject_version", 1),
            adaptation_type=adaptation_type,
            adaptation_category=kwargs.get("category", "runtime"),
            adaptation_reason=kwargs.get("reason"),
            pre_adaptation_state=pre_state,
            pre_coherence_score=pre_state.get("coherence", 1.0),
            post_adaptation_state=post_state,
            post_coherence_score=post_state.get("coherence", 1.0),
            governance_level=governance_level,
            approval_required=kwargs.get("requires_approval", True),
            approved_by=kwargs.get("approved_by"),
            approved_at=datetime.utcnow() if kwargs.get("approved_by") else None,
            adaptation_state="pending",
            impact_score=impact,
            risk_score=kwargs.get("risk_score", impact * 0.5),
            coherence_impact=kwargs.get("coherence_impact", 0.0),
            adapted_at=datetime.utcnow(),
            correlation_id=kwargs.get("correlation_id"),
        )

        self.db.add(adaptation)
        await self.db.commit()
        await self.db.refresh(adaptation)
        return adaptation

    def _calculate_impact(
        self,
        pre: Dict[str, Any],
        post: Dict[str, Any],
    ) -> float:
        """Calculate adaptation impact"""
        changes = sum(1 for k in set(pre.keys()) | set(post.keys()) if pre.get(k) != post.get(k))
        return min(1.0, changes / 50)

    async def approve_adaptation(
        self,
        adaptation_id: str,
        approver_id: str,
    ) -> OrchestrationAdaptation:
        """Approve an adaptation"""
        result = await self.db.execute(
            select(OrchestrationAdaptation).where(
                OrchestrationAdaptation.adaptation_id == adaptation_id)
        )
        adaptation = result.scalar_one_or_none()

        if not adaptation:
            raise ValueError(f"Adaptation not found: {adaptation_id}")

        adaptation.approved_by = approver_id
        adaptation.approved_at = datetime.utcnow()
        adaptation.adaptation_state = "approved"

        await self.db.commit()
        await self.db.refresh(adaptation)
        return adaptation

    async def complete_adaptation(
        self,
        adaptation_id: str,
        success: bool = True,
    ) -> OrchestrationAdaptation:
        """Complete an adaptation"""
        result = await self.db.execute(
            select(OrchestrationAdaptation).where(
                OrchestrationAdaptation.adaptation_id == adaptation_id)
        )
        adaptation = result.scalar_one_or_none()

        if not adaptation:
            raise ValueError(f"Adaptation not found: {adaptation_id}")

        adaptation.adaptation_state = "completed" if success else "failed"
        adaptation.completed_at = datetime.utcnow()
        adaptation.duration_ms = (
            adaptation.completed_at - adaptation.adapted_at
        ).total_seconds() * 1000

        await self.db.commit()
        await self.db.refresh(adaptation)
        return adaptation


# =====================================================================
# Distributed Mutation Coordinator (alias for already existing one)
# =====================================================================

DistributedMutationCoordinator = None  # Would import from mutation_tracking if needed


# =====================================================================
# Systemic Evolution Stabilizer
# =====================================================================

class SystemicEvolutionStabilizer:
    """
    Systemic evolution stabilizer.
    Manages platform-wide stabilization efforts.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize(self) -> None:
        """Initialize the stabilizer"""
        logger.info("SystemicEvolutionStabilizer initialized")

    async def begin_stabilization(
        self,
        session_id: str,
        lineage_id: str,
        stabilization_scope: str,
        affected_components: List[str],
        pre_state: Dict[str, Any],
        **kwargs,
    ) -> SystemicEvolutionStabilization:
        """Begin a stabilization effort"""
        stabilization_id = f"stabilize_{uuid4()}"

        stabilization = SystemicEvolutionStabilization(
            stabilization_id=stabilization_id,
            session_id=session_id,
            lineage_id=lineage_id,
            stabilization_scope=stabilization_scope,
            affected_components=affected_components,
            pre_stabilization_state=pre_state,
            coherence_before=pre_state.get("coherence", 1.0),
            coherence_after=pre_state.get("coherence", 1.0),
            stabilization_state="init",
            interventions_planned=kwargs.get("interventions"),
            started_at=datetime.utcnow(),
            correlation_id=kwargs.get("correlation_id"),
        )

        self.db.add(stabilization)
        await self.db.commit()
        await self.db.refresh(stabilization)
        return stabilization

    async def apply_intervention(
        self,
        stabilization_id: str,
        intervention: Dict[str, Any],
    ) -> SystemicEvolutionStabilization:
        """Apply a stabilization intervention"""
        result = await self.db.execute(
            select(SystemicEvolutionStabilization).where(
                SystemicEvolutionStabilization.stabilization_id == stabilization_id)
        )
        stabilization = result.scalar_one_or_none()

        if not stabilization:
            raise ValueError(f"Stabilization not found: {stabilization_id}")

        interventions = stabilization.interventions_applied or []
        interventions.append(intervention)
        stabilization.interventions_applied = interventions
        stabilization.iteration += 1

        # Update post state with any coherence improvements
        intervention_coherence = intervention.get("coherence_delta", 0)
        stabilization.coherence_after = min(
            1.0,
            stabilization.coherence_after + intervention_coherence
        )
        stabilization.stability_delta = (
            stabilization.coherence_after - stabilization.coherence_before
        )

        # Check convergence
        stabilization.convergence_score = stabilization.coherence_after
        if stabilization.convergence_score >= stabilization.convergence_threshold:
            stabilization.stabilization_state = "converged"
            stabilization.stabilization_complete = True
            stabilization.completed_at = datetime.utcnow()
            stabilization.duration_seconds = (
                stabilization.completed_at - stabilization.started_at
            ).total_seconds()

        await self.db.commit()
        await self.db.refresh(stabilization)
        return stabilization

    async def complete_stabilization(
        self,
        stabilization_id: str,
        post_state: Dict[str, Any],
        success: bool = True,
    ) -> SystemicEvolutionStabilization:
        """Complete a stabilization effort"""
        result = await self.db.execute(
            select(SystemicEvolutionStabilization).where(
                SystemicEvolutionStabilization.stabilization_id == stabilization_id)
        )
        stabilization = result.scalar_one_or_none()

        if not stabilization:
            raise ValueError(f"Stabilization not found: {stabilization_id}")

        stabilization.post_stabilization_state = post_state
        stabilization.stabilization_state = "completed" if success else "failed"
        stabilization.stabilization_complete = True
        stabilization.completed_at = datetime.utcnow()
        stabilization.duration_seconds = (
            stabilization.completed_at - stabilization.started_at
        ).total_seconds()
        stabilization.coherence_after = post_state.get("coherence", stabilization.coherence_after)
        stabilization.stability_delta = (
            stabilization.coherence_after - stabilization.coherence_before
        )

        await self.db.commit()
        await self.db.refresh(stabilization)
        return stabilization


__all__ = [
    "AdaptationArbitrationEngine",
    "RecursiveBalancingSystem",
    "SemanticEvolutionReconciler",
    "OrchestrationAdaptationGovernor",
    "SystemicEvolutionStabilizer",
    "ArbitrationResult",
    "BalanceAssessment",
    "ReconciliationResult",
]
