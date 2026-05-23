"""
Workflow Domain Services
"""
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.domains.workflows.models import (
    Workflow,
    WorkflowExecution,
    WorkflowStep,
    WorkflowStatus,
    ExecutionStatus,
    StepStatus,
    WorkflowRepository,
)

logger = logging.getLogger(__name__)


class WorkflowService:
    """
    Service for managing workflows and execution.
    Handles workflow CRUD and execution orchestration.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = WorkflowRepository(db)
    
    def create_workflow(
        self,
        name: str,
        workflow_type: str,
        definition: Dict[str, Any],
        created_by_id: UUID,
        description: Optional[str] = None,
        project_id: Optional[UUID] = None,
        trigger_type: Optional[str] = None,
        trigger_config: Optional[Dict] = None
    ) -> Workflow:
        """Create a new workflow"""
        workflow = Workflow(
            name=name,
            description=description,
            workflow_type=workflow_type,
            definition=definition,
            created_by_id=created_by_id,
            project_id=project_id,
            trigger_type=trigger_type,
            trigger_config=trigger_config
        )
        
        return self.repository.create(workflow)
    
    def get_workflow(self, workflow_id: UUID) -> Optional[Workflow]:
        return self.repository.get_by_id(workflow_id)
    
    def list_workflows(
        self,
        project_id: Optional[UUID] = None,
        workflow_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 50
    ) -> List[Workflow]:
        return self.repository.list_workflows(project_id, workflow_type, is_active, limit)
    
    def update_workflow(self, workflow_id: UUID, updates: Dict[str, Any]) -> Workflow:
        return self.repository.update(workflow_id, updates)
    
    def delete_workflow(self, workflow_id: UUID) -> bool:
        return self.repository.delete(workflow_id)
    
    def activate_workflow(self, workflow_id: UUID) -> Workflow:
        return self.repository.update(workflow_id, {"is_active": True})
    
    def deactivate_workflow(self, workflow_id: UUID) -> Workflow:
        return self.repository.update(workflow_id, {"is_active": False})
    
    # Execution
    
    def execute_workflow(
        self,
        workflow_id: UUID,
        input_data: Optional[Dict[str, Any]] = None,
        triggered_by: Optional[str] = None
    ) -> WorkflowExecution:
        """Execute a workflow"""
        workflow = self.get_workflow(workflow_id)
        
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if not workflow.is_active:
            raise ValueError(f"Workflow {workflow_id} is not active")
        
        # Create execution
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"
        
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            execution_id=execution_id,
            status=ExecutionStatus.PENDING.value,
            input_data=input_data,
            triggered_by=triggered_by,
            trigger_type=workflow.trigger_type
        )
        
        created = self.repository.create_execution(execution)
        
        # Create step records
        steps_def = workflow.definition.get("steps", [])
        for i, step_def in enumerate(steps_def):
            step = WorkflowStep(
                workflow_id=workflow_id,
                execution_id=created.id,
                step_id=step_def.get("id", f"step_{i}"),
                name=step_def.get("name", f"Step {i}"),
                step_type=step_def.get("type", "action"),
                config=step_def.get("config", {}),
                order=step_def.get("order", i),
                status=StepStatus.PENDING.value
            )
            self.db.add(step)
        
        self.db.commit()
        
        # Update workflow execution count
        workflow.execution_count += 1
        self.db.commit()
        
        return created
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        return self.repository.get_execution(execution_id)
    
    def list_executions(
        self,
        workflow_id: Optional[UUID] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[WorkflowExecution]:
        return self.repository.list_executions(workflow_id, status, limit)
    
    def cancel_execution(self, execution_id: str) -> WorkflowExecution:
        """Cancel a running execution"""
        execution = self.get_execution(execution_id)
        
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        
        if execution.status not in [ExecutionStatus.PENDING.value, ExecutionStatus.RUNNING.value]:
            raise ValueError(f"Cannot cancel execution in status: {execution.status}")
        
        execution.status = ExecutionStatus.CANCELLED.value
        execution.completed_at = datetime.utcnow()
        
        # Mark remaining steps as skipped
        for step in execution.steps:
            if step.status == StepStatus.PENDING.value:
                step.status = StepStatus.SKIPPED.value
        
        self.db.commit()
        return execution
    
    def get_step(self, step_id: UUID) -> Optional[WorkflowStep]:
        return self.db.query(WorkflowStep).filter(WorkflowStep.id == step_id).first()
    
    def update_step(
        self,
        step_id: UUID,
        status: str,
        output_data: Optional[Dict] = None,
        error: Optional[str] = None
    ) -> WorkflowStep:
        """Update step status and output"""
        step = self.get_step(step_id)
        
        if not step:
            raise ValueError(f"Step {step_id} not found")
        
        step.status = status
        
        if output_data:
            step.output_data = output_data
        
        if error:
            step.error_message = error
        
        if status == StepStatus.RUNNING.value:
            step.started_at = datetime.utcnow()
        elif status in [StepStatus.COMPLETED.value, StepStatus.FAILED.value]:
            step.completed_at = datetime.utcnow()
            if step.started_at:
                step.duration = int((step.completed_at - step.started_at).total_seconds())
        
        self.db.commit()
        return step


class WorkflowExecutor:
    """
    Executor for running workflow steps.
    Orchestrates step execution with retries and error handling.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.workflow_service = WorkflowService(db)
    
    def execute_step(self, step_id: UUID) -> Dict[str, Any]:
        """
        Execute a single workflow step.
        Returns result with status and output.
        """
        step = self.workflow_service.get_step(step_id)
        
        if not step:
            return {"status": "error", "message": "Step not found"}
        
        if step.status not in [StepStatus.PENDING.value, StepStatus.FAILED.value]:
            return {"status": "skipped", "message": f"Step in status: {step.status}"}
        
        try:
            # Mark as running
            self.workflow_service.update_step(step_id, StepStatus.RUNNING.value)
            
            # Execute based on step type
            result = self._execute_step_action(step)
            
            # Mark as completed
            self.workflow_service.update_step(
                step_id,
                StepStatus.COMPLETED.value,
                output_data=result
            )
            
            return {"status": "completed", "output": result}
            
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            
            # Check for retry
            if step.retry_count < 3:
                step.retry_count += 1
                self.db.commit()
                return {"status": "retry", "retry_count": step.retry_count}
            
            # Mark as failed
            self.workflow_service.update_step(
                step_id,
                StepStatus.FAILED.value,
                error=str(e)
            )
            
            return {"status": "failed", "error": str(e)}
    
    def _execute_step_action(self, step: WorkflowStep) -> Dict[str, Any]:
        """
        Execute the step action based on type.
        This is a simplified implementation - real workflow engine would
        support many action types like HTTP calls, database ops, etc.
        """
        step_type = step.step_type
        config = step.config or {}
        
        if step_type == "delay":
            import time
            duration = config.get("duration", 1)
            time.sleep(duration)
            return {"delayed": duration}
        
        elif step_type == "condition":
            # Evaluate condition
            condition = config.get("condition", "")
            # Simplified condition evaluation
            result = True  # Would evaluate actual condition
            return {"condition_met": result}
        
        elif step_type == "transform":
            # Transform data
            input_data = step.input_data or {}
            transform = config.get("transform", {})
            # Apply transform
            output = input_data
            return {"transformed": output}
        
        elif step_type == "render":
            # Trigger render job
            from app.domains.rendering.models import RenderJob
            from app.domains.rendering.services import RenderQueueService
            
            render_service = RenderQueueService(self.db)
            
            job = render_service.create_render_job(
                name=config.get("name", "Workflow render"),
                job_type=config.get("job_type", "video"),
                input_path=config.get("input_path"),
                output_path=config.get("output_path"),
                parameters=config.get("parameters"),
                priority=config.get("priority", "normal")
            )
            
            return {"job_id": str(job.id)}
        
        elif step_type == "analyze":
            # Trigger audio analysis
            from app.domains.audio.models import AudioAnalysis
            from app.domains.audio.services import AudioAnalysisService
            
            asset_id = config.get("asset_id")
            if asset_id:
                analysis_service = AudioAnalysisService(self.db)
                analysis = analysis_service.analyze_audio(UUID(asset_id))
                return {"bpm": analysis.bpm, "key": analysis.key}
            
            return {"analyzed": True}
        
        elif step_type == "export":
            # Export to platform
            from app.domains.rendering.services import ExportService
            
            export_service = ExportService(self.db)
            platform = config.get("platform")
            input_path = config.get("input_path")
            
            if platform and input_path:
                output_path = export_service.export_to_platform(input_path, platform)
                return {"output_path": output_path}
            
            return {"exported": True}
        
        else:
            # Generic action
            return {"action": step_type, "executed": True}
    
    def execute_workflow_steps(self, execution_id: str) -> Dict[str, Any]:
        """
        Execute all pending steps in a workflow execution.
        Used by Celery worker or background task.
        """
        execution = self.workflow_service.get_execution(execution_id)
        
        if not execution:
            return {"status": "error", "message": "Execution not found"}
        
        if execution.status != ExecutionStatus.PENDING.value:
            return {"status": "error", "message": f"Execution in status: {execution.status}"}
        
        # Mark as running
        execution.status = ExecutionStatus.RUNNING.value
        execution.started_at = datetime.utcnow()
        self.db.commit()
        
        failed_step = None
        
        for step in execution.steps:
            if step.status == StepStatus.SKIPPED.value:
                continue
            
            result = self.execute_step(step.id)
            
            if result["status"] == "failed":
                failed_step = step
                break
        
        if failed_step:
            execution.status = ExecutionStatus.FAILED.value
            execution.error_message = f"Step {failed_step.name} failed: {failed_step.error_message}"
        else:
            execution.status = ExecutionStatus.COMPLETED.value
        
        execution.completed_at = datetime.utcnow()
        if execution.started_at:
            execution.duration = int((execution.completed_at - execution.started_at).total_seconds())
        
        self.db.commit()
        
        return {
            "status": execution.status,
            "execution_id": execution_id,
            "duration": execution.duration
        }