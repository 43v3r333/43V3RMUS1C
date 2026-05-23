"""
Repositories package - exports all repositories
"""
from .base import BaseRepository
from .user_repository import UserRepository, RoleRepository, PermissionRepository
from .media_repository import ArtistRepository, AlbumRepository, TrackRepository, ProjectRepository
from .asset_repository import MediaAssetRepository, GeneratedAssetRepository
from .campaign_repository import CampaignRepository, SocialAccountRepository, SocialPostRepository
from .workflow_repository import (
    RenderJobRepository,
    WorkflowRepository,
    AutomationJobRepository,
    AIPromptRepository,
)

__all__ = [
    "BaseRepository",
    # User repositories
    "UserRepository",
    "RoleRepository",
    "PermissionRepository",
    # Media repositories
    "ArtistRepository",
    "AlbumRepository",
    "TrackRepository",
    "ProjectRepository",
    # Asset repositories
    "MediaAssetRepository",
    "GeneratedAssetRepository",
    # Campaign repositories
    "CampaignRepository",
    "SocialAccountRepository",
    "SocialPostRepository",
    # Workflow repositories
    "RenderJobRepository",
    "WorkflowRepository",
    "AutomationJobRepository",
    "AIPromptRepository",
]