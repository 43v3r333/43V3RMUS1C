"""
Forecasting Domain - Predictive runtime planning over long horizons.

Forecasts the future of orchestration:

  - Execution duration / queue time / failure probability per workflow class
  - Multi-stage execution graphs ahead of dispatch
  - Capacity / saturation projections for the next planning window

The domain pairs persistent forecast records with an in-process forecaster
that fuses historical execution stats with adaptive policy hints.
"""
from .models import (
    ForecastKind,
    ForecastHorizon,
    StrategyKind,
    ExecutionForecast,
    PredictiveRuntimeMetric,
    MultiStageExecutionGraph,
    OrchestrationStrategy,
)
from .services import (
    ForecastingService,
    MultiStagePlanner,
    OrchestrationStrategyEngine,
    ForecastSnapshot,
    StagePlanResult,
    StrategyDecision,
)

__all__ = [
    # Enums
    "ForecastKind",
    "ForecastHorizon",
    "StrategyKind",
    # Models
    "ExecutionForecast",
    "PredictiveRuntimeMetric",
    "MultiStageExecutionGraph",
    "OrchestrationStrategy",
    # Services
    "ForecastingService",
    "MultiStagePlanner",
    "OrchestrationStrategyEngine",
    # Data
    "ForecastSnapshot",
    "StagePlanResult",
    "StrategyDecision",
]
