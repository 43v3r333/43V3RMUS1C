"""
Semantic Domain Models - Media intelligence and understanding
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum
from dataclasses import dataclass, field

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class EmotionType(str, Enum):
    """Emotion types for media"""
    JOY = "joy"
    SADNESS = "sadness"
    TENSION = "tension"
    EXCITEMENT = "excitement"
    CALM = "calm"
    ENERGY = "energy"
    MYSTERY = "mystery"
    NOSTALGIA = "nostalgia"


class SceneSemanticType(str, Enum):
    """Scene semantic types"""
    INTRO = "intro"
    VERSE = "verse"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    OUTRO = "outro"
    BUILDUP = "buildup"
    DROPDOWN = "dropdown"
    INTERLUDE = "interlude"


class SemanticTag(str, Enum):
    """Semantic tag categories"""
    VISUAL = "visual"
    AUDIO = "audio"
    EMOTIONAL = "emotional"
    STRUCTURAL = "structural"
    TEMPORAL = "temporal"
    QUALITY = "quality"


@dataclass
class BeatInfo:
    """Beat information"""
    timestamp: float
    strength: float
    beat_type: str


@dataclass
class SemanticAnalysis:
    """Semantic analysis result"""
    primary_emotion: EmotionType
    secondary_emotion: Optional[EmotionType]
    energy_level: float
    pacing_score: float
    tags: List[str]


class MediaProfile(BaseModel):
    """Media profile model - semantic understanding of media"""
    __tablename__ = "semantic_media_profiles"
    
    asset_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Semantic classification
    semantic_type: Mapped[str] = mapped_column(String(50), nullable=True, index=True)
    
    # Emotional analysis
    primary_emotion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    secondary_emotion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    energy_level: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pacing_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Musical analysis (if applicable)
    bpm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    key: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    time_signature: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Structural analysis
    beats: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    segments: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Content tags
    visual_tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    audio_tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    emotional_tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    structural_tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Quality metrics
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    clarity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Metadata
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    format: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Confidence
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Analysis
    analysis_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    analyzed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class CompositionContext(BaseModel):
    """Composition context model - cinematic composition understanding"""
    __tablename__ = "composition_contexts"
    
    composition_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    composition_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Scene analysis
    scenes: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    transitions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Emotional arc
    emotional_arc: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    peak_moments: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    
    # Musical structure
    bpm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    musical_sections: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Pacing analysis
    avg_pacing: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pacing_variance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Recommendations
    recommended_transitions: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    recommended_overlays: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Analysis
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    analyzed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class SemanticTagging(BaseModel):
    """Semantic tagging model - manual and automatic tags"""
    __tablename__ = "semantic_tagging"
    
    tag_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Target
    asset_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    composition_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Tag info
    tag_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    tag_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tag_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Confidence (for auto-tags)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    is_manual: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Source
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Timing
    timestamp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Owner
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class TransitionRecommendation(BaseModel):
    """Transition recommendation model - intelligent transition suggestions"""
    __tablename__ = "transition_recommendations"
    
    recommendation_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Context
    from_scene_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    to_scene_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Recommendation
    transition_type: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Reasoning
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    emotional_fit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pacing_fit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Configuration
    suggested_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    suggested_parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class MusicalStructure(BaseModel):
    """Musical structure model - beat and section detection"""
    __tablename__ = "musical_structures"
    
    asset_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    # Basic musical info
    bpm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    key: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    time_signature: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Beat data
    beats: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    downbeats: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    
    # Section detection
    sections: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Hook points
    hook_candidates: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    strong_beat_markers: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    
    # Silence/pause detection
    silence_regions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    
    # Analysis
    analysis_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    analyzed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)