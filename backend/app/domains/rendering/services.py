"""
Render Graph Engine Services - Distributed render orchestration
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from uuid import UUID
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from .models import (
    RenderStatus,
    RenderPriority,
    RenderNodeType,
    RenderGraph,
    RenderNode,
    RenderJob,
    RenderPreset,
)

logger = logging.getLogger(__name__)


class NodeState(Enum):
    """Node execution states"""
    PENDING = "pending"
    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionContext:
    """Context for node execution"""
    job_id: str
    worker_id: str
    progress_callback: Optional[callable] = None
    cancel_event: Optional[asyncio.Event] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of node execution"""
    node_id: UUID
    success: bool
    output_data: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    error: Optional[str] = None


class RenderGraphEngine:
    """
    Distributed render graph engine.
    Handles render graphs, node execution, dependency resolution,
    distributed render workers, retries, cancellation, monitoring,
    and export presets.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._active_jobs: Dict[str, ExecutionContext] = {}
        self._node_results: Dict[str, Dict[str, Any]] = {}
    
    # ==================== Graph Operations ====================
    
    async def create_graph(
        self,
        name: str,
        description: Optional[str] = None,
        nodes: Optional[List[Dict]] = None,
        edges: Optional[List[Dict]] = None,
        output_format: str = "mp4",
        output_resolution: str = "1920x1080",
        frame_rate: float = 30.0,
        bitrate: int = 10_000_000,
    ) -> RenderGraph:
        """Create a new render graph"""
        graph = RenderGraph(
            name=name,
            description=description,
            nodes=nodes or [],
            edges=edges or [],
            output_format=output_format,
            output_resolution=output_resolution,
            frame_rate=frame_rate,
            bitrate=bitrate,
        )
        
        self.db.add(graph)
        await self.db.commit()
        await self.db.refresh(graph)
        
        return graph
    
    async def get_graph(self, graph_id: UUID) -> Optional[RenderGraph]:
        """Get graph by ID"""
        result = await self.db.execute(
            select(RenderGraph).where(RenderGraph.id == graph_id)
        )
        return result.scalar_one_or_none()
    
    async def update_graph(
        self,
        graph: RenderGraph,
        **kwargs,
    ) -> RenderGraph:
        """Update graph properties"""
        for key, value in kwargs.items():
            if hasattr(graph, key):
                setattr(graph, key, value)
        
        self.db.add(graph)
        await self.db.commit()
        await self.db.refresh(graph)
        
        return graph
    
    async def clone_graph(
        self,
        graph: RenderGraph,
        new_name: Optional[str] = None,
    ) -> RenderGraph:
        """Clone an existing graph"""
        cloned = RenderGraph(
            name=new_name or f"{graph.name} (Copy)",
            description=graph.description,
            nodes=graph.nodes,
            edges=graph.edges,
            output_format=graph.output_format,
            output_resolution=graph.output_resolution,
            frame_rate=graph.frame_rate,
            bitrate=graph.bitrate,
            preset_name=graph.preset_name,
            preset_data=graph.preset_data,
            parent_graph_id=graph.id,
            version=1,
        )
        
        self.db.add(cloned)
        await self.db.commit()
        await self.db.refresh(cloned)
        
        return cloned
    
    # ==================== Node Operations ====================
    
    async def add_node(
        self,
        graph: RenderGraph,
        name: str,
        node_type: RenderNodeType,
        operation: str,
        parameters: Optional[Dict] = None,
        position: Optional[Tuple[float, float]] = None,
    ) -> RenderNode:
        """Add a node to graph"""
        node = RenderNode(
            graph_id=graph.id,
            name=name,
            node_type=node_type.value,
            operation=operation,
            parameters=parameters or {},
            position_x=position[0] if position else 0.0,
            position_y=position[1] if position else 0.0,
        )
        
        self.db.add(node)
        await self.db.commit()
        await self.db.refresh(node)
        
        # Update graph nodes list
        if graph.nodes is None:
            graph.nodes = []
        
        graph.nodes.append({
            "id": str(node.id),
            "name": name,
            "type": node_type.value,
            "operation": operation,
        })
        
        await self.db.commit()
        
        return node
    
    async def remove_node(self, node: RenderNode) -> None:
        """Remove node from graph"""
        await self.db.delete(node)
        await self.db.commit()
    
    async def update_node(
        self,
        node: RenderNode,
        **kwargs,
    ) -> RenderNode:
        """Update node properties"""
        for key, value in kwargs.items():
            if hasattr(node, key):
                setattr(node, key, value)
        
        self.db.add(node)
        await self.db.commit()
        await self.db.refresh(node)
        
        return node
    
    # ==================== Dependency Resolution ====================
    
    async def resolve_dependencies(
        self,
        graph: RenderGraph,
    ) -> List[List[UUID]]:
        """
        Resolve node dependencies and return execution order.
        Uses topological sort with Kahn's algorithm.
        """
        if not graph.nodes or not graph.edges:
            return [[n["id"] for n in graph.nodes]]
        
        # Build adjacency list
        adj: Dict[UUID, List[UUID]] = {}
        in_degree: Dict[UUID, int] = {}
        
        nodes_by_id = {n["id"]: n for n in graph.nodes}
        
        # Initialize
        for node in graph.nodes:
            node_id = node["id"]
            adj[node_id] = []
            in_degree[node_id] = 0
        
        # Build graph
        for edge in graph.edges:
            if "source" in edge and "target" in edge:
                source = edge["source"]
                target = edge["target"]
                if source in adj and target in adj:
                    adj[source].append(target)
                    in_degree[target] += 1
        
        # Topological sort
        queue = [n for n, d in in_degree.items() if d == 0]
        result: List[List[UUID]] = []
        current_level = []
        
        while queue:
            current_level = []
            next_queue = []
            
            for node_id in queue:
                current_level.append(UUID(node_id))
                
                for neighbor in adj[node_id]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_queue.append(neighbor)
            
            result.append(current_level)
            queue = next_queue
        
        # Check for cycles
        if sum(in_degree.values()) > 0:
            raise ValueError("Graph contains cycles")
        
        return result
    
    # ==================== Job Operations ====================
    
    async def create_job(
        self,
        name: str,
        job_type: str,
        graph_id: Optional[UUID] = None,
        timeline_id: Optional[UUID] = None,
        priority: RenderPriority = RenderPriority.NORMAL,
        settings: Optional[Dict] = None,
    ) -> RenderJob:
        """Create a new render job"""
        job = RenderJob(
            name=name,
            job_type=job_type,
            graph_id=graph_id,
            timeline_id=timeline_id,
            status=RenderStatus.QUEUED.value,
            priority=priority.value,
            queued_at=datetime.utcnow(),
            settings=settings or {},
        )
        
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        
        return job
    
    async def get_job(self, job_id: UUID) -> Optional[RenderJob]:
        """Get job by ID"""
        result = await self.db.execute(
            select(RenderJob).where(RenderJob.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def get_jobs_by_status(
        self,
        status: RenderStatus,
        limit: int = 100,
    ) -> List[RenderJob]:
        """Get jobs by status"""
        result = await self.db.execute(
            select(RenderJob)
            .where(RenderJob.status == status.value)
            .order_by(RenderJob.queued_at)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_jobs_by_worker(
        self,
        worker_id: str,
        limit: int = 100,
    ) -> List[RenderJob]:
        """Get jobs assigned to a worker"""
        result = await self.db.execute(
            select(RenderJob)
            .where(RenderJob.worker_id == worker_id)
            .order_by(RenderJob.queued_at)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def update_job_status(
        self,
        job: RenderJob,
        status: RenderStatus,
        **kwargs,
    ) -> RenderJob:
        """Update job status and metadata"""
        job.status = status.value
        
        if status == RenderStatus.RENDERING:
            job.started_at = datetime.utcnow()
        elif status in (RenderStatus.COMPLETED, RenderStatus.FAILED):
            job.completed_at = datetime.utcnow()
        
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)
        
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        
        return job
    
    async def cancel_job(self, job: RenderJob) -> RenderJob:
        """Cancel a job"""
        return await self.update_job_status(job, RenderStatus.CANCELLED)
    
    async def retry_job(self, job: RenderJob) -> RenderJob:
        """Retry a failed job"""
        if job.retry_count >= job.max_retries:
            raise ValueError("Max retries exceeded")
        
        job.retry_count += 1
        return await self.update_job_status(job, RenderStatus.QUEUED)
    
    # ==================== Execution ====================
    
    async def execute_graph(
        self,
        job: RenderJob,
        worker_id: str,
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """Execute a render graph"""
        context = ExecutionContext(
            job_id=str(job.id),
            worker_id=worker_id,
            progress_callback=progress_callback,
            cancel_event=asyncio.Event(),
        )
        self._active_jobs[str(job.id)] = context
        
        try:
            # Get graph
            if job.graph_id:
                result = await self.db.execute(
                    select(RenderGraph).where(RenderGraph.id == job.graph_id)
                )
                graph = result.scalar_one_or_none()
            else:
                graph = None
            
            # Update job status
            await self.update_job_status(job, RenderStatus.RENDERING, worker_id=worker_id)
            
            if not graph:
                await self.update_job_status(
                    job, RenderStatus.FAILED,
                    error_message="Graph not found"
                )
                return {"error": "Graph not found"}
            
            # Resolve dependencies
            execution_order = await self.resolve_dependencies(graph)
            
            # Execute nodes in order
            total_nodes = sum(len(level) for level in execution_order)
            completed_nodes = 0
            
            for level_idx, level in enumerate(execution_order):
                level_results = await asyncio.gather(
                    *[self._execute_node(job, node_id, context) for node_id in level],
                    return_exceptions=True,
                )
                
                for node_result in level_results:
                    if isinstance(node_result, Exception):
                        logger.error(f"Node execution error: {node_result}")
                    completed_nodes += 1
                    
                    if progress_callback:
                        progress = (completed_nodes / total_nodes) * 100
                        await progress_callback(progress)
            
            # Update job
            await self.update_job_status(job, RenderStatus.COMPLETED)
            
            return {
                "success": True,
                "job_id": str(job.id),
                "nodes_executed": total_nodes,
            }
            
        except asyncio.CancelledError:
            await self.update_job_status(job, RenderStatus.CANCELLED)
            return {"error": "Job cancelled"}
            
        except Exception as e:
            logger.error(f"Graph execution error: {e}")
            await self.update_job_status(
                job, RenderStatus.FAILED,
                error_message=str(e)
            )
            return {"error": str(e)}
            
        finally:
            self._active_jobs.pop(str(job.id), None)
    
    async def _execute_node(
        self,
        job: RenderJob,
        node_id: UUID,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """Execute a single node"""
        start_time = datetime.utcnow()
        
        try:
            # Get node
            result = await self.db.execute(
                select(RenderNode).where(RenderNode.id == node_id)
            )
            node = result.scalar_one_or_none()
            
            if not node:
                return ExecutionResult(
                    node_id=node_id,
                    success=False,
                    error="Node not found",
                )
            
            # Simulate node execution (actual implementation would use FFmpeg, etc.)
            await asyncio.sleep(0.1)  # Placeholder
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ExecutionResult(
                node_id=node_id,
                success=True,
                output_data={"status": "completed"},
                execution_time=execution_time,
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return ExecutionResult(
                node_id=node_id,
                success=False,
                error=str(e),
                execution_time=execution_time,
            )
    
    async def cancel_execution(self, job_id: str) -> bool:
        """Cancel an ongoing execution"""
        context = self._active_jobs.get(job_id)
        if context and context.cancel_event:
            context.cancel_event.set()
            return True
        return False
    
    # ==================== Presets ====================
    
    async def create_preset(
        self,
        name: str,
        category: str,
        format: str,
        codec: str,
        container: str,
        resolution: str,
        frame_rate: float,
        bitrate: Optional[int] = None,
        parameters: Optional[Dict] = None,
        is_builtin: bool = False,
    ) -> RenderPreset:
        """Create a render preset"""
        preset = RenderPreset(
            name=name,
            category=category,
            format=format,
            codec=codec,
            container=container,
            resolution=resolution,
            frame_rate=frame_rate,
            bitrate=bitrate,
            parameters=parameters,
            is_builtin=is_builtin,
        )
        
        self.db.add(preset)
        await self.db.commit()
        await self.db.refresh(preset)
        
        return preset
    
    async def get_presets_by_category(
        self,
        category: str,
    ) -> List[RenderPreset]:
        """Get presets by category"""
        result = await self.db.execute(
            select(RenderPreset)
            .where(RenderPreset.category == category)
            .order_by(RenderPreset.usage_count.desc())
        )
        return list(result.scalars().all())
    
    async def apply_preset(
        self,
        graph: RenderGraph,
        preset: RenderPreset,
    ) -> RenderGraph:
        """Apply preset to graph"""
        graph.output_format = preset.format
        graph.output_resolution = preset.resolution
        graph.frame_rate = preset.frame_rate
        graph.bitrate = preset.bitrate or graph.bitrate
        graph.preset_name = preset.name
        graph.preset_data = preset.parameters
        
        # Increment usage
        preset.usage_count += 1
        
        self.db.add(graph)
        self.db.add(preset)
        await self.db.commit()
        await self.db.refresh(graph)
        
        return graph
    
    # ==================== Monitoring ====================
    
    async def get_job_progress(
        self,
        job_id: UUID,
    ) -> Optional[Dict[str, Any]]:
        """Get job progress"""
        job = await self.get_job(job_id)
        if not job:
            return None
        
        return {
            "job_id": str(job.id),
            "status": job.status,
            "progress": job.progress,
            "total_frames": job.total_frames,
            "processed_frames": job.processed_frames,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "estimated_remaining": self._estimate_remaining(job),
        }
    
    def _estimate_remaining(self, job: RenderJob) -> Optional[float]:
        """Estimate remaining time in seconds"""
        if job.status == RenderStatus.COMPLETED:
            return 0.0
        
        if job.started_at and job.total_frames > 0:
            elapsed = (datetime.utcnow() - job.started_at).total_seconds()
            if job.processed_frames > 0:
                time_per_frame = elapsed / job.processed_frames
                remaining_frames = job.total_frames - job.processed_frames
                return time_per_frame * remaining_frames
        
        return None
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        stats = {}
        
        for status in RenderStatus:
            result = await self.db.execute(
                select(RenderJob).where(RenderJob.status == status.value)
            )
            stats[status.value] = len(list(result.scalars().all()))
        
        return {
            "by_status": stats,
            "total": sum(stats.values()),
        }