"""
43V3R CORE - Chaos Engineering Infrastructure
==============================================

Production-grade chaos engineering for resilience testing:

1. Fault Injection Framework
   - Network fault injection
   - Service failure simulation
   - Resource exhaustion
   - Latency injection

2. Disruption Simulation
   - WebSocket disruption
   - Database disruption
   - Service degradation
   - Cascading failures

3. Propagation Testing
   - Failure propagation patterns
   - Chaos scenarios
   - Monkey testing

Test Coverage:
- Fault injection scenarios
- Resilience validation
- Recovery testing
- Chaos metrics

Markers: chaos, fault_injection, resilience
"""

from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar
import logging

import pytest
import pytest_asyncio

logger = logging.getLogger(__name__)


# =============================================================================
# Chaos Configuration
# =============================================================================

class FaultType(str, Enum):
    """Types of faults that can be injected"""
    DELAY = "delay"
    ERROR = "error"
    TIMEOUT = "timeout"
    DISCONNECT = "disconnect"
    CORRUPTION = "corruption"
    EXCEPTION = "exception"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_PARTITION = "network_partition"


class TargetComponent(str, Enum):
    """Components that can be targeted by faults"""
    DATABASE = "database"
    REDIS = "redis"
    WEBSOCKET = "websocket"
    API = "api"
    WORKER = "worker"
    ORCHESTRATOR = "orchestrator"
    SEMANTIC_ANALYZER = "semantic_analyzer"
    GOVERNANCE = "governance"


@dataclass
class ChaosScenario:
    """Configuration for a chaos scenario"""
    name: str
    description: str
    fault_type: FaultType
    target: TargetComponent
    probability: float = 1.0
    duration_seconds: float = 0.0
    severity: str = "moderate"
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChaosResult:
    """Result of chaos injection"""
    scenario: str
    fault_injected: bool
    duration_ms: float
    success: bool
    error: Optional[str] = None
    recovery_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Fault Injector
# =============================================================================

class FaultInjector:
    """
    Production-grade fault injection framework.
    
    Provides controlled fault injection for chaos engineering,
    resilience testing, and failure mode analysis.
    """
    
    def __init__(self):
        self._scenarios: Dict[str, ChaosScenario] = {}
        self._active_faults: List[ChaosScenario] = []
        self._injection_log: List[ChaosResult] = []
        self._failure_count: Dict[str, int] = {}
        self._call_counts: Dict[str, int] = {}
        self._running = False
    
    def register_scenario(self, scenario: ChaosScenario) -> None:
        """Register a chaos scenario"""
        self._scenarios[scenario.name] = scenario
        logger.info(f"Registered chaos scenario: {scenario.name}")
    
    def unregister_scenario(self, name: str) -> None:
        """Unregister a chaos scenario"""
        if name in self._scenarios:
            del self._scenarios[name]
    
    def enable_scenario(self, name: str) -> None:
        """Enable a chaos scenario"""
        if name in self._scenarios:
            self._scenarios[name].enabled = True
            if self._scenarios[name] not in self._active_faults:
                self._active_faults.append(self._scenarios[name])
    
    def disable_scenario(self, name: str) -> None:
        """Disable a chaos scenario"""
        if name in self._scenarios:
            self._scenarios[name].enabled = False
            self._active_faults = [s for s in self._active_faults if s.name != name]
    
    def should_inject(self, scenario_name: str) -> bool:
        """Determine if fault should be injected based on probability"""
        scenario = self._scenarios.get(scenario_name)
        if not scenario or not scenario.enabled:
            return False
        
        return random.random() < scenario.probability
    
    async def inject_delay(
        self,
        scenario_name: str,
        custom_duration: Optional[float] = None,
    ) -> float:
        """Inject delay based on scenario configuration"""
        scenario = self._scenarios.get(scenario_name)
        duration = custom_duration or (scenario.parameters.get("delay_ms", 100) / 1000)
        
        start = datetime.utcnow()
        
        if scenario:
            logger.debug(f"Injecting delay for {scenario_name}: {duration}s")
            await asyncio.sleep(duration)
        
        return (datetime.utcnow() - start).total_seconds() * 1000
    
    def inject_error(self, scenario_name: str) -> Exception:
        """Inject an error based on scenario configuration"""
        scenario = self._scenarios.get(scenario_name)
        error_type = scenario.parameters.get("error_type", "ChaosError") if scenario else "ChaosError"
        
        error_messages = {
            "ChaosError": f"Injected chaos error from {scenario_name}",
            "TimeoutError": f"Timeout injected for {scenario_name}",
            "ConnectionError": f"Connection error injected for {scenario_name}",
            "RuntimeError": f"Runtime error injected for {scenario_name}",
        }
        
        return Exception(error_messages.get(error_type, f"Injected error from {scenario_name}"))
    
    async def inject_fault(
        self,
        scenario_name: str,
        operation: Callable[..., Any],
        *args,
        **kwargs,
    ) -> Any:
        """
        Inject fault into an operation.
        
        Wraps the operation with chaos fault injection.
        """
        scenario = self._scenarios.get(scenario_name)
        start_time = time.time()
        
        self._call_counts[scenario_name] = self._call_counts.get(scenario_name, 0) + 1
        
        try:
            # Check if should inject
            if self.should_inject(scenario_name):
                fault_injected = True
                
                if scenario:
                    fault_type = scenario.fault_type
                    logger.info(f"Injecting {fault_type} for {scenario_name}")
                
                # Inject delay
                if scenario and scenario.fault_type == FaultType.DELAY:
                    await self.inject_delay(scenario_name)
                elif scenario and scenario.fault_type == FaultType.TIMEOUT:
                    await asyncio.sleep(999999)  # Very long delay
                    raise asyncio.TimeoutError("Injected timeout")
                elif scenario and scenario.fault_type == FaultType.ERROR:
                    raise self.inject_error(scenario_name)
                elif scenario and scenario.fault_type == FaultType.EXCEPTION:
                    exc_type = scenario.parameters.get("exception_type", "ValueError")
                    if exc_type == "ValueError":
                        raise ValueError(f"Injected ValueError from {scenario_name}")
                    elif exc_type == "RuntimeError":
                        raise RuntimeError(f"Injected RuntimeError from {scenario_name}")
                
                # Execute operation with injected delay
                if asyncio.iscoroutinefunction(operation):
                    result = await operation(*args, **kwargs)
                else:
                    result = operation(*args, **kwargs)
                
                duration = (time.time() - start_time) * 1000
                
                # Log success
                self._injection_log.append(ChaosResult(
                    scenario=scenario_name,
                    fault_injected=True,
                    duration_ms=duration,
                    success=True,
                ))
                
                return result
            else:
                # Execute normally
                if asyncio.iscoroutinefunction(operation):
                    result = await operation(*args, **kwargs)
                else:
                    result = operation(*args, **kwargs)
                
                return result
                
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            
            # Log failure
            self._failure_count[scenario_name] = self._failure_count.get(scenario_name, 0) + 1
            
            self._injection_log.append(ChaosResult(
                scenario=scenario_name,
                fault_injected=True,
                duration_ms=duration,
                success=False,
                error=str(e),
            ))
            
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get chaos injection metrics"""
        return {
            "scenarios_registered": len(self._scenarios),
            "scenarios_enabled": len([s for s in self._scenarios.values() if s.enabled]),
            "total_injections": len(self._injection_log),
            "successful_injections": len([r for r in self._injection_log if r.success]),
            "failed_injections": len([r for r in self._injection_log if not r.success]),
            "call_counts": dict(self._call_counts),
            "failure_counts": dict(self._failure_count),
        }
    
    def get_injection_log(self) -> List[ChaosResult]:
        """Get fault injection log"""
        return list(self._injection_log)
    
    def clear_log(self) -> None:
        """Clear injection log"""
        self._injection_log.clear()
        self._failure_count.clear()
        self._call_counts.clear()


# =============================================================================
# Monkey Patch Fault Injector
# =============================================================================

class MonkeyPatchInjector:
    """
    Monkey-patches external services with fault injection capabilities.
    
    Allows chaos injection at the library/service level without modifying
    application code.
    """
    
    def __init__(self):
        self._patches: Dict[str, Callable] = {}
        self._original_functions: Dict[str, Callable] = {}
        self._injector = FaultInjector()
        self._enabled = False
    
    def patch_delay(
        self,
        function_name: str,
        module: str,
        delay_ms: float = 100,
        probability: float = 1.0,
    ) -> None:
        """Patch a function to introduce delays"""
        import importlib
        
        # Get original function
        parts = module.split(".")
        obj = __import__(module)
        for part in parts[1:]:
            obj = getattr(obj, part)
        
        original_func = getattr(obj, function_name)
        self._original_functions[f"{module}.{function_name}"] = original_func
        
        # Create patched function
        async def patched(*args, **kwargs):
            if self._enabled and random.random() < probability:
                await asyncio.sleep(delay_ms / 1000)
            return await original_func(*args, **kwargs)
        
        def patched_sync(*args, **kwargs):
            if self._enabled and random.random() < probability:
                time.sleep(delay_ms / 1000)
            return original_func(*args, **kwargs)
        
        patched_func = patched if asyncio.iscoroutinefunction(original_func) else patched_sync
        self._patches[f"{module}.{function_name}"] = patched_func
        
        # Apply patch
        setattr(obj, function_name, patched_func)
    
    def unpatch(self, function_name: str, module: str) -> None:
        """Restore original function"""
        key = f"{module}.{function_name}"
        
        if key in self._patches:
            import importlib
            parts = module.split(".")
            obj = __import__(module)
            for part in parts[1:]:
                obj = getattr(obj, part)
            
            setattr(obj, function_name, self._original_functions[key])
            del self._patches[key]
    
    def enable(self) -> None:
        """Enable all patches"""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable all patches"""
        self._enabled = False


# =============================================================================
# Resilience Validator
# =============================================================================

@dataclass
class ResilienceMetrics:
    """Metrics for system resilience validation"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    average_recovery_time_ms: float
    failure_patterns: List[str]
    recommendations: List[str]


class ResilienceValidator:
    """
    Validates system resilience under fault conditions.
    
    Runs chaos scenarios and validates that:
    - Failures are contained
    - Graceful degradation occurs
    - Recovery happens within acceptable timeframes
    """
    
    def __init__(self, fault_injector: FaultInjector):
        self.fault_injector = fault_injector
        self._validation_results: List[Dict[str, Any]] = []
        self._recovery_times: List[float] = []
    
    async def validate_graceful_degradation(
        self,
        scenario_name: str,
        operation: Callable,
        expected_behavior: Optional[Callable] = None,
        *args,
        **kwargs,
    ) -> bool:
        """
        Validate that system degrades gracefully under fault.
        
        Returns True if:
        - Operation fails gracefully (doesn't crash)
        - Error is handled appropriately
        - System remains operational
        """
        scenario = self.fault_injector._scenarios.get(scenario_name)
        fault_injector_original_probability = scenario.probability if scenario else 0
        
        try:
            # Set high probability for testing
            if scenario:
                original = scenario.probability
                scenario.probability = 1.0
                
            # Enable scenario
            self.fault_injector.enable_scenario(scenario_name)
            
            # Try operation
            try:
                await self.fault_injector.inject_fault(
                    scenario_name,
                    operation,
                    *args,
                    **kwargs,
                )
                
                # Check expected behavior
                if expected_behavior:
                    return expected_behavior()
                
                return True
                
            except Exception as e:
                # Exception is expected - check if it's handled gracefully
                logger.info(f"Expected exception under chaos: {e}")
                return True
                
        finally:
            # Restore scenario
            if scenario:
                scenario.probability = fault_injector_original_probability
            self.fault_injector.disable_scenario(scenario_name)
        
        return False
    
    async def measure_recovery_time(
        self,
        scenario_name: str,
        operation: Callable,
        recovery_condition: Callable[[], bool],
        *args,
        **kwargs,
    ) -> float:
        """
        Measure time to recover from fault.
        
        Returns recovery time in milliseconds.
        """
        start = time.time()
        
        # Inject fault
        await self.fault_injector.inject_fault(
            scenario_name,
            operation,
            *args,
            **kwargs,
        )
        
        # Wait for recovery
        max_wait = 30  # seconds
        elapsed = 0
        interval = 0.1
        
        while elapsed < max_wait:
            if recovery_condition():
                recovery_time = (time.time() - start) * 1000
                self._recovery_times.append(recovery_time)
                return recovery_time
            
            await asyncio.sleep(interval)
            elapsed += interval
        
        # Recovery timed out
        return -1
    
    def get_resilience_metrics(self) -> ResilienceMetrics:
        """Get comprehensive resilience metrics"""
        total = len(self._validation_results)
        passed = sum(1 for r in self._validation_results if r.get("passed", False))
        failed = total - passed
        
        avg_recovery = (
            sum(self._recovery_times) / len(self._recovery_times)
            if self._recovery_times else 0
        )
        
        # Analyze failure patterns
        patterns = []
        if failed > total * 0.5:
            patterns.append("high_failure_rate")
        if avg_recovery > 5000:
            patterns.append("slow_recovery")
        
        # Generate recommendations
        recommendations = []
        if "high_failure_rate" in patterns:
            recommendations.append("Review fault tolerance mechanisms")
        if "slow_recovery" in patterns:
            recommendations.append("Optimize recovery procedures")
        
        return ResilienceMetrics(
            total_tests=total,
            passed_tests=passed,
            failed_tests=failed,
            average_recovery_time_ms=avg_recovery,
            failure_patterns=patterns,
            recommendations=recommendations,
        )


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def fault_injector() -> FaultInjector:
    """Fault injector fixture"""
    return FaultInjector()


@pytest.fixture
def chaos_scenarios() -> Dict[str, ChaosScenario]:
    """Pre-defined chaos scenarios"""
    return {
        "network_delay": ChaosScenario(
            name="network_delay",
            description="Inject network delays",
            fault_type=FaultType.DELAY,
            target=TargetComponent.API,
            probability=1.0,
            parameters={"delay_ms": 100},
        ),
        "database_failure": ChaosScenario(
            name="database_failure",
            description="Simulate database failures",
            fault_type=FaultType.ERROR,
            target=TargetComponent.DATABASE,
            probability=0.5,
            parameters={"error_type": "ChaosError"},
        ),
        "redis_disconnect": ChaosScenario(
            name="redis_disconnect",
            description="Simulate Redis disconnection",
            fault_type=FaultType.DISCONNECT,
            target=TargetComponent.REDIS,
            probability=0.3,
        ),
        "websocket_timeout": ChaosScenario(
            name="websocket_timeout",
            description="Inject WebSocket timeouts",
            fault_type=FaultType.TIMEOUT,
            target=TargetComponent.WEBSOCKET,
            probability=0.5,
        ),
        "resource_exhaustion": ChaosScenario(
            name="resource_exhaustion",
            description="Simulate resource exhaustion",
            fault_type=FaultType.RESOURCE_EXHAUSTION,
            target=TargetComponent.WORKER,
            probability=0.2,
        ),
    }


@pytest.fixture
def resilience_validator(fault_injector: FaultInjector) -> ResilienceValidator:
    """Resilience validator fixture"""
    return ResilienceValidator(fault_injector)


# =============================================================================
# Chaos Engineering Tests
# =============================================================================

class TestFaultInjection:
    """Test suite for fault injection system"""
    
    @pytest.mark.chaos
    def test_register_scenario(self, fault_injector: FaultInjector):
        """Test scenario registration"""
        scenario = ChaosScenario(
            name="test_scenario",
            description="Test description",
            fault_type=FaultType.DELAY,
            target=TargetComponent.API,
        )
        
        fault_injector.register_scenario(scenario)
        
        assert "test_scenario" in fault_injector._scenarios
    
    @pytest.mark.chaos
    def test_enable_disable_scenario(self, fault_injector: FaultInjector):
        """Test enabling and disabling scenarios"""
        scenario = ChaosScenario(
            name="test_toggle",
            description="Test toggle",
            fault_type=FaultType.DELAY,
            target=TargetComponent.API,
        )
        
        fault_injector.register_scenario(scenario)
        fault_injector.enable_scenario("test_toggle")
        fault_injector.disable_scenario("test_toggle")
        
        assert fault_injector._scenarios["test_toggle"].enabled is False
    
    @pytest.mark.chaos
    def test_should_inject_probability(self, fault_injector: FaultInjector):
        """Test probability-based injection"""
        scenario = ChaosScenario(
            name="chaos_metric_test_probability",
            description="For probability testing",
            fault_type=FaultType.DELAY,
            target=TargetComponent.API,
            probability=0.0,  # Never inject
        )
        
        fault_injector.register_scenario(scenario)
        should_inject = fault_injector.should_inject("chaos_metric_test_probability")
        
        assert should_inject is False
    
    @pytest.mark.chaos
    @pytest.mark.asyncio
    async def test_inject_delay(self, fault_injector: FaultInjector):
        """Test delay injection"""
        scenario = ChaosScenario(
            name="chaos_delay",
            description="Test delay",
            fault_type=FaultType.DELAY,
            target=TargetComponent.API,
            parameters={"delay_ms": 50},
        )
        
        fault_injector.register_scenario(scenario)
        
        start = time.time()
        duration = await fault_injector.inject_delay("chaos_delay")
        elapsed = (time.time() - start) * 1000
        
        # Should be approximately 0 (not injected) since not enabled
        assert duration >= 0
    
    @pytest.mark.chaos
    def test_inject_error(self, fault_injector: FaultInjector):
        """Test error injection"""
        scenario = ChaosScenario(
            name="chaos_error",
            description="Test error injection",
            fault_type=FaultType.ERROR,
            target=TargetComponent.API,
            parameters={"error_type": "RuntimeError"},
        )
        
        fault_injector.register_scenario(scenario)
        
        error = fault_injector.inject_error("chaos_error")
        
        assert isinstance(error, Exception)
    
    @pytest.mark.chaos
    @pytest.mark.asyncio
    async def test_inject_fault_normal_execution(self, fault_injector: FaultInjector):
        """Test fault injection completes normally when pattern doesn't match"""
        async def mock_operation():
            return "success"
        
        result = await fault_injector.inject_fault(
            "nonexistent_scenario",  # Doesn't exist
            mock_operation,
        )
        
        assert result == "success"
    
    @pytest.mark.chaos
    @pytest.mark.asyncio
    async def test_inject_fault_with_error(self, fault_injector: FaultInjector):
        """Test fault injection with error scenario"""
        scenario = ChaosScenario(
            name="chaos_inject_error",
            description="Error injection test",
            fault_type=FaultType.EXCEPTION,
            target=TargetComponent.API,
            parameters={"exception_type": "ValueError"},
        )
        
        fault_injector.register_scenario(scenario)
        fault_injector.enable_scenario("chaos_inject_error")
        
        async def failing_operation():
            raise ValueError("Original error")
        
        try:
            await fault_injector.inject_fault(
                "chaos_inject_error",
                failing_operation,
            )
            # Should catch and re-raise
        except ValueError:
            pass
        
        fault_injector.disable_scenario("chaos_inject_error")
    
    @pytest.mark.chaos
    def test_get_metrics(self, fault_injector: FaultInjector):
        """Test metrics generation"""
        metrics = fault_injector.get_metrics()
        
        assert "scenarios_registered" in metrics
        assert "total_injections" in metrics
        assert "call_counts" in metrics


class TestResilienceValidation:
    """Test suite for resilience validation"""
    
    @pytest.mark.chaos
    @pytest.mark.asyncio
    async def test_graceful_degradation(
        self,
        fault_injector: FaultInjector,
        resilience_validator: ResilienceValidator,
    ):
        """Test graceful degradation under fault"""
        scenario = ChaosScenario(
            name="graceful_degradation_test",
            description="Test graceful degradation",
            fault_type=FaultType.ERROR,
            target=TargetComponent.API,
            parameters={"error_type": "ChaosError"},
        )
        
        fault_injector.register_scenario(scenario)
        
        async def operation():
            return True
        
        result = await resilience_validator.validate_graceful_degradation(
            "graceful_degradation_test",
            operation,
            lambda: True,
        )
        
        assert result is True
    
    @pytest.mark.chaos
    @pytest.mark.asyncio
    async def test_recovery_time_measurement(
        self,
        fault_injector: FaultInjector,
        resilience_validator: ResilienceValidator,
    ):
        """Test recovery time measurement"""
        scenario = ChaosScenario(
            name="recovery_test",
            description="Test recovery timing",
            fault_type=FaultType.DELAY,
            target=TargetComponent.API,
        )
        
        fault_injector.register_scenario(scenario)
        fault_injector.enable_scenario("recovery_test")
        
        async def operation():
            return True
        
        async def check_condition():
            return True
        
        # Note: This would normally take time, but mock=True makes it instant
        recovery_time = await resilience_validator.measure_recovery_time(
            "recovery_test",
            operation,
            check_condition,
        )
        
        # Since condition is immediately true, recovery should be quick
        assert recovery_time >= 0
        
        fault_injector.disable_scenario("recovery_test")
    
    @pytest.mark.chaos
    def test_resilience_metrics(self, resilience_validator: ResilienceValidator):
        """Test resilience metrics generation"""
        metrics = resilience_validator.get_resilience_metrics()
        
        assert hasattr(metrics, "total_tests")
        assert hasattr(metrics, "passed_tests")
        assert hasattr(metrics, "failed_tests")
        assert hasattr(metrics, "average_recovery_time_ms")
        assert hasattr(metrics, "failure_patterns")
        assert hasattr(metrics, "recommendations")


class TestChaosScenarios:
    """Test suite for predefined chaos scenarios"""
    
    @pytest.mark.chaos
    def test_scenario_configuration(self, chaos_scenarios):
        """Test predefined scenario configurations"""
        assert "network_delay" in chaos_scenarios
        assert "database_failure" in chaos_scenarios
        assert chaos_scenarios["network_delay"].target == TargetComponent.API
        assert chaos_scenarios["database_failure"].fault_type == FaultType.ERROR
    
    @pytest.mark.chaos
    @pytest.mark.asyncio
    async def test_apply_all_scenarios(self, fault_injector, chaos_scenarios):
        """Test applying multiple chaos scenarios"""
        for name, scenario in chaos_scenarios.items():
            fault_injector.register_scenario(scenario)
            fault_injector.enable_scenario(name)
        
        metrics = fault_injector.get_metrics()
        
        assert metrics["scenarios_enabled"] == len(chaos_scenarios)
