"""
Services package - exports all services
"""
from .base import BaseService
from .user_service import UserService, RoleService
from .media_service import ArtistService, AlbumService, TrackService, ProjectService
from .asset_service import MediaAssetService, GeneratedAssetService
from .campaign_service import CampaignService, SocialAccountService, SocialPostService
from .workflow_service import (
    RenderJobService,
    WorkflowService,
    AutomationJobService,
    AIPromptService,
)

__all__ = [
    "BaseService",
    # User services
    "UserService",
    "RoleService",
    # Media services
    "ArtistService",
    "AlbumService",
    "TrackService",
    "ProjectService",
    # Asset services
    "MediaAssetService",
    "GeneratedAssetService",
    # Campaign services
    "CampaignService",
    "SocialAccountService",
    "SocialPostService",
    # Workflow services
    "RenderJobService",
    "WorkflowService",
    "AutomationJobService",
    "AIPromptService",
]