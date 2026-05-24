"""
Workflow Engine Services - Automation workflow execution
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from uuid import UUID
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import (
    WorkflowStatus,
    WorkflowStepStatus,
    StepType,
    StepResult,
    WorkflowExecution,
    Workflow,
    WorkflowStep,
)

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """
    Workflow engine for automation workflow execution.
    Handles workflow creation, step execution, condition evaluation,
    looping, error handling, and workflow state management.
    """
    
    def __init__(
        self,
        db: AsyncSession,
        task_executor: Optional[Callable] = None,
    ):
        self.db = db
        self.task_executor = task_executor
        self._active_executions: Dict[str, WorkflowExecution] = {}
        self._step_handlers: Dict[StepType, Callable] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default step handlers"""
        self._step_handlers[StepType.TASK] = self._execute_task
        self._step_handlers[StepType.CONDITION] = self._evaluate_condition
        self._step_handlers[StepType.LOOP] = self._execute_loop
        self._step_handlers[StepType.WAIT] = self._wait_step
        self._step_handlers[StepType.NOTIFY] = self._send_notification
        self._step_handlers[StepType.TRANSFORM] = self._transform_data
        self._step_handlers[StepType.APPROVAL] = self._request_approval
    
    def register_handler(self, step_type: StepType, handler: Callable):
        """Register a custom step handler"""
        self._step_handlers[step_type] = handler
    
    # ==================== Workflow Operations ====================
    
    async def create_workflow(
        self,
        name: str,
        description: Optional[str] = None,
        workflow_data: Optional[Dict] = None,
        project_id: Optional[UUID] = None,
        owner_id: Optional[UUID] = None,
    ) -> Workflow:
        """Create a new workflow"""
        workflow = Workflow(
            name=name,
            description=description,
            workflow_data=workflow_data,
            project_id=project_id,
            owner_id=owner_id,
            status=WorkflowStatus.DRAFT.value,
        )
        
        self.db.add(workflow)
        await self.db.commit()
        await self.db.refresh(workflow)
        
        return workflow
    
    async def get_workflow(self, workflow_id: UUID) -> Optional[Workflow]:
        """Get workflow by ID"""
        result = await self.db.execute(
            select(Workflow).where(Workflow.id == workflow_id)
        )
        return result.scalar_one_or_none()
    
    async def update_workflow(
        self,
        workflow: Workflow,
        **kwargs,
    ) -> Workflow:
        """Update workflow properties"""
        for key, value in kwargs.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)
        
        self.db.add(workflow)
        await self.db.commit()
        await self.db.refresh(workflow)
        
        return workflow
    
    async def delete_workflow(self, workflow: Workflow) -> None:
        """Delete workflow"""
        await self.db.delete(workflow)
        await self.db.commit()
    
    async def activate_workflow(self, workflow: Workflow) -> Workflow:
        """Activate a workflow"""
        workflow.status = WorkflowStatus.ACTIVE.value
        return await self.update_workflow(workflow)
    
    async def pause_workflow(self, workflow: Workflow) -> Workflow:
        """Pause a workflow"""
        workflow.status = WorkflowStatus.PAUSED.value
        return await self.update_workflow(workflow)
    
    # ==================== Step Operations ====================
    
    async def add_step(
        self,
        workflow: Workflow,
        name: str,
        step_type: StepType,
        config: Optional[Dict] = None,
        depends_on: Optional[List[str]] = None,
        conditions: Optional[Dict] = None,
        max_retries: int = 3,
    ) -> WorkflowStep:
        """Add a step to workflow"""
        step = WorkflowStep(
            workflow_id=workflow.id,
            name=name,
            step_type=step_type.value,
            config=config,
            depends_on=depends_on or [],
            conditions=conditions,
            max_retries=max_retries,
        )
        
        self.db.add(step)
        await self.db.commit()
        await self.db.refresh(step)
        
        return step
    
    async def get_workflow_steps(
        self,
        workflow: Workflow,
    ) -> List[WorkflowStep]:
        """Get all steps for a workflow"""
        result = await self.db.execute(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == workflow.id)
            .order_by(WorkflowStep.created_at)
        )
        return list(result.scalars().all())
    
    async def update_step(
        self,
        step: WorkflowStep,
        **kwargs,
    ) -> WorkflowStep:
        """Update step properties"""
        for key, value in kwargs.items():
            if hasattr(step, key):
                setattr(step, key, value)
        
        self.db.add(step)
        await self.db.commit()
        await self.db.refresh(step)
        
        return step
    
    # ==================== Workflow Execution ====================
    
    async def execute_workflow(
        self,
        workflow: Workflow,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a workflow"""
        import uuid
        execution_id = str(uuid.uuid4())
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=str(workflow.id),
            started_at=datetime.utcnow(),
            status=WorkflowStatus.ACTIVE,
        )
        
        self._active_executions[execution_id] = execution
        
        try:
            # Get steps
            steps = await self.get_workflow_steps(workflow)
            execution.steps_total = len(steps)
            
            # Build step map
            step_map: Dict[str, WorkflowStep] = {
                str(step.id): step for step in steps
            }
            
            # Build execution graph
            ready_steps = [
                step for step in steps
                if not step.depends_on or len(step.depends_on) == 0
            ]
            completed_steps: Set[str] = set()
            step_results: Dict[str, StepResult] = {}
            
            while ready_steps:
                # Execute ready steps in parallel
                results = await asyncio.gather(
                    *[self._execute_step(step, context, step_results) for step in ready_steps],
                    return_exceptions=True,
                )
                
                for step, result in zip(ready_steps, results):
                    step_id = str(step.id)
                    
                    if isinstance(result, Exception):
                        step_results[step_id] = StepResult(
                            step_id=step_id,
                            status=WorkflowStepStatus.FAILED,
                            error=str(result),
                        )
                    else:
                        step_results[step_id] = result
                    
                    completed_steps.add(step_id)
                    execution.steps_completed += 1
                
                # Find next ready steps
                ready_steps = []
                for step in steps:
                    step_id = str(step.id)
                    if step_id in completed_steps:
                        continue
                    
                    # Check if all dependencies are complete
                    deps = step.depends_on or []
                    if all(d in completed_steps for d in deps):
                        # Check conditions
                        if step.conditions:
                            should_run = await self._evaluate_step_conditions(
                                step.conditions, step_results
                            )
                            if not should_run:
                                step_results[step_id] = StepResult(
                                    step_id=step_id,
                                    status=WorkflowStepStatus.SKIPPED,
                                )
                                completed_steps.add(step_id)
                                execution.steps_completed += 1
                                continue
                        
                        ready_steps.append(step)
            
            # Determine workflow status
            failed_steps = [
                r for r in step_results.values()
                if r.status == WorkflowStepStatus.FAILED
            ]
            
            if failed_steps:
                execution.status = WorkflowStatus.FAILED
                workflow.status = WorkflowStatus.FAILED.value
            else:
                execution.status = WorkflowStatus.COMPLETED
                workflow.status = WorkflowStatus.COMPLETED.value
            
            workflow.execution_count += 1
            workflow.last_executed_at = datetime.utcnow()
            
            await self.db.commit()
            
            return {
                "execution_id": execution_id,
                "status": execution.status.value,
                "steps_completed": execution.steps_completed,
                "steps_total": execution.steps_total,
                "step_results": {
                    k: {
                        "status": v.status.value,
                        "output": v.output,
                        "error": v.error,
                        "duration": v.duration,
                    }
                    for k, v in step_results.items()
                },
            }
            
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            execution.status = WorkflowStatus.FAILED
            workflow.status = WorkflowStatus.FAILED.value
            await self.db.commit()
            
            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": str(e),
            }
            
        finally:
            self._active_executions.pop(execution_id, None)
    
    async def _execute_step(
        self,
        step: WorkflowStep,
        context: Optional[Dict[str, Any]],
        step_results: Dict[str, StepResult],
    ) -> StepResult:
        """Execute a single workflow step"""
        start_time = datetime.utcnow()
        step_id = str(step.id)
        
        try:
            step.status = WorkflowStepStatus.RUNNING.value
            step.last_executed_at = datetime.utcnow()
            self.db.add(step)
            await self.db.commit()
            
            # Get handler
            handler = self._step_handlers.get(StepType(step.step_type))
            
            if not handler:
                raise ValueError(f"No handler for step type: {step.step_type}")
            
            # Execute with retry logic
            last_error = None
            for attempt in range(step.max_retries + 1):
                try:
                    result = await handler(step, context, step_results)
                    
                    step.status = WorkflowStepStatus.COMPLETED.value
                    self.db.add(step)
                    await self.db.commit()
                    
                    duration = (datetime.utcnow() - start_time).total_seconds()
                    step.execution_time = duration
                    
                    return StepResult(
                        step_id=step_id,
                        status=WorkflowStepStatus.COMPLETED,
                        output=result or {},
                        duration=duration,
                    )
                    
                except Exception as e:
                    last_error = e
                    step.retry_count = attempt + 1
                    
                    if attempt < step.max_retries:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise
            
            raise last_error
            
        except Exception as e:
            logger.error(f"Step {step.name} failed: {e}")
            
            step.status = WorkflowStepStatus.FAILED.value
            step.error_message = str(e)
            step.retry_count += 1
            self.db.add(step)
            await self.db.commit()
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            step.execution_time = duration
            
            return StepResult(
                step_id=step_id,
                status=WorkflowStepStatus.FAILED,
                error=str(e),
                duration=duration,
            )
    
    # ==================== Step Handlers ====================
    
    async def _execute_task(
        self,
        step: WorkflowStep,
        context: Optional[Dict[str, Any]],
        step_results: Dict[str, StepResult],
    ) -> Dict[str, Any]:
        """Execute a task step"""
        config = step.config or {}
        task_name = config.get("task_name")
        
        if self.task_executor and task_name:
            result = await self.task_executor(task_name, context)
            return {"result": result}
        
        return {"message": f"Task {step.name} executed"}
    
    async def _evaluate_condition(
        self,
        step: WorkflowStep,
        context: Optional[Dict[str, Any]],
        step_results: Dict[str, StepResult],
    ) -> Dict[str, Any]:
        """Evaluate a condition step"""
        config = step.config or {}
        condition_type = config.get("type")
        
        if condition_type == "always_true":
            return {"result": True}
        elif condition_type == "always_false":
            return {"result": False}
        
        return {"result": True}
    
    async def _execute_loop(
        self,
        step: WorkflowStep,
        context: Optional[Dict[str, Any]],
        step_results: Dict[str, StepResult],
    ) -> Dict[str, Any]:
        """Execute a loop step"""
        config = step.config or {}
        iterations = config.get("iterations", 1)
        results = []
        
        for i in range(iterations):
            results.append({"iteration": i})
        
        return {"iterations": iterations, "results": results}
    
    async def _wait_step(
        self,
        step: WorkflowStep,
        context: Optional[Dict[str, Any]],
        step_results: Dict[str, StepResult],
    ) -> Dict[str, Any]:
        """Execute a wait step"""
        config = step.config or {}
        duration = config.get("duration", 1.0)  # seconds
        
        await asyncio.sleep(duration)
        
        return {"waited": duration}
    
    async def _send_notification(
        self,
        step: WorkflowStep,
        context: Optional[Dict[str, Any]],
        step_results: Dict[str, StepResult],
    ) -> Dict[str, Any]:
        """Send a notification"""
        config = step.config or {}
        message = config.get("message", "Notification")
        
        return {"notified": True, "message": message}
    
    async def _transform_data(
        self,
        step: WorkflowStep,
        context: Optional[Dict[str, Any]],
        step_results: Dict[str, StepResult],
    ) -> Dict[str, Any]:
        """Transform data"""
        config = step.config or {}
        transform_type = config.get("type")
        
        return {"transformed": True, "type": transform_type}
    
    async def _request_approval(
        self,
        step: WorkflowStep,
        context: Optional[Dict[str, Any]],
        step_results: Dict[str, StepResult],
    ) -> Dict[str, Any]:
        """Request approval"""
        config = step.config or {}
        approver = config.get("approver")
        
        return {"approval_requested": True, "approver": approver}
    
    async def _evaluate_step_conditions(
        self,
        conditions: Dict[str, Any],
        step_results: Dict[str, StepResult],
    ) -> bool:
        """Evaluate step conditions"""
        condition_type = conditions.get("type")
        
        if condition_type == "step_success":
            step_id = conditions.get("step_id")
            return step_results.get(step_id, StepResult(step_id="", status=WorkflowStepStatus.PENDING)).status == WorkflowStepStatus.COMPLETED
        
        return True


from typing import Set