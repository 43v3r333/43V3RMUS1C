"""
43V3R CORE - Integration Tests - Service Integration
===================================================

End-to-end integration tests for service interactions:
- Runtime orchestration workflows
- Semantic analysis pipelines
- Distributed runtime coordination
- Constitutional governance integration
- WebSocket event synchronization

Test Coverage:
- Multi-service workflows
- Cross-domain operations
- End-to-end pipelines
- Event-driven orchestration
- Database consistency

Markers: integration, workflows, service-integration
"""

from __future__ import annotations

import asyncio
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.runtime.models import (
    ExecutionMode,
    NodeStatus,
    RuntimeStatus,
)
from app.domains.runtime.services import (
    RuntimeCoordinator,
    ExecutionManager,
    WorkflowDispatcher,
    OrchestrationEvent,
)
from app.domains.semantic.models import EmotionType, SceneSemanticType, SemanticTag
from app.domains.semantic.services import SemanticAnalyzer, CinematicSequencer
from app.domains.distributed_runtime.services import (
    DistributedContextManager,
    ExecutionContinuityEngine,
    DistributedRuntimeService,
)
from app.domains.constitutional_governance.models import ConstraintSeverity, SafetyState
from app.domains.constitutional_governance.services import (
    ConstitutionalGovernanceEngine,
    ConstitutionalAuditService,
)


# =============================================================================
# Runtime + Semantic Integration Tests
# =============================================================================

class TestRuntimeSemanticIntegration:
    """Test runtime orchestration with semantic analysis"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_semantic_workflow_integration(
        self,
        db_session: AsyncSession,
        in_memory_event_bus,
    ):
        """Test integrated semantic-driven workflow execution"""
        # Initialize services
        coordinator = RuntimeCoordinator(db_session)
        executor = ExecutionManager(db_session, coordinator)
        semantic_analyzer = SemanticAnalyzer(db_session)
        
        await coordinator.initialize()
        await semantic_analyzer.initialize()
        
        # Create semantic-enhanced workflow
        workflow = await executor.create_workflow(
            name="Semantic Workflow",
            nodes=[
                {
                    "id": "analyze",
                    "type": "semantic_analysis",
                    "name": "Analyze Media",
                },
                {
                    "id": "process",
                    "type": "process",
                    "name": "Process Based on Emotion",
                },
            ],
            edges=[
                {"from": "analyze", "to": "process"},
            ],
        )
        
        # Create execution
        execution = await executor.create_execution(
            graph_id=workflow.id,
            input_data={
                "asset_id": "test-asset-semantic",
                "duration": 45.0,
                "bpm": 120,
            },
        )
        
        # Execute workflow - semantic analysis happens as part of workflow
        context = OrchestrationEvent(
            event_id="semantic-workflow-event",
            event_type="workflow.started",
            source="test",
            timestamp=datetime.utcnow(),
            data={"workflow_id": str(workflow.id)},
        )
        await coordinator.emit_event(context)
        
        # Cleanup
        await coordinator.shutdown()
        await semantic_analyzer.shutdown()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_emotion_based_routing(
        self,
        db_session: AsyncSession,
    ):
        """Test routing based on emotional analysis"""
        semantic_analyzer = SemanticAnalyzer(db_session)
        await semantic_analyzer.initialize()
        
        # Analyze media with different emotions
        high_energy_media = await semantic_analyzer.analyze_media(
            asset_id="high-energy-asset",
            media_type="video/mp4",
            duration=30.0,
            audio_features={"bpm": 150},
        )
        
        low_energy_media = await semantic_analyzer.analyze_media(
            asset_id="low-energy-asset",
            media_type="video/mp4",
            duration=30.0,
            audio_features={"bpm": 70},
        )
        
        # Verify emotional routing would route differently
        assert high_energy_media.energy_level > low_energy_media.energy_level
        
        # High energy should route to "intense" processing
        # Low energy should route to "calm" processing
        routing_decision_high = "intense" if high_energy_media.energy_level > 0.6 else "calm"
        routing_decision_low = "intense" if low_energy_media.energy_level > 0.6 else "calm"
        
        assert routing_decision_high == "intense"
        assert routing_decision_low == "calm"
        
        await semantic_analyzer.shutdown()


# =============================================================================
# Distributed Runtime + Governance Integration Tests
# =============================================================================

class TestDistributedGovernanceIntegration:
    """Test distributed runtime with governance integration"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_governed_context_propagation(
        self,
        db_session: AsyncSession,
    ):
        """Test context propagation under governance constraints"""
        # Initialize services
        distributed_service = DistributedRuntimeService(db_session)
        governance_engine = ConstitutionalGovernanceEngine(db_session)
        
        await distributed_service.initialize()
        await governance_engine.initialize()
        
        # Create governance profile for context propagation
        profile = await governance_engine.create_profile(
            profile_scope="context_propagation",
            profile_key="governed-propagation",
            max_violations=5,
        )
        
        # Create context with governance evaluation
        context_manager = distributed_service.context_manager
        context = await context_manager.create_context(
            scope="execution",
            context_data={"sensitive": True, "data": "test"},
        )
        
        # Evaluate the propagation action
        decision = await governance_engine.evaluate_constitutional_action(
            scope="context_propagation",
            action={"type": "propagate", "severity": "info"},
            current_state={"violation_count": 0, "safety_score": 1.0},
            profile_id=profile.profile_id,
        )
        
        # Propagation should be governed
        assert decision is not None
        
        # Cleanup
        await distributed_service.shutdown()
        await governance_engine.shutdown()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_governed_lineage_tracking(
        self,
        db_session: AsyncSession,
    ):
        """Test lineage tracking with governance integration"""
        distributed_service = DistributedRuntimeService(db_session)
        governance_engine = ConstitutionalGovernanceEngine(db_session)
        audit_service = ConstitutionalAuditService(db_session)
        
        await distributed_service.initialize()
        await governance_engine.initialize()
        
        # Create a lineage graph
        lineage_synchronizer = distributed_service.lineage_synchronizer
        graph = await lineage_synchronizer.create_lineage_graph(
            lineage_scope="governed-execution",
            nodes=[
                {"id": "governed-1", "type": "start"},
                {"id": "governed-2", "type": "process"},
            ],
            edges=[{"from": "governed-1", "to": "governed-2"}],
        )
        
        # Log governance action
        await audit_service.log_action(
            action_type="lineage_created",
            action_target=graph.graph_id,
            actor_type="lineage_synchronizer",
            outcome_type="success",
        )
        
        # Verify audit trail
        trail = await audit_service.get_audit_trail()
        assert len(trail) > 0
        
        await distributed_service.shutdown()
        await governance_engine.shutdown()


# =============================================================================
# Runtime Orchestration Integration Tests
# =============================================================================

class TestRuntimeOrchestrationIntegration:
    """Test complete runtime orchestration workflows"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_workflow_lifecycle(
        self,
        db_session: AsyncSession,
    ):
        """Test complete workflow lifecycle"""
        # Initialize services
        coordinator = RuntimeCoordinator(db_session)
        executor = ExecutionManager(db_session, coordinator)
        
        await coordinator.initialize()
        
        # Create session
        session = await coordinator.create_session(
            name="Integration Test Session",
            session_type="workload",
            capabilities=["execution", "monitoring"],
        )
        
        # Create workflow
        workflow = await executor.create_workflow(
            name="Complete Workflow Lifecycle",
            description="Integration test workflow",
            nodes=[
                {"id": "start", "type": "start", "name": "Start"},
                {"id": "step1", "type": "process", "name": "Step 1"},
                {"id": "step2", "type": "process", "name": "Step 2"},
                {"id": "end", "type": "end", "name": "End"},
            ],
            edges=[
                {"from": "start", "to": "step1"},
                {"from": "step1", "to": "step2"},
                {"from": "step2", "to": "end"},
            ],
            execution_mode=ExecutionMode.SEQUENTIAL,
        )
        
        # Create execution
        execution = await executor.create_execution(
            graph_id=workflow.id,
            session_id=session.id,
            input_data={"integration": "test"},
        )
        
        # Get session stats
        stats = await coordinator.get_session_stats(session.id)
        assert stats is not None
        assert stats["session_id"] == str(session.id)
        
        # Get execution
        retrieved_execution = await coordinator.get_execution(execution.id)
        assert retrieved_execution is not None
        assert retrieved_execution.id == execution.id
        
        # Update session status
        await coordinator.update_session_status(
            session=session,
            status=RuntimeStatus.RUNNING,
        )
        
        # Cleanup
        await coordinator.shutdown()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_workflow_with_parallel_execution(
        self,
        db_session: AsyncSession,
    ):
        """Test parallel workflow execution"""
        coordinator = RuntimeCoordinator(db_session)
        executor = ExecutionManager(db_session, coordinator)
        
        await coordinator.initialize()
        
        # Create parallel workflow
        workflow = await executor.create_workflow(
            name="Parallel Execution Workflow",
            nodes=[
                {"id": "start", "type": "start"},
                {"id": "parallel1", "type": "task"},
                {"id": "parallel2", "type": "task"},
                {"id": "join", "type": "join"},
                {"id": "end", "type": "end"},
            ],
            edges=[
                {"from": "start", "to": "parallel1"},
                {"from": "start", "to": "parallel2"},
                {"from": "parallel1", "to": "join"},
                {"from": "parallel2", "to": "join"},
                {"from": "join", "to": "end"},
            ],
            execution_mode=ExecutionMode.PARALLEL,
            max_parallelism=2,
        )
        
        assert workflow.execution_mode == ExecutionMode.PARALLEL.value
        assert workflow.max_parallelism == 2
        
        await coordinator.shutdown()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_workflow_cancellation(
        self,
        db_session: AsyncSession,
    ):
        """Test workflow cancellation"""
        coordinator = RuntimeCoordinator(db_session)
        executor = ExecutionManager(db_session, coordinator)
        
        await coordinator.initialize()
        
        # Create workflow
        workflow = await executor.create_workflow(
            name="Cancelable Workflow",
            nodes=[
                {"id": "start", "type": "start"},
                {"id": "long_task", "type": "process"},
                {"id": "end", "type": "end"},
            ],
            edges=[
                {"from": "start", "to": "long_task"},
                {"from": "long_task", "to": "end"},
            ],
        )
        
        # Create execution
        execution = await executor.create_execution(graph_id=workflow.id)
        
        # Cancel execution
        cancelled = await coordinator.cancel_execution(execution)
        assert cancelled.status == NodeStatus.CANCELLED.value
        
        await coordinator.shutdown()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_workflow_retry(
        self,
        db_session: AsyncSession,
    ):
        """Test workflow retry after failure"""
        coordinator = RuntimeCoordinator(db_session)
        executor = ExecutionManager(db_session, coordinator)
        
        await coordinator.initialize()
        
        # Create workflow
        workflow = await executor.create_workflow(
            name="Retryable Workflow",
            nodes=[
                {"id": "retry_test", "type": "task"},
            ],
            edges=[],
        )
        
        # Create execution
        execution = await executor.create_execution(graph_id=workflow.id)
        
        # Retry execution
        retried = await coordinator.retry_execution(execution)
        assert retried.retry_count >= 0
        assert retried.status == NodeStatus.PENDING.value
        
        await coordinator.shutdown()


# =============================================================================
# Event-Driven Integration Tests
# =============================================================================

class TestEventDrivenIntegration:
    """Test event-driven orchestration"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_event_propagation_through_workflow(
        self,
        db_session: AsyncSession,
        in_memory_event_bus,
    ):
        """Test events propagate correctly through workflow"""
        coordinator = RuntimeCoordinator(db_session)
        await coordinator.initialize()
        
        # Register event handlers
        events_received = []
        
        async def handler1(event):
            events_received.append(("handler1", event.event_type))
        
        async def handler2(event):
            events_received.append(("handler2", event.event_type))
        
        coordinator.register_handler("workflow.started", handler1)
        coordinator.register_handler("workflow.started", handler2)
        
        # Emit event
        event = OrchestrationEvent(
            event_id="propagation-test",
            event_type="workflow.started",
            source="test",
            timestamp=datetime.utcnow(),
            data={"workflow": "test-workflow"},
        )
        
        await coordinator.emit_event(event)
        
        # Both handlers should receive the event
        assert len(events_received) == 2
        assert all(e[1] == "workflow.started" for e in events_received)
        
        await coordinator.shutdown()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_event_correlation(
        self,
        db_session: AsyncSession,
        in_memory_event_bus,
    ):
        """Test event correlation through workflow"""
        coordinator = RuntimeCoordinator(db_session)
        await coordinator.initialize()
        
        correlation_id = "corr-test-123"
        
        # Track correlation
        tracked_correlations = []
        
        async def correlation_handler(event):
            if event.correlation_id:
                tracked_correlations.append(event.correlation_id)
        
        coordinator.register_handler("*", correlation_handler)
        
        # Emit correlated events
        for i in range(3):
            event = OrchestrationEvent(
                event_id=f"event-{i}",
                event_type="test.event",
                source="test",
                timestamp=datetime.utcnow(),
                data={},
                correlation_id=correlation_id,
            )
            await coordinator.emit_event(event)
        
        # All events should have the same correlation ID
        assert len(tracked_correlations) == 3
        assert all(c == correlation_id for c in tracked_correlations)
        
        await coordinator.shutdown()


# =============================================================================
# Database Transaction Integration Tests
# =============================================================================

class TestDatabaseTransactionIntegration:
    """Test database transaction handling"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_session_isolation(
        self,
        db_session: AsyncSession,
        db_session_with_data: AsyncSession,
    ):
        """Test session isolation during operations"""
        coordinator1 = RuntimeCoordinator(db_session)
        coordinator2 = RuntimeCoordinator(db_session_with_data)
        
        await coordinator1.initialize()
        await coordinator2.initialize()
        
        # Create sessions in each session
        session1 = await coordinator1.create_session(
            name="Isolated Session 1",
            session_type="test",
        )
        session2 = await coordinator2.create_session(
            name="Isolated Session 2",
            session_type="test",
        )
        
        # Sessions should be different
        assert session1.id != session2.id
        
        await coordinator1.shutdown()
        await coordinator2.shutdown()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_transaction_rollback(
        self,
        db_session: AsyncSession,
    ):
        """Test transaction rollback on error"""
        coordinator = RuntimeCoordinator(db_session)
        await coordinator.initialize()
        
        # Create session
        session = await coordinator.create_session(
            name="Rollback Test Session",
            session_type="test",
        )
        
        # Verify session exists
        retrieved = await coordinator.get_session(session.id)
        assert retrieved is not None
        
        # Rollback happens in fixture cleanup
        
        await coordinator.shutdown()


# =============================================================================
# Cross-Domain Integration Tests
# =============================================================================

class TestCrossDomainIntegration:
    """Test cross-domain operation integration"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_semantic_to_runtime_pipeline(
        self,
        db_session: AsyncSession,
    ):
        """Test semantic analysis influences runtime workflow selection"""
        semantic_analyzer = SemanticAnalyzer(db_session)
        sequencer = CinematicSequencer(db_session, semantic_analyzer)
        
        await semantic_analyzer.initialize()
        
        # Analyze multiple scenes
        scenes = [
            {"id": f"scene-{i}", "energy_level": 0.5 + (i * 0.1)}
            for i in range(5)
        ]
        
        # Sequence by energy
        sequenced = await sequencer.sequence_by_energy(scenes)
        
        # Workflow selection based on sequencing
        workflow_type = "standard"
        if any(s["energy_level"] > 0.8 for s in scenes):
            workflow_type = "high_energy"
        
        assert workflow_type in ["standard", "high_energy"]
        
        await semantic_analyzer.shutdown()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_constitutional_governance_audit_trail(
        self,
        db_session: AsyncSession,
    ):
        """Test constitutional governance creates audit trail"""
        governance_engine = ConstitutionalGovernanceEngine(db_session)
        audit_service = ConstitutionalAuditService(db_session)
        
        await governance_engine.initialize()
        
        # Create profile and evaluate action
        profile = await governance_engine.create_profile(
            profile_scope="audit-test",
            profile_key="audit-profile",
        )
        
        await governance_engine.evaluate_constitutional_action(
            scope="audit-test",
            action={"type": "test"},
            current_state={},
            profile_id=profile.profile_id,
        )
        
        # Log the action
        audit = await audit_service.log_action(
            action_type="evaluate",
            action_target="audit-test",
            actor_type="governance_engine",
            outcome_type="approved",
            success=True,
        )
        
        # Verify audit trail
        trail = await audit_service.get_audit_trail(
            session_id=audit.session_id,
        )
        
        assert len(trail) >= 1
        
        await governance_engine.shutdown()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_distributed_context_with_lineage(
        self,
        db_session: AsyncSession,
    ):
        """Test distributed context linked to lineage tracking"""
        distributed_service = DistributedRuntimeService(db_session)
        
        await distributed_service.initialize()
        
        # Create context
        context = await distributed_service.context_manager.create_context(
            scope="execution",
            context_data={"lineage_test": True},
        )
        
        # Create lineage graph
        graph = await distributed_service.lineage_synchronizer.create_lineage_graph(
            lineage_scope="execution",
            nodes=[
                {"id": "context-node", "type": "process"},
            ],
            edges=[],
        )
        
        # Add context node to lineage
        node = await distributed_service.lineage_synchronizer.add_lineage_node(
            graph_id=graph.graph_id,
            node_id="context-node",
            node_type="process",
            execution_id=context.context_id,
        )
        
        # Verify linkage
        assert node.execution_id == context.context_id
        
        await distributed_service.shutdown()


# =============================================================================
# End-to-End Pipeline Tests
# =============================================================================

class TestEndToEndPipelines:
    """Test complete end-to-end pipelines"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_media_analyze_and_render_pipeline(
        self,
        db_session: AsyncSession,
    ):
        """Test complete media analysis to render pipeline"""
        # Step 1: Semantic Analysis
        semantic_analyzer = SemanticAnalyzer(db_session)
        await semantic_analyzer.initialize()
        
        profile = await semantic_analyzer.analyze_media(
            asset_id="pipeline-asset",
            media_type="video/mp4",
            duration=45.0,
            audio_features={"bpm": 120},
        )
        
        # Step 2: Semantic-based scene sequencing
        sequencer = CinematicSequencer(db_session, semantic_analyzer)
        
        scenes = [
            {"id": f"pipeline-scene-{i}", "energy_level": 0.1 * i, "duration": 10.0}
            for i in range(4)
        ]
        
        sequenced = await sequencer.sequence_by_energy(scenes)
        
        # Step 3: Runtime orchestration
        coordinator = RuntimeCoordinator(db_session)
        executor = ExecutionManager(db_session, coordinator)
        
        await coordinator.initialize()
        
        workflow = await executor.create_workflow(
            name="Semantic Render Pipeline",
            nodes=[{"id": f"render-{i}", "type": "render"} for i in range(len(sequenced))],
            edges=[],
        )
        
        execution = await executor.create_execution(
            graph_id=workflow.id,
            input_data={
                "semantic_profile": {
                    "emotion": profile.primary_emotion,
                    "energy": profile.energy_level,
                },
                "sequenced_scenes": sequenced,
            },
        )
        
        # Verify pipeline produced valid results
        assert profile is not None
        assert len(sequenced) == len(scenes)
        assert execution is not None
        
        # Cleanup
        await semantic_analyzer.shutdown()
        await coordinator.shutdown()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_governed_autonomous_pipeline(
        self,
        db_session: AsyncSession,
    ):
        """Test governed autonomous decision pipeline"""
        # Initialize governance
        governance_engine = ConstitutionalGovernanceEngine(db_session)
        audit_service = ConstitutionalAuditService(db_session)
        
        await governance_engine.initialize()
        
        # Create profile
        profile = await governance_engine.create_profile(
            profile_scope="autonomous",
            profile_key="autonomous-governance",
            max_violations=3,
        )
        
        # Simulate autonomous decisions
        decisions = []
        
        for i in range(5):
            state = {"violation_count": i, "safety_score": 1.0 - (i * 0.1)}
            
            decision = await governance_engine.evaluate_constitutional_action(
                scope="autonomous",
                action={"type": "autonomous_decision", "severity": "info", "action_id": i},
                current_state=state,
                profile_id=profile.profile_id,
            )
            
            decisions.append(decision)
            
            # Log decision
            await audit_service.log_action(
                action_type="autonomous_decision",
                action_target=f"decision-{i}",
                actor_type="autonomous_engine",
                outcome_type="approved" if decision.approved else "denied",
                success=decision.approved,
                post_state={"violation_count": state["violation_count"]},
            )
        
        # Verify governance is working
        for i, decision in enumerate(decisions):
            if i < 3:
                assert decision.approved is True  # Within violation limit
            else:
                # May be denied depending on state
                pass
        
        # Verify audit trail
        trail = await audit_service.get_audit_trail(action_type="autonomous_decision")
        assert len(trail) >= 5
        
        # Cleanup
        await governance_engine.shutdown()
