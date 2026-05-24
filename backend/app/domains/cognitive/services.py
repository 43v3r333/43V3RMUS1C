"""
Cognitive Services - Adaptive orchestration and reasoning
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_

from .models import (
    PolicyType,
    PolicyAction,
    ExecutionState,
    OptimizationType,
    PredictionType,
    OrchestrationPolicy,
    AdaptiveExecutionState,
    ExecutionInsight,
    RuntimePrediction,
    OptimizationHistory,
    OrchestrationHeuristic,
    ExecutionPattern,
)

logger = logging.getLogger(__name__)


@dataclass
class PolicyResult:
    """Result of policy evaluation"""
    triggered: bool
    action: str
    action_config: Dict[str, Any] = field(default_factory=dict)
    policy_id: Optional[str] = None
    reason: str = ""


@dataclass
class OptimizationSuggestion:
    """Optimization suggestion"""
    optimization_type: OptimizationType
    target_id: str
    description: str
    expected_improvement: float
    confidence: float
    actions: List[Dict[str, Any]] = field(default_factory=list)


class OrchestrationReasoningEngine:
    """
    Orchestration reasoning engine.
    Handles adaptive execution planning, policy evaluation, and optimization.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._policies: Dict[str, OrchestrationPolicy] = {}
        self._execution_states: Dict[str, AdaptiveExecutionState] = {}
        self._heuristics: Dict[str, OrchestrationHeuristic] = {}
        self._patterns: Dict[str, ExecutionPattern] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize the reasoning engine"""
        await self._load_policies()
        await self._load_heuristics()
        await self._load_patterns()
        self._running = True
        logger.info("OrchestrationReasoningEngine initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the reasoning engine"""
        self._running = False
        logger.info("OrchestrationReasoningEngine shutdown")
    
    async def _load_policies(self) -> None:
        """Load policies from database"""
        result = await self.db.execute(
            select(OrchestrationPolicy).where(OrchestrationPolicy.is_active == True)
        )
        for policy in result.scalars().all():
            self._policies[policy.name] = policy
    
    async def _load_heuristics(self) -> None:
        """Load heuristics from database"""
        result = await self.db.execute(select(OrchestrationHeuristic))
        for heuristic in result.scalars().all():
            self._heuristics[heuristic.name] = heuristic
    
    async def _load_patterns(self) -> None:
        """Load execution patterns from database"""
        result = await self.db.execute(select(ExecutionPattern))
        for pattern in result.scalars().all():
            self._patterns[pattern.pattern_id] = pattern
    
    # ==================== Policy Management ====================
    
    async def create_policy(
        self,
        name: str,
        policy_type: PolicyType,
        conditions: Dict[str, Any],
        action: PolicyAction,
        action_config: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        owner_id: Optional[UUID] = None,
    ) -> OrchestrationPolicy:
        """Create an orchestration policy"""
        policy = OrchestrationPolicy(
            name=name,
            policy_type=policy_type.value,
            conditions=conditions,
            action=action.value,
            action_config=action_config,
            priority=priority,
            owner_id=owner_id,
        )
        
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        
        self._policies[name] = policy
        
        return policy
    
    async def evaluate_policies(
        self,
        context: Dict[str, Any],
        policy_type: Optional[PolicyType] = None,
    ) -> PolicyResult:
        """Evaluate policies against context"""
        applicable_policies = []
        
        for policy in self._policies.values():
            if policy_type and policy.policy_type != policy_type.value:
                continue
            
            # Check if conditions match
            if await self._evaluate_conditions(policy.conditions, context):
                applicable_policies.append(policy)
        
        # Sort by priority (descending)
        applicable_policies.sort(key=lambda p: p.priority, reverse=True)
        
        if not applicable_policies:
            return PolicyResult(triggered=False, reason="No matching policies")
        
        # Use highest priority policy
        best_policy = applicable_policies[0]
        
        # Update usage stats
        best_policy.trigger_count += 1
        self.db.add(best_policy)
        await self.db.commit()
        
        return PolicyResult(
            triggered=True,
            action=best_policy.action,
            action_config=best_policy.action_config or {},
            policy_id=str(best_policy.id),
            reason=f"Policy '{best_policy.name}' matched",
        )
    
    async def _evaluate_conditions(
        self,
        conditions: Dict[str, Any],
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate if conditions match context"""
        for key, expected in conditions.items():
            if key not in context:
                return False
            
            actual = context[key]
            
            # Handle different condition operators
            if isinstance(expected, dict):
                op = expected.get("op", "eq")
                value = expected.get("value")
                
                if op == "eq":
                    if actual != value:
                        return False
                elif op == "gt":
                    if actual <= value:
                        return False
                elif op == "gte":
                    if actual < value:
                        return False
                elif op == "lt":
                    if actual >= value:
                        return False
                elif op == "lte":
                    if actual > value:
                        return False
                elif op == "in":
                    if actual not in value:
                        return False
                elif op == "contains":
                    if value not in actual:
                        return False
            else:
                if actual != expected:
                    return False
        
        return True
    
    # ==================== Adaptive Execution ====================
    
    async def create_execution_state(
        self,
        execution_id: str,
        plan_id: Optional[UUID] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AdaptiveExecutionState:
        """Create adaptive execution state"""
        state = AdaptiveExecutionState(
            execution_id=execution_id,
            plan_id=plan_id,
            state=ExecutionState.PENDING.value,
            context=context,
            decisions=[],
            adaptation_history=[],
        )
        
        self.db.add(state)
        await self.db.commit()
        await self.db.refresh(state)
        
        self._execution_states[execution_id] = state
        
        return state
    
    async def adapt_execution(
        self,
        execution_id: str,
        adaptation_type: str,
        adaptation_data: Dict[str, Any],
    ) -> AdaptiveExecutionState:
        """Adapt execution based on runtime conditions"""
        state = self._execution_states.get(execution_id)
        
        if not state:
            result = await self.db.execute(
                select(AdaptiveExecutionState).where(
                    AdaptiveExecutionState.execution_id == execution_id
                )
            )
            state = result.scalar_one_or_none()
            
            if not state:
                raise ValueError(f"Execution state not found: {execution_id}")
        
        # Record adaptation
        adaptation = {
            "type": adaptation_type,
            "data": adaptation_data,
            "timestamp": datetime.utcnow().isoformat(),
            "state_before": state.state,
        }
        
        history = state.adaptation_history or []
        history.append(adaptation)
        state.adaptation_history = history
        state.adaptation_count += 1
        state.last_adaptation = datetime.utcnow()
        state.updated_at = datetime.utcnow()
        
        # Add decision
        decision = {
            "type": "adaptation",
            "adaptation_type": adaptation_type,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        decisions = state.decisions or []
        decisions.append(decision)
        state.decisions = decisions
        
        self.db.add(state)
        await self.db.commit()
        await self.db.refresh(state)
        
        return state
    
    async def get_execution_state(
        self,
        execution_id: str,
    ) -> Optional[AdaptiveExecutionState]:
        """Get execution state"""
        return self._execution_states.get(execution_id)
    
    # ==================== Optimization ====================
    
    async def analyze_optimization_opportunities(
        self,
        execution_id: str,
        current_metrics: Dict[str, float],
    ) -> List[OptimizationSuggestion]:
        """Analyze optimization opportunities"""
        suggestions = []
        
        # Analyze latency optimization
        if current_metrics.get("latency_ms", 0) > 100:
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.LATENCY,
                target_id=execution_id,
                description="High latency detected - consider parallel execution",
                expected_improvement=0.25,
                confidence=0.8,
                actions=[{"action": "parallelize", "threshold": 0.5}],
            ))
        
        # Analyze throughput
        if current_metrics.get("throughput", 0) < current_metrics.get("target_throughput", 100):
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.THROUGHPUT,
                target_id=execution_id,
                description="Throughput below target - consider batching",
                expected_improvement=0.3,
                confidence=0.75,
                actions=[{"action": "batch", "size": 10}],
            ))
        
        # Analyze resource usage
        if current_metrics.get("cpu_percent", 0) < 50:
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.RESOURCE,
                target_id=execution_id,
                description="Low CPU utilization - can handle more work",
                expected_improvement=0.2,
                confidence=0.85,
                actions=[{"action": "increase_parallelism"}],
            ))
        
        # Analyze cost
        if current_metrics.get("cost_per_execution", 0) > 0.5:
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.COST,
                target_id=execution_id,
                description="High cost per execution - consider optimization",
                expected_improvement=0.15,
                confidence=0.7,
                actions=[{"action": "reduce_retry"}],
            ))
        
        return suggestions
    
    async def apply_optimization(
        self,
        suggestion: OptimizationSuggestion,
        execution_id: str,
    ) -> OptimizationHistory:
        """Apply an optimization suggestion"""
        # Get current state
        state = self._execution_states.get(execution_id)
        before_state = state.context if state else {}
        before_metrics = state.current_performance if state else {}
        
        # Record optimization
        history = OptimizationHistory(
            optimization_id=str(uuid4()),
            optimization_type=suggestion.optimization_type.value,
            before_state=before_state,
            before_metrics=before_metrics,
            trigger_reason=suggestion.description,
        )
        
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        
        return history
    
    # ==================== Prediction ====================
    
    async def predict_execution_duration(
        self,
        plan_id: UUID,
        context: Optional[Dict[str, Any]] = None,
    ) -> RuntimePrediction:
        """Predict execution duration"""
        # Simple prediction based on historical data
        # In production, would use ML model
        base_duration = 300  # 5 minutes default
        confidence = 0.7
        
        if context:
            steps = context.get("steps", 0)
            complexity = context.get("complexity", 1.0)
            base_duration = steps * 30 * complexity
        
        prediction = RuntimePrediction(
            prediction_id=str(uuid4()),
            prediction_type=PredictionType.DURATION.value,
            target_id=str(plan_id),
            target_type="plan",
            predicted_value=base_duration,
            predicted_unit="seconds",
            confidence=confidence,
            predicted_for=datetime.utcnow() + timedelta(seconds=base_duration),
            generated_at=datetime.utcnow(),
        )
        
        self.db.add(prediction)
        await self.db.commit()
        await self.db.refresh(prediction)
        
        return prediction
    
    async def predict_queue_time(
        self,
        priority: int,
        queue_depth: int,
    ) -> RuntimePrediction:
        """Predict queue waiting time"""
        base_time = queue_depth * 30  # 30 seconds per job
        adjusted_time = base_time / (priority / 10)  # Higher priority = less wait
        
        prediction = RuntimePrediction(
            prediction_id=str(uuid4()),
            prediction_type=PredictionType.QUEUE_TIME.value,
            target_id=f"queue-{priority}",
            target_type="queue",
            predicted_value=adjusted_time,
            predicted_unit="seconds",
            confidence=0.75,
            min_value=adjusted_time * 0.5,
            max_value=adjusted_time * 2,
            predicted_for=datetime.utcnow() + timedelta(seconds=adjusted_time),
            generated_at=datetime.utcnow(),
        )
        
        self.db.add(prediction)
        await self.db.commit()
        await self.db.refresh(prediction)
        
        return prediction
    
    # ==================== Heuristic Management ====================
    
    async def learn_heuristic(
        self,
        name: str,
        heuristic_type: str,
        rule: Dict[str, Any],
        success: bool,
    ) -> OrchestrationHeuristic:
        """Learn a scheduling heuristic"""
        heuristic = self._heuristics.get(name)
        
        if heuristic:
            heuristic.hit_count += 1 if success else 0
            heuristic.miss_count += 0 if success else 1
            
            # Update success rate
            total = heuristic.hit_count + heuristic.miss_count
            heuristic.success_rate = heuristic.hit_count / total if total > 0 else 0
            
            # Adjust weight based on success
            if success:
                heuristic.weight = min(heuristic.weight * 1.1, 10.0)
            else:
                heuristic.weight = max(heuristic.weight * 0.9, 0.1)
            
            heuristic.last_used = datetime.utcnow()
        else:
            heuristic = OrchestrationHeuristic(
                name=name,
                heuristic_type=heuristic_type,
                rule=rule,
                hit_count=1 if success else 0,
                miss_count=0 if success else 1,
                success_rate=1.0 if success else 0.0,
                last_used=datetime.utcnow(),
            )
            self._heuristics[name] = heuristic
        
        self.db.add(heuristic)
        await self.db.commit()
        await self.db.refresh(heuristic)
        
        return heuristic
    
    async def get_best_heuristic(
        self,
        heuristic_type: str,
    ) -> Optional[OrchestrationHeuristic]:
        """Get best performing heuristic of a type"""
        candidates = [
            h for h in self._heuristics.values()
            if h.heuristic_type == heuristic_type and h.success_rate is not None
        ]
        
        if not candidates:
            return None
        
        # Sort by success rate * weight
        candidates.sort(key=lambda h: (h.success_rate or 0) * h.weight, reverse=True)
        
        return candidates[0]
    
    # ==================== Pattern Learning ====================
    
    async def learn_pattern(
        self,
        pattern_type: str,
        name: str,
        pattern_data: Dict[str, Any],
        metrics: Optional[Dict[str, float]] = None,
    ) -> ExecutionPattern:
        """Learn an execution pattern"""
        # Check for existing pattern
        existing = None
        for pattern in self._patterns.values():
            if pattern.pattern_type == pattern_type and pattern.name == name:
                existing = pattern
                break
        
        if existing:
            existing.frequency += 1
            existing.last_seen = datetime.utcnow()
            
            # Update averages
            if metrics:
                if existing.avg_duration:
                    existing.avg_duration = (existing.avg_duration + metrics.get("duration", 0)) / 2
                if existing.success_rate is not None:
                    existing.success_rate = (existing.success_rate + metrics.get("success", 1)) / 2
        else:
            existing = ExecutionPattern(
                pattern_id=str(uuid4()),
                pattern_type=pattern_type,
                name=name,
                pattern_data=pattern_data,
                avg_duration=metrics.get("duration") if metrics else None,
                success_rate=metrics.get("success") if metrics else None,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
            )
            self._patterns[existing.pattern_id] = existing
        
        self.db.add(existing)
        await self.db.commit()
        await self.db.refresh(existing)
        
        return existing
    
    # ==================== Insight Generation ====================
    
    async def generate_insight(
        self,
        insight_type: str,
        title: str,
        description: str,
        data: Optional[Dict[str, Any]] = None,
        source_execution: Optional[str] = None,
        source_type: str = "analysis",
    ) -> ExecutionInsight:
        """Generate an execution insight"""
        # Calculate impact score based on data
        impact_score = 0.5
        if data:
            improvement = data.get("potential_improvement")
            if improvement:
                impact_score = min(improvement / 100, 1.0)
        
        insight = ExecutionInsight(
            insight_id=str(uuid4()),
            insight_type=insight_type,
            title=title,
            description=description,
            data=data,
            source_execution=source_execution,
            source_type=source_type,
            impact_score=impact_score,
            generated_at=datetime.utcnow(),
        )
        
        self.db.add(insight)
        await self.db.commit()
        await self.db.refresh(insight)
        
        return insight
    
    async def get_actionable_insights(
        self,
        limit: int = 10,
    ) -> List[ExecutionInsight]:
        """Get actionable insights"""
        result = await self.db.execute(
            select(ExecutionInsight)
            .where(ExecutionInsight.is_applied == False)
            .order_by(ExecutionInsight.impact_score.desc())
            .limit(limit)
        )
        
        return list(result.scalars().all())


class AdaptiveScheduler:
    """
    Adaptive scheduler with learned heuristics.
    Optimizes scheduling based on historical data and patterns.
    """
    
    def __init__(self, db: AsyncSession, reasoning_engine: OrchestrationReasoningEngine):
        self.db = db
        self.reasoning_engine = reasoning_engine
    
    async def schedule_adaptively(
        self,
        jobs: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[Tuple[str, int]]:
        """Schedule jobs adaptively using heuristics"""
        if not jobs:
            return []
        
        # Get scheduling heuristic
        heuristic = await self.reasoning_engine.get_best_heuristic("scheduling")
        
        # Sort jobs by heuristic if available
        sorted_jobs = jobs.copy()
        
        if heuristic:
            # Apply heuristic-based sorting
            for job in sorted_jobs:
                score = 0
                
                # Priority weight
                score += (job.get("priority", 5) / 10) * heuristic.weight * 0.4
                
                # Urgency weight
                score += (1 / (job.get("urgency", 1) + 1)) * heuristic.weight * 0.3
                
                # Size weight (smaller jobs first for responsiveness)
                score += (1 / (job.get("estimated_duration", 100) + 1)) * heuristic.weight * 0.3
                
                job["_heuristic_score"] = score
            
            sorted_jobs.sort(key=lambda j: j.get("_heuristic_score", 0), reverse=True)
        else:
            # Default: priority then urgency
            sorted_jobs.sort(
                key=lambda j: (
                    -j.get("priority", 5),
                    j.get("urgency", 1),
                )
            )
        
        return [(job["id"], i) for i, job in enumerate(sorted_jobs)]
    
    async def predict_optimal_schedule(
        self,
        jobs: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Predict optimal schedule for jobs"""
        scheduled = []
        
        for job in jobs:
            # Calculate optimal start time
            start_time = datetime.utcnow()
            
            # Check for dependencies
            dependencies = job.get("dependencies", [])
            if dependencies:
                # Find latest end time of dependencies
                for dep in dependencies:
                    dep_end = self._get_dependency_end_time(dep)
                    if dep_end and dep_end > start_time:
                        start_time = dep_end
            
            scheduled_job = {
                "job_id": job.get("id"),
                "estimated_start": start_time.isoformat(),
                "estimated_duration": job.get("estimated_duration", 60),
                "estimated_end": (start_time + timedelta(seconds=job.get("estimated_duration", 60))).isoformat(),
            }
            
            scheduled.append(scheduled_job)
        
        return scheduled
    
    def _get_dependency_end_time(self, dependency_id: str) -> Optional[datetime]:
        """Get estimated end time of a dependency"""
        # Placeholder - would look up actual dependency state
        return None