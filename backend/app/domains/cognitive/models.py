"""
Cognitive Domain Models - Adaptive orchestration and reasoning
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum
from dataclasses import dataclass, field

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class PolicyType(str, Enum):
    """Policy types for orchestration"""
    SCHEDULING = "scheduling"
    EXECUTION = "execution"
    OPTIMIZATION = "optimization"
    FAILOVER = "failover"
    SCALING = "scaling"


class PolicyAction(str, Enum):
    """Policy actions"""
    ALLOW = "allow"
    DENY = "deny"
    MODIFY = "modify"
    QUEUE = "queue"
    PRIORITIZE = "prioritize"
    REJECT = "reject"


class ExecutionState(str, Enum):
    """Execution state"""
    PENDING = "pending"
    OPTIMIZING = "optimizing"
    SCHEDULED = "scheduled"
    EXECUTING = "executing"
    MONITORING = "monitoring"
    COMPLETED = "completed"
    FAILED = "failed"
    RECOVERING = "recovering"


class OptimizationType(str, Enum):
    """Optimization types"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    RESOURCE = "resource"
    COST = "cost"
    QUALITY = "quality"
    RELIABILITY = "reliability"


class PredictionType(str, Enum):
    """Prediction types"""
    DURATION = "duration"
    RESOURCE_NEED = "resource_need"
    FAILURE = "failure"
    QUEUE_TIME = "queue_time"
    OPTIMAL_SCHEDULE = "optimal_schedule"


class OrchestrationPolicy(BaseModel):
    """Orchestration policy model - runtime behavior rules"""
    __tablename__ = "orchestration_policies"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Policy type
    policy_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Conditions
    conditions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    
    # Action
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    action_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Priority
    priority: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Usage
    trigger_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Version
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    # Owner
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class AdaptiveExecutionState(BaseModel):
    """Adaptive execution state model - runtime adaptation tracking"""
    __tablename__ = "adaptive_execution_states"
    
    execution_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    plan_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    
    # State
    state: Mapped[str] = mapped_column(String(20), default=ExecutionState.PENDING.value, index=True)
    
    # Context
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Adaptation
    adaptation_count: Mapped[int] = mapped_column(Integer, default=0)
    last_adaptation: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    adaptation_history: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Metrics
    current_performance: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    target_performance: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    
    # Decisions
    decisions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ExecutionInsight(BaseModel):
    """Execution insight model - optimization insights"""
    __tablename__ = "execution_insights"
    
    insight_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    insight_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Source
    source_execution: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Data
    data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Confidence
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Impact
    impact_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    potential_improvement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status
    is_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timing
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Correlation
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)


class RuntimePrediction(BaseModel):
    """Runtime prediction model - execution forecasting"""
    __tablename__ = "runtime_predictions"
    
    prediction_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Prediction type
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Target
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Prediction
    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Confidence
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Range
    min_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Features
    features: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Validation
    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    prediction_error: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timing
    predicted_for: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class OptimizationHistory(BaseModel):
    """Optimization history model - tracked optimizations"""
    __tablename__ = "optimization_histories"
    
    optimization_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    optimization_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Before
    before_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    before_metrics: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    
    # After
    after_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    after_metrics: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    
    # Improvement
    improvement_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Trigger
    trigger_reason: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Policy
    policy_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class OrchestrationHeuristic(BaseModel):
    """Orchestration heuristic model - adaptive scheduling rules"""
    __tablename__ = "orchestration_heuristics"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Heuristic type
    heuristic_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Rule
    rule: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    conditions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Weight
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Performance
    hit_count: Mapped[int] = mapped_column(Integer, default=0)
    miss_count: Mapped[int] = mapped_column(Integer, default=0)
    success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Last used
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ExecutionPattern(BaseModel):
    """Execution pattern model - learned execution patterns"""
    __tablename__ = "execution_patterns"
    
    pattern_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Pattern type
    pattern_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Description
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Pattern data
    pattern_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, default=1)
    
    # Success metrics
    avg_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Conditions
    conditions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    first_seen: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)