"""
Agent Services - Multi-agent orchestration
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_

from .models import (
    AgentType,
    AgentStatus,
    AgentCapability,
    CoordinationAction,
    MessagePriority,
    AgentSession,
    AgentRegistration,
    CoordinationMessage,
    AgentTask,
    ArbitrationDecision,
    AgentHealth,
)

logger = logging.getLogger(__name__)


@dataclass
class AgentInfo:
    """Agent information"""
    agent_id: str
    name: str
    agent_type: AgentType
    capabilities: List[AgentCapability]
    status: AgentStatus
    current_tasks: int
    max_concurrent: int


@dataclass
class TaskAssignment:
    """Task assignment result"""
    task_id: str
    assigned_agent: Optional[str]
    reason: str
    confidence: float
    estimated_duration: float


class AgentRegistry:
    """
    Agent registry for multi-agent coordination.
    Manages agent registration, capability tracking, and health monitoring.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._agents: Dict[str, AgentRegistration] = {}
        self._capability_index: Dict[AgentCapability, List[str]] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize the agent registry"""
        await self._load_agents()
        self._running = True
        logger.info("AgentRegistry initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the registry"""
        self._running = False
        logger.info("AgentRegistry shutdown")
    
    async def _load_agents(self) -> None:
        """Load agents from database"""
        result = await self.db.execute(select(AgentRegistration))
        for agent in result.scalars().all():
            self._agents[agent.agent_id] = agent
            
            # Build capability index
            for cap in (agent.capabilities or []):
                try:
                    capability = AgentCapability(cap)
                    if capability not in self._capability_index:
                        self._capability_index[capability] = []
                    self._capability_index[capability].append(agent.agent_id)
                except ValueError:
                    pass
    
    # ==================== Registration ====================
    
    async def register_agent(
        self,
        agent_id: str,
        name: str,
        agent_type: AgentType,
        capabilities: List[AgentCapability],
        config: Optional[Dict[str, Any]] = None,
        max_concurrent_tasks: int = 5,
    ) -> AgentRegistration:
        """Register a new agent"""
        agent = AgentRegistration(
            agent_id=agent_id,
            name=name,
            agent_type=agent_type.value,
            capabilities=[c.value for c in capabilities],
            config=config,
            status=AgentStatus.IDLE.value,
            max_concurrent_tasks=max_concurrent_tasks,
            registered_at=datetime.utcnow(),
            last_seen=datetime.utcnow(),
        )
        
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        
        self._agents[agent_id] = agent
        
        # Update capability index
        for cap in capabilities:
            if cap not in self._capability_index:
                self._capability_index[cap] = []
            self._capability_index[cap].append(agent_id)
        
        return agent
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent"""
        agent = self._agents.get(agent_id)
        
        if not agent:
            return False
        
        agent.status = AgentStatus.TERMINATED.value
        self.db.add(agent)
        await self.db.commit()
        
        del self._agents[agent_id]
        
        # Remove from capability index
        for cap_list in self._capability_index.values():
            if agent_id in cap_list:
                cap_list.remove(agent_id)
        
        return True
    
    async def update_heartbeat(self, agent_id: str) -> AgentRegistration:
        """Update agent heartbeat"""
        agent = self._agents.get(agent_id)
        
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        agent.last_seen = datetime.utcnow()
        agent.last_heartbeat = datetime.utcnow()
        
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        
        return agent
    
    async def update_status(
        self,
        agent_id: str,
        status: AgentStatus,
    ) -> AgentRegistration:
        """Update agent status"""
        agent = self._agents.get(agent_id)
        
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        agent.status = status.value
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        
        return agent
    
    # ==================== Lookup ====================
    
    async def get_agent(self, agent_id: str) -> Optional[AgentRegistration]:
        """Get agent by ID"""
        return self._agents.get(agent_id)
    
    async def get_agents_by_type(self, agent_type: AgentType) -> List[AgentRegistration]:
        """Get agents by type"""
        return [a for a in self._agents.values() if a.agent_type == agent_type.value]
    
    async def get_agents_by_capability(
        self,
        capability: AgentCapability,
    ) -> List[AgentRegistration]:
        """Get agents by capability"""
        agent_ids = self._capability_index.get(capability, [])
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]
    
    async def get_available_agents(
        self,
        capability: Optional[AgentCapability] = None,
    ) -> List[AgentRegistration]:
        """Get available agents"""
        if capability:
            candidates = await self.get_agents_by_capability(capability)
        else:
            candidates = list(self._agents.values())
        
        return [
            a for a in candidates
            if a.status == AgentStatus.IDLE.value
            and a.current_tasks < a.max_concurrent_tasks
        ]
    
    # ==================== Task Assignment ====================
    
    async def assign_task(
        self,
        task: AgentTask,
        required_capability: Optional[AgentCapability] = None,
    ) -> TaskAssignment:
        """Assign task to best available agent"""
        # Get candidates
        if required_capability:
            candidates = await self.get_agents_by_capability(required_capability)
        else:
            candidates = list(self._agents.values())
        
        # Filter available
        available = [
            a for a in candidates
            if a.status == AgentStatus.IDLE.value
            and a.current_tasks < a.max_concurrent_tasks
        ]
        
        if not available:
            return TaskAssignment(
                task_id=task.task_id,
                assigned_agent=None,
                reason="No available agents",
                confidence=0.0,
                estimated_duration=task.estimated_duration or 60,
            )
        
        # Score agents (simple: fewer current tasks = better)
        scored = []
        for agent in available:
            score = 1.0 - (agent.current_tasks / agent.max_concurrent_tasks)
            if agent.avg_execution_time:
                # Prefer faster agents
                score *= (60 / max(agent.avg_execution_time, 1))
            scored.append((agent, score))
        
        # Sort by score (descending)
        scored.sort(key=lambda x: x[1], reverse=True)
        
        best_agent = scored[0][0]
        
        # Update agent task count
        best_agent.current_tasks += 1
        best_agent.status = AgentStatus.BUSY.value
        self.db.add(best_agent)
        await self.db.commit()
        
        return TaskAssignment(
            task_id=task.task_id,
            assigned_agent=best_agent.agent_id,
            reason=f"Best available agent (score: {scored[0][1]:.2f})",
            confidence=scored[0][1],
            estimated_duration=task.estimated_duration or best_agent.avg_execution_time or 60,
        )
    
    async def release_task(
        self,
        agent_id: str,
        task_id: str,
        success: bool,
    ) -> None:
        """Release task and update agent metrics"""
        agent = self._agents.get(agent_id)
        
        if not agent:
            return
        
        # Update task counts
        if agent.current_tasks > 0:
            agent.current_tasks -= 1
        
        if success:
            agent.tasks_completed += 1
            agent.status = AgentStatus.IDLE.value
        else:
            agent.tasks_failed += 1
            agent.error_count += 1
            agent.status = AgentStatus.IDLE.value
        
        self.db.add(agent)
        await self.db.commit()


class AgentCoordinationRuntime:
    """
    Agent coordination runtime.
    Handles multi-agent communication, delegation, and orchestration.
    """
    
    def __init__(self, db: AsyncSession, registry: AgentRegistry):
        self.db = db
        self.registry = registry
        self._sessions: Dict[str, AgentSession] = {}
        self._tasks: Dict[str, AgentTask] = {}
        self._message_handlers: Dict[str, Callable] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize the coordination runtime"""
        self._register_default_handlers()
        self._running = True
        logger.info("AgentCoordinationRuntime initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the runtime"""
        self._running = False
        logger.info("AgentCoordinationRuntime shutdown")
    
    def _register_default_handlers(self) -> None:
        """Register default message handlers"""
        self._message_handlers["delegate"] = self._handle_delegate
        self._message_handlers["notify"] = self._handle_notify
        self._message_handlers["request"] = self._handle_request
        self._message_handlers["grant"] = self._handle_grant
    
    # ==================== Sessions ====================
    
    async def create_session(
        self,
        session_type: str,
        config: Optional[Dict[str, Any]] = None,
        owner_id: Optional[UUID] = None,
    ) -> AgentSession:
        """Create an agent session"""
        session = AgentSession(
            session_id=str(uuid4()),
            session_type=session_type,
            config=config,
            status=AgentStatus.INITIALIZING.value,
            started_at=datetime.utcnow(),
            owner_id=owner_id,
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        self._sessions[session.session_id] = session
        
        return session
    
    async def update_session(
        self,
        session_id: str,
        status: AgentStatus,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentSession:
        """Update session status"""
        session = self._sessions.get(session_id)
        
        if not session:
            result = await self.db.execute(
                select(AgentSession).where(AgentSession.session_id == session_id)
            )
            session = result.scalar_one_or_none()
        
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        session.status = status.value
        session.last_activity = datetime.utcnow()
        
        if context:
            session.context = context
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        return session
    
    # ==================== Task Management ====================
    
    async def create_task(
        self,
        task_type: str,
        task_name: str,
        config: Optional[Dict[str, Any]] = None,
        priority: int = 5,
        dependencies: Optional[List[str]] = None,
        session_id: Optional[str] = None,
    ) -> AgentTask:
        """Create a task"""
        task = AgentTask(
            task_id=str(uuid4()),
            task_type=task_type,
            task_name=task_name,
            config=config,
            priority=priority,
            dependencies=dependencies,
            session_id=session_id,
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        self._tasks[task.task_id] = task
        
        return task
    
    async def get_task(self, task_id: str) -> Optional[AgentTask]:
        """Get task by ID"""
        return self._tasks.get(task_id)
    
    async def assign_task_to_agent(
        self,
        task_id: str,
        agent_id: str,
    ) -> AgentTask:
        """Assign task to specific agent"""
        task = self._tasks.get(task_id)
        
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        task.assigned_agent = agent_id
        task.status = "assigned"
        task.started_at = datetime.utcnow()
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    async def update_task_progress(
        self,
        task_id: str,
        progress: float,
        current_step: Optional[str] = None,
    ) -> AgentTask:
        """Update task progress"""
        task = self._tasks.get(task_id)
        
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        task.progress = progress
        task.current_step = current_step
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    async def complete_task(
        self,
        task_id: str,
        result: Dict[str, Any],
    ) -> AgentTask:
        """Mark task as completed"""
        task = self._tasks.get(task_id)
        
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        task.status = "completed"
        task.progress = 100.0
        task.result = result
        task.completed_at = datetime.utcnow()
        
        if task.started_at:
            task.actual_duration = (task.completed_at - task.started_at).total_seconds()
        
        # Release agent
        if task.assigned_agent:
            await self.registry.release_task(task.assigned_agent, task_id, True)
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    async def fail_task(
        self,
        task_id: str,
        error: str,
    ) -> AgentTask:
        """Mark task as failed"""
        task = self._tasks.get(task_id)
        
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        task.status = "failed"
        task.error = error
        task.completed_at = datetime.utcnow()
        
        if task.started_at:
            task.actual_duration = (task.completed_at - task.started_at).total_seconds()
        
        # Release agent
        if task.assigned_agent:
            await self.registry.release_task(task.assigned_agent, task_id, False)
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    # ==================== Coordination Messages ====================
    
    async def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        action: CoordinationAction,
        payload: Optional[Dict[str, Any]] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        session_id: Optional[str] = None,
    ) -> CoordinationMessage:
        """Send coordination message"""
        message = CoordinationMessage(
            message_id=str(uuid4()),
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            action=action.value,
            payload=payload,
            priority=priority.value,
            session_id=session_id,
        )
        
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        
        # Process message
        await self._process_message(message)
        
        return message
    
    async def _process_message(self, message: CoordinationMessage) -> None:
        """Process coordination message"""
        handler = self._message_handlers.get(message.message_type)
        
        if handler:
            try:
                await handler(message)
                message.status = "processed"
                message.processed_at = datetime.utcnow()
            except Exception as e:
                logger.error(f"Message processing error: {e}")
                message.retry_count += 1
                message.status = "retry" if message.retry_count < message.max_retries else "failed"
        else:
            message.status = "delivered"
            message.delivered_at = datetime.utcnow()
        
        self.db.add(message)
        await self.db.commit()
    
    async def _handle_delegate(self, message: CoordinationMessage) -> None:
        """Handle delegate message"""
        # Forward to target agent
        logger.info(f"Delegating to agent: {message.to_agent}")
    
    async def _handle_notify(self, message: CoordinationMessage) -> None:
        """Handle notify message"""
        logger.info(f"Notification to agent: {message.to_agent}")
    
    async def _handle_request(self, message: CoordinationMessage) -> None:
        """Handle request message"""
        logger.info(f"Request from agent: {message.from_agent}")
    
    async def _handle_grant(self, message: CoordinationMessage) -> None:
        """Handle grant message"""
        logger.info(f"Grant to agent: {message.to_agent}")
    
    # ==================== Arbitration ====================
    
    async def arbitrate_task_assignment(
        self,
        task_id: str,
        candidate_agents: List[str],
    ) -> ArbitrationDecision:
        """Arbitrate task assignment among candidates"""
        scores = {}
        
        for agent_id in candidate_agents:
            agent = self._agents.get(agent_id)
            if not agent:
                continue
            
            score = 0.0
            
            # Availability score
            if agent.status == AgentStatus.IDLE.value:
                score += 0.4
            
            # Capacity score
            capacity_score = 1.0 - (agent.current_tasks / agent.max_concurrent_tasks)
            score += capacity_score * 0.3
            
            # Performance score
            if agent.tasks_completed > 0:
                perf_score = agent.tasks_completed / (agent.tasks_completed + agent.tasks_failed)
                score += perf_score * 0.2
            
            # Speed score
            if agent.avg_execution_time:
                speed_score = 60 / max(agent.avg_execution_time, 1)
                score += min(speed_score, 1.0) * 0.1
            
            scores[agent_id] = score
        
        # Select best
        if scores:
            best_agent = max(scores.keys(), key=lambda a: scores[a])
        else:
            best_agent = None
        
        decision = ArbitrationDecision(
            decision_id=str(uuid4()),
            task_id=task_id,
            candidate_agents=candidate_agents,
            selected_agent=best_agent,
            decision_type="score_based",
            reason=f"Best score: {scores.get(best_agent, 0):.2f}" if best_agent else "No candidates",
            scores=scores,
            confidence=scores.get(best_agent, 0) if best_agent else 0.0,
            decided_at=datetime.utcnow(),
        )
        
        self.db.add(decision)
        await self.db.commit()
        await self.db.refresh(decision)
        
        return decision


class DistributedAgentCommunicator:
    """
    Distributed agent communication layer.
    Handles inter-agent communication across distributed agents.
    """
    
    def __init__(self, db: AsyncSession, coordination_runtime: AgentCoordinationRuntime):
        self.db = db
        self.runtime = coordination_runtime
        self._channels: Dict[str, asyncio.Queue] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize the communicator"""
        self._running = True
        logger.info("DistributedAgentCommunicator initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the communicator"""
        self._running = False
        logger.info("DistributedAgentCommunicator shutdown")
    
    async def create_channel(
        self,
        channel_id: str,
    ) -> asyncio.Queue:
        """Create communication channel"""
        queue = asyncio.Queue()
        self._channels[channel_id] = queue
        return queue
    
    async def join_channel(
        self,
        agent_id: str,
        channel_id: str,
    ) -> None:
        """Join a communication channel"""
        if channel_id not in self._channels:
            await self.create_channel(channel_id)
    
    async def broadcast(
        self,
        channel_id: str,
        message: Dict[str, Any],
        exclude_agent: Optional[str] = None,
    ) -> None:
        """Broadcast message to channel"""
        queue = self._channels.get(channel_id)
        
        if not queue:
            return
        
        # Add message to queue
        await queue.put({
            "sender": "system",
            "data": message,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    async def send_to_agent(
        self,
        agent_id: str,
        message: Dict[str, Any],
    ) -> None:
        """Send message to specific agent"""
        channel_id = f"agent_{agent_id}"
        queue = self._channels.get(channel_id)
        
        if queue:
            await queue.put({
                "sender": "system",
                "data": message,
                "timestamp": datetime.utcnow().isoformat(),
            })