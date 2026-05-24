"""
Runtime Domain Models - Centralized runtime orchestration
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


class RuntimeStatus(str, Enum):
    """Runtime session status"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class SessionStatus(str, Enum):
    """Session status"""
    ACTIVE = "active"
    IDLE = "idle"
    TERMINATED = "terminated"
    FAILED = "failed"


class NodeStatus(str, Enum):
    """Workflow node status"""
    PENDING = "pending"
    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class ExecutionMode(str, Enum):
    """Execution mode"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"


@dataclass
class ExecutionContext:
    """Context for workflow execution"""
    session_id: str
    workflow_id: str
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NodeResult:
    """Result of node execution"""
    node_id: str
    status: NodeStatus
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: float = 0.0
    retries: int = 0


class RuntimeSession(BaseModel):
    """Runtime session model - tracks active runtime sessions"""
    __tablename__ = "runtime_sessions"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    session_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default=RuntimeStatus.INITIALIZING.value, index=True)
    
    # Configuration
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    capabilities: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # State
    current_workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    active_nodes: Mapped[int] = mapped_column(Integer, default=0)
    total_executions: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metrics
    events_processed: Mapped[int] = mapped_column(Integer, default=0)
    events_failed: Mapped[int] = mapped_column(Integer, default=0)
    average_execution_time: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Error handling
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    
    # Resource limits
    max_concurrent_nodes: Mapped[int] = mapped_column(Integer, default=10)
    memory_limit_mb: Mapped[int] = mapped_column(Integer, default=1024)


class WorkflowGraph(BaseModel):
    """Workflow graph model - defines workflow structure"""
    __tablename__ = "workflow_graphs"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    # Graph structure
    nodes: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=False)
    edges: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=False)
    
    # Execution configuration
    execution_mode: Mapped[str] = mapped_column(String(20), default=ExecutionMode.SEQUENTIAL.value)
    max_parallelism: Mapped[int] = mapped_column(Integer, default=1)
    
    # Metadata
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Usage tracking
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    last_executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    # Parent for versioning
    parent_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class WorkflowNode(BaseModel):
    """Workflow node model - individual step in workflow"""
    __tablename__ = "workflow_nodes"
    
    graph_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workflow_graphs.id"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Position (for visualization)
    position_x: Mapped[float] = mapped_column(Float, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Configuration
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    
    # Dependencies
    depends_on: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    conditions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Retry configuration
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    retry_delay: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Timeout
    timeout_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Order for visualization
    order: Mapped[int] = mapped_column(Integer, default=0)


class WorkflowExecution(BaseModel):
    """Workflow execution model - tracks workflow runs"""
    __tablename__ = "workflow_executions"
    
    graph_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workflow_graphs.id"), nullable=False, index=True)
    session_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("runtime_sessions.id"), nullable=True)
    
    # Execution info
    status: Mapped[str] = mapped_column(String(20), default=NodeStatus.PENDING.value, index=True)
    execution_mode: Mapped[str] = mapped_column(String(20), default=ExecutionMode.SEQUENTIAL.value)
    
    # Input/output
    input_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    output_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Progress
    total_nodes: Mapped[int] = mapped_column(Integer, default=0)
    completed_nodes: Mapped[int] = mapped_column(Integer, default=0)
    failed_nodes: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    queued_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    # Parent for batching
    parent_execution_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class NodeExecution(BaseModel):
    """Node execution model - tracks individual node runs"""
    __tablename__ = "node_executions"
    
    execution_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workflow_executions.id"), nullable=False, index=True)
    node_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workflow_nodes.id"), nullable=False)
    
    # Status and timing
    status: Mapped[str] = mapped_column(String(20), default=NodeStatus.PENDING.value, index=True)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Input/output
    input_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    output_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Worker info
    worker_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Execution order
    order: Mapped[int] = mapped_column(Integer, default=0)


class RuntimeEventLog(BaseModel):
    """Runtime event log model - audit trail for runtime events"""
    __tablename__ = "runtime_event_logs"
    
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    execution_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Event info
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Source
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    node_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Data
    data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Severity
    severity: Mapped[str] = mapped_column(String(20), default="info")
    
    # User context
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class RuntimeMetric(BaseModel):
    """Runtime metric model - performance metrics"""
    __tablename__ = "runtime_metrics"
    
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Values
    value: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Tags
    tags: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON, nullable=True)
    
    # Aggregation
    aggregation: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)


class AIGenerationRequest(BaseModel):
    """AI generation request model"""
    __tablename__ = "ai_generation_requests"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    generation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Configuration
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    negative_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Model
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    
    # Input/Output
    input_assets: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    output_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    output_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timing
    queued_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Usage
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Error
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Execution
    execution_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


# Relationship imports
from ...models.user import User