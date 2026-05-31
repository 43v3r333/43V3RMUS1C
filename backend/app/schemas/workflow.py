"""
Workflow and job schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class RenderJobBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    job_type: str
    priority: str = "normal"
    input_path: Optional[str] = None
    output_path: Optional[str] = None


class RenderJobCreate(RenderJobBase):
    parameters: Optional[Dict[str, Any]] = None
    project_id: Optional[UUID] = None


class RenderJobUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    progress: Optional[float] = None
    output_path: Optional[str] = None
    error_message: Optional[str] = None


class RenderJobResponse(RenderJobBase):
    id: UUID
    status: str
    progress: float
    parameters: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    worker_id: Optional[str] = None
    retry_count: int
    max_retries: int
    error_message: Optional[str] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    project_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    workflow_type: str
    version: str = "1.0.0"


class WorkflowCreate(WorkflowBase):
    definition: Dict[str, Any]
    is_public: bool = False
    trigger_type: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    created_by_id: UUID
    project_id: Optional[UUID] = None


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    trigger_type: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None


class WorkflowResponse(WorkflowBase):
    id: UUID
    definition: Dict[str, Any]
    is_active: bool
    is_public: bool
    trigger_type: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    created_by_id: UUID
    project_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AutomationJobBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class AutomationJobCreate(AutomationJobBase):
    workflow_id: UUID
    input_data: Optional[Dict[str, Any]] = None
    triggered_by: Optional[str] = "manual"


class AutomationJobUpdate(BaseModel):
    status: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class AutomationJobResponse(AutomationJobBase):
    id: UUID
    status: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    workflow_id: UUID
    triggered_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIPromptBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    prompt_type: str
    template: str


class AIPromptCreate(AIPromptBase):
    variables: Optional[List[Dict[str, Any]]] = None
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_public: bool = False
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    created_by_id: Optional[UUID] = None


class AIPromptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template: Optional[str] = None
    variables: Optional[List[Dict[str, Any]]] = None
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class AIPromptResponse(AIPromptBase):
    id: UUID
    variables: Optional[List[Dict[str, Any]]] = None
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: bool
    is_public: bool
    use_count: int
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    created_by_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}