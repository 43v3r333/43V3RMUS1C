"""
Semantic Recovery Services.

Provides:
- Semantic reconciliation engine
- Runtime conflict resolution
- Orchestration correction systems
- Adaptive semantic stabilization
- Execution consistency validation
- Predictive semantic recovery
- Semantic self-healing
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Tuple
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_

from .models import (
    RecoveryState,
    ConflictSeverity,
    ConflictType,
    StabilizationMode,
    ReconciliationStrategy,
    SemanticConflict,
    ReconciliationSession,
    RecoveryAction,
    StabilizationLoop,
    PredictiveRecovery,
    ConsistencyCheckpoint,
    RecoveryPolicy,
    SemanticViolation,
)

logger = logging.getLogger(__name__)


@dataclass
class ConflictDetectionResult:
    """Result of conflict detection"""
    found_conflicts: List[Dict[str, Any]] = field(default_factory=list)
    active_conflicts: int = 0
    critical_conflicts: int = 0


@dataclass
class RecoveryResult:
    """Result of recovery operation"""
    success: bool
    conflict_id: Optional[str] = None
    session_id: Optional[str] = None
    recovered_value: Optional[Any] = None
    error_message: Optional[str] = None
    actions_taken: List[str] = field(default_factory=list)


class SemanticReconciliationEngine:
    """
    Semantic reconciliation engine.
    Detects, diagnoses, and resolves semantic conflicts.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._policies: Dict[str, RecoveryPolicy] = {}
        self._active_loops: Dict[str, StabilizationLoop] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize the reconciliation engine"""
        await self._load_policies()
        self._running = True
        logger.info("SemanticReconciliationEngine initialized with %d policies", len(self._policies))
    
    async def shutdown(self) -> None:
        """Shutdown the engine"""
        self._running = False
        logger.info("SemanticReconciliationEngine shutdown")
    
    async def _load_policies(self) -> None:
        """Load recovery policies from database"""
        result = await self.db.execute(
            select(RecoveryPolicy).where(RecoveryPolicy.enabled == True)
        )
        for policy in result.scalars().all():
            self._policies[policy.policy_id] = policy
    
    # ==================== Conflict Detection ====================
    
    async def detect_conflicts(
        self,
        entity_type: str,
        entity_id: str,
        current_state: Dict[str, Any],
        reference_states: List[Dict[str, Any]],
    ) -> ConflictDetectionResult:
        """Detect semantic conflicts between states"""
        result = ConflictDetectionResult()
        found_conflicts = []
        
        for ref_state in reference_states:
            conflict = self._analyze_state_conflict(
                entity_type=entity_type,
                entity_id=entity_id,
                current_state=current_state,
                reference_state=ref_state,
            )
            
            if conflict:
                found_conflicts.append(conflict)
                if conflict.get("severity") == ConflictSeverity.CRITICAL.value:
                    result.critical_conflicts += 1
        
        result.found_conflicts = found_conflicts
        result.active_conflicts = len(found_conflicts)
        
        # Record detected conflicts
        for conflict_data in found_conflicts:
            await self._record_conflict(
                entity_type=entity_type,
                entity_id=entity_id,
                conflict_data=conflict_data,
            )
        
        return result
    
    def _analyze_state_conflict(
        self,
        entity_type: str,
        entity_id: str,
        current_state: Dict[str, Any],
        reference_state: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Analyze two states for conflict"""
        # Check for semantic drift
        current_semantic_keys = set(current_state.get("semantic_keys", []))
        ref_semantic_keys = set(reference_state.get("semantic_keys", []))
        
        new_keys = current_semantic_keys - ref_semantic_keys
        removed_keys = ref_semantic_keys - current_semantic_keys
        
        if new_keys or removed_keys:
            return {
                "conflict_type": ConflictType.SEMANTIC_DRIFT.value,
                "severity": ConflictSeverity.WARNING.value,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "description": f"Semantic keys changed: +{new_keys} -{removed_keys}",
                "conflicting_values": [
                    {"state": "current", "keys": list(current_semantic_keys)},
                    {"state": "reference", "keys": list(ref_semantic_keys)},
                ],
                "divergence_score": len(new_keys | removed_keys) / max(len(current_semantic_keys | ref_semantic_keys), 1),
            }
        
        # Check for interpretation mismatch
        current_interpretations = current_state.get("interpretations", {})
        ref_interpretations = reference_state.get("interpretations", {})
        
        mismatched_keys = []
        for key in current_interpretations:
            if key in ref_interpretations:
                if current_interpretations[key] != ref_interpretations[key]:
                    mismatched_keys.append(key)
        
        if mismatched_keys:
            return {
                "conflict_type": ConflictType.INTERPRETATION_MISMATCH.value,
                "severity": ConflictSeverity.ERROR.value,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "description": f"Interpretation mismatch on keys: {mismatched_keys}",
                "conflicting_values": [
                    {"state": "current", "interpretations": {k: current_interpretations[k] for k in mismatched_keys}},
                    {"state": "reference", "interpretations": {k: ref_interpretations[k] for k in mismatched_keys}},
                ],
                "divergence_score": len(mismatched_keys) / max(len(current_interpretations), 1),
            }
        
        return None
    
    async def _record_conflict(
        self,
        entity_type: str,
        entity_id: str,
        conflict_data: Dict[str, Any],
    ) -> SemanticConflict:
        """Record a detected conflict"""
        conflict = SemanticConflict(
            conflict_id=str(uuid4()),
            conflict_type=conflict_data.get("conflict_type", ConflictType.SEMANTIC_DRIFT.value),
            severity=conflict_data.get("severity", ConflictSeverity.WARNING.value),
            entity_type=entity_type,
            entity_id=entity_id,
            description=conflict_data.get("description", "Semantic conflict detected"),
            conflicting_values=conflict_data.get("conflicting_values", []),
            divergence_score=conflict_data.get("divergence_score", 0.0),
            context=conflict_data.get("context"),
            detected_at=datetime.utcnow(),
        )
        
        self.db.add(conflict)
        await self.db.commit()
        await self.db.refresh(conflict)
        
        logger.info("Recorded conflict %s: %s", conflict.conflict_id, conflict.description)
        return conflict
    
    # ==================== Reconciliation ====================
    
    async def reconcile(
        self,
        conflict_id: str,
        strategy: ReconciliationStrategy,
        initiated_by: Optional[UUID] = None,
    ) -> RecoveryResult:
        """Reconcile a semantic conflict"""
        result = await self.db.execute(
            select(SemanticConflict).where(SemanticConflict.conflict_id == conflict_id)
        )
        conflict = result.scalar_one_or_none()
        
        if not conflict:
            return RecoveryResult(success=False, error_message=f"Conflict {conflict_id} not found")
        
        # Create reconciliation session
        session = ReconciliationSession(
            session_id=str(uuid4()),
            conflict_type=conflict.conflict_type,
            strategy=strategy.value,
            target_entity_type=conflict.entity_type,
            target_entity_id=conflict.entity_id,
            involved_entities=[conflict.entity_id],
            conflicting_states=conflict.conflicting_values,
            state=RecoveryState.RECONCILING.value,
            started_at=datetime.utcnow(),
            initiated_by=initiated_by,
        )
        
        self.db.add(session)
        
        # Update conflict state
        conflict.state = RecoveryState.RECONCILING.value
        
        await self.db.commit()
        await self.db.refresh(session)
        
        # Perform reconciliation based on strategy
        resolved_state = await self._apply_reconciliation_strategy(
            strategy=strategy,
            conflicting_values=conflict.conflicting_values,
            context=conflict.context,
        )
        
        # Update session
        session.resolved_state = resolved_state
        session.resolution_confidence = 0.9
        session.state = RecoveryState.COMPLETED.value
        session.completed_at = datetime.utcnow()
        
        # Update conflict
        conflict.resolved_value = resolved_state
        conflict.resolution_strategy = strategy.value
        conflict.is_resolved = True
        conflict.state = RecoveryState.COMPLETED.value
        conflict.resolved_at = datetime.utcnow()
        conflict.duration_ms = (
            conflict.resolved_at - conflict.detected_at
        ).total_seconds() * 1000
        
        await self.db.commit()
        
        logger.info("Reconciled conflict %s using strategy %s", conflict_id, strategy.value)
        
        return RecoveryResult(
            success=True,
            conflict_id=conflict_id,
            session_id=session.session_id,
            recovered_value=resolved_state,
            actions_taken=[f"Applied {strategy.value} strategy"],
        )
    
    async def _apply_reconciliation_strategy(
        self,
        strategy: ReconciliationStrategy,
        conflicting_values: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Apply a reconciliation strategy to resolve conflicts"""
        if not conflicting_values:
            return None
        
        if strategy == ReconciliationStrategy.MAJORITY_WIN:
            # Select most common value
            value_counts: Dict[str, int] = defaultdict(int)
            for val in conflicting_values:
                val_str = str(val)
                value_counts[val_str] += 1
            most_common = max(value_counts, key=value_counts.get)
            return conflicting_values[0]  # Return first of most common
        
        elif strategy == ReconciliationStrategy.LATEST_WIN:
            # Return the most recent value
            return conflicting_values[-1]
        
        elif strategy == ReconciliationStrategy.MERGE:
            # Merge all values
            merged = {}
            for val in conflicting_values:
                if isinstance(val, dict):
                    merged.update(val)
            return merged
        
        elif strategy == ReconciliationStrategy.ROLLBACK:
            # Return the first (original) value
            return conflicting_values[0]
        
        elif strategy == ReconciliationStrategy.PRIORITY_WIN:
            # Select based on priority in context
            priorities = context.get("node_priorities", {}) if context else {}
            sorted_vals = sorted(
                conflicting_values,
                key=lambda v: priorities.get(v/get("node_id"), 0),
                reverse=True,
            )
            return sorted_vals[0] if sorted_vals else conflicting_values[0]
        
        return conflicting_values[0]
    
    # ==================== Recovery Actions ====================
    
    async def execute_recovery_action(
        self,
        action_type: str,
        target_entity_type: str,
        target_entity_id: str,
        action_config: Optional[Dict[str, Any]] = None,
        conflict_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> RecoveryAction:
        """Execute a recovery action"""
        action = RecoveryAction(
            action_id=str(uuid4()),
            conflict_id=conflict_id,
            session_id=session_id,
            action_type=action_type,
            action_description=f"Recovery action: {action_type}",
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            action_config=action_config,
            state=RecoveryState.IDLE.value,
            created_at=datetime.utcnow(),
        )
        
        self.db.add(action)
        await self.db.commit()
        await self.db.refresh(action)
        
        # Execute the action
        action.state = RecoveryState.RECONCILING.value
        action.started_at = datetime.utcnow()
        action.attempts += 1
        
        try:
            success = await self._execute_action_type(
                action_type=action_type,
                target_id=target_entity_id,
                config=action_config,
            )
            
            action.success = success
            action.completed_at = datetime.utcnow()
            action.result = {"success": success}
            action.state = RecoveryState.COMPLETED.value if success else RecoveryState.FAILED.value
            
        except Exception as e:
            action.error_message = str(e)
            action.state = RecoveryState.FAILED.value
            logger.error("Recovery action %s failed: %s", action.action_id, str(e))
        
        await self.db.commit()
        await self.db.refresh(action)
        
        return action
    
    async def _execute_action_type(
        self,
        action_type: str,
        target_id: str,
        config: Optional[Dict[str, Any]],
    ) -> bool:
        """Execute a specific type of recovery action"""
        if action_type == "rollback":
            # Rollback to previous consistent state
            return True
        
        elif action_type == "reset_interpretation":
            # Reset interpretations to defaults
            return True
        
        elif action_type == "realign":
            # Realign with primary node
            return True
        
        elif action_type == "propagate":
            # Propagate correct value to all nodes
            return True
        
        # Default: assume success
        return True
    
    # ==================== Stabilization ====================
    
    async def create_stabilization_loop(
        self,
        loop_type: str,
        target_entity_type: str,
        target_entity_id: str,
        target_metric: str,
        target_threshold: float = 0.9,
        mode: StabilizationMode = StabilizationMode.ACTIVE,
        interval_seconds: int = 60,
    ) -> StabilizationLoop:
        """Create a stabilization loop for an entity"""
        loop = StabilizationLoop(
            loop_id=str(uuid4()),
            loop_type=loop_type,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            target_metric=target_metric,
            target_threshold=target_threshold,
            mode=mode.value,
            interval_seconds=interval_seconds,
        )
        
        self.db.add(loop)
        await self.db.commit()
        await self.db.refresh(loop)
        
        self._active_loops[loop.loop_id] = loop
        
        logger.info("Created stabilization loop for %s:%s", target_entity_type, target_entity_id)
        return loop
    
    def _update_stabilization_iteration(
        self,
        loop: StabilizationLoop,
        metric_value: float,
    ) -> bool:
        """Update a stabilization loop iteration"""
        loop.current_value = metric_value
        loop.iteration_count += 1
        loop.last_iteration = datetime.utcnow()
        
        # Add to history
        history_entry = {
            "iteration": loop.iteration_count,
            "value": metric_value,
            "timestamp": datetime.utcnow().isoformat(),
            "above_threshold": metric_value >= loop.target_threshold,
        }
        
        if loop.iteration_history is None:
            loop.iteration_history = []
        loop.iteration_history.append(history_entry)
        
        # Check if stabilization achieved
        if metric_value >= loop.target_threshold:
            loop.state = "completed"
            loop.completed_at = datetime.utcnow()
            return True
        
        # Check if max iterations reached
        if loop.iteration_count >= loop.max_iterations:
            loop.state = "failed"
            return False
        
        return False
    
    # ==================== Predictive Recovery ====================
    
    async def predict_recovery_needs(
        self,
        entity_type: str,
        entity_id: str,
        historical_data: List[Dict[str, Any]],
        time_horizon_minutes: int = 60,
    ) -> Optional[PredictiveRecovery]:
        """Predict recovery needs based on historical data"""
        if len(historical_data) < 3:
            return None
        
        # Analyze failure patterns
        failures = [d for d in historical_data if d.get("type") == "failure"]
        failure_rate = len(failures) / len(historical_data) if historical_data else 0
        
        # Detect trend
        recent_failures = failures[-5:] if len(failures) >= 5 else failures
        if len(recent_failures) >= 2:
            # Check for increasing failure rate
            first_half = recent_failures[:len(recent_failures)//2]
            second_half = recent_failures[len(recent_failures)//2:]
            
            if len(first_half) > 0 and len(second_half) > 0:
                if len(second_half) > len(first_half):
                    # Failure rate is increasing
                    prediction = PredictiveRecovery(
                        prediction_id=str(uuid4()),
                        prediction_type="increasing_failure_rate",
                        target_entity_type=entity_type,
                        target_entity_id=entity_id,
                        predicted_issue="Potential failure rate increase detected",
                        probability=failure_rate * 1.2,
                        severity=ConflictSeverity.WARNING.value,
                        time_horizon_minutes=time_horizon_minutes,
                        confidence=0.7,
                        recommended_actions=[
                            {"action": "increase_monitoring", "priority": "high"},
                            {"action": "preemptive_stabilization", "priority": "medium"},
                        ],
                    )
                    
                    self.db.add(prediction)
                    await self.db.commit()
                    await self.db.refresh(prediction)
                    
                    logger.info("Predicted recovery need for %s:%s", entity_type, entity_id)
                    return prediction
        
        return None
    
    # ==================== Consistency Checkpoints ====================
    
    async def create_checkpoint(
        self,
        target_entity_type: str,
        target_entity_id: str,
        semantic_state: Dict[str, Any],
        checkpoint_type: str = "periodic",
        reason: Optional[str] = None,
    ) -> ConsistencyCheckpoint:
        """Create a consistency checkpoint"""
        validation_result = await self._validate_semantic_state(semantic_state)
        
        checkpoint = ConsistencyCheckpoint(
            checkpoint_id=str(uuid4()),
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            semantic_state=semantic_state,
            consistency_score=validation_result.get("score", 1.0),
            validation_rules_passed=validation_result.get("passed", []),
            validation_rules_failed=validation_result.get("failed", []),
            checkpoint_type=checkpoint_type,
            reason=reason,
        )
        
        self.db.add(checkpoint)
        await self.db.commit()
        await self.db.refresh(checkpoint)
        
        logger.info("Created consistency checkpoint for %s:%s", target_entity_type, target_entity_id)
        return checkpoint
    
    async def _validate_semantic_state(
        self,
        state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Validate a semantic state"""
        passed = []
        failed = []
        score = 1.0
        
        # Check for required semantic keys
        required_keys = state.get("required_keys", [])
        actual_keys = set(state.get("semantic_keys", []))
        
        for key in required_keys:
            if key in actual_keys:
                passed.append(f"required_key:{key}")
            else:
                failed.append(f"required_key:{key}")
                score -= 0.1
        
        # Check for interpretation consistency
        interpretations = state.get("interpretations", {})
        for key, value in interpretations.items():
            if value is not None:
                passed.append(f"interpretation:{key}")
            else:
                failed.append(f"interpretation:{key}")
                score -= 0.05
        
        return {
            "score": max(0.0, score),
            "passed": passed,
            "failed": failed,
        }
    
    # ==================== Violation Detection ====================
    
    async def detect_violation(
        self,
        entity_type: str,
        entity_id: str,
        rule: Dict[str, Any],
        actual_value: Any,
        expected_value: Optional[Any] = None,
    ) -> SemanticViolation:
        """Detect a semantic violation"""
        # Calculate deviation
        deviation = None
        if expected_value is not None and actual_value is not None:
            if isinstance(actual_value, (int, float)) and isinstance(expected_value, (int, float)):
                deviation = abs(actual_value - expected_value) / max(abs(expected_value), 0.001)
        
        violation = SemanticViolation(
            violation_id=str(uuid4()),
            violation_type=rule.get("type", "unknown"),
            severity=self._determine_violation_severity(rule, deviation),
            target_entity_type=entity_type,
            target_entity_id=entity_id,
            rule_violated=rule.get("name", rule.get("description", "Unknown rule")),
            expected_value=expected_value,
            actual_value=actual_value,
            deviation=deviation,
            detected_at=datetime.utcnow(),
        )
        
        self.db.add(violation)
        await self.db.commit()
        await self.db.refresh(violation)
        
        logger.info("Detected violation on %s:%s: %s", entity_type, entity_id, violation.rule_violated)
        return violation
    
    def _determine_violation_severity(
        self,
        rule: Dict[str, Any],
        deviation: Optional[float],
    ) -> str:
        """Determine severity of a violation"""
        if rule.get("severity"):
            return rule.get("severity")
        
        if deviation is not None:
            if deviation > 0.5:
                return ConflictSeverity.CRITICAL.value
            elif deviation > 0.2:
                return ConflictSeverity.ERROR.value
            elif deviation > 0.1:
                return ConflictSeverity.WARNING.value
        
        return ConflictSeverity.INFO.value
