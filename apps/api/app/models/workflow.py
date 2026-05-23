"""
Workflow models: Workflow, RenderJob, AutomationJob, AIPrompt
"""
from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Workflow(BaseModel):
    """Workflow model for automated pipelines"""
    
    __tablename__ = "workflows"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    workflow_type = Column(String(50), nullable=False)  # render, generate, distribute, process
    version = Column(String(20), default="1.0.0")
    
    # Workflow definition (steps, conditions, etc.)
    definition = Column(JSON, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    # Trigger configuration
    trigger_type = Column(String(50), nullable=True)  # manual, scheduled, event
    trigger_config = Column(JSON, nullable=True)
    
    # Ownership
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    
    # Relationships
    automation_jobs = relationship("AutomationJob", back_populates="workflow", lazy="selectin")
    project = relationship("Project", back_populates="workflows", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<Workflow(id={self.id}, name={self.name})>"


class RenderJob(BaseModel):
    """Render job model for media processing"""
    
    __tablename__ = "render_jobs"
    
    name = Column(String(255), nullable=False, index=True)
    job_type = Column(String(50), nullable=False, index=True)  # video, audio, image, export
    status = Column(String(50), default="pending", index=True)  # pending, queued, processing, completed, failed, cancelled
    priority = Column(String(50), default="normal")  # low, normal, high, urgent
    
    # File paths
    input_path = Column(String(500), nullable=True)
    output_path = Column(String(500), nullable=True)
    
    # Processing parameters
    parameters = Column(JSON, nullable=True)
    
    # Progress tracking
    progress = Column(Float, default=0.0)  # 0.0 to 100.0
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Worker info
    worker_id = Column(String(100), nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Retry configuration
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Performance
    estimated_duration = Column(Integer, nullable=True)  # in seconds
    actual_duration = Column(Integer, nullable=True)
    
    # Ownership
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="render_jobs", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<RenderJob(id={self.id}, name={self.name}, status={self.status})>"


class AutomationJob(BaseModel):
    """Automation job model for workflow execution"""
    
    __tablename__ = "automation_jobs"
    
    name = Column(String(255), nullable=False, index=True)
    status = Column(String(50), default="pending", index=True)  # pending, running, completed, failed
    
    # Job data
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Execution log
    logs = Column(Text, nullable=True)
    
    # Relationships
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=True)
    workflow = relationship("Workflow", back_populates="automation_jobs", lazy="selectin")
    
    # Trigger info
    triggered_by = Column(String(50), nullable=True)
    
    def __repr__(self) -> str:
        return f"<AutomationJob(id={self.id}, name={self.name}, status={self.status})>"


class AIPrompt(BaseModel):
    """AI prompt model for reusable prompt templates"""
    
    __tablename__ = "ai_prompts"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    prompt_type = Column(String(50), nullable=False, index=True)  # tts, visual, text, music
    
    # Prompt template
    template = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)  # [{name, type, required}]
    
    # Model configuration
    model = Column(String(100), nullable=True)
    parameters = Column(JSON, nullable=True)  # temperature, max_tokens, etc.
    
    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    # Usage tracking
    use_count = Column(Integer, default=0)
    
    # Organization
    category = Column(String(100), nullable=True, index=True)
    tags = Column(JSON, nullable=True)
    
    # Ownership
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="prompts", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<AIPrompt(id={self.id}, name={self.name}, type={self.prompt_type})>"


# Additional import for Boolean type
from sqlalchemy import Boolean
from sqlalchemy import DateTime