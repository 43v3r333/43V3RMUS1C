"""
Campaign models: Campaign, SocialAccount, SocialPost
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Campaign(BaseModel):
    """Campaign model for marketing and distribution"""
    
    __tablename__ = "campaigns"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    campaign_type = Column(String(50), nullable=False)  # release, marketing, promotion
    status = Column(String(50), default="draft", index=True)  # draft, scheduled, active, paused, completed
    
    # Scheduling
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Budget
    budget = Column(Integer, nullable=True)
    
    # Targeting
    target_platforms = Column(JSON, nullable=True)  # ["instagram", "youtube"]
    target_audience = Column(JSON, nullable=True)
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    
    # Ownership
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    artist_id = Column(UUID(as_uuid=True), ForeignKey("artists.id"), nullable=True)
    
    # Relationships
    generated_assets = relationship("GeneratedAsset", back_populates="campaign", lazy="selectin")
    social_posts = relationship("SocialPost", back_populates="campaign", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<Campaign(id={self.id}, name={self.name})>"


class SocialAccount(BaseModel):
    """Social account model for platform connections"""
    
    __tablename__ = "social_accounts"
    
    platform = Column(String(50), nullable=False, index=True)  # instagram, youtube, twitter, spotify
    username = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=True)
    profile_url = Column(String(500), nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    
    # OAuth tokens
    access_token = Column(String(500), nullable=True)
    refresh_token = Column(String(500), nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)
    
    # Statistics
    stats = Column(JSON, nullable=True)  # follower count, etc.
    
    # Ownership
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    artist_id = Column(UUID(as_uuid=True), ForeignKey("artists.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="social_accounts", lazy="selectin")
    posts = relationship("SocialPost", back_populates="account", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<SocialAccount(id={self.id}, platform={self.platform}, username={self.username})>"


class SocialPost(BaseModel):
    """Social post model for content publishing"""
    
    __tablename__ = "social_posts"
    
    content = Column(Text, nullable=True)
    caption = Column(Text, nullable=True)
    media_urls = Column(JSON, nullable=True)
    hashtags = Column(JSON, nullable=True)
    
    platform = Column(String(50), nullable=False, index=True)
    post_type = Column(String(50), default="post")  # post, story, reel, video
    status = Column(String(50), default="draft", index=True)  # draft, scheduled, published, failed
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    
    # External reference
    external_id = Column(String(255), nullable=True)
    external_url = Column(String(500), nullable=True)
    
    # Performance metrics
    metrics = Column(JSON, nullable=True)  # likes, comments, shares, views
    
    # Ownership
    account_id = Column(UUID(as_uuid=True), ForeignKey("social_accounts.id"), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    track_id = Column(UUID(as_uuid=True), ForeignKey("tracks.id"), nullable=True)
    
    # Relationships
    account = relationship("SocialAccount", back_populates="posts", lazy="selectin")
    campaign = relationship("Campaign", back_populates="social_posts", lazy="selectin")
    track = relationship("Track", back_populates="social_posts", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<SocialPost(id={self.id}, platform={self.platform}, status={self.status})>"