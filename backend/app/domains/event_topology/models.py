"""
Event Topology Governance Models - Database models for centralized event topology.

Provides:
- Event contract registry
- Topology governance engine
- Schema versioning systems
- Event lineage tracking
- Distributed propagation policies
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class ContractStatus(str, Enum):
    """Event contract status"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ContractType(str, Enum):
    """Event contract type"""
    DOMAIN = "domain"
    COMMAND = "command"
    QUERY = "query"
    EVENT = "event"
    INTEGRATION = "integration"


class SchemaStatus(str, Enum):
    """Schema version status"""
    DRAFT = "draft"
    VALIDATED = "validated"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class PropagationMode(str, Enum):
    """Event propagation mode"""
    SYNC = "sync"
    ASYNC = "async"
    FANOUT = "fanout"
    PIPELINE = "pipeline"


class LineageEventType(str, Enum):
    """Lineage event type"""
    CREATED = "created"
    PUBLISHED = "published"
    CONSUMED = "consumed"
    CORRELATED = "correlated"
    TRANSFORMED = "transformed"


class EventContract(BaseModel):
    """Event contract registry - defines event schema contracts"""
    __tablename__ = "event_contracts"
    
    # Contract identification
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Contract type and category
    contract_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Description
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Schema definition (JSON Schema or similar)
    schema: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    schema_version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Constraints and validations
    constraints: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    validation_rules: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=ContractStatus.DRAFT.value, index=True)
    
    # Usage metrics
    publish_count: Mapped[int] = mapped_column(Integer, default=0)
    consume_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Provenance
    owner_team: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    
    # Lifecycle
    deprecated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Index for contract lookup
    __table_args__ = (
        Index('ix_event_contracts_type_version', 'contract_type', 'version'),
    )


class EventContractVersion(BaseModel):
    """Schema versioning for event contracts"""
    __tablename__ = "event_contract_versions"
    
    # Contract reference
    contract_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("event_contracts.id"), nullable=False, index=True)
    
    # Version info
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Schema snapshot
    schema: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    schema_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    
    # Change tracking
    changelog: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    breaking_changes: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Validation
    validation_schema: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False)
    validation_errors: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=SchemaStatus.DRAFT.value)
    
    # Provenance
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Index for version lookup
    __table_args__ = (
        Index('ix_event_contract_versions_contract_version', 'contract_id', 'version'),
    )


class TopologyNode(BaseModel):
    """Topology node - represents a service or component in event topology"""
    __tablename__ = "topology_nodes"
    
    # Node identification
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Physical/logical classification
    classification: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Connection details
    endpoint: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    protocol: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Capabilities
    capabilities: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    consumes_events: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    publishes_events: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    health_score: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Metrics
    events_received: Mapped[int] = mapped_column(Integer, default=0)
    events_published: Mapped[int] = mapped_column(Integer, default=0)
    error_rate: Mapped[float] = mapped_column(Float, default=0.0)
    latency_p99: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Location
    region: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    datacenter: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timing
    last_heartbeat: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class TopologyEdge(BaseModel):
    """Topology edge - represents connections between nodes"""
    __tablename__ = "topology_edges"
    
    # Edge identification
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Node references
    source_node_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("topology_nodes.id"), nullable=False, index=True)
    target_node_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("topology_nodes.id"), nullable=False, index=True)
    
    # Edge properties
    edge_type: Mapped[str] = mapped_column(String(50), nullable=False)
    protocol: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Traffic management
    bandwidth_mbps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    queue_depth: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metrics
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class PropagationPolicy(BaseModel):
    """Propagation policy - rules for event distribution"""
    __tablename__ = "propagation_policies"
    
    # Policy identification
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Scope
    event_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    source_node_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    target_node_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    
    # Propagation configuration
    propagation_mode: Mapped[str] = mapped_column(String(20), default=PropagationMode.SYNC.value)
    
    # Routing
    routing_rules: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    filters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    transformations: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # QoS
    priority: Mapped[int] = mapped_column(Integer, default=5)
    qos_level: Mapped[str] = mapped_column(String(20), default="best_effort")
    retry_policy: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Limits
    rate_limit_per_second: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_batch_size: Mapped[int] = mapped_column(Integer, default=100)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metrics
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class EventLineage(BaseModel):
    """Event lineage - tracks event history through the system"""
    __tablename__ = "event_lineages"
    
    # Event identification
    event_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Origin
    source_node_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    source_service: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Tracing
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    span_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Causality
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    causation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Path through system
    node_visits: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    transformation_history: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Lineage type
    lineage_type: Mapped[str] = mapped_column(String(50), default=LineageEventType.CREATED.value, index=True)
    
    # Payload reference (for replay)
    payload_digest: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    payload_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Indexes for lineage queries
    __table_args__ = (
        Index('ix_event_lineages_trace', 'trace_id', 'created_at'),
        Index('ix_event_lineages_correlation', 'correlation_id', 'created_at'),
    )


class EventCorrelation(BaseModel):
    """Event correlation - tracks relationships between events"""
    __tablename__ = "event_correlations"
    
    # Correlation identification
    correlation_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Scope
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Events in correlation
    event_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    event_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Semantic correlation
    correlation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    correlation_strength: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Temporal
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Context
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Status
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Index for correlation queries
    __table_args__ = (
        Index('ix_event_correlations_session', 'session_id', 'started_at'),
        Index('ix_event_correlations_workflow', 'workflow_id', 'started_at'),
    )


class TopologyValidationRule(BaseModel):
    """Topology validation rules - governance constraints"""
    __tablename__ = "topology_validation_rules"
    
    # Rule identification
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Rule type
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Scope
    applies_to_node_types: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    applies_to_event_types: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Rule definition
    rule_definition: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="warning")
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metrics
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    violation_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class EventContractAudit(BaseModel):
    """Event contract audit trail"""
    __tablename__ = "event_contract_audits"
    
    # Audit identification
    audit_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Contract reference
    contract_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("event_contracts.id"), nullable=False, index=True)
    
    # Action
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    previous_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    new_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Change details
    changed_fields: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    change_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Actor
    actor_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    actor_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)