"""
Campaign and social repository
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session

from ..models.campaign import Campaign, SocialAccount, SocialPost
from .base import BaseRepository


class CampaignRepository(BaseRepository[Campaign]):
    """Campaign repository"""
    
    def __init__(self, db: Session):
        super().__init__(Campaign, db)
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 20) -> List[Campaign]:
        """Get campaigns by status"""
        return self.db.query(Campaign).filter(
            Campaign.status == status,
            Campaign.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_type(self, campaign_type: str, skip: int = 0, limit: int = 20) -> List[Campaign]:
        """Get campaigns by type"""
        return self.db.query(Campaign).filter(
            Campaign.campaign_type == campaign_type,
            Campaign.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_creator(self, created_by_id: UUID, skip: int = 0, limit: int = 20) -> List[Campaign]:
        """Get campaigns by creator"""
        return self.db.query(Campaign).filter(
            Campaign.created_by_id == created_by_id,
            Campaign.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_active(self, skip: int = 0, limit: int = 20) -> List[Campaign]:
        """Get active campaigns"""
        now = datetime.utcnow()
        return self.db.query(Campaign).filter(
            Campaign.status == "active",
            Campaign.start_date <= now,
            Campaign.end_date >= now,
            Campaign.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()


class SocialAccountRepository(BaseRepository[SocialAccount]):
    """Social account repository"""
    
    def __init__(self, db: Session):
        super().__init__(SocialAccount, db)
    
    def get_by_platform(self, platform: str, skip: int = 0, limit: int = 20) -> List[SocialAccount]:
        """Get accounts by platform"""
        return self.db.query(SocialAccount).filter(
            SocialAccount.platform == platform,
            SocialAccount.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 20) -> List[SocialAccount]:
        """Get accounts by user"""
        return self.db.query(SocialAccount).filter(
            SocialAccount.user_id == user_id,
            SocialAccount.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_artist(self, artist_id: UUID, skip: int = 0, limit: int = 20) -> List[SocialAccount]:
        """Get accounts by artist"""
        return self.db.query(SocialAccount).filter(
            SocialAccount.artist_id == artist_id,
            SocialAccount.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_active(self, skip: int = 0, limit: int = 20) -> List[SocialAccount]:
        """Get active accounts"""
        return self.db.query(SocialAccount).filter(
            SocialAccount.is_active == True,
            SocialAccount.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()


class SocialPostRepository(BaseRepository[SocialPost]):
    """Social post repository"""
    
    def __init__(self, db: Session):
        super().__init__(SocialPost, db)
    
    def get_by_account(self, account_id: UUID, skip: int = 0, limit: int = 20) -> List[SocialPost]:
        """Get posts by account"""
        return self.db.query(SocialPost).filter(
            SocialPost.account_id == account_id,
            SocialPost.deleted_at.is_(None)
        ).order_by(SocialPost.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_platform(self, platform: str, skip: int = 0, limit: int = 20) -> List[SocialPost]:
        """Get posts by platform"""
        return self.db.query(SocialPost).filter(
            SocialPost.platform == platform,
            SocialPost.deleted_at.is_(None)
        ).order_by(SocialPost.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 20) -> List[SocialPost]:
        """Get posts by status"""
        return self.db.query(SocialPost).filter(
            SocialPost.status == status,
            SocialPost.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_campaign(self, campaign_id: UUID, skip: int = 0, limit: int = 20) -> List[SocialPost]:
        """Get posts by campaign"""
        return self.db.query(SocialPost).filter(
            SocialPost.campaign_id == campaign_id,
            SocialPost.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_scheduled(self, before: datetime, limit: int = 20) -> List[SocialPost]:
        """Get scheduled posts before a given time"""
        return self.db.query(SocialPost).filter(
            SocialPost.status == "scheduled",
            SocialPost.scheduled_at <= before,
            SocialPost.deleted_at.is_(None)
        ).limit(limit).all()
    
    def get_pending(self, limit: int = 20) -> List[SocialPost]:
        """Get pending posts for publishing"""
        return self.db.query(SocialPost).filter(
            SocialPost.status == "scheduled",
            SocialPost.deleted_at.is_(None)
        ).order_by(SocialPost.scheduled_at).limit(limit).all()