"""
Cognition Fabric Services - Unified cognition and orchestration intelligence.

Provides:
- Shared cognition memory management
- Orchestration intelligence fabric
- Semantic runtime awareness
- Distributed execution memory
- Adaptive cognition systems
"""
import asyncio
import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func

from .models import (
    AdaptiveCognitionMemory,
    SharedCognitionState,
    CognitionNode,
    CognitionEdge,
    OrchestrationIntelligenceFabric,
    CrossWorkflowIntelligence,
    CognitiveConsolidation,
    AdaptiveLearningProfile,
    SemanticRuntimeAwareness,
    CognitionConsistencyCheck,
    MemoryScope,
    MemoryKind,
    MemoryStatus,
    CognitionState,
    AdaptiveState,
)


logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Memory entry representation"""
    memory_id: str
    scope: str
    memory_kind: str
    title: str
    content: Dict[str, Any]
    importance: float
    recency: float
    confidence: float
    created_at: datetime


@dataclass
class CognitionInsight:
    """Cognition insight result"""
    insight_type: str
    confidence: float
    data: Dict[str, Any]
    recommendations: List[str]


class SharedCognitionMemory:
    """Manages shared cognition memory across the system"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._memories: Dict[str, AdaptiveCognitionMemory] = {}
        self._index_by_scope: Dict[str, Set[str]] = {}
        self._index_by_kind: Dict[str, Set[str]] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize shared cognition memory"""
        await self._load_memories()
        self._running = True
        logger.info("SharedCognitionMemory initialized with %d entries", len(self._memories))
    
    async def shutdown(self) -> None:
        """Shutdown shared cognition memory"""
        self._running = False
        logger.info("SharedCognitionMemory shutdown")
    
    async def _load_memories(self) -> None:
        """Load memories from database"""
        cutoff = datetime.utcnow() - timedelta(days=30)
        result = await self.db.execute(
            select(AdaptiveCognitionMemory).where(
                AdaptiveCognitionMemory.status == MemoryStatus.ACTIVE.value
            )
        )
        for memory in result.scalars().all():
            self._memories[memory.memory_id] = memory
            
            # Build indexes
            if memory.scope not in self._index_by_scope:
                self._index_by_scope[memory.scope] = set()
            self._index_by_scope[memory.scope].add(memory.memory_id)
            
            if memory.memory_kind not in self._index_by_kind:
                self._index_by_kind[memory.memory_kind] = set()
            self._index_by_kind[memory.memory_kind].add(memory.memory_id)
    
    # ==================== Memory Operations ====================
    
    async def store(
        self,
        scope: str,
        memory_kind: str,
        title: str,
        content: Dict[str, Any],
        subject: Optional[str] = None,
        subject_type: Optional[str] = None,
        importance: float = 0.5,
        confidence: float = 0.8,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> AdaptiveCognitionMemory:
        """Store new memory entry"""
        memory_id = f"mem-{uuid4()}"
        
        memory = AdaptiveCognitionMemory(
            memory_id=memory_id,
            scope=scope,
            memory_kind=memory_kind,
            title=title,
            content=content,
            subject=subject,
            subject_type=subject_type,
            importance=importance,
            recency=1.0,
            stability=0.5,
            confidence=confidence,
            correlation_id=correlation_id,
            context=context,
            expires_at=datetime.utcnow() + timedelta(seconds=ttl_seconds) if ttl_seconds else None,
        )
        
        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)
        
        self._memories[memory_id] = memory
        
        # Update indexes
        if scope not in self._index_by_scope:
            self._index_by_scope[scope] = set()
        self._index_by_scope[scope].add(memory_id)
        
        if memory_kind not in self._index_by_kind:
            self._index_by_kind[memory_kind] = set()
        self._index_by_kind[memory_kind].add(memory_id)
        
        return memory
    
    async def recall(
        self,
        scope: Optional[str] = None,
        memory_kind: Optional[str] = None,
        subject: Optional[str] = None,
        limit: int = 100,
    ) -> List[AdaptiveCognitionMemory]:
        """Recall memories matching criteria"""
        query = select(AdaptiveCognitionMemory).where(
            AdaptiveCognitionMemory.status == MemoryStatus.ACTIVE.value
        )
        
        if scope:
            query = query.where(AdaptiveCognitionMemory.scope == scope)
        
        if memory_kind:
            query = query.where(AdaptiveCognitionMemory.memory_kind == memory_kind)
        
        if subject:
            query = query.where(AdaptiveCognitionMemory.subject == subject)
        
        query = query.order_by(AdaptiveCognitionMemory.importance.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def access(self, memory_id: str) -> Optional[AdaptiveCognitionMemory]:
        """Access and update memory entry"""
        memory = self._memories.get(memory_id)
        if not memory:
            return None
        
        memory.access_count += 1
        memory.last_accessed = datetime.utcnow()
        
        # Update recency score
        memory.recency = min(1.0, memory.recency + 0.1)
        
        await self.db.commit()
        await self.db.refresh(memory)
        
        return memory
    
    async def update_importance(
        self,
        memory_id: str,
        importance_delta: float,
    ) -> Optional[AdaptiveCognitionMemory]:
        """Update memory importance"""
        memory = self._memories.get(memory_id)
        if not memory:
            return None
        
        memory.importance = max(0.0, min(1.0, memory.importance + importance_delta))
        memory.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return memory
    
    async def archive(self, memory_id: str) -> Optional[AdaptiveCognitionMemory]:
        """Archive memory entry"""
        memory = self._memories.get(memory_id)
        if not memory:
            return None
        
        memory.status = MemoryStatus.ARCHIVED.value
        memory.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return memory
    
    async def consolidate(
        self,
        source_ids: List[str],
    ) -> Optional[AdaptiveCognitionMemory]:
        """Consolidate multiple memories into one"""
        if not source_ids:
            return None
        
        sources = [self._memories.get(mid) for mid in source_ids if self._memories.get(mid)]
        if not sources:
            return None
        
        # Create consolidated memory
        avg_importance = sum(s.importance for s in sources) / len(sources)
        avg_confidence = sum(s.confidence for s in sources) / len(sources)
        
        consolidated_content = {
            "sources": [s.memory_id for s in sources],
            "original_contents": [s.content for s in sources],
            "consolidation_method": "averaging",
        }
        
        consolidated = await self.store(
            scope=sources[0].scope,
            memory_kind=sources[0].memory_kind,
            title=f"Consolidated from {len(sources)} memories",
            content=consolidated_content,
            importance=avg_importance,
            confidence=avg_confidence * 0.9,  # Slight confidence loss
        )
        
        # Archive sources
        for source in sources:
            await self.archive(source.memory_id)
        
        return consolidated
    
    async def search(
        self,
        query: str,
        limit: int = 20,
    ) -> List[AdaptiveCognitionMemory]:
        """Search memories by query"""
        # Simple substring search
        results = []
        query_lower = query.lower()
        
        for memory in self._memories.values():
            if memory.status != MemoryStatus.ACTIVE.value:
                continue
            
            if query_lower in memory.title.lower():
                results.append(memory)
            elif query_lower in str(memory.content).lower():
                results.append(memory)
        
        # Sort by relevance (importance * recency)
        results.sort(
            key=lambda m: m.importance * m.recency,
            reverse=True
        )
        
        return results[:limit]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        active_memories = [m for m in self._memories.values() if m.status == MemoryStatus.ACTIVE.value]
        
        scope_counts = {}
        kind_counts = {}
        
        for memory in active_memories:
            scope_counts[memory.scope] = scope_counts.get(memory.scope, 0) + 1
            kind_counts[memory.memory_kind] = kind_counts.get(memory.memory_kind, 0) + 1
        
        return {
            "total_memories": len(active_memories),
            "by_scope": scope_counts,
            "by_kind": kind_counts,
            "pinned": sum(1 for m in active_memories if m.is_pinned),
            "avg_importance": sum(m.importance for m in active_memories) / len(active_memories) if active_memories else 0,
        }


class OrchestrationIntelligenceFabric:
    """Manages global orchestration intelligence and knowledge"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._fabric: Optional[OrchestrationIntelligenceFabric] = None
        self._patterns: Dict[str, List[Dict[str, Any]]] = {}
        self._heuristics: List[Dict[str, Any]] = []
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize orchestration intelligence fabric"""
        await self._load_fabric()
        self._running = True
        logger.info("OrchestrationIntelligenceFabric initialized")
    
    async def shutdown(self) -> None:
        """Shutdown orchestration intelligence fabric"""
        self._running = False
        logger.info("OrchestrationIntelligenceFabric shutdown")
    
    async def _load_fabric(self) -> None:
        """Load fabric from database"""
        result = await self.db.execute(select(OrchestrationIntelligenceFabric))
        self._fabric = result.scalar_one_or_none()
        
        if self._fabric:
            if self._fabric.patterns:
                for pattern in self._fabric.patterns:
                    pattern_type = pattern.get("type", "unknown")
                    if pattern_type not in self._patterns:
                        self._patterns[pattern_type] = []
                    self._patterns[pattern_type].append(pattern)
            
            if self._fabric.heuristics:
                self._heuristics = self._fabric.heuristics
    
    # ==================== Fabric Operations ====================
    
    async def add_pattern(
        self,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        success_count: int = 0,
        total_uses: int = 0,
    ) -> None:
        """Add pattern to fabric"""
        pattern = {
            "type": pattern_type,
            "data": pattern_data,
            "success_rate": success_count / total_uses if total_uses > 0 else 0.5,
            "success_count": success_count,
            "total_uses": total_uses,
            "added_at": datetime.utcnow().isoformat(),
        }
        
        if pattern_type not in self._patterns:
            self._patterns[pattern_type] = []
        self._patterns[pattern_type].append(pattern)
        
        await self._persist_fabric()
    
    async def add_heuristic(
        self,
        heuristic_type: str,
        rule: Dict[str, Any],
        weight: float = 0.5,
        confidence: float = 0.5,
    ) -> None:
        """Add heuristic to fabric"""
        heuristic = {
            "type": heuristic_type,
            "rule": rule,
            "weight": weight,
            "confidence": confidence,
            "hit_count": 0,
            "miss_count": 0,
            "added_at": datetime.utcnow().isoformat(),
        }
        
        self._heuristics.append(heuristic)
        await self._persist_fabric()
    
    async def get_best_heuristic(
        self,
        heuristic_type: str,
        context: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Get best matching heuristic for context"""
        candidates = [h for h in self._heuristics if h["type"] == heuristic_type]
        
        if not candidates:
            return None
        
        # Score each heuristic
        scored = []
        for heuristic in candidates:
            score = self._score_heuristic(heuristic, context)
            scored.append((score, heuristic))
        
        # Return highest scoring
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored else None
    
    def _score_heuristic(
        self,
        heuristic: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """Score heuristic relevance"""
        base_score = heuristic["weight"]
        
        rule = heuristic["rule"]
        
        # Match conditions
        conditions = rule.get("conditions", {})
        matches = 0
        total = len(conditions)
        
        for key, expected in conditions.items():
            if key in context and context[key] == expected:
                matches += 1
        
        condition_score = matches / total if total > 0 else 0.5
        
        # Success rate
        total_uses = heuristic.get("total_uses", 0)
        success_count = heuristic.get("success_count", 0)
        success_rate = success_count / total_uses if total_uses > 0 else 0.5
        
        return base_score * 0.3 + condition_score * 0.4 + success_rate * 0.3
    
    async def record_heuristic_result(
        self,
        heuristic: Dict[str, Any],
        success: bool,
    ) -> None:
        """Record heuristic usage result"""
        for h in self._heuristics:
            if h["type"] == heuristic["type"] and h["rule"] == heuristic["rule"]:
                h["hit_count" if success else "miss_count"] += 1
                break
        
        await self._persist_fabric()
    
    async def get_recommendations(
        self,
        context: Dict[str, Any],
        recommendation_type: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get recommendations based on context"""
        recommendations = []
        
        # Check patterns
        patterns = self._patterns.get(recommendation_type, [])
        for pattern in patterns:
            score = self._score_pattern(pattern, context)
            if score > 0.5:
                recommendations.append({
                    "type": "pattern",
                    "data": pattern["data"],
                    "confidence": score,
                    "success_rate": pattern.get("success_rate", 0.5),
                })
        
        # Check heuristics
        for heuristic in self._heuristics:
            if heuristic["type"] == recommendation_type:
                score = self._score_heuristic(heuristic, context)
                if score > 0.5:
                    recommendations.append({
                        "type": "heuristic",
                        "data": heuristic["rule"],
                        "confidence": score,
                        "weight": heuristic["weight"],
                    })
        
        # Sort by confidence
        recommendations.sort(key=lambda r: r["confidence"], reverse=True)
        return recommendations[:limit]
    
    def _score_pattern(
        self,
        pattern: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """Score pattern relevance"""
        pattern_data = pattern.get("data", {})
        
        # Simple matching based on shared keys
        shared_keys = set(context.keys()) & set(pattern_data.keys())
        if not shared_keys:
            return 0.5
        
        matches = sum(1 for k in shared_keys if context[k] == pattern_data[k])
        return matches / len(shared_keys) if shared_keys else 0
    
    async def _persist_fabric(self) -> None:
        """Persist fabric to database"""
        if not self._fabric:
            self._fabric = OrchestrationIntelligenceFabric(
                fabric_id=f"fabric-{uuid4()}",
                fabric_type="orchestration",
                knowledge_graph={},
                patterns=[],
                heuristics=self._heuristics,
            )
            self.db.add(self._fabric)
        
        self._fabric.patterns = []
        for patterns in self._patterns.values():
            self._fabric.patterns.extend(patterns)
        
        self._fabric.heuristics = self._heuristics
        self._fabric.knowledge_size = len(self._patterns) + len(self._heuristics)
        self._fabric.updated_at = datetime.utcnow()
        
        await self.db.commit()


class SemanticRuntimeAwareness:
    """Manages semantic runtime awareness"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._awareness: Dict[str, SemanticRuntimeAwareness] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize semantic runtime awareness"""
        await self._load_awareness()
        self._running = True
        logger.info("SemanticRuntimeAwareness initialized")
    
    async def shutdown(self) -> None:
        """Shutdown semantic runtime awareness"""
        self._running = False
        logger.info("SemanticRuntimeAwareness shutdown")
    
    async def _load_awareness(self) -> None:
        """Load awareness from database"""
        result = await self.db.execute(select(SemanticRuntimeAwareness))
        for awareness in result.scalars().all():
            self._awareness[awareness.awareness_id] = awareness
    
    async def create_awareness(
        self,
        awareness_type: str,
        semantic_model: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        confidence: float = 0.5,
    ) -> SemanticRuntimeAwareness:
        """Create new semantic awareness"""
        awareness_id = f"awareness-{uuid4()}"
        
        awareness = SemanticRuntimeAwareness(
            awareness_id=awareness_id,
            awareness_type=awareness_type,
            semantic_model=semantic_model,
            context=context,
            confidence=confidence,
        )
        
        self.db.add(awareness)
        await self.db.commit()
        await self.db.refresh(awareness)
        
        self._awareness[awareness_id] = awareness
        return awareness
    
    async def evaluate_situation(
        self,
        awareness_type: str,
        situation: Dict[str, Any],
    ) -> CognitionInsight:
        """Evaluate situation using semantic awareness"""
        awarenesses = [a for a in self._awareness.values() if a.awareness_type == awareness_type]
        
        if not awarenesses:
            return CognitionInsight(
                insight_type="unknown",
                confidence=0.0,
                data={},
                recommendations=[],
            )
        
        # Combine awareness evaluations
        insights = []
        total_confidence = 0.0
        
        for awareness in awarenesses:
            match_score = self._evaluate_match(awareness.semantic_model, situation)
            insights.append({
                "awareness_id": awareness.awareness_id,
                "match_score": match_score,
                "confidence": awareness.confidence,
            })
            total_confidence += awareness.confidence
        
        avg_confidence = total_confidence / len(insights) if insights else 0
        
        # Generate recommendations
        recommendations = self._generate_recommendations(insights, situation)
        
        return CognitionInsight(
            insight_type=awareness_type,
            confidence=avg_confidence,
            data={"insights": insights},
            recommendations=recommendations,
        )
    
    def _evaluate_match(
        self,
        semantic_model: Dict[str, Any],
        situation: Dict[str, Any],
    ) -> float:
        """Evaluate match between semantic model and situation"""
        score = 0.0
        matches = 0
        
        for key, model_value in semantic_model.items():
            if key in situation:
                if situation[key] == model_value:
                    score += 1.0
                elif isinstance(model_value, dict) and isinstance(situation[key], dict):
                    score += self._evaluate_match(model_value, situation[key])
                matches += 1
        
        return score / matches if matches > 0 else 0.5
    
    def _generate_recommendations(
        self,
        insights: List[Dict[str, Any]],
        situation: Dict[str, Any],
    ) -> List[str]:
        """Generate recommendations based on insights"""
        recommendations = []
        
        for insight in insights:
            if insight["match_score"] > 0.7:
                recommendations.append(f"High confidence match with awareness {insight['awareness_id']}")
            elif insight["match_score"] < 0.3:
                recommendations.append(f"Consider additional context for awareness {insight['awareness_id']}")
        
        return recommendations[:5]
    
    async def update_awareness(
        self,
        awareness_id: str,
        updates: Dict[str, Any],
    ) -> Optional[SemanticRuntimeAwareness]:
        """Update awareness model"""
        awareness = self._awareness.get(awareness_id)
        if not awareness:
            return None
        
        if "semantic_model" in updates:
            awareness.semantic_model = updates["semantic_model"]
        if "context" in updates:
            awareness.context = updates["context"]
        if "confidence" in updates:
            awareness.confidence = updates["confidence"]
        
        awareness.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(awareness)
        
        return awareness


class CrossWorkflowIntelligence:
    """Manages intelligence that spans multiple workflows"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._intelligences: Dict[str, CrossWorkflowIntelligence] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize cross-workflow intelligence"""
        await self._load_intelligences()
        self._running = True
        logger.info("CrossWorkflowIntelligence initialized")
    
    async def shutdown(self) -> None:
        """Shutdown cross-workflow intelligence"""
        self._running = False
        logger.info("CrossWorkflowIntelligence shutdown")
    
    async def _load_intelligences(self) -> None:
        """Load intelligences from database"""
        result = await self.db.execute(
            select(CrossWorkflowIntelligence).where(
                CrossWorkflowIntelligence.is_validated == True
            )
        )
        for intelligence in result.scalars().all():
            self._intelligences[intelligence.intelligence_id] = intelligence
    
    async def create_intelligence(
        self,
        intelligence_type: str,
        workflow_ids: List[str],
        title: str,
        description: Optional[str] = None,
        insight_data: Optional[Dict[str, Any]] = None,
        confidence: float = 0.5,
        applicability: Optional[Dict[str, Any]] = None,
    ) -> CrossWorkflowIntelligence:
        """Create cross-workflow intelligence"""
        intelligence_id = f"intelligence-{uuid4()}"
        
        intelligence = CrossWorkflowIntelligence(
            intelligence_id=intelligence_id,
            intelligence_type=intelligence_type,
            workflow_ids=workflow_ids,
            workflow_count=len(workflow_ids),
            title=title,
            description=description,
            insight_data=insight_data,
            confidence=confidence,
            applicability=applicability,
        )
        
        self.db.add(intelligence)
        await self.db.commit()
        await self.db.refresh(intelligence)
        
        self._intelligences[intelligence_id] = intelligence
        return intelligence
    
    async def validate_intelligence(
        self,
        intelligence_id: str,
        validation_result: bool,
    ) -> Optional[CrossWorkflowIntelligence]:
        """Validate cross-workflow intelligence"""
        intelligence = self._intelligences.get(intelligence_id)
        if not intelligence:
            return None
        
        intelligence.validation_count += 1
        intelligence.is_validated = intelligence.validation_count >= 3
        
        if intelligence.is_validated:
            intelligence.validated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(intelligence)
        
        return intelligence
    
    async def get_applicable_intelligences(
        self,
        workflow_id: str,
        intelligence_type: Optional[str] = None,
    ) -> List[CrossWorkflowIntelligence]:
        """Get intelligences applicable to workflow"""
        applicable = []
        
        for intelligence in self._intelligences.values():
            if workflow_id in intelligence.workflow_ids:
                if intelligence_type and intelligence.intelligence_type != intelligence_type:
                    continue
                applicable.append(intelligence)
        
        return applicable


class AdaptiveLearningEngine:
    """Manages adaptive learning profiles"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._profiles: Dict[str, AdaptiveLearningProfile] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize adaptive learning engine"""
        await self._load_profiles()
        self._running = True
        logger.info("AdaptiveLearningEngine initialized")
    
    async def shutdown(self) -> None:
        """Shutdown adaptive learning engine"""
        self._running = False
        logger.info("AdaptiveLearningEngine shutdown")
    
    async def _load_profiles(self) -> None:
        """Load learning profiles"""
        result = await self.db.execute(
            select(AdaptiveLearningProfile).where(
                AdaptiveLearningProfile.state == AdaptiveState.LEARNING.value
            )
        )
        for profile in result.scalars().all():
            self._profiles[profile.profile_id] = profile
    
    async def create_profile(
        self,
        profile_type: str,
        patterns: Optional[List[Dict[str, Any]]] = None,
        learning_rate: float = 0.1,
    ) -> AdaptiveLearningProfile:
        """Create new learning profile"""
        profile_id = f"profile-{uuid4()}"
        
        profile = AdaptiveLearningProfile(
            profile_id=profile_id,
            profile_type=profile_type,
            patterns=patterns or [],
            learning_rate=learning_rate,
        )
        
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        
        self._profiles[profile_id] = profile
        return profile
    
    async def record_learning(
        self,
        profile_id: str,
        learning_data: Dict[str, Any],
        success: bool,
    ) -> Optional[AdaptiveLearningProfile]:
        """Record learning outcome"""
        profile = self._profiles.get(profile_id)
        if not profile:
            return None
        
        # Update adaptation
        profile.adaptation_cycles += 1
        
        # Update metrics
        if success:
            profile.accuracy = min(1.0, profile.accuracy + profile.learning_rate * 0.1)
        else:
            profile.accuracy = max(0.0, profile.accuracy - profile.learning_rate * 0.1)
        
        profile.last_training = datetime.utcnow()
        
        # Update patterns
        patterns = profile.patterns or []
        patterns.append({
            "data": learning_data,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
        })
        profile.patterns = patterns
        
        await self.db.commit()
        await self.db.refresh(profile)
        
        return profile
    
    async def adapt_profile(
        self,
        profile_id: str,
        adaptation_type: str,
    ) -> Optional[AdaptiveLearningProfile]:
        """Adapt learning profile"""
        profile = self._profiles.get(profile_id)
        if not profile:
            return None
        
        if adaptation_type == "increase_learning_rate":
            profile.learning_rate = min(1.0, profile.learning_rate * 1.2)
            profile.state = AdaptiveState.REFRACTING.value
        elif adaptation_type == "decrease_learning_rate":
            profile.learning_rate = max(0.01, profile.learning_rate * 0.8)
            profile.state = AdaptiveState.STABLE.value
        
        profile.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(profile)
        
        return profile


class CognitionConsistencyManager:
    """Manages cognition consistency checks"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._checks: Dict[str, CognitionConsistencyCheck] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize cognition consistency manager"""
        self._running = True
        logger.info("CognitionConsistencyManager initialized")
    
    async def shutdown(self) -> None:
        """Shutdown cognition consistency manager"""
        self._running = False
        logger.info("CognitionConsistencyManager shutdown")
    
    async def check_consistency(
        self,
        check_type: str,
        scope: str,
        memory_ids: List[str],
    ) -> CognitionConsistencyCheck:
        """Check consistency among memories"""
        check_id = f"check-{uuid4()}"
        
        # Perform consistency check
        violations = []
        
        # Check for conflicting data
        for i, mid1 in enumerate(memory_ids):
            for mid2 in memory_ids[i+1:]:
                conflict = self._detect_conflict(mid1, mid2)
                if conflict:
                    violations.append(conflict)
        
        is_consistent = len(violations) == 0
        consistency_score = 1.0 - (len(violations) / len(memory_ids)) if memory_ids else 1.0
        
        check = CognitionConsistencyCheck(
            check_id=check_id,
            check_type=check_type,
            scope=scope,
            is_consistent=is_consistent,
            violations=violations if violations else None,
            consistency_score=consistency_score,
        )
        
        self.db.add(check)
        await self.db.commit()
        await self.db.refresh(check)
        
        self._checks[check_id] = check
        return check
    
    def _detect_conflict(self, memory_id1: str, memory_id2: str) -> Optional[Dict[str, Any]]:
        """Detect conflict between two memories"""
        # Placeholder for conflict detection logic
        return None
    
    async def get_recent_checks(
        self,
        check_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[CognitionConsistencyCheck]:
        """Get recent consistency checks"""
        query = select(CognitionConsistencyCheck).order_by(
            CognitionConsistencyCheck.checked_at.desc()
        ).limit(limit)
        
        if check_type:
            query = query.where(CognitionConsistencyCheck.check_type == check_type)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())


class CognitionFabricService:
    """Main service for unified cognition fabric"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.shared_memory = SharedCognitionMemory(db)
        self.intelligence_fabric = OrchestrationIntelligenceFabric(db)
        self.semantic_awareness = SemanticRuntimeAwareness(db)
        self.cross_workflow_intelligence = CrossWorkflowIntelligence(db)
        self.learning_engine = AdaptiveLearningEngine(db)
        self.consistency_manager = CognitionConsistencyManager(db)
    
    async def initialize(self) -> None:
        """Initialize all sub-services"""
        await self.shared_memory.initialize()
        await self.intelligence_fabric.initialize()
        await self.semantic_awareness.initialize()
        await self.cross_workflow_intelligence.initialize()
        await self.learning_engine.initialize()
        await self.consistency_manager.initialize()
        logger.info("CognitionFabricService fully initialized")
    
    async def shutdown(self) -> None:
        """Shutdown all sub-services"""
        await self.shared_memory.shutdown()
        await self.intelligence_fabric.shutdown()
        await self.semantic_awareness.shutdown()
        await self.cross_workflow_intelligence.shutdown()
        await self.learning_engine.shutdown()
        await self.consistency_manager.shutdown()
        logger.info("CognitionFabricService shutdown")
    
    async def get_cognition_summary(self) -> Dict[str, Any]:
        """Get summary of cognition fabric state"""
        memory_stats = await self.shared_memory.get_stats()
        
        return {
            "memory_entries": memory_stats["total_memories"],
            "active_heuristics": len(self.intelligence_fabric._heuristics),
            "pattern_types": len(self.intelligence_fabric._patterns),
            "awareness_count": len(self.semantic_awareness._awareness),
            "cross_workflow_intelligences": len(self.cross_workflow_intelligence._intelligences),
            "learning_profiles": len(self.learning_engine._profiles),
        }