// ===============================================
// 43V3R CORE - TypeScript Type Definitions
// ===============================================

// User types
export interface User {
  id: string
  email: string
  username: string
  first_name?: string
  last_name?: string
  avatar_url?: string
  bio?: string
  is_active: boolean
  is_superuser: boolean
  is_verified: boolean
  role_id?: string
  created_at: string
  updated_at: string
  deleted_at?: string
}

export interface Role {
  id: string
  name: string
  description?: string
  created_at: string
  updated_at: string
}

// Media types
export interface Artist {
  id: string
  name: string
  slug: string
  bio?: string
  image_url?: string
  social_links?: Record<string, string>
  genre?: string
  label?: string
  website?: string
  is_verified: boolean
  user_id?: string
  created_at: string
  updated_at: string
}

export interface Album {
  id: string
  title: string
  slug: string
  description?: string
  cover_url?: string
  release_date?: string
  genre?: string
  label?: string
  total_tracks: number
  total_duration: number
  is_single: boolean
  artist_id?: string
  created_at: string
  updated_at: string
}

export interface Track {
  id: string
  title: string
  slug: string
  description?: string
  duration?: number
  track_number?: number
  bpm?: number
  key_signature?: string
  explicit: boolean
  audio_url?: string
  waveform_url?: string
  genre?: string
  mood?: string
  tags?: string[]
  play_count: number
  like_count: number
  artist_id?: string
  album_id?: string
  created_at: string
  updated_at: string
}

export interface Project {
  id: string
  name: string
  description?: string
  status: 'draft' | 'in_progress' | 'completed' | 'archived'
  project_type?: string
  cover_url?: string
  metadata?: Record<string, unknown>
  owner_id: string
  artist_id?: string
  created_at: string
  updated_at: string
}

// Asset types
export interface MediaAsset {
  id: string
  name: string
  file_name: string
  file_path: string
  file_size?: number
  mime_type?: string
  asset_type: 'audio' | 'video' | 'image' | 'document'
  status: 'pending' | 'processing' | 'ready' | 'failed'
  duration?: number
  width?: number
  height?: number
  metadata?: Record<string, unknown>
  tags?: string[]
  project_id?: string
  track_id?: string
  created_at: string
  updated_at: string
}

export interface GeneratedAsset {
  id: string
  name: string
  asset_type: string
  generation_type: string
  prompt?: string
  negative_prompt?: string
  parameters?: Record<string, unknown>
  output_path?: string
  output_url?: string
  preview_url?: string
  status: 'pending' | 'processing' | 'ready' | 'failed'
  error_message?: string
  generation_time?: number
  project_id?: string
  campaign_id?: string
  created_at: string
  updated_at: string
}

// Workflow types
export interface Workflow {
  id: string
  name: string
  description?: string
  workflow_type: string
  version: string
  definition: Record<string, unknown>
  is_active: boolean
  is_public: boolean
  trigger_type?: string
  trigger_config?: Record<string, unknown>
  created_by_id: string
  project_id?: string
  created_at: string
  updated_at: string
}

export interface RenderJob {
  id: string
  name: string
  job_type: string
  status: 'pending' | 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled'
  priority: 'low' | 'normal' | 'high' | 'urgent'
  input_path?: string
  output_path?: string
  parameters?: Record<string, unknown>
  progress: number
  started_at?: string
  completed_at?: string
  worker_id?: string
  retry_count: number
  max_retries: number
  error_message?: string
  estimated_duration?: number
  actual_duration?: number
  project_id?: string
  created_at: string
  updated_at: string
}

export interface AIPrompt {
  id: string
  name: string
  description?: string
  prompt_type: string
  template: string
  variables?: { name: string; type: string; required?: boolean }[]
  model?: string
  parameters?: Record<string, unknown>
  is_active: boolean
  is_public: boolean
  use_count: number
  category?: string
  tags?: string[]
  created_by_id?: string
  created_at: string
  updated_at: string
}

// Campaign types
export interface Campaign {
  id: string
  name: string
  description?: string
  campaign_type: string
  status: 'draft' | 'scheduled' | 'active' | 'paused' | 'completed'
  start_date?: string
  end_date?: string
  budget?: number
  target_platforms?: string[]
  target_audience?: Record<string, unknown>
  metadata?: Record<string, unknown>
  created_by_id: string
  artist_id?: string
  created_at: string
  updated_at: string
}

export interface SocialPost {
  id: string
  content?: string
  caption?: string
  media_urls?: string[]
  hashtags?: string[]
  platform: string
  post_type: string
  status: 'draft' | 'scheduled' | 'published' | 'failed'
  scheduled_at?: string
  published_at?: string
  external_id?: string
  external_url?: string
  metrics?: Record<string, number>
  account_id?: string
  campaign_id?: string
  track_id?: string
  created_at: string
  updated_at: string
}

// Analytics types
export interface PlatformMetric {
  id: string
  metric_name: string
  metric_type: string
  value: number
  unit?: string
  tags?: Record<string, string>
  timestamp: string
  created_at: string
}

// API Response types
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  has_more: boolean
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}