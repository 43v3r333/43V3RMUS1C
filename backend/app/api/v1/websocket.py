"""
WebSocket Gateway - Real-time communication infrastructure
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Set
from uuid import UUID
from datetime import datetime
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types"""
    # Connection
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    HEARTBEAT = "heartbeat"
    
    # Events
    EVENT_SUBSCRIBE = "subscribe"
    EVENT_UNSUBSCRIBE = "unsubscribe"
    
    # Render
    RENDER_PROGRESS = "render.progress"
    RENDER_COMPLETED = "render.completed"
    RENDER_FAILED = "render.failed"
    
    # Worker
    WORKER_STATUS = "worker.status"
    WORKER_METRICS = "worker.metrics"
    
    # Queue
    QUEUE_UPDATE = "queue.update"
    JOB_QUEUED = "job.queued"
    JOB_STARTED = "job.started"
    
    # Upload
    UPLOAD_PROGRESS = "upload.progress"
    UPLOAD_COMPLETED = "upload.completed"
    
    # General
    NOTIFICATION = "notification"
    ERROR = "error"


class ConnectionState:
    """WebSocket connection state"""
    
    def __init__(self, websocket: WebSocket, client_id: str):
        self.websocket = websocket
        self.client_id = client_id
        self.user_id: Optional[str] = None
        self.subscriptions: Set[str] = set()
        self.connected_at: datetime = datetime.utcnow()
        self.last_heartbeat: datetime = datetime.utcnow()
        self.metadata: Dict[str, Any] = {}
    
    @property
    def is_authenticated(self) -> bool:
        return self.user_id is not None
    
    async def send_json(self, data: Dict[str, Any]) -> bool:
        """Send JSON message"""
        try:
            await self.websocket.send_json(data)
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    async def send_text(self, message: str) -> bool:
        """Send text message"""
        try:
            await self.websocket.send_text(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False


class WebSocketGateway:
    """
    Production-grade WebSocket gateway for real-time communication.
    Handles connection management, event streaming, and pub/sub integration.
    """
    
    def __init__(
        self,
        redis_url: str,
        heartbeat_interval: int = 30,
        max_connections: int = 10000,
    ):
        self.redis_url = redis_url
        self.heartbeat_interval = heartbeat_interval
        self.max_connections = max_connections
        
        self._redis: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None
        self._connections: Dict[str, ConnectionState] = {}
        self._client_channels: Dict[str, List[str]] = {}
        self._running = False
        self._listener_task: Optional[asyncio.Task] = None
    
    async def connect(self) -> None:
        """Initialize Redis connection"""
        self._redis = redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        await self._redis.ping()
        logger.info("WebSocket gateway connected to Redis")
    
    async def disconnect(self) -> None:
        """Close connections"""
        self._running = False
        
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        
        for client_id in list(self._connections.keys()):
            await self.disconnect_client(client_id)
        
        if self._pubsub:
            await self._pubsub.close()
        if self._redis:
            await self._redis.close()
        
        logger.info("WebSocket gateway disconnected")
    
    async def handle_connection(self, websocket: WebSocket) -> str:
        """Handle new WebSocket connection"""
        client_id = str(UUID())
        
        # Check max connections
        if len(self._connections) >= self.max_connections:
            await websocket.close(code=1013, reason="Server at capacity")
            return None
        
        await websocket.accept()
        
        state = ConnectionState(websocket, client_id)
        self._connections[client_id] = state
        self._client_channels[client_id] = []
        
        logger.info(f"Client connected: {client_id}")
        
        return client_id
    
    async def disconnect_client(self, client_id: str) -> None:
        """Disconnect a client"""
        if client_id in self._connections:
            state = self._connections[client_id]
            
            # Unsubscribe from all channels
            for channel in self._client_channels.get(client_id, []):
                await self._unsubscribe_from_channel(client_id, channel)
            
            try:
                await state.websocket.close()
            except Exception:
                pass
            
            del self._connections[client_id]
            del self._client_channels[client_id]
            
            logger.info(f"Client disconnected: {client_id}")
    
    async def authenticate(
        self,
        client_id: str,
        user_id: str,
        token: Optional[str] = None,
    ) -> bool:
        """Authenticate a client"""
        if client_id not in self._connections:
            return False
        
        state = self._connections[client_id]
        state.user_id = user_id
        
        await self._publish_to_client(
            client_id,
            MessageType.CONNECT,
            {"status": "authenticated", "user_id": user_id}
        )
        
        return True
    
    async def subscribe_to_channel(
        self,
        client_id: str,
        channel: str,
    ) -> bool:
        """Subscribe client to a channel"""
        if client_id not in self._connections:
            return False
        
        state = self._connections[client_id]
        
        # Add to subscriptions
        state.subscriptions.add(channel)
        
        if channel not in self._client_channels[client_id]:
            self._client_channels[client_id].append(channel)
        
        # Subscribe to Redis channel if not already
        if self._pubsub:
            await self._pubsub.subscribe(channel)
        
        return True
    
    async def _subscribe_to_channel(self, channel: str) -> None:
        """Subscribe to a Redis channel"""
        if not self._pubsub:
            return
        
        try:
            await self._pubsub.subscribe(channel)
        except Exception as e:
            logger.error(f"Failed to subscribe to {channel}: {e}")
    
    async def _unsubscribe_from_channel(
        self,
        client_id: str,
        channel: str,
    ) -> None:
        """Unsubscribe from a channel"""
        if client_id in self._connections:
            state = self._connections[client_id]
            state.subscriptions.discard(channel)
        
        if channel in self._client_channels.get(client_id, []):
            self._client_channels[client_id].remove(channel)
    
    async def handle_message(
        self,
        client_id: str,
        message: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Handle incoming message from client"""
        if client_id not in self._connections:
            return None
        
        message_type = message.get("type")
        payload = message.get("payload", {})
        
        if message_type == MessageType.HEARTBEAT.value:
            return await self._handle_heartbeat(client_id)
        
        elif message_type == MessageType.EVENT_SUBSCRIBE.value:
            channel = payload.get("channel")
            if channel:
                await self.subscribe_to_channel(client_id, channel)
            return {"type": "subscribed", "channel": channel}
        
        elif message_type == MessageType.EVENT_UNSUBSCRIBE.value:
            channel = payload.get("channel")
            if channel:
                await self._unsubscribe_from_channel(client_id, channel)
            return {"type": "unsubscribed", "channel": channel}
        
        return None
    
    async def _handle_heartbeat(self, client_id: str) -> Dict[str, Any]:
        """Handle heartbeat"""
        if client_id in self._connections:
            state = self._connections[client_id]
            state.last_heartbeat = datetime.utcnow()
        
        return {"type": "heartbeat_ack"}
    
    async def broadcast(
        self,
        channel: str,
        message_type: str,
        payload: Dict[str, Any],
    ) -> int:
        """Broadcast message to all subscribers of a channel"""
        message = {
            "type": message_type,
            "channel": channel,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        count = 0
        for client_id, channels in self._client_channels.items():
            if channel in channels:
                sent = await self._publish_to_client(client_id, message_type, payload)
                if sent:
                    count += 1
        
        # Also publish to Redis for distributed broadcasting
        if self._redis:
            await self._redis.publish(channel, json.dumps(message))
        
        return count
    
    async def _publish_to_client(
        self,
        client_id: str,
        message_type: str,
        payload: Dict[str, Any],
    ) -> bool:
        """Publish message to specific client"""
        if client_id not in self._connections:
            return False
        
        state = self._connections[client_id]
        message = {
            "type": message_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        return await state.send_json(message)
    
    # ==================== Event Streaming ====================
    
    async def start_event_listener(self) -> None:
        """Start listening for Redis pub/sub events"""
        if not self._redis:
            await self.connect()
        
        self._pubsub = self._redis.pubsub()
        self._running = True
        self._listener_task = asyncio.create_task(self._event_listener_loop())
        logger.info("Event listener started")
    
    async def _event_listener_loop(self) -> None:
        """Main listener loop for Redis pub/sub"""
        while self._running:
            try:
                message = await self._pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0,
                )
                if message:
                    await self._process_redis_message(message)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event listener error: {e}")
                await asyncio.sleep(1)
    
    async def _process_redis_message(self, message: Dict[str, Any]) -> None:
        """Process Redis pub/sub message"""
        try:
            channel = message["channel"]
            data = json.loads(message["data"])
            
            # Broadcast to subscribed clients
            await self.broadcast(channel, data.get("type", "event"), data)
            
        except Exception as e:
            logger.error(f"Error processing Redis message: {e}")
    
    # ==================== Convenience Methods ====================
    
    async def emit_render_progress(
        self,
        job_id: str,
        progress: float,
        current_frame: int,
        total_frames: int,
    ) -> int:
        """Emit render progress event"""
        payload = {
            "job_id": job_id,
            "progress": progress,
            "current_frame": current_frame,
            "total_frames": total_frames,
        }
        
        return await self.broadcast(
            f"render:{job_id}",
            MessageType.RENDER_PROGRESS.value,
            payload
        )
    
    async def emit_worker_status(
        self,
        worker_id: str,
        status: str,
        current_jobs: List[str],
    ) -> int:
        """Emit worker status event"""
        payload = {
            "worker_id": worker_id,
            "status": status,
            "current_jobs": current_jobs,
        }
        
        return await self.broadcast(
            "workers",
            MessageType.WORKER_STATUS.value,
            payload
        )
    
    async def emit_worker_metrics(
        self,
        worker_id: str,
        metrics: Dict[str, Any],
    ) -> int:
        """Emit worker metrics event"""
        payload = {
            "worker_id": worker_id,
            "metrics": metrics,
        }
        
        return await self.broadcast(
            "workers",
            MessageType.WORKER_METRICS.value,
            payload
        )
    
    async def emit_queue_update(
        self,
        queue_stats: Dict[str, Any],
    ) -> int:
        """Emit queue update event"""
        return await self.broadcast(
            "queue",
            MessageType.QUEUE_UPDATE.value,
            queue_stats
        )
    
    async def emit_upload_progress(
        self,
        upload_id: str,
        progress: float,
        bytes_uploaded: int,
        total_bytes: int,
    ) -> int:
        """Emit upload progress event"""
        payload = {
            "upload_id": upload_id,
            "progress": progress,
            "bytes_uploaded": bytes_uploaded,
            "total_bytes": total_bytes,
        }
        
        return await self.broadcast(
            f"upload:{upload_id}",
            MessageType.UPLOAD_PROGRESS.value,
            payload
        )
    
    async def emit_notification(
        self,
        client_id: str,
        title: str,
        message: str,
        notification_type: str = "info",
    ) -> bool:
        """Send notification to specific client"""
        payload = {
            "title": title,
            "message": message,
            "type": notification_type,
        }
        
        return await self._publish_to_client(
            client_id,
            MessageType.NOTIFICATION.value,
            payload
        )
    
    # ==================== Health & Stats ====================
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        authenticated = sum(
            1 for c in self._connections.values() if c.is_authenticated
        )
        
        subscriptions_by_channel: Dict[str, int] = {}
        for client_id, channels in self._client_channels.items():
            for channel in channels:
                subscriptions_by_channel[channel] = subscriptions_by_channel.get(channel, 0) + 1
        
        return {
            "total_connections": len(self._connections),
            "authenticated_connections": authenticated,
            "total_subscriptions": sum(len(c) for c in self._client_channels.values()),
            "subscriptions_by_channel": subscriptions_by_channel,
            "active_channels": len(subscriptions_by_channel),
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check"""
        redis_ok = False
        if self._redis:
            try:
                await self._redis.ping()
                redis_ok = True
            except Exception:
                pass
        
        return {
            "status": "healthy" if redis_ok else "degraded",
            "redis_connected": redis_ok,
            "connections": len(self._connections),
            "max_connections": self.max_connections,
            "listener_running": self._running if self._listener_task else False,
        }


# Global gateway instance
_gateway: Optional[WebSocketGateway] = None


def get_gateway() -> WebSocketGateway:
    """Get or create global gateway"""
    global _gateway
    if _gateway is None:
        from ...core.config import settings
        _gateway = WebSocketGateway(
            redis_url=settings.redis_url,
            heartbeat_interval=30,
        )
    return _gateway