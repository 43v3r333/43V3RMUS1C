"""
Composition Services - Cinematic composition and scene orchestration
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from .models import (
    CompositionStatus,
    SceneType,
    TransitionType,
    CompositionGraph,
    CompositionScene,
    CompositionClip,
    CompositionTransition,
    CompositionOverlay,
    CompositionExecution,
)

logger = logging.getLogger(__name__)


@dataclass
class SceneGraph:
    """Scene graph for composition"""
    scene_id: str
    scene_type: SceneType
    clips: List[str]
    start_time: float
    end_time: float
    beats: List[Dict[str, float]]
    transitions: List[Dict[str, Any]] = field(default_factory=list)


class CompositionEngine:
    """
    Cinematic composition engine.
    Manages composition graphs, scene orchestration, and beat-aligned rendering.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._scene_handlers: Dict[str, Callable] = {}
        self._clip_handlers: Dict[str, Callable] = {}
    
    async def initialize(self) -> None:
        """Initialize the composition engine"""
        self._register_default_handlers()
        logger.info("CompositionEngine initialized")
    
    def _register_default_handlers(self) -> None:
        """Register default scene and clip handlers"""
        self._scene_handlers["intro"] = self._handle_intro_scene
        self._scene_handlers["verse"] = self._handle_verse_scene
        self._scene_handlers["chorus"] = self._handle_chorus_scene
        self._scene_handlers["bridge"] = self._handle_bridge_scene
        self._scene_handlers["outro"] = self._handle_outro_scene
        self._scene_handlers["interlude"] = self._handle_interlude_scene
    
    # ==================== Graph Operations ====================
    
    async def create_graph(
        self,
        name: str,
        description: Optional[str] = None,
        frame_rate: float = 30.0,
        resolution: tuple = (1920, 1080),
        owner_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
    ) -> CompositionGraph:
        """Create a new composition graph"""
        graph = CompositionGraph(
            name=name,
            description=description,
            frame_rate=frame_rate,
            resolution_width=resolution[0],
            resolution_height=resolution[1],
            status=CompositionStatus.DRAFT.value,
            owner_id=owner_id,
            project_id=project_id,
            scenes=[],
            clips=[],
            transitions=[],
            overlays=[],
        )
        
        self.db.add(graph)
        await self.db.commit()
        await self.db.refresh(graph)
        
        return graph
    
    async def get_graph(self, graph_id: UUID) -> Optional[CompositionGraph]:
        """Get composition graph by ID"""
        result = await self.db.execute(
            select(CompositionGraph).where(CompositionGraph.id == graph_id)
        )
        return result.scalar_one_or_none()
    
    async def update_graph(
        self,
        graph: CompositionGraph,
        **kwargs,
    ) -> CompositionGraph:
        """Update composition graph"""
        for key, value in kwargs.items():
            if hasattr(graph, key):
                setattr(graph, key, value)
        
        self.db.add(graph)
        await self.db.commit()
        await self.db.refresh(graph)
        
        return graph
    
    async def duplicate_graph(
        self,
        graph: CompositionGraph,
        name: Optional[str] = None,
    ) -> CompositionGraph:
        """Duplicate a composition graph"""
        new_graph = CompositionGraph(
            name=name or f"{graph.name} (Copy)",
            description=graph.description,
            frame_rate=graph.frame_rate,
            resolution_width=graph.resolution_width,
            resolution_height=graph.resolution_height,
            scenes=graph.scenes,
            clips=graph.clips,
            transitions=graph.transitions,
            overlays=graph.overlays,
            total_duration=graph.total_duration,
            tempo=graph.tempo,
            audio_tracks=graph.audio_tracks,
            background_music=graph.background_music,
            genre=graph.genre,
            mood=graph.mood,
            style=graph.style,
            version=1,
            parent_id=graph.id,
            owner_id=graph.owner_id,
            project_id=graph.project_id,
        )
        
        self.db.add(new_graph)
        await self.db.commit()
        await self.db.refresh(new_graph)
        
        return new_graph
    
    # ==================== Scene Operations ====================
    
    async def add_scene(
        self,
        graph: CompositionGraph,
        name: str,
        scene_type: SceneType,
        start_time: float,
        duration: float,
        config: Optional[Dict[str, Any]] = None,
        order: Optional[int] = None,
    ) -> CompositionScene:
        """Add a scene to the composition"""
        scene = CompositionScene(
            graph_id=graph.id,
            name=name,
            scene_type=scene_type.value,
            start_time=start_time,
            end_time=start_time + duration,
            duration=duration,
            config=config or {},
            order=order or len(graph.scenes or []),
        )
        
        self.db.add(scene)
        await self.db.commit()
        await self.db.refresh(scene)
        
        # Update graph scenes list
        scenes = graph.scenes or []
        scenes.append({
            "id": str(scene.id),
            "name": name,
            "type": scene_type.value,
            "start": start_time,
            "duration": duration,
        })
        graph.scenes = scenes
        graph.total_duration = max(graph.total_duration or 0, start_time + duration)
        
        self.db.add(graph)
        await self.db.commit()
        
        return scene
    
    async def get_scenes(self, graph_id: UUID) -> List[CompositionScene]:
        """Get all scenes in a composition"""
        result = await self.db.execute(
            select(CompositionScene)
            .where(CompositionScene.graph_id == graph_id)
            .order_by(CompositionScene.order)
        )
        return list(result.scalars().all())
    
    async def align_scene_to_beats(
        self,
        scene: CompositionScene,
        bpm: float,
        start_beat: int,
        end_beat: int,
    ) -> CompositionScene:
        """Align scene to beat markers"""
        beat_duration = 60.0 / bpm
        
        scene.start_beat = start_beat
        scene.end_beat = end_beat
        scene.start_time = start_beat * beat_duration
        scene.end_time = end_beat * beat_duration
        scene.duration = (end_beat - start_beat) * beat_duration
        
        # Generate beat markers
        beat_markers = []
        for beat in range(start_beat, end_beat + 1):
            beat_markers.append({
                "beat": beat,
                "timestamp": beat * beat_duration,
                "strength": 1.0 if beat % 4 == 0 else 0.5,
            })
        
        scene.beat_markers = beat_markers
        
        self.db.add(scene)
        await self.db.commit()
        await self.db.refresh(scene)
        
        return scene
    
    # ==================== Clip Operations ====================
    
    async def add_clip(
        self,
        graph: CompositionGraph,
        scene_id: Optional[UUID],
        name: str,
        clip_type: str,
        source_asset_id: Optional[str] = None,
        start_time: float = 0.0,
        duration: float = 0.0,
        source_start: float = 0.0,
        track_index: int = 0,
        order: Optional[int] = None,
    ) -> CompositionClip:
        """Add a clip to the composition"""
        clip = CompositionClip(
            graph_id=graph.id,
            scene_id=scene_id,
            name=name,
            clip_type=clip_type,
            source_asset_id=source_asset_id,
            start_time=start_time,
            duration=duration,
            source_start=source_start,
            source_end=source_start + duration,
            track_index=track_index,
            order=order or 0,
        )
        
        self.db.add(clip)
        await self.db.commit()
        await self.db.refresh(clip)
        
        # Update graph clips list
        clips = graph.clips or []
        clips.append({
            "id": str(clip.id),
            "name": name,
            "type": clip_type,
            "start": start_time,
            "duration": duration,
        })
        graph.clips = clips
        
        self.db.add(graph)
        await self.db.commit()
        
        return clip
    
    async def get_clips(
        self,
        graph_id: UUID,
        scene_id: Optional[UUID] = None,
    ) -> List[CompositionClip]:
        """Get clips in composition"""
        query = select(CompositionClip).where(CompositionClip.graph_id == graph_id)
        
        if scene_id:
            query = query.where(CompositionClip.scene_id == scene_id)
        
        query = query.order_by(CompositionClip.track_index, CompositionClip.order)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    # ==================== Transition Operations ====================
    
    async def add_transition(
        self,
        graph: CompositionGraph,
        transition_type: TransitionType,
        from_scene_id: Optional[UUID] = None,
        to_scene_id: Optional[UUID] = None,
        duration: float = 0.5,
        start_time: Optional[float] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> CompositionTransition:
        """Add a transition to the composition"""
        # Calculate timing from scene IDs if provided
        end_time = start_time + duration if start_time else 0
        
        if from_scene_id and not start_time:
            from_scene = await self.db.get(CompositionScene, from_scene_id)
            if from_scene:
                start_time = from_scene.end_time
                end_time = start_time + duration
        
        transition = CompositionTransition(
            graph_id=graph.id,
            from_scene_id=from_scene_id,
            to_scene_id=to_scene_id,
            transition_type=transition_type.value,
            duration=duration,
            start_time=start_time or 0,
            end_time=end_time,
            parameters=parameters,
        )
        
        self.db.add(transition)
        await self.db.commit()
        await self.db.refresh(transition)
        
        return transition
    
    # ==================== Overlay Operations ====================
    
    async def add_overlay(
        self,
        graph: CompositionGraph,
        name: str,
        overlay_type: str,
        content: str,
        start_time: float,
        duration: float,
        position: tuple = (0.5, 0.5),  # center
        size: Optional[tuple] = None,
        style: Optional[Dict[str, Any]] = None,
        scene_id: Optional[UUID] = None,
    ) -> CompositionOverlay:
        """Add an overlay to the composition"""
        overlay = CompositionOverlay(
            graph_id=graph.id,
            scene_id=scene_id,
            name=name,
            overlay_type=overlay_type,
            content=content,
            position_x=position[0],
            position_y=position[1],
            width=size[0] if size else None,
            height=size[1] if size else None,
            font_family=style.get("font_family") if style else None,
            font_size=style.get("font_size") if style else None,
            font_color=style.get("color") if style else None,
            start_time=start_time,
            end_time=start_time + duration,
            duration=duration,
        )
        
        self.db.add(overlay)
        await self.db.commit()
        await self.db.refresh(overlay)
        
        # Update graph overlays list
        overlays = graph.overlays or []
        overlays.append({
            "id": str(overlay.id),
            "name": name,
            "type": overlay_type,
            "start": start_time,
            "duration": duration,
        })
        graph.overlays = overlays
        
        self.db.add(graph)
        await self.db.commit()
        
        return overlay
    
    # ==================== Scene Handlers ====================
    
    async def _handle_intro_scene(self, scene: CompositionScene) -> Dict[str, Any]:
        """Handle intro scene composition"""
        return {
            "type": "intro",
            "duration": scene.duration,
            "effects": ["fade_in", "scale_up"],
        }
    
    async def _handle_verse_scene(self, scene: CompositionScene) -> Dict[str, Any]:
        """Handle verse scene composition"""
        return {
            "type": "verse",
            "duration": scene.duration,
            "effects": [],
        }
    
    async def _handle_chorus_scene(self, scene: CompositionScene) -> Dict[str, Any]:
        """Handle chorus scene composition"""
        return {
            "type": "chorus",
            "duration": scene.duration,
            "effects": ["color_enhance", "contrast_boost"],
        }
    
    async def _handle_bridge_scene(self, scene: CompositionScene) -> Dict[str, Any]:
        """Handle bridge scene composition"""
        return {
            "type": "bridge",
            "duration": scene.duration,
            "effects": ["blur", "desaturate"],
        }
    
    async def _handle_outro_scene(self, scene: CompositionScene) -> Dict[str, Any]:
        """Handle outro scene composition"""
        return {
            "type": "outro",
            "duration": scene.duration,
            "effects": ["fade_out"],
        }
    
    async def _handle_interlude_scene(self, scene: CompositionScene) -> Dict[str, Any]:
        """Handle interlude scene composition"""
        return {
            "type": "interlude",
            "duration": scene.duration,
            "effects": ["cross_dissolve"],
        }
    
    # ==================== Execution ====================
    
    async def execute_composition(
        self,
        graph: CompositionGraph,
        output_format: str = "mp4",
        quality: str = "high",
    ) -> CompositionExecution:
        """Execute composition render"""
        # Create execution record
        execution = CompositionExecution(
            graph_id=graph.id,
            status="queued",
            format=output_format,
            quality=quality,
            total_scenes=len(graph.scenes or []),
            queued_at=datetime.utcnow(),
            correlation_id=str(uuid4()),
        )
        
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        
        # Update graph status
        graph.status = CompositionStatus.COMPOSING.value
        self.db.add(graph)
        await self.db.commit()
        
        return execution
    
    async def update_execution_progress(
        self,
        execution: CompositionExecution,
        progress: float,
        current_scene: Optional[int] = None,
    ) -> CompositionExecution:
        """Update execution progress"""
        execution.progress = progress
        execution.current_scene = current_scene
        
        if execution.status == "queued" and progress > 0:
            execution.status = "processing"
            execution.started_at = datetime.utcnow()
        
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        
        return execution
    
    async def complete_execution(
        self,
        execution: CompositionExecution,
        output_path: str,
    ) -> CompositionExecution:
        """Complete composition execution"""
        execution.status = "completed"
        execution.progress = 100.0
        execution.output_path = output_path
        execution.completed_at = datetime.utcnow()
        
        # Update graph status
        graph = await self.get_graph(execution.graph_id)
        if graph:
            graph.status = CompositionStatus.COMPLETED.value
            self.db.add(graph)
        
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        
        return execution
    
    async def fail_execution(
        self,
        execution: CompositionExecution,
        error: str,
    ) -> CompositionExecution:
        """Mark execution as failed"""
        execution.status = "failed"
        execution.error_message = error
        execution.completed_at = datetime.utcnow()
        
        # Update graph status
        graph = await self.get_graph(execution.graph_id)
        if graph:
            graph.status = CompositionStatus.FAILED.value
            self.db.add(graph)
        
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        
        return execution
    
    async def get_execution(self, execution_id: UUID) -> Optional[CompositionExecution]:
        """Get execution by ID"""
        result = await self.db.execute(
            select(CompositionExecution).where(CompositionExecution.id == execution_id)
        )
        return result.scalar_one_or_none()
    
    async def get_executions(
        self,
        graph_id: UUID,
        status: Optional[str] = None,
    ) -> List[CompositionExecution]:
        """Get executions for a graph"""
        query = select(CompositionExecution).where(CompositionExecution.graph_id == graph_id)
        
        if status:
            query = query.where(CompositionExecution.status == status)
        
        query = query.order_by(CompositionExecution.queued_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    # ==================== Export Preparation ====================
    
    async def prepare_export(
        self,
        graph: CompositionGraph,
        preset: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Prepare composition for export"""
        scenes = await self.get_scenes(graph.id)
        clips = await self.get_clips(graph.id)
        
        export_config = {
            "resolution": (graph.resolution_width, graph.resolution_height),
            "frame_rate": graph.frame_rate,
            "format": preset.get("format", "mp4"),
            "codec": preset.get("codec", "h264"),
            "bitrate": preset.get("bitrate", "5M"),
            "scenes": [
                {
                    "id": str(s.id),
                    "name": s.name,
                    "start": s.start_time,
                    "duration": s.duration,
                    "clips": [
                        c for c in clips
                        if s.start_time <= c.start_time < s.end_time
                    ],
                }
                for s in scenes
            ],
        }
        
        return export_config
    
    # ==================== Beat Alignment ====================
    
    async def generate_beat_timeline(
        self,
        bpm: float,
        duration: float,
        start_beat: int = 1,
    ) -> List[Dict[str, Any]]:
        """Generate beat-aligned timeline"""
        beat_duration = 60.0 / bpm
        beats = []
        
        beat_num = start_beat
        current_time = 0.0
        
        while current_time < duration:
            is_bar_start = (beat_num - 1) % 4 == 0
            is_downbeat = (beat_num - 1) % 8 == 0
            
            beats.append({
                "beat": beat_num,
                "timestamp": current_time,
                "strength": 1.0 if is_downbeat else 0.8 if is_bar_start else 0.5,
                "type": "downbeat" if is_downbeat else "bar" if is_bar_start else "beat",
            })
            
            beat_num += 1
            current_time = (beat_num - start_beat) * beat_duration
        
        return beats


class SceneSequencer:
    """
    Scene sequencing engine for cinematic composition.
    Handles scene ordering, transitions, and timing.
    """
    
    def __init__(self, composition_engine: CompositionEngine):
        self.engine = composition_engine
        self._sequence_cache: Dict[str, List[SceneGraph]] = {}
    
    async def build_scene_sequence(
        self,
        graph_id: UUID,
        bpm: float,
    ) -> List[SceneGraph]:
        """Build ordered scene sequence with beat markers"""
        scenes = await self.engine.get_scenes(graph_id)
        
        sequence = []
        for scene in scenes:
            beat_duration = 60.0 / bpm
            start_beat = int(scene.start_time / beat_duration) + 1
            end_beat = start_beat + int(scene.duration / beat_duration)
            
            # Generate beat markers for scene
            beats = []
            for beat in range(start_beat, end_beat + 1):
                beats.append({
                    "beat": beat,
                    "timestamp": (beat - start_beat) * beat_duration,
                    "strength": 1.0 if beat % 4 == 0 else 0.6,
                })
            
            scene_graph = SceneGraph(
                scene_id=str(scene.id),
                scene_type=SceneType(scene.scene_type),
                clips=[],  # Would be populated from clips
                start_time=scene.start_time,
                end_time=scene.end_time,
                beats=beats,
            )
            
            sequence.append(scene_graph)
        
        return sequence
    
    async def calculate_transitions(
        self,
        scenes: List[SceneGraph],
        transition_type: TransitionType = TransitionType.DISSOLVE,
    ) -> List[Dict[str, Any]]:
        """Calculate transitions between scenes"""
        transitions = []
        
        for i in range(len(scenes) - 1):
            from_scene = scenes[i]
            to_scene = scenes[i + 1]
            
            transition = {
                "from_scene": from_scene.scene_id,
                "to_scene": to_scene.scene_id,
                "type": transition_type.value,
                "start_time": from_scene.end_time,
                "duration": 0.5,  # 500ms transition
            }
            
            transitions.append(transition)
        
        return transitions