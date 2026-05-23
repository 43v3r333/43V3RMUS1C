"""
Campaign, Social, and Distribution models
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class SocialPlatform(str, enum.Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"


class Campaign(BaseModel):
    """Marketing/Distribution campaign model"""
    __tablename__ = "campaigns"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    campaign_type = Column(String(50), nullable=False)  # release, promotion, awareness
    status = Column(String(50), default=CampaignStatus.DRAFT.value, index=True)
    
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    budget = Column(Integer, nullable=True)
    
    target_platforms = Column(JSON, nullable=True)  # ["instagram", "tiktok"]
    target_audience = Column(JSON, nullable=True)
    
    metadata = Column(JSON, nullable=True)
    
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", back_populates="campaigns")
    
    artist_id = Column(UUID(as_uuid=True), ForeignKey("artists.id"), nullable=True)
    artist = relationship("Artist")
    
    # Relationships
    generated_assets = relationship("GeneratedAsset", back_populates="campaign")
    social_posts = relationship("SocialPost", back_populates="campaign")


class SocialAccount(BaseModel):
    """Social media account connection model"""
    __tablename__ = "social_accounts"
    
    platform = Column(String(50), nullable=False, index=True)
    username = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=True)
    profile_url = Column(String(500), nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    
    access_token = Column(String(500), nullable=True)  # Encrypted
    refresh_token = Column(String(500), nullable=True)  # Encrypted
    token_expires_at = Column(DateTime, nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)
    
    stats = Column(JSON, nullable=True)  # {"followers": 10000, "following": 500}
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user = relationship("User")
    
    artist_id = Column(UUID(as_uuid=True), ForeignKey("artists.id"), nullable=True)
    artist = relationship("Artist")
    
    # Relationships
    posts = relationship("SocialPost", back_populates="account")


class SocialPost(BaseModel):
    """Social media post model"""
    __tablename__ = "social_posts"
    
    content = Column(Text, nullable=True)
    caption = Column(Text, nullable=True)
    
    media_urls = Column(JSON, nullable=True)
    hashtags = Column(JSON, nullable=True)
    
    platform = Column(String(50), nullable=False, index=True)
    post_type = Column(String(50), default="post")  # post, story, reel, short
    status = Column(String(50), default="draft", index=True)  # draft, scheduled, published, failed
    
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    
    external_id = Column(String(255), nullable=True)  # Platform's post ID
    external_url = Column(String(500), nullable=True)
    
    metrics = Column(JSON, nullable=True)  # {"likes": 100, "comments": 20}
    
    account_id = Column(UUID(as_uuid=True), ForeignKey("social_accounts.id"), nullable=True)
    account = relationship("SocialAccount", back_populates="posts")
    
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    campaign = relationship("Campaign", back_populates="social_posts")
    
    track_id = Column(UUID(as_uuid=True), ForeignKey("tracks.id"), nullable=True)
    track = relationship("Track")