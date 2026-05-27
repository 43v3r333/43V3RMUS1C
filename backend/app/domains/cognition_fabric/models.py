"""
Cognition Fabric Models - Unified cognition and orchestration memory.

Provides:
- Shared cognition memory
- Orchestration intelligence fabric
- Semantic runtime awareness
- Distributed execution memory
- Adaptive cognition systems
- Orchestration continuity coordination
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class MemoryScope(str, Enum):
    """Memory scope levels"""
    EPISODIC = "episodic"  # Specific experiences/events
    SEMANTIC = "semantic"  # General knowledge/concepts
    PROCEDURAL = "procedural"  # How to do things
    EVALUATIVE = "evaluative"  # Preferences/values
    STRATEGIC = "strategic"  # Long-term goals/plans


class MemoryKind(str, Enum):
    """Memory kind types"""
    EXECUTION_INSIGHT = "execution_insight"
    WORKFLOW_AUDIT = "workflow_audit"
    PERFORMANCE_PATTERN = "performance_pattern"
    ANOMALY_DETECTION = "anomaly_detection"
    OPTIMIZATION_HINT = "optimization_hint"
    POLICY_DECISION = "policy_decision"
    AGENT_COLLABORATION = "agent_collaboration"


class MemoryStatus(str, Enum):
    """Memory entry status"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    EXPIRED = "expired"
    CONSOLIDATED = "consolidated"


class CognitionState(str, Enum):
    """Cognition system state"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    CONSOLIDATING = "consolidating"
    DEGRADED = "degraded"
    RECOVERING = "recovering"


class AdaptiveState(str, Enum):
    """Adaptive learning state"""
    LEARNING = "learning"
    STABLE = "stable"
    REFRACTING = "refracting"
    MERGING = "merging"


class AdaptiveCognitionMemory(BaseModel):
    """Adaptive cognition memory - stores cognitive experiences and insights"""
    __tablename__ = "adaptive_cognition_memory"
    
    # Memory identification
    memory_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Scope and kind
    scope: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    memory_kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Subject reference
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    subject_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Importance and recency
    importance: Mapped[float] = mapped_column(Float, default=0.5)
    recency: Mapped[float] = mapped_column(Float, default=1.0)
    stability: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Access metrics
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Confidence
    confidence: Mapped[float] = mapped_column(Float, default=0.8)
    
    # Pin status
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Context
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=MemoryStatus.ACTIVE.value)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_cognition_memory_scope_kind', 'scope', 'memory_kind'),
        Index('ix_cognition_memory_subject', 'subject', 'created_at'),
    )


class SharedCognitionState(BaseModel):
    """Shared cognition state - distributed cognitive awareness"""
    __tablename__ = "shared_cognition_states"
    
    # State identification
    state_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # State type
    state_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Value
    value: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Scope
    scope: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Synchronization
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_consistent: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Source
    source_node: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_writer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class CognitionNode(BaseModel):
    """Cognition node - individual cognitive unit"""
    __tablename__ = "cognition_nodes"
    
    # Node identification
    node_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type and classification
    node_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    classification: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Connections
    connections: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    connection_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Activation
    activation_level: Mapped[float] = mapped_column(Float, default=0.0)
    activation_threshold: Mapped[float] = mapped_column(Float, default=0.5)
    
    # State
    state: Mapped[str] = mapped_column(String(20), default=CognitionState.ACTIVE.value)
    
    # Content
    semantic_content: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Metrics
    access_frequency: Mapped[int] = mapped_column(Integer, default=0)
    last_activated: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class CognitionEdge(BaseModel):
    """Cognition edge - connections between cognitive nodes"""
    __tablename__ = "cognition_edges"
    
    # Edge identification
    edge_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Nodes
    source_node_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_node_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Edge properties
    edge_type: Mapped[str] = mapped_column(String(50), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Properties
    semantic_relation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    strength: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Usage
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class OrchestrationIntelligenceFabric(BaseModel):
    """Orchestration intelligence fabric - global orchestration knowledge"""
    __tablename__ = "orchestration_intelligence_fabric"
    
    # Fabric identification
    fabric_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Fabric type
    fabric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Knowledge
    knowledge_graph: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    patterns: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    heuristics: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Metrics
    knowledge_size: Mapped[int] = mapped_column(Integer, default=0)
    coverage_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # State
    state: Mapped[str] = mapped_column(String(20), default=AdaptiveState.STABLE.value)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_sync: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class CrossWorkflowIntelligence(BaseModel):
    """Cross-workflow intelligence - insights spanning multiple workflows"""
    __tablename__ = "cross_workflow_intelligence"
    
    # Intelligence identification
    intelligence_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    intelligence_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Workflows involved
    workflow_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    workflow_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Insight
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    insight_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Confidence
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Applicability
    applicability: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Status
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False)
    validation_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class CognitiveConsolidation(BaseModel):
    """Cognitive consolidation - memory consolidation tracking"""
    __tablename__ = "cognitive_consolidations"
    
    # Consolidation identification
    consolidation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    consolidation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Memory sources
    source_memory_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    source_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Result
    result_memory_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    consolidated_content: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Process
    confidence_loss: Mapped[float] = mapped_column(Float, default=0.0)
    importance_blending: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    
    # Status
    state: Mapped[str] = mapped_column(String(20), default="pending")
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class AdaptiveLearningProfile(BaseModel):
    """Adaptive learning profile - tracks learning patterns"""
    __tablename__ = "adaptive_learning_profiles"
    
    # Profile identification
    profile_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Profile type
    profile_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Learning patterns
    patterns: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Adaptation state
    learning_rate: Mapped[float] = mapped_column(Float, default=0.1)
    adaptation_cycles: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metrics
    accuracy: Mapped[float] = mapped_column(Float, default=0.5)
    precision: Mapped[float] = mapped_column(Float, default=0.5)
    recall: Mapped[float] = mapped_column(Float, default=0.5)
    
    # State
    state: Mapped[str] = mapped_column(String(20), default=AdaptiveState.LEARNING.value)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_training: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class SemanticRuntimeAwareness(BaseModel):
    """Semantic runtime awareness - awareness of runtime semantics"""
    __tablename__ = "semantic_runtime_awareness"
    
    # Awareness identification
    awareness_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    awareness_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Semantic understanding
    semantic_model: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    semantic_embeddings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Context
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Confidence
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Coverage
    coverage_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    uncovered_aspects: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_eval: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class CognitionConsistencyCheck(BaseModel):
    """Cognition consistency check - tracks consistency validation"""
    __tablename__ = "cognition_consistency_checks"
    
    # Check identification
    check_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    check_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Scope
    scope: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Results
    is_consistent: Mapped[bool] = mapped_column(Boolean, default=True)
    violations: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    resolution_actions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Metrics
    consistency_score: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Timing
    checked_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)