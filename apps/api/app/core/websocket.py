"""
WebSocket infrastructure for real-time communication.
Provides live updates for renders, queues, and worker status.
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis

from app.core.event_bus import Event, EventType, get_event_bus

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections with room-based broadcasting.
    Supports multiple channels for different real-time features.
    """
    
    def __init__(self):
        # Active connections by channel
        self._connections: Dict[str, Set[WebSocket]] = {}
        # User connections by user_id
        self._user_connections: Dict[str, Set[WebSocket]] = {}
        # Redis pubsub for distributed connections
        self._redis_client: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None
        self._listener_task: Optional[asyncio.Task] = None
    
    async def connect(
        self,
        websocket: WebSocket,
        channel: str = "global",
        user_id: Optional[str] = None
    ) -> None:
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Add to channel
        if channel not in self._connections:
            self._connections[channel] = set()
        self._connections[channel].add(websocket)
        
        # Add to user connections if user_id provided
        if user_id:
            if user_id not in self._user_connections:
                self._user_connections[user_id] = set()
            self._user_connections[user_id].add(websocket)
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connected",
            "channel": channel,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
        logger.info(f"WebSocket connected: channel={channel}, user={user_id}")
    
    async def disconnect(
        self,
        websocket: WebSocket,
        channel: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """Remove a WebSocket connection"""
        # Remove from channel
        if channel and channel in self._connections:
            self._connections[channel].discard(websocket)
            if not self._connections[channel]:
                del self._connections[channel]
        
        # Remove from user connections
        if user_id and user_id in self._user_connections:
            self._user_connections[user_id].discard(websocket)
            if not self._user_connections[user_id]:
                del self._user_connections[user_id]
        
        logger.info(f"WebSocket disconnected: channel={channel}, user={user_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket) -> None:
        """Send a message to a single connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
    
    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]) -> None:
        """Broadcast message to all connections in a channel"""
        if channel not in self._connections:
            return
        
        disconnected = []
        for connection in self._connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to channel {channel}: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected
        for conn in disconnected:
            self._connections[channel].discard(conn)
    
    async def broadcast_to_user(self, user_id: str, message: Dict[str, Any]) -> None:
        """Send message to all connections for a specific user"""
        if user_id not in self._user_connections:
            return
        
        for connection in self._user_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to user {user_id}: {e}")
    
    async def broadcast_all(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connections"""
        for channel, connections in self._connections.items():
            await self.broadcast_to_channel(channel, message)
    
    def get_channel_count(self, channel: str) -> int:
        """Get number of connections in a channel"""
        return len(self._connections.get(channel, set()))
    
    def get_total_connections(self) -> int:
        """Get total number of active connections"""
        return sum(len(conns) for conns in self._connections.values())
    
    async def connect_redis(self, redis_url: str) -> None:
        """Connect to Redis for distributed broadcasting"""
        self._redis_client = redis.from_url(redis_url, decode_responses=True)
        self._pubsub = self._redis_client.pubsub()
        await self._pubsub.subscribe("realtime:*")
        self._listener_task = asyncio.create_task(self._listen_redis())
        logger.info(f"WebSocket manager connected to Redis: {redis_url}")
    
    async def _listen_redis(self) -> None:
        """Listen for Redis pub/sub messages"""
        while True:
            try:
                message = await self._pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    data = json.loads(message["data"])
                    channel = message["channel"].replace("realtime:", "")
                    await self.broadcast_to_channel(channel, data)
            except Exception as e:
                logger.error(f"Redis listener error: {e}")
                await asyncio.sleep(1)
    
    async def publish_to_redis(self, channel: str, message: Dict[str, Any]) -> None:
        """Publish message to Redis for distributed broadcasting"""
        if self._redis_client:
            await self._redis_client.publish(f"realtime:{channel}", json.dumps(message))
    
    async def close(self) -> None:
        """Close all connections and Redis"""
        if self._listener_task:
            self._listener_task.cancel()
        
        # Close all connections
        for connections in self._connections.values():
            for conn in connections:
                try:
                    await conn.close()
                except Exception:
                    pass
        
        if self._pubsub:
            await self._pubsub.close()
        if self._redis_client:
            await self._redis_client.close()


# Global connection manager
_connection_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """Get or create global connection manager"""
    global _connection_manager
    
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    
    return _connection_manager


class WebSocketManager:
    """
    High-level WebSocket management with event integration.
    Handles protocol, authentication, and event routing.
    """
    
    def __init__(self):
        self.manager = get_connection_manager()
        self._event_bus = get_event_bus()
    
    async def handle_connect(
        self,
        websocket: WebSocket,
        token: Optional[str] = None,
        channels: Optional[List[str]] = None
    ) -> bool:
        """
        Handle new WebSocket connection.
        Validates token and subscribes to channels.
        """
        user_id = None
        
        # Validate token if provided
        if token:
            try:
                from app.core.security import decode_token
                payload = decode_token(token)
                user_id = payload.get("sub")
            except Exception as e:
                logger.warning(f"Invalid WebSocket token: {e}")
                await websocket.close(code=4001)
                return False
        
        # Join default channel
        default_channel = "global"
        await self.manager.connect(websocket, default_channel, user_id)
        
        # Join additional channels
        if channels:
            for channel in channels:
                await self.manager.connect(websocket, channel, user_id)
        
        return True
    
    async def handle_message(self, websocket: WebSocket, message: Dict[str, Any]) -> None:
        """Handle incoming WebSocket message"""
        msg_type = message.get("type")
        
        if msg_type == "subscribe":
            channel = message.get("channel")
            if channel:
                await self.manager.connect(websocket, channel)
        
        elif msg_type == "unsubscribe":
            channel = message.get("channel")
            if channel:
                await self.manager.disconnect(websocket, channel)
        
        elif msg_type == "ping":
            await self.manager.send_personal_message({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            }, websocket)
        
        elif msg_type == "broadcast":
            channel = message.get("channel", "global")
            data = message.get("data", {})
            await self.manager.broadcast_to_channel(channel, data)
    
    async def emit_render_progress(
        self,
        job_id: str,
        progress: float,
        status: str
    ) -> None:
        """Emit render progress update"""
        message = {
            "type": "render.progress",
            "job_id": job_id,
            "progress": progress,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.broadcast_to_channel("renders", message)
        await self.manager.publish_to_redis("renders", message)
    
    async def emit_queue_update(self, stats: Dict[str, Any]) -> None:
        """Emit queue statistics update"""
        message = {
            "type": "queue.stats",
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.broadcast_to_channel("queue", message)
        await self.manager.publish_to_redis("queue", message)
    
    async def emit_worker_status(
        self,
        worker_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Emit worker status update"""
        message = {
            "type": "worker.status",
            "worker_id": worker_id,
            "status": status,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.broadcast_to_channel("workers", message)
        await self.manager.publish_to_redis("workers", message)
    
    async def emit_upload_progress(
        self,
        upload_id: str,
        filename: str,
        progress: float
    ) -> None:
        """Emit upload progress update"""
        message = {
            "type": "upload.progress",
            "upload_id": upload_id,
            "filename": filename,
            "progress": progress,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.broadcast_to_channel("uploads", message)
    
    async def emit_media_event(
        self,
        event_type: str,
        asset_id: str,
        data: Dict[str, Any]
    ) -> None:
        """Emit media lifecycle event"""
        message = {
            "type": f"media.{event_type}",
            "asset_id": asset_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.broadcast_to_channel("media", message)


# Event handler for real-time updates
class RealtimeEventHandler:
    """Handles domain events and broadcasts to WebSocket clients"""
    
    @property
    def event_types(self) -> Set[EventType]:
        return {
            EventType.RENDER_PROGRESS,
            EventType.RENDER_STARTED,
            EventType.RENDER_COMPLETED,
            EventType.RENDER_FAILED,
            EventType.QUEUE_STATS,
            EventType.WORKER_STATUS,
            EventType.MEDIA_PROCESSED,
            EventType.MEDIA_FAILED,
            EventType.AUDIO_ANALYZED,
            EventType.TRANSCODE_PROGRESS,
            EventType.TRANSCODE_COMPLETED,
        }
    
    async def handle(self, event: Event) -> None:
        """Handle domain event and broadcast to appropriate channel"""
        manager = get_connection_manager()
        channel_map = {
            EventType.RENDER_PROGRESS: "renders",
            EventType.RENDER_STARTED: "renders",
            EventType.RENDER_COMPLETED: "renders",
            EventType.RENDER_FAILED: "renders",
            EventType.QUEUE_STATS: "queue",
            EventType.WORKER_STATUS: "workers",
            EventType.MEDIA_PROCESSED: "media",
            EventType.MEDIA_FAILED: "media",
            EventType.AUDIO_ANALYZED: "media",
            EventType.TRANSCODE_PROGRESS: "renders",
            EventType.TRANSCODE_COMPLETED: "renders",
        }
        
        channel = channel_map.get(event.type, "global")
        message = {
            "type": event.type.value,
            "event_id": event.id,
            "data": event.data,
            "timestamp": event.timestamp.isoformat()
        }
        
        await manager.broadcast_to_channel(channel, message)
        await manager.publish_to_redis(channel, message)


# WebSocket endpoint handler
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = None,
    channels: Optional[str] = None
) -> None:
    """
    Main WebSocket endpoint handler.
    Parses query parameters and manages connection lifecycle.
    """
    manager = get_connection_manager()
    ws_manager = WebSocketManager()
    
    # Parse channels from query param
    channel_list = channels.split(",") if channels else None
    
    # Handle connection
    if not await ws_manager.handle_connect(websocket, token, channel_list):
        return
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            await ws_manager.handle_message(websocket, data)
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Clean up connection
        await manager.disconnect(websocket)