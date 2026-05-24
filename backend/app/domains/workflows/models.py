"""
Workflow Domain Models - Automation workflow management
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, JSON, Text, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class WorkflowStatus(str, Enum):
    """Workflow status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStepStatus(str, Enum):
    """Workflow step status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepType(str, Enum):
    """Workflow step types"""
    TASK = "task"
    CONDITION = "condition"
    LOOP = "loop"
    WAIT = "wait"
    NOTIFY = "notify"
    TRANSFORM = "transform"
    APPROVAL = "approval"


@dataclass
class StepResult:
    """Result of a workflow step execution"""
    step_id: str
    status: WorkflowStepStatus
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    duration: float = 0.0


@dataclass
class WorkflowExecution:
    """Workflow execution context"""
    execution_id: str
    workflow_id: str
    started_at: datetime
    status: WorkflowStatus
    steps_completed: int = 0
    steps_total: int = 0
    current_step: Optional[str] = None


class Workflow(BaseModel):
    """Workflow model"""
    __tablename__ = "workflows"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=WorkflowStatus.DRAFT.value, index=True)
    
    # Workflow data (steps, triggers, etc.)
    workflow_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Project reference
    project_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=True,
        index=True
    )
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    owner: Mapped[Optional["User"]] = relationship("User", back_populates="workflows")
    
    # Usage tracking
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    last_executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="workflows")


class WorkflowStep(BaseModel):
    """Workflow step model"""
    __tablename__ = "workflow_steps"
    
    workflow_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("workflows.id"),
        nullable=False,
        index=True
    )
    workflow: Mapped[Workflow] = relationship("Workflow", back_populates="steps")
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    step_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Step configuration
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Execution state
    status: Mapped[str] = mapped_column(String(50), default=WorkflowStepStatus.PENDING.value)
    last_executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    execution_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Error handling
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Dependencies
    depends_on: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    conditions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)


# Import for relationship
from ...models.media import Project
from ...models.user import User