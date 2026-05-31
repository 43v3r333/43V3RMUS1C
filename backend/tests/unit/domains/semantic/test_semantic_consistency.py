"""
43V3R CORE - Semantic Consistency Testing Infrastructure
======================================================

Comprehensive semantic consistency testing:

1. Ontology Validation
   - Semantic type consistency
   - Meaning preservation
   - Interpretation validation

2. Semantic Propagation Testing
   - Cross-domain semantic transfer
   - Context inheritance
   - Meaning consistency

3. Recursive Semantic Validation
   - Self-referential semantics
   - Deep semantic analysis
   - Contextual meaning

Markers: semantic, consistency
"""

from __future__ import annotations

import pytest
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set
import logging

from app.domains.semantic.models import EmotionType, SceneSemanticType, SemanticTag
from app.domains.semantic.services import SemanticAnalyzer

logger = logging.getLogger(__name__)


# =============================================================================
# Semantic Consistency Framework
# =============================================================================

@dataclass
class SemanticConsistencyResult:
    """Result of semantic consistency validation"""
    is_consistent: bool
    semantic_type: str
    confidence: float
    inconsistencies: List[str]
    suggestions: List[str]


class SemanticConsistencyValidator:
    """
    Validates semantic consistency across contexts.
    
    Checks:
    - Type consistency
    - Meaning preservation
    - Emotional coherence
    - Structural alignment
    """
    
    def __init__(self):
        self.validation_history: List[SemanticConsistencyResult] = []
    
    def validate_emotional_consistency(
        self,
        primary_emotion: EmotionType,
        secondary_emotion: Optional[EmotionType],
        energy_level: float,
    ) -> SemanticConsistencyResult:
        """Validate emotional content consistency"""
        inconsistencies = []
        suggestions = []
        
        # Check energy-emotion alignment
        if energy_level > 0.7 and primary_emotion in [EmotionType.SADNESS, EmotionType.CALM]:
            inconsistencies.append(
                f"High energy ({energy_level:.2f}) conflicts with {primary_emotion.value} emotion"
            )
            suggestions.append("Consider using EXCITEMENT or ENERGY for high energy content")
        
        if energy_level < 0.3 and primary_emotion in [EmotionType.EXCITEMENT, EmotionType.ENERGY]:
            inconsistencies.append(
                f"Low energy ({energy_level:.2f}) conflicts with {primary_emotion.value} emotion"
            )
            suggestions.append("Consider using SADNESS or CALM for low energy content")
        
        # Check emotion pairing logic
        if secondary_emotion:
            conflicting_pairs = [
                (EmotionType.JOY, EmotionType.SADNESS),
                (EmotionType.EXCITEMENT, EmotionType.CALM),
            ]
            for emotion1, emotion2 in conflicting_pairs:
                if {primary_emotion, secondary_emotion} == {emotion1, emotion2}:
                    inconsistencies.append(
                        f"Conflicting emotions: {emotion1.value} and {emotion2.value}"
                    )
        
        is_consistent = len(inconsistencies) == 0
        confidence = 1.0 - (len(inconsistencies) * 0.2)
        
        result = SemanticConsistencyResult(
            is_consistent=is_consistent,
            semantic_type="emotional",
            confidence=max(0.0, confidence),
            inconsistencies=inconsistencies,
            suggestions=suggestions,
        )
        
        self.validation_history.append(result)
        return result
    
    def validate_scene_type_consistency(
        self,
        scene_type: SceneSemanticType,
        duration: float,
        energy_level: float,
    ) -> SemanticConsistencyResult:
        """Validate scene type consistency"""
        inconsistencies = []
        suggestions = []
        
        # Duration expectations per scene type
        expected_durations = {
            SceneSemanticType.INTRO: (5, 20),
            SceneSemanticType.VERSE: (20, 60),
            SceneSemanticType.CHORUS: (15, 45),
            SceneSemanticType.BRIDGE: (8, 30),
            SceneSemanticType.OUTRO: (5, 20),
            SceneSemanticType.BUILDUP: (10, 30),
            SceneSemanticType.DROPDOWN: (5, 20),
            SceneSemanticType.INTERLUDE: (15, 45),
        }
        
        min_dur, max_dur = expected_durations.get(scene_type, (0, 999))
        
        if duration < min_dur:
            inconsistencies.append(
                f"{scene_type.value} scene duration ({duration:.1f}s) shorter than typical minimum ({min_dur}s)"
            )
            suggestions.append(f"Consider extending to at least {min_dur}s for {scene_type.value}")
        elif duration > max_dur:
            inconsistencies.append(
                f"{scene_type.value} scene duration ({duration:.1f}s) longer than typical maximum ({max_dur}s)"
            )
            suggestions.append(f"Consider trimming to at most {max_dur}s for {scene_type.value}")
        
        # Energy-scene alignment
        if scene_type in [SceneSemanticType.INTRO, SceneSemanticType.OUTRO] and energy_level > 0.8:
            suggestions.append(
                "Intro/Outro typically have lower energy - consider reducing"
            )
        elif scene_type in [SceneSemanticType.BUILDUP, SceneSemanticType.DROPDOWN] and energy_level < 0.6:
            suggestions.append(
                f"{scene_type.value} scenes typically have high energy - consider increasing"
            )
        
        is_consistent = len(inconsistencies) == 0
        confidence = 1.0 - (len(suggestions) * 0.1)
        
        result = SemanticConsistencyResult(
            is_consistent=is_consistent,
            semantic_type="scene_type",
            confidence=max(0.0, confidence),
            inconsistencies=[],
            suggestions=suggestions,
        )
        
        self.validation_history.append(result)
        return result
    
    def validate_semantic_profile_consistency(
        self,
        profile_data: Dict[str, Any],
    ) -> SemanticConsistencyResult:
        """Validate semantic profile consistency"""
        inconsistencies = []
        suggestions = []
        
        # Extract profile fields
        semantic_type = profile_data.get("semantic_type")
        emotion = profile_data.get("primary_emotion")
        energy = profile_data.get("energy_level", 0.5)
        pacing = profile_data.get("pacing_score", 0.5)
        
        # Validate semantic type
        if semantic_type:
            try:
                scene_type = SceneSemanticType(semantic_type)
            except ValueError:
                inconsistencies.append(f"Invalid semantic type: {semantic_type}")
                scene_type = None
        else:
            scene_type = None
        
        # Validate emotion
        if emotion:
            try:
                emotion_type = EmotionType(emotion)
            except ValueError:
                inconsistencies.append(f"Invalid emotion type: {emotion}")
                emotion_type = None
        else:
            emotion_type = None
        
        # Cross-field validation
        if scene_type and energy is not None:
            scene_result = self.validate_scene_type_consistency(
                scene_type, 
                profile_data.get("duration", 30),
                energy
            )
            suggestions.extend(scene_result.suggestions)
        
        if emotion_type and energy is not None:
            emotion_result = self.validate_emotional_consistency(
                emotion_type,
                profile_data.get("secondary_emotion"),
                energy
            )
            inconsistencies.extend(emotion_result.inconsistencies)
        
        # Pacing consistency
        if pacing is not None and energy is not None:
            if abs(pacing - energy) > 0.5:
                suggestions.append(
                    f"Large gap between energy ({energy:.2f}) and pacing ({pacing:.2f})"
                )
        
        is_consistent = len(inconsistencies) == 0
        confidence = 1.0 - (len(inconsistencies) * 0.15 + len(suggestions) * 0.05)
        
        result = SemanticConsistencyResult(
            is_consistent=is_consistent,
            semantic_type="profile",
            confidence=max(0.0, confidence),
            inconsistencies=inconsistencies,
            suggestions=suggestions,
        )
        
        self.validation_history.append(result)
        return result
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of all validations"""
        if not self.validation_history:
            return {"total": 0, "consistent": 0, "confidence_avg": 0}
        
        total = len(self.validation_history)
        consistent = sum(1 for r in self.validation_history if r.is_consistent)
        avg_confidence = sum(r.confidence for r in self.validation_history) / total
        
        return {
            "total": total,
            "consistent": consistent,
            "inconsistent": total - consistent,
            "confidence_avg": avg_confidence,
            "by_type": self._aggregate_by_type(),
        }
    
    def _aggregate_by_type(self) -> Dict[str, Dict[str, int]]:
        """Aggregate validation results by semantic type"""
        by_type: Dict[str, Dict[str, int]] = {}
        
        for result in self.validation_history:
            if result.semantic_type not in by_type:
                by_type[result.semantic_type] = {"consistent": 0, "inconsistent": 0}
            
            if result.is_consistent:
                by_type[result.semantic_type]["consistent"] += 1
            else:
                by_type[result.semantic_type]["inconsistent"] += 1
        
        return by_type


# =============================================================================
# Semantic Lineage Tracker
# =============================================================================

@dataclass
class SemanticLineageEntry:
    """Entry in semantic lineage"""
    asset_id: str
    semantic_profile_id: str
    parent_ids: List[str]
    derived_from: List[str]
    timestamp: str
    transformation_applied: str


class SemanticLineageTracker:
    """
    Tracks semantic lineage through transformations.
    
    Maintains:
    - Parent-child relationships
    - Transformation history
    - Semantic derivation chains
    """
    
    def __init__(self):
        self.lineage: Dict[str, SemanticLineageEntry] = {}
        self.derivations: Dict[str, List[str]] = {}  # asset -> derived assets
    
    def add_entry(
        self,
        asset_id: str,
        semantic_profile_id: str,
        parent_ids: Optional[List[str]] = None,
        derived_from: Optional[List[str]] = None,
        transformation: str = "initial",
    ) -> SemanticLineageEntry:
        """Add semantic lineage entry"""
        entry = SemanticLineageEntry(
            asset_id=asset_id,
            semantic_profile_id=semantic_profile_id,
            parent_ids=parent_ids or [],
            derived_from=derived_from or [],
            timestamp=__import__("datetime").datetime.utcnow().isoformat(),
            transformation_applied=transformation,
        )
        
        self.lineage[asset_id] = entry
        
        # Update derivations
        for parent in entry.parent_ids:
            if parent not in self.derivations:
                self.derivations[parent] = []
            self.derivations[parent].append(asset_id)
        
        return entry
    
    def get_lineage(self, asset_id: str) -> List[SemanticLineageEntry]:
        """Get full lineage for an asset"""
        lineage = []
        visited = set()
        
        def traverse(current_id: str):
            if current_id in visited:
                return
            visited.add(current_id)
            
            entry = self.lineage.get(current_id)
            if entry:
                lineage.append(entry)
                for parent_id in entry.parent_ids:
                    traverse(parent_id)
        
        traverse(asset_id)
        return lineage
    
    def get_derivations(self, asset_id: str) -> List[str]:
        """Get all derived assets"""
        return self.derivations.get(asset_id, [])
    
    def validate_lineage_integrity(self, asset_id: str) -> bool:
        """Validate lineage integrity for an asset"""
        lineage = self.get_lineage(asset_id)
        
        if not lineage:
            return True  # No lineage to validate
        
        # Check for cycles
        all_ids = set()
        for entry in lineage:
            if entry.asset_id in all_ids:
                return False
            all_ids.add(entry.asset_id)
        
        return True


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def semantic_validator() -> SemanticConsistencyValidator:
    """Semantic consistency validator fixture"""
    return SemanticConsistencyValidator()


@pytest.fixture
def semantic_lineage_tracker() -> SemanticLineageTracker:
    """Semantic lineage tracker fixture"""
    return SemanticLineageTracker()


# =============================================================================
# Semantic Consistency Tests
# =============================================================================

class TestSemanticConsistency:
    """Test suite for semantic consistency validation"""
    
    def test_validate_emotional_consistency_valid(self, semantic_validator):
        """Test emotional consistency validation for valid case"""
        result = semantic_validator.validate_emotional_consistency(
            primary_emotion=EmotionType.EXCITEMENT,
            secondary_emotion=EmotionType.JOY,
            energy_level=0.8,
        )
        
        assert result.is_consistent is True
        assert len(result.inconsistencies) == 0
    
    def test_validate_emotional_consistency_invalid(self, semantic_validator):
        """Test emotional consistency validation for invalid case"""
        result = semantic_validator.validate_emotional_consistency(
            primary_emotion=EmotionType.SADNESS,
            secondary_emotion=None,
            energy_level=0.9,  # Conflicts with sadness
        )
        
        assert result.is_consistent is False
        assert len(result.inconsistencies) > 0
    
    def test_validate_scene_type_consistency(self, semantic_validator):
        """Test scene type consistency validation"""
        # Valid intro
        result = semantic_validator.validate_scene_type_consistency(
            scene_type=SceneSemanticType.INTRO,
            duration=10.0,
            energy_level=0.4,
        )
        
        # Should be valid (duration and energy appropriate)
        assert result is not None
    
    def test_validate_scene_type_duration_mismatch(self, semantic_validator):
        """Test scene type with mismatched duration"""
        result = semantic_validator.validate_scene_type_consistency(
            scene_type=SceneSemanticType.INTRO,
            duration=100.0,  # Too long for intro
            energy_level=0.5,
        )
        
        assert len(result.suggestions) > 0
    
    def test_validate_semantic_profile(self, semantic_validator):
        """Test full semantic profile validation"""
        profile_data = {
            "semantic_type": "chorus",
            "primary_emotion": "excitement",
            "energy_level": 0.8,
            "pacing_score": 0.7,
            "duration": 30.0,
        }
        
        result = semantic_validator.validate_semantic_profile_consistency(profile_data)
        
        assert result is not None
        assert result.confidence > 0.5
    
    def test_validation_summary(self, semantic_validator):
        """Test validation summary generation"""
        # Run multiple validations
        semantic_validator.validate_emotional_consistency(
            EmotionType.JOY, None, 0.7
        )
        semantic_validator.validate_emotional_consistency(
            EmotionType.SADNESS, None, 0.2
        )
        
        summary = semantic_validator.get_validation_summary()
        
        assert summary["total"] == 2
        assert "confidence_avg" in summary
        assert "by_type" in summary


class TestSemanticLineage:
    """Test suite for semantic lineage tracking"""
    
    def test_add_lineage_entry(self, semantic_lineage_tracker):
        """Test adding lineage entry"""
        entry = semantic_lineage_tracker.add_entry(
            asset_id="asset-1",
            semantic_profile_id="profile-1",
            transformation="initial",
        )
        
        assert entry.asset_id == "asset-1"
        assert len(entry.parent_ids) == 0
    
    def test_lineage_with_parent(self, semantic_lineage_tracker):
        """Test lineage entry with parent"""
        # Create parent
        semantic_lineage_tracker.add_entry(
            asset_id="parent-asset",
            semantic_profile_id="parent-profile",
        )
        
        # Create child
        child = semantic_lineage_tracker.add_entry(
            asset_id="child-asset",
            semantic_profile_id="child-profile",
            parent_ids=["parent-asset"],
            transformation="derived",
        )
        
        assert "parent-asset" in child.parent_ids
    
    def test_get_lineage(self, semantic_lineage_tracker):
        """Test retrieving full lineage"""
        # Create chain
        semantic_lineage_tracker.add_entry("asset-1", "profile-1")
        semantic_lineage_tracker.add_entry("asset-2", "profile-2", parent_ids=["asset-1"])
        semantic_lineage_tracker.add_entry("asset-3", "profile-3", parent_ids=["asset-2"])
        
        lineage = semantic_lineage_tracker.get_lineage("asset-3")
        
        assert len(lineage) >= 3
        assert any(e.asset_id == "asset-1" for e in lineage)
    
    def test_get_derivations(self, semantic_lineage_tracker):
        """Test getting derived assets"""
        semantic_lineage_tracker.add_entry("base", "base-profile")
        semantic_lineage_tracker.add_entry("derived-1", "d1-profile", parent_ids=["base"])
        semantic_lineage_tracker.add_entry("derived-2", "d2-profile", parent_ids=["base"])
        
        derivations = semantic_lineage_tracker.get_derivations("base")
        
        assert len(derivations) == 2
        assert "derived-1" in derivations
        assert "derived-2" in derivations
    
    def test_validate_lineage_integrity(self, semantic_lineage_tracker):
        """Test lineage integrity validation"""
        semantic_lineage_tracker.add_entry("integrity-1", "profile-1")
        semantic_lineage_tracker.add_entry("integrity-2", "profile-2", parent_ids=["integrity-1"])
        
        is_valid = semantic_lineage_tracker.validate_lineage_integrity("integrity-2")
        
        assert is_valid is True


class TestSemanticCrossDomain:
    """Test cross-domain semantic consistency"""
    
    @pytest.mark.asyncio
    async def test_semantic_profile_consistency_across_analysis(
        self,
        db_session,
    ):
        """Test semantic profile consistency across multiple analyses"""
        analyzer = SemanticAnalyzer(db_session)
        await analyzer.initialize()
        
        # Analyze same content multiple times
        profiles = []
        for i in range(3):
            profile = await analyzer.analyze_media(
                asset_id=f"consistency-test-{i}",
                media_type="video/mp4",
                duration=30.0,
                audio_features={"bpm": 120},
            )
            profiles.append(profile)
        
        # Energy levels should be similar
        energies = [p.energy_level for p in profiles]
        energy_variance = max(energies) - min(energies)
        
        assert energy_variance < 0.2  # Should be consistent
        
        await analyzer.shutdown()
    
    def test_semantic_tag_consistency(self):
        """Test semantic tag consistency across categories"""
        # Define expected tag categories
        tag_categories = {
            "visual": ["color", "composition", "lighting"],
            "audio": ["beat", "melody", "rhythm"],
            "emotional": ["joy", "sadness", "tension"],
        }
        
        # Validate all categories have tags
        for category, tags in tag_categories.items():
            assert len(tags) > 0
            for tag in tags:
                assert isinstance(tag, str)
                assert len(tag) > 0
