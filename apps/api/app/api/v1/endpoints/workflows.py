"""
Workflow, Render Job, and AI Prompt endpoints
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_async_db, get_current_user
from app.models.user import User
from app.schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    RenderJobCreate, RenderJobUpdate, RenderJobResponse,
    AIPromptCreate, AIPromptUpdate, AIPromptResponse,
)
from app.schemas.base import PaginatedResponse
from app.models.workflow import Workflow, RenderJob, AIPrompt, AutomationJob
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)

# ============ Workflow Endpoints ============

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[WorkflowResponse])
async def list_workflows(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    workflow_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """List all workflows"""
    repo = BaseRepository(Workflow, db)
    filters = {}
    if workflow_type:
        filters["workflow_type"] = workflow_type
    if is_active is not None:
        filters["is_active"] = is_active
    workflows, total = await repo.paginate(page, per_page, filters=filters if filters else None)
    return PaginatedResponse.create(workflows, total, page, per_page)


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    data: WorkflowCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Create new workflow"""
    workflow = Workflow(**data.model_dump(), created_by_id=current_user.id)
    repo = BaseRepository(Workflow, db)
    workflow = await repo.create(workflow)
    logger.info(f"Workflow created: {workflow.name}")
    return workflow


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Get workflow by ID"""
    repo = BaseRepository(Workflow, db)
    workflow = await repo.get_by_id(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.patch("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    data: WorkflowUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Update workflow"""
    repo = BaseRepository(Workflow, db)
    workflow = await repo.get_by_id(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(workflow, key, value)
    
    workflow = await repo.update(workflow)
    return workflow


@router.post("/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    input_data: dict,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Execute a workflow"""
    repo = BaseRepository(Workflow, db)
    workflow = await repo.get_by_id(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Create automation job
    job = AutomationJob(
        name=f"{workflow.name} - Execution",
        input_data=input_data,
        workflow_id=workflow.id,
        triggered_by="manual",
    )
    job_repo = BaseRepository(AutomationJob, db)
    job = await job_repo.create(job)
    
    logger.info(f"Workflow execution started: {workflow_id}")
    
    return {"job_id": str(job.id), "status": "pending"}


# ============ Render Job Endpoints ============

render_jobs_router = APIRouter()


@render_jobs_router.get("/", response_model=PaginatedResponse[RenderJobResponse])
async def list_render_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    job_type: Optional[str] = None,
    project_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """List all render jobs"""
    repo = BaseRepository(RenderJob, db)
    filters = {}
    if status:
        filters["status"] = status
    if job_type:
        filters["job_type"] = job_type
    if project_id:
        filters["project_id"] = project_id
    jobs, total = await repo.paginate(page, per_page, filters=filters if filters else None)
    return PaginatedResponse.create(jobs, total, page, per_page)


@render_jobs_router.post("/", response_model=RenderJobResponse, status_code=status.HTTP_201_CREATED)
async def create_render_job(
    data: RenderJobCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Create new render job"""
    job = RenderJob(**data.model_dump())
    repo = BaseRepository(RenderJob, db)
    job = await repo.create(job)
    logger.info(f"Render job created: {job.name}")
    return job


@render_jobs_router.get("/{job_id}", response_model=RenderJobResponse)
async def get_render_job(
    job_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Get render job by ID"""
    repo = BaseRepository(RenderJob, db)
    job = await repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Render job not found")
    return job


@render_jobs_router.patch("/{job_id}", response_model=RenderJobResponse)
async def update_render_job(
    job_id: str,
    data: RenderJobUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Update render job"""
    repo = BaseRepository(RenderJob, db)
    job = await repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Render job not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(job, key, value)
    
    job = await repo.update(job)
    return job


@render_jobs_router.post("/{job_id}/cancel")
async def cancel_render_job(
    job_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a render job"""
    repo = BaseRepository(RenderJob, db)
    job = await repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Render job not found")
    
    job.status = "cancelled"
    job = await repo.update(job)
    
    logger.info(f"Render job cancelled: {job_id}")
    return job


# ============ AI Prompt Endpoints ============

prompts_router = APIRouter()


@prompts_router.get("/", response_model=PaginatedResponse[AIPromptResponse])
async def list_prompts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    prompt_type: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """List all AI prompts"""
    repo = BaseRepository(AIPrompt, db)
    filters = {}
    if prompt_type:
        filters["prompt_type"] = prompt_type
    if category:
        filters["category"] = category
    if is_active is not None:
        filters["is_active"] = is_active
    prompts, total = await repo.paginate(page, per_page, filters=filters if filters else None)
    return PaginatedResponse.create(prompts, total, page, per_page)


@prompts_router.post("/", response_model=AIPromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    data: AIPromptCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Create new AI prompt"""
    prompt = AIPrompt(**data.model_dump(), created_by_id=current_user.id)
    repo = BaseRepository(AIPrompt, db)
    prompt = await repo.create(prompt)
    logger.info(f"AI prompt created: {prompt.name}")
    return prompt


@prompts_router.get("/{prompt_id}", response_model=AIPromptResponse)
async def get_prompt(
    prompt_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Get AI prompt by ID"""
    repo = BaseRepository(AIPrompt, db)
    prompt = await repo.get_by_id(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@prompts_router.patch("/{prompt_id}", response_model=AIPromptResponse)
async def update_prompt(
    prompt_id: str,
    data: AIPromptUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Update AI prompt"""
    repo = BaseRepository(AIPrompt, db)
    prompt = await repo.get_by_id(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(prompt, key, value)
    
    prompt = await repo.update(prompt)
    return prompt