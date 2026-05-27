"""
Execution Fabric WebSocket Handlers - Real-time execution visibility.

Provides:
- Live orchestration lineage streams
- Semantic execution telemetry
- Distributed cognition visualization
- Runtime stabilization monitoring
- Adaptive orchestration analytics
- Execution topology visibility
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Set
from uuid import UUID
from datetime import datetime
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect

from ..websocket import MessageType

logger = logging.getLogger(__name__)


class ExecutionStreamType(str, Enum):
    """Execution stream types for real-time visibility"""
    LINEAGE_UPDATE = "lineage.update"
    TOPOLOGY_CHANGE = "topology.change"
    COGNITION_PULSE = "cognition.pulse"
    STABILITY_METRIC = "stability.metric"
    SEMANTIC_ANALYSIS = "semantic.analysis"
    ANOMALY_DETECTED = "anomaly.detected"
    RECOVERY_ACTION = "recovery.action"
    FORECAST_UPDATE = "forecast.update"


class ExecutionFabricStreamHandler:
    """
    Handles real-time execution fabric streams via WebSocket.
    Provides live visibility into distributed orchestration.
    """
    
    def __init__(self, websocket: WebSocket, client_id: str):
        self.websocket = websocket
        self.client_id = client_id
        self.subscriptions: Set[str] = set()
        self.stream_handlers: Dict[str, asyncio.Task] = {}
        self._running = False
    
    async def start_streaming(self) -> None:
        """Start streaming execution fabric data"""
        self._running = True
        
        # Start various stream handlers
        self.stream_handlers["lineage"] = asyncio.create_task(
            self._lineage_stream_loop()
        )
        self.stream_handlers["topology"] = asyncio.create_task(
            self._topology_stream_loop()
        )
        self.stream_handlers["stability"] = asyncio.create_task(
            self._stability_stream_loop()
        )
        self.stream_handlers["cognition"] = asyncio.create_task(
            self._cognition_stream_loop()
        )
        
        logger.info(f"Execution fabric streaming started for client {self.client_id}")
    
    async def stop_streaming(self) -> None:
        """Stop all streaming handlers"""
        self._running = False
        
        for task in self.stream_handlers.values():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.stream_handlers.clear()
        logger.info(f"Execution fabric streaming stopped for client {self.client_id}")
    
    async def subscribe(self, stream_type: str) -> None:
        """Subscribe to a stream type"""
        self.subscriptions.add(stream_type)
    
    async def unsubscribe(self, stream_type: str) -> None:
        """Unsubscribe from a stream type"""
        self.subscriptions.discard(stream_type)
    
    async def send_update(self, stream_type: str, data: Dict[str, Any]) -> None:
        """Send update to client"""
        if stream_type not in self.subscriptions:
            return
        
        message = {
            "type": stream_type,
            "payload": data,
            "timestamp": datetime.utcnow().isoformat(),
            "client_id": self.client_id,
        }
        
        try:
            await self.websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send update: {e}")
    
    async def _lineage_stream_loop(self) -> None:
        """Stream lineage updates"""
        while self._running:
            try:
                if ExecutionStreamType.LINEAGE_UPDATE.value in self.subscriptions:
                    # Generate lineage update
                    update = self._generate_lineage_update()
                    await self.send_update(
                        ExecutionStreamType.LINEAGE_UPDATE.value,
                        update
                    )
                
                await asyncio.sleep(2)  # Update every 2 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Lineage stream error: {e}")
                await asyncio.sleep(1)
    
    async def _topology_stream_loop(self) -> None:
        """Stream topology changes"""
        while self._running:
            try:
                if ExecutionStreamType.TOPOLOGY_CHANGE.value in self.subscriptions:
                    update = self._generate_topology_change()
                    await self.send_update(
                        ExecutionStreamType.TOPOLOGY_CHANGE.value,
                        update
                    )
                
                await asyncio.sleep(3)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Topology stream error: {e}")
                await asyncio.sleep(1)
    
    async def _stability_stream_loop(self) -> None:
        """Stream stability metrics"""
        while self._running:
            try:
                if ExecutionStreamType.STABILITY_METRIC.value in self.subscriptions:
                    update = self._generate_stability_update()
                    await self.send_update(
                        ExecutionStreamType.STABILITY_METRIC.value,
                        update
                    )
                
                await asyncio.sleep(5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Stability stream error: {e}")
                await asyncio.sleep(1)
    
    async def _cognition_stream_loop(self) -> None:
        """Stream cognition pulses"""
        while self._running:
            try:
                if ExecutionStreamType.COGNITION_PULSE.value in self.subscriptions:
                    update = self._generate_cognition_pulse()
                    await self.send_update(
                        ExecutionStreamType.COGNITION_PULSE.value,
                        update
                    )
                
                await asyncio.sleep(4)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cognition stream error: {e}")
                await asyncio.sleep(1)
    
    def _generate_lineage_update(self) -> Dict[str, Any]:
        """Generate lineage update"""
        import random
        return {
            "graph_id": f"graph-{UUID().hex[:8]}",
            "nodes": {
                "total": random.randint(50, 200),
                "active": random.randint(10, 50),
                "completed": random.randint(30, 150),
            },
            "edges": {
                "total": random.randint(100, 500),
                "active": random.randint(20, 80),
            },
            "latest_node": {
                "id": f"node-{UUID().hex[:8]}",
                "type": random.choice(["task", "workflow", "service"]),
                "status": random.choice(["running", "completed", "pending"]),
            },
            "throughput": {
                "nodes_per_second": round(random.uniform(0.5, 5.0), 2),
                "avg_completion_time_ms": round(random.uniform(50, 500), 1),
            },
        }
    
    def _generate_topology_change(self) -> Dict[str, Any]:
        """Generate topology change"""
        import random
        return {
            "change_type": random.choice(["node_joined", "node_left", "edge_created", "edge_removed"]),
            "node": {
                "id": f"node-{UUID().hex[:8]}",
                "type": random.choice(["service", "worker", "orchestrator"]),
                "region": random.choice(["us-east-1", "us-west-2", "eu-west-1"]),
            },
            "topology_metrics": {
                "total_nodes": random.randint(10, 100),
                "total_edges": random.randint(50, 500),
                "avg_connectivity": round(random.uniform(0.3, 0.9), 2),
            },
        }
    
    def _generate_stability_update(self) -> Dict[str, Any]:
        """Generate stability update"""
        import random
        return {
            "overall_health": round(random.uniform(0.7, 1.0), 3),
            "components": [
                {
                    "id": f"comp-{i}",
                    "name": f"Component-{i}",
                    "health": round(random.uniform(0.6, 1.0), 3),
                    "status": random.choice(["healthy", "degraded", "recovering"]),
                }
                for i in range(5)
            ],
            "alerts": random.randint(0, 3),
            "recoveries_in_progress": random.randint(0, 2),
        }
    
    def _generate_cognition_pulse(self) -> Dict[str, Any]:
        """Generate cognition pulse"""
        import random
        return {
            "pulse_type": random.choice(["memory_access", "insight_generated", "pattern_recognized"]),
            "cognitive_state": {
                "active_memories": random.randint(50, 200),
                "pattern_matches": random.randint(10, 50),
                "insights_generated": random.randint(5, 20),
            },
            "confidence": round(random.uniform(0.6, 0.95), 2),
        }


class ExecutionTelemetryHandler:
    """Handles execution telemetry streaming"""
    
    def __init__(self, websocket: WebSocket, client_id: str):
        self.websocket = websocket
        self.client_id = client_id
        self._running = False
    
    async def start_telemetry_stream(self, streams: List[str]) -> None:
        """Start telemetry streaming for specified streams"""
        self._running = True
        
        tasks = []
        for stream in streams:
            task = asyncio.create_task(self._stream_telemetry(stream))
            tasks.append(task)
        
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass
    
    async def stop_telemetry_stream(self) -> None:
        """Stop telemetry streaming"""
        self._running = False
    
    async def _stream_telemetry(self, stream_type: str) -> None:
        """Stream telemetry for specific type"""
        while self._running:
            try:
                import random
                from datetime import datetime
                
                telemetry_data = {
                    "stream_type": stream_type,
                    "data": {
                        "metrics": [
                            {
                                "name": "latency",
                                "value": round(random.uniform(10, 200), 2),
                                "unit": "ms",
                            },
                            {
                                "name": "throughput",
                                "value": round(random.uniform(100, 1000), 0),
                                "unit": "ops/s",
                            },
                            {
                                "name": "error_rate",
                                "value": round(random.uniform(0, 0.05), 4),
                                "unit": "%",
                            },
                        ],
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                }
                
                await self.websocket.send_json(telemetry_data)
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Telemetry stream error: {e}")
                await asyncio.sleep(1)


class ExecutionFabricWebSocketManager:
    """Manages WebSocket connections for execution fabric"""
    
    def __init__(self):
        self._connections: Dict[str, ExecutionFabricStreamHandler] = {}
        self._telemetry_handlers: Dict[str, ExecutionTelemetryHandler] = {}
        self._redis_client = None
    
    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
    ) -> ExecutionFabricStreamHandler:
        """Connect new client"""
        await websocket.accept()
        
        handler = ExecutionFabricStreamHandler(websocket, client_id)
        self._connections[client_id] = handler
        
        await handler.start_streaming()
        
        logger.info(f"Execution fabric client connected: {client_id}")
        return handler
    
    async def disconnect(self, client_id: str) -> None:
        """Disconnect client"""
        if client_id in self._connections:
            handler = self._connections[client_id]
            await handler.stop_streaming()
            del self._connections[client_id]
        
        if client_id in self._telemetry_handlers:
            handler = self._telemetry_handlers[client_id]
            await handler.stop_telemetry_stream()
            del self._telemetry_handlers[client_id]
        
        logger.info(f"Execution fabric client disconnected: {client_id}")
    
    async def handle_message(
        self,
        client_id: str,
        message: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Handle incoming message"""
        if client_id not in self._connections:
            return None
        
        handler = self._connections[client_id]
        message_type = message.get("type")
        payload = message.get("payload", {})
        
        if message_type == "subscribe":
            stream_type = payload.get("stream_type")
            if stream_type:
                await handler.subscribe(stream_type)
                return {"status": "subscribed", "stream_type": stream_type}
        
        elif message_type == "unsubscribe":
            stream_type = payload.get("stream_type")
            if stream_type:
                await handler.unsubscribe(stream_type)
                return {"status": "unsubscribed", "stream_type": stream_type}
        
        elif message_type == "start_telemetry":
            streams = payload.get("streams", [])
            if client_id not in self._telemetry_handlers:
                self._telemetry_handlers[client_id] = ExecutionTelemetryHandler(
                    handler.websocket,
                    client_id
                )
            await self._telemetry_handlers[client_id].start_telemetry_stream(streams)
            return {"status": "telemetry_started", "streams": streams}
        
        elif message_type == "stop_telemetry":
            if client_id in self._telemetry_handlers:
                await self._telemetry_handlers[client_id].stop_telemetry_stream()
            return {"status": "telemetry_stopped"}
        
        elif message_type == "request_snapshot":
            snapshot = self._generate_snapshot()
            await handler.websocket.send_json({
                "type": "snapshot",
                "payload": snapshot,
                "timestamp": datetime.utcnow().isoformat(),
            })
            return {"status": "snapshot_sent"}
        
        return None
    
    def _generate_snapshot(self) -> Dict[str, Any]:
        """Generate current execution fabric snapshot"""
        import random
        return {
            "execution_state": {
                "active_graphs": random.randint(5, 20),
                "running_nodes": random.randint(50, 200),
                "completed_nodes": random.randint(500, 2000),
                "failed_nodes": random.randint(0, 10),
            },
            "topology_state": {
                "total_nodes": random.randint(50, 200),
                "total_edges": random.randint(200, 1000),
                "healthy_components": random.randint(80, 100),
            },
            "cognition_state": {
                "memory_entries": random.randint(100, 500),
                "active_patterns": random.randint(20, 100),
                "insights_generated": random.randint(10, 50),
            },
            "stability_state": {
                "overall_health": round(random.uniform(0.8, 1.0), 3),
                "pending_recoveries": random.randint(0, 5),
                "critical_alerts": random.randint(0, 2),
            },
        }
    
    async def broadcast_to_all(
        self,
        stream_type: str,
        data: Dict[str, Any],
    ) -> int:
        """Broadcast message to all connected clients"""
        count = 0
        for client_id, handler in self._connections.items():
            if stream_type in handler.subscriptions:
                await handler.send_update(stream_type, data)
                count += 1
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": len(self._connections),
            "active_telemetry_streams": len(self._telemetry_handlers),
            "total_subscriptions": sum(
                len(h.subscriptions) for h in self._connections.values()
            ),
        }


# Global manager instance
_manager: Optional[ExecutionFabricWebSocketManager] = None


def get_execution_fabric_manager() -> ExecutionFabricWebSocketManager:
    """Get or create global execution fabric manager"""
    global _manager
    if _manager is None:
        _manager = ExecutionFabricWebSocketManager()
    return _manager