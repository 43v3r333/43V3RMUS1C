"""
Rendering Domain Models - Distributed render graph orchestration
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, JSON, Text, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ...models.base import BaseModel


class RenderStatus(str, Enum):
    """Render job status"""
    QUEUED = "queued"
    PREPARING = "preparing"
    RENDERING = "rendering"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class RenderPriority(str, Enum):
    """Render job priority"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class RenderNodeType(str, Enum):
    """Render node types"""
    SOURCE = "source"
    PROCESSOR = "processor"
    COMPOSITOR = "compositor"
    ENCODER = "encoder"
    DESTINATION = "destination"


@dataclass
class RenderPort:
    """Render port definition"""
    name: str
    port_type: str
    data_format: Optional[str] = None
    required: bool = True


@dataclass
class RenderNodeConfig:
    """Node configuration"""
    node_type: RenderNodeType
    name: str
    input_ports: List[RenderPort] = field(default_factory=list)
    output_ports: List[RenderPort] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)


class RenderGraph(BaseModel):
    """Render graph model"""
    __tablename__ = "render_graphs"

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    nodes = Column(JSON, nullable=False)
    edges = Column(JSON, nullable=False)
    
    status = Column(String(50), default="draft")
    version = Column(String(20), default="1.0.0")

    project_id = Column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)


class RenderNode(BaseModel):
    """Render node instance"""
    __tablename__ = "render_nodes"

    node_id = Column(String(100), nullable=False, index=True)
    graph_id = Column(PGUUID(as_uuid=True), ForeignKey("render_graphs.id"), nullable=False, index=True)
    
    node_type = Column(String(50), nullable=False)
    config = Column(JSON, nullable=False)
    
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    
    status = Column(String(50), default="pending")
    error_message = Column(Text, nullable=True)


# RenderJob is now imported from models.workflow to avoid duplicate table registration
# This stub class prevents import errors if something tries to import it from here
class RenderJob:
    """DEPRECATED: RenderJob has moved to models.workflow
    
    This class exists only to prevent ImportErrors.
    Use: from models.workflow import RenderJob
    """
    __table__ = None
    
    def __init__(self, *args, **kwargs):
        raise RuntimeError(
            "RenderJob is no longer in domains/rendering/models.py. "
            "Import from models.workflow instead: from models.workflow import RenderJob"
        )


class RenderPreset(BaseModel):
    """Render preset configuration"""
    __tablename__ = "render_presets"

    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    preset_type = Column(String(50), nullable=False)
    config = Column(JSON, nullable=False)
    
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)

    created_by_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)