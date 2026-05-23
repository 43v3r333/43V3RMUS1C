"""
Pydantic schemas package initialization
"""
from app.schemas.base import (
    BaseSchema,
    BaseResponse,
    PaginatedResponse,
    ErrorResponse,
)
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    TokenResponse,
    RoleCreate,
    RoleResponse,
)
from app.schemas.media import (
    ArtistCreate,
    ArtistUpdate,
    ArtistResponse,
    AlbumCreate,
    AlbumUpdate,
    AlbumResponse,
    TrackCreate,
    TrackUpdate,
    TrackResponse,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)
from app.schemas.asset import (
    MediaAssetCreate,
    MediaAssetUpdate,
    MediaAssetResponse,
    GeneratedAssetCreate,
    GeneratedAssetUpdate,
    GeneratedAssetResponse,
)
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    SocialAccountCreate,
    SocialAccountUpdate,
    SocialAccountResponse,
    SocialPostCreate,
    SocialPostUpdate,
    SocialPostResponse,
)
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    RenderJobCreate,
    RenderJobUpdate,
    RenderJobResponse,
    AIPromptCreate,
    AIPromptUpdate,
    AIPromptResponse,
)
from app.schemas.analytics import (
    AnalyticsEventResponse,
    TrendDataResponse,
    PlatformMetricResponse,
    BrandProfileCreate,
    BrandProfileUpdate,
    BrandProfileResponse,
)

__all__ = [
    # Base
    "BaseSchema",
    "BaseResponse",
    "PaginatedResponse",
    "ErrorResponse",
    
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "TokenResponse",
    "RoleCreate",
    "RoleResponse",
    
    # Media
    "ArtistCreate",
    "ArtistUpdate",
    "ArtistResponse",
    "AlbumCreate",
    "AlbumUpdate",
    "AlbumResponse",
    "TrackCreate",
    "TrackUpdate",
    "TrackResponse",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    
    # Asset
    "MediaAssetCreate",
    "MediaAssetUpdate",
    "MediaAssetResponse",
    "GeneratedAssetCreate",
    "GeneratedAssetUpdate",
    "GeneratedAssetResponse",
    
    # Campaign
    "CampaignCreate",
    "CampaignUpdate",
    "CampaignResponse",
    "SocialAccountCreate",
    "SocialAccountUpdate",
    "SocialAccountResponse",
    "SocialPostCreate",
    "SocialPostUpdate",
    "SocialPostResponse",
    
    # Workflow
    "WorkflowCreate",
    "WorkflowUpdate",
    "WorkflowResponse",
    "RenderJobCreate",
    "RenderJobUpdate",
    "RenderJobResponse",
    "AIPromptCreate",
    "AIPromptUpdate",
    "AIPromptResponse",
    
    # Analytics
    "AnalyticsEventResponse",
    "TrendDataResponse",
    "PlatformMetricResponse",
    "BrandProfileCreate",
    "BrandProfileUpdate",
    "BrandProfileResponse",
]