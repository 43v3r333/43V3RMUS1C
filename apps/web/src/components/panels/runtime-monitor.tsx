"""
Runtime Monitor - Real-time runtime monitoring panel
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Activity,
  Cpu,
  HardDrive,
  MemoryStick,
  Gauge,
  Clock,
  AlertTriangle,
  CheckCircle2,
  XCircle,
} from 'lucide-react'

interface SystemMetrics {
  cpu_percent: number
  memory_percent: number
  memory_used_mb: number
  memory_available_mb: number
  disk_used_mb: number
  disk_available_mb: number
  timestamp: string
}

interface WorkerHealth {
  worker_id: string
  status: string
  last_heartbeat: string
  healthy: boolean
  error_count: number
  uptime_seconds: number
  capabilities: string[]
}

interface QueueStats {
  total: number
  queued: number
  processing: number
  completed: number
  failed: number
}

interface RuntimeMonitorProps {
  onWorkerClick?: (workerId: string) => void
  onJobClick?: (jobId: string) => void
}

export function RuntimeMonitor({
  onWorkerClick,
  onJobClick,
}: RuntimeMonitorProps) {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null)
  const [workers, setWorkers] = useState<WorkerHealth[]>([])
  const [queueStats, setQueueStats] = useState<QueueStats>({
    total: 0,
    queued: 0,
    processing: 0,
    completed: 0,
    failed: 0,
  })
  const [selectedTab, setSelectedTab] = useState<'workers' | 'queue' | 'metrics'>('workers')

  // Simulated data updates (in production, this would be WebSocket)
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics({
        cpu_percent: Math.random() * 100,
        memory_percent: Math.random() * 100,
        memory_used_mb: Math.floor(Math.random() * 8000),
        memory_available_mb: Math.floor(Math.random() * 8000),
        disk_used_mb: Math.floor(Math.random() * 500000),
        disk_available_mb: Math.floor(Math.random() * 500000),
        timestamp: new Date().toISOString(),
      })

      setQueueStats({
        total: Math.floor(Math.random() * 100),
        queued: Math.floor(Math.random() * 30),
        processing: Math.floor(Math.random() * 10),
        completed: Math.floor(Math.random() * 80),
        failed: Math.floor(Math.random() * 5),
      })
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  const getWorkerStatusIcon = (status: string, healthy: boolean) => {
    if (!healthy) return <XCircle className="w-4 h-4 text-red-500" />
    switch (status) {
      case 'online':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />
      case 'busy':
        return <Activity className="w-4 h-4 text-yellow-500 animate-pulse" />
      case 'idle':
        return <Activity className="w-4 h-4 text-blue-500" />
      default:
        return <XCircle className="w-4 h-4 text-gray-500" />
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Tab Bar */}
      <div className="flex border-b border-border px-2">
        {(['workers', 'queue', 'metrics'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setSelectedTab(tab)}
            className={`px-4 py-2 text-xs font-medium uppercase tracking-wider border-b-2 ${
              selectedTab === tab
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {selectedTab === 'workers' && (
          <div className="divide-y divide-border">
            {/* Worker list */}
            {workers.length === 0 ? (
              <div className="p-4 text-center text-muted-foreground text-sm">
                No workers connected
              </div>
            ) : (
              workers.map((worker) => (
                <div
                  key={worker.worker_id}
                  onClick={() => onWorkerClick?.(worker.worker_id)}
                  className="flex items-center gap-3 px-4 py-3 hover:bg-card/50 cursor-pointer"
                >
                  {getWorkerStatusIcon(worker.status, worker.healthy)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      {worker.worker_id}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {worker.status} • {Math.floor(worker.uptime_seconds / 60)}m uptime
                    </p>
                  </div>
                  {worker.error_count > 0 && (
                    <AlertTriangle className="w-4 h-4 text-red-500" />
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {selectedTab === 'queue' && (
          <div className="p-4">
            {/* Queue stats */}
            <div className="grid grid-cols-5 gap-2 mb-4">
              <QueueStatCard
                label="Total"
                value={queueStats.total}
                color="bg-blue-500/10 text-blue-500"
              />
              <QueueStatCard
                label="Queued"
                value={queueStats.queued}
                color="bg-yellow-500/10 text-yellow-500"
              />
              <QueueStatCard
                label="Processing"
                value={queueStats.processing}
                color="bg-green-500/10 text-green-500"
              />
              <QueueStatCard
                label="Completed"
                value={queueStats.completed}
                color="bg-emerald-500/10 text-emerald-500"
              />
              <QueueStatCard
                label="Failed"
                value={queueStats.failed}
                color="bg-red-500/10 text-red-500"
              />
            </div>
          </div>
        )}

        {selectedTab === 'metrics' && metrics && (
          <div className="p-4 space-y-4">
            {/* CPU */}
            <MetricCard
              label="CPU Usage"
              value={`${metrics.cpu_percent.toFixed(1)}%`}
              icon={<Cpu className="w-4 h-4" />}
              progress={metrics.cpu_percent}
              color={metrics.cpu_percent > 80 ? 'red' : metrics.cpu_percent > 60 ? 'yellow' : 'blue'}
            />
            
            {/* Memory */}
            <MetricCard
              label="Memory"
              value={`${metrics.memory_percent.toFixed(1)}%`}
              subtext={`${metrics.memory_used_mb} / ${metrics.memory_used_mb + metrics.memory_available_mb} MB`}
              icon={<MemoryStick className="w-4 h-4" />}
              progress={metrics.memory_percent}
              color={metrics.memory_percent > 80 ? 'red' : metrics.memory_percent > 60 ? 'yellow' : 'blue'}
            />
            
            {/* Disk */}
            <MetricCard
              label="Disk"
              value={`${((metrics.disk_used_mb / (metrics.disk_used_mb + metrics.disk_available_mb)) * 100).toFixed(1)}%`}
              subtext={`${(metrics.disk_used_mb / 1024).toFixed(1)} / ${((metrics.disk_used_mb + metrics.disk_available_mb) / 1024).toFixed(1)} GB`}
              icon={<HardDrive className="w-4 h-4" />}
              progress={(metrics.disk_used_mb / (metrics.disk_used_mb + metrics.disk_available_mb)) * 100}
              color="blue"
            />
          </div>
        )}
      </div>
    </div>
  )
}

function QueueStatCard({
  label,
  value,
  color,
}: {
  label: string
  value: number
  color: string
}) {
  return (
    <div className={`${color} rounded p-3 text-center`}>
      <p className="text-2xl font-semibold">{value}</p>
      <p className="text-xs opacity-80">{label}</p>
    </div>
  )
}

function MetricCard({
  label,
  value,
  subtext,
  icon,
  progress,
  color,
}: {
  label: string
  value: string
  subtext?: string
  icon: React.ReactNode
  progress: number
  color: 'red' | 'yellow' | 'blue'
}) {
  const colorClasses = {
    red: 'bg-red-500',
    yellow: 'bg-yellow-500',
    blue: 'bg-blue-500',
  }

  return (
    <div className="bg-card/50 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-medium">{label}</span>
        </div>
        <span className="text-lg font-semibold">{value}</span>
      </div>
      {subtext && (
        <p className="text-xs text-muted-foreground mb-2">{subtext}</p>
      )}
      <div className="h-1.5 bg-muted rounded-full overflow-hidden">
        <div
          className={`h-full ${colorClasses[color]} transition-all`}
          style={{ width: `${Math.min(100, progress)}%` }}
        />
      </div>
    </div>
  )
}