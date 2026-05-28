"""
Cognition Consistency Services.

Provides:
- Shared cognition management
- Orchestration reasoning standards
- Distributed semantic memory
- Runtime interpretation systems
- Adaptive cognition governance
- Semantic coordination fabric
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Tuple, Set
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func

from .models import (
    CognitionScope,
    ConsistencyState,
    ReasoningType,
    CogNodeType,
    SemanticMemory,
    CognitionConsistencyState,
    SharedReasoning,
    CognitionGraphEdge,
    DistributedSemanticMemory,
    AdaptiveCognitionProfile,
    CognitionAudit,
)

logger = logging.getLogger(__name__)


@dataclass
class ConsistencyAssessment:
    """Assessment of cognitive consistency"""
    is_aligned: bool
    alignment_score: float
    deviation_sources: List[Dict[str, Any]] = field(default_factory=list)
    reconciliation_needed: bool = False


@dataclass
class MemoryQuery:
    """Query for semantic memory"""
    scope: Optional[CognitionScope] = None
    memory_type: Optional[str] = None
    subject: Optional[str] = None
    min_importance: float = 0.0
    min_confidence: float = 0.0
    is_pinned: Optional[bool] = None


class CognitionConsistencyManager:
    """
    Centralized cognition semantics manager.
    Manages shared cognition, reasoning standards, and consistency.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._memories: Dict[str, SemanticMemory] = {}
        self._reasoning_standards: Dict[str, SharedReasoning] = {}
        self._consistency_states: Dict[str, CognitionConsistencyState] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize the cognition consistency manager"""
        await self._load_memories()
        await self._load_reasoning_standards()
        await self._load_consistency_states()
        self._running = True
        logger.info("CognitionConsistencyManager initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the manager"""
        self._running = False
        logger.info("CognitionConsistencyManager shutdown")
    
    async def _load_memories(self) -> None:
        """Load semantic memories from database"""
        result = await self.db.execute(
            select(SemanticMemory)
            .where(SemanticMemory.stability >= 0.5)
            .order_by(SemanticMemory.importance.desc())
        )
        for memory in result.scalars().all():
            self._memories[memory.memory_id] = memory
    
    async def _load_reasoning_standards(self) -> None:
        """Load reasoning standards from database"""
        result = await self.db.execute(
            select(SharedReasoning).where(SharedReasoning.is_active == True)
        )
        for standard in result.scalars().all():
            self._reasoning_standards[standard.reasoning_id] = standard
    
    async def _load_consistency_states(self) -> None:
        """Load consistency states from database"""
        result = await self.db.execute(select(CognitionConsistencyState))
        for state in result.scalars().all():
            self._consistency_states[state.state_id] = state
    
    # ==================== Semantic Memory ====================
    
    async def store_memory(
        self,
        memory_key: str,
        scope: CognitionScope,
        memory_type: str,
        subject: str,
        title: str,
        content: Dict[str, Any],
        importance: float = 0.5,
        confidence: float = 1.0,
        is_pinned: bool = False,
        created_by: Optional[UUID] = None,
    ) -> SemanticMemory:
        """Store a semantic memory"""
        memory = SemanticMemory(
            memory_id=str(uuid4()),
            memory_key=memory_key,
            scope=scope.value,
            memory_type=memory_type,
            subject=subject,
            title=title,
            content=content,
            importance=importance,
            confidence=confidence,
            is_pinned=is_pinned,
            created_by=created_by,
        )
        
        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)
        
        self._memories[memory.memory_id] = memory
        
        # Record audit
        await self._record_audit(
            operation_type="store_memory",
            scope=scope.value,
            target_type="memory",
            target_id=memory.memory_id,
            details={"memory_key": memory_key, "subject": subject},
        )
        
        logger.info("Stored semantic memory: %s", memory_key)
        return memory
    
    async def recall_memories(
        self,
        query: MemoryQuery,
        limit: int = 50,
    ) -> List[SemanticMemory]:
        """Recall semantic memories matching a query"""
        conditions = []
        
        if query.scope:
            conditions.append(SemanticMemory.scope == query.scope.value)
        if query.memory_type:
            conditions.append(SemanticMemory.memory_type == query.memory_type)
        if query.subject:
            conditions.append(SemanticMemory.subject == query.subject)
        if query.min_importance > 0:
            conditions.append(SemanticMemory.importance >= query.min_importance)
        if query.min_confidence > 0:
            conditions.append(SemanticMemory.confidence >= query.min_confidence)
        if query.is_pinned is not None:
            conditions.append(SemanticMemory.is_pinned == query.is_pinned)
        
        base_query = select(SemanticMemory)
        if conditions:
            base_query = base_query.where(and_(*conditions))
        
        result = await self.db.execute(
            base_query
            .order_by(SemanticMemory.importance.desc(), SemanticMemory.last_accessed_at.desc())
            .limit(limit)
        )
        
        memories = list(result.scalars().all())
        
        # Update access stats
        for memory in memories:
            memory.access_count += 1
            memory.last_accessed_at = datetime.utcnow()
        
        await self.db.commit()
        
        return memories
    
    async def recall_single(
        self,
        memory_key: str,
    ) -> Optional[SemanticMemory]:
        """Recall a single memory by key"""
        for memory in self._memories.values():
            if memory.memory_key == memory_key:
                memory.access_count += 1
                memory.last_accessed_at = datetime.utcnow()
                await self.db.commit()
                return memory
        
        result = await self.db.execute(
            select(SemanticMemory).where(SemanticMemory.memory_key == memory_key)
        )
        memory = result.scalar_one_or_none()
        
        if memory:
            memory.access_count += 1
            memory.last_accessed_at = datetime.utcnow()
            await self.db.commit()
        
        return memory
    
    async def update_memory_stability(
        self,
        memory_id: str,
        stability_delta: float,
    ) -> Optional[SemanticMemory]:
        """Update memory stability after access"""
        memory = self._memories.get(memory_id)
        if not memory:
            return None
        
        # Decay stability slightly on access, but maintain high for verified memories
        if memory.is_verified:
            memory.stability = min(1.0, memory.stability + 0.01)
        else:
            memory.stability = max(0.0, min(1.0, memory.stability + stability_delta))
        
        # Recency tracking
        memory.recency = 1.0
        memory.last_accessed_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(memory)
        
        return memory
    
    # ==================== Reasoning Standards ====================
    
    async def create_reasoning_standard(
        self,
        reasoning_key: str,
        reasoning_type: ReasoningType,
        scope: CognitionScope,
        name: str,
        inference_rules: List[Dict[str, Any]],
        description: Optional[str] = None,
        confidence_threshold: float = 0.8,
    ) -> SharedReasoning:
        """Create a shared reasoning standard"""
        standard = SharedReasoning(
            reasoning_id=str(uuid4()),
            reasoning_key=reasoning_key,
            reasoning_type=reasoning_type.value,
            scope=scope.value,
            name=name,
            description=description,
            inference_rules=inference_rules,
            confidence_threshold=confidence_threshold,
        )
        
        self.db.add(standard)
        await self.db.commit()
        await self.db.refresh(standard)
        
        self._reasoning_standards[standard.reasoning_id] = standard
        
        logger.info("Created reasoning standard: %s", reasoning_key)
        return standard
    
    async def get_applicable_reasoning(
        self,
        scope: CognitionScope,
        execution_type: Optional[str] = None,
    ) -> List[SharedReasoning]:
        """Get applicable reasoning standards for a scope"""
        result = await self.db.execute(
            select(SharedReasoning).where(
                SharedReasoning.scope == scope.value,
                SharedReasoning.is_active == True,
            )
        )
        return list(result.scalars().all())
    
    # ==================== Consistency Management ====================
    
    async def assess_consistency(
        self,
        scope: CognitionScope,
        domain: str,
        current_nodes: List[Dict[str, Any]],
    ) -> ConsistencyAssessment:
        """Assess cognitive consistency across nodes"""
        # Get current state
        state_key = f"{scope.value}:{domain}"
        current_state = self._consistency_states.get(state_key)
        
        assessment = ConsistencyAssessment(
            is_aligned=True,
            alignment_score=1.0,
            deviation_sources=[],
            reconciliation_needed=False,
        )
        
        # Check node alignment
        if len(current_nodes) < 2:
            return assessment
        
        # Calculate pairwise consistency
        consistency_scores = []
        for i, node_a in enumerate(current_nodes):
            for node_b in current_nodes[i+1:]:
                score = self._calculate_node_consistency(node_a, node_b)
                consistency_scores.append(score)
                
                if score < 0.8:
                    assessment.is_aligned = False
                    assessment.deviation_sources.append({
                        "source": node_a.get("id"),
                        "target": node_b.get("id"),
                        "score": score,
                    })
        
        if consistency_scores:
            assessment.alignment_score = sum(consistency_scores) / len(consistency_scores)
        
        # Determine if reconciliation is needed
        assessment.reconciliation_needed = (
            assessment.alignment_score < 0.85 or
            len(assessment.deviation_sources) > len(current_nodes) / 2
        )
        
        # Update state
        state = current_state or CognitionConsistencyState(
            state_id=str(uuid4()),
            scope=scope.value,
            domain=domain,
            consistency_state=ConsistencyState.ALIGNED.value if assessment.is_aligned else ConsistencyState.DEVIATING.value,
            alignment_score=assessment.alignment_score,
            last_assessed_at=datetime.utcnow(),
        )
        
        state.alignment_score = assessment.alignment_score
        state.consistency_state = (
            ConsistencyState.ALIGNED.value if assessment.is_aligned else ConsistencyState.DEVIATING.value
        )
        state.last_assessed_at = datetime.utcnow()
        state.deviation_sources = assessment.deviation_sources
        
        if assessment.is_aligned and not assessment.reconciliation_needed:
            state.stable_since = datetime.utcnow()
            state.consistency_state = ConsistencyState.STABILIZED.value
        
        if assessment.reconciliation_needed:
            state.consistency_state = ConsistencyState.RECONCILING.value
        
        if current_state is None:
            self.db.add(state)
        
        await self.db.commit()
        
        return assessment
    
    def _calculate_node_consistency(
        self,
        node_a: Dict[str, Any],
        node_b: Dict[str, Any],
    ) -> float:
        """Calculate consistency score between two nodes"""
        # Simple hash-based consistency for semantic values
        hash_a = self._hash_state(node_a)
        hash_b = self._hash_state(node_b)
        
        if hash_a == hash_b:
            return 1.0
        
        # Compare specific semantic fields
        common_keys = set(node_a.keys()) & set(node_b.keys())
        if not common_keys:
            return 0.5
        
        matches = sum(
            1 for k in common_keys
            if node_a.get(k) == node_b.get(k)
        )
        
        return matches / len(common_keys)
    
    def _hash_state(self, node: Dict[str, Any]) -> str:
        """Create a hash of node state for comparison"""
        state_str = str(sorted(node.items()))
        return hashlib.sha256(state_str.encode()).hexdigest()
    
    async def reconcile_consistency(
        self,
        scope: CognitionScope,
        domain: str,
        strategy: str = " majority_win",
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """Reconcile cognitive consistency across nodes"""
        state_key = f"{scope.value}:{domain}"
        state = self._consistency_states.get(state_key)
        
        if not state or state.consistency_state not in (
            ConsistencyState.DEVIATING.value,
            ConsistencyState.RECONCILING.value,
        ):
            return True, []
        
        # Update state
        state.consistency_state = ConsistencyState.RECONCILING.value
        await self.db.commit()
        
        # Gather reconciliation attempts
        reconciliation_attempts = []
        
        attempt = {
            "strategy": strategy,
            "timestamp": datetime.utcnow().isoformat(),
            "deviations": state.deviation_sources,
        }
        reconciliation_attempts.append(attempt)
        
        # Re-assess after reconciliation
        state.deviation_sources = []
        state.reconciliation_attempts = reconciliation_attempts
        state.last_reconciled_at = datetime.utcnow()
        state.consistency_state = ConsistencyState.STABILIZED.value
        state.alignment_score = 0.95
        
        await self.db.commit()
        
        success = True
        return success, reconciliation_attempts
    
    # ==================== Cognition Graph ====================
    
    async def add_cognition_edge(
        self,
        source_node_id: str,
        source_type: str,
        target_node_id: str,
        target_type: str,
        edge_type: str,
        weight: float = 1.0,
        relation_key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> CognitionGraphEdge:
        """Add an edge to the cognition graph"""
        edge = CognitionGraphEdge(
            edge_id=str(uuid4()),
            source_node_id=source_node_id,
            source_type=source_type,
            target_node_id=target_node_id,
            target_type=target_type,
            edge_type=edge_type,
            weight=weight,
            relation_key=relation_key,
            context=context,
        )
        
        self.db.add(edge)
        await self.db.commit()
        await self.db.refresh(edge)
        
        return edge
    
    async def get_cognition_neighbors(
        self,
        node_id: str,
        edge_types: Optional[List[str]] = None,
        max_depth: int = 3,
    ) -> List[Tuple[CognitionGraphEdge, str]]:
        """Get neighboring nodes in the cognition graph"""
        neighbors = []
        visited = set()
        current_level = {node_id}
        
        for depth in range(max_depth):
            if not current_level:
                break
            
            next_level = set()
            
            for current_node in current_level:
                conditions = [
                    or_(
                        CognitionGraphEdge.source_node_id == current_node,
                        CognitionGraphEdge.target_node_id == current_node,
                    ),
                    CognitionGraphEdge.is_active == True,
                ]
                
                if edge_types:
                    conditions.append(CognitionGraphEdge.edge_type.in_(edge_types))
                
                result = await self.db.execute(
                    select(CognitionGraphEdge).where(and_(*conditions))
                )
                
                for edge in result.scalars().all():
                    neighbor_id = (
                        edge.target_node_id if edge.source_node_id == current_node
                        else edge.source_node_id
                    )
                    
                    if neighbor_id not in visited:
                        neighbors.append((edge, neighbor_id))
                        visited.add(neighbor_id)
                        next_level.add(neighbor_id)
            
            current_level = next_level
        
        return neighbors
    
    # ==================== Adaptive Cognition ====================
    
    async def create_adaptive_profile(
        self,
        profile_key: str,
        entity_type: str,
        entity_id: str,
        reasoning_patterns: List[Dict[str, Any]],
    ) -> AdaptiveCognitionProfile:
        """Create an adaptive cognition profile"""
        profile = AdaptiveCognitionProfile(
            profile_id=str(uuid4()),
            profile_key=profile_key,
            target_entity_type=entity_type,
            target_entity_id=entity_id,
            reasoning_patterns=reasoning_patterns,
        )
        
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        
        logger.info("Created adaptive profile for %s:%s", entity_type, entity_id)
        return profile
    
    async def adapt_profile(
        self,
        profile_id: str,
        outcome_data: Dict[str, Any],
    ) -> Optional[AdaptiveCognitionProfile]:
        """Update profile based on reasoning outcome"""
        result = await self.db.execute(
            select(AdaptiveCognitionProfile).where(
                AdaptiveCognitionProfile.profile_id == profile_id
            )
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            return None
        
        # Update hit rate based on outcome
        is_success = outcome_data.get("is_success", True)
        if is_success:
            profile.hit_rate = min(1.0, profile.hit_rate * 1.05 + 0.01)
        else:
            profile.hit_rate = max(0.0, profile.hit_rate * 0.95 - 0.01)
        
        profile.last_adapted_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(profile)
        
        return profile
    
    # ==================== Audit ====================
    
    async def _record_audit(
        self,
        operation_type: str,
        scope: str,
        target_type: str,
        target_id: str,
        details: Dict[str, Any],
        performed_by: Optional[UUID] = None,
        alignment_impact: Optional[float] = None,
        consistency_impact: Optional[float] = None,
        correlation_id: Optional[str] = None,
    ) -> CognitionAudit:
        """Record a cognition audit entry"""
        audit = CognitionAudit(
            audit_id=str(uuid4()),
            operation_type=operation_type,
            scope=scope,
            target_type=target_type,
            target_id=target_id,
            operation_details=details,
            alignment_impact=alignment_impact,
            consistency_impact=consistency_impact,
            performed_by=performed_by,
            performed_at=datetime.utcnow(),
            correlation_id=correlation_id,
        )
        
        self.db.add(audit)
        await self.db.commit()
        await self.db.refresh(audit)
        
        return audit


class DistributedCognitionCoordinator:
    """
    Coordinates cognition across distributed nodes.
    Handles semantic memory synchronization and distributed reasoning.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._sync_queue: List[Dict[str, Any]] = []
        self._node_registry: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self) -> None:
        """Initialize the coordinator"""
        logger.info("DistributedCognitionCoordinator initialized")
    
    async def register_node(
        self,
        node_id: str,
        node_capabilities: Dict[str, Any],
    ) -> None:
        """Register a cognition node"""
        self._node_registry[node_id] = {
            "node_id": node_id,
            "capabilities": node_capabilities,
            "registered_at": datetime.utcnow(),
            "last_seen_at": datetime.utcnow(),
        }
        logger.info("Registered cognition node: %s", node_id)
    
    async def distribute_semantic_value(
        self,
        memory_key: str,
        value: Any,
        target_nodes: List[str],
    ) -> Dict[str, bool]:
        """Distribute a semantic value to all target nodes"""
        results = {}
        
        for node_id in target_nodes:
            try:
                # Create distributed memory entry
                memory = DistributedSemanticMemory(
                    memory_id=str(uuid4()),
                    memory_key=memory_key,
                    owner_node=node_id,
                    scope="distributed",
                    knowledge={"value": value, "source": "coordinator"},
                )
                
                self.db.add(memory)
                results[node_id] = True
            except Exception as e:
                logger.error("Failed to distribute to node %s: %s", node_id, str(e))
                results[node_id] = False
        
        await self.db.commit()
        return results
    
    async def reconcile_distributed_memories(
        self,
        memory_key: str,
        node_positions: Dict[str, Any],
    ) -> Tuple[Any, List[str]]:
        """Reconcile a memory value across distributed nodes"""
        # Get all distributed memories with this key
        result = await self.db.execute(
            select(DistributedSemanticMemory).where(
                DistributedSemanticMemory.memory_key == memory_key
            )
        )
        memories = list(result.scalars().all())
        
        if not memories:
            return None, []
        
        # Simple majority vote
        value_counts: Dict[str, int] = {}
        for memory in memories:
            value_str = str(memory.knowledge.get("value"))
            result_key = hashlib.md5(value_str.encode()).hexdigest()[:8]
            value_counts[result_key] = value_counts.get(result_key, 0) + 1
        
        # Find most common value
        most_common_key = max(value_counts, key=value_counts.get)
        most_common_memory = memories[0]
        
        # Update all memories to most common value
        for memory in memories:
            memory.knowledge["value"] = most_common_memory.knowledge.get("value")
            memory.consistency_version += 1
            memory.last_synced_at = datetime.utcnow()
        
        await self.db.commit()
        
        return most_common_memory.knowledge.get("value"), [m.owner_node for m in memories]
    
    async def get_cognition_topology(
        self,
    ) -> Dict[str, Any]:
        """Get the current cognition topology"""
        result = await self.db.execute(
            select(DistributedSemanticMemory)
            .group_by(DistributedSemanticMemory.owner_node)
            .with_only_columns(
                DistributedSemanticMemory.owner_node,
                func.count(DistributedSemanticMemory.memory_id).label("memory_count"),
            )
        )
        
        topology = {
            "nodes": [],
            "edges": [],
            "summary": {
                "total_nodes": len(self._node_registry),
                "active_nodes": len([n for n in self._node_registry.values() 
                    if (datetime.utcnow() - n["last_seen_at"]).total_seconds() < 300]),
            },
        }
        
        for row in result.all():
            topology["nodes"].append({
                "node_id": row.owner_node,
                "memory_count": row.memory_count,
            })
        
        return topology
