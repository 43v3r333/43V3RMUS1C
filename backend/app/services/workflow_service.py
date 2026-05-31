"""
Workflow and job services
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from ..models.workflow import RenderJob, Workflow, AutomationJob, AIPrompt
from ..schemas.workflow import (
    RenderJobCreate, RenderJobUpdate,
    WorkflowCreate, WorkflowUpdate,
    AutomationJobCreate, AutomationJobUpdate,
    AIPromptCreate, AIPromptUpdate,
)
from ..repositories.workflow_repository import (
    RenderJobRepository, WorkflowRepository,
    AutomationJobRepository, AIPromptRepository,
)
from .base import BaseService


class RenderJobService(BaseService[RenderJob]):
    """Render job service"""
    
    def __init__(self, repository: RenderJobRepository):
        super().__init__(repository)
        self.repo = repository
    
    def get_pending(self, limit: int = 20) -> List[RenderJob]:
        """Get pending jobs"""
        return self.repo.get_pending(limit)
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 20) -> List[RenderJob]:
        """Get jobs by status"""
        return self.repo.get_by_status(status, skip, limit)
    
    def create(self, job_data: RenderJobCreate) -> RenderJob:
        """Create new render job"""
        job = RenderJob(
            name=job_data.name,
            job_type=job_data.job_type,
            priority=job_data.priority,
            input_path=job_data.input_path,
            output_path=job_data.output_path,
            parameters=job_data.parameters,
            project_id=job_data.project_id,
        )
        return self.repo.create(job)
    
    def queue(self, job: RenderJob) -> RenderJob:
        """Queue a job for processing"""
        job.status = "queued"
        return self.repo.update(job)
    
    def start(self, job: RenderJob, worker_id: str) -> RenderJob:
        """Start job processing"""
        job.status = "processing"
        job.worker_id = worker_id
        job.started_at = datetime.utcnow()
        return self.repo.update(job)
    
    def complete(self, job: RenderJob, output_path: str) -> RenderJob:
        """Complete job processing"""
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.output_path = output_path
        job.progress = 1.0
        return self.repo.update(job)
    
    def fail(self, job: RenderJob, error: str) -> RenderJob:
        """Mark job as failed"""
        job.status = "failed"
        job.error_message = error
        job.completed_at = datetime.utcnow()
        return self.repo.update(job)
    
    def retry(self, job: RenderJob) -> RenderJob:
        """Retry a failed job"""
        if job.retry_count >= job.max_retries:
            return job
        job.retry_count += 1
        job.status = "queued"
        job.error_message = None
        job.completed_at = None
        return self.repo.update(job)
    
    def update_progress(self, job: RenderJob, progress: float) -> RenderJob:
        """Update job progress"""
        job.progress = min(1.0, max(0.0, progress))
        return self.repo.update(job)
    
    def update(self, job: RenderJob, job_data: RenderJobUpdate) -> RenderJob:
        """Update render job"""
        update_data = job_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(job, field):
                setattr(job, field, value)
        return self.repo.update(job)


class WorkflowService(BaseService[Workflow]):
    """Workflow service"""
    
    def __init__(self, repository: WorkflowRepository):
        super().__init__(repository)
        self.repo = repository
    
    def get_by_type(self, workflow_type: str, skip: int = 0, limit: int = 20) -> List[Workflow]:
        """Get workflows by type"""
        return self.repo.get_by_type(workflow_type, skip, limit)
    
    def get_public(self, skip: int = 0, limit: int = 20) -> List[Workflow]:
        """Get public workflows"""
        return self.repo.get_public(skip, limit)
    
    def get_by_creator(self, created_by_id: UUID, skip: int = 0, limit: int = 20) -> List[Workflow]:
        """Get workflows by creator"""
        return self.repo.get_by_creator(created_by_id, skip, limit)
    
    def create(self, workflow_data: WorkflowCreate) -> Workflow:
        """Create new workflow"""
        workflow = Workflow(
            name=workflow_data.name,
            description=workflow_data.description,
            workflow_type=workflow_data.workflow_type,
            version=workflow_data.version,
            definition=workflow_data.definition,
            is_public=workflow_data.is_public,
            trigger_type=workflow_data.trigger_type,
            trigger_config=workflow_data.trigger_config,
            created_by_id=workflow_data.created_by_id,
            project_id=workflow_data.project_id,
        )
        return self.repo.create(workflow)
    
    def update(self, workflow: Workflow, workflow_data: WorkflowUpdate) -> Workflow:
        """Update workflow"""
        update_data = workflow_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(workflow, field):
                setattr(workflow, field, value)
        return self.repo.update(workflow)


class AutomationJobService(BaseService[AutomationJob]):
    """Automation job service"""
    
    def __init__(self, repository: AutomationJobRepository):
        super().__init__(repository)
        self.repo = repository
    
    def get_by_workflow(self, workflow_id: UUID, skip: int = 0, limit: int = 20) -> List[AutomationJob]:
        """Get jobs by workflow"""
        return self.repo.get_by_workflow(workflow_id, skip, limit)
    
    def get_recent(self, limit: int = 20) -> List[AutomationJob]:
        """Get recent jobs"""
        return self.repo.get_recent(limit)
    
    def create(self, job_data: AutomationJobCreate) -> AutomationJob:
        """Create new automation job"""
        job = AutomationJob(
            name=job_data.name,
            input_data=job_data.input_data,
            workflow_id=job_data.workflow_id,
            triggered_by=job_data.triggered_by,
        )
        return self.repo.create(job)
    
    def start(self, job: AutomationJob) -> AutomationJob:
        """Start job"""
        job.status = "processing"
        job.started_at = datetime.utcnow()
        return self.repo.update(job)
    
    def complete(self, job: AutomationJob, output_data: dict) -> AutomationJob:
        """Complete job"""
        job.status = "completed"
        job.output_data = output_data
        job.completed_at = datetime.utcnow()
        return self.repo.update(job)
    
    def fail(self, job: AutomationJob, error: str) -> AutomationJob:
        """Fail job"""
        job.status = "failed"
        job.error_message = error
        job.completed_at = datetime.utcnow()
        return self.repo.update(job)


class AIPromptService(BaseService[AIPrompt]):
    """AI Prompt service"""
    
    def __init__(self, repository: AIPromptRepository):
        super().__init__(repository)
        self.repo = repository
    
    def get_by_type(self, prompt_type: str, skip: int = 0, limit: int = 20) -> List[AIPrompt]:
        """Get prompts by type"""
        return self.repo.get_by_type(prompt_type, skip, limit)
    
    def get_by_category(self, category: str, skip: int = 0, limit: int = 20) -> List[AIPrompt]:
        """Get prompts by category"""
        return self.repo.get_by_category(category, skip, limit)
    
    def search(self, query: str, skip: int = 0, limit: int = 20) -> List[AIPrompt]:
        """Search prompts"""
        return self.repo.search(query, skip, limit)
    
    def create(self, prompt_data: AIPromptCreate) -> AIPrompt:
        """Create new prompt"""
        prompt = AIPrompt(
            name=prompt_data.name,
            description=prompt_data.description,
            prompt_type=prompt_data.prompt_type,
            template=prompt_data.template,
            variables=prompt_data.variables,
            model=prompt_data.model,
            parameters=prompt_data.parameters,
            is_public=prompt_data.is_public,
            category=prompt_data.category,
            tags=prompt_data.tags,
            created_by_id=prompt_data.created_by_id,
        )
        return self.repo.create(prompt)
    
    def update(self, prompt: AIPrompt, prompt_data: AIPromptUpdate) -> AIPrompt:
        """Update prompt"""
        update_data = prompt_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(prompt, field):
                setattr(prompt, field, value)
        return self.repo.update(prompt)
    
    def increment_use_count(self, prompt_id: UUID) -> None:
        """Increment prompt use count"""
        self.repo.increment_use_count(prompt_id)