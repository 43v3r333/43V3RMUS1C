"""
Workflow Domain Models
"""
import enum
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, Session

from app.models.base import BaseModel


class WorkflowStatus(str, enum.Enum):
    """Workflow status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ExecutionStatus(str, enum.Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, enum.Enum):
    """Workflow step status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class Workflow(BaseModel):
    """
    Workflow model for automation pipelines.
    Defines reusable automation workflows with steps.
    """
    __tablename__ = "workflows"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Workflow type
    workflow_type = Column(String(50), nullable=False)
    version = Column(String(20), default="1.0.0")
    
    # Definition (steps, conditions, etc.)
    definition = Column(JSON, nullable=False)
    
    # Configuration
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    # Trigger configuration
    trigger_type = Column(String(50), nullable=True)
    trigger_config = Column(JSON, nullable=True)
    
    # Ownership
    created_by_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    
    # Stats
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Relationships
    executions = relationship("WorkflowExecution", back_populates="workflow", lazy="selectin")
    project = relationship("Project", back_populates="workflows")
    
    def __repr__(self) -> str:
        return f"<Workflow(id={self.id}, name={self.name}, type={self.workflow_type})>"


class WorkflowStep(BaseModel):
    """
    Workflow step model for individual actions.
    """
    __tablename__ = "workflow_steps"
    
    workflow_id = Column(PGUUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    execution_id = Column(PGUUID(as_uuid=True), ForeignKey("workflow_executions.id"), nullable=True)
    
    # Step identification
    step_id = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    step_type = Column(String(50), nullable=False)
    
    # Status
    status = Column(String(20), default=StepStatus.PENDING.value, index=True)
    
    # Configuration
    config = Column(JSON, nullable=True)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    
    # Timing
    order = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # seconds
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="steps")
    execution = relationship("WorkflowExecution", back_populates="steps")
    
    def __repr__(self) -> str:
        return f"<WorkflowStep(id={self.id}, name={self.name}, status={self.status})>"


class WorkflowExecution(BaseModel):
    """
    Workflow execution model for tracking workflow runs.
    """
    __tablename__ = "workflow_executions"
    
    workflow_id = Column(PGUUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    
    # Execution info
    execution_id = Column(String(100), nullable=False, unique=True, index=True)
    status = Column(String(20), default=ExecutionStatus.PENDING.value, index=True)
    
    # Input/Output
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Trigger info
    triggered_by = Column(String(50), nullable=True)
    trigger_type = Column(String(50), nullable=True)
    
    # Execution log
    logs = Column(JSON, nullable=True)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="executions")
    steps = relationship(
        "WorkflowStep",
        back_populates="execution",
        lazy="selectin",
        order_by="WorkflowStep.order"
    )
    
    def __repr__(self) -> str:
        return f"<WorkflowExecution(id={self.id}, execution_id={self.execution_id}, status={self.status})>"


class WorkflowRepository:
    """Repository for workflow data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, workflow_id: UUID) -> Optional[Workflow]:
        return self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
    
    def list_workflows(
        self,
        project_id: Optional[UUID] = None,
        workflow_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Workflow]:
        query = self.db.query(Workflow)
        
        if project_id:
            query = query.filter(Workflow.project_id == project_id)
        if workflow_type:
            query = query.filter(Workflow.workflow_type == workflow_type)
        if is_active is not None:
            query = query.filter(Workflow.is_active == is_active)
        
        return query.order_by(Workflow.created_at.desc()).offset(offset).limit(limit).all()
    
    def create(self, workflow: Workflow) -> Workflow:
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow
    
    def update(self, workflow_id: UUID, updates: dict) -> Workflow:
        workflow = self.get_by_id(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        for key, value in updates.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)
        
        workflow.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(workflow)
        return workflow
    
    def delete(self, workflow_id: UUID) -> bool:
        workflow = self.get_by_id(workflow_id)
        if not workflow:
            return False
        
        self.db.delete(workflow)
        self.db.commit()
        return True
    
    # Execution methods
    def create_execution(self, execution: WorkflowExecution) -> WorkflowExecution:
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        return (
            self.db.query(WorkflowExecution)
            .filter(WorkflowExecution.execution_id == execution_id)
            .first()
        )
    
    def update_execution(self, execution_id: str, updates: dict) -> WorkflowExecution:
        execution = self.get_execution(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        
        for key, value in updates.items():
            if hasattr(execution, key):
                setattr(execution, key, value)
        
        execution.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(execution)
        return execution
    
    def list_executions(
        self,
        workflow_id: Optional[UUID] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[WorkflowExecution]:
        query = self.db.query(WorkflowExecution)
        
        if workflow_id:
            query = query.filter(WorkflowExecution.workflow_id == workflow_id)
        if status:
            query = query.filter(WorkflowExecution.status == status)
        
        return query.order_by(WorkflowExecution.created_at.desc()).limit(limit).all()