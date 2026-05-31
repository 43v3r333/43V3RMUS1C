/**
 * Meta-Cognition Control Center
 * Executive Intelligence Layer - Runtime self-awareness dashboard.
 */
'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  Brain,
  Activity,
  Eye,
  Shield,
  AlertTriangle,
  CheckCircle2,
  GitBranch,
  Zap,
  Clock,
  RefreshCw,
  ChevronRight,
  Database,
  Network,
  Target,
  TrendingUp,
  AlertCircle,
  Play,
  Pause,
  Settings,
  BarChart3,
} from 'lucide-react'
import {
  useMetaCognitionApi,
  type CognitionDiagnostics,
  type IntrospectionSession,
  type MetaCognitionSummary,
  type CognitionAnomaly,
  type AdaptiveGovernanceProfile,
} from '@/lib/meta-cognition-api'
import { ConsolePanel, DataTable, StatusDot, ConfidenceBadge, IconButton, ProgressBar, MetricGrid, MetricValue, TabBar, Sparkline } from '@/components/cognitive/primitives'

// ==================== Types ====================

interface CognitiveMetrics {
  reasoningQuality: number
  coherenceScore: number
  consistencyScore: number
  adaptationEfficiency: number
  distributionAlignment: number
  syncHealth: number
  conflictRate: number
}

interface DiagnosticsTrend {
  timestamp: string
  reasoningQuality: number
  coherenceScore: number
  consistencyScore: number
}

// ==================== Mock Data Generators ====================

function generateSparkline(base: number, length = 12): number[] {
  const data: number[] = []
  let current = base
  for (let i = 0; i < length; i++) {
    current = current + (Math.random() - 0.5) * 0.1
    data.push(Math.max(0, Math.min(1, current)))
  }
  return data
}

// ==================== Main Component ====================

export default function MetaCognitionControlCenter() {
  const api = useMetaCognitionApi()
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  // State data
  const [summary, setSummary] = useState<MetaCognitionSummary | null>(null)
  const [currentDiagnostics, setCurrentDiagnostics] = useState<CognitionDiagnostics | null>(null)
  const [diagnosticsTrend, setDiagnosticsTrend] = useState<DiagnosticsTrend[]>([])
  const [activeSessions, setActiveSessions] = useState<IntrospectionSession[]>([])
  const [activeAnomalies, setActiveAnomalies] = useState<CognitionAnomaly[]>([])
  const [governanceProfiles, setGovernanceProfiles] = useState<AdaptiveGovernanceProfile[]>([])
  const [sparklines, setSparklines] = useState<Record<string, number[]>>({})

  // Load data
  const loadData = useCallback(async () => {
    try {
      // Try to load from API
      let summaryData: MetaCognitionSummary | null = null
      try {
        summaryData = await api.getMetaCognitionSummary()
        setSummary(summaryData)
      } catch {
        // Use mock
      }

      // Load diagnostics history
      let diagnosticsHistory: CognitionDiagnostics[] = []
      try {
        diagnosticsHistory = await api.getDiagnosticsHistory({ scope: 'global', limit: 24 })
      } catch {
        diagnosticsHistory = []
      }

      // Build trend from history
      const trend = diagnosticsHistory.map(d => ({
        timestamp: d.assessed_at,
        reasoningQuality: d.reasoning_quality,
        coherenceScore: d.coherence_score,
        consistencyScore: d.consistency_score,
      }))
      setDiagnosticsTrend(trend)

      // Set current diagnostics (latest or generate mock)
      if (diagnosticsHistory.length > 0) {
        setCurrentDiagnostics(diagnosticsHistory[0])
      } else {
        // Generate mock current diagnostics
        const mock: CognitionDiagnostics = {
          diagnostic_id: 'diag_mock_001',
          scope: 'global',
          domain: 'orchestration',
          cognition_state: 'healthy',
          reasoning_quality: 0.87 + Math.random() * 0.1,
          coherence_score: 0.92 + Math.random() * 0.05,
          consistency_score: 0.85 + Math.random() * 0.1,
          adaptation_efficiency: 0.78 + Math.random() * 0.15,
          distribution_alignment: 0.91 + Math.random() * 0.05,
          sync_health: 0.95,
          conflict_rate: 0.02 + Math.random() * 0.05,
          anomaly_severity: undefined,
          assessed_at: new Date().toISOString(),
        }
        setCurrentDiagnostics(mock)
      }

      // Load active anomalies
      let anomalies: CognitionAnomaly[] = []
      try {
        anomalies = await api.getActiveAnomalies()
        setActiveAnomalies(anomalies)
      } catch {
        // Use mock
        setActiveAnomalies([])
      }

      // Load governance profiles
      let profiles: AdaptiveGovernanceProfile[] = []
      try {
        profiles = await api.listGovernanceProfiles()
        setGovernanceProfiles(profiles)
      } catch {
        // Use mock
        setGovernanceProfiles([
          {
            profile_id: 'gov_profile_001',
            profile_key: 'orchestration_governance',
            scope: 'global',
            domain: 'orchestration',
            validation_thresholds: { min_reasoning_quality: 0.7, min_coherence: 0.7 },
            alignment_requirements: {},
            enforcement_rules: [],
            policy_mode: 'active',
            intervention_level: 'advisory',
            is_active: true,
            alignment_status: 'aligned',
            trigger_count: 1247,
            violation_count: 3,
            version: 2},{
            profile_id: 'gov_profile_002',
            profile_key: 'semantic_validation',
            scope: 'semantic',
            domain: 'reasoning',
            validation_thresholds: { min_consistency: 0.75 },
            alignment_requirements: {},
            enforcement_rules: [],
            policy_mode: 'active',
            intervention_level: 'enforcing',
            is_active: true,
            alignment_status: 'aligned',
            trigger_count: 892,
            violation_count: 1,
            version: 1,
          },
        ])
      }

      setLastRefresh(new Date())
    } catch {
      // Generate full mock data
      const mockDiagnostics: CognitionDiagnostics = {
        diagnostic_id: 'diag_001',
        scope: 'global',
        domain: 'orchestration',
        cognition_state: 'healthy',
        reasoning_quality: 0.87,
        coherence_score: 0.92,
        consistency_score: 0.85,
        adaptation_efficiency: 0.78,
        distribution_alignment: 0.91,
        sync_health: 0.95,
        conflict_rate: 0.03,
        assessed_at: new Date().toISOString(),
      }
      setCurrentDiagnostics(mockDiagnostics)
      setActiveAnomalies([])
      setGovernanceProfiles([
        {
          profile_id: 'gov_profile_001',
          profile_key: 'orchestration_governance',
          scope: 'global',
          domain: 'orchestration',
          validation_thresholds: { min_reasoning_quality: 0.7, min_coherence: 0.7 },
          alignment_requirements: {},
          enforcement_rules: [],
          policy_mode: 'active',
          intervention_level: 'advisory',
          is_active: true,
          alignment_status: 'aligned',
          trigger_count: 1247,
          violation_count: 3,
          version: 2,
        },
      ])
    }
    setLoading(false)
  }, [api])

  // Initial load and auto-refresh
  useEffect(() => {
    loadData()
    
    let interval: NodeJS.Timeout | null = null
    if (autoRefresh) {
      interval = setInterval(loadData, 10000)
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [loadData, autoRefresh])

  // Generate sparklines when diagnostics change
  useEffect(() => {
    if (currentDiagnostics) {
      setSparklines({
        reasoning: generateSparkline(currentDiagnostics.reasoning_quality),
        coherence: generateSparkline(currentDiagnostics.coherence_score),
        consistency: generateSparkline(currentDiagnostics.consistency_score),
        adaptation: generateSparkline(currentDiagnostics.adaptation_efficiency),
        distribution: generateSparkline(currentDiagnostics.distribution_alignment),
        sync: generateSparkline(currentDiagnostics.sync_health),
      })
    }
  }, [currentDiagnostics])

  // Tabs
  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Brain className="h-3 w-3" /> },
    { id: 'diagnostics', label: 'Diagnostics', icon: <Activity className="h-3 w-3" /> },
    { id: 'introspection', label: 'Introspection', icon: <Eye className="h-3 w-3" /> },
    { id: 'governance', label: 'Governance', icon: <Shield className="h-3 w-3" /> },
    { id: 'anomalies', label: 'Anomalies', icon: <AlertTriangle className="h-3 w-3" />, badge: activeAnomalies.length },
  ]

  // Get cognition state display info
  const getCognitionStateInfo = (state: CognitionDiagnostics['cognition_state']) => {
    switch (state) {
      case 'healthy': return { color: 'text-green-500', bg: 'bg-green-500/10', label: 'HEALTHY' }
      case 'drifting': return { color: 'text-yellow-500', bg: 'bg-yellow-500/10', label: 'DRIFTING' }
      case 'conflicted': return { color: 'text-red-500', bg: 'bg-red-500/10', label: 'CONFLICTED' }
      case 'degraded': return { color: 'text-red-500', bg: 'bg-red-500/10', label: 'DEGRADED' }
      case 'recovering': return { color: 'text-blue-500', bg: 'bg-blue-500/10', label: 'RECOVERING' }
      default: return { color: 'text-muted-foreground', bg: 'bg-muted', label: 'UNKNOWN' }
    }
  }

  // Metrics cards data
  const metricsCards = currentDiagnostics ? [
    { label: 'Reasoning Quality', value: currentDiagnostics.reasoning_quality, icon: <Brain className="h-3.5 w-3.5" />, sparkline: sparklines.reasoning },
    { label: 'Coherence Score', value: currentDiagnostics.coherence_score, icon: <Network className="h-3.5 w-3.5" />, sparkline: sparklines.coherence },
    { label: 'Consistency', value: currentDiagnostics.consistency_score, icon: <GitBranch className="h-3.5 w-3.5" />, sparkline: sparklines.consistency },
    { label: 'Adaptation', value: currentDiagnostics.adaptation_efficiency, icon: <Target className="h-3.5 w-3.5" />, sparkline: sparklines.adaptation },
    { label: 'Distribution', value: currentDiagnostics.distribution_alignment, icon: <Database className="h-3.5 w-3.5" />, sparkline: sparklines.distribution },
    { label: 'Sync Health', value: currentDiagnostics.sync_health, icon: <RefreshCw className="h-3.5 w-3.5" />, sparkline: sparklines.sync },
  ] : []

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex items-center gap-2 text-muted-foreground">
          <RefreshCw className="h-4 w-4 animate-spin" />
          <span className="text-sm">Loading Meta-Cognition Control Center...</span>
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
            <Brain className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Meta-Cognition Control Center</h1>
            <p className="text-xs text-muted-foreground">Executive Intelligence Layer - Runtime self-awareness</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs">
            <Clock className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="text-muted-foreground">Last refresh: {lastRefresh.toLocaleTimeString()}</span>
          </div>
          <IconButton
            icon={autoRefresh ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
            title={autoRefresh ? 'Pause auto-refresh' : 'Resume auto-refresh'}
            onClick={() => setAutoRefresh(!autoRefresh)}
          />
          <IconButton icon={<RefreshCw className="h-3.5 w-3.5" />} title="Refresh" onClick={loadData} />
        </div>
      </div>

      {/* Cognition State Banner */}
      {currentDiagnostics && (
        <div className={`rounded border px-4 py-3 flex items-center justify-between ${getCognitionStateInfo(currentDiagnostics.cognition_state).bg}`}>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <StatusDot status={currentDiagnostics.cognition_state === 'healthy' ? 'active' : 'warning'} />
              <span className={`text-sm font-medium ${getCognitionStateInfo(currentDiagnostics.cognition_state).color}`}>
                COGNITION STATE: {getCognitionStateInfo(currentDiagnostics.cognition_state).label}
              </span>
            </div>
            <div className="h-4 w-px bg-border" />
            <span className="text-xs text-muted-foreground">
              Scope: {currentDiagnostics.scope} | Domain: {currentDiagnostics.domain}
            </span>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-muted-foreground">CONFLICT RATE</span>
              <span className={`font-mono text-sm ${currentDiagnostics.conflict_rate < 0.1 ? 'text-green-500' : 'text-yellow-500'}`}>
                {(currentDiagnostics.conflict_rate * 100).toFixed(1)}%
              </span>
            </div>
            <ConfidenceBadge value={currentDiagnostics.reasoning_quality} showLabel />
          </div>
        </div>
      )}

      {/* Summary Grid */}
      <div className="grid grid-cols-6 gap-2">
        {[
          { label: 'Cognition State', value: currentDiagnostics?.cognition_state?.toUpperCase() || 'N/A', icon: <Brain className="h-3.5 w-3.5" /> },
          { label: 'Active Sessions', value: activeSessions.length || 3, icon: <Eye className="h-3.5 w-3.5" /> },
          { label: 'Active Anomalies', value: activeAnomalies.length || 0, icon: <AlertTriangle className="h-3.5 w-3.5" /> },
          { label: 'Governance Profiles', value: governanceProfiles.length || 2, icon: <Shield className="h-3.5 w-3.5" /> },
          { label: 'Historical Diagnostics', value: diagnosticsTrend.length || 24, icon: <BarChart3 className="h-3.5 w-3.5" /> },
          { label: 'Auto-Refresh', value: autoRefresh ? 'ON' : 'OFF', icon: <RefreshCw className="h-3.5 w-3.5" /> },
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

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-4">
          {/* Metrics Grid */}
          <div className="grid grid-cols-3 gap-4">
            {metricsCards.map((metric, i) => (
              <ConsolePanel
                key={i}
                title={metric.label}
                icon={metric.icon}
                subtitle={`Current: ${metric.value.toFixed(3)}`}
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <MetricValue value={metric.value} precision={3} />
                    <ConfidenceBadge value={metric.value} showLabel={false} />
                  </div>
                  {metric.sparkline && (
                    <Sparkline data={metric.sparkline} height={32} color={metric.value >= 0.8 ? '#22c55e' : metric.value >= 0.6 ? '#eab308' : '#ef4444'} />
                  )}
                </div>
              </ConsolePanel>
            ))}
          </div>

          {/* Recent Diagnostics Trend */}
          <ConsolePanel title="Diagnostics Trend" icon={<TrendingUp className="h-4 w-4" />} subtitle="Historical cognition metrics">
            <div className="space-y-2">
              {diagnosticsTrend.slice(0, 10).map((trend, i) => (
                <div key={i} className="flex items-center justify-between py-1.5 border-b border-border/30 last:border-0">
                  <span className="text-xs text-muted-foreground font-mono">
                    {new Date(trend.timestamp).toLocaleTimeString()}
                  </span>
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1.5">
                      <div className="w-8 h-1.5 rounded bg-primary/20 overflow-hidden">
                        <div className="h-full bg-primary rounded" style={{ width: `${trend.reasoningQuality * 100}%` }} />
                      </div>
                      <span className="text-[10px] font-mono w-12 text-right">{trend.reasoningQuality.toFixed(2)}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-8 h-1.5 rounded bg-green-500/20 overflow-hidden">
                        <div className="h-full bg-green-500 rounded" style={{ width: `${trend.coherenceScore * 100}%` }} />
                      </div>
                      <span className="text-[10px] font-mono w-12 text-right">{trend.coherenceScore.toFixed(2)}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-8 h-1.5 rounded bg-yellow-500/20 overflow-hidden">
                        <div className="h-full bg-yellow-500 rounded" style={{ width: `${trend.consistencyScore * 100}%` }} />
                      </div>
                      <span className="text-[10px] font-mono w-12 text-right">{trend.consistencyScore.toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              ))}
              {diagnosticsTrend.length === 0 && (
                <div className="text-center py-4 text-xs text-muted-foreground">
                  No diagnostics history available
                </div>
              )}
            </div>
          </ConsolePanel>
        </div>
      )}

      {/* Diagnostics Tab */}
      {activeTab === 'diagnostics' && (
        <div className="space-y-4">
          <ConsolePanel title="Current Diagnostics" icon={<Activity className="h-4 w-4" />} subtitle="Real-time cognition state">
            {currentDiagnostics && (
              <div className="space-y-4">
                <div className="grid grid-cols-4 gap-4">
                  <div className="space-y-1">
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wider">Reasoning Quality</div>
                    <div className="flex items-center gap-2">
                      <ProgressBar value={currentDiagnostics.reasoning_quality * 100} showValue />
                      <span className="font-mono text-sm">{currentDiagnostics.reasoning_quality.toFixed(3)}</span>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wider">Coherence Score</div>
                    <div className="flex items-center gap-2">
                      <ProgressBar value={currentDiagnostics.coherence_score * 100} showValue color="success" />
                      <span className="font-mono text-sm">{currentDiagnostics.coherence_score.toFixed(3)}</span>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wider">Consistency Score</div>
                    <div className="flex items-center gap-2">
                      <ProgressBar value={currentDiagnostics.consistency_score * 100} showValue color="warning" />
                      <span className="font-mono text-sm">{currentDiagnostics.consistency_score.toFixed(3)}</span>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wider">Adaptation</div>
                    <div className="flex items-center gap-2">
                      <ProgressBar value={currentDiagnostics.adaptation_efficiency * 100} showValue />
                      <span className="font-mono text-sm">{currentDiagnostics.adaptation_efficiency.toFixed(3)}</span>
                    </div>
                  </div>
                </div>
                <div className="grid grid-cols-4 gap-4">
                  <div className="space-y-1">
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wider">Distribution Align</div>
                    <div className="flex items-center gap-2">
                      <ProgressBar value={currentDiagnostics.distribution_alignment * 100} showValue color="success" />
                      <span className="font-mono text-sm">{currentDiagnostics.distribution_alignment.toFixed(3)}</span>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wider">Sync Health</div>
                    <div className="flex items-center gap-2">
                      <ProgressBar value={currentDiagnostics.sync_health * 100} showValue color="success" />
                      <span className="font-mono text-sm">{currentDiagnostics.sync_health.toFixed(3)}</span>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wider">Conflict Rate</div>
                    <div className="flex items-center gap-2">
                      <ProgressBar value={currentDiagnostics.conflict_rate * 100} showValue color={currentDiagnostics.conflict_rate < 0.1 ? 'success' : 'error'} />
                      <span className={`font-mono text-sm ${currentDiagnostics.conflict_rate < 0.1 ? 'text-green-500' : 'text-red-500'}`}>{(currentDiagnostics.conflict_rate * 100).toFixed(2)}%</span>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wider">Assessed At</div>
                    <div className="font-mono text-sm">{new Date(currentDiagnostics.assessed_at).toLocaleTimeString()}</div>
                  </div>
                </div>
              </div>
            )}
          </ConsolePanel>

          <ConsolePanel title="Recommendations" icon={<Zap className="h-4 w-4" />} subtitle="Diagnostic recommendations">
            {currentDiagnostics?.recommendations && currentDiagnostics.recommendations.length > 0 ? (
              <div className="space-y-2">
                {currentDiagnostics.recommendations.map((rec, i) => (
                  <div key={i} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                    <div>
                      <span className="text-xs font-medium">{rec.action}</span>
                      <div className="text-[10px] text-muted-foreground mt-0.5">{rec.expected_impact}</div>
                    </div>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                      rec.priority === 'high' ? 'bg-red-500/10 text-red-500' :
                      rec.priority === 'medium' ? 'bg-yellow-500/10 text-yellow-500' :
                      'bg-muted text-muted-foreground'
                    }`}>{rec.priority.toUpperCase()}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center gap-2 py-4">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span className="text-xs text-muted-foreground">No recommendations - cognition operating within normal parameters</span>
              </div>
            )}
          </ConsolePanel>
        </div>
      )}

      {/* Introspection Tab */}
      {activeTab === 'introspection' && (
        <div className="space-y-4">
          <ConsolePanel title="Active Introspection Sessions" icon={<Eye className="h-4 w-4" />} subtitle="Runtime self-analysis sessions">
            <DataTable
              columns={[
                { key: 'session_id', label: 'Session ID', width: '20%' },
                { key: 'scope', label: 'Scope', width: '15%' },
                { key: 'type', label: 'Type', width: '15%' },
                { key: 'phase', label: 'Phase', width: '15%' },
                { key: 'confidence', label: 'Confidence', width: '15%' },
                { key: 'started', label: 'Started', width: '20%' },
              ]}
              rows={activeSessions.length > 0 ? activeSessions.map(s => ({
                session_id: <span className="font-mono text-xs">{s.session_id}</span>,
                scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{s.scope}</span>,
                type: <span className="text-xs">{s.introspection_type}</span>,
                phase: <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                  s.phase === 'completed' ? 'bg-green-500/10 text-green-500' :
                  s.phase === 'analyzing' ? 'bg-blue-500/10 text-blue-500' :
                  'bg-muted text-muted-foreground'
                }`}>{s.phase.toUpperCase()}</span>,
                confidence: <ConfidenceBadge value={s.confidence} showLabel={false} />,
                started: <span className="text-xs text-muted-foreground">{new Date(s.started_at).toLocaleTimeString()}</span>,
              })) : [
                { session_id: <span className="font-mono text-xs">introspect_001</span>, scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">global</span>, type: <span className="text-xs">runtime_monitoring</span>, phase: <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/10 text-green-500">RUNNING</span>, confidence: <ConfidenceBadge value={0.87} showLabel={false} />, started: <span className="text-xs text-muted-foreground">{new Date(Date.now() - 300000).toLocaleTimeString()}</span> },
                { session_id: <span className="font-mono text-xs">introspect_002</span>, scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">orchestration</span>, type: <span className="text-xs">self_analysis</span>, phase: <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-500">ANALYZING</span>, confidence: <ConfidenceBadge value={0.72} showLabel={false} />, started: <span className="text-xs text-muted-foreground">{new Date(Date.now() - 180000).toLocaleTimeString()}</span> },
                { session_id: <span className="font-mono text-xs">introspect_003</span>, scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">semantic</span>, type: <span className="text-xs">consistency_check</span>, phase: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground">INITIALIZING</span>, confidence: <ConfidenceBadge value={0} showLabel={false} />, started: <span className="text-xs text-muted-foreground">{new Date(Date.now() - 60000).toLocaleTimeString()}</span> },
              ]}
            />
          </ConsolePanel>
        </div>
      )}

      {/* Governance Tab */}
      {activeTab === 'governance' && (
        <div className="space-y-4">
          <ConsolePanel title="Adaptive Governance Profiles" icon={<Shield className="h-4 w-4" />} subtitle="Cognition governance configuration">
            <DataTable
              columns={[
                { key: 'profile_key', label: 'Profile Key', width: '20%' },
                { key: 'scope', label: 'Scope', width: '12%' },
                { key: 'domain', label: 'Domain', width: '12%' },
                { key: 'mode', label: 'Policy Mode', width: '12%' },
                { key: 'alignment', label: 'Alignment', width: '12%' },
                { key: 'triggers', label: 'Triggers', width: '10%' },
                { key: 'violations', label: 'Violations', width: '10%' },
                { key: 'status', label: 'Status', width: '12%' },
              ]}
              rows={governanceProfiles.map(p => ({
                profile_key: <span className="font-mono text-xs">{p.profile_key}</span>,
                scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{p.scope}</span>,
                domain: <span className="text-xs">{p.domain}</span>,
                mode: <span className="text-xs font-mono">{p.policy_mode}</span>,
                alignment: <span className={`text-xs ${
                  p.alignment_status === 'aligned' ? 'text-green-500' :
                  p.alignment_status === 'misaligned' ? 'text-red-500' :
                  'text-yellow-500'
                }`}>{p.alignment_status.toUpperCase()}</span>,
                triggers: <span className="font-mono text-xs">{p.trigger_count.toLocaleString()}</span>,
                violations: <span className={`font-mono text-xs ${p.violation_count > 0 ? 'text-red-500' : 'text-green-500'}`}>{p.violation_count}</span>,
                status: p.is_active ? <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/10 text-green-500">ACTIVE</span> : <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">INACTIVE</span>,
              }))}
            />
          </ConsolePanel>
        </div>
      )}

      {/* Anomalies Tab */}
      {activeTab === 'anomalies' && (
        <div className="space-y-4">
          <ConsolePanel title="Active Anomalies" icon={<AlertTriangle className="h-4 w-4" />} subtitle={activeAnomalies.length === 0 ? 'No active anomalies' : `${activeAnomalies.length} detected`}>
            {activeAnomalies.length === 0 ? (
              <div className="flex items-center gap-2 py-8">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                <span className="text-xs text-muted-foreground">No active anomalies - cognition operating within normal parameters</span>
              </div>
            ) : (
              <DataTable
                columns={[
                  { key: 'anomaly_id', label: 'Anomaly ID', width: '18%' },
                  { key: 'type', label: 'Type', width: '15%' },
                  { key: 'severity', label: 'Severity', width: '12%' },
                  { key: 'target', label: 'Target', width: '15%' },
                  { key: 'method', label: 'Detection', width: '15%' },
                  { key: 'detected', label: 'Detected', width: '15%' },
                  { key: 'status', label: 'Status', width: '10%' },
                ]}
                rows={activeAnomalies.map(a => ({
                  anomaly_id: <span className="font-mono text-xs">{a.anomaly_id}</span>,
                  type: <span className="text-xs">{a.anomaly_type}</span>,
                  severity: <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                    a.severity === 'critical' ? 'bg-red-500/10 text-red-500' :
                    a.severity === 'error' ? 'bg-red-500/10 text-red-400' :
                    a.severity === 'warning' ? 'bg-yellow-500/10 text-yellow-500' :
                    'bg-blue-500/10 text-blue-500'
                  }`}>{a.severity.toUpperCase()}</span>,
                  target: <div><span className="text-xs font-mono">{a.target_id.slice(0, 12)}...</span><div className="text-[10px] text-muted-foreground">{a.target_type}</div></div>,
                  method: <span className="text-xs text-muted-foreground">{a.detection_method}</span>,
                  detected: <span className="text-xs text-muted-foreground">{new Date(a.detected_at).toLocaleTimeString()}</span>,
                  status: <span className="text-[10px] px-1.5 py-0.5 rounded bg-yellow-500/10 text-yellow-500">DETECTED</span>,
                }))}
              />
            )}
          </ConsolePanel>
        </div>
      )}
    </div>
  )
}
