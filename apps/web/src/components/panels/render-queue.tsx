"""
Render Queue Panel - Real-time render job management
"""
'use client'

import { useState, useEffect } from 'react'
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
  Filter,
  ArrowUpDown,
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
}

export function RenderQueuePanel() {
  const [jobs, setJobs] = useState<RenderJob[]>([])
  const [stats, setStats] = useState<QueueStats>({
    total: 0,
    queued: 0,
    processing: 0,
    completed: 0,
    failed: 0,
  })
  const [selectedJobs, setSelectedJobs] = useState<Set<string>>(new Set())
  const [filter, setFilter] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'name' | 'status' | 'priority' | 'time'>('time')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')

  // Simulated real-time updates
  useEffect(() => {
    // Initial data
    setJobs([
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
      {
        id: '5',
        name: 'Social Clip Export',
        job_type: 'export',
        status: 'processing',
        priority: 'high',
        progress: 23,
        worker_id: 'render-worker-2',
      },
    ])

    // Simulate progress updates
    const interval = setInterval(() => {
      setJobs((prev) =>
        prev.map((job) =>
          job.status === 'processing'
            ? { ...job, progress: Math.min(100, job.progress + Math.random() * 5) }
            : job
        )
      )
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  // Update stats when jobs change
  useEffect(() => {
    setStats({
      total: jobs.length,
      queued: jobs.filter((j) => j.status === 'queued').length,
      processing: jobs.filter((j) => j.status === 'processing').length,
      completed: jobs.filter((j) => j.status === 'completed').length,
      failed: jobs.filter((j) => j.status === 'failed').length,
    })
  }, [jobs])

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

  const filteredJobs = jobs.filter((job) => {
    if (filter === 'all') return true
    return job.status === filter
  })

  const sortedJobs = [...filteredJobs].sort((a, b) => {
    let comparison = 0
    switch (sortBy) {
      case 'name':
        comparison = a.name.localeCompare(b.name)
        break
      case 'status':
        comparison = a.status.localeCompare(b.status)
        break
      case 'priority':
        const priorityOrder = { urgent: 0, high: 1, normal: 2, low: 3 }
        comparison = (priorityOrder[a.priority] || 0) - (priorityOrder[b.priority] || 0)
        break
      case 'time':
        comparison = new Date(a.started_at || 0).getTime() - new Date(b.started_at || 0).getTime()
        break
    }
    return sortOrder === 'asc' ? comparison : -comparison
  })

  return (
    <div className="flex flex-col h-full">
      {/* Stats Bar */}
      <div className="grid grid-cols-6 border-b border-border">
        <StatCell label="Total" value={stats.total} />
        <StatCell label="Queued" value={stats.queued} color="text-yellow-500" />
        <StatCell label="Processing" value={stats.processing} color="text-blue-500" />
        <StatCell label="Completed" value={stats.completed} color="text-green-500" />
        <StatCell label="Failed" value={stats.failed} color="text-red-500" />
        <StatCell
          label="Avg Time"
          value="2m 25s"
        />
      </div>

      {/* Filters and Actions */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-border">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-muted-foreground" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="text-xs bg-transparent border border-border rounded px-2 py-1"
          >
            <option value="all">All</option>
            <option value="queued">Queued</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="flex items-center gap-1 px-2 py-1 text-xs hover:bg-accent rounded"
          >
            <ArrowUpDown className="w-3 h-3" />
            Sort
          </button>
        </div>
      </div>

      {/* Job List */}
      <div className="flex-1 overflow-auto">
        <table className="w-full">
          <thead className="sticky top-0 bg-card border-b border-border z-10">
            <tr className="text-left text-xs text-muted-foreground uppercase tracking-wider">
              <th className="px-4 py-3 w-10"></th>
              <th className="px-4 py-3">Job</th>
              <th className="px-4 py-3 w-24">Status</th>
              <th className="px-4 py-3 w-24">Priority</th>
              <th className="px-4 py-3 w-40">Progress</th>
              <th className="px-4 py-3 w-20">Duration</th>
              <th className="px-4 py-3 w-28">Worker</th>
              <th className="px-4 py-3 w-10"></th>
            </tr>
          </thead>
          <tbody>
            {sortedJobs.map((job) => (
              <tr
                key={job.id}
                className="border-b border-border hover:bg-card/50 transition-colors"
              >
                <td className="px-4 py-3">
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
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(job.status)}
                    <div>
                      <p className="text-sm font-medium">{job.name}</p>
                      <p className="text-xs text-muted-foreground capitalize">{job.job_type}</p>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center gap-1.5 text-xs font-medium ${
                    job.status === 'completed' ? 'text-green-500' :
                    job.status === 'failed' ? 'text-red-500' :
                    job.status === 'processing' ? 'text-blue-500' :
                    'text-muted-foreground'
                  }`}>
                    {getStatusIcon(job.status)}
                    <span className="capitalize">{job.status}</span>
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${getPriorityColor(job.priority)}`}>
                    {job.priority}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
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
                    <span className="text-xs text-muted-foreground w-10">
                      {Math.round(job.progress)}%
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="text-xs text-muted-foreground">
                    {job.actual_duration ? formatDuration(job.actual_duration) : '-'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className="text-xs text-muted-foreground">
                    {job.worker_id || '-'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <button className="p-1 hover:bg-accent rounded">
                    <MoreVertical className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Error Messages */}
        {jobs.filter((j) => j.status === 'failed').map((job) => (
          <div
            key={`error-${job.id}`}
            className="px-4 py-2 bg-red-500/5 border-b border-red-500/20"
          >
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
        <div className="flex items-center justify-between px-4 py-3 border-t border-border bg-card">
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

function StatCell({
  label,
  value,
  color = 'text-foreground',
}: {
  label: string
  value: string | number
  color?: string
}) {
  return (
    <div className="px-4 py-3 border-r border-border">
      <p className={`text-xl font-semibold ${color}`}>{value}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  )
}