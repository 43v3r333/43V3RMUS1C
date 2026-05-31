"""
Cognition Consistency Domain Models.

Provides:
- Shared cognition semantics
- Orchestration reasoning standards
- Distributed semantic memory
- Runtime interpretation systems
- Adaptive cognition governance
- Semantic coordination fabric
- Shared orchestration cognition
- Runtime reasoning consistency
- Semantic workflow awareness
- Distributed cognition alignment
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class CognitionScope(str, Enum):
    """Cognition scope types"""
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"
    EVALUATIVE = "evaluative"
    STRATEGIC = "strategic"


class ConsistencyState(str, Enum):
    """Consistency state"""
    ALIGNED = "aligned"
    DEVIATING = "deviating"
    RECONCILING = "reconciling"
    CONFLICTED = "conflicted"
    STABILIZED = "stabilized"


class ReasoningType(str, Enum):
    """Reasoning type"""
    DEDUCTIVE = "deductive"
    ABDUCTIVE = "abductive"
    INDUCTIVE = "inductive"
    ANALOGICAL = "analogical"
    CAUSAL = "causal"


class CogNodeType(str, Enum):
    """Cognition node type"""
    EXECUTION = "execution"
    WORKFLOW = "workflow"
    POLICY = "policy"
    METRIC = "metric"
    ANOMALY = "anomaly"
    INSIGHT = "insight"


class SemanticMemory(BaseModel):
    """Semantic memory - persistent shared knowledge"""
    __tablename__ = "semantic_cognition_memories"
    
    # Memory identification
    memory_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    memory_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    
    # Scope and type
    scope: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    memory_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Content
    subject: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Attributes
    importance: Mapped[float] = mapped_column(Float, default=0.5, index=True)
    recency: Mapped[float] = mapped_column(Float, default=1.0)
    stability: Mapped[float] = mapped_column(Float, default=1.0)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Access tracking
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # State
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class CognitionConsistencyState(BaseModel):
    """Cognition consistency state - tracks alignment across cognition nodes"""
    __tablename__ = "cognition_consistency_states"
    
    # State identification
    state_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Scope
    scope: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Current state
    consistency_state: Mapped[str] = mapped_column(String(20), default=ConsistencyState.ALIGNED.value, index=True)
    alignment_score: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Metrics
    coherence_score: Mapped[float] = mapped_column(Float, default=1.0)
    divergence_score: Mapped[float] = mapped_column(Float, default=0.0)
    reconciliation_progress: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Analysis data
    deviation_sources: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    reconciliation_attempts: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    last_assessed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    last_reconciled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    stable_since: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class SharedReasoning(BaseModel):
    """Shared reasoning - governance standards for reasoning processes"""
    __tablename__ = "shared_reasoning_standards"
    
    # Reasoning identification
    reasoning_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    reasoning_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    
    # Type and scope
    reasoning_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Definition
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Rules
    inference_rules: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    validation_rules: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    constraint_rules: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Standards
    confidence_threshold: Mapped[float] = mapped_column(Float, default=0.8)
    reasoning_depth_limit: Mapped[int] = mapped_column(Integer, default=10)
    
    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class CognitionGraphEdge(BaseModel):
    """Cognition graph edge - semantic links between nodes"""
    __tablename__ = "cognition_graph_edges"
    
    # Edge identification
    edge_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Connection
    source_node_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_node_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Edge properties
    edge_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Semantic context
    relation_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class DistributedSemanticMemory(BaseModel):
    """Distributed semantic memory - distributed knowledge storage"""
    __tablename__ = "distributed_semantic_memories"
    
    # Memory identification
    memory_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    memory_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Ownership
    owner_node: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Content
    knowledge: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    metadata_: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)
    
    # Distribution
    replicas: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    sync_strategy: Mapped[str] = mapped_column(String(20), default="eager")
    
    # State
    consistency_version: Mapped[int] = mapped_column(Integer, default=1)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class AdaptiveCognitionProfile(BaseModel):
    """Adaptive cognition profile - learned reasoning patterns"""
    __tablename__ = "adaptive_cognition_profiles"
    
    # Profile identification
    profile_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    profile_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    
    # Target
    target_entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Learned patterns
    reasoning_patterns: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    inference_effectiveness: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    confidence_weights: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    
    # Performance
    hit_rate: Mapped[float] = mapped_column(Float, default=0.0)
    adaptation_rate: Mapped[float] = mapped_column(Float, default=0.1)
    last_adapted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class CognitionAudit(BaseModel):
    """Cognition audit - tracking cognitive operations"""
    __tablename__ = "cognition_audits"
    
    # Audit identification
    audit_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Operation
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Target
    target_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Details
    operation_details: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    result: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Impact
    alignment_impact: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    consistency_impact: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Audit
    performed_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    performed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
