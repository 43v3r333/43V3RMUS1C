"""
Coherence API Router - Unified Runtime Identity and Cognitive Continuity.

Provides RESTful endpoints for:
- Runtime identity management
- Orchestration lineage tracking
- Cognitive memory operations
- Semantic execution coordination
- Adaptive runtime tuning
- Governance enforcement
- Stability prediction
- Distributed agent coordination
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ...core.deps import get_db, CurrentUser
from ...domains.coherence.services import (
    UnifiedIdentityManager,
    CognitiveContinuityEngine,
    SemanticCoordinator,
    AdaptiveRuntimeTuner,
    GovernanceEnforcer,
    StabilityPredictor,
    DistributedCoherenceService,
)
from ...domains.coherence.models import (
    IdentityScope,
    LineageEventType,
    MemoryRetrievalMode,
    SemanticRelationType,
    TuningStrategy,
    PolicySeverity,
    StabilityStatus,
    ConsensusState,
    ExecutionHorizon,
)

router = APIRouter(prefix="/coherence", tags=["coherence"])


# ============================================================================
# Request/Response Models
# ============================================================================


# Identity Models
class IdentityCreateRequest(BaseModel):
    identity_scope: str
    identity_key: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    correlation_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = {}
    capabilities: Optional[List[str]] = []
    owner_id: Optional[str] = None


class IdentityUpdateRequest(BaseModel):
    properties: Optional[Dict[str, Any]] = None
    lifecycle_state: Optional[str] = None


class IdentityResponse(BaseModel):
    id: str
    identity_scope: str
    identity_key: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    root_id: Optional[str] = None
    properties: Dict[str, Any]
    capabilities: List[str]
    lifecycle_state: str
    version: int
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    created_at: datetime
    last_accessed_at: Optional[datetime] = None


# Context Models
class ContextSetRequest(BaseModel):
    context_key: str
    value: Dict[str, Any]
    context_scope: Optional[str] = None
    expires_at: Optional[datetime] = None
    correlation_id: Optional[str] = None


class ContextResponse(BaseModel):
    id: str
    identity_id: str
    context_key: str
    context_scope: str
    value: Dict[str, Any]
    version: int
    correlation_id: Optional[str] = None


# Memory Models
class MemoryStoreRequest(BaseModel):
    scope: str
    memory_kind: str
    subject: str
    title: str
    content: Dict[str, Any]
    importance: float = 0.5
    confidence: float = 1.0
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    correlation_id: Optional[str] = None
    is_pinned: bool = False
    expires_at: Optional[datetime] = None


class MemoryResponse(BaseModel):
    id: str
    identity_id: str
    scope: str
    memory_kind: str
    subject: str
    title: str
    content: Dict[str, Any]
    importance: float
    recency: float
    confidence: float
    access_count: int
    last_accessed_at: Optional[datetime] = None
    created_at: datetime


# Semantic Graph Models
class GraphCreateRequest(BaseModel):
    graph_id: str
    name: str
    description: Optional[str] = None
    owner_id: Optional[str] = None
    correlation_id: Optional[str] = None


class NodeAddRequest(BaseModel):
    node_key: str
    node_type: str
    semantic_key: str
    label: str
    properties: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []
    semantic_type: str = "execution"
    position_x: float = 0.0
    position_y: float = 0.0


class EdgeAddRequest(BaseModel):
    source_key: str
    target_key: str
    relation_type: str
    label: Optional[str] = None
    weight: float = 1.0
    confidence: float = 1.0
    attributes: Optional[Dict[str, Any]] = {}


# Adaptive Profile Models
class ProfileCreateRequest(BaseModel):
    profile_key: str
    context_key: str
    parameters: Optional[Dict[str, Any]] = {}
    baseline_metrics: Optional[Dict[str, float]] = {}
    tuning_strategy: str = "gradient_ascent"
    correlation_id: Optional[str] = None


class ParametersUpdateRequest(BaseModel):
    parameters: Dict[str, Any]
    record_tuning: bool = True


class MetricsRecordRequest(BaseModel):
    metrics: Dict[str, float]
    iteration: Optional[int] = None


# Governance Models
class PolicyCreateRequest(BaseModel):
    policy_key: str
    name: str
    policy_scope: str
    conditions: Dict[str, Any]
    enforcement_action: str
    description: Optional[str] = None
    severity: str = "warning"
    action_config: Optional[Dict[str, Any]] = {}
    priority: int = 0
    owner_id: Optional[str] = None


class PolicyEvaluationRequest(BaseModel):
    context: Dict[str, Any]
    scope_filter: Optional[List[str]] = None


class ArbitrationRequest(BaseModel):
    arbitration_type: str
    parties: List[str]
    context: Dict[str, Any]


# Stability Models
class StabilityMetricsRequest(BaseModel):
    metrics: Dict[str, Any]
    correlation_id: Optional[str] = None


class ForecastCreateRequest(BaseModel):
    subject_kind: str
    subject_key: str
    forecast_kind: str
    horizon: str
    predicted_value: float
    predicted_unit: Optional[str] = None
    confidence: float = 0.8
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    features: Optional[Dict[str, float]] = None


class AnomalyDetectionRequest(BaseModel):
    anomaly_type: str
    description: str
    baseline: Dict[str, float]
    observed: Dict[str, float]
    metric_name: str
    severity: str = "warning"
    threshold: Optional[float] = None


# Distributed Coordination Models
class ContextStateCreateRequest(BaseModel):
    context_key: str
    partition_key: str
    state: Dict[str, Any]
    participating_nodes: Optional[List[str]] = []
    correlation_id: Optional[str] = None
    expires_at: Optional[datetime] = None


class ContextStateUpdateRequest(BaseModel):
    state: Dict[str, Any]
    node_id: str
    wait_for_consensus: bool = True
    required_nodes: int = 3


class ConsensusInitiateRequest(BaseModel):
    topic_kind: str
    topic_key: str
    required_votes: int = 3
    expires_at: Optional[datetime] = None


class VoteCastRequest(BaseModel):
    agent_id: str
    vote: str
    reason: str


class AuthorityDelegateRequest(BaseModel):
    delegate_id: str
    authority_type: str
    scope: Optional[Dict[str, Any]] = {}
    constraints: Optional[Dict[str, Any]] = {}
    max_depth: int = 3
    expires_at: Optional[datetime] = None


# ============================================================================
# Service Dependency
# ============================================================================


async def get_coherence_services(db=Depends(get_db)):
    """Get all coherence services initialized with database session"""
    identity_manager = UnifiedIdentityManager(db)
    cognitive_engine = CognitiveContinuityEngine(db, identity_manager)
    semantic_coordinator = SemanticCoordinator(db, identity_manager)
    runtime_tuner = AdaptiveRuntimeTuner(db, identity_manager)
    governance_enforcer = GovernanceEnforcer(db, identity_manager)
    stability_predictor = StabilityPredictor(db, identity_manager)
    distributed_service = DistributedCoherenceService(db, identity_manager)
    
    return {
        "identity_manager": identity_manager,
        "cognitive_engine": cognitive_engine,
        "semantic_coordinator": semantic_coordinator,
        "runtime_tuner": runtime_tuner,
        "governance_enforcer": governance_enforcer,
        "stability_predictor": stability_predictor,
        "distributed_service": distributed_service,
    }


# ============================================================================
# Identity Endpoints
# ============================================================================


@router.post("/identities", response_model=Dict[str, Any])
async def create_identity(
    request: IdentityCreateRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Create a new runtime identity with associated lineage and context"""
    identity_manager = services["identity_manager"]
    
    parent_id = UUID(request.parent_id) if request.parent_id else None
    owner_id = UUID(request.owner_id) if request.owner_id else None
    
    result = await identity_manager.create_identity(
        identity_scope=IdentityScope(request.identity_scope),
        identity_key=request.identity_key,
        name=request.name,
        description=request.description,
        parent_id=parent_id,
        correlation_id=request.correlation_id,
        properties=request.properties,
        capabilities=request.capabilities,
        owner_id=owner_id,
    )
    
    return {
        "identity": {
            "id": str(result.identity.id),
            "identity_scope": result.identity.identity_scope,
            "identity_key": result.identity.identity_key,
            "name": result.identity.name,
            "trace_id": result.identity.trace_id,
        },
        "lineage": {
            "id": str(result.lineage.id),
            "started_at": result.lineage.started_at.isoformat(),
        },
        "context": {
            "id": str(result.context.id),
            "context_key": result.context.context_key,
        },
    }


@router.get("/identities/{scope}/{key}", response_model=IdentityResponse)
async def get_identity(
    scope: str,
    key: str,
    services: Dict = Depends(get_coherence_services),
):
    """Get identity by scope and key"""
    identity_manager = services["identity_manager"]
    
    identity = await identity_manager.get_identity(
        identity_scope=IdentityScope(scope),
        identity_key=key,
    )
    
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")
    
    return IdentityResponse(
        id=str(identity.id),
        identity_scope=identity.identity_scope,
        identity_key=identity.identity_key,
        name=identity.name,
        description=identity.description,
        parent_id=str(identity.parent_id) if identity.parent_id else None,
        root_id=str(identity.root_id) if identity.root_id else None,
        properties=identity.properties,
        capabilities=identity.capabilities,
        lifecycle_state=identity.lifecycle_state,
        version=identity.version,
        correlation_id=identity.correlation_id,
        trace_id=identity.trace_id,
        created_at=identity.created_at,
        last_accessed_at=identity.last_accessed_at,
    )


@router.get("/identities/by-id/{identity_id}", response_model=IdentityResponse)
async def get_identity_by_id(
    identity_id: str,
    services: Dict = Depends(get_coherence_services),
):
    """Get identity by ID"""
    identity_manager = services["identity_manager"]
    
    identity = await identity_manager.get_identity_by_id(UUID(identity_id))
    
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")
    
    return IdentityResponse(
        id=str(identity.id),
        identity_scope=identity.identity_scope,
        identity_key=identity.identity_key,
        name=identity.name,
        description=identity.description,
        parent_id=str(identity.parent_id) if identity.parent_id else None,
        root_id=str(identity.root_id) if identity.root_id else None,
        properties=identity.properties,
        capabilities=identity.capabilities,
        lifecycle_state=identity.lifecycle_state,
        version=identity.version,
        correlation_id=identity.correlation_id,
        trace_id=identity.trace_id,
        created_at=identity.created_at,
        last_accessed_at=identity.last_accessed_at,
    )


@router.patch("/identities/{identity_id}", response_model=IdentityResponse)
async def update_identity(
    identity_id: str,
    request: IdentityUpdateRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Update identity properties"""
    identity_manager = services["identity_manager"]
    
    identity = await identity_manager.update_identity(
        identity_id=UUID(identity_id),
        properties=request.properties,
        lifecycle_state=request.lifecycle_state,
    )
    
    return IdentityResponse(
        id=str(identity.id),
        identity_scope=identity.identity_scope,
        identity_key=identity.identity_key,
        name=identity.name,
        description=identity.description,
        parent_id=str(identity.parent_id) if identity.parent_id else None,
        root_id=str(identity.root_id) if identity.root_id else None,
        properties=identity.properties,
        capabilities=identity.capabilities,
        lifecycle_state=identity.lifecycle_state,
        version=identity.version,
        correlation_id=identity.correlation_id,
        trace_id=identity.trace_id,
        created_at=identity.created_at,
        last_accessed_at=identity.last_accessed_at,
    )


@router.post("/identities/{identity_id}/context", response_model=Dict[str, Any])
async def propagate_context(
    identity_id: str,
    request: ContextSetRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Propagate context across identity hierarchy"""
    identity_manager = services["identity_manager"]
    
    contexts = await identity_manager.propagate_context(
        source_identity_id=UUID(identity_id),
        context_key=request.context_key,
        value=request.value,
        correlation_id=request.correlation_id,
    )
    
    return {
        "contexts": [
            {
                "id": str(ctx.id),
                "context_key": ctx.context_key,
                "context_scope": ctx.context_scope,
                "propagation_depth": ctx.propagation_depth,
            }
            for ctx in contexts
        ],
    }


@router.get("/identities/{identity_id}/lineage", response_model=Dict[str, Any])
async def get_identity_lineage(
    identity_id: str,
    event_types: Optional[str] = Query(None, description="Comma-separated event types"),
    limit: int = Query(100, le=500),
    services: Dict = Depends(get_coherence_services),
):
    """Get lineage for an identity"""
    identity_manager = services["identity_manager"]
    
    lineage = await identity_manager.get_lineage(UUID(identity_id))
    
    if not lineage:
        raise HTTPException(status_code=404, detail="Lineage not found")
    
    # Get nodes
    types_filter = event_types.split(",") if event_types else None
    nodes = await identity_manager.get_lineage_nodes(
        lineage_id=lineage.id,
        event_types=types_filter,
        limit=limit,
    )
    
    return {
        "lineage": {
            "id": str(lineage.id),
            "root_identity_id": str(lineage.root_identity_id),
            "lineage_type": lineage.lineage_type,
            "status": lineage.status,
            "total_nodes": lineage.total_nodes,
            "total_events": lineage.total_events,
            "depth": lineage.depth,
            "started_at": lineage.started_at.isoformat(),
            "completed_at": lineage.completed_at.isoformat() if lineage.completed_at else None,
        },
        "nodes": [
            {
                "node_id": node.node_id,
                "event_type": node.event_type,
                "depth": node.depth,
                "timestamp": node.timestamp.isoformat(),
                "duration_ms": node.duration_ms,
                "correlation_id": node.correlation_id,
            }
            for node in nodes
        ],
    }


# ============================================================================
# Context Endpoints
# ============================================================================


@router.post("/contexts/{identity_id}", response_model=ContextResponse)
async def set_context(
    identity_id: str,
    request: ContextSetRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Set context value for an identity"""
    identity_manager = services["identity_manager"]
    
    context = await identity_manager.set_context(
        identity_id=UUID(identity_id),
        context_key=request.context_key,
        value=request.value,
        context_scope=request.context_scope,
        expires_at=request.expires_at,
        correlation_id=request.correlation_id,
    )
    
    return ContextResponse(
        id=str(context.id),
        identity_id=str(context.identity_id),
        context_key=context.context_key,
        context_scope=context.context_scope,
        value=context.value,
        version=context.version,
        correlation_id=context.correlation_id,
    )


@router.get("/contexts/{identity_id}/{context_key}", response_model=ContextResponse)
async def get_context(
    identity_id: str,
    context_key: str,
    services: Dict = Depends(get_coherence_services),
):
    """Get context value for an identity"""
    identity_manager = services["identity_manager"]
    
    context = await identity_manager.get_context(
        identity_id=UUID(identity_id),
        context_key=context_key,
    )
    
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    
    return ContextResponse(
        id=str(context.id),
        identity_id=str(context.identity_id),
        context_key=context.context_key,
        context_scope=context.context_scope,
        value=context.value,
        version=context.version,
        correlation_id=context.correlation_id,
    )


@router.get("/contexts/{identity_id}", response_model=List[ContextResponse])
async def get_contexts_by_scope(
    identity_id: str,
    scope: Optional[str] = None,
    services: Dict = Depends(get_coherence_services),
):
    """Get all contexts for an identity"""
    identity_manager = services["identity_manager"]
    
    contexts = await identity_manager.get_contexts_by_scope(
        identity_id=UUID(identity_id),
        scope=scope,
    )
    
    return [
        ContextResponse(
            id=str(ctx.id),
            identity_id=str(ctx.identity_id),
            context_key=ctx.context_key,
            context_scope=ctx.context_scope,
            value=ctx.value,
            version=ctx.version,
            correlation_id=ctx.correlation_id,
        )
        for ctx in contexts
    ]


# ============================================================================
# Memory Endpoints
# ============================================================================


@router.post("/memory/{identity_id}", response_model=MemoryResponse)
async def store_memory(
    identity_id: str,
    request: MemoryStoreRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Store a cognitive memory item"""
    cognitive_engine = services["cognitive_engine"]
    
    memory = await cognitive_engine.store(
        identity_id=UUID(identity_id),
        scope=request.scope,
        memory_kind=request.memory_kind,
        subject=request.subject,
        title=request.title,
        content=request.content,
        importance=request.importance,
        confidence=request.confidence,
        workflow_id=request.workflow_id,
        agent_id=request.agent_id,
        correlation_id=request.correlation_id,
        is_pinned=request.is_pinned,
        expires_at=request.expires_at,
    )
    
    return MemoryResponse(
        id=str(memory.id),
        identity_id=str(memory.identity_id),
        scope=memory.scope,
        memory_kind=memory.memory_kind,
        subject=memory.subject,
        title=memory.title,
        content=memory.content,
        importance=memory.importance,
        recency=memory.recency,
        confidence=memory.confidence,
        access_count=memory.access_count,
        last_accessed_at=memory.last_accessed_at,
        created_at=memory.created_at,
    )


@router.get("/memory/{identity_id}", response_model=Dict[str, Any])
async def recall_memory(
    identity_id: str,
    scope: Optional[str] = None,
    memory_kind: Optional[str] = None,
    subject: Optional[str] = None,
    retrieval_mode: str = Query("mixed", description="semantic, episodic, procedural, mixed, contextual"),
    min_importance: float = Query(0.0, ge=0, le=1),
    limit: int = Query(50, le=200),
    services: Dict = Depends(get_coherence_services),
):
    """Recall memory items based on retrieval mode"""
    cognitive_engine = services["cognitive_engine"]
    
    result = await cognitive_engine.recall(
        identity_id=UUID(identity_id),
        scope=scope,
        memory_kind=memory_kind,
        subject=subject,
        retrieval_mode=MemoryRetrievalMode(retrieval_mode),
        min_importance=min_importance,
        limit=limit,
    )
    
    return {
        "items": [
            {
                "id": str(item.id),
                "scope": item.scope,
                "memory_kind": item.memory_kind,
                "subject": item.subject,
                "title": item.title,
                "importance": item.importance,
                "recency": item.recency,
                "confidence": item.confidence,
                "access_count": item.access_count,
                "created_at": item.created_at.isoformat(),
            }
            for item in result.items
        ],
        "fragments": [
            {
                "id": str(frag.id),
                "memory_id": str(frag.memory_id),
                "fragment_id": frag.fragment_id,
                "fragment_type": frag.fragment_type,
                "relevance_score": frag.relevance_score,
            }
            for frag in result.fragments
        ],
        "relevance_scores": result.relevance_scores,
        "total_importance": result.total_importance,
    }


# ============================================================================
# Semantic Graph Endpoints
# ============================================================================


@router.post("/graphs", response_model=Dict[str, Any])
async def create_graph(
    request: GraphCreateRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Create a semantic execution graph"""
    identity_id = request.owner_id or "system"
    
    # Get or create system identity
    identity_manager = services["identity_manager"]
    identity_result = await identity_manager.create_identity(
        identity_scope=IdentityScope.SYSTEM,
        identity_key=f"graph:{request.graph_id}",
        name=request.name,
        description=request.description,
        correlation_id=request.correlation_id,
    )
    
    semantic_coordinator = services["semantic_coordinator"]
    
    graph = await semantic_coordinator.create_graph(
        identity_id=identity_result.identity.id,
        graph_id=request.graph_id,
        name=request.name,
        description=request.description,
        owner_id=UUID(request.owner_id) if request.owner_id else None,
        correlation_id=request.correlation_id,
    )
    
    return {
        "graph_id": graph.graph_id,
        "name": graph.name,
        "node_count": graph.node_count,
        "edge_count": graph.edge_count,
    }


@router.get("/graphs/{graph_id}", response_model=Dict[str, Any])
async def get_graph(
    graph_id: str,
    services: Dict = Depends(get_coherence_services),
):
    """Get semantic execution graph"""
    semantic_coordinator = services["semantic_coordinator"]
    
    graph = await semantic_coordinator.get_graph(graph_id)
    
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    return {
        "graph_id": graph.graph_id,
        "name": graph.name,
        "description": graph.description,
        "nodes": graph.nodes,
        "edges": graph.edges,
        "node_count": graph.node_count,
        "edge_count": graph.edge_count,
        "semantic_depth": graph.semantic_depth,
        "lifecycle_state": graph.lifecycle_state,
    }


@router.post("/graphs/{graph_id}/nodes", response_model=Dict[str, Any])
async def add_node(
    graph_id: str,
    request: NodeAddRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Add a node to a semantic graph"""
    semantic_coordinator = services["semantic_coordinator"]
    
    node = await semantic_coordinator.add_node(
        graph_id=graph_id,
        node_key=request.node_key,
        node_type=request.node_type,
        semantic_key=request.semantic_key,
        label=request.label,
        properties=request.properties,
        tags=request.tags,
        semantic_type=request.semantic_type,
        position_x=request.position_x,
        position_y=request.position_y,
    )
    
    return {
        "node_id": str(node.id),
        "node_key": node.node_key,
        "node_type": node.node_type,
        "semantic_key": node.semantic_key,
        "label": node.label,
    }


@router.post("/graphs/{graph_id}/edges", response_model=Dict[str, Any])
async def add_edge(
    graph_id: str,
    request: EdgeAddRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Add an edge to a semantic graph"""
    semantic_coordinator = services["semantic_coordinator"]
    
    edge = await semantic_coordinator.add_edge(
        graph_id=graph_id,
        source_key=request.source_key,
        target_key=request.target_key,
        relation_type=SemanticRelationType(request.relation_type),
        label=request.label,
        weight=request.weight,
        confidence=request.confidence,
        attributes=request.attributes,
    )
    
    if not edge:
        raise HTTPException(status_code=400, detail="Could not create edge - source or target node not found")
    
    return {
        "edge_id": str(edge.id),
        "source_key": request.source_key,
        "target_key": request.target_key,
        "relation_type": edge.relation_type,
    }


@router.get("/graphs/{graph_id}/path", response_model=Dict[str, Any])
async def find_path(
    graph_id: str,
    source_key: str,
    target_key: str,
    max_depth: int = Query(10, le=50),
    services: Dict = Depends(get_coherence_services),
):
    """Find semantic path between nodes"""
    semantic_coordinator = services["semantic_coordinator"]
    
    path = await semantic_coordinator.find_path(
        graph_id=graph_id,
        source_key=source_key,
        target_key=target_key,
        max_depth=max_depth,
    )
    
    if not path:
        return {"path": None, "message": "No path found"}
    
    return {
        "nodes": path.nodes,
        "edges": path.edges,
        "total_weight": path.total_weight,
        "confidence": path.confidence,
    }


# ============================================================================
# Adaptive Runtime Endpoints
# ============================================================================


@router.post("/profiles", response_model=Dict[str, Any])
async def create_profile(
    request: ProfileCreateRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Create an adaptive profile"""
    runtime_tuner = services["runtime_tuner"]
    
    profile = await runtime_tuner.create_profile(
        identity_id=UUID("00000000-0000-0000-0000-000000000000"),  # System identity
        profile_key=request.profile_key,
        context_key=request.context_key,
        parameters=request.parameters,
        baseline_metrics=request.baseline_metrics,
        tuning_strategy=TuningStrategy(request.tuning_strategy),
        correlation_id=request.correlation_id,
    )
    
    return {
        "profile_id": str(profile.id),
        "profile_key": profile.profile_key,
        "context_key": profile.context_key,
        "optimization_iterations": profile.optimization_iterations,
    }


@router.get("/profiles/{profile_key}/{context_key}", response_model=Dict[str, Any])
async def get_profile(
    profile_key: str,
    context_key: str,
    services: Dict = Depends(get_coherence_services),
):
    """Get adaptive profile"""
    runtime_tuner = services["runtime_tuner"]
    
    profile = await runtime_tuner.get_profile(profile_key, context_key)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "profile_id": str(profile.id),
        "profile_key": profile.profile_key,
        "context_key": profile.context_key,
        "parameters": profile.parameters,
        "baseline_metrics": profile.baseline_metrics,
        "current_metrics": profile.current_metrics,
        "best_score": profile.best_score,
        "optimization_iterations": profile.optimization_iterations,
        "profile_state": profile.profile_state,
        "last_tuned_at": profile.last_tuned_at.isoformat() if profile.last_tuned_at else None,
    }


@router.patch("/profiles/{profile_id}", response_model=Dict[str, Any])
async def update_parameters(
    profile_id: str,
    request: ParametersUpdateRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Update profile parameters"""
    runtime_tuner = services["runtime_tuner"]
    
    profile, history = await runtime_tuner.update_parameters(
        profile_id=UUID(profile_id),
        parameters=request.parameters,
        record_tuning=request.record_tuning,
    )
    
    return {
        "profile_id": str(profile.id),
        "parameters": profile.parameters,
        "optimization_iterations": profile.optimization_iterations,
        "tuning_history": {
            "tuning_id": history.tuning_id if history else None,
            "improvement_percent": history.improvement_percent if history else None,
        } if history else None,
    }


@router.post("/profiles/{profile_id}/metrics", response_model=Dict[str, Any])
async def record_metrics(
    profile_id: str,
    request: MetricsRecordRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Record optimization metrics"""
    runtime_tuner = services["runtime_tuner"]
    
    metric = await runtime_tuner.record_metrics(
        profile_id=UUID(profile_id),
        metrics=request.metrics,
        iteration=request.iteration,
    )
    
    return {
        "metric_id": str(metric.id),
        "metric_name": metric.metric_name,
        "value": metric.value,
        "iteration": metric.iteration,
    }


@router.get("/profiles/{profile_id}/suggestions", response_model=Dict[str, Any])
async def suggest_parameters(
    profile_id: str,
    services: Dict = Depends(get_coherence_services),
):
    """Get suggested optimized parameters"""
    runtime_tuner = services["runtime_tuner"]
    
    suggested = await runtime_tuner.suggest_parameters(UUID(profile_id))
    
    return {"suggested_parameters": suggested}


# ============================================================================
# Governance Endpoints
# ============================================================================


@router.post("/policies", response_model=Dict[str, Any])
async def create_policy(
    request: PolicyCreateRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Create a governance policy"""
    governance_enforcer = services["governance_enforcer"]
    
    policy = await governance_enforcer.create_policy(
        policy_key=request.policy_key,
        name=request.name,
        policy_scope=request.policy_scope,
        conditions=request.conditions,
        enforcement_action=request.enforcement_action,
        description=request.description,
        severity=PolicySeverity(request.severity),
        action_config=request.action_config,
        priority=request.priority,
        owner_id=UUID(request.owner_id) if request.owner_id else None,
    )
    
    return {
        "policy_id": str(policy.id),
        "policy_key": policy.policy_key,
        "name": policy.name,
        "trigger_count": policy.trigger_count,
    }


@router.post("/evaluate", response_model=Dict[str, Any])
async def evaluate_policies(
    identity_id: str,
    request: PolicyEvaluationRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Evaluate policies for a context"""
    governance_enforcer = services["governance_enforcer"]
    
    result = await governance_enforcer.evaluate_policies(
        identity_id=UUID(identity_id),
        context=request.context,
        scope_filter=request.scope_filter,
    )
    
    return {
        "triggered": result.triggered,
        "policy": {
            "id": str(result.policy.id) if result.policy else None,
            "name": result.policy.name if result.policy else None,
            "enforcement_action": result.enforcement_action,
        } if result.policy else None,
        "violations": [
            {
                "id": str(v.id),
                "severity": v.severity,
                "violation_type": v.violation_type,
            }
            for v in result.violations
        ],
        "reason": result.reason,
    }


@router.post("/arbitrate", response_model=Dict[str, Any])
async def arbitrate(
    identity_id: str,
    request: ArbitrationRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Perform orchestration arbitration"""
    governance_enforcer = services["governance_enforcer"]
    
    record = await governance_enforcer.arbitrate(
        identity_id=UUID(identity_id),
        arbitration_type=request.arbitration_type,
        parties=request.parties,
        context=request.context,
    )
    
    return {
        "record_id": record.record_id,
        "arbitration_type": record.arbitration_type,
        "decision": record.decision,
        "reason": record.reason,
        "confidence": record.confidence,
        "decided_at": record.decided_at.isoformat(),
    }


@router.get("/violations", response_model=List[Dict[str, Any]])
async def get_violations(
    policy_id: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(100, le=500),
    services: Dict = Depends(get_coherence_services),
):
    """Get policy violations"""
    governance_enforcer = services["governance_enforcer"]
    
    violations = await governance_enforcer.get_violations(
        policy_id=UUID(policy_id) if policy_id else None,
        severity=severity,
        limit=limit,
    )
    
    return [
        {
            "id": str(v.id),
            "violation_id": v.violation_id,
            "severity": v.severity,
            "violation_type": v.violation_type,
            "description": v.description,
            "detected_at": v.detected_at.isoformat(),
            "resolved": v.is_resolved,
        }
        for v in violations
    ]


# ============================================================================
# Stability & Prediction Endpoints
# ============================================================================


@router.post("/stability/{identity_id}", response_model=Dict[str, Any])
async def record_stability_metrics(
    identity_id: str,
    request: StabilityMetricsRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Record stability metrics"""
    stability_predictor = services["stability_predictor"]
    
    metrics = await stability_predictor.record_stability_metrics(
        identity_id=UUID(identity_id),
        metrics=request.metrics,
        correlation_id=request.correlation_id,
    )
    
    return {
        "stability_id": str(metrics.id),
        "stability_status": metrics.stability_status,
        "stability_score": metrics.stability_score,
        "health_score": metrics.health_score,
        "error_rate": metrics.error_rate,
    }


@router.get("/stability/{identity_id}/assessment", response_model=Dict[str, Any])
async def assess_stability(
    identity_id: str,
    window_seconds: int = Query(300, le=3600),
    services: Dict = Depends(get_coherence_services),
):
    """Assess stability of an identity"""
    stability_predictor = services["stability_predictor"]
    
    assessment = await stability_predictor.assess_stability(
        identity_id=UUID(identity_id),
        window_seconds=window_seconds,
    )
    
    return {
        "status": assessment.status.value,
        "score": assessment.score,
        "health_score": assessment.health_score,
        "issues": assessment.issues,
        "recommendations": assessment.recommendations,
    }


@router.post("/forecasts", response_model=Dict[str, Any])
async def create_forecast(
    request: ForecastCreateRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Create an execution forecast"""
    stability_predictor = services["stability_predictor"]
    
    forecast = await stability_predictor.create_forecast(
        subject_kind=request.subject_kind,
        subject_key=request.subject_key,
        forecast_kind=request.forecast_kind,
        horizon=ExecutionHorizon(request.horizon),
        predicted_value=request.predicted_value,
        predicted_unit=request.predicted_unit,
        confidence=request.confidence,
        min_value=request.min_value,
        max_value=request.max_value,
        features=request.features,
    )
    
    return {
        "forecast_id": forecast.forecast_id,
        "subject_key": forecast.subject_key,
        "forecast_kind": forecast.forecast_kind,
        "horizon": forecast.horizon,
        "predicted_value": forecast.predicted_value,
        "confidence": forecast.confidence,
        "predicted_for": forecast.predicted_for.isoformat(),
    }


@router.get("/forecasts", response_model=List[Dict[str, Any]])
async def get_active_forecasts(
    subject_key: Optional[str] = None,
    forecast_kind: Optional[str] = None,
    limit: int = Query(20, le=100),
    services: Dict = Depends(get_coherence_services),
):
    """Get active forecasts"""
    stability_predictor = services["stability_predictor"]
    
    forecasts = await stability_predictor.get_active_forecasts(
        subject_key=subject_key,
        forecast_kind=forecast_kind,
        limit=limit,
    )
    
    return [
        {
            "forecast_id": f.forecast_id,
            "subject_kind": f.subject_kind,
            "subject_key": f.subject_key,
            "forecast_kind": f.forecast_kind,
            "horizon": f.horizon,
            "predicted_value": f.predicted_value,
            "predicted_unit": f.predicted_unit,
            "confidence": f.confidence,
            "predicted_for": f.predicted_for.isoformat(),
            "forecast_state": f.forecast_state,
        }
        for f in forecasts
    ]


@router.post("/anomalies/{identity_id}", response_model=Dict[str, Any])
async def detect_anomaly(
    identity_id: str,
    request: AnomalyDetectionRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Detect and record an anomaly"""
    stability_predictor = services["stability_predictor"]
    
    anomaly = await stability_predictor.detect_anomaly(
        identity_id=UUID(identity_id),
        anomaly_type=request.anomaly_type,
        description=request.description,
        baseline=request.baseline,
        observed=request.observed,
        metric_name=request.metric_name,
        severity=request.severity,
        threshold=request.threshold,
    )
    
    return {
        "anomaly_id": anomaly.anomaly_id,
        "anomaly_type": anomaly.anomaly_type,
        "severity": anomaly.severity,
        "deviation": anomaly.deviation,
        "detected_at": anomaly.detected_at.isoformat(),
    }


@router.get("/anomalies", response_model=List[Dict[str, Any]])
async def get_recent_anomalies(
    identity_id: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    limit: int = Query(50, le=200),
    services: Dict = Depends(get_coherence_services),
):
    """Get recent anomalies"""
    stability_predictor = services["stability_predictor"]
    
    anomalies = await stability_predictor.get_recent_anomalies(
        identity_id=UUID(identity_id) if identity_id else None,
        is_resolved=is_resolved,
        limit=limit,
    )
    
    return [
        {
            "anomaly_id": a.anomaly_id,
            "anomaly_type": a.anomaly_type,
            "severity": a.severity,
            "description": a.description,
            "deviation": a.deviation,
            "detected_at": a.detected_at.isoformat(),
            "is_resolved": a.is_resolved,
        }
        for a in anomalies
    ]


# ============================================================================
# Distributed Coordination Endpoints
# ============================================================================


@router.post("/distributed-contexts", response_model=Dict[str, Any])
async def create_context_state(
    identity_id: str,
    request: ContextStateCreateRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Create a distributed context state"""
    distributed_service = services["distributed_service"]
    
    ctx_state = await distributed_service.create_context_state(
        identity_id=UUID(identity_id),
        context_key=request.context_key,
        partition_key=request.partition_key,
        state=request.state,
        participating_nodes=request.participating_nodes,
        correlation_id=request.correlation_id,
        expires_at=request.expires_at,
    )
    
    return {
        "context_id": str(ctx_state.id),
        "context_key": ctx_state.context_key,
        "partition_key": ctx_state.partition_key,
        "consensus_state": ctx_state.consensus_state,
    }


@router.patch("/distributed-contexts/{context_key}/{partition_key}", response_model=Dict[str, Any])
async def update_context_state(
    context_key: str,
    partition_key: str,
    request: ContextStateUpdateRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Update a distributed context state"""
    distributed_service = services["distributed_service"]
    
    ctx_state = await distributed_service.update_context_state(
        context_key=context_key,
        partition_key=partition_key,
        state=request.state,
        node_id=request.node_id,
        wait_for_consensus=request.wait_for_consensus,
        required_nodes=request.required_nodes,
    )
    
    return {
        "version": ctx_state.version,
        "consensus_state": ctx_state.consensus_state,
        "participating_nodes": ctx_state.participating_nodes,
    }


@router.get("/distributed-contexts/{context_key}/{partition_key}", response_model=Dict[str, Any])
async def get_context_state(
    context_key: str,
    partition_key: str,
    services: Dict = Depends(get_coherence_services),
):
    """Get distributed context state"""
    distributed_service = services["distributed_service"]
    
    ctx_state = await distributed_service.get_context_state(context_key, partition_key)
    
    if not ctx_state:
        raise HTTPException(status_code=404, detail="Context state not found")
    
    return {
        "context_id": str(ctx_state.id),
        "context_key": ctx_state.context_key,
        "partition_key": ctx_state.partition_key,
        "state": ctx_state.state,
        "version": ctx_state.version,
        "consensus_state": ctx_state.consensus_state,
        "participating_nodes": ctx_state.participating_nodes,
        "node_versions": ctx_state.node_versions,
    }


@router.post("/consensus", response_model=Dict[str, Any])
async def initiate_consensus(
    request: ConsensusInitiateRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Initiate agent consensus"""
    distributed_service = services["distributed_service"]
    
    consensus = await distributed_service.initiate_consensus(
        topic_kind=request.topic_kind,
        topic_key=request.topic_key,
        required_votes=request.required_votes,
        expires_at=request.expires_at,
    )
    
    return {
        "consensus_id": consensus.consensus_id,
        "topic_key": consensus.topic_key,
        "consensus_state": consensus.consensus_state,
        "required_votes": consensus.required_votes,
    }


@router.post("/consensus/{consensus_id}/vote", response_model=Dict[str, Any])
async def cast_vote(
    consensus_id: str,
    request: VoteCastRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Cast a vote in consensus"""
    distributed_service = services["distributed_service"]
    
    consensus = await distributed_service.cast_vote(
        consensus_id=consensus_id,
        agent_id=request.agent_id,
        vote=request.vote,
        reason=request.reason,
    )
    
    return {
        "consensus_id": consensus.consensus_id,
        "decision": consensus.decision,
        "consensus_state": consensus.consensus_state,
        "gathered_votes": consensus.gathered_votes,
        "confidence": consensus.confidence,
    }


@router.get("/consensus/{consensus_id}", response_model=Dict[str, Any])
async def get_consensus(
    consensus_id: str,
    services: Dict = Depends(get_coherence_services),
):
    """Get consensus by ID"""
    distributed_service = services["distributed_service"]
    
    consensus = await distributed_service.get_consensus(consensus_id)
    
    if not consensus:
        raise HTTPException(status_code=404, detail="Consensus not found")
    
    return {
        "consensus_id": consensus.consensus_id,
        "topic_kind": consensus.topic_kind,
        "topic_key": consensus.topic_key,
        "decision": consensus.decision,
        "reason": consensus.reason,
        "votes": consensus.votes,
        "consensus_state": consensus.consensus_state,
        "confidence": consensus.confidence,
        "gathered_votes": consensus.gathered_votes,
        "required_votes": consensus.required_votes,
    }


@router.post("/delegation", response_model=Dict[str, Any])
async def delegate_authority(
    delegator_id: str,
    request: AuthorityDelegateRequest,
    services: Dict = Depends(get_coherence_services),
):
    """Delegate authority to another agent"""
    distributed_service = services["distributed_service"]
    
    delegation = await distributed_service.delegate_authority(
        delegator_id=delegator_id,
        delegate_id=request.delegate_id,
        authority_type=request.authority_type,
        scope=request.scope,
        constraints=request.constraints,
        max_depth=request.max_depth,
        expires_at=request.expires_at,
    )
    
    return {
        "delegation_id": delegation.delegation_id,
        "delegator_id": delegation.delegator_id,
        "delegate_id": delegation.delegate_id,
        "authority_type": delegation.authority_type,
        "delegation_state": delegation.delegation_state,
    }


@router.post("/delegation/{delegation_id}/invoke", response_model=Dict[str, Any])
async def invoke_delegated_authority(
    delegation_id: str,
    services: Dict = Depends(get_coherence_services),
):
    """Invoke a delegated authority"""
    distributed_service = services["distributed_service"]
    
    delegation = await distributed_service.invoke_delegated_authority(delegation_id)
    
    return {
        "delegation_id": delegation.delegation_id,
        "current_depth": delegation.current_depth,
        "invocation_count": delegation.invocation_count,
        "delegation_state": delegation.delegation_state,
    }


@router.post("/delegation/{delegation_id}/revoke", response_model=Dict[str, Any])
async def revoke_delegation(
    delegation_id: str,
    reason: str,
    services: Dict = Depends(get_coherence_services),
):
    """Revoke an authority delegation"""
    distributed_service = services["distributed_service"]
    
    delegation = await distributed_service.revoke_delegation(delegation_id, reason)
    
    return {
        "delegation_id": delegation.delegation_id,
        "delegation_state": delegation.delegation_state,
        "revocation_reason": delegation.revocation_reason,
    }


# ============================================================================
# System Status Endpoint
# ============================================================================


@router.get("/status", response_model=Dict[str, Any])
async def get_system_status(
    services: Dict = Depends(get_coherence_services),
):
    """Get overall coherence system status"""
    identity_manager = services["identity_manager"]
    
    return {
        "service": "coherence",
        "status": "operational",
        "capabilities": [
            "unified_identity",
            "cognitive_continuity",
            "semantic_coordination",
            "adaptive_runtime",
            "governance_enforcement",
            "stability_prediction",
            "distributed_coordination",
        ],
        "timestamp": datetime.utcnow().isoformat(),
    }