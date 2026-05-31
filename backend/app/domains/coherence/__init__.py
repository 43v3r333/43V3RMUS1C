"""
Coherence Domain - Unified Runtime Identity and Cognitive Continuity.

This domain implements the UNIFIED COGNITIVE COHERENCE LAYER:
- Unified runtime identity management
- Persistent cognitive continuity
- Platform-wide orchestration coherence
- Self-optimizing execution infrastructure
- Semantic runtime coordination
- Autonomous system stabilization
- Predictive adaptive governance
- Orchestration consolidation

These models become the SYSTEMIC COGNITIVE FABRIC of the platform.
"""
from .models import (
    # Identity & Lineage
    RuntimeIdentity,
    OrchestrationLineage,
    ExecutionLineageNode,
    RuntimeContext,
    
    # Cognitive Memory
    CognitiveMemoryItem,
    MemoryFragment,
    ContextSnapshot,
    
    # Semantic Execution
    SemanticExecutionGraph,
    SemanticNode,
    SemanticEdge,
    
    # Adaptive Runtime
    AdaptiveProfile,
    OptimizationMetric,
    ExecutionTuningHistory,
    
    # Governance
    GovernancePolicy,
    PolicyViolation,
    ArbitrationRecord,
    
    # Stability & Prediction
    OrchestrationStabilityMetrics,
    # ExecutionForecast removed - moved to forecasting.models
    # AnomalyDetection removed - moved to predictive_observability.models
    
    # Distributed Coordination
    # DistributedContextState removed - moved to distributed_runtime.models
    AgentConsensus,
    AuthorityDelegation,
    
    # Enums
    IdentityScope,
    LineageEventType,
    MemoryRetrievalMode,
    SemanticRelationType,
    TuningStrategy,
    PolicySeverity,
    StabilityStatus,
    ConsensusState,
    ExecutionHorizon,
)

from .services import (
    UnifiedIdentityManager,
    CognitiveContinuityEngine,
    SemanticCoordinator,
    AdaptiveRuntimeTuner,
    GovernanceEnforcer,
    StabilityPredictor,
    DistributedCoherenceService,
)

__all__ = [
    # Models
    "RuntimeIdentity",
    "OrchestrationLineage",
    "ExecutionLineageNode",
    "RuntimeContext",
    "CognitiveMemoryItem",
    "MemoryFragment",
    "ContextSnapshot",
    "SemanticExecutionGraph",
    "SemanticNode",
    "SemanticEdge",
    "AdaptiveProfile",
    "OptimizationMetric",
    "ExecutionTuningHistory",
    "GovernancePolicy",
    "PolicyViolation",
    "ArbitrationRecord",
    "OrchestrationStabilityMetrics",
    # "ExecutionForecast" - moved to forecasting.models
    # "AnomalyDetection" - moved to predictive_observability.models
    # "DistributedContextState" - moved to distributed_runtime.models
    "AgentConsensus",
    "AuthorityDelegation",
    "IdentityScope",
    "LineageEventType",
    "MemoryRetrievalMode",
    "SemanticRelationType",
    "TuningStrategy",
    "PolicySeverity",
    "StabilityStatus",
    "ConsensusState",
    "ExecutionHorizon",
    
    # Services
    "UnifiedIdentityManager",
    "CognitiveContinuityEngine",
    "SemanticCoordinator",
    "AdaptiveRuntimeTuner",
    "GovernanceEnforcer",
    "StabilityPredictor",
    "DistributedCoherenceService",
]