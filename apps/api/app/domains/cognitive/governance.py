"""
Multi-Agent Governance Service

Advanced distributed agent governance with agent society runtime,
authority hierarchies, execution diplomacy, and distributed negotiation.
"""
import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cognitive import (
    AgentGovernanceSession, AgentDecision, GovernanceRole, GovernanceAction
)

logger = logging.getLogger(__name__)


class MultiAgentGovernanceService:
    """
    Multi-agent civilization governance system.
    
    Capabilities:
    - Inter-agent coordination: Orchestrate multiple agents
    - Execution conflict prevention: Resolve resource conflicts
    - Adaptive governance: Evolve governance rules
    - Distributed authority management: Manage agent authorities
    - Orchestration diplomacy: Negotiate between agents
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ---- Session Management ----
    
    async def create_session(
        self,
        name: str,
        session_type: str,
        coordinator_id: Optional[str] = None,
        participant_ids: Optional[List[str]] = None,
        authority_level: str = GovernanceRole.ORCHESTRATOR.value,
        scope_kind: Optional[str] = None,
        scope_id: Optional[str] = None,
        expected_duration: Optional[int] = None,
        parent_session_id: Optional[UUID] = None,
    ) -> AgentGovernanceSession:
        """
        Create a new governance session.
        
        Args:
            name: Session name
            session_type: Type (coordination, arbitration, planning)
            coordinator_id: Lead agent ID
            participant_ids: List of agent IDs
            authority_level: Authority hierarchy level
            scope_kind: Target resource kind
            scope_id: Target resource ID
            expected_duration: Expected duration in seconds
            parent_session_id: Parent session for nested governance
            
        Returns:
            Created AgentGovernanceSession
        """
        session = AgentGovernanceSession(
            name=name,
            session_type=session_type,
            status="active",
            coordinator_id=coordinator_id,
            participant_ids=participant_ids or [],
            authority_level=authority_level,
            scope_kind=scope_kind,
            scope_id=scope_id,
            expected_duration=expected_duration,
            session_start=datetime.utcnow(),
            negotiation_rounds=0,
            consensus_reached=False,
            efficiency_score=0.0,
            parent_session_id=parent_session_id,
        )
        self.db.add(session)
        await self.db.flush()
        logger.info(f"Created governance session: {session.id} [{name}]")
        return session
    
    async def get_session(self, session_id: UUID) -> Optional[AgentGovernanceSession]:
        """Get a session by ID."""
        return await self.db.get(AgentGovernanceSession, session_id)
    
    async def update_session(
        self,
        session_id: UUID,
        **kwargs,
    ) -> Optional[AgentGovernanceSession]:
        """Update session attributes."""
        session = await self.db.get(AgentGovernanceSession, session_id)
        if not session:
            return None
        
        for key, value in kwargs.items():
            if hasattr(session, key) and value is not None:
                setattr(session, key, value)
        
        await self.db.flush()
        return session
    
    async def end_session(
        self,
        session_id: UUID,
        resolution: Optional[Dict[str, Any]] = None,
        execution_plan: Optional[Dict[str, Any]] = None,
    ) -> Optional[AgentGovernanceSession]:
        """
        End a governance session.
        
        Args:
            session_id: Session to end
            resolution: Final resolution data
            execution_plan: Resulting execution plan
            
        Returns:
            Updated session
        """
        session = await self.db.get(AgentGovernanceSession, session_id)
        if not session:
            return None
        
        session.status = "completed"
        session.session_end = datetime.utcnow()
        
        if resolution:
            session.resolution = resolution
        if execution_plan:
            session.execution_plan = execution_plan
        
        # Calculate efficiency
        if session.session_start and session.session_end:
            duration = (session.session_end - session.session_start).total_seconds()
            if duration > 0 and session.expected_duration:
                efficiency = session.expected_duration / duration
                session.efficiency_score = min(1.0, efficiency)
        
        await self.db.flush()
        logger.info(f"Ended governance session: {session_id}")
        return session
    
    async def list_sessions(
        self,
        status: Optional[str] = None,
        session_type: Optional[str] = None,
        coordinator_id: Optional[str] = None,
        scope_kind: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[AgentGovernanceSession]:
        """List sessions with filtering."""
        query = select(AgentGovernanceSession).where(
            AgentGovernanceSession.deleted_at.is_(None)
        )
        
        if status:
            query = query.where(AgentGovernanceSession.status == status)
        if session_type:
            query = query.where(AgentGovernanceSession.session_type == session_type)
        if coordinator_id:
            query = query.where(AgentGovernanceSession.coordinator_id == coordinator_id)
        if scope_kind:
            query = query.where(AgentGovernanceSession.scope_kind == scope_kind)
        
        query = query.order_by(desc(AgentGovernanceSession.session_start))
        query = query.offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_active_sessions(
        self,
        scope_kind: Optional[str] = None,
    ) -> List[AgentGovernanceSession]:
        """Get all active sessions."""
        query = select(AgentGovernanceSession).where(
            and_(
                AgentGovernanceSession.status == "active",
                AgentGovernanceSession.deleted_at.is_(None),
            )
        )
        
        if scope_kind:
            query = query.where(AgentGovernanceSession.scope_kind == scope_kind)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    # ---- Negotiation and Coordination ----
    
    async def add_action(
        self,
        session_id: UUID,
        action_type: str,
        agent_id: str,
        action_data: Dict[str, Any],
    ) -> Optional[AgentGovernanceSession]:
        """
        Add a governance action to a session.
        
        Args:
            session_id: Session to add action to
            action_type: Type of action
            agent_id: Agent performing action
            action_data: Action details
            
        Returns:
            Updated session
        """
        session = await self.db.get(AgentGovernanceSession, session_id)
        if not session:
            return None
        
        actions = session.actions_taken or []
        actions.append({
            'type': action_type,
            'agent_id': agent_id,
            'data': action_data,
            'timestamp': datetime.utcnow().isoformat(),
        })
        session.actions_taken = actions
        session.negotiation_rounds += 1
        
        await self.db.flush()
        return session
    
    async def add_decision(
        self,
        session_id: UUID,
        agent_id: str,
        agent_role: str,
        decision_type: str,
        context: Dict[str, Any],
        confidence: float = 0.8,
        rationale: Optional[str] = None,
        alternatives: Optional[List[Dict[str, Any]]] = None,
    ) -> AgentDecision:
        """
        Record an agent decision within a session.
        
        Args:
            session_id: Session context
            agent_id: Agent making decision
            agent_role: Agent's authority role
            decision_type: Type of decision
            context: Decision context data
            confidence: Decision confidence
            rationale: Decision reasoning
            alternatives: Alternatives considered
            
        Returns:
            Created AgentDecision
        """
        decision = AgentDecision(
            session_id=session_id,
            agent_id=agent_id,
            agent_role=agent_role,
            decision_type=decision_type,
            confidence=confidence,
            context=context,
            rationale=rationale,
            alternatives_considered=alternatives,
            decision_time=datetime.utcnow(),
        )
        self.db.add(decision)
        
        # Also add to session's decisions
        session = await self.db.get(AgentGovernanceSession, session_id)
        if session:
            decisions = session.decisions_made or []
            decisions.append({
                'decision_id': str(decision.id),
                'agent_id': agent_id,
                'type': decision_type,
                'timestamp': datetime.utcnow().isoformat(),
            })
            session.decisions_made = decisions
        
        await self.db.flush()
        return decision
    
    async def reach_consensus(
        self,
        session_id: UUID,
        consensus_data: Dict[str, Any],
        disagreements_resolved: Optional[List[str]] = None,
    ) -> Optional[AgentGovernanceSession]:
        """
        Mark consensus as reached in a session.
        
        Args:
            session_id: Session to finalize
            consensus_data: Agreed data
            disagreements_resolved: List of resolved disagreements
            
        Returns:
            Updated session
        """
        session = await self.db.get(AgentGovernanceSession, session_id)
        if not session:
            return None
        
        session.consensus_reached = True
        session.resolution = consensus_data
        if disagreements_resolved:
            session.disagreements = [d for d in (session.disagreements or []) if d not in disagreements_resolved]
        
        await self.db.flush()
        logger.info(f"Consensus reached in session: {session_id}")
        return session
    
    async def add_disagreement(
        self,
        session_id: UUID,
        disagreement: str,
        involved_agents: Optional[List[str]] = None,
    ) -> Optional[AgentGovernanceSession]:
        """Add a disagreement to a session."""
        session = await self.db.get(AgentGovernanceSession, session_id)
        if not session:
            return None
        
        disagreements = session.disagreements or []
        disagreements.append({
            'text': disagreement,
            'agents': involved_agents or [],
            'timestamp': datetime.utcnow().isoformat(),
        })
        session.disagreements = disagreements
        
        await self.db.flush()
        return session
    
    # ---- Conflict Resolution ----
    
    async def resolve_resource_conflict(
        self,
        session_id: UUID,
        resource_id: str,
        competing_agents: List[str],
        resolution_strategy: str = "priority",
    ) -> Dict[str, Any]:
        """
        Resolve resource allocation conflict.
        
        Args:
            session_id: Governance session
            resource_id: Contested resource
            competing_agents: Agents competing for resource
            resolution_strategy: Strategy (priority, fair_sharing, etc.)
            
        Returns:
            Resolution details
        """
        # Get agent priorities
        priorities = {}
        for agent_id in competing_agents:
            # In production, query actual agent priority
            priorities[agent_id] = 0.5
        
        if resolution_strategy == "priority":
            # Give to highest priority
            winner = max(priorities, key=priorities.get)
            allocation = {winner: 1.0}
        elif resolution_strategy == "fair_sharing":
            # Split equally
            share = 1.0 / len(competing_agents)
            allocation = {agent: share for agent in competing_agents}
        else:
            allocation = {}
        
        # Record decision
        await self.add_decision(
            session_id=session_id,
            agent_id="governance_system",
            agent_role=GovernanceRole.COORDINATOR.value,
            decision_type="resource_allocation",
            context={
                'resource_id': resource_id,
                'competing_agents': competing_agents,
                'strategy': resolution_strategy,
            },
            confidence=0.85,
            rationale=f"Resource conflict resolved using {resolution_strategy} strategy",
        )
        
        return {
            'resource_id': resource_id,
            'allocation': allocation,
            'strategy': resolution_strategy,
            'winner': list(allocation.keys())[0] if allocation else None,
        }
    
    async def arbitrate_priority_conflict(
        self,
        session_id: UUID,
        conflicting_tasks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Arbitrate task priority conflicts.
        
        Args:
            session_id: Governance session
            conflicting_tasks: Tasks with priority conflicts
            
        Returns:
            Arbitration result with resolved priorities
        """
        # Simple priority arbitration based on task attributes
        resolved = []
        for task in conflicting_tasks:
            priority = task.get('priority', 5)
            urgency = task.get('urgency', 0.5)
            impact = task.get('impact', 0.5)
            
            # Calculate composite priority score
            score = (priority / 10) * 0.4 + urgency * 0.3 + impact * 0.3
            
            resolved.append({
                'task_id': task.get('id'),
                'original_priority': priority,
                'resolved_score': score,
                'resolved_priority': int(score * 10),
            })
        
        # Sort by resolved priority
        resolved.sort(key=lambda x: x['resolved_score'], reverse=True)
        
        # Record arbitration
        await self.add_decision(
            session_id=session_id,
            agent_id="governance_system",
            agent_role=GovernanceRole.ORCHESTRATOR.value,
            decision_type="priority_arbitration",
            context={'conflicting_tasks': [t.get('id') for t in conflicting_tasks]},
            confidence=0.75,
            rationale="Priority conflict arbitrated based on composite scoring",
        )
        
        return {
            'arbitration_method': 'composite_scoring',
            'resolved_tasks': resolved,
            'order': [t['task_id'] for t in resolved],
        }
    
    # ---- Authority Management ----
    
    async def set_decision_authority(
        self,
        session_id: UUID,
        decision_type: str,
        agent_ids: List[str],
    ) -> Optional[AgentGovernanceSession]:
        """Set which agents have authority for specific decision types."""
        session = await self.db.get(AgentGovernanceSession, session_id)
        if not session:
            return None
        
        authority = session.decision_authority or {}
        authority[decision_type] = agent_ids
        session.decision_authority = authority
        
        await self.db.flush()
        return session
    
    async def check_authority(
        self,
        session_id: UUID,
        agent_id: str,
        decision_type: str,
    ) -> bool:
        """Check if an agent has authority for a decision type."""
        session = await self.db.get(AgentGovernanceSession, session_id)
        if not session:
            return False
        
        # Check coordinator authority
        if session.coordinator_id == agent_id:
            return True
        
        # Check explicit authority
        authority = session.decision_authority or {}
        authorized_agents = authority.get(decision_type, [])
        return agent_id in authorized_agents
    
    # ---- Decision Tracking ----
    
    async def get_session_decisions(
        self,
        session_id: UUID,
        decision_type: Optional[str] = None,
    ) -> List[AgentDecision]:
        """Get all decisions for a session."""
        query = select(AgentDecision).where(
            AgentDecision.session_id == session_id
        )
        
        if decision_type:
            query = query.where(AgentDecision.decision_type == decision_type)
        
        query = query.order_by(AgentDecision.decision_time)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def validate_decision(
        self,
        decision_id: UUID,
        validation_notes: str,
        is_valid: bool = True,
    ) -> Optional[AgentDecision]:
        """Validate a decision with review notes."""
        decision = await self.db.get(AgentDecision, decision_id)
        if not decision:
            return None
        
        decision.is_validated = True
        decision.validation_notes = validation_notes
        
        if not is_valid:
            decision.outcome = {'valid': False, 'reason': validation_notes}
        
        await self.db.flush()
        return decision
    
    # ---- Session Statistics ----
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get governance system statistics."""
        # Session counts by status
        status_query = select(
            AgentGovernanceSession.status,
            func.count(AgentGovernanceSession.id).label('count'),
        ).where(AgentGovernanceSession.deleted_at.is_(None)).group_by(
            AgentGovernanceSession.status
        )
        
        status_result = await self.db.execute(status_query)
        by_status = {row.status: row.count for row in status_result.all()}
        
        # Session counts by type
        type_query = select(
            AgentGovernanceSession.session_type,
            func.count(AgentGovernanceSession.id).label('count'),
        ).where(AgentGovernanceSession.deleted_at.is_(None)).group_by(
            AgentGovernanceSession.session_type
        )
        
        type_result = await self.db.execute(type_query)
        by_type = {row.session_type: row.count for row in type_result.all()}
        
        # Average efficiency
        avg_eff_query = select(func.avg(AgentGovernanceSession.efficiency_score)).where(
            AgentGovernanceSession.deleted_at.is_(None)
        )
        avg_eff_result = await self.db.execute(avg_eff_query)
        avg_efficiency = float(avg_eff_result.scalar() or 0.5)
        
        # Consensus rate
        consensus_query = select(
            func.count(AgentGovernanceSession.id)
        ).where(
            and_(
                AgentGovernanceSession.deleted_at.is_(None),
                AgentGovernanceSession.consensus_reached == True,
            )
        )
        consensus_result = await self.db.execute(consensus_query)
        consensus_count = consensus_result.scalar() or 0
        
        total_sessions = sum(by_status.values())
        
        # Decision statistics
        decision_count_query = select(func.count(AgentDecision.id))
        decision_result = await self.db.execute(decision_count_query)
        total_decisions = decision_result.scalar() or 0
        
        return {
            'total_sessions': total_sessions,
            'by_status': by_status,
            'by_type': by_type,
            'avg_efficiency': avg_efficiency,
            'consensus_rate': consensus_count / total_sessions if total_sessions > 0 else 0,
            'active_sessions': by_status.get('active', 0),
            'total_decisions': total_decisions,
            'validated_decisions': await self._count_validated_decisions(),
        }
    
    async def _count_validated_decisions(self) -> int:
        """Count validated decisions."""
        query = select(func.count(AgentDecision.id)).where(
            AgentDecision.is_validated == True
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    # ---- Child Sessions ----
    
    async def get_child_sessions(
        self,
        parent_session_id: UUID,
    ) -> List[AgentGovernanceSession]:
        """Get all child sessions of a parent session."""
        query = select(AgentGovernanceSession).where(
            and_(
                AgentGovernanceSession.parent_session_id == parent_session_id,
                AgentGovernanceSession.deleted_at.is_(None),
            )
        ).order_by(AgentGovernanceSession.session_start)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())


# ---- Convenience Functions ----

async def create_coordination_session(
    name: str,
    coordinator_id: str,
    participant_ids: List[str],
    scope_kind: str,
    scope_id: str,
) -> Optional[AgentGovernanceSession]:
    """Create a coordination session."""
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        service = MultiAgentGovernanceService(db)
        try:
            return await service.create_session(
                name=name,
                session_type="coordination",
                coordinator_id=coordinator_id,
                participant_ids=participant_ids,
                authority_level=GovernanceRole.ORCHESTRATOR.value,
                scope_kind=scope_kind,
                scope_id=scope_id,
            )
        except Exception as e:
            logger.error(f"Failed to create coordination session: {e}")
            return None