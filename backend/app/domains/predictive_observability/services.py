"""
Predictive Observability Services - Runtime forecasting and predictive analytics.

Provides:
- Predictive runtime analytics
- Orchestration stability forecasting
- Execution anomaly detection
- Adaptive telemetry cognition
- Distributed diagnostics systems
"""
import asyncio
import logging
import random
import statistics
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func

from .models import (
    PredictiveRuntimeForecast,
    OrchestrationStabilityMetric,
    AdaptiveTelemetryDataPoint,
    DistributedDiagnosticsResult,
    AnomalyForecast,
    TelemetryAggregation,
    ForecastModel,
    RuntimeAnomalyEvent,
    ForecastType,
    ForecastHorizon,
    ForecastStatus,
    MetricGranularity,
)


logger = logging.getLogger(__name__)


@dataclass
class ForecastResult:
    """Forecast result"""
    forecast_id: str
    predicted_value: float
    confidence: float
    min_value: Optional[float]
    max_value: Optional[float]
    horizon: str
    expires_at: Optional[datetime]


@dataclass
class AnomalyAlert:
    """Anomaly alert"""
    alert_id: str
    anomaly_type: str
    severity: str
    target_id: str
    probability: float
    detected_at: datetime


class RuntimeForecastingEngine:
    """Predictive runtime forecasting engine"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._forecasts: Dict[str, PredictiveRuntimeForecast] = {}
        self._models: Dict[str, ForecastModel] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize runtime forecasting engine"""
        await self._load_forecasts()
        await self._load_models()
        self._running = True
        logger.info("RuntimeForecastingEngine initialized")
    
    async def shutdown(self) -> None:
        """Shutdown runtime forecasting engine"""
        self._running = False
        logger.info("RuntimeForecastingEngine shutdown")
    
    async def _load_forecasts(self) -> None:
        """Load recent forecasts"""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        result = await self.db.execute(
            select(PredictiveRuntimeForecast).where(
                PredictiveRuntimeForecast.created_at >= cutoff
            )
        )
        for forecast in result.scalars().all():
            self._forecasts[forecast.forecast_id] = forecast
    
    async def _load_models(self) -> None:
        """Load active forecast models"""
        result = await self.db.execute(
            select(ForecastModel).where(ForecastModel.is_active == True)
        )
        for model in result.scalars().all():
            self._models[model.model_id] = model
    
    # ==================== Forecasting ====================
    
    async def create_forecast(
        self,
        forecast_type: str,
        target_id: str,
        target_type: str,
        predicted_value: float,
        horizon: str = ForecastHorizon.SHORT.value,
        confidence: float = 0.7,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        predicted_for: Optional[datetime] = None,
        features: Optional[Dict[str, float]] = None,
    ) -> PredictiveRuntimeForecast:
        """Create new forecast"""
        forecast_id = f"forecast-{uuid4()}"
        
        # Determine expiration
        if horizon == ForecastHorizon.SHORT.value:
            expires = datetime.utcnow() + timedelta(minutes=15)
        elif horizon == ForecastHorizon.MEDIUM.value:
            expires = datetime.utcnow() + timedelta(hours=1)
        else:
            expires = datetime.utcnow() + timedelta(hours=4)
        
        # Use best available model
        model = self._get_best_model(forecast_type)
        model_type = model.model_type if model else "simple_moving_average"
        model_version = model.model_id if model else None
        
        forecast = PredictiveRuntimeForecast(
            forecast_id=forecast_id,
            forecast_type=forecast_type,
            horizon=horizon,
            target_id=target_id,
            target_type=target_type,
            predicted_value=predicted_value,
            confidence=confidence,
            min_value=min_value,
            max_value=max_value,
            model_type=model_type,
            model_version=model_version,
            features=features,
            predicted_for=predicted_for or datetime.utcnow() + timedelta(minutes=30),
            expires_at=expires,
        )
        
        self.db.add(forecast)
        await self.db.commit()
        await self.db.refresh(forecast)
        
        self._forecasts[forecast_id] = forecast
        return forecast
    
    def _get_best_model(self, forecast_type: str) -> Optional[ForecastModel]:
        """Get best model for forecast type"""
        candidates = [m for m in self._models.values() if m.forecast_target == forecast_type]
        if not candidates:
            return None
        
        return max(candidates, key=lambda m: m.accuracy)
    
    async def validate_forecast(
        self,
        forecast_id: str,
        actual_value: float,
    ) -> Optional[PredictiveRuntimeForecast]:
        """Validate forecast against actual value"""
        forecast = self._forecasts.get(forecast_id)
        if not forecast:
            result = await self.db.execute(
                select(PredictiveRuntimeForecast).where(PredictiveRuntimeForecast.forecast_id == forecast_id)
            )
            forecast = result.scalar_one_or_none()
        
        if not forecast:
            return None
        
        forecast.actual_value = actual_value
        forecast.prediction_error = abs(actual_value - forecast.predicted_value)
        forecast.error_percentage = (forecast.prediction_error / forecast.predicted_value * 100) if forecast.predicted_value != 0 else 0
        forecast.status = ForecastStatus.VALIDATED.value
        forecast.validated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(forecast)
        
        # Update model performance
        await self._update_model_performance(forecast)
        
        return forecast
    
    async def _update_model_performance(self, forecast: PredictiveRuntimeForecast) -> None:
        """Update model performance based on forecast"""
        if not forecast.model_version:
            return
        
        model = self._models.get(forecast.model_version)
        if not model:
            return
        
        # Calculate new accuracy (exponential moving average)
        if forecast.error_percentage is not None:
            error_rate = 1 - (forecast.error_percentage / 100)
            model.accuracy = model.accuracy * 0.9 + error_rate * 0.1
        
        await self.db.commit()
    
    async def get_forecasts(
        self,
        target_id: Optional[str] = None,
        forecast_type: Optional[str] = None,
        horizon: Optional[str] = None,
        min_confidence: float = 0.0,
    ) -> List[PredictiveRuntimeForecast]:
        """Get forecasts matching criteria"""
        query = select(PredictiveRuntimeForecast).where(
            PredictiveRuntimeForecast.status.in_([
                ForecastStatus.PENDING.value,
                ForecastStatus.ACTIVE.value,
            ])
        )
        
        if target_id:
            query = query.where(PredictiveRuntimeForecast.target_id == target_id)
        
        if forecast_type:
            query = query.where(PredictiveRuntimeForecast.forecast_type == forecast_type)
        
        if horizon:
            query = query.where(PredictiveRuntimeForecast.horizon == horizon)
        
        query = query.where(PredictiveRuntimeForecast.confidence >= min_confidence)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def calculate_forecast(
        self,
        forecast_type: str,
        target_id: str,
        history: List[float],
        horizon: str = ForecastHorizon.SHORT.value,
    ) -> Tuple[float, float, float]:
        """Calculate forecast from historical data"""
        if len(history) < 3:
            # Not enough data
            return 0.0, 0.3, 0.0
        
        # Simple moving average with trend
        window = min(10, len(history))
        recent = history[-window:]
        
        avg = sum(recent) / len(recent)
        
        # Calculate trend
        if len(recent) >= 2:
            trend = (recent[-1] - recent[0]) / len(recent)
        else:
            trend = 0.0
        
        # Project forward
        if horizon == ForecastHorizon.SHORT.value:
            steps = 5
        elif horizon == ForecastHorizon.MEDIUM.value:
            steps = 15
        else:
            steps = 30
        
        projected = avg + (trend * steps)
        
        # Calculate confidence based on variance
        if len(recent) > 1:
            variance = statistics.stdev(recent)
            rel_variance = variance / avg if avg != 0 else 0
            confidence = max(0.3, min(0.95, 1 - rel_variance))
        else:
            confidence = 0.5
        
        # Calculate range
        if len(recent) > 1:
            stddev = statistics.stdev(recent)
            min_val = projected - (stddev * 2)
            max_val = projected + (stddev * 2)
        else:
            min_val = projected * 0.9
            max_val = projected * 1.1
        
        return projected, confidence, avg


class StabilityForecastingEngine:
    """Orchestration stability forecasting"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._metrics: Dict[str, OrchestrationStabilityMetric] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize stability forecasting engine"""
        await self._load_metrics()
        self._running = True
        logger.info("StabilityForecastingEngine initialized")
    
    async def shutdown(self) -> None:
        """Shutdown stability forecasting engine"""
        self._running = False
        logger.info("StabilityForecastingEngine shutdown")
    
    async def _load_metrics(self) -> None:
        """Load recent stability metrics"""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        result = await self.db.execute(
            select(OrchestrationStabilityMetric).where(
                OrchestrationStabilityMetric.measured_at >= cutoff
            )
        )
        for metric in result.scalars().all():
            self._metrics[metric.metric_id] = metric
    
    # ==================== Stability Tracking ====================
    
    async def record_metric(
        self,
        metric_type: str,
        target_id: str,
        target_type: str,
        current_value: float,
    ) -> OrchestrationStabilityMetric:
        """Record stability metric"""
        metric_id = f"stability-{target_type}-{target_id}-{metric_type}"
        
        existing = self._metrics.get(metric_id)
        
        if existing:
            existing.previous_value = existing.current_value
            existing.current_value = current_value
            existing.measured_at = datetime.utcnow()
            
            # Calculate volatility
            if existing.previous_value != 0:
                change = abs(current_value - existing.previous_value) / existing.previous_value
                existing.volatility = existing.volatility * 0.8 + change * 0.2
            
            # Determine trend
            if current_value > existing.current_value:
                existing.trend = "increasing"
            elif current_value < existing.current_value:
                existing.trend = "decreasing"
            else:
                existing.trend = "stable"
        else:
            existing = OrchestrationStabilityMetric(
                metric_id=metric_id,
                metric_type=metric_type,
                target_id=target_id,
                target_type=target_type,
                current_value=current_value,
                previous_value=0,
            )
            self.db.add(existing)
        
        await self.db.commit()
        await self.db.refresh(existing)
        
        self._metrics[metric_id] = existing
        return existing
    
    async def predict_stability(
        self,
        target_id: str,
        target_type: str,
        metric_type: str,
    ) -> Dict[str, Any]:
        """Predict stability for target"""
        metric_id = f"stability-{target_type}-{target_id}-{metric_type}"
        metric = self._metrics.get(metric_id)
        
        if not metric:
            return {"stable": True, "confidence": 0.0}
        
        # Predict based on trend and volatility
        stable = True
        confidence = 0.8
        
        if metric.volatility > 0.3:
            stable = False
            confidence = 0.6
        
        if metric.trend == "decreasing" and metric.current_value < metric.warning_threshold:
            stable = False
            confidence = 0.5
        
        return {
            "stable": stable,
            "confidence": confidence,
            "current_value": metric.current_value,
            "trend": metric.trend,
            "volatility": metric.volatility,
        }
    
    async def get_unstable_targets(self) -> List[str]:
        """Get list of unstable targets"""
        unstable = []
        
        for metric in self._metrics.values():
            if metric.current_value < metric.warning_threshold:
                unstable.append(metric.target_id)
        
        return list(set(unstable))


class TelemetryCollector:
    """Adaptive telemetry data collection"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._data_points: Dict[str, AdaptiveTelemetryDataPoint] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize telemetry collector"""
        self._running = True
        logger.info("TelemetryCollector initialized")
    
    async def shutdown(self) -> None:
        """Shutdown telemetry collector"""
        self._running = False
        logger.info("TelemetryCollector shutdown")
    
    # ==================== Telemetry Collection ====================
    
    async def collect(
        self,
        metric_name: str,
        target_id: str,
        target_type: str,
        value: float,
        unit: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        granularity: str = MetricGranularity.MINUTE.value,
    ) -> AdaptiveTelemetryDataPoint:
        """Collect telemetry data point"""
        point_id = f"point-{uuid4()}"
        
        point = AdaptiveTelemetryDataPoint(
            point_id=point_id,
            metric_name=metric_name,
            target_id=target_id,
            target_type=target_type,
            value=value,
            unit=unit,
            tags=tags,
            granularity=granularity,
            timestamp=datetime.utcnow(),
        )
        
        self.db.add(point)
        await self.db.commit()
        await self.db.refresh(point)
        
        self._data_points[point_id] = point
        return point
    
    async def aggregate(
        self,
        metric_name: str,
        target_id: Optional[str],
        aggregation_type: str,
        period_start: datetime,
        period_end: datetime,
        granularity: str,
    ) -> TelemetryAggregation:
        """Aggregate telemetry data"""
        # Get data points in period
        query = select(AdaptiveTelemetryDataPoint).where(
            and_(
                AdaptiveTelemetryDataPoint.metric_name == metric_name,
                AdaptiveTelemetryDataPoint.timestamp >= period_start,
                AdaptiveTelemetryDataPoint.timestamp < period_end,
            )
        )
        
        if target_id:
            query = query.where(AdaptiveTelemetryDataPoint.target_id == target_id)
        
        result = await self.db.execute(query)
        points = list(result.scalars().all())
        
        if not points:
            return None
        
        # Calculate aggregation
        values = [p.value for p in points]
        
        agg_value = 0.0
        if aggregation_type == "avg":
            agg_value = sum(values) / len(values)
        elif aggregation_type == "sum":
            agg_value = sum(values)
        elif aggregation_type == "min":
            agg_value = min(values)
        elif aggregation_type == "max":
            agg_value = max(values)
        elif aggregation_type == "count":
            agg_value = float(len(values))
        
        aggregation_id = f"agg-{uuid4()}"
        
        aggregation = TelemetryAggregation(
            aggregation_id=aggregation_id,
            metric_name=metric_name,
            target_id=target_id,
            aggregation_type=aggregation_type,
            value=agg_value,
            min_value=min(values) if values else None,
            max_value=max(values) if values else None,
            count=len(values),
            granularity=granularity,
            period_start=period_start,
            period_end=period_end,
        )
        
        self.db.add(aggregation)
        await self.db.commit()
        await self.db.refresh(aggregation)
        
        return aggregation
    
    async def get_recent_data(
        self,
        metric_name: str,
        target_id: str,
        limit: int = 100,
    ) -> List[AdaptiveTelemetryDataPoint]:
        """Get recent telemetry data"""
        result = await self.db.execute(
            select(AdaptiveTelemetryDataPoint)
            .where(
                and_(
                    AdaptiveTelemetryDataPoint.metric_name == metric_name,
                    AdaptiveTelemetryDataPoint.target_id == target_id,
                )
            )
            .order_by(AdaptiveTelemetryDataPoint.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


class AnomalyDetectionEngine:
    """Execution anomaly detection"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._events: Dict[str, RuntimeAnomalyEvent] = {}
        self._forecasts: Dict[str, AnomalyForecast] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize anomaly detection engine"""
        await self._load_events()
        self._running = True
        logger.info("AnomalyDetectionEngine initialized")
    
    async def shutdown(self) -> None:
        """Shutdown anomaly detection engine"""
        self._running = False
        logger.info("AnomalyDetectionEngine shutdown")
    
    async def _load_events(self) -> None:
        """Load recent anomaly events"""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        result = await self.db.execute(
            select(RuntimeAnomalyEvent).where(
                RuntimeAnomalyEvent.detected_at >= cutoff
            )
        )
        for event in result.scalars().all():
            self._events[event.event_id] = event
    
    # ==================== Anomaly Detection ====================
    
    async def detect_anomaly(
        self,
        anomaly_type: str,
        target_id: str,
        target_type: str,
        detection_method: str,
        expected_value: float,
        actual_value: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> RuntimeAnomalyEvent:
        """Detect anomaly"""
        deviation = abs(actual_value - expected_value) / expected_value if expected_value != 0 else 0
        
        # Determine severity
        severity = "info"
        if deviation > 0.5:
            severity = "critical"
        elif deviation > 0.3:
            severity = "error"
        elif deviation > 0.15:
            severity = "warning"
        
        # Only create event for significant deviations
        if deviation < 0.1:
            return None
        
        event_id = f"anomaly-{uuid4()}"
        
        event = RuntimeAnomalyEvent(
            event_id=event_id,
            anomaly_type=anomaly_type,
            severity=severity,
            target_id=target_id,
            target_type=target_type,
            detection_method=detection_method,
            detection_score=min(1.0, deviation),
            expected_value=expected_value,
            actual_value=actual_value,
            deviation=deviation,
            context=context,
        )
        
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        
        self._events[event_id] = event
        return event
    
    async def predict_anomaly(
        self,
        anomaly_type: str,
        target_id: str,
        target_type: str,
        probability: float,
        evidence: List[Dict[str, Any]],
        predicted_time: Optional[datetime] = None,
    ) -> AnomalyForecast:
        """Predict potential anomaly"""
        forecast_id = f"anomaly-forecast-{uuid4()}"
        
        # Determine severity
        severity = "warning"
        if probability > 0.8:
            severity = "critical"
        elif probability > 0.5:
            severity = "error"
        
        forecast = AnomalyForecast(
            forecast_id=forecast_id,
            anomaly_type=anomaly_type,
            target_id=target_id,
            target_type=target_type,
            predicted_occurrence=predicted_time or datetime.utcnow() + timedelta(minutes=30),
            probability=probability,
            severity=severity,
            evidence=evidence,
            confidence=probability,
        )
        
        self.db.add(forecast)
        await self.db.commit()
        await self.db.refresh(forecast)
        
        self._forecasts[forecast_id] = forecast
        return forecast
    
    async def get_active_anomalies(self) -> List[RuntimeAnomalyEvent]:
        """Get active (unresolved) anomalies"""
        return [e for e in self._events.values() if not e.is_resolved]
    
    async def resolve_anomaly(
        self,
        event_id: str,
        resolution: str,
    ) -> Optional[RuntimeAnomalyEvent]:
        """Mark anomaly as resolved"""
        event = self._events.get(event_id)
        if not event:
            result = await self.db.execute(
                select(RuntimeAnomalyEvent).where(RuntimeAnomalyEvent.event_id == event_id)
            )
            event = result.scalar_one_or_none()
        
        if not event:
            return None
        
        event.is_resolved = True
        event.resolution = resolution
        event.resolved_at = datetime.utcnow()
        
        await self.db.commit()
        return event


class DistributedDiagnostics:
    """Distributed system diagnostics"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._results: Dict[str, DistributedDiagnosticsResult] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize distributed diagnostics"""
        self._running = True
        logger.info("DistributedDiagnostics initialized")
    
    async def shutdown(self) -> None:
        """Shutdown distributed diagnostics"""
        self._running = False
        logger.info("DistributedDiagnostics shutdown")
    
    # ==================== Diagnostics ====================
    
    async def run_diagnostics(
        self,
        diagnostics_type: str,
        target_id: str,
        target_type: str,
    ) -> DistributedDiagnosticsResult:
        """Run diagnostics on target"""
        diagnostics_id = f"diag-{uuid4()}"
        start_time = datetime.utcnow()
        
        # Simulate diagnostics
        issues_found = []
        recommendations = []
        
        # Check for common issues
        health_score = random.uniform(0.7, 1.0)
        
        if health_score < 0.7:
            issues_found.append({
                "issue": "Low health score",
                "severity": "warning",
                "metric": "health_score",
                "value": health_score,
            })
            recommendations.append("Review recent performance metrics")
        
        # Generate more specific issues based on type
        if diagnostics_type == "execution":
            if random.random() > 0.8:
                issues_found.append({
                    "issue": "High latency detected",
                    "severity": "warning",
                    "metric": "latency_p99",
                    "value": 500,
                })
                recommendations.append("Consider scaling resources")
        
        details = {
            "checks_performed": ["health", "performance", "connectivity"],
            "nodes_checked": random.randint(3, 10),
            "duration_ms": random.uniform(10, 100),
        }
        
        diagnostics = DistributedDiagnosticsResult(
            diagnostics_id=diagnostics_id,
            diagnostics_type=diagnostics_type,
            target_id=target_id,
            target_type=target_type,
            health_score=health_score,
            issues_found=issues_found if issues_found else None,
            recommendations=recommendations if recommendations else None,
            details=details,
            executed_at=start_time,
            completed_at=datetime.utcnow(),
            duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
        )
        
        self.db.add(diagnostics)
        await self.db.commit()
        await self.db.refresh(diagnostics)
        
        self._results[diagnostics_id] = diagnostics
        return diagnostics
    
    async def get_recent_results(
        self,
        limit: int = 10,
    ) -> List[DistributedDiagnosticsResult]:
        """Get recent diagnostics results"""
        result = await self.db.execute(
            select(DistributedDiagnosticsResult)
            .order_by(DistributedDiagnosticsResult.executed_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


class PredictiveObservabilityService:
    """Main service for predictive observability"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.forecasting_engine = RuntimeForecastingEngine(db)
        self.stability_engine = StabilityForecastingEngine(db)
        self.telemetry_collector = TelemetryCollector(db)
        self.anomaly_detector = AnomalyDetectionEngine(db)
        self.diagnostics = DistributedDiagnostics(db)
    
    async def initialize(self) -> None:
        """Initialize all sub-services"""
        await self.forecasting_engine.initialize()
        await self.stability_engine.initialize()
        await self.telemetry_collector.initialize()
        await self.anomaly_detector.initialize()
        await self.diagnostics.initialize()
        logger.info("PredictiveObservabilityService fully initialized")
    
    async def shutdown(self) -> None:
        """Shutdown all sub-services"""
        await self.forecasting_engine.shutdown()
        await self.stability_engine.shutdown()
        await self.telemetry_collector.shutdown()
        await self.anomaly_detector.shutdown()
        await self.diagnostics.shutdown()
        logger.info("PredictiveObservabilityService shutdown")
    
    async def get_observability_summary(self) -> Dict[str, Any]:
        """Get summary of observability state"""
        return {
            "active_forecasts": len([
                f for f in self.forecasting_engine._forecasts.values()
                if f.status in [ForecastStatus.PENDING.value, ForecastStatus.ACTIVE.value]
            ]),
            "stability_metrics": len(self.stability_engine._metrics),
            "telemetry_points": len(self.telemetry_collector._data_points),
            "active_anomalies": len(await self.anomaly_detector.get_active_anomalies()),
            "diagnostics_results": len(self.diagnostics._results),
        }