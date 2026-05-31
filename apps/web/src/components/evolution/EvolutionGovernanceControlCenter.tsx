/**
 * 43V3R CORE - Evolution Governance Control Center
 * Production-grade orchestration intelligence interface.
 */
'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  Activity,
  Brain,
  Shield,
  GitBranch,
  Zap,
  RefreshCw,
  ChevronRight,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Target,
  TrendingUp,
  TrendingDown,
  Layers,
  Database,
  Network,
  Settings,
  Play,
  Pause,
  BarChart3,
} from 'lucide-react'
import { useEvolutionApi } from '@/lib/evolution-api'
import {
  ConsolePanel,
  DataTable,
  StatusDot,
  ConfidenceBadge,
  IconButton,
  ProgressBar,
  MetricGrid,
  MetricValue,
  TabBar,
  Sparkline,
  Badge,
} from '@/components/cognitive/primitives'

// =====================================================================
// Types
// =====================================================================

interface GovernanceMetrics {
  activeProfiles: number
  mutationPolicies: number
  coherenceScore: number
  evolutionCycles: number
  successfulAdaptations: number
  failedAdaptations: number
}

interface ProfileMetrics {
  profileId: string
  scope: string
  governanceLevel: string
  adaptationStrategy: string
  coherenceTarget: number
  cycleCount: number
  mutations: number
}

interface MutationMetrics {
  mutationId: string
  type: string
  severity: string
  status: string
  impact: number
  timestamp: string
}

// =====================================================================
// Mock Data Generators
// =====================================================================

function generateSparkline(base: number, length = 12): number[] {
  const data: number[] = []
  let current = base
  for (let i = 0; i < length; i++) {
    current = current + (Math.random() - 0.5) * 0.1
    data.push(Math.max(0, Math.min(1, current)))
  }
  return data
}

function generateMetrics(): GovernanceMetrics {
  return {
    activeProfiles: 12 + Math.floor(Math.random() * 5),
    mutationPolicies: 24 + Math.floor(Math.random() * 10),
    coherenceScore: 0.85 + (Math.random() - 0.5) * 0.1,
    evolutionCycles: 156 + Math.floor(Math.random() * 50),
    successfulAdaptations: 89 + Math.floor(Math.random() * 20),
    failedAdaptations: 12 + Math.floor(Math.random() * 8),
  }
}

function generateProfiles(): ProfileMetrics[] {
  const scopes = ['orchestration', 'cognition', 'semantic', 'runtime', 'governance']
  const levels = ['observation', 'recommendation', 'intervention', 'enforcement']
  const strategies = ['conservative', 'balanced', 'aggressive', 'recursive']

  return Array.from({ length: 8 }, (_, i) => ({
    profileId: `evo_profile_${i + 1}`,
    scope: scopes[i % scopes.length],
    governanceLevel: levels[i % levels.length],
    adaptationStrategy: strategies[i % strategies.length],
    coherenceTarget: 0.75 + Math.random() * 0.2,
    cycleCount: Math.floor(Math.random() * 100) + 10,
    mutations: Math.floor(Math.random() * 50) + 5,
  }))
}

function generateMutations(): MutationMetrics[] {
  const types = ['weight_adjustment', 'threshold_update', 'policy_change', 'state_mutation']
  const severities = ['trivial', 'minor', 'moderate', 'major', 'critical']
  const statuses = ['proposed', 'pending', 'approved', 'applied', 'verified']

  return Array.from({ length: 12 }, (_, i) => ({
    mutationId: `mut_${(Date.now() - i * 100000).toString(36)}`,
    type: types[i % types.length],
    severity: severities[i % severities.length],
    status: statuses[i % statuses.length],
    impact: Math.random() * 0.5,
    timestamp: new Date(Date.now() - i * 60000).toISOString(),
  }))
}

// =====================================================================
// Main Component
// =====================================================================

export default function EvolutionGovernanceControlCenter() {
  const api = useEvolutionApi()
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  // State data
  const [metrics, setMetrics] = useState<GovernanceMetrics | null>(null)
  const [profiles, setProfiles] = useState<ProfileMetrics[]>([])
  const [mutations, setMutations] = useState<MutationMetrics[]>([])
  const [sparklines, setSparklines] = useState<Record<string, number[]>>({})
  const [selectedProfile, setSelectedProfile] = useState<string | null>(null)

  // Load data
  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      // Generate mock data for demonstration
      const newMetrics = generateMetrics()
      setMetrics(newMetrics)
      setProfiles(generateProfiles())
      setMutations(generateMutations())
      setSparklines({
        coherence: generateSparkline(newMetrics.coherenceScore),
        cycles: generateSparkline(0.6),
        success: generateSparkline(0.85),
      })
      setLastRefresh(new Date())
    } catch (error) {
      console.error('Failed to load evolution governance data:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  // Initial load
  useEffect(() => {
    loadData()
  }, [loadData])

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return
    const interval = setInterval(loadData, 10000)
    return () => clearInterval(interval)
  }, [autoRefresh, loadData])

  // Tab configuration
  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'profiles', label: 'Profiles' },
    { id: 'mutations', label: 'Mutations' },
    { id: 'coherence', label: 'Coherence' },
    { id: 'policies', label: 'Policies' },
  ]

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-card">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center h-8 w-8 rounded-md bg-purple-500/20">
            <Brain className="h-4 w-4 text-purple-400" />
          </div>
          <div>
            <h1 className="text-sm font-semibold text-foreground">Evolution Governance</h1>
            <p className="text-xs text-muted-foreground">
              Adaptive Coherence Supervision
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <StatusDot
            status={loading ? 'processing' : 'active'}
            size="sm"
            pulse={loading}
          />
          <span className="text-xs text-muted-foreground">
            {lastRefresh.toLocaleTimeString()}
          </span>
          <IconButton
            icon={autoRefresh ? <Pause className="h-3 w-3" /> : <Play className="h-3 w-3" />}
            onClick={() => setAutoRefresh(!autoRefresh)}
            variant="ghost"
            size="sm"
          />
          <IconButton
            icon={<RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />}
            onClick={loadData}
            variant="ghost"
            size="sm"
          />
        </div>
      </div>

      {/* Tab Bar */}
      <TabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {activeTab === 'overview' && <OverviewTab metrics={metrics} sparklines={sparklines} />}
        {activeTab === 'profiles' && <ProfilesTab profiles={profiles} onSelect={setSelectedProfile} />}
        {activeTab === 'mutations' && <MutationsTab mutations={mutations} />}
        {activeTab === 'coherence' && <CoherenceTab sparklines={sparklines} />}
        {activeTab === 'policies' && <PoliciesTab />}
      </div>
    </div>
  )
}

// =====================================================================
// Tab Components
// =====================================================================

function OverviewTab({
  metrics,
  sparklines,
}: {
  metrics: GovernanceMetrics | null
  sparklines: Record<string, number[]>
}) {
  if (!metrics) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  return (
    <div className="space-y-4">
      {/* Key Metrics */}
      <div className="grid grid-cols-6 gap-3">
        <MetricGrid
          title="Active Profiles"
          value={metrics.activeProfiles}
          icon={<Shield className="h-4 w-4" />}
          trend={sparklines.coherence}
          compact
        />
        <MetricGrid
          title="Mutation Policies"
          value={metrics.mutationPolicies}
          icon={<GitBranch className="h-4 w-4" />}
          trend={sparklines.cycles}
          compact
        />
        <MetricGrid
          title="Coherence Score"
          value={`${(metrics.coherenceScore * 100).toFixed(1)}%`}
          icon={<Activity className="h-4 w-4" />}
          trend={sparklines.coherence}
          trendUp={true}
          compact
        />
        <MetricGrid
          title="Evolution Cycles"
          value={metrics.evolutionCycles}
          icon={<Layers className="h-4 w-4" />}
          compact
        />
        <MetricGrid
          title="Successful"
          value={metrics.successfulAdaptations}
          icon={<CheckCircle2 className="h-4 w-4" />}
          trend={sparklines.success}
          trendUp={true}
          compact
        />
        <MetricGrid
          title="Failed"
          value={metrics.failedAdaptations}
          icon={<AlertTriangle className="h-4 w-4" />}
          trendDown={true}
          compact
        />
      </div>

      {/* Coherence Evolution Chart */}
      <ConsolePanel
        title="Coherence Evolution"
        icon={<TrendingUp className="h-4 w-4" />}
      >
        <div className="h-40">
          <Sparkline
            data={sparklines.coherence || []}
            height={140}
            color="var(--purple-500)"
          />
        </div>
        <div className="mt-2 text-xs text-muted-foreground">
          Last 12 cycles • Target: 85% • Current: {(metrics.coherenceScore * 100).toFixed(1)}%
        </div>
      </ConsolePanel>

      {/* Governance Overview */}
      <div className="grid grid-cols-2 gap-4">
        <ConsolePanel
          title="Adaptation Strategy Distribution"
          icon={<Target className="h-4 w-4" />}
        >
          <div className="space-y-2">
            {[
              { label: 'Balanced', value: 0.45, color: 'bg-purple-500' },
              { label: 'Recursive', value: 0.25, color: 'bg-blue-500' },
              { label: 'Conservative', value: 0.20, color: 'bg-green-500' },
              { label: 'Aggressive', value: 0.10, color: 'bg-orange-500' },
            ].map((item) => (
              <div key={item.label} className="flex items-center gap-2">
                <div className={`w-1.5 h-1.5 rounded-full ${item.color}`} />
                <span className="text-xs text-muted-foreground flex-1">{item.label}</span>
                <span className="text-xs font-mono">{(item.value * 100).toFixed(0)}%</span>
                <div className="w-24 h-1.5 bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${item.color}`}
                    style={{ width: `${item.value * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </ConsolePanel>

        <ConsolePanel
          title="Governance Authority Levels"
          icon={<Shield className="h-4 w-4" />}
        >
          <div className="space-y-2">
            {[
              { label: 'Observation', count: 3, level: 36 },
              { label: 'Recommendation', count: 5, level: 58 },
              { label: 'Intervention', count: 8, level: 72 },
              { label: 'Enforcement', count: 2, level: 94 },
            ].map((item, i) => (
              <div key={item.label} className="flex items-center gap-2">
                <div className="flex items-center justify-center w-5 h-5 rounded bg-purple-500/20 text-[10px] text-purple-400">
                  {i + 1}
                </div>
                <span className="text-xs text-muted-foreground flex-1">{item.label}</span>
                <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                  {item.count}
                </Badge>
                <div className="w-20 h-1.5 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full bg-purple-500"
                    style={{ width: `${item.level}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </ConsolePanel>
      </div>
    </div>
  )
}

function ProfilesTab({
  profiles,
  onSelect,
}: {
  profiles: ProfileMetrics[]
  onSelect: (id: string) => void
}) {
  const columns = [
    { key: 'profileId', label: 'Profile ID', width: 'w-32' },
    { key: 'scope', label: 'Scope', width: 'w-28' },
    { key: 'governanceLevel', label: 'Gov Level', width: 'w-32' },
    { key: 'adaptationStrategy', label: 'Strategy', width: 'w-28' },
    { key: 'coherenceTarget', label: 'Target', width: 'w-20', render: (v: number) => `${(v * 100).toFixed(0)}%` },
    { key: 'cycleCount', label: 'Cycles', width: 'w-20', render: (v: number) => String(v) },
    { key: 'mutations', label: 'Mutations', width: 'w-24', render: (v: number) => String(v) },
  ]

  return (
    <div className="space-y-4">
      <ConsolePanel title="Evolution Profiles" icon={<Shield className="h-4 w-4" />}>
        <DataTable
          columns={columns}
          data={profiles}
          onRowClick={onSelect}
          rowClassName="cursor-pointer"
        />
      </ConsolePanel>
    </div>
  )
}

function MutationsTab({ mutations }: { mutations: MutationMetrics[] }) {
  const columns = [
    { key: 'mutationId', label: 'Mutation ID', width: 'w-36' },
    { key: 'type', label: 'Type', width: 'w-36' },
    { key: 'severity', label: 'Severity', width: 'w-24', render: (v: string) => (
      <Badge variant={v === 'critical' ? 'destructive' : 'outline'} className="text-[10px]">
        {v}
      </Badge>
    )},
    { key: 'status', label: 'Status', width: 'w-24', render: (v: string) => (
      <StatusDot status={v === 'verified' ? 'active' : v === 'failed' ? 'error' : 'processing'} size="sm" />
    )},
    { key: 'impact', label: 'Impact', width: 'w-20', render: (v: number) => `${(v * 100).toFixed(0)}%` },
    { key: 'timestamp', label: 'Timestamp', width: 'w-36', render: (v: string) => new Date(v).toLocaleTimeString() },
  ]

  return (
    <div className="space-y-4">
      <ConsolePanel title="Mutation Lineage" icon={<GitBranch className="h-4 w-4" />}>
        <DataTable columns={columns} data={mutations} />
      </ConsolePanel>
    </div>
  )
}

function CoherenceTab({ sparklines }: { sparklines: Record<string, number[]> }) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <ConsolePanel title="Systemic Coherence" icon={<Activity className="h-4 w-4" />}>
          <div className="h-32">
            <Sparkline
              data={sparklines.coherence || []}
              height={112}
              color="var(--green-500)"
            />
          </div>
          <div className="mt-2 grid grid-cols-4 gap-2">
            <MetricValue label="Orchestration" value="92%" />
            <MetricValue label="Cognition" value="89%" />
            <MetricValue label="Semantic" value="95%" />
            <MetricValue label="Distributed" value="87%" />
          </div>
        </ConsolePanel>

        <ConsolePanel title="Evolution Velocity" icon={<Zap className="h-4 w-4" />}>
          <div className="h-32">
            <Sparkline
              data={sparklines.cycles || []}
              height={112}
              color="var(--blue-500)"
            />
          </div>
          <div className="mt-2 grid grid-cols-4 gap-2">
            <MetricValue label="Mutations/s" value="2.4" />
            <MetricValue label="Adaptations/s" value="1.8" />
            <MetricValue label="Reconciliations/s" value="0.6" />
            <MetricValue label="Stabilizations/s" value="0.3" />
          </div>
        </ConsolePanel>
      </div>

      <ConsolePanel title="Component Coherence States" icon={<Database className="h-4 w-4" />}>
        <div className="grid grid-cols-6 gap-2">
          {[
            { name: 'orchestrator', health: 0.95 },
            { name: 'executor', health: 0.92 },
            { name: 'guardian', health: 0.88 },
            { name: 'memory', health: 0.97 },
            { name: 'planner', health: 0.85 },
            { name: 'evaluator', health: 0.91 },
          ].map((comp) => (
            <div key={comp.name} className="p-2 rounded border border-border bg-card">
              <div className="text-[10px] text-muted-foreground text-center uppercase">
                {comp.name}
              </div>
              <div className="mt-1 h-1.5 bg-muted rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${comp.health > 0.9 ? 'bg-green-500' : comp.health > 0.8 ? 'bg-yellow-500' : 'bg-red-500'}`}
                  style={{ width: `${comp.health * 100}%` }}
                />
              </div>
              <div className="text-xs text-center font-mono mt-1">
                {(comp.health * 100).toFixed(0)}%
              </div>
            </div>
          ))}
        </div>
      </ConsolePanel>
    </div>
  )
}

function PoliciesTab() {
  return (
    <ConsolePanel title="Mutation Policies" icon={<Shield className="h-4 w-4" />}>
      <div className="space-y-2">
        {[
          { name: 'orchestration_default', domain: 'orchestration', severity: 'moderate', active: true },
          { name: 'cognition_adaptation', domain: 'cognition', severity: 'major', active: true },
          { name: 'semantic_preservation', domain: 'semantic', severity: 'critical', active: true },
          { name: 'runtime_mutation', domain: 'runtime', severity: 'minor', active: false },
        ].map((policy) => (
          <div
            key={policy.name}
            className="flex items-center gap-3 p-2 rounded border border-border bg-card"
          >
            <StatusDot status={policy.active ? 'active' : 'idle'} size="sm" />
            <div className="flex-1">
              <div className="text-xs font-medium">{policy.name}</div>
              <div className="text-[10px] text-muted-foreground">{policy.domain}</div>
            </div>
            <Badge
              variant={policy.severity === 'critical' ? 'destructive' : 'outline'}
              className="text-[10px]"
            >
              {policy.severity}
            </Badge>
            <IconButton
              icon={<Settings className="h-3 w-3" />}
              variant="ghost"
              size="sm"
            />
          </div>
        ))}
      </div>
    </ConsolePanel>
  )
}
