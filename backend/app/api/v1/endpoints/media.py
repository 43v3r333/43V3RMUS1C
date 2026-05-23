"""
Media endpoints for artists, albums, tracks, projects
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.deps import get_current_active_user
from ....schemas.media import (
    ArtistCreate, ArtistUpdate, ArtistResponse,
    AlbumCreate, AlbumUpdate, AlbumResponse,
    TrackCreate, TrackUpdate, TrackResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse,
)
from ....services.media_service import (
    ArtistService, AlbumService, TrackService, ProjectService
)
from ....repositories.media_repository import (
    ArtistRepository, AlbumRepository, TrackRepository, ProjectRepository
)

router = APIRouter(prefix="/media", tags=["media"])


# Artists
@router.get("/artists", response_model=List[ArtistResponse])
async def list_artists(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    genre: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List artists with optional genre filter"""
    repo = ArtistRepository(db)
    service = ArtistService(repo)
    
    if genre:
        return repo.get_by_genre(genre, skip, limit)
    return service.get_all(skip, limit)


@router.post("/artists", response_model=ArtistResponse)
async def create_artist(
    artist_data: ArtistCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create new artist"""
    repo = ArtistRepository(db)
    service = ArtistService(repo)
    
    existing = service.get_by_slug(artist_data.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Artist with this slug already exists"
        )
    
    return service.create(artist_data)


@router.get("/artists/{artist_id}", response_model=ArtistResponse)
async def get_artist(
    artist_id: UUID,
    db: Session = Depends(get_db)
):
    """Get artist by ID"""
    repo = ArtistRepository(db)
    service = ArtistService(repo)
    
    artist = service.get_by_id(artist_id)
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found"
        )
    return artist


@router.get("/artists/slug/{slug}", response_model=ArtistResponse)
async def get_artist_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get artist by slug"""
    repo = ArtistRepository(db)
    service = ArtistService(repo)
    
    artist = service.get_by_slug(slug)
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found"
        )
    return artist


@router.put("/artists/{artist_id}", response_model=ArtistResponse)
async def update_artist(
    artist_id: UUID,
    artist_data: ArtistUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update artist"""
    repo = ArtistRepository(db)
    service = ArtistService(repo)
    
    artist = service.get_by_id(artist_id)
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found"
        )
    
    return service.update(artist, artist_data)


@router.delete("/artists/{artist_id}")
async def delete_artist(
    artist_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Delete artist (soft delete)"""
    repo = ArtistRepository(db)
    service = ArtistService(repo)
    
    artist = service.get_by_id(artist_id)
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found"
        )
    
    service.repository.delete(artist)
    return {"message": "Artist deleted successfully"}


# Albums
@router.get("/albums", response_model=List[AlbumResponse])
async def list_albums(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    artist_id: Optional[UUID] = None,
    genre: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List albums with optional filters"""
    repo = AlbumRepository(db)
    service = AlbumService(repo)
    
    if artist_id:
        return repo.get_by_artist(artist_id, skip, limit)
    if genre:
        return repo.get_by_genre(genre, skip, limit)
    return service.get_all(skip, limit)


@router.post("/albums", response_model=AlbumResponse)
async def create_album(
    album_data: AlbumCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create new album"""
    repo = AlbumRepository(db)
    service = AlbumService(repo)
    
    return service.create(album_data)


@router.get("/albums/{album_id}", response_model=AlbumResponse)
async def get_album(
    album_id: UUID,
    db: Session = Depends(get_db)
):
    """Get album by ID"""
    repo = AlbumRepository(db)
    service = AlbumService(repo)
    
    album = service.get_by_id(album_id)
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not found"
        )
    return album


@router.put("/albums/{album_id}", response_model=AlbumResponse)
async def update_album(
    album_id: UUID,
    album_data: AlbumUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update album"""
    repo = AlbumRepository(db)
    service = AlbumService(repo)
    
    album = service.get_by_id(album_id)
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not found"
        )
    
    return service.update(album, album_data)


# Tracks
@router.get("/tracks", response_model=List[TrackResponse])
async def list_tracks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    artist_id: Optional[UUID] = None,
    album_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """List tracks with optional filters"""
    repo = TrackRepository(db)
    service = TrackService(repo)
    
    if artist_id:
        return repo.get_by_artist(artist_id, skip, limit)
    if album_id:
        return repo.get_by_album(album_id, skip, limit)
    return service.get_all(skip, limit)


@router.post("/tracks", response_model=TrackResponse)
async def create_track(
    track_data: TrackCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create new track"""
    repo = TrackRepository(db)
    service = TrackService(repo)
    
    return service.create(track_data)


@router.get("/tracks/{track_id}", response_model=TrackResponse)
async def get_track(
    track_id: UUID,
    db: Session = Depends(get_db)
):
    """Get track by ID"""
    repo = TrackRepository(db)
    service = TrackService(repo)
    
    track = service.get_by_id(track_id)
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    return track


@router.put("/tracks/{track_id}", response_model=TrackResponse)
async def update_track(
    track_id: UUID,
    track_data: TrackUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update track"""
    repo = TrackRepository(db)
    service = TrackService(repo)
    
    track = service.get_by_id(track_id)
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    
    return service.update(track, track_data)


@router.post("/tracks/{track_id}/play")
async def play_track(
    track_id: UUID,
    db: Session = Depends(get_db)
):
    """Increment track play count"""
    repo = TrackRepository(db)
    service = TrackService(repo)
    
    track = service.get_by_id(track_id)
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    
    service.increment_play_count(track_id)
    return {"message": "Play count incremented"}


# Projects
@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List projects"""
    repo = ProjectRepository(db)
    service = ProjectService(repo)
    
    if status:
        return repo.get_by_status(status, skip, limit)
    return repo.get_by_owner(current_user.id, skip, limit)


@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create new project"""
    repo = ProjectRepository(db)
    service = ProjectService(repo)
    
    # Override owner_id with current user
    project_data.owner_id = current_user.id
    return service.create(project_data)


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get project by ID"""
    repo = ProjectRepository(db)
    service = ProjectService(repo)
    
    project = service.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Update project"""
    repo = ProjectRepository(db)
    service = ProjectService(repo)
    
    project = service.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return service.update(project, project_data)


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Delete project (soft delete)"""
    repo = ProjectRepository(db)
    service = ProjectService(repo)
    
    project = service.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    service.repository.delete(project)
    return {"message": "Project deleted successfully"}