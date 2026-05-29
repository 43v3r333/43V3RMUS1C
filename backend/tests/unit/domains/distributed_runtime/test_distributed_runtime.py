"""
43V3R CORE - Distributed Runtime Domain Unit Tests
====================================================

Comprehensive unit tests for distributed runtime propagation systems:
- DistributedContextManager: Context creation, propagation, policies
- ExecutionContinuityEngine: Session continuity, recovery
- RuntimeLineageSynchronizer: Lineage tracking, graph management
- ExecutionIdentityManager: Identity propagation
- CrossServiceCoordinator: Cross-service coordination
- ExecutionSnapshotManager: Snapshot management for recovery

Test Coverage:
- Context state management
- Propagation policies and transformations
- Continuity state transitions
- Lineage graph operations
- Identity chain propagation
- Cross-service coordination
- Snapshot creation and restoration

Markers: unit, distributed, distributed_runtime
"""

from __future__ import annotations

import asyncio
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.distributed_runtime.models import (
    ContextScope,
    PropagationStatus,
    ContinuityState,
    SyncMode,
    DistributedContextState,
    RuntimePropagationSession,
    OrchestrationLineageGraph,
    ExecutionIdentity,
    ContextPropagationPolicy,
    RuntimeLineageNode,
    CrossServiceCoordination,
    ExecutionSnapshot,
)
from app.domains.distributed_runtime.services import (
    DistributedContextManager,
    ExecutionContinuityEngine,
    RuntimeLineageSynchronizer,
    ExecutionIdentityManager,
    CrossServiceCoordinator,
    ExecutionSnapshotManager,
    DistributedRuntimeService,
    ContextPropagationResult,
    LineageNode,
)


# =============================================================================
# DistributedContextManager Tests
# =============================================================================

class TestDistributedContextManager:
    """Test suite for DistributedContextManager"""
    
    @pytest_asyncio.fixture
    async def context_manager(
        self,
        db_session: AsyncSession,
    ) -> DistributedContextManager:
        """Create context manager for testing"""
        manager = DistributedContextManager(db_session)
        await manager.initialize()
        yield manager
        await manager.shutdown()
    
    # ----------------------------------------------------------------
    # Initialization Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_manager_initialization(self, context_manager: DistributedContextManager):
        """Test manager initializes correctly"""
        assert context_manager is not None
        assert context_manager._running is True
        assert isinstance(context_manager._contexts, dict)
        assert isinstance(context_manager._policies, dict)
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_manager_shutdown(self, context_manager: DistributedContextManager):
        """Test manager shuts down gracefully"""
        await context_manager.shutdown()
        assert context_manager._running is False
    
    # ----------------------------------------------------------------
    # Context Creation Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_create_context_basic(
        self,
        context_manager: DistributedContextManager,
        db_session: AsyncSession,
    ):
        """Test basic context creation"""
        context = await context_manager.create_context(
            scope=ContextScope.SESSION.value,
            origin_service="test-service",
            context_data={"key": "value"},
        )
        
        assert context is not None
        assert context.context_id.startswith("ctx-")
        assert context.scope == ContextScope.SESSION.value
        assert context.origin_service == "test-service"
        assert context.context_data["key"] == "value"
        assert context.context_version == 1
        assert context.propagation_status == PropagationStatus.PENDING.value
        assert context.propagation_count == 0
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_create_context_with_ttl(
        self,
        context_manager: DistributedContextManager,
        db_session: AsyncSession,
    ):
        """Test context creation with TTL"""
        context = await context_manager.create_context(
            scope=ContextScope.WORKFLOW.value,
            context_data={},
            ttl_seconds=3600,
        )
        
        assert context.expires_at is not None
        assert context.expires_at > datetime.utcnow()
        assert context.expires_at < datetime.utcnow() + timedelta(hours=2)
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_create_context_with_node_id(
        self,
        context_manager: DistributedContextManager,
        db_session: AsyncSession,
    ):
        """Test context creation with origin node ID"""
        node_id = uuid4()
        
        context = await context_manager.create_context(
            scope=ContextScope.NODE.value,
            origin_node_id=node_id,
        )
        
        assert context.origin_node_id == node_id
    
    # ----------------------------------------------------------------
    # Context Propagation Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_propagate_context_success(
        self,
        context_manager: DistributedContextManager,
        db_session: AsyncSession,
    ):
        """Test successful context propagation"""
        context = await context_manager.create_context(
            scope=ContextScope.EXECUTION.value,
            context_data={"test": "data"},
        )
        
        target_node_id = uuid4()
        result = await context_manager.propagate_context(
            context_id=context.context_id,
            target_node_id=target_node_id,
            target_service="target-service",
        )
        
        assert result.success is True
        assert result.context_id == context.context_id
        assert "target-service" in result.propagated_to
        assert len(result.failed_nodes) == 0
        assert result.latency_ms >= 0
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_propagate_context_not_found(
        self,
        context_manager: DistributedContextManager,
    ):
        """Test propagation of non-existent context"""
        result = await context_manager.propagate_context(
            context_id="non-existent",
            target_node_id=uuid4(),
            target_service="test",
        )
        
        assert result.success is False
        assert result.error == "Context not found"
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_propagate_context_tracks_visits(
        self,
        context_manager: DistributedContextManager,
        db_session: AsyncSession,
    ):
        """Test propagation tracks visited nodes"""
        context = await context_manager.create_context(
            scope=ContextScope.SESSION.value,
        )
        
        node1 = uuid4()
        node2 = uuid4()
        
        # Propagate to first node
        await context_manager.propagate_context(
            context_id=context.context_id,
            target_node_id=node1,
            target_service="service-1",
        )
        
        # Propagate to second node
        await context_manager.propagate_context(
            context_id=context.context_id,
            target_node_id=node2,
            target_service="service-2",
        )
        
        # Check context state
        updated = context_manager._contexts.get(context.context_id)
        assert updated is not None
        assert updated.propagation_count == 2
        assert updated.last_propagated_to == node2
        assert len(updated.visited_nodes) == 2
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_propagate_context_updates_status(
        self,
        context_manager: DistributedContextManager,
        db_session: AsyncSession,
    ):
        """Test propagation updates context status"""
        context = await context_manager.create_context(
            scope=ContextScope.SESSION.value,
        )
        
        # First propagation should change status to PROPAGATING
        await context_manager.propagate_context(
            context_id=context.context_id,
            target_node_id=uuid4(),
            target_service="test-service",
        )
        
        await db_session.refresh(context)
        
        # Status should be updated to propagating
        assert context.propagation_status in [
            PropagationStatus.PROPAGATING.value,
            PropagationStatus.PROPAGATED.value,
        ]
    
    # ----------------------------------------------------------------
    # Policy Transformation Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_apply_policy_transformations_with_include(
        self,
        context_manager: DistributedContextManager,
    ):
        """Test policy transformations with field inclusion"""
        policy = ContextPropagationPolicy(
            name="test-policy",
            scope="session",
            included_fields=["allowed_field"],
            transformations={"test": "transform"},
        )
        
        context_data = {
            "allowed_field": "allowed_value",
            "excluded_field": "excluded_value",
        }
        
        result = context_manager._apply_policy_transformations(
            context_data, policy
        )
        
        assert "allowed_field" in result
        assert "allowed_value" in result.values()
        assert "excluded_field" not in result
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_apply_policy_transformations_with_exclude(
        self,
        context_manager: DistributedContextManager,
    ):
        """Test policy transformations with field exclusion"""
        policy = ContextPropagationPolicy(
            name="test-policy",
            scope="session",
            excluded_fields=["secret_field"],
        )
        
        context_data = {
            "visible_field": "visible_value",
            "secret_field": "secret_value",
        }
        
        result = context_manager._apply_policy_transformations(
            context_data, policy
        )
        
        assert "visible_field" in result
        assert "secret_field" not in result
    
    # ----------------------------------------------------------------
    # Context State Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_get_context_state(
        self,
        context_manager: DistributedContextManager,
        db_session: AsyncSession,
    ):
        """Test retrieving context state"""
        context = await context_manager.create_context(
            scope=ContextScope.SESSION.value,
            context_data={"state": "test"},
        )
        
        state = await context_manager.get_context_state(context.context_id)
        
        assert state is not None
        assert state.context_id == context.context_id
        assert state.context_data["state"] == "test"
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_update_context_data(
        self,
        context_manager: DistributedContextManager,
        db_session: AsyncSession,
    ):
        """Test updating context data"""
        context = await context_manager.create_context(
            scope=ContextScope.SESSION.value,
            context_data={"version": 1},
        )
        
        success = await context_manager.update_context_data(
            context.context_id,
            {"version": 2, "added": "value"},
        )
        
        assert success is True
        
        updated = await context_manager.get_context_state(context.context_id)
        assert updated.context_version == 2
        assert updated.context_data["added"] == "value"


# =============================================================================
# ExecutionContinuityEngine Tests
# =============================================================================

class TestExecutionContinuityEngine:
    """Test suite for ExecutionContinuityEngine"""
    
    @pytest_asyncio.fixture
    async def continuity_engine(
        self,
        db_session: AsyncSession,
        context_manager: DistributedContextManager,
    ) -> ExecutionContinuityEngine:
        """Create continuity engine for testing"""
        engine = ExecutionContinuityEngine(db_session, context_manager)
        await engine.initialize()
        yield engine
        await engine.shutdown()
    
    # ----------------------------------------------------------------
    # Session Lifecycle Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_create_propagation_session(
        self,
        continuity_engine: ExecutionContinuityEngine,
        db_session: AsyncSession,
    ):
        """Test creating propagation session"""
        session = await continuity_engine.create_propagation_session(
            workflow_id="workflow-1",
            execution_id="execution-1",
            correlation_id="corr-1",
        )
        
        assert session is not None
        assert session.session_id.startswith("psess-")
        assert session.workflow_id == "workflow-1"
        assert session.execution_id == "execution-1"
        assert session.correlation_id == "corr-1"
        assert session.continuity_state == ContinuityState.ACTIVE.value
        assert session.sync_mode == SyncMode.LAZY.value
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_suspend_session(
        self,
        continuity_engine: ExecutionContinuityEngine,
        db_session: AsyncSession,
    ):
        """Test suspending continuity session"""
        session = await continuity_engine.create_propagation_session(
            workflow_id="workflow-2",
        )
        
        suspended = await continuity_engine.suspend_session(session.session_id)
        
        assert suspended.continuity_state == ContinuityState.SUSPENDED.value
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_resume_session(
        self,
        continuity_engine: ExecutionContinuityEngine,
        db_session: AsyncSession,
    ):
        """Test resuming continuity session"""
        session = await continuity_engine.create_propagation_session(
            workflow_id="workflow-3",
        )
        
        await continuity_engine.suspend_session(session.session_id)
        resumed = await continuity_engine.resume_session(session.session_id)
        
        assert resumed.continuity_state == ContinuityState.ACTIVE.value
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_terminate_session(
        self,
        continuity_engine: ExecutionContinuityEngine,
        db_session: AsyncSession,
    ):
        """Test terminating continuity session"""
        session = await continuity_engine.create_propagation_session(
            workflow_id="workflow-4",
        )
        
        terminated = await continuity_engine.terminate_session(session.session_id)
        
        assert terminated.continuity_state == ContinuityState.TERMINATED.value
        assert terminated.terminated_at is not None
    
    # ----------------------------------------------------------------
    # Recovery Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_get_active_sessions(
        self,
        continuity_engine: ExecutionContinuityEngine,
        db_session: AsyncSession,
    ):
        """Test retrieving active sessions"""
        # Create multiple sessions
        await continuity_engine.create_propagation_session(workflow_id="wf1")
        await continuity_engine.create_propagation_session(workflow_id="wf2")
        await continuity_engine.create_propagation_session(workflow_id="wf3")
        
        active = await continuity_engine.get_active_sessions()
        
        assert len(active) >= 3
        assert all(s.continuity_state == ContinuityState.ACTIVE.value for s in active)
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_get_active_sessions_by_workflow(
        self,
        continuity_engine: ExecutionContinuityEngine,
        db_session: AsyncSession,
    ):
        """Test retrieving active sessions by workflow"""
        await continuity_engine.create_propagation_session(workflow_id="specific-wf")
        await continuity_engine.create_propagation_session(workflow_id="other-wf")
        
        active = await continuity_engine.get_active_sessions(workflow_id="specific-wf")
        
        assert len(active) >= 1
        assert all(s.workflow_id == "specific-wf" for s in active)


# =============================================================================
# RuntimeLineageSynchronizer Tests
# =============================================================================

class TestRuntimeLineageSynchronizer:
    """Test suite for RuntimeLineageSynchronizer"""
    
    @pytest_asyncio.fixture
    async def lineage_synchronizer(
        self,
        db_session: AsyncSession,
    ) -> RuntimeLineageSynchronizer:
        """Create lineage synchronizer for testing"""
        synchronizer = RuntimeLineageSynchronizer(db_session)
        await synchronizer.initialize()
        yield synchronizer
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_create_lineage_graph(
        self,
        lineage_synchronizer: RuntimeLineageSynchronizer,
        db_session: AsyncSession,
    ):
        """Test creating lineage graph"""
        graph = await lineage_synchronizer.create_lineage_graph(
            lineage_scope="execution",
            nodes=[
                {"id": "n1", "type": "start"},
                {"id": "n2", "type": "process"},
                {"id": "n3", "type": "end"},
            ],
            edges=[
                {"from": "n1", "to": "n2"},
                {"from": "n2", "to": "n3"},
            ],
        )
        
        assert graph is not None
        assert graph.graph_id.startswith("lgph-")
        assert graph.lineage_scope == "execution"
        assert graph.node_count == 3
        assert graph.edge_count == 2
        assert graph.is_complete is False
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_add_lineage_node(
        self,
        lineage_synchronizer: RuntimeLineageSynchronizer,
        db_session: AsyncSession,
    ):
        """Test adding node to lineage graph"""
        graph = await lineage_synchronizer.create_lineage_graph(
            lineage_scope="execution",
            nodes=[],
            edges=[],
        )
        
        node = await lineage_synchronizer.add_lineage_node(
            graph_id=graph.graph_id,
            node_id="new-node",
            node_type="process",
            execution_id="exec-1",
        )
        
        assert node is not None
        assert node.node_id == "new-node"
        assert node.node_type == "process"
        assert node.execution_id == "exec-1"
        assert node.status == "pending"
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_add_lineage_edge(
        self,
        lineage_synchronizer: RuntimeLineageSynchronizer,
        db_session: AsyncSession,
    ):
        """Test adding edge to lineage graph"""
        graph = await lineage_synchronizer.create_lineage_graph(
            lineage_scope="execution",
            nodes=[
                {"id": "n1", "type": "start"},
                {"id": "n2", "type": "end"},
            ],
            edges=[],
        )
        
        edge = await lineage_synchronizer.add_lineage_edge(
            graph_id=graph.graph_id,
            from_node_id="n1",
            to_node_id="n2",
            edge_type="dependency",
        )
        
        assert edge is not None
        assert edge["from"] == "n1"
        assert edge["to"] == "n2"
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_mark_graph_complete(
        self,
        lineage_synchronizer: RuntimeLineageSynchronizer,
        db_session: AsyncSession,
    ):
        """Test marking lineage graph complete"""
        graph = await lineage_synchronizer.create_lineage_graph(
            lineage_scope="execution",
            nodes=[{"id": "n1"}],
            edges=[],
        )
        
        await lineage_synchronizer.mark_graph_complete(graph.graph_id)
        
        await db_session.refresh(graph)
        
        assert graph.is_complete is True
        assert graph.completed_at is not None
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_get_execution_lineage(
        self,
        lineage_synchronizer: RuntimeLineageSynchronizer,
        db_session: AsyncSession,
    ):
        """Test retrieving execution lineage"""
        graph = await lineage_synchronizer.create_lineage_graph(
            lineage_scope="execution",
            nodes=[
                {"id": "lineage-n1", "type": "start"},
                {"id": "lineage-n2", "type": "process"},
            ],
            edges=[{"from": "lineage-n1", "to": "lineage-n2"}],
        )
        
        # Add nodes with execution IDs
        node1 = await lineage_synchronizer.add_lineage_node(
            graph_id=graph.graph_id,
            node_id="lineage-n1",
            node_type="start",
            execution_id="exec-lineage-1",
        )
        node2 = await lineage_synchronizer.add_lineage_node(
            graph_id=graph.graph_id,
            node_id="lineage-n2",
            node_type="process",
            execution_id="exec-lineage-2",
        )
        
        # Get lineage
        lineage = await lineage_synchronizer.get_execution_lineage(graph.graph_id)
        
        assert len(lineage) == 2


# =============================================================================
# ExecutionIdentityManager Tests
# =============================================================================

class TestExecutionIdentityManager:
    """Test suite for ExecutionIdentityManager"""
    
    @pytest_asyncio.fixture
    async def identity_manager(
        self,
        db_session: AsyncSession,
    ) -> ExecutionIdentityManager:
        """Create identity manager for testing"""
        manager = ExecutionIdentityManager(db_session)
        await manager.initialize()
        yield manager
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_create_identity(
        self,
        identity_manager: ExecutionIdentityManager,
        db_session: AsyncSession,
    ):
        """Test creating execution identity"""
        identity = await identity_manager.create_identity(
            identity_type="workflow",
            properties={
                "workflow_name": "test-workflow",
                "version": "1.0",
            },
        )
        
        assert identity is not None
        assert identity.identity_id.startswith("eid-")
        assert identity.identity_type == "workflow"
        assert identity.propagation_count == 0
        assert identity.access_count == 1
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_record_identity_access(
        self,
        identity_manager: ExecutionIdentityManager,
        db_session: AsyncSession,
    ):
        """Test recording identity access"""
        identity = await identity_manager.create_identity(
            identity_type="session",
            properties={"type": "creation"},
        )
        
        await identity_manager.record_identity_access(identity.identity_id)
        await db_session.refresh(identity)
        
        assert identity.access_count == 2  # Initial + one record
        assert identity.last_accessed is not None
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_update_identity_path(
        self,
        identity_manager: ExecutionIdentityManager,
        db_session: AsyncSession,
    ):
        """Test updating identity propagation path"""
        identity = await identity_manager.create_identity(
            identity_type="execution",
            properties={"exec": "test"},
        )
        
        success = await identity_manager.update_identity_path(
            identity.identity_id,
            ["node-1", "node-2"],
        )
        
        assert success is True
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_update_identity_path_empty(
        self,
        identity_manager: ExecutionIdentityManager,
        db_session: AsyncSession,
    ):
        """Test updating identity path to empty clears path"""
        identity = await identity_manager.create_identity(
            identity_type="execution",
            properties={"exec": "test"},
        )
        
        success = await identity_manager.update_identity_path(
            identity.identity_id,
            [],
        )
        
        assert success is True


# =============================================================================
# CrossServiceCoordinator Tests
# =============================================================================

class TestCrossServiceCoordinator:
    """Test suite for CrossServiceCoordinator"""
    
    @pytest_asyncio.fixture
    async def coordinator(
        self,
        db_session: AsyncSession,
    ) -> CrossServiceCoordinator:
        """Create coordinator for testing"""
        coord = CrossServiceCoordinator(db_session)
        await coord.initialize()
        yield coord
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_create_coordination(
        self,
        coordinator: CrossServiceCoordinator,
        db_session: AsyncSession,
    ):
        """Test creating cross-service coordination"""
        coordination = await coordinator.create_coordination(
            coordination_type="sync",
            source_service="service-a",
            target_services=["service-b", "service-c"],
            payload={"sync_data": "value"},
            correlation_id="sync-corr-1",
        )
        
        assert coordination is not None
        assert coordination.coordination_id.startswith("coord-")
        assert coordination.coordination_type == "sync"
        assert coordination.source_service == "service-a"
        assert len(coordination.target_services) == 2
        assert coordination.state == "pending"
        assert coordination.correlation_id == "sync-corr-1"
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_acknowledge_coordination(
        self,
        coordinator: CrossServiceCoordinator,
        db_session: AsyncSession,
    ):
        """Test acknowledging coordination"""
        coordination = await coordinator.create_coordination(
            coordination_type="ack-test",
            source_service="master",
            target_services=["slave1"],
        )
        
        acknowledged = await coordinator.acknowledge(coordination.coordination_id)
        
        assert acknowledged.state == "acknowledged"
        assert acknowledged.acknowledged_at is not None
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_complete_coordination(
        self,
        coordinator: CrossServiceCoordinator,
        db_session: AsyncSession,
    ):
        """Test completing coordination"""
        coordination = await coordinator.create_coordination(
            coordination_type="complete-test",
            source_service="initiator",
            target_services=["receiver"],
        )
        
        completed = await coordinator.complete(coordination.coordination_id)
        
        assert completed.state == "completed"
        assert completed.completed_at is not None
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_get_pending_coordinations(
        self,
        coordinator: CrossServiceCoordinator,
        db_session: AsyncSession,
    ):
        """Test retrieving pending coordinations"""
        await coordinator.create_coordination(
            coordination_type="pending-test-1",
            source_service="source-1",
            target_services=["target-1"],
        )
        await coordinator.create_coordination(
            coordination_type="pending-test-2",
            source_service="source-2",
            target_services=["target-2"],
        )
        
        pending = coordinator.get_pending_coordinations()
        
        assert len(pending) >= 2
        assert all(c.state == "pending" for c in pending)
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_get_pending_coordinations_by_source(
        self,
        coordinator: CrossServiceCoordinator,
        db_session: AsyncSession,
    ):
        """Test retrieving pending coordinations by source service"""
        await coordinator.create_coordination(
            coordination_type="source-filter-test",
            source_service="specific-source",
            target_services=["target"],
        )
        await coordinator.create_coordination(
            coordination_type="source-filter-test-2",
            source_service="other-source",
            target_services=["target"],
        )
        
        pending = coordinator.get_pending_coordinations(source_service="specific-source")
        
        assert len(pending) >= 1
        assert all(c.source_service == "specific-source" for c in pending)


# =============================================================================
# ExecutionSnapshotManager Tests
# =============================================================================

class TestExecutionSnapshotManager:
    """Test suite for ExecutionSnapshotManager"""
    
    @pytest_asyncio.fixture
    async def snapshot_manager(
        self,
        db_session: AsyncSession,
    ) -> ExecutionSnapshotManager:
        """Create snapshot manager for testing"""
        manager = ExecutionSnapshotManager(db_session)
        await manager.initialize()
        yield manager
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_create_snapshot(
        self,
        snapshot_manager: ExecutionSnapshotManager,
        db_session: AsyncSession,
    ):
        """Test creating execution snapshot"""
        snapshot = await snapshot_manager.create_snapshot(
            execution_id="exec-snap-1",
            workflow_id="workflow-snap-1",
            context_state={"state": "data"},
            snapshot_type="checkpoint",
            reason="Scheduled checkpoint",
        )
        
        assert snapshot is not None
        assert snapshot.snapshot_id.startswith("snap-")
        assert snapshot.execution_id == "exec-snap-1"
        assert snapshot.context_state["state"] == "data"
        assert snapshot.snapshot_type == "checkpoint"
        assert snapshot.reason == "Scheduled checkpoint"
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_create_snapshot_with_node_states(
        self,
        snapshot_manager: ExecutionSnapshotManager,
        db_session: AsyncSession,
    ):
        """Test creating snapshot with node states"""
        node_states = [
            {"node_id": "n1", "status": "completed"},
            {"node_id": "n2", "status": "pending"},
        ]
        
        snapshot = await snapshot_manager.create_snapshot(
            execution_id="exec-snap-2",
            context_state={},
            snapshot_type="checkpoint",
            node_states=node_states,
        )
        
        assert snapshot.node_states is not None
        assert len(snapshot.node_states) == 2
        assert snapshot.node_states[0]["node_id"] == "n1"
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_create_snapshot_with_variables(
        self,
        snapshot_manager: ExecutionSnapshotManager,
        db_session: AsyncSession,
    ):
        """Test creating snapshot with variables"""
        variables = {
            "counter": 42,
            "flag": True,
            "name": "test",
        }
        
        snapshot = await snapshot_manager.create_snapshot(
            execution_id="exec-snap-3",
            context_state={},
            snapshot_type="checkpoint",
            variables=variables,
        )
        
        assert snapshot.variables is not None
        assert snapshot.variables["counter"] == 42
        assert snapshot.variables["flag"] is True
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_get_latest_snapshot(
        self,
        snapshot_manager: ExecutionSnapshotManager,
        db_session: AsyncSession,
    ):
        """Test retrieving latest snapshot"""
        # Create multiple snapshots
        await snapshot_manager.create_snapshot(
            execution_id="exec-latest-1",
            context_state={"version": 1},
            snapshot_type="checkpoint",
        )
        await snapshot_manager.create_snapshot(
            execution_id="exec-latest-1",
            context_state={"version": 2},
            snapshot_type="checkpoint",
        )
        latest = await snapshot_manager.create_snapshot(
            execution_id="exec-latest-1",
            context_state={"version": 3},
            snapshot_type="checkpoint",
        )
        
        result = await snapshot_manager.get_latest_snapshot("exec-latest-1")
        
        assert result is not None
        assert result.context_state["version"] == 3
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_get_latest_snapshot_nonexistent(
        self,
        snapshot_manager: ExecutionSnapshotManager,
    ):
        """Test retrieving latest snapshot for non-existent execution"""
        result = await snapshot_manager.get_latest_snapshot("non-existent-exec")
        
        assert result is None
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_restore_snapshot(
        self,
        snapshot_manager: ExecutionSnapshotManager,
        db_session: AsyncSession,
    ):
        """Test restoring execution from snapshot"""
        snapshot = await snapshot_manager.create_snapshot(
            execution_id="exec-restore-1",
            context_state={"restored": True, "counter": 100},
            snapshot_type="checkpoint",
        )
        
        context_manager = DistributedContextManager(db_session)
        
        # Add to manager's cache for restoration
        snapshot_manager._snapshots[snapshot.snapshot_id] = snapshot
        
        restored = await snapshot_manager.restore_snapshot(snapshot.snapshot_id)
        
        assert restored is not None
        assert restored["context_state"]["restored"] is True
        assert restored["context_state"]["counter"] == 100
        assert restored["sequence_number"] >= 0


# =============================================================================
# DistributedRuntimeService Tests
# =============================================================================

class TestDistributedRuntimeService:
    """Test suite for DistributedRuntimeService"""
    
    @pytest_asyncio.fixture
    async def service(
        self,
        db_session: AsyncSession,
    ) -> DistributedRuntimeService:
        """Create distributed runtime service for testing"""
        svc = DistributedRuntimeService(db_session)
        await svc.initialize()
        yield svc
        await svc.shutdown()
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_service_initialization(self, service: DistributedRuntimeService):
        """Test service initializes all sub-services"""
        assert service.context_manager is not None
        assert service.continuity_engine is not None
        assert service.lineage_synchronizer is not None
        assert service.identity_manager is not None
        assert service.coordinator is not None
        assert service.snapshot_manager is not None
    
    @pytest.mark.unit
    @pytest.mark.distributed
    async def test_get_runtime_summary(
        self,
        service: DistributedRuntimeService,
        db_session: AsyncSession,
    ):
        """Test getting runtime summary"""
        summary = await service.get_runtime_summary()
        
        assert summary is not None
        assert "active_contexts" in summary
        assert "active_sessions" in summary
        assert "active_graphs" in summary
        assert "active_identities" in summary
        assert "pending_coordinations" in summary


# =============================================================================
# Model Tests
# =============================================================================

class TestDistributedRuntimeModels:
    """Test suite for distributed runtime models"""
    
    @pytest.mark.unit
    @pytest.mark.distributed
    def test_context_scope_enum_values(self):
        """Test ContextScope enum has expected values"""
        assert ContextScope.SESSION.value == "session"
        assert ContextScope.WORKFLOW.value == "workflow"
        assert ContextScope.EXECUTION.value == "execution"
        assert ContextScope.NODE.value == "node"
    
    @pytest.mark.unit
    @pytest.mark.distributed
    def test_propagation_status_enum_values(self):
        """Test PropagationStatus enum has expected values"""
        assert PropagationStatus.PENDING.value == "pending"
        assert PropagationStatus.PROPAGATING.value == "propagating"
        assert PropagationStatus.PROPAGATED.value == "propagated"
        assert PropagationStatus.FAILED.value == "failed"
        assert PropagationStatus.EXPIRED.value == "expired"
    
    @pytest.mark.unit
    @pytest.mark.distributed
    def test_continuity_state_enum_values(self):
        """Test ContinuityState enum has expected values"""
        assert ContinuityState.ACTIVE.value == "active"
        assert ContinuityState.SUSPENDED.value == "suspended"
        assert ContinuityState.RECOVERING.value == "recovering"
        assert ContinuityState.TERMINATED.value == "terminated"
    
    @pytest.mark.unit
    @pytest.mark.distributed
    def test_sync_mode_enum_values(self):
        """Test SyncMode enum has expected values"""
        assert SyncMode.EAGER.value == "eager"
        assert SyncMode.LAZY.value == "lazy"
        assert SyncMode.EVENTUAL.value == "eventual"


# =============================================================================
# Data Class Tests
# =============================================================================

class TestDistributedRuntimeDataClasses:
    """Test suite for distributed runtime data classes"""
    
    @pytest.mark.unit
    @pytest.mark.distributed
    def test_context_propagation_result(self):
        """Test ContextPropagationResult dataclass"""
        result = ContextPropagationResult(
            success=True,
            context_id="ctx-result-1",
            propagated_to=["node1", "node2"],
            failed_nodes=[],
            latency_ms=25.5,
        )
        
        assert result.success is True
        assert result.context_id == "ctx-result-1"
        assert len(result.propagated_to) == 2
        assert result.latency_ms == 25.5
    
    @pytest.mark.unit
    @pytest.mark.distributed
    def test_lineage_node(self):
        """Test LineageNode dataclass"""
        start = datetime.utcnow()
        end = start + timedelta(seconds=1)
        
        node = LineageNode(
            node_id="lineage-node-1",
            execution_id="exec-1",
            node_type="process",
            status="completed",
            start_time=start,
            end_time=end,
            duration_ms=1000.0,
            dependencies=["dep1", "dep2"],
        )
        
        assert node.node_id == "lineage-node-1"
        assert node.status == "completed"
        assert node.duration_ms == 1000.0
        assert len(node.dependencies) == 2
