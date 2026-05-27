"""
Self-Healing Orchestration Services - Runtime stabilization and recovery.

Provides:
- Orchestration recovery engine
- Predictive anomaly prevention
- Execution resilience systems
- Adaptive stabilization loops
- Runtime recovery intelligence
"""
import asyncio
import logging
import random
from typing import Dict, List, Optional, Any, Callable
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func

from .models import (
    OrchestrationResilienceMetric,
    AnomalyDetection,
    RecoveryAction,
    StabilizationLoop,
    FailurePrediction,
    ResiliencePolicy,
    HealthCheck,
    FailoverRecord,
    RecoveryCheckpoint,
    RecoveryState,
    AnomalySeverity,
    ResilienceState,
    StabilizationMode,
)


logger = logging.getLogger(__name__)


@dataclass
class AnomalyAlert:
    """Anomaly alert representation"""
    anomaly_id: str
    severity: str
    title: str
    description: str
    target_id: Optional[str]
    detected_at: datetime
    deviation: Optional[float]


@dataclass
class RecoveryResult:
    """Recovery operation result"""
    success: bool
    action_id: str
    duration_ms: float
    message: Optional[str] = None
    recovery_state: Optional[Dict[str, Any]] = None


class AnomalyDetector:
    """Detects anomalies in runtime behavior"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._anomalies: Dict[str, AnomalyDetection] = {}
        self._detectors: Dict[str, Callable] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize anomaly detector"""
        await self._load_anomalies()
        self._register_builtin_detectors()
        self._running = True
        logger.info("AnomalyDetector initialized")
    
    async def shutdown(self) -> None:
        """Shutdown anomaly detector"""
        self._running = False
        logger.info("AnomalyDetector shutdown")
    
    async def _load_anomalies(self) -> None:
        """Load recent anomalies"""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        result = await self.db.execute(
            select(AnomalyDetection).where(
                AnomalyDetection.detected_at >= cutoff
            )
        )
        for anomaly in result.scalars().all():
            self._anomalies[anomaly.anomaly_id] = anomaly
    
    def _register_builtin_detectors(self) -> None:
        """Register built-in anomaly detectors"""
        self._detectors["threshold"] = self._detect_threshold_violation
        self._detectors["trend"] = self._detect_trend_anomaly
        self._detectors["pattern"] = self._detect_pattern_anomaly
        self._detectors["correlation"] = self._detect_correlation_breakdown
    
    # ==================== Detection ====================
    
    async def detect(
        self,
        target_id: str,
        target_type: str,
        current_value: float,
        expected_value: Optional[float] = None,
        metric_type: str = "performance",
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[AnomalyDetection]:
        """Detect anomaly in metric"""
        # Calculate deviation
        deviation = None
        if expected_value:
            deviation = abs(current_value - expected_value) / expected_value if expected_value != 0 else 0
        
        # Determine severity
        severity = AnomalySeverity.INFO.value
        if deviation and deviation > 0.5:
            severity = AnomalySeverity.CRITICAL.value
        elif deviation and deviation > 0.3:
            severity = AnomalySeverity.ERROR.value
        elif deviation and deviation > 0.15:
            severity = AnomalySeverity.WARNING.value
        
        # Create anomaly if significant deviation
        if deviation and deviation > 0.1:
            anomaly_id = f"anomaly-{uuid4()}"
            
            anomaly = AnomalyDetection(
                anomaly_id=anomaly_id,
                anomaly_type=metric_type,
                severity=severity,
                target_id=target_id,
                target_type=target_type,
                title=f"{metric_type.capitalize()} anomaly detected",
                detection_method="statistical",
                expected_value=expected_value,
                actual_value=current_value,
                deviation=deviation,
                context=context,
            )
            
            self.db.add(anomaly)
            await self.db.commit()
            await self.db.refresh(anomaly)
            
            self._anomalies[anomaly_id] = anomaly
            return anomaly
        
        return None
    
    def _detect_threshold_violation(
        self,
        current: float,
        threshold: float,
    ) -> Optional[Dict[str, Any]]:
        """Detect threshold violation"""
        if abs(current) > threshold:
            return {
                "type": "threshold_violation",
                "current": current,
                "threshold": threshold,
                "deviation": abs(current - threshold) / threshold,
            }
        return None
    
    def _detect_trend_anomaly(
        self,
        history: List[float],
        current: float,
    ) -> Optional[Dict[str, Any]]:
        """Detect trend anomaly"""
        if len(history) < 3:
            return None
        
        # Calculate trend
        changes = [history[i+1] - history[i] for i in range(len(history)-1)]
        avg_change = sum(changes) / len(changes)
        
        # Current change from last
        current_change = current - history[-1]
        
        # Detect if change is significantly different from trend
        if abs(current_change - avg_change) > abs(avg_change) * 2:
            return {
                "type": "trend_anomaly",
                "avg_change": avg_change,
                "current_change": current_change,
                "deviation": abs(current_change - avg_change) / abs(avg_change) if avg_change != 0 else 0,
            }
        
        return None
    
    def _detect_pattern_anomaly(
        self,
        expected_pattern: List[float],
        actual: float,
        pattern_position: int,
    ) -> Optional[Dict[str, Any]]:
        """Detect pattern anomaly"""
        if pattern_position >= len(expected_pattern):
            return None
        
        expected = expected_pattern[pattern_position]
        deviation = abs(actual - expected) / expected if expected != 0 else 0
        
        if deviation > 0.2:
            return {
                "type": "pattern_anomaly",
                "expected": expected,
                "actual": actual,
                "deviation": deviation,
            }
        
        return None
    
    def _detect_correlation_breakdown(
        self,
        metric1: List[float],
        metric2: List[float],
    ) -> Optional[Dict[str, Any]]:
        """Detect correlation breakdown"""
        if len(metric1) < 5 or len(metric2) < 5:
            return None
        
        # Calculate correlation
        n = min(len(metric1), len(metric2))
        recent_m1 = metric1[-n:]
        recent_m2 = metric2[-n:]
        
        mean1 = sum(recent_m1) / n
        mean2 = sum(recent_m2) / n
        
        covariance = sum((recent_m1[i] - mean1) * (recent_m2[i] - mean2) for i in range(n)) / n
        
        std1 = (sum((x - mean1) ** 2 for x in recent_m1) / n) ** 0.5
        std2 = (sum((x - mean2) ** 2 for x in recent_m2) / n) ** 0.5
        
        correlation = covariance / (std1 * std2) if std1 > 0 and std2 > 0 else 0
        
        if abs(correlation) < 0.3:  # Low correlation
            return {
                "type": "correlation_breakdown",
                "correlation": correlation,
                "deviation": 1 - abs(correlation),
            }
        
        return None
    
    async def get_active_anomalies(
        self,
        min_severity: Optional[str] = None,
    ) -> List[AnomalyDetection]:
        """Get all active (unresolved) anomalies"""
        query = select(AnomalyDetection).where(
            AnomalyDetection.is_resolved == False
        )
        
        if min_severity:
            severity_order = {
                AnomalySeverity.INFO.value: 0,
                AnomalySeverity.WARNING.value: 1,
                AnomalySeverity.ERROR.value: 2,
                AnomalySeverity.CRITICAL.value: 3,
            }
            min_level = severity_order.get(min_severity, 0)
            query = query.filter(
                AnomalyDetection.severity.in_([
                    k for k, v in severity_order.items() if v >= min_level
                ])
            )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def resolve_anomaly(
        self,
        anomaly_id: str,
        resolution_action: str,
    ) -> Optional[AnomalyDetection]:
        """Mark anomaly as resolved"""
        anomaly = self._anomalies.get(anomaly_id)
        if not anomaly:
            result = await self.db.execute(
                select(AnomalyDetection).where(AnomalyDetection.anomaly_id == anomaly_id)
            )
            anomaly = result.scalar_one_or_none()
        
        if not anomaly:
            return None
        
        anomaly.is_resolved = True
        anomaly.resolution_action = resolution_action
        anomaly.resolved_at = datetime.utcnow()
        
        if anomaly.detected_at:
            anomaly.duration_ms = (anomaly.resolved_at - anomaly.detected_at).total_seconds() * 1000
        
        await self.db.commit()
        return anomaly


class RecoveryEngine:
    """Orchestration recovery engine"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._actions: Dict[str, RecoveryAction] = {}
        self._policies: Dict[str, ResiliencePolicy] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize recovery engine"""
        await self._load_actions()
        await self._load_policies()
        self._running = True
        logger.info("RecoveryEngine initialized")
    
    async def shutdown(self) -> None:
        """Shutdown recovery engine"""
        self._running = False
        logger.info("RecoveryEngine shutdown")
    
    async def _load_actions(self) -> None:
        """Load recent recovery actions"""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        result = await self.db.execute(
            select(RecoveryAction).where(
                or_(
                    RecoveryAction.completed_at == None,
                    RecoveryAction.completed_at >= cutoff
                )
            )
        )
        for action in result.scalars().all():
            self._actions[action.action_id] = action
    
    async def _load_policies(self) -> None:
        """Load resilience policies"""
        result = await self.db.execute(
            select(ResiliencePolicy).where(ResiliencePolicy.enabled == True)
        )
        for policy in result.scalars().all():
            self._policies[policy.name] = policy
    
    # ==================== Recovery Actions ====================
    
    async def create_recovery_action(
        self,
        action_type: str,
        action_description: str,
        target_id: Optional[str] = None,
        target_type: Optional[str] = None,
        anomaly_id: Optional[str] = None,
        action_config: Optional[Dict[str, Any]] = None,
    ) -> RecoveryAction:
        """Create recovery action"""
        action_id = f"recovery-{uuid4()}"
        
        action = RecoveryAction(
            action_id=action_id,
            anomaly_id=anomaly_id,
            action_type=action_type,
            action_description=action_description,
            target_id=target_id,
            target_type=target_type,
            action_config=action_config,
            state=RecoveryState.IDLE.value,
        )
        
        self.db.add(action)
        await self.db.commit()
        await self.db.refresh(action)
        
        self._actions[action_id] = action
        return action
    
    async def execute_recovery(
        self,
        action_id: str,
    ) -> RecoveryResult:
        """Execute recovery action"""
        action = self._actions.get(action_id)
        if not action:
            result = await self.db.execute(
                select(RecoveryAction).where(RecoveryAction.action_id == action_id)
            )
            action = result.scalar_one_or_none()
        
        if not action:
            return RecoveryResult(
                success=False,
                action_id=action_id,
                duration_ms=0,
                message="Action not found",
            )
        
        start_time = datetime.utcnow()
        action.state = RecoveryState.DETECTING.value
        action.started_at = start_time
        action.attempts += 1
        
        await self.db.commit()
        
        try:
            # Execute based on action type
            if action.action_type == "retry":
                result_data = await self._execute_retry(action)
            elif action.action_type == "restart":
                result_data = await self._execute_restart(action)
            elif action.action_type == "failover":
                result_data = await self._execute_failover(action)
            elif action.action_type == "scale":
                result_data = await self._execute_scale(action)
            elif action.action_type == "restart_node":
                result_data = await self._execute_restart_node(action)
            else:
                result_data = await self._execute_default(action)
            
            action.state = RecoveryState.COMPLETED.value
            action.success = True
            action.result = result_data
            
        except Exception as e:
            logger.error(f"Recovery action failed: {e}")
            action.state = RecoveryState.FAILED.value
            action.error_message = str(e)
            
            if action.attempts < action.max_attempts:
                action.state = RecoveryState.IDLE.value  # Allow retry
            
        end_time = datetime.utcnow()
        action.completed_at = end_time
        action.duration_ms = (end_time - start_time).total_seconds() * 1000
        
        await self.db.commit()
        
        return RecoveryResult(
            success=action.success,
            action_id=action_id,
            duration_ms=action.duration_ms or 0,
            message=action.error_message,
            recovery_state=action.result,
        )
    
    async def _execute_retry(self, action: RecoveryAction) -> Dict[str, Any]:
        """Execute retry recovery"""
        await asyncio.sleep(0.1)  # Simulate retry delay
        return {"retried": True, "delay_ms": 100}
    
    async def _execute_restart(self, action: RecoveryAction) -> Dict[str, Any]:
        """Execute restart recovery"""
        await asyncio.sleep(0.2)  # Simulate restart
        return {"restarted": True, "clean_shutdown": True}
    
    async def _execute_failover(self, action: RecoveryAction) -> Dict[str, Any]:
        """Execute failover recovery"""
        await asyncio.sleep(0.3)  # Simulate failover
        return {"failover_initiated": True, "target_node": action.target_id}
    
    async def _execute_scale(self, action: RecoveryAction) -> Dict[str, Any]:
        """Execute scale recovery"""
        config = action.action_config or {}
        scale_factor = config.get("scale_factor", 2)
        return {"scaled": True, "scale_factor": scale_factor}
    
    async def _execute_restart_node(self, action: RecoveryAction) -> Dict[str, Any]:
        """Execute node restart recovery"""
        await asyncio.sleep(0.15)  # Simulate node restart
        return {"node_restarted": True, "node_id": action.target_id}
    
    async def _execute_default(self, action: RecoveryAction) -> Dict[str, Any]:
        """Execute default recovery"""
        return {"executed": True, "type": action.action_type}
    
    async def get_pending_actions(self) -> List[RecoveryAction]:
        """Get pending recovery actions"""
        return [a for a in self._actions.values() if a.state in [
            RecoveryState.IDLE.value,
            RecoveryState.DETECTING.value,
        ]]
    
    async def get_action_history(
        self,
        limit: int = 100,
    ) -> List[RecoveryAction]:
        """Get action history"""
        result = await self.db.execute(
            select(RecoveryAction)
            .order_by(RecoveryAction.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


class StabilizationLoopManager:
    """Manages adaptive stabilization loops"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._loops: Dict[str, StabilizationLoop] = {}
        self._running = False
        self._active_loops: Dict[str, asyncio.Task] = {}
    
    async def initialize(self) -> None:
        """Initialize stabilization loop manager"""
        await self._load_loops()
        self._running = True
        logger.info("StabilizationLoopManager initialized")
    
    async def shutdown(self) -> None:
        """Shutdown stabilization loop manager"""
        # Cancel active loops
        for task in self._active_loops.values():
            task.cancel()
        self._running = False
        logger.info("StabilizationLoopManager shutdown")
    
    async def _load_loops(self) -> None:
        """Load active loops"""
        result = await self.db.execute(
            select(StabilizationLoop).where(
                StabilizationLoop.state == "running"
            )
        )
        for loop in result.scalars().all():
            self._loops[loop.loop_id] = loop
    
    # ==================== Loop Management ====================
    
    async def create_loop(
        self,
        loop_type: str,
        target_id: Optional[str],
        target_type: Optional[str],
        target_metric: str,
        target_value: float,
        mode: str = StabilizationMode.ACTIVE.value,
        interval_seconds: int = 60,
        max_iterations: int = 10,
    ) -> StabilizationLoop:
        """Create new stabilization loop"""
        loop_id = f"loop-{uuid4()}"
        
        loop = StabilizationLoop(
            loop_id=loop_id,
            loop_type=loop_type,
            target_id=target_id,
            target_type=target_type,
            mode=mode,
            interval_seconds=interval_seconds,
            target_metric=target_metric,
            target_value=target_value,
            state="running",
            iteration_history=[],
        )
        
        self.db.add(loop)
        await self.db.commit()
        await self.db.refresh(loop)
        
        self._loops[loop_id] = loop
        
        # Start loop execution
        self._active_loops[loop_id] = asyncio.create_task(
            self._run_loop(loop)
        )
        
        return loop
    
    async def _run_loop(self, loop: StabilizationLoop) -> None:
        """Run stabilization loop"""
        while loop.state == "running" and loop.iteration_count < loop.max_iterations:
            try:
                # Execute iteration
                result = await self._execute_iteration(loop)
                
                # Record iteration
                history = loop.iteration_history or []
                history.append({
                    "iteration": loop.iteration_count,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat(),
                })
                loop.iteration_history = history
                loop.last_iteration = datetime.utcnow()
                
                # Check convergence
                if loop.current_value >= loop.target_value:
                    loop.state = "converged"
                    await self.db.commit()
                    break
                
                loop.iteration_count += 1
                await self.db.commit()
                
                # Wait for next iteration
                await asyncio.sleep(loop.interval_seconds)
                
            except asyncio.CancelledError:
                loop.state = "cancelled"
                await self.db.commit()
                break
            except Exception as e:
                logger.error(f"Stabilization loop error: {e}")
                loop.state = "error"
                await self.db.commit()
                break
        
        # Cleanup
        self._active_loops.pop(loop.loop_id, None)
    
    async def _execute_iteration(self, loop: StabilizationLoop) -> Dict[str, Any]:
        """Execute single stabilization iteration"""
        # Simulate metric improvement
        improvement = random.uniform(0.05, 0.15)
        loop.current_value = min(1.0, loop.current_value + improvement)
        
        return {
            "current_value": loop.current_value,
            "improvement": improvement,
            "target_value": loop.target_value,
        }
    
    async def stop_loop(self, loop_id: str) -> Optional[StabilizationLoop]:
        """Stop stabilization loop"""
        loop = self._loops.get(loop_id)
        if not loop:
            return None
        
        loop.state = "stopped"
        loop.completed_at = datetime.utcnow()
        
        # Cancel task
        task = self._active_loops.get(loop_id)
        if task:
            task.cancel()
            self._active_loops.pop(loop_id, None)
        
        await self.db.commit()
        return loop
    
    async def get_active_loops(self) -> List[StabilizationLoop]:
        """Get all active loops"""
        return [l for l in self._loops.values() if l.state == "running"]


class FailurePredictionEngine:
    """Predicts failures before they occur"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._predictions: Dict[str, FailurePrediction] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize failure prediction engine"""
        await self._load_predictions()
        self._running = True
        logger.info("FailurePredictionEngine initialized")
    
    async def shutdown(self) -> None:
        """Shutdown failure prediction engine"""
        self._running = False
        logger.info("FailurePredictionEngine shutdown")
    
    async def _load_predictions(self) -> None:
        """Load recent predictions"""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        result = await self.db.execute(
            select(FailurePrediction).where(
                FailurePrediction.created_at >= cutoff
            )
        )
        for prediction in result.scalars().all():
            self._predictions[prediction.prediction_id] = prediction
    
    # ==================== Prediction ====================
    
    async def predict(
        self,
        target_id: str,
        target_type: str,
        prediction_type: str,
        evidence: List[Dict[str, Any]],
        time_horizon_minutes: int = 60,
    ) -> FailurePrediction:
        """Create failure prediction"""
        # Calculate probability based on evidence
        probability = self._calculate_failure_probability(evidence)
        
        # Determine severity
        severity = AnomalySeverity.WARNING.value
        if probability > 0.8:
            severity = AnomalySeverity.CRITICAL.value
        elif probability > 0.5:
            severity = AnomalySeverity.ERROR.value
        
        prediction_id = f"prediction-{uuid4()}"
        
        prediction = FailurePrediction(
            prediction_id=prediction_id,
            prediction_type=prediction_type,
            target_id=target_id,
            target_type=target_type,
            predicted_failure=prediction_type,
            failure_probability=probability,
            severity=severity,
            evidence=evidence,
            time_horizon_minutes=time_horizon_minutes,
            predicted_time=datetime.utcnow() + timedelta(minutes=time_horizon_minutes),
        )
        
        self.db.add(prediction)
        await self.db.commit()
        await self.db.refresh(prediction)
        
        self._predictions[prediction_id] = prediction
        return prediction
    
    def _calculate_failure_probability(self, evidence: List[Dict[str, Any]]) -> float:
        """Calculate failure probability from evidence"""
        if not evidence:
            return 0.1
        
        # Average of evidence scores
        scores = []
        for e in evidence:
            if "score" in e:
                scores.append(e["score"])
            elif "confidence" in e:
                scores.append(e["confidence"])
            elif "deviation" in e:
                scores.append(min(1.0, e["deviation"]))
        
        if not scores:
            return 0.1
        
        return min(1.0, sum(scores) / len(scores) + 0.1)
    
    async def get_critical_predictions(
        self,
        min_probability: float = 0.5,
    ) -> List[FailurePrediction]:
        """Get critical failure predictions"""
        return [p for p in self._predictions.values() 
                if p.failure_probability >= min_probability 
                and not p.is_acted_upon]
    
    async def validate_prediction(
        self,
        prediction_id: str,
        actual_occurred: bool,
    ) -> Optional[FailurePrediction]:
        """Validate prediction against actual outcome"""
        prediction = self._predictions.get(prediction_id)
        if not prediction:
            result = await self.db.execute(
                select(FailurePrediction).where(FailurePrediction.prediction_id == prediction_id)
            )
            prediction = result.scalar_one_or_none()
        
        if not prediction:
            return None
        
        prediction.actual_occurred = actual_occurred
        prediction.validated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(prediction)
        
        return prediction


class HealthMonitor:
    """Monitors system health"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._metrics: Dict[str, OrchestrationResilienceMetric] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize health monitor"""
        await self._load_metrics()
        self._running = True
        logger.info("HealthMonitor initialized")
    
    async def shutdown(self) -> None:
        """Shutdown health monitor"""
        self._running = False
        logger.info("HealthMonitor shutdown")
    
    async def _load_metrics(self) -> None:
        """Load recent metrics"""
        result = await self.db.execute(
            select(OrchestrationResilienceMetric)
            .order_by(OrchestrationResilienceMetric.last_updated.desc())
            .limit(100)
        )
        for metric in result.scalars().all():
            self._metrics[metric.metric_id] = metric
    
    # ==================== Health Checks ====================
    
    async def record_metric(
        self,
        metric_type: str,
        target_id: str,
        target_type: str,
        current_value: float,
    ) -> OrchestrationResilienceMetric:
        """Record resilience metric"""
        metric_id = f"metric-{target_type}-{target_id}-{metric_type}"
        
        # Get existing or create new
        metric = self._metrics.get(metric_id)
        
        if metric:
            metric.previous_value = metric.current_value
            metric.current_value = current_value
            metric.last_updated = datetime.utcnow()
            
            # Calculate trend
            if metric.previous_value != 0:
                metric.change_rate = (current_value - metric.previous_value) / metric.previous_value
                if metric.change_rate > 0:
                    metric.trend = "increasing"
                elif metric.change_rate < 0:
                    metric.trend = "decreasing"
                else:
                    metric.trend = "stable"
        else:
            metric = OrchestrationResilienceMetric(
                metric_id=metric_id,
                metric_type=metric_type,
                target_id=target_id,
                target_type=target_type,
                current_value=current_value,
                previous_value=0,
                healthy_threshold=0.9,
                warning_threshold=0.7,
                critical_threshold=0.5,
            )
            self.db.add(metric)
        
        # Determine state
        if current_value >= metric.healthy_threshold:
            metric.state = ResilienceState.HEALTHY.value
        elif current_value >= metric.warning_threshold:
            metric.state = ResilienceState.DEGRADED.value
        else:
            metric.state = ResilienceState.RECOVERING.value
        
        await self.db.commit()
        await self.db.refresh(metric)
        
        self._metrics[metric_id] = metric
        return metric
    
    async def perform_health_check(
        self,
        check_type: str,
        target_id: Optional[str] = None,
        target_type: Optional[str] = None,
    ) -> HealthCheck:
        """Perform health check"""
        check_id = f"health-{uuid4()}"
        start_time = datetime.utcnow()
        
        # Simulate health check
        is_healthy = random.random() > 0.1  # 90% healthy
        health_score = random.uniform(0.85, 1.0) if is_healthy else random.uniform(0.3, 0.7)
        
        check = HealthCheck(
            check_id=check_id,
            check_type=check_type,
            target_id=target_id,
            target_type=target_type,
            is_healthy=is_healthy,
            health_score=health_score,
            check_duration_ms=random.uniform(5, 50),
        )
        
        self.db.add(check)
        await self.db.commit()
        await self.db.refresh(check)
        
        return check
    
    async def get_unhealthy_components(self) -> List[OrchestrationResilienceMetric]:
        """Get components that are unhealthy"""
        return [m for m in self._metrics.values() 
                if m.state != ResilienceState.HEALTHY.value]


class SelfHealingOrchestrationService:
    """Main service for self-healing orchestration"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.anomaly_detector = AnomalyDetector(db)
        self.recovery_engine = RecoveryEngine(db)
        self.stabilization_loops = StabilizationLoopManager(db)
        self.prediction_engine = FailurePredictionEngine(db)
        self.health_monitor = HealthMonitor(db)
    
    async def initialize(self) -> None:
        """Initialize all sub-services"""
        await self.anomaly_detector.initialize()
        await self.recovery_engine.initialize()
        await self.stabilization_loops.initialize()
        await self.prediction_engine.initialize()
        await self.health_monitor.initialize()
        logger.info("SelfHealingOrchestrationService fully initialized")
    
    async def shutdown(self) -> None:
        """Shutdown all sub-services"""
        await self.anomaly_detector.shutdown()
        await self.recovery_engine.shutdown()
        await self.stabilization_loops.shutdown()
        await self.prediction_engine.shutdown()
        await self.health_monitor.shutdown()
        logger.info("SelfHealingOrchestrationService shutdown")
    
    async def detect_and_recover(
        self,
        target_id: str,
        target_type: str,
        metric_value: float,
        expected_value: Optional[float] = None,
    ) -> RecoveryResult:
        """Detect anomaly and trigger recovery if needed"""
        # Detect anomaly
        anomaly = await self.anomaly_detector.detect(
            target_id=target_id,
            target_type=target_type,
            current_value=metric_value,
            expected_value=expected_value,
        )
        
        if anomaly and anomaly.severity in [
            AnomalySeverity.ERROR.value,
            AnomalySeverity.CRITICAL.value,
        ]:
            # Create recovery action
            action = await self.recovery_engine.create_recovery_action(
                action_type="retry",
                action_description=f"Recovery for {anomaly.title}",
                target_id=target_id,
                target_type=target_type,
                anomaly_id=anomaly.anomaly_id,
            )
            
            # Execute recovery
            return await self.recovery_engine.execute_recovery(action.action_id)
        
        return RecoveryResult(
            success=True,
            action_id="",
            duration_ms=0,
            message="No anomaly detected",
        )
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary of the system"""
        healthy_count = 0
        degraded_count = 0
        recovering_count = 0
        
        for metric in self.health_monitor._metrics.values():
            if metric.state == ResilienceState.HEALTHY.value:
                healthy_count += 1
            elif metric.state == ResilienceState.DEGRADED.value:
                degraded_count += 1
            elif metric.state == ResilienceState.RECOVERING.value:
                recovering_count += 1
        
        return {
            "total_components": len(self.health_monitor._metrics),
            "healthy": healthy_count,
            "degraded": degraded_count,
            "recovering": recovering_count,
            "active_anomalies": len(await self.anomaly_detector.get_active_anomalies()),
            "pending_recoveries": len(await self.recovery_engine.get_pending_actions()),
            "active_loops": len(await self.stabilization_loops.get_active_loops()),
            "critical_predictions": len(await self.prediction_engine.get_critical_predictions()),
        }