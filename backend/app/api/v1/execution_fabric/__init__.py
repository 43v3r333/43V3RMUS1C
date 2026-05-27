"""
Execution Fabric API - Unified execution fabric endpoints.

Provides:
- Event topology governance
- Distributed runtime propagation
- Cognition fabric
- Self-healing orchestration
- Semantic execution
- Predictive observability
- Real-time WebSocket streaming
"""
from .router import router
from .websocket_handlers import (
    ExecutionFabricStreamHandler,
    ExecutionTelemetryHandler,
    ExecutionFabricWebSocketManager,
    ExecutionStreamType,
    get_execution_fabric_manager,
)

__all__ = [
    "router",
    "ExecutionFabricStreamHandler",
    "ExecutionTelemetryHandler",
    "ExecutionFabricWebSocketManager",
    "ExecutionStreamType",
    "get_execution_fabric_manager",
]