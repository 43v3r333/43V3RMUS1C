"""
Event Bus Infrastructure for Domain-Driven Architecture.
Provides pub/sub event handling with Redis backend.
"""
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type
from uuid import UUID, uuid4

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Core system event types"""
    # Media events
    MEDIA_UPLOADED = "media.uploaded"
    MEDIA_PROCESSING = "media.processing"
    MEDIA_PROCESSED = "media.processed"
    MEDIA_FAILED = "media.failed"
    MEDIA_DELETED = "media.deleted"
    
    # Asset events
    ASSET_CREATED = "asset.created"
    ASSET_UPDATED = "asset.updated"
    ASSET_ARCHIVED = "asset.archived"
    
    # Waveform events
    WAVEFORM_GENERATED = "waveform.generated"
    
    # Audio analysis events
    AUDIO_ANALYZED = "audio.analyzed"
    BPM_DETECTED = "audio.bpm_detected"
    BEATS_DETECTED = "audio.beats_detected"
    
    # Transcoding events
    TRANSCODE_STARTED = "transcode.started"
    TRANSCODE_PROGRESS = "transcode.progress"
    TRANSCODE_COMPLETED = "transcode.completed"
    TRANSCODE_FAILED = "transcode.failed"
    
    # Render events
    RENDER_STARTED = "render.started"
    RENDER_PROGRESS = "render.progress"
    RENDER_COMPLETED = "render.completed"
    RENDER_FAILED = "render.failed"
    RENDER_CANCELLED = "render.cancelled"
    
    # Timeline events
    TIMELINE_CREATED = "timeline.created"
    TIMELINE_UPDATED = "timeline.updated"
    TIMELINE_RENDER_STARTED = "timeline.render.started"
    TIMELINE_RENDER_COMPLETED = "timeline.render.completed"
    
    # Clip events
    CLIP_ADDED = "clip.added"
    CLIP_UPDATED = "clip.updated"
    CLIP_DELETED = "clip.deleted"
    
    # Workflow events
    WORKFLOW_EXECUTED = "workflow.executed"
    WORKFLOW_STEP_COMPLETED = "workflow.step.completed"
    WORKFLOW_FAILED = "workflow.failed"
    
    # System events
    WORKER_STATUS = "worker.status"
    QUEUE_STATS = "queue.stats"
    SYSTEM_ALERT = "system.alert"


@dataclass
class Event:
    """Base event class for all domain events"""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: EventType = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    source: str = "system"
    version: str = "1.0"
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize event to dictionary"""
        return {
            "id": self.id,
            "type": self.type.value if isinstance(self.type, EventType) else self.type,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "source": self.source,
            "version": self.version,
            "data": self.data,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Deserialize event from dictionary"""
        event = cls()
        event.id = data.get("id", str(uuid4()))
        event.type = EventType(data["type"]) if "type" in data else None
        event.timestamp = datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.utcnow()
        event.correlation_id = data.get("correlation_id")
        event.causation_id = data.get("causation_id")
        event.source = data.get("source", "system")
        event.version = data.get("version", "1.0")
        event.data = data.get("data", {})
        event.metadata = data.get("metadata", {})
        return event
    
    def with_correlation(self, correlation_id: str) -> "Event":
        """Add correlation ID for distributed tracing"""
        self.correlation_id = correlation_id
        return self
    
    def with_causation(self, causation_id: str) -> "Event":
        """Add causation ID for event chaining"""
        self.causation_id = causation_id
        return self


class EventHandler(ABC):
    """Abstract base class for event handlers"""
    
    @property
    @abstractmethod
    def event_types(self) -> Set[EventType]:
        """Return set of event types this handler handles"""
        pass
    
    @abstractmethod
    async def handle(self, event: Event) -> None:
        """Handle an event"""
        pass
    
    async def on_error(self, event: Event, error: Exception) -> None:
        """Handle errors during event processing"""
        logger.error(f"Event handler error for {event.type}: {error}")


class EventSubscription:
    """Subscription to an event stream"""
    
    def __init__(
        self,
        handler: EventHandler,
        event_types: List[EventType],
        pattern: Optional[str] = None
    ):
        self.id = str(uuid4())
        self.handler = handler
        self.event_types = set(event_types)
        self.pattern = pattern
        self.active = True
    
    def matches(self, event_type: EventType) -> bool:
        """Check if this subscription matches the event type"""
        if not self.active:
            return False
        if self.pattern:
            return event_type.value.startswith(self.pattern)
        return event_type in self.event_types


class EventBus:
    """
    Central event bus for pub/sub event handling.
    Supports Redis pub/sub for distributed event streaming.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self._subscriptions: List[EventSubscription] = []
        self._redis_client: Optional[redis.Redis] = None
        self._redis_url = redis_url
        self._pubsub: Optional[redis.client.PubSub] = None
        self._running = False
        
        # Local event queue for non-Redis mode
        self._local_queue: List[Event] = []
    
    async def connect(self) -> None:
        """Connect to Redis if URL provided"""
        if self._redis_url:
            self._redis_client = redis.from_url(self._redis_url, decode_responses=True)
            self._pubsub = self._redis_client.pubsub()
            logger.info(f"Event bus connected to Redis: {self._redis_url}")
    
    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self._pubsub:
            await self._pubsub.close()
        if self._redis_client:
            await self._redis_client.close()
        self._running = False
        logger.info("Event bus disconnected")
    
    def subscribe(self, handler: EventHandler) -> str:
        """Subscribe a handler to events"""
        subscription = EventSubscription(
            handler=handler,
            event_types=list(handler.event_types)
        )
        self._subscriptions.append(subscription)
        logger.info(f"Handler subscribed to {len(handler.event_types)} event types")
        return subscription.id
    
    def subscribe_pattern(self, handler: EventHandler, pattern: str) -> str:
        """Subscribe with wildcard pattern matching"""
        subscription = EventSubscription(
            handler=handler,
            event_types=[],
            pattern=pattern
        )
        self._subscriptions.append(subscription)
        logger.info(f"Handler subscribed to pattern: {pattern}")
        return subscription.id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe a handler"""
        for i, sub in enumerate(self._subscriptions):
            if sub.id == subscription_id:
                sub.active = False
                del self._subscriptions[i]
                return True
        return False
    
    async def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.
        Also publishes to Redis if connected.
        """
        # Publish locally
        for subscription in self._subscriptions:
            if subscription.matches(event.type):
                try:
                    await subscription.handler.handle(event)
                except Exception as e:
                    await subscription.handler.on_error(event, e)
                    logger.error(f"Handler failed for {event.type}: {e}")
        
        # Publish to Redis
        if self._redis_client and self._pubsub:
            channel = f"events:{event.type.value}"
            await self._redis_client.publish(channel, json.dumps(event.to_dict()))
        
        logger.debug(f"Event published: {event.type.value}")
    
    async def publish_domain_event(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None
    ) -> Event:
        """Helper to create and publish a domain event"""
        event = Event(
            type=event_type,
            correlation_id=correlation_id,
            causation_id=causation_id,
            data=data
        )
        await self.publish(event)
        return event
    
    async def start_listening(self) -> None:
        """Start listening for Redis events"""
        if not self._redis_client or not self._pubsub:
            return
        
        self._running = True
        await self._pubsub.subscribe("events:*")
        
        while self._running:
            try:
                message = await self._pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    data = json.loads(message["data"])
                    event = Event.from_dict(data)
                    await self.publish(event)
            except Exception as e:
                logger.error(f"Error in event listener: {e}")
    
    def get_subscriptions(self, event_type: EventType) -> List[EventSubscription]:
        """Get all subscriptions for a specific event type"""
        return [sub for sub in self._subscriptions if sub.matches(event_type)]


class EventStore:
    """
    Event store for persisting and replaying events.
    Maintains event history for audit and debugging.
    """
    
    def __init__(self, db_session=None):
        self._db = db_session
    
    async def append(self, event: Event) -> None:
        """Append event to the event store"""
        # This would store to a database events table
        logger.debug(f"Event stored: {event.id}")
    
    async def get_events(
        self,
        event_type: Optional[EventType] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Event]:
        """Get events from the store"""
        return []
    
    async def get_events_by_correlation(self, correlation_id: str) -> List[Event]:
        """Get all events in a correlation chain"""
        return []


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get or create global event bus"""
    global _event_bus
    
    if _event_bus is None:
        from app.core.config import settings
        redis_url = getattr(settings, 'redis_url', None)
        _event_bus = EventBus(redis_url)
    
    return _event_bus


async def emit_event(
    event_type: EventType,
    data: Dict[str, Any],
    correlation_id: Optional[str] = None
) -> Event:
    """Emit a domain event"""
    bus = get_event_bus()
    return await bus.publish_domain_event(event_type, data, correlation_id)


# Decorator for automatic event emission
def on_event(event_types: List[EventType]):
    """Decorator to mark a method as an event handler"""
    def decorator(func):
        func._event_types = event_types
        return func
    return decorator


class EventDrivenService:
    """
    Base class for services that emit and handle events.
    Provides common event bus integration.
    """
    
    def __init__(self):
        self._event_bus = get_event_bus()
        self._handlers: List[EventHandler] = []
    
    def register_handlers(self) -> None:
        """Register event handlers - override in subclasses"""
        pass
    
    async def emit(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> Event:
        """Emit a domain event"""
        return await self._event_bus.publish_domain_event(
            event_type, data, correlation_id
        )