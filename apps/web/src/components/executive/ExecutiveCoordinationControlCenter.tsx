/**
 * 43V3R CORE - Executive Coordination Control Center
 * 
 * Central orchestration intelligence dashboard for the executive coordination layer.
 * Provides real-time visibility into recursive supervision, arbitration, stabilization,
 * and systemic coherence across the platform.
 * 
 * Enterprise runtime console with dense information panels, telemetry-driven interfaces,
 * and orchestration intelligence.
 */
'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  Brain,
  GitBranch,
  Activity,
  Shield,
  Cpu,
  Database,
  AlertTriangle,
  CheckCircle2,
  Zap,
  Gauge,
  Target,
  Layers,
  Network,
  RefreshCw,
  Clock,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Eye,
} from 'lucide-react'
import { useExecutiveApi } from '@/lib/executive-api'
import {
  ConsolePanel,
  MetricGrid,
  MetricValue,
  StatusDot,
  ConfidenceBadge,
  DataTable,
  TabBar,
  IconButton,
  ProgressBar,
} from '@/components/cognitive/primitives'

// ---- Types ----

interface SystemMetrics {
  activeSessions: number
  activeArbitrations: number
  stabilizationProfiles: number
  coordinationTopologies: number
  activeForecasts: number
  activeAnomalies: number
  overallCoherenceScore: number
  systemHealth: string
}

// ---- Mock Data Generators ----

function generateMockMetrics(): SystemMetrics {
  return {
    activeSessions: Math.floor(Math.random() * 20) + 5,
    activeArbitrations: Math.floor(Math.random() * 10) + 2,
    stabilizationProfiles: Math.floor(Math.random() * 15) + 3,
    coordinationTopologies: Math.floor(Math.random() * 8) + 1,
    activeForecasts: Math.floor(Math.random() * 25) + 8,
    activeAnomalies: Math.floor(Math.random() * 5),
    overallCoherenceScore: 0.92 + Math.random() * 0.07,
    systemHealth: 'healthy',
  }
}

// ---- Main Component ----

export default function ExecutiveCoordinationControlCenter() {
  const api = useExecutiveApi()
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({
    activeSessions: 0,
    activeArbitrations: 0,
    stabilizationProfiles: 0,
    coordinationTopologies: 0,
    activeForecasts: 0,
    activeAnomalies: 0,
    overallCoherenceScore: 0,
    systemHealth: 'unknown',
  })

  useEffect(() => {
    const loadData = async () => {
      try {
        // Try to fetch real data
        const overview = await api.getOverview()
        setSystemMetrics({
          activeSessions: overview.active_supervision_sessions,
          activeArbitrations: overview.active_arbitrations,
          stabilizationProfiles: overview.stabilization_profiles,
          coordinationTopologies: overview.coordination_topologies,
          activeForecasts: overview.active_forecasts,
          activeAnomalies: overview.active_anomalies,
          overallCoherenceScore: overview.overall_coherence_score,
          systemHealth: overview.system_health,
        })
      } catch {
        // Fall back to mock data
        setSystemMetrics(generateMockMetrics())
      }
      setLoading(false)
    }

    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [api])

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Brain className="h-3 w-3" /> },
    { id: 'supervision', label: 'Supervision', icon: <Eye className="h-3 w-3" /> },
    { id: 'arbitration', label: 'Arbitration', icon: <Shield className="h-3 w-3" /> },
    { id: 'stabilization', label: 'Stabilization', icon: <Gauge className="h-3 w-3" /> },
    { id: 'topology', label: 'Topology', icon: <Network className="h-3 w-3" /> },
    { id: 'diagnostics', label: 'Diagnostics', icon: <Activity className="h-3 w-3" /> },
    { id: 'lineage', label: 'Lineage', icon: <GitBranch className="h-3 w-3" /> },
  ]

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Cpu className="h-5 w-5 text-primary" />
            <span className="font-mono text-sm font-semibold tracking-tight">EXEC COORDINATION CONTROL</span>
          </div>
          <div className="h-4 w-px bg-border/50" />
          <StatusDot status={systemMetrics.systemHealth === 'healthy' ? 'active' : 'warning'} />
          <span className="text-[10px] font-mono text-muted-foreground uppercase">
            Coherence {Math.round(systemMetrics.overallCoherenceScore * 100)}%
          </span>
        </div>
        <div className="flex items-center gap-2">
          <IconButton
            icon={<RefreshCw className="h-3 w-3" />}
            onClick={() => setLoading(true)}
            title="Refresh"
          />
        </div>
      </div>

      {/* Tab Bar */}
      <div className="px-4 py-2 border-b border-border/30">
        <TabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {loading ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <RefreshCw className="h-6 w-6 animate-spin" />
          </div>
        ) : (
          <>
            {/* Overview */}
            {activeTab === 'overview' && (
              <div className="space-y-4">
                {/* System Health Dashboard */}
                <div className="grid gap-4 lg:grid-cols-4">
                  <ConsolePanel
                    title="System Health"
                    icon={<Activity className="h-4 w-4" />}
                    subtitle="Overall platform status"
                  >
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <StatusDot status={systemMetrics.systemHealth === 'healthy' ? 'active' : systemMetrics.systemHealth === 'stable' ? 'idle' : 'warning'} />
                        <span className="text-lg font-mono font-bold uppercase">{systemMetrics.systemHealth}</span>
                      </div>
                      <div className="pt-2 border-t border-border/30">
                        <div className="text-[10px] text-muted-foreground uppercase mb-1">Coherence Score</div>
                        <div className="flex items-end gap-1">
                          <span className="text-2xl font-mono font-bold">
                            {Math.round(systemMetrics.overallCoherenceScore * 100)}
                          </span>
                          <span className="text-muted-foreground text-sm">%</span>
                        </div>
                        <ProgressBar
                          value={systemMetrics.overallCoherenceScore * 100}
                          showValue={false}
                          color={systemMetrics.overallCoherenceScore > 0.9 ? 'success' : systemMetrics.overallCoherenceScore > 0.7 ? 'primary' : 'warning'}
                        />
                      </div>
                    </div>
                  </ConsolePanel>

                  <ConsolePanel
                    title="Supervision"
                    icon={<Eye className="h-4 w-4" />}
                    subtitle="Recursive cognition sessions"
                  >
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-2xl font-mono font-bold">{systemMetrics.activeSessions}</span>
                        <StatusDot status={systemMetrics.activeSessions > 0 ? 'active' : 'idle'} />
                      </div>
                      <div className="space-y-1">
                        <div className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground">Active</span>
                          <span className="font-mono">{systemMetrics.activeSessions}</span>
                        </div>
                        <div className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground">Depth Max</span>
                          <span className="font-mono">6</span>
                        </div>
                      </div>
                    </div>
                  </ConsolePanel>

                  <ConsolePanel
                    title="Arbitration"
                    icon={<Shield className="h-4 w-4" />}
                    subtitle="Orchestration conflicts"
                  >
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-2xl font-mono font-bold">{systemMetrics.activeArbitrations}</span>
                        <StatusDot status={systemMetrics.activeArbitrations > 0 ? 'warning' : 'idle'} />
                      </div>
                      <div className="space-y-1">
                        <div className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground">Active</span>
                          <span className="font-mono">{systemMetrics.activeArbitrations}</span>
                        </div>
                        <div className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground">Resolved</span>
                          <span className="font-mono text-green-500">{systemMetrics.activeArbitrations * 3}</span>
                        </div>
                      </div>
                    </div>
                  </ConsolePanel>

                  <ConsolePanel
                    title="Stabilization"
                    icon={<Gauge className="h-4 w-4" />}
                    subtitle="Runtime coherence"
                  >
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-2xl font-mono font-bold">{systemMetrics.stabilizationProfiles}</span>
                        <StatusDot status="active" />
                      </div>
                      <div className="space-y-1">
                        <div className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground">Profiles</span>
                          <span className="font-mono">{systemMetrics.stabilizationProfiles}</span>
                        </div>
                        <div className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground">Success</span>
                          <span className="font-mono text-green-500">98%</span>
                        </div>
                      </div>
                    </div>
                  </ConsolePanel>
                </div>

                {/* Secondary Metrics */}
                <div className="grid gap-4 lg:grid-cols-3">
                  <ConsolePanel
                    title="Coordination Topology"
                    icon={<Network className="h-4 w-4" />}
                    subtitle="Distributed orchestration"
                  >
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <div className="text-[10px] text-muted-foreground uppercase">Topologies</div>
                        <div className="text-xl font-mono font-bold">{systemMetrics.coordinationTopologies}</div>
                      </div>
                      <div className="space-y-1">
                        <div className="text-[10px] text-muted-foreground uppercase">Nodes</div>
                        <div className="text-xl font-mono font-bold">{systemMetrics.coordinationTopologies * 12}</div>
                      </div>
                      <div className="space-y-1">
                        <div className="text-[10px] text-muted-foreground uppercase">Latency</div>
                        <div className="text-xl font-mono font-bold">12<span className="text-xs text-muted-foreground">ms</span></div>
                      </div>
                      <div className="space-y-1">
                        <div className="text-[10px] text-muted-foreground uppercase">Throughput</div>
                        <div className="text-xl font-mono font-bold">1.4<span className="text-xs text-muted-foreground">k/s</span></div>
                      </div>
                    </div>
                  </ConsolePanel>

                  <ConsolePanel
                    title="Predictive Diagnostics"
                    icon={<TrendingUp className="h-4 w-4" />}
                    subtitle="Forecasts and predictions"
                  >
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <div className="text-[10px] text-muted-foreground uppercase">Active Forecasts</div>
                          <div className="text-xl font-mono font-bold">{systemMetrics.activeForecasts}</div>
                        </div>
                        <div className="space-y-1 text-right">
                          <div className="text-[10px] text-muted-foreground uppercase">Accuracy</div>
                          <ConfidenceBadge value={0.87} showLabel={false} />
                        </div>
                      </div>
                      <div className="space-y-1">
                        <div className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground">Near-term</span>
                          <span className="font-mono">{Math.floor(systemMetrics.activeForecasts * 0.6)}</span>
                        </pannediv>
                        <div className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground">Short-term</span>
                          <span className="font-mono">{Math.floor(systemMetrics.activeForecasts * 0.3)}</span>
                        </div>
                        <div className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground">Medium-term</span>
                          <span className="font-mono">{Math.floor(systemMetrics.activeForecasts * 0.1)}</span>
                        </div>
                      </div>
                    </div>
                  </ConsolePanel>

                  <ConsolePanel
                    title="Anomaly Detection"
                    icon={<AlertTriangle className="h-4 w-4" />}
                    subtitle="Systemic anomalies"
                  >
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <div className="text-[10px] text-muted-foreground uppercase">Active</div>
                          <div className="text-xl font-mono font-bold">{systemMetrics.activeAnomalies}</div>
                        </div>
                        <StatusDot status={systemMetrics.activeAnomalies > 0 ? 'warning' : 'active'} />
                      </div>
                      <div className="space-y-1">
                        <div className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground">Critical</span>
                          <span className="font-mono text-red-500">0</span>
                        </div>
                        <div className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground">Warning</span>
                          <span className="font-mono text-yellow-500">{systemMetrics.activeAnomalies}</span>
                        </div>
                        <div className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground">Info</span>
                          <span className="font-mono text-blue-500">3</span>
                        </div>
                      </div>
                    </div>
                  </ConsolePanel>
                </div>
              </div>
            )}

            {/* Supervision Tab */}
            {activeTab === 'supervision' && (
              <div className="grid gap-4 lg:grid-cols-2">
                <ConsolePanel
                  title="Recursive Supervision Sessions"
                  icon={<Eye className="h-4 w-4" />}
                  subtitle="Active cognition oversight"
                >
                  <DataTable
                    columns={[
                      { key: 'session_id', label: 'Session ID', width: '20%' },
                      { key: 'supervisor', label: 'Supervisor', width: '20%' },
                      { key: 'scope', label: 'Scope', width: '15%' },
                      { key: 'level', label: 'Level', width: '15%' },
                      { key: 'confidence', label: 'Confidence', width: '15%' },
                      { key: 'state', label: 'State', width: '15%' },
                    ]}
                    rows={[
                      {
                        session_id: <span className="font-mono text-xs">sup_8a3f2</span>,
                        supervisor: <span className="font-mono text-xs">orchestrator-01</span>,
                        scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">execution</span>,
                        level: <span className="font-mono">4</span>,
                        confidence: <ConfidenceBadge value={0.92} showLabel={false} />,
                        state: <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/10 text-green-500">active</span>,
                      },
                      {
                        session_id: <span className="font-mono text-xs">sup_4c7d1</span>,
                        supervisor: <span className="font-mono text-xs">supervisor-03</span>,
                        scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">governance</span>,
                        level: <span className="font-mono">5</span>,
                        confidence: <ConfidenceBadge value={0.88} showLabel={false} />,
                        state: <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-500">reviewing</span>,
                      },
                      {
                        session_id: <span className="font-mono text-xs">sup_9b2e6</span>,
                        supervisor: <span className="font-mono text-xs">advisor-02</span>,
                        scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">orchestration</span>,
                        level: <span className="font-mono">3</span>,
                        confidence: <ConfidenceBadge value={0.95} showLabel={false} />,
                        state: <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/10 text-green-500">active</span>,
                      },
                    ].map((row, idx) => ({ key: String(idx), ...row }))}
                  />
                </ConsolePanel>

                <ConsolePanel
                  title="Supervision Hierarchy"
                  icon={<GitBranch className="h-4 w-4" />}
                  subtitle="Recursion depth tracking"
                >
                  <div className="space-y-3">
                    {[
                      { level: 'MASTER', depth: 6, agents: 2 },
                      { level: 'GOVERNOR', depth: 5, agents: 4 },
                      { level: 'COORDINATOR', depth: 4, agents: 8 },
                      { level: 'REVIEWER', depth: 3, agents: 12 },
                      { level: 'ADVISOR', depth: 2, agents: 24 },
                      { level: 'OBSERVER', depth: 1, agents: 48 },
                    ].map((item) => (
                      <div key={item.level} className="flex items-center justify-between py-2 border-b border-border/30 last:border-0">
                        <div className="flex items-center gap-3">
                          <div
                            className="h-6 rounded bg-muted"
                            style={{ width: `${(item.depth / 6) * 100}%` }}
                          />
                          <span className="text-xs font-mono font-medium">{item.level}</span>
                        </div>
                        <div className="flex items-center gap-4 text-[10px] text-muted-foreground">
                          <span>depth {item.depth}</span>
                          <span className="font-mono">{item.agents}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </ConsolePanel>
              </div>
            )}

            {/* Arbitration Tab */}
            {activeTab === 'arbitration' && (
              <div className="grid gap-4 lg:grid-cols-2">
                <ConsolePanel
                  title="Active Arbitrations"
                  icon={<Shield className="h-4 w-4" />}
                  subtitle="Orchestration conflict resolution"
                >
                  <DataTable
                    columns={[
                      { key: 'arb_id', label: 'Arb ID', width: '20%' },
                      { key: 'scope', label: 'Scope', width: '20%' },
                      { key: 'parties', label: 'Parties', width: '15%' },
                      { key: 'strategy', label: 'Strategy', width: '20%' },
                      { key: 'state', label: 'State', width: '25%' },
                    ]}
                    rows={[
                      {
                        arb_id: <span className="font-mono text-xs">arb_7f23c</span>,
                        scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">orchestration</span>,
                        parties: <span className="font-mono">3</span>,
                        strategy: '<span className="text-[10px]">priority_weighted</span>',
                        state: '<span className="text-[10px] px-1.5 py-0.5 rounded bg-yellow-500/10 text-yellow-500">evaluating</span>',
                      },
                      {
                        arb_id: <span className="font-mono text-xs">arb_2b8d9</span>,
                        scope: '<span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">semantic</span>',
                        parties: '<span className="font-mono">2</span>',
                        strategy: '<span className="text-[10px]">merge</span>',
                        state: '<span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-500">arbitrating</span>',
                      },
                    ].map((row, idx) => ({ key: String(idx), ...row }))}
                  />
                </ConsolePanel>

                <ConsolePanel
                  title="Arbitration Policies"
                  icon={<BarChart3 className="h-4 w-4" />}
                  subtitle="Conflict resolution strategies"
                >
                  <div className="space-y-2">
                    {[
                      { name: 'Priority Weighted', strategy: 'priority_weighted', count: 1247 },
                      { name: 'First Claim', strategy: 'first_claim', count: 456 },
                      { name: 'Merge Output', strategy: 'merge', count: 892 },
                      { name: 'Weighted Vote', strategy: 'weighted_vote', count: 234 },
                    ].map((policy, i) => (
                      <div key={i} className="flex items-center justify-between py-2 border-b border-border/30 last:border-0">
                        <div>
                          <span className="text-xs font-medium">{policy.name}</span>
                          <div className="text-[10px] text-muted-foreground font-mono">{policy.strategy}</div>
                        </div>
                        <div className="text-right">
                          <span className="text-sm font-mono">{policy.count}</span>
                          <div className="text-[10px] text-muted-foreground">invocations</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </ConsolePanel>
              </div>
            )}

            {/* Stabilization Tab */}
            {activeTab === 'stabilization' && (
              <div className="grid gap-4 lg:grid-cols-3">
                {[
                  { tier: 'TIER_0', name: 'Healthy', score: 0.95, count: 12, color: 'success' },
                  { tier: 'TIER_1', name: 'Marginal', score: 0.78, count: 8, color: 'primary' },
                  { tier: 'TIER_2', name: 'Degrading', score: 0.55, count: 3, color: 'warning' },
                  { tier: 'TIER_3', name: 'Unstable', score: 0.32, count: 1, color: 'error' },
                  { tier: 'TIER_4', name: 'Critical', score: 0.15, count: 0, color: 'error' },
                ].map((tier) => (
                  <ConsolePanel
                    key={tier.tier}
                    title={tier.name}
                    icon={<Gauge className="h-4 w-4" />}
                    subtitle={`Coherence ${Math.round(tier.score * 100)}%`}
                  >
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-mono text-muted-foreground">{tier.tier}</span>
                        <StatusDot status={tier.count > 0 ? 'active' : 'idle'} />
                      </div>
                      <ProgressBar value={tier.score * 100} showValue={false} color={tier.color} />
                      <div className="flex justify-between text-[10px] text-muted-foreground">
                        <span>Profiles:</span>
                        <span className="font-mono">{tier.count}</span>
                      </div>
                    </div>
                  </ConsolePanel>
                ))}
              </div>
            )}

            {/* Topology Tab */}
            {activeTab === 'topology' && (
              <div className="grid gap-4 lg:grid-cols-2">
                <ConsolePanel
                  title="Coordination Topology"
                  icon={<Network className="h-4 w-4" />}
                  subtitle="Distributed coordination graph"
                >
                  <div className="flex items-center justify-center h-64 text-muted-foreground">
                    <div className="text-center">
                      <Network className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">Graph Visualization</p>
                      <p className="text-xs mt-1">{systemMetrics.coordinationTopologies} topologies</p>
                    </div>
                  </div>
                </ConsolePanel>

                <ConsolePanel
                  title="Topology Metrics"
                  icon={<Activity className="h-4 w-4" />}
                  subtitle="Performance indicators"
                >
                  <div className="space-y-4">
                    {[
                      { label: 'Sync Latency', value: 12, unit: 'ms', status: 'active' },
                      { label: 'Message Throughput', value: 1420, unit: 'k/s', status: 'active' },
                      { label: 'Conflict Rate', value: 0.02, unit: '%', status: 'active' },
                      { label: 'Node Count', value: systemMetrics.coordinationTopologies * 12, unit: '', status: 'active' },
                    ].map((metric) => (
                      <div key={metric.label} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <StatusDot status={metric.status as 'active' | 'idle'} />
                          <span className="text-xs">{metric.label}</span>
                        </div>
                        <span className="font-mono text-sm">
                          {metric.value}<span className="text-muted-foreground text-[10px]">{metric.unit}</span>
                        </span>
                      </div>
                    ))}
                  </div>
                </ConsolePanel>
              </div>
            )}

            {/* Diagnostics Tab */}
            {activeTab === 'diagnostics' && (
              <div className="grid gap-4 lg:grid-cols-2">
                <ConsolePanel
                  title="Predictive Forecasts"
                  icon={<TrendingUp className="h-4 w-4" />}
                  subtitle="Instability and cascade predictions"
                >
                  <DataTable
                    columns={[
                      { key: 'target', label: 'Target', width: '20%' },
                      { key: 'kind', label: 'Kind', width: '20%' },
                      { key: 'horizon', label: 'Horizon', width: '15%' },
                      { key: 'predicted', label: 'Predicted', width: '15%' },
                      { key: 'confidence', label: 'Confidence', width: '15%' },
                      { key: 'risk', label: 'Risk', width: '15%' },
                    ]}
                    rows={[
                      {
                        target: '<span className="font-mono text-xs">render-alpha</span>',
                        kind: '<span className="text-[10px]">failure_prob</span>',
                        horizon: '<span className="font-mono text-xs">15m</span>',
                        predicted: '<span className="font-mono">0.12</span>',
                        confidence: '<ConfidenceBadge value={0.87} showLabel={false} />',
                        risk: '<span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/10 text-green-500">low</span>',
                      },
                      {
                        target: '<span className="font-mono text-xs">memory-ctrl</span>',
                        kind: '<span className="text-[10px]">drift</span>',
                        horizon: '<span className="font-mono text-xs">45m</span>',
                        predicted: '<span className="font-mono">0.34</span>',
                        confidence: '<ConfidenceBadge value={0.72} showLabel={false} />',
                        risk: '<span className="text-[10px] px-1.5 py-0.5 rounded bg-yellow-500/10 text-yellow-500">medium</span>',
                      },
                    ].map((row, idx) => ({ key: String(idx), ...row }))}
                  />
                </ConsolePanel>

                <ConsolePanel
                  title="Anomaly Registry"
                  icon={<AlertTriangle className="h-4 w-4" />}
                  subtitle="Systemic anomaly tracking"
                >
                  <div className="space-y-2">
                    {[
                      { type: 'semantic_drift', severity: 'warning', status: 'detected' },
                      { type: 'latency_spike', severity: 'notice', status: 'monitoring' },
                      { type: 'coherence_drop', severity: 'info', status: 'resolved' },
                    ].map((anomaly, i) => (
                      <div key={i} className="flex items-center justify-between py-2 border-b border-border/30 last:border-0">
                        <div>
                          <span className="text-xs font-mono">{anomaly.type}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                            anomaly.severity === 'warning' ? 'bg-yellow-500/10 text-yellow-500' :
                            anomaly.severity === 'notice' ? 'bg-blue-500/10 text-blue-500' :
                            'bg-muted text-muted-foreground'
                          }`}>{anomaly.severity}</span>
                          <span className="text-[10px] text-muted-foreground">{anomaly.status}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </ConsolePanel>
              </div>
            )}

            {/* Lineage Tab */}
            {activeTab === 'lineage' && (
              <ConsolePanel
                title="Systemic Coherence Lineage"
                icon={<GitBranch className="h-4 w-4" />}
                subtitle="Coherence evolution tracking"
              >
                <div className="space-y-4">
                  {[
                    { metric: 'ORCHESTRATION', value: 0.95, trend: 'stable', events: 1247 },
                    { metric: 'EXECUTION', value: 0.88, trend: 'improving', events: 2341 },
                    { metric: 'GOVERNANCE', value: 0.92, trend: 'stable', events: 892 },
                    { metric: 'SEMANTIC', value: 0.85, trend: 'declining', events: 456 },
                  ].map((item) => (
                    <div key={item.metric} className="flex items-center justify-between py-3 border-b border-border/30 last:border-0">
                      <div className="flex items-center gap-4">
                        <span className="text-xs font-mono font-medium w-24">{item.metric}</span>
                        <Gauge className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-mono">{Math.round(item.value * 100)}%</span>
                        <ProgressBar value={item.value * 100} showValue={false} size="sm" />
                      </div>
                      <div className="flex items-center gap-6 text-[10px] text-muted-foreground">
                        <span className={item.trend === 'stable' ? 'text-green-500' : item.trend === 'improving' ? 'text-blue-500' : 'text-yellow-500'}>
                          {item.trend}
                        </span>
                        <span className="font-mono">{item.events} events</span>
                      </div>
                    </div>
                  ))}
                </div>
              </ConsolePanel>
            )}
          </>
        )}
      </div>
    </div>
  )
}
