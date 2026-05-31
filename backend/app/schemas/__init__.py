"""
Schemas package - exports all schemas
"""
from .base import (
    BaseSchema,
    PaginationParams,
    SuccessResponse,
    ErrorResponse,
    SoftDeleteSchema,
)
from .user import (
    PermissionCreate, PermissionResponse,
    RoleCreate, RoleUpdate, RoleResponse,
    UserCreate, UserUpdate, UserResponse, UserBrief,
    TokenResponse, TokenRefreshRequest, LoginRequest,
    ChangePasswordRequest, PasswordResetRequest, PasswordResetConfirm,
)
from .media import (
    ArtistCreate, ArtistUpdate, ArtistResponse,
    AlbumCreate, AlbumUpdate, AlbumResponse,
    TrackCreate, TrackUpdate, TrackResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse,
)
from .asset import (
    MediaAssetCreate, MediaAssetUpdate, MediaAssetResponse,
    GeneratedAssetCreate, GeneratedAssetUpdate, GeneratedAssetResponse,
    AssetUploadResponse,
)
from .campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse,
    SocialAccountCreate, SocialAccountUpdate, SocialAccountResponse,
    SocialPostCreate, SocialPostUpdate, SocialPostResponse,
)
from .workflow import (
    RenderJobCreate, RenderJobUpdate, RenderJobResponse,
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    AutomationJobCreate, AutomationJobUpdate, AutomationJobResponse,
    AIPromptCreate, AIPromptUpdate, AIPromptResponse,
)
from .analytics import (
    AnalyticsEventCreate, AnalyticsEventResponse,
    TrendDataCreate, TrendDataResponse,
    PlatformMetricCreate, PlatformMetricResponse,
    BrandProfileCreate, BrandProfileUpdate, BrandProfileResponse,
    SystemLogCreate, SystemLogResponse,
)

__all__ = [
    # Base schemas
    "BaseSchema",
    "PaginationParams",
    "SuccessResponse",
    "ErrorResponse",
    "SoftDeleteSchema",
    # User schemas
    "PermissionCreate", "PermissionResponse",
    "RoleCreate", "RoleUpdate", "RoleResponse",
    "UserCreate", "UserUpdate", "UserResponse", "UserBrief",
    "TokenResponse", "TokenRefreshRequest", "LoginRequest",
    "ChangePasswordRequest", "PasswordResetRequest", "PasswordResetConfirm",
    # Media schemas
    "ArtistCreate", "ArtistUpdate", "ArtistResponse",
    "AlbumCreate", "AlbumUpdate", "AlbumResponse",
    "TrackCreate", "TrackUpdate", "TrackResponse",
    "ProjectCreate", "ProjectUpdate", "ProjectResponse",
    # Asset schemas
    "MediaAssetCreate", "MediaAssetUpdate", "MediaAssetResponse",
    "GeneratedAssetCreate", "GeneratedAssetUpdate", "GeneratedAssetResponse",
    "AssetUploadResponse",
    # Campaign schemas
    "CampaignCreate", "CampaignUpdate", "CampaignResponse",
    "SocialAccountCreate", "SocialAccountUpdate", "SocialAccountResponse",
    "SocialPostCreate", "SocialPostUpdate", "SocialPostResponse",
    # Workflow schemas
    "RenderJobCreate", "RenderJobUpdate", "RenderJobResponse",
    "WorkflowCreate", "WorkflowUpdate", "WorkflowResponse",
    "AutomationJobCreate", "AutomationJobUpdate", "AutomationJobResponse",
    "AIPromptCreate", "AIPromptUpdate", "AIPromptResponse",
    # Analytics schemas
    "AnalyticsEventCreate", "AnalyticsEventResponse",
    "TrendDataCreate", "TrendDataResponse",
    "PlatformMetricCreate", "PlatformMetricResponse",
    "BrandProfileCreate", "BrandProfileUpdate", "BrandProfileResponse",
    "SystemLogCreate", "SystemLogResponse",
]