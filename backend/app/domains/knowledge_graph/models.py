"""
Knowledge Graph Models - Persistent semantic orchestration memory.

These models implement a typed property-graph stored in PostgreSQL:

  - ExecutionKnowledgeNode  : typed vertices (workflow, execution, asset, agent...)
  - DependencyEdge          : typed edges with weight + confidence
  - SemanticRelationship    : higher-level semantic links between domain objects
  - OrchestrationMemory     : ranked memory items (episodic / semantic / procedural)
  - ExecutionGraphSnapshot  : materialized graph views captured at decision time

Every record is UUID-keyed, indexed for retrieval and lifecycle-stamped via
``BaseModel`` (created_at, updated_at, deleted_at) so the cognitive layer can
audit and prune memory deterministically.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from ...models.base import BaseModel


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class KnowledgeNodeKind(str, Enum):
    """Typed vertices in the orchestration knowledge graph."""

    WORKFLOW = "workflow"
    EXECUTION = "execution"
    EXECUTION_STEP = "execution_step"
    RENDER_JOB = "render_job"
    MEDIA_ASSET = "media_asset"
    AGENT = "agent"
    PROMPT = "prompt"
    MODEL = "model"
    COMPOSITION = "composition"
    SCENE = "scene"
    POLICY = "policy"
    HEURISTIC = "heuristic"
    INSIGHT = "insight"
    DECISION = "decision"
    OBSERVATION = "observation"


class KnowledgeEdgeKind(str, Enum):
    """Typed edges expressing runtime semantics."""

    DEPENDS_ON = "depends_on"
    PRODUCES = "produces"
    CONSUMES = "consumes"
    DERIVED_FROM = "derived_from"
    SIMILAR_TO = "similar_to"
    PRECEDES = "precedes"
    SUCCEEDS = "succeeds"
    TRIGGERS = "triggers"
    GOVERNS = "governs"
    OPTIMIZES = "optimizes"
    EXPLAINS = "explains"
    CONFLICTS_WITH = "conflicts_with"


class MemoryScope(str, Enum):
    """Memory scope - controls retention, retrieval, decay."""

    EPISODIC = "episodic"  # single execution context
    SEMANTIC = "semantic"  # generalized facts / relationships
    PROCEDURAL = "procedural"  # how-to / runbook style memory
    EVALUATIVE = "evaluative"  # quality / outcome assessments
    STRATEGIC = "strategic"  # long-horizon planning context


# ---------------------------------------------------------------------------
# Graph vertices and edges
# ---------------------------------------------------------------------------


class ExecutionKnowledgeNode(BaseModel):
    """A typed vertex in the orchestration knowledge graph.

    Nodes are uniquely identified by ``(node_kind, node_key)``. ``node_key`` is
    a stable string identifier defined by the source domain (e.g. workflow id,
    asset id, execution uuid). The ``vector`` field is reserved for embedding
    coordinates so we can layer ANN retrieval without changing the schema.
    """

    __tablename__ = "kg_nodes"
    __table_args__ = (
        UniqueConstraint("node_kind", "node_key", name="uq_kg_nodes_kind_key"),
        Index("ix_kg_nodes_kind_status", "node_kind", "lifecycle_state"),
        Index("ix_kg_nodes_relevance", "relevance_score"),
    )

    node_kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    node_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    label: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Property bag for graph attributes (arbitrary JSON keyed by string)
    properties: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    tags: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    # Optional dense vector (stored as list of floats); reserved for ANN/embedding hooks
    vector: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    vector_dim: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Ranking signals
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    centrality: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Lifecycle
    lifecycle_state: Mapped[str] = mapped_column(
        String(32), nullable=False, default="active", index=True
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Auditing
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    seen_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Provenance
    source_domain: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class DependencyEdge(BaseModel):
    """A typed edge between two ``ExecutionKnowledgeNode`` records.

    Edges carry a confidence and a weight so the planner can perform weighted
    traversal (e.g. critical-path analysis) and the learning layer can adjust
    confidence as new evidence is observed.
    """

    __tablename__ = "kg_edges"
    __table_args__ = (
        UniqueConstraint(
            "source_node_id", "target_node_id", "edge_kind",
            name="uq_kg_edges_triplet",
        ),
        Index("ix_kg_edges_kind_state", "edge_kind", "lifecycle_state"),
        Index("ix_kg_edges_weight", "weight"),
    )

    source_node_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("kg_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_node_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("kg_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    edge_kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    attributes: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    lifecycle_state: Mapped[str] = mapped_column(
        String(32), nullable=False, default="active", index=True
    )
    last_reinforced_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class SemanticRelationship(BaseModel):
    """High-level semantic relationships between domain objects.

    Distinct from the low-level graph edges, ``SemanticRelationship`` records are
    curated/derived knowledge (e.g. *"workflow A is the canonical pipeline for
    artist B"*) that survives across executions and is consumed by the creative
    intelligence layer and the long-horizon planner.
    """

    __tablename__ = "semantic_relationships"
    __table_args__ = (
        Index("ix_sem_rel_subject", "subject_kind", "subject_key"),
        Index("ix_sem_rel_object", "object_kind", "object_key"),
        Index("ix_sem_rel_predicate", "predicate"),
    )

    subject_kind: Mapped[str] = mapped_column(String(50), nullable=False)
    subject_key: Mapped[str] = mapped_column(String(255), nullable=False)

    predicate: Mapped[str] = mapped_column(String(80), nullable=False)

    object_kind: Mapped[str] = mapped_column(String(50), nullable=False)
    object_key: Mapped[str] = mapped_column(String(255), nullable=False)

    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    evidence: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    derived_from: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)


class OrchestrationMemory(BaseModel):
    """Ranked, scoped memory items used by the cognitive reasoner.

    Memory items are bounded contexts retrieved through ``MemoryQuery``. They
    capture episodic events, generalized semantic facts, runbooks and outcome
    evaluations. Each memory has an importance + recency component that drives
    eviction/decay.
    """

    __tablename__ = "orchestration_memory"
    __table_args__ = (
        Index("ix_orch_memory_scope_kind", "scope", "memory_kind"),
        Index("ix_orch_memory_importance", "importance"),
        Index("ix_orch_memory_correlation", "correlation_id"),
    )

    scope: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    memory_kind: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    subject: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    importance: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    recency: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    access_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    agent_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ExecutionGraphSnapshot(BaseModel):
    """Materialized view of a sub-graph captured at decision time.

    The planner asks for a graph projection (root, depth, kinds-of-interest);
    the materialized snapshot is what was actually used so any future audit can
    explain "what the system knew when it decided X".
    """

    __tablename__ = "execution_graph_snapshots"
    __table_args__ = (
        Index("ix_kg_snapshot_root", "root_kind", "root_key"),
        Index("ix_kg_snapshot_purpose", "purpose"),
    )

    root_kind: Mapped[str] = mapped_column(String(50), nullable=False)
    root_key: Mapped[str] = mapped_column(String(255), nullable=False)

    purpose: Mapped[str] = mapped_column(String(100), nullable=False)
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=2)

    nodes: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    edges: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)

    node_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    edge_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    critical_path: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    insights: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


__all__ = [
    "KnowledgeNodeKind",
    "KnowledgeEdgeKind",
    "MemoryScope",
    "ExecutionKnowledgeNode",
    "DependencyEdge",
    "SemanticRelationship",
    "OrchestrationMemory",
    "ExecutionGraphSnapshot",
]
