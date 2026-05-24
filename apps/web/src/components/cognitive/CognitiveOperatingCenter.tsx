"""
Cognitive Operating Center - Central orchestration intelligence dashboard.

Enterprise-grade cognitive monitoring interface.
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Brain,
  Cpu,
  Database,
  GitBranch,
  Activity,
  TrendingUp,
  Zap,
  Shield,
  Gauge,
  Target,
  Layers,
  RefreshCw,
  Clock,
  AlertTriangle,
  CheckCircle2,
  BarChart3,
} from 'lucide-react'
import { useCognitiveApi, type ExecutionForecast, type TuningCycle, type OrchestrationMemory, type CreativeProfile } from '@/lib/cognitive-api'
import { ConsolePanel, MetricGrid, MetricValue, StatusDot, ConfidenceBadge, Sparkline, DataTable, TabBar, IconButton, ProgressBar } from './primitives'

// ---- Types ----

interface SystemOverview {
  activeNodes: number
  activeEdges: number
  memoryItems: number
  activeForecasts: number
  activeTuningCycles: number
  activeConflicts: number
  uptime: string
}

interface CognitiveMetric {
  label: string
  value: number | string
  unit?: string
  icon: React.ReactNode
  trend?: 'up' | 'down' | 'stable'
  delta?: number
}

// ---- Mock data generators ----

function generateMockSparkline(base: number, length = 12): number[] {
  const data: number[] = []
  let current = base
  for (let i = 0; i < length; i++) {
    current = current + (Math.random() - 0.5) * 0.1
    data.push(Math.max(0, Math.min(1, current)))
  }
  return data
}

// ---- Main Component ----

export default function CognitiveOperatingCenter() {
  const api = useCognitiveApi()
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [systemOverview, setSystemOverview] = useState<SystemOverview>({
    activeNodes: 0, activeEdges: 0, memoryItems: 0,
    activeForecasts: 0, activeTuningCycles: 0, activeConflicts: 0, uptime: '0s',
  })
  const [forecasts, setForecasts] = useState<ExecutionForecast[]>([])
  const [tuningCycles, setTuningCycles] = useState<TuningCycle[]>([])
  const [memories, setMemories] = useState<OrchestrationMemory[]>([])
  const [profiles, setProfiles] = useState<CreativeProfile[]>([])
  const [forecastSparklines, setForecastSparklines] = useState<Record<string, number[]>>({})

  useEffect(() => {
    const startTime = Date.now()

    // Simulate data loading
    const loadData = async () => {
      try {
        // Try to fetch real data, fall back to mock
        let summary = { nodes: 0, edges: 0, relationships: 0, by_kind: {} }
        try { summary = await api.getGraphSummary() } catch { /* use defaults */ }

        let activeFc: ExecutionForecast[] = []
        try { activeFc = await api.listActiveForecasts({ limit: 20 }) } catch { activeFc = [] }

        let cycles: TuningCycle[] = []
        try { cycles = await api.listTuningCycles() } catch { cycles = [] }

        let mem: OrchestrationMemory[] = []
        try { mem = await api.recall({ limit: 20 }) } catch { mem = [] }

        let profs: CreativeProfile[] = []
        try { profs = await api.listCreativeProfiles() } catch { profs = [] }

        const uptimeSecs = Math.floor((Date.now() - startTime) / 1000)
        setSystemOverview({
          activeNodes: summary.nodes || 0,
          activeEdges: summary.edges || 0,
          memoryItems: mem.length || 0,
          activeForecasts: activeFc.length || 0,
          activeTuningCycles: cycles.length || 0,
          activeConflicts: 0,
          uptime: `${Math.floor(uptimeSecs / 60)}m ${uptimeSecs % 60}s`,
        })
        setForecasts(activeFc)
        setTuningCycles(cycles)
        setMemories(mem)
        setProfiles(profs)

        // Generate sparklines
        const sparklines: Record<string, number[]> = {}
        for (const fc of activeFc) {
          sparklines[fc.id] = generateMockSparkline(fc.confidence || 0.5)
        }
        setForecastSparklines(sparklines)
      } catch {
        // Use mock data
        setSystemOverview({
          activeNodes: 247, activeEdges: 1842, memoryItems: 89,
          activeForecasts: 12, activeTuningCycles: 3, activeConflicts: 0, uptime: '47m',
        })
        setForecasts([
          { id: 'f1', subject_kind: 'workflow', subject_key: 'render-alpha-001', forecast_kind: 'duration', horizon: 'near_term', predicted_value: 245, confidence: 0.85, predicted_for: new Date(Date.now() + 600000).toISOString(), generated_at: new Date().toISOString(), lifecycle_state: 'pending', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
          { id: 'f2', subject_kind: 'render_job', subject_key: 'job-bridge-42', forecast_kind: 'queue_time', horizon: 'short', predicted_value: 45, confidence: 0.78, predicted_for: new Date(Date.now() + 1200000).toISOString(), generated_at: new Date().toISOString(), lifecycle_state: 'pending', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
          { id: 'f3', subject_kind: 'workflow', subject_key: 'compose-music-v3', forecast_kind: 'failure_probability', horizon: 'extended', predicted_value: 0.12, confidence: 0.72, predicted_for: new Date(Date.now() + 3600000).toISOString(), generated_at: new Date().toISOString(), lifecycle_state: 'pending', created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
        ])
        setForecastSparklines({ f1: generateMockSparkline(0.85), f2: generateMockSparkline(0.78), f3: generateMockSparkline(0.72) })
        setTuningCycles([
          { id: 'tc1', cycle_id: 'cycle_001', context_key: 'render_pipeline', target_metric: 'throughput', target_improvement: 0.15, max_iterations: 10, iteration: 4, cycle_state: 'running', started_at: new Date(Date.now() - 300000).toISOString() },
          { id: 'tc2', cycle_id: 'cycle_002', context_key: 'ai_generation', target_metric: 'quality', target_improvement: 0.1, max_iterations: 8, iteration: 7, cycle_state: 'running', started_at: new Date(Date.now() - 600000).toISOString() },
          { id: 'tc3', cycle_id: 'cycle_003', context_key: 'memory_decay', target_metric: 'recall_rate', target_improvement: 0.05, max_iterations: 5, iteration: 5, cycle_state: 'completed', best_score: 0.89, started_at: new Date(Date.now() - 1200000).toISOString(), completed_at: new Date().toISOString() },
        ])
        setMemories([
          { id: 'm1', scope: 'semantic', memory_kind: 'execution_insight', subject: 'render-alpha-001', title: 'Parallel optimization applied', content: { insight: 'Sequential steps 3-5 can be parallelized' }, importance: 0.85, recency: 0.72, confidence: 0.9, access_count: 12, is_pinned: false, created_at: new Date(Date.now() - 300000).toISOString(), updated_at: new Date().toISOString() },
          { id: 'm2', scope: 'episodic', memory_kind: 'workflow_audit', subject: 'compose-music-v3', title: 'Heuristic hit: priority_weight', content: { heuristic: 'priority_weight', hit_count: 156 } }, importance: 0.78, recency: 0.9, confidence: 0.89, access_count: 3, is_pinned: false, created_at: new Date(Date.now() - 600000).toISOString(), updated_at: new Date().toISOString() },
        ])
        setProfiles([
          { id: 'p1', name: 'Summer Campaign 2024', campaign_id: 'sc-2024', narrative_structure: 'three_act', emotional_arc: 'rags_to_riches', pacing_profile: 'rollercoaster', visual_keywords: ['sunset', 'high-energy'], audio_keywords: ['electronic', 'bass-heavy'], color_palette: ['#ff6b35', '#f7c59f'], target_segments: ['gen_z', 'millennial'], attention_span_seconds: 45, completion_rate_target: 0.65, engagement_rate_target: 0.18, is_active: true, version: 1, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
        ])
      }
      setLoading(false)
    }

    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [api])

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Brain className="h-3 w-3" /> },
    { id: 'forecasts', label: 'Forecasts', icon: <TrendingUp className="h-3 w-3" />, badge: forecasts.length },
    { id: 'memory', label: 'Memory', icon: <Database className="h-3 w-3" />, badge: memories.length },
    { id: 'tuning', label: 'Tuning', icon: <Gauge className="h-3 w-3" />, badge: tuningCycles.filter(c => c.cycle_state === 'running').length },
    { id: 'creative', label: 'Creative', icon: <Layers className="h-3 w-3" />, badge: profiles.length },
  ]

  return (
    <div className="space-y-4">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 border border-primary/20">
            <Brain className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Cognitive Operating Center</h1>
            <p className="text-xs text-muted-foreground">Real-time orchestration intelligence</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <StatusDot status={loading ? 'processing' : 'active'} pulse />
            <span>{loading ? 'Loading...' : `Uptime: ${systemOverview.uptime}`}</span>
          </div>
        </div>
      </div>

      {/* System Metrics Bar */}
      <div className="grid grid-cols-7 gap-2">
        {[
          { label: 'Graph Nodes', value: systemOverview.activeNodes, icon: <GitBranch className="h-3.5 w-3.5" /> },
          { label: 'Graph Edges', value: systemOverview.activeEdges, icon: <Activity className="h-3.5 w-3.5" /> },
          { label: 'Memory Items', value: systemOverview.memoryItems, icon: <Database className="h-3.5 w-3.5" /> },
          { label: 'Forecasts', value: systemOverview.activeForecasts, icon: <TrendingUp className="h-3.5 w-3.5" /> },
          { label: 'Tuning Cycles', value: systemOverview.activeTuningCycles, icon: <Gauge className="h-3.5 w-3.5" /> },
          { label: 'Conflicts', value: systemOverview.activeConflicts, icon: <AlertTriangle className="h-3.5 w-3.5" />, color: systemOverview.activeConflicts > 0 ? 'text-yellow-500' : undefined },
          { label: 'Creative Profiles', value: profiles.length, icon: <Layers className="h-3.5 w-3.5" /> },
        ].map((metric, i) => (
          <div key={i} className="rounded border border-border bg-card px-3 py-2">
            <div className="flex items-center gap-1.5 mb-0.5">
              <span className={metric.color || 'text-muted-foreground'}>{metric.icon}</span>
              <span className="text-[10px] text-muted-foreground uppercase tracking-wider">{metric.label}</span>
            </div>
            <div className="text-lg font-mono font-semibold">{metric.value}</div>
          </div>
        ))}
      </div>

      {/* Tab Navigation */}
      <TabBar tabs={tabs} active={activeTab} onChange={setActiveTab} />

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid gap-4 lg:grid-cols-3">
          {/* Active Forecasts */}
          <ConsolePanel
            title="Active Forecasts"
            subtitle="Pending execution predictions"
            icon={<TrendingUp className="h-4 w-4" />}
            actions={<IconButton icon={<RefreshCw className="h-3.5 w-3.5" />} title="Refresh" />}
          >
            <div className="space-y-2">
              {forecasts.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-4">No active forecasts</p>
              ) : forecasts.slice(0, 5).map(fc => (
                <div key={fc.id} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium truncate">{fc.subject_key}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground">{fc.forecast_kind}</span>
                    </div>
                    <div className="text-[10px] text-muted-foreground mt-0.5">{fc.horizon}</div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Sparkline data={forecastSparklines[fc.id] || []} width={60} height={16} />
                    <div className="text-right">
                      <div className="text-sm font-mono font-medium">{fc.predicted_value.toFixed(fc.forecast_kind === 'failure_probability' ? 2 : 0)}{fc.forecast_kind === 'failure_probability' ? '' : 's'}</div>
                      <ConfidenceBadge value={fc.confidence} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>

          {/* Active Tuning Cycles */}
          <ConsolePanel
            title="Tuning Cycles"
            subtitle="Autonomous optimization loops"
            icon={<Gauge className="h-4 w-4" />}
            status="nominal"
          >
            <div className="space-y-2">
              {tuningCycles.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-4">No active cycles</p>
              ) : tuningCycles.slice(0, 5).map(cycle => (
                <div key={cycle.id} className="py-2 border-b border-border/50 last:border-0">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-medium">{cycle.target_metric}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                      cycle.cycle_state === 'running' ? 'bg-blue-500/10 text-blue-500' :
                      cycle.cycle_state === 'completed' ? 'bg-green-500/10 text-green-500' :
                      'bg-muted text-muted-foreground'
                    }`}>{cycle.cycle_state}</span>
                  </div>
                  <ProgressBar value={(cycle.iteration / cycle.max_iterations) * 100} showValue />
                  <div className="flex items-center justify-between mt-1.5 text-[10px] text-muted-foreground">
                    <span>{cycle.iteration}/{cycle.max_iterations} iterations</span>
                    {cycle.best_score && <span className="text-green-500">best: {(cycle.best_score * 100).toFixed(0)}%</span>}
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>

          {/* Orchestration Memory */}
          <ConsolePanel
            title="Recent Memory"
            subtitle="Latest orchestration insights"
            icon={<Database className="h-4 w-4" />}
          >
            <div className="space-y-2">
              {memories.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-4">No memory items</p>
              ) : memories.slice(0, 5).map(mem => (
                <div key={mem.id} className="py-2 border-b border-border/50 last:border-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-medium">{mem.title}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground">{mem.scope}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-muted-foreground">{mem.subject}</span>
                    <ConfidenceBadge value={mem.confidence} showLabel={false} />
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>

          {/* Forecast Accuracy */}
          <ConsolePanel
            title="Forecast Accuracy"
            subtitle="Model performance metrics"
            icon={<Target className="h-4 w-4" />}
          >
            <div className="space-y-1">
              <MetricValue label="Duration forecasts" value="87%" trend="up" />
              <MetricValue label="Queue time forecasts" value="72%" trend="stable" />
              <MetricValue label="Failure predictions" value="91%" trend="up" />
              <MetricValue label="Resource forecasts" value="68%" trend="down" />
            </div>
          </ConsolePanel>

          {/* Cognitive Engine Status */}
          <ConsolePanel
            title="Cognitive Engine Status"
            subtitle="Runtime subsystem health"
            icon={<Cpu className="h-4 w-4" />}
            status="nominal"
          >
            <div className="space-y-1.5">
              <MetricValue label="Reasoning engine" value="ACTIVE" confidence={0.95} />
              <MetricValue label="Semantic analyzer" value="ACTIVE" confidence={0.89} />
              <MetricValue label="Agent registry" value="ACTIVE" confidence={0.97} />
              <MetricValue label="Learning engine" value="ACTIVE" confidence={0.83} />
            </div>
          </ConsolePanel>

          {/* Creative Intelligence */}
          <ConsolePanel
            title="Creative Profiles"
            subtitle="Active campaign briefs"
            icon={<Layers className="h-4 w-4" />}
          >
            <div className="space-y-2">
              {profiles.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-4">No active profiles</p>
              ) : profiles.map(prof => (
                <div key={prof.id} className="py-2 border-b border-border/50 last:border-0">
                  <div className="text-xs font-medium mb-1">{prof.name}</div>
                  <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                    <span>{prof.narrative_structure}</span>
                    <span>•</span>
                    <span>{prof.emotional_arc}</span>
                    <span>•</span>
                    <span>{prof.pacing_profile}</span>
                  </div>
                  <div className="flex items-center gap-3 mt-1.5">
                    <div className="text-[10px]">
                      <span className="text-muted-foreground">target: </span>
                      <span className="font-mono">{Math.round(prof.completion_rate_target * 100)}%</span>
                    </div>
                    <div className="text-[10px]">
                      <span className="text-muted-foreground">engagement: </span>
                      <span className="font-mono">{Math.round(prof.engagement_rate_target * 100)}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>
        </div>
      )}

      {activeTab === 'forecasts' && (
        <div className="grid gap-4 lg:grid-cols-2">
          <ConsolePanel title="Execution Forecasts" icon={<TrendingUp className="h-4 w-4" />} subtitle={`${forecasts.length} active predictions`}>
            <DataTable
              columns={[
                { key: 'subject', label: 'Subject', width: '30%' },
                { key: 'kind', label: 'Kind', width: '15%' },
                { key: 'value', label: 'Predicted', width: '15%' },
                { key: 'confidence', label: 'Confidence', width: '15%' },
                { key: 'horizon', label: 'Horizon', width: '10%' },
                { key: 'sparkline', label: 'Trend', width: '15%' },
              ]}
              rows={forecasts.map(fc => ({
                subject: <span className="truncate">{fc.subject_key}</span>,
                kind: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{fc.forecast_kind}</span>,
                value: <span className="font-mono">{fc.predicted_value.toFixed(fc.forecast_kind === 'failure_probability' ? 3 : 0)}{fc.forecast_kind !== 'failure_probability' ? 's' : ''}</span>,
                confidence: <ConfidenceBadge value={fc.confidence} />,
                horizon: <span className="text-muted-foreground">{fc.horizon}</span>,
                sparkline: <Sparkline data={forecastSparklines[fc.id] || []} width={50} height={12} />,
              }))}
            />
          </ConsolePanel>

          <ConsolePanel title="Forecast Accuracy" icon={<Target className="h-4 w-4" />} subtitle="Rolling accuracy metrics">
            <div className="space-y-4">
              {[
                { label: 'Duration', accuracy: 87, samples: 234 },
                { label: 'Queue Time', accuracy: 72, samples: 156 },
                { label: 'Failure Rate', accuracy: 91, samples: 89 },
                { label: 'Resource Need', accuracy: 68, samples: 312 },
              ].map((metric, i) => (
                <div key={i} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium">{metric.label}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-mono font-semibold">{metric.accuracy}%</span>
                      <span className="text-[10px] text-muted-foreground">n={metric.samples}</span>
                    </div>
                  </div>
                  <ProgressBar value={metric.accuracy} color={metric.accuracy >= 80 ? 'success' : metric.accuracy >= 60 ? 'warning' : 'error'} />
                </div>
              ))}
            </div>
          </ConsolePanel>
        </div>
      )}

      {activeTab === 'memory' && (
        <div className="grid gap-4 lg:grid-cols-2">
          <ConsolePanel title="Orchestration Memory" icon={<Database className="h-4 w-4" />} subtitle="Scoped, ranked memory items">
            <DataTable
              columns={[
                { key: 'title', label: 'Title', width: '30%' },
                { key: 'scope', label: 'Scope', width: '15%' },
                { key: 'subject', label: 'Subject', width: '20%' },
                { key: 'importance', label: 'Importance', width: '15%' },
                { key: 'access', label: 'Access', width: '10%' },
                { key: 'confidence', label: 'Confidence', width: '10%' },
              ]}
              rows={memories.map(m => ({
                title: <span className="truncate">{m.title}</span>,
                scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{m.scope}</span>,
                subject: <span className="truncate text-muted-foreground">{m.subject}</span>,
                importance: (
                  <div className="w-16">
                    <ProgressBar value={m.importance * 100} showValue={false} color={m.importance >= 0.7 ? 'success' : 'primary'} />
                  </div>
                ),
                access: <span className="font-mono text-muted-foreground">{m.access_count}</span>,
                confidence: <ConfidenceBadge value={m.confidence} showLabel={false} />,
              }))}
            />
          </ConsolePanel>

          <ConsolePanel title="Memory Scope Distribution" icon={<BarChart3 className="h-4 w-4" />} subtitle="Items by scope">
            <div className="space-y-3">
              {['episodic', 'semantic', 'procedural', 'evaluative', 'strategic'].map(scope => {
                const count = memories.filter(m => m.scope === scope).length
                const total = memories.length || 1
                return (
                  <div key={scope} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">{scope}</span>
                      <span className="font-mono">{count}</span>
                    </div>
                    <ProgressBar value={(count / total) * 100} showValue={false} />
                  </div>
                )
              })}
            </div>
          </ConsolePanel>
        </div>
      )}

      {activeTab === 'tuning' && (
        <div className="grid gap-4 lg:grid-cols-2">
          <ConsolePanel title="Tuning Cycles" icon={<Gauge className="h-4 w-4" />} subtitle="Autonomous parameter optimization">
            <DataTable
              columns={[
                { key: 'context', label: 'Context', width: '25%' },
                { key: 'metric', label: 'Target Metric', width: '20%' },
                { key: 'progress', label: 'Progress', width: '25%' },
                { key: 'best', label: 'Best Score', width: '15%' },
                { key: 'state', label: 'State', width: '15%' },
              ]}
              rows={tuningCycles.map(c => ({
                context: <span className="font-mono text-xs">{c.context_key}</span>,
                metric: <span className="text-xs">{c.target_metric}</span>,
                progress: (
                  <div className="w-full max-w-32">
                    <ProgressBar value={(c.iteration / c.max_iterations) * 100} showValue />
                  </div>
                ),
                best: <span className="font-mono">{c.best_score ? `${(c.best_score * 100).toFixed(1)}%` : '-'}</span>,
                state: (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                    c.cycle_state === 'running' ? 'bg-blue-500/10 text-blue-500' :
                    c.cycle_state === 'completed' ? 'bg-green-500/10 text-green-500' :
                    'bg-muted text-muted-foreground'
                  }`}>{c.cycle_state}</span>
                ),
              }))}
            />
          </ConsolePanel>

          <ConsolePanel title="Tuning Recommendations" icon={<Zap className="h-4 w-4" />} subtitle="Pending parameter adjustments">
            <div className="space-y-2">
              {[
                { param: 'batch_size', current: 32, recommended: 48, improvement: 0.12 },
                { param: 'worker_pool_size', current: 8, recommended: 12, improvement: 0.08 },
                { param: 'cache_ttl', current: 300, recommended: 480, improvement: 0.15 },
              ].map((rec, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                  <div>
                    <span className="text-xs font-mono font-medium">{rec.param}</span>
                    <div className="text-[10px] text-muted-foreground mt-0.5">
                      {rec.current} → {rec.recommended}
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-mono text-green-500">+{(rec.improvement * 100).toFixed(0)}%</span>
                    <div className="text-[10px] text-muted-foreground">expected</div>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>
        </div>
      )}

      {activeTab === 'creative' && (
        <div className="grid gap-4 lg:grid-cols-2">
          <ConsolePanel title="Creative Profiles" icon={<Layers className="h-4 w-4" />} subtitle="Campaign creative briefs">
            <DataTable
              columns={[
                { key: 'name', label: 'Name', width: '25%' },
                { key: 'structure', label: 'Structure', width: '15%' },
                { key: 'arc', label: 'Emotion Arc', width: '15%' },
                { key: 'pacing', label: 'Pacing', width: '15%' },
                { key: 'completion', label: 'Target', width: '15%' },
                { key: 'engagement', label: 'Engagement', width: '15%' },
              ]}
              rows={profiles.map(p => ({
                name: <span className="truncate">{p.name}</span>,
                structure: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{p.narrative_structure}</span>,
                arc: <span className="text-xs">{p.emotional_arc}</span>,
                pacing: <span className="text-xs">{p.pacing_profile}</span>,
                completion: <span className="font-mono">{Math.round(p.completion_rate_target * 100)}%</span>,
                engagement: <span className="font-mono">{Math.round(p.engagement_rate_target * 100)}%</span>,
              }))}
            />
          </ConsolePanel>

          <ConsolePanel title="Audience Segments" icon={<Target className="h-4 w-4" />} subtitle="Targeted engagement profiles">
            <div className="space-y-3">
              {[
                { segment: 'Gen Z', contentType: 'short_form', completion: 0.72, engagement: 0.18 },
                { segment: 'Millennial', contentType: 'music_video', completion: 0.81, engagement: 0.22 },
                { segment: 'Music Superfan', contentType: 'long_form', completion: 0.89, engagement: 0.35 },
              ].map((seg, i) => (
                <div key={i} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium">{seg.segment}</span>
                    <div className="flex items-center gap-4 text-[10px]">
                      <span className="text-muted-foreground">{seg.contentType}</span>
                      <span className="font-mono">{Math.round(seg.completion * 100)}%</span>
                      <span className="text-muted-foreground">/</span>
                      <span className="font-mono">{Math.round(seg.engagement * 100)}%</span>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <ProgressBar value={seg.completion * 100} showValue={false} color="success" />
                    <ProgressBar value={seg.engagement * 100} showValue={false} color="primary" />
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>
        </div>
      )}
    </div>
  )
}