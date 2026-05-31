"""
Learning Domain Models - Runtime learning and optimization
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class LearningType(str, Enum):
    """Learning types"""
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    REINFORCEMENT = "reinforcement"
    ADAPTIVE = "adaptive"


class ModelStatus(str, Enum):
    """Model status"""
    TRAINING = "training"
    VALIDATING = "validating"
    ACTIVE = "active"
    DEGRADED = "degraded"
    ARCHIVED = "archived"


class OptimizationMetric(str, Enum):
    """Optimization metric types"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    COST = "cost"
    QUALITY = "quality"
    RELIABILITY = "reliability"


class ExecutionLearning(BaseModel):
    """Execution learning model - runtime learning data"""
    __tablename__ = "execution_learning"
    
    learning_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Learning type
    learning_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Target
    target_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Learning data
    features: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    labels: Mapped[Optional[List[Any]]] = mapped_column(JSON, nullable=True)
    
    # Performance
    performance: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Feedback
    feedback: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    reward: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Context
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    evaluated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class PredictiveModel(BaseModel):
    """Predictive model model - ML models for predictions"""
    __tablename__ = "predictive_models"
    
    model_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Model info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Configuration
    config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    features_used: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=ModelStatus.TRAINING.value, index=True)
    
    # Performance
    accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precision: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recall: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    f1_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Training
    training_samples: Mapped[int] = mapped_column(Integer, default=0)
    validation_samples: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metrics
    avg_error: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_eval_error: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Versions
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_model_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    trained_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deprecated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class OptimizationHistory(BaseModel):
    """Optimization history model - tracked optimizations"""
    __tablename__ = "optimization_history"
    
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


class AnomalyDetection(BaseModel):
    """Anomaly detection model - detected anomalies"""
    __tablename__ = "anomaly_detections"
    
    anomaly_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Anomaly info
    anomaly_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Detection
    detection_method: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="warning")
    
    # Metrics
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    expected_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    deviation: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Context
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Resolution
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timing
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class LearningCurve(BaseModel):
    """Learning curve model - training progress"""
    __tablename__ = "learning_curves"
    
    curve_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Model
    model_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Curve data
    iteration: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Metrics
    loss: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    validation_loss: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    validation_accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Learning rate
    learning_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timing
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class AdaptiveThreshold(BaseModel):
    """Adaptive threshold model - dynamic thresholds"""
    __tablename__ = "adaptive_thresholds"
    
    threshold_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Metric
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Threshold values
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    lower_bound: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    upper_bound: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Adaptation
    adaptation_method: Mapped[str] = mapped_column(String(50), default="moving_average")
    adaptation_window: Mapped[int] = mapped_column(Integer, default=100)
    
    # Performance
    trigger_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    false_positive_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Updated
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class ReinforcementReward(BaseModel):
    """Reinforcement reward model - reward tracking"""
    __tablename__ = "reinforcement_rewards"
    
    reward_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Episode
    episode_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Action
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Reward
    reward_value: Mapped[float] = mapped_column(Float, nullable=False)
    reward_source: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # State
    state_before: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    state_after: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    step: Mapped[int] = mapped_column(Integer, default=0)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)