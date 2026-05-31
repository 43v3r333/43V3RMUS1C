"""
Semantic Execution Infrastructure Models - Semantic orchestration and execution graphs.

Provides:
- Semantic execution graphs
- Orchestration relationship mapping
- Runtime dependency intelligence
- Execution topology analysis
- Adaptive semantic coordination
- Workflow cognition topology
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class GraphStatus(str, Enum):
    """Graph status"""
    DRAFT = "draft"
    VALIDATED = "validated"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class NodeExecutionMode(str, Enum):
    """Node execution mode"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"


class RelationshipType(str, Enum):
    """Relationship type"""
    DEPENDENCY = "dependency"
    DATA_FLOW = "data_flow"
    CONTROL_FLOW = "control_flow"
    EVENT_TRIGGER = "event_trigger"
    TEMPORAL = "temporal"


class SemanticExecutionRelationship(BaseModel):
    """Semantic execution relationships - tracks relationships between execution nodes"""
    __tablename__ = "semantic_execution_relationships"
    
    # Relationship identification
    relationship_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Nodes
    source_node_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target_node_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Semantic description
    semantic_label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Properties
    properties: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Dependency info
    is_blocking: Mapped[bool] = mapped_column(Boolean, default=True)
    delay_ms: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Index for relationship queries
    __table_args__ = (
        Index('ix_relationships_source_target', 'source_node_id', 'target_node_id'),
    )


class ExecutionGraph(BaseModel):
    """Execution graph - semantic execution graph"""
    __tablename__ = "execution_graphs"
    
    # Graph identification
    graph_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Graph metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Version
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_graph_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Structure
    nodes: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=False)
    edges: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=False)
    node_count: Mapped[int] = mapped_column(Integer, default=0)
    edge_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Semantic metadata
    semantic_tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    execution_mode: Mapped[str] = mapped_column(String(20), default=NodeExecutionMode.SEQUENTIAL.value)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=GraphStatus.DRAFT.value, index=True)
    
    # Metrics
    complexity_score: Mapped[float] = mapped_column(Float, default=0.0)
    parallelization_potential: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class DependencyIntelligence(BaseModel):
    """Dependency intelligence - runtime dependency analysis"""
    __tablename__ = "dependency_intelligence"
    
    # Dependency identification
    dependency_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    dependency_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Target
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Dependencies
    depends_on: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    depends_on_types: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Analysis
    critical_path: Mapped[bool] = mapped_column(Boolean, default=False)
    fan_out: Mapped[int] = mapped_column(Integer, default=0)
    fan_in: Mapped[int] = mapped_column(Integer, default=0)
    
    # Analysis results
    analysis_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class TopologyAnalysis(BaseModel):
    """Topology analysis - execution topology analysis"""
    __tablename__ = "topology_analyses"
    
    # Analysis identification
    analysis_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Target
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Analysis type
    analysis_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Results
    structure_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Complexity
    complexity_score: Mapped[float] = mapped_column(Float, default=0.0)
    cyclomatic_complexity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Optimizations
    optimization_hints: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class WorkflowCognitionTopology(BaseModel):
    """Workflow cognition topology - cognitive mapping of workflows"""
    __tablename__ = "workflow_cognition_topology"
    
    # Topology identification
    topology_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Workflow reference
    workflow_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Cognitive map
    cognitive_nodes: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    cognitive_edges: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Semantic understanding
    semantic_map: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    intent_analysis: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Confidence
    understanding_confidence: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Coverage
    coverage_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    uncovered_aspects: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class AdaptiveSemanticCoordination(BaseModel):
    """Adaptive semantic coordination - dynamic semantic coordination"""
    __tablename__ = "adaptive_semantic_coordinations"
    
    # Coordination identification
    coordination_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    coordination_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Targets
    source_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    
    # Semantic context
    semantic_context: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Coordination strategy
    strategy: Mapped[str] = mapped_column(String(50), nullable=False)
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # State
    state: Mapped[str] = mapped_column(String(20), default="pending")
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ExecutionPattern(BaseModel):
    """Execution pattern - recognized execution patterns"""
    __tablename__ = "execution_patterns_v2"
    
    # Pattern identification
    pattern_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    pattern_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Description
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Pattern data
    pattern_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    signature: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Metrics
    frequency: Mapped[int] = mapped_column(Integer, default=1)
    success_rate: Mapped[float] = mapped_column(Float, default=1.0)
    avg_duration_ms: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Conditions
    conditions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    first_observed: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    last_observed: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class SemanticExecutionMetrics(BaseModel):
    """Semantic execution metrics - metrics for semantic execution"""
    __tablename__ = "semantic_execution_metrics"
    
    # Metric identification
    metric_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Target
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Values
    value: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Semantic context
    semantic_tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    measured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)