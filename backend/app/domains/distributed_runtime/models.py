"""
Distributed Runtime Propagation Models - Execution continuity and context propagation.

Provides:
- Distributed context propagation
- Orchestration continuity engine
- Runtime lineage synchronization
- Semantic execution tracking
- Execution identity propagation
- Cross-service cognition coordination
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class ContextScope(str, Enum):
    """Context scope levels"""
    SESSION = "session"
    WORKFLOW = "workflow"
    EXECUTION = "execution"
    NODE = "node"


class PropagationStatus(str, Enum):
    """Propagation status"""
    PENDING = "pending"
    PROPAGATING = "propagating"
    PROPAGATED = "propagated"
    FAILED = "failed"
    EXPIRED = "expired"


class ContinuityState(str, Enum):
    """Orchestration continuity state"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    RECOVERING = "recovering"
    TERMINATED = "terminated"


class SyncMode(str, Enum):
    """Synchronization mode"""
    EAGER = "eager"
    LAZY = "lazy"
    EVENTUAL = "eventual"


class DistributedContextState(BaseModel):
    """Distributed context state - tracks context across nodes"""
    __tablename__ = "distributed_context_states"
    
    # Context identification
    context_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    scope: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Origin
    origin_node_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    origin_service: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Context data
    context_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    context_version: Mapped[int] = mapped_column(Integer, default=1)
    
    # Propagation state
    propagation_status: Mapped[str] = mapped_column(String(20), default=PropagationStatus.PENDING.value, index=True)
    propagation_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Visited nodes
    visited_nodes: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    last_propagated_to: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    # Lifecycle
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    
    # Index for context queries
    __table_args__ = (
        Index('ix_distributed_context_scope_origin', 'scope', 'origin_node_id'),
    )


class RuntimePropagationSession(BaseModel):
    """Runtime propagation session - manages context propagation lifecycle"""
    __tablename__ = "runtime_propagation_sessions"
    
    # Session identification
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    execution_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Synchronization
    sync_mode: Mapped[str] = mapped_column(String(20), default=SyncMode.LAZY.value)
    
    # State
    continuity_state: Mapped[str] = mapped_column(String(20), default=ContinuityState.ACTIVE.value, index=True)
    
    # Contexts in session
    context_count: Mapped[int] = mapped_column(Integer, default=0)
    propagated_contexts: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Nodes involved
    involved_nodes: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    current_node_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    # Metrics
    propagation_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    propagation_failures: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    terminated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Index for session queries
    __table_args__ = (
        Index('ix_propagation_session_workflow', 'workflow_id', 'created_at'),
        Index('ix_propagation_session_correlation', 'correlation_id', 'created_at'),
    )


class OrchestrationLineageGraph(BaseModel):
    """Orchestration lineage graph - tracks execution lineage across distributed nodes"""
    __tablename__ = "orchestration_lineage_graphs"
    
    # Graph identification
    graph_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Scope
    lineage_scope: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    parent_graph_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Nodes in lineage
    nodes: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=False)
    node_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Edges/relationships
    edges: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=False)
    edge_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Versioning
    version: Mapped[int] = mapped_column(Integer, default=1)
    root_node_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Status
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    is_forked: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ExecutionIdentity(BaseModel):
    """Execution identity - propagates identity through distributed execution"""
    __tablename__ = "execution_identities"
    
    # Identity identification
    identity_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Identity type
    identity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Properties
    properties: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Lineage
    lineage_chain: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Propagation
    propagation_path: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Metrics
    propagation_count: Mapped[int] = mapped_column(Integer, default=0)
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    last_accessed: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ContextPropagationPolicy(BaseModel):
    """Context propagation policy - rules for context distribution"""
    __tablename__ = "context_propagation_policies"
    
    # Policy identification
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Scope
    scope: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    applies_to_workflows: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    applies_to_nodes: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Propagation rules
    propagation_mode: Mapped[str] = mapped_column(String(20), default=SyncMode.LAZY.value)
    target_nodes: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Data selection
    included_fields: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    excluded_fields: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    transformations: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    propagation_timeout_ms: Mapped[int] = mapped_column(Integer, default=5000)
    retry_count: Mapped[int] = mapped_column(Integer, default=3)
    retry_delay_ms: Mapped[int] = mapped_column(Integer, default=1000)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metrics
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class RuntimeLineageNode(BaseModel):
    """Runtime lineage node - individual node in execution lineage"""
    __tablename__ = "runtime_lineage_nodes"
    
    # Lineage reference
    graph_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Node identification
    node_id: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Execution info
    execution_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Timing
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # State
    status: Mapped[str] = mapped_column(String(20), default="pending")
    input_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    output_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Dependencies
    depends_on: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    depended_by: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Index for lineage queries
    __table_args__ = (
        Index('ix_lineage_node_graph_execution', 'graph_id', 'execution_id'),
    )


class CrossServiceCoordination(BaseModel):
    """Cross-service coordination - manages coordination across services"""
    __tablename__ = "cross_service_coordinations"
    
    # Coordination identification
    coordination_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    coordination_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Services involved
    source_service: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_services: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    
    # Coordination payload
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # State
    state: Mapped[str] = mapped_column(String(20), default="pending")
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Index for coordination queries
    __table_args__ = (
        Index('ix_coordination_source', 'source_service', 'created_at'),
        Index('ix_coordination_correlation', 'correlation_id', 'state'),
    )


class ExecutionSnapshot(BaseModel):
    """Execution snapshot - point-in-time execution state"""
    __tablename__ = "execution_snapshots"
    
    # Snapshot identification
    snapshot_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Reference execution
    execution_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Snapshot data
    context_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    node_states: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    variables: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Sequence
    sequence_number: Mapped[int] = mapped_column(Integer, default=0)
    
    # Reason
    snapshot_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Index
    __table_args__ = (
        Index('ix_execution_snapshot_workflow', 'workflow_id', 'sequence_number'),
    )