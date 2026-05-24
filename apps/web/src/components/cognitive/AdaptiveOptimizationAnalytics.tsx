"""
Adaptive Optimization Analytics - Feedback loops and tuning analytics.
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Gauge,
  Zap,
  Activity,
  TrendingUp,
  RefreshCw,
  BarChart3,
  Target,
  Clock,
  AlertTriangle,
  CheckCircle2,
  Layers,
} from 'lucide-react'
import { useCognitiveApi, type OrchestrationFeedback, type TuningCycle } from '@/lib/cognitive-api'
import { ConsolePanel, DataTable, MetricGrid, StatusDot, ConfidenceBadge, IconButton, ProgressBar, Sparkline, TabBar } from './primitives'

interface TuningRecordData {
  id: string
  parameter: string
  before: number
  after: number
  delta: number
  action: string
  reason: string
  state: string
  confidence: number
  time: string
}

interface OutcomeData {
  feedback_type: string
  mean_actual: number
  mean_delta: number
  mean_quality: number
  count: number
}

export default function AdaptiveOptimizationAnalytics() {
  const api = useCognitiveApi()
  const [activeTab, setActiveTab] = useState('overview')
  const [feedback, setFeedback] = useState<OrchestrationFeedback[]>([])
  const [tuningCycles, setTuningCycles] = useState<TuningCycle[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const fb = await api.analyzeFeedbackOutcomes({}).catch(() => ({ count: 0, mean_actual: 0, mean_delta_pct: 0, mean_quality: 0 }))
        const tc = await api.listTuningCycles().catch(() => [])
        setTuningCycles(tc)
      } catch {
        // use mock
        setTuningCycles([
          { id: 'tc1', cycle_id: 'cycle_001', context_key: 'render_pipeline', target_metric: 'throughput', target_improvement: 0.15, max_iterations: 10, iteration: 4, cycle_state: 'running', started_at: new Date(Date.now() - 300000).toISOString() },
          { id: 'tc2', cycle_id: 'cycle_002', context_key: 'ai_generation', target_metric: 'quality', target_improvement: 0.1, max_iterations: 8, iteration: 7, cycle_state: 'running', started_at: new Date(Date.now() - 600000).toISOString() },
          { id: 'tc3', cycle_id: 'cycle_003', context_key: 'memory_decay', target_metric: 'recall_rate', target_improvement: 0.05, max_iterations: 5, iteration: 5, cycle_state: 'completed', best_score: 0.89, started_at: new Date(Date.now() - 1200000).toISOString(), completed_at: new Date().toISOString() },
        ])
      }
      setLoading(false)
    }
    load()
  }, [api])

  const outcomeData: OutcomeData[] = [
    { feedback_type: 'duration', mean_actual: 245, mean_delta: -0.08, mean_quality: 0.89, count: 234 },
    { feedback_type: 'quality', mean_actual: 0.87, mean_delta: 0.12, mean_quality: 0.92, count: 156 },
    { feedback_type: 'throughput', mean_actual: 120, mean_delta: 0.05, mean_quality: 0.85, count: 312 },
    { feedback_type: 'error_rate', mean_actual: 0.03, mean_delta: -0.15, mean_quality: 0.95, count: 89 },
  ]

  const tuningRecords: TuningRecordData[] = [
    { id: 'tr1', parameter: 'batch_size', before: 32, after: 48, delta: 16, action: 'scale_up', reason: 'trend=up; avg_outcome=0.62', state: 'applied', confidence: 0.82, time: '2m ago' },
    { id: 'tr2', parameter: 'worker_pool_size', before: 8, after: 12, delta: 4, action: 'scale_up', reason: 'trend=up; avg_outcome=0.58', state: 'applied', confidence: 0.75, time: '8m ago' },
    { id: 'tr3', parameter: 'cache_ttl', before: 300, after: 480, delta: 180, action: 'scale_up', reason: 'trend=up; avg_outcome=0.65', state: 'applied', confidence: 0.88, time: '15m ago' },
    { id: 'tr4', parameter: 'batch_size', before: 48, after: 40, delta: -8, action: 'scale_down', reason: 'trend=down; avg_outcome=0.41', state: 'applied', confidence: 0.71, time: '23m ago' },
    { id: 'tr5', parameter: 'retry_backoff', before: 1.5, after: 2.0, delta: 0.5, action: 'parameter_tune', reason: 'trend=up; avg_outcome=0.68', state: 'applied', confidence: 0.79, time: '45m ago' },
  ]

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Gauge className="h-3 w-3" /> },
    { id: 'feedback', label: 'Feedback Signals', icon: <Activity className="h-3 w-3" />, badge: tuningCycles.length },
    { id: 'tuning', label: 'Tuning Records', icon: <RefreshCw className="h-3 w-3" />, badge: tuningRecords.length },
    { id: 'outcomes', label: 'Outcomes', icon: <BarChart3 className="h-3 w-3" /> },
  ]

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 border border-primary/20">
            <Gauge className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Adaptive Optimization Analytics</h1>
            <p className="text-xs text-muted-foreground">Self-optimizing runtime feedback and autonomous tuning</p>
          </div>
        </div>
        <IconButton icon={<RefreshCw className="h-3.5 w-3.5" />} title="Refresh" />
      </div>

      {/* Summary */}
      <div className="grid grid-cols-5 gap-2">
        {[
          { label: 'Active Cycles', value: tuningCycles.filter(c => c.cycle_state === 'running').length, icon: <RefreshCw className="h-3.5 w-3.5" /> },
          { label: 'Completed', value: tuningCycles.filter(c => c.cycle_state === 'completed').length, icon: <CheckCircle2 className="h-3.5 w-3.5" /> },
          { label: 'Total Records', value: tuningRecords.length, icon: <Zap className="h-3.5 w-3.5" /> },
          { label: 'Avg Improvement', value: '11.2%', icon: <TrendingUp className="h-3.5 w-3.5" />, trend: 'up' },
          { label: 'Feedback Signals', value: outcomeData.reduce((s, o) => s + o.count, 0), icon: <Activity className="h-3.5 w-3.5" /> },
        ].map((stat, i) => (
          <div key={i} className="rounded border border-border bg-card px-3 py-2">
            <div className="flex items-center gap-1.5 mb-0.5">
              <span className="text-muted-foreground">{stat.icon}</span>
              <span className="text-[10px] text-muted-foreground uppercase tracking-wider">{stat.label}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-lg font-mono font-semibold">{stat.value}</span>
              {stat.trend && stat.trend === 'up' && <TrendingUp className="h-3 w-3 text-green-500" />}
            </div>
          </div>
        ))}
      </div>

      <TabBar tabs={tabs} active={activeTab} onChange={setActiveTab} />

      {activeTab === 'overview' && (
        <div className="grid gap-4 lg:grid-cols-3">
          {/* Active Tuning Cycles */}
          <ConsolePanel title="Active Tuning Cycles" icon={<RefreshCw className="h-4 w-4" />} subtitle="Currently running optimization loops">
            <div className="space-y-3">
              {tuningCycles.filter(c => c.cycle_state === 'running').map(c => (
                <div key={c.cycle_id} className="p-3 rounded border border-border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono">{c.context_key}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-500">RUNNING</span>
                  </div>
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Target Metric</span>
                      <span className="font-mono">{c.target_metric}</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Progress</span>
                      <span className="font-mono">{c.iteration}/{c.max_iterations}</span>
                    </div>
                    <ProgressBar value={(c.iteration / c.max_iterations) * 100} showValue />
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Target Improvement</span>
                      <span className="font-mono">{(c.target_improvement * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              ))}
              {tuningCycles.filter(c => c.cycle_state === 'completed').length > 0 && (
                <div className="pt-2 mt-2 border-t border-border">
                  <div className="text-[10px] text-muted-foreground mb-2">Recently completed:</div>
                  {tuningCycles.filter(c => c.cycle_state === 'completed').map(c => (
                    <div key={c.cycle_id} className="flex items-center justify-between py-1.5 border-b border-border/50 last:border-0">
                      <span className="text-xs font-mono text-muted-foreground">{c.context_key}</span>
                      <span className="text-xs font-mono text-green-500">
                        {c.best_score ? `${(c.best_score * 100).toFixed(1)}%` : '-'}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </ConsolePanel>

          {/* Outcome Trends */}
          <ConsolePanel title="Outcome Trends" icon={<TrendingUp className="h-4 w-4" />} subtitle="Aggregate feedback by type">
            <div className="space-y-3">
              {outcomeData.map(o => (
                <div key={o.feedback_type} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium">{o.feedback_type}</span>
                    <div className="flex items-center gap-3 text-[10px]">
                      <span className="text-muted-foreground">n={o.count}</span>
                      <span className={`font-mono ${o.mean_delta >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {o.mean_delta >= 0 ? '+' : ''}{(o.mean_delta * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                    <div
                      className="h-full bg-primary"
                      style={{ width: `${Math.min(100, o.mean_actual * (o.feedback_type === 'error_rate' ? 100 : o.feedback_type === 'quality' ? 100 : 50))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>

          {/* Optimization Summary */}
          <ConsolePanel title="Optimization Summary" icon={<Target className="h-4 w-4" />} subtitle="Key optimization metrics">
            <div className="space-y-2">
              {[
                { label: 'Avg Improvement', value: '11.2%', delta: 2.3 },
                { label: 'Best Score', value: '0.89', delta: 0.05 },
                { label: 'Cycles Completed', value: '24', delta: 8 },
                { label: 'Avg Cycle Time', value: '45m', delta: -5.2 },
              ].map(m => (
                <div key={m.label} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                  <span className="text-xs text-muted-foreground">{m.label}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-mono font-semibold">{m.value}</span>
                    <span className={`text-[10px] font-mono ${m.delta >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {m.delta >= 0 ? '+' : ''}{m.delta}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>

          {/* Recent Tuning Records */}
          <ConsolePanel title="Recent Tuning" icon={<Zap className="h-4 w-4" />} subtitle="Latest parameter adjustments">
            <div className="space-y-2">
              {tuningRecords.slice(0, 4).map(r => (
                <div key={r.id} className="flex items-center justify-between py-1.5 border-b border-border/50 last:border-0">
                  <div>
                    <span className="text-xs font-mono">{r.parameter}</span>
                    <div className="text-[10px] text-muted-foreground">{r.action}</div>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-mono">
                    <span className="text-muted-foreground">{r.before}</span>
                    <span className="text-muted-foreground">→</span>
                    <span className="text-primary">{r.after}</span>
                    <span className={`text-[10px] ${r.delta >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      ({r.delta >= 0 ? '+' : ''}{r.delta})
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>

          {/* Improvement History */}
          <ConsolePanel title="Improvement History" icon={<Activity className="h-4 w-4" />} subtitle="Rolling improvement trend">
            <div className="h-24 flex items-end gap-1">
              {[12, 8, 15, 11, 14, 9, 16, 12, 18, 11].map((v, i) => (
                <div key={i} className="flex-1 rounded-t-sm bg-primary/80" style={{ height: `${(v / 20) * 100}%` }} title={`${v}%`} />
              ))}
            </div>
            <div className="flex items-center justify-between mt-2 text-[10px] text-muted-foreground">
              <span>10 cycles ago</span>
              <span className="text-primary">+11.2% avg</span>
              <span>now</span>
            </div>
          </ConsolePanel>

          {/* Confidence Trend */}
          <ConsolePanel title="Tuning Confidence" icon={<Gauge className="h-4 w-4" />} subtitle="Confidence of active tuning cycles">
            <div className="space-y-2">
              {tuningCycles.filter(c => c.cycle_state === 'running').map(c => {
                const conf = 0.75 + (c.iteration / c.max_iterations) * 0.15
                return (
                  <div key={c.cycle_id} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-mono text-muted-foreground truncate max-w-28">{c.context_key}</span>
                      <ConfidenceBadge value={conf} />
                    </div>
                    <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                      <div className="h-full bg-primary" style={{ width: `${conf * 100}%` }} />
                    </div>
                  </div>
                )
              })}
              {tuningCycles.filter(c => c.cycle_state === 'running').length === 0 && (
                <p className="text-xs text-muted-foreground text-center py-4">No active tuning cycles</p>
              )}
            </div>
          </ConsolePanel>
        </div>
      )}

      {activeTab === 'feedback' && (
        <ConsolePanel title="Feedback Signals" icon={<Activity className="h-4 w-4" />} subtitle="Runtime outcome signals">
          <DataTable
            columns={[
              { key: 'type', label: 'Feedback Type', width: '15%' },
              { key: 'subject', label: 'Subject', width: '20%' },
              { key: 'expected', label: 'Expected', width: '12%' },
              { key: 'actual', label: 'Actual', width: '12%' },
              { key: 'delta', label: 'Delta %', width: '12%' },
              { key: 'quality', label: 'Quality', width: '12%' },
              { key: 'time', label: 'Observed', width: '17%' },
            ]}
            rows={outcomeData.map(o => ({
              type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{o.feedback_type}</span>,
              subject: <span className="text-xs text-muted-foreground">-</span>,
              expected: <span className="font-mono text-xs">{o.mean_actual.toFixed(o.feedback_type === 'quality' ? 2 : 0)}</span>,
              actual: <span className="font-mono text-xs">{o.mean_actual.toFixed(o.feedback_type === 'quality' ? 2 : 0)}</span>,
              delta: <span className={`font-mono text-xs ${o.mean_delta >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {o.mean_delta >= 0 ? '+' : ''}{(o.mean_delta * 100).toFixed(0)}%
              </span>,
              quality: <span className="font-mono text-xs">{Math.round(o.mean_quality * 100)}%</span>,
              time: <span className="text-xs text-muted-foreground">Rolling window</span>,
            }))}
          />
        </ConsolePanel>
      )}

      {activeTab === 'tuning' && (
        <ConsolePanel title="Tuning Records" icon={<RefreshCw className="h-4 w-4" />} subtitle="Parameter adjustment history">
          <DataTable
            columns={[
              { key: 'parameter', label: 'Parameter', width: '18%' },
              { key: 'before_after', label: 'Before → After', width: '20%' },
              { key: 'delta', label: 'Delta', width: '10%' },
              { key: 'action', label: 'Action', width: '12%' },
              { key: 'reason', label: 'Reason', width: '20%' },
              { key: 'confidence', label: 'Confidence', width: '10%' },
              { key: 'state', label: 'State', width: '10%' },
            ]}
            rows={tuningRecords.map(r => ({
              parameter: <span className="font-mono text-xs">{r.parameter}</span>,
              before_after: (
                <div className="flex items-center gap-1.5 text-xs font-mono">
                  <span className="text-muted-foreground">{r.before}</span>
                  <span className="text-muted-foreground">→</span>
                  <span className="text-primary">{r.after}</span>
                </div>
              ),
              delta: <span className={`font-mono text-xs ${r.delta >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {r.delta >= 0 ? '+' : ''}{r.delta}
              </span>,
              action: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{r.action}</span>,
              reason: <span className="text-[10px] text-muted-foreground truncate max-w-48">{r.reason}</span>,
              confidence: <ConfidenceBadge value={r.confidence} showLabel={false} />,
              state: <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/10 text-green-500">{r.state}</span>,
            }))}
          />
        </ConsolePanel>
      )}

      {activeTab === 'outcomes' && (
        <div className="grid gap-4 lg:grid-cols-2">
          <ConsolePanel title="Outcome Analysis" icon={<BarChart3 className="h-4 w-4" />} subtitle="Aggregate metrics by feedback type">
            <div className="space-y-4">
              {outcomeData.map(o => (
                <div key={o.feedback_type} className="p-3 rounded border border-border">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-medium">{o.feedback_type}</span>
                    <span className="text-xs font-mono text-muted-foreground">n={o.count}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">Mean Actual</div>
                      <div className="text-lg font-mono font-semibold">{o.mean_actual.toFixed(o.feedback_type === 'quality' || o.feedback_type === 'error_rate' ? 2 : 0)}</div>
                    </div>
                    <div>
                      <div className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">Delta</div>
                      <div className={`text-lg font-mono font-semibold ${o.mean_delta >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {o.mean_delta >= 0 ? '+' : ''}{(o.mean_delta * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">Quality</div>
                      <div className="text-lg font-mono font-semibold">{Math.round(o.mean_quality * 100)}%</div>
                    </div>
                    <div>
                      <div className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">Improvement</div>
                      <div className="text-lg font-mono font-semibold text-green-500">{(o.mean_delta * 100 / Math.abs(o.mean_delta || 1)).toFixed(0)}%</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>

          <ConsolePanel title="Tuning Cycle Performance" icon={<Layers className="h-4 w-4" />} subtitle="Performance of completed cycles">
            <div className="space-y-3">
              {tuningCycles.map(c => (
                <div key={c.cycle_id} className="p-3 rounded border border-border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono">{c.context_key}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                      c.cycle_state === 'completed' ? 'bg-green-500/10 text-green-500' :
                      c.cycle_state === 'running' ? 'bg-blue-500/10 text-blue-500' :
                      'bg-muted text-muted-foreground'
                    }`}>{c.cycle_state}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-3 text-xs">
                    <div>
                      <div className="text-[10px] text-muted-foreground">Target</div>
                      <div className="font-mono">{c.target_metric}</div>
                    </div>
                    <div>
                      <div className="text-[10px] text-muted-foreground">Iterations</div>
                      <div className="font-mono">{c.iteration}/{c.max_iterations}</div>
                    </div>
                    <div>
                      <div className="text-[10px] text-muted-foreground">Best Score</div>
                      <div className="font-mono text-green-500">
                        {c.best_score ? `${(c.best_score * 100).toFixed(1)}%` : '-'}
                      </div>
                    </div>
                  </div>
                  <div className="mt-2">
                    <ProgressBar value={(c.iteration / c.max_iterations) * 100} showValue />
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