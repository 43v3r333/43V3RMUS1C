"""
AI Runtime Models - AI task and context management
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum
from dataclasses import dataclass, field

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class TaskStatus(str, Enum):
    """AI task status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """AI task priority"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ModelProvider(str, Enum):
    """AI model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    CUSTOM = "custom"


@dataclass
class TaskConfig:
    """Configuration for AI task execution"""
    model: str
    provider: ModelProvider
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    stop: Optional[List[str]] = None
    seed: Optional[int] = None


@dataclass
class AIResponse:
    """AI model response"""
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIContext:
    """Context for AI operations"""
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    timeline_id: Optional[str] = None
    assets: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    system_prompt: Optional[str] = None


class AITask(BaseModel):
    """AI task model"""
    __tablename__ = "ai_tasks"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default=TaskStatus.PENDING.value, index=True)
    
    # Task configuration
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Model configuration
    model: Mapped[str] = mapped_column(String(100), default="gpt-4")
    provider: Mapped[str] = mapped_column(String(50), default=ModelProvider.OPENAI.value)
    model_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Execution state
    priority: Mapped[str] = mapped_column(String(20), default=TaskPriority.NORMAL.value)
    
    # Results
    response: Mapped[Optional[Text]] = mapped_column(Text, nullable=True)
    response_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Timing
    queued_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    
    # References
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    project_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    timeline_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("timelines.id"), nullable=True)
    
    # Parent task for chaining
    parent_task_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)