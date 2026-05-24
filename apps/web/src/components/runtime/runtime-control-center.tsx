"""
Runtime Control Center - Enterprise runtime monitoring dashboard
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Activity,
  Cpu,
  HardDrive,
  MemoryStick,
  Server,
  GitBranch,
  Zap,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Pause,
  Play,
  RotateCcw,
  Settings,
  Terminal,
} from 'lucide-react'

interface SessionInfo {
  id: string
  name: string
  status: string
  started_at: string
  uptime_seconds: number
  active_nodes: number
  total_executions: number
  events_processed: number
  events_failed: number
}

interface ExecutionInfo {
  id: string
  name: string
  status: string
  progress: number
  total_nodes: number
  completed_nodes: number
  started_at: string
}

interface SystemMetrics {
  cpu_percent: number
  memory_percent: number
  disk_percent: number
  active_sessions: number
  total_executions: number
  queue_depth: number
}

export function RuntimeControlCenter() {
  const [activeTab, setActiveTab] = useState<'sessions' | 'executions' | 'metrics' | 'logs'>('sessions')
  const [sessions, setSessions] = useState<SessionInfo[]>([])
  const [executions, setExecutions] = useState<ExecutionInfo[]>([])
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null)
  const [selectedSession, setSelectedSession] = useState<string | null>(null)

  // Simulated data updates
  useEffect(() => {
    setSessions([
      {
        id: 'session-1',
        name: 'media-processing-runtime',
        status: 'running',
        started_at: new Date(Date.now() - 3600000).toISOString(),
        uptime_seconds: 3600,
        active_nodes: 5,
        total_executions: 127,
        events_processed: 5432,
        events_failed: 3,
      },
      {
        id: 'session-2',
        name: 'ai-inference-runtime',
        status: 'running',
        started_at: new Date(Date.now() - 7200000).toISOString(),
        uptime_seconds: 7200,
        active_nodes: 2,
        total_executions: 89,
        events_processed: 2341,
        events_failed: 0,
      },
    ])

    setExecutions([
      {
        id: 'exec-1',
        name: 'Media Reel Generation',
        status: 'running',
        progress: 67,
        total_nodes: 12,
        completed_nodes: 8,
        started_at: new Date(Date.now() - 1800000).toISOString(),
      },
      {
        id: 'exec-2',
        name: 'Audio Analysis Pipeline',
        status: 'completed',
        progress: 100,
        total_nodes: 5,
        completed_nodes: 5,
        started_at: new Date(Date.now() - 3600000).toISOString(),
      },
    ])

    setMetrics({
      cpu_percent: 34.5,
      memory_percent: 67.2,
      disk_percent: 45.8,
      active_sessions: 2,
      total_executions: 216,
      queue_depth: 12,
    })

    // Simulate updates
    const interval = setInterval(() => {
      setMetrics((m) => m ? {
        ...m,
        cpu_percent: Math.max(0, Math.min(100, m.cpu_percent + (Math.random() - 0.5) * 5)),
        memory_percent: Math.max(0, Math.min(100, m.memory_percent + (Math.random() - 0.5) * 2)),
      } : null)
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  const formatUptime = (seconds: number) => {
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = seconds % 60
    return `${h}h ${m}m ${s}s`
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-500'
      case 'completed': return 'text-blue-500'
      case 'failed': return 'text-red-500'
      case 'paused': return 'text-yellow-500'
      default: return 'text-muted-foreground'
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-card">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Terminal className="w-5 h-5 text-primary" />
            <h1 className="text-lg font-semibold">Runtime Control Center</h1>
          </div>
          
          {/* Quick stats */}
          <div className="flex items-center gap-6 ml-8">
            <MetricDisplay
              icon={<Activity className="w-4 h-4" />}
              label="Sessions"
              value={sessions.length.toString()}
              color="text-green-500"
            />
            <MetricDisplay
              icon={<Zap className="w-4 h-4" />}
              label="Executions"
              value={executions.length.toString()}
              color="text-blue-500"
            />
            <MetricDisplay
              icon={<Cpu className="w-4 h-4" />}
              label="CPU"
              value={`${metrics?.cpu_percent.toFixed(1) || 0}%`}
              color={metrics?.cpu_percent && metrics.cpu_percent > 80 ? 'text-red-500' : 'text-foreground'}
            />
            <MetricDisplay
              icon={<MemoryStick className="w-4 h-4" />}
              label="Memory"
              value={`${metrics?.memory_percent.toFixed(1) || 0}%`}
              color={metrics?.memory_percent && metrics.memory_percent > 80 ? 'text-red-500' : 'text-foreground'}
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 px-3 py-1.5 text-sm bg-primary text-primary-foreground rounded hover:bg-primary/90">
            <Play className="w-4 h-4" />
            Start Session
          </button>
          <button className="p-2 hover:bg-accent rounded">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Tab bar */}
      <div className="flex border-b border-border px-4">
        {(['sessions', 'executions', 'metrics', 'logs'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {activeTab === 'sessions' && (
          <div className="space-y-4">
            {/* Session cards */}
            <div className="grid grid-cols-2 gap-4">
              {sessions.map((session) => (
                <SessionCard
                  key={session.id}
                  session={session}
                  selected={selectedSession === session.id}
                  onSelect={() => setSelectedSession(session.id)}
                  formatUptime={formatUptime}
                  getStatusColor={getStatusColor}
                />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'executions' && (
          <div className="space-y-4">
            {/* Execution list */}
            <div className="border border-border rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-card">
                  <tr className="text-left text-xs text-muted-foreground uppercase tracking-wider">
                    <th className="px-4 py-3">Execution</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Progress</th>
                    <th className="px-4 py-3">Nodes</th>
                    <th className="px-4 py-3">Started</th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody>
                  {executions.map((exec) => (
                    <tr key={exec.id} className="border-t border-border hover:bg-card/50">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <GitBranch className="w-4 h-4 text-muted-foreground" />
                          <span className="font-medium">{exec.name}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`flex items-center gap-1.5 text-sm ${getStatusColor(exec.status)}`}>
                          {exec.status === 'running' && <Activity className="w-3 h-3 animate-pulse" />}
                          {exec.status === 'completed' && <CheckCircle2 className="w-3 h-3" />}
                          {exec.status === 'failed' && <XCircle className="w-3 h-3" />}
                          {exec.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-1.5 bg-muted rounded-full overflow-hidden">
                            <div
                              className={`h-full ${exec.status === 'failed' ? 'bg-red-500' : exec.status === 'completed' ? 'bg-green-500' : 'bg-primary'}`}
                              style={{ width: `${exec.progress}%` }}
                            />
                          </div>
                          <span className="text-xs text-muted-foreground">{exec.progress}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        {exec.completed_nodes}/{exec.total_nodes}
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        {new Date(exec.started_at).toLocaleTimeString()}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1">
                          {exec.status === 'running' && (
                            <button className="p-1.5 hover:bg-accent rounded" title="Pause">
                              <Pause className="w-3 h-3" />
                            </button>
                          )}
                          {exec.status === 'failed' && (
                            <button className="p-1.5 hover:bg-accent rounded" title="Retry">
                              <RotateCcw className="w-3 h-3" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'metrics' && metrics && (
          <div className="grid grid-cols-3 gap-4">
            <MetricCard
              label="CPU Usage"
              value={`${metrics.cpu_percent.toFixed(1)}%`}
              icon={<Cpu className="w-5 h-5" />}
              progress={metrics.cpu_percent}
            />
            <MetricCard
              label="Memory Usage"
              value={`${metrics.memory_percent.toFixed(1)}%`}
              icon={<MemoryStick className="w-5 h-5" />}
              progress={metrics.memory_percent}
            />
            <MetricCard
              label="Disk Usage"
              value={`${metrics.disk_percent.toFixed(1)}%`}
              icon={<HardDrive className="w-5 h-5" />}
              progress={metrics.disk_percent}
            />
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="font-mono text-xs bg-card border border-border rounded-lg p-4 h-96 overflow-auto">
            {sessions.map((session) => (
              <div key={session.id} className="mb-4">
                <p className="text-muted-foreground">[{new Date().toISOString()}] INFO: Session {session.name} status: {session.status}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function MetricDisplay({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode
  label: string
  value: string
  color?: string
}) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-muted-foreground">{icon}</span>
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className={`text-sm font-semibold ${color || ''}`}>{value}</p>
      </div>
    </div>
  )
}

function SessionCard({
  session,
  selected,
  onSelect,
  formatUptime,
  getStatusColor,
}: {
  session: SessionInfo
  selected: boolean
  onSelect: () => void
  formatUptime: (s: number) => string
  getStatusColor: (s: string) => string
}) {
  return (
    <div
      onClick={onSelect}
      className={`bg-card border rounded-lg p-4 cursor-pointer transition-colors ${
        selected ? 'border-primary ring-1 ring-primary' : 'border-border hover:border-primary/50'
      }`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Server className="w-4 h-4 text-primary" />
          <span className="font-medium">{session.name}</span>
        </div>
        <span className={`text-sm ${getStatusColor(session.status)}`}>
          {session.status}
        </span>
      </div>

      <div className="grid grid-cols-4 gap-4 text-sm">
        <div>
          <p className="text-xs text-muted-foreground">Uptime</p>
          <p className="font-mono">{formatUptime(session.uptime_seconds)}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Active Nodes</p>
          <p className="font-mono">{session.active_nodes}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Executions</p>
          <p className="font-mono">{session.total_executions}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Events</p>
          <p className="font-mono">{session.events_processed.toLocaleString()}</p>
        </div>
      </div>

      {session.events_failed > 0 && (
        <div className="flex items-center gap-1 mt-3 text-red-500 text-xs">
          <AlertTriangle className="w-3 h-3" />
          {session.events_failed} failed events
        </div>
      )}
    </div>
  )
}

function MetricCard({
  label,
  value,
  icon,
  progress,
}: {
  label: string
  value: string
  icon: React.ReactNode
  progress: number
}) {
  return (
    <div className="bg-card border border-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium">{label}</span>
        <span className="text-muted-foreground">{icon}</span>
      </div>
      <p className="text-3xl font-semibold mb-4">{value}</p>
      <div className="h-1.5 bg-muted rounded-full overflow-hidden">
        <div
          className={`h-full ${progress > 80 ? 'bg-red-500' : progress > 60 ? 'bg-yellow-500' : 'bg-primary'}`}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  )
}