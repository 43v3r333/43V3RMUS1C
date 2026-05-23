"""
Media endpoints (Artists, Albums, Tracks, Projects)
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_async_db, get_current_user
from app.models.user import User
from app.schemas.media import (
    ArtistCreate, ArtistUpdate, ArtistResponse,
    AlbumCreate, AlbumUpdate, AlbumResponse,
    TrackCreate, TrackUpdate, TrackResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse,
)
from app.schemas.base import PaginatedResponse
from app.models.media import Artist, Album, Track, Project
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)

router = APIRouter()

# ============ Artist Endpoints ============

@router.get("/artists", response_model=PaginatedResponse[ArtistResponse])
async def list_artists(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """List all artists"""
    repo = BaseRepository(Artist, db)
    artists, total = await repo.paginate(page, per_page)
    return PaginatedResponse.create(artists, total, page, per_page)


@router.post("/artists", response_model=ArtistResponse, status_code=status.HTTP_201_CREATED)
async def create_artist(
    data: ArtistCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Create new artist"""
    artist = Artist(**data.model_dump())
    repo = BaseRepository(Artist, db)
    artist = await repo.create(artist)
    logger.info(f"Artist created: {artist.name}")
    return artist


@router.get("/artists/{artist_id}", response_model=ArtistResponse)
async def get_artist(
    artist_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Get artist by ID"""
    repo = BaseRepository(Artist, db)
    artist = await repo.get_by_id(artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist


@router.patch("/artists/{artist_id}", response_model=ArtistResponse)
async def update_artist(
    artist_id: str,
    data: ArtistUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Update artist"""
    repo = BaseRepository(Artist, db)
    artist = await repo.get_by_id(artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(artist, key, value)
    
    artist = await repo.update(artist)
    return artist


# ============ Album Endpoints ============

@router.get("/albums", response_model=PaginatedResponse[AlbumResponse])
async def list_albums(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    artist_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """List all albums"""
    repo = BaseRepository(Album, db)
    filters = {"artist_id": artist_id} if artist_id else None
    albums, total = await repo.paginate(page, per_page, filters=filters)
    return PaginatedResponse.create(albums, total, page, per_page)


@router.post("/albums", response_model=AlbumResponse, status_code=status.HTTP_201_CREATED)
async def create_album(
    data: AlbumCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Create new album"""
    album = Album(**data.model_dump())
    repo = BaseRepository(Album, db)
    album = await repo.create(album)
    logger.info(f"Album created: {album.title}")
    return album


@router.get("/albums/{album_id}", response_model=AlbumResponse)
async def get_album(
    album_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Get album by ID"""
    repo = BaseRepository(Album, db)
    album = await repo.get_by_id(album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    return album


# ============ Track Endpoints ============

@router.get("/tracks", response_model=PaginatedResponse[TrackResponse])
async def list_tracks(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    artist_id: Optional[str] = None,
    album_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """List all tracks"""
    repo = BaseRepository(Track, db)
    filters = {}
    if artist_id:
        filters["artist_id"] = artist_id
    if album_id:
        filters["album_id"] = album_id
    tracks, total = await repo.paginate(page, per_page, filters=filters if filters else None)
    return PaginatedResponse.create(tracks, total, page, per_page)


@router.post("/tracks", response_model=TrackResponse, status_code=status.HTTP_201_CREATED)
async def create_track(
    data: TrackCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Create new track"""
    track = Track(**data.model_dump())
    repo = BaseRepository(Track, db)
    track = await repo.create(track)
    logger.info(f"Track created: {track.title}")
    return track


@router.get("/tracks/{track_id}", response_model=TrackResponse)
async def get_track(
    track_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Get track by ID"""
    repo = BaseRepository(Track, db)
    track = await repo.get_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track


# ============ Project Endpoints ============

@router.get("/projects", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    owner_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """List all projects"""
    repo = BaseRepository(Project, db)
    filters = {}
    if status:
        filters["status"] = status
    if owner_id:
        filters["owner_id"] = owner_id
    projects, total = await repo.paginate(page, per_page, filters=filters if filters else None)
    return PaginatedResponse.create(projects, total, page, per_page)


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Create new project"""
    project = Project(**data.model_dump(), owner_id=current_user.id)
    repo = BaseRepository(Project, db)
    project = await repo.create(project)
    logger.info(f"Project created: {project.name}")
    return project


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Get project by ID"""
    repo = BaseRepository(Project, db)
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Update project"""
    repo = BaseRepository(Project, db)
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    
    project = await repo.update(project)
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Delete project (soft delete)"""
    repo = BaseRepository(Project, db)
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await repo.delete(project)
    logger.info(f"Project deleted: {project_id}")
    return None