"""
43V3R CORE - Observability Domain Unit Tests
==========================================

Comprehensive unit tests for observability systems:
- Telemetry collection
- Distributed tracing
- Metrics aggregation
- Log management
- Health monitoring

Test Coverage:
- Telemetry data collection
- Trace propagation
- Metric aggregation
- Health checks
- Alert generation

Markers: unit, observability, telemetry
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.observability.models import (
    TraceStatus,
    MetricType,
    AlertSeverity,
    ExecutionTrace,
    TelemetryEvent,
    RuntimeMetric,
    OrchestrationMetric,
    HealthCheck,
    Alert,
    LogEntry,
)
from app.domains.observability.services import (
    TelemetryCollector,
    RuntimeStateManager,
)


# =============================================================================
# TelemetryCollector Tests
# =============================================================================

class TestTelemetryCollector:
    """Test suite for TelemetryCollector"""
    
    @pytest_asyncio.fixture
    async def collector(
        self,
        db_session: AsyncSession,
    ) -> TelemetryCollector:
        """Create telemetry collector for testing"""
        coll = TelemetryCollector(db_session)
        await coll.initialize()
        yield coll
        await coll.shutdown()
    
    # ----------------------------------------------------------------
    # Initialization Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_collector_initialization(self, collector: TelemetryCollector):
        """Test collector initializes correctly"""
        assert collector is not None
        assert collector._running is True
        assert isinstance(collector._active_traces, dict)
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_collector_shutdown(self, collector: TelemetryCollector):
        """Test collector shuts down gracefully"""
        await collector.shutdown()
        assert collector._running is False
    
    # ----------------------------------------------------------------
    # Distributed Tracing Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_start_trace(
        self,
        collector: TelemetryCollector,
        db_session: AsyncSession,
    ):
        """Test starting a trace span"""
        span = await collector.start_trace(
            operation_name="test.operation",
            operation_type="test",
            service_name="test-service",
        )
        
        assert span is not None
        assert span.operation_name == "test.operation"
        assert span.service_name == "test-service"
        assert span.trace_id is not None
        assert span.span_id is not None
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_start_trace_with_parent(
        self,
        collector: TelemetryCollector,
        db_session: AsyncSession,
    ):
        """Test starting trace with parent span"""
        parent = await collector.start_trace(
            operation_name="parent.operation",
            operation_type="test",
            service_name="test-service",
        )
        
        child = await collector.start_trace(
            operation_name="child.operation",
            operation_type="test",
            service_name="test-service",
            parent_span_id=parent.span_id,
        )
        
        assert child.parent_span_id == parent.span_id
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_end_trace(
        self,
        collector: TelemetryCollector,
        db_session: AsyncSession,
    ):
        """Test ending a trace span"""
        span = await collector.start_trace(
            operation_name="end.test",
            operation_type="test",
            service_name="test-service",
        )
        
        trace = await collector.end_trace(
            span=span,
            status=TraceStatus.COMPLETED,
        )
        
        assert trace is not None
        assert trace.status == TraceStatus.COMPLETED.value
        assert trace.duration_ms is not None
        assert span.span_id not in collector._active_traces
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_end_trace_with_error(
        self,
        collector: TelemetryCollector,
        db_session: AsyncSession,
    ):
        """Test ending trace with error"""
        span = await collector.start_trace(
            operation_name="error.test",
            operation_type="test",
            service_name="test-service",
        )
        
        trace = await collector.end_trace(
            span=span,
            status=TraceStatus.FAILED,
            error="Test error",
        )
        
        assert trace.status == TraceStatus.FAILED.value
        assert trace.error_message == "Test error"
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_get_trace(
        self,
        collector: TelemetryCollector,
        db_session: AsyncSession,
    ):
        """Test retrieving trace by ID"""
        span = await collector.start_trace(
            operation_name="get.trace",
            operation_type="test",
            service_name="test-service",
        )
        
        await collector.end_trace(span=span)
        
        trace = await collector.get_trace(span.trace_id)
        
        assert len(trace) >= 1
    
    # ----------------------------------------------------------------
    # Metrics Collection Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_record_counter(
        self,
        collector: TelemetryCollector,
        db_session: AsyncSession,
    ):
        """Test recording counter metric"""
        metric = await collector.record_counter(
            name="test.counter",
            value=1.0,
            source="test-source",
        )
        
        assert metric is not None
        assert metric.metric_name == "test.counter"
        assert metric.value == 1.0
        assert metric.metric_type == MetricType.COUNTER.value
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_record_gauge(
        self,
        collector: TelemetryCollector,
        db_session: AsyncSession,
    ):
        """Test recording gauge metric"""
        metric = await collector.record_gauge(
            name="test.gauge",
            value=50.0,
            source="test-source",
        )
        
        assert metric is not None
        assert metric.metric_name == "test.gauge"
        assert metric.metric_type == MetricType.GAUGE.value
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_record_histogram(
        self,
        collector: TelemetryCollector,
        db_session: AsyncSession,
    ):
        """Test recording histogram metric"""
        metric = await collector.record_histogram(
            name="test.histogram",
            value=100.0,
            source="test-source",
        )
        
        assert metric is not None
        assert metric.metric_name == "test.histogram"
        assert metric.metric_type == MetricType.HISTOGRAM.value
    
    # ----------------------------------------------------------------
    # Alert Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_create_alert(
        self,
        collector: TelemetryCollector,
        db_session: AsyncSession,
    ):
        """Test creating alert"""
        alert = await collector.create_alert(
            name="Test Alert",
            alert_type="test",
            severity=AlertSeverity.WARNING,
            source="test-source",
            description="Test alert description",
        )
        
        assert alert is not None
        assert alert.name == "Test Alert"
        assert alert.severity == AlertSeverity.WARNING.value
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_get_active_alerts(
        self,
        collector: TelemetryCollector,
        db_session: AsyncSession,
    ):
        """Test retrieving active alerts"""
        await collector.create_alert(
            name="Active Alert",
            alert_type="test",
            severity=AlertSeverity.ERROR,
            source="test-source",
        )
        
        alerts = await collector.get_active_alerts()
        
        assert len(alerts) >= 1
        assert all(a.is_resolved is False for a in alerts)
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_resolve_alert(
        self,
        collector: TelemetryCollector,
        db_session: AsyncSession,
    ):
        """Test resolving alert"""
        alert = await collector.create_alert(
            name="Resolve Test",
            alert_type="test",
            severity=AlertSeverity.INFO,
            source="test-source",
        )
        
        resolved = await collector.resolve_alert(alert.alert_id)
        
        assert resolved is not None
        assert resolved.is_resolved is True
        assert resolved.resolved_at is not None
    
    # ----------------------------------------------------------------
    # Event Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_record_event(
        self,
        collector: TelemetryCollector,
        db_session: AsyncSession,
    ):
        """Test recording telemetry event"""
        event = await collector.record_event(
            event_type="test.event",
            source="test-source",
            source_type="test",
            category="test",
            data={"key": "value"},
        )
        
        assert event is not None
        assert event.event_type == "test.event"
        assert event.source == "test-source"
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_get_events(
        self,
        collector: TelemetryCollector,
        db_session: AsyncSession,
    ):
        """Test retrieving events"""
        await collector.record_event(
            event_type="retrieve.event",
            source="test-source",
            source_type="test",
            category="test",
        )
        
        events = await collector.get_events()
        
        assert len(events) >= 1
    
    # ----------------------------------------------------------------
    # Logging Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_log(
        self,
        collector: TelemetryCollector,
        db_session: AsyncSession,
    ):
        """Test logging entry"""
        entry = await collector.log(
            level="INFO",
            message="Test log message",
            logger_name="test.logger",
            source="test-source",
        )
        
        assert entry is not None
        assert entry.level == "INFO"
        assert entry.message == "Test log message"
    
    # ----------------------------------------------------------------
    # Orchestration Metrics Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_record_orchestration_metric(
        self,
        collector: TelemetryCollector,
        db_session: AsyncSession,
    ):
        """Test recording orchestration metric"""
        metric = await collector.record_orchestration_metric(
            metric_name="orchestration.test",
            value=100.0,
            category="test",
            session_id="test-session",
        )
        
        assert metric is not None
        assert metric.metric_name == "orchestration.test"
        assert metric.session_id == "test-session"
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_get_orchestration_stats(
        self,
        collector: TelemetryCollector,
        db_session: AsyncSession,
    ):
        """Test getting orchestration statistics"""
        session_id = "stats-test-session"
        
        await collector.record_orchestration_metric(
            metric_name="metric.1",
            value=100.0,
            category="test",
            session_id=session_id,
        )
        await collector.record_orchestration_metric(
            metric_name="metric.1",
            value=200.0,
            category="test",
            session_id=session_id,
        )
        
        stats = await collector.get_orchestration_stats(session_id)
        
        assert "metric.1" in stats
        assert stats["metric.1"]["count"] == 2
    
    # ----------------------------------------------------------------
    # Observer Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_add_remove_observer(self, collector: TelemetryCollector):
        """Test adding and removing observers"""
        async def observer(span):
            pass
        
        collector.add_observer(observer)
        assert len(collector._observers) == 1
        
        collector.remove_observer(observer)
        assert len(collector._observers) == 0


# =============================================================================
# RuntimeStateManager Tests
# =============================================================================

class TestRuntimeStateManager:
    """Test suite for RuntimeStateManager"""
    
    @pytest_asyncio.fixture
    async def state_manager(
        self,
        db_session: AsyncSession,
    ) -> RuntimeStateManager:
        """Create state manager for testing"""
        manager = RuntimeStateManager(db_session)
        await manager.initialize()
        yield manager
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_state_manager_initialization(
        self,
        state_manager: RuntimeStateManager,
    ):
        """Test state manager initializes correctly"""
        assert state_manager is not None
        assert isinstance(state_manager._state_cache, dict)
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_set_and_get_state(
        self,
        state_manager: RuntimeStateManager,
    ):
        """Test setting and getting state"""
        await state_manager.set_state(
            key="test-key",
            value={"data": "value"},
        )
        
        state = await state_manager.get_state("test-key")
        
        assert state is not None
        assert state["value"]["data"] == "value"
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_update_state(
        self,
        state_manager: RuntimeStateManager,
    ):
        """Test updating state"""
        await state_manager.set_state(
            key="update-key",
            value={"initial": True},
        )
        
        await state_manager.update_state(
            key="update-key",
            updates={"updated": True},
        )
        
        state = await state_manager.get_state("update-key")
        
        assert state["value"]["initial"] is True
        assert state["value"]["updated"] is True
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_delete_state(
        self,
        state_manager: RuntimeStateManager,
    ):
        """Test deleting state"""
        await state_manager.set_state(
            key="delete-key",
            value={"data": "test"},
        )
        
        await state_manager.delete_state("delete-key")
        
        state = await state_manager.get_state("delete-key")
        assert state is None
    
    @pytest.mark.unit
    @pytest.mark.observability
    async def test_list_states(
        self,
        state_manager: RuntimeStateManager,
    ):
        """Test listing states"""
        await state_manager.set_state(key="prefix:test1", value={})
        await state_manager.set_state(key="prefix:test2", value={})
        await state_manager.set_state(key="other:key", value={})
        
        prefixed = await state_manager.list_states(prefix="prefix:")
        
        assert len(prefixed) == 2
        assert "prefix:test1" in prefixed
        assert "prefix:test2" in prefixed
