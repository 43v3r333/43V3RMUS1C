"""
Distributed Runtime Services - Context propagation and execution continuity.

Provides:
- Distributed context propagation
- Orchestration continuity engine
- Runtime lineage synchronization
- Semantic execution tracking
- Execution identity propagation
"""
import asyncio
import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Callable
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_

from .models import (
    DistributedContextState,
    RuntimePropagationSession,
    OrchestrationLineageGraph,
    ExecutionIdentity,
    ContextPropagationPolicy,
    RuntimeLineageNode,
    CrossServiceCoordination,
    ExecutionSnapshot,
    ContextScope,
    PropagationStatus,
    ContinuityState,
    SyncMode,
)


logger = logging.getLogger(__name__)


@dataclass
class ContextPropagationResult:
    """Result of context propagation"""
    success: bool
    context_id: str
    propagated_to: List[str]
    failed_nodes: List[str]
    latency_ms: float
    error: Optional[str] = None


@dataclass
class LineageNode:
    """Lineage node representation"""
    node_id: str
    execution_id: str
    node_type: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    dependencies: List[str] = field(default_factory=list)


class DistributedContextManager:
    """Manages distributed context across execution nodes"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._contexts: Dict[str, DistributedContextState] = {}
        self._policies: Dict[str, ContextPropagationPolicy] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize distributed context manager"""
        await self._load_contexts()
        await self._load_policies()
        self._running = True
        logger.info("DistributedContextManager initialized")
    
    async def shutdown(self) -> None:
        """Shutdown distributed context manager"""
        self._running = False
        logger.info("DistributedContextManager shutdown")
    
    async def _load_contexts(self) -> None:
        """Load active contexts from database"""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        result = await self.db.execute(
            select(DistributedContextState).where(
                or_(
                    DistributedContextState.expires_at == None,
                    DistributedContextState.expires_at > datetime.utcnow()
                )
            )
        )
        for ctx in result.scalars().all():
            self._contexts[ctx.context_id] = ctx
    
    async def _load_policies(self) -> None:
        """Load propagation policies"""
        result = await self.db.execute(
            select(ContextPropagationPolicy).where(ContextPropagationPolicy.is_active == True)
        )
        for policy in result.scalars().all():
            self._policies[policy.name] = policy
    
    # ==================== Context Management ====================
    
    async def create_context(
        self,
        scope: str,
        origin_node_id: Optional[UUID] = None,
        origin_service: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> DistributedContextState:
        """Create new distributed context"""
        context_id = f"ctx-{uuid4()}"
        
        context = DistributedContextState(
            context_id=context_id,
            scope=scope,
            origin_node_id=origin_node_id,
            origin_service=origin_service,
            context_data=context_data or {},
            context_version=1,
            propagation_status=PropagationStatus.PENDING.value,
            visited_nodes=[],
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=ttl_seconds) if ttl_seconds else None,
        )
        
        self.db.add(context)
        await self.db.commit()
        await self.db.refresh(context)
        
        self._contexts[context_id] = context
        return context
    
    async def propagate_context(
        self,
        context_id: str,
        target_node_id: UUID,
        target_service: str,
    ) -> ContextPropagationResult:
        """Propagate context to target node"""
        context = self._contexts.get(context_id)
        if not context:
            return ContextPropagationResult(
                success=False,
                context_id=context_id,
                propagated_to=[],
                failed_nodes=[],
                latency_ms=0,
                error="Context not found",
            )
        
        start_time = datetime.utcnow()
        
        try:
            # Get matching policy
            policy = self._get_matching_policy(context.scope, target_service)
            
            # Apply transformations if policy exists
            data = self._apply_policy_transformations(context.context_data, policy)
            
            # Create visited record
            visit = {
                "node_id": str(target_node_id),
                "service": target_service,
                "timestamp": start_time.isoformat(),
            }
            
            visited = context.visited_nodes or []
            visited.append(visit)
            context.visited_nodes = visited
            context.propagation_count += 1
            context.last_propagated_to = target_node_id
            
            if context.propagation_status == PropagationStatus.PENDING.value:
                context.propagation_status = PropagationStatus.PROPAGATING.value
            
            await self.db.commit()
            
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return ContextPropagationResult(
                success=True,
                context_id=context_id,
                propagated_to=[target_service],
                failed_nodes=[],
                latency_ms=latency,
            )
            
        except Exception as e:
            logger.error(f"Context propagation failed: {e}")
            return ContextPropagationResult(
                success=False,
                context_id=context_id,
                propagated_to=[],
                failed_nodes=[target_service],
                latency_ms=0,
                error=str(e),
            )
    
    def _get_matching_policy(
        self,
        scope: str,
        target_service: str,
    ) -> Optional[ContextPropagationPolicy]:
        """Get matching propagation policy"""
        for policy in self._policies.values():
            if policy.scope != scope:
                continue
            if policy.applies_to_nodes and target_service not in policy.applies_to_nodes:
                continue
            return policy
        return None
    
    def _apply_policy_transformations(
        self,
        context_data: Dict[str, Any],
        policy: Optional[ContextPropagationPolicy],
    ) -> Dict[str, Any]:
        """Apply policy transformations to context data"""
        if not policy or not policy.transformations:
            return context_data
        
        result = context_data.copy()
        transforms = policy.transformations
        
        # Apply field inclusions
        if policy.included_fields:
            included = {}
            for field in policy.included_fields:
                if field in result:
                    included[field] = result[field]
            result = included
        
        # Apply field exclusions
        if policy.excluded_fields:
            for field in policy.excluded_fields:
                result.pop(field, None)
        
        # Apply transformation rules
        if "rename" in transforms:
            for old_name, new_name in transforms["rename"].items():
                if old_name in result:
                    result[new_name] = result.pop(old_name)
        
        return result
    
    async def get_context(self, context_id: str) -> Optional[DistributedContextState]:
        """Get context by ID"""
        return self._contexts.get(context_id)
    
    async def update_context(
        self,
        context_id: str,
        updates: Dict[str, Any],
    ) -> Optional[DistributedContextState]:
        """Update context data"""
        context = self._contexts.get(context_id)
        if not context:
            return None
        
        # Merge updates
        current_data = context.context_data.copy()
        current_data.update(updates)
        context.context_data = current_data
        context.context_version += 1
        context.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(context)
        
        return context

    async def get_context_state(self, context_id: str) -> Optional[DistributedContextState]:
        """Get context state by ID (alias for get_context)"""
        return await self.get_context(context_id)

    async def update_context_data(
        self,
        context_id: str,
        updates: Dict[str, Any],
    ) -> bool:
        """Update context data - returns bool for convenience"""
        context = await self.update_context(context_id, updates)
        return context is not None


class ExecutionContinuityEngine:
    """Engine for maintaining execution continuity across distributed nodes"""
    
    def __init__(self, db: AsyncSession, context_manager: DistributedContextManager):
        self.db = db
        self.context_manager = context_manager
        self._sessions: Dict[str, RuntimePropagationSession] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize execution continuity engine"""
        await self._load_sessions()
        self._running = True
        logger.info("ExecutionContinuityEngine initialized")
    
    async def shutdown(self) -> None:
        """Shutdown execution continuity engine"""
        self._running = False
        logger.info("ExecutionContinuityEngine shutdown")
    
    async def _load_sessions(self) -> None:
        """Load active propagation sessions"""
        result = await self.db.execute(
            select(RuntimePropagationSession).where(
                RuntimePropagationSession.continuity_state == ContinuityState.ACTIVE.value
            )
        )
        for session in result.scalars().all():
            self._sessions[session.session_id] = session
    
    # ==================== Session Management ====================
    
    async def create_propagation_session(
        self,
        workflow_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        sync_mode: str = SyncMode.LAZY.value,
    ) -> RuntimePropagationSession:
        """Create new propagation session (alias for create_session)"""
        return await self.create_session(workflow_id, execution_id, correlation_id, sync_mode)
    
    async def create_session(
        self,
        workflow_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        sync_mode: str = SyncMode.LAZY.value,
    ) -> RuntimePropagationSession:
        """Create new propagation session"""
        session_id = f"session-{uuid4()}"
        
        session = RuntimePropagationSession(
            session_id=session_id,
            workflow_id=workflow_id,
            execution_id=execution_id,
            correlation_id=correlation_id,
            sync_mode=sync_mode,
            continuity_state=ContinuityState.ACTIVE.value,
            context_count=0,
            propagated_contexts=[],
            involved_nodes=[],
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        self._sessions[session_id] = session
        return session
    
    async def attach_context(
        self,
        session_id: str,
        context_id: str,
    ) -> Optional[RuntimePropagationSession]:
        """Attach context to propagation session"""
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        contexts = session.propagated_contexts or []
        if context_id not in contexts:
            contexts.append(context_id)
            session.propagated_contexts = contexts
            session.context_count += 1
        
        session.last_activity = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    async def record_node_involvement(
        self,
        session_id: str,
        node_id: str,
        node_name: str,
    ) -> Optional[RuntimePropagationSession]:
        """Record node involvement in session"""
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        nodes = session.involved_nodes or []
        if node_id not in nodes:
            nodes.append(node_id)
            session.involved_nodes = nodes
        
        session.last_activity = datetime.utcnow()
        
        await self.db.commit()
        return session
    
    async def suspend_session(self, session_id: str) -> Optional[RuntimePropagationSession]:
        """Suspend propagation session"""
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        session.continuity_state = ContinuityState.SUSPENDED.value
        session.last_activity = datetime.utcnow()
        
        await self.db.commit()
        return session
    
    async def resume_session(self, session_id: str) -> Optional[RuntimePropagationSession]:
        """Resume suspended propagation session"""
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        session.continuity_state = ContinuityState.ACTIVE.value
        session.last_activity = datetime.utcnow()
        
        await self.db.commit()
        return session
    
    async def terminate_session(
        self,
        session_id: str,
        reason: Optional[str] = None,
    ) -> Optional[RuntimePropagationSession]:
        """Terminate propagation session"""
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        session.continuity_state = ContinuityState.TERMINATED.value
        session.terminated_at = datetime.utcnow()
        
        await self.db.commit()
        
        # Remove from cache
        self._sessions.pop(session_id, None)
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[RuntimePropagationSession]:
        """Get session by ID"""
        return self._sessions.get(session_id)
    
    async def get_sessions_by_workflow(self, workflow_id: str) -> List[RuntimePropagationSession]:
        """Get all sessions for a workflow"""
        return [s for s in self._sessions.values() if s.workflow_id == workflow_id]


class RuntimeLineageSynchronizer:
    """Synchronizes runtime lineage across distributed execution"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._graphs: Dict[str, OrchestrationLineageGraph] = {}
        self._nodes: Dict[str, RuntimeLineageNode] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize runtime lineage synchronizer"""
        await self._load_graphs()
        self._running = True
        logger.info("RuntimeLineageSynchronizer initialized")
    
    async def shutdown(self) -> None:
        """Shutdown runtime lineage synchronizer"""
        self._running = False
        logger.info("RuntimeLineageSynchronizer shutdown")
    
    async def _load_graphs(self) -> None:
        """Load lineage graphs from database"""
        result = await self.db.execute(
            select(OrchestrationLineageGraph).where(
                OrchestrationLineageGraph.is_complete == False
            )
        )
        for graph in result.scalars().all():
            self._graphs[graph.graph_id] = graph
    
    # ==================== Graph Management ====================
    
    async def create_graph(
        self,
        lineage_scope: str,
        root_node_id: Optional[str] = None,
        parent_graph_id: Optional[str] = None,
    ) -> OrchestrationLineageGraph:
        """Create new lineage graph"""
        graph_id = f"graph-{uuid4()}"
        
        graph = OrchestrationLineageGraph(
            graph_id=graph_id,
            lineage_scope=lineage_scope,
            parent_graph_id=parent_graph_id,
            nodes=[],
            node_count=0,
            edges=[],
            edge_count=0,
            version=1,
            root_node_id=root_node_id,
            is_complete=False,
            is_forked=False,
            created_at=datetime.utcnow(),
        )
        
        self.db.add(graph)
        await self.db.commit()
        await self.db.refresh(graph)
        
        self._graphs[graph_id] = graph
        return graph
    
    async def add_node(
        self,
        graph_id: str,
        node_id: str,
        node_type: str,
        execution_id: Optional[str] = None,
        depends_on: Optional[List[str]] = None,
    ) -> RuntimeLineageNode:
        """Add node to lineage graph"""
        graph = self._graphs.get(graph_id)
        if not graph:
            raise ValueError(f"Graph not found: {graph_id}")
        
        # Create lineage node
        lineage_node = RuntimeLineageNode(
            graph_id=graph_id,
            node_id=node_id,
            execution_id=execution_id,
            node_type=node_type,
            status="pending",
            depends_on=depends_on,
        )
        
        self.db.add(lineage_node)
        
        # Update graph
        nodes = graph.nodes or []
        nodes.append({
            "id": node_id,
            "type": node_type,
            "execution_id": execution_id,
            "added_at": datetime.utcnow().isoformat(),
        })
        graph.nodes = nodes
        graph.node_count = len(nodes)
        graph.last_updated = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(lineage_node)
        
        self._nodes[f"{graph_id}:{node_id}"] = lineage_node
        
        # Update dependencies
        if depends_on:
            for dep_id in depends_on:
                dep_key = f"{graph_id}:{dep_id}"
                dep_node = self._nodes.get(dep_key)
                if dep_node:
                    deps = dep_node.depended_by or []
                    deps.append(node_id)
                    dep_node.depended_by = deps
        
        return lineage_node
    
    async def update_node_status(
        self,
        graph_id: str,
        node_id: str,
        status: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[RuntimeLineageNode]:
        """Update node status in lineage"""
        node_key = f"{graph_id}:{node_id}"
        node = self._nodes.get(node_key)
        if not node:
            return None
        
        node.status = status
        if start_time:
            node.start_time = start_time
        if end_time:
            node.end_time = end_time
            if node.start_time:
                node.duration_ms = (end_time - node.start_time).total_seconds() * 1000
        
        if input_data:
            node.input_hash = hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()
        
        if output_data:
            node.output_hash = hashlib.sha256(json.dumps(output_data, sort_keys=True).encode()).hexdigest()
        
        await self.db.commit()
        await self.db.refresh(node)
        
        return node
    
    async def add_edge(
        self,
        graph_id: str,
        source_node_id: str,
        target_node_id: str,
        edge_type: str = "dependency",
    ) -> Optional[OrchestrationLineageGraph]:
        """Add edge between nodes in lineage graph"""
        graph = self._graphs.get(graph_id)
        if not graph:
            return None
        
        edges = graph.edges or []
        edges.append({
            "source": source_node_id,
            "target": target_node_id,
            "type": edge_type,
            "created_at": datetime.utcnow().isoformat(),
        })
        graph.edges = edges
        graph.edge_count = len(edges)
        graph.last_updated = datetime.utcnow()
        
        await self.db.commit()
        return graph
    
    async def complete_graph(self, graph_id: str) -> Optional[OrchestrationLineageGraph]:
        """Mark lineage graph as complete"""
        graph = self._graphs.get(graph_id)
        if not graph:
            return None
        
        graph.is_complete = True
        graph.completed_at = datetime.utcnow()
        graph.last_updated = datetime.utcnow()
        
        await self.db.commit()
        return graph
    
    async def get_graph(self, graph_id: str) -> Optional[OrchestrationLineageGraph]:
        """Get lineage graph by ID"""
        return self._graphs.get(graph_id)
    
    async def get_graph_nodes(self, graph_id: str) -> List[RuntimeLineageNode]:
        """Get all nodes in a graph"""
        result = await self.db.execute(
            select(RuntimeLineageNode).where(RuntimeLineageNode.graph_id == graph_id)
        )
        return list(result.scalars().all())


class ExecutionIdentityManager:
    """Manages execution identity propagation"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._identities: Dict[str, ExecutionIdentity] = {}
    
    async def initialize(self) -> None:
        """Initialize execution identity manager"""
        await self._load_identities()
        logger.info("ExecutionIdentityManager initialized")
    
    async def _load_identities(self) -> None:
        """Load identities from database"""
        result = await self.db.execute(
            select(ExecutionIdentity).where(
                or_(
                    ExecutionIdentity.expires_at == None,
                    ExecutionIdentity.expires_at > datetime.utcnow()
                )
            )
        )
        for identity in result.scalars().all():
            self._identities[identity.identity_id] = identity
    
    async def create_identity(
        self,
        identity_type: str,
        properties: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
    ) -> ExecutionIdentity:
        """Create new execution identity"""
        identity_id = f"identity-{uuid4()}"
        
        identity = ExecutionIdentity(
            identity_id=identity_id,
            identity_type=identity_type,
            properties=properties,
            lineage_chain=[],
            propagation_path=[],
            expires_at=datetime.utcnow() + timedelta(seconds=ttl_seconds) if ttl_seconds else None,
        )
        
        self.db.add(identity)
        await self.db.commit()
        await self.db.refresh(identity)
        
        self._identities[identity_id] = identity
        return identity
    
    async def propagate_identity(
        self,
        identity_id: str,
        target_service: str,
    ) -> Optional[ExecutionIdentity]:
        """Propagate identity to target service"""
        identity = self._identities.get(identity_id)
        if not identity:
            return None
        
        path = identity.propagation_path or []
        path.append(target_service)
        identity.propagation_path = path
        identity.propagation_count += 1
        identity.last_accessed = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(identity)
        
        return identity
    
    async def extend_lineage(
        self,
        identity_id: str,
        lineage_entry: Dict[str, Any],
    ) -> Optional[ExecutionIdentity]:
        """Extend identity lineage chain"""
        identity = self._identities.get(identity_id)
        if not identity:
            return None
        
        chain = identity.lineage_chain or []
        chain.append(lineage_entry)
        identity.lineage_chain = chain
        
        await self.db.commit()
        await self.db.refresh(identity)
        
        return identity


class CrossServiceCoordinator:
    """Coordinates operations across services"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._coordinations: Dict[str, CrossServiceCoordination] = {}
    
    async def initialize(self) -> None:
        """Initialize cross-service coordinator"""
        await self._load_coordinations()
        logger.info("CrossServiceCoordinator initialized")
    
    async def _load_coordinations(self) -> None:
        """Load active coordinations"""
        result = await self.db.execute(
            select(CrossServiceCoordination).where(
                CrossServiceCoordination.state.in_(["pending", "acknowledged"])
            )
        )
        for coord in result.scalars().all():
            self._coordinations[coord.coordination_id] = coord
    
    async def create_coordination(
        self,
        coordination_type: str,
        source_service: str,
        target_services: List[str],
        payload: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> CrossServiceCoordination:
        """Create new cross-service coordination"""
        coordination_id = f"coord-{uuid4()}"
        
        coordination = CrossServiceCoordination(
            coordination_id=coordination_id,
            coordination_type=coordination_type,
            source_service=source_service,
            target_services=target_services,
            payload=payload,
            state="pending",
            correlation_id=correlation_id,
        )
        
        self.db.add(coordination)
        await self.db.commit()
        await self.db.refresh(coordination)
        
        self._coordinations[coordination_id] = coordination
        return coordination
    
    async def acknowledge(
        self,
        coordination_id: str,
    ) -> Optional[CrossServiceCoordination]:
        """Acknowledge coordination"""
        coordination = self._coordinations.get(coordination_id)
        if not coordination:
            return None
        
        coordination.state = "acknowledged"
        coordination.acknowledged_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(coordination)
        
        return coordination
    
    async def complete(
        self,
        coordination_id: str,
    ) -> Optional[CrossServiceCoordination]:
        """Complete coordination"""
        coordination = self._coordinations.get(coordination_id)
        if not coordination:
            return None
        
        coordination.state = "completed"
        coordination.completed_at = datetime.utcnow()
        
        await self.db.commit()
        return coordination
    
    async def get_pending_coordinations(
        self,
        source_service: Optional[str] = None,
    ) -> List[CrossServiceCoordination]:
        """Get pending coordinations"""
        coordinations = [c for c in self._coordinations.values() if c.state == "pending"]
        if source_service:
            coordinations = [c for c in coordinations if c.source_service == source_service]
        return coordinations


class ExecutionSnapshotManager:
    """Manages execution snapshots for recovery and replay"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._snapshots: Dict[str, ExecutionSnapshot] = {}
    
    async def initialize(self) -> None:
        """Initialize execution snapshot manager"""
        logger.info("ExecutionSnapshotManager initialized")
    
    async def create_snapshot(
        self,
        execution_id: str,
        context_state: Dict[str, Any],
        snapshot_type: str,
        workflow_id: Optional[str] = None,
        node_states: Optional[List[Dict[str, Any]]] = None,
        variables: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
    ) -> ExecutionSnapshot:
        """Create execution snapshot"""
        # Get next sequence number
        result = await self.db.execute(
            select(RuntimeLineageNode.execution_id).where(
                RuntimeLineageNode.execution_id == execution_id
            ).order_by(RuntimeLineageNode.start_time.desc()).limit(1)
        )
        seq = 0
        if result:
            seq += 1
        
        snapshot_id = f"snap-{uuid4()}"
        
        snapshot = ExecutionSnapshot(
            snapshot_id=snapshot_id,
            execution_id=execution_id,
            workflow_id=workflow_id,
            context_state=context_state,
            node_states=node_states,
            variables=variables,
            sequence_number=seq,
            snapshot_type=snapshot_type,
            reason=reason,
        )
        
        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)
        
        self._snapshots[snapshot_id] = snapshot
        return snapshot
    
    async def get_latest_snapshot(self, execution_id: str) -> Optional[ExecutionSnapshot]:
        """Get latest snapshot for execution"""
        result = await self.db.execute(
            select(ExecutionSnapshot)
            .where(ExecutionSnapshot.execution_id == execution_id)
            .order_by(ExecutionSnapshot.sequence_number.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def restore_snapshot(
        self,
        snapshot_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Restore execution from snapshot"""
        snapshot = self._snapshots.get(snapshot_id)
        if not snapshot:
            return None
        
        return {
            "context_state": snapshot.context_state,
            "node_states": snapshot.node_states,
            "variables": snapshot.variables,
            "sequence_number": snapshot.sequence_number,
        }


class DistributedRuntimeService:
    """Main service for distributed runtime propagation and coordination"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.context_manager = DistributedContextManager(db)
        self.continuity_engine = ExecutionContinuityEngine(db, self.context_manager)
        self.lineage_synchronizer = RuntimeLineageSynchronizer(db)
        self.identity_manager = ExecutionIdentityManager(db)
        self.coordinator = CrossServiceCoordinator(db)
        self.snapshot_manager = ExecutionSnapshotManager(db)
    
    async def initialize(self) -> None:
        """Initialize all sub-services"""
        await self.context_manager.initialize()
        await self.continuity_engine.initialize()
        await self.lineage_synchronizer.initialize()
        await self.identity_manager.initialize()
        await self.coordinator.initialize()
        await self.snapshot_manager.initialize()
        logger.info("DistributedRuntimeService fully initialized")
    
    async def shutdown(self) -> None:
        """Shutdown all sub-services"""
        await self.context_manager.shutdown()
        await self.continuity_engine.shutdown()
        await self.lineage_synchronizer.shutdown()
        logger.info("DistributedRuntimeService shutdown")
    
    async def get_runtime_summary(self) -> Dict[str, Any]:
        """Get summary of distributed runtime state"""
        return {
            "active_contexts": len(self.context_manager._contexts),
            "active_sessions": len(self.continuity_engine._sessions),
            "active_graphs": len(self.lineage_synchronizer._graphs),
            "active_identities": len(self.identity_manager._identities),
            "pending_coordinations": len([
                c for c in self.coordinator._coordinations.values()
                if c.state == "pending"
            ]),
        }