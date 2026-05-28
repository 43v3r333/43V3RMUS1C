"""
Meta-Cognition Domain - EXECUTIVE INTELLIGENCE LAYER.

Runtime self-awareness, orchestration introspection, cognition diagnostics,
semantic consistency auditing, and adaptive governance.
"""
from .models import (
    IntrospectionPhase,
    CognitionState,
    AuditSeverity,
    DiagnosticType,
    ReconciliationStatus,
    PredictionHorizon,
    GovernanceAlignment,
    CognitionDiagnostics,
    IntrospectionSession,
    SemanticConsistencyAudit,
    AdaptiveGovernanceProfile,
    CognitionReconciliationState,
    RuntimeSelfAwarenessMetrics,
    PredictiveCognitionForecast,
    OrchestrationReasoningLineage,
    CognitionAnomalyRegistry,
)
from .services import MetaCognitionEngine, RuntimeSelfAnalyzer

__all__ = [
    # Enums
    "IntrospectionPhase",
    "CognitionState",
    "AuditSeverity",
    "DiagnosticType",
    "ReconciliationStatus",
    "PredictionHorizon",
    "GovernanceAlignment",
    # Models
    "CognitionDiagnostics",
    "IntrospectionSession",
    "SemanticConsistencyAudit",
    "AdaptiveGovernanceProfile",
    "CognitionReconciliationState",
    "RuntimeSelfAwarenessMetrics",
    "PredictiveCognitionForecast",
    "OrchestrationReasoningLineage",
    "CognitionAnomalyRegistry",
    # Services
    "MetaCognitionEngine",
    "RuntimeSelfAnalyzer",
]
