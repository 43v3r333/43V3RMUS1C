"""
Feedback Domain - Self-optimizing runtime systems and adaptive learning.

Implements the self-improvement loop:

  - OrchestrationFeedback   : execution outcome feedback from the runtime
  - AdaptiveLearningState    : current learned parameters per context
  - AutonomousTuningRecord   : autonomous parameter adjustments + outcomes
"""
from .models import (
    FeedbackType,
    TuningAction,
    OrchestrationFeedback,
    AdaptiveLearningState,
    AutonomousTuningRecord,
    TuningCycle,
)
from .services import (
    FeedbackLoopService,
    AdaptiveTuningService,
    FeedbackSnapshot,
    TuningRecommendation,
)

__all__ = [
    # Enums
    "FeedbackType",
    "TuningAction",
    # Models
    "OrchestrationFeedback",
    "AdaptiveLearningState",
    "AutonomousTuningRecord",
    "TuningCycle",
    # Services
    "FeedbackLoopService",
    "AdaptiveTuningService",
    # Data
    "FeedbackSnapshot",
    "TuningRecommendation",
]