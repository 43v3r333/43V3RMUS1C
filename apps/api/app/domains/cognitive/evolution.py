"""
Self-Evolution Service

Autonomous optimization infrastructure with adaptive runtime evolution,
optimization learning loops, predictive self-tuning, and workflow refinement.
"""
import logging
import random
import math
from typing import Optional, List, Dict, Any, Tuple, Callable
from uuid import UUID
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cognitive import (
    AdaptiveOptimizationCycle, RuntimeEvolutionMetric, TuningState
)
from app.models.cognitive import StrategicExecutionPlan

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Result of an optimization iteration."""
    parameters: Dict[str, Any]
    score: float
    improvement: float
    converged: bool
    iteration: int


class SelfEvolutionService:
    """
    Self-evolution and autonomous optimization system.
    
    Capabilities:
    - Self-optimization: Automatically tune system parameters
    - Orchestration refinement: Improve workflow execution
    - Adaptive execution evolution: Evolve based on feedback
    - Predictive balancing: Balance resource usage
    - Intelligent recovery: Recover from failures
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ---- Optimization Cycle Management ----
    
    async def create_cycle(
        self,
        cycle_id: str,
        name: str,
        context_key: str,
        target_metric: str,
        parameter_space: Dict[str, Any],
        target_improvement: float = 0.1,
        max_iterations: int = 10,
        patience: int = 3,
        baseline_score: Optional[float] = None,
        linked_plan_id: Optional[UUID] = None,
    ) -> AdaptiveOptimizationCycle:
        """
        Create a new optimization cycle.
        
        Args:
            cycle_id: Unique cycle identifier
            name: Cycle name
            context_key: Optimization context (render_pipeline, ai_generation)
            target_metric: Metric to optimize
            parameter_space: Search space definition
            target_improvement: Expected % improvement
            max_iterations: Maximum optimization iterations
            patience: Iterations without improvement before stop
            baseline_score: Starting score
            linked_plan_id: Associated strategic plan
            
        Returns:
            Created AdaptiveOptimizationCycle
        """
        cycle = AdaptiveOptimizationCycle(
            cycle_id=cycle_id,
            name=name,
            context_key=context_key,
            target_metric=target_metric,
            parameter_space=parameter_space,
            target_improvement=target_improvement,
            max_iterations=max_iterations,
            iteration=0,
            patience=patience,
            cycle_state=TuningState.PENDING.value,
            best_score=baseline_score,
            baseline_score=baseline_score,
            current_parameters={},
            best_parameters={},
            exploration_history=[],
            exploitation_history=[],
            linked_plan_id=linked_plan_id,
        )
        self.db.add(cycle)
        await self.db.flush()
        logger.info(f"Created optimization cycle: {cycle_id}")
        return cycle
    
    async def start_cycle(
        self,
        cycle_id: str,
    ) -> Optional[AdaptiveOptimizationCycle]:
        """
        Start an optimization cycle.
        
        Args:
            cycle_id: Cycle to start
            
        Returns:
            Updated cycle
        """
        cycle = await self._get_cycle_by_cycle_id(cycle_id)
        if not cycle:
            return None
        
        cycle.cycle_state = TuningState.RUNNING.value
        cycle.started_at = datetime.utcnow()
        
        # Initialize with baseline parameters
        cycle.current_parameters = self._sample_initial_parameters(
            cycle.parameter_space
        )
        
        await self.db.flush()
        logger.info(f"Started optimization cycle: {cycle_id}")
        return cycle
    
    async def _get_cycle_by_cycle_id(self, cycle_id: str) -> Optional[AdaptiveOptimizationCycle]:
        """Get cycle by cycle_id field."""
        query = select(AdaptiveOptimizationCycle).where(
            AdaptiveOptimizationCycle.cycle_id == cycle_id
        )
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def record_iteration(
        self,
        cycle_id: str,
        parameters: Dict[str, Any],
        score: float,
    ) -> Optional[AdaptiveOptimizationCycle]:
        """
        Record an optimization iteration result.
        
        Args:
            cycle_id: Cycle identifier
            parameters: Parameters evaluated
            score: Achievement score
            
        Returns:
            Updated cycle with convergence status
        """
        cycle = await self._get_cycle_by_cycle_id(cycle_id)
        if not cycle or cycle.cycle_state != TuningState.RUNNING.value:
            return None
        
        cycle.iteration += 1
        cycle.current_parameters = parameters
        cycle.current_score = score
        
        # Track best
        if cycle.best_score is None or score > cycle.best_score:
            cycle.best_score = score
            cycle.best_parameters = parameters.copy()
            cycle.improvements_found = cycle.improvements_found or []
            cycle.improvements_found.append({
                'iteration': cycle.iteration,
                'parameters': parameters.copy(),
                'score': score,
                'timestamp': datetime.utcnow().isoformat(),
            })
        
        # Record in history
        history_entry = {
            'iteration': cycle.iteration,
            'parameters': parameters,
            'score': score,
            'is_exploration': self._is_exploration(parameters, cycle),
        }
        
        if history_entry['is_exploration']:
            exploration = cycle.exploration_history or []
            exploration.append(history_entry)
            cycle.exploration_history = exploration
        else:
            exploitation = cycle.exploitation_history or []
            exploitation.append(history_entry)
            cycle.exploitation_history = exploitation
        
        # Check convergence
        cycle = await self._check_convergence(cycle)
        
        await self.db.flush()
        return cycle
    
    def _is_exploration(
        self,
        parameters: Dict[str, Any],
        cycle: AdaptiveOptimizationCycle,
    ) -> bool:
        """Determine if iteration was exploratory (trying new parameter regions)."""
        # Simple heuristic: if significantly different from best, it's exploration
        if not cycle.best_parameters:
            return True
        
        param_diff = sum(
            abs(parameters.get(k, 0) - cycle.best_parameters.get(k, 0))
            for k in set(list(parameters.keys()) + list(cycle.best_parameters.keys()))
        )
        
        return param_diff > 0.3  # Threshold for exploration
        
    async def _check_convergence(
        self,
        cycle: AdaptiveOptimizationCycle,
    ) -> AdaptiveOptimizationCycle:
        """Check if optimization has converged."""
        # Check max iterations
        if cycle.iteration >= cycle.max_iterations:
            cycle.cycle_state = TuningState.CONVERGED.value
            cycle.completed_at = datetime.utcnow()
            return cycle
        
        # Check convergence threshold
        if cycle.best_score is not None and cycle.baseline_score is not None:
            improvement = (cycle.best_score - cycle.baseline_score) / max(cycle.baseline_score, 0.001)
            if improvement >= cycle.target_improvement:
                cycle.cycle_state = TuningState.CONVERGED.value
                cycle.completed_at = datetime.utcnow()
                return cycle
        
        # Check patience (iterations without improvement)
        if cycle.iteration > cycle.patience:
            recent_scores = []
            exploration = cycle.exploration_history or []
            exploitation = cycle.exploitation_history or []
            all_history = exploration + exploitation
            all_history.sort(key=lambda x: x['iteration'], reverse=True)
            
            for entry in all_history[:cycle.patience]:
                if entry['score'] == cycle.best_score:
                    recent_scores.append(entry['score'])
            
            if len(set(recent_scores)) == 1:  # No improvement
                # Continue but flag that we're stuck
                pass
        
        return cycle
    
    async def stop_cycle(
        self,
        cycle_id: str,
        reason: str = "manual",
    ) -> Optional[AdaptiveOptimizationCycle]:
        """Stop an optimization cycle."""
        cycle = await self._get_cycle_by_cycle_id(cycle_id)
        if not cycle:
            return None
        
        cycle.cycle_state = TuningState.CANCELLED.value
        cycle.completed_at = datetime.utcnow()
        cycle.failed_attempts = cycle.failed_attempts or []
        cycle.failed_attempts.append({
            'reason': reason,
            'iteration': cycle.iteration,
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        await self.db.flush()
        return cycle
    
    async def get_cycle(
        self,
        cycle_id: str,
    ) -> Optional[AdaptiveOptimizationCycle]:
        """Get cycle by ID."""
        return await self._get_cycle_by_cycle_id(cycle_id)
    
    async def list_cycles(
        self,
        cycle_state: Optional[str] = None,
        context_key: Optional[str] = None,
        limit: int = 50,
    ) -> List[AdaptiveOptimizationCycle]:
        """List optimization cycles."""
        query = select(AdaptiveOptimizationCycle).where(
            AdaptiveOptimizationCycle.deleted_at.is_(None)
        )
        
        if cycle_state:
            query = query.where(AdaptiveOptimizationCycle.cycle_state == cycle_state)
        if context_key:
            query = query.where(AdaptiveOptimizationCycle.context_key == context_key)
        
        query = query.order_by(desc(AdaptiveOptimizationCycle.started_at))
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_active_cycles(self) -> List[AdaptiveOptimizationCycle]:
        """Get all active (running) optimization cycles."""
        query = select(AdaptiveOptimizationCycle).where(
            and_(
                AdaptiveOptimizationCycle.cycle_state == TuningState.RUNNING.value,
                AdaptiveOptimizationCycle.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    # ---- Parameter Optimization ----
    
    def _sample_initial_parameters(
        self,
        parameter_space: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Sample initial parameters from search space."""
        params = {}
        for param_name, param_def in parameter_space.items():
            param_type = param_def.get('type', 'float')
            if param_type == 'float':
                min_val = param_def.get('min', 0)
                max_val = param_def.get('max', 1)
                params[param_name] = random.uniform(min_val, max_val)
            elif param_type == 'int':
                min_val = param_def.get('min', 0)
                max_val = param_def.get('max', 100)
                params[param_name] = random.randint(min_val, max_val)
            elif param_type == 'choice':
                choices = param_def.get('choices', [])
                if choices:
                    params[param_name] = random.choice(choices)
            elif param_type == 'log':
                min_val = math.log(param_def.get('min', 1))
                max_val = math.log(param_def.get('max', 100))
                params[param_name] = math.exp(random.uniform(min_val, max_val))
        return params
    
    def suggest_next_parameters(
        self,
        cycle: AdaptiveOptimizationCycle,
        strategy: str = "balanced",
    ) -> Dict[str, Any]:
        """
        Suggest next parameters based on optimization history.
        
        Args:
            cycle: Current optimization cycle
            strategy: Strategy (explore, exploit, balanced)
            
        Returns:
            Suggested parameters
        """
        parameter_space = cycle.parameter_space
        best_params = cycle.best_parameters or {}
        
        if strategy == "explore":
            # Focus on exploring new regions
            return self._sample_initial_parameters(parameter_space)
        elif strategy == "exploit":
            # Focus on refining best region
            return self._refine_parameters(best_params, parameter_space, 0.1)
        else:  # balanced
            # Mix exploration and exploitation
            if random.random() < 0.3:
                return self._sample_initial_parameters(parameter_space)
            else:
                return self._refine_parameters(best_params, parameter_space, 0.2)
    
    def _refine_parameters(
        self,
        base_params: Dict[str, Any],
        parameter_space: Dict[str, Any],
        noise_scale: float,
    ) -> Dict[str, Any]:
        """Refine parameters with bounded noise."""
        refined = {}
        for param_name, current_val in base_params.items():
            param_def = parameter_space.get(param_name, {})
            param_type = param_def.get('type', 'float')
            
            if param_type == 'float':
                min_val = param_def.get('min', 0)
                max_val = param_def.get('max', 1)
                range_size = max_val - min_val
                noise = random.gauss(0, noise_scale * range_size)
                new_val = current_val + noise
                refined[param_name] = max(min_val, min(max_val, new_val))
            elif param_type == 'int':
                min_val = param_def.get('min', 0)
                max_val = param_def.get('max', 100)
                range_size = max_val - min_val
                noise = random.gauss(0, noise_scale * range_size)
                new_val = current_val + noise
                refined[param_name] = max(min_val, min(max_val, int(new_val)))
            elif param_type == 'choice':
                choices = param_def.get('choices', [])
                if choices and random.random() < 0.2:  # Small chance to change
                    refined[param_name] = random.choice(choices)
                else:
                    refined[param_name] = current_val
            else:
                refined[param_name] = current_val
        
        return refined
    
    # ---- Runtime Evolution Metrics ----
    
    async def record_metric(
        self,
        metric_type: str,
        metric_name: str,
        value: float,
        subject_kind: Optional[str] = None,
        subject_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        baseline_value: Optional[float] = None,
    ) -> RuntimeEvolutionMetric:
        """
        Record a runtime evolution metric.
        
        Args:
            metric_type: Metric category
            metric_name: Metric name
            value: Metric value
            subject_kind: Subject type
            subject_id: Subject identifier
            context: Additional context
            tags: Metric tags
            baseline_value: Baseline for comparison
            
        Returns:
            Created RuntimeEvolutionMetric
        """
        metric = RuntimeEvolutionMetric(
            metric_type=metric_type,
            metric_name=metric_name,
            value=value,
            subject_kind=subject_kind,
            subject_id=subject_id,
            context=context,
            tags=tags,
            recorded_at=datetime.utcnow(),
            baseline_value=baseline_value,
            delta=value - baseline_value if baseline_value is not None else None,
        )
        
        if baseline_value and baseline_value != 0:
            metric.delta_percentage = ((value - baseline_value) / baseline_value) * 100
        
        # Determine change direction
        if baseline_value is not None:
            if value > baseline_value * 1.05:
                metric.change_direction = "improving"
            elif value < baseline_value * 0.95:
                metric.change_direction = "declining"
            else:
                metric.change_direction = "stable"
        
        self.db.add(metric)
        await self.db.flush()
        return metric
    
    async def get_metrics(
        self,
        metric_name: Optional[str] = None,
        subject_kind: Optional[str] = None,
        subject_id: Optional[str] = None,
        metric_type: Optional[str] = None,
        time_window: Optional[timedelta] = None,
        limit: int = 100,
    ) -> List[RuntimeEvolutionMetric]:
        """Query runtime metrics."""
        query = select(RuntimeEvolutionMetric).where(
            RuntimeEvolutionMetric.deleted_at.is_(None)
        )
        
        if metric_name:
            query = query.where(RuntimeEvolutionMetric.metric_name == metric_name)
        if subject_kind:
            query = query.where(RuntimeEvolutionMetric.subject_kind == subject_kind)
        if subject_id:
            query = query.where(RuntimeEvolutionMetric.subject_id == subject_id)
        if metric_type:
            query = query.where(RuntimeEvolutionMetric.metric_type == metric_type)
        if time_window:
            cutoff = datetime.utcnow() - time_window
            query = query.where(RuntimeEvolutionMetric.recorded_at >= cutoff)
        
        query = query.order_by(desc(RuntimeEvolutionMetric.recorded_at))
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_metric_trends(
        self,
        metric_name: str,
        subject_id: Optional[str] = None,
        period_hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Get metric trend analysis.
        
        Args:
            metric_name: Metric to analyze
            subject_id: Subject identifier
            period_hours: Analysis period
            
        Returns:
            Trend analysis results
        """
        cutoff = datetime.utcnow() - timedelta(hours=period_hours)
        
        query = select(RuntimeEvolutionMetric).where(
            and_(
                RuntimeEvolutionMetric.metric_name == metric_name,
                RuntimeEvolutionMetric.recorded_at >= cutoff,
                RuntimeEvolutionMetric.deleted_at.is_(None),
            )
        ).order_by(RuntimeEvolutionMetric.recorded_at)
        
        if subject_id:
            query = query.where(RuntimeEvolutionMetric.subject_id == subject_id)
        
        result = await self.db.execute(query)
        metrics = list(result.scalars().all())
        
        if not metrics:
            return {
                'count': 0,
                'trend': 'unknown',
                'values': [],
            }
        
        values = [m.value for m in metrics]
        
        # Calculate trend
        if len(values) >= 2:
            # Simple linear regression slope
            n = len(values)
            x_mean = (n - 1) / 2
            y_mean = sum(values) / n
            
            numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
            denominator = sum((i - x_mean) ** 2 for i in range(n))
            
            if denominator != 0:
                slope = numerator / denominator
            else:
                slope = 0
            
            if slope > 0.01:
                trend = "increasing"
            elif slope < -0.01:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            'count': len(metrics),
            'trend': trend,
            'current': values[-1] if values else None,
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'values': values,
            'timestamps': [m.recorded_at.isoformat() for m in metrics],
        }
    
    # ---- Optimization Statistics ----
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get self-evolution system statistics."""
        # Cycle counts by state
        state_query = select(
            AdaptiveOptimizationCycle.cycle_state,
            func.count(AdaptiveOptimizationCycle.id).label('count'),
        ).where(AdaptiveOptimizationCycle.deleted_at.is_(None)).group_by(
            AdaptiveOptimizationCycle.cycle_state
        )
        
        state_result = await self.db.execute(state_query)
        by_state = {row.cycle_state: row.count for row in state_result.all()}
        
        # Cycle counts by context
        context_query = select(
            AdaptiveOptimizationCycle.context_key,
            func.count(AdaptiveOptimizationCycle.id).label('count'),
        ).where(AdaptiveOptimizationCycle.deleted_at.is_(None)).group_by(
            AdaptiveOptimizationCycle.context_key
        )
        
        context_result = await self.db.execute(context_query)
        by_context = {row.context_key: row.count for row in context_result.all()}
        
        # Best improvement achieved
        best_query = select(func.max(AdaptiveOptimizationCycle.best_score)).where(
            and_(
                AdaptiveOptimizationCycle.deleted_at.is_(None),
                AdaptiveOptimizationCycle.best_score.isnot(None),
            )
        )
        best_result = await self.db.execute(best_query)
        best_score = best_result.scalar()
        
        # Metric counts
        metric_count_query = select(func.count(RuntimeEvolutionMetric.id)).where(
            RuntimeEvolutionMetric.deleted_at.is_(None)
        )
        metric_result = await self.db.execute(metric_count_query)
        metric_count = metric_result.scalar() or 0
        
        return {
            'total_cycles': sum(by_state.values()),
            'by_state': by_state,
            'by_context': by_context,
            'best_score_achieved': float(best_score) if best_score else None,
            'active_cycles': by_state.get(TuningState.RUNNING.value, 0),
            'converged_cycles': by_state.get(TuningState.CONVERGED.value, 0),
            'total_metrics_recorded': metric_count,
        }
    
    # ---- Adaptive Learning Loop ----
    
    async def run_optimization(
        self,
        cycle_id: str,
        evaluate_fn: Callable[[Dict[str, Any]], float],
        max_iterations: Optional[int] = None,
    ) -> OptimizationResult:
        """
        Run a complete optimization cycle.
        
        Args:
            cycle_id: Cycle to run
            evaluate_fn: Function that evaluates parameters and returns score
            max_iterations: Override max iterations
            
        Returns:
            Final optimization result
        """
        cycle = await self._get_cycle_by_cycle_id(cycle_id)
        if not cycle:
            raise ValueError(f"Cycle {cycle_id} not found")
        
        if max_iterations:
            cycle.max_iterations = max_iterations
        
        # Start cycle
        await self.start_cycle(cycle_id)
        
        # Run iterations
        while cycle.cycle_state == TuningState.RUNNING.value:
            # Get current or suggest new parameters
            if cycle.iteration == 0:
                params = cycle.current_parameters
            else:
                params = self.suggest_next_parameters(cycle, strategy="balanced")
            
            # Evaluate
            score = evaluate_fn(params)
            
            # Record iteration
            cycle = await self.record_iteration(cycle_id, params, score)
            
            # Check if converged
            if cycle.cycle_state in [TuningState.CONVERGED.value, TuningState.FAILED.value]:
                break
        
        # Return result
        best_score = cycle.best_score or 0
        baseline = cycle.baseline_score or best_score
        improvement = (best_score - baseline) / max(baseline, 0.001) if baseline != 0 else 0
        
        return OptimizationResult(
            parameters=cycle.best_parameters or {},
            score=best_score,
            improvement=improvement,
            converged=cycle.cycle_state == TuningState.CONVERGED.value,
            iteration=cycle.iteration,
        )
    
    # ---- Workflow Refinement ----
    
    async def record_workflow_refinement(
        self,
        workflow_id: str,
        original_parameters: Dict[str, Any],
        refined_parameters: Dict[str, Any],
        improvement_score: float,
    ) -> RuntimeEvolutionMetric:
        """Record a workflow parameter refinement."""
        return await self.record_metric(
            metric_type="workflow_refinement",
            metric_name="parameter_improvement",
            value=improvement_score,
            subject_kind="workflow",
            subject_id=workflow_id,
            context={
                'original': original_parameters,
                'refined': refined_parameters,
            },
            tags=["workflow", "refinement"],
            baseline_value=0.5,
        )
    
    async def suggest_workflow_improvements(
        self,
        workflow_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Suggest improvements for a workflow based on historical data.
        
        Args:
            workflow_id: Workflow to improve
            
        Returns:
            List of improvement suggestions
        """
        # Get recent metrics for this workflow
        metrics = await self.get_metrics(
            subject_id=workflow_id,
            subject_kind="workflow",
            time_window=timedelta(days=7),
            limit=50,
        )
        
        if not metrics:
            return []
        
        # Analyze patterns
        suggestions = []
        
        # Group by metric type
        by_type: Dict[str, List[RuntimeEvolutionMetric]] = {}
        for m in metrics:
            if m.metric_type not in by_type:
                by_type[m.metric_type] = []
            by_type[m.metric_type].append(m)
        
        # Generate suggestions
        for metric_type, type_metrics in by_type.items():
            values = [m.value for m in type_metrics]
            avg_value = sum(values) / len(values)
            
            if metric_type == "performance" and avg_value < 0.7:
                suggestions.append({
                    'type': 'performance',
                    'priority': 'high',
                    'description': 'Performance metrics below optimal threshold',
                    'current_avg': avg_value,
                    'target': 0.8,
                })
            elif metric_type == "quality" and avg_value < 0.6:
                suggestions.append({
                    'type': 'quality',
                    'priority': 'medium',
                    'description': 'Quality metrics need improvement',
                    'current_avg': avg_value,
                    'target': 0.75,
                })
        
        return suggestions


# ---- Module-level Functions ----

async def run_quick_optimization(
    context_key: str,
    target_metric: str,
    parameter_space: Dict[str, Any],
    evaluate_fn: Callable[[Dict[str, Any]], float],
    target_improvement: float = 0.1,
) -> OptimizationResult:
    """
    Run a quick optimization without persistent cycle.
    
    Args:
        context_key: Optimization context
        target_metric: Metric to optimize
        parameter_space: Search space
        evaluate_fn: Evaluation function
        target_improvement: Target improvement
        
    Returns:
        Optimization result
    """
    import uuid
    cycle_id = f"quick_{uuid.uuid4().hex[:8]}"
    
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        service = SelfEvolutionService(db)
        try:
            # Create temporary cycle
            cycle = await service.create_cycle(
                cycle_id=cycle_id,
                name=f"Quick optimization - {context_key}",
                context_key=context_key,
                target_metric=target_metric,
                parameter_space=parameter_space,
                target_improvement=target_improvement,
                max_iterations=5,  # Limited iterations for quick optimization
            )
            
            # Run optimization
            result = await service.run_optimization(cycle_id, evaluate_fn)
            
            return result
        except Exception as e:
            logger.error(f"Quick optimization failed: {e}")
            raise