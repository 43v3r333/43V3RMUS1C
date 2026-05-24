"""
Orchestration Dashboard - Runtime orchestration and intelligence console
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Activity,
  Cpu,
  Server,
  Zap,
  Clock,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Play,
  Pause,
  RotateCcw,
  Settings,
  Terminal,
  GitBranch,
  Layers,
  Brain,
  HardDrive,
  Gauge,
  TrendingUp,
} from 'lucide-react'

interface PlanData {
  id: string
  name: string
  type: string
  status: 'pending' | 'planning' | 'scheduled' | 'executing' | 'completed' | 'failed'
  priority: 'low' | 'normal' | 'high' | 'urgent'
  progress: number
  steps_total: number
  steps_completed: number
  started_at: string
  estimated_duration: number
}

interface QueueData {
  queue_name: string
  depth: number
  low: number
  normal: number
  high: number
  urgent: number
}

interface WorkerPoolData {
  name: string
  type: string
  active: number
  busy: number
  idle: number
  utilization: number
  jobs_processed: number
}

interface ProviderData {
  name: string
  status: 'healthy' | 'degraded' | 'unavailable'
  latency_ms: number
  success_rate: number
  rate_limit_remaining: number
}

interface OrchestrationDashboardProps {
  onPlanClick?: (planId: string) => void
}

export function OrchestrationDashboard({ onPlanClick }: OrchestrationDashboardProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'plans' | 'workers' | 'ai' | 'analytics'>('overview')
  const [plans, setPlans] = useState<PlanData[]>([])
  const [queues, setQueues] = useState<QueueData[]>([])
  const [workerPools, setWorkerPools] = useState<WorkerPoolData[]>([])
  const [providers, setProviders] = useState<ProviderData[]>([])

  // Simulated data
  useEffect(() => {
    setPlans([
      { id: 'plan-1', name: 'Media Reel Generation', type: 'render', status: 'executing', priority: 'high', progress: 67, steps_total: 12, steps_completed: 8, started_at: new Date(Date.now() - 1800000).toISOString(), estimated_duration: 3600 },
      { id: 'plan-2', name: 'Audio Analysis Pipeline', type: 'analysis', status: 'completed', priority: 'normal', progress: 100, steps_total: 5, steps_completed: 5, started_at: new Date(Date.now() - 3600000).toISOString(), estimated_duration: 1800 },
      { id: 'plan-3', name: 'AI Script Generation', type: 'ai', status: 'pending', priority: 'urgent', progress: 0, steps_total: 3, steps_completed: 0, started_at: new Date().toISOString(), estimated_duration: 600 },
      { id: 'plan-4', name: 'Thumbnail Generation', type: 'media', status: 'failed', priority: 'low', progress: 45, steps_total: 8, steps_completed: 3, started_at: new Date(Date.now() - 7200000).toISOString(), estimated_duration: 900 },
    ])

    setQueues([
      { queue_name: 'render', depth: 12, low: 3, normal: 6, high: 2, urgent: 1 },
      { queue_name: 'ai', depth: 8, low: 1, normal: 4, high: 2, urgent: 1 },
      { queue_name: 'media', depth: 15, low: 8, normal: 5, high: 1, urgent: 1 },
      { queue_name: 'analytics', depth: 5, low: 3, normal: 2, high: 0, urgent: 0 },
    ])

    setWorkerPools([
      { name: 'render-pool', type: 'render', active: 4, busy: 3, idle: 1, utilization: 75, jobs_processed: 234 },
      { name: 'ai-pool', type: 'ai', active: 2, busy: 2, idle: 0, utilization: 100, jobs_processed: 89 },
      { name: 'media-pool', type: 'media', active: 6, busy: 4, idle: 2, utilization: 67, jobs_processed: 456 },
      { name: 'analytics-pool', type: 'analytics', active: 2, busy: 1, idle: 1, utilization: 50, jobs_processed: 123 },
    ])

    setProviders([
      { name: 'openai', status: 'healthy', latency_ms: 145, success_rate: 99.8, rate_limit_remaining: 45000 },
      { name: 'anthropic', status: 'healthy', latency_ms: 230, success_rate: 99.5, rate_limit_remaining: 32000 },
      { name: 'local', status: 'healthy', latency_ms: 45, success_rate: 100, rate_limit_remaining: -1 },
    ])
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-500'
      case 'executing': return 'text-blue-500'
      case 'failed': return 'text-red-500'
      case 'pending': return 'text-muted-foreground'
      case 'planning': return 'text-yellow-500'
      case 'scheduled': return 'text-purple-500'
      default: return 'text-muted-foreground'
    }
  }

  const getPriorityBadge = (priority: string) => {
    const colors = {
      low: 'bg-gray-500/10 text-gray-400',
      normal: 'bg-blue-500/10 text-blue-400',
      high: 'bg-orange-500/10 text-orange-400',
      urgent: 'bg-red-500/10 text-red-400',
    }
    return colors[priority as keyof typeof colors] || colors.normal
  }

  const formatDuration = (seconds: number) => {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${m}m ${s}s`
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-card">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Terminal className="w-5 h-5 text-primary" />
            <h1 className="text-lg font-semibold">Orchestration Center</h1>
          </div>
          
          {/* Quick stats */}
          <div className="flex items-center gap-4 ml-8">
            <MetricDisplay
              icon={<GitBranch className="w-4 h-4" />}
              label="Active Plans"
              value={plans.filter(p => p.status === 'executing' || p.status === 'planning').length.toString()}
            />
            <MetricDisplay
              icon={<Layers className="w-4 h-4" />}
              label="Queues"
              value={queues.reduce((sum, q) => sum + q.depth, 0).toString()}
            />
            <MetricDisplay
              icon={<Server className="w-4 h-4" />}
              label="Workers"
              value={workerPools.reduce((sum, p) => sum + p.active, 0).toString()}
            />
            <MetricDisplay
              icon={<Brain className="w-4 h-4" />}
              label="AI Providers"
              value={providers.filter(p => p.status === 'healthy').length.toString()}
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 px-3 py-1.5 text-sm bg-primary text-primary-foreground rounded hover:bg-primary/90">
            <Play className="w-4 h-4" />
            Create Plan
          </button>
          <button className="p-2 hover:bg-accent rounded">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Tab bar */}
      <div className="flex border-b border-border px-4">
        {(['overview', 'plans', 'workers', 'ai', 'analytics'] as const).map((tab) => (
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
        {activeTab === 'overview' && (
          <div className="space-y-4">
            {/* Key metrics */}
            <div className="grid grid-cols-4 gap-4">
              <MetricCard
                label="Active Plans"
                value={plans.filter(p => p.status === 'executing').length.toString()}
                icon={<GitBranch className="w-5 h-5" />}
                trend="up"
              />
              <MetricCard
                label="Queue Depth"
                value={queues.reduce((sum, q) => sum + q.depth, 0).toString()}
                icon={<Layers className="w-5 h-5" />}
                trend="stable"
              />
              <MetricCard
                label="Avg Utilization"
                value={`${Math.round(workerPools.reduce((sum, p) => sum + p.utilization, 0) / workerPools.length)}%`}
                icon={<Gauge className="w-5 h-5" />}
                trend="up"
              />
              <MetricCard
                label="AI Latency"
                value={`${Math.round(providers.reduce((sum, p) => sum + p.latency_ms, 0) / providers.length)}ms`}
                icon={<Activity className="w-5 h-5" />}
                trend="down"
              />
            </div>

            {/* Worker pools */}
            <div className="border border-border rounded-lg overflow-hidden">
              <div className="px-4 py-3 border-b border-border bg-card">
                <h3 className="text-sm font-medium">Worker Pools</h3>
              </div>
              <div className="divide-y divide-border">
                {workerPools.map((pool) => (
                  <div key={pool.name} className="flex items-center justify-between px-4 py-3">
                    <div className="flex items-center gap-3">
                      <Server className="w-4 h-4 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium">{pool.name}</p>
                        <p className="text-xs text-muted-foreground capitalize">{pool.type}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      <div className="text-sm">
                        <span className="text-green-500">{pool.busy}</span>
                        <span className="text-muted-foreground"> / </span>
                        <span>{pool.active}</span>
                        <span className="text-xs text-muted-foreground ml-1">active</span>
                      </div>
                      <div className="w-24">
                        <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                          <div
                            className={`h-full ${pool.utilization > 80 ? 'bg-red-500' : pool.utilization > 60 ? 'bg-yellow-500' : 'bg-primary'}`}
                            style={{ width: `${pool.utilization}%` }}
                          />
                        </div>
                      </div>
                      <span className="text-xs text-muted-foreground w-12">{pool.utilization}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Active plans */}
            <div className="border border-border rounded-lg overflow-hidden">
              <div className="px-4 py-3 border-b border-border bg-card flex items-center justify-between">
                <h3 className="text-sm font-medium">Active Plans</h3>
                <span className="text-xs text-muted-foreground">
                  {plans.filter(p => p.status === 'executing').length} executing
                </span>
              </div>
              <div className="divide-y divide-border">
                {plans.filter(p => p.status === 'executing').map((plan) => (
                  <div
                    key={plan.id}
                    onClick={() => onPlanClick?.(plan.id)}
                    className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-card/50"
                  >
                    <div className="flex items-center gap-3">
                      {plan.status === 'executing' ? (
                        <Activity className="w-4 h-4 text-blue-500 animate-pulse" />
                      ) : (
                        <CheckCircle2 className="w-4 h-4 text-green-500" />
                      )}
                      <div>
                        <p className="text-sm font-medium">{plan.name}</p>
                        <p className="text-xs text-muted-foreground capitalize">{plan.type}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${getPriorityBadge(plan.priority)}`}>
                        {plan.priority}
                      </span>
                      <div className="w-24">
                        <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary"
                            style={{ width: `${plan.progress}%` }}
                          />
                        </div>
                      </div>
                      <span className="text-xs text-muted-foreground w-12">{plan.progress}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'plans' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  placeholder="Search plans..."
                  className="text-sm bg-transparent border border-border rounded px-3 py-2 w-64"
                />
              </div>
              <button className="flex items-center gap-1 px-3 py-2 text-sm bg-primary text-primary-foreground rounded hover:bg-primary/90">
                <Play className="w-4 h-4" />
                Create Plan
              </button>
            </div>

            <div className="border border-border rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-card">
                  <tr className="text-left text-xs text-muted-foreground uppercase tracking-wider">
                    <th className="px-4 py-3">Plan</th>
                    <th className="px-4 py-3">Type</th>
                    <th className="px-4 py-3">Priority</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Progress</th>
                    <th className="px-4 py-3">Steps</th>
                    <th className="px-4 py-3">Duration</th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody>
                  {plans.map((plan) => (
                    <tr key={plan.id} className="border-t border-border hover:bg-card/50">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          {plan.status === 'executing' && <Activity className="w-4 h-4 text-blue-500 animate-pulse" />}
                          {plan.status === 'completed' && <CheckCircle2 className="w-4 h-4 text-green-500" />}
                          {plan.status === 'failed' && <XCircle className="w-4 h-4 text-red-500" />}
                          <span className="text-sm font-medium">{plan.name}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground capitalize">{plan.type}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${getPriorityBadge(plan.priority)}`}>
                          {plan.priority}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`text-sm capitalize ${getStatusColor(plan.status)}`}>
                          {plan.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 bg-muted rounded-full overflow-hidden">
                            <div
                              className={`h-full ${plan.status === 'failed' ? 'bg-red-500' : plan.status === 'completed' ? 'bg-green-500' : 'bg-primary'}`}
                              style={{ width: `${plan.progress}%` }}
                            />
                          </div>
                          <span className="text-xs text-muted-foreground">{plan.progress}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        {plan.steps_completed}/{plan.steps_total}
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        {formatDuration(plan.estimated_duration)}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1">
                          {plan.status === 'executing' && (
                            <button className="p-1 hover:bg-accent rounded" title="Pause">
                              <Pause className="w-3 h-3" />
                            </button>
                          )}
                          {plan.status === 'failed' && (
                            <button className="p-1 hover:bg-accent rounded" title="Retry">
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

        {activeTab === 'workers' && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {workerPools.map((pool) => (
                <div key={pool.name} className="border border-border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Server className="w-5 h-5 text-primary" />
                      <h3 className="text-sm font-medium">{pool.name}</h3>
                    </div>
                    <span className="text-xs text-muted-foreground capitalize">{pool.type}</span>
                  </div>
                  <div className="grid grid-cols-4 gap-4 mb-4">
                    <div className="text-center">
                      <p className="text-2xl font-semibold">{pool.active}</p>
                      <p className="text-xs text-muted-foreground">Active</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-semibold text-green-500">{pool.busy}</p>
                      <p className="text-xs text-muted-foreground">Busy</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-semibold text-blue-500">{pool.idle}</p>
                      <p className="text-xs text-muted-foreground">Idle</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-semibold">{pool.jobs_processed}</p>
                      <p className="text-xs text-muted-foreground">Jobs</p>
                    </div>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full ${pool.utilization > 80 ? 'bg-red-500' : pool.utilization > 60 ? 'bg-yellow-500' : 'bg-primary'}`}
                      style={{ width: `${pool.utilization}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground mt-2 text-center">
                    {pool.utilization}% utilization
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'ai' && (
          <div className="space-y-4">
            <h3 className="text-sm font-medium">AI Providers</h3>
            <div className="grid grid-cols-3 gap-4">
              {providers.map((provider) => (
                <div key={provider.name} className="border border-border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Brain className="w-5 h-5 text-primary" />
                      <h3 className="text-sm font-medium capitalize">{provider.name}</h3>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      provider.status === 'healthy' ? 'bg-green-500/10 text-green-500' :
                      provider.status === 'degraded' ? 'bg-yellow-500/10 text-yellow-500' :
                      'bg-red-500/10 text-red-500'
                    }`}>
                      {provider.status}
                    </span>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Latency</span>
                      <span className="font-mono">{provider.latency_ms}ms</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Success Rate</span>
                      <span className="font-mono">{provider.success_rate}%</span>
                    </div>
                    {provider.rate_limit_remaining > 0 && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Rate Limit</span>
                        <span className="font-mono">{provider.rate_limit_remaining.toLocaleString()}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Orchestration Analytics</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="border border-border rounded-lg p-4">
                <h4 className="text-xs font-medium text-muted-foreground mb-3">Queue Distribution</h4>
                <div className="space-y-2">
                  {queues.map((queue) => (
                    <div key={queue.queue_name} className="flex items-center justify-between text-sm">
                      <span className="capitalize">{queue.queue_name}</span>
                      <div className="flex items-center gap-4">
                        <div className="flex gap-1">
                          {queue.urgent > 0 && <span className="px-1 bg-red-500/10 text-red-500 text-xs rounded">{queue.urgent}</span>}
                          {queue.high > 0 && <span className="px-1 bg-orange-500/10 text-orange-500 text-xs rounded">{queue.high}</span>}
                          {queue.normal > 0 && <span className="px-1 bg-blue-500/10 text-blue-500 text-xs rounded">{queue.normal}</span>}
                          {queue.low > 0 && <span className="px-1 bg-gray-500/10 text-gray-400 text-xs rounded">{queue.low}</span>}
                        </div>
                        <span className="font-mono text-muted-foreground">{queue.depth}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="border border-border rounded-lg p-4">
                <h4 className="text-xs font-medium text-muted-foreground mb-3">Plan Status Distribution</h4>
                <div className="space-y-2">
                  {['executing', 'completed', 'pending', 'failed'].map((status) => {
                    const count = plans.filter(p => p.status === status).length
                    return (
                      <div key={status} className="flex items-center justify-between text-sm">
                        <span className="capitalize">{status}</span>
                        <span className="font-mono">{count}</span>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
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
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-muted-foreground">{icon}</span>
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="text-sm font-semibold">{value}</p>
      </div>
    </div>
  )
}

function MetricCard({
  label,
  value,
  icon,
  trend,
}: {
  label: string
  value: string
  icon: React.ReactNode
  trend?: 'up' | 'down' | 'stable'
}) {
  return (
    <div className="bg-card border border-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="text-muted-foreground">{icon}</span>
      </div>
      <p className="text-2xl font-semibold">{value}</p>
      {trend && (
        <div className="mt-2">
          {trend === 'up' && <TrendingUp className="w-4 h-4 text-green-500" />}
          {trend === 'down' && <TrendingUp className="w-4 h-4 text-red-500 transform rotate-180" />}
          {trend === 'stable' && <span className="text-xs text-muted-foreground">stable</span>}
        </div>
      )}
    </div>
  )
}