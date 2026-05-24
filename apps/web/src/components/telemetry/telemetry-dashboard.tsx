"""
Telemetry Dashboard - Production observability console
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  Cpu,
  Server,
  TrendingUp,
  TrendingDown,
  Minus,
  Eye,
  Filter,
  Download,
  RefreshCw,
} from 'lucide-react'

interface MetricData {
  name: string
  value: number
  previous_value: number
  unit: string
  timestamp: string
}

interface AlertData {
  id: string
  name: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  source: string
  message: string
  timestamp: string
  acknowledged: boolean
}

interface TraceData {
  trace_id: string
  operation: string
  duration_ms: number
  status: 'completed' | 'failed' | 'running'
  timestamp: string
}

interface EventData {
  id: string
  type: string
  source: string
  severity: string
  message: string
  timestamp: string
}

interface TelemetryMetrics {
  cpu_percent: number
  memory_percent: number
  disk_percent: number
  active_sessions: number
  total_traces: number
  error_rate: number
  avg_latency_ms: number
  uptime_seconds: number
}

export function TelemetryDashboard() {
  const [activeTab, setActiveTab] = useState<'overview' | 'traces' | 'alerts' | 'events'>('overview')
  const [metrics, setMetrics] = useState<TelemetryMetrics | null>(null)
  const [alerts, setAlerts] = useState<AlertData[]>([])
  const [traces, setTraces] = useState<TraceData[]>([])
  const [events, setEvents] = useState<EventData[]>([])
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('1h')

  // Simulated data
  useEffect(() => {
    setMetrics({
      cpu_percent: 45.2,
      memory_percent: 67.8,
      disk_percent: 34.5,
      active_sessions: 8,
      total_traces: 12543,
      error_rate: 0.02,
      avg_latency_ms: 125,
      uptime_seconds: 864000,
    })

    setAlerts([
      {
        id: 'alert-1',
        name: 'High Memory Usage',
        severity: 'warning',
        source: 'worker-01',
        message: 'Memory usage exceeded 80% threshold',
        timestamp: new Date(Date.now() - 300000).toISOString(),
        acknowledged: false,
      },
      {
        id: 'alert-2',
        name: 'Worker Offline',
        severity: 'error',
        source: 'render-worker-3',
        message: 'Worker disconnected unexpectedly',
        timestamp: new Date(Date.now() - 1200000).toISOString(),
        acknowledged: true,
      },
      {
        id: 'alert-3',
        name: 'High Error Rate',
        severity: 'critical',
        source: 'api-gateway',
        message: 'Error rate exceeded 5% threshold',
        timestamp: new Date(Date.now() - 600000).toISOString(),
        acknowledged: false,
      },
    ])

    setTraces([
      { trace_id: 'trace-001', operation: 'workflow.execute', duration_ms: 245, status: 'completed', timestamp: new Date(Date.now() - 10000).toISOString() },
      { trace_id: 'trace-002', operation: 'media.transcode', duration_ms: 1523, status: 'completed', timestamp: new Date(Date.now() - 20000).toISOString() },
      { trace_id: 'trace-003', operation: 'ai.generate', duration_ms: 890, status: 'completed', timestamp: new Date(Date.now() - 30000).toISOString() },
      { trace_id: 'trace-004', operation: 'render.composite', duration_ms: 0, status: 'running', timestamp: new Date(Date.now() - 5000).toISOString() },
      { trace_id: 'trace-005', operation: 'timeline.sync', duration_ms: 56, status: 'failed', timestamp: new Date(Date.now() - 40000).toISOString() },
    ])

    setEvents([
      { id: 'evt-1', type: 'execution.started', source: 'runtime-1', severity: 'info', message: 'Workflow execution started', timestamp: new Date(Date.now() - 5000).toISOString() },
      { id: 'evt-2', type: 'render.completed', source: 'render-worker-1', severity: 'info', message: 'Render job completed successfully', timestamp: new Date(Date.now() - 15000).toISOString() },
      { id: 'evt-3', type: 'worker.heartbeat', source: 'media-worker-2', severity: 'info', message: 'Worker heartbeat received', timestamp: new Date(Date.now() - 30000).toISOString() },
    ])

    const interval = setInterval(() => {
      setMetrics((m) => m ? {
        ...m,
        cpu_percent: Math.max(0, Math.min(100, m.cpu_percent + (Math.random() - 0.5) * 5)),
        memory_percent: Math.max(0, Math.min(100, m.memory_percent + (Math.random() - 0.5) * 2)),
      } : null)
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const getTrend = (current: number, previous: number) => {
    const diff = current - previous
    if (diff > 0) return 'up'
    if (diff < 0) return 'down'
    return 'stable'
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-500 bg-red-500/10'
      case 'error': return 'text-red-400 bg-red-400/10'
      case 'warning': return 'text-yellow-500 bg-yellow-500/10'
      case 'info': return 'text-blue-500 bg-blue-500/10'
      default: return 'text-muted-foreground bg-muted/10'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle2 className="w-4 h-4 text-green-500" />
      case 'failed': return <XCircle className="w-4 h-4 text-red-500" />
      case 'running': return <Activity className="w-4 h-4 text-blue-500 animate-pulse" />
      default: return <Clock className="w-4 h-4 text-muted-foreground" />
    }
  }

  const formatUptime = (seconds: number) => {
    const d = Math.floor(seconds / 86400)
    const h = Math.floor((seconds % 86400) / 3600)
    return `${d}d ${h}h`
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-card">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-primary" />
            <h1 className="text-lg font-semibold">Telemetry Dashboard</h1>
          </div>
          
          <div className="flex items-center gap-2 ml-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as any)}
              className="text-xs bg-transparent border border-border rounded px-2 py-1"
            >
              <option value="1h">Last 1 hour</option>
              <option value="6h">Last 6 hours</option>
              <option value="24h">Last 24 hours</option>
              <option value="7d">Last 7 days</option>
            </select>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1 px-3 py-1.5 text-sm hover:bg-accent rounded">
            <Download className="w-4 h-4" />
            Export
          </button>
          <button className="flex items-center gap-1 px-3 py-1.5 text-sm hover:bg-accent rounded">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Tab bar */}
      <div className="flex border-b border-border px-4">
        {(['overview', 'traces', 'alerts', 'events'] as const).map((tab) => (
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
        {activeTab === 'overview' && metrics && (
          <div className="space-y-4">
            {/* Key metrics */}
            <div className="grid grid-cols-4 gap-4">
              <MetricCard
                label="CPU Usage"
                value={`${metrics.cpu_percent.toFixed(1)}%`}
                icon={<Cpu className="w-5 h-5" />}
                trend={getTrend(metrics.cpu_percent, 40)}
                progress={metrics.cpu_percent}
              />
              <MetricCard
                label="Memory"
                value={`${metrics.memory_percent.toFixed(1)}%`}
                icon={<Server className="w-5 h-5" />}
                trend={getTrend(metrics.memory_percent, 65)}
                progress={metrics.memory_percent}
              />
              <MetricCard
                label="Active Sessions"
                value={metrics.active_sessions.toString()}
                icon={<Activity className="w-5 h-5" />}
                trend="stable"
              />
              <MetricCard
                label="Error Rate"
                value={`${(metrics.error_rate * 100).toFixed(2)}%`}
                icon={<AlertTriangle className="w-5 h-5" />}
                trend={getTrend(metrics.error_rate, 0.03)}
                status={metrics.error_rate > 0.05 ? 'critical' : metrics.error_rate > 0.01 ? 'warning' : 'normal'}
              />
            </div>

            {/* Performance metrics */}
            <div className="grid grid-cols-3 gap-4">
              <PerformanceCard
                label="Avg Latency"
                value={`${metrics.avg_latency_ms}ms`}
                icon={<Clock className="w-4 h-4" />}
              />
              <PerformanceCard
                label="Total Traces"
                value={metrics.total_traces.toLocaleString()}
                icon={<Activity className="w-4 h-4" />}
              />
              <PerformanceCard
                label="Uptime"
                value={formatUptime(metrics.uptime_seconds)}
                icon={<TrendingUp className="w-4 h-4" />}
              />
            </div>

            {/* Quick alert summary */}
            <div className="border border-border rounded-lg overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-card">
                <span className="text-sm font-medium">Active Alerts</span>
                <span className="text-xs text-muted-foreground">{alerts.filter(a => !a.acknowledged).length} unacknowledged</span>
              </div>
              <div className="divide-y divide-border">
                {alerts.slice(0, 3).map((alert) => (
                  <div key={alert.id} className="flex items-center gap-3 px-4 py-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${getSeverityColor(alert.severity)}`}>
                      {alert.severity}
                    </span>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{alert.name}</p>
                      <p className="text-xs text-muted-foreground">{alert.source}</p>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'traces' && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search traces..."
                className="flex-1 max-w-md text-sm bg-transparent border border-border rounded px-3 py-2"
              />
            </div>

            <div className="border border-border rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-card">
                  <tr className="text-left text-xs text-muted-foreground uppercase tracking-wider">
                    <th className="px-4 py-3">Trace ID</th>
                    <th className="px-4 py-3">Operation</th>
                    <th className="px-4 py-3">Duration</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Timestamp</th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody>
                  {traces.map((trace) => (
                    <tr key={trace.trace_id} className="border-t border-border hover:bg-card/50">
                      <td className="px-4 py-3 font-mono text-xs">{trace.trace_id}</td>
                      <td className="px-4 py-3 text-sm">{trace.operation}</td>
                      <td className="px-4 py-3 font-mono text-sm">{trace.duration_ms}ms</td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(trace.status)}
                          <span className="text-sm capitalize">{trace.status}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-xs text-muted-foreground">
                        {new Date(trace.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="px-4 py-3">
                        <button className="p-1 hover:bg-accent rounded" title="View details">
                          <Eye className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'alerts' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-sm text-muted-foreground">
                  {alerts.filter(a => !a.acknowledged).length} active alerts
                </span>
              </div>
              <button className="flex items-center gap-1 px-3 py-1.5 text-sm bg-primary text-primary-foreground rounded hover:bg-primary/90">
                Create Alert
              </button>
            </div>

            <div className="space-y-2">
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`border rounded-lg p-4 ${alert.acknowledged ? 'opacity-60' : ''}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${getSeverityColor(alert.severity)}`}>
                        {alert.severity}
                      </span>
                      <div>
                        <p className="text-sm font-medium">{alert.name}</p>
                        <p className="text-xs text-muted-foreground">{alert.message}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">
                        {new Date(alert.timestamp).toLocaleString()}
                      </span>
                      {!alert.acknowledged && (
                        <button className="text-xs text-primary hover:underline">
                          Acknowledge
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'events' && (
          <div className="space-y-2">
            {events.map((event) => (
              <div key={event.id} className="border border-border rounded-lg px-4 py-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${getSeverityColor(event.severity)}`}>
                      {event.severity}
                    </span>
                    <div>
                      <p className="text-sm font-medium">{event.type}</p>
                      <p className="text-xs text-muted-foreground">{event.message}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span>{event.source}</span>
                    <span>{new Date(event.timestamp).toLocaleTimeString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function MetricCard({
  label,
  value,
  icon,
  trend,
  progress,
  status,
}: {
  label: string
  value: string
  icon: React.ReactNode
  trend?: 'up' | 'down' | 'stable'
  progress?: number
  status?: 'normal' | 'warning' | 'critical'
}) {
  const getTrendIcon = () => {
    if (trend === 'up') return <TrendingUp className="w-3 h-3 text-red-500" />
    if (trend === 'down') return <TrendingDown className="w-3 h-3 text-green-500" />
    return <Minus className="w-3 h-3 text-muted-foreground" />
  }

  const statusColors = {
    normal: 'text-foreground',
    warning: 'text-yellow-500',
    critical: 'text-red-500',
  }

  return (
    <div className="bg-card border border-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="text-muted-foreground">{icon}</span>
      </div>
      <p className={`text-2xl font-semibold ${status ? statusColors[status] : ''}`}>{value}</p>
      <div className="flex items-center justify-between mt-2">
        {trend && getTrendIcon()}
        {progress !== undefined && (
          <div className="flex-1 ml-2">
            <div className="h-1.5 bg-muted rounded-full overflow-hidden">
              <div
                className={`h-full ${progress > 80 ? 'bg-red-500' : progress > 60 ? 'bg-yellow-500' : 'bg-primary'}`}
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function PerformanceCard({
  label,
  value,
  icon,
}: {
  label: string
  value: string
  icon: React.ReactNode
}) {
  return (
    <div className="bg-card border border-border rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-muted-foreground">{icon}</span>
        <span className="text-sm text-muted-foreground">{label}</span>
      </div>
      <p className="text-xl font-semibold">{value}</p>
    </div>
  )
}