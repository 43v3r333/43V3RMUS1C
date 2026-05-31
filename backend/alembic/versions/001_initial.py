"""Initial migration - create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE assettype AS ENUM ('audio', 'video', 'image', 'document', 'other')")
    op.execute("CREATE TYPE assetstatus AS ENUM ('pending', 'processing', 'ready', 'failed')")
    op.execute("CREATE TYPE campaignstatus AS ENUM ('draft', 'scheduled', 'active', 'paused', 'completed')")
    op.execute("CREATE TYPE socialplatform AS ENUM ('instagram', 'tiktok', 'youtube', 'twitter', 'facebook', 'spotify', 'apple_music')")
    op.execute("CREATE TYPE jobstatus AS ENUM ('pending', 'queued', 'processing', 'completed', 'failed', 'cancelled')")
    op.execute("CREATE TYPE jobpriority AS ENUM ('low', 'normal', 'high', 'urgent')")
    
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(50), unique=True, nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
    )
    op.create_index('ix_roles_name', 'roles', ['name'])
    
    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('resource', sa.String(50), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
    )
    op.create_index('ix_permissions_name', 'permissions', ['name'])
    op.create_index('ix_permissions_resource', 'permissions', ['resource'])
    
    # Create role_permissions junction table
    op.create_table(
        'role_permissions',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.id'), primary_key=True),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('permissions.id'), primary_key=True),
    )
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('username', sa.String(100), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('is_superuser', sa.Boolean(), default=False, nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.id'), nullable=True),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    
    # Create artists table
    op.create_table(
        'artists',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), unique=True, nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('social_links', postgresql.JSON(), nullable=True),
        sa.Column('genre', sa.String(100), nullable=True),
        sa.Column('label', sa.String(255), nullable=True),
        sa.Column('website', sa.String(500), nullable=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
    )
    op.create_index('ix_artists_name', 'artists', ['name'])
    op.create_index('ix_artists_slug', 'artists', ['slug'])
    op.create_index('ix_artists_genre', 'artists', ['genre'])
    
    # Create albums table
    op.create_table(
        'albums',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), unique=True, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cover_url', sa.String(500), nullable=True),
        sa.Column('release_date', sa.DateTime(), nullable=True),
        sa.Column('genre', sa.String(100), nullable=True),
        sa.Column('label', sa.String(255), nullable=True),
        sa.Column('total_tracks', sa.Integer(), default=0),
        sa.Column('total_duration', sa.Integer(), default=0),
        sa.Column('is_single', sa.Boolean(), default=False),
        sa.Column('artist_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('artists.id'), nullable=True),
    )
    op.create_index('ix_albums_title', 'albums', ['title'])
    op.create_index('ix_albums_slug', 'albums', ['slug'])
    op.create_index('ix_albums_genre', 'albums', ['genre'])
    
    # Create tracks table
    op.create_table(
        'tracks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), unique=True, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('track_number', sa.Integer(), nullable=True),
        sa.Column('bpm', sa.Integer(), nullable=True),
        sa.Column('key_signature', sa.String(20), nullable=True),
        sa.Column('explicit', sa.Boolean(), default=False),
        sa.Column('audio_url', sa.String(500), nullable=True),
        sa.Column('waveform_url', sa.String(500), nullable=True),
        sa.Column('genre', sa.String(100), nullable=True),
        sa.Column('mood', sa.String(100), nullable=True),
        sa.Column('tags', postgresql.JSON(), nullable=True),
        sa.Column('play_count', sa.Integer(), default=0),
        sa.Column('like_count', sa.Integer(), default=0),
        sa.Column('artist_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('artists.id'), nullable=True),
        sa.Column('album_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('albums.id'), nullable=True),
    )
    op.create_index('ix_tracks_title', 'tracks', ['title'])
    op.create_index('ix_tracks_slug', 'tracks', ['slug'])
    op.create_index('ix_tracks_genre', 'tracks', ['genre'])
    
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('project_type', sa.String(50), nullable=True),
        sa.Column('cover_url', sa.String(500), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('artist_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('artists.id'), nullable=True),
    )
    op.create_index('ix_projects_name', 'projects', ['name'])
    op.create_index('ix_projects_status', 'projects', ['status'])
    
    # Create media_assets table
    op.create_table(
        'media_assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('asset_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('tags', postgresql.JSON(), nullable=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=True),
        sa.Column('track_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tracks.id'), nullable=True),
    )
    op.create_index('ix_media_assets_name', 'media_assets', ['name'])
    op.create_index('ix_media_assets_asset_type', 'media_assets', ['asset_type'])
    op.create_index('ix_media_assets_status', 'media_assets', ['status'])
    
    # Create generated_assets table
    op.create_table(
        'generated_assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('asset_type', sa.String(50), nullable=False),
        sa.Column('generation_type', sa.String(50), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=True),
        sa.Column('negative_prompt', sa.Text(), nullable=True),
        sa.Column('parameters', postgresql.JSON(), nullable=True),
        sa.Column('output_path', sa.String(500), nullable=True),
        sa.Column('output_url', sa.String(500), nullable=True),
        sa.Column('preview_url', sa.String(500), nullable=True),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('generation_time', sa.Integer(), nullable=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaigns.id'), nullable=True),
    )
    op.create_index('ix_generated_assets_name', 'generated_assets', ['name'])
    op.create_index('ix_generated_assets_asset_type', 'generated_assets', ['asset_type'])
    op.create_index('ix_generated_assets_status', 'generated_assets', ['status'])
    
    # Create campaigns table
    op.create_table(
        'campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('campaign_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('budget', sa.Integer(), nullable=True),
        sa.Column('target_platforms', postgresql.JSON(), nullable=True),
        sa.Column('target_audience', postgresql.JSON(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('artist_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('artists.id'), nullable=True),
    )
    op.create_index('ix_campaigns_name', 'campaigns', ['name'])
    op.create_index('ix_campaigns_status', 'campaigns', ['status'])
    
    # Create social_accounts table
    op.create_table(
        'social_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('username', sa.String(255), nullable=True),
        sa.Column('display_name', sa.String(255), nullable=True),
        sa.Column('profile_url', sa.String(500), nullable=True),
        sa.Column('profile_image_url', sa.String(500), nullable=True),
        sa.Column('access_token', sa.String(500), nullable=True),
        sa.Column('refresh_token', sa.String(500), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_primary', sa.Boolean(), default=False),
        sa.Column('stats', postgresql.JSON(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('artist_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('artists.id'), nullable=True),
    )
    op.create_index('ix_social_accounts_platform', 'social_accounts', ['platform'])
    
    # Create social_posts table
    op.create_table(
        'social_posts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('caption', sa.Text(), nullable=True),
        sa.Column('media_urls', postgresql.JSON(), nullable=True),
        sa.Column('hashtags', postgresql.JSON(), nullable=True),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('post_type', sa.String(50), default='post'),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('external_id', sa.String(255), nullable=True),
        sa.Column('external_url', sa.String(500), nullable=True),
        sa.Column('metrics', postgresql.JSON(), nullable=True),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('social_accounts.id'), nullable=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('campaigns.id'), nullable=True),
        sa.Column('track_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tracks.id'), nullable=True),
    )
    op.create_index('ix_social_posts_platform', 'social_posts', ['platform'])
    op.create_index('ix_social_posts_status', 'social_posts', ['status'])
    
    # Create render_jobs table
    op.create_table(
        'render_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('job_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('priority', sa.String(50), default='normal'),
        sa.Column('input_path', sa.String(500), nullable=True),
        sa.Column('output_path', sa.String(500), nullable=True),
        sa.Column('parameters', postgresql.JSON(), nullable=True),
        sa.Column('progress', sa.Float(), default=0.0),
        sa.Column('started_at', sa.String(50), nullable=True),
        sa.Column('completed_at', sa.String(50), nullable=True),
        sa.Column('worker_id', sa.String(100), nullable=True),
        sa.Column('retry_count', sa.Integer(), default=0),
        sa.Column('max_retries', sa.Integer(), default=3),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('logs', sa.Text(), nullable=True),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('actual_duration', sa.Integer(), nullable=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=True),
    )
    op.create_index('ix_render_jobs_name', 'render_jobs', ['name'])
    op.create_index('ix_render_jobs_job_type', 'render_jobs', ['job_type'])
    op.create_index('ix_render_jobs_status', 'render_jobs', ['status'])
    
    # Create workflows table
    op.create_table(
        'workflows',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('workflow_type', sa.String(50), nullable=False),
        sa.Column('version', sa.String(20), default='1.0.0'),
        sa.Column('definition', postgresql.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_public', sa.Boolean(), default=False),
        sa.Column('trigger_type', sa.String(50), nullable=True),
        sa.Column('trigger_config', postgresql.JSON(), nullable=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=True),
    )
    op.create_index('ix_workflows_name', 'workflows', ['name'])
    op.create_index('ix_workflows_workflow_type', 'workflows', ['workflow_type'])
    
    # Create automation_jobs table
    op.create_table(
        'automation_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('input_data', postgresql.JSON(), nullable=True),
        sa.Column('output_data', postgresql.JSON(), nullable=True),
        sa.Column('started_at', sa.String(50), nullable=True),
        sa.Column('completed_at', sa.String(50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('logs', sa.Text(), nullable=True),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workflows.id'), nullable=True),
        sa.Column('triggered_by', sa.String(50), nullable=True),
    )
    op.create_index('ix_automation_jobs_status', 'automation_jobs', ['status'])
    
    # Create ai_prompts table
    op.create_table(
        'ai_prompts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('prompt_type', sa.String(50), nullable=False),
        sa.Column('template', sa.Text(), nullable=False),
        sa.Column('variables', postgresql.JSON(), nullable=True),
        sa.Column('model', sa.String(100), nullable=True),
        sa.Column('parameters', postgresql.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_public', sa.Boolean(), default=False),
        sa.Column('use_count', sa.Integer(), default=0),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('tags', postgresql.JSON(), nullable=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
    )
    op.create_index('ix_ai_prompts_name', 'ai_prompts', ['name'])
    op.create_index('ix_ai_prompts_prompt_type', 'ai_prompts', ['prompt_type'])
    op.create_index('ix_ai_prompts_category', 'ai_prompts', ['category'])
    
    # Create analytics_events table
    op.create_table(
        'analytics_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('event_name', sa.String(255), nullable=False),
        sa.Column('user_id', sa.String(100), nullable=True),
        sa.Column('session_id', sa.String(100), nullable=True),
        sa.Column('properties', postgresql.JSON(), nullable=True),
        sa.Column('traits', postgresql.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('referrer', sa.String(500), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_analytics_events_event_type', 'analytics_events', ['event_type'])
    op.create_index('ix_analytics_events_event_name', 'analytics_events', ['event_name'])
    op.create_index('ix_analytics_events_user_id', 'analytics_events', ['user_id'])
    
    # Create trend_data table
    op.create_table(
        'trend_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('trend_type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('external_id', sa.String(255), nullable=True),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('change', sa.String(50), nullable=True),
        sa.Column('change_value', sa.Integer(), nullable=True),
        sa.Column('metrics', postgresql.JSON(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('region', sa.String(50), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_trend_data_source', 'trend_data', ['source'])
    op.create_index('ix_trend_data_trend_type', 'trend_data', ['trend_type'])
    op.create_index('ix_trend_data_name', 'trend_data', ['name'])
    op.create_index('ix_trend_data_date', 'trend_data', ['date'])
    op.create_index('ix_trend_data_region', 'trend_data', ['region'])
    
    # Create platform_metrics table
    op.create_table(
        'platform_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('metric_type', sa.String(50), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('tags', postgresql.JSON(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_platform_metrics_metric_name', 'platform_metrics', ['metric_name'])
    op.create_index('ix_platform_metrics_timestamp', 'platform_metrics', ['timestamp'])
    
    # Create brand_profiles table
    op.create_table(
        'brand_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('colors', postgresql.JSON(), nullable=True),
        sa.Column('fonts', postgresql.JSON(), nullable=True),
        sa.Column('visual_style', postgresql.JSON(), nullable=True),
        sa.Column('tone_of_voice', postgresql.JSON(), nullable=True),
        sa.Column('content_guidelines', postgresql.JSON(), nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('assets', postgresql.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('artist_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('artists.id'), nullable=True),
    )
    op.create_index('ix_brand_profiles_name', 'brand_profiles', ['name'])
    
    # Create system_logs table
    op.create_table(
        'system_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('level', sa.String(20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('logger_name', sa.String(100), nullable=True),
        sa.Column('module', sa.String(100), nullable=True),
        sa.Column('function', sa.String(100), nullable=True),
        sa.Column('line_number', sa.Integer(), nullable=True),
        sa.Column('request_id', sa.String(100), nullable=True),
        sa.Column('user_id', sa.String(100), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('extra_data', postgresql.JSON(), nullable=True),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_system_logs_level', 'system_logs', ['level'])
    op.create_index('ix_system_logs_request_id', 'system_logs', ['request_id'])
    op.create_index('ix_system_logs_user_id', 'system_logs', ['user_id'])
    op.create_index('ix_system_logs_timestamp', 'system_logs', ['timestamp'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('system_logs')
    op.drop_table('brand_profiles')
    op.drop_table('platform_metrics')
    op.drop_table('trend_data')
    op.drop_table('analytics_events')
    op.drop_table('ai_prompts')
    op.drop_table('automation_jobs')
    op.drop_table('workflows')
    op.drop_table('render_jobs')
    op.drop_table('social_posts')
    op.drop_table('social_accounts')
    op.drop_table('campaigns')
    op.drop_table('generated_assets')
    op.drop_table('media_assets')
    op.drop_table('projects')
    op.drop_table('tracks')
    op.drop_table('albums')
    op.drop_table('artists')
    op.drop_table('users')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('roles')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS jobpriority")
    op.execute("DROP TYPE IF EXISTS jobstatus")
    op.execute("DROP TYPE IF EXISTS socialplatform")
    op.execute("DROP TYPE IF EXISTS campaignstatus")
    op.execute("DROP TYPE IF EXISTS assetstatus")
    op.execute("DROP TYPE IF EXISTS assettype")