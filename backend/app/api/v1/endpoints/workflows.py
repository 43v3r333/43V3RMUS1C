"""
Workflow and job endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.deps import get_current_active_user
from ....schemas.workflow import (
    RenderJobCreate, RenderJobUpdate, RenderJobResponse,
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    AutomationJobCreate, AutomationJobUpdate, AutomationJobResponse,
    AIPromptCreate, AIPromptUpdate, AIPromptResponse,
)
from ....services.workflow_service import (
    RenderJobService, WorkflowService,
    AutomationJobService, AIPromptService
)
from ....repositories.workflow_repository import (
    RenderJobRepository, WorkflowRepository,
    AutomationJobRepository, AIPromptRepository
)

router = APIRouter(prefix="/workflows", tags=["workflows"])


# Render Jobs
@router.get("/jobs", response_model=List[RenderJobResponse])
async def list_render_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    job_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List render jobs with optional filters"""
    repo = RenderJobRepository(db)
    service = RenderJobService(repo)
    
    if status:
        return repo.get_by_status(status, skip, limit)
    if job_type:
        return repo.get_by_type(job_type, skip, limit)
    return service.get_all(skip, limit)


@router.post("/jobs", response_model=RenderJobResponse)
async def create_render_job(
    job_data: RenderJobCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create new render job"""
    repo = RenderJobRepository(db)
    service = RenderJobService(repo)
    
    return service.create(job_data)


@router.get("/jobs/{job_id}", response_model=RenderJobResponse)
async def get_render_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get render job by ID"""
    repo = RenderJobRepository(db)
    service = RenderJobService(repo)
    
    job = service.get_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return job


@router.put("/jobs/{job_id}", response_model=RenderJobResponse)
async def update_render_job(
    job_id: UUID,
    job_data: RenderJobUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update render job"""
    repo = RenderJobRepository(db)
    service = RenderJobService(repo)
    
    job = service.get_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return service.update(job, job_data)


@router.post("/jobs/{job_id}/queue")
async def queue_render_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Queue a render job for processing"""
    repo = RenderJobRepository(db)
    service = RenderJobService(repo)
    
    job = service.get_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job = service.queue(job)
    return {"message": "Job queued", "job_id": str(job.id)}


@router.post("/jobs/{job_id}/retry")
async def retry_render_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Retry a failed render job"""
    repo = RenderJobRepository(db)
    service = RenderJobService(repo)
    
    job = service.get_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.retry_count >= job.max_retries:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum retries exceeded"
        )
    
    job = service.retry(job)
    return {"message": "Job retried", "job_id": str(job.id), "retry_count": job.retry_count}


# Workflows
@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    workflow_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List workflows"""
    repo = WorkflowRepository(db)
    service = WorkflowService(repo)
    
    if workflow_type:
        return repo.get_by_type(workflow_type, skip, limit)
    return repo.get_by_creator(current_user.id, skip, limit)


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create new workflow"""
    repo = WorkflowRepository(db)
    service = WorkflowService(repo)
    
    workflow_data.created_by_id = current_user.id
    return service.create(workflow_data)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get workflow by ID"""
    repo = WorkflowRepository(db)
    service = WorkflowService(repo)
    
    workflow = service.get_by_id(workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    workflow_data: WorkflowUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update workflow"""
    repo = WorkflowRepository(db)
    service = WorkflowService(repo)
    
    workflow = service.get_by_id(workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return service.update(workflow, workflow_data)


# AI Prompts
prompts_router = APIRouter(prefix="/prompts", tags=["prompts"])


@prompts_router.get("/", response_model=List[AIPromptResponse])
async def list_prompts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    prompt_type: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List AI prompts with optional filters"""
    repo = AIPromptRepository(db)
    service = AIPromptService(repo)
    
    if prompt_type:
        return repo.get_by_type(prompt_type, skip, limit)
    if category:
        return repo.get_by_category(category, skip, limit)
    return service.get_all(skip, limit)


@prompts_router.post("/", response_model=AIPromptResponse)
async def create_prompt(
    prompt_data: AIPromptCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create new AI prompt"""
    repo = AIPromptRepository(db)
    service = AIPromptService(repo)
    
    prompt_data.created_by_id = current_user.id
    return service.create(prompt_data)


@prompts_router.get("/{prompt_id}", response_model=AIPromptResponse)
async def get_prompt(
    prompt_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get AI prompt by ID"""
    repo = AIPromptRepository(db)
    service = AIPromptService(repo)
    
    prompt = service.get_by_id(prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    return prompt


@prompts_router.put("/{prompt_id}", response_model=AIPromptResponse)
async def update_prompt(
    prompt_id: UUID,
    prompt_data: AIPromptUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update AI prompt"""
    repo = AIPromptRepository(db)
    service = AIPromptService(repo)
    
    prompt = service.get_by_id(prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    return service.update(prompt, prompt_data)


@prompts_router.delete("/{prompt_id}")
async def delete_prompt(
    prompt_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Delete AI prompt (soft delete)"""
    repo = AIPromptRepository(db)
    service = AIPromptService(repo)
    
    prompt = service.get_by_id(prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    service.repository.delete(prompt)
    return {"message": "Prompt deleted successfully"}