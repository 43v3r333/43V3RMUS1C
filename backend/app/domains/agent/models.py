"""
Agent Domain Models - Multi-agent orchestration
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class AgentType(str, Enum):
    """Agent types"""
    GENERATOR = "generator"
    OPTIMIZER = "optimizer"
    ANALYZER = "analyzer"
    ORCHESTRATOR = "orchestrator"
    SCHEDULER = "scheduler"
    MONITOR = "monitor"


class AgentStatus(str, Enum):
    """Agent status"""
    INITIALIZING = "initializing"
    IDLE = "idle"
    BUSY = "busy"
    WAITING = "waiting"
    ERROR = "error"
    TERMINATED = "terminated"


class AgentCapability(str, Enum):
    """Agent capabilities"""
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    AUDIO_GENERATION = "audio_generation"
    VIDEO_GENERATION = "video_generation"
    ANALYSIS = "analysis"
    OPTIMIZATION = "optimization"
    SCHEDULING = "scheduling"
    COORDINATION = "coordination"


class CoordinationAction(str, Enum):
    """Coordination actions"""
    REQUEST = "request"
    GRANT = "grant"
    RELEASE = "release"
    DELEGATE = "delegate"
    TERMINATE = "terminate"
    NOTIFY = "notify"


class MessagePriority(str, Enum):
    """Message priority"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AgentSession(BaseModel):
    """Agent session model - tracks agent execution sessions"""
    __tablename__ = "agent_sessions"
    
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    agent_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    session_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Configuration
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # State
    status: Mapped[str] = mapped_column(String(20), default=AgentStatus.INITIALIZING.value, index=True)
    
    # Metrics
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
    tasks_failed: Mapped[int] = mapped_column(Integer, default=0)
    
    # Context
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class AgentRegistration(BaseModel):
    """Agent registration model - agent registry entry"""
    __tablename__ = "agent_registrations"
    
    agent_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Agent info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Capabilities
    capabilities: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    supported_models: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=AgentStatus.IDLE.value, index=True)
    
    # Configuration
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Metrics
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
    tasks_failed: Mapped[int] = mapped_column(Integer, default=0)
    avg_execution_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Resource limits
    max_concurrent_tasks: Mapped[int] = mapped_column(Integer, default=5)
    current_tasks: Mapped[int] = mapped_column(Integer, default=0)
    
    # Health
    health_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_heartbeat: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Registration
    registered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class CoordinationMessage(BaseModel):
    """Coordination message model - agent communication"""
    __tablename__ = "coordination_messages"
    
    message_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Sender & receiver
    from_agent: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    to_agent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    message_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Content
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Priority
    priority: Mapped[str] = mapped_column(String(20), default=MessagePriority.NORMAL.value)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    
    # Session
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Retry
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)


class AgentTask(BaseModel):
    """Agent task model - task assignment tracking"""
    __tablename__ = "agent_tasks"
    
    task_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Assignment
    assigned_agent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    delegation_chain: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Task info
    task_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Configuration
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    
    # Priority
    priority: Mapped[int] = mapped_column(Integer, default=5)
    
    # Dependencies
    dependencies: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    blocking_tasks: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Progress
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    current_step: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Result
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    estimated_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Session
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class ArbitrationDecision(BaseModel):
    """Arbitration decision model - task arbitration records"""
    __tablename__ = "arbitration_decisions"
    
    decision_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Task info
    task_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Candidates
    candidate_agents: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    selected_agent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Decision
    decision_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Scoring
    scores: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timing
    decided_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class AgentHealth(BaseModel):
    """Agent health model - agent health monitoring"""
    __tablename__ = "agent_health"
    
    agent_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="healthy", index=True)
    
    # Metrics
    cpu_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    memory_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gpu_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Performance
    avg_latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    throughput: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Errors
    error_count_1h: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Check
    checked_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)