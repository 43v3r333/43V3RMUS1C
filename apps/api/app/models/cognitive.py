"""
Cognitive Kernel Models

Persistent orchestration memory, strategic execution planning,
creative reasoning, multi-agent governance, and self-evolution systems.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from enum import Enum

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime,
    ForeignKey, JSON, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class MemoryScope(str, Enum):
    """Memory scope types for orchestration recall"""
    EPISODIC = "episodic"      # Event-based execution memories
    SEMANTIC = "semantic"      # Knowledge and concept memories
    PROCEDURAL = "procedural"  # Workflow and process memories
    EVALUATIVE = "evaluative" # Judgment and evaluation memories
    STRATEGIC = "strategic"   # Planning and goal memories


class MemoryKind(str, Enum):
    """Memory classification by content type"""
    EXECUTION_INSIGHT = "execution_insight"
    WORKFLOW_AUDIT = "workflow_audit"
    AGENT_DECISION = "agent_decision"
    OPTIMIZATION_RESULT = "optimization_result"
    PATTERN_RECOGNITION = "pattern_recognition"
    STRATEGY_OUTCOME = "strategy_outcome"
    CONFLICT_RESOLUTION = "conflict_resolution"
    ADAPTATION_RECORD = "adaptation_record"


class PlanStatus(str, Enum):
    """Strategic plan lifecycle states"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"


class PlanHorizon(str, Enum):
    """Planning time horizons"""
    IMMEDIATE = "immediate"    # Seconds to minutes
    SHORT_TERM = "short_term"  # Minutes to hours
    MEDIUM_TERM = "medium_term"  # Hours to days
    LONG_TERM = "long_term"    # Days to weeks
    STRATEGIC = "strategic"    # Weeks to months


class StrategyKind(str, Enum):
    """Strategy classification"""
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    RESOURCE_ALLOCATION = "resource_allocation"
    QUALITY_IMPROVEMENT = "quality_improvement"
    RISK_MITIGATION = "risk_mitigation"
    CREATIVE_DIRECTION = "creative_direction"
    AGENT_COORDINATION = "agent_coordination"
    ADAPTIVE_TUNING = "adaptive_tuning"


class GovernanceRole(str, Enum):
    """Agent authority roles"""
    COORDINATOR = "coordinator"
    EXECUTOR = "executor"
    MONITOR = "monitor"
    PLANNER = "planner"
    ARCHITECT = "architect"
    ORCHESTRATOR = "orchestrator"
    ANALYST = "analyst"


class GovernanceAction(str, Enum):
    """Governance session action types"""
    PROPOSE = "propose"
    APPROVE = "approve"
    REJECT = "reject"
    DELEGATE = "delegate"
    COORDINATE = "coordinate"
    ARBITRATE = "arbitrate"
    SYNC = "sync"


class TuningState(str, Enum):
    """Self-evolution cycle states"""
    PENDING = "pending"
    RUNNING = "running"
    CONVERGED = "converged"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ForecastKind(str, Enum):
    """Execution forecast types"""
    DURATION = "duration"
    RESOURCE_USAGE = "resource_usage"
    SUCCESS_PROBABILITY = "success_probability"
    QUEUE_TIME = "queue_time"
    FAILURE_PROBABILITY = "failure_probability"
    QUALITY_METRIC = "quality_metric"
    THROUGHPUT = "throughput"


class ForecastHorizon(str, Enum):
    """Forecast time horizons"""
    NEAR_TERM = "near_term"    # < 1 hour
    SHORT = "short"            # 1-6 hours
    MEDIUM = "medium"          # 6-24 hours
    EXTENDED = "extended"      # > 24 hours


class ArchiveState(str, Enum):
    """Semantic archive states"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    PRUNED = "pruned"


# ============================================================
# ORCHESTRATION MEMORIES
# ============================================================

class OrchestrationMemory(BaseModel):
    """
    Persistent orchestration memory system.
    
    Stores episodic, semantic, procedural, evaluative, and strategic
    memories for execution recall and pattern analysis.
    """
    
    __tablename__ = "orchestration_memories"
    
    # Memory classification
    scope = Column(String(20), nullable=False, index=True)  # MemoryScope
    memory_kind = Column(String(40), nullable=False, index=True)  # MemoryKind
    
    # Subject identification
    subject = Column(String(255), nullable=True, index=True)  # Workflow, job, or agent ID
    subject_kind = Column(String(50), nullable=True, index=True)  # workflow, render_job, agent
    
    # Memory content
    title = Column(String(255), nullable=False)
    content = Column(JSON, nullable=False)  # Structured memory data
    
    # Memory significance
    importance = Column(Float, default=0.5)  # 0.0 to 1.0
    recency = Column(Float, default=1.0)    # Temporal decay factor
    confidence = Column(Float, default=0.8)  # Reliability of memory
    
    # Access tracking
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime, nullable=True)
    
    # Memory state
    is_pinned = Column(Boolean, default=False)
    tags = Column(JSON, nullable=True)
    
    # Relationships
    related_memory_ids = Column(JSON, nullable=True)  # UUIDs of related memories
    parent_memory_id = Column(UUID(as_uuid=True), ForeignKey("orchestration_memories.id"), nullable=True)
    
    # Context
    execution_context = Column(JSON, nullable=True)  # Runtime environment data
    outcome = Column(JSON, nullable=True)  # Result data
    
    # Indexes for efficient recall
    __table_args__ = (
        Index('ix_memory_subject_scope', 'subject', 'scope'),
        Index('ix_memory_kind_importance', 'memory_kind', 'importance'),
        Index('ix_memory_recency_importance', 'recency', 'importance'),
    )
    
    def __repr__(self) -> str:
        return f"<OrchestrationMemory(id={self.id}, scope={self.scope}, kind={self.memory_kind})>"


# ============================================================
# STRATEGIC EXECUTION PLANS
# ============================================================

class StrategicExecutionPlan(BaseModel):
    """
    Strategic execution planning system.
    
    Enables long-horizon workflow planning, objective coordination,
    and predictive dependency analysis.
    """
    
    __tablename__ = "strategic_execution_plans"
    
    # Plan identification
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    plan_type = Column(String(50), nullable=False, index=True)  # workflow, render, creative
    
    # Lifecycle state
    status = Column(String(20), nullable=False, default=PlanStatus.DRAFT.value, index=True)
    
    # Planning horizon
    horizon = Column(String(20), nullable=False, index=True)  # PlanHorizon
    planning_depth = Column(Integer, default=3)  # Number of planning iterations
    
    # Strategy classification
    strategy_kind = Column(String(40), nullable=False, index=True)  # StrategyKind
    
    # Objectives and outcomes
    objectives = Column(JSON, nullable=False)  # List of strategic objectives
    expected_outcomes = Column(JSON, nullable=True)
    actual_outcomes = Column(JSON, nullable=True)
    
    # Dependencies and constraints
    dependencies = Column(JSON, nullable=True)  # Plan dependencies
    constraints = Column(JSON, nullable=True)  # Planning constraints
    risks = Column(JSON, nullable=True)  # Identified risks
    
    # Resource allocation
    required_resources = Column(JSON, nullable=True)
    allocated_resources = Column(JSON, nullable=True)
    
    # Timeline
    estimated_start = Column(DateTime, nullable=True)
    estimated_end = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    
    # Confidence and priority
    confidence_score = Column(Float, default=0.5)
    priority = Column(Integer, default=5)  # 1-10
    estimated_impact = Column(Float, default=0.0)
    
    # Planning metadata
    parent_plan_id = Column(UUID(as_uuid=True), ForeignKey("strategic_execution_plans.id"), nullable=True)
    related_workflow_ids = Column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_plan_status_horizon', 'status', 'horizon'),
        Index('ix_plan_strategy_priority', 'strategy_kind', 'priority'),
        Index('ix_plan_confidence', 'confidence_score'),
    )
    
    def __repr__(self) -> str:
        return f"<StrategicExecutionPlan(id={self.id}, name={self.name}, status={self.status})>"


# ============================================================
# CREATIVE REASONING PROFILES
# ============================================================

class CreativeReasoningProfile(BaseModel):
    """
    Cinematic creative reasoning system.
    
    Stores narrative continuity intelligence, engagement prediction,
    aesthetic consistency analysis, and semantic pacing systems.
    """
    
    __tablename__ = "creative_reasoning_profiles"
    
    # Profile identification
    name = Column(String(255), nullable=False)
    profile_type = Column(String(50), nullable=False, index=True)  # campaign, series, content
    
    # Campaign association
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    
    # Narrative structure
    narrative_structure = Column(String(50), nullable=True)  # three_act, hero_journey, episodic
    emotional_arc = Column(String(50), nullable=True)  # rags_to_riches, tragedy, redemption
    
    # Pacing profile
    pacing_profile = Column(String(50), nullable=True)  # rollercoaster, build, steady, alternating
    pacing_intensity = Column(Float, default=0.5)  # 0-1 energy level
    
    # Visual identity
    visual_keywords = Column(JSON, nullable=True)
    color_palette = Column(JSON, nullable=True)
    visual_style = Column(String(100), nullable=True)
    
    # Audio identity
    audio_keywords = Column(JSON, nullable=True)
    music_mood = Column(String(100), nullable=True)
    sound_design = Column(String(100), nullable=True)
    
    # Audience targeting
    target_segments = Column(JSON, nullable=True)
    attention_span_seconds = Column(Integer, default=60)
    
    # Performance targets
    completion_rate_target = Column(Float, default=0.7)
    engagement_rate_target = Column(Float, default=0.15)
    retention_target = Column(Float, default=0.5)
    
    # Creative constraints
    max_duration = Column(Integer, nullable=True)  # seconds
    min_duration = Column(Integer, nullable=True)
    content_guidelines = Column(JSON, nullable=True)
    
    # Profile state
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    
    # Relationships
    scene_templates = Column(JSON, nullable=True)
    transition_rules = Column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_creative_campaign_active', 'campaign_id', 'is_active'),
        Index('ix_creative_profile_type', 'profile_type', 'version'),
    )
    
    def __repr__(self) -> str:
        return f"<CreativeReasoningProfile(id={self.id}, name={self.name})>"


# ============================================================
# AGENT GOVERNANCE SESSIONS
# ============================================================

class AgentGovernanceSession(BaseModel):
    """
    Multi-agent civilization governance system.
    
    Manages agent society runtime, authority hierarchies,
    execution diplomacy, and distributed negotiation.
    """
    
    __tablename__ = "agent_governance_sessions"
    
    # Session identification
    name = Column(String(255), nullable=False)
    session_type = Column(String(50), nullable=False, index=True)  # coordination, arbitration, planning
    
    # Lifecycle state
    status = Column(String(20), nullable=False, default="active", index=True)
    
    # Participants
    coordinator_id = Column(String(255), nullable=True)  # Lead agent ID
    participant_ids = Column(JSON, nullable=True)  # List of agent IDs
    
    # Authority structure
    authority_level = Column(String(20), nullable=False, default=GovernanceRole.ORCHESTRATOR.value)
    decision_authority = Column(JSON, nullable=True)  # Who can decide what
    
    # Session scope
    scope_kind = Column(String(50), nullable=True)  # workflow, render, creative
    scope_id = Column(String(255), nullable=True)  # Target resource ID
    
    # Actions and decisions
    actions_taken = Column(JSON, nullable=True)  # List of governance actions
    decisions_made = Column(JSON, nullable=True)
    
    # Negotiation state
    negotiation_rounds = Column(Integer, default=0)
    consensus_reached = Column(Boolean, default=False)
    disagreements = Column(JSON, nullable=True)
    
    # Outcomes
    resolution = Column(JSON, nullable=True)
    execution_plan = Column(JSON, nullable=True)
    
    # Timing
    session_start = Column(DateTime, nullable=True)
    session_end = Column(DateTime, nullable=True)
    expected_duration = Column(Integer, nullable=True)  # seconds
    
    # Performance metrics
    efficiency_score = Column(Float, default=0.0)
    consensus_time = Column(Integer, nullable=True)  # milliseconds
    
    # Relationships
    parent_session_id = Column(UUID(as_uuid=True), ForeignKey("agent_governance_sessions.id"), nullable=True)
    related_workflow_ids = Column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_governance_status_coordinator', 'status', 'coordinator_id'),
        Index('ix_governance_scope', 'scope_kind', 'scope_id'),
    )
    
    def __repr__(self) -> str:
        return f"<AgentGovernanceSession(id={self.id}, name={self.name}, status={self.status})>"


class AgentDecision(BaseModel):
    """
    Individual agent decisions within governance sessions.
    
    Tracks decision rationale, outcomes, and impact.
    """
    
    __tablename__ = "agent_decisions"
    
    # Decision identification
    decision_type = Column(String(50), nullable=False, index=True)  # resource, schedule, priority
    confidence = Column(Float, default=0.8)
    
    # Decision context
    session_id = Column(UUID(as_uuid=True), ForeignKey("agent_governance_sessions.id"), nullable=True)
    agent_id = Column(String(255), nullable=False, index=True)
    agent_role = Column(String(20), nullable=False, index=True)
    
    # Decision data
    context = Column(JSON, nullable=False)  # Decision context
    rationale = Column(Text, nullable=True)
    alternatives_considered = Column(JSON, nullable=True)
    
    # Decision outcome
    outcome = Column(JSON, nullable=True)
    impact_score = Column(Float, default=0.0)
    
    # Timing
    decision_time = Column(DateTime, default=datetime.utcnow)
    execution_time = Column(Integer, nullable=True)  # milliseconds
    
    # Review and validation
    is_validated = Column(Boolean, default=False)
    validation_notes = Column(Text, nullable=True)
    
    # Relationships
    related_decision_ids = Column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f"<AgentDecision(id={self.id}, type={self.decision_type}, agent={self.agent_id})>"


# ============================================================
# RUNTIME EVOLUTION METRICS
# ============================================================

class RuntimeEvolutionMetric(BaseModel):
    """
    Runtime evolution and adaptation tracking.
    
    Monitors system performance, adaptation patterns,
    and self-improvement trajectories.
    """
    
    __tablename__ = "runtime_evolution_metrics"
    
    # Metric identification
    metric_type = Column(String(50), nullable=False, index=True)  # performance, quality, efficiency
    metric_name = Column(String(100), nullable=False)
    
    # Subject tracking
    subject_kind = Column(String(50), nullable=True)  # workflow, agent, system
    subject_id = Column(String(255), nullable=True, index=True)
    
    # Metric value
    value = Column(Float, nullable=False)
    previous_value = Column(Float, nullable=True)
    baseline_value = Column(Float, nullable=True)
    
    # Change analysis
    delta = Column(Float, nullable=True)
    delta_percentage = Column(Float, nullable=True)
    change_direction = Column(String(10), nullable=True)  # improving, declining, stable
    
    # Context and metadata
    context = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Timestamp tracking
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    
    # Aggregation data
    aggregation_level = Column(String(20), default="point")  # point, minute, hour, day
    sample_count = Column(Integer, default=1)
    
    # Relationships
    linked_metric_ids = Column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_metric_subject_time', 'subject_kind', 'subject_id', 'recorded_at'),
        Index('ix_metric_type_recorded', 'metric_type', 'recorded_at'),
    )
    
    def __repr__(self) -> str:
        return f"<RuntimeEvolutionMetric(id={self.id}, name={self.metric_name}, value={self.value})>"


# ============================================================
# ADAPTIVE OPTIMIZATION CYCLES
# ============================================================

class AdaptiveOptimizationCycle(BaseModel):
    """
    Self-evolution and autonomous optimization system.
    
    Implements adaptive runtime evolution, optimization learning loops,
    predictive self-tuning, and workflow refinement.
    """
    
    __tablename__ = "adaptive_optimization_cycles"
    
    # Cycle identification
    cycle_id = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    
    # Lifecycle state
    cycle_state = Column(String(20), nullable=False, default=TuningState.PENDING.value, index=True)
    
    # Optimization context
    context_key = Column(String(100), nullable=False, index=True)  # render_pipeline, ai_generation
    context_data = Column(JSON, nullable=True)
    
    # Target metric
    target_metric = Column(String(100), nullable=False)  # throughput, quality, latency
    target_improvement = Column(Float, default=0.1)  # Expected % improvement
    
    # Optimization parameters
    parameter_space = Column(JSON, nullable=False)  # Search space definition
    current_parameters = Column(JSON, nullable=True)
    best_parameters = Column(JSON, nullable=True)
    
    # Iteration tracking
    max_iterations = Column(Integer, default=10)
    iteration = Column(Integer, default=0)
    patience = Column(Integer, default=3)  # Iterations without improvement before stop
    
    # Scoring
    current_score = Column(Float, nullable=True)
    best_score = Column(Float, nullable=True)
    baseline_score = Column(Float, nullable=True)
    convergence_threshold = Column(Float, default=0.01)
    
    # Learning data
    exploration_history = Column(JSON, nullable=True)
    exploitation_history = Column(JSON, nullable=True)
    
    # Results
    improvements_found = Column(JSON, nullable=True)
    failed_attempts = Column(JSON, nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_duration = Column(Integer, nullable=True)
    
    # Resource usage
    resources_consumed = Column(JSON, nullable=True)
    
    # Relationships
    linked_plan_id = Column(UUID(as_uuid=True), ForeignKey("strategic_execution_plans.id"), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_cycle_state_context', 'cycle_state', 'context_key'),
        Index('ix_cycle_iteration', 'iteration', 'max_iterations'),
    )
    
    def __repr__(self) -> str:
        return f"<AdaptiveOptimizationCycle(id={self.id}, cycle_id={self.cycle_id}, state={self.cycle_state})>"


# ============================================================
# ORCHESTRATION FORECASTS
# ============================================================

class OrchestrationForecast(BaseModel):
    """
    Predictive runtime intelligence system.
    
    Enables execution forecasting, resource prediction,
    and failure probability estimation.
    """
    
    __tablename__ = "orchestration_forecasts"
    
    # Forecast identification
    forecast_kind = Column(String(50), nullable=False, index=True)  # ForecastKind
    
    # Subject tracking
    subject_kind = Column(String(50), nullable=False)  # workflow, render_job, agent
    subject_key = Column(String(255), nullable=False)  # Specific resource key
    
    # Forecast horizon
    horizon = Column(String(20), nullable=False, index=True)  # ForecastHorizon
    predicted_for = Column(DateTime, nullable=False, index=True)
    
    # Prediction
    predicted_value = Column(Float, nullable=False)
    confidence = Column(Float, default=0.5)  # Forecast confidence
    
    # Prediction bounds
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)
    
    # Methodology
    prediction_method = Column(String(50), nullable=True)  # ml_model, heuristic, statistical
    model_version = Column(String(50), nullable=True)
    training_data_size = Column(Integer, nullable=True)
    
    # Context and features
    features_used = Column(JSON, nullable=True)
    context_data = Column(JSON, nullable=True)
    
    # Validation
    actual_value = Column(Float, nullable=True)
    prediction_error = Column(Float, nullable=True)
    validated_at = Column(DateTime, nullable=True)
    
    # Lifecycle state
    lifecycle_state = Column(String(20), default="pending", index=True)  # pending, validated, expired
    
    # Relationships
    related_plan_id = Column(UUID(as_uuid=True), ForeignKey("strategic_execution_plans.id"), nullable=True)
    related_memory_ids = Column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_forecast_subject_horizon', 'subject_kind', 'subject_key', 'horizon'),
        Index('ix_forecast_validated', 'lifecycle_state', 'validated_at'),
        Index('ix_forecast_confidence', 'confidence', 'horizon'),
    )
    
    def __repr__(self) -> str:
        return f"<OrchestrationForecast(id={self.id}, kind={self.forecast_kind}, subject={self.subject_key})>"


# ============================================================
# SEMANTIC CONTEXT ARCHIVES
# ============================================================

class SemanticContextArchive(BaseModel):
    """
    Semantic knowledge expansion and context archiving.
    
    Stores execution knowledge graphs, semantic workflow relationships,
    creative intelligence memory, and orchestration reasoning context.
    """
    
    __tablename__ = "semantic_context_archives"
    
    # Archive identification
    name = Column(String(255), nullable=False)
    archive_type = Column(String(50), nullable=False, index=True)  # knowledge_graph, workflow_context, creative
    
    # Content structure
    domain = Column(String(100), nullable=True, index=True)  # rendering, creative, orchestration
    schema_version = Column(String(20), nullable=True)
    
    # Knowledge content
    entities = Column(JSON, nullable=True)  # Entity definitions
    relationships = Column(JSON, nullable=True)  # Relationship definitions
    attributes = Column(JSON, nullable=True)  # Attribute data
    
    # Semantic analysis
    embeddings = Column(JSON, nullable=True)  # Vector embeddings
    semantic_tags = Column(JSON, nullable=True)
    
    # Provenance
    source_type = Column(String(50), nullable=True)  # workflow_execution, user_feedback, ai_generation
    source_id = Column(String(255), nullable=True)
    created_by = Column(String(255), nullable=True)  # agent or user ID
    
    # Lifecycle
    archive_state = Column(String(20), default=ArchiveState.ACTIVE.value, index=True)
    
    # Usage tracking
    use_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)
    
    # Quality metrics
    completeness = Column(Float, default=0.5)
    accuracy = Column(Float, default=0.8)
    relevance = Column(Float, default=0.7)
    
    # Relationships
    parent_archive_id = Column(UUID(as_uuid=True), ForeignKey("semantic_context_archives.id"), nullable=True)
    linked_workflow_ids = Column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_archive_type_domain', 'archive_type', 'domain'),
        Index('ix_archive_state_use', 'archive_state', 'use_count'),
    )
    
    def __repr__(self) -> str:
        return f"<SemanticContextArchive(id={self.id}, name={self.name}, type={self.archive_type})>"


# ============================================================
# RELATIONSHIP DEFINITIONS
# ============================================================

# Define relationships after all models are created

# OrchestrationMemory relationships
OrchestrationMemory.parent = relationship(
    "OrchestrationMemory",
    remote_side=[OrchestrationMemory.id],
    backref="children",
    foreign_keys=[OrchestrationMemory.parent_memory_id]
)

# StrategicExecutionPlan relationships
StrategicExecutionPlan.parent = relationship(
    "StrategicExecutionPlan",
    remote_side=[StrategicExecutionPlan.id],
    backref="sub_plans",
    foreign_keys=[StrategicExecutionPlan.parent_plan_id]
)

# AgentGovernanceSession relationships
AgentGovernanceSession.parent = relationship(
    "AgentGovernanceSession",
    remote_side=[AgentGovernanceSession.id],
    backref="child_sessions",
    foreign_keys=[AgentGovernanceSession.parent_session_id]
)

# SemanticContextArchive relationships
SemanticContextArchive.parent = relationship(
    "SemanticContextArchive",
    remote_side=[SemanticContextArchive.id],
    backref="derived_archives",
    foreign_keys=[SemanticContextArchive.parent_archive_id]
)