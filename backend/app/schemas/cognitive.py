"""
Cognitive Schemas - Pydantic schemas for the cognitive orchestration subsystem.

Covers schemas for:
  - Knowledge graph nodes, edges, neighborhoods
  - Orchestration memory items
  - Execution forecasts and runtime metrics
  - Creative profiles and narrative sequences
  - Governance rules, authority hierarchies, conflict resolutions
  - Feedback signals and tuning records
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Base / shared
# ---------------------------------------------------------------------------

class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime


class UUIDSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


# ---------------------------------------------------------------------------
# Knowledge graph
# ---------------------------------------------------------------------------

class KnowledgeNodeBase(BaseModel):
    node_kind: str
    node_key: str
    label: str
    summary: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    relevance_score: float = 0.0
    source_domain: Optional[str] = None


class KnowledgeNodeCreate(KnowledgeNodeBase):
    vector: Optional[List[float]] = None
    correlation_id: Optional[str] = None
    owner_id: Optional[UUID] = None


class KnowledgeNodeResponse(UUIDSchema, KnowledgeNodeBase):
    lifecycle_state: str
    centrality: float
    last_seen_at: datetime
    seen_count: int
    correlation_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DependencyEdgeCreate(BaseModel):
    source_kind: str
    source_key: str
    target_kind: str
    target_key: str
    edge_kind: str
    weight: float = 1.0
    confidence: float = 1.0
    label: Optional[str] = None
    correlation_id: Optional[str] = None


class DependencyEdgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_node_id: UUID
    target_node_id: UUID
    edge_kind: str
    label: Optional[str]
    weight: float
    confidence: float
    evidence_count: int
    lifecycle_state: str

    model_config = ConfigDict(from_attributes=True)


class GraphNeighborhoodResponse(BaseModel):
    root: KnowledgeNodeResponse
    nodes: List[KnowledgeNodeResponse]
    edges: List[DependencyEdgeResponse]
    depth: int


class SemanticRelationshipCreate(BaseModel):
    subject_kind: str
    subject_key: str
    predicate: str
    object_kind: str
    object_key: str
    confidence: float = 1.0
    weight: float = 1.0
    evidence: Optional[Dict[str, Any]] = None
    derived_from: Optional[str] = None


class SemanticRelationshipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subject_kind: str
    subject_key: str
    predicate: str
    object_kind: str
    object_key: str
    confidence: float
    weight: float
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrchestrationMemoryCreate(BaseModel):
    scope: str
    memory_kind: str
    subject: str
    title: str
    content: Dict[str, Any]
    importance: float = 0.5
    confidence: float = 1.0
    correlation_id: Optional[str] = None
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None


class OrchestrationMemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    scope: str
    memory_kind: str
    subject: str
    title: str
    content: Dict[str, Any]
    importance: float
    recency: float
    confidence: float
    access_count: int
    last_accessed_at: Optional[datetime]
    correlation_id: Optional[str]
    workflow_id: Optional[str]
    agent_id: Optional[str]
    is_pinned: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GraphSnapshotRequest(BaseModel):
    kind: str
    key: str
    depth: int = 2
    purpose: str = "decision"
    correlation_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Forecasting
# ---------------------------------------------------------------------------

class ForecastRequest(BaseModel):
    subject_kind: str
    subject_key: str
    forecast_kind: str  # duration, queue_time, failure_probability, etc.
    features: Optional[Dict[str, Any]] = None
    horizon: Optional[str] = None  # immediate, near_term, short, long, extended


class ExecutionForecastResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subject_kind: str
    subject_key: str
    forecast_kind: str
    horizon: str
    predicted_value: float
    lower_bound: Optional[float]
    upper_bound: Optional[float]
    confidence: float
    predicted_for: datetime
    generated_at: datetime
    actual_value: Optional[float]
    realized_at: Optional[datetime]
    error_pct: Optional[float]
    lifecycle_state: str

    model_config = ConfigDict(from_attributes=True)


class ForecastRealizeRequest(BaseModel):
    subject_kind: str
    subject_key: str
    forecast_kind: str
    actual_value: float


class MultiStageGraphCreate(BaseModel):
    subject_kind: str
    subject_key: str
    plan_label: str
    steps: List[Dict[str, Any]]
    selected_strategy: Optional[str] = None
    correlation_id: Optional[str] = None


class MultiStageGraphResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subject_kind: str
    subject_key: str
    plan_label: str
    stages: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    stage_count: int
    parallelism_factor: float
    estimated_duration: float
    estimated_cost: float
    risk_score: float
    selected_strategy: Optional[str]
    lifecycle_state: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StrategySelectRequest(BaseModel):
    subject_kind: str
    subject_key: str
    context: Dict[str, Any]
    correlation_id: Optional[str] = None


class StrategyDecisionResponse(BaseModel):
    strategy: str
    rationale: str
    expected_improvement: float
    confidence: float
    scores: Dict[str, float]


# ---------------------------------------------------------------------------
# Creative intelligence
# ---------------------------------------------------------------------------

class CreativeProfileCreate(BaseModel):
    name: str
    campaign_id: Optional[str] = None
    artist_id: Optional[str] = None
    narrative_structure: str = "linear"
    emotional_arc: str = "steady"
    pacing_profile: str = "bruiser"
    visual_keywords: List[str] = Field(default_factory=list)
    audio_keywords: List[str] = Field(default_factory=list)
    target_segments: List[str] = Field(default_factory=list)


class CreativeProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    campaign_id: Optional[str]
    artist_id: Optional[str]
    narrative_structure: str
    emotional_arc: str
    pacing_profile: str
    visual_keywords: List[str]
    audio_keywords: List[str]
    color_palette: List[str]
    target_segments: List[str]
    attention_span_seconds: float
    completion_rate_target: float
    engagement_rate_target: float
    is_active: bool
    version: int
    created_at: datetime


class NarrativeSequenceCreate(BaseModel):
    name: str
    profile_id: Optional[UUID] = None
    campaign_id: Optional[str] = None
    structure: str = "linear"
    emotional_arc: str = "steady"
    beats: List[Dict[str, Any]]
    target_duration: float
    target_bpm: Optional[float] = None
    target_key: Optional[str] = None


class NarrativeSequenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    profile_id: Optional[UUID]
    campaign_id: Optional[str]
    structure: str
    emotional_arc: str
    beats: List[Dict[str, Any]]
    beat_count: int
    target_duration: float
    target_bpm: Optional[float]
    target_key: Optional[str]
    creative_score: float
    confidence: float
    is_locked: bool
    version: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmotionMappingCreate(BaseModel):
    source_type: str
    source_value: str
    target_type: str
    target_value: str
    strength: float = 0.5
    profile_id: Optional[UUID] = None


class EmotionMappingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_type: str
    source_value: str
    target_type: str
    target_value: str
    strength: float
    confidence: float
    trigger_threshold: Optional[float]
    fade_duration: float
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Governance
# ---------------------------------------------------------------------------

class GovernanceRuleCreate(BaseModel):
    name: str
    rule_type: str
    conditions: Dict[str, Any]
    action: str  # allow / deny / escalate
    agent_kind: Optional[str] = None
    priority: int = 0


class GovernanceRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    rule_type: str
    conditions: Dict[str, Any]
    action: str
    agent_kind: Optional[str]
    priority: int
    is_active: bool
    trigger_count: int
    success_count: int
    failure_count: int
    version: int
    created_at: datetime


class GovernanceActionEvaluateRequest(BaseModel):
    agent_id: str
    agent_kind: str
    action_type: str
    action_params: Dict[str, Any] = Field(default_factory=dict)


class GovernanceDecisionResponse(BaseModel):
    action: str
    reason: str
    triggered_rules: List[str] = Field(default_factory=list)
    escalation_agent: Optional[str] = None
    confidence: float


class ArbitrationPolicyCreate(BaseModel):
    name: str
    domain: str
    strategy: str  # priority / round_robin / weighted_vote / mediated / retry / merge
    fallback_strategy: Optional[str] = None
    escalation_threshold: int = 3
    priority: int = 0


class ConflictResolutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conflict_id: str
    domain: str
    agent_ids: List[str]
    authority_levels: List[int]
    conflict_type: str
    strategy_used: str
    resolution_outcome: str
    winning_agent_id: Optional[str]
    resolution_state: str
    escalation_required: bool
    human_review: bool
    detected_at: datetime
    resolved_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Feedback / tuning
# ---------------------------------------------------------------------------

class FeedbackIngestRequest(BaseModel):
    subject_kind: str
    subject_key: str
    feedback_type: str  # duration, quality, cost, throughput, error_rate, satisfaction
    actual_value: float
    expected_value: Optional[float] = None
    quality_score: Optional[float] = None
    error_rate: Optional[float] = None
    context: Optional[Dict[str, Any]] = None
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    execution_start: datetime


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subject_kind: str
    subject_key: str
    feedback_type: str
    actual_value: Optional[float]
    expected_value: Optional[float]
    delta_pct: Optional[float]
    quality_score: Optional[float]
    error_rate: Optional[float]
    workflow_id: Optional[str]
    agent_id: Optional[str]
    observed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TuningCycleCreate(BaseModel):
    context_key: str
    target_metric: str
    target_improvement: float = 0.1
    max_iterations: int = 10
    description: Optional[str] = None


class TuningCycleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    cycle_id: str
    context_key: str
    target_metric: str
    target_improvement: float
    max_iterations: int
    iteration: int
    cycle_state: str
    best_score: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class TuningParameterRequest(BaseModel):
    parameter_name: str
    context_key: str
    current_value: float
    outcome_score: Optional[float] = None
    action: str = "parameter_tune"
    reason: str = ""
    triggered_by: Optional[str] = None
    cycle_id: Optional[str] = None
    correlation_id: Optional[str] = None


class TuningRecommendationResponse(BaseModel):
    parameter_name: str
    current_value: float
    recommended_value: float
    action: str
    reason: str
    expected_improvement: float
    confidence: float