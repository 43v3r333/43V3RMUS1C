"""
Render queue and timeline API endpoints.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.core.database import get_async_db
from app.services.render_service import RenderQueueService, ExportService
from app.services.timeline_service import TimelineService
from app.schemas.media_schema import (
    RenderJobResponse,
    RenderJobCreate,
    RenderQueueStats,
    ExportPresetResponse,
    TimelineResponse,
    TimelineCreate,
    TimelineUpdate,
    TimelineClipCreate,
    TimelineClipUpdate
)
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/render", tags=["render"])


@router.get("/jobs", response_model=List[RenderJobResponse])
async def list_render_jobs(
    status: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """List render jobs with filters"""
    service = RenderQueueService(db)
    
    project_uuid = uuid.UUID(project_id) if project_id else None
    
    jobs = service.list_jobs(
        status=status,
        job_type=job_type,
        project_id=project_uuid,
        limit=limit,
        offset=offset
    )
    
    return [RenderJobResponse.model_validate(j) for j in jobs]


@router.post("/jobs", response_model=RenderJobResponse)
async def create_render_job(
    job: RenderJobCreate,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new render job"""
    service = RenderQueueService(db)
    
    project_uuid = job.project_id if job.project_id else None
    
    created_job = service.create_render_job(
        name=job.name,
        job_type=job.job_type,
        input_path=job.input_path,
        output_path=job.output_path,
        parameters=job.parameters,
        priority=job.priority,
        project_id=project_uuid
    )
    
    return RenderJobResponse.model_validate(created_job)


@router.get("/jobs/stats", response_model=RenderQueueStats)
async def get_queue_stats(
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get render queue statistics"""
    service = RenderQueueService(db)
    stats = service.get_queue_stats()
    return RenderQueueStats(**stats)


@router.get("/jobs/{job_id}", response_model=RenderJobResponse)
async def get_render_job(
    job_id: str = Path(...),
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific render job"""
    service = RenderQueueService(db)
    
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    job = service.get_job(job_uuid)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return RenderJobResponse.model_validate(job)


@router.post("/jobs/{job_id}/cancel")
async def cancel_render_job(
    job_id: str,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a queued or processing job"""
    service = RenderQueueService(db)
    
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    try:
        job = service.cancel_job(job_uuid)
        return {"status": "cancelled", "job_id": str(job.id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/jobs/{job_id}/retry")
async def retry_render_job(
    job_id: str,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Retry a failed job"""
    service = RenderQueueService(db)
    
    try:
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    try:
        job = service.retry_job(job_uuid)
        return {"status": "queued", "job_id": str(job.id), "retry_count": job.retry_count}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Export presets
export_router = APIRouter(prefix="/export", tags=["export"])


@export_router.get("/presets", response_model=List[ExportPresetResponse])
async def list_export_presets(
    platform: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """List export presets"""
    service = ExportService(db)
    presets = service.list_presets(platform=platform, category=category)
    return [ExportPresetResponse.model_validate(p) for p in presets]


@export_router.get("/presets/{preset_id}", response_model=ExportPresetResponse)
async def get_export_preset(
    preset_id: str,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific export preset"""
    service = ExportService(db)
    
    try:
        preset_uuid = uuid.UUID(preset_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid preset ID format")
    
    preset = service.get_preset(preset_uuid)
    
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    
    return ExportPresetResponse.model_validate(preset)


@export_router.get("/platforms")
async def get_supported_platforms(
    current_user: User = Depends(get_current_user)
):
    """Get list of supported export platforms"""
    return {
        "platforms": ["tiktok", "youtube_shorts", "instagram_reels", "twitter", "facebook", "linkedin"]
    }


# Timeline endpoints
timeline_router = APIRouter(prefix="/timelines", tags=["timeline"])


@timeline_router.get("", response_model=List[TimelineResponse])
async def list_timelines(
    project_id: Optional[str] = Query(None),
    is_published: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """List timelines"""
    service = TimelineService(db)
    
    project_uuid = uuid.UUID(project_id) if project_id else None
    
    timelines = service.list_timelines(
        project_id=project_uuid,
        is_published=is_published,
        limit=limit
    )
    
    return [TimelineResponse.model_validate(t) for t in timelines]


@timeline_router.post("", response_model=TimelineResponse)
async def create_timeline(
    timeline: TimelineCreate,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new timeline"""
    service = TimelineService(db)
    
    project_uuid = timeline.project_id if timeline.project_id else None
    
    created = service.create_timeline(
        name=timeline.name,
        description=timeline.description,
        project_id=project_uuid,
        created_by_id=current_user.id,
        frame_rate=timeline.frame_rate,
        resolution_width=timeline.resolution_width,
        resolution_height=timeline.resolution_height,
        aspect_ratio=timeline.aspect_ratio
    )
    
    return TimelineResponse.model_validate(created)


@timeline_router.get("/{timeline_id}", response_model=TimelineResponse)
async def get_timeline(
    timeline_id: str,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get timeline with all tracks and clips"""
    service = TimelineService(db)
    
    try:
        timeline_uuid = uuid.UUID(timeline_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timeline ID format")
    
    timeline = service.get_timeline(timeline_uuid)
    
    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")
    
    return TimelineResponse.model_validate(timeline)


@timeline_router.patch("/{timeline_id}", response_model=TimelineResponse)
async def update_timeline(
    timeline_id: str,
    updates: TimelineUpdate,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Update timeline properties"""
    service = TimelineService(db)
    
    try:
        timeline_uuid = uuid.UUID(timeline_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timeline ID format")
    
    try:
        timeline = service.update_timeline(timeline_uuid, updates.model_dump(exclude_unset=True))
        return TimelineResponse.model_validate(timeline)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@timeline_router.delete("/{timeline_id}")
async def delete_timeline(
    timeline_id: str,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a timeline"""
    service = TimelineService(db)
    
    try:
        timeline_uuid = uuid.UUID(timeline_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timeline ID format")
    
    success = service.delete_timeline(timeline_uuid)
    
    if not success:
        raise HTTPException(status_code=404, detail="Timeline not found")
    
    return {"status": "deleted"}


@timeline_router.post("/{timeline_id}/render")
async def render_timeline(
    timeline_id: str,
    preset_id: Optional[str] = Query(None),
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Render timeline to video file"""
    service = TimelineService(db)
    
    try:
        timeline_uuid = uuid.UUID(timeline_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timeline ID format")
    
    # Get preset if specified
    preset = None
    if preset_id:
        export_service = ExportService(db)
        try:
            preset_uuid = uuid.UUID(preset_id)
            preset = export_service.get_preset(preset_uuid)
        except ValueError:
            pass
    
    # Render timeline
    success, result = service.render_timeline(timeline_uuid, preset)
    
    if success:
        return {
            "status": "completed",
            "output_path": result
        }
    else:
        raise HTTPException(status_code=500, detail=result)


# Clip endpoints under timeline
@timeline_router.post("/{timeline_id}/clips", response_model=dict)
async def add_clip(
    timeline_id: str,
    clip: TimelineClipCreate,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Add a clip to timeline"""
    service = TimelineService(db)
    
    try:
        timeline_uuid = uuid.UUID(timeline_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timeline ID format")
    
    created = service.add_clip(
        track_id=clip.track_id,
        asset_id=clip.asset_id,
        timeline_start=clip.timeline_start,
        timeline_end=clip.timeline_end,
        source_start=clip.source_start,
        source_end=clip.source_end,
        name=clip.name
    )
    
    return {
        "id": str(created.id),
        "track_id": str(created.track_id),
        "timeline_start": created.timeline_start,
        "timeline_end": created.timeline_end
    }


@timeline_router.patch("/{timeline_id}/clips/{clip_id}")
async def update_clip(
    timeline_id: str,
    clip_id: str,
    updates: TimelineClipUpdate,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Update a clip on the timeline"""
    service = TimelineService(db)
    
    try:
        clip_uuid = uuid.UUID(clip_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid clip ID format")
    
    try:
        clip = service.update_clip(clip_uuid, updates.model_dump(exclude_unset=True))
        return {"id": str(clip.id), "status": "updated"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@timeline_router.delete("/{timeline_id}/clips/{clip_id}")
async def delete_clip(
    timeline_id: str,
    clip_id: str,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a clip from timeline"""
    service = TimelineService(db)
    
    try:
        clip_uuid = uuid.UUID(clip_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid clip ID format")
    
    success = service.delete_clip(clip_uuid)
    
    if not success:
        raise HTTPException(status_code=404, detail="Clip not found")
    
    return {"status": "deleted"}