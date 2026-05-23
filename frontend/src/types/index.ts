"""
TypeScript types for the application
*/

// User types
export interface User {
  id: string
  email: string
  username: string
  firstName?: string
  lastName?: string
  avatarUrl?: string
  isActive: boolean
  isSuperuser: boolean
  role: Role
  createdAt: string
  updatedAt: string
}

export interface Role {
  id: string
  name: string
  description?: string
  permissions: Permission[]
}

export interface Permission {
  id: string
  name: string
  resource: string
  action: string
}

// Media types
export interface Artist {
  id: string
  name: string
  slug: string
  bio?: string
  imageUrl?: string
  socialLinks?: Record<string, string>
  genre?: string
  label?: string
  website?: string
  isVerified: boolean
  userId?: string
  createdAt: string
  updatedAt: string
}

export interface Album {
  id: string
  title: string
  slug: string
  description?: string
  coverUrl?: string
  releaseDate?: string
  genre?: string
  label?: string
  totalTracks: number
  totalDuration: number
  isSingle: boolean
  artistId: string
  createdAt: string
  updatedAt: string
}

export interface Track {
  id: string
  title: string
  slug: string
  description?: string
  duration?: number
  trackNumber?: number
  bpm?: number
  keySignature?: string
  explicit: boolean
  audioUrl?: string
  waveformUrl?: string
  genre?: string
  mood?: string
  tags?: string[]
  playCount: number
  likeCount: number
  artistId?: string
  albumId?: string
  createdAt: string
  updatedAt: string
}

export interface Project {
  id: string
  name: string
  description?: string
  status: "draft" | "in_progress" | "completed" | "archived"
  projectType?: string
  coverUrl?: string
  metadata?: Record<string, unknown>
  ownerId: string
  artistId?: string
  createdAt: string
  updatedAt: string
}

// Asset types
export interface MediaAsset {
  id: string
  name: string
  fileName: string
  filePath: string
  fileSize?: number
  mimeType?: string
  assetType: "audio" | "video" | "image" | "document" | "other"
  status: "pending" | "processing" | "ready" | "failed"
  duration?: number
  width?: number
  height?: number
  metadata?: Record<string, unknown>
  tags?: string[]
  projectId?: string
  trackId?: string
  createdAt: string
  updatedAt: string
}

export interface GeneratedAsset {
  id: string
  name: string
  assetType: string
  generationType: string
  prompt?: string
  negativePrompt?: string
  parameters?: Record<string, unknown>
  outputPath?: string
  outputUrl?: string
  previewUrl?: string
  status: "pending" | "processing" | "ready" | "failed"
  errorMessage?: string
  generationTime?: number
  projectId?: string
  campaignId?: string
  createdAt: string
  updatedAt: string
}

// Workflow types
export interface RenderJob {
  id: string
  name: string
  jobType: string
  status: "pending" | "queued" | "processing" | "completed" | "failed" | "cancelled"
  priority: "low" | "normal" | "high" | "urgent"
  inputPath?: string
  outputPath?: string
  parameters?: Record<string, unknown>
  progress: number
  startedAt?: string
  completedAt?: string
  workerId?: string
  retryCount: number
  maxRetries: number
  errorMessage?: string
  projectId?: string
  createdAt: string
  updatedAt: string
}

export interface Workflow {
  id: string
  name: string
  description?: string
  workflowType: string
  version: string
  definition: Record<string, unknown>
  isActive: boolean
  isPublic: boolean
  triggerType?: string
  triggerConfig?: Record<string, unknown>
  createdById: string
  projectId?: string
  createdAt: string
  updatedAt: string
}

export interface AIPrompt {
  id: string
  name: string
  description?: string
  promptType: string
  template: string
  variables?: { name: string; type: string; required: boolean }[]
  model?: string
  parameters?: Record<string, unknown>
  isActive: boolean
  isPublic: boolean
  useCount: number
  category?: string
  tags?: string[]
  createdById?: string
  createdAt: string
  updatedAt: string
}

// Campaign types
export interface Campaign {
  id: string
  name: string
  description?: string
  campaignType: string
  status: "draft" | "scheduled" | "active" | "paused" | "completed"
  startDate?: string
  endDate?: string
  budget?: number
  targetPlatforms?: string[]
  targetAudience?: Record<string, unknown>
  metadata?: Record<string, unknown>
  createdById: string
  artistId?: string
  createdAt: string
  updatedAt: string
}

export interface SocialPost {
  id: string
  content?: string
  caption?: string
  mediaUrls?: string[]
  hashtags?: string[]
  platform: string
  postType: string
  status: "draft" | "scheduled" | "published" | "failed"
  scheduledAt?: string
  publishedAt?: string
  externalId?: string
  externalUrl?: string
  metrics?: Record<string, unknown>
  accountId: string
  campaignId?: string
  trackId?: string
  createdAt: string
  updatedAt: string
}

// Analytics types
export interface AnalyticsEvent {
  id: string
  eventType: string
  eventName: string
  userId?: string
  sessionId?: string
  properties?: Record<string, unknown>
  traits?: Record<string, unknown>
  timestamp: string
}

export interface PlatformMetric {
  id: string
  metricName: string
  metricType: string
  value: number
  unit?: string
  tags?: Record<string, string>
  metadata?: Record<string, unknown>
  timestamp: string
}

// API Response types
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  perPage: number
  hasMore: boolean
}

export interface ApiError {
  detail: string
  code?: string
}