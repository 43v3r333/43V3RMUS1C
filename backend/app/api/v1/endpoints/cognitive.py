"""
Cognitive Endpoints - Knowledge graph, forecasting, creative, governance, and feedback.

Provides API endpoints for the entire cognitive operating core:
  - /cognitive/graph      : knowledge graph CRUD and traversal
  - /cognitive/memory      : orchestration memory operations
  - /cognitive/forecast    : execution forecasts and runtime predictions
  - /cognitive/creative    : creative profiles and narrative sequencing
  - /cognitive/governance  : agent governance, rules, and arbitration
  - /cognitive/feedback    : feedback ingestion and adaptive tuning
"""
from __future__ import annotations

from typing import List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Body, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User

from app.schemas.cognitive import (
    KnowledgeNodeCreate,
    KnowledgeNodeResponse,
    DependencyEdgeCreate,
    DependencyEdgeResponse,
    GraphNeighborhoodResponse,
    SemanticRelationshipCreate,
    SemanticRelationshipResponse,
    OrchestrationMemoryCreate,
    OrchestrationMemoryResponse,
    GraphSnapshotRequest,
    ForecastRequest,
    ExecutionForecastResponse,
    ForecastRealizeRequest,
    MultiStageGraphCreate,
    MultiStageGraphResponse,
    StrategySelectRequest,
    StrategyDecisionResponse,
    CreativeProfileCreate,
    CreativeProfileResponse,
    NarrativeSequenceCreate,
    NarrativeSequenceResponse,
    EmotionMappingCreate,
    EmotionMappingResponse,
    GovernanceRuleCreate,
    GovernanceRuleResponse,
    GovernanceActionEvaluateRequest,
    GovernanceDecisionResponse,
    ArbitrationPolicyCreate,
    ConflictResolutionResponse,
    FeedbackIngestRequest,
    FeedbackResponse,
    TuningCycleCreate,
    TuningCycleResponse,
    TuningParameterRequest,
    TuningRecommendationResponse,
)

# Import domain services
from app.domains.knowledge_graph import (
    KnowledgeGraphService,
    OrchestrationMemoryService,
    DependencyIntelligenceService,
    KnowledgeNodeKind,
    KnowledgeEdgeKind,
    MemoryScope,
    ExecutionKnowledgeNode,
)
from app.domains.forecasting import (
    ForecastingService,
    MultiStagePlanner,
    OrchestrationStrategyEngine,
    ForecastKind,
    ForecastHorizon,
    StrategyKind,
)
from app.domains.creative import (
    CreativeIntelligenceService,
    CinematicSequencerService,
    CreativeProfileService,
    NarrativeStructure,
    EmotionalArc,
    AudienceSegment,
)
from app.domains.governance import (
    GovernanceService,
    ArbitrationEngine,
    AuthorityRegistry,
    ArbitrationStrategy,
)
from app.domains.feedback import (
    FeedbackLoopService,
    AdaptiveTuningService,
    FeedbackType,
    TuningAction,
)


router = APIRouter(prefix="/cognitive", tags=["Cognitive Operating Core"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _kg(db: Session) -> KnowledgeGraphService:
    return KnowledgeGraphService(db)


def _mem(db: Session) -> OrchestrationMemoryService:
    return OrchestrationMemoryService(db)


def _dep(db: Session) -> DependencyIntelligenceService:
    return DependencyIntelligenceService(db)


def _fc(db: Session) -> ForecastingService:
    return ForecastingService(db)


def _planner(db: Session) -> MultiStagePlanner:
    return MultiStagePlanner(db)


def _strategy(db: Session) -> OrchestrationStrategyEngine:
    return OrchestrationStrategyEngine(db)


def _creative(db: Session) -> CreativeIntelligenceService:
    return CreativeIntelligenceService(db)


def _seq(db: Session) -> CinematicSequencerService:
    return CinematicSequencerService(db)


def _creative_prof(db: Session) -> CreativeProfileService:
    return CreativeProfileService(db)


def _gov(db: Session) -> GovernanceService:
    return GovernanceService(db)


def _arb(db: Session) -> ArbitrationEngine:
    return ArbitrationEngine(db)


def _feedback(db: Session) -> FeedbackLoopService:
    return FeedbackLoopService(db)


def _tuning(db: Session) -> AdaptiveTuningService:
    return AdaptiveTuningService(db)


# ---------------------------------------------------------------------------
# Knowledge Graph
# ---------------------------------------------------------------------------

@router.get("/graph/summary", response_model=dict)
async def graph_summary(db: Session = Depends(get_db)):
    """Get knowledge graph statistics."""
    service = _kg(db)
    return service.summary()


@router.post("/graph/nodes", response_model=KnowledgeNodeResponse)
async def upsert_node(
    data: KnowledgeNodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Upsert a knowledge graph node."""
    service = _kg(db)
    node = service.upsert_node(
        kind=data.node_kind,
        key=data.node_key,
        label=data.label,
        summary=data.summary,
        properties=data.properties,
        tags=data.tags,
        vector=data.vector,
        relevance_score=data.relevance_score,
        source_domain=data.source_domain,
        correlation_id=data.correlation_id,
        owner_id=data.owner_id or current_user.id,
    )
    return node


@router.get("/graph/nodes", response_model=List[KnowledgeNodeResponse])
async def list_nodes(
    kind: Optional[str] = Query(None),
    lifecycle_state: Optional[str] = "active",
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List knowledge graph nodes."""
    service = _kg(db)
    k = KnowledgeNodeKind(kind) if kind else None
    return service.list_nodes(kind=k, lifecycle_state=lifecycle_state, limit=limit, offset=offset)


@router.post("/graph/edges", response_model=DependencyEdgeResponse)
async def reinforce_edge(
    data: DependencyEdgeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create or reinforce a graph edge."""
    service = _kg(db)

    # Resolve source and target nodes
    source = service.get_node(data.source_kind, data.source_key)
    target = service.get_node(data.target_kind, data.target_key)
    if source is None or target is None:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"source or target node not found",
        )

    edge = service.reinforce_edge(
        source=source,
        target=target,
        kind=KnowledgeEdgeKind(data.edge_kind),
        label=data.label,
        correlation_id=data.correlation_id,
    )
    return edge


@router.post("/graph/neighborhood", response_model=GraphNeighborhoodResponse)
async def get_neighborhood(
    data: GraphSnapshotRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a graph neighborhood around a node."""
    service = _kg(db)
    result = service.neighborhood(
        kind=KnowledgeNodeKind(data.kind),
        key=data.key,
        depth=data.depth,
    )
    if result is None:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="node not found")
    return result


@router.post("/graph/snapshot")
async def create_snapshot(
    data: GraphSnapshotRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create and persist a graph snapshot."""
    service = _kg(db)
    snapshot = service.snapshot_neighborhood(
        kind=KnowledgeNodeKind(data.kind),
        key=data.key,
        depth=data.depth,
        purpose=data.purpose,
        correlation_id=data.correlation_id,
    )
    if snapshot is None:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="node not found")
    return {"snapshot_id": str(snapshot.id), "node_count": snapshot.node_count, "edge_count": snapshot.edge_count}


@router.get("/graph/neighborhood", response_model=GraphNeighborhoodResponse)
async def get_neighborhood_by_key(
    kind: str = Query(...),
    key: str = Query(...),
    depth: int = Query(2, ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a graph neighborhood by kind and key (GET variant)."""
    service = _kg(db)
    result = service.neighborhood(
        kind=KnowledgeNodeKind(kind),
        key=key,
        depth=depth,
    )
    if result is None:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="node not found")
    return result


# Relationships

@router.post("/graph/relationships", response_model=SemanticRelationshipResponse)
async def assert_relationship(
    data: SemanticRelationshipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Assert a semantic relationship."""
    service = _kg(db)
    rel = service.assert_relationship(
        subject_kind=data.subject_kind,
        subject_key=data.subject_key,
        predicate=data.predicate,
        object_kind=data.object_kind,
        object_key=data.object_key,
        confidence=data.confidence,
        weight=data.weight,
        evidence=data.evidence,
        derived_from=data.derived_from,
    )
    return rel


@router.get("/graph/relationships", response_model=List[SemanticRelationshipResponse])
async def list_relationships(
    subject_kind: Optional[str] = None,
    subject_key: Optional[str] = None,
    predicate: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List semantic relationships."""
    service = _kg(db)
    return service.list_relationships(
        subject_kind=subject_kind,
        subject_key=subject_key,
        predicate=predicate,
        limit=limit,
    )


# ---------------------------------------------------------------------------
# Orchestration Memory
# ---------------------------------------------------------------------------

@router.post("/memory", response_model=OrchestrationMemoryResponse)
async def remember(
    data: OrchestrationMemoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Store an orchestration memory item."""
    service = _mem(db)
    memory = service.remember(
        scope=MemoryScope(data.scope),
        memory_kind=data.memory_kind,
        subject=data.subject,
        title=data.title,
        content=data.content,
        importance=data.importance,
        confidence=data.confidence,
        correlation_id=data.correlation_id,
        workflow_id=data.workflow_id,
        agent_id=data.agent_id,
    )
    return memory


@router.get("/memory", response_model=List[OrchestrationMemoryResponse])
async def recall(
    scope: Optional[str] = Query(None),
    memory_kind: Optional[str] = None,
    subject: Optional[str] = None,
    correlation_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    min_importance: float = Query(0.0, ge=0, le=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Recall orchestration memory items."""
    service = _mem(db)
    from app.domains.knowledge_graph import MemoryQuery
    query = MemoryQuery(
        subject=subject,
        scope=MemoryScope(scope) if scope else None,
        memory_kind=memory_kind,
        correlation_id=correlation_id,
        workflow_id=workflow_id,
        agent_id=agent_id,
        min_importance=min_importance,
        limit=limit,
    )
    return service.recall(query)


@router.patch("/memory/{memory_id}/pin")
async def pin_memory(
    memory_id: UUID,
    pinned: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Pin or unpin a memory item."""
    service = _mem(db)
    memory = service.pin(memory_id, pinned)
    if memory is None:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="memory not found")
    return {"id": str(memory.id), "is_pinned": memory.is_pinned}


# ---------------------------------------------------------------------------
# Forecasting
# ---------------------------------------------------------------------------

@router.post("/forecast", response_model=ExecutionForecastResponse)
async def create_forecast(
    data: ForecastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create an execution forecast."""
    service = _fc(db)
    forecast = service.forecast(
        subject_kind=data.subject_kind,
        subject_key=data.subject_key,
        forecast_kind=ForecastKind(data.forecast_kind),
        features=data.features,
        horizon=ForecastHorizon(data.horizon) if data.horizon else None,
    )
    return forecast


@router.get("/forecast/active", response_model=List[ExecutionForecastResponse])
async def list_active_forecasts(
    subject_kind: Optional[str] = None,
    subject_key: Optional[str] = None,
    horizon: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List active (pending) forecasts."""
    service = _fc(db)
    return service.get_active_forecasts(
        subject_kind=subject_kind,
        subject_key=subject_key,
        horizon=horizon,
        limit=limit,
    )


@router.post("/forecast/realize")
async def realize_forecast(
    data: ForecastRealizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Record the realized outcome for a forecast."""
    service = _fc(db)
    forecast = service.realize_latest(
        subject_kind=data.subject_kind,
        subject_key=data.subject_key,
        forecast_kind=ForecastKind(data.forecast_kind),
        actual=data.actual_value,
    )
    if forecast is None:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no pending forecast found")
    return {"id": str(forecast.id), "error_pct": forecast.error_pct}


@router.get("/forecast/accuracy", response_model=dict)
async def get_forecast_accuracy(
    subject_kind: Optional[str] = None,
    forecast_kind: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get forecast accuracy metrics."""
    service = _fc(db)
    return service.get_forecast_accuracy(subject_kind=subject_kind, forecast_kind=forecast_kind)


@router.post("/forecast/multi-stage", response_model=MultiStageGraphResponse)
async def create_multi_stage_graph(
    data: MultiStageGraphCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a multi-stage execution graph."""
    service = _planner(db)
    graph = service.plan(
        subject_kind=data.subject_kind,
        subject_key=data.subject_key,
        plan_label=data.plan_label,
        steps=data.steps,
        selected_strategy=StrategyKind(data.selected_strategy) if data.selected_strategy else None,
        correlation_id=data.correlation_id,
        owner_id=current_user.id,
    )
    return graph


@router.get("/forecast/multi-stage", response_model=List[MultiStageGraphResponse])
async def list_active_graphs(
    subject_kind: Optional[str] = None,
    subject_key: Optional[str] = None,
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List active multi-stage execution graphs."""
    service = _planner(db)
    return service.get_active_graphs(subject_kind=subject_kind, subject_key=subject_key, limit=limit)


@router.post("/forecast/strategy", response_model=StrategyDecisionResponse)
async def select_strategy(
    data: StrategySelectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Select an orchestration strategy."""
    service = _strategy(db)
    decision = service.select(
        subject_kind=data.subject_kind,
        subject_key=data.subject_key,
        context=data.context,
        correlation_id=data.correlation_id,
    )
    return StrategyDecisionResponse(
        strategy=decision.strategy.value,
        rationale=decision.rationale,
        expected_improvement=decision.expected_improvement,
        confidence=decision.confidence,
        scores=decision.scores,
    )


@router.get("/forecast/strategy", response_model=dict)
async def get_active_strategy(
    subject_kind: str = Query(...),
    subject_key: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get the active strategy for a subject."""
    service = _strategy(db)
    strategy = service.get_active(subject_kind, subject_key)
    if strategy is None:
        return {"strategy_kind": None, "is_active": False}
    return {
        "strategy_kind": strategy.strategy_kind,
        "rationale": strategy.rationale,
        "scores": strategy.scores,
        "expected_improvement": strategy.expected_improvement,
        "confidence": strategy.confidence,
        "is_active": strategy.is_active,
    }


# ---------------------------------------------------------------------------
# Creative Intelligence
# ---------------------------------------------------------------------------

@router.post("/creative/profiles", response_model=CreativeProfileResponse)
async def create_creative_profile(
    data: CreativeProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a creative profile."""
    service = _creative(db)
    profile = service.create_profile(
        name=data.name,
        campaign_id=data.campaign_id,
        artist_id=data.artist_id,
        narrative_structure=NarrativeStructure(data.narrative_structure),
        emotional_arc=EmotionalArc(data.emotional_arc),
        pacing_profile=data.pacing_profile,
        visual_keywords=data.visual_keywords,
        audio_keywords=data.audio_keywords,
        target_segments=data.target_segments,
        owner_id=current_user.id,
    )
    return profile


@router.get("/creative/profiles", response_model=List[CreativeProfileResponse])
async def list_creative_profiles(
    campaign_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List creative profiles."""
    service = _creative(db)
    return service.list_profiles(campaign_id=campaign_id, limit=limit)


@router.post("/creative/sequences", response_model=NarrativeSequenceResponse)
async def create_narrative_sequence(
    data: NarrativeSequenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a narrative sequence."""
    service = _creative(db)
    seq = service.create_sequence(
        name=data.name,
        profile_id=data.profile_id,
        campaign_id=data.campaign_id,
        structure=NarrativeStructure(data.structure),
        emotional_arc=EmotionalArc(data.emotional_arc),
        beats=data.beats,
        target_duration=data.target_duration,
        target_bpm=data.target_bpm,
        target_key=data.target_key,
        owner_id=current_user.id,
    )
    return seq


@router.get("/creative/sequences", response_model=List[NarrativeSequenceResponse])
async def list_sequences(
    campaign_id: Optional[str] = None,
    profile_id: Optional[UUID] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List narrative sequences."""
    service = _creative(db)
    return service.list_sequences(campaign_id=campaign_id, profile_id=profile_id, limit=limit)


@router.post("/creative/emotion-mappings", response_model=EmotionMappingResponse)
async def create_emotion_mapping(
    data: EmotionMappingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create an audio-to-visual emotion mapping."""
    service = _creative(db)
    mapping = service.create_emotion_mapping(
        source_type=data.source_type,
        source_value=data.source_value,
        target_type=data.target_type,
        target_value=data.target_value,
        strength=data.strength,
        profile_id=data.profile_id,
        owner_id=current_user.id,
    )
    return mapping


@router.get("/creative/emotion-mappings", response_model=List[EmotionMappingResponse])
async def get_emotion_mappings(
    source_type: str = Query(...),
    source_value: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get emotion mappings for a source."""
    service = _creative(db)
    return service.get_emotion_mapping(source_type=source_type, source_value=source_value)


@router.post("/creative/build-arc")
async def build_narrative_arc(
    campaign_id: str = Query(...),
    asset_count: int = Query(8, ge=1, le=100),
    style_hint: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Build a narrative arc automatically."""
    service = _creative(db)
    arc = service.build_narrative_arc(
        campaign_id=campaign_id,
        asset_count=asset_count,
        style_hint=style_hint,
    )
    return arc


@router.get("/creative/engagement-prediction", response_model=dict)
async def predict_engagement(
    audience_segment: str = Query(...),
    content_duration: float = Query(...),
    content_type: str = Query("short_form"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Predict audience engagement for a content profile."""
    service = _creative_prof(db)
    result = service.predict_engagement(
        audience_segment=AudienceSegment(audience_segment),
        content_duration=content_duration,
        content_type=content_type,
    )
    return result


# ---------------------------------------------------------------------------
# Governance
# ---------------------------------------------------------------------------

@router.get("/governance/rules", response_model=List[GovernanceRuleResponse])
async def list_governance_rules(
    agent_kind: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List governance rules."""
    service = _gov(db)
    return service.get_rules(agent_kind=agent_kind, limit=limit)


@router.post("/governance/rules", response_model=GovernanceRuleResponse)
async def create_governance_rule(
    data: GovernanceRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a governance rule."""
    service = _gov(db)
    rule = service.create_rule(
        name=data.name,
        rule_type=data.rule_type,
        conditions=data.conditions,
        action=data.action,
        agent_kind=data.agent_kind,
        priority=data.priority,
        owner_id=current_user.id,
    )
    return rule


@router.post("/governance/evaluate", response_model=GovernanceDecisionResponse)
async def evaluate_action(
    data: GovernanceActionEvaluateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Evaluate whether an agent action is permitted."""
    service = _gov(db)
    decision = service.evaluate_action(
        agent_id=data.agent_id,
        agent_kind=data.agent_kind,
        action_type=data.action_type,
        action_params=data.action_params,
    )
    return GovernanceDecisionResponse(
        action=decision.action,
        reason=decision.reason,
        triggered_rules=[r.rule.name for r in decision.triggered_rules],
        escalation_agent=decision.escalation_agent,
        confidence=decision.confidence,
    )


@router.post("/governance/arbitration-policies", response_model=dict)
async def create_arbitration_policy(
    data: ArbitrationPolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create an arbitration policy."""
    service = _gov(db)
    policy = service.create_arbitration_policy(
        name=data.name,
        domain=data.domain,
        strategy=ArbitrationStrategy(data.strategy),
        fallback_strategy=ArbitrationStrategy(data.fallback_strategy) if data.fallback_strategy else None,
        escalation_threshold=data.escalation_threshold,
        priority=data.priority,
    )
    return {"id": str(policy.id), "name": policy.name, "domain": policy.domain, "strategy": policy.strategy}


@router.post("/governance/conflicts", response_model=ConflictResolutionResponse)
async def register_conflict(
    domain: str = Query(...),
    agents: List[dict] = Body(...),
    conflicting_actions: List[dict] = Body(...),
    context: Optional[dict] = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Register and resolve a conflict between agents."""
    service = _gov(db)
    resolution = service.register_conflict(
        domain=domain,
        agents=agents,
        conflicting_actions=conflicting_actions,
        context=context,
    )
    return resolution


@router.get("/governance/conflicts", response_model=List[ConflictResolutionResponse])
async def list_active_conflicts(
    domain: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List active conflicts."""
    service = _arb(db)
    return service.get_active_conflicts(domain=domain)


@router.get("/governance/violations", response_model=list)
async def list_violations(
    agent_id: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List policy violations."""
    service = _gov(db)
    return service.list_violations(agent_id=agent_id, resolved=resolved, limit=limit)


@router.get("/governance/authority-level")
async def get_authority_level(
    agent_kind: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get authority level for an agent kind."""
    service = _gov(db)
    level = service.get_authority_level(agent_kind)
    return {"agent_kind": agent_kind, "authority_level": level}


# ---------------------------------------------------------------------------
# Feedback / Tuning
# ---------------------------------------------------------------------------

@router.post("/feedback", response_model=FeedbackResponse)
async def ingest_feedback(
    data: FeedbackIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ingest an execution feedback signal."""
    service = _feedback(db)
    feedback = service.ingest(
        subject_kind=data.subject_kind,
        subject_key=data.subject_key,
        feedback_type=FeedbackType(data.feedback_type),
        actual_value=data.actual_value,
        expected_value=data.expected_value,
        quality_score=data.quality_score,
        error_rate=data.error_rate,
        context=data.context,
        workflow_id=data.workflow_id,
        agent_id=data.agent_id,
        execution_start=data.execution_start,
    )
    return feedback


@router.get("/feedback", response_model=List[FeedbackResponse])
async def get_feedback(
    subject_key: Optional[str] = None,
    feedback_type: Optional[str] = None,
    workflow_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get recent feedback signals."""
    service = _feedback(db)
    return service.get_recent_feedback(
        subject_key=subject_key,
        feedback_type=FeedbackType(feedback_type) if feedback_type else None,
        limit=limit,
    )


@router.get("/feedback/analysis", response_model=dict)
async def analyze_feedback_outcomes(
    subject_kind: Optional[str] = None,
    feedback_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get aggregate outcome statistics."""
    service = _feedback(db)
    return service.analyze_outcomes(subject_kind=subject_kind, feedback_type=FeedbackType(feedback_type) if feedback_type else None)


@router.post("/feedback/tuning-cycles", response_model=TuningCycleResponse)
async def create_tuning_cycle(
    data: TuningCycleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create an autonomous tuning cycle."""
    service = _tuning(db)
    cycle = service.create_tuning_cycle(
        context_key=data.context_key,
        target_metric=data.target_metric,
        target_improvement=data.target_improvement,
        max_iterations=data.max_iterations,
        description=data.description,
    )
    return cycle


@router.post("/feedback/tune", response_model=dict)
async def tune_parameter(
    data: TuningParameterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Apply a parameter tuning step."""
    service = _tuning(db)
    record = service.tune_parameter(
        parameter_name=data.parameter_name,
        context_key=data.context_key,
        current_value=data.current_value,
        outcome_score=data.outcome_score,
        action=TuningAction(data.action),
        reason=data.reason,
        triggered_by=data.triggered_by,
        cycle_id=data.cycle_id,
        correlation_id=data.correlation_id,
    )
    return {
        "record_id": str(record.id),
        "before_value": record.before_value,
        "after_value": record.after_value,
        "delta": record.delta,
        "tuning_state": record.tuning_state,
    }


@router.get("/feedback/tuning-recommendations", response_model=List[TuningRecommendationResponse])
async def get_tuning_recommendations(
    context_key: str = Query(...),
    parameters: str = Query(..., description="comma-separated parameter names"),
    current_values: str = Query(..., description="JSON dict of param->value"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get tuning recommendations for parameters."""
    import json
    service = _tuning(db)
    params = [p.strip() for p in parameters.split(",")]
    values = json.loads(current_values)
    # Get last 10 outcomes for context
    recent_outcomes = [0.5] * 10
    return service.get_tuning_recommendations(
        context_key=context_key,
        parameters=params,
        current_values=values,
        recent_outcomes=recent_outcomes,
    )


@router.get("/feedback/tuning-cycles", response_model=List[TuningCycleResponse])
async def list_tuning_cycles(
    context_key: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List tuning cycles."""
    service = _tuning(db)
    if context_key:
        cycle = service.get_active_cycle(context_key)
        return [cycle] if cycle else []
    return service.get_tuning_history(limit=limit)


@router.get("/feedback/tuning-history", response_model=list)
async def get_tuning_history(
    parameter_name: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get tuning history records."""
    service = _tuning(db)
    return service.get_tuning_history(parameter_name=parameter_name, limit=limit)