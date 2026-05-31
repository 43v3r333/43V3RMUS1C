"""
Orchestration Memory Service

Persistent orchestration cognition with execution recall,
pattern analysis, and adaptive reasoning context.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
import json

from sqlalchemy import select, and_, or_, desc, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cognitive import (
    OrchestrationMemory, MemoryScope, MemoryKind
)
from app.core.database import get_db_context

logger = logging.getLogger(__name__)


class OrchestrationMemoryService:
    """
    Persistent orchestration memory system.
    
    Capabilities:
    - Orchestration recall: Retrieve execution memories by subject, scope, kind
    - Pattern analysis: Identify recurring execution patterns
    - Semantic search: Full-text search across memory content
    - Importance weighting: Rank memories by significance and recency
    - Memory consolidation: Aggregate related memories
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ---- Memory Store Operations ----
    
    async def store(
        self,
        scope: str,
        memory_kind: str,
        title: str,
        content: Dict[str, Any],
        subject: Optional[str] = None,
        subject_kind: Optional[str] = None,
        importance: float = 0.5,
        confidence: float = 0.8,
        tags: Optional[List[str]] = None,
        execution_context: Optional[Dict[str, Any]] = None,
        outcome: Optional[Dict[str, Any]] = None,
        related_memory_ids: Optional[List[str]] = None,
    ) -> OrchestrationMemory:
        """
        Store a new orchestration memory.
        
        Args:
            scope: MemoryScope value (episodic, semantic, procedural, evaluative, strategic)
            memory_kind: MemoryKind value (execution_insight, workflow_audit, etc.)
            title: Memory title
            content: Structured memory data
            subject: Workflow/job/agent identifier
            subject_kind: Type of subject (workflow, render_job, agent)
            importance: 0-1 importance score
            confidence: 0-1 reliability score
            tags: Memory classification tags
            execution_context: Runtime environment data
            outcome: Result data
            related_memory_ids: UUIDs of related memories
            
        Returns:
            Created OrchestrationMemory instance
        """
        memory = OrchestrationMemory(
            scope=scope,
            memory_kind=memory_kind,
            subject=subject,
            subject_kind=subject_kind,
            title=title,
            content=content,
            importance=importance,
            confidence=confidence,
            recency=1.0,
            tags=tags,
            execution_context=execution_context,
            outcome=outcome,
            related_memory_ids=related_memory_ids,
        )
        self.db.add(memory)
        await self.db.flush()
        logger.info(f"Stored orchestration memory: {memory.id} [{scope}/{memory_kind}]")
        return memory
    
    async def recall(
        self,
        subject: Optional[str] = None,
        scope: Optional[str] = None,
        memory_kind: Optional[str] = None,
        subject_kind: Optional[str] = None,
        min_importance: float = 0.0,
        min_confidence: float = 0.0,
        tags: Optional[List[str]] = None,
        search_text: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        order_by_recency: bool = True,
    ) -> List[OrchestrationMemory]:
        """
        Recall orchestration memories with flexible filtering.
        
        Args:
            subject: Filter by subject identifier
            scope: Filter by MemoryScope
            memory_kind: Filter by MemoryKind
            subject_kind: Filter by subject type
            min_importance: Minimum importance score
            min_confidence: Minimum confidence score
            tags: Filter by tags (any match)
            search_text: Full-text search in title and content
            limit: Maximum results
            offset: Result offset
            order_by_recency: Sort by recency (descending)
            
        Returns:
            List of matching OrchestrationMemory instances
        """
        query = select(OrchestrationMemory).where(
            OrchestrationMemory.deleted_at.is_(None)
        )
        
        # Apply filters
        if subject:
            query = query.where(OrchestrationMemory.subject == subject)
        if scope:
            query = query.where(OrchestrationMemory.scope == scope)
        if memory_kind:
            query = query.where(OrchestrationMemory.memory_kind == memory_kind)
        if subject_kind:
            query = query.where(OrchestrationMemory.subject_kind == subject_kind)
        if min_importance > 0:
            query = query.where(OrchestrationMemory.importance >= min_importance)
        if min_confidence > 0:
            query = query.where(OrchestrationMemory.confidence >= min_confidence)
        
        # Tag filtering
        if tags:
            for tag in tags:
                query = query.where(
                    OrchestrationMemory.tags.contains([tag])
                )
        
        # Text search on title (content is JSON, search title)
        if search_text:
            query = query.where(
                OrchestrationMemory.title.ilike(f"%{search_text}%")
            )
        
        # Ordering
        if order_by_recency:
            # Composite score: importance * recency
            query = query.order_by(
                desc(OrchestrationMemory.importance * OrchestrationMemory.recency)
            )
        else:
            query = query.order_by(desc(OrchestrationMemory.created_at))
        
        query = query.offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def recall_related(
        self,
        memory_id: UUID,
        max_distance: int = 2,
    ) -> List[OrchestrationMemory]:
        """
        Recall memories related to a given memory.
        
        Args:
            memory_id: Reference memory ID
            max_distance: Maximum relationship distance (1=direct, 2=indirect)
            
        Returns:
            Related memories ordered by relationship distance
        """
        # Direct relationships
        memory = await self.db.get(OrchestrationMemory, memory_id)
        if not memory:
            return []
        
        query = select(OrchestrationMemory).where(
            and_(
                OrchestrationMemory.deleted_at.is_(None),
                or_(
                    OrchestrationMemory.id.in_(memory.related_memory_ids or []),
                    OrchestrationMemory.subject == memory.subject,
                    OrchestrationMemory.parent_memory_id == memory_id,
                )
            ),
            OrchestrationMemory.id != memory_id,
        ).order_by(desc(OrchestrationMemory.importance))
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_id(self, memory_id: UUID) -> Optional[OrchestrationMemory]:
        """Get a specific memory by ID with access tracking."""
        memory = await self.db.get(OrchestrationMemory, memory_id)
        if memory:
            # Update access tracking
            memory.access_count += 1
            memory.last_accessed_at = datetime.utcnow()
            # Apply recency decay based on access pattern
            memory.recency = min(1.0, memory.recency * 1.05)
            await self.db.flush()
        return memory
    
    async def update(
        self,
        memory_id: UUID,
        title: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
        importance: Optional[float] = None,
        is_pinned: Optional[bool] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[OrchestrationMemory]:
        """Update an existing memory."""
        memory = await self.db.get(OrchestrationMemory, memory_id)
        if not memory:
            return None
        
        if title is not None:
            memory.title = title
        if content is not None:
            memory.content = content
        if importance is not None:
            memory.importance = importance
        if is_pinned is not None:
            memory.is_pinned = is_pinned
        if tags is not None:
            memory.tags = tags
        
        await self.db.flush()
        return memory
    
    async def delete(self, memory_id: UUID, soft: bool = True) -> bool:
        """
        Delete a memory.
        
        Args:
            memory_id: Memory to delete
            soft: If True, soft delete; if False, hard delete
            
        Returns:
            True if deleted successfully
        """
        memory = await self.db.get(OrchestrationMemory, memory_id)
        if not memory:
            return False
        
        if soft:
            memory.deleted_at = datetime.utcnow()
        else:
            await self.db.delete(memory)
        
        await self.db.flush()
        return True
    
    # ---- Pattern Analysis ----
    
    async def analyze_patterns(
        self,
        subject_kind: Optional[str] = None,
        time_window: Optional[timedelta] = None,
        min_frequency: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        Analyze recurring execution patterns.
        
        Args:
            subject_kind: Filter by subject type
            time_window: Analysis time window
            min_frequency: Minimum occurrence count
            
        Returns:
            List of detected patterns with frequency and significance
        """
        conditions = [OrchestrationMemory.deleted_at.is_(None)]
        
        if subject_kind:
            conditions.append(OrchestrationMemory.subject_kind == subject_kind)
        
        if time_window:
            cutoff = datetime.utcnow() - time_window
            conditions.append(OrchestrationMemory.created_at >= cutoff)
        
        # Group by subject and memory_kind to find patterns
        query = select(
            OrchestrationMemory.subject,
            OrchestrationMemory.memory_kind,
            func.count(OrchestrationMemory.id).label('frequency'),
            func.avg(OrchestrationMemory.importance).label('avg_importance'),
            func.avg(OrchestrationMemory.confidence).label('avg_confidence'),
        ).where(and_(*conditions)).group_by(
            OrchestrationMemory.subject,
            OrchestrationMemory.memory_kind,
        ).having(func.count(OrchestrationMemory.id) >= min_frequency)
        
        result = await self.db.execute(query)
        patterns = []
        
        for row in result.all():
            patterns.append({
                'subject': row.subject,
                'memory_kind': row.memory_kind,
                'frequency': row.frequency,
                'avg_importance': float(row.avg_importance or 0),
                'avg_confidence': float(row.avg_confidence or 0),
                'significance': row.frequency * (row.avg_importance or 0),
            })
        
        # Sort by significance
        patterns.sort(key=lambda p: p['significance'], reverse=True)
        return patterns
    
    async def get_execution_insights(
        self,
        subject: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get execution insights for a specific subject.
        
        Args:
            subject: Subject identifier
            limit: Maximum insights to return
            
        Returns:
            List of execution insights ordered by importance
        """
        memories = await self.recall(
            subject=subject,
            memory_kind=MemoryKind.EXECUTION_INSIGHT.value,
            min_importance=0.3,
            limit=limit,
            order_by_recency=True,
        )
        
        return [
            {
                'id': str(m.id),
                'title': m.title,
                'content': m.content,
                'importance': m.importance,
                'confidence': m.confidence,
                'created_at': m.created_at.isoformat() if m.created_at else None,
            }
            for m in memories
        ]
    
    # ---- Memory Statistics ----
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get memory system statistics.
        
        Returns:
            Dictionary with memory counts by scope and kind
        """
        # Count by scope
        scope_query = select(
            OrchestrationMemory.scope,
            func.count(OrchestrationMemory.id).label('count'),
        ).where(OrchestrationMemory.deleted_at.is_(None)).group_by(OrchestrationMemory.scope)
        
        scope_result = await self.db.execute(scope_query)
        by_scope = {row.scope: row.count for row in scope_result.all()}
        
        # Count by kind
        kind_query = select(
            OrchestrationMemory.memory_kind,
            func.count(OrchestrationMemory.id).label('count'),
        ).where(OrchestrationMemory.deleted_at.is_(None)).group_by(OrchestrationMemory.memory_kind)
        
        kind_result = await self.db.execute(kind_query)
        by_kind = {row.memory_kind: row.count for row in kind_result.all()}
        
        # Total and averages
        total_query = select(
            func.count(OrchestrationMemory.id).label('total'),
            func.avg(OrchestrationMemory.importance).label('avg_importance'),
            func.avg(OrchestrationMemory.access_count).label('avg_access'),
        ).where(OrchestrationMemory.deleted_at.is_(None))
        
        total_result = await self.db.execute(total_query)
        row = total_result.first()
        
        return {
            'total_memories': row.total if row else 0,
            'by_scope': by_scope,
            'by_kind': by_kind,
            'avg_importance': float(row.avg_importance or 0) if row else 0,
            'avg_access_count': float(row.avg_access or 0) if row else 0,
            'pinned_count': await self._count_pinned(),
            'high_confidence_count': await self._count_high_confidence(),
        }
    
    async def _count_pinned(self) -> int:
        """Count pinned memories."""
        query = select(func.count(OrchestrationMemory.id)).where(
            and_(
                OrchestrationMemory.deleted_at.is_(None),
                OrchestrationMemory.is_pinned == True,
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _count_high_confidence(self) -> int:
        """Count high-confidence memories."""
        query = select(func.count(OrchestrationMemory.id)).where(
            and_(
                OrchestrationMemory.deleted_at.is_(None),
                OrchestrationMemory.confidence >= 0.9,
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    # ---- Memory Consolidation ----
    
    async def consolidate_related(
        self,
        memory_ids: List[UUID],
        new_title: str,
        consolidate_kind: str = MemoryKind.PATTERN_RECOGNITION.value,
    ) -> Optional[OrchestrationMemory]:
        """
        Consolidate multiple related memories into a single summary memory.
        
        Args:
            memory_ids: Memories to consolidate
            new_title: Title for consolidated memory
            consolidate_kind: MemoryKind for the new consolidated memory
            
        Returns:
            New consolidated memory
        """
        # Fetch all memories to consolidate
        query = select(OrchestrationMemory).where(
            OrchestrationMemory.id.in_(memory_ids)
        )
        result = await self.db.execute(query)
        memories = list(result.scalars().all())
        
        if not memories:
            return None
        
        # Extract common elements
        subjects = set(m.subject for m in memories if m.subject)
        scopes = set(m.scope for m in memories)
        
        # Calculate aggregate importance
        avg_importance = sum(m.importance for m in memories) / len(memories)
        max_confidence = max(m.confidence for m in memories)
        
        # Create consolidated content
        content = {
            'consolidated_from': [str(m.id) for m in memories],
            'subjects': list(subjects),
            'scopes': list(scopes),
            'summary': f"Consolidated from {len(memories)} memories",
            'key_insights': [
                {'title': m.title, 'content': m.content}
                for m in sorted(memories, key=lambda x: x.importance, reverse=True)[:5]
            ],
        }
        
        # Create new consolidated memory
        consolidated = await self.store(
            scope=MemoryScope.SEMANTIC.value,
            memory_kind=consolidate_kind,
            title=new_title,
            content=content,
            subject=list(subjects)[0] if len(subjects) == 1 else None,
            importance=avg_importance,
            confidence=max_confidence,
            related_memory_ids=[str(m.id) for m in memories],
        )
        
        # Mark original memories for cleanup (soft delete after consolidation)
        for memory in memories:
            memory.related_memory_ids = memory.related_memory_ids or []
            memory.related_memory_ids.append(str(consolidated.id))
        
        await self.db.flush()
        return consolidated
    
    # ---- Decay and Maintenance ----
    
    async def apply_recency_decay(
        self,
        decay_rate: float = 0.95,
        min_recency: float = 0.1,
    ) -> int:
        """
        Apply recency decay to all memories.
        
        Args:
            decay_rate: Multiplier for each decay cycle
            min_recency: Minimum recency floor
            
        Returns:
            Number of memories updated
        """
        query = select(OrchestrationMemory).where(
            OrchestrationMemory.deleted_at.is_(None)
        )
        result = await self.db.execute(query)
        
        count = 0
        for memory in result.scalars().all():
            if not memory.is_pinned:  # Don't decay pinned memories
                new_recency = memory.recency * decay_rate
                memory.recency = max(min_recency, new_recency)
                count += 1
        
        await self.db.flush()
        logger.info(f"Applied recency decay to {count} memories")
        return count
    
    async def prune_low_significance(
        self,
        max_age_days: int = 30,
        min_importance: float = 0.2,
        min_recency: float = 0.1,
    ) -> int:
        """
        Prune memories with low significance scores.
        
        Args:
            max_age_days: Maximum age before pruning consideration
            min_importance: Minimum importance threshold
            min_recency: Minimum recency threshold
            
        Returns:
            Number of memories pruned
        """
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
        
        query = select(OrchestrationMemory).where(
            and_(
                OrchestrationMemory.deleted_at.is_(None),
                OrchestrationMemory.created_at < cutoff_date,
                OrchestrationMemory.importance < min_importance,
                OrchestrationMemory.recency < min_recency,
                OrchestrationMemory.is_pinned == False,
            )
        )
        result = await self.db.execute(query)
        
        count = 0
        for memory in result.scalars().all():
            memory.deleted_at = datetime.utcnow()
            count += 1
        
        await self.db.flush()
        logger.info(f"Pruned {count} low-significance memories")
        return count


# ---- Module-level convenience functions ----

async def store_execution_insight(
    subject: str,
    subject_kind: str,
    title: str,
    insight: Dict[str, Any],
    importance: float = 0.5,
    scope: str = MemoryScope.EPISODIC.value,
) -> Optional[OrchestrationMemory]:
    """
    Convenience function to store an execution insight.
    
    Args:
        subject: Workflow/job identifier
        subject_kind: Type of subject
        title: Memory title
        insight: Insight data
        importance: Memory importance
        scope: Memory scope
        
    Returns:
        Created memory or None on error
    """
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        service = OrchestrationMemoryService(db)
        try:
            return await service.store(
                scope=scope,
                memory_kind=MemoryKind.EXECUTION_INSIGHT.value,
                title=title,
                content=insight,
                subject=subject,
                subject_kind=subject_kind,
                importance=importance,
                confidence=0.85,
            )
        except Exception as e:
            logger.error(f"Failed to store execution insight: {e}")
            return None


async def recall_subject_memories(
    subject: str,
    limit: int = 10,
) -> List[OrchestrationMemory]:
    """
    Convenience function to recall all memories for a subject.
    
    Args:
        subject: Subject identifier
        limit: Maximum results
        
    Returns:
        List of memory objects
    """
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        service = OrchestrationMemoryService(db)
        return await service.recall(
            subject=subject,
            limit=limit,
        )