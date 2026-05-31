/**
 * Predictive Cognition Analytics
 * Anticipatory cognition health predictions and risk assessment.
 */
'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  TrendingUp,
  AlertTriangle,
  Clock,
  RefreshCw,
  Play,
  Pause,
  Target,
  Zap,
  Shield,
  Activity,
  Eye,
} from 'lucide-react'
import {
  useMetaCognitionApi,
  type PredictiveCognitionForecast,
} from '@/lib/meta-cognition-api'
import { ConsolePanel, DataTable, StatusDot, ConfidenceBadge, IconButton, ProgressBar, TabBar, Sparkline } from '@/components/cognitive/primitives'

// ==================== Mock Data ====================

const mockForecasts: PredictiveCognitionForecast[] = [
  {
    forecast_id: 'forecast_001',
    target_id: 'exec_render_001',
    target_type: 'execution',
    scope: 'global',
    forecast_kind: 'cognition_drift',
    horizon: 'near_term',
    predicted_value: 0.82,
    confidence: 0.75,
    probability: 0.15,
    min_value: 0.75,
    max_value: 0.89,
    risk_factors: ['low_reasoning_quality'],
    recommended_actions: ['run_full_diagnostics'],
    risk_level: 'low',
    predicted_for: new Date(Date.now() + 1800000).toISOString(),
    generated_at: new Date(Date.now() - 300000).toISOString(),
    predicted: true,
  },
  {
    forecast_id: 'forecast_002',
    target_id: 'exec_compose_002',
    target_type: 'execution',
    scope: 'orchestration',
    forecast_kind: 'cognition_drift',
    horizon: 'short',
    predicted_value: 0.68,
    confidence: 0.68,
    probability: 0.42,
    risk_factors: ['low_reasoning_quality', 'inconsistent_semantics'],
    recommended_actions: ['run_full_diagnostics', 'initiate_reconciliation'],
    risk_level: 'medium',
    predicted_for: new Date(Date.now() + 3600000).toISOString(),
    generated_at: new Date(Date.now() - 600000).toISOString(),
    predicted: true,
  },
  {
    forecast_id: 'forecast_003',
    target_id: 'session_monitor_001',
    target_type: 'session',
    scope: 'semantic',
    forecast_kind: 'cognition_drift',
    horizon: 'immediate',
    predicted_value: 0.91,
    confidence: 0.88,
    probability: 0.08,
    risk_factors: [],
    recommended_actions: [],
    risk_level: 'low',
    predicted_for: new Date(Date.now() + 300000).toISOString(),
    generated_at: new Date(Date.now() - 120000).toISOString(),
    predicted: true,
  },
]

// ==================== Main Component ====================

export default function PredictiveCognitionAnalytics() {
  const api = useMetaCognitionApi()
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [forecasts, setForecasts] = useState<PredictiveCognitionForecast[]>([])
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  // Load data
  const loadData = useCallback(async () => {
    try {
      // Would load from API
      setForecasts(mockForecasts)
    } catch {
      setForecasts(mockForecasts)
    }
    setLastRefresh(new Date())
    setLoading(false)
  }, [api])

  useEffect(() => {
    loadData()
    
    let interval: NodeJS.Timeout | null = null
    if (autoRefresh) {
      interval = setInterval(loadData, 8000)
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [loadData, autoRefresh])

  // Tabs
  const tabs = [
    { id: 'overview', label: 'Overview', icon: <TrendingUp className="h-3 w-3" /> },
    { id: 'forecasts', label: 'Forecasts', icon: <Target className="h-3 w-3" /> },
    { id: 'risk', label: 'Risk Assessment', icon: <AlertTriangle className="h-3 w-3" /> },
  ]

  // Calculate metrics
  const lowRiskCount = forecasts.filter(f => f.risk_level === 'low').length
  const mediumRiskCount = forecasts.filter(f => f.risk_level === 'medium').length
  const highRiskCount = forecasts.filter(f => f.risk_level === 'high').length
  const avgProbability = forecasts.length > 0
    ? forecasts.reduce((sum, f) => sum + f.probability, 0) / forecasts.length
    : 0
  const avgConfidence = forecasts.length > 0
    ? forecasts.reduce((sum, f) => sum + f.confidence, 0) / forecasts.length
    : 0

  // Generate sparkline
  function generateSparkline(base: number, length = 12): number[] {
    const data: number[] = []
    let current = base
    for (let i = 0; i < length; i++) {
      current = current + (Math.random() - 0.5) * 0.08
      data.push(Math.max(0, Math.min(1, current)))
    }
    return data
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex items-center gap-2 text-muted-foreground">
          <RefreshCw className="h-4 w-4 animate-spin" />
          <span className="text-sm">Loading Predictive Cognition...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 border border-primary/20">
            <TrendingUp className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Predictive Cognition Analytics</h1>
            <p className="text-xs text-muted-foreground">Anticipatory cognition health predictions and risk assessment</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs">
            <Clock className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="text-muted-foreground">Last: {lastRefresh.toLocaleTimeString()}</span>
          </div>
          <IconButton
            icon={autoRefresh ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
            title={autoRefresh ? 'Pause' : 'Resume'}
            onClick={() => setAutoRefresh(!autoRefresh)}
          />
          <IconButton icon={<RefreshCw className="h-3.5 w-3.5" />} title="Refresh" onClick={loadData} />
        </div>
      </div>

      {/* Summary Grid */}
      <div className="grid grid-cols-6 gap-2">
        {[
          { label: 'Total Forecasts', value: forecasts.length, icon: <Target className="h-3.5 w-3.5" /> },
          { label: 'Avg Probability', value: `${(avgProbability * 100).toFixed(1)}%`, icon: <Activity className="h-3.5 w-3.5" /> },
          { label: 'Avg Confidence', value: `${(avgConfidence * 100).toFixed(0)}%`, icon: <Shield className="h-3.5 w-3.5" /> },
          { label: 'Low Risk', value: lowRiskCount, icon: <Zap className="h-3.5 w-3.5" />, color: 'text-green-500' },
          { label: 'Medium Risk', value: mediumRiskCount, icon: <AlertTriangle className="h-3.5 w-3.5" />, color: 'text-yellow-500' },
          { label: 'High Risk', value: highRiskCount, icon: <AlertTriangle className="h-3.5 w-3.5" />, color: 'text-red-500' },
        ].map((stat, i) => (
          <div key={i} className="rounded border border-border bg-card px-3 py-2">
            <div className="flex items-center gap-1.5 mb-0.5">
              <span className="text-muted-foreground">{stat.icon}</span>
              <span className="text-[10px] text-muted-foreground uppercase tracking-wider">{stat.label}</span>
            </div>
            <div className={`text-lg font-mono font-semibold ${stat.color || ''}`}>{stat.value}</div>
          </div>
        ))}
      </div>

      <TabBar tabs={tabs} active={activeTab} onChange={setActiveTab} />

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-4">
          {/* Forecast Summary */}
          <div className="grid grid-cols-3 gap-4">
            {forecasts.slice(0, 3).map((forecast) => (
              <ConsolePanel
                key={forecast.forecast_id}
                title={`${forecast.target_type.toUpperCase()}: ${forecast.target_id.slice(0, 12)}...`}
                icon={forecast.risk_level === 'high' ? <AlertTriangle className="h-4 w-4 text-red-500" /> :
                       forecast.risk_level === 'medium' ? <AlertTriangle className="h-4 w-4 text-yellow-500" /> :
                       <Shield className="h-4 w-4 text-green-500" />}
                subtitle={`${forecast.horizon.replace('_', ' ')} horizon`}
              >
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <div className="text-[10px] text-muted-foreground uppercase tracking-wider">Probability</div>
                      <div className="text-lg font-mono">{(forecast.probability * 100).toFixed(1)}%</div>
                    </div>
                    <div>
                      <div className="text-[10px] text-muted-foreground uppercase tracking-wider">Confidence</div>
                      <div className="text-lg font-mono">{(forecast.confidence * 100).toFixed(0)}%</div>
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">Predicted Value</div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 rounded bg-muted overflow-hidden">
                        <div
                          className={`h-full rounded ${
                            forecast.predicted_value >= 0.8 ? 'bg-green-500' :
                            forecast.predicted_value >= 0.6 ? 'bg-yellow-500' :
                            'bg-red-500'
                          }`}
                          style={{ width: `${forecast.predicted_value * 100}%` }}
                        />
                      </div>
                      <span className="font-mono text-sm">{(forecast.predicted_value * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                  <div className={`text-[10px] px-1.5 py-0.5 rounded inline-block ${
                    forecast.risk_level === 'high' ? 'bg-red-500/10 text-red-500' :
                    forecast.risk_level === 'medium' ? 'bg-yellow-500/10 text-yellow-500' :
                    'bg-green-500/10 text-green-500'
                  }`}>{forecast.risk_level.toUpperCase()} RISK</div>
                </div>
              </ConsolePanel>
            ))}
          </div>

          {/* Risk Trend */}
          <ConsolePanel title="Probability Trend" icon={<TrendingUp className="h-4 w-4" />} subtitle="Cognition drift probability over time">
            <Sparkline data={generateSparkline(avgProbability)} height={48} color="#22c55e" />
          </ConsolePanel>
        </div>
      )}

      {/* Forecasts Tab */}
      {activeTab === 'forecasts' && (
        <ConsolePanel title="All Forecasts" icon={<Target className="h-4 w-4" />} subtitle={`${forecasts.length} active predictions`}>
          <DataTable
            columns={[
              { key: 'forecast_id', label: 'Forecast ID', width: '14%' },
              { key: 'target', label: 'Target', width: '18%' },
              { key: 'scope', label: 'Scope', width: '10%' },
              { key: 'horizon', label: 'Horizon', width: '10%' },
              { key: 'probability', label: 'Probability', width: '12%' },
              { key: 'value', label: 'Predicted Value', width: '14%' },
              { key: 'risk', label: 'Risk Level', width: '10%' },
              { key: 'predicted_for', label: 'Predicted For', width: '12%' },
            ]}
            rows={forecasts.map(f => ({
              forecast_id: <span className="font-mono text-xs">{f.forecast_id.slice(0, 12)}...</span>,
              target: <div><span className="font-mono text-xs">{f.target_id.slice(0, 10)}...</span><div className="text-[10px] text-muted-foreground">{f.target_type}</div></div>,
              scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{f.scope}</span>,
              horizon: <span className="text-xs">{f.horizon.replace('_', ' ')}</span>,
              probability: <div className="flex items-center gap-2"><ProgressBar value={f.probability * 100} showValue={false} className="w-12" color={f.probability > 0.5 ? 'error' : f.probability > 0.3 ? 'warning' : 'success'} /><span className="font-mono text-xs">{(f.probability * 100).toFixed(0)}%</span></div>,
              value: <span className="font-mono text-xs">{f.predicted_value.toFixed(3)}</span>,
              risk: <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                f.risk_level === 'high' ? 'bg-red-500/10 text-red-500' :
                f.risk_level === 'medium' ? 'bg-yellow-500/10 text-yellow-500' :
                'bg-green-500/10 text-green-500'
              }`>{f.risk_level.toUpperCase()}</span>,
              predicted_for: <span className="text-xs text-muted-foreground">{new Date(f.predicted_for).toLocaleTimeString()}</span>,
            }))}
          />
        </ConsolePanel>
      )}

      {/* Risk Assessment Tab */}
      {activeTab === 'risk' && (
        <div className="grid gap-4 lg:grid-cols-2">
          <ConsolePanel title="Risk Factor Analysis" icon={<AlertTriangle className="h-4 w-4" />} subtitle="Identified risk factors">
            <div className="space-y-3">
              {forecasts.filter(f => f.risk_factors && f.risk_factors.length > 0).map((forecast) => (
                <div key={forecast.forecast_id} className="p-3 rounded border border-border bg-card">
                  <div className="text-xs font-mono mb-2">{forecast.target_id.slice(0, 12)}...</div>
                  <div className="flex flex-wrap gap-1">
                    {forecast.risk_factors?.map((factor, i) => (
                      <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-red-500/10 text-red-500">
                        {factor.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
              {forecasts.filter(f => f.risk_factors && f.risk_factors.length > 0).length === 0 && (
                <div className="text-center py-4 text-xs text-muted-foreground">
                  No risk factors identified
                </div>
              )}
            </div>
          </ConsolePanel>

          <ConsolePanel title="Recommended Actions" icon={<Zap className="h-4 w-4" />} subtitle="Preventive measures">
            <div className="space-y-3">
              {forecasts.filter(f => f.recommended_actions && f.recommended_actions.length > 0).map((forecast) => (
                <div key={forecast.forecast_id} className="p-3 rounded border border-border bg-card">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono">{forecast.forecast_id.slice(0, 12)}...</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                      forecast.risk_level === 'high' ? 'bg-red-500/10 text-red-500' :
                      forecast.risk_level === 'medium' ? 'bg-yellow-500/10 text-yellow-500' :
                      'bg-green-500/10 text-green-500'
                    }`}>{forecast.risk_level.toUpperCase()}</span>
                  </div>
                  <div className="space-y-1">
                    {forecast.recommended_actions?.map((action, i) => (
                      <div key={i} className="flex items-center gap-2 text-xs">
                        <Zap className="h-3 w-3 text-primary" />
                        <span className="text-muted-foreground">{action.replace(/_/g, ' ')}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
              {forecasts.filter(f => f.recommended_actions && f.recommended_actions.length > 0).length === 0 && (
                <div className="text-center py-4 text-xs text-muted-foreground">
                  No actions recommended
                </div>
              )}
            </div>
          </ConsolePanel>
        </div>
      )}
    </div>
  )
}
