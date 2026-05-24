"""
Observability Services - Production-grade telemetry and monitoring
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from .models import (
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

logger = logging.getLogger(__name__)


@dataclass
class TraceSpan:
    """Trace span for distributed tracing"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    operation_type: str
    service_name: str
    start_time: datetime
    attributes: Dict[str, Any] = field(default_factory=dict)
    end_time: Optional[datetime] = None
    status: str = TraceStatus.STARTED.value
    error: Optional[str] = None


class TelemetryCollector:
    """
    Production-grade telemetry collector.
    Handles distributed tracing, metrics collection, and event streaming.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._active_traces: Dict[str, TraceSpan] = {}
        self._metrics_buffer: deque = deque(maxlen=1000)
        self._observers: List[Callable] = []
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize the telemetry collector"""
        self._running = True
        logger.info("TelemetryCollector initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the telemetry collector"""
        self._running = False
        logger.info("TelemetryCollector shutdown")
    
    # ==================== Distributed Tracing ====================
    
    async def start_trace(
        self,
        operation_name: str,
        operation_type: str,
        service_name: str,
        parent_span_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> TraceSpan:
        """Start a new trace span"""
        trace_id = str(uuid4())
        span_id = str(uuid4())
        
        span = TraceSpan(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            operation_type=operation_type,
            service_name=service_name,
            start_time=datetime.utcnow(),
            attributes=attributes or {},
        )
        
        self._active_traces[span_id] = span
        
        # Create trace record
        trace = ExecutionTrace(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            service_name=service_name,
            operation_name=operation_name,
            operation_type=operation_type,
            start_time=span.start_time,
            status=TraceStatus.STARTED.value,
            resource_id=resource_id,
            user_id=user_id,
            attributes=attributes,
        )
        
        self.db.add(trace)
        await self.db.commit()
        
        return span
    
    async def end_trace(
        self,
        span: TraceSpan,
        status: TraceStatus = TraceStatus.COMPLETED,
        error: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> ExecutionTrace:
        """End a trace span"""
        span.end_time = datetime.utcnow()
        span.status = status.value
        span.error = error
        
        if attributes:
            span.attributes.update(attributes)
        
        # Calculate duration
        duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
        
        # Update or create trace record
        result = await self.db.execute(
            select(ExecutionTrace).where(ExecutionTrace.span_id == span.span_id)
        )
        trace = result.scalar_one_or_none()
        
        if trace:
            trace.end_time = span.end_time
            trace.duration_ms = duration_ms
            trace.status = status.value
            trace.error_message = error
            if attributes:
                trace.attributes = span.attributes
            self.db.add(trace)
        else:
            trace = ExecutionTrace(
                trace_id=span.trace_id,
                span_id=span.span_id,
                parent_span_id=span.parent_span_id,
                service_name=span.service_name,
                operation_name=span.operation_name,
                operation_type=span.operation_type,
                start_time=span.start_time,
                end_time=span.end_time,
                duration_ms=duration_ms,
                status=status.value,
                error_message=error,
                attributes=span.attributes,
            )
            self.db.add(trace)
        
        await self.db.commit()
        
        # Remove from active traces
        if span.span_id in self._active_traces:
            del self._active_traces[span.span_id]
        
        # Notify observers
        for observer in self._observers:
            try:
                result_data = observer(span)
                if asyncio.iscoroutine(result_data):
                    await result_data
            except Exception as e:
                logger.error(f"Trace observer error: {e}")
        
        return trace
    
    async def get_trace(self, trace_id: str) -> List[ExecutionTrace]:
        """Get all spans for a trace"""
        result = await self.db.execute(
            select(ExecutionTrace)
            .where(ExecutionTrace.trace_id == trace_id)
            .order_by(ExecutionTrace.start_time)
        )
        return list(result.scalars().all())
    
    async def get_execution_trace(self, execution_id: str) -> List[ExecutionTrace]:
        """Get execution trace"""
        result = await self.db.execute(
            select(ExecutionTrace)
            .where(ExecutionTrace.execution_id == execution_id)
            .order_by(ExecutionTrace.start_time)
        )
        return list(result.scalars().all())
    
    # ==================== Metrics Collection ====================
    
    async def record_metric(
        self,
        metric_name: str,
        value: float,
        metric_type: MetricType,
        source: str,
        source_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        unit: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        labels: Optional[Dict[str, str]] = None,
    ) -> RuntimeMetric:
        """Record a metric"""
        metric = RuntimeMetric(
            metric_name=metric_name,
            metric_type=metric_type.value,
            value=value,
            unit=unit,
            source=source,
            source_type=source_type,
            resource_id=resource_id,
            resource_type=resource_type,
            tags=tags,
            labels=labels,
            timestamp=datetime.utcnow(),
        )
        
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        
        return metric
    
    async def record_counter(
        self,
        name: str,
        value: float = 1.0,
        source: str = "system",
        tags: Optional[Dict[str, str]] = None,
    ) -> RuntimeMetric:
        """Record a counter metric"""
        return await self.record_metric(
            metric_name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            source=source,
            tags=tags,
        )
    
    async def record_gauge(
        self,
        name: str,
        value: float,
        source: str = "system",
        tags: Optional[Dict[str, str]] = None,
    ) -> RuntimeMetric:
        """Record a gauge metric"""
        return await self.record_metric(
            metric_name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            source=source,
            tags=tags,
        )
    
    async def record_histogram(
        self,
        name: str,
        value: float,
        source: str = "system",
        tags: Optional[Dict[str, str]] = None,
    ) -> RuntimeMetric:
        """Record a histogram metric"""
        return await self.record_metric(
            metric_name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            source=source,
            tags=tags,
        )
    
    async def get_metrics(
        self,
        metric_name: Optional[str] = None,
        source: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[RuntimeMetric]:
        """Get metrics with filtering"""
        query = select(RuntimeMetric)
        
        if metric_name:
            query = query.where(RuntimeMetric.metric_name == metric_name)
        if source:
            query = query.where(RuntimeMetric.source == source)
        if since:
            query = query.where(RuntimeMetric.timestamp >= since)
        if until:
            query = query.where(RuntimeMetric.timestamp <= until)
        
        query = query.order_by(RuntimeMetric.timestamp.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_metric_aggregates(
        self,
        metric_name: str,
        since: datetime,
        until: Optional[datetime] = None,
        aggregation: str = "avg",
    ) -> Dict[str, float]:
        """Get aggregated metric values"""
        query = select(RuntimeMetric).where(
            RuntimeMetric.metric_name == metric_name,
            RuntimeMetric.timestamp >= since,
        )
        
        if until:
            query = query.where(RuntimeMetric.timestamp <= until)
        
        result = await self.db.execute(query)
        metrics = list(result.scalars().all())
        
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        if aggregation == "avg":
            return {"avg": sum(values) / len(values)}
        elif aggregation == "sum":
            return {"sum": sum(values)}
        elif aggregation == "min":
            return {"min": min(values)}
        elif aggregation == "max":
            return {"max": max(values)}
        elif aggregation == "count":
            return {"count": len(values)}
        
        return {}
    
    # ==================== Event Telemetry ====================
    
    async def emit_event(
        self,
        event_type: str,
        category: str,
        source: str,
        source_type: str,
        severity: AlertSeverity = AlertSeverity.INFO,
        data: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, float]] = None,
        correlation_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> TelemetryEvent:
        """Emit a telemetry event"""
        event = TelemetryEvent(
            event_id=str(uuid4()),
            event_type=event_type,
            category=category,
            source=source,
            source_type=source_type,
            severity=severity.value,
            timestamp=datetime.utcnow(),
            data=data,
            metrics=metrics,
            correlation_id=correlation_id,
            session_id=session_id,
            user_id=user_id,
        )
        
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        
        # Notify observers
        for observer in self._observers:
            try:
                result = observer(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Event observer error: {e}")
        
        return event
    
    async def get_events(
        self,
        event_type: Optional[str] = None,
        source: Optional[str] = None,
        severity: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[TelemetryEvent]:
        """Get telemetry events"""
        query = select(TelemetryEvent)
        
        if event_type:
            query = query.where(TelemetryEvent.event_type == event_type)
        if source:
            query = query.where(TelemetryEvent.source == source)
        if severity:
            query = query.where(TelemetryEvent.severity == severity)
        if since:
            query = query.where(TelemetryEvent.timestamp >= since)
        
        query = query.order_by(TelemetryEvent.timestamp.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    # ==================== Health Monitoring ====================
    
    async def record_health_check(
        self,
        service_name: str,
        service_type: str,
        status: str,
        is_healthy: bool,
        checks: Optional[Dict[str, Any]] = None,
        dependencies: Optional[Dict[str, bool]] = None,
        response_time_ms: Optional[float] = None,
        uptime_seconds: Optional[float] = None,
    ) -> HealthCheck:
        """Record a health check"""
        health = HealthCheck(
            service_name=service_name,
            service_type=service_type,
            status=status,
            is_healthy=is_healthy,
            checks=checks,
            dependencies=dependencies,
            response_time_ms=response_time_ms,
            uptime_seconds=uptime_seconds,
            checked_at=datetime.utcnow(),
        )
        
        self.db.add(health)
        await self.db.commit()
        await self.db.refresh(health)
        
        return health
    
    async def get_health_status(self, service_name: Optional[str] = None) -> List[HealthCheck]:
        """Get health status"""
        query = select(HealthCheck)
        
        if service_name:
            query = query.where(HealthCheck.service_name == service_name)
        
        query = query.order_by(HealthCheck.checked_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    # ==================== Alerts ====================
    
    async def create_alert(
        self,
        name: str,
        alert_type: str,
        severity: AlertSeverity,
        source: str,
        source_type: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
        resource_id: Optional[str] = None,
        execution_id: Optional[str] = None,
    ) -> Alert:
        """Create an alert"""
        alert = Alert(
            name=name,
            alert_type=alert_type,
            severity=severity.value,
            source=source,
            source_type=source_type,
            title=title,
            description=description,
            metrics=metrics,
            resource_id=resource_id,
            execution_id=execution_id,
            triggered_at=datetime.utcnow(),
        )
        
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        
        return alert
    
    async def resolve_alert(
        self,
        alert: Alert,
        acknowledged_by: Optional[str] = None,
    ) -> Alert:
        """Resolve an alert"""
        alert.is_resolved = True
        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()
        alert.acknowledged = True
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.utcnow()
        
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        
        return alert
    
    async def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        source: Optional[str] = None,
    ) -> List[Alert]:
        """Get active alerts"""
        query = select(Alert).where(Alert.is_resolved == False)
        
        if severity:
            query = query.where(Alert.severity == severity.value)
        if source:
            query = query.where(Alert.source == source)
        
        query = query.order_by(Alert.triggered_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    # ==================== Logging ====================
    
    async def log(
        self,
        level: str,
        message: str,
        logger_name: str,
        source: str,
        context: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> LogEntry:
        """Log an entry"""
        entry = LogEntry(
            log_id=str(uuid4()),
            logger=logger_name,
            source=source,
            level=level,
            message=message,
            context=context,
            trace_id=trace_id,
            span_id=span_id,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            resource_id=resource_id,
            resource_type=resource_type,
        )
        
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        
        return entry
    
    # ==================== Observers ====================
    
    def add_observer(self, observer: Callable) -> None:
        """Add an event observer"""
        self._observers.append(observer)
    
    def remove_observer(self, observer: Callable) -> None:
        """Remove an event observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    # ==================== Orchestration Metrics ====================
    
    async def record_orchestration_metric(
        self,
        metric_name: str,
        value: float,
        category: str,
        session_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> OrchestrationMetric:
        """Record an orchestration metric"""
        metric = OrchestrationMetric(
            metric_name=metric_name,
            value=value,
            category=category,
            session_id=session_id,
            execution_id=execution_id,
            tags=tags,
            timestamp=datetime.utcnow(),
        )
        
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        
        return metric
    
    async def get_orchestration_stats(
        self,
        session_id: str,
    ) -> Dict[str, Any]:
        """Get orchestration statistics"""
        # Get executions
        result = await self.db.execute(
            select(OrchestrationMetric).where(
                OrchestrationMetric.session_id == session_id
            )
        )
        metrics = list(result.scalars().all())
        
        # Aggregate by metric name
        aggregated: Dict[str, List[float]] = {}
        for metric in metrics:
            if metric.metric_name not in aggregated:
                aggregated[metric.metric_name] = []
            aggregated[metric.metric_name].append(metric.value)
        
        stats = {}
        for name, values in aggregated.items():
            stats[name] = {
                "count": len(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "sum": sum(values),
            }
        
        return stats
    
    # ==================== Dashboard Data ====================
    
    async def get_dashboard_metrics(
        self,
        since: datetime,
    ) -> Dict[str, Any]:
        """Get dashboard metrics for the time period"""
        # Error rate
        error_traces = await self.db.execute(
            select(ExecutionTrace).where(
                ExecutionTrace.status == TraceStatus.FAILED.value,
                ExecutionTrace.start_time >= since,
            )
        )
        error_count = len(list(error_traces.scalars().all()))
        
        total_traces = await self.db.execute(
            select(func.count(ExecutionTrace.id)).where(
                ExecutionTrace.start_time >= since
            )
        )
        total_count = total_traces.scalar() or 0
        
        # Average duration
        duration_result = await self.db.execute(
            select(func.avg(ExecutionTrace.duration_ms)).where(
                ExecutionTrace.start_time >= since,
                ExecutionTrace.duration_ms.isnot(None),
            )
        )
        avg_duration = duration_result.scalar() or 0
        
        # Active alerts
        active_alerts = await self.get_active_alerts()
        
        # Recent events
        recent_events = await self.get_events(since=since, limit=50)
        
        return {
            "time_range": {
                "since": since.isoformat(),
                "until": datetime.utcnow().isoformat(),
            },
            "traces": {
                "total": total_count,
                "errors": error_count,
                "error_rate": error_count / total_count if total_count > 0 else 0,
            },
            "performance": {
                "avg_duration_ms": avg_duration,
            },
            "alerts": {
                "active": len(active_alerts),
                "critical": len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL.value]),
                "warning": len([a for a in active_alerts if a.severity == AlertSeverity.WARNING.value]),
            },
            "recent_events": len(recent_events),
        }


class RuntimeStateManager:
    """
    Runtime state coordination manager.
    Manages distributed runtime state and coordination.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._state_cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize the state manager"""
        logger.info("RuntimeStateManager initialized")
    
    # ==================== State Operations ====================
    
    async def set_state(
        self,
        key: str,
        value: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Set runtime state"""
        async with self._lock:
            self._state_cache[key] = {
                "value": value,
                "updated_at": datetime.utcnow(),
                "ttl": ttl_seconds,
            }
    
    async def get_state(self, key: str) -> Optional[Dict[str, Any]]:
        """Get runtime state"""
        return self._state_cache.get(key)
    
    async def delete_state(self, key: str) -> None:
        """Delete runtime state"""
        async with self._lock:
            if key in self._state_cache:
                del self._state_cache[key]
    
    async def update_state(
        self,
        key: str,
        updates: Dict[str, Any],
    ) -> None:
        """Update runtime state"""
        async with self._lock:
            if key in self._state_cache:
                self._state_cache[key]["value"].update(updates)
                self._state_cache[key]["updated_at"] = datetime.utcnow()
            else:
                self._state_cache[key] = {
                    "value": updates,
                    "updated_at": datetime.utcnow(),
                    "ttl": None,
                }
    
    async def list_states(
        self,
        prefix: Optional[str] = None,
    ) -> List[str]:
        """List runtime state keys"""
        if prefix:
            return [k for k in self._state_cache.keys() if k.startswith(prefix)]
        return list(self._state_cache.keys())