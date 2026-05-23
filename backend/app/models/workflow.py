"""
Job queue, workflow, and automation models
"""
from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class RenderJob(BaseModel):
    """Render job model for media processing"""
    __tablename__ = "render_jobs"
    
    name = Column(String(255), nullable=False, index=True)
    job_type = Column(String(50), nullable=False, index=True)  # render, encode, transcode
    status = Column(String(50), default=JobStatus.PENDING.value, index=True)
    priority = Column(String(50), default=JobPriority.NORMAL.value, index=True)
    
    input_path = Column(String(500), nullable=True)
    output_path = Column(String(500), nullable=True)
    
    parameters = Column(JSON, nullable=True)  # {"resolution": "1080p", "format": "mp4"}
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    
    started_at = Column(String(50), nullable=True)
    completed_at = Column(String(50), nullable=True)
    
    worker_id = Column(String(100), nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    error_message = Column(Text, nullable=True)
    logs = Column(Text, nullable=True)
    
    estimated_duration = Column(Integer, nullable=True)  # seconds
    actual_duration = Column(Integer, nullable=True)  # seconds
    
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    project = relationship("Project")


class Workflow(BaseModel):
    """Workflow definition model"""
    __tablename__ = "workflows"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    workflow_type = Column(String(50), nullable=False)  # generation, processing, distribution
    version = Column(String(20), default="1.0.0")
    
    definition = Column(JSON, nullable=False)  # Workflow steps and configuration
    
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    trigger_type = Column(String(50), nullable=True)  # manual, scheduled, event
    trigger_config = Column(JSON, nullable=True)
    
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", back_populates="workflows")
    
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    project = relationship("Project", back_populates="workflows")
    
    # Relationships
    automation_jobs = relationship("AutomationJob", back_populates="workflow")


class AutomationJob(BaseModel):
    """Automation job execution model"""
    __tablename__ = "automation_jobs"
    
    name = Column(String(255), nullable=False)
    status = Column(String(50), default=JobStatus.PENDING.value, index=True)
    
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    
    started_at = Column(String(50), nullable=True)
    completed_at = Column(String(50), nullable=True)
    
    error_message = Column(Text, nullable=True)
    logs = Column(Text, nullable=True)
    
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=True)
    workflow = relationship("Workflow", back_populates="automation_jobs")
    
    triggered_by = Column(String(50), nullable=True)  # manual, scheduled, webhook


class AIPrompt(BaseModel):
    """AI Prompt template model"""
    __tablename__ = "ai_prompts"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    prompt_type = Column(String(50), nullable=False, index=True)  # tts, music, visual, general
    
    template = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)  # [{"name": "text", "type": "string", "required": true}]
    
    model = Column(String(100), nullable=True)  # gpt-4, claude-3, etc.
    parameters = Column(JSON, nullable=True)  # {"temperature": 0.7, "max_tokens": 1000}
    
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    use_count = Column(Integer, default=0)
    
    category = Column(String(100), nullable=True, index=True)
    tags = Column(JSON, nullable=True)
    
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_by = relationship("User")