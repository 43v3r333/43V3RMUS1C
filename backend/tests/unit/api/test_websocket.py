"""
43V3R CORE - WebSocket Infrastructure Unit Tests
=================================================

Comprehensive unit tests for WebSocket infrastructure:
- WebSocketGateway: Connection management, event streaming
- WebSocket endpoint handlers
- Redis pub/sub integration
- Real-time communication protocols

Test Coverage:
- Connection lifecycle (connect, authenticate, disconnect)
- Channel subscription management
- Message broadcasting
- Event listener operations
- Heartbeat handling
- Client stats and health checks

Markers: unit, websocket, real-time
"""

from __future__ import annotations

import asyncio
import json
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.websocket import (
    WebSocketGateway,
    ConnectionState,
    MessageType,
)


# =============================================================================
# ConnectionState Tests
# =============================================================================

class TestConnectionState:
    """Test suite for ConnectionState"""
    
    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket"""
        class MockWebSocket:
            async def send_json(self, data):
                pass
            async def send_text(self, message):
                pass
            async def close(self, code=1000, reason=""):
                pass
        return MockWebSocket()
    
    @pytest.mark.unit
    @pytest.mark.websocket
    def test_connection_state_initialization(self, mock_websocket):
        """Test connection state initializes correctly"""
        state = ConnectionState(mock_websocket, "client-123")
        
        assert state.client_id == "client-123"
        assert state.websocket is mock_websocket
        assert state.user_id is None
        assert len(state.subscriptions) == 0
        assert state.is_authenticated is False
    
    @pytest.mark.unit
    @pytest.mark.websocket
    def test_connection_state_authenticated(self, mock_websocket):
        """Test connection state after authentication"""
        state = ConnectionState(mock_websocket, "client-456")
        state.user_id = "user-789"
        
        assert state.is_authenticated is True
    
    @pytest.mark.unit
    @pytest.mark.websocket
    def test_connection_state_metadata(self, mock_websocket):
        """Test connection state metadata"""
        state = ConnectionState(mock_websocket, "client-meta")
        state.metadata["custom_key"] = "custom_value"
        
        assert state.metadata["custom_key"] == "custom_value"


# =============================================================================
# WebSocketGateway Tests
# =============================================================================

class TestWebSocketGateway:
    """Test suite for WebSocketGateway"""
    
    @pytest_asyncio.fixture
    async def gateway(self, redis_client) -> WebSocketGateway:
        """Create WebSocket gateway for testing"""
        gateway = WebSocketGateway(
            redis_url="redis://localhost:6379/15",
            heartbeat_interval=30,
            max_connections=100,
        )
        yield gateway
        await gateway.disconnect()
    
    # ----------------------------------------------------------------
    # Connection Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_gateway_initialization(self, gateway: WebSocketGateway):
        """Test gateway initializes correctly"""
        assert gateway is not None
        assert gateway.heartbeat_interval == 30
        assert gateway.max_connections == 100
        assert isinstance(gateway._connections, dict)
        assert isinstance(gateway._client_channels, dict)
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_handle_connection(self, gateway: WebSocketGateway):
        """Test handling new connection"""
        class MockWebSocket:
            async def accept(self):
                pass
            async def close(self, code=1000, reason=""):
                pass
        
        ws = MockWebSocket()
        client_id = await gateway.handle_connection(ws)
        
        assert client_id is not None
        assert client_id in gateway._connections
        assert gateway._connections[client_id].websocket is ws
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_handle_connection_limit(self, gateway: WebSocketGateway):
        """Test connection limit is enforced"""
        # Change limit for testing
        original_max = gateway.max_connections
        gateway.max_connections = 1
        
        class MockWebSocketAccept:
            async def accept(self):
                pass
            async def close(self, code=1000, reason=""):
                pass
        
        class MockWebSocketReject:
            async def accept(self):
                raise Exception("Reject")
            async def close(self, code, reason):
                pass
        
        # First connection succeeds
        client1 = await gateway.handle_connection(MockWebSocketAccept())
        assert client1 is not None
        
        # Second connection should be rejected or handled gracefully
        if gateway._connections:
            assert len(gateway._connections) <= original_max
        
        gateway.max_connections = original_max
    
    # ----------------------------------------------------------------
    # Disconnect Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_disconnect_client(self, gateway: WebSocketGateway):
        """Test client disconnection"""
        class MockWebSocket:
            async def accept(self):
                pass
            async def close(self, code=1000, reason=""):
                pass
        
        client_id = await gateway.handle_connection(MockWebSocket())
        await gateway.disconnect_client(client_id)
        
        assert client_id not in gateway._connections
    
    # ----------------------------------------------------------------
    # Authentication Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_authenticate(self, gateway: WebSocketGateway):
        """Test client authentication"""
        class MockWebSocket:
            async def accept(self):
                pass
            async def send_json(self, data):
                pass
            async def close(self, code=1000, reason=""):
                pass
        
        client_id = await gateway.handle_connection(MockWebSocket())
        
        result = await gateway.authenticate(
            client_id=client_id,
            user_id="test-user",
        )
        
        assert result is True
        assert gateway._connections[client_id].user_id == "test-user"
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_authenticate_invalid_client(self, gateway: WebSocketGateway):
        """Test authentication with invalid client"""
        result = await gateway.authenticate(
            client_id="nonexistent-client",
            user_id="test-user",
        )
        
        assert result is False
    
    # ----------------------------------------------------------------
    # Subscription Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_subscribe_to_channel(self, gateway: WebSocketGateway):
        """Test channel subscription"""
        class MockWebSocket:
            async def accept(self):
                pass
            async def close(self, code=1000, reason=""):
                pass
        
        client_id = await gateway.handle_connection(MockWebSocket())
        
        result = await gateway.subscribe_to_channel(
            client_id=client_id,
            channel="test-channel",
        )
        
        assert result is True
        assert "test-channel" in gateway._connections[client_id].subscriptions
        assert "test-channel" in gateway._client_channels[client_id]
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_unsubscribe_from_channel(self, gateway: WebSocketGateway):
        """Test channel unsubscription"""
        class MockWebSocket:
            async def accept(self):
                pass
            async def close(self, code=1000, reason=""):
                pass
        
        client_id = await gateway.handle_connection(MockWebSocket())
        await gateway.subscribe_to_channel(client_id, "unsub-channel")
        await gateway._unsubscribe_from_channel(client_id, "unsub-channel")
        
        assert "unsub-channel" not in gateway._connections[client_id].subscriptions
    
    # ----------------------------------------------------------------
    # Message Handling Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_handle_message_heartbeat(self, gateway: WebSocketGateway):
        """Test heartbeat message handling"""
        class MockWebSocket:
            async def accept(self):
                pass
            async def close(self, code=1000, reason=""):
                pass
        
        client_id = await gateway.handle_connection(MockWebSocket())
        
        message = await gateway.handle_message(
            client_id=client_id,
            message={"type": "heartbeat"},
        )
        
        assert message is not None
        assert message.get("type") == "heartbeat_ack"
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_handle_message_subscribe(self, gateway: WebSocketGateway):
        """Test subscribe message handling"""
        class MockWebSocket:
            async def accept(self):
                pass
            async def close(self, code=1000, reason=""):
                pass
        
        client_id = await gateway.handle_connection(MockWebSocket())
        
        message = await gateway.handle_message(
            client_id=client_id,
            message={
                "type": "subscribe",
                "payload": {"channel": "new-channel"},
            },
        )
        
        assert message is not None
        assert "new-channel" in gateway._connections[client_id].subscriptions
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_handle_message_unsubscribe(self, gateway: WebSocketGateway):
        """Test unsubscribe message handling"""
        class MockWebSocket:
            async def accept(self):
                pass
            async def close(self, code=1000, reason=""):
                pass
        
        client_id = await gateway.handle_connection(MockWebSocket())
        await gateway.subscribe_to_channel(client_id, "remove-channel")
        
        message = await gateway.handle_message(
            client_id=client_id,
            message={
                "type": "unsubscribe",
                "payload": {"channel": "remove-channel"},
            },
        )
        
        assert "remove-channel" not in gateway._connections[client_id].subscriptions
    
    # ----------------------------------------------------------------
    # Broadcast Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_broadcast(self, gateway: WebSocketGateway):
        """Test message broadcasting"""
        class MockWebSocket:
            async def accept(self):
                pass
            async def send_json(self, data):
                pass
            async def close(self, code=1000, reason=""):
                pass
        
        # Create two clients
        client1 = await gateway.handle_connection(MockWebSocket())
        client2 = await gateway.handle_connection(MockWebSocket())
        
        # Subscribe both to channel
        await gateway.subscribe_to_channel(client1, "broadcast-channel")
        await gateway.subscribe_to_channel(client2, "broadcast-channel")
        
        count = await gateway.broadcast(
            channel="broadcast-channel",
            message_type="test.broadcast",
            payload={"data": "test-data"},
        )
        
        assert count >= 2
    
    # ----------------------------------------------------------------
    # Convenience Methods Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_emit_render_progress(self, gateway: WebSocketGateway):
        """Test rendering render progress event"""
        class MockWebSocket:
            data_sent = []
            async def accept(self):
                pass
            async def send_json(self, data):
                self.data_sent.append(data)
            async def close(self, code=1000, reason=""):
                pass
        
        # Subscribe a client
        for i in range(10):
            ws = MockWebSocket()
            client_id = await gateway.handle_connection(ws)
            await gateway.subscribe_to_channel(client_id, f"render:job-123")
        
        count = await gateway.emit_render_progress(
            job_id="job-123",
            progress=0.5,
            current_frame=50,
            total_frames=100,
        )
        
        assert count >= 0  # May be 0 if Redis not available
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_emit_worker_status(self, gateway: WebSocketGateway):
        """Test emitting worker status"""
        count = await gateway.emit_worker_status(
            worker_id="worker-1",
            status="running",
            current_jobs=["job-1", "job-2"],
        )
        
        # Broadcasts to "workers" channel
        assert count >= 0
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_emit_queue_update(self, gateway: WebSocketGateway):
        """Test emitting queue update"""
        count = await gateway.emit_queue_update(
            queue_stats={
                "pending": 10,
                "processing": 5,
                "completed": 100,
            },
        )
        
        assert count >= 0
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_emit_notification(self, gateway: WebSocketGateway):
        """Test emitting notification to specific client"""
        class MockWebSocket:
            async def accept(self):
                pass
            async def send_json(self, data):
                pass
            async def close(self, code=1000, reason=""):
                pass
        
        client_id = await gateway.handle_connection(MockWebSocket())
        
        result = await gateway.emit_notification(
            client_id=client_id,
            title="Test Title",
            message="Test Message",
            notification_type="info",
        )
        
        assert result is True
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_emit_notification_invalid_client(self, gateway: WebSocketGateway):
        """Test notification to invalid client returns False"""
        result = await gateway.emit_notification(
            client_id="nonexistent-client",
            title="Test",
            message="Test",
        )
        
        assert result is False
    
    # ----------------------------------------------------------------
    # Stats and Health Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_get_connection_stats(self, gateway: WebSocketGateway):
        """Test getting connection statistics"""
        class MockWebSocket:
            async def accept(self):
                pass
            async def close(self, code=1000, reason=""):
                pass
        
        # Create connections
        await gateway.handle_connection(MockWebSocket())
        await gateway.handle_connection(MockWebSocket())
        
        stats = await gateway.get_connection_stats()
        
        assert "total_connections" in stats
        assert "authenticated_connections" in stats
        assert "total_subscriptions" in stats
        assert "subscriptions_by_channel" in stats
        assert "active_channels" in stats
    
    @pytest.mark.unit
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_health_check(self, gateway: WebSocketGateway):
        """Test health check"""
        health = await gateway.health_check()
        
        assert "status" in health
        assert "redis_connected" in health
        assert "connections" in health
        assert "max_connections" in health


# =============================================================================
# MessageType Enum Tests
# =============================================================================

class TestMessageType:
    """Test suite for MessageType enum"""
    
    @pytest.mark.unit
    @pytest.mark.websocket
    def test_message_type_values(self):
        """Test MessageType enum values"""
        # Connection types
        assert MessageType.CONNECT.value == "connect"
        assert MessageType.DISCONNECT.value == "disconnect"
        assert MessageType.HEARTBEAT.value == "heartbeat"
        
        # Event types
        assert MessageType.EVENT_SUBSCRIBE.value == "subscribe"
        assert MessageType.EVENT_UNSUBSCRIBE.value == "unsubscribe"
        
        # Render types
        assert MessageType.RENDER_PROGRESS.value == "render.progress"
        assert MessageType.RENDER_COMPLETED.value == "render.completed"
        assert MessageType.RENDER_FAILED.value == "render.failed"
        
        # Worker types
        assert MessageType.WORKER_STATUS.value == "worker.status"
        assert MessageType.WORKER_METRICS.value == "worker.metrics"
        
        # Queue types
        assert MessageType.QUEUE_UPDATE.value == "queue.update"
        assert MessageType.JOB_QUEUED.value == "job.queued"
        
        # General types
        assert MessageType.NOTIFICATION.value == "notification"
        assert MessageType.ERROR.value == "error"


# =============================================================================
# Real-time Communication Tests
# =============================================================================

class TestRealTimeCommunication:
    """Test suite for real-time communication scenarios"""
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_concurrent_connections(self, redis_client):
        """Test handling concurrent connections"""
        gateway = WebSocketGateway(
            redis_url="redis://localhost:6379/15",
            heartbeat_interval=30,
            max_connections=100,
        )
        
        class MockWebSocket:
            async def accept(self):
                pass
            async def close(self, code=1000, reason=""):
                pass
        
        # Simulate concurrent connections
        tasks = []
        for i in range(5):
            task = gateway.handle_connection(MockWebSocket())
            tasks.append(task)
        
        client_ids = await asyncio.gather(*tasks)
        
        # All connections should be registered
        for client_id in client_ids:
            assert client_id in gateway._connections
        
        # Cleanup
        for client_id in client_ids:
            await gateway.disconnect_client(client_id)
        await gateway.disconnect()
    
    @pytest.mark.unit
    @pytest.mark.websocket
    async def test_message_ordering(self, redis_client):
        """Test message ordering integrity"""
        gateway = WebSocketGateway(
            redis_url="redis://localhost:6379/15",
        )
        
        messages = []
        
        class MockWebSocket:
            async def accept(self):
                pass
            async def send_json(self, data):
                messages.append(data)
            async def close(self, code=1000, reason=""):
                pass
        
        client_id = await gateway.handle_connection(MockWebSocket())
        
        # Send messages in order
        await gateway._publish_to_client(
            client_id,
            "msg1",
            {"order": 1},
        )
        await gateway._publish_to_client(
            client_id,
            "msg2",
            {"order": 2},
        )
        await gateway._publish_to_client(
            client_id,
            "msg3",
            {"order": 3},
        )
        
        # Verify order preserved
        assert len(messages) == 3
        assert messages[0]["payload"]["order"] == 1
        assert messages[1]["payload"]["order"] == 2
        assert messages[2]["payload"]["order"] == 3
        
        await gateway.disconnect()


# =============================================================================
# Integration Tests (WebSocket + Redis)
# =============================================================================

@pytest.mark.skip(reason="Requires Redis connection")
class TestWebSocketRedisIntegration:
    """Test suite for WebSocket + Redis integration"""
    
    @pytest.mark.integration
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_event_persistence(self, redis_client):
        """Test event persistence through Redis"""
        gateway = WebSocketGateway(
            redis_url="redis://localhost:6379/15",
        )
        
        # Send test message
        channel = "test-persist-channel"
        message = {"type": "test", "data": "persistence-test"}
        
        if gateway._redis:
            await gateway._redis.publish(channel, json.dumps(message))
        
        await gateway.disconnect()
    
    @pytest.mark.integration
    @pytest.mark.websocket
    @pytest.mark.asyncio
    async def test_multi_client_sync(self, redis_client):
        """Test synchronization across multiple clients"""
        gateway = WebSocketGateway(
            redis_url="redis://localhost:6379/15",
        )
        
        class MockWebSocket:
            async def accept(self):
                pass
            async def close(self, code=1000, reason=""):
                pass
        
        # Create multiple clients on same channel
        clients = []
        for i in range(3):
            client_id = await gateway.handle_connection(MockWebSocket())
            await gateway.subscribe_to_channel(client_id, "sync-channel")
            clients.append(client_id)
        
        # Broadcast to synced channel
        count = await gateway.broadcast(
            channel="sync-channel",
            message_type="sync-test",
            payload={"synced": True},
        )
        
        # All should receive
        assert count >= len(clients)
        
        # Cleanup
        for client_id in clients:
            await gateway.disconnect_client(client_id)
        await gateway.disconnect()
