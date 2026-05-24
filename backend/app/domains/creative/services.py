"""
Creative Intelligence Services - Narrative sequencing, emotion mapping, and creative profiling.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from .models import (
    AudienceEngagementHeuristic,
    AudienceSegment,
    CreativeProfile,
    EmotionMapping,
    NarrativeSequence,
    NarrativeStructure,
    EmotionalArc,
    PacingHeuristic,
    PacingProfile,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data transfer types
# ---------------------------------------------------------------------------

@dataclass
class NarrativeArc:
    sequence_id: str
    beats: List[Dict[str, Any]]
    structure: str
    emotional_arc: str
    estimated_duration: float
    creative_score: float


@dataclass
class SequenceRecommendation:
    sequence_id: str
    sequence_name: str
    confidence: float
    alignment_score: float
    reason: str
    matched_assets: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Creative intelligence service
# ---------------------------------------------------------------------------

class CreativeIntelligenceService:
    """Orchestrates narrative and creative decisions across compositions.

    Wraps the cinematic sequencer, emotion mapper and audience heuristic
    engines into a single facade for the AI runtime layer.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # ---- Creative profiles -----------------------------------------------

    def create_profile(
        self,
        *,
        name: str,
        campaign_id: Optional[str] = None,
        artist_id: Optional[str] = None,
        narrative_structure: NarrativeStructure = NarrativeStructure.LINEAR,
        emotional_arc: EmotionalArc = EmotionalArc.STEADY,
        pacing_profile: PacingProfile = PacingProfile.BRUISER,
        visual_keywords: Optional[List[str]] = None,
        audio_keywords: Optional[List[str]] = None,
        target_segments: Optional[List[str]] = None,
        owner_id: Optional[UUID] = None,
    ) -> CreativeProfile:
        profile = CreativeProfile(
            campaign_id=campaign_id,
            artist_id=artist_id,
            name=name,
            narrative_structure=narrative_structure.value,
            emotional_arc=emotional_arc.value,
            pacing_profile=pacing_profile.value,
            visual_keywords=list(visual_keywords or []),
            audio_keywords=list(audio_keywords or []),
            target_segments=list(target_segments or []),
            owner_id=owner_id,
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def get_active_profile(
        self,
        *,
        campaign_id: Optional[str] = None,
        artist_id: Optional[str] = None,
    ) -> Optional[CreativeProfile]:
        query = self.db.query(CreativeProfile).filter(CreativeProfile.is_active.is_(True))
        if campaign_id:
            query = query.filter(CreativeProfile.campaign_id == campaign_id)
        elif artist_id:
            query = query.filter(CreativeProfile.artist_id == artist_id)
        return query.order_by(CreativeProfile.created_at.desc()).first()

    def list_profiles(
        self,
        *,
        campaign_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[CreativeProfile]:
        query = self.db.query(CreativeProfile)
        if campaign_id:
            query = query.filter(CreativeProfile.campaign_id == campaign_id)
        return query.order_by(CreativeProfile.created_at.desc()).limit(limit).all()

    # ---- Narrative sequences --------------------------------------------

    def create_sequence(
        self,
        *,
        name: str,
        profile_id: Optional[UUID] = None,
        campaign_id: Optional[str] = None,
        structure: NarrativeStructure = NarrativeStructure.LINEAR,
        emotional_arc: EmotionalArc = EmotionalArc.STEADY,
        beats: List[Dict[str, Any]],
        target_duration: float,
        target_bpm: Optional[float] = None,
        target_key: Optional[str] = None,
        owner_id: Optional[UUID] = None,
    ) -> NarrativeSequence:
        seq = NarrativeSequence(
            profile_id=profile_id,
            campaign_id=campaign_id,
            name=name,
            structure=structure.value,
            emotional_arc=emotional_arc.value,
            beats=list(beats),
            beat_count=len(beats),
            target_duration=target_duration,
            target_bpm=target_bpm,
            target_key=target_key,
            owner_id=owner_id,
        )
        self.db.add(seq)
        self.db.commit()
        self.db.refresh(seq)
        return seq

    def build_narrative_arc(
        self,
        *,
        profile_id: Optional[UUID] = None,
        campaign_id: Optional[str] = None,
        asset_count: int,
        style_hint: Optional[str] = None,
    ) -> NarrativeArc:
        """Build a narrative arc automatically from a profile and asset count."""
        profile = None
        if profile_id:
            profile = self.db.get(CreativeProfile, profile_id)
        elif campaign_id:
            profile = self.get_active_profile(campaign_id=campaign_id)

        structure = NarrativeStructure(profile.structure if profile else NarrativeStructure.LINEAR.value)
        emotional_arc = EmotionalArc(profile.emotional_arc if profile else EmotionalArc.STEADY.value)

        # Generate beats based on structure
        beats = self._generate_beats(
            structure=structure,
            emotional_arc=emotional_arc,
            count=asset_count,
            style_hint=style_hint,
        )

        total_duration = sum(b.get("duration", 5.0) for b in beats)

        seq = self.create_sequence(
            name=f"arc_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            profile_id=profile_id,
            campaign_id=campaign_id,
            structure=structure,
            emotional_arc=emotional_arc,
            beats=beats,
            target_duration=total_duration,
            owner_id=profile.owner_id if profile else None,
        )

        return NarrativeArc(
            sequence_id=str(seq.id),
            beats=beats,
            structure=structure.value,
            emotional_arc=emotional_arc.value,
            estimated_duration=total_duration,
            creative_score=seq.creative_score,
        )

    def _generate_beats(
        self,
        *,
        structure: NarrativeStructure,
        emotional_arc: EmotionalArc,
        count: int,
        style_hint: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Generate a sequence of beats given the structure and arc."""
        beats: List[Dict[str, Any]] = []

        if structure == NarrativeStructure.LINEAR:
            positions = [(i + 1) / max(count, 1) for i in range(count)]
        elif structure == NarrativeStructure.THREE_ACT:
            act_size = max(count // 3, 1)
            positions = []
            for act in range(3):
                act_count = act_size + (1 if act < (count % 3) else 0)
                for i in range(act_count):
                    positions.append((act + 1) / 3 + (i / act_count) * (1 / 3))
        elif structure == NarrativeStructure.MONTAGE:
            positions = [(i + 1) / max(count, 1) for i in range(count)]
        else:
            positions = [(i + 1) / max(count, 1) for i in range(count)]

        for i, pos in enumerate(positions[:count]):
            beats.append({
                "beat_id": f"beat_{i}",
                "position": round(pos, 3),
                "duration": 4.0 + (2.0 if i % 2 == 0 else 1.5),
                "energy": min(1.0, pos + 0.1 * (i % 3)),
                "tempo_factor": 0.9 + 0.2 * (pos % 1),
                "style_hint": style_hint or "default",
                "type": self._beat_type(pos, count),
            })
        return beats

    def _beat_type(self, position: float, total: int) -> str:
        if position < 0.1:
            return "intro"
        elif position > 0.9:
            return "outro"
        elif 0.3 <= position <= 0.5:
            return "chorus"
        elif 0.15 <= position < 0.3:
            return "verse"
        else:
            return "interlude"

    def list_sequences(
        self,
        *,
        campaign_id: Optional[str] = None,
        profile_id: Optional[UUID] = None,
        limit: int = 20,
    ) -> List[NarrativeSequence]:
        query = self.db.query(NarrativeSequence)
        if campaign_id:
            query = query.filter(NarrativeSequence.campaign_id == campaign_id)
        if profile_id:
            query = query.filter(NarrativeSequence.profile_id == profile_id)
        return query.order_by(NarrativeSequence.created_at.desc()).limit(limit).all()

    # ---- Emotion mappings -----------------------------------------------

    def create_emotion_mapping(
        self,
        *,
        source_type: str,
        source_value: str,
        target_type: str,
        target_value: str,
        strength: float = 0.5,
        profile_id: Optional[UUID] = None,
        owner_id: Optional[UUID] = None,
    ) -> EmotionMapping:
        mapping = EmotionMapping(
            source_type=source_type,
            source_value=source_value,
            target_type=target_type,
            target_value=target_value,
            strength=strength,
            profile_id=profile_id,
            owner_id=owner_id,
        )
        self.db.add(mapping)
        self.db.commit()
        self.db.refresh(mapping)
        return mapping

    def get_emotion_mapping(
        self,
        *,
        source_type: str,
        source_value: str,
    ) -> List[EmotionMapping]:
        return (
            self.db.query(EmotionMapping)
            .filter(
                EmotionMapping.source_type == source_type,
                EmotionMapping.source_value == source_value,
                EmotionMapping.is_active.is_(True),
            )
            .all()
        )

    def resolve_visual_style(
        self,
        *,
        audio_energy: float,
        bpm: float,
        key: Optional[str] = None,
        profile_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Map audio features to visual style parameters."""
        mappings = []
        if profile_id:
            mappings = (
                self.db.query(EmotionMapping)
                .filter(
                    EmotionMapping.profile_id == profile_id,
                    EmotionMapping.is_active.is_(True),
                )
                .all()
            )

        if not mappings:
            # Built-in defaults
            if audio_energy < 0.3:
                color_grade = "dark_cinematic"
                motion_intensity = 0.3
            elif audio_energy < 0.7:
                color_grade = "vibrant"
                motion_intensity = 0.6
            else:
                color_grade = "high_energy"
                motion_intensity = 0.9

            return {
                "color_grade": color_grade,
                "motion_intensity": motion_intensity,
                "transition_style": "dissolve" if audio_energy < 0.5 else "cut",
                "overlay_intensity": audio_energy,
            }

        # Apply mapped rules
        result = {"color_grade": "neutral", "motion_intensity": 0.5}
        for m in mappings:
            if m.source_type == "audio_energy":
                if m.trigger_threshold is None or audio_energy >= m.trigger_threshold:
                    if m.target_type == "color_grade":
                        result["color_grade"] = m.target_value
                    elif m.target_type == "motion_intensity":
                        result["motion_intensity"] = m.strength

        return result


# ---------------------------------------------------------------------------
# Cinematic sequencer service
# ---------------------------------------------------------------------------

class CinematicSequencerService:
    """Sequences media assets into a coherent cinematic arc."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def recommend_sequence(
        self,
        *,
        campaign_id: Optional[str] = None,
        audience_segment: Optional[AudienceSegment] = None,
        target_duration: float,
        available_assets: List[Dict[str, Any]],
    ) -> SequenceRecommendation:
        """Score and order available assets into a recommended narrative sequence."""
        if not available_assets:
            return SequenceRecommendation(
                sequence_id="",
                sequence_name="empty",
                confidence=0.0,
                alignment_score=0.0,
                reason="no assets available",
            )

        # Heuristic: sort by duration fit and emotional alignment
        scored = []
        for asset in available_assets:
            score = 0.5
            duration = float(asset.get("duration", 0))
            # Prefer assets that fit into target segments
            if 0 < duration <= target_duration / max(len(available_assets), 1) * 2:
                score += 0.3
            # Prefer assets with strong tags
            if asset.get("tags"):
                score += 0.1
            scored.append((score, asset))

        scored.sort(key=lambda x: x[0], reverse=True)
        sorted_ids = [a["id"] for _, a in scored]

        total_duration = sum(float(a.get("duration", 5)) for _, a in scored)

        return SequenceRecommendation(
            sequence_id=f"rec_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            sequence_name=f"auto_seq_{campaign_id or 'general'}",
            confidence=0.75,
            alignment_score=1.0 - abs(total_duration - target_duration) / max(target_duration, 1),
            reason="auto-sequenced by energy and duration fit",
            matched_assets=sorted_ids,
        )

    def score_narrative_alignment(
        self,
        *,
        sequence: List[Dict[str, Any]],
        profile_id: Optional[UUID] = None,
        campaign_id: Optional[str] = None,
    ) -> float:
        """Score how well a sequence aligns with its profile's narrative arc."""
        if not sequence:
            return 0.0

        profile = None
        if profile_id:
            profile = self.db.get(CreativeProfile, profile_id)
        elif campaign_id:
            profile = (
                self.db.query(CreativeProfile)
                .filter(
                    CreativeProfile.campaign_id == campaign_id,
                    CreativeProfile.is_active.is_(True),
                )
                .first()
            )

        if profile is None:
            return 0.5  # neutral baseline

        # Score based on energy curve alignment
        arc_type = EmotionalArc(profile.emotional_arc)
        pacing_type = PacingProfile(profile.pacing_profile)

        energies = [float(s.get("energy", 0.5)) for s in sequence]

        # Calculate variance from expected arc
        if arc_type == EmotionalArc.RICHES_TO_RAGS:
            expected = [1.0 - (i / max(len(sequence) - 1, 1)) for i in range(len(sequence))]
        elif arc_type == EmotionalArc.RAGS_TO_RICHES:
            expected = [(i / max(len(sequence) - 1, 1)) for i in range(len(sequence))]
        elif arc_type == EmotionalArc.MAN_IN_HOLE:
            mid = len(sequence) // 2
            expected = [
                (i / mid) if i <= mid else (len(sequence) - 1 - i) / (len(sequence) - 1 - mid)
                for i in range(len(sequence))
            ]
        else:
            expected = [0.5] * len(sequence)

        if len(expected) != len(energies):
            return 0.5

        variance = sum(abs(energies[i] - expected[i]) for i in range(len(energies))) / len(energies)
        score = max(0.0, 1.0 - variance)

        return round(score, 3)


# ---------------------------------------------------------------------------
# Creative profile service (additional helpers)
# ---------------------------------------------------------------------------

class CreativeProfileService:
    """High-level helpers for creative profile management."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_pacing_heuristic(
        self,
        *,
        composition_class: str,
        genre: Optional[str] = None,
        campaign_type: Optional[str] = None,
    ) -> Optional[PacingHeuristic]:
        query = self.db.query(PacingHeuristic).filter(PacingHeuristic.is_active.is_(True))
        if genre:
            query = query.filter(
                or_(
                    PacingHeuristic.genre == genre,
                    PacingHeuristic.genre.is_(None),
                )
            )
        if campaign_type:
            query = query.filter(
                or_(
                    PacingHeuristic.campaign_type == campaign_type,
                    PacingHeuristic.campaign_type.is_(None),
                )
            )
        query = query.filter(PacingHeuristic.composition_class == composition_class)
        return query.order_by(PacingHeuristic.hit_count.desc()).first()

    def get_audience_heuristic(
        self,
        *,
        audience_segment: AudienceSegment,
        content_type: str,
    ) -> Optional[AudienceEngagementHeuristic]:
        return (
            self.db.query(AudienceEngagementHeuristic)
            .filter(
                AudienceEngagementHeuristic.audience_segment == audience_segment.value,
                AudienceEngagementHeuristic.content_type == content_type,
                AudienceEngagementHeuristic.is_active.is_(True),
            )
            .first()
        )

    def predict_engagement(
        self,
        *,
        audience_segment: AudienceSegment,
        content_duration: float,
        content_type: str = "short_form",
    ) -> Dict[str, Any]:
        heuristic = self.get_audience_heuristic(
            audience_segment=audience_segment,
            content_type=content_type,
        )
        if heuristic is None:
            return {
                "expected_completion_rate": 0.5,
                "expected_engagement_score": 0.5,
                "first_drop_seconds": 5.0,
                "confidence": 0.3,
            }

        # Simple linear model based on retention curve
        retention_curve = heuristic.retention_curve
        if retention_curve and len(retention_curve) > 0:
            # Find retention at content_duration
            t = 0.0
            retention = 1.0
            for point in sorted(retention_curve, key=lambda p: p.get("t", 0)):
                if point.get("t", 0) >= content_duration:
                    retention = point.get("retention", 0.5)
                    break
        else:
            retention = heuristic.expected_completion_rate

        return {
            "expected_completion_rate": heuristic.expected_completion_rate * (retention / 0.5),
            "expected_engagement_score": heuristic.expected_engagement_score,
            "first_drop_seconds": heuristic.first_drop_seconds,
            "critical_drop_seconds": heuristic.critical_drop_seconds,
            "confidence": heuristic.observed_completion_rate or 0.5,
        }


__all__ = [
    "CreativeIntelligenceService",
    "CinematicSequencerService",
    "CreativeProfileService",
    "NarrativeArc",
    "SequenceRecommendation",
]