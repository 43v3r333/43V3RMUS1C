"""
Runtime Services - Centralized runtime orchestration
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Set, TypeVar
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_

from .models import (
    RuntimeStatus,
    SessionStatus,
    NodeStatus,
    ExecutionMode,
    ExecutionContext,
    NodeResult,
    RuntimeSession,
    WorkflowGraph,
    WorkflowNode,
    WorkflowExecution,
    NodeExecution,
    RuntimeEventLog,
    RuntimeMetric,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class OrchestrationEvent:
    """Event for runtime orchestration"""
    event_id: str
    event_type: str
    source: str
    timestamp: datetime
    data: Dict[str, Any]
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None


class RuntimeCoordinator:
    """
    Centralized runtime coordinator.
    Manages runtime sessions, coordinates workers, and propagates state.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._sessions: Dict[str, RuntimeSession] = {}
        self._active_workflows: Dict[str, WorkflowExecution] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize the runtime coordinator"""
        self._running = True
        logger.info("RuntimeCoordinator initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the runtime coordinator"""
        self._running = False
        logger.info("RuntimeCoordinator shutdown")
    
    # ==================== Session Management ====================
    
    async def create_session(
        self,
        name: str,
        session_type: str,
        owner_id: Optional[UUID] = None,
        config: Optional[Dict[str, Any]] = None,
        capabilities: Optional[List[str]] = None,
    ) -> RuntimeSession:
        """Create a new runtime session"""
        session = RuntimeSession(
            name=name,
            session_type=session_type,
            status=RuntimeStatus.INITIALIZING.value,
            config=config or {},
            capabilities=capabilities or [],
            owner_id=owner_id,
            started_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        self._sessions[str(session.id)] = session
        
        await self._log_event(
            session_id=str(session.id),
            event_type="session_created",
            event_category="runtime",
            source="coordinator",
            severity="info",
        )
        
        return session
    
    async def get_session(self, session_id: UUID) -> Optional[RuntimeSession]:
        """Get session by ID"""
        result = await self.db.execute(
            select(RuntimeSession).where(RuntimeSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if session:
            self._sessions[str(session_id)] = session
        
        return session
    
    async def update_session_status(
        self,
        session: RuntimeSession,
        status: RuntimeStatus,
        error: Optional[str] = None,
    ) -> RuntimeSession:
        """Update session status"""
        session.status = status.value
        session.last_activity = datetime.utcnow()
        
        if status in (RuntimeStatus.STOPPED, RuntimeStatus.ERROR):
            session.ended_at = datetime.utcnow()
        
        if error:
            session.error_count += 1
            session.last_error = error
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        await self._log_event(
            session_id=str(session.id),
            event_type="session_status_changed",
            event_category="runtime",
            source="coordinator",
            severity="warning" if status == RuntimeStatus.ERROR else "info",
            data={"status": status.value, "error": error},
        )
        
        return session
    
    async def list_sessions(
        self,
        status: Optional[RuntimeStatus] = None,
        owner_id: Optional[UUID] = None,
        limit: int = 100,
    ) -> List[RuntimeSession]:
        """List runtime sessions"""
        query = select(RuntimeSession)
        
        if status:
            query = query.where(RuntimeSession.status == status.value)
        if owner_id:
            query = query.where(RuntimeSession.owner_id == owner_id)
        
        query = query.order_by(RuntimeSession.started_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_session_stats(self, session_id: UUID) -> Dict[str, Any]:
        """Get session statistics"""
        session = await self.get_session(session_id)
        if not session:
            return {}
        
        # Get active executions
        result = await self.db.execute(
            select(WorkflowExecution)
            .where(
                WorkflowExecution.session_id == session_id,
                WorkflowExecution.status == NodeStatus.RUNNING.value,
            )
        )
        active_executions = list(result.scalars().all())
        
        return {
            "session_id": str(session.id),
            "status": session.status,
            "active_executions": len(active_executions),
            "total_executions": session.total_executions,
            "events_processed": session.events_processed,
            "events_failed": session.events_failed,
            "average_execution_time": session.average_execution_time,
            "uptime": (datetime.utcnow() - session.started_at).total_seconds() if session.started_at else 0,
        }
    
    # ==================== Event Handling ====================
    
    def register_handler(
        self,
        event_type: str,
        handler: Callable,
    ) -> None:
        """Register an event handler"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    def unregister_handler(
        self,
        event_type: str,
        handler: Callable,
    ) -> None:
        """Unregister an event handler"""
        if event_type in self._event_handlers:
            self._event_handlers[event_type] = [
                h for h in self._event_handlers[event_type] if h != handler
            ]
    
    async def emit_event(
        self,
        event: OrchestrationEvent,
    ) -> None:
        """Emit an orchestration event"""
        # Log event
        await self._log_event(
            session_id=event.source,
            event_type=event.event_type,
            event_category="orchestration",
            source=event.source,
            correlation_id=event.correlation_id,
            trace_id=event.trace_id,
            data=event.data,
        )
        
        # Invoke handlers
        handlers = self._event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Event handler error: {e}")
        
        # Update session metrics
        if event.source in self._sessions:
            session = self._sessions[event.source]
            session.events_processed += 1
            session.last_activity = datetime.utcnow()
    
    async def _log_event(
        self,
        session_id: str,
        event_type: str,
        event_category: str,
        source: str,
        severity: str = "info",
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """Log an event to the database"""
        log = RuntimeEventLog(
            session_id=session_id,
            event_type=event_type,
            event_category=event_category,
            source=source,
            severity=severity,
            correlation_id=correlation_id,
            trace_id=trace_id,
            data=data,
            user_id=user_id,
        )
        
        self.db.add(log)
        await self.db.commit()
    
    # ==================== State Propagation ====================
    
    async def propagate_state(
        self,
        session_id: UUID,
        state_type: str,
        state_data: Dict[str, Any],
    ) -> None:
        """Propagate state to all interested parties"""
        session = await self.get_session(session_id)
        if not session:
            return
        
        event = OrchestrationEvent(
            event_id=str(uuid4()),
            event_type="state_propagated",
            source=str(session_id),
            timestamp=datetime.utcnow(),
            data={
                "state_type": state_type,
                "state_data": state_data,
            },
        )
        
        await self.emit_event(event)
    
    # ==================== Health & Metrics ====================
    
    async def record_metric(
        self,
        session_id: str,
        metric_type: str,
        value: float,
        unit: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> RuntimeMetric:
        """Record a runtime metric"""
        metric = RuntimeMetric(
            session_id=session_id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            tags=tags,
        )
        
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        
        return metric
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get overall runtime health status"""
        total_sessions = len(self._sessions)
        active_sessions = sum(
            1 for s in self._sessions.values()
            if s.status == RuntimeStatus.RUNNING.value
        )
        
        return {
            "status": "healthy" if active_sessions > 0 else "idle",
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "coordinator_running": self._running,
            "timestamp": datetime.utcnow().isoformat(),
        }


class ExecutionManager:
    """
    Workflow execution manager.
    Handles workflow graph execution, node orchestration, and result aggregation.
    """
    
    def __init__(self, db: AsyncSession, coordinator: RuntimeCoordinator):
        self.db = db
        self.coordinator = coordinator
        self._execution_handlers: Dict[str, Callable] = {}
        self._node_handlers: Dict[str, Callable] = {}
    
    # ==================== Workflow Execution ====================
    
    async def create_execution(
        self,
        graph_id: UUID,
        session_id: Optional[UUID] = None,
        owner_id: Optional[UUID] = None,
        input_data: Optional[Dict[str, Any]] = None,
        execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL,
    ) -> WorkflowExecution:
        """Create a new workflow execution"""
        execution = WorkflowExecution(
            graph_id=graph_id,
            session_id=session_id,
            status=NodeStatus.PENDING.value,
            execution_mode=execution_mode.value,
            input_data=input_data,
            owner_id=owner_id,
            queued_at=datetime.utcnow(),
            correlation_id=str(uuid4()),
            trace_id=str(uuid4()),
        )
        
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        
        # Update session stats
        if session_id:
            session = await self.coordinator.get_session(session_id)
            if session:
                session.total_executions += 1
                self.db.add(session)
                await self.db.commit()
        
        return execution
    
    async def execute_workflow(
        self,
        execution: WorkflowExecution,
        context: Optional[ExecutionContext] = None,
    ) -> WorkflowExecution:
        """Execute a workflow graph"""
        try:
            # Update status
            execution.status = NodeStatus.RUNNING.value
            execution.started_at = datetime.utcnow()
            self.db.add(execution)
            await self.db.commit()
            
            # Get graph
            result = await self.db.execute(
                select(WorkflowGraph).where(WorkflowGraph.id == execution.graph_id)
            )
            graph = result.scalar_one_or_none()
            
            if not graph:
                raise ValueError(f"Graph {execution.graph_id} not found")
            
            # Resolve execution order
            execution_order = await self._resolve_execution_order(graph)
            execution.total_nodes = len(execution_order)
            
            # Execute nodes
            node_results: Dict[str, NodeResult] = {}
            context = context or ExecutionContext(
                session_id=str(execution.session_id) if execution.session_id else "",
                workflow_id=str(execution.id),
            )
            
            for batch in execution_order:
                if execution_mode := ExecutionMode(graph.execution_mode):
                    if execution_mode == ExecutionMode.PARALLEL:
                        # Execute batch in parallel
                        results = await asyncio.gather(
                            *[self._execute_node(execution, node_id, node_results, context) for node_id in batch],
                            return_exceptions=True,
                        )
                        for node_id, result in zip(batch, results):
                            if isinstance(result, Exception):
                                node_results[node_id] = NodeResult(
                                    node_id=node_id,
                                    status=NodeStatus.FAILED,
                                    error=str(result),
                                )
                            elif isinstance(result, NodeResult):
                                node_results[node_id] = result
                    else:
                        # Execute sequentially
                        for node_id in batch:
                            result = await self._execute_node(execution, node_id, node_results, context)
                            node_results[node_id] = result
                
                # Update progress
                execution.completed_nodes = sum(
                    1 for r in node_results.values()
                    if r.status in (NodeStatus.COMPLETED, NodeStatus.FAILED, NodeStatus.SKIPPED)
                )
                execution.failed_nodes = sum(
                    1 for r in node_results.values()
                    if r.status == NodeStatus.FAILED
                )
                self.db.add(execution)
                await self.db.commit()
            
            # Finalize
            if execution.failed_nodes > 0:
                execution.status = NodeStatus.FAILED.value
                execution.error_message = f"{execution.failed_nodes} nodes failed"
            else:
                execution.status = NodeStatus.COMPLETED.value
            
            execution.completed_at = datetime.utcnow()
            execution.output_data = {
                "node_results": {k: v.__dict__ for k, v in node_results.items()}
            }
            
            self.db.add(execution)
            await self.db.commit()
            
            return execution
            
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            execution.status = NodeStatus.FAILED.value
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            self.db.add(execution)
            await self.db.commit()
            raise
    
    async def _resolve_execution_order(
        self,
        graph: WorkflowGraph,
    ) -> List[List[str]]:
        """Resolve node execution order using topological sort"""
        nodes = graph.nodes or []
        edges = graph.edges or []
        
        # Build adjacency and in-degree
        node_ids = [n["id"] for n in nodes]
        adj: Dict[str, List[str]] = {nid: [] for nid in node_ids}
        in_degree: Dict[str, int] = {nid: 0 for nid in node_ids}
        
        for edge in edges:
            if "source" in edge and "target" in edge:
                adj[edge["source"]].append(edge["target"])
                in_degree[edge["target"]] += 1
        
        # Topological sort with levels
        order: List[List[str]] = []
        remaining = set(node_ids)
        
        while remaining:
            # Find nodes with no dependencies
            ready = [
                nid for nid in remaining
                if in_degree.get(nid, 0) == 0
            ]
            
            if not ready:
                raise ValueError("Graph contains cycles")
            
            order.append(ready)
            
            # Remove ready nodes and update degrees
            for node_id in ready:
                remaining.remove(node_id)
                for neighbor in adj.get(node_id, []):
                    if neighbor in in_degree:
                        in_degree[neighbor] -= 1
        
        return order
    
    async def _execute_node(
        self,
        execution: WorkflowExecution,
        node_id: str,
        previous_results: Dict[str, NodeResult],
        context: ExecutionContext,
    ) -> NodeResult:
        """Execute a single workflow node"""
        # Get node
        result = await self.db.execute(
            select(WorkflowNode)
            .where(WorkflowNode.id == UUID(node_id))
        )
        node = result.scalar_one_or_none()
        
        if not node:
            return NodeResult(
                node_id=node_id,
                status=NodeStatus.FAILED,
                error="Node not found",
            )
        
        start_time = datetime.utcnow()
        
        try:
            # Check conditions
            if node.conditions:
                should_execute = await self._evaluate_conditions(
                    node.conditions, previous_results
                )
                if not should_execute:
                    return NodeResult(
                        node_id=node_id,
                        status=NodeStatus.SKIPPED,
                        start_time=start_time,
                        end_time=datetime.utcnow(),
                        execution_time=0.0,
                    )
            
            # Get handler
            handler = self._node_handlers.get(node.node_type)
            
            if not handler:
                raise ValueError(f"No handler for node type: {node.node_type}")
            
            # Build input from previous results
            input_data = {
                "node_config": node.config,
                "execution_input": execution.input_data,
                "previous_results": {
                    k: v.output for k, v in previous_results.items()
                },
            }
            
            # Execute with timeout
            if node.timeout_seconds:
                result_data = await asyncio.wait_for(
                    handler(input_data, context),
                    timeout=node.timeout_seconds,
                )
            else:
                result_data = await handler(input_data, context)
            
            end_time = datetime.utcnow()
            
            return NodeResult(
                node_id=node_id,
                status=NodeStatus.COMPLETED,
                output=result_data or {},
                start_time=start_time,
                end_time=end_time,
                execution_time=(end_time - start_time).total_seconds(),
            )
            
        except asyncio.TimeoutError:
            return NodeResult(
                node_id=node_id,
                status=NodeStatus.FAILED,
                error=f"Node timed out after {node.timeout_seconds}s",
                start_time=start_time,
                end_time=datetime.utcnow(),
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
            )
            
        except Exception as e:
            logger.error(f"Node execution error: {e}")
            return NodeResult(
                node_id=node_id,
                status=NodeStatus.FAILED,
                error=str(e),
                start_time=start_time,
                end_time=datetime.utcnow(),
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
            )
    
    async def _evaluate_conditions(
        self,
        conditions: List[Dict[str, Any]],
        results: Dict[str, NodeResult],
    ) -> bool:
        """Evaluate node conditions"""
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")
            
            # Get value from results
            context_value = None
            if field.startswith("results."):
                node_id = field.replace("results.", "")
                if node_id in results:
                    context_value = results[node_id].output.get(field.split(".")[-1])
            elif field.startswith("output."):
                output_key = field.replace("output.", "")
                context_value = results.get(output_key)
            
            # Evaluate
            if operator == "equals" and context_value != value:
                return False
            elif operator == "not_equals" and context_value == value:
                return False
            elif operator == "exists" and context_value is None:
                return False
            elif operator == "not_exists" and context_value is not None:
                return False
        
        return True
    
    async def add_node(
        self,
        graph_id: UUID,
        name: str,
        node_type: str,
        config: Optional[Dict[str, Any]] = None,
        depends_on: Optional[List[str]] = None,
    ) -> WorkflowNode:
        """Add a node to a workflow graph"""
        node = WorkflowNode(
            graph_id=graph_id,
            name=name,
            node_type=node_type,
            config=config or {},
            depends_on=depends_on or [],
        )
        
        self.db.add(node)
        await self.db.commit()
        await self.db.refresh(node)
        
        return node

    async def create_workflow(
        self,
        name: str,
        description: Optional[str] = None,
        nodes: Optional[List[Dict[str, Any]]] = None,
        edges: Optional[List[Dict[str, Any]]] = None,
        execution_mode: Optional[ExecutionMode] = None,
        max_parallelism: Optional[int] = None,
    ) -> WorkflowGraph:
        """Create a new workflow graph"""
        graph = WorkflowGraph(
            name=name,
            description=description,
            nodes=nodes or [],
            edges=edges or [],
            execution_mode=execution_mode.value if execution_mode else ExecutionMode.SEQUENTIAL.value,
            max_parallelism=max_parallelism or 1,
        )
        
        self.db.add(graph)
        await self.db.commit()
        await self.db.refresh(graph)
        
        # Create workflow nodes for each node in the graph
        for node_data in (nodes or []):
            await self.add_node(
                graph_id=graph.id,
                name=node_data.get("name", node_data.get("id", "unnamed")),
                node_type=node_data.get("type", "process"),
                config={},
                depends_on=[],
            )
        
        return graph

    def register_node_handler(self, node_type: str, handler: Callable) -> None:
        """Register a node execution handler"""
        self._node_handlers[node_type] = handler
    
    # ==================== Execution Control ====================
    
    async def cancel_execution(
        self,
        execution: WorkflowExecution,
    ) -> WorkflowExecution:
        """Cancel a running execution"""
        execution.status = NodeStatus.CANCELLED.value
        execution.completed_at = datetime.utcnow()
        
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        
        return execution
    
    async def retry_execution(
        self,
        execution: WorkflowExecution,
    ) -> WorkflowExecution:
        """Retry a failed execution"""
        execution.status = NodeStatus.PENDING.value
        execution.retry_count += 1
        execution.error_message = None
        
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        
        return execution
    
    async def get_execution(self, execution_id: UUID) -> Optional[WorkflowExecution]:
        """Get execution by ID"""
        result = await self.db.execute(
            select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
        )
        return result.scalar_one_or_none()


class WorkflowDispatcher:
    """
    Workflow dispatcher.
    Handles workflow routing, scheduling, and triggering.
    """
    
    def __init__(self, db: AsyncSession, executor: ExecutionManager):
        self.db = db
        self.executor = executor
        self._triggers: Dict[str, Callable] = {}
        self._scheduled_workflows: Dict[str, asyncio.Task] = {}
    
    def register_trigger(
        self,
        trigger_type: str,
        handler: Callable,
    ) -> None:
        """Register a workflow trigger"""
        self._triggers[trigger_type] = handler
    
    async def dispatch(
        self,
        graph_id: UUID,
        trigger_type: str,
        input_data: Optional[Dict[str, Any]] = None,
        session_id: Optional[UUID] = None,
        owner_id: Optional[UUID] = None,
    ) -> WorkflowExecution:
        """Dispatch a workflow"""
        trigger = self._triggers.get(trigger_type)
        
        if trigger:
            input_data = await trigger(input_data) or input_data
        
        # Create execution
        execution = await self.executor.create_execution(
            graph_id=graph_id,
            session_id=session_id,
            owner_id=owner_id,
            input_data=input_data,
        )
        
        # Start execution
        context = ExecutionContext(
            session_id=str(session_id) if session_id else "",
            workflow_id=str(execution.id),
        )
        
        await self.executor.execute_workflow(execution, context)
        
        return execution
    
    async def schedule_workflow(
        self,
        schedule_id: str,
        graph_id: UUID,
        cron_expression: str,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Schedule a workflow for periodic execution"""
        # Parse cron and schedule
        # This is a placeholder - actual implementation would use croniter
        pass
    
    async def cancel_scheduled(
        self,
        schedule_id: str,
    ) -> None:
        """Cancel a scheduled workflow"""
        if schedule_id in self._scheduled_workflows:
            self._scheduled_workflows[schedule_id].cancel()
            del self._scheduled_workflows[schedule_id]