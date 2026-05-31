"""
FFmpeg orchestration engine for media processing.
Provides a clean abstraction layer for FFmpeg operations.
"""
import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


@dataclass
class FFmpegInput:
    """FFmpeg input configuration"""
    path: str
    start_time: Optional[float] = None  # seconds
    duration: Optional[float] = None  # seconds
    volume: Optional[float] = None  # 0.0 to 2.0
    speed: Optional[float] = None  # playback speed multiplier
    loops: Optional[int] = None  # number of loops (-1 for infinite)
    
    def to_filter_args(self) -> List[str]:
        """Convert to FFmpeg filter arguments"""
        args = []
        if self.start_time is not None:
            args.extend(["-ss", str(self.start_time)])
        if self.duration is not None:
            args.extend(["-t", str(self.duration)])
        return args


@dataclass
class FFmpegOutput:
    """FFmpeg output configuration"""
    path: str
    format: Optional[str] = None  # mp4, mp3, webm, etc.
    
    # Video settings
    video_codec: Optional[str] = None  # libx264, libvpx, etc.
    width: Optional[int] = None
    height: Optional[int] = None
    frame_rate: Optional[float] = None
    bitrate: Optional[str] = None  # e.g., "5M"
    
    # Audio settings
    audio_codec: Optional[str] = None  # aac, libmp3lame, etc.
    audio_bitrate: Optional[str] = None  # e.g., "192k"
    audio_sample_rate: Optional[int] = None  # e.g., 44100
    channels: Optional[int] = None  # 1 = mono, 2 = stereo
    volume: Optional[float] = None  # 0.0 to 2.0
    
    # Encoding quality
    preset: str = "medium"  # ultrafast, fast, medium, slow, veryslow
    crf: int = 23  # 0-51, lower = better quality
    
    # Overwrite output
    overwrite: bool = True


@dataclass
class FFmpegFilter:
    """FFmpeg video/audio filter"""
    name: str
    params: Dict[str, Any] = field(default_factory=dict)
    
    def to_ffmpeg_arg(self) -> str:
        """Convert to FFmpeg filter string"""
        if not self.params:
            return self.name
        param_str = ",".join(f"{k}={v}" for k, v in self.params.items())
        return f"{self.name}={param_str}"


@dataclass
class RenderRequest:
    """Complete render request with inputs, outputs, and filters"""
    inputs: List[FFmpegInput]
    output: FFmpegOutput
    filters: List[FFmpegFilter] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_ffmpeg_command(self) -> List[str]:
        """Build FFmpeg command from request"""
        cmd = ["ffmpeg"]
        
        # Global options
        if self.output.overwrite:
            cmd.append("-y")
        
        # Input files
        for inp in self.inputs:
            cmd.extend(["-i", inp.path])
        
        # Input-specific options (seek, duration)
        for inp in self.inputs:
            cmd.extend(inp.to_filter_args())
        
        # Video filters
        if self.filters:
            filter_chain = ";".join(f.to_ffmpeg_arg() for f in self.filters)
            cmd.extend(["-vf", filter_chain])
        
        # Output options
        if self.output.video_codec:
            cmd.extend(["-c:v", self.output.video_codec])
        
        if self.output.width and self.output.height:
            cmd.extend(["-s", f"{self.output.width}x{self.output.height}"])
        
        if self.output.frame_rate:
            cmd.extend(["-r", str(self.output.frame_rate)])
        
        if self.output.bitrate:
            cmd.extend(["-b:v", self.output.bitrate])
        
        # Audio options
        if self.output.audio_codec:
            cmd.extend(["-c:a", self.output.audio_codec])
        
        if self.output.audio_bitrate:
            cmd.extend(["-b:a", self.output.audio_bitrate])
        
        if self.output.audio_sample_rate:
            cmd.extend(["-ar", str(self.output.audio_sample_rate)])
        
        if self.output.channels:
            cmd.extend(["-ac", str(self.output.channels)])
        
        # Encoding preset
        cmd.extend(["-preset", self.output.preset])
        cmd.extend(["-crf", str(self.output.crf)])
        
        # Output file
        cmd.append(self.output.path)
        
        return cmd


@dataclass
class MediaProbeResult:
    """Media file metadata from ffprobe"""
    format: str
    duration: float
    size: int
    bit_rate: int
    streams: List[Dict[str, Any]]
    
    @property
    def video_stream(self) -> Optional[Dict[str, Any]]:
        """Get first video stream"""
        for s in self.streams:
            if s.get("codec_type") == "video":
                return s
        return None
    
    @property
    def audio_stream(self) -> Optional[Dict[str, Any]]:
        """Get first audio stream"""
        for s in self.streams:
            if s.get("codec_type") == "audio":
                return s
        return None
    
    @property
    def width(self) -> Optional[int]:
        return self.video_stream.get("width") if self.video_stream else None
    
    @property
    def height(self) -> Optional[int]:
        return self.video_stream.get("height") if self.video_stream else None
    
    @property
    def frame_rate(self) -> Optional[float]:
        if self.video_stream and "r_frame_rate" in self.video_stream:
            num, denom = self.video_stream["r_frame_rate"].split("/")
            return float(num) / float(denom)
        return None
    
    @property
    def audio_channels(self) -> Optional[int]:
        return self.audio_stream.get("channels") if self.audio_stream else None
    
    @property
    def audio_sample_rate(self) -> Optional[int]:
        if self.audio_stream and "sample_rate" in self.audio_stream:
            return int(self.audio_stream["sample_rate"])
        return None
    
    @property
    def video_codec(self) -> Optional[str]:
        return self.video_stream.get("codec_name") if self.video_stream else None
    
    @property
    def audio_codec(self) -> Optional[str]:
        return self.audio_stream.get("codec_name") if self.audio_stream else None


class FFmpegEngine:
    """
    FFmpeg orchestration engine.
    Provides high-level operations for media processing.
    """
    
    def __init__(self, ffmpeg_path: str = "ffmpeg", ffprobe_path: str = "ffprobe"):
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path
    
    def probe(self, media_path: str) -> MediaProbeResult:
        """
        Probe media file and extract metadata.
        
        Args:
            media_path: Path to media file
            
        Returns:
            MediaProbeResult with extracted metadata
        """
        cmd = [
            self.ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            media_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            format_info = data.get("format", {})
            
            streams = []
            for stream in data.get("streams", []):
                streams.append({
                    "codec_type": stream.get("codec_type"),
                    "codec_name": stream.get("codec_name"),
                    "width": stream.get("width"),
                    "height": stream.get("height"),
                    "r_frame_rate": stream.get("r_frame_rate"),
                    "sample_rate": stream.get("sample_rate"),
                    "channels": stream.get("channels"),
                    "duration": stream.get("duration"),
                })
            
            return MediaProbeResult(
                format=format_info.get("format_name", "unknown"),
                duration=float(format_info.get("duration", 0)),
                size=int(format_info.get("size", 0)),
                bit_rate=int(format_info.get("bit_rate", 0)),
                streams=streams
            )
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFprobe failed: {e.stderr}")
            raise RuntimeError(f"Failed to probe media: {e.stderr}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse ffprobe output: {e}")
            raise RuntimeError("Failed to parse media metadata")
    
    def execute(self, request: RenderRequest) -> Tuple[int, str, str]:
        """
        Execute a render request.
        
        Args:
            request: RenderRequest with input/output configuration
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        cmd = request.to_ffmpeg_command()
        logger.info(f"Executing FFmpeg: {' '.join(cmd[:5])}...")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg execution timed out")
            raise RuntimeError("FFmpeg execution timed out (1 hour limit)")
        except Exception as e:
            logger.error(f"FFmpeg execution failed: {e}")
            raise
    
    def transcode(
        self,
        input_path: str,
        output_path: str,
        format: str = "mp4",
        video_codec: str = "libx264",
        audio_codec: str = "aac",
        bitrate: str = "5M",
        preset: str = "medium"
    ) -> bool:
        """
        Simple transcoding operation.
        
        Args:
            input_path: Source file path
            output_path: Destination file path
            format: Output format
            video_codec: Video codec to use
            audio_codec: Audio codec to use
            bitrate: Video bitrate
            preset: Encoding preset
            
        Returns:
            True if successful
        """
        output = FFmpegOutput(
            path=output_path,
            format=format,
            video_codec=video_codec,
            audio_codec=audio_codec,
            bitrate=bitrate,
            preset=preset
        )
        
        request = RenderRequest(
            inputs=[FFmpegInput(path=input_path)],
            output=output
        )
        
        returncode, _, stderr = self.execute(request)
        
        if returncode != 0:
            logger.error(f"Transcode failed: {stderr}")
            return False
        
        return True
    
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
        output = FFmpegOutput(
            path=output_path,
            format=format,
            audio_codec="libmp3lame" if format == "mp3" else None,
            audio_bitrate=bitrate
        )
        
        request = RenderRequest(
            inputs=[FFmpegInput(path=input_path)],
            output=output
        )
        
        returncode, _, stderr = self.execute(request)
        return returncode == 0
    
    def create_thumbnail(
        self,
        input_path: str,
        output_path: str,
        timestamp: str = "00:00:01",
        width: int = 320,
        height: int = 180
    ) -> bool:
        """
        Generate thumbnail from video at specific timestamp.
        
        Args:
            input_path: Source video path
            output_path: Thumbnail output path
            timestamp: Timestamp to extract frame (HH:MM:SS)
            width: Output width
            height: Output height
        """
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-ss", timestamp,
            "-i", input_path,
            "-vframes", "1",
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
            "-q:v", "2",  # JPEG quality
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return False
    
    def concatenate_videos(
        self,
        input_paths: List[str],
        output_path: str,
        temp_dir: str = "/tmp"
    ) -> bool:
        """
        Concatenate multiple videos into one.
        Uses concat demuxer for reliable concatenation.
        """
        # Create temp file list
        list_file = os.path.join(temp_dir, "concat_list.txt")
        
        with open(list_file, "w") as f:
            for path in input_paths:
                f.write(f"file '{path}'\n")
        
        try:
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", list_file,
                "-c", "copy",  # Stream copy for speed
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Video concatenation failed: {e}")
            return False
        finally:
            if os.path.exists(list_file):
                os.unlink(list_file)
    
    def normalize_audio(
        self,
        input_path: str,
        output_path: str,
        target_loudness: float = -14.0  # LUFS
    ) -> bool:
        """
        Normalize audio loudness using loudnorm filter.
        """
        cmd = [
            self.ffmpeg_path,
            "-i", input_path,
            "-af", f"loudnorm=I={target_loudness}:TP=-1.5:LRA=11",
            "-ar", "44100",
            "-ac", "2",
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Audio normalization failed: {e}")
            return False
    
    def generate_waveform(
        self,
        input_path: str,
        output_path: str,
        samples_per_second: int = 100,
        width: int = 1920,
        height: int = 200
    ) -> bool:
        """
        Generate waveform image from audio file.
        """
        cmd = [
            self.ffmpeg_path,
            "-i", input_path,
            "-filter_complex",
            f"aformat=channel_layouts=mono,showwavespic=s={width}x{height}:colors='#f97316'",
            "-frames:v", "1",
            "-y",
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Waveform generation failed: {e}")
            return False
    
    def trim_video(
        self,
        input_path: str,
        output_path: str,
        start_time: float,
        end_time: float,
        quality: str = "high"
    ) -> bool:
        """
        Trim video to specified time range.
        """
        # Set quality parameters
        preset_map = {
            "low": "ultrafast",
            "medium": "fast",
            "high": "medium",
            "ultra": "slow"
        }
        
        preset = preset_map.get(quality, "medium")
        
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-ss", str(start_time),
            "-i", input_path,
            "-t", str(end_time - start_time),
            "-c:v", "libx264",
            "-preset", preset,
            "-crf", "18" if quality == "high" else "23",
            "-c:a", "aac",
            "-b:a", "192k",
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Video trim failed: {e}")
            return False
    
    def get_duration(self, media_path: str) -> float:
        """Get duration of media file in seconds"""
        probe = self.probe(media_path)
        return probe.duration
    
    def get_video_info(self, media_path: str) -> Dict[str, Any]:
        """Get comprehensive video information"""
        probe = self.probe(media_path)
        return {
            "duration": probe.duration,
            "width": probe.width,
            "height": probe.height,
            "frame_rate": probe.frame_rate,
            "video_codec": probe.video_codec,
            "audio_codec": probe.audio_codec,
            "audio_channels": probe.audio_channels,
            "audio_sample_rate": probe.audio_sample_rate,
            "bit_rate": probe.bit_rate,
            "size": probe.size
        }


# Global FFmpeg engine instance
_ffmpeg_engine: Optional[FFmpegEngine] = None


def get_ffmpeg_engine() -> FFmpegEngine:
    """Get or create global FFmpeg engine"""
    global _ffmpeg_engine
    
    if _ffmpeg_engine is None:
        from app.core.config import settings
        ffmpeg_path = getattr(settings, 'ffmpeg_path', 'ffmpeg')
        ffprobe_path = getattr(settings, 'ffprobe_path', 'ffprobe')
        _ffmpeg_engine = FFmpegEngine(ffmpeg_path, ffprobe_path)
    
    return _ffmpeg_engine