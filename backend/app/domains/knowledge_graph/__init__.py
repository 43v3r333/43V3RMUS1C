"""
Knowledge Graph Domain - Semantic orchestration memory and execution intelligence.

The knowledge graph stores typed nodes (workflows, executions, assets, agents) and
typed edges (dependencies, produces, derived_from, etc.) so the cognitive layer can
reason about the past, the present and the planned future of every orchestration.
"""
from .models import (
    KnowledgeNodeKind,
    KnowledgeEdgeKind,
    MemoryScope,
    OrchestrationMemory,
    SemanticRelationship,
    ExecutionKnowledgeNode,
    DependencyEdge,
    ExecutionGraphSnapshot,
)
from .services import (
    KnowledgeGraphService,
    OrchestrationMemoryService,
    DependencyIntelligenceService,
    GraphNeighborhood,
    MemoryQuery,
    GraphReasoningResult,
)

__all__ = [
    # Enums
    "KnowledgeNodeKind",
    "KnowledgeEdgeKind",
    "MemoryScope",
    # Models
    "OrchestrationMemory",
    "SemanticRelationship",
    "ExecutionKnowledgeNode",
    "DependencyEdge",
    "ExecutionGraphSnapshot",
    # Services
    "KnowledgeGraphService",
    "OrchestrationMemoryService",
    "DependencyIntelligenceService",
    # Data
    "GraphNeighborhood",
    "MemoryQuery",
    "GraphReasoningResult",
]
