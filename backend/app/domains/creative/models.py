"""
Creative Intelligence Models - Cinematic cognition, narrative sequencing, and audience engagement.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from ...models.base import BaseModel


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class NarrativeStructure(str, Enum):
    LINEAR = "linear"
    BRANCHING = "branching"
    LOOPING = "looping"
    HEROES_JOURNEY = "hero_journey"
    THREE_ACT = "three_act"
    FIVE_ACT = "five_act"
    MONTAGE = "montage"
    MASHUP = "mashup"


class EmotionalArc(str, Enum):
    RAGS_TO_RICHES = "rags_to_riches"
    RICHES_TO_RAGS = "riches_to_rags"
    MAN_IN_HOLE = "man_in_hole"
    BOY_MEETS_GIRL = "boy_meets_girl"
    CINDERELLA = "cinderella"
    TRAGEDY = "tragedy"
    OVERCOMING_THE_MONSTER = "overcoming_the_monster"
    COMEDY = "comedy"
    REBIRTH = "rebirth"
    QUEST = "quest"
    STEADY = "steady"


class PacingProfile(str, Enum):
    BRUISER = "bruiser"          # sustained energy throughout
    ROLLERCOASTER = "rollercoaster"
    BUILDING = "building"        # slow-burn tension
    FRAGMENTED = "fragmented"   # rapid cuts / high contrast
    MINIMALIST = "minimalist"    # sparse, atmospheric
    MAXIMALIST = "maximalist"    # everything at once


class AudienceSegment(str, Enum):
    GEN_Z = "gen_z"
    MILLENNIAL = "millennial"
    GEN_X = "gen_x"
    BOOMER = "boomer"
    MUSIC_SUPERFAN = "music_superfan"
    CASUAL_LISTENER = "casual_listener"
    VIDEOCAST_FAN = "videocast_fan"
    TIKTOK_NATIVE = "tiktok_native"
    YOUTUBE_REGULAR = "youtube_regular"


# ---------------------------------------------------------------------------
# Creative Profile - per-campaign/artist style guide
# ---------------------------------------------------------------------------

class CreativeProfile(BaseModel):
    """Per-campaign / artist creative brief and style guide."""

    __tablename__ = "creative_profiles"
    __table_args__ = (
        Index("ix_creative_profile_campaign", "campaign_id"),
        Index("ix_creative_profile_artist", "artist_id"),
    )

    campaign_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    artist_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    narrative_structure: Mapped[str] = mapped_column(
        String(32), nullable=False, default=NarrativeStructure.LINEAR.value
    )
    emotional_arc: Mapped[str] = mapped_column(
        String(32), nullable=False, default=EmotionalArc.STEADY.value
    )
    pacing_profile: Mapped[str] = mapped_column(
        String(32), nullable=False, default=PacingProfile.BRUISER.value
    )

    # Style parameters
    visual_keywords: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    audio_keywords: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    color_palette: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    motion_style: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tone_keywords: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    # Target audience
    target_segments: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    attention_span_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=45.0)
    drop_off_point_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Validation / effectiveness
    completion_rate_target: Mapped[float] = mapped_column(Float, nullable=False, default=0.6)
    engagement_rate_target: Mapped[float] = mapped_column(Float, nullable=False, default=0.15)

    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


# ---------------------------------------------------------------------------
# Narrative Sequence - planned scene/story arc
# ---------------------------------------------------------------------------

class NarrativeSequence(BaseModel):
    """A structured narrative plan for a composition.

    Models a scene/story arc as an ordered sequence of beats. The orchestrator
    uses this to arrange media assets in a meaningful temporal order.
    """

    __tablename__ = "narrative_sequences"
    __table_args__ = (
        Index("ix_narr_seq_campaign", "campaign_id"),
        Index("ix_narr_seq_profile", "profile_id"),
    )

    profile_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("creative_profiles.id"), nullable=True
    )
    campaign_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    structure: Mapped[str] = mapped_column(
        String(32), nullable=False, default=NarrativeStructure.LINEAR.value
    )
    emotional_arc: Mapped[str] = mapped_column(
        String(32), nullable=False, default=EmotionalArc.STEADY.value
    )

    beats: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    beat_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    target_duration: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    target_bpm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    target_key: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    creative_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


# ---------------------------------------------------------------------------
# Emotion Mapping - audio mood ↔ visual mood bridges
# ---------------------------------------------------------------------------

class EmotionMapping(BaseModel):
    """Maps audio/emotional features to visual style parameters.

    These mappings let the render engine pick visual treatments that match
    the musical energy at each moment in the composition.
    """

    __tablename__ = "emotion_mappings"
    __table_args__ = (
        Index("ix_emotion_map_source", "source_type", "source_value"),
        Index("ix_emotion_map_target", "target_type", "target_value"),
    )

    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_value: Mapped[str] = mapped_column(String(100), nullable=False)

    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_value: Mapped[str] = mapped_column(String(100), nullable=False)

    strength: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    trigger_threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fade_duration: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    profile_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


# ---------------------------------------------------------------------------
# Pacing Heuristic - tempo/energy curves per composition class
# ---------------------------------------------------------------------------

class PacingHeuristic(BaseModel):
    """Tempo/energy curve definition for a composition class."""

    __tablename__ = "pacing_heuristics"
    __table_args__ = (
        Index("ix_pacing_heuristic_composition", "composition_class"),
        Index("ix_pacing_heuristic_genre", "genre"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    composition_class: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    genre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    campaign_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Energy curve defined as a sequence of breakpoints
    energy_curve: Mapped[List[Dict[str, float]]] = mapped_column(JSON, nullable=False, default=list)
    tempo_curve: Mapped[List[Dict[str, float]]] = mapped_column(JSON, nullable=False, default=list)

    # Baseline parameters
    target_bpm: Mapped[float] = mapped_column(Float, nullable=False, default=120.0)
    avg_energy_level: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Performance stats
    hit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)


# ---------------------------------------------------------------------------
# Audience Engagement Heuristic - retention signal predictions
# ---------------------------------------------------------------------------

class AudienceEngagementHeuristic(BaseModel):
    """Predicted retention/engagement signals for audience segments."""

    __tablename__ = "audience_engagement_heuristics"
    __table_args__ = (
        Index("ix_audience_heuristic_segment", "audience_segment"),
        Index("ix_audience_heuristic_content", "content_type"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    audience_segment: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Engagement curve - expected retention at each second
    retention_curve: Mapped[List[Dict[str, float]]] = mapped_column(JSON, nullable=False, default=list)
    expected_completion_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    expected_engagement_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Drop-off predictors
    first_drop_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=5.0)
    critical_drop_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Platform-specific weights
    platform_weights: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)

    # Performance
    hit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    observed_completion_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    observed_engagement_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


__all__ = [
    "NarrativeStructure",
    "EmotionalArc",
    "PacingProfile",
    "AudienceSegment",
    "CreativeProfile",
    "NarrativeSequence",
    "EmotionMapping",
    "PacingHeuristic",
    "AudienceEngagementHeuristic",
]