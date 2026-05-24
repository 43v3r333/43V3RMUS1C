"""
Audio Intelligence Engine Services - Librosa-powered analysis
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np

from .models import (
    WaveformData,
    AudioAnalysis,
    BeatMarker,
    Segment,
    HookCandidate,
)

logger = logging.getLogger(__name__)


class AudioIntelligenceEngine:
    """
    Audio intelligence engine with Librosa processing.
    Handles BPM detection, beat markers, transient analysis,
    waveform generation, silence detection, and hook analysis.
    """
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        sample_rate: int = 22050,
    ):
        self.storage_path = Path(storage_path or "./storage/audio")
        self.sample_rate = sample_rate
        self._librosa = None  # Lazy import
    
    def _get_librosa(self):
        """Lazy import of librosa"""
        if self._librosa is None:
            try:
                import librosa
                self._librosa = librosa
            except ImportError:
                logger.warning("Librosa not available. Audio analysis will be limited.")
                return None
        return self._librosa
    
    async def analyze_audio(
        self,
        file_path: str,
        media_asset_id: UUID,
    ) -> AudioAnalysis:
        """
        Full audio analysis pipeline using Librosa.
        """
        librosa = self._get_librosa()
        if librosa is None:
            raise RuntimeError("Librosa is required for audio analysis")
        
        analysis = AudioAnalysis(media_asset_id=media_asset_id)
        
        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=self.sample_rate)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # BPM detection
            bpm, beats = await self.detect_bpm(file_path, y, sr)
            analysis.bpm = bpm
            analysis.bpm_confidence = self._calculate_bpm_confidence(beats)
            
            # Beat markers
            beat_times = librosa.frames_to_time(beats, sr=sr)
            analysis.beat_markers = beat_times.tolist()
            
            # Downbeat detection (if possible)
            try:
                downbeats = self._detect_downbeats(beats)
                if downbeats is not None:
                    analysis.downbeat_markers = librosa.frames_to_time(
                        downbeats, sr=sr
                    ).tolist()
            except Exception as e:
                logger.debug(f"Downbeat detection failed: {e}")
            
            # Time signature
            analysis.time_signature = self._estimate_time_signature(beats)
            
            # Transient detection
            transients, onset_env = await self.detect_transients(file_path, y, sr)
            analysis.transient_markers = librosa.frames_to_time(
                transients, sr=sr
            ).tolist()
            analysis.onset_strength = onset_env.tolist() if len(onset_env) < 10000 else None
            
            # Spectral analysis
            spectral = await self._analyze_spectral(y, sr)
            analysis.spectral_centroid = spectral.get("centroid")
            analysis.spectral_rolloff = spectral.get("rolloff")
            analysis.spectral_flux = spectral.get("flux")
            
            # Silence detection
            silence_regions = await self.detect_silence(file_path, y, sr)
            analysis.silence_regions = silence_regions
            
            # Key signature estimation
            key_info = self._estimate_key(y, sr)
            analysis.key_signature = key_info.get("key")
            analysis.key_confidence = key_info.get("confidence")
            analysis.mode = key_info.get("mode")
            
            # Hook/chorus analysis foundations
            hook_candidates = await self.analyze_potential_hooks(
                file_path, y, sr, beat_times
            )
            analysis.hook_candidates = [
                {"start": h.start_time, "end": h.end_time, "score": h.score}
                for h in hook_candidates
            ]
            
            # Chorus regions
            chorus_regions = await self._find_chorus_regions(y, sr, hook_candidates)
            analysis.chorus_regions = chorus_regions
            
            # Dynamic range and loudness
            analysis.dynamic_range = float(np.ptp(y))
            analysis.loudness = float(np.sqrt(np.mean(y ** 2)))
            
            # Store features data
            analysis.features_data = {
                "duration": duration,
                "sample_rate": sr,
                "rms": float(np.sqrt(np.mean(y ** 2))),
                "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(y)[0])),
            }
            
        except Exception as e:
            logger.error(f"Audio analysis error: {e}")
            raise
        
        return analysis
    
    async def detect_bpm(
        self,
        file_path: str,
        y: Optional[np.ndarray] = None,
        sr: Optional[int] = None,
    ) -> Tuple[float, np.ndarray]:
        """
        Detect BPM using multiple methods and ensemble them.
        """
        librosa = self._get_librosa()
        if librosa is None:
            return 0.0, np.array([])
        
        if y is None:
            y, sr = librosa.load(file_path, sr=self.sample_rate)
        
        # Use both onset envelope and beat tracking
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        
        # Method 1: Tempo from onset strength
        tempo_1, beats_1 = librosa.beat.beat_track(
            onset_envelope=onset_env, sr=sr, units="frames"
        )
        
        # Method 2: Full tempogram
        tempogram = librosa.feature.ftempogram(
            y=y, sr=sr, onset_envelope=onset_env, lag=[1, 2, 3, 4]
        )
        
        # Use median for more robust estimation
        tempo_values = [float(tempo_1)]
        
        # Get tempo from autocorrelation of tempogram
        try:
            autocoor = np.mean(tempogram, axis=0)
            peaks = np.where(
                (autocoor[1:] > autocoor[:-1]) & 
                (autocoor[1:] > autocoor[2:])
            )[0] + 1
            if len(peaks) > 0:
                tempo_values.append(float(sr * 512 / peaks[0]))
        except:
            pass
        
        # Return median BPM and best beats
        bpm = float(np.median(tempo_values))
        beats = beats_1
        
        # Normalize to 60-200 range
        while bpm < 60 and bpm > 0:
            bpm *= 2
        while bpm > 200:
            bpm /= 2
        
        return bpm, beats
    
    def _calculate_bpm_confidence(self, beats: np.ndarray) -> float:
        """Calculate confidence score for BPM detection"""
        if len(beats) < 2:
            return 0.0
        
        # Calculate beat intervals
        intervals = np.diff(beats)
        
        if len(intervals) == 0:
            return 0.0
        
        # Coefficient of variation
        cv = np.std(intervals) / (np.mean(intervals) + 1e-6)
        
        # Higher confidence for lower variation
        confidence = max(0.0, 1.0 - cv)
        
        return float(confidence)
    
    async def detect_transients(
        self,
        file_path: str,
        y: Optional[np.ndarray] = None,
        sr: Optional[int] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect transients using onset detection.
        """
        librosa = self._get_librosa()
        if librosa is None:
            return np.array([]), np.array([])
        
        if y is None:
            y, sr = librosa.load(file_path, sr=self.sample_rate)
        
        # Onset strength envelope
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        
        # Detect onsets
        onsets = librosa.onset.onset_detect(
            y=y, sr=sr, onset_envelope=onset_env, backtrack=False
        )
        
        return onsets, onset_env
    
    async def detect_silence(
        self,
        file_path: str,
        y: Optional[np.ndarray] = None,
        sr: Optional[int] = None,
        threshold_db: float = -40,
        min_duration: float = 0.5,
    ) -> List[Dict[str, float]]:
        """
        Detect silence regions in audio.
        """
        librosa = self._get_librosa()
        if librosa is None:
            return []
        
        if y is None:
            y, sr = librosa.load(file_path, sr=self.sample_rate)
        
        # Convert threshold to amplitude
        threshold = librosa.db_to_amplitude(threshold_db)
        
        # Get frame-level energy
        hop_length = 512
        rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
        times = librosa.times_like(rms, sr=sr, hop_length=hop_length)
        
        # Find silence regions
        silence_regions = []
        in_silence = False
        silence_start = 0
        
        for i, (t, r) in enumerate(zip(times, rms)):
            is_silent = r < threshold
            
            if is_silent and not in_silence:
                silence_start = t
                in_silence = True
            elif not is_silent and in_silence:
                duration = t - silence_start
                if duration >= min_duration:
                    silence_regions.append({
                        "start": float(silence_start),
                        "end": float(t),
                        "duration": float(duration),
                    })
                in_silence = False
        
        # Handle end of file silence
        if in_silence:
            duration = times[-1] - silence_start
            if duration >= min_duration:
                silence_regions.append({
                    "start": float(silence_start),
                    "end": float(times[-1]),
                    "duration": float(duration),
                })
        
        return silence_regions
    
    async def detect_segments(
        self,
        file_path: str,
        y: Optional[np.ndarray] = None,
        sr: Optional[int] = None,
    ) -> List[Segment]:
        """
        Segment audio into structural parts.
        """
        librosa = self._get_librosa()
        if librosa is None:
            return []
        
        if y is None:
            y, sr = librosa.load(file_path, sr=self.sample_rate)
        
        # Use beat-synchronous chroma for structure analysis
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        
        # Self-similarity matrix
        S = librosa.segment.similarity_matrix(chroma)
        
        # Find segment boundaries
        bound_frames = librosa.segment.recurrence_matrix(
            S, sparse=True
        ).toarray()
        
        # Refine boundaries
        try:
            boundaries = librosa.segment.detect_gmm_boundary(
                S, librosa.segment.recurrence_to_likelihood(S)
            )
        except:
            # Fallback to simpler boundary detection
            boundaries = librosa.onset.onset_detect(y=y, sr=sr)
        
        # Convert to times
        boundary_times = librosa.frames_to_time(boundaries, sr=sr)
        
        # Build segments
        segments = []
        for i, t in enumerate(boundary_times[:-1]):
            segments.append(Segment(
                start_time=float(t),
                end_time=float(boundary_times[i + 1]),
                segment_type="section",
                confidence=1.0,
            ))
        
        return segments
    
    async def analyze_potential_hooks(
        self,
        file_path: str,
        y: np.ndarray,
        sr: int,
        beat_times: np.ndarray,
    ) -> List[HookCandidate]:
        """
        Analyze potential hook regions.
        """
        librosa = self._get_librosa()
        if librosa is None:
            return []
        
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Get RMS energy for each beat
        hop_length = 512
        rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
        rms_times = librosa.times_like(rms, sr=sr, hop_length=hop_length)
        
        # Find high-energy regions that repeat
        candidates = []
        
        # Look for high RMS regions (potential hooks)
        rms_threshold = np.percentile(rms, 80)
        high_energy_frames = np.where(rms > rms_threshold)[0]
        
        if len(high_energy_frames) > 0:
            # Cluster nearby high-energy frames
            frame_diff = np.diff(high_energy_frames)
            splits = np.where(frame_diff > sr / hop_length)[0] + 1
            
            regions = np.split(high_energy_frames, splits)
            
            for region in regions:
                if len(region) < 10:
                    continue
                
                start_time = rms_times[region[0]]
                end_time = rms_times[region[-1]]
                duration_seg = end_time - start_time
                
                # Hook should be between 4 and 32 seconds
                if 4 <= duration_seg <= 32:
                    # Calculate score based on energy and structure
                    region_rms = np.mean(rms[region])
                    score = float(region_rms / (rms_threshold + 1e-6))
                    
                    candidates.append(HookCandidate(
                        start_time=float(start_time),
                        end_time=float(end_time),
                        score=score,
                        characteristics={
                            "energy": float(region_rms),
                            "duration": float(duration_seg),
                        }
                    ))
        
        # Sort by score and return top candidates
        candidates.sort(key=lambda c: c.score, reverse=True)
        
        return candidates[:10]  # Top 10 candidates
    
    def _detect_downbeats(self, beats: np.ndarray) -> Optional[np.ndarray]:
        """Detect downbeats from beat sequence"""
        if len(beats) < 4:
            return None
        
        # Simple heuristic: every 4th beat is a downbeat
        return beats[::4]
    
    def _estimate_time_signature(self, beats: np.ndarray) -> str:
        """Estimate time signature from beat pattern"""
        if len(beats) < 8:
            return "4/4"
        
        # Calculate intervals
        intervals = np.diff(beats)
        
        # Cluster intervals
        mean_interval = np.mean(intervals)
        
        # Most common interval patterns
        patterns = {
            "4/4": 4,
            "3/4": 3,
            "6/8": 6,
        }
        
        for sig, count in patterns.items():
            if abs(mean_interval - count) < 0.5:
                return sig
        
        return "4/4"
    
    async def _analyze_spectral(
        self,
        y: np.ndarray,
        sr: int,
    ) -> Dict[str, float]:
        """Analyze spectral features"""
        librosa = self._get_librosa()
        if librosa is None:
            return {}
        
        try:
            centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            flux = librosa.feature.spectral_flux(y=y)
            
            return {
                "centroid": float(np.mean(centroid)),
                "rolloff": float(np.mean(rolloff)),
                "flux": float(np.mean(flux)),
            }
        except:
            return {}
    
    def _estimate_key(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Estimate key signature"""
        librosa = self._get_librosa()
        if librosa is None:
            return {"key": "C", "confidence": 0.0, "mode": "major"}
        
        try:
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            
            # Chroma features
            chroma_mean = np.mean(chroma, axis=1)
            
            # Key profiles (simplified)
            key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            
            # Major/minor profiles
            major_profile = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
            minor_profile = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
            
            # Find best match
            best_key = 0
            best_mode = "major"
            best_corr = -1
            
            for key in range(12):
                # Shift chroma
                shifted = np.roll(chroma_mean, -key)
                
                # Correlate with profiles
                major_corr = np.corrcoef(shifted, major_profile)[0, 1]
                minor_corr = np.corrcoef(shifted, minor_profile)[0, 1]
                
                if major_corr > best_corr:
                    best_corr = major_corr
                    best_key = key
                    best_mode = "major"
                
                if minor_corr > best_corr:
                    best_corr = minor_corr
                    best_key = key
                    best_mode = "minor"
            
            return {
                "key": key_names[best_key],
                "confidence": float(max(0, best_corr)),
                "mode": best_mode,
            }
        except:
            return {"key": "C", "confidence": 0.0, "mode": "major"}
    
    async def _find_chorus_regions(
        self,
        y: np.ndarray,
        sr: int,
        hook_candidates: List[HookCandidate],
    ) -> List[Dict[str, float]]:
        """Find chorus regions from hook candidates"""
        # For now, use hook candidates with high scores
        chorus = []
        
        for hook in hook_candidates:
            if hook.score > 0.8:  # High score threshold
                chorus.append({
                    "start": hook.start_time,
                    "end": hook.end_time,
                    "duration": hook.end_time - hook.start_time,
                    "score": hook.score,
                })
        
        return chorus
    
    async def generate_waveform(
        self,
        file_path: str,
        samples_per_pixel: int = 512,
        display_width: int = 1000,
    ) -> Dict[str, Any]:
        """
        Generate waveform data for visualization.
        """
        librosa = self._get_librosa()
        
        if librosa is None:
            return {"peaks": [], "duration": 0}
        
        try:
            y, sr = librosa.load(file_path, sr=self.sample_rate)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Load file and compute peaks
            peaks = []
            
            # Calculate samples per display pixel
            total_pixels = display_width
            samples_per_pixel = len(y) // total_pixels
            
            if samples_per_pixel > 0:
                # Reshape into chunks
                chunks = y[:total_pixels * samples_per_pixel].reshape(
                    total_pixels, samples_per_pixel
                )
                peaks = np.max(np.abs(chunks), axis=1).tolist()
            else:
                peaks = np.abs(y).tolist()[:display_width]
            
            return {
                "peaks": peaks,
                "duration": float(duration),
                "sample_rate": sr,
                "num_channels": 1,
            }
            
        except Exception as e:
            logger.error(f"Waveform generation error: {e}")
            return {"peaks": [], "duration": 0}