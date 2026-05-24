"""
Scheduler Domain Models - Resource scheduling and allocation
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


class WorkerType(str, Enum):
    """Worker types for scheduling"""
    MEDIA = "media"
    RENDER = "render"
    AI = "ai"
    RUNTIME = "runtime"
    ANALYTICS = "analytics"
    GENERAL = "general"


class AllocationStatus(str, Enum):
    """Allocation status"""
    PENDING = "pending"
    ALLOCATED = "allocated"
    RESERVED = "reserved"
    RELEASED = "released"
    EXPIRED = "expired"


class ResourceType(str, Enum):
    """Resource types"""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"


class QueuePriority(str, Enum):
    """Queue priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class WorkerPool(BaseModel):
    """Worker pool model - manages worker groups"""
    __tablename__ = "worker_pools"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Pool type
    worker_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Capacity
    min_workers: Mapped[int] = mapped_column(Integer, default=1)
    max_workers: Mapped[int] = mapped_column(Integer, default=10)
    desired_workers: Mapped[int] = mapped_column(Integer, default=5)
    
    # Current state
    active_workers: Mapped[int] = mapped_column(Integer, default=0)
    busy_workers: Mapped[int] = mapped_column(Integer, default=0)
    idle_workers: Mapped[int] = mapped_column(Integer, default=0)
    
    # Resource allocation
    memory_per_worker_mb: Mapped[int] = mapped_column(Integer, default=4096)
    gpu_per_worker: Mapped[int] = mapped_column(Integer, default=0)
    
    # Configuration
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="active")
    is_autoscaling: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Metrics
    total_jobs_processed: Mapped[int] = mapped_column(Integer, default=0)
    total_failures: Mapped[int] = mapped_column(Integer, default=0)
    avg_job_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class ResourcePool(BaseModel):
    """Resource pool model - manages resource allocation"""
    __tablename__ = "resource_pools"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    
    # Resource type
    resource_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Total capacity
    total_capacity: Mapped[float] = mapped_column(Float, default=0.0)
    total_units: Mapped[int] = mapped_column(Integer, default=0)
    
    # Available
    available_capacity: Mapped[float] = mapped_column(Float, default=0.0)
    available_units: Mapped[int] = mapped_column(Integer, default=0)
    
    # Allocation
    allocated_capacity: Mapped[float] = mapped_column(Float, default=0.0)
    allocated_units: Mapped[int] = mapped_column(Integer, default=0)
    
    # Utilization
    utilization_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Configuration
    reservation_policy: Mapped[str] = mapped_column(String(50), default="fair")
    max_allocation_per_job: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="active")
    
    # Metrics
    peak_utilization: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class JobAllocation(BaseModel):
    """Job allocation model - tracks job-resource assignments"""
    __tablename__ = "job_allocations"
    
    job_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    job_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Resource info
    resource_pool_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("resource_pools.id"), nullable=True)
    worker_pool_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("worker_pools.id"), nullable=True)
    
    # Allocation
    allocated_worker: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    allocated_resources: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=AllocationStatus.PENDING.value, index=True)
    
    # Timing
    allocated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    released_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Usage
    memory_used_mb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gpu_used: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cpu_percent_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Priority
    priority: Mapped[str] = mapped_column(String(20), default=QueuePriority.NORMAL.value)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    # Correlation
    plan_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class QueueEntry(BaseModel):
    """Queue entry model - job queue management"""
    __tablename__ = "queue_entries"
    
    job_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    job_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Queue info
    queue_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Priority
    priority: Mapped[str] = mapped_column(String(20), default=QueuePriority.NORMAL.value, index=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="queued", index=True)
    
    # Configuration
    requirements: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    constraints: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    enqueued_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    scheduled_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    actual_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Estimated
    estimated_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    estimated_wait_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Retry
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    
    # Error
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Position
    position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class SchedulingDecision(BaseModel):
    """Scheduling decision model - decision audit trail"""
    __tablename__ = "scheduling_decisions"
    
    decision_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Job info
    job_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Decision
    decision_type: Mapped[str] = mapped_column(String(50), nullable=False)
    decision_reason: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Allocation
    assigned_worker: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    assigned_resources: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Alternatives considered
    alternatives: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    rejected_reasons: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    decision_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Metrics
    queue_depth: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    worker_utilization: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class CapacityMetric(BaseModel):
    """Capacity metric model - resource capacity tracking"""
    __tablename__ = "capacity_metrics"
    
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Value
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Source
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Context
    pool_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Tags
    tags: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON, nullable=True)
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)