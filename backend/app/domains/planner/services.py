"""
Planner Services - Execution orchestration and scheduling
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Set, TypeVar
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_

from .models import (
    PlanStatus,
    ExecutionStrategy,
    PriorityLevel,
    AllocationState,
    ExecutionPlan,
    ExecutionStepRecord,
    ResourceAllocation,
    SchedulerMetric,
    WorkloadSnapshot,
    OrchestrationSession,
    ExecutionProfile,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class PlanStep:
    """Plan step for execution"""
    step_id: str
    name: str
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: float = 0.0
    priority: PriorityLevel = PriorityLevel.NORMAL
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    retry_config: Optional[Dict[str, Any]] = None


@dataclass
class ScheduleResult:
    """Result of scheduling operation"""
    scheduled: bool
    plan_id: Optional[str] = None
    start_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    allocated_resources: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class ResourceAvailability:
    """Resource availability information"""
    resource_type: str
    resource_id: str
    available: bool
    capacity: float
    utilized: float
    memory_mb: Optional[int] = None
    gpu_available: bool = False


class ExecutionPlanner:
    """
    Centralized execution planner.
    Handles execution planning, dependency resolution, and scheduling optimization.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._active_plans: Dict[str, ExecutionPlan] = {}
        self._plan_handlers: Dict[str, Callable] = {}
        self._optimization_strategies: Dict[str, Callable] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize the execution planner"""
        self._running = True
        self._register_default_handlers()
        logger.info("ExecutionPlanner initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the execution planner"""
        self._running = False
        logger.info("ExecutionPlanner shutdown")
    
    def _register_default_handlers(self) -> None:
        """Register default execution handlers"""
        self._plan_handlers["media_ingest"] = self._handle_media_ingest
        self._plan_handlers["transcode"] = self._handle_transcode
        self._plan_handlers["render"] = self._handle_render
        self._plan_handlers["ai_generate"] = self._handle_ai_generate
        self._plan_handlers["analyze"] = self._handle_analyze
        self._plan_handlers["workflow"] = self._handle_workflow
    
    # ==================== Plan Creation ====================
    
    async def create_plan(
        self,
        name: str,
        plan_type: str,
        steps: List[PlanStep],
        strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL,
        priority: PriorityLevel = PriorityLevel.NORMAL,
        owner_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        resource_requirements: Optional[Dict[str, Any]] = None,
    ) -> ExecutionPlan:
        """Create a new execution plan"""
        # Calculate estimated duration
        estimated_duration = sum(s.estimated_duration for s in steps)
        
        # Build steps list
        steps_data = [
            {
                "step_id": s.step_id,
                "name": s.name,
                "dependencies": s.dependencies,
                "estimated_duration": s.estimated_duration,
                "priority": s.priority.value,
                "resource_requirements": s.resource_requirements,
                "retry_config": s.retry_config,
            }
            for s in steps
        ]
        
        plan = ExecutionPlan(
            name=name,
            plan_type=plan_type,
            steps=steps_data,
            strategy=strategy.value,
            status=PlanStatus.PENDING.value,
            priority=priority.value,
            estimated_duration=estimated_duration,
            resource_requirements=resource_requirements,
            owner_id=owner_id,
            project_id=project_id,
            correlation_id=str(uuid4()),
        )
        
        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)
        
        self._active_plans[str(plan.id)] = plan
        
        return plan
    
    async def get_plan(self, plan_id: UUID) -> Optional[ExecutionPlan]:
        """Get execution plan by ID"""
        result = await self.db.execute(
            select(ExecutionPlan).where(ExecutionPlan.id == plan_id)
        )
        plan = result.scalar_one_or_none()
        
        if plan:
            self._active_plans[str(plan_id)] = plan
        
        return plan
    
    async def update_plan_status(
        self,
        plan: ExecutionPlan,
        status: PlanStatus,
        error: Optional[str] = None,
    ) -> ExecutionPlan:
        """Update plan status"""
        plan.status = status.value
        
        if status == PlanStatus.EXECUTING:
            plan.started_at = datetime.utcnow()
        elif status in (PlanStatus.COMPLETED, PlanStatus.FAILED, PlanStatus.CANCELLED):
            plan.completed_at = datetime.utcnow()
            if plan.started_at:
                plan.actual_duration = (plan.completed_at - plan.started_at).total_seconds()
        
        if error:
            plan.error_message = error
        
        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)
        
        return plan
    
    # ==================== Dependency Resolution ====================
    
    async def resolve_dependencies(
        self,
        steps: List[PlanStep],
    ) -> List[List[str]]:
        """
        Resolve step dependencies using topological sort.
        Returns steps grouped by execution level.
        """
        # Build adjacency list and in-degree count
        step_ids = [s.step_id for s in steps]
        in_degree: Dict[str, int] = {sid: 0 for sid in step_ids}
        adj: Dict[str, List[str]] = {sid: [] for sid in step_ids}
        
        for step in steps:
            for dep in step.dependencies:
                if dep in step_ids:
                    adj[dep].append(step.step_id)
                    in_degree[step.step_id] += 1
        
        # Topological sort with levels
        execution_order: List[List[str]] = []
        remaining = set(step_ids)
        
        while remaining:
            # Find all steps with no dependencies
            ready = [sid for sid in remaining if in_degree[sid] == 0]
            
            if not ready:
                raise ValueError("Plan contains circular dependencies")
            
            execution_order.append(ready)
            
            # Remove ready steps and update in-degrees
            for step_id in ready:
                remaining.remove(step_id)
                for dependent in adj[step_id]:
                    in_degree[dependent] -= 1
        
        return execution_order
    
    # ==================== Scheduling ====================
    
    async def schedule_plan(
        self,
        plan: ExecutionPlan,
        scheduled_start: Optional[datetime] = None,
        resource_constraints: Optional[Dict[str, Any]] = None,
    ) -> ScheduleResult:
        """Schedule an execution plan"""
        try:
            # Update status
            plan.status = PlanStatus.PLANNING.value
            self.db.add(plan)
            await self.db.commit()
            
            # Resolve dependencies
            steps_data = plan.steps or []
            steps = [
                PlanStep(
                    step_id=s["step_id"],
                    name=s["name"],
                    dependencies=s.get("dependencies", []),
                    estimated_duration=s.get("estimated_duration", 0),
                    priority=PriorityLevel(s.get("priority", "normal")),
                    resource_requirements=s.get("resource_requirements", {}),
                    retry_config=s.get("retry_config"),
                )
                for s in steps_data
            ]
            
            execution_order = await self.resolve_dependencies(steps)
            
            # Allocate resources
            allocated_resources = await self._allocate_resources(
                plan, resource_constraints
            )
            
            # Schedule start time
            scheduled_start = scheduled_start or datetime.utcnow()
            
            # Calculate completion time
            total_duration = plan.estimated_duration or 0
            estimated_completion = scheduled_start + timedelta(seconds=total_duration)
            
            # Update plan
            plan.status = PlanStatus.SCHEDULED.value
            plan.scheduled_start = scheduled_start
            plan.allocated_resources = allocated_resources
            self.db.add(plan)
            await self.db.commit()
            await self.db.refresh(plan)
            
            return ScheduleResult(
                scheduled=True,
                plan_id=str(plan.id),
                start_time=scheduled_start,
                estimated_completion=estimated_completion,
                allocated_resources=allocated_resources,
            )
            
        except Exception as e:
            logger.error(f"Plan scheduling error: {e}")
            return ScheduleResult(
                scheduled=False,
                plan_id=str(plan.id),
                error=str(e),
            )
    
    async def _allocate_resources(
        self,
        plan: ExecutionPlan,
        constraints: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Allocate resources for plan execution"""
        # Placeholder - actual implementation would query available workers
        return {
            "worker_type": "default",
            "memory_required_mb": plan.resource_requirements.get("memory_mb", 1024),
            "gpu_required": plan.resource_requirements.get("gpu", False),
        }
    
    # ==================== Plan Execution ====================
    
    async def execute_plan(
        self,
        plan: ExecutionPlan,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionPlan:
        """Execute an execution plan"""
        try:
            # Update status
            plan.status = PlanStatus.EXECUTING.value
            plan.started_at = datetime.utcnow()
            self.db.add(plan)
            await self.db.commit()
            
            # Get execution order
            steps_data = plan.steps or []
            steps = [
                PlanStep(
                    step_id=s["step_id"],
                    name=s["name"],
                    dependencies=s.get("dependencies", []),
                    estimated_duration=s.get("estimated_duration", 0),
                    priority=PriorityLevel(s.get("priority", "normal")),
                    resource_requirements=s.get("resource_requirements", {}),
                    retry_config=s.get("retry_config"),
                )
                for s in steps_data
            ]
            
            execution_order = await self.resolve_dependencies(steps)
            
            # Execute steps
            context = context or {}
            completed_count = 0
            failed_count = 0
            
            for batch in execution_order:
                for step_id in batch:
                    step_data = next((s for s in steps_data if s["step_id"] == step_id), None)
                    if not step_data:
                        continue
                    
                    # Create step record
                    step_record = ExecutionStepRecord(
                        plan_id=plan.id,
                        step_id=step_id,
                        step_name=step_data["name"],
                        step_order=len([s for s in execution_order[:execution_order.index([step_id])] + [[step_id]]]) - 1,
                        status="running",
                        scheduled_start=datetime.utcnow(),
                    )
                    
                    self.db.add(step_record)
                    await self.db.commit()
                    
                    # Execute step
                    handler = self._plan_handlers.get(plan.plan_type)
                    if handler:
                        try:
                            result = await handler(step_data, context)
                            step_record.status = "completed"
                            step_record.actual_end = datetime.utcnow()
                            step_record.output = result
                        except Exception as e:
                            logger.error(f"Step {step_id} failed: {e}")
                            step_record.status = "failed"
                            step_record.error_message = str(e)
                            step_record.actual_end = datetime.utcnow()
                            failed_count += 1
                    else:
                        step_record.status = "completed"
                        step_record.actual_end = datetime.utcnow()
                    
                    await self.db.commit()
                    completed_count += 1
                
                plan.completed_steps = completed_count
                plan.failed_steps = failed_count
                self.db.add(plan)
                await self.db.commit()
            
            # Finalize
            if failed_count > 0:
                plan.status = PlanStatus.FAILED.value
                plan.error_message = f"{failed_count} steps failed"
            else:
                plan.status = PlanStatus.COMPLETED.value
            
            plan.completed_at = datetime.utcnow()
            if plan.started_at:
                plan.actual_duration = (plan.completed_at - plan.started_at).total_seconds()
            
            self.db.add(plan)
            await self.db.commit()
            await self.db.refresh(plan)
            
            return plan
            
        except Exception as e:
            logger.error(f"Plan execution error: {e}")
            plan.status = PlanStatus.FAILED.value
            plan.error_message = str(e)
            plan.completed_at = datetime.utcnow()
            self.db.add(plan)
            await self.db.commit()
            raise
    
    # ==================== Step Handlers ====================
    
    async def _handle_media_ingest(
        self,
        step_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle media ingest step"""
        return {"status": "completed", "file_path": step_data.get("file_path")}
    
    async def _handle_transcode(
        self,
        step_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle transcode step"""
        return {"status": "completed", "output_path": step_data.get("output_path")}
    
    async def _handle_render(
        self,
        step_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle render step"""
        return {"status": "completed", "render_id": step_data.get("render_id")}
    
    async def _handle_ai_generate(
        self,
        step_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle AI generate step"""
        return {"status": "completed", "generation_id": step_data.get("generation_id")}
    
    async def _handle_analyze(
        self,
        step_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle analyze step"""
        return {"status": "completed", "analysis": step_data.get("analysis")}
    
    async def _handle_workflow(
        self,
        step_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle workflow step"""
        return {"status": "completed", "workflow_id": step_data.get("workflow_id")}
    
    # ==================== Recovery ====================
    
    async def recover_plan(
        self,
        plan: ExecutionPlan,
    ) -> ExecutionPlan:
        """Recover a failed or paused plan"""
        if plan.retry_count >= plan.max_retries:
            raise ValueError("Max retries exceeded")
        
        plan.retry_count += 1
        plan.status = PlanStatus.PENDING.value
        plan.error_message = None
        
        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)
        
        return plan
    
    # ==================== Optimization ====================
    
    async def optimize_plan(
        self,
        plan: ExecutionPlan,
        optimization_hint: Optional[str] = None,
    ) -> ExecutionPlan:
        """Optimize execution plan"""
        # Placeholder for optimization logic
        return plan


class WorkloadBalancer:
    """
    Workload balancer for distributed execution.
    Handles workload distribution and queue balancing.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._worker_capabilities: Dict[str, Dict[str, Any]] = {}
        self._queue_buffers: Dict[str, List[str]] = defaultdict(list)
    
    async def get_worker_availability(
        self,
        worker_type: Optional[str] = None,
    ) -> List[ResourceAvailability]:
        """Get available workers"""
        # Placeholder - would query worker registry
        return []
    
    async def balance_workload(
        self,
        pending_jobs: List[str],
        available_workers: List[ResourceAvailability],
    ) -> Dict[str, str]:
        """Balance workload across workers"""
        assignment = {}
        
        for job in pending_jobs:
            # Simple round-robin assignment
            if available_workers:
                worker = available_workers[len(assignment) % len(available_workers)]
                assignment[job] = worker.resource_id
        
        return assignment
    
    async def record_workload_snapshot(self) -> WorkloadSnapshot:
        """Record current workload snapshot"""
        snapshot = WorkloadSnapshot(
            snapshot_time=datetime.utcnow(),
        )
        
        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)
        
        return snapshot
    
    async def record_scheduler_metric(
        self,
        metric_name: str,
        value: float,
        category: str,
        tags: Optional[Dict[str, str]] = None,
    ) -> SchedulerMetric:
        """Record scheduler metric"""
        metric = SchedulerMetric(
            metric_name=metric_name,
            value=value,
            source="planner",
            category=category,
            tags=tags,
            timestamp=datetime.utcnow(),
        )
        
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        
        return metric


class ExecutionScheduler:
    """
    Execution scheduler with priority and resource awareness.
    Handles scheduling decisions and queue management.
    """
    
    def __init__(self, db: AsyncSession, planner: ExecutionPlanner):
        self.db = db
        self.planner = planner
        self._schedule_queue: List[ExecutionPlan] = []
        self._priority_weights = {
            PriorityLevel.CRITICAL: 1000,
            PriorityLevel.URGENT: 100,
            PriorityLevel.HIGH: 10,
            PriorityLevel.NORMAL: 1,
            PriorityLevel.LOW: 0.1,
        }
    
    async def enqueue_plan(
        self,
        plan: ExecutionPlan,
    ) -> None:
        """Enqueue plan for execution"""
        plan.status = PlanStatus.PENDING.value
        self.db.add(plan)
        await self.db.commit()
        
        self._schedule_queue.append(plan)
        self._sort_queue()
    
    def _sort_queue(self) -> None:
        """Sort queue by priority and scheduled time"""
        self._schedule_queue.sort(
            key=lambda p: (
                -self._priority_weights.get(PriorityLevel(p.priority), 1),
                p.scheduled_start or datetime.max,
            )
        )
    
    async def get_next_executable(
        self,
        resource_constraints: Optional[Dict[str, Any]] = None,
    ) -> Optional[ExecutionPlan]:
        """Get next executable plan"""
        for plan in self._schedule_queue:
            if plan.status == PlanStatus.PENDING:
                # Check resource requirements
                if await self._check_resources(plan, resource_constraints):
                    return plan
        
        return None
    
    async def _check_resources(
        self,
        plan: ExecutionPlan,
        constraints: Optional[Dict[str, Any]],
    ) -> bool:
        """Check if resources are available for plan"""
        requirements = plan.resource_requirements or {}
        
        if constraints:
            memory_required = requirements.get("memory_mb", 1024)
            memory_available = constraints.get("memory_available_mb", 0)
            if memory_required > memory_available:
                return False
        
        return True
    
    async def schedule_next(self) -> Optional[ExecutionPlan]:
        """Schedule next available plan"""
        plan = await self.get_next_executable()
        
        if plan:
            result = await self.planner.schedule_plan(plan)
            if result.scheduled:
                return plan
        
        return None