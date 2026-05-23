"""
Campaign, Social Account, and Social Post endpoints
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_async_db, get_current_user
from app.models.user import User
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse,
    SocialAccountCreate, SocialAccountUpdate, SocialAccountResponse,
    SocialPostCreate, SocialPostUpdate, SocialPostResponse,
)
from app.schemas.base import PaginatedResponse
from app.models.campaign import Campaign, SocialAccount, SocialPost
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)

# ============ Campaign Endpoints ============

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[CampaignResponse])
async def list_campaigns(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    campaign_type: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """List all campaigns"""
    repo = BaseRepository(Campaign, db)
    filters = {}
    if status:
        filters["status"] = status
    if campaign_type:
        filters["campaign_type"] = campaign_type
    campaigns, total = await repo.paginate(page, per_page, filters=filters if filters else None)
    return PaginatedResponse.create(campaigns, total, page, per_page)


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    data: CampaignCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Create new campaign"""
    campaign = Campaign(**data.model_dump(), created_by_id=current_user.id)
    repo = BaseRepository(Campaign, db)
    campaign = await repo.create(campaign)
    logger.info(f"Campaign created: {campaign.name}")
    return campaign


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Get campaign by ID"""
    repo = BaseRepository(Campaign, db)
    campaign = await repo.get_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    data: CampaignUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Update campaign"""
    repo = BaseRepository(Campaign, db)
    campaign = await repo.get_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(campaign, key, value)
    
    campaign = await repo.update(campaign)
    return campaign


# ============ Social Account Endpoints ============

social_accounts_router = APIRouter()


@social_accounts_router.get("/", response_model=PaginatedResponse[SocialAccountResponse])
async def list_social_accounts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    platform: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """List social accounts for current user"""
    repo = BaseRepository(SocialAccount, db)
    filters = {"user_id": str(current_user.id)}
    if platform:
        filters["platform"] = platform
    if is_active is not None:
        filters["is_active"] = is_active
    accounts, total = await repo.paginate(page, per_page, filters=filters)
    return PaginatedResponse.create(accounts, total, page, per_page)


@social_accounts_router.post("/", response_model=SocialAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_social_account(
    data: SocialAccountCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Connect a new social account"""
    account = SocialAccount(**data.model_dump(), user_id=current_user.id)
    repo = BaseRepository(SocialAccount, db)
    account = await repo.create(account)
    logger.info(f"Social account connected: {account.platform}")
    return account


@social_accounts_router.get("/{account_id}", response_model=SocialAccountResponse)
async def get_social_account(
    account_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Get social account by ID"""
    repo = BaseRepository(SocialAccount, db)
    account = await repo.get_by_id(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Social account not found")
    return account


@social_accounts_router.patch("/{account_id}", response_model=SocialAccountResponse)
async def update_social_account(
    account_id: str,
    data: SocialAccountUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Update social account"""
    repo = BaseRepository(SocialAccount, db)
    account = await repo.get_by_id(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Social account not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(account, key, value)
    
    account = await repo.update(account)
    return account


@social_accounts_router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_social_account(
    account_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Disconnect a social account"""
    repo = BaseRepository(SocialAccount, db)
    account = await repo.get_by_id(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Social account not found")
    
    await repo.delete(account)
    return None


# ============ Social Post Endpoints ============

social_posts_router = APIRouter()


@social_posts_router.get("/", response_model=PaginatedResponse[SocialPostResponse])
async def list_social_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    platform: Optional[str] = None,
    campaign_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """List social posts"""
    repo = BaseRepository(SocialPost, db)
    filters = {}
    if status:
        filters["status"] = status
    if platform:
        filters["platform"] = platform
    if campaign_id:
        filters["campaign_id"] = campaign_id
    posts, total = await repo.paginate(page, per_page, filters=filters if filters else None)
    return PaginatedResponse.create(posts, total, page, per_page)


@social_posts_router.post("/", response_model=SocialPostResponse, status_code=status.HTTP_201_CREATED)
async def create_social_post(
    data: SocialPostCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new social post"""
    post = SocialPost(**data.model_dump())
    repo = BaseRepository(SocialPost, db)
    post = await repo.create(post)
    logger.info(f"Social post created: {post.platform}")
    return post


@social_posts_router.get("/{post_id}", response_model=SocialPostResponse)
async def get_social_post(
    post_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Get social post by ID"""
    repo = BaseRepository(SocialPost, db)
    post = await repo.get_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Social post not found")
    return post


@social_posts_router.patch("/{post_id}", response_model=SocialPostResponse)
async def update_social_post(
    post_id: str,
    data: SocialPostUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Update social post"""
    repo = BaseRepository(SocialPost, db)
    post = await repo.get_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Social post not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(post, key, value)
    
    post = await repo.update(post)
    return post


@social_posts_router.post("/{post_id}/publish")
async def publish_social_post(
    post_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Publish a social post to the platform"""
    repo = BaseRepository(SocialPost, db)
    post = await repo.get_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Social post not found")
    
    # Update status to scheduled for now (actual publishing would be done by a worker)
    post.status = "scheduled"
    post = await repo.update(post)
    
    logger.info(f"Social post scheduled for publishing: {post_id}")
    return post