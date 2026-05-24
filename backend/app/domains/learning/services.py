"""
Learning Services - Runtime learning and optimization
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func

from .models import (
    LearningType,
    ModelStatus,
    OptimizationMetric,
    ExecutionLearning,
    PredictiveModel,
    AnomalyDetection,
    LearningCurve,
    AdaptiveThreshold,
    ReinforcementReward,
)

logger = logging.getLogger(__name__)


@dataclass
class AnomalyResult:
    """Anomaly detection result"""
    is_anomaly: bool
    score: float
    severity: str
    description: str


@dataclass
class PredictionResult:
    """Prediction result"""
    predicted_value: float
    confidence: float
    model_id: str
    features_used: List[str]


class RuntimeLearningEngine:
    """
    Runtime learning engine.
    Handles execution learning, pattern recognition, and adaptive optimization.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._models: Dict[str, PredictiveModel] = {}
        self._learning_buffer: deque = deque(maxlen=1000)
        self._thresholds: Dict[str, AdaptiveThreshold] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize the learning engine"""
        await self._load_models()
        await self._load_thresholds()
        self._running = True
        logger.info("RuntimeLearningEngine initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the learning engine"""
        self._running = False
        logger.info("RuntimeLearningEngine shutdown")
    
    async def _load_models(self) -> None:
        """Load predictive models from database"""
        result = await self.db.execute(
            select(PredictiveModel).where(PredictiveModel.status == ModelStatus.ACTIVE.value)
        )
        for model in result.scalars().all():
            self._models[model.model_id] = model
    
    async def _load_thresholds(self) -> None:
        """Load adaptive thresholds from database"""
        result = await self.db.execute(select(AdaptiveThreshold).where(AdaptiveThreshold.is_active == True))
        for threshold in result.scalars().all():
            self._thresholds[threshold.metric_name] = threshold
    
    # ==================== Execution Learning ====================
    
    async def record_execution(
        self,
        learning_type: LearningType,
        target_type: str,
        target_id: str,
        features: Dict[str, Any],
        performance: Optional[Dict[str, float]] = None,
        feedback: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionLearning:
        """Record execution for learning"""
        learning = ExecutionLearning(
            learning_id=str(uuid4()),
            learning_type=learning_type.value,
            target_type=target_type,
            target_id=target_id,
            features=features,
            performance=performance,
            feedback=feedback,
            context=context,
        )
        
        self.db.add(learning)
        await self.db.commit()
        await self.db.refresh(learning)
        
        # Add to buffer for batch processing
        self._learning_buffer.append(learning)
        
        return learning
    
    async def get_learning_data(
        self,
        target_id: str,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[ExecutionLearning]:
        """Get learning data for target"""
        query = select(ExecutionLearning).where(
            ExecutionLearning.target_id == target_id
        )
        
        if since:
            query = query.where(ExecutionLearning.created_at >= since)
        
        query = query.order_by(ExecutionLearning.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def analyze_patterns(
        self,
        target_type: str,
        time_window: timedelta = timedelta(hours=24),
    ) -> Dict[str, Any]:
        """Analyze execution patterns"""
        since = datetime.utcnow() - time_window
        
        result = await self.db.execute(
            select(ExecutionLearning).where(
                ExecutionLearning.target_type == target_type,
                ExecutionLearning.created_at >= since,
            )
        )
        
        learnings = list(result.scalars().all())
        
        if not learnings:
            return {"patterns": [], "count": 0}
        
        # Analyze performance distribution
        performances = [l.performance for l in learnings if l.performance]
        
        avg_performance = {}
        if performances:
            keys = performances[0].keys()
            for key in keys:
                values = [p.get(key, 0) for p in performances]
                avg_performance[key] = sum(values) / len(values)
        
        # Identify high/low performers
        high_performers = [
            l for l in learnings
            if l.performance and any(v > 0.8 for v in l.performance.values())
        ]
        low_performers = [
            l for l in learnings
            if l.performance and any(v < 0.4 for v in l.performance.values())
        ]
        
        return {
            "total_executions": len(learnings),
            "avg_performance": avg_performance,
            "high_performer_count": len(high_performers),
            "low_performer_count": len(low_performers),
            "patterns": [
                self._extract_features(high_performers),
                self._extract_features(low_performers),
            ],
        }
    
    def _extract_features(self, learnings: List[ExecutionLearning]) -> Dict[str, Any]:
        """Extract common features from learnings"""
        if not learnings:
            return {}
        
        # Use most common feature values
        feature_keys = list(learnings[0].features.keys())
        common_features = {}
        
        for key in feature_keys:
            values = [l.features.get(key) for l in learnings]
            # Get most common value
            from collections import Counter
            counter = Counter(v for v in values if v is not None)
            if counter:
                common_features[key] = counter.most_common(1)[0][0]
        
        return common_features
    
    # ==================== Anomaly Detection ====================
    
    async def detect_anomaly(
        self,
        metric_name: str,
        value: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> AnomalyResult:
        """Detect anomaly in metric"""
        # Check adaptive threshold
        threshold = self._thresholds.get(metric_name)
        
        if threshold:
            is_anomaly = (
                value < threshold.lower_bound or
                value > threshold.upper_bound
            ) if threshold.lower_bound and threshold.upper_bound else value > threshold.threshold_value
            
            if is_anomaly:
                # Calculate anomaly score
                if threshold.threshold_value > 0:
                    score = abs(value - threshold.threshold_value) / threshold.threshold_value
                else:
                    score = 0.0
                
                severity = self._calculate_severity(score)
                
                # Record anomaly
                await self._record_anomaly(
                    metric_name, value, threshold.threshold_value,
                    severity, context
                )
                
                return AnomalyResult(
                    is_anomaly=True,
                    score=score,
                    severity=severity,
                    description=f"Value {value:.2f} exceeds threshold {threshold.threshold_value:.2f}",
                )
        
        return AnomalyResult(
            is_anomaly=False,
            score=0.0,
            severity="none",
            description="Value within normal range",
        )
    
    def _calculate_severity(self, score: float) -> str:
        """Calculate anomaly severity"""
        if score > 2.0:
            return "critical"
        elif score > 1.0:
            return "warning"
        elif score > 0.5:
            return "info"
        else:
            return "none"
    
    async def _record_anomaly(
        self,
        metric_name: str,
        actual_value: float,
        expected_value: float,
        severity: str,
        context: Optional[Dict[str, Any]],
    ) -> AnomalyDetection:
        """Record detected anomaly"""
        deviation = abs(actual_value - expected_value) / expected_value if expected_value > 0 else 0
        
        anomaly = AnomalyDetection(
            anomaly_id=str(uuid4()),
            anomaly_type="threshold_breach",
            detection_method="adaptive_threshold",
            confidence=0.8,
            description=f"Metric {metric_name} breached threshold",
            severity=severity,
            metric_name=metric_name,
            expected_value=expected_value,
            actual_value=actual_value,
            deviation=deviation,
            context=context,
        )
        
        self.db.add(anomaly)
        await self.db.commit()
        await self.db.refresh(anomaly)
        
        return anomaly
    
    # ==================== Threshold Management ====================
    
    async def update_threshold(
        self,
        metric_name: str,
        new_value: float,
        lower_bound: Optional[float] = None,
        upper_bound: Optional[float] = None,
    ) -> AdaptiveThreshold:
        """Update adaptive threshold"""
        threshold = self._thresholds.get(metric_name)
        
        if not threshold:
            threshold = AdaptiveThreshold(
                threshold_id=str(uuid4()),
                metric_name=metric_name,
                metric_type="performance",
                threshold_value=new_value,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
            )
            self.db.add(threshold)
        else:
            threshold.threshold_value = new_value
            threshold.lower_bound = lower_bound
            threshold.upper_bound = upper_bound
            threshold.updated_at = datetime.utcnow()
        
        self.db.add(threshold)
        await self.db.commit()
        await self.db.refresh(threshold)
        
        self._thresholds[metric_name] = threshold
        
        return threshold
    
    # ==================== Predictive Models ====================
    
    async def create_model(
        self,
        model_id: str,
        name: str,
        model_type: str,
        config: Optional[Dict[str, Any]] = None,
        features_used: Optional[List[str]] = None,
    ) -> PredictiveModel:
        """Create a predictive model"""
        model = PredictiveModel(
            model_id=model_id,
            name=name,
            model_type=model_type,
            config=config,
            features_used=features_used,
            status=ModelStatus.TRAINING.value,
            created_at=datetime.utcnow(),
        )
        
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        
        self._models[model_id] = model
        
        return model
    
    async def update_model_stats(
        self,
        model_id: str,
        accuracy: float,
        loss: float,
        training_samples: int,
    ) -> PredictiveModel:
        """Update model training statistics"""
        model = self._models.get(model_id)
        
        if not model:
            result = await self.db.execute(
                select(PredictiveModel).where(PredictiveModel.model_id == model_id)
            )
            model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"Model not found: {model_id}")
        
        model.accuracy = accuracy
        model.training_samples = training_samples
        
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        
        return model
    
    async def activate_model(self, model_id: str) -> PredictiveModel:
        """Activate a trained model"""
        model = self._models.get(model_id)
        
        if not model:
            raise ValueError(f"Model not found: {model_id}")
        
        model.status = ModelStatus.ACTIVE.value
        model.last_used = datetime.utcnow()
        
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        
        return model
    
    # ==================== Reinforcement Learning ====================
    
    async def record_reward(
        self,
        episode_id: str,
        action_type: str,
        reward_value: float,
        reward_source: str,
        state_before: Optional[Dict[str, Any]] = None,
        state_after: Optional[Dict[str, Any]] = None,
        step: int = 0,
    ) -> ReinforcementReward:
        """Record reinforcement reward"""
        reward = ReinforcementReward(
            reward_id=str(uuid4()),
            episode_id=episode_id,
            action_type=action_type,
            reward_value=reward_value,
            reward_source=reward_source,
            state_before=state_before,
            state_after=state_after,
            step=step,
            timestamp=datetime.utcnow(),
        )
        
        self.db.add(reward)
        await self.db.commit()
        await self.db.refresh(reward)
        
        return reward
    
    async def get_episode_rewards(
        self,
        episode_id: str,
    ) -> List[ReinforcementReward]:
        """Get rewards for an episode"""
        result = await self.db.execute(
            select(ReinforcementReward)
            .where(ReinforcementReward.episode_id == episode_id)
            .order_by(ReinforcementReward.step)
        )
        
        return list(result.scalars().all())
    
    async def calculate_episode_score(self, episode_id: str) -> float:
        """Calculate total episode score"""
        rewards = await self.get_episode_rewards(episode_id)
        
        if not rewards:
            return 0.0
        
        # Sum discounted rewards
        total = 0.0
        gamma = 0.9  # Discount factor
        
        for i, reward in enumerate(rewards):
            total += reward.reward_value * (gamma ** i)
        
        return total


class AdaptiveOptimizer:
    """
    Adaptive optimizer using learned patterns.
    Optimizes execution parameters based on historical data.
    """
    
    def __init__(self, db: AsyncSession, learning_engine: RuntimeLearningEngine):
        self.db = db
        self.learning_engine = learning_engine
        self._optimization_history: List[Dict[str, Any]] = []
    
    async def optimize_parameters(
        self,
        target_type: str,
        target_id: str,
        current_params: Dict[str, float],
        objective: str = "latency",
    ) -> Dict[str, float]:
        """Optimize execution parameters"""
        # Get historical data
        learnings = await self.learning_engine.get_learning_data(target_id, limit=100)
        
        if len(learnings) < 10:
            # Not enough data, return current params
            return current_params
        
        # Find best performing configurations
        best_configs = await self._find_best_configurations(learnings, objective)
        
        if not best_configs:
            return current_params
        
        # Blend with current params
        optimized = current_params.copy()
        
        for key, best_value in best_configs.items():
            if key in current_params:
                # Gradual blend (30% towards best)
                optimized[key] = current_params[key] * 0.7 + best_value * 0.3
        
        return optimized
    
    async def _find_best_configurations(
        self,
        learnings: List[ExecutionLearning],
        objective: str,
    ) -> Dict[str, float]:
        """Find best performing configurations"""
        # Sort by performance
        sorted_learnings = sorted(
            learnings,
            key=lambda l: l.performance.get(objective, 0) if l.performance else 0,
            reverse=True,
        )
        
        # Get top 20%
        top_count = max(1, len(sorted_learnings) // 5)
        top_learnings = sorted_learnings[:top_count]
        
        if not top_learnings:
            return {}
        
        # Average the best configurations
        feature_keys = list(top_learnings[0].features.keys())
        best_config = {}
        
        for key in feature_keys:
            if isinstance(top_learnings[0].features[key], (int, float)):
                values = [l.features[key] for l in top_learnings]
                best_config[key] = sum(values) / len(values)
        
        return best_config
    
    async def apply_optimization(
        self,
        optimization_type: str,
        target_id: str,
        before_params: Dict[str, Any],
        after_params: Dict[str, Any],
        improvement: float,
    ) -> None:
        """Record optimization application"""
        self._optimization_history.append({
            "type": optimization_type,
            "target_id": target_id,
            "before": before_params,
            "after": after_params,
            "improvement": improvement,
            "timestamp": datetime.utcnow().isoformat(),
        })


class BottleneckPredictor:
    """
    Bottleneck predictor for runtime issues.
    Predicts potential bottlenecks before they occur.
    """
    
    def __init__(self, db: AsyncSession, learning_engine: RuntimeLearningEngine):
        self.db = db
        self.learning_engine = learning_engine
        self._prediction_models: Dict[str, Any] = {}
    
    async def predict_bottleneck(
        self,
        workload_type: str,
        current_metrics: Dict[str, float],
    ) -> Dict[str, Any]:
        """Predict potential bottleneck"""
        predictions = []
        
        # Check CPU
        if current_metrics.get("cpu_percent", 0) > 70:
            predictions.append({
                "type": "cpu",
                "severity": "high" if current_metrics["cpu_percent"] > 85 else "medium",
                "predicted_impact": "slowdown",
                "time_to_impact": self._estimate_time(70, current_metrics["cpu_percent"], 5),
            })
        
        # Check Memory
        if current_metrics.get("memory_percent", 0) > 80:
            predictions.append({
                "type": "memory",
                "severity": "high" if current_metrics["memory_percent"] > 90 else "medium",
                "predicted_impact": "oom_risk",
                "time_to_impact": self._estimate_time(80, current_metrics["memory_percent"], 2),
            })
        
        # Check Queue depth
        if current_metrics.get("queue_depth", 0) > 50:
            predictions.append({
                "type": "queue",
                "severity": "medium",
                "predicted_impact": "increased_latency",
                "time_to_impact": 300,  # 5 minutes
            })
        
        return {
            "has_bottlenecks": len(predictions) > 0,
            "predictions": predictions,
            "recommendation": self._generate_recommendation(predictions),
        }
    
    def _estimate_time(self, threshold: float, current: float, rate: float) -> int:
        """Estimate time to reach threshold"""
        if current <= threshold:
            return 600  # 10 minutes
        
        rate_per_minute = rate
        remaining = current - threshold
        
        return int(remaining / rate_per_minute * 60) if rate_per_minute > 0 else 600
    
    def _generate_recommendation(self, predictions: List[Dict[str, Any]]) -> str:
        """Generate recommendation based on predictions"""
        if not predictions:
            return "No immediate action required"
        
        types = [p["type"] for p in predictions]
        
        if "cpu" in types and "memory" in types:
            return "Consider scaling out or optimizing resource usage"
        elif "cpu" in types:
            return "Consider CPU optimization or scaling horizontally"
        elif "memory" in types:
            return "Consider memory optimization or scaling up"
        elif "queue" in types:
            return "Consider adding workers to reduce queue depth"
        
        return "Monitor the situation closely"