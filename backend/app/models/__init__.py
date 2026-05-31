"""
Models package - exports all database models
"""
from .base import BaseModel
from .user import User, Role, Permission
from .media import Artist, Album, Track, Project
from .asset import MediaAsset, GeneratedAsset, AssetType, AssetStatus
from .campaign import Campaign, SocialAccount, SocialPost, CampaignStatus, SocialPlatform
from .workflow import RenderJob, Workflow, AutomationJob, AIPrompt, JobStatus, JobPriority
from .analytics import (
    AnalyticsEvent,
    TrendData,
    PlatformMetric,
    BrandProfile,
    SystemLog
)

__all__ = [
    "BaseModel",
    # User models
    "User",
    "Role",
    "Permission",
    # Media models
    "Artist",
    "Album",
    "Track",
    "Project",
    # Asset models
    "MediaAsset",
    "GeneratedAsset",
    "AssetType",
    "AssetStatus",
    # Campaign models
    "Campaign",
    "SocialAccount",
    "SocialPost",
    "CampaignStatus",
    "SocialPlatform",
    # Workflow models
    "RenderJob",
    "Workflow",
    "AutomationJob",
    "AIPrompt",
    "JobStatus",
    "JobPriority",
    # Analytics models
    "AnalyticsEvent",
    "TrendData",
    "PlatformMetric",
    "BrandProfile",
    "SystemLog",
]