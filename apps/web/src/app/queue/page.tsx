"""
Render Queue Page - Production-grade render monitoring interface
"""
'use client'

import { useState } from 'react'
import {
  Play,
  Pause,
  RotateCcw,
  Trash2,
  MoreVertical,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Loader2,
  Zap,
  Server,
} from 'lucide-react'

interface RenderJob {
  id: string
  name: string
  job_type: string
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled'
  priority: 'low' | 'normal' | 'high' | 'urgent'
  progress: number
  started_at?: string
  completed_at?: string
  worker_id?: string
  estimated_duration?: number
  actual_duration?: number
  error_message?: string
}

interface QueueStats {
  total: number
  queued: number
  processing: number
  completed: number
  failed: number
  avg_duration: number
}

export default function RenderQueuePage() {
  const [selectedJobs, setSelectedJobs] = useState<Set<string>>(new Set())
  
  // Mock data
  const stats: QueueStats = {
    total: 47,
    queued: 12,
    processing: 3,
    completed: 28,
    failed: 4,
    avg_duration: 145,
  }
  
  const jobs: RenderJob[] = [
    {
      id: '1',
      name: 'Export TikTok Reel',
      job_type: 'export',
      status: 'processing',
      priority: 'high',
      progress: 67,
      started_at: new Date().toISOString(),
      worker_id: 'render-worker-1',
    },
    {
      id: '2',
      name: 'Audio Transcode',
      job_type: 'transcode',
      status: 'queued',
      priority: 'normal',
      progress: 0,
    },
    {
      id: '3',
      name: 'Thumbnail Generation',
      job_type: 'thumbnail',
      status: 'completed',
      priority: 'low',
      progress: 100,
      completed_at: new Date().toISOString(),
      actual_duration: 23,
    },
    {
      id: '4',
      name: 'Video Render',
      job_type: 'video',
      status: 'failed',
      priority: 'urgent',
      progress: 45,
      error_message: 'FFmpeg encoding error: Invalid codec',
    },
  ]
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />
      case 'processing':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />
      case 'queued':
        return <Clock className="w-4 h-4 text-yellow-500" />
      case 'cancelled':
        return <AlertCircle className="w-4 h-4 text-muted-foreground" />
      default:
        return <Clock className="w-4 h-4" />
    }
  }
  
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'text-red-500 bg-red-500/10'
      case 'high':
        return 'text-orange-500 bg-orange-500/10'
      case 'normal':
        return 'text-blue-500 bg-blue-500/10'
      case 'low':
        return 'text-muted-foreground bg-muted/10'
      default:
        return 'text-muted-foreground bg-muted/10'
    }
  }
  
  const formatDuration = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-border">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-semibold">Render Queue</h1>
          <span className="text-sm text-muted-foreground">
            {stats.total} jobs
          </span>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors text-sm font-medium">
            <Zap className="w-4 h-4" />
            New Render
          </button>
        </div>
      </div>
      
      {/* Stats Bar */}
      <div className="grid grid-cols-6 border-b border-border">
        <div className="px-6 py-4 border-r border-border">
          <p className="text-2xl font-semibold">{stats.total}</p>
          <p className="text-xs text-muted-foreground">Total</p>
        </div>
        <div className="px-6 py-4 border-r border-border">
          <p className="text-2xl font-semibold text-yellow-500">{stats.queued}</p>
          <p className="text-xs text-muted-foreground">Queued</p>
        </div>
        <div className="px-6 py-4 border-r border-border">
          <p className="text-2xl font-semibold text-blue-500">{stats.processing}</p>
          <p className="text-xs text-muted-foreground">Processing</p>
        </div>
        <div className="px-6 py-4 border-r border-border">
          <p className="text-2xl font-semibold text-green-500">{stats.completed}</p>
          <p className="text-xs text-muted-foreground">Completed</p>
        </div>
        <div className="px-6 py-4 border-r border-border">
          <p className="text-2xl font-semibold text-red-500">{stats.failed}</p>
          <p className="text-xs text-muted-foreground">Failed</p>
        </div>
        <div className="px-6 py-4">
          <p className="text-2xl font-semibold">{formatDuration(stats.avg_duration)}</p>
          <p className="text-xs text-muted-foreground">Avg Duration</p>
        </div>
      </div>
      
      {/* Job List */}
      <div className="flex-1 overflow-auto">
        <table className="w-full">
          <thead className="sticky top-0 bg-card border-b border-border z-10">
            <tr className="text-left text-xs text-muted-foreground uppercase tracking-wider">
              <th className="px-6 py-3 w-12"></th>
              <th className="px-6 py-3">Job</th>
              <th className="px-6 py-3 w-24">Status</th>
              <th className="px-6 py-3 w-24">Priority</th>
              <th className="px-6 py-3 w-48">Progress</th>
              <th className="px-6 py-3 w-24">Duration</th>
              <th className="px-6 py-3 w-32">Worker</th>
              <th className="px-6 py-3 w-16"></th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr key={job.id} className="border-b border-border hover:bg-card/50 transition-colors">
                <td className="px-6 py-4">
                  <input
                    type="checkbox"
                    checked={selectedJobs.has(job.id)}
                    onChange={() => {
                      const newSelection = new Set(selectedJobs)
                      if (newSelection.has(job.id)) {
                        newSelection.delete(job.id)
                      } else {
                        newSelection.add(job.id)
                      }
                      setSelectedJobs(newSelection)
                    }}
                    className="w-4 h-4 rounded border-border"
                  />
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(job.status)}
                    <div>
                      <p className="text-sm font-medium">{job.name}</p>
                      <p className="text-xs text-muted-foreground capitalize">{job.job_type}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center gap-1.5 text-xs font-medium capitalize ${
                    job.status === 'completed' ? 'text-green-500' :
                    job.status === 'failed' ? 'text-red-500' :
                    job.status === 'processing' ? 'text-blue-500' :
                    'text-muted-foreground'
                  }`}>
                    {getStatusIcon(job.status)}
                    {job.status}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${getPriorityColor(job.priority)}`}>
                    {job.priority}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all ${
                          job.status === 'failed' ? 'bg-red-500' :
                          job.status === 'completed' ? 'bg-green-500' :
                          'bg-primary'
                        }`}
                        style={{ width: `${job.progress}%` }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground w-10">{job.progress}%</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="text-xs text-muted-foreground">
                    {job.actual_duration ? formatDuration(job.actual_duration) : '-'}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className="text-xs text-muted-foreground">
                    {job.worker_id || '-'}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <button className="p-1.5 hover:bg-accent rounded">
                    <MoreVertical className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {/* Error Message Display */}
        {jobs.filter(j => j.status === 'failed').map((job) => (
          <div key={job.id} className="px-6 py-3 bg-red-500/5 border-b border-red-500/20">
            <div className="flex items-center gap-2 text-red-500 text-sm">
              <AlertCircle className="w-4 h-4" />
              <span className="font-medium">{job.name}:</span>
              <span className="text-muted-foreground">{job.error_message}</span>
            </div>
          </div>
        ))}
      </div>
      
      {/* Actions Bar */}
      {selectedJobs.size > 0 && (
        <div className="flex items-center justify-between px-6 py-3 border-t border-border bg-card">
          <span className="text-sm">{selectedJobs.size} selected</span>
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-2 px-3 py-1.5 text-sm hover:bg-accent rounded">
              <RotateCcw className="w-4 h-4" />
              Retry
            </button>
            <button className="flex items-center gap-2 px-3 py-1.5 text-sm hover:bg-accent rounded">
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
          </div>
        </div>
      )}
    </div>
  )
}