"""
Media services for artists, albums, tracks, projects
"""
from typing import Optional, List
from uuid import UUID

from ..models.media import Artist, Album, Track, Project
from ..schemas.media import ArtistCreate, ArtistUpdate, AlbumCreate, AlbumUpdate, TrackCreate, TrackUpdate, ProjectCreate, ProjectUpdate
from ..repositories.media_repository import ArtistRepository, AlbumRepository, TrackRepository, ProjectRepository
from .base import BaseService


class ArtistService(BaseService[Artist]):
    """Artist service"""
    
    def __init__(self, repository: ArtistRepository):
        super().__init__(repository)
        self.repo = repository
    
    def get_by_slug(self, slug: str) -> Optional[Artist]:
        """Get artist by slug"""
        return self.repo.get_by_slug(slug)
    
    def get_by_user(self, user_id: UUID) -> List[Artist]:
        """Get artists by user"""
        return self.repo.get_by_user(user_id)
    
    def create(self, artist_data: ArtistCreate) -> Artist:
        """Create new artist"""
        artist = Artist(
            name=artist_data.name,
            slug=artist_data.slug,
            bio=artist_data.bio,
            image_url=artist_data.image_url,
            social_links=artist_data.social_links,
            genre=artist_data.genre,
            label=artist_data.label,
            website=artist_data.website,
            user_id=artist_data.user_id,
        )
        return self.repo.create(artist)
    
    def update(self, artist: Artist, artist_data: ArtistUpdate) -> Artist:
        """Update artist"""
        update_data = artist_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(artist, field):
                setattr(artist, field, value)
        return self.repo.update(artist)
    
    def verify(self, artist: Artist) -> Artist:
        """Mark artist as verified"""
        artist.is_verified = True
        return self.repo.update(artist)


class AlbumService(BaseService[Album]):
    """Album service"""
    
    def __init__(self, repository: AlbumRepository):
        super().__init__(repository)
        self.repo = repository
    
    def get_by_slug(self, slug: str) -> Optional[Album]:
        """Get album by slug"""
        return self.repo.get_by_slug(slug)
    
    def get_by_artist(self, artist_id: UUID, skip: int = 0, limit: int = 20) -> List[Album]:
        """Get albums by artist"""
        return self.repo.get_by_artist(artist_id, skip, limit)
    
    def create(self, album_data: AlbumCreate) -> Album:
        """Create new album"""
        album = Album(
            title=album_data.title,
            slug=album_data.slug,
            description=album_data.description,
            cover_url=album_data.cover_url,
            release_date=album_data.release_date,
            genre=album_data.genre,
            label=album_data.label,
            total_tracks=album_data.total_tracks,
            total_duration=album_data.total_duration,
            is_single=album_data.is_single,
            artist_id=album_data.artist_id,
        )
        return self.repo.create(album)
    
    def update(self, album: Album, album_data: AlbumUpdate) -> Album:
        """Update album"""
        update_data = album_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(album, field):
                setattr(album, field, value)
        return self.repo.update(album)


class TrackService(BaseService[Track]):
    """Track service"""
    
    def __init__(self, repository: TrackRepository):
        super().__init__(repository)
        self.repo = repository
    
    def get_by_slug(self, slug: str) -> Optional[Track]:
        """Get track by slug"""
        return self.repo.get_by_slug(slug)
    
    def get_by_artist(self, artist_id: UUID, skip: int = 0, limit: int = 20) -> List[Track]:
        """Get tracks by artist"""
        return self.repo.get_by_artist(artist_id, skip, limit)
    
    def get_by_album(self, album_id: UUID, skip: int = 0, limit: int = 50) -> List[Track]:
        """Get tracks by album"""
        return self.repo.get_by_album(album_id, skip, limit)
    
    def create(self, track_data: TrackCreate) -> Track:
        """Create new track"""
        track = Track(
            title=track_data.title,
            slug=track_data.slug,
            description=track_data.description,
            duration=track_data.duration,
            track_number=track_data.track_number,
            bpm=track_data.bpm,
            key_signature=track_data.key_signature,
            explicit=track_data.explicit,
            audio_url=track_data.audio_url,
            waveform_url=track_data.waveform_url,
            genre=track_data.genre,
            mood=track_data.mood,
            tags=track_data.tags,
            artist_id=track_data.artist_id,
            album_id=track_data.album_id,
        )
        return self.repo.create(track)
    
    def update(self, track: Track, track_data: TrackUpdate) -> Track:
        """Update track"""
        update_data = track_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(track, field):
                setattr(track, field, value)
        return self.repo.update(track)
    
    def increment_play_count(self, track_id: UUID) -> None:
        """Increment play count"""
        self.repo.increment_play_count(track_id)


class ProjectService(BaseService[Project]):
    """Project service"""
    
    def __init__(self, repository: ProjectRepository):
        super().__init__(repository)
        self.repo = repository
    
    def get_by_owner(self, owner_id: UUID, skip: int = 0, limit: int = 20) -> List[Project]:
        """Get projects by owner"""
        return self.repo.get_by_owner(owner_id, skip, limit)
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 20) -> List[Project]:
        """Get projects by status"""
        return self.repo.get_by_status(status, skip, limit)
    
    def create(self, project_data: ProjectCreate) -> Project:
        """Create new project"""
        project = Project(
            name=project_data.name,
            description=project_data.description,
            status=project_data.status,
            project_type=project_data.project_type,
            cover_url=project_data.cover_url,
            metadata_dict=project_data.metadata,
            owner_id=project_data.owner_id,
            artist_id=project_data.artist_id,
        )
        return self.repo.create(project)
    
    def update(self, project: Project, project_data: ProjectUpdate) -> Project:
        """Update project"""
        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(project, field):
                setattr(project, field, value)
        return self.repo.update(project)