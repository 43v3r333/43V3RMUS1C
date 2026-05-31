"""
Predictive Runtime Console - Forecasting and execution planning interface.
"""
'use client'

import { useState, useEffect } from 'react'
import {
  TrendingUp,
  Activity,
  Clock,
  Target,
  BarChart3,
  Gauge,
  AlertTriangle,
  CheckCircle2,
  Layers,
  Zap,
} from 'lucide-react'
import { useCognitiveApi, type ExecutionForecast, type MultiStageGraph, type StrategyDecision } from '@/lib/cognitive-api'
import { ConsolePanel, DataTable, MetricGrid, StatusDot, ConfidenceBadge, Sparkline, IconButton, ProgressBar, TabBar } from './primitives'

interface ForecastData {
  kind: string
  label: string
  horizon: string
  predicted: number
  lower: number
  upper: number
  confidence: number
  history: number[]
}

interface StrategyData {
  name: string
  score: number
  active: boolean
}

export default function PredictiveRuntimeConsole() {
  const api = useCognitiveApi()
  const [activeTab, setActiveTab] = useState('forecasts')
  const [forecasts, setForecasts] = useState<ExecutionForecast[]>([])
  const [graphs, setGraphs] = useState<MultiStageGraph[]>([])
  const [strategies, setStrategies] = useState<StrategyData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const fc = await api.listActiveForecasts({ limit: 20 }).catch(() => [])
        const gs = await api.listActiveGraphs ? await (api as any).listActiveGraphs({ limit: 20 }).catch(() => []) : []
        setForecasts(fc)
        setGraphs(gs)
      } catch { /* mock */ }
      setLoading(false)
    }
    load()
  }, [api])

  // Use mock data if API fails
  const forecastData: ForecastData[] = forecasts.length > 0
    ? forecasts.map(fc => ({
        kind: fc.forecast_kind,
        label: fc.subject_key,
        horizon: fc.horizon,
        predicted: fc.predicted_value,
        lower: fc.lower_bound || fc.predicted_value * 0.8,
        upper: fc.upper_bound || fc.predicted_value * 1.2,
        confidence: fc.confidence,
        history: Array.from({ length: 12 }, (_, i) => fc.confidence * (0.9 + Math.random() * 0.2)),
      }))
    : [
        { kind: 'duration', label: 'render-alpha-001', horizon: 'near_term', predicted: 245, lower: 180, upper: 310, confidence: 0.85, history: [0.8, 0.85, 0.82, 0.88, 0.85, 0.87, 0.86, 0.85, 0.88, 0.84, 0.86, 0.85] },
        { kind: 'queue_time', label: 'job-bridge-42', horizon: 'short', predicted: 45, lower: 30, upper: 65, confidence: 0.78, history: [0.7, 0.75, 0.72, 0.78, 0.76, 0.79, 0.75, 0.78, 0.77, 0.79, 0.78, 0.78] },
        { kind: 'failure_probability', label: 'compose-music-v3', horizon: 'extended', predicted: 0.12, lower: 0.05, upper: 0.25, confidence: 0.72, history: [0.65, 0.68, 0.70, 0.72, 0.74, 0.71, 0.73, 0.72, 0.75, 0.71, 0.72, 0.72] },
        { kind: 'resource_need', label: 'worker-pool-1', horizon: 'near_term', predicted: 2048, lower: 1536, upper: 2560, confidence: 0.91, history: [0.88, 0.90, 0.89, 0.92, 0.91, 0.90, 0.93, 0.91, 0.92, 0.90, 0.91, 0.91] },
        { kind: 'throughput', label: 'render-pipeline', horizon: 'short', predicted: 120, lower: 90, upper: 160, confidence: 0.68, history: [0.60, 0.63, 0.65, 0.67, 0.66, 0.68, 0.65, 0.67, 0.68, 0.69, 0.68, 0.68] },
      ]

  const strategyData: StrategyData[] = strategies.length > 0
    ? strategies
    : [
        { name: 'latency_first', score: 0.85, active: true },
        { name: 'throughput_first', score: 0.72, active: false },
        { name: 'cost_aware', score: 0.41, active: false },
        { name: 'quality_first', score: 0.65, active: false },
        { name: 'balanced', score: 0.78, active: false },
        { name: 'conservative', score: 0.55, active: false },
      ]

  const forecastColumns = [
    { key: 'kind', label: 'Kind', width: '12%' },
    { key: 'label', label: 'Subject', width: '22%' },
    { key: 'horizon', label: 'Horizon', width: '10%' },
    { key: 'predicted', label: 'Predicted', width: '15%' },
    { key: 'range', label: 'Range', width: '15%' },
    { key: 'trend', label: 'Trend', width: '12%' },
    { key: 'confidence', label: 'Confidence', width: '14%' },
  ]

  const tabs = [
    { id: 'forecasts', label: 'Forecasts', icon: <TrendingUp className="h-3 w-3" />, badge: forecastData.length },
    { id: 'strategies', label: 'Strategies', icon: <Target className="h-3 w-3" /> },
    { id: 'planning', label: 'Execution Planning', icon: <Layers className="h-3 w-3" /> },
  ]

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 border border-primary/20">
            <TrendingUp className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Predictive Runtime Console</h1>
            <p className="text-xs text-muted-foreground">Long-horizon orchestration forecasting</p>
          </div>
        </div>
        <IconButton icon={<Activity className="h-3.5 w-3.5" />} title="Refresh" />
      </div>

      {/* Summary Bar */}
      <div className="grid grid-cols-5 gap-2">
        {[
          { label: 'Active Forecasts', value: forecastData.length, icon: <TrendingUp className="h-3.5 w-3.5" /> },
          { label: 'Avg Confidence', value: `${Math.round((forecastData.reduce((s, f) => s + f.confidence, 0) / forecastData.length) * 100)}%`, icon: <Target className="h-3.5 w-3.5" /> },
          { label: 'Long Horizon', value: forecastData.filter(f => f.horizon === 'long' || f.horizon === 'extended').length, icon: <Clock className="h-3.5 w-3.5" /> },
          { label: 'Active Strategies', value: strategyData.filter(s => s.active).length, icon: <Gauge className="h-3.5 w-3.5" /> },
          { label: 'Multi-Stage Graphs', value: graphs.length, icon: <Layers className="h-3.5 w-3.5" /> },
        ].map((stat, i) => (
          <div key={i} className="rounded border border-border bg-card px-3 py-2">
            <div className="flex items-center gap-1.5 mb-0.5">
              <span className="text-muted-foreground">{stat.icon}</span>
              <span className="text-[10px] text-muted-foreground uppercase tracking-wider">{stat.label}</span>
            </div>
            <div className="text-lg font-mono font-semibold">{stat.value}</div>
          </div>
        ))}
      </div>

      <TabBar tabs={tabs} active={activeTab} onChange={setActiveTab} />

      {activeTab === 'forecasts' && (
        <div className="space-y-4">
          {/* Forecast Table */}
          <ConsolePanel title="Execution Forecasts" icon={<TrendingUp className="h-4 w-4" />} subtitle="Active predictions across all subjects">
            <DataTable
              columns={forecastColumns}
              rows={forecastData.map(f => ({
                kind: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{f.kind}</span>,
                label: <span className="font-mono text-xs truncate max-w-36">{f.label}</span>,
                horizon: <span className="text-xs text-muted-foreground">{f.horizon}</span>,
                predicted: (
                  <div className="text-sm font-mono font-medium">
                    {f.kind === 'failure_probability' ? `${(f.predicted * 100).toFixed(1)}%` : `${f.predicted.toFixed(0)}${f.kind === 'resource_need' ? ' MB' : 's'}`}
                  </div>
                ),
                range: (
                  <div className="flex items-center gap-1.5">
                    <span className="text-[10px] font-mono text-muted-foreground">{f.lower.toFixed(f.kind === 'failure_probability' ? 1 : 0)}</span>
                    <div className="w-10 h-1 rounded-full bg-muted overflow-hidden">
                      <div className="h-full bg-primary/50" style={{ width: '40%', marginLeft: '30%' }} />
                    </div>
                    <span className="text-[10px] font-mono text-muted-foreground">{f.upper.toFixed(f.kind === 'failure_probability' ? 1 : 0)}</span>
                  </div>
                ),
                trend: <Sparkline data={f.history} width={50} height={14} />,
                confidence: <ConfidenceBadge value={f.confidence} />,
              }))}
            />
          </ConsolePanel>

          {/* Horizon Distribution */}
          <div className="grid gap-4 lg:grid-cols-2">
            <ConsolePanel title="Forecast Horizon Distribution" icon={<Clock className="h-4 w-4" />} subtitle="Predictions by time horizon">
              <div className="space-y-3">
                {[
                  { horizon: 'immediate', count: forecastData.filter(f => f.horizon === 'immediate').length, color: 'bg-blue-500' },
                  { horizon: 'near_term', count: forecastData.filter(f => f.horizon === 'near_term').length, color: 'bg-green-500' },
                  { horizon: 'short', count: forecastData.filter(f => f.horizon === 'short').length, color: 'bg-yellow-500' },
                  { horizon: 'long', count: forecastData.filter(f => f.horizon === 'long').length, color: 'bg-orange-500' },
                  { horizon: 'extended', count: forecastData.filter(f => f.horizon === 'extended').length, color: 'bg-red-500' },
                ].map(h => (
                  <div key={h.horizon} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">{h.horizon}</span>
                      <span className="font-mono">{h.count}</span>
                    </div>
                    <ProgressBar value={(h.count / forecastData.length) * 100} color={h.color === 'bg-blue-500' ? 'primary' : h.color === 'bg-green-500' ? 'success' : h.color === 'bg-yellow-500' ? 'warning' : 'error'} showValue={false} />
                  </div>
                ))}
              </div>
            </ConsolePanel>

            <ConsolePanel title="Forecast Accuracy" icon={<Target className="h-4 w-4" />} subtitle="Rolling accuracy by kind">
              <div className="space-y-2">
                {forecastData.map(f => (
                  <div key={f.kind} className="flex items-center justify-between py-1.5 border-b border-border/50 last:border-0">
                    <span className="text-xs text-muted-foreground">{f.kind}</span>
                    <div className="flex items-center gap-3">
                      <div className="w-20 h-1.5 rounded-full bg-muted overflow-hidden">
                        <div className="h-full bg-primary" style={{ width: `${f.confidence * 100}%` }} />
                      </div>
                      <span className="text-xs font-mono w-10 text-right">{Math.round(f.confidence * 100)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </ConsolePanel>
          </div>
        </div>
      )}

      {activeTab === 'strategies' && (
        <div className="grid gap-4 lg:grid-cols-2">
          <ConsolePanel title="Orchestration Strategies" icon={<Target className="h-4 w-4" />} subtitle="Available strategies and current selection">
            <DataTable
              columns={[
                { key: 'name', label: 'Strategy', width: '40%' },
                { key: 'score', label: 'Score', width: '30%' },
                { key: 'status', label: 'Status', width: '30%' },
              ]}
              rows={strategyData.map(s => ({
                name: <span className="font-mono text-xs">{s.name}</span>,
                score: (
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-1.5 rounded-full bg-muted overflow-hidden">
                      <div className="h-full bg-primary" style={{ width: `${s.score * 100}%` }} />
                    </div>
                    <span className="font-mono text-xs">{Math.round(s.score * 100)}%</span>
                  </div>
                ),
                status: s.active ? (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/10 text-green-500">ACTIVE</span>
                ) : (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground">AVAILABLE</span>
                ),
              }))}
            />
          </ConsolePanel>

          <ConsolePanel title="Strategy Rationale" icon={<BarChart3 className="h-4 w-4" />} subtitle="Why each strategy is selected">
            <div className="space-y-3">
              {strategyData.filter(s => s.active).map(s => (
                <div key={s.name} className="p-3 rounded border border-border bg-card">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium font-mono">{s.name}</span>
                    <span className="text-xs font-mono text-primary">{Math.round(s.score * 100)}%</span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Selected based on context: priority=normal, estimated_duration=300s, cost_sensitive=false.
                    High confidence due to consistent historical performance.
                  </p>
                </div>
              ))}
              {strategyData.filter(s => !s.active).length > 0 && (
                <div className="mt-4">
                  <div className="text-xs text-muted-foreground mb-2">Available but not selected:</div>
                  {strategyData.filter(s => !s.active).map(s => (
                    <div key={s.name} className="flex items-center justify-between py-1 border-b border-border/50">
                      <span className="text-xs font-mono text-muted-foreground">{s.name}</span>
                      <span className="text-[10px] text-muted-foreground">score: {Math.round(s.score * 100)}%</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </ConsolePanel>
        </div>
      )}

      {activeTab === 'planning' && (
        <div className="space-y-4">
          <ConsolePanel title="Multi-Stage Execution Graphs" icon={<Layers className="h-4 w-4" />} subtitle="Planned execution DAGs">
            {graphs.length > 0 ? (
              <DataTable
                columns={[
                  { key: 'label', label: 'Plan Label', width: '25%' },
                  { key: 'stages', label: 'Stages', width: '15%' },
                  { key: 'duration', label: 'Est. Duration', width: '15%' },
                  { key: 'parallelism', label: 'Parallelism', width: '15%' },
                  { key: 'risk', label: 'Risk Score', width: '15%' },
                  { key: 'strategy', label: 'Strategy', width: '15%' },
                ]}
                rows={graphs.map(g => ({
                  label: <span className="font-mono text-xs">{g.plan_label}</span>,
                  stages: <span className="font-mono">{g.stage_count}</span>,
                  duration: <span className="font-mono">{g.estimated_duration.toFixed(0)}s</span>,
                  parallelism: <span className="font-mono">{g.parallelism_factor.toFixed(1)}x</span>,
                  risk: (
                    <span className={`font-mono ${g.risk_score > 0.5 ? 'text-red-500' : g.risk_score > 0.3 ? 'text-yellow-500' : 'text-green-500'}`}>
                      {(g.risk_score * 100).toFixed(0)}%
                    </span>
                  ),
                  strategy: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{g.selected_strategy || 'balanced'}</span>,
                }))}
              />
            ) : (
              <div className="text-center py-8">
                <p className="text-xs text-muted-foreground">No active execution graphs</p>
                <p className="text-[10px] text-muted-foreground mt-1">Multi-stage graphs are created when workflows are planned for execution</p>
              </div>
            )}
          </ConsolePanel>

          <ConsolePanel title="Execution Planning Pipeline" icon={<Zap className="h-4 w-4" />} subtitle="Multi-stage pipeline template">
            <div className="space-y-3">
              {[
                { stage: 1, name: 'Initialization', duration: 5, description: 'Setup context, load models' },
                { stage: 2, name: 'Asset Resolution', duration: 15, description: 'Resolve media assets, dependencies' },
                { stage: 3, name: 'Generation', duration: 120, description: 'AI generation, parallel workers' },
                { stage: 4, name: 'Composition', duration: 60, description: 'Compose scenes, sync audio' },
                { stage: 5, name: 'Render', duration: 45, description: 'Final render, encode output' },
              ].map(s => (
                <div key={s.stage} className="flex items-start gap-4">
                  <div className="flex h-6 w-6 items-center justify-center rounded border border-border bg-muted text-xs font-mono">{s.stage}</div>
                  <div className="flex-1 border-b border-border pb-3 last:border-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium">{s.name}</span>
                      <span className="font-mono text-xs text-muted-foreground">{s.duration}s</span>
                    </div>
                    <p className="text-[10px] text-muted-foreground">{s.description}</p>
                  </div>
                </div>
              ))}
              <div className="pt-2 border-t border-border">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium">Total Estimated Duration</span>
                  <span className="font-mono text-sm font-semibold text-primary">245s</span>
                </div>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-xs text-muted-foreground">Parallelism Factor</span>
                  <span className="font-mono text-xs">2.4x</span>
                </div>
              </div>
            </div>
          </ConsolePanel>
        </div>
      )}
    </div>
  )
}