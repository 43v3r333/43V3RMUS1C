"""
Cognitive Kernel API Endpoints

Orchestration memory, strategic planning, creative reasoning,
multi-agent governance, and self-evolution endpoints.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.deps import get_current_user, get_optional_user

from app.domains.cognitive import (
    OrchestrationMemoryService,
    StrategicPlanningService,
    OrchestrationForecastService,
    CreativeReasoningService,
    SemanticArchiveService,
    MultiAgentGovernanceService,
    SelfEvolutionService,
    store_execution_insight,
)
from app.models.cognitive import (
    MemoryScope, MemoryKind, PlanStatus, PlanHorizon, StrategyKind,
    GovernanceRole, TuningState, ForecastKind, ForecastHorizon,
)

router = APIRouter(prefix="/cognitive", tags=["cognitive"])


# ============================================================
# ORCHESTRATION MEMORY ENDPOINTS
# ============================================================

@router.post("/memories")
async def create_memory(
    scope: str,
    memory_kind: str,
    title: str,
    content: Dict[str, Any],
    subject: Optional[str] = None,
    subject_kind: Optional[str] = None,
    importance: float = 0.5,
    confidence: float = 0.8,
    tags: Optional[List[str]] = None,
    execution_context: Optional[Dict[str, Any]] = None,
    outcome: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Store a new orchestration memory.
    
    Args:
        scope: MemoryScope (episodic, semantic, procedural, evaluative, strategic)
        memory_kind: MemoryKind (execution_insight, workflow_audit, etc.)
        title: Memory title
        content: Structured memory data
        
    Returns:
        Created memory
    """
    service = OrchestrationMemoryService(db)
    memory = await service.store(
        scope=scope,
        memory_kind=memory_kind,
        title=title,
        content=content,
        subject=subject,
        subject_kind=subject_kind,
        importance=importance,
        confidence=confidence,
        tags=tags,
        execution_context=execution_context,
        outcome=outcome,
    )
    await db.commit()
    return {"id": str(memory.id), "status": "created"}


@router.get("/memories")
async def list_memories(
    subject: Optional[str] = None,
    scope: Optional[str] = None,
    memory_kind: Optional[str] = None,
    subject_kind: Optional[str] = None,
    min_importance: float = 0.0,
    min_confidence: float = 0.0,
    tags: Optional[str] = None,
    search_text: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
):
    """
    List orchestration memories with filtering.
    
    Args:
        subject: Filter by subject
        scope: Filter by scope
        memory_kind: Filter by kind
        min_importance: Minimum importance
        min_confidence: Minimum confidence
        tags: Comma-separated tags
        search_text: Full-text search
        limit: Max results
        offset: Result offset
        
    Returns:
        List of memories
    """
    service = OrchestrationMemoryService(db)
    tag_list = tags.split(",") if tags else None
    
    memories = await service.recall(
        subject=subject,
        scope=scope,
        memory_kind=memory_kind,
        subject_kind=subject_kind,
        min_importance=min_importance,
        min_confidence=min_confidence,
        tags=tag_list,
        search_text=search_text,
        limit=limit,
        offset=offset,
    )
    
    return {
        "items": [
            {
                "id": str(m.id),
                "scope": m.scope,
                "memory_kind": m.memory_kind,
                "title": m.title,
                "subject": m.subject,
                "importance": m.importance,
                "confidence": m.confidence,
                "access_count": m.access_count,
                "recency": m.recency,
                "is_pinned": m.is_pinned,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in memories
        ],
        "total": len(memories),
        "limit": limit,
        "offset": offset,
    }


@router.get("/memories/{memory_id}")
async def get_memory(
    memory_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a specific memory by ID with access tracking."""
    service = OrchestrationMemoryService(db)
    memory = await service.get_by_id(memory_id)
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return {
        "id": str(memory.id),
        "scope": memory.scope,
        "memory_kind": memory.memory_kind,
        "title": memory.title,
        "content": memory.content,
        "subject": memory.subject,
        "subject_kind": memory.subject_kind,
        "importance": memory.importance,
        "confidence": memory.confidence,
        "access_count": memory.access_count,
        "last_accessed_at": memory.last_accessed_at.isoformat() if memory.last_accessed_at else None,
        "recency": memory.recency,
        "is_pinned": memory.is_pinned,
        "tags": memory.tags,
        "execution_context": memory.execution_context,
        "outcome": memory.outcome,
        "created_at": memory.created_at.isoformat() if memory.created_at else None,
        "updated_at": memory.updated_at.isoformat() if memory.updated_at else None,
    }


@router.delete("/memories/{memory_id}")
async def delete_memory(
    memory_id: UUID,
    hard: bool = False,
    db: AsyncSession = Depends(get_async_db),
):
    """Delete a memory."""
    service = OrchestrationMemoryService(db)
    deleted = await service.delete(memory_id, soft=not hard)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    await db.commit()
    return {"status": "deleted"}


@router.post("/memories/{memory_id}/pin")
async def pin_memory(
    memory_id: UUID,
    pinned: bool = True,
    db: AsyncSession = Depends(get_async_db),
):
    """Pin or unpin a memory."""
    service = OrchestrationMemoryService(db)
    memory = await service.update(memory_id, is_pinned=pinned)
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    await db.commit()
    return {"status": "updated", "is_pinned": pinned}


@router.get("/memories/stats")
async def get_memory_stats(
    db: AsyncSession = Depends(get_async_db),
):
    """Get memory system statistics."""
    service = OrchestrationMemoryService(db)
    stats = await service.get_statistics()
    return stats


@router.get("/memories/patterns")
async def analyze_patterns(
    subject_kind: Optional[str] = None,
    days: int = 7,
    min_frequency: int = 2,
    db: AsyncSession = Depends(get_async_db),
):
    """Analyze execution patterns."""
    from datetime import timedelta
    service = OrchestrationMemoryService(db)
    
    time_window = timedelta(days=days) if days > 0 else None
    patterns = await service.analyze_patterns(
        subject_kind=subject_kind,
        time_window=time_window,
        min_frequency=min_frequency,
    )
    
    return {"patterns": patterns}


# ============================================================
# STRATEGIC PLANNING ENDPOINTS
# ============================================================

@router.post("/plans")
async def create_plan(
    name: str,
    plan_type: str,
    strategy_kind: str,
    objectives: List[Dict[str, Any]],
    horizon: str = PlanHorizon.MEDIUM_TERM.value,
    description: Optional[str] = None,
    dependencies: Optional[List[Dict[str, Any]]] = None,
    constraints: Optional[Dict[str, Any]] = None,
    required_resources: Optional[Dict[str, Any]] = None,
    estimated_start: Optional[datetime] = None,
    estimated_end: Optional[datetime] = None,
    priority: int = 5,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new strategic execution plan."""
    service = StrategicPlanningService(db)
    
    plan = await service.create_plan(
        name=name,
        plan_type=plan_type,
        strategy_kind=strategy_kind,
        objectives=objectives,
        horizon=horizon,
        description=description,
        dependencies=dependencies,
        constraints=constraints,
        required_resources=required_resources,
        estimated_start=estimated_start,
        estimated_end=estimated_end,
        priority=priority,
    )
    
    await db.commit()
    return {"id": str(plan.id), "status": "created"}


@router.get("/plans")
async def list_plans(
    status: Optional[str] = None,
    strategy_kind: Optional[str] = None,
    horizon: Optional[str] = None,
    min_priority: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
):
    """List strategic plans with filtering."""
    service = StrategicPlanningService(db)
    
    plans = await service.list_plans(
        status=status,
        strategy_kind=strategy_kind,
        horizon=horizon,
        min_priority=min_priority,
        limit=limit,
        offset=offset,
    )
    
    return {
        "items": [
            {
                "id": str(p.id),
                "name": p.name,
                "status": p.status,
                "horizon": p.horizon,
                "strategy_kind": p.strategy_kind,
                "priority": p.priority,
                "confidence_score": p.confidence_score,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in plans
        ],
        "total": len(plans),
    }


@router.get("/plans/{plan_id}")
async def get_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a strategic plan by ID."""
    service = StrategicPlanningService(db)
    plan = await service.get_plan(plan_id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return {
        "id": str(plan.id),
        "name": plan.name,
        "description": plan.description,
        "plan_type": plan.plan_type,
        "status": plan.status,
        "horizon": plan.horizon,
        "strategy_kind": plan.strategy_kind,
        "objectives": plan.objectives,
        "dependencies": plan.dependencies,
        "constraints": plan.constraints,
        "required_resources": plan.required_resources,
        "allocated_resources": plan.allocated_resources,
        "estimated_start": plan.estimated_start.isoformat() if plan.estimated_start else None,
        "estimated_end": plan.estimated_end.isoformat() if plan.estimated_end else None,
        "actual_start": plan.actual_start.isoformat() if plan.actual_start else None,
        "actual_end": plan.actual_end.isoformat() if plan.actual_end else None,
        "confidence_score": plan.confidence_score,
        "priority": plan.priority,
    }


@router.post("/plans/{plan_id}/activate")
async def activate_plan(
    plan_id: UUID,
    allocated_resources: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Activate a draft plan."""
    service = StrategicPlanningService(db)
    plan = await service.activate_plan(plan_id, allocated_resources)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    await db.commit()
    return {"status": "activated", "id": str(plan.id)}


@router.post("/plans/{plan_id}/complete")
async def complete_plan(
    plan_id: UUID,
    actual_outcomes: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Mark a plan as completed."""
    service = StrategicPlanningService(db)
    plan = await service.complete_plan(plan_id, actual_outcomes)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    await db.commit()
    return {"status": "completed", "id": str(plan.id)}


@router.get("/plans/stats")
async def get_planning_stats(
    db: AsyncSession = Depends(get_async_db),
):
    """Get strategic planning statistics."""
    service = StrategicPlanningService(db)
    stats = await service.get_statistics()
    return stats


# ============================================================
# FORECAST ENDPOINTS
# ============================================================

@router.post("/forecasts")
async def create_forecast(
    subject_kind: str,
    subject_key: str,
    forecast_kind: str,
    predicted_value: float,
    horizon: str,
    predicted_for: datetime,
    confidence: float = 0.5,
    lower_bound: Optional[float] = None,
    upper_bound: Optional[float] = None,
    features_used: Optional[Dict[str, Any]] = None,
    context_data: Optional[Dict[str, Any]] = None,
    prediction_method: str = "statistical",
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new execution forecast."""
    service = OrchestrationForecastService(db)
    
    forecast = await service.create_forecast(
        subject_kind=subject_kind,
        subject_key=subject_key,
        forecast_kind=forecast_kind,
        predicted_value=predicted_value,
        horizon=horizon,
        predicted_for=predicted_for,
        confidence=confidence,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        features_used=features_used,
        context_data=context_data,
        prediction_method=prediction_method,
    )
    
    await db.commit()
    return {"id": str(forecast.id), "status": "created"}


@router.get("/forecasts")
async def list_forecasts(
    subject_kind: Optional[str] = None,
    subject_key: Optional[str] = None,
    forecast_kind: Optional[str] = None,
    horizon: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_async_db),
):
    """List active forecasts."""
    service = OrchestrationForecastService(db)
    
    forecasts = await service.get_active_forecasts(
        subject_kind=subject_kind,
        subject_key=subject_key,
        forecast_kind=forecast_kind,
        horizon=horizon,
        limit=limit,
    )
    
    return {
        "items": [
            {
                "id": str(f.id),
                "subject_kind": f.subject_kind,
                "subject_key": f.subject_key,
                "forecast_kind": f.forecast_kind,
                "predicted_value": f.predicted_value,
                "confidence": f.confidence,
                "horizon": f.horizon,
                "predicted_for": f.predicted_for.isoformat() if f.predicted_for else None,
                "lifecycle_state": f.lifecycle_state,
            }
            for f in forecasts
        ],
        "total": len(forecasts),
    }


@router.get("/forecasts/accuracy")
async def get_forecast_accuracy(
    subject_kind: Optional[str] = None,
    days: int = 7,
    db: AsyncSession = Depends(get_async_db),
):
    """Calculate forecast accuracy metrics."""
    from datetime import timedelta
    service = OrchestrationForecastService(db)
    
    time_window = timedelta(days=days) if days > 0 else None
    accuracy = await service.get_forecast_accuracy(
        subject_kind=subject_kind,
        time_window=time_window,
    )
    
    return accuracy


# ============================================================
# CREATIVE REASONING ENDPOINTS
# ============================================================

@router.post("/profiles")
async def create_creative_profile(
    name: str,
    profile_type: str,
    narrative_structure: Optional[str] = None,
    emotional_arc: Optional[str] = None,
    pacing_profile: str = "steady",
    pacing_intensity: float = 0.5,
    visual_keywords: Optional[List[str]] = None,
    color_palette: Optional[List[str]] = None,
    audio_keywords: Optional[List[str]] = None,
    target_segments: Optional[List[str]] = None,
    attention_span_seconds: int = 60,
    completion_rate_target: float = 0.7,
    engagement_rate_target: float = 0.15,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new creative reasoning profile."""
    service = CreativeReasoningService(db)
    
    profile = await service.create_profile(
        name=name,
        profile_type=profile_type,
        narrative_structure=narrative_structure,
        emotional_arc=emotional_arc,
        pacing_profile=pacing_profile,
        pacing_intensity=pacing_intensity,
        visual_keywords=visual_keywords,
        color_palette=color_palette,
        audio_keywords=audio_keywords,
        target_segments=target_segments,
        attention_span_seconds=attention_span_seconds,
        completion_rate_target=completion_rate_target,
        engagement_rate_target=engagement_rate_target,
    )
    
    await db.commit()
    return {"id": str(profile.id), "status": "created"}


@router.get("/profiles")
async def list_creative_profiles(
    profile_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
):
    """List creative profiles."""
    service = CreativeReasoningService(db)
    
    profiles = await service.list_profiles(
        profile_type=profile_type,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    
    return {
        "items": [
            {
                "id": str(p.id),
                "name": p.name,
                "profile_type": p.profile_type,
                "narrative_structure": p.narrative_structure,
                "emotional_arc": p.emotional_arc,
                "pacing_profile": p.pacing_profile,
                "is_active": p.is_active,
                "version": p.version,
            }
            for p in profiles
        ],
        "total": len(profiles),
    }


@router.get("/profiles/{profile_id}")
async def get_creative_profile(
    profile_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a creative profile by ID."""
    service = CreativeReasoningService(db)
    profile = await service.get_profile(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {
        "id": str(profile.id),
        "name": profile.name,
        "profile_type": profile.profile_type,
        "narrative_structure": profile.narrative_structure,
        "emotional_arc": profile.emotional_arc,
        "pacing_profile": profile.pacing_profile,
        "pacing_intensity": profile.pacing_intensity,
        "visual_keywords": profile.visual_keywords,
        "color_palette": profile.color_palette,
        "audio_keywords": profile.audio_keywords,
        "target_segments": profile.target_segments,
        "attention_span_seconds": profile.attention_span_seconds,
        "completion_rate_target": profile.completion_rate_target,
        "engagement_rate_target": profile.engagement_rate_target,
        "is_active": profile.is_active,
        "version": profile.version,
    }


@router.post("/profiles/{profile_id}/analyze")
async def analyze_content_narrative(
    profile_id: UUID,
    content_segments: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_async_db),
):
    """Analyze content segments against a profile's narrative structure."""
    service = CreativeReasoningService(db)
    analysis = await service.analyze_narrative_structure(profile_id, content_segments)
    return analysis


@router.post("/profiles/{profile_id}/predict")
async def predict_engagement(
    profile_id: UUID,
    content_data: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db),
):
    """Predict engagement metrics for content."""
    service = CreativeReasoningService(db)
    prediction = await service.predict_engagement(profile_id, content_data)
    return prediction


# ============================================================
# MULTI-AGENT GOVERNANCE ENDPOINTS
# ============================================================

@router.post("/sessions")
async def create_governance_session(
    name: str,
    session_type: str,
    coordinator_id: Optional[str] = None,
    participant_ids: Optional[List[str]] = None,
    authority_level: str = GovernanceRole.ORCHESTRATOR.value,
    scope_kind: Optional[str] = None,
    scope_id: Optional[str] = None,
    expected_duration: Optional[int] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new governance session."""
    service = MultiAgentGovernanceService(db)
    
    session = await service.create_session(
        name=name,
        session_type=session_type,
        coordinator_id=coordinator_id,
        participant_ids=participant_ids,
        authority_level=authority_level,
        scope_kind=scope_kind,
        scope_id=scope_id,
        expected_duration=expected_duration,
    )
    
    await db.commit()
    return {"id": str(session.id), "status": "created"}


@router.get("/sessions")
async def list_governance_sessions(
    status: Optional[str] = None,
    session_type: Optional[str] = None,
    coordinator_id: Optional[str] = None,
    scope_kind: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
):
    """List governance sessions."""
    service = MultiAgentGovernanceService(db)
    
    sessions = await service.list_sessions(
        status=status,
        session_type=session_type,
        coordinator_id=coordinator_id,
        scope_kind=scope_kind,
        limit=limit,
        offset=offset,
    )
    
    return {
        "items": [
            {
                "id": str(s.id),
                "name": s.name,
                "session_type": s.session_type,
                "status": s.status,
                "coordinator_id": s.coordinator_id,
                "participant_count": len(s.participant_ids or []),
                "consensus_reached": s.consensus_reached,
                "efficiency_score": s.efficiency_score,
            }
            for s in sessions
        ],
        "total": len(sessions),
    }


@router.get("/sessions/{session_id}")
async def get_governance_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a governance session by ID."""
    service = MultiAgentGovernanceService(db)
    session = await service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "id": str(session.id),
        "name": session.name,
        "session_type": session.session_type,
        "status": session.status,
        "coordinator_id": session.coordinator_id,
        "participant_ids": session.participant_ids,
        "authority_level": session.authority_level,
        "scope_kind": session.scope_kind,
        "scope_id": session.scope_id,
        "actions_taken": session.actions_taken,
        "decisions_made": session.decisions_made,
        "negotiation_rounds": session.negotiation_rounds,
        "consensus_reached": session.consensus_reached,
        "disagreements": session.disagreements,
        "resolution": session.resolution,
        "efficiency_score": session.efficiency_score,
        "session_start": session.session_start.isoformat() if session.session_start else None,
        "session_end": session.session_end.isoformat() if session.session_end else None,
    }


@router.post("/sessions/{session_id}/action")
async def add_session_action(
    session_id: UUID,
    action_type: str,
    agent_id: str,
    action_data: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db),
):
    """Add a governance action to a session."""
    service = MultiAgentGovernanceService(db)
    session = await service.add_action(session_id, action_type, agent_id, action_data)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await db.commit()
    return {"status": "action_added"}


@router.post("/sessions/{session_id}/consensus")
async def reach_consensus(
    session_id: UUID,
    consensus_data: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db),
):
    """Mark consensus as reached."""
    service = MultiAgentGovernanceService(db)
    session = await service.reach_consensus(session_id, consensus_data)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await db.commit()
    return {"status": "consensus_reached"}


@router.post("/sessions/{session_id}/end")
async def end_governance_session(
    session_id: UUID,
    resolution: Optional[Dict[str, Any]] = None,
    execution_plan: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """End a governance session."""
    service = MultiAgentGovernanceService(db)
    session = await service.end_session(session_id, resolution, execution_plan)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await db.commit()
    return {"status": "ended", "efficiency_score": session.efficiency_score}


@router.get("/sessions/stats")
async def get_governance_stats(
    db: AsyncSession = Depends(get_async_db),
):
    """Get governance system statistics."""
    service = MultiAgentGovernanceService(db)
    stats = await service.get_statistics()
    return stats


# ============================================================
# SELF-EVOLUTION ENDPOINTS
# ============================================================

@router.post("/optimization/cycles")
async def create_optimization_cycle(
    cycle_id: str,
    name: str,
    context_key: str,
    target_metric: str,
    parameter_space: Dict[str, Any],
    target_improvement: float = 0.1,
    max_iterations: int = 10,
    patience: int = 3,
    baseline_score: Optional[float] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new optimization cycle."""
    service = SelfEvolutionService(db)
    
    cycle = await service.create_cycle(
        cycle_id=cycle_id,
        name=name,
        context_key=context_key,
        target_metric=target_metric,
        parameter_space=parameter_space,
        target_improvement=target_improvement,
        max_iterations=max_iterations,
        patience=patience,
        baseline_score=baseline_score,
    )
    
    await db.commit()
    return {"cycle_id": cycle.cycle_id, "status": "created"}


@router.post("/optimization/cycles/{cycle_id}/start")
async def start_optimization_cycle(
    cycle_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Start an optimization cycle."""
    service = SelfEvolutionService(db)
    cycle = await service.start_cycle(cycle_id)
    
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    
    await db.commit()
    return {"cycle_id": cycle.cycle_id, "status": "started"}


@router.post("/optimization/cycles/{cycle_id}/iteration")
async def record_optimization_iteration(
    cycle_id: str,
    parameters: Dict[str, Any],
    score: float,
    db: AsyncSession = Depends(get_async_db),
):
    """Record an optimization iteration result."""
    service = SelfEvolutionService(db)
    cycle = await service.record_iteration(cycle_id, parameters, score)
    
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    
    await db.commit()
    return {
        "cycle_id": cycle.cycle_id,
        "iteration": cycle.iteration,
        "current_score": cycle.current_score,
        "best_score": cycle.best_score,
        "state": cycle.cycle_state,
    }


@router.get("/optimization/cycles")
async def list_optimization_cycles(
    cycle_state: Optional[str] = None,
    context_key: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_async_db),
):
    """List optimization cycles."""
    service = SelfEvolutionService(db)
    
    cycles = await service.list_cycles(
        cycle_state=cycle_state,
        context_key=context_key,
        limit=limit,
    )
    
    return {
        "items": [
            {
                "cycle_id": c.cycle_id,
                "name": c.name,
                "context_key": c.context_key,
                "target_metric": c.target_metric,
                "cycle_state": c.cycle_state,
                "iteration": c.iteration,
                "max_iterations": c.max_iterations,
                "current_score": c.current_score,
                "best_score": c.best_score,
                "best_parameters": c.best_parameters,
            }
            for c in cycles
        ],
        "total": len(cycles),
    }


@router.get("/optimization/cycles/{cycle_id}")
async def get_optimization_cycle(
    cycle_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Get an optimization cycle by ID."""
    service = SelfEvolutionService(db)
    cycle = await service.get_cycle(cycle_id)
    
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    
    return {
        "cycle_id": cycle.cycle_id,
        "name": cycle.name,
        "context_key": cycle.context_key,
        "target_metric": cycle.target_metric,
        "parameter_space": cycle.parameter_space,
        "current_parameters": cycle.current_parameters,
        "best_parameters": cycle.best_parameters,
        "target_improvement": cycle.target_improvement,
        "cycle_state": cycle.cycle_state,
        "iteration": cycle.iteration,
        "max_iterations": cycle.max_iterations,
        "current_score": cycle.current_score,
        "best_score": cycle.best_score,
        "baseline_score": cycle.baseline_score,
        "exploration_history": cycle.exploration_history,
        "exploitation_history": cycle.exploitation_history,
        "improvements_found": cycle.improvements_found,
    }


@router.post("/metrics")
async def record_metric(
    metric_type: str,
    metric_name: str,
    value: float,
    subject_kind: Optional[str] = None,
    subject_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
    baseline_value: Optional[float] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Record a runtime evolution metric."""
    service = SelfEvolutionService(db)
    
    metric = await service.record_metric(
        metric_type=metric_type,
        metric_name=metric_name,
        value=value,
        subject_kind=subject_kind,
        subject_id=subject_id,
        context=context,
        tags=tags,
        baseline_value=baseline_value,
    )
    
    await db.commit()
    return {"id": str(metric.id), "status": "recorded"}


@router.get("/metrics")
async def list_metrics(
    metric_name: Optional[str] = None,
    subject_kind: Optional[str] = None,
    subject_id: Optional[str] = None,
    metric_type: Optional[str] = None,
    hours: int = 24,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
):
    """List runtime metrics."""
    from datetime import timedelta
    
    service = SelfEvolutionService(db)
    
    time_window = timedelta(hours=hours) if hours > 0 else None
    
    metrics = await service.get_metrics(
        metric_name=metric_name,
        subject_kind=subject_kind,
        subject_id=subject_id,
        metric_type=metric_type,
        time_window=time_window,
        limit=limit,
    )
    
    return {
        "items": [
            {
                "id": str(m.id),
                "metric_type": m.metric_type,
                "metric_name": m.metric_name,
                "value": m.value,
                "subject_kind": m.subject_kind,
                "subject_id": m.subject_id,
                "delta": m.delta,
                "change_direction": m.change_direction,
                "recorded_at": m.recorded_at.isoformat() if m.recorded_at else None,
            }
            for m in metrics
        ],
        "total": len(metrics),
    }


@router.get("/metrics/{metric_name}/trend")
async def get_metric_trend(
    metric_name: str,
    subject_id: Optional[str] = None,
    period_hours: int = 24,
    db: AsyncSession = Depends(get_async_db),
):
    """Get metric trend analysis."""
    service = SelfEvolutionService(db)
    trend = await service.get_metric_trends(metric_name, subject_id, period_hours)
    return trend


@router.get("/optimization/stats")
async def get_evolution_stats(
    db: AsyncSession = Depends(get_async_db),
):
    """Get self-evolution system statistics."""
    service = SelfEvolutionService(db)
    stats = await service.get_statistics()
    return stats


# ============================================================
# SEMANTIC ARCHIVE ENDPOINTS
# ============================================================

@router.post("/archives")
async def create_semantic_archive(
    name: str,
    archive_type: str,
    domain: Optional[str] = None,
    entities: Optional[Dict[str, Any]] = None,
    relationships: Optional[List[Dict[str, Any]]] = None,
    attributes: Optional[Dict[str, Any]] = None,
    semantic_tags: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new semantic archive."""
    service = SemanticArchiveService(db)
    
    archive = await service.create_archive(
        name=name,
        archive_type=archive_type,
        domain=domain,
        entities=entities,
        relationships=relationships,
        attributes=attributes,
        semantic_tags=semantic_tags,
    )
    
    await db.commit()
    return {"id": str(archive.id), "status": "created"}


@router.get("/archives/search")
async def search_archives(
    query: str,
    archive_type: Optional[str] = None,
    domain: Optional[str] = None,
    tags: Optional[str] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_db),
):
    """Search semantic archives."""
    service = SemanticArchiveService(db)
    tag_list = tags.split(",") if tags else None
    
    archives = await service.search_archives(
        query=query,
        archive_type=archive_type,
        domain=domain,
        tags=tag_list,
        limit=limit,
    )
    
    return {
        "items": [
            {
                "id": str(a.id),
                "name": a.name,
                "archive_type": a.archive_type,
                "domain": a.domain,
                "use_count": a.use_count,
                "completeness": a.completeness,
            }
            for a in archives
        ],
        "total": len(archives),
    }


# ============================================================
# CONVENIENCE ENDPOINTS
# ============================================================

@router.post("/insights/store")
async def store_execution_insight_endpoint(
    subject: str,
    subject_kind: str,
    title: str,
    insight: Dict[str, Any],
    importance: float = 0.5,
):
    """Convenience endpoint to store an execution insight."""
    memory = await store_execution_insight(
        subject=subject,
        subject_kind=subject_kind,
        title=title,
        insight=insight,
        importance=importance,
    )
    
    if not memory:
        raise HTTPException(status_code=500, detail="Failed to store insight")
    
    return {"id": str(memory.id), "status": "stored"}


@router.get("/cognitive/summary")
async def get_cognitive_summary(
    db: AsyncSession = Depends(get_async_db),
):
    """Get comprehensive cognitive kernel summary."""
    memory_service = OrchestrationMemoryService(db)
    planning_service = StrategicPlanningService(db)
    creative_service = CreativeReasoningService(db)
    governance_service = MultiAgentGovernanceService(db)
    evolution_service = SelfEvolutionService(db)
    
    memory_stats = await memory_service.get_statistics()
    planning_stats = await planning_service.get_statistics()
    creative_stats = await creative_service.get_statistics()
    governance_stats = await governance_service.get_statistics()
    evolution_stats = await evolution_service.get_statistics()
    
    return {
        "orchestration_memory": memory_stats,
        "strategic_planning": planning_stats,
        "creative_reasoning": creative_stats,
        "multi_agent_governance": governance_stats,
        "self_evolution": evolution_stats,
        "timestamp": datetime.utcnow().isoformat(),
    }