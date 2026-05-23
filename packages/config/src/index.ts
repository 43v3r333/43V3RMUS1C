// 43V3R CORE - Shared Configuration

export const config = {
  app: {
    name: '43V3R CORE',
    version: '1.0.0',
    description: 'Enterprise-Grade Autonomous Media Operating System',
  },
  api: {
    prefix: '/api/v1',
    timeout: 30000,
    retries: 3,
  },
  pagination: {
    default_page: 1,
    default_per_page: 20,
    max_per_page: 100,
  },
  auth: {
    access_token_expire_minutes: 30,
    refresh_token_expire_days: 7,
    password_min_length: 8,
  },
  storage: {
    max_file_size_mb: 500,
    allowed_audio_types: ['audio/mpeg', 'audio/wav', 'audio/flac', 'audio/aac', 'audio/ogg'],
    allowed_video_types: ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm'],
    allowed_image_types: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  },
  render: {
    default_priority: 'normal',
    max_retries: 3,
    timeout_seconds: 3600,
    concurrent_jobs_limit: 10,
  },
  analytics: {
    enabled: true,
    retention_days: 90,
  },
} as const

export type Config = typeof config