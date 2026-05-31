"""
Scheduler Services - Resource management and scheduling
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Set
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_

from .models import (
    WorkerType,
    AllocationStatus,
    ResourceType,
    QueuePriority,
    WorkerPool,
    ResourcePool,
    JobAllocation,
    QueueEntry,
    SchedulingDecision,
    CapacityMetric,
)

logger = logging.getLogger(__name__)


@dataclass
class ResourceRequest:
    """Resource request for job scheduling"""
    job_id: str
    job_type: str
    memory_mb: int = 1024
    gpu_required: bool = False
    gpu_memory_mb: Optional[int] = None
    estimated_duration: float = 60.0
    priority: QueuePriority = QueuePriority.NORMAL
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AllocationDecision:
    """Allocation decision"""
    job_id: str
    allocated: bool
    worker: Optional[str] = None
    resources: Dict[str, Any] = field(default_factory=dict)
    wait_time: float = 0.0
    reason: str = ""


class ResourceScheduler:
    """
    Resource scheduler for distributed execution.
    Handles resource allocation, worker management, and queue balancing.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._worker_pools: Dict[str, WorkerPool] = {}
        self._resource_pools: Dict[str, ResourcePool] = {}
        self._active_allocations: Dict[str, JobAllocation] = {}
        self._queue_buffers: Dict[str, List[QueueEntry]] = defaultdict(list)
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize the resource scheduler"""
        await self._load_pools()
        self._running = True
        logger.info("ResourceScheduler initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the scheduler"""
        self._running = False
        # Release all allocations
        for allocation in self._active_allocations.values():
            await self.release_allocation(allocation.job_id)
        logger.info("ResourceScheduler shutdown")
    
    async def _load_pools(self) -> None:
        """Load worker and resource pools from database"""
        # Load worker pools
        result = await self.db.execute(select(WorkerPool))
        for pool in result.scalars().all():
            self._worker_pools[pool.name] = pool
        
        # Load resource pools
        result = await self.db.execute(select(ResourcePool))
        for pool in result.scalars().all():
            self._resource_pools[pool.name] = pool
    
    # ==================== Worker Pool Management ====================
    
    async def create_worker_pool(
        self,
        name: str,
        worker_type: WorkerType,
        min_workers: int = 1,
        max_workers: int = 10,
        memory_per_worker_mb: int = 4096,
        gpu_per_worker: int = 0,
        is_autoscaling: bool = False,
    ) -> WorkerPool:
        """Create a worker pool"""
        pool = WorkerPool(
            name=name,
            worker_type=worker_type.value,
            min_workers=min_workers,
            max_workers=max_workers,
            desired_workers=(min_workers + max_workers) // 2,
            memory_per_worker_mb=memory_per_worker_mb,
            gpu_per_worker=gpu_per_worker,
            is_autoscaling=is_autoscaling,
        )
        
        self.db.add(pool)
        await self.db.commit()
        await self.db.refresh(pool)
        
        self._worker_pools[name] = pool
        
        return pool
    
    async def get_worker_pool(
        self,
        name: str,
    ) -> Optional[WorkerPool]:
        """Get worker pool by name"""
        return self._worker_pools.get(name)
    
    async def update_worker_pool_status(
        self,
        pool: WorkerPool,
        active_workers: int,
        busy_workers: int,
    ) -> WorkerPool:
        """Update worker pool status"""
        pool.active_workers = active_workers
        pool.busy_workers = busy_workers
        pool.idle_workers = active_workers - busy_workers
        
        self.db.add(pool)
        await self.db.commit()
        await self.db.refresh(pool)
        
        return pool
    
    # ==================== Resource Pool Management ====================
    
    async def create_resource_pool(
        self,
        name: str,
        resource_type: ResourceType,
        total_capacity: float,
        total_units: int,
        reservation_policy: str = "fair",
    ) -> ResourcePool:
        """Create a resource pool"""
        pool = ResourcePool(
            name=name,
            resource_type=resource_type.value,
            total_capacity=total_capacity,
            total_units=total_units,
            available_capacity=total_capacity,
            available_units=total_units,
        )
        
        self.db.add(pool)
        await self.db.commit()
        await self.db.refresh(pool)
        
        self._resource_pools[name] = pool
        
        return pool
    
    async def allocate_resources(
        self,
        resource_type: ResourceType,
        quantity: float,
        job_id: Optional[str] = None,
    ) -> Optional[ResourcePool]:
        """Allocate resources from pool"""
        pool_name = f"{resource_type.value}_pool"
        pool = self._resource_pools.get(pool_name)
        
        if not pool or pool.available_capacity < quantity:
            return None
        
        pool.available_capacity -= quantity
        pool.available_units -= int(quantity)
        pool.allocated_capacity += quantity
        pool.allocated_units += int(quantity)
        pool.utilization_percent = (pool.allocated_capacity / pool.total_capacity) * 100
        
        self.db.add(pool)
        await self.db.commit()
        
        return pool
    
    async def release_resources(
        self,
        resource_type: ResourceType,
        quantity: float,
    ) -> Optional[ResourcePool]:
        """Release resources back to pool"""
        pool_name = f"{resource_type.value}_pool"
        pool = self._resource_pools.get(pool_name)
        
        if not pool:
            return None
        
        pool.available_capacity += quantity
        pool.available_units += int(quantity)
        pool.allocated_capacity -= quantity
        pool.allocated_units -= int(quantity)
        pool.utilization_percent = (pool.allocated_capacity / pool.total_capacity) * 100
        
        self.db.add(pool)
        await self.db.commit()
        
        return pool
    
    # ==================== Queue Management ====================
    
    async def enqueue_job(
        self,
        job_id: str,
        job_name: str,
        job_type: str,
        queue_name: str,
        priority: QueuePriority = QueuePriority.NORMAL,
        requirements: Optional[Dict[str, Any]] = None,
        estimated_duration: Optional[float] = None,
        owner_id: Optional[UUID] = None,
    ) -> QueueEntry:
        """Add job to queue"""
        entry = QueueEntry(
            job_id=job_id,
            job_name=job_name,
            job_type=job_type,
            queue_name=queue_name,
            priority=priority.value,
            requirements=requirements,
            estimated_duration=estimated_duration,
            owner_id=owner_id,
        )
        
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        
        self._queue_buffers[queue_name].append(entry)
        self._sort_queue(queue_name)
        
        return entry
    
    def _sort_queue(self, queue_name: str) -> None:
        """Sort queue by priority and enqueue time"""
        priority_weights = {
            QueuePriority.URGENT.value: 1000,
            QueuePriority.HIGH.value: 100,
            QueuePriority.NORMAL.value: 10,
            QueuePriority.LOW.value: 1,
        }
        
        self._queue_buffers[queue_name].sort(
            key=lambda e: (
                -priority_weights.get(e.priority, 10),
                e.enqueued_at,
            )
        )
    
    async def get_next_job(self, queue_name: str) -> Optional[QueueEntry]:
        """Get next job from queue"""
        queue = self._queue_buffers.get(queue_name, [])
        
        for entry in queue:
            if entry.status == "queued":
                return entry
        
        return None
    
    async def dequeue_job(self, job_id: str) -> Optional[QueueEntry]:
        """Remove job from queue"""
        for queue_name, queue in self._queue_buffers.items():
            for i, entry in enumerate(queue):
                if entry.job_id == job_id:
                    self._queue_buffers[queue_name].pop(i)
                    entry.status = "dequeued"
                    self.db.add(entry)
                    await self.db.commit()
                    return entry
        
        return None
    
    async def get_queue_depth(self, queue_name: str) -> Dict[str, int]:
        """Get queue depth statistics"""
        queue = self._queue_buffers.get(queue_name, [])
        
        return {
            "total": len(queue),
            "queued": len([e for e in queue if e.status == "queued"]),
            "processing": len([e for e in queue if e.status == "processing"]),
            "completed": len([e for e in queue if e.status == "completed"]),
            "failed": len([e for e in queue if e.status == "failed"]),
        }
    
    # ==================== Allocation ====================
    
    async def allocate_job(
        self,
        request: ResourceRequest,
    ) -> AllocationDecision:
        """Allocate resources for a job"""
        # Check worker availability
        pool_name = f"{request.job_type}_pool"
        pool = self._worker_pools.get(pool_name)
        
        if not pool or pool.idle_workers <= 0:
            return AllocationDecision(
                job_id=request.job_id,
                allocated=False,
                reason="No available workers",
            )
        
        # Check memory availability
        if request.memory_mb > pool.memory_per_worker_mb:
            return AllocationDecision(
                job_id=request.job_id,
                allocated=False,
                reason="Insufficient memory per worker",
            )
        
        # Allocate worker
        worker_id = f"{pool.name}-worker-{pool.idle_workers}"
        
        # Create allocation record
        allocation = JobAllocation(
            job_id=request.job_id,
            job_type=request.job_type,
            worker_pool_id=pool.id,
            allocated_worker=worker_id,
            allocated_resources={
                "memory_mb": request.memory_mb,
                "gpu_required": request.gpu_required,
                "gpu_memory_mb": request.gpu_memory_mb,
            },
            status=AllocationStatus.ALLOCATED.value,
            priority=request.priority.value,
        )
        
        self.db.add(allocation)
        await self.db.commit()
        await self.db.refresh(allocation)
        
        self._active_allocations[request.job_id] = allocation
        
        # Update pool
        pool.busy_workers += 1
        pool.idle_workers -= 1
        self.db.add(pool)
        await self.db.commit()
        
        return AllocationDecision(
            job_id=request.job_id,
            allocated=True,
            worker=worker_id,
            resources=allocation.allocated_resources or {},
        )
    
    async def release_allocation(self, job_id: str) -> Optional[JobAllocation]:
        """Release job allocation"""
        allocation = self._active_allocations.get(job_id)
        
        if not allocation:
            return None
        
        # Update allocation
        allocation.status = AllocationStatus.RELEASED.value
        allocation.released_at = datetime.utcnow()
        self.db.add(allocation)
        await self.db.commit()
        
        # Update worker pool
        if allocation.worker_pool_id:
            result = await self.db.execute(
                select(WorkerPool).where(WorkerPool.id == allocation.worker_pool_id)
            )
            pool = result.scalar_one_or_none()
            
            if pool and pool.busy_workers > 0:
                pool.busy_workers -= 1
                pool.idle_workers += 1
                self.db.add(pool)
                await self.db.commit()
        
        # Release resources
        resources = allocation.allocated_resources or {}
        if resources.get("memory_mb"):
            await self.release_resources(
                ResourceType.MEMORY,
                resources["memory_mb"],
            )
        
        del self._active_allocations[job_id]
        
        return allocation
    
    # ==================== Scheduling Decisions ====================
    
    async def record_decision(
        self,
        decision_type: str,
        job_id: str,
        decision_reason: str,
        assigned_worker: Optional[str] = None,
        assigned_resources: Optional[Dict[str, Any]] = None,
        alternatives: Optional[List[Dict[str, Any]]] = None,
        rejected_reasons: Optional[List[str]] = None,
    ) -> SchedulingDecision:
        """Record scheduling decision"""
        # Get current queue depth and utilization
        queue_depth = len(self._queue_buffers.get("default", []))
        worker_utilization = 0.0
        
        for pool in self._worker_pools.values():
            if pool.active_workers > 0:
                worker_utilization = max(
                    worker_utilization,
                    (pool.busy_workers / pool.active_workers) * 100,
                )
        
        decision = SchedulingDecision(
            decision_id=str(uuid4()),
            job_id=job_id,
            decision_type=decision_type,
            decision_reason=decision_reason,
            assigned_worker=assigned_worker,
            assigned_resources=assigned_resources,
            alternatives=alternatives,
            rejected_reasons=rejected_reasons,
            decision_time=datetime.utcnow(),
            queue_depth=queue_depth,
            worker_utilization=worker_utilization,
        )
        
        self.db.add(decision)
        await self.db.commit()
        await self.db.refresh(decision)
        
        return decision
    
    # ==================== Metrics ====================
    
    async def record_capacity_metric(
        self,
        metric_name: str,
        value: float,
        unit: str,
        source: str,
        source_type: str,
        pool_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> CapacityMetric:
        """Record capacity metric"""
        metric = CapacityMetric(
            metric_name=metric_name,
            value=value,
            unit=unit,
            source=source,
            source_type=source_type,
            pool_id=pool_id,
            tags=tags,
            timestamp=datetime.utcnow(),
        )
        
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        
        return metric
    
    async def get_pool_utilization(self) -> Dict[str, Dict[str, float]]:
        """Get utilization for all pools"""
        utilization = {}
        
        for name, pool in self._worker_pools.items():
            if pool.active_workers > 0:
                utilization[name] = {
                    "total_workers": pool.active_workers,
                    "busy_workers": pool.busy_workers,
                    "idle_workers": pool.idle_workers,
                    "utilization_percent": (pool.busy_workers / pool.active_workers) * 100,
                    "total_jobs": pool.total_jobs_processed,
                    "failures": pool.total_failures,
                    "failure_rate": (pool.total_failures / pool.total_jobs_processed * 100) if pool.total_jobs_processed > 0 else 0,
                }
        
        return utilization


class AdaptiveScheduler:
    """
    Adaptive scheduler with workload-aware decisions.
    Adjusts scheduling based on system state and metrics.
    """
    
    def __init__(self, db: AsyncSession, resource_scheduler: ResourceScheduler):
        self.db = db
        self.resource_scheduler = resource_scheduler
        self._scaling_policies: Dict[str, Dict[str, Any]] = {}
    
    async def should_scale_up(
        self,
        pool_name: str,
    ) -> tuple[bool, Optional[int]]:
        """Determine if pool should scale up"""
        pool = self.resource_scheduler._worker_pools.get(pool_name)
        
        if not pool or not pool.is_autoscaling:
            return False, None
        
        # Check queue depth
        queue = self.resource_scheduler._queue_buffers.get(pool.worker_type, [])
        queue_depth = len(queue)
        
        # Check utilization
        if pool.active_workers > 0:
            utilization = pool.busy_workers / pool.active_workers
        else:
            utilization = 0
        
        # Scale up if queue is long or utilization is high
        if queue_depth > pool.max_workers * 2 or utilization > 0.8:
            new_desired = min(pool.desired_workers + 1, pool.max_workers)
            return True, new_desired
        
        return False, None
    
    async def should_scale_down(
        self,
        pool_name: str,
    ) -> tuple[bool, Optional[int]]:
        """Determine if pool should scale down"""
        pool = self.resource_scheduler._worker_pools.get(pool_name)
        
        if not pool or not pool.is_autoscaling:
            return False, None
        
        # Check queue depth
        queue = self.resource_scheduler._queue_buffers.get(pool.worker_type, [])
        queue_depth = len(queue)
        
        # Check utilization
        if pool.active_workers > 0:
            utilization = pool.busy_workers / pool.active_workers
        else:
            utilization = 0
        
        # Scale down if queue is empty and utilization is low
        if queue_depth == 0 and utilization < 0.3 and pool.active_workers > pool.min_workers:
            new_desired = max(pool.desired_workers - 1, pool.min_workers)
            return True, new_desired
        
        return False, None
    
    async def apply_scaling_decision(
        self,
        pool_name: str,
        target_workers: int,
    ) -> None:
        """Apply scaling decision to pool"""
        pool = self.resource_scheduler._worker_pools.get(pool_name)
        
        if not pool:
            return
        
        pool.desired_workers = target_workers
        self.db.add(pool)
        await self.db.commit()
        
        logger.info(f"Scaled pool {pool_name} to {target_workers} workers")