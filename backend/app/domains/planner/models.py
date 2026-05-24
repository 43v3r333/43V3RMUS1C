"""
Planner Domain Models - Execution orchestration and scheduling
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


class PlanStatus(str, Enum):
    """Execution plan status"""
    PENDING = "pending"
    PLANNING = "planning"
    SCHEDULED = "scheduled"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ExecutionStrategy(str, Enum):
    """Execution strategy"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    ADAPTIVE = "adaptive"
    DISTRIBUTED = "distributed"


class PriorityLevel(str, Enum):
    """Priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class AllocationState(str, Enum):
    """Resource allocation state"""
    PENDING = "pending"
    ALLOCATED = "allocated"
    RESERVED = "reserved"
    RELEASED = "released"
    FAILED = "failed"


@dataclass
class ExecutionStep:
    """Execution step in a plan"""
    step_id: str
    name: str
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: float = 0.0
    priority: PriorityLevel = PriorityLevel.NORMAL
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    retry_config: Optional[Dict[str, Any]] = None


@dataclass
class ResourceRequirement:
    """Resource requirement for execution"""
    resource_type: str
    quantity: float
    memory_mb: Optional[int] = None
    gpu_required: bool = False
    gpu_memory_mb: Optional[int] = None
    network_required: bool = False


class ExecutionPlan(BaseModel):
    """Execution plan model - defines planned execution"""
    __tablename__ = "execution_plans"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Plan configuration
    plan_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    strategy: Mapped[str] = mapped_column(String(20), default=ExecutionStrategy.SEQUENTIAL.value)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=PlanStatus.PENDING.value, index=True)
    
    # Steps
    steps: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=False)
    current_step: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    completed_steps: Mapped[int] = mapped_column(Integer, default=0)
    failed_steps: Mapped[int] = mapped_column(Integer, default=0)
    
    # Scheduling
    priority: Mapped[str] = mapped_column(String(20), default=PriorityLevel.NORMAL.value, index=True)
    scheduled_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    estimated_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Resources
    resource_requirements: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    allocated_resources: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    
    # Context
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    parent_plan_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    project_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    
    # Tags
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)


class ExecutionStepRecord(BaseModel):
    """Execution step record model - tracks step execution"""
    __tablename__ = "execution_step_records"
    
    plan_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("execution_plans.id"), nullable=False, index=True)
    
    # Step info
    step_id: Mapped[str] = mapped_column(String(100), nullable=False)
    step_name: Mapped[str] = mapped_column(String(255), nullable=False)
    step_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    
    # Timing
    scheduled_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    actual_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    actual_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    estimated_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Resource allocation
    allocated_worker: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    allocated_gpu: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    
    # Output
    output: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)


class ResourceAllocation(BaseModel):
    """Resource allocation model - tracks resource usage"""
    __tablename__ = "resource_allocations"
    
    plan_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("execution_plans.id"), nullable=True, index=True)
    step_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Resource info
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Allocation state
    state: Mapped[str] = mapped_column(String(20), default=AllocationState.PENDING.value, index=True)
    
    # Allocation details
    allocated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    released_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    requested_quantity: Mapped[float] = mapped_column(Float, default=1.0)
    allocated_quantity: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Capacity usage
    memory_used_mb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gpu_memory_used_mb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cpu_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Cost tracking
    cost_per_hour: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class SchedulerMetric(BaseModel):
    """Scheduler metric model - performance tracking"""
    __tablename__ = "scheduler_metrics"
    
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Value
    value: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Source
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Category
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Tags
    tags: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON, nullable=True)
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class WorkloadSnapshot(BaseModel):
    """Workload snapshot model - queue state tracking"""
    __tablename__ = "workload_snapshots"
    
    snapshot_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Queue stats
    total_jobs: Mapped[int] = mapped_column(Integer, default=0)
    pending_jobs: Mapped[int] = mapped_column(Integer, default=0)
    running_jobs: Mapped[int] = mapped_column(Integer, default=0)
    completed_jobs: Mapped[int] = mapped_column(Integer, default=0)
    failed_jobs: Mapped[int] = mapped_column(Integer, default=0)
    
    # Priority breakdown
    low_priority: Mapped[int] = mapped_column(Integer, default=0)
    normal_priority: Mapped[int] = mapped_column(Integer, default=0)
    high_priority: Mapped[int] = mapped_column(Integer, default=0)
    urgent_priority: Mapped[int] = mapped_column(Integer, default=0)
    
    # Resource usage
    total_memory_mb: Mapped[int] = mapped_column(Integer, default=0)
    available_memory_mb: Mapped[int] = mapped_column(Integer, default=0)
    total_gpu_count: Mapped[int] = mapped_column(Integer, default=0)
    available_gpu_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Worker stats
    total_workers: Mapped[int] = mapped_column(Integer, default=0)
    active_workers: Mapped[int] = mapped_column(Integer, default=0)
    idle_workers: Mapped[int] = mapped_column(Integer, default=0)
    busy_workers: Mapped[int] = mapped_column(Integer, default=0)


class OrchestrationSession(BaseModel):
    """Orchestration session model - runtime session tracking"""
    __tablename__ = "orchestration_sessions"
    
    session_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    session_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    
    # Configuration
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Metrics
    total_plans: Mapped[int] = mapped_column(Integer, default=0)
    active_plans: Mapped[int] = mapped_column(Integer, default=0)
    completed_plans: Mapped[int] = mapped_column(Integer, default=0)
    failed_plans: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class ExecutionProfile(BaseModel):
    """Execution profile model - workflow optimization"""
    __tablename__ = "execution_profiles"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Profile type
    profile_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Configuration
    execution_strategy: Mapped[str] = mapped_column(String(20), default=ExecutionStrategy.SEQUENTIAL.value)
    max_parallelism: Mapped[int] = mapped_column(Integer, default=1)
    timeout_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Resource config
    resource_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Optimization hints
    hints: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Usage stats
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Version
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)