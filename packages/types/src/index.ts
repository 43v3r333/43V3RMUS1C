// Shared type definitions for 43V3R CORE

export interface BaseEntity {
  id: string
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

export interface PaginationParams {
  page?: number
  per_page?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  has_more: boolean
}

export interface ApiError {
  detail: string
  code?: string
  field?: string
}

export type Status = 'pending' | 'active' | 'inactive' | 'deleted'
export type AssetType = 'audio' | 'video' | 'image' | 'document'
export type ProjectStatus = 'draft' | 'in_progress' | 'completed' | 'archived'
export type RenderJobStatus = 'pending' | 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled'
export type RenderJobPriority = 'low' | 'normal' | 'high' | 'urgent'
export type CampaignStatus = 'draft' | 'scheduled' | 'active' | 'paused' | 'completed'

export interface TimeStamped {
  created_at: string
  updated_at: string
}

export interface SoftDeletable extends TimeStamped {
  deleted_at?: string | null
}

export interface UserBrief {
  id: string
  username: string
  email: string
}

export interface ArtistBrief {
  id: string
  name: string
  slug: string
}

export interface ProjectBrief {
  id: string
  name: string
}

export interface MediaAssetBrief {
  id: string
  name: string
  asset_type: AssetType
}

export interface TrackBrief {
  id: string
  title: string
  artist_name?: string
}

export interface WorkflowBrief {
  id: string
  name: string
  workflow_type: string
}

export interface CampaignBrief {
  id: string
  name: string
  status: CampaignStatus
}

// Event types for analytics
export type EventType = 'page_view' | 'click' | 'form_submit' | 'render_complete' | 'upload' | 'download' | 'api_call'

export interface AnalyticsEvent {
  id: string
  event_type: EventType
  event_name: string
  user_id?: string
  session_id?: string
  properties?: Record<string, unknown>
  traits?: Record<string, unknown>
  ip_address?: string
  user_agent?: string
  timestamp: string
}

// Platform integration types
export type Platform = 'spotify' | 'apple_music' | 'youtube' | 'soundcloud' | 'instagram' | 'tiktok' | 'twitter' | 'facebook'

export interface SocialMetrics {
  followers?: number
  following?: number
  posts?: number
  engagement_rate?: number
}

export interface PlatformCredentials {
  access_token: string
  refresh_token?: string
  expires_at?: string
  token_type?: string
}

// Media processing types
export interface MediaMetadata {
  duration?: number
  width?: number
  height?: number
  bitrate?: number
  codec?: string
  sample_rate?: number
  channels?: number
}

export interface RenderParameters {
  format: string
  quality: 'low' | 'medium' | 'high' | 'ultra'
  codec?: string
  bitrate?: number
  resolution?: string
}

export interface GenerationParameters {
  model?: string
  style?: string
  seed?: number
  steps?: number
  guidance_scale?: number
}

export interface WorkflowDefinition {
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
}

export interface WorkflowNode {
  id: string
  type: string
  position: { x: number; y: number }
  data: Record<string, unknown>
}

export interface WorkflowEdge {
  id: string
  source: string
  target: string
  label?: string
}