"""
Workflow-related Pydantic schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, TimestampSchema


# ============ Workflow Schemas ============

class WorkflowBase(BaseSchema):
    """Base workflow schema"""
    
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    workflow_type: str
    version: str = "1.0.0"
    definition: Dict[str, Any]
    is_active: bool = True
    is_public: bool = False
    trigger_type: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None


class WorkflowCreate(WorkflowBase):
    """Workflow creation schema"""
    
    project_id: Optional[UUID] = None


class WorkflowUpdate(BaseSchema):
    """Workflow update schema"""
    
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    trigger_type: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None


class WorkflowResponse(TimestampSchema):
    """Workflow response schema"""
    
    name: str
    description: Optional[str] = None
    workflow_type: str
    version: str
    definition: Dict[str, Any]
    is_active: bool
    is_public: bool
    trigger_type: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    created_by_id: UUID
    project_id: Optional[UUID] = None


# ============ Render Job Schemas ============

class RenderJobBase(BaseSchema):
    """Base render job schema"""
    
    name: str = Field(min_length=1, max_length=255)
    job_type: str
    status: str = "pending"
    priority: str = "normal"
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class RenderJobCreate(RenderJobBase):
    """Render job creation schema"""
    
    project_id: Optional[UUID] = None


class RenderJobUpdate(BaseSchema):
    """Render job update schema"""
    
    name: Optional[str] = Field(default=None, max_length=255)
    status: Optional[str] = None
    priority: Optional[str] = None
    output_path: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    progress: Optional[float] = None


class RenderJobResponse(TimestampSchema):
    """Render job response schema"""
    
    name: str
    job_type: str
    status: str
    priority: str
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    progress: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    worker_id: Optional[str] = None
    retry_count: int
    max_retries: int
    error_message: Optional[str] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    project_id: Optional[UUID] = None


# ============ AI Prompt Schemas ============

class AIPromptBase(BaseSchema):
    """Base AI prompt schema"""
    
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    prompt_type: str
    template: str
    variables: Optional[List[Dict[str, Any]]] = None
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: bool = True
    is_public: bool = False
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class AIPromptCreate(AIPromptBase):
    """AI prompt creation schema"""
    
    pass


class AIPromptUpdate(BaseSchema):
    """AI prompt update schema"""
    
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    template: Optional[str] = None
    variables: Optional[List[Dict[str, Any]]] = None
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class AIPromptResponse(TimestampSchema):
    """AI prompt response schema"""
    
    name: str
    description: Optional[str] = None
    prompt_type: str
    template: str
    variables: Optional[List[Dict[str, Any]]] = None
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: bool
    is_public: bool
    use_count: int
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    created_by_id: Optional[UUID] = None