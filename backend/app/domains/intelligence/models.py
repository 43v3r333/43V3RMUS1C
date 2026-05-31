"""
Intelligence Domain Models - AI coordination and orchestration
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum
from dataclasses import dataclass, field

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class InferenceStatus(str, Enum):
    """Inference execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelProvider(str, Enum):
    """AI model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    NVIDIA = "nvidia"
    CUSTOM = "custom"


class PromptType(str, Enum):
    """Prompt types"""
    COMPLETION = "completion"
    CHAT = "chat"
    EMBEDDING = "embedding"
    IMAGE = "image"
    AUDIO = "audio"


@dataclass
class InferenceMetrics:
    """Inference metrics"""
    tokens_per_second: float = 0.0
    first_token_latency_ms: float = 0.0
    total_latency_ms: float = 0.0
    cache_hit_rate: float = 0.0


class InferenceRequest(BaseModel):
    """Inference request model - tracks AI generation requests"""
    __tablename__ = "inference_requests"
    
    request_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Request info
    prompt_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Input
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    messages: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Configuration
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, default=4096)
    top_p: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=InferenceStatus.PENDING.value, index=True)
    
    # Output
    response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    finish_reason: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Metrics
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    input_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Latency
    queued_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    total_latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Error
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Context
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    session_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    project_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class PromptTemplate(BaseModel):
    """Prompt template model - reusable prompt patterns"""
    __tablename__ = "prompt_templates"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Template type
    template_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Template content
    system_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_template: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Variables
    variables: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    required_variables: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Configuration
    default_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    recommended_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Usage
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Version
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class ModelSelection(BaseModel):
    """Model selection model - tracks model selection decisions"""
    __tablename__ = "model_selections"
    
    selection_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Request info
    request_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Selection
    selected_model: Mapped[str] = mapped_column(String(100), nullable=False)
    selected_provider: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Alternatives considered
    alternatives: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    selection_reason: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Requirements
    requirements: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Performance
    actual_latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_quality: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timing
    selected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class GenerationPipeline(BaseModel):
    """Generation pipeline model - multi-step AI pipelines"""
    __tablename__ = "generation_pipelines"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Pipeline config
    pipeline_type: Mapped[str] = mapped_column(String(50), nullable=False)
    steps: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="draft")
    
    # Version
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class PipelineExecution(BaseModel):
    """Pipeline execution model - tracks pipeline runs"""
    __tablename__ = "pipeline_executions"
    
    pipeline_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("generation_pipelines.id"), nullable=False, index=True)
    
    # Execution info
    execution_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default=InferenceStatus.PENDING.value, index=True)
    
    # Input
    input_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Output
    output_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    step_results: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Metrics
    total_steps: Mapped[int] = mapped_column(Integer, default=0)
    completed_steps: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    total_duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Error
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class AICoordinationLog(BaseModel):
    """AI coordination log - audit trail for AI operations"""
    __tablename__ = "ai_coordination_logs"
    
    log_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Event info
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    event_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Source
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Data
    data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Timing
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Severity
    severity: Mapped[str] = mapped_column(String(20), default="info")


class ProviderHealth(BaseModel):
    """Provider health model - tracks AI provider status"""
    __tablename__ = "provider_health"
    
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="healthy", index=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metrics
    avg_latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    requests_per_minute: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Limits
    rate_limit_remaining: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rate_limit_reset: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Errors
    error_count_24h: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Last check
    last_check: Mapped[datetime] = mapped_column(DateTime, nullable=False)