"""
Audio Domain Models - Audio analysis and waveform data
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from enum import Enum

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, JSON, LargeBinary
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class WaveformData(BaseModel):
    """Audio waveform data model"""
    __tablename__ = "waveform_data"
    
    media_asset_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("media_assets.id"), 
        nullable=False,
        unique=True,
        index=True
    )
    media_asset: Mapped["MediaAsset"] = relationship(
        "MediaAsset", 
        back_populates="waveform", 
        foreign_keys=[media_asset_id]
    )
    
    # Waveform data
    samples_per_pixel: Mapped[int] = mapped_column(Integer, default=512)
    sample_rate: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    num_channels: Mapped[int] = mapped_column(Integer, default=1)
    
    # Stored as JSON array of peak values
    peaks: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    peaks_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    
    # Pre-computed display data
    display_width: Mapped[int] = mapped_column(Integer, default=1000)
    
    # Analysis metadata
    peak_amplitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rms_level: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class AudioAnalysis(BaseModel):
    """Audio analysis results model"""
    __tablename__ = "audio_analyses"
    
    media_asset_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("media_assets.id"), 
        nullable=False,
        unique=True,
        index=True
    )
    
    # BPM and rhythm analysis
    bpm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bpm_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    time_signature: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Beat markers (stored as list of timestamps in seconds)
    beat_markers: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    downbeat_markers: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    
    # Transient detection
    transient_markers: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    onset_strength: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    
    # Spectral analysis
    spectral_centroid: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    spectral_rolloff: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    spectral_flux: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Silence detection
    silence_regions: Mapped[Optional[List[Dict[str, float]]]] = mapped_column(JSON, nullable=True)
    
    # Musical features
    key_signature: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    key_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Hook analysis foundations
    hook_candidates: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    chorus_regions: Mapped[Optional[List[Dict[str, float]]]] = mapped_column(JSON, nullable=True)
    
    # Overall characteristics
    dynamic_range: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    loudness: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Raw features for advanced processing
    features_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    analysis_version: Mapped[str] = mapped_column(String(20), default="1.0")


@dataclass
class BeatMarker:
    """Beat marker data structure"""
    timestamp: float
    beat_number: int
    beat_strength: float
    is_downbeat: bool = False


@dataclass
class Segment:
    """Audio segment data structure"""
    start_time: float
    end_time: float
    segment_type: str  # "silence", "transient", "hook", "chorus", etc.
    confidence: float = 1.0
    labels: List[str] = field(default_factory=list)


@dataclass
class HookCandidate:
    """Hook candidate for potential hooks"""
    start_time: float
    end_time: float
    score: float
    characteristics: Dict[str, Any] = field(default_factory=dict)


from dataclasses import dataclass, field
from typing import List as TypingList