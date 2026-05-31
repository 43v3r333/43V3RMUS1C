"""
Media repository for artists, albums, tracks, projects
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from ..models.media import Artist, Album, Track, Project
from .base import BaseRepository


class ArtistRepository(BaseRepository[Artist]):
    """Artist repository"""
    
    def __init__(self, db: Session):
        super().__init__(Artist, db)
    
    def get_by_slug(self, slug: str) -> Optional[Artist]:
        """Get artist by slug"""
        return self.db.query(Artist).filter(
            Artist.slug == slug,
            Artist.deleted_at.is_(None)
        ).first()
    
    def get_by_user(self, user_id: UUID) -> List[Artist]:
        """Get artists by user"""
        return self.db.query(Artist).filter(
            Artist.user_id == user_id,
            Artist.deleted_at.is_(None)
        ).all()
    
    def search(self, query: str, skip: int = 0, limit: int = 20) -> List[Artist]:
        """Search artists by name"""
        return self.db.query(Artist).filter(
            Artist.name.ilike(f"%{query}%"),
            Artist.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_genre(self, genre: str, skip: int = 0, limit: int = 20) -> List[Artist]:
        """Get artists by genre"""
        return self.db.query(Artist).filter(
            Artist.genre == genre,
            Artist.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_verified(self, skip: int = 0, limit: int = 20) -> List[Artist]:
        """Get verified artists"""
        return self.db.query(Artist).filter(
            Artist.is_verified == True,
            Artist.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()


class AlbumRepository(BaseRepository[Album]):
    """Album repository"""
    
    def __init__(self, db: Session):
        super().__init__(Album, db)
    
    def get_by_slug(self, slug: str) -> Optional[Album]:
        """Get album by slug"""
        return self.db.query(Album).filter(
            Album.slug == slug,
            Album.deleted_at.is_(None)
        ).first()
    
    def get_by_artist(self, artist_id: UUID, skip: int = 0, limit: int = 20) -> List[Album]:
        """Get albums by artist"""
        return self.db.query(Album).filter(
            Album.artist_id == artist_id,
            Album.deleted_at.is_(None)
        ).order_by(Album.release_date.desc()).offset(skip).limit(limit).all()
    
    def get_by_genre(self, genre: str, skip: int = 0, limit: int = 20) -> List[Album]:
        """Get albums by genre"""
        return self.db.query(Album).filter(
            Album.genre == genre,
            Album.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()


class TrackRepository(BaseRepository[Track]):
    """Track repository"""
    
    def __init__(self, db: Session):
        super().__init__(Track, db)
    
    def get_by_slug(self, slug: str) -> Optional[Track]:
        """Get track by slug"""
        return self.db.query(Track).filter(
            Track.slug == slug,
            Track.deleted_at.is_(None)
        ).first()
    
    def get_by_artist(self, artist_id: UUID, skip: int = 0, limit: int = 20) -> List[Track]:
        """Get tracks by artist"""
        return self.db.query(Track).filter(
            Track.artist_id == artist_id,
            Track.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_album(self, album_id: UUID, skip: int = 0, limit: int = 50) -> List[Track]:
        """Get tracks by album"""
        return self.db.query(Track).filter(
            Track.album_id == album_id,
            Track.deleted_at.is_(None)
        ).order_by(Track.track_number).offset(skip).limit(limit).all()
    
    def search(self, query: str, skip: int = 0, limit: int = 20) -> List[Track]:
        """Search tracks by title"""
        return self.db.query(Track).filter(
            or_(
                Track.title.ilike(f"%{query}%"),
                Track.genre.ilike(f"%{query}%")
            ),
            Track.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_top(self, limit: int = 20) -> List[Track]:
        """Get top tracks by play count"""
        return self.db.query(Track).filter(
            Track.deleted_at.is_(None)
        ).order_by(Track.play_count.desc()).limit(limit).all()
    
    def increment_play_count(self, track_id: UUID) -> None:
        """Increment track play count"""
        self.db.query(Track).filter(Track.id == track_id).update(
            {Track.play_count: Track.play_count + 1}
        )
        self.db.commit()


class ProjectRepository(BaseRepository[Project]):
    """Project repository"""
    
    def __init__(self, db: Session):
        super().__init__(Project, db)
    
    def get_by_owner(self, owner_id: UUID, skip: int = 0, limit: int = 20) -> List[Project]:
        """Get projects by owner"""
        return self.db.query(Project).filter(
            Project.owner_id == owner_id,
            Project.deleted_at.is_(None)
        ).order_by(Project.updated_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 20) -> List[Project]:
        """Get projects by status"""
        return self.db.query(Project).filter(
            Project.status == status,
            Project.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_artist(self, artist_id: UUID, skip: int = 0, limit: int = 20) -> List[Project]:
        """Get projects by artist"""
        return self.db.query(Project).filter(
            Project.artist_id == artist_id,
            Project.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def search(self, query: str, skip: int = 0, limit: int = 20) -> List[Project]:
        """Search projects by name"""
        return self.db.query(Project).filter(
            or_(
                Project.name.ilike(f"%{query}%"),
                Project.description.ilike(f"%{query}%")
            ),
            Project.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()