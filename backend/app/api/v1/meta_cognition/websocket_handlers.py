"""
Meta-Cognition WebSocket Handler - Real-time executive intelligence streaming.

Provides:
- Live cognition telemetry
- Orchestration introspection streams
- Semantic consistency visualization
- Adaptive governance monitoring
- Runtime self-awareness analytics
- Distributed cognition visibility
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.domains.meta_cognition import MetaCognitionEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws/meta-cognition", tags=["meta_cognition_websocket"])


class MetaCognitionWebSocketManager:
    """
    WebSocket manager for meta-cognition real-time streaming.
    """
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.cognition_streams: Dict[str, asyncio.Queue] = {}
        self._running = False
        self._broadcast_tasks: Dict[str, asyncio.Task] = {}
    
    async def initialize(self) -> None:
        """Initialize the WebSocket manager"""
        self._running = True
        logger.info("MetaCognitionWebSocketManager initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the WebSocket manager"""
        self._running = False
        for task in self._broadcast_tasks.values():
            task.cancel()
        logger.info("MetaCognitionWebSocketManager shutdown")
    
    async def connect(
        self,
        websocket: WebSocket,
        stream_type: str = "default",
    ) -> str:
        """Connect a WebSocket client"""
        await websocket.accept()
        
        connection_id = str(uuid4())
        
        if stream_type not in self.active_connections:
            self.active_connections[stream_type] = set()
            self.cognition_streams[stream_type] = asyncio.Queue()
            self._broadcast_tasks[stream_type] = asyncio.create_task(
                self._broadcast_loop(stream_type)
            )
        
        self.active_connections[stream_type].add(websocket)
        
        logger.info(f"WebSocket connected: {connection_id} for stream: {stream_type}")
        
        # Send initial state
        await self._send_initial_state(websocket, stream_type)
        
        return connection_id
    
    async def disconnect(
        self,
        websocket: WebSocket,
        stream_type: str = "default",
    ) -> None:
        """Disconnect a WebSocket client"""
        if stream_type in self.active_connections:
            self.active_connections[stream_type].discard(websocket)
            
            if not self.active_connections[stream_type]:
                del self.active_connections[stream_type]
                if stream_type in self.cognition_streams:
                    del self.cognition_streams[stream_type]
                if stream_type in self._broadcast_tasks:
                    self._broadcast_tasks[stream_type].cancel()
                    del self._broadcast_tasks[stream_type]
        
        logger.info(f"WebSocket disconnected for stream: {stream_type}")
    
    async def _send_initial_state(
        self,
        websocket: WebSocket,
        stream_type: str,
    ) -> None:
        """Send initial state to new connection"""
        async with async_session_maker() as db:
            engine = MetaCognitionEngine(db)
            await engine.initialize()
            
            try:
                # Build initial state
                initial_state = {
                    "type": "initial_state",
                    "timestamp": datetime.utcnow().isoformat(),
                    "stream_type": stream_type,
                    "data": {
                        "status": "active",
                        "connection_id": str(uuid4()),
                        "capabilities": [
                            "diagnostics",
                            "introspection",
                            "semantic_audits",
                            "governance",
                            "reconciliation",
                            "forecasts",
                            "anomalies",
                        ],
                    }
                }
                
                await websocket.send_json(initial_state)
                
            except Exception as e:
                logger.error(f"Error sending initial state: {e}")
    
    async def broadcast(
        self,
        stream_type: str,
        message: Dict[str, Any],
    ) -> None:
        """Broadcast a message to all clients of a stream type"""
        if stream_type in self.cognition_streams:
            await self.cognition_streams[stream_type].put(message)
    
    async def _broadcast_loop(self, stream_type: str) -> None:
        """Broadcast loop for a stream type"""
        while self._running:
            try:
                message = await asyncio.wait_for(
                    self.cognition_streams[stream_type].get(),
                    timeout=0.5
                )
                
                disconnected = set()
                
                for websocket in self.active_connections.get(stream_type, set()):
                    try:
                        await websocket.send_json(message)
                    except Exception:
                        disconnected.add(websocket)
                
                # Clean up disconnected clients
                for ws in disconnected:
                    await self.disconnect(ws, stream_type)
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Broadcast error for {stream_type}: {e}")
    
    async def broadcast_diagnostics(
        self,
        diagnostics: Dict[str, Any],
    ) -> None:
        """Broadcast diagnostics update"""
        await self.broadcast("diagnostics", {
            "type": "diagnostics_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": diagnostics,
        })
    
    async def broadcast_introspection(
        self,
        session_id: str,
        phase: str,
        findings: List[Dict[str, Any]],
        confidence: float,
    ) -> None:
        """Broadcast introspection update"""
        await self.broadcast("introspection", {
            "type": "introspection_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "session_id": session_id,
                "phase": phase,
                "findings": findings,
                "confidence": confidence,
            }
        })
    
    async def broadcast_semantic_alert(
        self,
        audit_id: str,
        severity: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Broadcast semantic consistency alert"""
        await self.broadcast("semantic", {
            "type": "semantic_alert",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "audit_id": audit_id,
                "severity": severity,
                "message": message,
                "details": details,
            }
        })
    
    async def broadcast_governance_event(
        self,
        event_type: str,
        profile_id: str,
        details: Dict[str, Any],
    ) -> None:
        """Broadcast governance event"""
        await self.broadcast("governance", {
            "type": "governance_event",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "event_type": event_type,
                "profile_id": profile_id,
                "details": details,
            }
        })
    
    async def broadcast_reconciliation_update(
        self,
        state_id: str,
        status: str,
        metrics: Dict[str, Any],
    ) -> None:
        """Broadcast reconciliation update"""
        await self.broadcast("reconciliation", {
            "type": "reconciliation_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "state_id": state_id,
                "status": status,
                "metrics": metrics,
            }
        })
    
    async def broadcast_forecast(
        self,
        forecast: Dict[str, Any],
    ) -> None:
        """Broadcast forecast update"""
        await self.broadcast("forecasts", {
            "type": "forecast_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": forecast,
        })
    
    async def broadcast_anomaly(
        self,
        anomaly_id: str,
        anomaly_type: str,
        severity: str,
        target_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Broadcast anomaly detection"""
        await self.broadcast("anomalies", {
            "type": "anomaly_detected",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "anomaly_id": anomaly_id,
                "anomaly_type": anomaly_type,
                "severity": severity,
                "target_id": target_id,
                "details": details,
            }
        })


# Global WebSocket manager instance
ws_manager = MetaCognitionWebSocketManager()


@router.websocket("/stream")
async def websocket_meta_cognition(
    websocket: WebSocket,
    stream_type: str = "default",
):
    """
    WebSocket endpoint for meta-cognition real-time streaming.
    
    Connect to receive real-time updates on:
    - Cognition diagnostics
    - Introspection sessions
    - Semantic consistency audits
    - Governance events
    - Reconciliation updates
    - Cognition forecasts
    - Anomaly detections
    """
    connection_id = await ws_manager.connect(websocket, stream_type)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                
                elif message_type == "subscribe":
                    # Handle subscription to specific streams
                    channels = message.get("channels", [])
                    await websocket.send_json({
                        "type": "subscription_confirmed",
                        "channels": channels,
                    })
                
                elif message_type == "request_state":
                    # Send full state
                    async with async_session_maker() as db:
                        engine = MetaCognitionEngine(db)
                        await engine.initialize()
                        
                        await websocket.send_json({
                            "type": "state_response",
                            "timestamp": datetime.utcnow().isoformat(),
                            "data": {
                                "engine_status": "active",
                                "stream_type": stream_type,
                            }
                        })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON message",
                })
    
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, stream_type)
        logger.info(f"WebSocket disconnected: {connection_id}")


@router.websocket("/diagnostics")
async def websocket_diagnostics(websocket: WebSocket):
    """
    WebSocket endpoint specifically for diagnostics streaming.
    """
    connection_id = await ws_manager.connect(websocket, "diagnostics")
    
    try:
        async with async_session_maker() as db:
            engine = MetaCognitionEngine(db)
            await engine.initialize()
            
            # Start diagnostics loop
            while True:
                # Run diagnostics
                diagnostics = await engine.run_cognition_diagnostics(
                    scope="websocket_stream",
                    domain="real_time",
                )
                
                await ws_manager.broadcast_diagnostics({
                    "diagnostic_id": diagnostics.diagnostic_id,
                    "cognition_state": diagnostics.cognition_state,
                    "reasoning_quality": diagnostics.reasoning_quality,
                    "coherence_score": diagnostics.coherence_score,
                    "consistency_score": diagnostics.consistency_score,
                    "adaptation_efficiency": diagnostics.adaptation_efficiency,
                    "distribution_alignment": diagnostics.distribution_alignment,
                    "conflict_rate": diagnostics.conflict_rate,
                    "assessed_at": diagnostics.assessed_at.isoformat(),
                })
                
                # Wait before next update
                await asyncio.sleep(5)
    
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, "diagnostics")


@router.websocket("/introspection")
async def websocket_introspection(websocket: WebSocket):
    """
    WebSocket endpoint for introspection session streaming.
    """
    connection_id = await ws_manager.connect(websocket, "introspection")
    
    try:
        async with async_session_maker() as db:
            engine = MetaCognitionEngine(db)
            await engine.initialize()
            
            # Create an introspection session
            session = await engine.start_introspection_session(
                scope="websocket_stream",
                introspection_type="real_time_monitoring",
            )
            
            # Send session info
            await websocket.send_json({
                "type": "session_started",
                "session_id": session.session_id,
                "timestamp": datetime.utcnow().isoformat(),
            })
            
            # Start session updates
            while True:
                await asyncio.sleep(2)
                
                await ws_manager.broadcast_introspection(
                    session_id=session.session_id,
                    phase=session.phase,
                    findings=session.findings or [],
                    confidence=session.confidence,
                )
    
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, "introspection")


__all__ = [
    "MetaCognitionWebSocketManager",
    "ws_manager",
    "websocket_meta_cognition",
    "websocket_diagnostics",
    "websocket_introspection",
]
