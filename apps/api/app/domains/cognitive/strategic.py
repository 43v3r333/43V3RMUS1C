"""
Strategic Planning Service

Predictive orchestration planning with long-horizon workflow planning,
objective coordination, and adaptive planning heuristics.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
import uuid as uuid_lib

from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cognitive import (
    StrategicExecutionPlan, PlanStatus, PlanHorizon, StrategyKind,
    OrchestrationForecast, ForecastKind, ForecastHorizon
)
from app.services.base import BaseService

logger = logging.getLogger(__name__)


class StrategicPlanningService:
    """
    Strategic execution planning system.
    
    Capabilities:
    - Predictive execution planning: Generate execution roadmaps
    - Workflow strategy optimization: Optimize workflow sequences
    - Autonomous scheduling: Schedule tasks based on constraints
    - Long-running coordination: Manage extended workflows
    - Adaptive orchestration evolution: Evolve plans based on feedback
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ---- Plan Management ----
    
    async def create_plan(
        self,
        name: str,
        plan_type: str,
        strategy_kind: str,
        objectives: List[Dict[str, Any]],
        horizon: str = PlanHorizon.MEDIUM_TERM.value,
        description: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        constraints: Optional[Dict[str, Any]] = None,
        required_resources: Optional[Dict[str, Any]] = None,
        estimated_start: Optional[datetime] = None,
        estimated_end: Optional[datetime] = None,
        priority: int = 5,
        parent_plan_id: Optional[UUID] = None,
    ) -> StrategicExecutionPlan:
        """
        Create a new strategic execution plan.
        
        Args:
            name: Plan name
            plan_type: Type of plan (workflow, render, creative)
            strategy_kind: Strategy classification
            objectives: List of strategic objectives
            horizon: Planning time horizon
            description: Plan description
            dependencies: Plan dependencies
            constraints: Planning constraints
            required_resources: Resource requirements
            estimated_start: Estimated start time
            estimated_end: Estimated end time
            priority: Plan priority (1-10)
            parent_plan_id: Parent plan ID for sub-plans
            
        Returns:
            Created StrategicExecutionPlan instance
        """
        plan = StrategicExecutionPlan(
            name=name,
            plan_type=plan_type,
            strategy_kind=strategy_kind,
            status=PlanStatus.DRAFT.value,
            horizon=horizon,
            description=description,
            objectives=objectives,
            dependencies=dependencies,
            constraints=constraints,
            required_resources=required_resources,
            estimated_start=estimated_start,
            estimated_end=estimated_end,
            priority=priority,
            planning_depth=3,
            confidence_score=0.5,
            parent_plan_id=parent_plan_id,
        )
        self.db.add(plan)
        await self.db.flush()
        logger.info(f"Created strategic plan: {plan.id} [{name}]")
        return plan
    
    async def activate_plan(
        self,
        plan_id: UUID,
        allocated_resources: Optional[Dict[str, Any]] = None,
    ) -> Optional[StrategicExecutionPlan]:
        """
        Activate a draft plan for execution.
        
        Args:
            plan_id: Plan to activate
            allocated_resources: Resources allocated to the plan
            
        Returns:
            Updated plan or None if not found
        """
        plan = await self.db.get(StrategicExecutionPlan, plan_id)
        if not plan:
            return None
        
        plan.status = PlanStatus.ACTIVE.value
        plan.actual_start = datetime.utcnow()
        plan.allocated_resources = allocated_resources or plan.allocated_resources
        
        await self.db.flush()
        logger.info(f"Activated plan: {plan_id}")
        return plan
    
    async def complete_plan(
        self,
        plan_id: UUID,
        actual_outcomes: Optional[Dict[str, Any]] = None,
    ) -> Optional[StrategicExecutionPlan]:
        """
        Mark a plan as completed.
        
        Args:
            plan_id: Plan to complete
            actual_outcomes: Actual outcomes achieved
            
        Returns:
            Updated plan or None if not found
        """
        plan = await self.db.get(StrategicExecutionPlan, plan_id)
        if not plan:
            return None
        
        plan.status = PlanStatus.COMPLETED.value
        plan.actual_end = datetime.utcnow()
        if actual_outcomes:
            plan.actual_outcomes = actual_outcomes
        
        # Calculate confidence based on outcomes
        if plan.expected_outcomes and actual_outcomes:
            plan.confidence_score = self._calculate_outcome_confidence(
                plan.expected_outcomes, actual_outcomes
            )
        
        await self.db.flush()
        logger.info(f"Completed plan: {plan_id}")
        return plan
    
    async def pause_plan(self, plan_id: UUID) -> Optional[StrategicExecutionPlan]:
        """Pause an active plan."""
        plan = await self.db.get(StrategicExecutionPlan, plan_id)
        if not plan or plan.status != PlanStatus.ACTIVE.value:
            return None
        
        plan.status = PlanStatus.PAUSED.value
        await self.db.flush()
        return plan
    
    async def resume_plan(self, plan_id: UUID) -> Optional[StrategicExecutionPlan]:
        """Resume a paused plan."""
        plan = await self.db.get(StrategicExecutionPlan, plan_id)
        if not plan or plan.status != PlanStatus.PAUSED.value:
            return None
        
        plan.status = PlanStatus.ACTIVE.value
        await self.db.flush()
        return plan
    
    async def fail_plan(
        self,
        plan_id: UUID,
        reason: Optional[str] = None,
    ) -> Optional[StrategicExecutionPlan]:
        """Mark a plan as failed."""
        plan = await self.db.get(StrategicExecutionPlan, plan_id)
        if not plan:
            return None
        
        plan.status = PlanStatus.FAILED.value
        plan.actual_end = datetime.utcnow()
        if reason:
            plan.description = f"{plan.description or ''}\nFailure: {reason}"
        
        await self.db.flush()
        return plan
    
    async def get_plan(self, plan_id: UUID) -> Optional[StrategicExecutionPlan]:
        """Get a plan by ID."""
        return await self.db.get(StrategicExecutionPlan, plan_id)
    
    async def update_plan(
        self,
        plan_id: UUID,
        **kwargs,
    ) -> Optional[StrategicExecutionPlan]:
        """
        Update plan attributes.
        
        Args:
            plan_id: Plan to update
            **kwargs: Attributes to update
            
        Returns:
            Updated plan or None
        """
        plan = await self.db.get(StrategicExecutionPlan, plan_id)
        if not plan:
            return None
        
        for key, value in kwargs.items():
            if hasattr(plan, key) and value is not None:
                setattr(plan, key, value)
        
        await self.db.flush()
        return plan
    
    # ---- Plan Queries ----
    
    async def list_plans(
        self,
        status: Optional[str] = None,
        strategy_kind: Optional[str] = None,
        horizon: Optional[str] = None,
        min_priority: Optional[int] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[StrategicExecutionPlan]:
        """
        List plans with filtering.
        
        Args:
            status: Filter by status
            strategy_kind: Filter by strategy type
            horizon: Filter by planning horizon
            min_priority: Minimum priority threshold
            limit: Maximum results
            offset: Result offset
            
        Returns:
            List of matching plans
        """
        query = select(StrategicExecutionPlan).where(
            StrategicExecutionPlan.deleted_at.is_(None)
        )
        
        if status:
            query = query.where(StrategicExecutionPlan.status == status)
        if strategy_kind:
            query = query.where(StrategicExecutionPlan.strategy_kind == strategy_kind)
        if horizon:
            query = query.where(StrategicExecutionPlan.horizon == horizon)
        if min_priority is not None:
            query = query.where(StrategicExecutionPlan.priority >= min_priority)
        
        query = query.order_by(desc(StrategicExecutionPlan.priority), desc(StrategicExecutionPlan.created_at))
        query = query.offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_active_plans(
        self,
        strategy_kind: Optional[str] = None,
    ) -> List[StrategicExecutionPlan]:
        """Get all active plans, optionally filtered by strategy kind."""
        query = select(StrategicExecutionPlan).where(
            and_(
                StrategicExecutionPlan.status == PlanStatus.ACTIVE.value,
                StrategicExecutionPlan.deleted_at.is_(None),
            )
        )
        
        if strategy_kind:
            query = query.where(StrategicExecutionPlan.strategy_kind == strategy_kind)
        
        query = query.order_by(desc(StrategicExecutionPlan.priority))
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_sub_plans(
        self,
        parent_plan_id: UUID,
    ) -> List[StrategicExecutionPlan]:
        """Get all sub-plans of a parent plan."""
        query = select(StrategicExecutionPlan).where(
            and_(
                StrategicExecutionPlan.parent_plan_id == parent_plan_id,
                StrategicExecutionPlan.deleted_at.is_(None),
            )
        ).order_by(StrategicExecutionPlan.priority)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    # ---- Plan Dependencies ----
    
    async def add_dependency(
        self,
        plan_id: UUID,
        dependency_id: str,
        dependency_type: str = "plan",
    ) -> Optional[StrategicExecutionPlan]:
        """Add a dependency to a plan."""
        plan = await self.db.get(StrategicExecutionPlan, plan_id)
        if not plan:
            return None
        
        dependencies = plan.dependencies or []
        dependencies.append({
            'id': dependency_id,
            'type': dependency_type,
            'added_at': datetime.utcnow().isoformat(),
        })
        plan.dependencies = dependencies
        
        await self.db.flush()
        return plan
    
    async def check_dependencies(
        self,
        plan_id: UUID,
    ) -> Tuple[bool, List[str]]:
        """
        Check if all plan dependencies are satisfied.
        
        Args:
            plan_id: Plan to check
            
        Returns:
            Tuple of (all_satisfied, blocked_by)
        """
        plan = await self.db.get(StrategicExecutionPlan, plan_id)
        if not plan:
            return False, ["Plan not found"]
        
        dependencies = plan.dependencies or []
        if not dependencies:
            return True, []
        
        blocked_by = []
        for dep in dependencies:
            if dep.get('type') == 'plan':
                dep_id = dep.get('id')
                try:
                    dep_uuid = UUID(dep_id)
                    dep_plan = await self.db.get(StrategicExecutionPlan, dep_uuid)
                    if dep_plan and dep_plan.status != PlanStatus.COMPLETED.value:
                        blocked_by.append(f"Plan {dep_id} is {dep_plan.status}")
                except ValueError:
                    blocked_by.append(f"Invalid dependency: {dep_id}")
        
        return len(blocked_by) == 0, blocked_by
    
    # ---- Strategy Optimization ----
    
    async def optimize_plan_sequence(
        self,
        plan_id: UUID,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Optimize the execution sequence of a plan's objectives.
        
        Args:
            plan_id: Plan to optimize
            
        Returns:
            Optimized sequence of objectives
        """
        plan = await self.db.get(StrategicExecutionPlan, plan_id)
        if not plan or not plan.objectives:
            return None
        
        objectives = plan.objectives
        
        # Simple dependency-based ordering
        # In a real implementation, this would use more sophisticated algorithms
        optimized = sorted(
            objectives,
            key=lambda obj: (
                obj.get('priority', 5),
                obj.get('estimated_duration', 60),
                -obj.get('impact', 0.5),
            ),
            reverse=True,
        )
        
        # Update plan with optimized sequence
        plan.objectives = [
            {**obj, 'sequence_order': i}
            for i, obj in enumerate(optimized)
        ]
        
        await self.db.flush()
        logger.info(f"Optimized plan sequence: {plan_id}")
        return optimized
    
    async def evaluate_plan_feasibility(
        self,
        plan_id: UUID,
    ) -> Dict[str, Any]:
        """
        Evaluate the feasibility of a plan.
        
        Args:
            plan_id: Plan to evaluate
            
        Returns:
            Feasibility assessment
        """
        plan = await self.db.get(StrategicExecutionPlan, plan_id)
        if not plan:
            return {'feasible': False, 'reason': 'Plan not found'}
        
        issues = []
        score = 1.0
        
        # Check constraints
        if plan.constraints:
            constraints = plan.constraints
            # Validate required fields
            if not plan.objectives:
                issues.append("No objectives defined")
                score -= 0.3
        
        # Check timeline
        if plan.estimated_start and plan.estimated_end:
            duration = (plan.estimated_end - plan.estimated_start).total_seconds()
            if duration <= 0:
                issues.append("Invalid timeline")
                score -= 0.2
        
        # Check dependencies
        deps_satisfied, blocked = await self.check_dependencies(plan_id)
        if not deps_satisfied:
            issues.extend(blocked)
            score -= 0.2 * len(blocked)
        
        # Check resources
        if not plan.required_resources:
            issues.append("No resource requirements defined")
            score -= 0.1
        
        return {
            'feasible': score >= 0.5,
            'score': max(0, score),
            'issues': issues,
            'recommendations': self._generate_recommendations(issues),
        }
    
    def _calculate_outcome_confidence(
        self,
        expected: Dict[str, Any],
        actual: Dict[str, Any],
    ) -> float:
        """Calculate confidence score based on expected vs actual outcomes."""
        if not expected or not actual:
            return 0.5
        
        # Simple matching based on key presence
        expected_keys = set(expected.keys())
        actual_keys = set(actual.keys())
        
        match_ratio = len(expected_keys & actual_keys) / len(expected_keys | actual_keys)
        
        # Calculate value similarity for matching keys
        value_similarities = []
        for key in expected_keys & actual_keys:
            exp_val = expected[key]
            act_val = actual[key]
            
            if isinstance(exp_val, (int, float)) and isinstance(act_val, (int, float)):
                diff = abs(exp_val - act_val)
                max_val = max(abs(exp_val), abs(act_val), 1)
                similarity = 1 - min(1, diff / max_val)
                value_similarities.append(similarity)
        
        if value_similarities:
            value_score = sum(value_similarities) / len(value_similarities)
        else:
            value_score = match_ratio
        
        return (match_ratio + value_score) / 2
    
    def _generate_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations to address issues."""
        recommendations = []
        for issue in issues:
            if "No objectives" in issue:
                recommendations.append("Define clear, measurable objectives")
            if "Invalid timeline" in issue:
                recommendations.append("Set realistic start and end dates")
            if "dependencies" in issue.lower():
                recommendations.append("Review and resolve dependency conflicts")
            if "resources" in issue.lower():
                recommendations.append("Define specific resource requirements")
        return recommendations
    
    # ---- Plan Statistics ----
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get planning system statistics."""
        # Status breakdown
        status_query = select(
            StrategicExecutionPlan.status,
            func.count(StrategicExecutionPlan.id).label('count'),
        ).where(StrategicExecutionPlan.deleted_at.is_(None)).group_by(StrategicExecutionPlan.status)
        
        status_result = await self.db.execute(status_query)
        by_status = {row.status: row.count for row in status_result.all()}
        
        # Strategy breakdown
        strategy_query = select(
            StrategicExecutionPlan.strategy_kind,
            func.count(StrategicExecutionPlan.id).label('count'),
        ).where(StrategicExecutionPlan.deleted_at.is_(None)).group_by(StrategicExecutionPlan.strategy_kind)
        
        strategy_result = await self.db.execute(strategy_query)
        by_strategy = {row.strategy_kind: row.count for row in strategy_result.all()}
        
        # Average confidence
        avg_conf_query = select(func.avg(StrategicExecutionPlan.confidence_score)).where(
            StrategicExecutionPlan.deleted_at.is_(None)
        )
        avg_result = await self.db.execute(avg_conf_query)
        avg_confidence = float(avg_result.scalar() or 0.5)
        
        return {
            'total_plans': sum(by_status.values()),
            'by_status': by_status,
            'by_strategy': by_strategy,
            'avg_confidence': avg_confidence,
            'active_count': by_status.get(PlanStatus.ACTIVE.value, 0),
            'completed_count': by_status.get(PlanStatus.COMPLETED.value, 0),
        }


# ---- Orchestration Forecasting ----

class OrchestrationForecastService:
    """
    Predictive runtime intelligence system.
    
    Capabilities:
    - Execution forecasting: Predict execution durations
    - Resource prediction: Predict resource requirements
    - Failure probability: Estimate failure likelihood
    - Queue time estimation: Predict wait times
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_forecast(
        self,
        subject_kind: str,
        subject_key: str,
        forecast_kind: str,
        predicted_value: float,
        horizon: str,
        predicted_for: datetime,
        confidence: float = 0.5,
        lower_bound: Optional[float] = None,
        upper_bound: Optional[float] = None,
        features_used: Optional[Dict[str, Any]] = None,
        context_data: Optional[Dict[str, Any]] = None,
        prediction_method: str = "statistical",
        related_plan_id: Optional[UUID] = None,
    ) -> OrchestrationForecast:
        """
        Create a new execution forecast.
        
        Args:
            subject_kind: Type of subject (workflow, render_job)
            subject_key: Subject identifier
            forecast_kind: Type of forecast (duration, queue_time, etc.)
            predicted_value: Predicted value
            horizon: Time horizon
            predicted_for: When the prediction applies
            confidence: Forecast confidence
            lower_bound: Lower prediction bound
            upper_bound: Upper prediction bound
            features_used: ML features used
            context_data: Additional context
            prediction_method: Method used for prediction
            related_plan_id: Related strategic plan
            
        Returns:
            Created OrchestrationForecast instance
        """
        forecast = OrchestrationForecast(
            subject_kind=subject_kind,
            subject_key=subject_key,
            forecast_kind=forecast_kind,
            predicted_value=predicted_value,
            horizon=horizon,
            predicted_for=predicted_for,
            confidence=confidence,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            features_used=features_used,
            context_data=context_data,
            prediction_method=prediction_method,
            lifecycle_state="pending",
            related_plan_id=related_plan_id,
        )
        self.db.add(forecast)
        await self.db.flush()
        return forecast
    
    async def validate_forecast(
        self,
        forecast_id: UUID,
        actual_value: float,
    ) -> Optional[OrchestrationForecast]:
        """
        Validate a forecast against actual value.
        
        Args:
            forecast_id: Forecast to validate
            actual_value: Actual observed value
            
        Returns:
            Updated forecast with prediction error
        """
        forecast = await self.db.get(OrchestrationForecast, forecast_id)
        if not forecast:
            return None
        
        forecast.actual_value = actual_value
        forecast.prediction_error = abs(actual_value - forecast.predicted_value)
        forecast.validated_at = datetime.utcnow()
        forecast.lifecycle_state = "validated"
        
        # Update confidence based on error
        error_ratio = forecast.prediction_error / max(abs(forecast.predicted_value), 1)
        forecast.confidence = max(0.1, forecast.confidence - error_ratio * 0.1)
        
        await self.db.flush()
        return forecast
    
    async def get_active_forecasts(
        self,
        subject_kind: Optional[str] = None,
        subject_key: Optional[str] = None,
        forecast_kind: Optional[str] = None,
        horizon: Optional[str] = None,
        limit: int = 50,
    ) -> List[OrchestrationForecast]:
        """Get active forecasts with optional filtering."""
        query = select(OrchestrationForecast).where(
            OrchestrationForecast.lifecycle_state.in_(["pending", "validated"])
        )
        
        if subject_kind:
            query = query.where(OrchestrationForecast.subject_kind == subject_kind)
        if subject_key:
            query = query.where(OrchestrationForecast.subject_key == subject_key)
        if forecast_kind:
            query = query.where(OrchestrationForecast.forecast_kind == forecast_kind)
        if horizon:
            query = query.where(OrchestrationForecast.horizon == horizon)
        
        query = query.order_by(desc(OrchestrationForecast.confidence), OrchestrationForecast.predicted_for)
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def expire_old_forecasts(self, max_age_hours: int = 24) -> int:
        """Expire forecasts older than max_age_hours."""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        query = select(OrchestrationForecast).where(
            and_(
                OrchestrationForecast.lifecycle_state == "pending",
                OrchestrationForecast.predicted_for < cutoff,
            )
        )
        result = await self.db.execute(query)
        
        count = 0
        for forecast in result.scalars().all():
            forecast.lifecycle_state = "expired"
            count += 1
        
        await self.db.flush()
        return count
    
    async def get_forecast_accuracy(
        self,
        subject_kind: Optional[str] = None,
        time_window: Optional[timedelta] = None,
    ) -> Dict[str, Any]:
        """Calculate forecast accuracy metrics."""
        query = select(OrchestrationForecast).where(
            OrchestrationForecast.lifecycle_state == "validated"
        )
        
        if subject_kind:
            query = query.where(OrchestrationForecast.subject_kind == subject_kind)
        if time_window:
            cutoff = datetime.utcnow() - time_window
            query = query.where(OrchestrationForecast.validated_at >= cutoff)
        
        result = await self.db.execute(query)
        forecasts = list(result.scalars().all())
        
        if not forecasts:
            return {
                'count': 0,
                'avg_error': None,
                'avg_accuracy': None,
            }
        
        errors = [f.prediction_error for f in forecasts]
        accuracies = []
        for f in forecasts:
            if f.predicted_value != 0:
                accuracy = 1 - min(1, abs(f.prediction_error) / abs(f.predicted_value))
                accuracies.append(accuracy)
        
        return {
            'count': len(forecasts),
            'avg_error': sum(errors) / len(errors) if errors else 0,
            'avg_accuracy': sum(accuracies) / len(accuracies) if accuracies else 0,
            'by_forecast_kind': self._aggregate_by_kind(forecasts),
        }
    
    def _aggregate_by_kind(
        self,
        forecasts: List[OrchestrationForecast],
    ) -> Dict[str, Dict[str, float]]:
        """Aggregate accuracy by forecast kind."""
        by_kind: Dict[str, List[float]] = {}
        for f in forecasts:
            if f.forecast_kind not in by_kind:
                by_kind[f.forecast_kind] = []
            if f.predicted_value != 0:
                accuracy = 1 - min(1, abs(f.prediction_error) / abs(f.predicted_value))
                by_kind[f.forecast_kind].append(accuracy)
        
        return {
            kind: {
                'count': len(accuracies),
                'avg_accuracy': sum(accuracies) / len(accuracies) if accuracies else 0,
            }
            for kind, accuracies in by_kind.items()
        }