"""
Workflows Domain Models - Automation workflow management

NOTE: Many models have been moved to app.models.workflow to avoid duplicate table registrations.
Import from app.models.workflow for: Workflow, RenderJob, AutomationJob, etc.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Optional as Opt
from uuid import UUID
from enum import Enum
from dataclasses import dataclass

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, JSON, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class WorkflowStatus(str, Enum):
    """Workflow status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStepStatus(str, Enum):
    """Workflow step status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepType(str, Enum):
    """Step type enumeration"""
    GENERATION = "generation"
    PROCESSING = "processing"
    APPROVAL = "approval"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"


@dataclass
class StepResult:
    """Result of a step execution"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# WorkflowExecution is moved to domains/runtime/models.py to avoid duplicate with workflows
# This is a stub to prevent import errors
class WorkflowExecution:
    """DEPRECATED: WorkflowExecution is no longer in this file.
    
    This is a stub to prevent ImportErrors during migration.
    """
    __table__ = None
    
    def __init__(self, *args, **kwargs):
        raise RuntimeError(
            "WorkflowExecution is deprecated in domains/workflows/models.py. "
            "Check app.domains.runtime.models for correct location."
        )


# Workflow is stubbed - import from models.workflow
class Workflow:
    """DEPRECATED: Workflow has moved to models.workflow"""
    __table__ = None
    
    def __init__(self, *args, **kwargs):
        raise RuntimeError(
            "Workflow is no longer in domains/workflows/models.py. "
            "Import from models.workflow: from models.workflow import Workflow"
        )


class WorkflowStep(BaseModel):
    """Workflow step model"""
    __tablename__ = "workflow_steps"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    step_type = Column(String(50), nullable=False)
    step_order = Column(Integer, nullable=False, index=True)
    
    config = Column(JSON, nullable=False)
    input_schema = Column(JSON, nullable=True)
    output_schema = Column(JSON, nullable=True)
    
    is_optional = Column(Boolean, default=False)
    is_parallel = Column(Boolean, default=False)
    
    timeout_seconds = Column(Integer, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    status = Column(String(50), default=WorkflowStepStatus.PENDING.value, index=True)
    error_message = Column(Text, nullable=True)
    
    workflow_id = Column(PGUUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False, index=True)
    workflow = relationship("Workflow", back_populates="steps")
    
    __table_args__ = (
        UniqueConstraint('workflow_id', 'step_order', name='uq_workflow_step_order'),
    )