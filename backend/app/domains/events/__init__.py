"""
Event Bus System - Production-grade event-driven architecture
"""
from enum import Enum
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
import asyncio
import json
import logging
from contextlib import asynccontextmanager

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Core domain events"""
    # Media events
    MEDIA_INGESTED = "media.ingested"
    MEDIA_VALIDATED = "media.validated"
    MEDIA_ANALYZED = "media.analyzed"
    MEDIA_TRANSFORMED = "media.transformed"
    MEDIA_DELETED = "media.deleted"
    
    # Audio events
    WAVEFORM_GENERATED = "waveform.generated"
    AUDIO_ANALYZED = "audio.analyzed"
    BPM_DETECTED = "bpm.detected"
    BEAT_MARKERS_DETECTED = "beat_markers.detected"
    TRANSIENT_DETECTED = "transient.detected"
    SILENCE_DETECTED = "silence.detected"
    
    # Render events
    RENDER_QUEUED = "render.queued"
    RENDER_STARTED = "render.started"
    RENDER_PROGRESS = "render.progress"
    RENDER_COMPLETED = "render.completed"
    RENDER_FAILED = "render.failed"
    RENDER_CANCELLED = "render.cancelled"
    
    # Timeline events
    TIMELINE_CREATED = "timeline.created"
    TIMELINE_UPDATED = "timeline.updated"
    TIMELINE_DELETED = "timeline.deleted"
    CLIP_ADDED = "clip.added"
    CLIP_REMOVED = "clip.removed"
    CLIP_UPDATED = "clip.updated"
    TRACK_ADDED = "track.added"
    
    # Workflow events
    WORKFLOW_EXECUTED = "workflow.executed"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    STEP_COMPLETED = "step.completed"
    
    # Asset events
    ASSET_UPLOADED = "asset.uploaded"
    ASSET_TRANSCODED = "asset.transcoded"
    ASSET_THUMBNAILED = "asset.thumbnailed"
    ASSET_FINGERPRINTED = "asset.fingerprinted"
    
    # Worker events
    WORKER_HEARTBEAT = "worker.heartbeat"
    WORKER_REGISTERED = "worker.registered"
    WORKER_OFFLINE = "worker.offline"
    
    # System events
    HEALTH_CHECK = "system.health_check"
    ERROR_OCCURRED = "system.error"


@dataclass
class DomainEvent:
    """Base domain event with tracing support"""
    event_type: EventType
    aggregate_id: UUID
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_id: UUID = field(default_factory=uuid4)
    correlation_id: Optional[UUID] = None
    causation_id: Optional[UUID] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "event_id": str(self.event_id),
            "aggregate_id": str(self.aggregate_id),
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": str(self.correlation_id) if self.correlation_id else None,
            "causation_id": str(self.causation_id) if self.causation_id else None,
            "metadata": self.metadata,
            "user_id": str(self.user_id) if self.user_id else None,
            "session_id": str(self.session_id) if self.session_id else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainEvent":
        return cls(
            event_type=EventType(data["event_type"]),
            event_id=UUID(data["event_id"]),
            aggregate_id=UUID(data["aggregate_id"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            correlation_id=UUID(data["correlation_id"]) if data.get("correlation_id") else None,
            causation_id=UUID(data["causation_id"]) if data.get("causation_id") else None,
            metadata=data.get("metadata", {}),
            user_id=UUID(data["user_id"]) if data.get("user_id") else None,
            session_id=UUID(data["session_id"]) if data.get("session_id") else None,
        )


class EventSubscription:
    """Subscription to events"""
    def __init__(
        self,
        event_type: EventType,
        handler: Callable[[DomainEvent], Any],
        filter_func: Optional[Callable[[DomainEvent], bool]] = None,
    ):
        self.event_type = event_type
        self.handler = handler
        self.filter_func = filter_func
        self.subscription_id = uuid4()
        self.created_at = datetime.utcnow()


class EventBus:
    """
    Production-grade event bus with Redis pub/sub, retry handling,
    dead-letter queue strategy, and event tracing.
    """
    
    def __init__(
        self,
        redis_url: str,
        db_session_factory: Optional[Callable[[], AsyncSession]] = None,
        dead_letter_queue: str = "events:dlq",
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        self.redis_url = redis_url
        self.db_session_factory = db_session_factory
        self.dead_letter_queue = dead_letter_queue
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self._redis: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None
        self._subscriptions: Dict[str, List[EventSubscription]] = {}
        self._handlers: Dict[EventType, List[Callable]] = {}
        self._event_publishers: Dict[str, Any] = {}
        
        self._running = False
        self._listener_task: Optional[asyncio.Task] = None
        self._event_counter: Dict[str, int] = {}
        
    async def connect(self) -> None:
        """Initialize Redis connection"""
        self._redis = redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        await self._redis.ping()
        logger.info("EventBus connected to Redis")
    
    async def disconnect(self) -> None:
        """Close Redis connection"""
        self._running = False
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        if self._pubsub:
            await self._pubsub.close()
        if self._redis:
            await self._redis.close()
        logger.info("EventBus disconnected from Redis")
    
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish event to Redis pub/sub and persist for replay.
        """
        if not self._redis:
            await self.connect()
        
        channel = f"events:{event.event_type.value}"
        event_data = json.dumps(event.to_dict())
        
        # Publish to Redis pub/sub
        await self._redis.publish(channel, event_data)
        
        # Increment event counter
        self._event_counter[event.event_type.value] = self._event_counter.get(
            event.event_type.value, 0
        ) + 1
        
        # Persist event for replay capability
        event_stream_key = f"events:stream:{event.aggregate_id}"
        await self._redis.xadd(
            event_stream_key,
            {"event": event_data},
            maxlen=1000,
        )
        
        logger.debug(f"Published event {event.event_type.value} for {event.aggregate_id}")
    
    async def subscribe(
        self,
        event_types: List[EventType],
        handler: Callable[[DomainEvent], Any],
        filter_func: Optional[Callable[[DomainEvent], bool]] = None,
    ) -> EventSubscription:
        """Subscribe to specific event types"""
        for event_type in event_types:
            if event_type.value not in self._subscriptions:
                self._subscriptions[event_type.value] = []
            
            subscription = EventSubscription(event_type, handler, filter_func)
            self._subscriptions[event_type.value].append(subscription)
            
            if event_type.value not in self._handlers:
                self._handlers[event_type.value] = []
            self._handlers[event_type.value].append(handler)
        
        logger.info(f"Subscribed handler to {len(event_types)} event types")
        return subscription
    
    async def start_listening(self) -> None:
        """Start Redis pub/sub listener"""
        if not self._redis:
            await self.connect()
        
        self._pubsub = self._redis.pubsub()
        
        # Subscribe to all registered channels
        channels = [f"events:{et.value}" for et in EventType]
        await self._pubsub.subscribe(*channels)
        
        self._running = True
        self._listener_task = asyncio.create_task(self._listen_loop())
        logger.info("EventBus listener started")
    
    async def _listen_loop(self) -> None:
        """Main listener loop for processing events"""
        while self._running:
            try:
                message = await self._pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0,
                )
                if message:
                    await self._process_message(message)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in event listener: {e}")
                await asyncio.sleep(1)
    
    async def _process_message(self, message: Dict[str, Any]) -> None:
        """Process incoming pub/sub message"""
        try:
            channel = message["channel"]
            event_type = channel.replace("events:", "")
            event_data = json.loads(message["data"])
            
            event = DomainEvent.from_dict(event_data)
            
            if event_type in self._subscriptions:
                for subscription in self._subscriptions[event_type]:
                    if subscription.filter_func and not subscription.filter_func(event):
                        continue
                    await self._execute_with_retry(subscription.handler, event)
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _execute_with_retry(
        self,
        handler: Callable,
        event: DomainEvent,
    ) -> None:
        """Execute handler with retry logic"""
        retries = 0
        while retries <= self.max_retries:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
                return
            except Exception as e:
                retries += 1
                if retries > self.max_retries:
                    await self._send_to_dlq(event, str(e))
                    logger.error(
                        f"Event {event.event_id} failed after {self.max_retries} retries: {e}"
                    )
                else:
                    await asyncio.sleep(self.retry_delay * retries)
    
    async def _send_to_dlq(self, event: DomainEvent, error: str) -> None:
        """Send failed event to dead-letter queue"""
        dlq_message = {
            "event": event.to_dict(),
            "error": error,
            "failed_at": datetime.utcnow().isoformat(),
            "retry_count": self.max_retries,
        }
        await self._redis.lpush(self.dead_letter_queue, json.dumps(dlq_message))
    
    async def get_event_history(
        self,
        aggregate_id: UUID,
        limit: int = 100,
    ) -> List[DomainEvent]:
        """Retrieve event history for an aggregate"""
        if not self._redis:
            await self.connect()
        
        event_stream_key = f"events:stream:{aggregate_id}"
        events_data = await self._redis.xrange(event_stream_key, count=limit)
        
        events = []
        for _, data in events_data:
            try:
                event = DomainEvent.from_dict(json.loads(data["event"]))
                events.append(event)
            except Exception as e:
                logger.error(f"Error parsing event history: {e}")
        
        return events
    
    async def get_dlq_events(self, limit: int = 100) -> List[Dict]:
        """Retrieve dead-letter queue events"""
        if not self._redis:
            await self.connect()
        
        dlq_data = await self._redis.lrange(self.dead_letter_queue, 0, limit - 1)
        return [json.loads(data) for data in dlq_data]
    
    async def retry_dlq_event(self, dlq_event: Dict) -> None:
        """Retry a dead-letter queue event"""
        event = DomainEvent.from_dict(dlq_event["event"])
        await self.publish(event)
        logger.info(f"Retrying DLQ event {event.event_id}")
    
    def get_event_stats(self) -> Dict[str, Any]:
        """Get event statistics"""
        return {
            "total_events_published": sum(self._event_counter.values()),
            "events_by_type": self._event_counter.copy(),
            "active_subscriptions": sum(len(s) for s in self._subscriptions.values()),
            "handler_count": sum(len(h) for h in self._handlers.values()),
        }


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get or create global event bus"""
    global _event_bus
    if _event_bus is None:
        from ...core.config import settings
        _event_bus = EventBus(
            redis_url=settings.redis_url,
            dead_letter_queue=settings.redis_dlq,
            max_retries=3,
        )
    return _event_bus


# Event Router for internal routing
class EventRouter:
    """Internal event routing with handler registration"""
    
    def __init__(self):
        self._routes: Dict[EventType, List[Callable]] = {}
    
    def register(
        self,
        event_type: EventType,
        handler: Callable,
    ) -> None:
        """Register a handler for an event type"""
        if event_type not in self._routes:
            self._routes[event_type] = []
        self._routes[event_type].append(handler)
    
    def route(self, event: DomainEvent) -> List[Any]:
        """Route an event to all registered handlers"""
        handlers = self._routes.get(event.event_type, [])
        results = []
        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    result = asyncio.create_task(result)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")
        return results
    
    def unregister(self, event_type: EventType, handler: Callable) -> None:
        """Unregister a handler"""
        if event_type in self._routes:
            self._routes[event_type] = [
                h for h in self._routes[event_type] if h != handler
            ]


event_router = EventRouter()


@asynccontextmanager
async def event_bus_context():
    """Context manager for event bus lifecycle"""
    bus = get_event_bus()
    await bus.connect()
    await bus.start_listening()
    try:
        yield bus
    finally:
        await bus.disconnect()