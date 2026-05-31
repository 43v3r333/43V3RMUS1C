"""
43V3R CORE - Constitutional Governance Unit Tests
==================================================

Comprehensive unit tests for constitutional governance systems:
- ConstitutionalGovernanceEngine: Profile management, action evaluation
- InvariantPolicyManager: Invariant policy CRUD, violation detection
- CognitionBoundaryEnforcer: Boundary enforcement, limit validation
- RecursiveSafetyGovernance: Safety state tracking, collapse prevention
- SystemicConstraintSupervisor: Constraint evaluation
- ConstitutionalAuditService: Audit trail management
- GovernanceBoundaryValidator: Boundary validation

Test Coverage:
- Constitutional profile creation and evaluation
- Invariant policy lifecycle
- Cognition boundary enforcement
- Recursive safety state transitions
- Constraint violation tracking
- Audit trail operations
- Boundary validation

Markers: unit, governance, constitutional_governance
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.constitutional_governance.models import (
    ConstraintSeverity,
    GovernanceScope,
    BoundaryType,
    InvariantType,
    SafetyState,
    ConstitutionalProfile,
    InvariantPolicy,
    CognitionBoundary,
    RecursiveSafetyRule,
    SystemicConstraint,
    ConstitutionalAudit,
    GovernanceBoundary,
    ConstraintViolation,
)
from app.domains.constitutional_governance.services import (
    ConstitutionalGovernanceEngine,
    InvariantPolicyManager,
    CognitionBoundaryEnforcer,
    RecursiveSafetyGovernance,
    SystemicConstraintSupervisor,
    ConstitutionalAuditService,
    GovernanceBoundaryValidator,
    ConstitutionalDecision,
    InvariantValidationResult,
    BoundaryAssessment,
    SafetyAssessment,
)


# =============================================================================
# ConstitutionalGovernanceEngine Tests
# =============================================================================

class TestConstitutionalGovernanceEngine:
    """Test suite for ConstitutionalGovernanceEngine"""
    
    @pytest_asyncio.fixture
    async def engine(
        self,
        db_session: AsyncSession,
    ) -> ConstitutionalGovernanceEngine:
        """Create governance engine for testing"""
        eng = ConstitutionalGovernanceEngine(db_session)
        await eng.initialize()
        yield eng
        await eng.shutdown()
    
    # ----------------------------------------------------------------
    # Initialization Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_engine_initialization(self, engine: ConstitutionalGovernanceEngine):
        """Test engine initializes correctly"""
        assert engine is not None
        assert engine._running is True
        assert isinstance(engine._profiles, dict)
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_engine_shutdown(self, engine: ConstitutionalGovernanceEngine):
        """Test engine shuts down gracefully"""
        await engine.shutdown()
        assert engine._running is False
    
    # ----------------------------------------------------------------
    # Profile Management Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_create_profile(
        self,
        engine: ConstitutionalGovernanceEngine,
        db_session: AsyncSession,
    ):
        """Test constitutional profile creation"""
        profile = await engine.create_profile(
            profile_scope="orchestration",
            profile_key="test-governance",
            governance_scope=GovernanceScope.ECOSYSTEM,
            max_violations=5,
            severity_cap=ConstraintSeverity.HIGH,
        )
        
        assert profile is not None
        assert profile.profile_id.startswith("con_profile_")
        assert profile.profile_scope == "orchestration"
        assert profile.profile_key == "test-governance"
        assert profile.governance_scope == GovernanceScope.ECOSYSTEM.value
        assert profile.max_violations_per_cycle == 5
        assert profile.violation_severity_cap == ConstraintSeverity.HIGH.value
        assert profile.is_active is True
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_create_profile_with_defaults(
        self,
        engine: ConstitutionalGovernanceEngine,
        db_session: AsyncSession,
    ):
        """Test profile creation with default values"""
        profile = await engine.create_profile(
            profile_scope="test",
            profile_key="default-test",
        )
        
        assert profile.max_violations_per_cycle == 3  # default
        assert profile.violation_severity_cap == ConstraintSeverity.HIGH.value  # default
        assert profile.auto_remediation_enabled is True  # default
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_get_profile(
        self,
        engine: ConstitutionalGovernanceEngine,
        db_session: AsyncSession,
    ):
        """Test profile retrieval"""
        created = await engine.create_profile(
            profile_scope="retrieval-test",
            profile_key="retrieval-key",
        )
        
        retrieved = await engine.get_profile(created.profile_id)
        
        assert retrieved is not None
        assert retrieved.profile_id == created.profile_id
    
    # ----------------------------------------------------------------
    # Constitutional Action Evaluation Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_evaluate_action_permissive_without_profile(
        self,
        engine: ConstitutionalGovernanceEngine,
    ):
        """Test action evaluation is permissive when no profile exists"""
        decision = await engine.evaluate_constitutional_action(
            scope="nonexistent",
            action={"action": "test"},
            current_state={},
        )
        
        assert decision.approved is True
        assert decision.reason == "no profile found"
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_evaluate_action_approves_valid_action(
        self,
        engine: ConstitutionalGovernanceEngine,
        db_session: AsyncSession,
    ):
        """Test valid action is approved"""
        profile = await engine.create_profile(
            profile_scope="evaluation-test",
            profile_key="eval-key",
        )
        
        decision = await engine.evaluate_constitutional_action(
            scope="evaluation-test",
            action={"type": "allow", "severity": "info"},
            current_state={"violation_count": 0, "safety_score": 1.0},
            profile_id=profile.profile_id,
        )
        
        assert decision.approved is True
        assert decision.action == "allow"
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_evaluate_action_denies_violation_limit(
        self,
        engine: ConstitutionalGovernanceEngine,
        db_session: AsyncSession,
    ):
        """Test action denied when violation limit exceeded"""
        profile = await engine.create_profile(
            profile_scope="violation-limit-test",
            profile_key="violation-limit-key",
            max_violations=3,
        )
        
        decision = await engine.evaluate_constitutional_action(
            scope="violation-limit-test",
            action={"type": "deny"},
            current_state={"violation_count": 5, "safety_score": 1.0},
            profile_id=profile.profile_id,
        )
        
        assert decision.approved is False
        assert "violation_limit_exceeded" in decision.violations
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_evaluate_action_denies_severity_cap_exceeded(
        self,
        engine: ConstitutionalGovernanceEngine,
        db_session: AsyncSession,
    ):
        """Test action denied when severity exceeds cap"""
        profile = await engine.create_profile(
            profile_scope="severity-cap-test",
            profile_key="severity-cap-key",
            severity_cap=ConstraintSeverity.MODERATE,
        )
        
        decision = await engine.evaluate_constitutional_action(
            scope="severity-cap-test",
            action={"type": "action", "severity": "critical"},
            current_state={"violation_count": 0, "safety_score": 1.0},
            profile_id=profile.profile_id,
        )
        
        assert decision.approved is False
        assert "severity_cap_exceeded" in decision.violations
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_evaluate_action_emergency_shutdown(
        self,
        engine: ConstitutionalGovernanceEngine,
        db_session: AsyncSession,
    ):
        """Test emergency shutdown when safety score too low"""
        profile = await engine.create_profile(
            profile_scope="safety-test",
            profile_key="safety-key",
            emergency_shutdown_threshold=0.2,
        )
        
        decision = await engine.evaluate_constitutional_action(
            scope="safety-test",
            action={"type": "action"},
            current_state={"violation_count": 0, "safety_score": 0.1},
            profile_id=profile.profile_id,
        )
        
        assert decision.approved is False
        assert decision.action == "emergency_shutdown"
        assert decision.severity == ConstraintSeverity.CRITICAL
    
    # ----------------------------------------------------------------
    # Safety State Assessment Tests
    # ----------------------------------------------------------------
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_assess_safety_state_nominal(
        self,
        engine: ConstitutionalGovernanceEngine,
        db_session: AsyncSession,
    ):
        """Test safety assessment for nominal state"""
        profile = await engine.create_profile(
            profile_scope="safety-assessment-test",
            profile_key="safety-assessment-key",
        )
        
        assessment = await engine.assess_safety_state(
            profile_id=profile.profile_id,
            current_state={"risk_score": 0.1, "violation_rate": 0.05},
        )
        
        assert assessment.safety_state == SafetyState.NOMINAL
        assert assessment.risk_score == 0.1
        assert assessment.collapse_probability < 0.3
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_assess_safety_state_warning(
        self,
        engine: ConstitutionalGovernanceEngine,
        db_session: AsyncSession,
    ):
        """Test safety assessment for warning state"""
        profile = await engine.create_profile(
            profile_scope="warning-assessment-test",
            profile_key="warning-assessment-key",
        )
        
        assessment = await engine.assess_safety_state(
            profile_id=profile.profile_id,
            current_state={"risk_score": 0.6, "violation_rate": 0.2},
        )
        
        assert assessment.safety_state in [
            SafetyState.WARNING,
            SafetyState.CAUTION,
        ]
        assert assessment.risk_score >= 0.6


# =============================================================================
# InvariantPolicyManager Tests
# =============================================================================

class TestInvariantPolicyManager:
    """Test suite for InvariantPolicyManager"""
    
    @pytest_asyncio.fixture
    async def policy_manager(
        self,
        db_session: AsyncSession,
    ) -> InvariantPolicyManager:
        """Create policy manager for testing"""
        manager = InvariantPolicyManager(db_session)
        await manager.initialize()
        yield manager
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_create_policy(
        self,
        policy_manager: InvariantPolicyManager,
        db_session: AsyncSession,
    ):
        """Test invariant policy creation"""
        policy = await policy_manager.create_policy(
            policy_scope="execution",
            policy_key="test-invariant",
            invariant_type=InvariantType.SAFETY,
            invariant_expression="x > 0",
            constraint_type="range",
        )
        
        assert policy is not None
        assert policy.policy_id.startswith("inv_policy_")
        assert policy.policy_scope == "execution"
        assert policy.invariant_type == InvariantType.SAFETY.value
        assert policy.invariant_expression == "x > 0"
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_create_policy_with_preconditions(
        self,
        policy_manager: InvariantPolicyManager,
        db_session: AsyncSession,
    ):
        """Test policy with preconditions"""
        policy = await policy_manager.create_policy(
            policy_scope="test",
            policy_key="precond-policy",
            invariant_type=InvariantType.CONSISTENCY,
            invariant_expression="state.valid",
            constraint_type="check",
            preconditions={"system_state": "initialized"},
        )
        
        assert policy.preconditions is not None
        assert policy.preconditions.get("system_state") == "initialized"
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_evaluate_policy_valid(
        self,
        policy_manager: InvariantPolicyManager,
        db_session: AsyncSession,
    ):
        """Test policy evaluation with valid state"""
        policy = await policy_manager.create_policy(
            policy_scope="valid-test",
            policy_key="valid-policy",
            invariant_type=InvariantType.SAFETY,
            invariant_expression="counter < 100",
            constraint_type="range",
            constraint_parameters={"metric": "counter", "max": 100},
        )
        
        result = await policy_manager.evaluate_policy(
            policy_id=policy.policy_id,
            component_states={"counter": 50},
        )
        
        assert result.is_valid is True
        assert len(result.violations) == 0
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_evaluate_policy_invalid(
        self,
        policy_manager: InvariantPolicyManager,
        db_session: AsyncSession,
    ):
        """Test policy evaluation with invalid state"""
        policy = await policy_manager.create_policy(
            policy_scope="invalid-test",
            policy_key="invalid-policy",
            invariant_type=InvariantType.SAFETY,
            invariant_expression="counter < 100",
            constraint_type="range",
            constraint_parameters={"metric": "counter", "max": 100},
        )
        
        result = await policy_manager.evaluate_policy(
            policy_id=policy.policy_id,
            component_states={"counter": 150},
        )
        
        assert result.is_valid is False
        assert len(result.violations) > 0
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_get_policies_by_scope(
        self,
        policy_manager: InvariantPolicyManager,
        db_session: AsyncSession,
    ):
        """Test retrieving policies by scope"""
        await policy_manager.create_policy(
            policy_scope="specific-scope",
            policy_key="policy1",
            invariant_type=InvariantType.SAFETY,
            invariant_expression="x > 0",
            constraint_type="check",
        )
        await policy_manager.create_policy(
            policy_scope="specific-scope",
            policy_key="policy2",
            invariant_type=InvariantType.CONSISTENCY,
            invariant_expression="y != 0",
            constraint_type="check",
        )
        await policy_manager.create_policy(
            policy_scope="other-scope",
            policy_key="policy3",
            invariant_type=InvariantType.INTEGRITY,
            invariant_expression="z == true",
            constraint_type="check",
        )
        
        policies = await policy_manager.get_policies_by_scope("specific-scope")
        
        assert len(policies) >= 2
        assert all(p.policy_scope == "specific-scope" for p in policies)


# =============================================================================
# CognitionBoundaryEnforcer Tests
# =============================================================================

class TestCognitionBoundaryEnforcer:
    """Test suite for CognitionBoundaryEnforcer"""
    
    @pytest_asyncio.fixture
    async def enforcer(
        self,
        db_session: AsyncSession,
    ) -> CognitionBoundaryEnforcer:
        """Create boundary enforcer for testing"""
        enf = CognitionBoundaryEnforcer(db_session)
        await enf.initialize()
        yield enf
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_create_boundary(
        self,
        enforcer: CognitionBoundaryEnforcer,
        db_session: AsyncSession,
    ):
        """Test cognition boundary creation"""
        boundary = await enforcer.create_boundary(
            boundary_scope="recursive_depth",
            boundary_key="max_depth",
            max_depth=10,
            max_iterations=100,
        )
        
        assert boundary is not None
        assert boundary.boundary_id.startswith("cog_boundary_")
        assert boundary.boundary_type == BoundaryType.HARD_LIMIT.value
        assert boundary.max_depth == 10
        assert boundary.max_iterations == 100
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_enforce_boundary_within_limits(
        self,
        enforcer: CognitionBoundaryEnforcer,
        db_session: AsyncSession,
    ):
        """Test boundary enforcement within limits"""
        boundary = await enforcer.create_boundary(
            boundary_scope="depth-test",
            boundary_key="depth-limit",
            max_depth=10,
        )
        
        assessment = await enforcer.enforce_boundary(
            boundary_id=boundary.boundary_id,
            current_depth=5,
        )
        
        assert assessment.within_bounds is True
        assert assessment.current_value == 5
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_enforce_boundary_exceeded(
        self,
        enforcer: CognitionBoundaryEnforcer,
        db_session: AsyncSession,
    ):
        """Test boundary enforcement when limit exceeded"""
        boundary = await enforcer.create_boundary(
            boundary_scope="exceeded-test",
            boundary_key="exceeded-limit",
            max_depth=10,
        )
        
        assessment = await enforcer.enforce_boundary(
            boundary_id=boundary.boundary_id,
            current_depth=15,
        )
        
        assert assessment.within_bounds is False
        assert len(assessment.violations) > 0


# =============================================================================
# RecursiveSafetyGovernance Tests
# =============================================================================

class TestRecursiveSafetyGovernance:
    """Test suite for RecursiveSafetyGovernance"""
    
    @pytest_asyncio.fixture
    async def safety_governance(
        self,
        db_session: AsyncSession,
    ) -> RecursiveSafetyGovernance:
        """Create safety governance for testing"""
        gov = RecursiveSafetyGovernance(db_session)
        await gov.initialize()
        yield gov
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_initialize_default_rules(
        self,
        safety_governance: RecursiveSafetyGovernance,
    ):
        """Test initialization creates default safety rules"""
        assert len(safety_governance._rules) > 0
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_evaluate_safety_state_nominal(
        self,
        safety_governance: RecursiveSafetyGovernance,
        db_session: AsyncSession,
    ):
        """Test safety evaluation for nominal state"""
        assessment = await safety_governance.evaluate_safety_state(
            metrics={
                "recursion_depth": 5,
                "violation_rate": 0.01,
                "memory_usage": 0.3,
            },
        )
        
        assert assessment.safety_state in [SafetyState.NOMINAL, SafetyState.CAUTION]
        assert assessment.risk_score < 0.5
        assert assessment.collapse_probability < 0.2
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_evaluate_safety_state_critical(
        self,
        safety_governance: RecursiveSafetyGovernance,
        db_session: AsyncSession,
    ):
        """Test safety evaluation for critical state"""
        assessment = await safety_governance.evaluate_safety_state(
            metrics={
                "recursion_depth": 50,
                "violation_rate": 0.8,
                "memory_usage": 0.95,
            },
        )
        
        assert assessment.safety_state in [
            SafetyState.CRITICAL,
            SafetyState.COLLAPSE,
        ]
        assert assessment.risk_score > 0.7
        assert assessment.collapse_probability > 0.5
        assert assessment.interventions_needed is True
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_create_safety_rule(
        self,
        safety_governance: RecursiveSafetyGovernance,
        db_session: AsyncSession,
    ):
        """Test creating custom safety rule"""
        rule = await safety_governance.create_safety_rule(
            rule_key="custom_safety",
            rule_type="threshold",
            threshold_value=0.8,
            severity=ConstraintSeverity.HIGH,
        )
        
        assert rule is not None
        assert rule.rule_id.startswith("rec_safety_")
        assert rule.rule_key == "custom_safety"
        assert rule.threshold_value == 0.8


# =============================================================================
# ConstitutionalAuditService Tests
# =============================================================================

class TestConstitutionalAuditService:
    """Test suite for ConstitutionalAuditService"""
    
    @pytest_asyncio.fixture
    async def audit_service(
        self,
        db_session: AsyncSession,
    ) -> ConstitutionalAuditService:
        """Create audit service for testing"""
        return ConstitutionalAuditService(db_session)
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_log_action(
        self,
        audit_service: ConstitutionalAuditService,
        db_session: AsyncSession,
    ):
        """Test logging constitutional action"""
        audit = await audit_service.log_action(
            action_type="evaluate",
            action_target="test-session",
            actor_type="engine",
            outcome_type="approved",
            success=True,
            pre_state={"count": 0},
            post_state={"count": 1},
        )
        
        assert audit is not None
        assert audit.audit_id.startswith("con_audit_")
        assert audit.action_type == "evaluate"
        assert audit.success is True
        assert audit.pre_state["count"] == 0
        assert audit.post_state["count"] == 1
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_log_action_with_violation(
        self,
        audit_service: ConstitutionalAuditService,
        db_session: AsyncSession,
    ):
        """Test logging action with violation"""
        audit = await audit_service.log_action(
            action_type="enforce",
            action_target="constraint-1",
            actor_type="validator",
            outcome_type="denied",
            success=False,
            violation_detected=True,
        )
        
        assert audit.violation_detected is True
        assert audit.success is False
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_get_audit_trail(
        self,
        audit_service: ConstitutionalAuditService,
        db_session: AsyncSession,
    ):
        """Test retrieving audit trail"""
        # Log multiple actions
        await audit_service.log_action(
            action_type="test-action-1",
            action_target="target-1",
            actor_type="test",
            outcome_type="success",
        )
        await audit_service.log_action(
            action_type="test-action-2",
            action_target="target-2",
            actor_type="test",
            outcome_type="success",
        )
        
        trail = await audit_service.get_audit_trail(limit=10)
        
        assert len(trail) >= 2
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_get_audit_trail_filtered(
        self,
        audit_service: ConstitutionalAuditService,
        db_session: AsyncSession,
    ):
        """Test retrieving filtered audit trail"""
        await audit_service.log_action(
            action_type="specific-type",
            action_target="filter-target",
            actor_type="test",
            outcome_type="success",
        )
        await audit_service.log_action(
            action_type="other-type",
            action_target="filter-target",
            actor_type="test",
            outcome_type="success",
        )
        
        trail = await audit_service.get_audit_trail(action_type="specific-type")
        
        assert all(a.action_type == "specific-type" for a in trail)


# =============================================================================
# GovernanceBoundaryValidator Tests
# =============================================================================

class TestGovernanceBoundaryValidator:
    """Test suite for GovernanceBoundaryValidator"""
    
    @pytest_asyncio.fixture
    async def validator(
        self,
        db_session: AsyncSession,
    ) -> GovernanceBoundaryValidator:
        """Create boundary validator for testing"""
        val = GovernanceBoundaryValidator(db_session)
        await val.initialize()
        yield val
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_create_boundary(
        self,
        validator: GovernanceBoundaryValidator,
        db_session: AsyncSession,
    ):
        """Test governance boundary creation"""
        boundary = await validator.create_boundary(
            boundary_scope="rate-limit",
            boundary_type=BoundaryType.RATE_LIMIT,
            boundary_key="api-rate",
            min_value=0,
            max_value=1000,
        )
        
        assert boundary is not None
        assert boundary.boundary_id.startswith("gov_boundary_")
        assert boundary.boundary_type == BoundaryType.RATE_LIMIT.value
        assert boundary.max_value == 1000
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_validate_boundary_within_bounds(
        self,
        validator: GovernanceBoundaryValidator,
        db_session: AsyncSession,
    ):
        """Test validation when value within bounds"""
        boundary = await validator.create_boundary(
            boundary_scope="validation-test",
            boundary_type=BoundaryType.HARD_LIMIT,
            boundary_key="max-requests",
            max_value=100,
        )
        
        valid, violations = await validator.validate_boundary(
            boundary_id=boundary.boundary_id,
            value=50,
        )
        
        assert valid is True
        assert len(violations) == 0
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_validate_boundary_exceeds_max(
        self,
        validator: GovernanceBoundaryValidator,
        db_session: AsyncSession,
    ):
        """Test validation when value exceeds maximum"""
        boundary = await validator.create_boundary(
            boundary_scope="max-test",
            boundary_type=BoundaryType.HARD_LIMIT,
            boundary_key="max-value",
            max_value=100,
        )
        
        valid, violations = await validator.validate_boundary(
            boundary_id=boundary.boundary_id,
            value=150,
        )
        
        assert valid is False
        assert len(violations) > 0
        assert any("above maximum" in v for v in violations)
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_validate_boundary_below_min(
        self,
        validator: GovernanceBoundaryValidator,
        db_session: AsyncSession,
    ):
        """Test validation when value below minimum"""
        boundary = await validator.create_boundary(
            boundary_scope="min-test",
            boundary_type=BoundaryType.THRESHOLD,
            boundary_key="min-value",
            min_value=10,
        )
        
        valid, violations = await validator.validate_boundary(
            boundary_id=boundary.boundary_id,
            value=5,
        )
        
        assert valid is False
        assert any("below minimum" in v for v in violations)
    
    @pytest.mark.unit
    @pytest.mark.governance
    async def test_validate_boundary_nonexistent(
        self,
        validator: GovernanceBoundaryValidator,
    ):
        """Test validation with non-existent boundary is permissive"""
        valid, violations = await validator.validate_boundary(
            boundary_id="nonexistent-boundary",
            value=999,
        )
        
        assert valid is True
        assert len(violations) == 0


# =============================================================================
# Model Tests
# =============================================================================

class TestConstitutionalGovernanceModels:
    """Test suite for constitutional governance models"""
    
    @pytest.mark.unit
    @pytest.mark.governance
    def test_constraint_severity_enum_values(self):
        """Test ConstraintSeverity enum values"""
        assert ConstraintSeverity.INFO.value == "info"
        assert ConstraintSeverity.WARNING.value == "warning"
        assert ConstraintSeverity.MODERATE.value == "moderate"
        assert ConstraintSeverity.HIGH.value == "high"
        assert ConstraintSeverity.CRITICAL.value == "critical"
        assert ConstraintSeverity.BLOCKING.value == "blocking"
    
    @pytest.mark.unit
    @pytest.mark.governance
    def test_governance_scope_enum_values(self):
        """Test GovernanceScope enum values"""
        assert GovernanceScope.LOCAL.value == "local"
        assert GovernanceScope.ORCHESTRATION.value == "orchestration"
        assert GovernanceScope.SESSION.value == "session"
        assert GovernanceScope.DOMAIN.value == "domain"
        assert GovernanceScope.ECOSYSTEM.value == "ecosystem"
        assert GovernanceScope.GLOBAL.value == "global"
    
    @pytest.mark.unit
    @pytest.mark.governance
    def test_boundary_type_enum_values(self):
        """Test BoundaryType enum values"""
        assert BoundaryType.HARD_LIMIT.value == "hard_limit"
        assert BoundaryType.SOFT_LIMIT.value == "soft_limit"
        assert BoundaryType.THRESHOLD.value == "threshold"
        assert BoundaryType.RATE_LIMIT.value == "rate_limit"
        assert BoundaryType.RESOURCE.value == "resource"
        assert BoundaryType.SEMANTIC.value == "semantic"
    
    @pytest.mark.unit
    @pytest.mark.governance
    def test_invariant_type_enum_values(self):
        """Test InvariantType enum values"""
        assert InvariantType.SAFETY.value == "safety"
        assert InvariantType.CONSISTENCY.value == "consistency"
        assert InvariantType.INTEGRITY.value == "integrity"
        assert InvariantType.COHERENCE.value == "coherence"
        assert InvariantType.TERMINATION.value == "termination"
        assert InvariantType.RESOURCE.value == "resource"
        assert InvariantType.SECURITY.value == "security"
    
    @pytest.mark.unit
    @pytest.mark.governance
    def test_safety_state_enum_values(self):
        """Test SafetyState enum values"""
        assert SafetyState.NOMINAL.value == "nominal"
        assert SafetyState.CAUTION.value == "caution"
        assert SafetyState.WARNING.value == "warning"
        assert SafetyState.CRITICAL.value == "critical"
        assert SafetyState.COLLAPSE.value == "collapse"


# =============================================================================
# Data Class Tests
# =============================================================================

class TestConstitutionalGovernanceDataClasses:
    """Test suite for constitutional governance data classes"""
    
    @pytest.mark.unit
    @pytest.mark.governance
    def test_constitutional_decision(self):
        """Test ConstitutionalDecision dataclass"""
        decision = ConstitutionalDecision(
            approved=True,
            action="allow",
            reason="test passed",
            severity=ConstraintSeverity.INFO,
            violations=[],
            remediations=["remediate-1"],
            safety_state=SafetyState.NOMINAL,
            confidence=0.95,
        )
        
        assert decision.approved is True
        assert decision.action == "allow"
        assert decision.reason == "test passed"
        assert decision.severity == ConstraintSeverity.INFO
        assert decision.confidence == 0.95
    
    @pytest.mark.unit
    @pytest.mark.governance
    def test_invariant_validation_result(self):
        """Test InvariantValidationResult dataclass"""
        result = InvariantValidationResult(
            is_valid=True,
            constraint_id="constraint-1",
            violations=[],
            warnings=["minor-warning"],
            remediation_suggestions=["fix-this"],
            confidence=0.9,
        )
        
        assert result.is_valid is True
        assert result.constraint_id == "constraint-1"
        assert len(result.warnings) == 1
        assert len(result.remediation_suggestions) == 1
    
    @pytest.mark.unit
    @pytest.mark.governance
    def test_boundary_assessment(self):
        """Test BoundaryAssessment dataclass"""
        assessment = BoundaryAssessment(
            within_bounds=True,
            boundary_id="boundary-1",
            current_value=50.0,
            limit_type="max",
            distance_from_limit=50.0,
            violations=[],
        )
        
        assert assessment.within_bounds is True
        assert assessment.current_value == 50.0
        assert assessment.distance_from_limit == 50.0
    
    @pytest.mark.unit
    @pytest.mark.governance
    def test_safety_assessment(self):
        """Test SafetyAssessment dataclass"""
        assessment = SafetyAssessment(
            safety_state=SafetyState.NOMINAL,
            risk_score=0.2,
            collapse_probability=0.05,
            contributing_factors=["low-violation-rate"],
            recommendations=["continue-monitoring"],
            interventions_needed=False,
        )
        
        assert assessment.safety_state == SafetyState.NOMINAL
        assert assessment.risk_score == 0.2
        assert assessment.collapse_probability == 0.05
        assert assessment.interventions_needed is False
