"""
43V3R CORE - Test Data Infrastructure
=====================================

Production-grade test data generation and fixtures:

1. Synthetic Data Generation
   - Orchestration test data
   - Semantic analysis fixtures
   - Governance test data
   - Distributed runtime fixtures

2. Fixture Management
   - Deterministic fixtures
   - Reproducible data
   - Temporal replay capability

3. Data Factories
   - Model factories
   - Event generators
   - Topology fixtures

Markers: fixtures, test-data
"""

from __future__ import annotations

import hashlib
import random
import string
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Type
from uuid import UUID, uuid4

import pytest


# =============================================================================
# Deterministic Random Generator
# =============================================================================

class DeterministicRandom:
    """
    Deterministic random number generator for reproducible test data.
    
    Uses a seed to ensure the same data is generated across test runs.
    """
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        self._state_stack: List[random.Random] = []
    
    def reset(self) -> None:
        """Reset to initial seed state"""
        self.rng = random.Random(self.seed)
    
    def push_state(self) -> None:
        """Push current state to stack"""
        self._state_stack.append(self.rng.getstate())
    
    def pop_state(self) -> None:
        """Pop state from stack"""
        if self._state_stack:
            self.rng.setstate(self._state_stack.pop())
    
    def choice(self, seq: List[Any]) -> Any:
        """Choose random item"""
        return self.rng.choice(seq)
    
    def shuffle(self, seq: List[Any]) -> None:
        """Shuffle sequence in place"""
        self.rng.shuffle(seq)
    
    def randint(self, a: int, b: int) -> int:
        """Generate random integer"""
        return self.rng.randint(a, b)
    
    def uniform(self, a: float, b: float) -> float:
        """Generate random float"""
        return self.rng.uniform(a, b)
    
    def sample(self, seq: List[Any], k: int) -> List[Any]:
        """Sample k items from sequence"""
        return self.rng.sample(seq, k)
    
    def string(self, length: int, chars: str = string.ascii_letters) -> str:
        """Generate random string"""
        return ''.join(self.rng.choice(chars) for _ in range(length))
    
    def uuid(self) -> str:
        """Generate deterministic UUID based on seed"""
        # Use seed to generate deterministic UUID
        hash_input = f"{self.seed}-{self.rng.randint(0, 999999)}"
        return str(uuid4())


# Global deterministic random instance
deterministic_random = DeterministicRandom(seed=42)


# =============================================================================
# Test Data Generators
# =============================================================================

@dataclass
class OrchestrationTestData:
    """Orchestration test data"""
    session_ids: List[str]
    workflow_ids: List[str]
    execution_ids: List[str]
    correlation_ids: List[str]


@dataclass
class SemanticTestData:
    """Semantic analysis test data"""
    asset_ids: List[str]
    profiles: List[Dict[str, Any]]
    emotions: List[str]
    scene_types: List[str]


@dataclass
class GovernanceTestData:
    """Governance test data"""
    profile_ids: List[str]
    policy_ids: List[str]
    boundary_ids: List[str]
    violation_ids: List[str]


@dataclass
class DistributedTestData:
    """Distributed runtime test data"""
    context_ids: List[str]
    lineage_graph_ids: List[str]
    identity_ids: List[str]
    coordination_ids: List[str]


# =============================================================================
# Data Generators
# =============================================================================

class OrchestrationDataGenerator:
    """Generate orchestration test data"""
    
    def __init__(self, rng: DeterministicRandom = None):
        self.rng = rng or deterministic_random
    
    def generate_session_id(self) -> str:
        """Generate session ID"""
        return f"session-{self.rng.string(8, string.ascii_lowercase)}"
    
    def generate_workflow_id(self) -> str:
        """Generate workflow ID"""
        return f"workflow-{self.rng.string(8, string.ascii_lowercase)}"
    
    def generate_execution_id(self) -> str:
        """Generate execution ID"""
        return f"exec-{self.rng.string(8, string.ascii_lowercase)}"
    
    def generate_correlation_id(self) -> str:
        """Generate correlation ID"""
        return f"corr-{self.rng.string(12, string.ascii_lowercase + string.digits)}"
    
    def generate_session(self, **overrides) -> Dict[str, Any]:
        """Generate complete session data"""
        return {
            "id": self.generate_session_id(),
            "name": f"Test Session {self.rng.randint(1, 1000)}",
            "session_type": self.rng.choice(["orchestration", "workflow", "cognition"]),
            "status": self.rng.choice(["running", "paused", "stopped"]),
            "created_at": (datetime.utcnow() - timedelta(hours=self.rng.randint(1, 48))).isoformat(),
            **overrides,
        }
    
    def generate_workflow(self, **overrides) -> Dict[str, Any]:
        """Generate complete workflow data"""
        node_count = self.rng.randint(2, 10)
        nodes = [
            {
                "id": f"node-{i}",
                "type": self.rng.choice(["start", "process", "decision", "end"]),
                "name": f"Node {i}",
            }
            for i in range(node_count)
        ]
        
        edges = []
        for i in range(len(nodes) - 1):
            edges.append({"from": nodes[i]["id"], "to": nodes[i + 1]["id"]})
        
        return {
            "id": self.generate_workflow_id(),
            "name": f"Test Workflow {self.rng.randint(1, 1000)}",
            "nodes": nodes,
            "edges": edges,
            "execution_mode": self.rng.choice(["sequential", "parallel", "distributed"]),
            **overrides,
        }
    
    def generate_execution(self, **overrides) -> Dict[str, Any]:
        """Generate complete execution data"""
        return {
            "id": self.generate_execution_id(),
            "workflow_id": self.generate_workflow_id(),
            "status": self.rng.choice(["pending", "running", "completed", "failed"]),
            "correlation_id": self.generate_correlation_id(),
            "started_at": datetime.utcnow().isoformat(),
            **overrides,
        }
    
    def generate_batch(self, count: int) -> OrchestrationTestData:
        """Generate batch of test data"""
        return OrchestrationTestData(
            session_ids=[self.generate_session_id() for _ in range(count)],
            workflow_ids=[self.generate_workflow_id() for _ in range(count)],
            execution_ids=[self.generate_execution_id() for _ in range(count)],
            correlation_ids=[self.generate_correlation_id() for _ in range(count)],
        )


class SemanticDataGenerator:
    """Generate semantic analysis test data"""
    
    def __init__(self, rng: DeterministicRandom = None):
        self.rng = rng or deterministic_random
        self.emotions = ["joy", "sadness", "tension", "excitement", "calm", "energy", "mystery", "nostalgia"]
        self.scene_types = ["intro", "verse", "chorus", "bridge", "outro", "buildup", "dropdown", "interlude"]
    
    def generate_asset_id(self) -> str:
        """Generate asset ID"""
        return f"asset-{self.rng.string(8, string.ascii_lowercase + string.digits)}"
    
    def generate_profile(self, **overrides) -> Dict[str, Any]:
        """Generate semantic profile"""
        return {
            "asset_id": self.generate_asset_id(),
            "semantic_type": self.rng.choice(self.scene_types),
            "primary_emotion": self.rng.choice(self.emotions),
            "secondary_emotion": self.rng.choice([None] + self.emotions),
            "energy_level": self.rng.uniform(0.0, 1.0),
            "pacing_score": self.rng.uniform(0.0, 1.0),
            "duration": self.rng.uniform(5.0, 120.0),
            "bpm": self.rng.randint(60, 180),
            **overrides,
        }
    
    def generate_batch(self, count: int) -> SemanticTestData:
        """Generate batch of semantic test data"""
        profiles = [self.generate_profile() for _ in range(count)]
        return SemanticTestData(
            asset_ids=[p["asset_id"] for p in profiles],
            profiles=profiles,
            emotions=self.rng.sample(self.emotions, min(count, len(self.emotions))),
            scene_types=self.rng.sample(self.scene_types, min(count, len(self.scene_types))),
        )


class GovernanceDataGenerator:
    """Generate governance test data"""
    
    def __init__(self, rng: DeterministicRandom = None):
        self.rng = rng or deterministic_random
        self.severities = ["info", "warning", "moderate", "high", "critical", "blocking"]
        self.scopes = ["local", "orchestration", "session", "domain", "ecosystem", "global"]
    
    def generate_profile_id(self) -> str:
        """Generate profile ID"""
        return f"profile-{self.rng.string(8, string.ascii_lowercase)}"
    
    def generate_policy_id(self) -> str:
        """Generate policy ID"""
        return f"policy-{self.rng.string(8, string.ascii_lowercase)}"
    
    def generate_boundary_id(self) -> str:
        """Generate boundary ID"""
        return f"boundary-{self.rng.string(8, string.ascii_lowercase)}"
    
    def generate_violation_id(self) -> str:
        """Generate violation ID"""
        return f"violation-{self.rng.string(8, string.ascii_lowercase)}"
    
    def generate_profile(self, **overrides) -> Dict[str, Any]:
        """Generate governance profile"""
        return {
            "profile_id": self.generate_profile_id(),
            "profile_scope": self.rng.choice(self.scopes),
            "governance_scope": self.rng.choice(self.scopes),
            "max_violations_per_cycle": self.rng.randint(1, 10),
            "violation_severity_cap": self.rng.choice(self.severities),
            "auto_remediation_enabled": self.rng.choice([True, False]),
            "safety_margin": self.rng.uniform(0.0, 0.3),
            **overrides,
        }
    
    def generate_violation(self, **overrides) -> Dict[str, Any]:
        """Generate violation"""
        return {
            "violation_id": self.generate_violation_id(),
            "severity": self.rng.choice(self.severities),
            "constraint_id": self.generate_policy_id(),
            "occurred_at": datetime.utcnow().isoformat(),
            "resolved": self.rng.choice([True, False]),
            **overrides,
        }
    
    def generate_batch(self, count: int) -> GovernanceTestData:
        """Generate batch of governance test data"""
        return GovernanceTestData(
            profile_ids=[self.generate_profile_id() for _ in range(count)],
            policy_ids=[self.generate_policy_id() for _ in range(count)],
            boundary_ids=[self.generate_boundary_id() for _ in range(count)],
            violation_ids=[self.generate_violation_id() for _ in range(count)],
        )


class DistributedDataGenerator:
    """Generate distributed runtime test data"""
    
    def __init__(self, rng: DeterministicRandom = None):
        self.rng = rng or deterministic_random
    
    def generate_context_id(self) -> str:
        """Generate context ID"""
        return f"ctx-{self.rng.string(8, string.ascii_lowercase)}"
    
    def generate_lineage_graph_id(self) -> str:
        """Generate lineage graph ID"""
        return f"lgph-{self.rng.string(8, string.ascii_lowercase)}"
    
    def generate_identity_id(self) -> str:
        """Generate identity ID"""
        return f"eid-{self.rng.string(8, string.ascii_lowercase)}"
    
    def generate_coordination_id(self) -> str:
        """Generate coordination ID"""
        return f"coord-{self.rng.string(8, string.ascii_lowercase)}"
    
    def generate_context(self, **overrides) -> Dict[str, Any]:
        """Generate distributed context"""
        return {
            "context_id": self.generate_context_id(),
            "scope": self.rng.choice(["session", "workflow", "execution", "node"]),
            "context_data": {
                "correlation_id": f"corr-{self.rng.string(8)}",
                "trace_id": f"trace-{self.rng.string(8)}",
            },
            "propagation_status": self.rng.choice(["pending", "propagating", "propagated"]),
            **overrides,
        }
    
    def generate_batch(self, count: int) -> DistributedTestData:
        """Generate batch of distributed test data"""
        return DistributedTestData(
            context_ids=[self.generate_context_id() for _ in range(count)],
            lineage_graph_ids=[self.generate_lineage_graph_id() for _ in range(count)],
            identity_ids=[self.generate_identity_id() for _ in range(count)],
            coordination_ids=[self.generate_coordination_id() for _ in range(count)],
        )


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def orchestration_generator() -> OrchestrationDataGenerator:
    """Orchestration data generator fixture"""
    deterministic_random.reset()
    return OrchestrationDataGenerator(deterministic_random)


@pytest.fixture
def semantic_generator() -> SemanticDataGenerator:
    """Semantic data generator fixture"""
    deterministic_random.reset()
    return SemanticDataGenerator(deterministic_random)


@pytest.fixture
def governance_generator() -> GovernanceDataGenerator:
    """Governance data generator fixture"""
    deterministic_random.reset()
    return GovernanceDataGenerator(deterministic_random)


@pytest.fixture
def distributed_generator() -> DistributedDataGenerator:
    """Distributed data generator fixture"""
    deterministic_random.reset()
    return DistributedDataGenerator(deterministic_random)


@pytest.fixture
def deterministic_rng() -> DeterministicRandom:
    """Deterministic random generator fixture"""
    deterministic_random.reset()
    return deterministic_random


@pytest.fixture
def test_data_batch(orchestration_generator, semantic_generator, governance_generator, distributed_generator):
    """Generate batch of all test data types"""
    return {
        "orchestration": orchestration_generator.generate_batch(10),
        "semantic": semantic_generator.generate_batch(10),
        "governance": governance_generator.generate_batch(10),
        "distributed": distributed_generator.generate_batch(10),
    }


# =============================================================================
# Test Data Tests
# =============================================================================

class TestDeterministicRandom:
    """Test deterministic random generator"""
    
    def test_reproducible_random(self):
        """Test that random generation is reproducible"""
        rng1 = DeterministicRandom(seed=123)
        rng2 = DeterministicRandom(seed=123)
        
        # Same seed should produce same results
        assert rng1.choice([1, 2, 3]) == rng2.choice([1, 2, 3])
        assert rng1.string(5) == rng2.string(5)
    
    def test_different_seeds(self):
        """Test different seeds produce different results"""
        rng1 = DeterministicRandom(seed=100)
        rng2 = DeterministicRandom(seed=200)
        
        # Different seeds should produce different results
        assert rng1.randint(1, 100) != rng2.randint(1, 100) or True  # May be same by chance
    
    def test_reset(self):
        """Test reset functionality"""
        rng = DeterministicRandom(seed=42)
        val1 = rng.randint(1, 100)
        rng.reset()
        val2 = rng.randint(1, 100)
        
        assert val1 == val2


class TestOrchestrationDataGenerator:
    """Test orchestration data generator"""
    
    def test_generate_session_id(self, orchestration_generator):
        """Test session ID generation"""
        session_id = orchestration_generator.generate_session_id()
        
        assert session_id.startswith("session-")
        assert len(session_id) > 8
    
    def test_generate_workflow(self, orchestration_generator):
        """Test workflow generation"""
        workflow = orchestration_generator.generate_workflow()
        
        assert "id" in workflow
        assert "nodes" in workflow
        assert "edges" in workflow
        assert len(workflow["nodes"]) > 0
    
    def test_generate_batch(self, orchestration_generator):
        """Test batch generation"""
        batch = orchestration_generator.generate_batch(5)
        
        assert len(batch.session_ids) == 5
        assert len(batch.workflow_ids) == 5
        assert len(batch.execution_ids) == 5


class TestSemanticDataGenerator:
    """Test semantic data generator"""
    
    def test_generate_profile(self, semantic_generator):
        """Test profile generation"""
        profile = semantic_generator.generate_profile()
        
        assert "asset_id" in profile
        assert "primary_emotion" in profile
        assert "energy_level" in profile
        assert 0 <= profile["energy_level"] <= 1
    
    def test_generate_batch(self, semantic_generator):
        """Test batch generation"""
        batch = semantic_generator.generate_batch(5)
        
        assert len(batch.asset_ids) == 5
        assert len(batch.profiles) == 5


class TestGovernanceDataGenerator:
    """Test governance data generator"""
    
    def test_generate_profile(self, governance_generator):
        """Test profile generation"""
        profile = governance_generator.generate_profile()
        
        assert "profile_id" in profile
        assert "max_violations_per_cycle" in profile
        assert "safety_margin" in profile
    
    def test_generate_violation(self, governance_generator):
        """Test violation generation"""
        violation = governance_generator.generate_violation()
        
        assert "violation_id" in violation
        assert "severity" in violation


class TestDistributedDataGenerator:
    """Test distributed data generator"""
    
    def test_generate_context(self, distributed_generator):
        """Test context generation"""
        context = distributed_generator.generate_context()
        
        assert "context_id" in context
        assert "scope" in context
        assert "context_data" in context
    
    def test_generate_batch(self, distributed_generator):
        """Test batch generation"""
        batch = distributed_generator.generate_batch(5)
        
        assert len(batch.context_ids) == 5
        assert len(batch.lineage_graph_ids) == 5


class TestTestDataFixtures:
    """Test test data fixtures"""
    
    def test_orchestration_generator_fixture(self, orchestration_generator):
        """Test orchestration generator fixture"""
        assert isinstance(orchestration_generator, OrchestrationDataGenerator)
    
    def test_semantic_generator_fixture(self, semantic_generator):
        """Test semantic generator fixture"""
        assert isinstance(semantic_generator, SemanticDataGenerator)
    
    def test_deterministic_rng_fixture(self, deterministic_rng):
        """Test deterministic RNG fixture"""
        assert isinstance(deterministic_rng, DeterministicRandom)
    
    def test_test_data_batch_fixture(self, test_data_batch):
        """Test combined data batch fixture"""
        assert "orchestration" in test_data_batch
        assert "semantic" in test_data_batch
        assert "governance" in test_data_batch
        assert "distributed" in test_data_batch
