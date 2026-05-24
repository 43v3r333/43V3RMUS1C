"""
Semantic Services - Media intelligence and understanding
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Tuple
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_

from .models import (
    EmotionType,
    SceneSemanticType,
    SemanticTag,
    MediaProfile,
    CompositionContext,
    SemanticTagging,
    TransitionRecommendation,
    MusicalStructure,
)

logger = logging.getLogger(__name__)


@dataclass
class SceneAnalysis:
    """Scene analysis result"""
    scene_id: str
    semantic_type: SceneSemanticType
    primary_emotion: EmotionType
    energy_level: float
    recommended_tags: List[str]
    pacing_score: float


@dataclass
class CompositionRecommendation:
    """Composition recommendation"""
    recommendation_type: str
    target_id: str
    description: str
    confidence: float
    priority: int = 0


class SemanticAnalyzer:
    """
    Semantic analyzer for media understanding.
    Handles scene analysis, emotional classification, and semantic tagging.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._profiles: Dict[str, MediaProfile] = {}
        self._contexts: Dict[str, CompositionContext] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize the semantic analyzer"""
        await self._load_profiles()
        self._running = True
        logger.info("SemanticAnalyzer initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the semantic analyzer"""
        self._running = False
        logger.info("SemanticAnalyzer shutdown")
    
    async def _load_profiles(self) -> None:
        """Load media profiles from database"""
        result = await self.db.execute(select(MediaProfile))
        for profile in result.scalars().all():
            self._profiles[profile.asset_id] = profile
    
    # ==================== Media Profiling ====================
    
    async def analyze_media(
        self,
        asset_id: str,
        media_type: str,
        duration: float,
        audio_features: Optional[Dict[str, Any]] = None,
        visual_features: Optional[Dict[str, Any]] = None,
    ) -> MediaProfile:
        """Analyze media and create semantic profile"""
        # Determine semantic type based on duration and features
        semantic_type = self._infer_semantic_type(duration, audio_features)
        
        # Analyze emotional content
        primary_emotion, secondary_emotion, energy_level = self._analyze_emotion(
            audio_features, visual_features
        )
        
        # Calculate pacing score
        pacing_score = self._calculate_pacing(audio_features)
        
        # Generate tags
        tags = self._generate_tags(media_type, semantic_type, primary_emotion)
        
        # Create profile
        profile = MediaProfile(
            asset_id=asset_id,
            semantic_type=semantic_type,
            primary_emotion=primary_emotion.value if primary_emotion else None,
            secondary_emotion=secondary_emotion.value if secondary_emotion else None,
            energy_level=energy_level,
            pacing_score=pacing_score,
            duration=duration,
            format=media_type,
            tags={
                "visual": [t for t in tags if self._is_visual_tag(t)],
                "audio": [t for t in tags if self._is_audio_tag(t)],
                "emotional": [t for t in tags if self._is_emotional_tag(t)],
            },
            confidence=0.85,
            analysis_method="ml_classification",
            analyzed_at=datetime.utcnow(),
        )
        
        # Include audio features if available
        if audio_features:
            if audio_features.get("bpm"):
                profile.bpm = audio_features["bpm"]
            if audio_features.get("key"):
                profile.key = audio_features["key"]
            if audio_features.get("beats"):
                profile.beats = audio_features["beats"]
        
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        
        self._profiles[asset_id] = profile
        
        return profile
    
    def _infer_semantic_type(
        self,
        duration: float,
        audio_features: Optional[Dict[str, Any]],
    ) -> str:
        """Infer semantic type from duration and features"""
        # Classification based on duration
        if duration < 15:
            return SceneSemanticType.INTRO.value
        elif duration < 30:
            if audio_features and audio_features.get("bpm", 0) > 120:
                return SceneSemanticType.BUILDUP.value
            return SceneSemanticType.INTERLUDE.value
        elif duration < 45:
            return SceneSemanticType.VERSE.value
        elif duration < 60:
            return SceneSemanticType.CHORUS.value
        else:
            return SceneSemanticType.BRIDGE.value
    
    def _analyze_emotion(
        self,
        audio_features: Optional[Dict[str, Any]],
        visual_features: Optional[Dict[str, Any]],
    ) -> Tuple[EmotionType, Optional[EmotionType], float]:
        """Analyze emotional content"""
        energy_level = 0.5
        
        if audio_features:
            bpm = audio_features.get("bpm", 120)
            # Higher BPM = more energy
            energy_level = min(bpm / 180, 1.0)
        
        # Determine primary emotion based on energy
        if energy_level > 0.7:
            primary_emotion = EmotionType.EXCITEMENT
        elif energy_level > 0.5:
            primary_emotion = EmotionType.ENERGY
        elif energy_level > 0.3:
            primary_emotion = EmotionType.CALM
        else:
            primary_emotion = EmotionType.SADNESS
        
        secondary_emotion = None
        
        return primary_emotion, secondary_emotion, energy_level
    
    def _calculate_pacing(self, audio_features: Optional[Dict[str, Any]]) -> float:
        """Calculate pacing score"""
        if not audio_features:
            return 0.5
        
        # Based on beat density and variation
        beats = audio_features.get("beats", [])
        if len(beats) < 2:
            return 0.5
        
        # Calculate beat intervals
        intervals = []
        for i in range(1, len(beats)):
            intervals.append(beats[i]["timestamp"] - beats[i-1]["timestamp"])
        
        if not intervals:
            return 0.5
        
        # Lower variance = more consistent pacing
        avg_interval = sum(intervals) / len(intervals)
        variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)
        
        # Convert to score (lower variance = higher score)
        pacing_score = max(0, 1 - (variance / (avg_interval * 2)))
        
        return pacing_score
    
    def _generate_tags(
        self,
        media_type: str,
        semantic_type: str,
        primary_emotion: EmotionType,
    ) -> List[str]:
        """Generate semantic tags"""
        tags = []
        
        # Add media type tag
        tags.append(f"type:{media_type}")
        
        # Add semantic type tag
        tags.append(f"scene:{semantic_type}")
        
        # Add emotion tag
        tags.append(f"emotion:{primary_emotion.value}")
        
        # Add pacing tag
        tags.append("pacing:steady")
        
        return tags
    
    def _is_visual_tag(self, tag: str) -> bool:
        return tag.startswith("visual:") or "color" in tag or "composition" in tag
    
    def _is_audio_tag(self, tag: str) -> bool:
        return tag.startswith("audio:") or "beat" in tag or "melody" in tag
    
    def _is_emotional_tag(self, tag: str) -> bool:
        return tag.startswith("emotion:") or tag.startswith("mood:")
    
    # ==================== Composition Context ====================
    
    async def analyze_composition(
        self,
        composition_id: str,
        composition_type: str,
        scenes: List[Dict[str, Any]],
        audio_analysis: Optional[Dict[str, Any]] = None,
    ) -> CompositionContext:
        """Analyze composition for context"""
        # Analyze emotional arc
        emotional_arc = self._analyze_emotional_arc(scenes)
        
        # Identify peak moments
        peak_moments = self._find_peak_moments(scenes)
        
        # Analyze transitions
        transitions = self._analyze_transitions(scenes)
        
        # Generate recommendations
        recommendations = await self._generate_composition_recommendations(
            scenes, emotional_arc, transitions
        )
        
        # Create context
        context = CompositionContext(
            composition_id=composition_id,
            composition_type=composition_type,
            scenes=scenes,
            transitions=transitions,
            emotional_arc=emotional_arc,
            peak_moments=peak_moments,
            bpm=audio_analysis.get("bpm") if audio_analysis else None,
            musical_sections=audio_analysis.get("sections") if audio_analysis else None,
            avg_pacing=self._calculate_avg_pacing(scenes),
            pacing_variance=self._calculate_pacing_variance(scenes),
            recommended_transitions=recommendations["transitions"],
            recommended_overlays=recommendations["overlays"],
            confidence=0.8,
            analyzed_at=datetime.utcnow(),
        )
        
        self.db.add(context)
        await self.db.commit()
        await self.db.refresh(context)
        
        self._contexts[composition_id] = context
        
        return context
    
    def _analyze_emotional_arc(
        self,
        scenes: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Analyze emotional arc across scenes"""
        arc = []
        
        cumulative_energy = 0
        for i, scene in enumerate(scenes):
            scene_energy = scene.get("energy_level", 0.5)
            cumulative_energy += scene_energy
            
            arc.append({
                "scene_index": i,
                "timestamp": scene.get("start_time", 0),
                "energy": scene_energy,
                "cumulative_energy": cumulative_energy,
                "emotion": scene.get("primary_emotion", "neutral"),
            })
        
        return arc
    
    def _find_peak_moments(self, scenes: List[Dict[str, Any]]) -> List[float]:
        """Find peak moments in composition"""
        peaks = []
        
        for scene in scenes:
            if scene.get("energy_level", 0) > 0.7:
                peaks.append(scene.get("start_time", 0))
        
        return peaks
    
    def _analyze_transitions(
        self,
        scenes: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Analyze transitions between scenes"""
        transitions = []
        
        for i in range(len(scenes) - 1):
            from_scene = scenes[i]
            to_scene = scenes[i + 1]
            
            # Calculate compatibility
            energy_diff = abs(
                from_scene.get("energy_level", 0.5) - to_scene.get("energy_level", 0.5)
            )
            
            transitions.append({
                "from_index": i,
                "to_index": i + 1,
                "energy_difference": energy_diff,
                "recommended_type": self._recommend_transition_type(
                    from_scene.get("semantic_type"),
                    to_scene.get("semantic_type"),
                    energy_diff,
                ),
            })
        
        return transitions
    
    def _recommend_transition_type(
        self,
        from_type: Optional[str],
        to_type: Optional[str],
        energy_diff: float,
    ) -> str:
        """Recommend transition type"""
        if energy_diff > 0.5:
            # High energy change = hard cut
            return "cut"
        elif energy_diff > 0.2:
            # Medium change = dissolve
            return "dissolve"
        else:
            # Low change = fade
            return "fade"
    
    async def _generate_composition_recommendations(
        self,
        scenes: List[Dict[str, Any]],
        emotional_arc: List[Dict[str, Any]],
        transitions: List[Dict[str, Any]],
    ) -> Dict[str, List[str]]:
        """Generate composition recommendations"""
        recommendations = {
            "transitions": [],
            "overlays": [],
        }
        
        # Transition recommendations
        for transition in transitions:
            if transition["energy_difference"] > 0.4:
                recommendations["transitions"].append(
                    f"Scene {transition['from_index']} -> {transition['to_index']}: use {transition['recommended_type']}"
                )
        
        # Overlay recommendations based on peak moments
        peaks = [arc for arc in emotional_arc if arc["energy"] > 0.6]
        if len(peaks) > 0:
            recommendations["overlays"].append(f"Add dynamic text at {len(peaks)} high-energy moments")
        
        return recommendations
    
    def _calculate_avg_pacing(self, scenes: List[Dict[str, Any]]) -> float:
        """Calculate average pacing"""
        if not scenes:
            return 0.5
        
        total_pacing = sum(s.get("pacing_score", 0.5) for s in scenes)
        return total_pacing / len(scenes)
    
    def _calculate_pacing_variance(self, scenes: List[Dict[str, Any]]) -> float:
        """Calculate pacing variance"""
        if len(scenes) < 2:
            return 0.0
        
        pacings = [s.get("pacing_score", 0.5) for s in scenes]
        avg = sum(pacings) / len(pacings)
        variance = sum((p - avg) ** 2 for p in pacings) / len(pacings)
        
        return variance
    
    # ==================== Musical Analysis ====================
    
    async def analyze_musical_structure(
        self,
        asset_id: str,
        bpm: float,
        beats: List[Dict[str, Any]],
        sections: Optional[List[Dict[str, Any]]] = None,
    ) -> MusicalStructure:
        """Analyze musical structure"""
        # Identify downbeats (usually first beat of each bar)
        time_signature = "4/4"  # Default
        beats_per_bar = 4
        downbeats = []
        strong_beats = []
        
        for i, beat in enumerate(beats):
            if i % beats_per_bar == 0:
                downbeats.append(beat["timestamp"])
            if i % 4 == 0:  # Every 4th beat is strong
                strong_beats.append(beat["timestamp"])
        
        # Find hook candidates (sections with high energy or distinctive features)
        hook_candidates = []
        if sections:
            for section in sections:
                if section.get("energy", 0.5) > 0.6 or section.get("is_peak", False):
                    hook_candidates.append({
                        "timestamp": section.get("start_time"),
                        "reason": section.get("reason", "High energy section"),
                    })
        
        # Create structure
        structure = MusicalStructure(
            asset_id=asset_id,
            bpm=bpm,
            time_signature=time_signature,
            beats=beats,
            downbeats=downbeats,
            sections=sections,
            hook_candidates=hook_candidates,
            strong_beat_markers=strong_beats,
            analysis_method="librosa",
            confidence=0.9,
            analyzed_at=datetime.utcnow(),
        )
        
        self.db.add(structure)
        await self.db.commit()
        await self.db.refresh(structure)
        
        return structure
    
    # ==================== Tagging ====================
    
    async def add_tag(
        self,
        target_id: str,
        target_type: str,
        tag_category: SemanticTag,
        tag_name: str,
        tag_value: Optional[str] = None,
        confidence: float = 1.0,
        is_manual: bool = False,
        created_by: Optional[UUID] = None,
    ) -> SemanticTagging:
        """Add semantic tag"""
        tagging = SemanticTagging(
            tag_id=str(uuid4()),
            asset_id=target_id if target_type == "asset" else None,
            composition_id=target_id if target_type == "composition" else None,
            tag_category=tag_category.value,
            tag_name=tag_name,
            tag_value=tag_value,
            confidence=confidence,
            is_manual=is_manual,
            source="manual" if is_manual else "auto",
            created_by=created_by,
        )
        
        self.db.add(tagging)
        await self.db.commit()
        await self.db.refresh(tagging)
        
        return tagging
    
    async def get_tags(
        self,
        target_id: str,
        target_type: str,
        category: Optional[SemanticTag] = None,
    ) -> List[SemanticTagging]:
        """Get tags for a target"""
        if target_type == "asset":
            query = select(SemanticTagging).where(SemanticTagging.asset_id == target_id)
        else:
            query = select(SemanticTagging).where(SemanticTagging.composition_id == target_id)
        
        if category:
            query = query.where(SemanticTagging.tag_category == category.value)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())


class CinematicSequencer:
    """
    Cinematic sequencer for intelligent composition.
    Handles scene ordering, beat alignment, and pacing optimization.
    """
    
    def __init__(self, db: AsyncSession, semantic_analyzer: SemanticAnalyzer):
        self.db = db
        self.semantic_analyzer = semantic_analyzer
    
    async def sequence_by_energy(
        self,
        scenes: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Sequence scenes by energy curve (low to high to low)"""
        # Sort by energy
        sorted_scenes = sorted(scenes, key=lambda s: s.get("energy_level", 0.5))
        
        # Build energy arc
        n = len(sorted_scenes)
        if n <= 3:
            # Simple linear arc
            return sorted_scenes
        
        # Build intro (low) -> build -> peak -> outro (low)
        sequenced = []
        
        # Intro: first quarter
        intro_end = n // 4
        sequenced.extend(sorted_scenes[:intro_end])
        
        # Build: second quarter
        build_end = n // 2
        sequenced.extend(sorted_scenes[intro_end:build_end])
        
        # Peak: third quarter (reversed for high energy)
        peak_end = 3 * n // 4
        peak_scenes = sorted(scenes[build_end:peak_end], key=lambda s: -s.get("energy_level", 0.5))
        sequenced.extend(peak_scenes)
        
        # Outro: last quarter (reversed for smooth landing)
        outro_scenes = sorted(scenes[peak_end:], key=lambda s: -s.get("energy_level", 0.5))
        sequenced.extend(outro_scenes)
        
        return sequenced
    
    async def sequence_by_beat(
        self,
        scenes: List[Dict[str, Any]],
        beats: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Sequence scenes aligned to beats"""
        # Align scene transitions to downbeats
        downbeats = [b for b in beats if b.get("is_downbeat", False)]
        
        if not downbeats:
            return scenes
        
        sequenced = []
        scene_idx = 0
        
        for downbeat in downbeats:
            if scene_idx >= len(scenes):
                break
            
            # Start new scene at this downbeat
            scene = scenes[scene_idx].copy()
            scene["start_time"] = downbeat["timestamp"]
            
            # Calculate end time based on duration
            duration = scene.get("duration", 8.0)
            scene["end_time"] = scene["start_time"] + duration
            
            sequenced.append(scene)
            scene_idx += 1
        
        # Add remaining scenes
        while scene_idx < len(scenes):
            scene = scenes[scene_idx].copy()
            scene["start_time"] = sequenced[-1]["end_time"] if sequenced else 0
            scene["end_time"] = scene["start_time"] + scene.get("duration", 8.0)
            sequenced.append(scene)
            scene_idx += 1
        
        return sequenced
    
    async def optimize_pacing(
        self,
        scenes: List[Dict[str, Any]],
        target_pacing: float,
    ) -> List[Dict[str, Any]]:
        """Optimize scene pacing"""
        optimized = []
        
        for scene in scenes:
            optimized_scene = scene.copy()
            
            # Adjust duration to match target pacing
            current_pacing = scene.get("pacing_score", 0.5)
            
            if current_pacing < target_pacing:
                # Increase pace (shorter duration)
                duration = scene.get("duration", 8.0)
                new_duration = duration * (current_pacing / target_pacing)
                optimized_scene["duration"] = max(2.0, new_duration)  # Min 2 seconds
            elif current_pacing > target_pacing:
                # Decrease pace (longer duration)
                duration = scene.get("duration", 8.0)
                new_duration = duration * (current_pacing / target_pacing)
                optimized_scene["duration"] = min(30.0, new_duration)  # Max 30 seconds
            
            optimized.append(optimized_scene)
        
        return optimized