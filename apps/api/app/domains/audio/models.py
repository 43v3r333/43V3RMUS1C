"""
Audio Domain Models
"""
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, Session

from app.models.base import BaseModel


class WaveformData(BaseModel):
    """
    Waveform visualization data.
    Stores pre-computed peaks for real-time display.
    """
    __tablename__ = "waveform_data"
    
    asset_id = Column(PGUUID(as_uuid=True), ForeignKey("media_assets.id"), nullable=False, unique=True)
    
    # Waveform configuration
    sample_rate = Column(Integer, nullable=False)
    samples_per_second = Column(Integer, default=100)
    channel_mode = Column(String(20), default="stereo")
    
    # Peak data
    peaks_left = Column(JSON, nullable=True)
    peaks_right = Column(JSON, nullable=True)
    peaks_mono = Column(JSON, nullable=True)
    
    # Statistics
    duration = Column(Float, nullable=True)
    peak_amplitude = Column(Float, nullable=True)
    rms_level = Column(Float, nullable=True)
    
    processing_version = Column(String(20), default="1.0")
    
    asset = relationship("MediaAsset")
    
    def __repr__(self) -> str:
        return f"<WaveformData(asset_id={self.asset_id})>"


class AudioAnalysis(BaseModel):
    """
    Audio analysis results for music intelligence.
    Stores BPM, key, beats, energy, and other audio features.
    """
    __tablename__ = "audio_analysis"
    
    asset_id = Column(PGUUID(as_uuid=True), ForeignKey("media_assets.id"), nullable=False, unique=True)
    
    # Tempo
    bpm = Column(Float, nullable=True, index=True)
    bpm_confidence = Column(Float, nullable=True)
    
    # Beats
    beats = Column(JSON, nullable=True)  # List of beat timestamps
    beat_confidence = Column(Float, nullable=True)
    
    # Key
    key = Column(String(10), nullable=True, index=True)
    key_confidence = Column(Float, nullable=True)
    
    # Energy/mood
    energy = Column(Float, nullable=True)  # 0.0 to 1.0
    valence = Column(Float, nullable=True)  # Positive/negative
    danceability = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Time markers
    intro_start = Column(Float, nullable=True)
    intro_end = Column(Float, nullable=True)
    hook_start = Column(Float, nullable=True)
    hook_end = Column(Float, nullable=True)
    outro_start = Column(Float, nullable=True)
    outro_end = Column(Float, nullable=True)
    
    # Silence detection
    silent_regions = Column(JSON, nullable=True)  # List of (start, end) tuples
    
    # Spectral features
    spectral_centroid = Column(Float, nullable=True)
    spectral_rolloff = Column(Float, nullable=True)
    spectral_bandwidth = Column(Float, nullable=True)
    
    # Transient detection
    transients = Column(JSON, nullable=True)  # Transient onset times
    
    # Loudness
    loudness = Column(Float, nullable=True)  # LUFS
    dynamic_range = Column(Float, nullable=True)
    
    # Chroma
    chroma = Column(JSON, nullable=True)  # Chromagram features
    
    # Analysis metadata
    analysis_version = Column(String(20), default="1.0")
    confidence_score = Column(Float, nullable=True)
    
    asset = relationship("MediaAsset")
    
    def __repr__(self) -> str:
        return f"<AudioAnalysis(asset_id={self.asset_id}, bpm={self.bpm})>"
    
    def to_features_dict(self) -> dict:
        """Convert to features dictionary for ML models"""
        return {
            "bpm": self.bpm,
            "key": self.key,
            "energy": self.energy,
            "valence": self.valence,
            "danceability": self.danceability,
            "loudness": self.loudness,
            "spectral_centroid": self.spectral_centroid,
        }


class AudioSegment(BaseModel):
    """
    Audio segment for structured editing.
    Represents sections like intro, verse, chorus, hook, outro.
    """
    __tablename__ = "audio_segments"
    
    asset_id = Column(PGUUID(as_uuid=True), ForeignKey("media_assets.id"), nullable=False)
    
    # Segment timing
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    
    # Classification
    segment_type = Column(String(50), nullable=False)  # intro, verse, chorus, hook, bridge, outro
    label = Column(String(255), nullable=True)
    confidence = Column(Float, nullable=True)
    
    # Features
    features = Column(JSON, nullable=True)  # Segment-specific features
    
    # Editing
    is_edited = Column(String(20), default="original")
    source_region = Column(JSON, nullable=True)  # Original region if edited
    
    # Metadata
    notes = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<AudioSegment(id={self.id}, type={self.segment_type}, {self.start_time}-{self.end_time})>"


class AudioAnalysisRepository:
    """Repository for audio analysis data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_asset_id(self, asset_id: UUID) -> Optional[AudioAnalysis]:
        return self.db.query(AudioAnalysis).filter(AudioAnalysis.asset_id == asset_id).first()
    
    def get_waveform_by_asset_id(self, asset_id: UUID) -> Optional[WaveformData]:
        return self.db.query(WaveformData).filter(WaveformData.asset_id == asset_id).first()
    
    def get_segments_by_asset(self, asset_id: UUID) -> List[AudioSegment]:
        return (
            self.db.query(AudioSegment)
            .filter(AudioSegment.asset_id == asset_id)
            .order_by(AudioSegment.start_time)
            .all()
        )
    
    def create_analysis(self, analysis: AudioAnalysis) -> AudioAnalysis:
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis
    
    def create_waveform(self, waveform: WaveformData) -> WaveformData:
        self.db.add(waveform)
        self.db.commit()
        self.db.refresh(waveform)
        return waveform
    
    def create_segment(self, segment: AudioSegment) -> AudioSegment:
        self.db.add(segment)
        self.db.commit()
        self.db.refresh(segment)
        return segment
    
    def update_analysis(self, asset_id: UUID, updates: dict) -> AudioAnalysis:
        analysis = self.get_by_asset_id(asset_id)
        if not analysis:
            raise ValueError(f"Analysis for asset {asset_id} not found")
        
        for key, value in updates.items():
            if hasattr(analysis, key):
                setattr(analysis, key, value)
        
        analysis.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(analysis)
        return analysis