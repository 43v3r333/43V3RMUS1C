"""
Cognitive WebSocket Router - Real-time cognitive telemetry and streaming.

Provides WebSocket channels for:
  - Cognitive reasoning streams
  - Orchestration memory updates
  - Predictive execution streams
  - Agent governance visibility
  - Adaptive optimization telemetry
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class CognitiveChannel(str, Enum):
    """Cognitive WebSocket channels."""

    REASONING = "cognitive.reasoning"
    MEMORY = "cognitive.memory"
    FORECAST = "cognitive.forecast"
    GOVERNANCE = "cognitive.governance"
    FEEDBACK = "cognitive.feedback"
    OPTIMIZATION = "cognitive.optimization"
    AGENT = "cognitive.agent"
    PREDICTION = "cognitive.prediction"


@dataclass
class CognitiveStreamEvent:
    """A cognitive stream event."""

    channel: str
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    source: str = "cognitive_core"


class CognitiveWebSocketRouter:
    """WebSocket router for cognitive telemetry streams.

    Supports subscription to multiple cognitive channels with per-channel
    event filtering and broadcast management.
    """

    def __init__(self) -> None:
        self._connections: Dict[WebSocket, Set[str]] = {}
        self._running = False

    async def connect(self, websocket: WebSocket, channels: List[str]) -> None:
        """Accept a WebSocket connection and subscribe to channels."""
        await websocket.accept()
        subscribed = set(channels) if channels else set(CognitiveChannel)
        self._connections[websocket] = subscribed
        logger.info(f"Cognitive WS: connected, channels={subscribed}")

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        self._connections.pop(websocket, None)

    def is_subscribed(self, websocket: WebSocket, channel: str) -> bool:
        """Check if a connection is subscribed to a channel."""
        return channel in self._connections.get(websocket, set())

    async def broadcast(
        self,
        channel: str,
        event_type: str,
        data: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> int:
        """Broadcast an event to all connections subscribed to a channel."""
        count = 0
        for websocket, channels in list(self._connections.items()):
            if channel in channels:
                try:
                    event = {
                        "channel": channel,
                        "event_type": event_type,
                        "data": data,
                        "timestamp": datetime.utcnow().isoformat(),
                        "correlation_id": correlation_id,
                        "source": "cognitive_core",
                    }
                    await websocket.send_json(event)
                    count += 1
                except Exception:
                    self.disconnect(websocket)
        return count

    # ---- Specific stream methods ----------------------------------------

    async def emit_reasoning(
        self,
        reasoning_type: str,
        context: Dict[str, Any],
        result: Dict[str, Any],
        confidence: float,
    ) -> int:
        """Emit a cognitive reasoning event."""
        return await self.broadcast(
            channel=CognitiveChannel.REASONING,
            event_type=f"reasoning.{reasoning_type}",
            data={
                "reasoning_type": reasoning_type,
                "context": context,
                "result": result,
                "confidence": confidence,
            },
        )

    async def emit_memory_update(
        self,
        memory_kind: str,
        action: str,
        memory_id: str,
        content: Dict[str, Any],
        importance: float,
    ) -> int:
        """Emit an orchestration memory update."""
        return await self.broadcast(
            channel=CognitiveChannel.MEMORY,
            event_type=f"memory.{action}",
            data={
                "memory_kind": memory_kind,
                "memory_id": memory_id,
                "content": content,
                "importance": importance,
            },
        )

    async def emit_forecast(
        self,
        forecast_kind: str,
        subject_key: str,
        predicted_value: float,
        confidence: float,
        horizon: str,
    ) -> int:
        """Emit a new execution forecast."""
        return await self.broadcast(
            channel=CognitiveChannel.FORECAST,
            event_type="forecast.created",
            data={
                "forecast_kind": forecast_kind,
                "subject_key": subject_key,
                "predicted_value": predicted_value,
                "confidence": confidence,
                "horizon": horizon,
            },
        )

    async def emit_governance_event(
        self,
        event_type: str,
        agent_id: str,
        rule_name: Optional[str],
        decision: str,
        reason: str,
    ) -> int:
        """Emit an agent governance event."""
        return await self.broadcast(
            channel=CognitiveChannel.GOVERNANCE,
            event_type=f"governance.{event_type}",
            data={
                "event_type": event_type,
                "agent_id": agent_id,
                "rule_name": rule_name,
                "decision": decision,
                "reason": reason,
            },
        )

    async def emit_feedback(
        self,
        feedback_type: str,
        subject_key: str,
        actual_value: float,
        delta_pct: Optional[float],
        quality_score: Optional[float],
    ) -> int:
        """Emit a feedback signal."""
        return await self.broadcast(
            channel=CognitiveChannel.FEEDBACK,
            event_type="feedback.ingested",
            data={
                "feedback_type": feedback_type,
                "subject_key": subject_key,
                "actual_value": actual_value,
                "delta_pct": delta_pct,
                "quality_score": quality_score,
            },
        )

    async def emit_optimization(
        self,
        optimization_type: str,
        parameter_name: str,
        before_value: float,
        after_value: float,
        improvement_pct: Optional[float],
    ) -> int:
        """Emit an adaptive optimization event."""
        return await self.broadcast(
            channel=CognitiveChannel.OPTIMIZATION,
            event_type="optimization.applied",
            data={
                "optimization_type": optimization_type,
                "parameter_name": parameter_name,
                "before_value": before_value,
                "after_value": after_value,
                "improvement_pct": improvement_pct,
            },
        )

    async def emit_agent_health(
        self,
        agent_id: str,
        agent_kind: str,
        status: str,
        metrics: Dict[str, Any],
    ) -> int:
        """Emit agent health and metrics."""
        return await self.broadcast(
            channel=CognitiveChannel.AGENT,
            event_type="agent.health",
            data={
                "agent_id": agent_id,
                "agent_kind": agent_kind,
                "status": status,
                "metrics": metrics,
            },
        )

    async def emit_prediction(
        self,
        prediction_type: str,
        subject_key: str,
        predicted_value: float,
        confidence: float,
        features: Dict[str, Any],
    ) -> int:
        """Emit a predictive event."""
        return await self.broadcast(
            channel=CognitiveChannel.PREDICTION,
            event_type="prediction.generated",
            data={
                "prediction_type": prediction_type,
                "subject_key": subject_key,
                "predicted_value": predicted_value,
                "confidence": confidence,
                "features": features,
            },
        )

    @property
    def connection_count(self) -> int:
        return len(self._connections)

    @property
    def channel_summary(self) -> Dict[str, int]:
        summary: Dict[str, int] = {}
        for channel in CognitiveChannel:
            count = sum(
                1 for ws, chans in self._connections.items() if channel.value in chans
            )
            if count:
                summary[channel.value] = count
        return summary


# Global router instance
_cognitive_router: Optional[CognitiveWebSocketRouter] = None


def get_cognitive_router() -> CognitiveWebSocketRouter:
    """Get or create the global cognitive WebSocket router."""
    global _cognitive_router
    if _cognitive_router is None:
        _cognitive_router = CognitiveWebSocketRouter()
    return _cognitive_router


# ---------------------------------------------------------------------------
# FastAPI router
# ---------------------------------------------------------------------------

router = APIRouter()


@router.websocket("/ws/cognitive")
async def cognitive_websocket(
    websocket: WebSocket,
    channels: Optional[str] = None,
):
    """WebSocket endpoint for cognitive telemetry streams.

    Query params:
      - channels: comma-separated list of channels (default: all)
    """
    router_instance = get_cognitive_router()

    requested = []
    if channels:
        requested = [ch.strip() for ch in channels.split(",") if ch.strip()]

    await router_instance.connect(websocket, requested)

    try:
        # Send welcome
        await websocket.send_json({
            "event_type": "connected",
            "channels": list(router_instance._connections.get(websocket, set())),
            "timestamp": datetime.utcnow().isoformat(),
            "source": "cognitive_core",
        })

        # Heartbeat loop
        async def heartbeat():
            while True:
                await asyncio.sleep(30)
                try:
                    await websocket.send_json({
                        "event_type": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat(),
                        "source": "cognitive_core",
                    })
                except Exception:
                    break

        heartbeat_task = asyncio.create_task(heartbeat())

        while True:
            # Receive messages (subscribe/unsubscribe)
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                action = msg.get("action")
                if action == "subscribe":
                    target_channels = msg.get("channels", [])
                    if websocket in router_instance._connections:
                        router_instance._connections[websocket].update(target_channels)
                    await websocket.send_json({
                        "event_type": "subscribed",
                        "channels": target_channels,
                    })
                elif action == "unsubscribe":
                    target_channels = msg.get("channels", [])
                    if websocket in router_instance._connections:
                        for ch in target_channels:
                            router_instance._connections[websocket].discard(ch)
                    await websocket.send_json({
                        "event_type": "unsubscribed",
                        "channels": target_channels,
                    })
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        logger.info("Cognitive WS: client disconnected")
    finally:
        heartbeat_task.cancel()
        router_instance.disconnect(websocket)


@router.get("/ws/cognitive/stats")
async def cognitive_stats():
    """Get cognitive WebSocket statistics."""
    router_instance = get_cognitive_router()
    return {
        "connection_count": router_instance.connection_count,
        "channels": router_instance.channel_summary,
        "status": "healthy",
    }