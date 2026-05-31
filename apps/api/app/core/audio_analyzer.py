"""
Audio analysis engine using Librosa for music intelligence.
Provides beat tracking, BPM detection, waveform generation, and audio features.
"""
import json
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class AudioFeatures:
    """Audio analysis results"""
    # Tempo
    bpm: float
    bpm_confidence: float
    
    # Beat information
    beats: List[float]  # timestamps in seconds
    beat_confidence: float
    
    # Musical key
    key: str  # e.g., "C major"
    key_confidence: float
    
    # Energy and mood (0.0 to 1.0)
    energy: float
    valence: float  # positive/negative
    danceability: float
    
    # Time markers
    intro_start: Optional[float] = None
    intro_end: Optional[float] = None
    hook_start: Optional[float] = None
    hook_end: Optional[float] = None
    outro_start: Optional[float] = None
    outro_end: Optional[float] = None
    
    # Silence regions
    silent_regions: List[Tuple[float, float]] = []  # (start, end) tuples
    
    # Spectral features
    spectral_centroid: float
    spectral_rolloff: float
    
    # Loudness
    loudness: float  # LUFS
    dynamic_range: float
    
    # Overall confidence
    confidence_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "bpm": self.bpm,
            "bpm_confidence": self.bpm_confidence,
            "beats": self.beats,
            "beat_confidence": self.beat_confidence,
            "key": self.key,
            "key_confidence": self.key_confidence,
            "energy": self.energy,
            "valence": self.valence,
            "danceability": self.danceability,
            "intro_start": self.intro_start,
            "intro_end": self.intro_end,
            "hook_start": self.hook_start,
            "hook_end": self.hook_end,
            "outro_start": self.outro_start,
            "outro_end": self.outro_end,
            "silent_regions": self.silent_regions,
            "spectral_centroid": self.spectral_centroid,
            "spectral_rolloff": self.spectral_rolloff,
            "loudness": self.loudness,
            "dynamic_range": self.dynamic_range,
            "confidence_score": self.confidence_score,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AudioFeatures":
        """Create from dictionary"""
        return cls(
            bpm=data.get("bpm", 0),
            bpm_confidence=data.get("bpm_confidence", 0),
            beats=data.get("beats", []),
            beat_confidence=data.get("beat_confidence", 0),
            key=data.get("key", "unknown"),
            key_confidence=data.get("key_confidence", 0),
            energy=data.get("energy", 0),
            valence=data.get("valence", 0),
            danceability=data.get("danceability", 0),
            intro_start=data.get("intro_start"),
            intro_end=data.get("intro_end"),
            hook_start=data.get("hook_start"),
            hook_end=data.get("hook_end"),
            outro_start=data.get("outro_start"),
            outro_end=data.get("outro_end"),
            silent_regions=data.get("silent_regions", []),
            spectral_centroid=data.get("spectral_centroid", 0),
            spectral_rolloff=data.get("spectral_rolloff", 0),
            loudness=data.get("loudness", 0),
            dynamic_range=data.get("dynamic_range", 0),
            confidence_score=data.get("confidence_score", 0),
        )


@dataclass
class WaveformData:
    """Waveform peak data for visualization"""
    peaks: List[float]  # Normalized peaks (0.0 to 1.0)
    duration: float  # Total duration in seconds
    samples_per_second: int  # Display resolution
    
    def to_json(self) -> str:
        """Export as JSON string"""
        return json.dumps({
            "peaks": self.peaks,
            "duration": self.duration,
            "samples_per_second": self.samples_per_second
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> "WaveformData":
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls(
            peaks=data["peaks"],
            duration=data["duration"],
            samples_per_second=data["samples_per_second"]
        )


class AudioAnalyzer:
    """
    Audio analysis engine using Librosa.
    Performs beat tracking, BPM detection, waveform generation, and feature extraction.
    """
    
    def __init__(self):
        self._librosa_available = self._check_librosa()
    
    def _check_librosa(self) -> bool:
        """Check if librosa is available"""
        try:
            import librosa
            return True
        except ImportError:
            logger.warning("Librosa not available, using fallback methods")
            return False
    
    def analyze(self, audio_path: str) -> AudioFeatures:
        """
        Perform comprehensive audio analysis.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            AudioFeatures with analysis results
        """
        if self._librosa_available:
            return self._analyze_with_librosa(audio_path)
        else:
            return self._analyze_fallback(audio_path)
    
    def _analyze_with_librosa(self, audio_path: str) -> AudioFeatures:
        """Full analysis using librosa"""
        import librosa
        
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=None, mono=False)
            
            # Ensure mono for analysis
            if len(y.shape) > 1:
                y = librosa.to_mono(y)
            
            duration = len(y) / sr
            
            # BPM detection
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            bpm = float(tempo)
            
            # Beat timestamps
            beat_times = librosa.frames_to_time(beats, sr=sr).tolist()
            
            # Key detection (simplified)
            key = self._detect_key(y, sr)
            
            # Energy features
            rms = librosa.feature.rms(y=y)[0]
            energy = float(np.mean(rms))
            
            # Spectral features
            spectral_cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_roll = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            # Compute dynamic range
            dynamic_range = float(np.max(rms) - np.min(rms))
            
            # Silence detection
            silent_regions = self._detect_silence(y, sr)
            
            # Estimate confidence (based on beat clarity)
            beat_confidence = self._estimate_beat_confidence(beat_times, bpm)
            
            return AudioFeatures(
                bpm=bpm,
                bpm_confidence=beat_confidence,
                beats=beat_times,
                beat_confidence=beat_confidence,
                key=key[0],
                key_confidence=key[1],
                energy=energy,
                valence=0.5,  # Placeholder - would need ML model for valence
                danceability=0.5,  # Placeholder
                spectral_centroid=float(np.mean(spectral_cent)),
                spectral_rolloff=float(np.mean(spectral_roll)),
                loudness=energy * 100,  # Rough approximation
                dynamic_range=dynamic_range,
                silent_regions=silent_regions,
                confidence_score=beat_confidence
            )
            
        except Exception as e:
            logger.error(f"Librosa analysis failed: {e}")
            return self._analyze_fallback(audio_path)
    
    def _analyze_fallback(self, audio_path: str) -> AudioFeatures:
        """
        Fallback analysis using ffprobe/ffmpeg when librosa is not available.
        Extracts basic metadata and uses heuristic estimates.
        """
        from app.core.ffmpeg_engine import get_ffmpeg_engine
        
        ffmpeg = get_ffmpeg_engine()
        
        try:
            # Get basic info from ffprobe
            info = ffmpeg.get_video_info(audio_path)
            duration = info.get("duration", 0)
            
            # Try to get BPM from filename or metadata
            bpm = self._estimate_bpm_from_duration(duration)
            
            return AudioFeatures(
                bpm=bpm,
                bpm_confidence=0.3,  # Low confidence for fallback
                beats=[],
                beat_confidence=0.3,
                key="unknown",
                key_confidence=0.0,
                energy=0.5,
                valence=0.5,
                danceability=0.5,
                spectral_centroid=0,
                spectral_rolloff=0,
                loudness=0,
                dynamic_range=0,
                silent_regions=[],
                confidence_score=0.3
            )
            
        except Exception as e:
            logger.error(f"Fallback analysis failed: {e}")
            return AudioFeatures(
                bpm=120,
                bpm_confidence=0.0,
                beats=[],
                beat_confidence=0.0,
                key="unknown",
                key_confidence=0.0,
                energy=0,
                valence=0,
                danceability=0,
                spectral_centroid=0,
                spectral_rolloff=0,
                loudness=0,
                dynamic_range=0,
                silent_regions=[],
                confidence_score=0.0
            )
    
    def _detect_key(self, y: np.ndarray, sr: int) -> Tuple[str, float]:
        """Detect musical key (simplified chroma-based)"""
        try:
            import librosa
            
            # Compute chromagram
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            
            # Get mean chroma profile
            chroma_mean = np.mean(chroma, axis=1)
            
            # Map to key (simplified - no minor/major detection)
            notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            key_index = np.argmax(chroma_mean)
            key = notes[key_index] + " major"
            
            # Confidence based on how dominant the key note is
            confidence = float(chroma_mean[key_index] / np.sum(chroma_mean))
            
            return key, confidence
            
        except Exception as e:
            logger.error(f"Key detection failed: {e}")
            return "unknown", 0.0
    
    def _estimate_beat_confidence(self, beats: List[float], bpm: float) -> float:
        """Estimate confidence in beat detection"""
        if len(beats) < 2:
            return 0.0
        
        # Calculate beat intervals
        intervals = [beats[i+1] - beats[i] for i in range(len(beats)-1)]
        
        if not intervals:
            return 0.0
        
        # Check variance in intervals (consistent = more confident)
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        if mean_interval == 0:
            return 0.0
        
        # Lower variance = higher confidence
        cv = std_interval / mean_interval  # Coefficient of variation
        confidence = max(0.0, min(1.0, 1.0 - cv))
        
        return confidence
    
    def _detect_silence(self, y: np.ndarray, sr: int, threshold_db: float = -50) -> List[Tuple[float, float]]:
        """Detect silent regions in audio"""
        try:
            import librosa
            
            # Convert threshold to amplitude
            threshold = librosa.db_to_amplitude(threshold_db)
            
            # Calculate RMS in small windows
            frame_length = int(0.1 * sr)  # 100ms windows
            hop_length = frame_length // 2
            
            rms = librosa.feature.rms(
                y=y,
                frame_length=frame_length,
                hop_length=hop_length
            )[0]
            
            # Find silent frames
            silent_frames = np.where(rms < threshold)[0]
            
            if len(silent_frames) == 0:
                return []
            
            # Group consecutive silent frames into regions
            regions = []
            start_frame = silent_frames[0]
            
            for i in range(1, len(silent_frames)):
                if silent_frames[i] - silent_frames[i-1] > 1:
                    # Gap found - end current region
                    start_time = start_frame * hop_length / sr
                    end_time = (silent_frames[i-1] + 1) * hop_length / sr
                    
                    # Only add if region is longer than 0.1 seconds
                    if end_time - start_time > 0.1:
                        regions.append((start_time, end_time))
                    
                    start_frame = silent_frames[i]
            
            # Add final region
            start_time = start_frame * hop_length / sr
            end_time = (silent_frames[-1] + 1) * hop_length / sr
            if end_time - start_time > 0.1:
                regions.append((start_time, end_time))
            
            return regions
            
        except Exception as e:
            logger.error(f"Silence detection failed: {e}")
            return []
    
    def _estimate_bpm_from_duration(self, duration: float) -> float:
        """Heuristic BPM estimation based on audio duration"""
        # Common BPM ranges for different music genres
        if duration < 60:  # Short clip
            return 140  # Fast-paced social content
        elif duration < 180:  # Standard song
            return 120  # Default pop/electronic
        else:
            return 100  # Slower music
    
    def generate_waveform(
        self,
        audio_path: str,
        samples_per_second: int = 100
    ) -> WaveformData:
        """
        Generate waveform peaks for visualization.
        
        Args:
            audio_path: Path to audio file
            samples_per_second: Number of samples per second of audio
            
        Returns:
            WaveformData with peak values
        """
        if self._librosa_available:
            return self._generate_waveform_librosa(audio_path, samples_per_second)
        else:
            return self._generate_waveform_ffmpeg(audio_path, samples_per_second)
    
    def _generate_waveform_librosa(
        self,
        audio_path: str,
        samples_per_second: int
    ) -> WaveformData:
        """Generate waveform using librosa"""
        import librosa
        
        try:
            y, sr = librosa.load(audio_path, sr=None, mono=True)
            duration = len(y) / sr
            
            # Calculate samples per display point
            samples_per_peak = sr // samples_per_second
            
            # Downsample audio to get peaks
            n_peaks = int(duration * samples_per_second)
            
            # Resample audio
            if n_peaks > 0:
                indices = np.linspace(0, len(y) - 1, n_peaks).astype(int)
                peaks_raw = y[indices]
                
                # Normalize peaks to 0-1 range
                peaks = (peaks_raw - peaks_raw.min()) / (peaks_raw.max() - peaks_raw.min() + 1e-10)
                peaks = peaks.tolist()
            else:
                peaks = []
            
            return WaveformData(
                peaks=peaks,
                duration=duration,
                samples_per_second=samples_per_second
            )
            
        except Exception as e:
            logger.error(f"Waveform generation failed: {e}")
            return WaveformData(peaks=[], duration=0, samples_per_second=samples_per_second)
    
    def _generate_waveform_ffmpeg(
        self,
        audio_path: str,
        samples_per_second: int
    ) -> WaveformData:
        """Fallback waveform generation using FFmpeg"""
        from app.core.ffmpeg_engine import get_ffmpeg_engine
        
        ffmpeg = get_ffmpeg_engine()
        
        try:
            duration = ffmpeg.get_duration(audio_path)
            n_peaks = int(duration * samples_per_second)
            
            # Use FFmpeg to get audio samples and downsample
            # This is a simplified approach - real implementation would
            # parse the raw PCM data
            
            # Generate placeholder peaks (would need FFmpeg filter complex)
            peaks = [0.5] * n_peaks  # Placeholder
            
            return WaveformData(
                peaks=peaks,
                duration=duration,
                samples_per_second=samples_per_second
            )
            
        except Exception as e:
            logger.error(f"FFmpeg waveform generation failed: {e}")
            return WaveformData(peaks=[], duration=0, samples_per_second=samples_per_second)
    
    def detect_hooks(
        self,
        audio_path: str,
        bpm: float,
        beats: List[float]
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Detect the "hook" section of a song (the most memorable/repeated part).
        Uses energy and beat density analysis.
        
        Returns:
            Tuple of (hook_start, hook_end) in seconds, or (None, None) if not detected
        """
        if not self._librosa_available:
            return None, None
        
        import librosa
        
        try:
            y, sr = librosa.load(audio_path, sr=None, mono=True)
            duration = len(y) / sr
            
            # Calculate energy in windows
            window_size = int(0.1 * sr)  # 100ms windows
            hop_length = window_size // 2
            
            rms = librosa.feature.rms(
                y=y,
                frame_length=window_size,
                hop_length=hop_length
            )[0]
            
            # Find sections with high energy that repeat
            # Simplified: look for the first major energy spike after intro
            intro_duration = duration * 0.1  # Assume 10% intro
            
            # Find peak energy after intro
            intro_frames = int(intro_duration * samples_per_second)
            if intro_frames >= len(rms):
                return None, None
            
            peak_frame = intro_frames + np.argmax(rms[intro_frames:])
            peak_time = peak_frame / samples_per_second
            
            # Hook typically 8-16 bars
            beat_duration = 60 / bpm
            hook_duration = beat_duration * 8  # 8 bars
            
            hook_start = peak_time
            hook_end = min(peak_time + hook_duration, duration)
            
            return hook_start, hook_end
            
        except Exception as e:
            logger.error(f"Hook detection failed: {e}")
            return None, None
    
    def segment_audio(
        self,
        audio_path: str,
        segments: List[Dict[str, float]]
    ) -> List[Tuple[float, float]]:
        """
        Analyze audio and suggest segmentation points based on:
        - Beat grid alignment
        - Silence regions
        - Energy changes
        
        Args:
            audio_path: Path to audio file
            segments: List of dicts with 'start' and 'end' keys
            
        Returns:
            List of (start, end) tuples for each segment
        """
        # Get audio features
        features = self.analyze(audio_path)
        
        result_segments = []
        
        for seg in segments:
            start = seg.get("start", 0)
            end = seg.get("end", features.beats[-1] if features.beats else 0)
            
            # Ensure segments align to beats if possible
            if features.beats:
                # Snap start to nearest beat
                nearest_start = min(features.beats, key=lambda b: abs(b - start))
                # Snap end to nearest beat
                nearest_end = min(features.beats, key=lambda b: abs(b - end))
                
                # Only snap if within 0.5 seconds
                if abs(nearest_start - start) < 0.5:
                    start = nearest_start
                if abs(nearest_end - end) < 0.5:
                    end = nearest_end
            
            result_segments.append((start, end))
        
        return result_segments


# Global audio analyzer instance
_audio_analyzer: Optional[AudioAnalyzer] = None


def get_audio_analyzer() -> AudioAnalyzer:
    """Get or create global audio analyzer"""
    global _audio_analyzer
    
    if _audio_analyzer is None:
        _audio_analyzer = AudioAnalyzer()
    
    return _audio_analyzer