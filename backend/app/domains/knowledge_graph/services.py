"""
Knowledge Graph Services - Reasoning over orchestration memory.

This module implements three coordinated services:

  - ``KnowledgeGraphService``     CRUD + traversal over typed nodes and edges
  - ``OrchestrationMemoryService`` ranked retrieval with decay over memory items
  - ``DependencyIntelligenceService`` higher-order analysis (critical path,
                                       blast-radius, semantic clustering)

The services operate on top of synchronous SQLAlchemy sessions because the
rest of the cognitive layer is invoked from request handlers and Celery tasks
that already use that pattern.
"""
from __future__ import annotations

import logging
import math
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from .models import (
    DependencyEdge,
    ExecutionGraphSnapshot,
    ExecutionKnowledgeNode,
    KnowledgeEdgeKind,
    KnowledgeNodeKind,
    MemoryScope,
    OrchestrationMemory,
    SemanticRelationship,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data transfer types
# ---------------------------------------------------------------------------


@dataclass
class GraphNeighborhood:
    """Result of a neighborhood query."""

    root: ExecutionKnowledgeNode
    nodes: List[ExecutionKnowledgeNode]
    edges: List[DependencyEdge]
    depth: int

    def to_payload(self) -> Dict[str, Any]:
        """Serialize for storage in ``ExecutionGraphSnapshot``."""
        return {
            "root": _serialize_node(self.root),
            "nodes": [_serialize_node(n) for n in self.nodes],
            "edges": [_serialize_edge(e) for e in self.edges],
            "depth": self.depth,
        }


@dataclass
class MemoryQuery:
    """Filtering parameters for memory retrieval."""

    subject: Optional[str] = None
    scope: Optional[MemoryScope] = None
    memory_kind: Optional[str] = None
    correlation_id: Optional[str] = None
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    min_importance: float = 0.0
    limit: int = 20


@dataclass
class GraphReasoningResult:
    """Result of a higher-order graph reasoning operation."""

    summary: str
    critical_path: List[str] = field(default_factory=list)
    blast_radius: List[str] = field(default_factory=list)
    clusters: List[List[str]] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)


def _serialize_node(node: ExecutionKnowledgeNode) -> Dict[str, Any]:
    return {
        "id": str(node.id),
        "kind": node.node_kind,
        "key": node.node_key,
        "label": node.label,
        "relevance_score": node.relevance_score,
        "centrality": node.centrality,
        "tags": list(node.tags or []),
        "lifecycle_state": node.lifecycle_state,
    }


def _serialize_edge(edge: DependencyEdge) -> Dict[str, Any]:
    return {
        "id": str(edge.id),
        "source_id": str(edge.source_node_id),
        "target_id": str(edge.target_node_id),
        "kind": edge.edge_kind,
        "weight": edge.weight,
        "confidence": edge.confidence,
    }


# ---------------------------------------------------------------------------
# Knowledge graph service
# ---------------------------------------------------------------------------


class KnowledgeGraphService:
    """CRUD + traversal over the orchestration knowledge graph."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ---- node management ------------------------------------------------

    def upsert_node(
        self,
        *,
        kind: KnowledgeNodeKind | str,
        key: str,
        label: str,
        summary: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        tags: Optional[Sequence[str]] = None,
        vector: Optional[Sequence[float]] = None,
        relevance_score: Optional[float] = None,
        source_domain: Optional[str] = None,
        correlation_id: Optional[str] = None,
        owner_id: Optional[UUID] = None,
    ) -> ExecutionKnowledgeNode:
        """Insert or update a graph node atomically.

        Returns the persistent record. Repeat calls reinforce ``seen_count``
        and ``last_seen_at`` so the cognitive layer can rank by recency.
        """
        kind_value = kind.value if isinstance(kind, KnowledgeNodeKind) else kind

        node = (
            self.db.query(ExecutionKnowledgeNode)
            .filter(
                ExecutionKnowledgeNode.node_kind == kind_value,
                ExecutionKnowledgeNode.node_key == key,
            )
            .first()
        )

        if node is None:
            node = ExecutionKnowledgeNode(
                node_kind=kind_value,
                node_key=key,
                label=label,
                summary=summary,
                properties=dict(properties or {}),
                tags=list(tags or []),
                vector=list(vector) if vector is not None else None,
                vector_dim=len(vector) if vector is not None else None,
                relevance_score=relevance_score or 0.0,
                source_domain=source_domain,
                correlation_id=correlation_id,
                owner_id=owner_id,
            )
            self.db.add(node)
        else:
            node.label = label
            if summary is not None:
                node.summary = summary
            if properties is not None:
                merged = dict(node.properties or {})
                merged.update(properties)
                node.properties = merged
            if tags is not None:
                node.tags = list(tags)
            if vector is not None:
                node.vector = list(vector)
                node.vector_dim = len(vector)
            if relevance_score is not None:
                node.relevance_score = max(node.relevance_score, relevance_score)
            if source_domain is not None:
                node.source_domain = source_domain
            if correlation_id is not None:
                node.correlation_id = correlation_id
            node.last_seen_at = datetime.utcnow()
            node.seen_count = (node.seen_count or 0) + 1

        self.db.commit()
        self.db.refresh(node)
        return node

    def get_node(self, kind: KnowledgeNodeKind | str, key: str) -> Optional[ExecutionKnowledgeNode]:
        kind_value = kind.value if isinstance(kind, KnowledgeNodeKind) else kind
        return (
            self.db.query(ExecutionKnowledgeNode)
            .filter(
                ExecutionKnowledgeNode.node_kind == kind_value,
                ExecutionKnowledgeNode.node_key == key,
            )
            .first()
        )

    def list_nodes(
        self,
        *,
        kind: Optional[KnowledgeNodeKind | str] = None,
        lifecycle_state: Optional[str] = "active",
        limit: int = 100,
        offset: int = 0,
    ) -> List[ExecutionKnowledgeNode]:
        query = self.db.query(ExecutionKnowledgeNode)
        if kind is not None:
            kind_value = kind.value if isinstance(kind, KnowledgeNodeKind) else kind
            query = query.filter(ExecutionKnowledgeNode.node_kind == kind_value)
        if lifecycle_state is not None:
            query = query.filter(ExecutionKnowledgeNode.lifecycle_state == lifecycle_state)
        return (
            query.order_by(
                ExecutionKnowledgeNode.relevance_score.desc(),
                ExecutionKnowledgeNode.last_seen_at.desc(),
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

    # ---- edge management ------------------------------------------------

    def reinforce_edge(
        self,
        *,
        source: ExecutionKnowledgeNode,
        target: ExecutionKnowledgeNode,
        kind: KnowledgeEdgeKind | str,
        weight_delta: float = 0.0,
        confidence: Optional[float] = None,
        attributes: Optional[Dict[str, Any]] = None,
        label: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> DependencyEdge:
        """Create or reinforce a typed edge.

        ``weight_delta`` is added to the current weight (bounded to >= 0).
        ``confidence`` overrides if supplied; otherwise we increment evidence.
        """
        kind_value = kind.value if isinstance(kind, KnowledgeEdgeKind) else kind

        edge = (
            self.db.query(DependencyEdge)
            .filter(
                DependencyEdge.source_node_id == source.id,
                DependencyEdge.target_node_id == target.id,
                DependencyEdge.edge_kind == kind_value,
            )
            .first()
        )

        if edge is None:
            edge = DependencyEdge(
                source_node_id=source.id,
                target_node_id=target.id,
                edge_kind=kind_value,
                weight=max(weight_delta, 1.0),
                confidence=confidence if confidence is not None else 1.0,
                evidence_count=1,
                attributes=dict(attributes or {}),
                label=label,
                correlation_id=correlation_id,
            )
            self.db.add(edge)
        else:
            edge.weight = max(0.0, edge.weight + weight_delta)
            edge.evidence_count = (edge.evidence_count or 0) + 1
            if confidence is not None:
                edge.confidence = confidence
            if attributes:
                merged = dict(edge.attributes or {})
                merged.update(attributes)
                edge.attributes = merged
            if label is not None:
                edge.label = label
            if correlation_id is not None:
                edge.correlation_id = correlation_id
            edge.last_reinforced_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(edge)
        return edge

    def list_edges_from(
        self, node_id: UUID, *, kinds: Optional[Iterable[str]] = None
    ) -> List[DependencyEdge]:
        query = self.db.query(DependencyEdge).filter(DependencyEdge.source_node_id == node_id)
        if kinds:
            query = query.filter(DependencyEdge.edge_kind.in_(list(kinds)))
        return query.order_by(DependencyEdge.weight.desc()).all()

    # ---- traversal ------------------------------------------------------

    def neighborhood(
        self,
        kind: KnowledgeNodeKind | str,
        key: str,
        *,
        depth: int = 2,
        max_nodes: int = 200,
        edge_kinds: Optional[Iterable[str]] = None,
    ) -> Optional[GraphNeighborhood]:
        """Materialize a breadth-first neighborhood up to ``depth``."""
        root = self.get_node(kind, key)
        if root is None:
            return None

        visited_nodes: Dict[UUID, ExecutionKnowledgeNode] = {root.id: root}
        edge_kinds_set = set(edge_kinds) if edge_kinds else None
        collected_edges: List[DependencyEdge] = []

        frontier: deque[Tuple[UUID, int]] = deque([(root.id, 0)])
        while frontier and len(visited_nodes) < max_nodes:
            node_id, level = frontier.popleft()
            if level >= depth:
                continue

            out_edges = self.list_edges_from(node_id, kinds=edge_kinds_set)
            for edge in out_edges:
                collected_edges.append(edge)
                if edge.target_node_id in visited_nodes:
                    continue
                neighbor = self.db.get(ExecutionKnowledgeNode, edge.target_node_id)
                if neighbor is None:
                    continue
                visited_nodes[neighbor.id] = neighbor
                frontier.append((neighbor.id, level + 1))
                if len(visited_nodes) >= max_nodes:
                    break

        nodes = list(visited_nodes.values())
        nodes.sort(key=lambda n: n.relevance_score, reverse=True)
        return GraphNeighborhood(root=root, nodes=nodes, edges=collected_edges, depth=depth)

    def snapshot_neighborhood(
        self,
        *,
        kind: KnowledgeNodeKind | str,
        key: str,
        depth: int = 2,
        purpose: str = "decision",
        correlation_id: Optional[str] = None,
        critical_path: Optional[Sequence[str]] = None,
        insights: Optional[Sequence[str]] = None,
    ) -> Optional[ExecutionGraphSnapshot]:
        neighborhood = self.neighborhood(kind, key, depth=depth)
        if neighborhood is None:
            return None

        snapshot = ExecutionGraphSnapshot(
            root_kind=neighborhood.root.node_kind,
            root_key=neighborhood.root.node_key,
            purpose=purpose,
            depth=depth,
            nodes=[_serialize_node(n) for n in neighborhood.nodes],
            edges=[_serialize_edge(e) for e in neighborhood.edges],
            node_count=len(neighborhood.nodes),
            edge_count=len(neighborhood.edges),
            critical_path=list(critical_path or []),
            insights=list(insights or []),
            correlation_id=correlation_id,
        )
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    # ---- relationships --------------------------------------------------

    def assert_relationship(
        self,
        *,
        subject_kind: str,
        subject_key: str,
        predicate: str,
        object_kind: str,
        object_key: str,
        confidence: float = 1.0,
        weight: float = 1.0,
        evidence: Optional[Dict[str, Any]] = None,
        derived_from: Optional[str] = None,
    ) -> SemanticRelationship:
        existing = (
            self.db.query(SemanticRelationship)
            .filter(
                SemanticRelationship.subject_kind == subject_kind,
                SemanticRelationship.subject_key == subject_key,
                SemanticRelationship.predicate == predicate,
                SemanticRelationship.object_kind == object_kind,
                SemanticRelationship.object_key == object_key,
            )
            .first()
        )
        if existing is None:
            rel = SemanticRelationship(
                subject_kind=subject_kind,
                subject_key=subject_key,
                predicate=predicate,
                object_kind=object_kind,
                object_key=object_key,
                confidence=confidence,
                weight=weight,
                evidence=dict(evidence or {}),
                derived_from=derived_from,
            )
            self.db.add(rel)
        else:
            # Average confidence with evidence accumulation
            existing.confidence = (existing.confidence + confidence) / 2.0
            existing.weight = existing.weight + weight
            if evidence:
                merged = dict(existing.evidence or {})
                merged.update(evidence)
                existing.evidence = merged
            rel = existing

        self.db.commit()
        self.db.refresh(rel)
        return rel

    def list_relationships(
        self,
        *,
        subject_kind: Optional[str] = None,
        subject_key: Optional[str] = None,
        predicate: Optional[str] = None,
        limit: int = 100,
    ) -> List[SemanticRelationship]:
        query = self.db.query(SemanticRelationship).filter(
            SemanticRelationship.is_active.is_(True)
        )
        if subject_kind:
            query = query.filter(SemanticRelationship.subject_kind == subject_kind)
        if subject_key:
            query = query.filter(SemanticRelationship.subject_key == subject_key)
        if predicate:
            query = query.filter(SemanticRelationship.predicate == predicate)
        return query.order_by(SemanticRelationship.confidence.desc()).limit(limit).all()

    # ---- metrics --------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        node_count = self.db.query(ExecutionKnowledgeNode).count()
        edge_count = self.db.query(DependencyEdge).count()
        rel_count = self.db.query(SemanticRelationship).count()

        by_kind: Dict[str, int] = defaultdict(int)
        for row in self.db.query(ExecutionKnowledgeNode.node_kind).all():
            by_kind[row[0]] += 1

        return {
            "nodes": node_count,
            "edges": edge_count,
            "relationships": rel_count,
            "by_kind": dict(by_kind),
        }


# ---------------------------------------------------------------------------
# Memory service
# ---------------------------------------------------------------------------


class OrchestrationMemoryService:
    """Bounded retrieval over ranked memory items."""

    HALF_LIFE_HOURS = 72.0  # exponential recency decay

    def __init__(self, db: Session) -> None:
        self.db = db

    def remember(
        self,
        *,
        scope: MemoryScope | str,
        memory_kind: str,
        subject: str,
        title: str,
        content: Dict[str, Any],
        importance: float = 0.5,
        confidence: float = 1.0,
        correlation_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        ttl: Optional[timedelta] = None,
    ) -> OrchestrationMemory:
        scope_value = scope.value if isinstance(scope, MemoryScope) else scope
        memory = OrchestrationMemory(
            scope=scope_value,
            memory_kind=memory_kind,
            subject=subject,
            title=title,
            content=dict(content),
            importance=max(0.0, min(1.0, importance)),
            recency=1.0,
            confidence=max(0.0, min(1.0, confidence)),
            correlation_id=correlation_id,
            workflow_id=workflow_id,
            agent_id=agent_id,
            expires_at=(datetime.utcnow() + ttl) if ttl else None,
        )
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def recall(self, query: MemoryQuery) -> List[OrchestrationMemory]:
        """Retrieve memory items ranked by importance * recency * confidence."""
        clauses = []
        if query.scope is not None:
            clauses.append(OrchestrationMemory.scope == query.scope.value)
        if query.memory_kind is not None:
            clauses.append(OrchestrationMemory.memory_kind == query.memory_kind)
        if query.subject is not None:
            clauses.append(OrchestrationMemory.subject == query.subject)
        if query.correlation_id is not None:
            clauses.append(OrchestrationMemory.correlation_id == query.correlation_id)
        if query.workflow_id is not None:
            clauses.append(OrchestrationMemory.workflow_id == query.workflow_id)
        if query.agent_id is not None:
            clauses.append(OrchestrationMemory.agent_id == query.agent_id)

        clauses.append(OrchestrationMemory.importance >= query.min_importance)
        clauses.append(
            or_(
                OrchestrationMemory.expires_at.is_(None),
                OrchestrationMemory.expires_at > datetime.utcnow(),
            )
        )

        candidates = (
            self.db.query(OrchestrationMemory)
            .filter(and_(*clauses))
            .order_by(OrchestrationMemory.importance.desc())
            .limit(max(query.limit * 4, 32))
            .all()
        )

        # Re-rank with composite score
        ranked = []
        now = datetime.utcnow()
        for memory in candidates:
            recency = self._recency(memory, now)
            pin_bonus = 0.2 if memory.is_pinned else 0.0
            score = (memory.importance * 0.55) + (recency * 0.3) + (memory.confidence * 0.15) + pin_bonus
            ranked.append((score, memory))

        ranked.sort(key=lambda item: item[0], reverse=True)
        winners = [m for _, m in ranked[: query.limit]]

        # Update access stats
        for memory in winners:
            memory.access_count = (memory.access_count or 0) + 1
            memory.last_accessed_at = now
        if winners:
            self.db.commit()

        return winners

    def pin(self, memory_id: UUID, pinned: bool = True) -> Optional[OrchestrationMemory]:
        memory = self.db.get(OrchestrationMemory, memory_id)
        if memory is None:
            return None
        memory.is_pinned = pinned
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def prune(self, *, before: datetime, min_importance: float = 0.1) -> int:
        """Hard delete low-importance items older than ``before``."""
        targets = (
            self.db.query(OrchestrationMemory)
            .filter(
                OrchestrationMemory.is_pinned.is_(False),
                OrchestrationMemory.importance < min_importance,
                OrchestrationMemory.created_at < before,
            )
            .all()
        )
        for memory in targets:
            self.db.delete(memory)
        if targets:
            self.db.commit()
        return len(targets)

    def _recency(self, memory: OrchestrationMemory, now: datetime) -> float:
        anchor = memory.last_accessed_at or memory.created_at or now
        age_hours = max(0.0, (now - anchor).total_seconds() / 3600.0)
        decay = math.exp(-age_hours / self.HALF_LIFE_HOURS)
        return max(0.0, min(1.0, decay))


# ---------------------------------------------------------------------------
# Dependency intelligence
# ---------------------------------------------------------------------------


class DependencyIntelligenceService:
    """Higher-order graph analytics for adaptive planning."""

    def __init__(self, db: Session, graph_service: Optional[KnowledgeGraphService] = None) -> None:
        self.db = db
        self.graph = graph_service or KnowledgeGraphService(db)

    def critical_path(
        self,
        *,
        kind: KnowledgeNodeKind | str,
        key: str,
        depth: int = 4,
        edge_kinds: Optional[Sequence[str]] = None,
    ) -> List[ExecutionKnowledgeNode]:
        """Compute the longest weighted path of dependencies starting from a node."""
        edge_kinds = list(edge_kinds or [KnowledgeEdgeKind.DEPENDS_ON.value, KnowledgeEdgeKind.PRECEDES.value])
        neighborhood = self.graph.neighborhood(kind, key, depth=depth, edge_kinds=edge_kinds)
        if neighborhood is None or not neighborhood.nodes:
            return []

        # Build adjacency restricted to neighborhood
        node_ids = {n.id for n in neighborhood.nodes}
        node_map = {n.id: n for n in neighborhood.nodes}
        forward: Dict[UUID, List[Tuple[UUID, float]]] = defaultdict(list)
        in_degree: Dict[UUID, int] = defaultdict(int)
        for edge in neighborhood.edges:
            if edge.source_node_id in node_ids and edge.target_node_id in node_ids:
                forward[edge.source_node_id].append((edge.target_node_id, edge.weight))
                in_degree[edge.target_node_id] += 1

        # Topological order via Kahn (cycles fall back to neighborhood order)
        topo: List[UUID] = []
        ready: deque[UUID] = deque(
            n.id for n in neighborhood.nodes if in_degree.get(n.id, 0) == 0
        )
        remaining = dict(in_degree)
        while ready:
            current = ready.popleft()
            topo.append(current)
            for nxt, _ in forward.get(current, []):
                remaining[nxt] = remaining.get(nxt, 0) - 1
                if remaining[nxt] == 0:
                    ready.append(nxt)

        if len(topo) != len(neighborhood.nodes):
            topo = [n.id for n in neighborhood.nodes]

        # DP for longest weighted path
        best_score: Dict[UUID, float] = {nid: 0.0 for nid in topo}
        parent: Dict[UUID, Optional[UUID]] = {nid: None for nid in topo}
        for nid in topo:
            for nxt, weight in forward.get(nid, []):
                candidate = best_score[nid] + max(weight, 1.0)
                if candidate > best_score.get(nxt, 0.0):
                    best_score[nxt] = candidate
                    parent[nxt] = nid

        terminal = max(best_score.items(), key=lambda kv: kv[1])[0] if best_score else neighborhood.root.id

        # Walk parents back
        path: List[UUID] = []
        cursor: Optional[UUID] = terminal
        while cursor is not None and cursor in node_map and len(path) < depth + 8:
            path.append(cursor)
            cursor = parent.get(cursor)
        path.reverse()
        return [node_map[nid] for nid in path]

    def blast_radius(
        self,
        *,
        kind: KnowledgeNodeKind | str,
        key: str,
        depth: int = 3,
    ) -> GraphReasoningResult:
        """Estimate downstream blast radius if a node fails."""
        neighborhood = self.graph.neighborhood(
            kind,
            key,
            depth=depth,
            edge_kinds=[
                KnowledgeEdgeKind.PRODUCES.value,
                KnowledgeEdgeKind.TRIGGERS.value,
                KnowledgeEdgeKind.GOVERNS.value,
                KnowledgeEdgeKind.PRECEDES.value,
            ],
        )
        if neighborhood is None:
            return GraphReasoningResult(summary="root node not found")

        affected = [
            f"{n.node_kind}:{n.node_key}" for n in neighborhood.nodes if n.id != neighborhood.root.id
        ]
        avg_weight = (
            sum(e.weight for e in neighborhood.edges) / len(neighborhood.edges)
            if neighborhood.edges
            else 0.0
        )
        insights = []
        if len(affected) >= 10:
            insights.append("high downstream coupling")
        if avg_weight >= 5.0:
            insights.append("strong dependency reinforcement; impact is likely")

        return GraphReasoningResult(
            summary=f"{len(affected)} downstream nodes within depth={depth}",
            blast_radius=affected,
            metrics={
                "downstream_count": float(len(affected)),
                "avg_edge_weight": avg_weight,
                "depth": float(depth),
            },
            insights=insights,
        )

    def cluster_by_tag(self, *, tag: str, limit: int = 50) -> List[ExecutionKnowledgeNode]:
        """Return nodes carrying ``tag`` ordered by centrality."""
        rows = (
            self.db.query(ExecutionKnowledgeNode)
            .filter(ExecutionKnowledgeNode.tags.contains([tag]))  # type: ignore[arg-type]
            .order_by(ExecutionKnowledgeNode.centrality.desc())
            .limit(limit)
            .all()
        )
        return rows

    def recompute_centrality(self, *, decay: float = 0.85) -> int:
        """Inexpensive degree-based centrality refresh."""
        in_counts: Dict[UUID, int] = defaultdict(int)
        out_counts: Dict[UUID, int] = defaultdict(int)
        for edge in self.db.query(DependencyEdge).filter(DependencyEdge.lifecycle_state == "active").all():
            in_counts[edge.target_node_id] += 1
            out_counts[edge.source_node_id] += 1

        nodes = self.db.query(ExecutionKnowledgeNode).all()
        for node in nodes:
            in_d = in_counts.get(node.id, 0)
            out_d = out_counts.get(node.id, 0)
            raw = in_d * decay + out_d * (1.0 - decay)
            node.centrality = math.log1p(raw)
        self.db.commit()
        return len(nodes)


__all__ = [
    "KnowledgeGraphService",
    "OrchestrationMemoryService",
    "DependencyIntelligenceService",
    "GraphNeighborhood",
    "MemoryQuery",
    "GraphReasoningResult",
]
