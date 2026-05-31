"""
Worker Telemetry Panel - Worker health and performance monitoring
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Activity,
  Cpu,
  HardDrive,
  MemoryStick,
  Clock,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Signal,
  Server,
} from 'lucide-react'

interface WorkerMetric {
  worker_id: string
  timestamp: string
  cpu_percent: number
  memory_percent: number
  memory_used_mb: number
  memory_available_mb: number
  disk_used_mb: number
  disk_available_mb: number
  jobs_processed: number
  jobs_failed: number
  current_jobs: string[]
}

interface WorkerInfo {
  worker_id: string
  worker_type: string
  status: string
  hostname: string
  last_heartbeat: string
  healthy: boolean
  error_count: number
  uptime_seconds: number
  capabilities: string[]
}

export function WorkerTelemetryPanel() {
  const [workers, setWorkers] = useState<WorkerInfo[]>([])
  const [metrics, setMetrics] = useState<Map<string, WorkerMetric>>(new Map())
  const [selectedWorker, setSelectedWorker] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  // Simulated data
  useEffect(() => {
    const mockWorkers: WorkerInfo[] = [
      {
        worker_id: 'media-worker-1',
        worker_type: 'media',
        status: 'online',
        hostname: 'verse-worker-media-1',
        last_heartbeat: new Date().toISOString(),
        healthy: true,
        error_count: 0,
        uptime_seconds: 86400 * 3,
        capabilities: ['transcode', 'analyze', 'thumbnail'],
      },
      {
        worker_id: 'media-worker-2',
        worker_type: 'media',
        status: 'busy',
        hostname: 'verse-worker-media-2',
        last_heartbeat: new Date().toISOString(),
        healthy: true,
        error_count: 0,
        uptime_seconds: 86400 * 7,
        capabilities: ['transcode', 'analyze', 'thumbnail'],
      },
      {
        worker_id: 'render-worker-1',
        worker_type: 'render',
        status: 'online',
        hostname: 'verse-worker-render-1',
        last_heartbeat: new Date().toISOString(),
        healthy: true,
        error_count: 0,
        uptime_seconds: 86400 * 5,
        capabilities: ['video', 'export', 'composite'],
      },
      {
        worker_id: 'render-worker-2',
        worker_type: 'render',
        status: 'idle',
        hostname: 'verse-worker-render-2',
        last_heartbeat: new Date().toISOString(),
        healthy: true,
        error_count: 0,
        uptime_seconds: 86400 * 2,
        capabilities: ['video', 'export', 'composite'],
      },
      {
        worker_id: 'audio-worker-1',
        worker_type: 'audio',
        status: 'busy',
        hostname: 'verse-worker-audio-1',
        last_heartbeat: new Date().toISOString(),
        healthy: true,
        error_count: 0,
        uptime_seconds: 86400 * 4,
        capabilities: ['analyze', 'waveform', 'bpm'],
      },
    ]

    setWorkers(mockWorkers)

    // Generate mock metrics
    const mockMetrics = new Map<string, WorkerMetric>()
    mockWorkers.forEach((w) => {
      mockMetrics.set(w.worker_id, {
        worker_id: w.worker_id,
        timestamp: new Date().toISOString(),
        cpu_percent: Math.random() * 100,
        memory_percent: Math.random() * 100,
        memory_used_mb: Math.floor(Math.random() * 16000),
        memory_available_mb: Math.floor(Math.random() * 16000),
        disk_used_mb: Math.floor(Math.random() * 500000),
        disk_available_mb: Math.floor(Math.random() * 500000),
        jobs_processed: Math.floor(Math.random() * 1000),
        jobs_failed: Math.floor(Math.random() * 10),
        current_jobs: w.status === 'busy' ? ['job-123', 'job-124'] : [],
      })
    })
    setMetrics(mockMetrics)

    // Update metrics periodically
    const interval = setInterval(() => {
      setMetrics((prev) => {
        const newMetrics = new Map(prev)
        prev.forEach((metric, workerId) => {
          newMetrics.set(workerId, {
            ...metric,
            timestamp: new Date().toISOString(),
            cpu_percent: Math.max(0, Math.min(100, metric.cpu_percent + (Math.random() - 0.5) * 10)),
            memory_percent: Math.max(0, Math.min(100, metric.memory_percent + (Math.random() - 0.5) * 5)),
          })
        })
        return newMetrics
      })
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = (status: string, healthy: boolean) => {
    if (!healthy) return <XCircle className="w-4 h-4 text-red-500" />
    switch (status) {
      case 'online':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />
      case 'busy':
        return <Activity className="w-4 h-4 text-yellow-500 animate-pulse" />
      case 'idle':
        return <Signal className="w-4 h-4 text-blue-500" />
      default:
        return <XCircle className="w-4 h-4 text-gray-500" />
    }
  }

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    if (days > 0) return `${days}d ${hours}h`
    return `${hours}h`
  }

  const selectedMetric = selectedWorker ? metrics.get(selectedWorker) : null

  return (
    <div className="flex flex-col h-full">
      {/* View toggle */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-border">
        <div className="flex items-center gap-2">
          <Server className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium">
            {workers.length} Workers
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setViewMode('grid')}
            className={`px-2 py-1 text-xs rounded ${
              viewMode === 'grid' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'
            }`}
          >
            Grid
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`px-2 py-1 text-xs rounded ${
              viewMode === 'list' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'
            }`}
          >
            List
          </button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Worker list */}
        <div className={`overflow-auto ${selectedWorker ? 'w-1/2 border-r border-border' : 'w-full'}`}>
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-2 gap-2 p-4">
              {workers.map((worker) => {
                const metric = metrics.get(worker.worker_id)
                return (
                  <div
                    key={worker.worker_id}
                    onClick={() => setSelectedWorker(worker.worker_id)}
                    className={`p-3 bg-card/50 rounded-lg cursor-pointer hover:bg-card transition-colors ${
                      selectedWorker === worker.worker_id ? 'ring-2 ring-primary' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      {getStatusIcon(worker.status, worker.healthy)}
                      <span className="text-xs text-muted-foreground capitalize">
                        {worker.worker_type}
                      </span>
                    </div>
                    <p className="text-sm font-medium truncate">{worker.worker_id}</p>
                    <p className="text-xs text-muted-foreground mb-2">
                      {formatUptime(worker.uptime_seconds)} uptime
                    </p>
                    {metric && (
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <Cpu className="w-3 h-3 text-muted-foreground" />
                          <div className="flex-1 h-1 bg-muted rounded-full overflow-hidden">
                            <div
                              className={`h-full ${
                                metric.cpu_percent > 80 ? 'bg-red-500' :
                                metric.cpu_percent > 60 ? 'bg-yellow-500' : 'bg-green-500'
                              }`}
                              style={{ width: `${metric.cpu_percent}%` }}
                            />
                          </div>
                          <span className="text-xs text-muted-foreground w-10">
                            {metric.cpu_percent.toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="divide-y divide-border">
              {workers.map((worker) => {
                const metric = metrics.get(worker.worker_id)
                return (
                  <div
                    key={worker.worker_id}
                    onClick={() => setSelectedWorker(worker.worker_id)}
                    className={`flex items-center gap-4 px-4 py-3 cursor-pointer hover:bg-card/50 ${
                      selectedWorker === worker.worker_id ? 'bg-card' : ''
                    }`}
                  >
                    {getStatusIcon(worker.status, worker.healthy)}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{worker.worker_id}</p>
                      <p className="text-xs text-muted-foreground">
                        {worker.hostname}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs capitalize">{worker.status}</p>
                      <p className="text-xs text-muted-foreground">
                        {formatUptime(worker.uptime_seconds)}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Detail panel */}
        {selectedWorker && selectedMetric && (
          <div className="w-1/2 p-4 overflow-auto">
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium mb-2">System Resources</h3>
                <div className="space-y-3">
                  <MetricBar
                    label="CPU"
                    value={selectedMetric.cpu_percent}
                    icon={<Cpu className="w-4 h-4" />}
                  />
                  <MetricBar
                    label="Memory"
                    value={selectedMetric.memory_percent}
                    subtext={`${selectedMetric.memory_used_mb} / ${selectedMetric.memory_used_mb + selectedMetric.memory_available_mb} MB`}
                    icon={<MemoryStick className="w-4 h-4" />}
                  />
                  <MetricBar
                    label="Disk"
                    value={(selectedMetric.disk_used_mb / (selectedMetric.disk_used_mb + selectedMetric.disk_available_mb)) * 100}
                    subtext={`${(selectedMetric.disk_used_mb / 1024).toFixed(0)} / ${((selectedMetric.disk_used_mb + selectedMetric.disk_available_mb) / 1024).toFixed(0)} GB`}
                    icon={<HardDrive className="w-4 h-4" />}
                  />
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium mb-2">Job Statistics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-card/50 rounded p-3">
                    <p className="text-2xl font-semibold">
                      {selectedMetric.jobs_processed}
                    </p>
                    <p className="text-xs text-muted-foreground">Jobs Completed</p>
                  </div>
                  <div className="bg-card/50 rounded p-3">
                    <p className="text-2xl font-semibold">
                      {selectedMetric.jobs_failed}
                    </p>
                    <p className="text-xs text-muted-foreground">Jobs Failed</p>
                  </div>
                </div>
              </div>

              {selectedMetric.current_jobs.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium mb-2">Current Jobs</h3>
                  <div className="space-y-1">
                    {selectedMetric.current_jobs.map((job) => (
                      <div
                        key={job}
                        className="px-3 py-2 bg-card/50 rounded text-sm"
                      >
                        {job}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function MetricBar({
  label,
  value,
  subtext,
  icon,
}: {
  label: string
  value: number
  subtext?: string
  icon: React.ReactNode
}) {
  const colorClass =
    value > 80 ? 'text-red-500' : value > 60 ? 'text-yellow-500' : 'text-green-500'
  const barClass =
    value > 80 ? 'bg-red-500' : value > 60 ? 'bg-yellow-500' : 'bg-green-500'

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <span className={colorClass}>{icon}</span>
          <span className="text-sm">{label}</span>
        </div>
        <span className={`text-sm font-medium ${colorClass}`}>
          {value.toFixed(1)}%
        </span>
      </div>
      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <div className={`h-full ${barClass} transition-all`} style={{ width: `${value}%` }} />
      </div>
      {subtext && <p className="text-xs text-muted-foreground mt-1">{subtext}</p>}
    </div>
  )
}