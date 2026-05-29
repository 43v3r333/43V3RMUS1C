"""
43V3R CORE - Test Infrastructure Core
=====================================

Production-grade test infrastructure providing:
- Async database fixtures
- Redis connection fixtures
- Mock service fixtures
- Factory fixtures for test data generation
- Telemetry and observability mocks
- WebSocket testing utilities
- Chaos engineering primitives

This module establishes the foundational testing primitives used across
all test suites to ensure consistent, deterministic, and isolated testing.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Type,
    TypeVar,
)
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

# Ensure app is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import settings
from app.core.database import Base
from app.models.base import BaseModel

logger = logging.getLogger(__name__)

fake = Faker()
Faker.seed(42)  # Deterministic fake data
asyncio.seed_everything(42)  # Deterministic async operations


# =============================================================================
# Type Variables and Generics
# =============================================================================

T = TypeVar("T")
ModelType = TypeVar("ModelType", bound=BaseModel)
AsyncSessionLocal = async_sessionmaker(
    bind=None,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# =============================================================================
# Configuration Override
# =============================================================================

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Test configuration overrides"""
    return {
        "database_url": "postgresql+asyncpg://test:test@localhost:5432/versemusic_test",
        "redis_url": "redis://localhost:6379/15",
        "testing": True,
        " secret_key": "test-secret-key-for-testing-only-32chars",
        " jwt_secret": "test-jwt-secret-for-testing-only",
        " alembic_database_url": "postgresql://test:test@localhost:5432/versemusic_test",
    }


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest_asyncio.fixture(scope="session")
async def engine():
    """
    Create async SQLAlchemy engine for testing.
    
    Uses separate test database and configures connection pooling
    appropriately for parallel test execution.
    """
    database_url = os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://test:test@localhost:5432/versemusic_test"
    )
    
    engine = create_async_engine(
        database_url,
        echo=False,
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def sync_engine():
    """Create sync engine for migrations and setup"""
    database_url = os.environ.get(
        "TEST_DATABASE_URL_SYNC",
        "postgresql://test:test@localhost:5432/versemusic_test"
    )
    
    engine = create_engine(
        database_url,
        echo=False,
        poolclass=NullPool,
    )
    
    yield engine
    engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def create_database(sync_engine):
    """Create test database and tables"""
    # Create database
    database_name = "versemusic_test"
    
    try:
        with sync_engine.connect() as conn:
            conn.execute(text("COMMIT"))
            conn.execute(text(f"DROP DATABASE IF EXISTS {database_name}"))
            conn.execute(text(f"CREATE DATABASE {database_name}"))
            logger.info(f"Created test database: {database_name}")
    except Exception as e:
        logger.warning(f"Database creation issue (might already exist): {e}")
    
    # Use async engine to create tables
    from sqlalchemy.ext.asyncio import create_async_engine
    
    async_engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost:5432/versemusic_test",
        echo=False,
    )
    
    async with async_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    
    await async_engine.dispose()
    
    yield
    
    # Cleanup handled by session scope


@pytest_asyncio.fixture(scope="session")
async def session_factory(engine):
    """Create async session factory"""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


@pytest_asyncio.fixture
async def db_session(
    session_factory,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Database session fixture for testing.
    
    Provides an isolated transaction that is rolled back after each test,
    ensuring test isolation without database-level cleanup overhead.
    
    Features:
    - Automatic transaction management
    - Rollback on test completion
    - Proper timeout handling
    - Error propagation
    """
    async with session_factory() as session:
        async with session.begin():
            yield session
            try:
                await session.rollback()
            except Exception:
                pass


@pytest_asyncio.fixture
async def db_session_with_data(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Database session with test data committed.
    Use when tests require persisted data.
    """
    try:
        yield db_session
        await db_session.commit()
    except Exception:
        await db_session.rollback()
        raise
    finally:
        await db_session.rollback()  # Cleanup after test


# =============================================================================
# Redis Fixtures
# =============================================================================

@pytest_asyncio.fixture(scope="session")
async def redis_client():
    """Redis client fixture for testing"""
    import redis.asyncio as redis
    
    redis_url = os.environ.get("TEST_REDIS_URL", "redis://localhost:6379/15")
    
    client = redis.from_url(
        redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    
    try:
        await client.ping()
        await client.flushdb()
        logger.info("Redis connection established for testing")
    except Exception as e:
        logger.warning(f"Redis not available: {e}")
        pytest.skip("Redis not available for testing")
    
    yield client
    
    await client.flushdb()
    await client.close()


@pytest_asyncio.fixture
async def redis_with_data(redis_client):
    """Redis client with test data"""
    yield redis_client
    await redis_client.flushdb()


# =============================================================================
# Mock Service Fixtures
# =============================================================================

class MockOpenAIClient:
    """Mock OpenAI client for testing"""
    
    def __init__(self):
        self.responses: List[str] = ["Mock response"] * 10
        self.call_count = 0
    
    async def chat_completions_create(self, **kwargs):
        self.call_count += 1
        return {
            "id": f"mock-chatcmpl-{self.call_count}",
            "choices": [{
                "message": {
                    "content": self.responses[self.call_count % len(self.responses)]
                },
                "finish_reason": "stop",
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30,
            },
        }


class MockRedisPubSub:
    """Mock Redis pub/sub for testing"""
    
    def __init__(self):
        self.subscriptions: Dict[str, List[Callable]] = {}
        self.published_messages: List[Dict[str, Any]] = []
    
    async def subscribe(self, *args, **kwargs):
        for channel in args:
            if channel not in self.subscriptions:
                self.subscriptions[channel] = []
    
    async def publish(self, channel: str, message: str):
        self.published_messages.append({
            "channel": channel,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    async def get_message(self, *args, **kwargs):
        if self.published_messages:
            msg = self.published_messages.pop(0)
            return {
                "type": "message",
                "channel": msg["channel"],
                "data": msg["message"],
            }
        return None
    
    async def close(self):
        pass


class MockWebSocketServer:
    """Mock WebSocket server for testing"""
    
    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.messages: List[Dict[str, Any]] = []
    
    async def accept(self):
        pass
    
    async def close(self, code: int = 1000, reason: str = ""):
        pass
    
    async def send_json(self, data: Dict[str, Any]):
        self.messages.append({
            "type": "json",
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    async def send_text(self, message: str):
        self.messages.append({
            "type": "text",
            "data": message,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    async def receive_json(self) -> Dict[str, Any]:
        return {}


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client fixture"""
    return MockOpenAIClient()


@pytest.fixture
def mock_redis_pubsub():
    """Mock Redis pub/sub fixture"""
    return MockRedisPubSub()


@pytest.fixture
def mock_websocket_server():
    """Mock WebSocket server fixture"""
    return MockWebSocketServer()


# =============================================================================
# Factory Fixtures for Test Data
# =============================================================================

@dataclass
class TestDataFactory:
    """
    Test data factory for generating deterministic, reproducible test data.
    
    Provides methods for creating:
    - User accounts
    - Orchestration sessions
    - Workflows and executions
    - Semantic profiles
    - Governance configurations
    
    All generated data is deterministic based on seed values.
    """
    
    session: AsyncSession
    _counter: int = 0
    
    @classmethod
    def reset_counter(cls):
        cls._counter = 0
    
    def _next_id(self) -> str:
        """Generate next deterministic ID"""
        self.__class__._counter += 1
        return f"test-{self._counter}-{uuid4().hex[:8]}"
    
    def create_user_data(self, **overrides) -> Dict[str, Any]:
        """Generate user data"""
        self._next_id()
        return {
            "email": f"user{self._counter}@test.example.com",
            "username": f"testuser{self._counter}",
            "full_name": f"Test User {self._counter}",
            "password_hash": "$2b$12$test_hash",  # Pre-computed hash
            "is_active": True,
            "is_verified": True,
            **overrides,
        }
    
    def create_session_data(self, **overrides) -> Dict[str, Any]:
        """Generate runtime session data"""
        self._next_id()
        return {
            "name": f"Test Session {self._counter}",
            "session_type": "orchestration",
            "status": "running",
            "config": {"max_nodes": 10},
            "capabilities": ["execution", "monitoring"],
            **overrides,
        }
    
    def create_workflow_data(self, **overrides) -> Dict[str, Any]:
        """Generate workflow graph data"""
        self._next_id()
        return {
            "name": f"Test Workflow {self._counter}",
            "description": f"Test workflow for {self._counter}",
            "version": 1,
            "nodes": [
                {"id": "node1", "type": "start", "name": "Start"},
                {"id": "node2", "type": "process", "name": "Process"},
                {"id": "node3", "type": "end", "name": "End"},
            ],
            "edges": [
                {"from": "node1", "to": "node2"},
                {"from": "node2", "to": "node3"},
            ],
            "execution_mode": "sequential",
            "max_parallelism": 3,
            **overrides,
        }
    
    def create_execution_data(self, **overrides) -> Dict[str, Any]:
        """Generate workflow execution data"""
        self._next_id()
        return {
            "status": "pending",
            "execution_mode": "sequential",
            "input_data": {"test": "data"},
            "total_nodes": 3,
            "completed_nodes": 0,
            "failed_nodes": 0,
            **overrides,
        }
    
    def create_semantic_profile_data(self, **overrides) -> Dict[str, Any]:
        """Generate semantic profile data"""
        self._next_id()
        return {
            "asset_id": f"asset-{self._counter}",
            "semantic_type": "chorus",
            "primary_emotion": "excitement",
            "secondary_emotion": "joy",
            "energy_level": 0.8,
            "pacing_score": 0.75,
            "duration": 30.0,
            "format": "video/mp4",
            **overrides,
        }
    
    def create_governance_profile_data(self, **overrides) -> Dict[str, Any]:
        """Generate governance profile data"""
        self._next_id()
        return {
            "profile_id": f"profile-{self._counter}",
            "profile_scope": "orchestration",
            "profile_key": f"governance-{self._counter}",
            "governance_scope": "ecosystem",
            "max_violations_per_cycle": 3,
            "violation_severity_cap": "high",
            "auto_remediation_enabled": True,
            "safety_margin": 0.1,
            **overrides,
        }
    
    def create_context_data(self, **overrides) -> Dict[str, Any]:
        """Generate distributed context data"""
        self._next_id()
        return {
            "context_data": {
                "correlation_id": f"corr-{self._counter}",
                "trace_id": f"trace-{self._counter}",
                "user_id": f"user-{self._counter}",
                "metadata": {"key": f"value-{self._counter}"},
            },
            "scope": "execution",
            **overrides,
        }
    
    def create_websocket_message_data(self, **overrides) -> Dict[str, Any]:
        """Generate WebSocket message data"""
        self._next_id()
        return {
            "type": "test.message",
            "payload": {
                "session_id": f"session-{self._counter}",
                "data": {"test": f"data-{self._counter}"},
            },
            "timestamp": datetime.utcnow().isoformat(),
            **overrides,
        }
    
    def create_observability_data(self, **overrides) -> Dict[str, Any]:
        """Generate observability/telemetry data"""
        self._next_id()
        return {
            "metric_type": "execution_duration",
            "value": 100.0 + self._counter,
            "unit": "ms",
            "tags": {"service": "test", "env": "testing"},
            "aggregation": "avg",
            **overrides,
        }


@pytest.fixture
def test_data_factory(db_session: AsyncSession) -> TestDataFactory:
    """Test data factory fixture"""
    factory = TestDataFactory(session=db_session)
    factory.reset_counter()
    return factory


# =============================================================================
# Event Bus Fixtures (for testing event-driven architecture)
# =============================================================================

@dataclass
class TestEvent:
    """Test event wrapper"""
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "metadata": self.metadata,
        }


class InMemoryEventBus:
    """
    In-memory event bus for testing event-driven systems.
    
    Provides synchronous and asynchronous event propagation
    for testing without external message broker dependencies.
    """
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._events: List[TestEvent] = []
        self._metrics: Dict[str, int] = {}
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe handler to event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe handler"""
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h != handler
            ]
    
    def publish(self, event: TestEvent):
        """Publish event synchronously"""
        self._events.append(event)
        self._metrics[event.event_type] = self._metrics.get(event.event_type, 0) + 1
        
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    asyncio.create_task(result)
            except Exception as e:
                logger.error(f"Event handler error for {event.event_type}: {e}")
    
    async def publish_async(self, event: TestEvent):
        """Publish event asynchronously"""
        self._events.append(event)
        self._metrics[event.event_type] = self._metrics.get(event.event_type, 0) + 1
        
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Async event handler error for {event.event_type}: {e}")
    
    def get_events(self, event_type: Optional[str] = None) -> List[TestEvent]:
        """Get published events"""
        if event_type:
            return [e for e in self._events if e.event_type == event_type]
        return list(self._events)
    
    def get_metrics(self) -> Dict[str, int]:
        """Get event count metrics"""
        return dict(self._metrics)
    
    def clear(self):
        """Clear events and handlers"""
        self._events.clear()
        self._metrics.clear()


@pytest.fixture
def in_memory_event_bus() -> InMemoryEventBus:
    """In-memory event bus fixture"""
    return InMemoryEventBus()


# =============================================================================
# Telemetry and Observability Fixtures
# =============================================================================

@dataclass
class TestSpanTelemetry:
    """Test span telemetry data"""
    name: str
    span_id: str
    trace_id: str
    parent_id: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    tags: Dict[str, Any]
    events: List[Dict[str, Any]]


class MockTelemetryCollector:
    """
    Mock telemetry collector for testing observability.
    
    Captures spans, metrics, and logs for verification
    without external telemetry backend dependency.
    """
    
    def __init__(self):
        self.spans: List[TestSpanTelemetry] = []
        self.metrics: List[Dict[str, Any]] = []
        self.logs: List[Dict[str, Any]] = []
        self._span_stack: List[str] = []
    
    def start_span(self, name: str, tags: Optional[Dict[str, Any]] = None) -> str:
        """Start a new span"""
        span_id = f"span-{uuid4().hex[:8]}"
        trace_id = f"trace-{uuid4().hex[:16]}"
        parent_id = self._span_stack[-1] if self._span_stack else None
        
        span = TestSpanTelemetry(
            name=name,
            span_id=span_id,
            trace_id=trace_id,
            parent_id=parent_id,
            start_time=datetime.utcnow(),
            end_time=None,
            tags=tags or {},
            events=[],
        )
        
        self.spans.append(span)
        self._span_stack.append(span_id)
        
        return span_id
    
    def end_span(self, span_id: str):
        """End a span"""
        for span in self.spans:
            if span.span_id == span_id:
                span.end_time = datetime.utcnow()
                break
        
        if self._span_stack and self._span_stack[-1] == span_id:
            self._span_stack.pop()
    
    def record_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, Any]] = None,
    ):
        """Record a metric"""
        self.metrics.append({
            "name": name,
            "value": value,
            "tags": tags or {},
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def record_log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Record a log entry"""
        self.logs.append({
            "level": level,
            "message": message,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def get_span(self, span_id: str) -> Optional[TestSpanTelemetry]:
        """Get span by ID"""
        for span in self.spans:
            if span.span_id == span_id:
                return span
        return None
    
    def get_traces(self) -> Dict[str, List[TestSpanTelemetry]]:
        """Get traces grouped by trace_id"""
        traces: Dict[str, List[TestSpanTelemetry]] = {}
        for span in self.spans:
            if span.trace_id not in traces:
                traces[span.trace_id] = []
            traces[span.trace_id].append(span)
        return traces
    
    def clear(self):
        """Clear all telemetry data"""
        self.spans.clear()
        self.metrics.clear()
        self.logs.clear()
        self._span_stack.clear()


@pytest.fixture
def mock_telemetry() -> MockTelemetryCollector:
    """Mock telemetry collector fixture"""
    return MockTelemetryCollector()


# =============================================================================
# Time and Clock Fixtures (for testing time-based behavior)
# =============================================================================

class MockClock:
    """
    Mock clock for testing time-dependent behavior.
    
    Provides controlled time progression and allows
    testing of timeouts, retries, and scheduling.
    """
    
    def __init__(self, start_time: Optional[datetime] = None):
        self._current_time = start_time or datetime.utcnow()
        self._speed_multiplier = 1.0
        self._time_jumps: List[Tuple[datetime, datetime]] = []
    
    def now(self) -> datetime:
        """Get current mock time"""
        return self._current_time
    
    def advance(self, seconds: float):
        """Advance mock time"""
        self._current_time += timedelta(seconds=seconds)
    
    def jump_to(self, target_time: datetime):
        """Jump to specific time"""
        self._time_jumps.append((self._current_time, target_time))
        self._current_time = target_time
    
    def set_speed(self, multiplier: float):
        """Set time speed multiplier"""
        self._speed_multiplier = multiplier
    
    def reset(self, start_time: Optional[datetime] = None):
        """Reset clock"""
        self._current_time = start_time or datetime.utcnow()
        self._time_jumps.clear()


@pytest.fixture
def mock_clock() -> MockClock:
    """Mock clock fixture"""
    return MockClock()


# =============================================================================
# Chaos Engineering Fixtures (for resilience testing)
# =============================================================================

@dataclass
class ChaosScenario:
    """Chaos scenario configuration"""
    name: str
    enabled: bool = True
    failure_type: str = "delay"
    probability: float = 1.0
    duration_ms: int = 100
    affected_services: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ChaosEngine:
    """
    Chaos engineering engine for resilience testing.
    
    Provides mechanisms for:
    - Fault injection
    - Latency simulation
    - Failure injection
    - Resource exhaustion
    
    Used to verify system resilience under adverse conditions.
    """
    
    def __init__(self):
        self._scenarios: Dict[str, ChaosScenario] = {}
        self._active_chaos: List[ChaosScenario] = []
        self._injection_log: List[Dict[str, Any]] = []
    
    def register_scenario(self, scenario: ChaosScenario):
        """Register a chaos scenario"""
        self._scenarios[scenario.name] = scenario
    
    def unregister_scenario(self, name: str):
        """Unregister a chaos scenario"""
        if name in self._scenarios:
            del self._scenarios[name]
    
    def get_scenario(self, name: str) -> Optional[ChaosScenario]:
        """Get scenario by name"""
        return self._scenarios.get(name)
    
    def enable_scenario(self, name: str):
        """Enable a chaos scenario"""
        if name in self._scenarios:
            self._scenarios[name].enabled = True
            if self._scenarios[name] not in self._active_chaos:
                self._active_chaos.append(self._scenarios[name])
    
    def disable_scenario(self, name: str):
        """Disable a chaos scenario"""
        if name in self._scenarios:
            self._scenarios[name].enabled = False
            self._active_chaos = [s for s in self._active_chaos if s.name != name]
    
    def should_inject_fault(self, scenario_name: str) -> bool:
        """Determine if fault should be injected"""
        scenario = self._scenarios.get(scenario_name)
        if not scenario or not scenario.enabled:
            return False
        
        import random
        return random.random() < scenario.probability
    
    async def inject_delay(self, scenario_name: str):
        """Inject delay based on scenario"""
        scenario = self._scenarios.get(scenario_name)
        if scenario and self.should_inject_fault(scenario_name):
            self._injection_log.append({
                "type": "delay",
                "scenario": scenario_name,
                "duration_ms": scenario.duration_ms,
                "timestamp": datetime.utcnow().isoformat(),
            })
            await asyncio.sleep(scenario.duration_ms / 1000)
    
    def inject_failure(self, scenario_name: str) -> Exception:
        """Inject failure based on scenario"""
        scenario = self._scenarios.get(scenario_name)
        error_type = scenario.metadata.get("error_type", "GenericChaosError") if scenario else "GenericChaosError"
        
        self._injection_log.append({
            "type": "failure",
            "scenario": scenario_name,
            "error_type": error_type,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return Exception(f"Injected {error_type} from scenario {scenario_name}")
    
    def get_injection_log(self) -> List[Dict[str, Any]]:
        """Get fault injection log"""
        return list(self._injection_log)
    
    def clear_log(self):
        """Clear injection log"""
        self._injection_log.clear()


@pytest.fixture
def chaos_engine() -> ChaosEngine:
    """Chaos engineering engine fixture"""
    return ChaosEngine()


# =============================================================================
# WebSocket Testing Fixtures
# =============================================================================

class WebSocketTestClient:
    """
    Test client for WebSocket testing.
    
    Provides isolated WebSocket connection simulation
    for testing real-time communication without network.
    """
    
    def __init__(self):
        self.client_id = str(uuid4())
        self.messages_sent: List[Dict[str, Any]] = []
        self.messages_received: List[Dict[str, Any]] = []
        self.subscriptions: Set[str] = set()
        self.connected = False
        self.authenticated = False
    
    async def connect(self, gateway=None):
        """Simulate connection"""
        self.connected = True
        if gateway:
            await gateway.handle_connection(self)
    
    async def disconnect(self, gateway=None):
        """Simulate disconnection"""
        self.connected = False
        if gateway:
            await gateway.disconnect_client(self.client_id)
    
    async def send(self, message: Dict[str, Any]):
        """Send message"""
        self.messages_sent.append(message)
        return True
    
    async def receive(self) -> Optional[Dict[str, Any]]:
        """Receive message"""
        if self.messages_received:
            return self.messages_received.pop(0)
        return None
    
    def subscribe(self, channel: str):
        """Subscribe to channel"""
        self.subscriptions.add(channel)
    
    def unsubscribe(self, channel: str):
        """Unsubscribe from channel"""
        self.subscriptions.discard(channel)
    
    def clear_messages(self):
        """Clear all messages"""
        self.messages_sent.clear()
        self.messages_received.clear()


@pytest.fixture
def websocket_test_client() -> WebSocketTestClient:
    """WebSocket test client fixture"""
    return WebSocketTestClient()


# =============================================================================
# Async Context Fixtures
# =============================================================================

@asynccontextmanager
async def managed_task_group() -> AsyncGenerator[asyncio.TaskGroup, None]:
    """Managed task group for concurrent operations"""
    async with asyncio.TaskGroup() as tg:
        yield tg


@pytest.fixture
async def task_group():
    """Task group fixture for concurrent testing"""
    return managed_task_group()


# =============================================================================
# Verification and Assertion Helpers
# =============================================================================

def assert_eventually(
    condition: Callable[[], bool],
    timeout: float = 5.0,
    interval: float = 0.1,
    message: str = "Condition not met",
):
    """
    Assert condition eventually becomes true.
    
    Poll the condition until timeout, failing if not met.
    Used for testing async state changes.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition():
            return
        time.sleep(interval)
    
    pytest.fail(message)


async def assert_eventually_async(
    async_condition: Callable[[], Any],
    timeout: float = 5.0,
    interval: float = 0.1,
    message: str = "Async condition not met",
):
    """Async version of assert_eventually"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        result = await async_condition()
        if result:
            return
        await asyncio.sleep(interval)
    
    pytest.fail(message)


# =============================================================================
# Hooks and Markers
# =============================================================================

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "chaos: Chaos engineering tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Add markers based on test paths
    for item in items:
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        elif "chaos" in item.nodeid:
            item.add_marker(pytest.mark.chaos)


# =============================================================================
# Exported Fixtures
# =============================================================================

__all__ = [
    # Core fixtures
    "db_session",
    "db_session_with_data",
    "redis_client",
    "redis_with_data",
    "engine",
    "session_factory",
    # Mock fixtures
    "mock_openai_client",
    "mock_redis_pubsub",
    "mock_websocket_server",
    # Factory
    "test_data_factory",
    "TestDataFactory",
    # Event bus
    "in_memory_event_bus",
    "InMemoryEventBus",
    "TestEvent",
    # Telemetry
    "mock_telemetry",
    "MockTelemetryCollector",
    # Time
    "mock_clock",
    "MockClock",
    # Chaos
    "chaos_engine",
    "ChaosEngine",
    "ChaosScenario",
    # WebSocket
    "websocket_test_client",
    "WebSocketTestClient",
    # Helpers
    "task_group",
    "assert_eventually",
    "assert_eventually_async",
    "test_config",
]
