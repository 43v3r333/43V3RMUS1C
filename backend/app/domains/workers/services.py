"""
Worker Orchestrator Services - Worker management and telemetry
"""
import asyncio
import logging
import psutil
from typing import Dict, List, Optional, Any
from uuid import UUID
from dataclasses import dataclass
from datetime import datetime, timedelta
import socket

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from .models import (
    WorkerStatus,
    WorkerType,
    WorkerMetrics,
    WorkerHealth,
    Worker,
    WorkerMetric,
    WorkerEvent,
    ProcessingState,
    RuntimeLog,
)

logger = logging.getLogger(__name__)


class WorkerRegistry:
    """
    Worker registry for tracking registered workers.
    """
    
    def __init__(self):
        self._workers: Dict[str, Dict[str, Any]] = {}
        self._heartbeat_tasks: Dict[str, asyncio.Task] = {}
    
    def register_worker(
        self,
        worker_id: str,
        worker_type: WorkerType,
        capabilities: List[str],
        hostname: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Register a new worker"""
        self._workers[worker_id] = {
            "worker_id": worker_id,
            "worker_type": worker_type.value,
            "capabilities": capabilities,
            "hostname": hostname or socket.gethostname(),
            "ip_address": ip_address,
            "registered_at": datetime.utcnow(),
            "last_heartbeat": datetime.utcnow(),
            "status": WorkerStatus.ONLINE.value,
            "current_jobs": [],
        }
        
        logger.info(f"Worker registered: {worker_id}")
        return self._workers[worker_id]
    
    def unregister_worker(self, worker_id: str) -> bool:
        """Unregister a worker"""
        if worker_id in self._workers:
            del self._workers[worker_id]
            logger.info(f"Worker unregistered: {worker_id}")
            return True
        return False
    
    def get_worker(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """Get worker info"""
        return self._workers.get(worker_id)
    
    def get_workers_by_type(self, worker_type: WorkerType) -> List[Dict[str, Any]]:
        """Get workers by type"""
        return [
            w for w in self._workers.values()
            if w["worker_type"] == worker_type.value
        ]
    
    def get_online_workers(self) -> List[Dict[str, Any]]:
        """Get all online workers"""
        return [
            w for w in self._workers.values()
            if w["status"] == WorkerStatus.ONLINE.value
        ]
    
    def update_heartbeat(
        self,
        worker_id: str,
        current_jobs: Optional[List[str]] = None,
    ) -> bool:
        """Update worker heartbeat"""
        if worker_id in self._workers:
            self._workers[worker_id]["last_heartbeat"] = datetime.utcnow()
            if current_jobs is not None:
                self._workers[worker_id]["current_jobs"] = current_jobs
            return True
        return False
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """Get worker statistics"""
        total = len(self._workers)
        online = sum(
            1 for w in self._workers.values()
            if w["status"] == WorkerStatus.ONLINE.value
        )
        busy = sum(
            1 for w in self._workers.values()
            if w["status"] == WorkerStatus.BUSY.value
        )
        
        by_type: Dict[str, int] = {}
        for w in self._workers.values():
            t = w["worker_type"]
            by_type[t] = by_type.get(t, 0) + 1
        
        return {
            "total_workers": total,
            "online": online,
            "busy": busy,
            "by_type": by_type,
        }


class WorkerOrchestrator:
    """
    Worker orchestrator for managing distributed workers.
    Handles worker registration, health checks, telemetry,
    job routing, and processing state management.
    """
    
    def __init__(self, db: AsyncSession, registry: Optional[WorkerRegistry] = None):
        self.db = db
        self.registry = registry or WorkerRegistry()
        self._health_check_interval = 30  # seconds
        self._running = False
    
    # ==================== Worker Management ====================
    
    async def register_worker(
        self,
        worker_id: str,
        worker_type: WorkerType,
        hostname: Optional[str] = None,
        ip_address: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        max_concurrent_jobs: int = 1,
    ) -> Worker:
        """Register a new worker in the database"""
        worker = Worker(
            worker_id=worker_id,
            worker_type=worker_type.value,
            status=WorkerStatus.ONLINE.value,
            hostname=hostname or socket.gethostname(),
            ip_address=ip_address,
            capabilities=capabilities or [],
            max_concurrent_jobs=max_concurrent_jobs,
            started_at=datetime.utcnow(),
            last_heartbeat=datetime.utcnow(),
        )
        
        self.db.add(worker)
        await self.db.commit()
        await self.db.refresh(worker)
        
        # Also register in-memory
        self.registry.register_worker(
            worker_id, worker_type, capabilities or [], hostname, ip_address
        )
        
        return worker
    
    async def unregister_worker(self, worker_id: str) -> bool:
        """Unregister a worker"""
        result = await self.db.execute(
            select(Worker).where(Worker.worker_id == worker_id)
        )
        worker = result.scalar_one_or_none()
        
        if worker:
            worker.status = WorkerStatus.OFFLINE.value
            self.db.add(worker)
            await self.db.commit()
            
            self.registry.unregister_worker(worker_id)
            return True
        
        return False
    
    async def get_worker(self, worker_id: str) -> Optional[Worker]:
        """Get worker by ID"""
        result = await self.db.execute(
            select(Worker).where(Worker.worker_id == worker_id)
        )
        return result.scalar_one_or_none()
    
    async def get_online_workers(
        self,
        worker_type: Optional[WorkerType] = None,
    ) -> List[Worker]:
        """Get all online workers"""
        query = select(Worker).where(Worker.status == WorkerStatus.ONLINE.value)
        
        if worker_type:
            query = query.where(Worker.worker_type == worker_type.value)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_available_worker(
        self,
        worker_type: WorkerType,
        capabilities: Optional[List[str]] = None,
    ) -> Optional[Worker]:
        """Get an available worker for job assignment"""
        workers = await self.get_online_workers(worker_type)
        
        for worker in workers:
            # Check if worker has required capabilities
            if capabilities:
                worker_caps = worker.capabilities or []
                if not all(c in worker_caps for c in capabilities):
                    continue
            
            # Check if worker can accept more jobs
            current_jobs = len(self.registry.get_worker(worker.worker_id or "") or {}).get("current_jobs", [])
            
            if worker.max_concurrent_jobs > len(current_jobs):
                return worker
        
        return None
    
    # ==================== Heartbeat Management ====================
    
    async def process_heartbeat(
        self,
        worker_id: str,
        metrics: Optional[WorkerMetrics] = None,
        current_jobs: Optional[List[str]] = None,
    ) -> bool:
        """Process worker heartbeat"""
        result = await self.db.execute(
            select(Worker).where(Worker.worker_id == worker_id)
        )
        worker = result.scalar_one_or_none()
        
        if not worker:
            return False
        
        worker.last_heartbeat = datetime.utcnow()
        worker.status = WorkerStatus.ONLINE.value if not current_jobs else WorkerStatus.BUSY.value
        
        # Update in-memory registry
        self.registry.update_heartbeat(worker_id, current_jobs)
        
        # Record metrics
        if metrics:
            metric = WorkerMetric(
                worker_id=worker_id,
                cpu_percent=metrics.cpu_percent,
                memory_percent=metrics.memory_percent,
                memory_used_mb=metrics.memory_used_mb,
                memory_available_mb=metrics.memory_available_mb,
                disk_used_mb=metrics.disk_used_mb,
                disk_available_mb=metrics.disk_available_mb,
                jobs_processed=metrics.jobs_processed,
                jobs_failed=metrics.jobs_failed,
                current_jobs=metrics.current_jobs,
            )
            self.db.add(metric)
        
        self.db.add(worker)
        await self.db.commit()
        
        return True
    
    async def check_worker_health(self, worker_id: str) -> WorkerHealth:
        """Check worker health status"""
        result = await self.db.execute(
            select(Worker).where(Worker.worker_id == worker_id)
        )
        worker = result.scalar_one_or_none()
        
        if not worker:
            return WorkerHealth(
                worker_id=worker_id,
                status=WorkerStatus.OFFLINE,
                last_heartbeat=datetime.utcnow(),
                healthy=False,
                error_count=0,
                uptime_seconds=0,
                capabilities=[],
            )
        
        # Check if heartbeat is stale (> 2 minutes)
        is_healthy = True
        if worker.last_heartbeat:
            time_since_heartbeat = (datetime.utcnow() - worker.last_heartbeat).total_seconds()
            is_healthy = time_since_heartbeat < 120
        
        status = WorkerStatus(worker.status)
        
        return WorkerHealth(
            worker_id=worker.worker_id,
            status=status,
            last_heartbeat=worker.last_heartbeat or datetime.utcnow(),
            healthy=is_healthy and status not in (WorkerStatus.ERROR, WorkerStatus.MAINTENANCE),
            error_count=worker.error_count,
            uptime_seconds=worker.uptime,
            capabilities=worker.capabilities or [],
        )
    
    # ==================== Telemetry ====================
    
    async def record_worker_metrics(
        self,
        worker_id: str,
        cpu_percent: float,
        memory_percent: float,
        memory_used_mb: int,
        memory_available_mb: int,
        disk_used_mb: int,
        disk_available_mb: int,
        jobs_processed: int = 0,
        jobs_failed: int = 0,
        current_jobs: Optional[List[str]] = None,
    ) -> WorkerMetric:
        """Record worker metrics snapshot"""
        metric = WorkerMetric(
            worker_id=worker_id,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            memory_available_mb=memory_available_mb,
            disk_used_mb=disk_used_mb,
            disk_available_mb=disk_available_mb,
            jobs_processed=jobs_processed,
            jobs_failed=jobs_failed,
            current_jobs=current_jobs,
        )
        
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        
        return metric
    
    async def get_worker_metrics(
        self,
        worker_id: str,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[WorkerMetric]:
        """Get worker metrics history"""
        query = select(WorkerMetric).where(WorkerMetric.worker_id == worker_id)
        
        if since:
            query = query.where(WorkerMetric.timestamp >= since)
        
        query = query.order_by(WorkerMetric.timestamp.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_mb": memory.used // (1024 * 1024),
            "memory_available_mb": memory.available // (1024 * 1024),
            "disk_used_mb": disk.used // (1024 * 1024),
            "disk_available_mb": disk.free // (1024 * 1024),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    # ==================== Event Logging ====================
    
    async def log_worker_event(
        self,
        worker_id: str,
        event_type: str,
        message: str,
        severity: str = "info",
        job_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> WorkerEvent:
        """Log a worker event"""
        event = WorkerEvent(
            worker_id=worker_id,
            event_type=event_type,
            severity=severity,
            message=message,
            job_id=job_id,
            metadata=metadata,
        )
        
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        
        return event
    
    # ==================== Processing State ====================
    
    async def create_processing_state(
        self,
        job_id: str,
        state_type: str,
        state_data: Optional[Dict] = None,
        total_items: int = 0,
        expires_at: Optional[datetime] = None,
    ) -> ProcessingState:
        """Create a processing state for resume capability"""
        state = ProcessingState(
            job_id=job_id,
            state_type=state_type,
            state_data=state_data,
            total_items=total_items,
            started_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            expires_at=expires_at,
        )
        
        self.db.add(state)
        await self.db.commit()
        await self.db.refresh(state)
        
        return state
    
    async def update_processing_state(
        self,
        job_id: str,
        progress: Optional[float] = None,
        processed_items: Optional[int] = None,
        state_data: Optional[Dict] = None,
    ) -> Optional[ProcessingState]:
        """Update processing state"""
        result = await self.db.execute(
            select(ProcessingState).where(ProcessingState.job_id == job_id)
        )
        state = result.scalar_one_or_none()
        
        if not state:
            return None
        
        if progress is not None:
            state.progress = progress
        if processed_items is not None:
            state.processed_items = processed_items
        if state_data is not None:
            state.state_data = state_data
        
        state.updated_at = datetime.utcnow()
        
        self.db.add(state)
        await self.db.commit()
        await self.db.refresh(state)
        
        return state
    
    async def get_processing_state(self, job_id: str) -> Optional[ProcessingState]:
        """Get processing state"""
        result = await self.db.execute(
            select(ProcessingState).where(ProcessingState.job_id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def cleanup_expired_states(self) -> int:
        """Clean up expired processing states"""
        result = await self.db.execute(
            select(ProcessingState).where(
                ProcessingState.expires_at < datetime.utcnow()
            )
        )
        states = result.scalars().all()
        
        for state in states:
            await self.db.delete(state)
        
        await self.db.commit()
        
        return len(states)
    
    # ==================== Runtime Logging ====================
    
    async def log_runtime(
        self,
        worker_id: str,
        message: str,
        log_level: str = "info",
        job_id: Optional[str] = None,
        task_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> RuntimeLog:
        """Log a runtime message"""
        log = RuntimeLog(
            worker_id=worker_id,
            log_level=log_level,
            message=message,
            job_id=job_id,
            task_id=task_id,
            trace_id=trace_id,
            metadata=metadata,
        )
        
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        
        return log
    
    # ==================== Health Monitoring ====================
    
    async def get_orchestrator_health(self) -> Dict[str, Any]:
        """Get overall orchestrator health"""
        total_workers = await self.db.execute(select(func.count(Worker.id)))
        total = total_workers.scalar() or 0
        
        online_workers = await self.db.execute(
            select(func.count(Worker.id)).where(
                Worker.status == WorkerStatus.ONLINE.value
            )
        )
        online = online_workers.scalar() or 0
        
        return {
            "status": "healthy" if online > 0 else "degraded",
            "total_workers": total,
            "online_workers": online,
            "timestamp": datetime.utcnow().isoformat(),
        }