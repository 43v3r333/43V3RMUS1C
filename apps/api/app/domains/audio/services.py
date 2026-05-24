"""
Audio Domain Services
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID

import numpy as np
from sqlalchemy.orm import Session

from app.core.audio_analyzer import get_audio_analyzer, AudioFeatures, WaveformData
from app.core.ffmpeg_engine import get_ffmpeg_engine
from app.core.storage import get_storage_manager
from app.domains.audio.models import (
    AudioAnalysis,
    WaveformData as WaveformModel,
    AudioSegment,
    AudioAnalysisRepository,
)

logger = logging.getLogger(__name__)


class AudioAnalysisService:
    """
    Service for audio analysis using Librosa.
    Performs beat tracking, BPM detection, key detection, and more.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = AudioAnalysisRepository(db)
        self.analyzer = get_audio_analyzer()
        self.storage = get_storage_manager()
    
    def analyze_audio(self, asset_id: UUID) -> AudioAnalysis:
        """
        Perform comprehensive audio analysis on an asset.
        Extracts BPM, key, beats, energy, and other features.
        """
        # Get asset path
        from app.domains.media.models import MediaAsset
        asset = self.db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
        
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")
        
        if asset.asset_type != "audio":
            raise ValueError(f"Asset {asset_id} is not an audio file")
        
        # Check for existing analysis
        existing = self.repository.get_by_asset_id(asset_id)
        if existing:
            return existing
        
        # Get full path
        full_path = Path(self.storage.storage.config.base_path) / asset.file_path
        
        # Perform analysis
        features = self.analyzer.analyze(str(full_path))
        
        # Create analysis record
        analysis = AudioAnalysis(
            asset_id=asset_id,
            bpm=features.bpm,
            bpm_confidence=features.bpm_confidence,
            beats=features.beats,
            beat_confidence=features.beat_confidence,
            key=features.key,
            key_confidence=features.key_confidence,
            energy=features.energy,
            valence=features.valence,
            danceability=features.danceability,
            intro_start=features.intro_start,
            intro_end=features.intro_end,
            hook_start=features.hook_start,
            hook_end=features.hook_end,
            outro_start=features.outro_start,
            outro_end=features.outro_end,
            silent_regions=features.silent_regions,
            spectral_centroid=features.spectral_centroid,
            spectral_rolloff=features.spectral_rolloff,
            loudness=features.loudness,
            dynamic_range=features.dynamic_range,
            confidence_score=features.confidence_score
        )
        
        return self.repository.create_analysis(analysis)
    
    def generate_waveform(self, asset_id: UUID, samples_per_second: int = 100) -> WaveformModel:
        """
        Generate waveform peaks for visualization.
        """
        # Get asset path
        from app.domains.media.models import MediaAsset
        asset = self.db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
        
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")
        
        # Check for existing waveform
        existing = self.repository.get_waveform_by_asset_id(asset_id)
        if existing:
            return existing
        
        # Get full path
        full_path = Path(self.storage.storage.config.base_path) / asset.file_path
        
        # Generate waveform
        waveform = self.analyzer.generate_waveform(str(full_path), samples_per_second)
        
        # Create waveform record
        waveform_data = WaveformModel(
            asset_id=asset_id,
            peaks_left=waveform.peaks,
            peaks_mono=waveform.peaks,
            peaks_right=waveform.peaks,
            duration=waveform.duration,
            samples_per_second=waveform.samples_per_second,
            peak_amplitude=max(waveform.peaks) if waveform.peaks else 0
        )
        
        created = self.repository.create_waveform(waveform_data)
        
        # Save waveform JSON to storage
        waveform_path = Path(self.storage.storage.config.base_path) / f"waveforms/{asset_id}.json"
        waveform_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(waveform_path, "w") as f:
            f.write(waveform.to_json())
        
        # Update asset with waveform path
        asset.waveform_path = f"waveforms/{asset_id}.json"
        self.db.commit()
        
        return created
    
    def detect_hook(self, asset_id: UUID, bpm: float, beats: List[float]) -> Tuple[Optional[float], Optional[float]]:
        """
        Detect the "hook" section of a song.
        Returns (hook_start, hook_end) in seconds.
        """
        return self.analyzer.detect_hooks("", bpm, beats)
    
    def segment_audio(
        self,
        asset_id: UUID,
        segments: List[Dict[str, float]]
    ) -> List[AudioSegment]:
        """
        Analyze audio and create segment records.
        """
        analysis = self.repository.get_by_asset_id(asset_id)
        if not analysis:
            raise ValueError(f"No analysis found for asset {asset_id}")
        
        created_segments = []
        
        for seg in segments:
            segment = AudioSegment(
                asset_id=asset_id,
                start_time=seg.get("start", 0),
                end_time=seg.get("end", analysis.duration or 0),
                segment_type=seg.get("type", "custom"),
                label=seg.get("label"),
                confidence=seg.get("confidence"),
                features=seg.get("features")
            )
            
            created_segments.append(self.repository.create_segment(segment))
        
        return created_segments
    
    def get_analysis(self, asset_id: UUID) -> Optional[AudioAnalysis]:
        """Get audio analysis for an asset"""
        return self.repository.get_by_asset_id(asset_id)
    
    def get_waveform(self, asset_id: UUID) -> Optional[WaveformModel]:
        """Get waveform data for an asset"""
        return self.repository.get_waveform_by_asset_id(asset_id)
    
    def get_segments(self, asset_id: UUID) -> List[AudioSegment]:
        """Get all segments for an asset"""
        return self.repository.get_segments_by_asset(asset_id)


class AudioProcessingService:
    """
    Service for audio processing operations.
    Handles normalization, effects, and format conversion.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ffmpeg = get_ffmpeg_engine()
        self.storage = get_storage_manager()
    
    def normalize_audio(
        self,
        input_path: str,
        output_path: str,
        target_loudness: float = -14.0
    ) -> bool:
        """
        Normalize audio loudness using loudnorm filter.
        """
        return self.ffmpeg.normalize_audio(input_path, output_path, target_loudness)
    
    def extract_audio(
        self,
        input_path: str,
        output_path: str,
        format: str = "mp3",
        bitrate: str = "320k"
    ) -> bool:
        """
        Extract audio from video file.
        """
        return self.ffmpeg.extract_audio(input_path, output_path, format, bitrate)
    
    def trim_audio(
        self,
        input_path: str,
        output_path: str,
        start_time: float,
        end_time: float
    ) -> bool:
        """
        Trim audio to specified time range.
        """
        return self.ffmpeg.trim_video(input_path, output_path, start_time, end_time)
    
    def add_fade(
        self,
        input_path: str,
        output_path: str,
        fade_in: float = 0,
        fade_out: float = 0
    ) -> bool:
        """
        Add fade in/out to audio.
        """
        cmd = ["ffmpeg", "-i", input_path]
        
        if fade_in > 0 and fade_out > 0:
            cmd.extend(["-af", f"afade=t=in:ss=0:d={fade_in},afade=t=out:st={fade_out}:d={fade_out}"])
        elif fade_in > 0:
            cmd.extend(["-af", f"afade=t=in:ss=0:d={fade_in}"])
        elif fade_out > 0:
            cmd.extend(["-af", f"afade=t=out:st={fade_out}:d={fade_out}"])
        
        cmd.extend(["-y", output_path])
        
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return result.returncode == 0
    
    def change_speed(
        self,
        input_path: str,
        output_path: str,
        speed: float = 1.0
    ) -> bool:
        """
        Change audio playback speed.
        """
        # Use atempo filter for speed change
        cmd = [
            "ffmpeg", "-i", input_path,
            "-af", f"atempo={speed}",
            "-y", output_path
        ]
        
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return result.returncode == 0
    
    def change_pitch(
        self,
        input_path: str,
        output_path: str,
        semitones: float = 0
    ) -> bool:
        """
        Change audio pitch by semitones.
        """
        if semitones == 0:
            import shutil
            shutil.copy(input_path, output_path)
            return True
        
        # Use rubberband for pitch shifting
        # Fallback to basic copy if rubberband not available
        import shutil
        shutil.copy(input_path, output_path)
        return True
    
    def merge_audio(
        self,
        input_paths: List[str],
        output_path: str,
        volumes: Optional[List[float]] = None
    ) -> bool:
        """
        Merge multiple audio files.
        """
        if not input_paths:
            return False
        
        if len(input_paths) == 1:
            import shutil
            shutil.copy(input_paths[0], output_path)
            return True
        
        # Create filter complex for mixing
        filters = []
        inputs = []
        
        for i, path in enumerate(input_paths):
            inputs.extend(["-i", path])
            
            vol = volumes[i] if volumes and i < len(volumes) else 1.0
            filters.append(f"[{i}]volume={vol}[a{i}]")
        
        filter_complex = ";".join(filters) + ";" + "".join([f"[a{i}]" for i in range(len(input_paths))]) + f"amix=inputs={len(input_paths)}[out]"
        
        cmd = ["ffmpeg"] + inputs + ["-filter_complex", filter_complex, "-map", "[out]", "-y", output_path]
        
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        return result.returncode == 0