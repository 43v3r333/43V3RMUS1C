"""
Domain Event Models for audit and event sourcing.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.models.base import BaseModel


class DomainEvent(BaseModel):
    """
    Domain event store for audit and event sourcing.
    Maintains complete event history for debugging and analytics.
    """
    __tablename__ = "domain_events"
    
    # Event identification
    event_id = Column(String(100), nullable=False, unique=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    
    # Causation
    correlation_id = Column(String(100), nullable=True, index=True)
    causation_id = Column(String(100), nullable=True)
    
    # Source
    aggregate_type = Column(String(50), nullable=False, index=True)
    aggregate_id = Column(String(100), nullable=False, index=True)
    
    # Event data
    data = Column(JSON, nullable=False)
    metadata = Column(JSON, nullable=True)
    
    # Timing
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Source info
    source = Column(String(100), nullable=True)
    version = Column(String(20), default="1.0")
    
    # Indexes
    __table_args__ = (
        Index("ix_domain_events_aggregate", "aggregate_type", "aggregate_id"),
        Index("ix_domain_events_correlation", "correlation_id", "timestamp"),
        Index("ix_domain_events_type_time", "event_type", "timestamp"),
    )
    
    def __repr__(self) -> str:
        return f"<DomainEvent(id={self.event_id}, type={self.event_type})>"
    
    @classmethod
    def from_event(cls, event, aggregate_type: str, aggregate_id: str):
        """Create event record from EventBus event"""
        return cls(
            event_id=event.id,
            event_type=event.type.value if hasattr(event.type, 'value') else str(event.type),
            correlation_id=event.correlation_id,
            causation_id=event.causation_id,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            data=event.data,
            metadata=event.metadata,
            timestamp=event.timestamp,
            source=event.source,
            version=event.version
        )


class WorkerTelemetry(BaseModel):
    """
    Worker telemetry for monitoring and diagnostics.
    """
    __tablename__ = "worker_telemetry"
    
    # Worker identification
    worker_id = Column(String(100), nullable=False, index=True)
    worker_type = Column(String(50), nullable=False)
    
    # Metrics
    cpu_usage = Column(JSON, nullable=True)
    memory_usage = Column(JSON, nullable=True)
    gpu_usage = Column(JSON, nullable=True)
    
    # Job info
    current_job_id = Column(String(100), nullable=True)
    current_job_progress = Column(JSON, nullable=True)
    
    # Stats
    jobs_completed = Column(String(50), default="0")
    jobs_failed = Column(String(50), default="0")
    avg_job_duration = Column(String(50), nullable=True)
    
    # Health
    health_status = Column(String(20), default="healthy")
    health_details = Column(JSON, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self) -> str:
        return f"<WorkerTelemetry(worker_id={self.worker_id}, status={self.health_status})>"


class RenderGraph(BaseModel):
    """
    Render graph for complex render pipelines.
    Stores render dependency information.
    """
    __tablename__ = "render_graphs"
    
    # Graph identification
    graph_id = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    
    # Graph definition
    nodes = Column(JSON, nullable=False)  # List of render nodes
    edges = Column(JSON, nullable=False)  # Dependencies between nodes
    
    # Execution info
    status = Column(String(20), default="pending")
    current_node = Column(String(100), nullable=True)
    
    # Results
    outputs = Column(JSON, nullable=True)
    errors = Column(JSON, nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Ownership
    project_id = Column(PGUUID(as_uuid=True), nullable=True)
    created_by_id = Column(PGUUID(as_uuid=True), nullable=True)
    
    def __repr__(self) -> str:
        return f"<RenderGraph(id={self.graph_id}, name={self.name})>"