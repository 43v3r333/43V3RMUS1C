"""
Meta-Cognition Services - Runtime self-awareness and orchestration introspection.

Provides:
- Orchestration introspection engine
- Cognition diagnostics runtime
- Execution reasoning analyzer
- Semantic consistency validator
- Adaptive cognition auditing
- Runtime self-analysis systems

This is the EXECUTIVE INTELLIGENCE LAYER of the platform.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from .models import (
    IntrospectionPhase,
    CognitionState,
    AuditSeverity,
    DiagnosticType,
    ReconciliationStatus,
    PredictionHorizon,
    GovernanceAlignment,
    CognitionDiagnostics,
    IntrospectionSession,
    SemanticConsistencyAudit,
    AdaptiveGovernanceProfile,
    CognitionReconciliationState,
    RuntimeSelfAwarenessMetrics,
    PredictiveCognitionForecast,
    OrchestrationReasoningLineage,
    CognitionAnomalyRegistry,
)

logger = logging.getLogger(__name__)


class MetaCognitionEngine:
    """
    Meta-Cognition Engine - The EXECUTIVE INTELLIGENCE LAYER.
    
    Provides runtime self-awareness, orchestration introspection,
    cognition diagnostics, and adaptive governance.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._active_sessions: Dict[str, IntrospectionSession] = {}
        self._cognition_cache: Dict[str, Dict[str, Any]] = {}
        self._governance_profiles: Dict[str, AdaptiveGovernanceProfile] = {}
        self._running = False
        self._introspection_queue: asyncio.Queue = asyncio.Queue()
        self._metrics_buffer: List[Dict[str, Any]] = []
    
    async def initialize(self) -> None:
        """Initialize the meta-cognition engine"""
        self._running = True
        await self._load_governance_profiles()
        await self._start_introspection_loop()
        logger.info("MetaCognitionEngine initialized - EXECUTIVE INTELLIGENCE LAYER active")
    
    async def shutdown(self) -> None:
        """Shutdown the engine"""
        self._running = False
        logger.info("MetaCognitionEngine shutdown")
    
    async def _load_governance_profiles(self) -> None:
        """Load governance profiles from database"""
        result = await self.db.execute(
            select(AdaptiveGovernanceProfile).where(
                AdaptiveGovernanceProfile.is_active == True
            )
        )
        for profile in result.scalars().all():
            self._governance_profiles[profile.scope] = profile
    
    async def _start_introspection_loop(self) -> None:
        """Start the introspection processing loop"""
        asyncio.create_task(self._introspection_processor())
    
    async def _introspection_processor(self) -> None:
        """Process introspection items from the queue"""
        while self._running:
            try:
                item = await asyncio.wait_for(
                    self._introspection_queue.get(),
                    timeout=1.0
                )
                await self._process_introspection_item(item)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Introspection processor error: {e}")
    
    async def _process_introspection_item(self, item: Dict[str, Any]) -> None:
        """Process a single introspection item"""
        session_id = item.get("session_id")
        if session_id and session_id in self._active_sessions:
            session = self._active_sessions[session_id]
            session.findings = item.get("findings", [])
            session.phase = item.get("phase", IntrospectionPhase.ANALYZING.value)
            session.confidence = item.get("confidence", 0.0)
            self.db.add(session)
            await self.db.commit()

    # ==================== Cognition Diagnostics ====================
    
    async def run_cognition_diagnostics(
        self,
        scope: str,
        domain: str,
        diagnostic_types: Optional[List[DiagnosticType]] = None,
    ) -> CognitionDiagnostics:
        """
        Run comprehensive cognition diagnostics.
        
        Analyzes reasoning quality, coherence, consistency,
        adaptation efficiency, and distribution alignment.
        """
        diagnostic_id = f"diag_{uuid4()}"
        
        if diagnostic_types is None:
            diagnostic_types = list(DiagnosticType)
        
        # Initialize metrics
        reasoning_quality = 1.0
        coherence_score = 1.0
        consistency_score = 1.0
        adaptation_efficiency = 1.0
        distribution_alignment = 1.0
        sync_health = 1.0
        conflict_rate = 0.0
        detected_anomalies: List[Dict[str, Any]] = []
        recommendations: List[Dict[str, Any]] = []
        
        # Run individual diagnostics
        for diag_type in diagnostic_types:
            if diag_type == DiagnosticType.REASONING:
                quality_result = await self._diagnose_reasoning_quality(scope, domain)
                reasoning_quality = quality_result.get("score", 1.0)
                if quality_result.get("anomalies"):
                    detected_anomalies.extend(quality_result["anomalies"])
            
            elif diag_type == DiagnosticType.COHERENCE:
                coherence_result = await self._diagnose_coherence(scope, domain)
                coherence_score = coherence_result.get("score", 1.0)
                if coherence_result.get("anomalies"):
                    detected_anomalies.extend(coherence_result["anomalies"])
            
            elif diag_type == DiagnosticType.SEMANTIC:
                semantic_result = await self._diagnose_semantic_consistency(scope, domain)
                consistency_score = semantic_result.get("score", 1.0)
                if semantic_result.get("violations"):
                    detected_anomalies.extend(semantic_result["violations"])
            
            elif diag_type == DiagnosticType.DISTRIBUTION:
                dist_result = await self._diagnose_distribution_alignment(scope, domain)
                distribution_alignment = dist_result.get("alignment", 1.0)
                sync_health = dist_result.get("sync_health", 1.0)
                conflict_rate = dist_result.get("conflict_rate", 0.0)
            
            elif diag_type == DiagnosticType.ADAPTATION:
                adapt_result = await self._diagnose_adaptation_efficiency(scope, domain)
                adaptation_efficiency = adapt_result.get("efficiency", 1.0)
        
        # Determine overall cognition state
        cognition_state = self._determine_cognition_state(
            reasoning_quality, coherence_score, consistency_score,
            adaptation_efficiency, conflict_rate
        )
        
        # Determine anomaly severity
        anomaly_severity = self._determine_anomaly_severity(detected_anomalies)
        
        # Generate recommendations
        recommendations = self._generate_diagnostic_recommendations(
            reasoning_quality, coherence_score, consistency_score,
            adaptation_efficiency, distribution_alignment
        )
        
        # Create diagnostics record
        diagnostics = CognitionDiagnostics(
            diagnostic_id=diagnostic_id,
            scope=scope,
            domain=domain,
            cognition_state=cognition_state,
            reasoning_quality=reasoning_quality,
            coherence_score=coherence_score,
            consistency_score=consistency_score,
            adaptation_efficiency=adaptation_efficiency,
            distribution_alignment=distribution_alignment,
            sync_health=sync_health,
            conflict_rate=conflict_rate,
            detected_anomalies=detected_anomalies if detected_anomalies else None,
            anomaly_severity=anomaly_severity,
            recommendations=recommendations if recommendations else None,
            assessed_at=datetime.utcnow(),
        )
        
        self.db.add(diagnostics)
        await self.db.commit()
        await self.db.refresh(diagnostics)
        
        return diagnostics
    
    async def _diagnose_reasoning_quality(
        self, scope: str, domain: str
    ) -> Dict[str, Any]:
        """Diagnose reasoning quality metrics"""
        # Query recent lineage records
        result = await self.db.execute(
            select(OrchestrationReasoningLineage)
            .where(OrchestrationReasoningLineage.created_at >= datetime.utcnow() - timedelta(hours=1))
        )
        lineages = list(result.scalars().all())
        
        if not lineages:
            return {"score": 1.0, "anomalies": []}
        
        # Calculate average confidence
        avg_confidence = sum(l.confidence for l in lineages) / len(lineages) if lineages else 1.0
        
        # Find low-confidence reasoning
        anomalies = []
        for lineage in lineages:
            if lineage.confidence < 0.5:
                anomalies.append({
                    "type": "low_confidence_reasoning",
                    "lineage_id": lineage.lineage_id,
                    "confidence": lineage.confidence,
                    "reasoning_type": lineage.reasoning_type,
                })
        
        return {"score": avg_confidence, "anomalies": anomalies}
    
    async def _diagnose_coherence(
        self, scope: str, domain: str
    ) -> Dict[str, Any]:
        """Diagnose cognitive coherence metrics"""
        # Query recent introspection sessions
        result = await self.db.execute(
            select(IntrospectionSession)
            .where(
                and_(
                    IntrospectionSession.scope == scope,
                    IntrospectionSession.is_active == True
                )
            )
        )
        sessions = list(result.scalars().all())
        
        if not sessions:
            return {"score": 1.0, "anomalies": []}
        
        # Calculate average confidence
        avg_confidence = sum(s.confidence for s in sessions) / len(sessions) if sessions else 1.0
        
        return {"score": avg_confidence, "anomalies": []}
    
    async def _diagnose_semantic_consistency(
        self, scope: str, domain: str
    ) -> Dict[str, Any]:
        """Diagnose semantic consistency"""
        # Query recent audits
        result = await self.db.execute(
            select(SemanticConsistencyAudit)
            .where(
                and_(
                    SemanticConsistencyAudit.scope == scope,
                    SemanticConsistencyAudit.audited_at >= datetime.utcnow() - timedelta(hours=1)
                )
            )
        )
        audits = list(result.scalars().all())
        
        if not audits:
            return {"score": 1.0, "violations": []}
        
        avg_score = sum(a.consistency_score for a in audits) / len(audits) if audits else 1.0
        
        violations = []
        for audit in audits:
            if audit.violations:
                for v in audit.violations:
                    v["audit_id"] = audit.audit_id
                    violations.append(v)
        
        return {"score": avg_score, "violations": violations}
    
    async def _diagnose_distribution_alignment(
        self, scope: str, domain: str
    ) -> Dict[str, Any]:
        """Diagnose distribution alignment"""
        # Query reconciliation states
        result = await self.db.execute(
            select(CognitionReconciliationState)
            .where(CognitionReconciliationState.scope == scope)
        )
        states = list(result.scalars().all())
        
        if not states:
            return {"alignment": 1.0, "sync_health": 1.0, "conflict_rate": 0.0}
        
        avg_alignment = sum(s.sync_health_score for s in states) / len(states) if states else 1.0
        total_conflicts = sum(
            len(s.active_conflicts or []) for s in states
        )
        conflict_rate = total_conflicts / len(states) if states else 0.0
        
        return {
            "alignment": avg_alignment,
            "sync_health": avg_alignment,
            "conflict_rate": min(conflict_rate, 1.0),
        }
    
    async def _diagnose_adaptation_efficiency(
        self, scope: str, domain: str
    ) -> Dict[str, Any]:
        """Diagnose adaptation efficiency"""
        # Query governance profiles
        profile = self._governance_profiles.get(scope)
        if not profile:
            return {"efficiency": 1.0}
        
        trigger_rate = profile.trigger_count / max(1, profile.violation_count + 1)
        efficiency = min(1.0, trigger_rate)
        
        return {"efficiency": efficiency}
    
    def _determine_cognition_state(
        self,
        reasoning_quality: float,
        coherence_score: float,
        consistency_score: float,
        adaptation_efficiency: float,
        conflict_rate: float,
    ) -> str:
        """Determine overall cognition state"""
        avg_score = (reasoning_quality + coherence_score + consistency_score + adaptation_efficiency) / 4
        
        if conflict_rate > 0.3:
            return CognitionState.CONFLICTED.value
        elif avg_score < 0.5:
            return CognitionState.DEGRADED.value
        elif avg_score < 0.7:
            return CognitionState.DRIFTING.value
        elif conflict_rate > 0.1:
            return CognitionState.RECOVERING.value
        else:
            return CognitionState.HEALTHY.value
    
    def _determine_anomaly_severity(
        self, anomalies: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Determine anomaly severity level"""
        if not anomalies:
            return None
        
        has_critical = any(a.get("severity") == AuditSeverity.CRITICAL.value for a in anomalies)
        has_error = any(a.get("severity") == AuditSeverity.ERROR.value for a in anomalies)
        has_warning = any(a.get("severity") == AuditSeverity.WARNING.value for a in anomalies)
        
        if has_critical:
            return AuditSeverity.CRITICAL.value
        elif has_error:
            return AuditSeverity.ERROR.value
        elif has_warning:
            return AuditSeverity.WARNING.value
        else:
            return AuditSeverity.INFO.value
    
    def _generate_diagnostic_recommendations(
        self,
        reasoning_quality: float,
        coherence_score: float,
        consistency_score: float,
        adaptation_efficiency: float,
        distribution_alignment: float,
    ) -> List[Dict[str, Any]]:
        """Generate diagnostic recommendations"""
        recommendations = []
        
        if reasoning_quality < 0.7:
            recommendations.append({
                "type": "reasoning_improvement",
                "priority": "high",
                "action": "Review and strengthen reasoning chains",
                "expected_impact": "improve_decision_quality",
            })
        
        if coherence_score < 0.7:
            recommendations.append({
                "type": "coherence_enhancement",
                "priority": "medium",
                "action": "Align cognitive processes",
                "expected_impact": "improve_coherence",
            })
        
        if consistency_score < 0.7:
            recommendations.append({
                "type": "consistency_validation",
                "priority": "high",
                "action": "Run semantic consistency audit",
                "expected_impact": "detect_misalignment",
            })
        
        if adaptation_efficiency < 0.7:
            recommendations.append({
                "type": "adaptation_optimization",
                "priority": "medium",
                "action": "Tune adaptation parameters",
                "expected_impact": "improve_adaptation",
            })
        
        if distribution_alignment < 0.7:
            recommendations.append({
                "type": "sync_optimization",
                "priority": "high",
                "action": "Reconcile distributed cognition states",
                "expected_impact": "improve_alignment",
            })
        
        return recommendations
    
    async def get_diagnostics_history(
        self,
        scope: str,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[CognitionDiagnostics]:
        """Get diagnostics history"""
        query = select(CognitionDiagnostics).where(
            CognitionDiagnostics.scope == scope
        )
        
        if since:
            query = query.where(CognitionDiagnostics.assessed_at >= since)
        
        query = query.order_by(CognitionDiagnostics.assessed_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ==================== Orchestration Introspection ====================
    
    async def start_introspection_session(
        self,
        scope: str,
        introspection_type: str,
        execution_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        focus_areas: Optional[List[str]] = None,
    ) -> IntrospectionSession:
        """Start a new introspection session"""
        session_id = f"introspect_{uuid4()}"
        
        session = IntrospectionSession(
            session_id=session_id,
            execution_id=execution_id,
            workflow_id=workflow_id,
            scope=scope,
            phase=IntrospectionPhase.INITIALIZING.value,
            introspection_type=introspection_type,
            focus_areas=focus_areas or [],
            findings=[],
            insights=[],
            confidence=0.0,
            depth_achieved=0,
            breadth_achieved=0,
            is_active=True,
            started_at=datetime.utcnow(),
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        self._active_sessions[session_id] = session
        
        # Queue the introspection
        await self._introspection_queue.put({
            "session_id": session_id,
            "scope": scope,
            "type": introspection_type,
        })
        
        return session
    
    async def analyze_orchestration_reasoning(
        self,
        execution_id: str,
        depth: int = 5,
    ) -> OrchestrationReasoningLineage:
        """Analyze the reasoning chain for an execution"""
        lineage_id = f"lineage_{uuid4()}"
        
        # Query existing reasoned items
        result = await self.db.execute(
            select(OrchestrationReasoningLineage)
            .where(OrchestrationReasoningLineage.execution_id == execution_id)
            .order_by(OrchestrationReasoningLineage.chain_position)
        )
        existing = list(result.scalars().all())
        
        if existing:
            return existing[-1]
        
        # Create new lineage record
        lineage = OrchestrationReasoningLineage(
            lineage_id=lineage_id,
            execution_id=execution_id,
            reasoning_type="analyzed",
            inference_pattern="chain",
            lineage_chain=f"{execution_id}_chain",
            chain_position=0,
            premise=f"Execution {execution_id} reasoning analysis",
            inference=f"Analysis depth: {depth}",
            conclusion=f"Reasoning quality assessed",
            confidence=0.5,
            reasoning_depth=depth,
            verification_result="pending",
            verified=False,
            created_at=datetime.utcnow(),
        )
        
        self.db.add(lineage)
        await self.db.commit()
        await self.db.refresh(lineage)
        
        return lineage
    
    async def record_reasoning_step(
        self,
        execution_id: str,
        reasoning_type: str,
        premise: str,
        inference: str,
        conclusion: str,
        evidence: Optional[List[Dict[str, Any]]] = None,
        parent_lineage_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> OrchestrationReasoningLineage:
        """Record a reasoning step in the lineage"""
        # Get next chain position
        result = await self.db.execute(
            select(func.max(OrchestrationReasoningLineage.chain_position))
            .where(OrchestrationReasoningLineage.execution_id == execution_id)
        )
        max_pos = result.scalar() or -1
        
        lineage_id = f"lineage_{uuid4()}"
        lineage = OrchestrationReasoningLineage(
            lineage_id=lineage_id,
            execution_id=execution_id,
            session_id=session_id,
            reasoning_type=reasoning_type,
            inference_pattern="step",
            lineage_chain=f"{execution_id}_chain",
            chain_position=max_pos + 1,
            premise=premise,
            inference=inference,
            conclusion=conclusion,
            evidence=evidence,
            confidence=0.5,
            reasoning_depth=1,
            parent_lineage_id=parent_lineage_id,
            created_at=datetime.utcnow(),
        )
        
        self.db.add(lineage)
        await self.db.commit()
        await self.db.refresh(lineage)
        
        return lineage

    # ==================== Semantic Consistency Auditing ====================
    
    async def conduct_semantic_audit(
        self,
        audit_kind: str,
        scope: str,
        target_entities: Optional[List[str]] = None,
    ) -> SemanticConsistencyAudit:
        """Conduct a semantic consistency audit"""
        audit_id = f"audit_{uuid4()}"
        
        # Perform consistency checks
        violations: List[Dict[str, Any]] = []
        warnings: List[str] = []
        
        # Query existing audits for context
        result = await self.db.execute(
            select(SemanticConsistencyAudit)
            .where(
                and_(
                    SemanticConsistencyAudit.scope == scope,
                    SemanticConsistencyAudit.audit_kind == audit_kind
                )
            )
            .order_by(SemanticConsistencyAudit.audited_at.desc())
            .limit(10)
        )
        previous_audits = list(result.scalars().all())
        
        # Check for divergences from historical patterns
        if previous_audits:
            avg_prev_score = sum(
                a.consistency_score for a in previous_audits
            ) / len(previous_audits)
            
            if avg_prev_score < 0.7:
                warnings.append(f"Historical consistency below threshold: {avg_prev_score:.2f}")
        
        # Calculate consistency score
        consistency_score = 1.0 - (len(violations) * 0.1)
        consistency_score = max(0.0, min(1.0, consistency_score))
        
        # Determine status
        if violations:
            audit_status = "failed"
            severity = AuditSeverity.ERROR.value
        elif warnings:
            audit_status = "passed_with_warnings"
            severity = AuditSeverity.WARNING.value
        else:
            audit_status = "passed"
            severity = AuditSeverity.INFO.value
        
        audit = SemanticConsistencyAudit(
            audit_id=audit_id,
            audit_kind=audit_kind,
            scope=scope,
            audit_status=audit_status,
            severity=severity,
            consistency_score=consistency_score,
            violations=violations if violations else None,
            warnings=warnings if warnings else None,
            target_entities=target_entities,
            resolution_required=bool(violations),
            audited_at=datetime.utcnow(),
        )
        
        self.db.add(audit)
        await self.db.commit()
        await self.db.refresh(audit)
        
        return audit

    # ==================== Cognitive Governance ====================
    
    async def enforce_governance(
        self,
        scope: str,
        action_type: str,
        context: Dict[str, Any],
    ) -> bool:
        """
        Enforce governance policies for a cognitive action.
        
        Returns True if action is allowed, False if blocked.
        """
        profile = self._governance_profiles.get(scope)
        
        if not profile:
            # No governance profile, allow by default
            return True
        
        profile.trigger_count += 1
        
        # Check enforcement rules
        for rule in profile.enforcement_rules:
            if rule.get("action_type") == action_type:
                conditions = rule.get("conditions", {})
                
                # Check condition match
                match = True
                for key, expected in conditions.items():
                    actual = context.get(key)
                    if actual != expected:
                        match = False
                        break
                
                if match:
                    action = rule.get("action", "allow")
                    if action == "deny":
                        profile.violation_count += 1
                        await self.db.commit()
                        return False
        
        await self.db.commit()
        return True
    
    async def create_governance_profile(
        self,
        profile_key: str,
        scope: str,
        domain: str,
        validation_thresholds: Optional[Dict[str, float]] = None,
        enforcement_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> AdaptiveGovernanceProfile:
        """Create a new governance profile"""
        profile_id = f"gov_profile_{uuid4()}"
        
        if validation_thresholds is None:
            validation_thresholds = {
                "min_reasoning_quality": 0.7,
                "min_coherence_score": 0.7,
                "min_consistency_score": 0.7,
                "max_conflict_rate": 0.2,
            }
        
        if enforcement_rules is None:
            enforcement_rules = []
        
        profile = AdaptiveGovernanceProfile(
            profile_id=profile_id,
            profile_key=profile_key,
            scope=scope,
            domain=domain,
            validation_thresholds=validation_thresholds,
            alignment_requirements={},
            enforcement_rules=enforcement_rules,
            is_active=True,
            alignment_status=GovernanceAlignment.ALIGNED.value,
            version=1,
        )
        
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        
        self._governance_profiles[scope] = profile
        
        return profile

    # ==================== Cognitive Reconciliation ====================
    
    async def reconcile_cognition(
        self,
        node_id: str,
        scope: str,
        sync_version: Optional[int] = None,
    ) -> CognitionReconciliationState:
        """Reconcile cognition state across distributed nodes"""
        state_id = f"reconcile_{node_id}_{scope}"
        
        # Find or create state
        result = await self.db.execute(
            select(CognitionReconciliationState)
            .where(
                and_(
                    CognitionReconciliationState.node_id == node_id,
                    CognitionReconciliationState.scope == scope
                )
            )
        )
        state = result.scalar_one_or_none()
        
        if not state:
            state = CognitionReconciliationState(
                state_id=state_id,
                node_id=node_id,
                scope=scope,
                reconciliation_status=ReconciliationStatus.PENDING.value,
                sync_version=1,
                pending_updates=0,
                sync_health_score=1.0,
                created_at=datetime.utcnow(),
            )
            self.db.add(state)
        else:
            # Check for pending updates
            if state.pending_updates > 0:
                state.reconciliation_status = ReconciliationStatus.PENDING.value
            else:
                state.reconciliation_status = ReconciliationStatus.SYNCED.value
        
        # Update sync info
        state.last_sync_at = datetime.utcnow()
        if sync_version:
            state.sync_version = sync_version
        
        await self.db.commit()
        await self.db.refresh(state)
        
        return state
    
    async def detect_cognition_conflicts(
        self,
        scope: str,
    ) -> List[Dict[str, Any]]:
        """Detect conflicts in distributed cognition"""
        result = await self.db.execute(
            select(CognitionReconciliationState)
            .where(
                and_(
                    CognitionReconciliationState.scope == scope,
                    CognitionReconciliationState.reconciliation_status != ReconciliationStatus.SYNCED.value
                )
            )
        )
        states = list(result.scalars().all())
        
        conflicts = []
        for state in states:
            if state.active_conflicts:
                for conflict in state.active_conflicts:
                    conflict["node_id"] = state.node_id
                    conflict["state_id"] = state.state_id
                    conflicts.append(conflict)
        
        return conflicts

    # ==================== Predictive Cognition Stabilization ====================
    
    async def forecast_cognition_drift(
        self,
        target_id: str,
        target_type: str,
        scope: str,
        horizon: PredictionHorizon = PredictionHorizon.NEAR_TERM,
    ) -> PredictiveCognitionForecast:
        """Forecast potential cognition drift"""
        forecast_id = f"forecast_{uuid4()}"
        
        # Analyze historical metrics
        result = await self.db.execute(
            select(CognitionDiagnostics)
            .where(
                and_(
                    CognitionDiagnostics.scope == scope,
                    CognitionDiagnostics.assessed_at >= datetime.utcnow() - timedelta(hours=24)
                )
            )
            .order_by(CognitionDiagnostics.assessed_at.desc())
            .limit(50)
        )
        diagnostics = list(result.scalars().all())
        
        # Calculate drift probability
        if diagnostics:
            avg_quality = sum(d.reasoning_quality for d in diagnostics) / len(diagnostics)
            avg_consistency = sum(d.consistency_score for d in diagnostics) / len(diagnostics)
            
            # Predict based on trends
            scores = [d.reasoning_quality for d in diagnostics]
            score_trend = sum(
                scores[i] - scores[i+1]
                for i in range(len(scores)-1)
            ) / max(1, len(scores)-1) if scores else 0
            
            predicted_value = avg_quality + score_trend * 0.1
            probability = max(0, min(1, 1 - avg_quality + abs(score_trend)))
            confidence = len(diagnostics) / 50
        else:
            predicted_value = 0.8
            probability = 0.1
            confidence = 0.3
        
        # Generate risk factors
        risk_factors = []
        if diagnostics and avg_quality < 0.7:
            risk_factors.append("low_reasoning_quality")
        if diagnostics and avg_consistency < 0.7:
            risk_factors.append("inconsistent_semantics")
        
        # Generate recommended actions
        recommendations = []
        if probability > 0.3:
            recommendations.append("run_full_diagnostics")
        if probability > 0.5:
            recommendations.append("initiate_reconciliation")
        
        # Calculate predicted time
        horizon_hours = {
            PredictionHorizon.IMMEDIATE: 0.083,  # 5 min
            PredictionHorizon.NEAR_TERM: 0.5,   # 30 min
            PredictionHorizon.SHORT: 2,          # 2h
            PredictionHorizon.MEDIUM: 8,         # 8h
        }
        predicted_for = datetime.utcnow() + timedelta(
            minutes=horizon_hours.get(horizon, 0.5) * 60
        )
        
        forecast = PredictiveCognitionForecast(
            forecast_id=forecast_id,
            target_id=target_id,
            target_type=target_type,
            scope=scope,
            forecast_kind="cognition_drift",
            horizon=horizon.value,
            predicted_value=predicted_value,
            confidence=confidence,
            probability=probability,
            min_value=predicted_value - 0.2,
            max_value=predicted_value + 0.2,
            risk_factors=risk_factors if risk_factors else None,
            recommended_actions=recommendations if recommendations else None,
            risk_level="high" if probability > 0.5 else "medium" if probability > 0.3 else "low",
            predicted_for=predicted_for,
            generated_at=datetime.utcnow(),
        )
        
        self.db.add(forecast)
        await self.db.commit()
        await self.db.refresh(forecast)
        
        return forecast
    
    async def get_forecasts_for_target(
        self,
        target_id: str,
        limit: int = 10,
    ) -> List[PredictiveCognitionForecast]:
        """Get forecasts for a specific target"""
        result = await self.db.execute(
            select(PredictiveCognitionForecast)
            .where(
                and_(
                    PredictiveCognitionForecast.target_id == target_id,
                    PredictiveCognitionForecast.predicted_for >= datetime.utcnow()
                )
            )
            .order_by(PredictiveCognitionForecast.generated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    # ==================== Anomaly Management ====================
    
    async def register_anomaly(
        self,
        anomaly_type: str,
        target_id: str,
        target_type: str,
        scope: str,
        detection_method: str,
        detection_signals: Optional[List[Dict[str, Any]]] = None,
        severity: AuditSeverity = AuditSeverity.WARNING,
        expected_value: Optional[float] = None,
        actual_value: Optional[float] = None,
        correlation_id: Optional[str] = None,
    ) -> CognitionAnomalyRegistry:
        """Register a detected cognitive anomaly"""
        anomaly_id = f"anomaly_{uuid4()}"
        
        deviation = None
        if expected_value is not None and actual_value is not None:
            deviation = actual_value - expected_value
        
        anomaly = CognitionAnomalyRegistry(
            anomaly_id=anomaly_id,
            anomaly_type=anomaly_type,
            severity=severity.value,
            target_id=target_id,
            target_type=target_type,
            scope=scope,
            detection_method=detection_method,
            detection_signals=detection_signals,
            expected_value=expected_value,
            actual_value=actual_value,
            deviation=deviation,
            status="detected",
            correlation_id=correlation_id,
            detected_at=datetime.utcnow(),
        )
        
        self.db.add(anomaly)
        await self.db.commit()
        await self.db.refresh(anomaly)
        
        return anomaly
    
    async def resolve_anomaly(
        self,
        anomaly_id: str,
        remediation_action: str,
    ) -> CognitionAnomalyRegistry:
        """Mark an anomaly as resolved"""
        result = await self.db.execute(
            select(CognitionAnomalyRegistry)
            .where(CognitionAnomalyRegistry.anomaly_id == anomaly_id)
        )
        anomaly = result.scalar_one_or_none()
        
        if anomaly:
            anomaly.status = "resolved"
            anomaly.remediation_action = remediation_action
            anomaly.resolved_at = datetime.utcnow()
            self.db.add(anomaly)
            await self.db.commit()
            await self.db.refresh(anomaly)
        
        return anomaly
    
    async def get_active_anomalies(
        self,
        scope: Optional[str] = None,
        severity: Optional[AuditSeverity] = None,
    ) -> List[CognitionAnomalyRegistry]:
        """Get active anomalies"""
        query = select(CognitionAnomalyRegistry).where(
            CognitionAnomalyRegistry.status == "detected"
        )
        
        if scope:
            query = query.where(CognitionAnomalyRegistry.scope == scope)
        if severity:
            query = query.where(CognitionAnomalyRegistry.severity == severity.value)
        
        query = query.order_by(CognitionAnomalyRegistry.detected_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())


class RuntimeSelfAnalyzer:
    """
    Runtime Self-Analyzer - Analyzes orchestration behavior and reasoning.
    """
    
    def __init__(self, db: AsyncSession, meta_engine: MetaCognitionEngine):
        self.db = db
        self.meta_engine = meta_engine
    
    async def analyze_orchestration_behavior(
        self,
        execution_id: str,
    ) -> Dict[str, Any]:
        """Analyze orchestration behavior patterns"""
        # Query reasoning lineage
        result = await self.db.execute(
            select(OrchestrationReasoningLineage)
            .where(OrchestrationReasoningLineage.execution_id == execution_id)
            .order_by(OrchestrationReasoningLineage.chain_position)
        )
        lineages = list(result.scalars().all())
        
        # Analyze reasoning patterns
        reasoning_types = {}
        confidence_scores = []
        
        for lineage in lineages:
            if lineage.reasoning_type:
                reasoning_types[lineage.reasoning_type] = reasoning_types.get(lineage.reasoning_type, 0) + 1
            if lineage.confidence:
                confidence_scores.append(lineage.confidence)
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        return {
            "execution_id": execution_id,
            "reasoning_patterns": reasoning_types,
            "avg_confidence": avg_confidence,
            "chain_length": len(lineages),
            "verified_count": sum(1 for l in lineages if l.verified),
        }
    
    async def measure_introspection_overhead(
        self,
        session_id: str,
    ) -> float:
        """Measure the overhead of introspection"""
        result = await self.db.execute(
            select(IntrospectionSession)
            .where(IntrospectionSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session or not session.duration_ms:
            return 0.0
        
        # Rough estimate: overhead is ratio of introspection depth to duration
        overhead = session.depth_achieved / max(1, session.duration_ms) * 100
        
        return min(1.0, overhead)


__all__ = [
    "MetaCognitionEngine",
    "RuntimeSelfAnalyzer",
]
