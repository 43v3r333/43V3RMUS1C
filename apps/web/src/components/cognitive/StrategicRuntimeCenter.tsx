"""
Strategic Runtime Center

Strategic execution planning interface with plan management,
objective tracking, and orchestration coordination.
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Target,
  Clock,
  TrendingUp,
  Layers,
  ChevronRight,
  Play,
  Pause,
  CheckCircle2,
  AlertTriangle,
  Zap,
} from 'lucide-react'
import { useCognitiveApi, type StrategicPlan, type PlanningStatistics } from '@/lib/cognitive-api'
import { ConsolePanel, DataTable, TabBar, IconButton, ProgressBar, StatusDot, ConfidenceBadge } from './primitives'

interface PlanWithStats extends StrategicPlan {
  progress?: number
  blockingIssues?: string[]
}

export default function StrategicRuntimeCenter() {
  const api = useCognitiveApi()
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [plans, setPlans] = useState<StrategicPlan[]>([])
  const [stats, setStats] = useState<PlanningStatistics | null>(null)

  useEffect(() => {
    const loadData = async () => {
      try {
        const [plansData, statsData] = await Promise.all([
          api.listPlans({ limit: 50 }),
          api.getPlanningStats(),
        ])
        setPlans(plansData.items)
        setStats(statsData)
      } catch {
        // Use mock data
        setPlans([
          {
            id: 'p1', name: 'Summer Campaign Pipeline', plan_type: 'workflow', status: 'active',
            horizon: 'medium_term', strategy_kind: 'creative_direction', objectives: [],
            confidence_score: 0.82, priority: 8, created_at: new Date().toISOString(),
          },
          {
            id: 'p2', name: 'Q4 Render Infrastructure', plan_type: 'render', status: 'draft',
            horizon: 'long_term', strategy_kind: 'resource_allocation', objectives: [],
            confidence_score: 0.65, priority: 6, created_at: new Date().toISOString(),
          },
        ])
        setStats({
          total_plans: 12, by_status: { active: 5, draft: 4, completed: 3 },
          by_strategy: { creative_direction: 4, resource_allocation: 3, workflow_optimization: 5 },
          avg_confidence: 0.74, active_count: 5, completed_count: 3,
        })
      }
      setLoading(false)
    }

    loadData()
    const interval = setInterval(loadData, 45000)
    return () => clearInterval(interval)
  }, [api])

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Target className="h-3 w-3" /> },
    { id: 'plans', label: 'Plans', icon: <Layers className="h-3 w-3" />, badge: plans.length },
    { id: 'forecasts', label: 'Forecasts', icon: <TrendingUp className="h-3 w-3" /> },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Target className="h-5 w-5" />
            Strategic Runtime Center
          </h2>
          <p className="text-xs text-muted-foreground">
            Predictive orchestration planning and execution coordination
          </p>
        </div>
        <div className="flex items-center gap-2">
          <StatusDot status="active" pulse />
          <span className="text-xs text-muted-foreground">Real-time</span>
        </div>
      </div>

      <TabBar tabs={tabs} active={activeTab} onChange={setActiveTab} />

      {activeTab === 'overview' && (
        <>
          {/* Key Metrics */}
          <div className="grid gap-4 lg:grid-cols-4">
            <ConsolePanel title="Active Plans" icon={<Target className="h-4 w-4" />} subtitle="Currently executing">
              <div className="text-2xl font-mono font-bold">{stats?.active_count || 0}</div>
              <div className="text-xs text-muted-foreground mt-1">
                of {stats?.total_plans || 0} total
              </div>
            </ConsolePanel>

            <ConsolePanel title="Completed" icon={<CheckCircle2 className="h-4 w-4" />} subtitle="Successfully finished">
              <div className="text-2xl font-mono font-bold text-green-500">{stats?.completed_count || 0}</div>
              <div className="text-xs text-muted-foreground mt-1">this period</div>
            </ConsolePanel>

            <ConsolePanel title="Avg Confidence" icon={<TrendingUp className="h-4 w-4" />} subtitle="Plan reliability">
              <div className="text-2xl font-mono font-bold">
                {stats ? `${Math.round(stats.avg_confidence * 100)}%` : '—'}
              </div>
              <ConfidenceBadge value={stats?.avg_confidence || 0.5} />
            </ConsolePanel>

            <ConsolePanel title="By Strategy" icon={<Layers className="h-4 w-4" />} subtitle="Distribution">
              <div className="space-y-1">
                {stats && Object.entries(stats.by_strategy).slice(0, 3).map(([kind, count]) => (
                  <div key={kind} className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground truncate">{kind}</span>
                    <span className="font-mono">{count}</span>
                  </div>
                ))}
              </div>
            </ConsolePanel>
          </div>

          {/* Active Plans Overview */}
          <ConsolePanel title="Strategic Execution" icon={<Target className="h-4 w-4" />} subtitle="Active plan monitoring">
            <div className="space-y-3">
              {plans.filter(p => p.status === 'active').map(plan => (
                <div key={plan.id} className="border border-border rounded p-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <StatusDot status="active" />
                      <span className="text-sm font-medium">{plan.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{plan.horizon}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-500">{plan.strategy_kind}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 text-xs">
                      <span className="text-muted-foreground">Priority</span>
                      <span className="font-mono">{plan.priority}/10</span>
                    </div>
                    <ConfidenceBadge value={plan.confidence_score} />
                  </div>
                </div>
              ))}
              {plans.filter(p => p.status === 'active').length === 0 && (
                <div className="text-center py-4 text-muted-foreground text-sm">No active plans</div>
              )}
            </div>
          </ConsolePanel>
        </>
      )}

      {activeTab === 'plans' && (
        <ConsolePanel title="Strategic Plans" icon={<Layers className="h-4 w-4" />} subtitle="All execution plans">
          <DataTable
            columns={[
              { key: 'name', label: 'Plan', width: '25%' },
              { key: 'status', label: 'Status', width: '12%' },
              { key: 'horizon', label: 'Horizon', width: '12%' },
              { key: 'strategy', label: 'Strategy', width: '15%' },
              { key: 'priority', label: 'Priority', width: '10%' },
              { key: 'confidence', label: 'Confidence', width: '12%' },
              { key: 'actions', label: '', width: '14%' },
            ]}
            rows={plans.map(plan => ({
              name: (
                <div className="flex items-center gap-2">
                  <StatusDot status={plan.status === 'active' ? 'active' : plan.status === 'draft' ? 'idle' : 'processing'} />
                  <span className="truncate font-medium">{plan.name}</span>
                </div>
              ),
              status: (
                <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                  plan.status === 'active' ? 'bg-green-500/10 text-green-500' :
                  plan.status === 'draft' ? 'bg-muted text-muted-foreground' :
                  plan.status === 'completed' ? 'bg-blue-500/10 text-blue-500' :
                  'bg-yellow-500/10 text-yellow-500'
                }`}>{plan.status}</span>
              ),
              horizon: <span className="text-xs">{plan.horizon}</span>,
              strategy: <span className="text-xs text-muted-foreground truncate">{plan.strategy_kind}</span>,
              priority: <span className="font-mono">{plan.priority}</span>,
              confidence: <ConfidenceBadge value={plan.confidence_score} />,
              actions: (
                <div className="flex items-center gap-1">
                  {plan.status === 'draft' && (
                    <IconButton icon={<Play className="h-3 w-3" />} title="Activate" size="sm" />
                  )}
                  {plan.status === 'active' && (
                    <IconButton icon={<Pause className="h-3 w-3" />} title="Pause" size="sm" />
                  )}
                  <IconButton icon={<ChevronRight className="h-3 w-3" />} title="Details" size="sm" />
                </div>
              ),
            }))}
          />
        </ConsolePanel>
      )}

      {activeTab === 'forecasts' && (
        <ConsolePanel title="Execution Forecasts" icon={<TrendingUp className="h-4 w-4" />} subtitle="Predictive orchestration">
          <div className="space-y-3">
            <div className="text-sm text-muted-foreground mb-3">Active forecasts across all subjects</div>
            {[
              { kind: 'duration', subject: 'render-alpha-001', horizon: 'near_term', value: '245s', confidence: 0.85 },
              { kind: 'queue_time', subject: 'job-bridge-42', horizon: 'short', value: '45s', confidence: 0.78 },
              { kind: 'failure_probability', subject: 'compose-music-v3', horizon: 'extended', value: '12%', confidence: 0.72 },
            ].map((fc, i) => (
              <div key={i} className="flex items-center justify-between p-2 border border-border rounded">
                <div className="flex items-center gap-3">
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{fc.kind}</span>
                  <span className="text-xs font-mono">{fc.subject}</span>
                  <span className="text-[10px] text-muted-foreground">{fc.horizon}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-mono font-medium">{fc.value}</span>
                  <ConfidenceBadge value={fc.confidence} showLabel={false} />
                </div>
              </div>
            ))}
          </div>
        </ConsolePanel>
      )}
    </div>
  )
}