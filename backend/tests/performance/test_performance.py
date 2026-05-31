"""
43V3R CORE - Performance Tests
================================

Production-grade performance and load testing:

1. Benchmark Infrastructure
   - Async operation benchmarks
   - Database operation benchmarks
   - Memory profiling
   - Latency measurements

2. Load Testing Scenarios
   - Concurrent request handling
   - Throughput testing
   - Scalability validation

3. Memory and Resource Tests
   - Memory leak detection
   - Resource exhaustion testing
   - Connection pool testing

Markers: performance, benchmarks
"""

from __future__ import annotations

import asyncio
import gc
import psutil
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import logging

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.runtime.services import (
    RuntimeCoordinator,
    ExecutionManager,
)
from app.domains.semantic.services import SemanticAnalyzer
from app.domains.distributed_runtime.services import DistributedContextManager

logger = logging.getLogger(__name__)


# =============================================================================
# Performance Metrics
# =============================================================================

@dataclass
class PerformanceMetrics:
    """Performance metrics for benchmarking"""
    operation: str
    iterations: int
    total_time_ms: float
    average_time_ms: float
    min_time_ms: float
    max_time_ms: float
    p50_time_ms: float
    p95_time_ms: float
    p99_time_ms: float
    throughput_per_sec: float
    memory_delta_bytes: int
    cpu_percent: float


@dataclass
class LoadTestMetrics:
    """Load test metrics"""
    concurrent_requests: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_rps: float
    error_rate: float


# =============================================================================
# Benchmark Utilities
# =============================================================================

class BenchmarkRunner:
    """
    Benchmark runner for measuring operation performance.
    
    Provides statistical analysis of operation timings,
    memory usage, and resource consumption.
    """
    
    def __init__(self):
        self.results: List[PerformanceMetrics] = []
    
    async def benchmark(
        self,
        operation: Callable,
        iterations: int = 100,
        warmup: int = 10,
        name: Optional[str] = None,
        *args,
        **kwargs,
    ) -> PerformanceMetrics:
        """
        Benchmark an async operation.
        
        Returns comprehensive performance metrics.
        """
        operation_name = name or getattr(operation, '__name__', 'unknown')
        
        # Warmup
        for _ in range(warmup):
            await operation(*args, **kwargs)
        
        # Collect timings
        timings: List[float] = []
        gc.collect()
        process = psutil.Process()
        mem_before = process.memory_info().rss
        
        for _ in range(iterations):
            start = time.perf_counter()
            await operation(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            timings.append(elapsed)
        
        gc.collect()
        mem_after = process.memory_info().rss
        
        # Calculate statistics
        timings.sort()
        n = len(timings)
        
        total_time = sum(timings)
        avg_time = total_time / n
        min_time = timings[0]
        max_time = timings[-1]
        p50 = timings[n // 2]
        p95 = timings[int(n * 0.95)]
        p99 = timings[int(n * 0.99)]
        
        throughput = 1000 / avg_time if avg_time > 0 else 0
        memory_delta = mem_after - mem_before
        cpu_percent = process.cpu_percent()
        
        metrics = PerformanceMetrics(
            operation=operation_name,
            iterations=iterations,
            total_time_ms=total_time,
            average_time_ms=avg_time,
            min_time_ms=min_time,
            max_time_ms=max_time,
            p50_time_ms=p50,
            p95_time_ms=p95,
            p99_time_ms=p99,
            throughput_per_sec=throughput,
            memory_delta_bytes=memory_delta,
            cpu_percent=cpu_percent,
        )
        
        self.results.append(metrics)
        return metrics
    
    def benchmark_sync(
        self,
        operation: Callable,
        iterations: int = 100,
        warmup: int = 10,
        name: Optional[str] = None,
        *args,
        **kwargs,
    ) -> PerformanceMetrics:
        """Benchmark a synchronous operation"""
        operation_name = name or getattr(operation, '__name__', 'unknown')
        
        # Warmup
        for _ in range(warmup):
            operation(*args, **kwargs)
        
        # Collect timings
        timings: List[float] = []
        gc.collect()
        process = psutil.Process()
        mem_before = process.memory_info().rss
        
        for _ in range(iterations):
            start = time.perf_counter()
            operation(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            timings.append(elapsed)
        
        gc.collect()
        mem_after = process.memory_info().rss
        
        # Calculate statistics
        timings.sort()
        n = len(timings)
        
        total_time = sum(timings)
        avg_time = total_time / n
        min_time = timings[0]
        max_time = timings[-1]
        p50 = timings[n // 2]
        p95 = timings[int(n * 0.95)]
        p99 = timings[int(n * 0.99)]
        
        throughput = 1000 / avg_time if avg_time > 0 else 0
        memory_delta = mem_after - mem_before
        cpu_percent = process.cpu_percent()
        
        metrics = PerformanceMetrics(
            operation=operation_name,
            iterations=iterations,
            total_time_ms=total_time,
            average_time_ms=avg_time,
            min_time_ms=min_time,
            max_time_ms=max_time,
            p50_time_ms=p50,
            p95_time_ms=p95,
            p99_time_ms=p99,
            throughput_per_sec=throughput,
            memory_delta_bytes=memory_delta,
            cpu_percent=cpu_percent,
        )
        
        self.results.append(metrics)
        return metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all benchmark results"""
        return {
            "total_benchmarks": len(self.results),
            "results": [
                {
                    "operation": r.operation,
                    "avg_ms": r.average_time_ms,
                    "p95_ms": r.p95_time_ms,
                    "throughput": r.throughput_per_sec,
                }
                for r in self.results
            ],
        }


class LoadTestRunner:
    """
    Load test runner for concurrent request testing.
    
    Simulates concurrent load and measures:
    - Throughput (requests per second)
    - Latency distribution
    - Error rates
    - Resource usage
    """
    
    def __init__(self):
        self.results: Optional[LoadTestMetrics] = None
    
    async def run_load_test(
        self,
        operation: Callable,
        concurrent_users: int = 10,
        requests_per_user: int = 100,
        timeout: float = 60.0,
    ) -> LoadTestMetrics:
        """
        Run a load test with concurrent users.
        
        Each user runs requests_per_user requests concurrently.
        """
        latencies: List[float] = []
        errors: int = 0
        successful: int = 0
        
        async def user_session(user_id: int):
            nonlocal successful, errors
            
            for _ in range(requests_per_user):
                start = time.perf_counter()
                
                try:
                    if asyncio.iscoroutinefunction(operation):
                        await asyncio.wait_for(
                            operation(),
                            timeout=timeout / requests_per_user,
                        )
                    else:
                        operation()
                    
                    elapsed = (time.perf_counter() - start) * 1000
                    latencies.append(elapsed)
                    successful += 1
                    
                except Exception as e:
                    errors += 1
                    latencies.append(timeout * 1000)
        
        # Run concurrent user sessions
        start_time = time.time()
        
        tasks = [user_session(i) for i in range(concurrent_users)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        total_requests = successful + errors
        
        # Calculate metrics
        latencies.sort()
        n = len(latencies)
        
        avg_latency = sum(latencies) / n if n > 0 else 0
        p95 = latencies[int(n * 0.95)] if n > 0 else 0
        p99 = latencies[int(n * 0.99)] if n > 0 else 0
        throughput = total_requests / total_time if total_time > 0 else 0
        error_rate = errors / total_requests if total_requests > 0 else 0
        
        self.results = LoadTestMetrics(
            concurrent_requests=concurrent_users,
            total_requests=total_requests,
            successful_requests=successful,
            failed_requests=errors,
            average_latency_ms=avg_latency,
            p95_latency_ms=p95,
            p99_latency_ms=p99,
            throughput_rps=throughput,
            error_rate=error_rate,
        )
        
        return self.results


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def benchmark_runner() -> BenchmarkRunner:
    """Benchmark runner fixture"""
    return BenchmarkRunner()


@pytest.fixture
def load_test_runner() -> LoadTestRunner:
    """Load test runner fixture"""
    return LoadTestRunner()


# =============================================================================
# Runtime Performance Tests
# =============================================================================

class TestRuntimePerformance:
    """Performance tests for runtime orchestration"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_session_creation_performance(
        self,
        benchmark_runner: BenchmarkRunner,
        db_session: AsyncSession,
    ):
        """Benchmark session creation"""
        coordinator = RuntimeCoordinator(db_session)
        await coordinator.initialize()
        
        async def create_session():
            return await coordinator.create_session(
                name=f"perf-session-{time.time()}",
                session_type="performance",
            )
        
        metrics = await benchmark_runner.benchmark(
            create_session,
            iterations=50,
            warmup=5,
            name="session_creation",
        )
        
        assert metrics.average_time_ms < 100  # Should be under 100ms
        logger.info(f"Session creation: {metrics.average_time_ms:.2f}ms avg")
        
        await coordinator.shutdown()
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_workflow_creation_performance(
        self,
        benchmark_runner: BenchmarkRunner,
        db_session: AsyncSession,
    ):
        """Benchmark workflow creation"""
        coordinator = RuntimeCoordinator(db_session)
        executor = ExecutionManager(db_session, coordinator)
        await coordinator.initialize()
        
        async def create_workflow():
            return await executor.create_workflow(
                name=f"perf-workflow-{time.time()}",
                nodes=[{"id": "perf-node"}],
                edges=[],
            )
        
        metrics = await benchmark_runner.benchmark(
            create_workflow,
            iterations=50,
            warmup=5,
            name="workflow_creation",
        )
        
        assert metrics.average_time_ms < 150  # Should be under 150ms
        logger.info(f"Workflow creation: {metrics.average_time_ms:.2f}ms avg")
        
        await coordinator.shutdown()
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_event_emission_performance(
        self,
        benchmark_runner: BenchmarkRunner,
        db_session: AsyncSession,
    ):
        """Benchmark event emission"""
        coordinator = RuntimeCoordinator(db_session)
        await coordinator.initialize()
        
        from app.domains.runtime.services import OrchestrationEvent
        
        async def emit_event():
            return await coordinator.emit_event(
                OrchestrationEvent(
                    event_id=f"perf-event-{time.time()}",
                    event_type="test.event",
                    source="perf",
                    timestamp=datetime.utcnow(),
                    data={},
                )
            )
        
        metrics = await benchmark_runner.benchmark(
            emit_event,
            iterations=100,
            warmup=10,
            name="event_emission",
        )
        
        assert metrics.average_time_ms < 50  # Should be under 50ms
        logger.info(f"Event emission: {metrics.average_time_ms:.2f}ms avg")
        
        await coordinator.shutdown()


# =============================================================================
# Semantic Performance Tests
# =============================================================================

class TestSemanticPerformance:
    """Performance tests for semantic analysis"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_media_analysis_performance(
        self,
        benchmark_runner: BenchmarkRunner,
        db_session: AsyncSession,
    ):
        """Benchmark media semantic analysis"""
        analyzer = SemanticAnalyzer(db_session)
        await analyzer.initialize()
        
        async def analyze_media():
            return await analyzer.analyze_media(
                asset_id=f"perf-asset-{time.time()}",
                media_type="video/mp4",
                duration=30.0,
                audio_features={"bpm": 120, "beats": [{"timestamp": 0}]},
            )
        
        metrics = await benchmark_runner.benchmark(
            analyze_media,
            iterations=30,
            warmup=3,
            name="media_analysis",
        )
        
        assert metrics.average_time_ms < 200  # Should be under 200ms
        logger.info(f"Media analysis: {metrics.average_time_ms:.2f}ms avg")
        
        await analyzer.shutdown()


# =============================================================================
# Distributed Runtime Performance Tests
# =============================================================================

class TestDistributedRuntimePerformance:
    """Performance tests for distributed runtime"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_context_creation_performance(
        self,
        benchmark_runner: BenchmarkRunner,
        db_session: AsyncSession,
    ):
        """Benchmark distributed context creation"""
        context_manager = DistributedContextManager(db_session)
        await context_manager.initialize()
        
        async def create_context():
            return await context_manager.create_context(
                scope="execution",
                context_data={"perf": True},
            )
        
        metrics = await benchmark_runner.benchmark(
            create_context,
            iterations=50,
            warmup=5,
            name="context_creation",
        )
        
        assert metrics.average_time_ms < 100
        logger.info(f"Context creation: {metrics.average_time_ms:.2f}ms avg")
        
        await context_manager.shutdown()
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_context_propagation_performance(
        self,
        benchmark_runner: BenchmarkRunner,
        db_session: AsyncSession,
    ):
        """Benchmark context propagation"""
        context_manager = DistributedContextManager(db_session)
        await context_manager.initialize()
        
        # Create context first
        context = await context_manager.create_context(
            scope="session",
            context_data={},
        )
        
        from uuid import uuid4
        
        async def propagate_context():
            return await context_manager.propagate_context(
                context_id=context.context_id,
                target_node_id=uuid4(),
                target_service="perf-target",
            )
        
        metrics = await benchmark_runner.benchmark(
            propagate_context,
            iterations=50,
            warmup=5,
            name="context_propagation",
        )
        
        assert metrics.average_time_ms < 50
        logger.info(f"Context propagation: {metrics.average_time_ms:.2f}ms avg")
        
        await context_manager.shutdown()


# =============================================================================
# Load Tests
# =============================================================================

class TestLoadHandling:
    """Load testing for concurrent operations"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_session_creation(
        self,
        load_test_runner: LoadTestRunner,
        db_session: AsyncSession,
    ):
        """Test concurrent session creation under load"""
        coordinator = RuntimeCoordinator(db_session)
        await coordinator.initialize()
        
        counter = {"value": 0}
        
        async def create_session():
            counter["value"] += 1
            await coordinator.create_session(
                name=f"load-session-{counter['value']}",
                session_type="load_test",
            )
        
        metrics = await load_test_runner.run_load_test(
            create_session,
            concurrent_users=5,
            requests_per_user=20,
        )
        
        assert metrics.error_rate < 0.05  # Less than 5% errors
        assert metrics.average_latency_ms < 200
        logger.info(f"Load test: {metrics.throughput_rps:.2f} req/s, {metrics.error_rate:.2%} errors")
        
        await coordinator.shutdown()
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_event_emission(
        self,
        load_test_runner: LoadTestRunner,
        db_session: AsyncSession,
    ):
        """Test concurrent event emission under load"""
        coordinator = RuntimeCoordinator(db_session)
        await coordinator.initialize()
        
        from app.domains.runtime.services import OrchestrationEvent
        
        async def emit_event():
            await coordinator.emit_event(
                OrchestrationEvent(
                    event_id=f"load-event-{time.time()}",
                    event_type="load.event",
                    source="load_test",
                    timestamp=datetime.utcnow(),
                    data={},
                )
            )
        
        metrics = await load_test_runner.run_load_test(
            emit_event,
            concurrent_users=10,
            requests_per_user=50,
        )
        
        assert metrics.error_rate < 0.01  # Less than 1% errors
        assert metrics.p95_latency_ms < 100
        logger.info(f"Event load: {metrics.throughput_rps:.2f} events/s")
        
        await coordinator.shutdown()


# =============================================================================
# Memory Tests
# =============================================================================

class TestMemoryUsage:
    """Memory usage and leak detection tests"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_stability(
        self,
        benchmark_runner: BenchmarkRunner,
        db_session: AsyncSession,
    ):
        """Test memory stability during repeated operations"""
        coordinator = RuntimeCoordinator(db_session)
        await coordinator.initialize()
        
        import psutil
        process = psutil.Process()
        
        # Get initial memory
        gc.collect()
        initial_memory = process.memory_info().rss
        
        # Run many operations
        for i in range(100):
            await coordinator.create_session(
                name=f"memory-test-{i}",
                session_type="memory",
            )
        
        # Check final memory
        gc.collect()
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable (less than 100MB)
        assert memory_growth < 100 * 1024 * 1024
        logger.info(f"Memory growth: {memory_growth / 1024 / 1024:.2f} MB")
        
        await coordinator.shutdown()
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_connection_pool_stability(
        self,
        db_session: AsyncSession,
    ):
        """Test connection pool stability"""
        coordinator = RuntimeCoordinator(db_session)
        await coordinator.initialize()
        
        # Create and close many sessions
        sessions = []
        for i in range(50):
            session = await coordinator.create_session(
                name=f"pool-test-{i}",
                session_type="pool",
            )
            sessions.append(session)
        
        # Verify all sessions are accessible
        for session in sessions:
            retrieved = await coordinator.get_session(session.id)
            assert retrieved is not None
        
        logger.info(f"Connection pool stable with {len(sessions)} sessions")
        
        await coordinator.shutdown()


# =============================================================================
# Scalability Tests
# =============================================================================

class TestScalability:
    """Scalability validation tests"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_horizontal_scaling_simulation(
        self,
        db_session: AsyncSession,
    ):
        """Simulate horizontal scaling behavior"""
        coordinator = RuntimeCoordinator(db_session)
        await coordinator.initialize()
        
        # Measure time to create sessions at different "scales"
        scale_results = []
        
        for scale in [10, 50, 100]:
            start = time.time()
            
            tasks = []
            for i in range(scale):
                task = coordinator.create_session(
                    name=f"scale-test-{scale}-{i}",
                    session_type="scaling",
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            elapsed = time.time() - start
            throughput = scale / elapsed
            
            scale_results.append({
                "scale": scale,
                "time": elapsed,
                "throughput": throughput,
            })
        
        # Verify throughput doesn't degrade too much
        # With proper scaling, throughput should remain relatively stable
        first_throughput = scale_results[0]["throughput"]
        last_throughput = scale_results[-1]["throughput"]
        degradation = (first_throughput - last_throughput) / first_throughput
        
        # Allow 50% degradation at high scale
        assert degradation < 0.5
        logger.info(f"Scaling test: {scale_results}")
        
        await coordinator.shutdown()
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_event_throughput_limits(
        self,
        db_session: AsyncSession,
    ):
        """Test event processing throughput limits"""
        coordinator = RuntimeCoordinator(db_session)
        await coordinator.initialize()
        
        from app.domains.runtime.services import OrchestrationEvent
        
        event_count = 1000
        
        start = time.time()
        
        tasks = []
        for i in range(event_count):
            task = coordinator.emit_event(
                OrchestrationEvent(
                    event_id=f"throughput-test-{i}",
                    event_type="throughput.event",
                    source="throughput_test",
                    timestamp=datetime.utcnow(),
                    data={"index": i},
                )
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        elapsed = time.time() - start
        throughput = event_count / elapsed
        
        assert throughput > 100  # Should handle > 100 events/sec
        logger.info(f"Event throughput: {throughput:.2f} events/sec")
        
        await coordinator.shutdown()
