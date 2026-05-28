"""
Semantic Recovery Domain Models.

Provides:
- Semantic reconciliation engine
- Runtime conflict resolution
- Orchestration correction systems
- Adaptive semantic stabilization
- Execution consistency validation
- Predictive semantic recovery
- Semantic self-healing
- Orchestration reconciliation
- Adaptive correction
- Execution consistency enforcement
- Predictive stabilization
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class RecoveryState(str, Enum):
    """Recovery state"""
    IDLE = "idle"
    DETECTING = "detecting"
    DIAGNOSING = "diagnosing"
    RECONCILING = "reconciling"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


class ConflictSeverity(str, Enum):
    """Conflict severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ConflictType(str, Enum):
    """Types of semantic conflicts"""
    SEMANTIC_DRIFT = "semantic_drift"
    INTERPRETATION_MISMATCH = "interpretation_mismatch"
    CONSISTENCY_BREACH = "consistency_breach"
    CONTRACT_VIOLATION = "contract_violation"
    DEPENDENCY_CYCLE = "dependency_cycle"
    DATA_RACE = "data_race"


class StabilizationMode(str, Enum):
    """Stabilization mode"""
    ACTIVE = "active"
    PASSIVE = "passive"
    PREDICTIVE = "predictive"


class ReconciliationStrategy(str, Enum):
    """Reconciliation strategies"""
    MAJORITY_WIN = "majority_win"
    PRIORITY_WIN = "priority_win"
    LATEST_WIN = "latest_win"
    MERGE = "merge"
    ROLLBACK = "rollback"


class SemanticConflict(BaseModel):
    """Semantic conflict - detected conflict between semantic states"""
    __tablename__ = "semantic_conflicts"
    
    # Conflict identification
    conflict_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type and severity
    conflict_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), default=ConflictSeverity.WARNING.value, index=True)
    
    # Involved entities
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Conflict details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    conflicting_values: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    divergence_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Context
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    affected_nodes: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Resolution
    resolution_strategy: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    resolved_value: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    
    # State
    state: Mapped[str] = mapped_column(String(20), default=RecoveryState.IDLE.value, index=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Timing
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class ReconciliationSession(BaseModel):
    """Reconciliation session - tracks semantic reconciliation operations"""
    __tablename__ = "reconciliation_sessions"
    
    # Session identification
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type and strategy
    conflict_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    strategy: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Target
    target_entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Involved entities
    involved_entities: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    conflicting_states: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    
    # Resolution
    resolved_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    resolution_confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    # State progression
    state: Mapped[str] = mapped_column(String(20), default=RecoveryState.IDLE.value, index=True)
    state_history: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Audit
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    initiated_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class RecoveryAction(BaseModel):
    """Recovery action - tracked recovery operations"""
    __tablename__ = "semantic_recovery_actions"
    
    # Action identification
    action_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Related conflict
    conflict_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Action details
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action_description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Target
    target_entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Configuration
    action_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # State
    state: Mapped[str] = mapped_column(String(20), default=RecoveryState.IDLE.value, index=True)
    
    # Execution
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Result
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class StabilizationLoop(BaseModel):
    """Stabilization loop - adaptive stabilization cycles"""
    __tablename__ = "semantic_stabilization_loops"
    
    # Loop identification
    loop_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type and target
    loop_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Configuration
    mode: Mapped[str] = mapped_column(String(20), default=StabilizationMode.ACTIVE.value)
    interval_seconds: Mapped[int] = mapped_column(Integer, default=60)
    
    # Metrics
    target_metric: Mapped[str] = mapped_column(String(50), nullable=False)
    target_threshold: Mapped[float] = mapped_column(Float, default=0.9)
    current_value: Mapped[float] = mapped_column(Float, default=0.0)
    
    # State
    state: Mapped[str] = mapped_column(String(20), default="running", index=True)
    
    # Iteration tracking
    iteration_count: Mapped[int] = mapped_column(Integer, default=0)
    max_iterations: Mapped[int] = mapped_column(Integer, default=10)
    iteration_history: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_iteration: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class PredictiveRecovery(BaseModel):
    """Predictive recovery - predicted failures and recovery needs"""
    __tablename__ = "predictive_semantic_recovery"
    
    # Prediction identification
    prediction_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Target
    target_entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Prediction
    predicted_issue: Mapped[str] = mapped_column(String(255), nullable=False)
    probability: Mapped[float] = mapped_column(Float, default=0.0)
    severity: Mapped[str] = mapped_column(String(20), default=ConflictSeverity.WARNING.value)
    
    # Timeline
    predicted_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    time_horizon_minutes: Mapped[int] = mapped_column(Integer, default=60)
    
    # Evidence
    evidence: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Action
    recommended_actions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    is_acted_upon: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Validation
    actual_occurred: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ConsistencyCheckpoint(BaseModel):
    """Consistency checkpoint - point-in-time validation state"""
    __tablename__ = "semantic_consistency_checkpoints"
    
    # Checkpoint identification
    checkpoint_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Target
    target_entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # State snapshot
    semantic_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    interpretation_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    consistency_score: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Validation
    validation_rules_passed: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    validation_rules_failed: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    checkpoint_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class RecoveryPolicy(BaseModel):
    """Recovery policy - rules for recovery behavior"""
    __tablename__ = "semantic_recovery_policies"
    
    # Policy identification
    policy_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    policy_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    
    # Scope
    conflict_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Trigger conditions
    trigger_conditions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Actions
    actions: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    action_order: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Configuration
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=5)
    auto_recover: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metrics
    trigger_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


class SemanticViolation(BaseModel):
    """Semantic violation - detected contract/policy violations"""
    __tablename__ = "semantic_violations"
    
    # Violation identification
    violation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Type
    violation_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), default=ConflictSeverity.WARNING.value)
    
    # Target
    target_entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Violation details
    rule_violated: Mapped[str] = mapped_column(String(255), nullable=False)
    expected_value: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    actual_value: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    deviation: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Context
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Resolution
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    resolution_action: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Timing
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    auto_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
