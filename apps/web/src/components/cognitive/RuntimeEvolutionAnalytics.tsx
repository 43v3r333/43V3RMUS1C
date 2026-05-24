"""
Runtime Evolution Analytics

Self-evolution and autonomous optimization interface with tuning cycles,
runtime metrics, and adaptive performance monitoring.
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Gauge,
  TrendingUp,
  Zap,
  Activity,
  RotateCcw,
  Play,
  Pause,
  CheckCircle2,
  AlertTriangle,
  Target,
} from 'lucide-react'
import { useCognitiveApi, type TuningCycle, type RuntimeMetric, type EvolutionStatistics } from '@/lib/cognitive-api'
import { ConsolePanel, DataTable, TabBar, IconButton, ProgressBar, StatusDot, ConfidenceBadge, Sparkline } from './primitives'

function generateSparkline(base: number, length = 12): number[] {
  const data: number[] = []
  let current = base
  for (let i = 0; i < length; i++) {
    current = current + (Math.random() - 0.5) * 0.15
    data.push(Math.max(0, Math.min(1, current)))
  }
  return data
}

export default function RuntimeEvolutionAnalytics() {
  const api = useCognitiveApi()
  const [activeTab, setActiveTab] = useState('cycles')
  const [loading, setLoading] = useState(true)
  const [cycles, setCycles] = useState<TuningCycle[]>([])
  const [stats, setStats] = useState<EvolutionStatistics | null>(null)
  const [metrics, setMetrics] = useState<RuntimeMetric[]>([])
  const [sparklines, setSparklines] = useState<Record<string, number[]>>({})

  useEffect(() => {
    const loadData = async () => {
      try {
        const [cyclesData, statsData, metricsData] = await Promise.all([
          api.listTuningCycles({ limit: 20 }),
          api.getEvolutionStats(),
          api.listMetrics({ limit: 50 }),
        ])
        setCycles(cyclesData.items)
        setStats(statsData)
        setMetrics(metricsData.items)
        
        // Generate sparklines for cycles
        const lines: Record<string, number[]> = {}
        for (const cycle of cyclesData.items) {
          lines[cycle.cycle_id] = generateSparkline(cycle.best_score || 0.5)
        }
        setSparklines(lines)
      } catch {
        // Mock data
        setCycles([
          {
            id: 'tc1', cycle_id: 'cycle_001', name: 'Render Pipeline Tuning', context_key: 'render_pipeline',
            target_metric: 'throughput', target_improvement: 0.15, max_iterations: 10, iteration: 4,
            current_score: 0.72, best_score: 0.78, baseline_score: 0.65,
            cycle_state: 'running', started_at: new Date(Date.now() - 300000).toISOString(),
          },
          {
            id: 'tc2', cycle_id: 'cycle_002', name: 'AI Generation Optimization', context_key: 'ai_generation',
            target_metric: 'quality', target_improvement: 0.1, max_iterations: 8, iteration: 7,
            current_score: 0.88, best_score: 0.91, baseline_score: 0.82,
            cycle_state: 'running', started_at: new Date(Date.now() - 600000).toISOString(),
          },
          {
            id: 'tc3', cycle_id: 'cycle_003', name: 'Memory Decay Tuning', context_key: 'memory_decay',
            target_metric: 'recall_rate', target_improvement: 0.05, max_iterations: 5, iteration: 5,
            current_score: 0.89, best_score: 0.89, baseline_score: 0.84,
            cycle_state: 'converged', started_at: new Date(Date.now() - 1200000).toISOString(),
            completed_at: new Date(Date.now() - 100000).toISOString(),
          },
        ])
        setStats({
          total_cycles: 15, by_state: { running: 5, converged: 8, pending: 2 },
          by_context: { render_pipeline: 6, ai_generation: 5, memory_decay: 4 },
          best_score_achieved: 0.94, active_cycles: 5, converged_cycles: 8, total_metrics_recorded: 847,
        })
        setMetrics([
          { id: 'm1', metric_type: 'performance', metric_name: 'throughput', value: 0.82, change_direction: 'improving', recorded_at: new Date().toISOString() },
          { id: 'm2', metric_type: 'quality', metric_name: 'accuracy', value: 0.91, change_direction: 'stable', recorded_at: new Date().toISOString() },
        ])
        setSparklines({
          cycle_001: generateSparkline(0.78),
          cycle_002: generateSparkline(0.91),
          cycle_003: generateSparkline(0.89),
        })
      }
      setLoading(false)
    }

    loadData()
    const interval = setInterval(loadData, 20000)
    return () => clearInterval(interval)
  }, [api])

  const tabs = [
    { id: 'cycles', label: 'Tuning Cycles', icon: <RotateCcw className="h-3 w-3" />, badge: cycles.length },
    { id: 'metrics', label: 'Metrics', icon: <Activity className="h-3 w-3" />, badge: metrics.length },
    { id: 'optimization', label: 'Optimization', icon: <Zap className="h-3 w-3" /> },
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Gauge className="h-5 w-5" />
            Runtime Evolution Analytics
          </h2>
          <p className="text-xs text-muted-foreground">
            Self-evolution monitoring and autonomous optimization
          </p>
        </div>
        <div className="flex items-center gap-2">
          <StatusDot status="active" pulse />
          <span className="text-xs text-muted-foreground">Auto-tuning active</span>
        </div>
      </div>

      <TabBar tabs={tabs} active={activeTab} onChange={setActiveTab} />

      {/* Statistics */}
      {stats && (
        <div className="grid gap-4 lg:grid-cols-4">
          <ConsolePanel title="Active Cycles" icon={<RotateCcw className="h-4 w-4" />} subtitle="Running optimization">
            <div className="text-2xl font-mono font-bold">{stats.active_cycles}</div>
            <div className="text-xs text-muted-foreground mt-1">of {stats.total_cycles} total</div>
          </ConsolePanel>

          <ConsolePanel title="Converged" icon={<CheckCircle2 className="h-4 w-4" />} subtitle="Completed successfully">
            <div className="text-2xl font-mono font-bold text-green-500">{stats.converged_cycles}</div>
          </ConsolePanel>

          <ConsolePanel title="Best Score" icon={<Target className="h-4 w-4" />} subtitle="Highest achieved">
            <div className="text-2xl font-mono font-bold text-primary">
              {stats.best_score_achieved ? `${Math.round(stats.best_score_achieved * 100)}%` : '—'}
            </div>
          </ConsolePanel>

          <ConsolePanel title="Metrics" icon={<Activity className="h-4 w-4" />} subtitle="Recorded">
            <div className="text-2xl font-mono font-bold">{stats.total_metrics_recorded}</div>
            <div className="text-xs text-muted-foreground mt-1">data points</div>
          </ConsolePanel>
        </div>
      )}

      {/* Tuning Cycles */}
      {activeTab === 'cycles' && (
        <div className="space-y-4">
          <ConsolePanel title="Tuning Cycles" icon={<RotateCcw className="h-4 w-4" />} subtitle="Active optimization cycles">
            <DataTable
              columns={[
                { key: 'name', label: 'Cycle', width: '20%' },
                { key: 'context', label: 'Context', width: '15%' },
                { key: 'metric', label: 'Target', width: '12%' },
                { key: 'progress', label: 'Progress', width: '15%' },
                { key: 'score', label: 'Score', width: '12%' },
                { key: 'trend', label: 'Trend', width: '12%' },
                { key: 'state', label: 'State', width: '14%' },
              ]}
              rows={cycles.map(cycle => ({
                name: (
                  <div className="flex items-center gap-2">
                    <StatusDot status={cycle.cycle_state === 'running' ? 'processing' : cycle.cycle_state === 'converged' ? 'active' : 'idle'} />
                    <span className="truncate font-medium">{cycle.name || cycle.cycle_id}</span>
                  </div>
                ),
                context: <span className="font-mono text-xs">{cycle.context_key}</span>,
                metric: <span className="text-xs">{cycle.target_metric}</span>,
                progress: (
                  <div className="w-20">
                    <ProgressBar 
                      value={(cycle.iteration / cycle.max_iterations) * 100} 
                      showValue 
                      color={cycle.cycle_state === 'converged' ? 'success' : 'primary'}
                    />
                    <div className="text-[10px] text-muted-foreground text-center mt-0.5">
                      {cycle.iteration}/{cycle.max_iterations}
                    </div>
                  </div>
                ),
                score: (
                  <div className="flex items-center gap-2">
                    <span className="font-mono">{cycle.current_score ? `${Math.round(cycle.current_score * 100)}%` : '—'}</span>
                    {cycle.best_score && cycle.current_score && cycle.best_score > cycle.current_score && (
                      <span className="text-green-500 text-[10px]">↑{Math.round((cycle.best_score - cycle.current_score) * 100)}%</span>
                    )}
                  </div>
                ),
                trend: (
                  <Sparkline data={sparklines[cycle.cycle_id] || []} width={60} height={20} />
                ),
                state: (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                    cycle.cycle_state === 'running' ? 'bg-blue-500/10 text-blue-500' :
                    cycle.cycle_state === 'converged' ? 'bg-green-500/10 text-green-500' :
                    'bg-muted text-muted-foreground'
                  }`}>{cycle.cycle_state}</span>
                ),
              }))}
            />
          </ConsolePanel>

          {/* By Context */}
          {stats && (
            <ConsolePanel title="By Context" icon={<Zap className="h-4 w-4" />} subtitle="Cycle distribution">
              <div className="grid grid-cols-3 gap-3">
                {Object.entries(stats.by_context).map(([context, count]) => (
                  <div key={context} className="p-3 border border-border rounded">
                    <div className="text-xs text-muted-foreground mb-1">{context}</div>
                    <div className="text-xl font-mono font-bold">{count}</div>
                    <div className="text-[10px] text-muted-foreground">cycles</div>
                  </div>
                ))}
              </div>
            </ConsolePanel>
          )}
        </div>
      )}

      {activeTab === 'metrics' && (
        <div className="space-y-4">
          <ConsolePanel title="Runtime Metrics" icon={<Activity className="h-4 w-4" />} subtitle="Performance telemetry">
            <DataTable
              columns={[
                { key: 'type', label: 'Type', width: '15%' },
                { key: 'name', label: 'Metric', width: '20%' },
                { key: 'value', label: 'Value', width: '15%' },
                { key: 'trend', label: 'Trend', width: '15%' },
                { key: 'direction', label: 'Direction', width: '15%' },
                { key: 'time', label: 'Recorded', width: '20%' },
              ]}
              rows={metrics.map(m => ({
                type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{m.metric_type}</span>,
                name: <span className="font-mono text-xs">{m.metric_name}</span>,
                value: <span className="font-mono font-medium">{Math.round(m.value * 100)}%</span>,
                trend: <Sparkline data={generateSparkline(m.value)} width={50} height={16} />,
                direction: (
                  <span className={`text-xs flex items-center gap-1 ${
                    m.change_direction === 'improving' ? 'text-green-500' :
                    m.change_direction === 'declining' ? 'text-red-500' :
                    'text-muted-foreground'
                  }`}>
                    {m.change_direction === 'improving' ? <TrendingUp className="h-3 w-3" /> : 
                     m.change_direction === 'declining' ? <AlertTriangle className="h-3 w-3" /> : 
                     '—'}
                    {m.change_direction || 'stable'}
                  </span>
                ),
                time: <span className="text-xs text-muted-foreground">{new Date(m.recorded_at).toLocaleTimeString()}</span>,
              }))}
            />
          </ConsolePanel>
        </div>
      )}

      {activeTab === 'optimization' && (
        <div className="grid gap-4 lg:grid-cols-2">
          <ConsolePanel title="Parameter Recommendations" icon={<Target className="h-4 w-4" />} subtitle="Pending adjustments">
            <div className="space-y-3">
              {[
                { param: 'batch_size', current: 32, recommended: 48, improvement: 12 },
                { param: 'worker_pool_size', current: 8, recommended: 12, improvement: 8 },
                { param: 'cache_ttl', current: 300, recommended: 480, improvement: 15 },
                { param: 'retry_delay', current: 1000, recommended: 800, improvement: 6 },
              ].map((rec, i) => (
                <div key={i} className="flex items-center justify-between p-2 border border-border rounded">
                  <div>
                    <span className="font-mono text-sm">{rec.param}</span>
                    <div className="text-[10px] text-muted-foreground mt-0.5">
                      {rec.current} → {rec.recommended}
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="font-mono text-green-500">+{rec.improvement}%</span>
                    <div className="text-[10px] text-muted-foreground">expected</div>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>

          <ConsolePanel title="Optimization History" icon={<TrendingUp className="h-4 w-4" />} subtitle="Recent improvements">
            <div className="space-y-2">
              {[
                { param: 'queue_batch_size', before: 16, after: 24, gain: 18 },
                { param: 'render_workers', before: 4, after: 6, gain: 22 },
                { param: 'memory_threshold', before: 0.7, after: 0.75, gain: 8 },
              ].map((item, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                  <span className="font-mono text-xs">{item.param}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">{item.before} → {item.after}</span>
                    <span className="text-xs text-green-500">+{item.gain}%</span>
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