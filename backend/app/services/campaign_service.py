"""
Campaign and social services
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from ..models.campaign import Campaign, SocialAccount, SocialPost
from ..schemas.campaign import (
    CampaignCreate, CampaignUpdate,
    SocialAccountCreate, SocialAccountUpdate,
    SocialPostCreate, SocialPostUpdate,
)
from ..repositories.campaign_repository import CampaignRepository, SocialAccountRepository, SocialPostRepository
from .base import BaseService


class CampaignService(BaseService[Campaign]):
    """Campaign service"""
    
    def __init__(self, repository: CampaignRepository):
        super().__init__(repository)
        self.repo = repository
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 20) -> List[Campaign]:
        """Get campaigns by status"""
        return self.repo.get_by_status(status, skip, limit)
    
    def get_by_creator(self, created_by_id: UUID, skip: int = 0, limit: int = 20) -> List[Campaign]:
        """Get campaigns by creator"""
        return self.repo.get_by_creator(created_by_id, skip, limit)
    
    def get_active(self, skip: int = 0, limit: int = 20) -> List[Campaign]:
        """Get active campaigns"""
        return self.repo.get_active(skip, limit)
    
    def create(self, campaign_data: CampaignCreate) -> Campaign:
        """Create new campaign"""
        campaign = Campaign(
            name=campaign_data.name,
            description=campaign_data.description,
            campaign_type=campaign_data.campaign_type,
            start_date=campaign_data.start_date,
            end_date=campaign_data.end_date,
            budget=campaign_data.budget,
            target_platforms=campaign_data.target_platforms,
            target_audience=campaign_data.target_audience,
            created_by_id=campaign_data.created_by_id,
            artist_id=campaign_data.artist_id,
        )
        return self.repo.create(campaign)
    
    def update(self, campaign: Campaign, campaign_data: CampaignUpdate) -> Campaign:
        """Update campaign"""
        update_data = campaign_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(campaign, field):
                setattr(campaign, field, value)
        return self.repo.update(campaign)
    
    def activate(self, campaign: Campaign) -> Campaign:
        """Activate campaign"""
        campaign.status = "active"
        return self.repo.update(campaign)
    
    def pause(self, campaign: Campaign) -> Campaign:
        """Pause campaign"""
        campaign.status = "paused"
        return self.repo.update(campaign)


class SocialAccountService(BaseService[SocialAccount]):
    """Social account service"""
    
    def __init__(self, repository: SocialAccountRepository):
        super().__init__(repository)
        self.repo = repository
    
    def get_by_platform(self, platform: str, skip: int = 0, limit: int = 20) -> List[SocialAccount]:
        """Get accounts by platform"""
        return self.repo.get_by_platform(platform, skip, limit)
    
    def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 20) -> List[SocialAccount]:
        """Get accounts by user"""
        return self.repo.get_by_user(user_id, skip, limit)
    
    def create(self, account_data: SocialAccountCreate) -> SocialAccount:
        """Create new social account"""
        account = SocialAccount(
            platform=account_data.platform,
            username=account_data.username,
            display_name=account_data.display_name,
            profile_url=account_data.profile_url,
            access_token=account_data.access_token,
            refresh_token=account_data.refresh_token,
            token_expires_at=account_data.token_expires_at,
            user_id=account_data.user_id,
            artist_id=account_data.artist_id,
        )
        return self.repo.create(account)
    
    def update(self, account: SocialAccount, account_data: SocialAccountUpdate) -> SocialAccount:
        """Update social account"""
        update_data = account_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(account, field):
                setattr(account, field, value)
        return self.repo.update(account)


class SocialPostService(BaseService[SocialPost]):
    """Social post service"""
    
    def __init__(self, repository: SocialPostRepository):
        super().__init__(repository)
        self.repo = repository
    
    def get_by_account(self, account_id: UUID, skip: int = 0, limit: int = 20) -> List[SocialPost]:
        """Get posts by account"""
        return self.repo.get_by_account(account_id, skip, limit)
    
    def get_by_platform(self, platform: str, skip: int = 0, limit: int = 20) -> List[SocialPost]:
        """Get posts by platform"""
        return self.repo.get_by_platform(platform, skip, limit)
    
    def get_by_campaign(self, campaign_id: UUID, skip: int = 0, limit: int = 20) -> List[SocialPost]:
        """Get posts by campaign"""
        return self.repo.get_by_campaign(campaign_id, skip, limit)
    
    def get_pending(self, limit: int = 20) -> List[SocialPost]:
        """Get pending posts for publishing"""
        return self.repo.get_pending(limit)
    
    def create(self, post_data: SocialPostCreate) -> SocialPost:
        """Create new social post"""
        post = SocialPost(
            content=post_data.content,
            caption=post_data.caption,
            media_urls=post_data.media_urls,
            hashtags=post_data.hashtags,
            platform=post_data.platform,
            post_type=post_data.post_type,
            account_id=post_data.account_id,
            campaign_id=post_data.campaign_id,
            track_id=post_data.track_id,
            scheduled_at=post_data.scheduled_at,
        )
        return self.repo.create(post)
    
    def schedule(self, post: SocialPost, scheduled_at: datetime) -> SocialPost:
        """Schedule a post"""
        post.status = "scheduled"
        post.scheduled_at = scheduled_at
        return self.repo.update(post)
    
    def publish(self, post: SocialPost, external_id: str, external_url: str) -> SocialPost:
        """Mark post as published"""
        post.status = "published"
        post.published_at = datetime.utcnow()
        post.external_id = external_id
        post.external_url = external_url
        return self.repo.update(post)
    
    def fail(self, post: SocialPost, error: str) -> SocialPost:
        """Mark post as failed"""
        post.status = "failed"
        return self.repo.update(post)