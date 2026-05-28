/**
 * Runtime Self-Awareness Workspace
 * Orchestration behavior analysis and introspection monitoring.
 */
'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  Eye,
  Activity,
  Brain,
  GitBranch,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Clock,
  RefreshCw,
  Play,
  Pause,
  Settings,
  Network,
  Target,
} from 'lucide-react'
import {
  useMetaCognitionApi,
  type IntrospectionSession,
  type RuntimeSelfAwarenessMetrics,
} from '@/lib/meta-cognition-api'
import { ConsolePanel, DataTable, StatusDot, ConfidenceBadge, IconButton, ProgressBar, MetricGrid, MetricValue, TabBar, Sparkline } from '@/components/cognitive/primitives'

// ==================== Types ====================

interface SelfAwarenessData {
  introspectionDepth: number
  reflectionAccuracy: number
  selfModelAccuracy: number
  insightRelevance: number
  findingAccuracy: number
  overhead: number
  latencyMs: number
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

export default function RuntimeSelfAwarenessWorkspace() {
  const api = useMetaCognitionApi()
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  // State data
  const [introspectionSessions, setIntrospectionSessions] = useState<IntrospectionSession[]>([])
  const [metrics, setMetrics] = useState<SelfAwarenessData | null>(null)
  const [sparklines, setSparklines] = useState<Record<string, number[]>>({})

  // Load data
  const loadData = useCallback(async () => {
    try {
      // Load introspection sessions
      try {
        // Would fetch from API with scope filter
        setIntrospectionSessions([])
      } catch {
        setIntrospectionSessions([])
      }

      // Set mock metrics
      const mockMetrics: SelfAwarenessData = {
        introspectionDepth: 0.82 + Math.random() * 0.1,
        reflectionAccuracy: 0.88 + Math.random() * 0.08,
        selfModelAccuracy: 0.85 + Math.random() * 0.1,
        insightRelevance: 0.79 + Math.random() * 0.12,
        findingAccuracy: 0.91 + Math.random() * 0.05,
        overhead: 0.03 + Math.random() * 0.02,
        latencyMs: 45 + Math.random() * 30,
      }
      setMetrics(mockMetrics)

      // Generate sparklines
      setSparklines({
        depth: generateSparkline(mockMetrics.introspectionDepth),
        accuracy: generateSparkline(mockMetrics.reflectionAccuracy),
        selfModel: generateSparkline(mockMetrics.selfModelAccuracy),
        relevance: generateSparkline(mockMetrics.insightRelevance),
        finding: generateSparkline(mockMetrics.findingAccuracy),
      })

      setLastRefresh(new Date())
    } catch {
      // Use defaults
      setMetrics({
        introspectionDepth: 0.82,
        reflectionAccuracy: 0.88,
        selfModelAccuracy: 0.85,
        insightRelevance: 0.79,
        findingAccuracy: 0.91,
        overhead: 0.03,
        latencyMs: 45,
      })
    }
    setLoading(false)
  }, [api])

  // Initial load and auto-refresh
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
    { id: 'overview', label: 'Overview', icon: <Eye className="h-3 w-3" /> },
    { id: 'sessions', label: 'Sessions', icon: <Brain className="h-3 w-3" /> },
    { id: 'metrics', label: 'Metrics', icon: <Activity className="h-3 w-3" /> },
  ]

  // Mock sessions
  const mockSessions: IntrospectionSession[] = [
    {
      session_id: 'introspect_001',
      scope: 'global',
      phase: 'analyzing',
      introspection_type: 'runtime_monitoring',
      focus_areas: ['reasoning_quality', 'coherence'],
      confidence: 0.87,
      depth_achieved: 5,
      breadth_achieved: 12,
      is_active: true,
      started_at: new Date(Date.now() - 300000).toISOString(),
    },
    {
      session_id: 'introspect_002',
      scope: 'orchestration',
      phase: 'synthesizing',
      introspection_type: 'self_analysis',
      focus_areas: ['decision_patterns', 'execution_flow'],
      confidence: 0.72,
      depth_achieved: 3,
      breadth_achieved: 8,
      is_active: true,
      started_at: new Date(Date.now() - 180000).toISOString(),
    },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex items-center gap-2 text-muted-foreground">
          <RefreshCw className="h-4 w-4 animate-spin" />
          <span className="text-sm">Loading Runtime Self-Awareness...</span>
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
            <Eye className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Runtime Self-Awareness</h1>
            <p className="text-xs text-muted-foreground">Orchestration introspection and behavior analysis</p>
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
          { label: 'Active Sessions', value: mockSessions.filter(s => s.is_active).length, icon: <Brain className="h-3.5 w-3.5" /> },
          { label: 'Introspection Depth', value: `${((metrics?.introspectionDepth || 0) * 100).toFixed(0)}%`, icon: <Target className="h-3.5 w-3.5" /> },
          { label: 'Reflection Accuracy', value: `${((metrics?.reflectionAccuracy || 0) * 100).toFixed(0)}%`, icon: <Activity className="h-3.5 w-3.5" /> },
          { label: 'Self-Model Accuracy', value: `${((metrics?.selfModelAccuracy || 0) * 100).toFixed(0)}%`, icon: <Network className="h-3.5 w-3.5" /> },
          { label: 'Processing Overhead', value: `${((metrics?.overhead || 0) * 100).toFixed(1)}%`, icon: <TrendingUp className="h-3.5 w-3.5" /> },
          { label: 'Avg Latency', value: `${(metrics?.latencyMs || 0).toFixed(0)}ms`, icon: <Clock className="h-3.5 w-3.5" /> },
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
          {/* Self-Awareness Metrics */}
          <div className="grid grid-cols-3 gap-4">
            {metrics && [
              { label: 'Introspection Depth', value: metrics.introspectionDepth, icon: <Target className="h-4 w-4" />, sparkline: sparklines.depth },
              { label: 'Reflection Accuracy', value: metrics.reflectionAccuracy, icon: <Activity className="h-4 w-4" />, sparkline: sparklines.accuracy },
              { label: 'Self-Model Accuracy', value: metrics.selfModelAccuracy, icon: <Network className="h-4 w-4" />, sparkline: sparklines.selfModel },
            ].map((metric, i) => (
              <ConsolePanel key={i} title={metric.label} icon={metric.icon} subtitle={`Current: ${(metric.value * 100).toFixed(1)}%`}>
                <div className="space-y-3">
                  <ProgressBar value={metric.value * 100} showValue />
                  {metric.sparkline && (
                    <Sparkline data={metric.sparkline} height={24} color="#22c55e" />
                  )}
                </div>
              </ConsolePanel>
            ))}
          </div>

          {/* Additional Metrics */}
          <div className="grid grid-cols-2 gap-4">
            {metrics && [
              { label: 'Insight Relevance', value: metrics.insightRelevance, icon: <TrendingUp className="h-4 w-4" /> },
              { label: 'Finding Accuracy', value: metrics.findingAccuracy, icon: <CheckCircle2 className="h-4 w-4" /> },
            ].map((metric, i) => (
              <ConsolePanel key={i} title={metric.label} icon={metric.icon} subtitle={`${(metric.value * 100).toFixed(1)}%`}>
                <ProgressBar value={metric.value * 100} showValue color={metric.value > 0.8 ? 'success' : 'warning'} />
              </ConsolePanel>
            ))}
          </div>
        </div>
      )}

      {/* Sessions Tab */}
      {activeTab === 'sessions' && (
        <ConsolePanel title="Introspection Sessions" icon={<Brain className="h-4 w-4" />} subtitle="Active runtime self-analysis">
          <DataTable
            columns={[
              { key: 'session_id', label: 'Session ID', width: '18%' },
              { key: 'scope', label: 'Scope', width: '12%' },
              { key: 'type', label: 'Type', width: '15%' },
              { key: 'phase', label: 'Phase', width: '12%' },
              { key: 'confidence', label: 'Confidence', width: '12%' },
              { key: 'depth', label: 'Depth', width: '10%' },
              { key: 'breadth', label: 'Breadth', width: '10%' },
              { key: 'status', label: 'Status', width: '11%' },
            ]}
            rows={mockSessions.map(s => ({
              session_id: <span className="font-mono text-xs">{s.session_id}</span>,
              scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{s.scope}</span>,
              type: <span className="text-xs">{s.introspection_type}</span>,
              phase: <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                s.phase === 'completed' ? 'bg-green-500/10 text-green-500' :
                s.phase === 'analyzing' || s.phase === 'synthesizing' ? 'bg-blue-500/10 text-blue-500' :
                'bg-muted text-muted-foreground'
              }`}>{s.phase.toUpperCase()}</span>,
              confidence: <ConfidenceBadge value={s.confidence} showLabel={false} />,
              depth: <span className="font-mono text-xs">{s.depth_achieved}</span>,
              breadth: <span className="font-mono text-xs">{s.breadth_achieved}</span>,
              status: s.is_active ? <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/10 text-green-500">ACTIVE</span> : <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">INACTIVE</span>,
            }))}
          />
        </ConsolePanel>
      )}

      {/* Metrics Tab */}
      {activeTab === 'metrics' && (
        <div className="grid gap-4 lg:grid-cols-2">
          <ConsolePanel title="Introspection Performance" icon={<Activity className="h-4 w-4" />} subtitle="Processing efficiency">
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b border-border/50">
                <span className="text-xs">Processing Overhead</span>
                <span className="font-mono text-sm">{((metrics?.overhead || 0) * 100).toFixed(2)}%</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-border/50">
                <span className="text-xs">Avg Latency</span>
                <span className="font-mono text-sm">{(metrics?.latencyMs || 0).toFixed(0)}ms</span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-xs">Session Count</span>
                <span className="font-mono text-sm">{mockSessions.length}</span>
              </div>
            </div>
          </ConsolePanel>

          <ConsolePanel title="Quality Metrics" icon={<TrendingUp className="h-4 w-4" />} subtitle="Self-awareness quality indicators">
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b border-border/50">
                <span className="text-xs">Insight Relevance</span>
                <span className="font-mono text-sm text-green-500">{((metrics?.insightRelevance || 0) * 100).toFixed(1)}%</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-border/50">
                <span className="text-xs">Finding Accuracy</span>
                <span className="font-mono text-sm text-green-500">{((metrics?.findingAccuracy || 0) * 100).toFixed(1)}%</span>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-xs">Self-Model Match</span>
                <span className="font-mono text-sm">{((metrics?.selfModelAccuracy || 0) * 100).toFixed(1)}%</span>
              </div>
            </div>
          </ConsolePanel>
        </div>
      )}
    </div>
  )
}
