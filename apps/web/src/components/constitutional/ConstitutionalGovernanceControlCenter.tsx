/**
 * 43V3R CORE - Constitutional Governance Control Center
 * Production-grade orchestration intelligence interface.
 */
'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  Shield,
  Lock,
  AlertTriangle,
  CheckCircle2,
  GitBranch,
  RefreshCw,
  Play,
  Pause,
  Settings,
  Activity,
  Brain,
  Target,
  TrendingUp,
  TrendingDown,
  Layers,
} from 'lucide-react'
import { useConstitutionalApi } from '@/lib/constitutional-api'
import {
  ConsolePanel,
  DataTable,
  StatusDot,
  ConfidenceBadge,
  IconButton,
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
  invariantPolicies: number
  safetyScore: number
  coherenceScore: number
  violations: number
  criticalViolations: number
}

interface ProfileMetrics {
  profileId: string
  scope: string
  governanceScope: string
  cycleCount: number
  violations: number
  isActive: boolean
}

interface SafetyMetrics {
  safetyState: string
  riskScore: number
  collapseProbability: number
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
    activeProfiles: 8 + Math.floor(Math.random() * 4),
    invariantPolicies: 16 + Math.floor(Math.random() * 8),
    safetyScore: 0.92 + (Math.random() - 0.5) * 0.05,
    coherenceScore: 0.88 + (Math.random() - 0.5) * 0.08,
    violations: 3 + Math.floor(Math.random() * 5),
    criticalViolations: Math.floor(Math.random() * 2),
  }
}

function generateProfiles(): ProfileMetrics[] {
  const scopes = ['orchestration', 'ecosystem', 'governance', 'cognition']
  const govScopes = ['local', 'ecosystem', 'global']

  return Array.from({ length: 6 }, (_, i) => ({
    profileId: `con_profile_${i + 1}`,
    scope: scopes[i % scopes.length],
    governanceScope: govScopes[i % govScopes.length],
    cycleCount: Math.floor(Math.random() * 50) + 10,
    violations: Math.floor(Math.random() * 10),
    isActive: Math.random() > 0.2,
  }))
}

// =====================================================================
// Main Component
// =====================================================================

export default function ConstitutionalGovernanceControlCenter() {
  const api = useConstitutionalApi()
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  // State data
  const [metrics, setMetrics] = useState<GovernanceMetrics | null>(null)
  const [profiles, setProfiles] = useState<ProfileMetrics[]>([])
  const [sparklines, setSparklines] = useState<Record<string, number[]>>({})

  // Load data
  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      const newMetrics = generateMetrics()
      setMetrics(newMetrics)
      setProfiles(generateProfiles())
      setSparklines({
        safety: generateSparkline(newMetrics.safetyScore),
        coherence: generateSparkline(newMetrics.coherenceScore),
      })
      setLastRefresh(new Date())
    } catch (error) {
      console.error('Failed to load constitutional governance data:', error)
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
    { id: 'invariants', label: 'Invariants' },
    { id: 'safety', label: 'Safety' },
    { id: 'audit', label: 'Audit' },
  ]

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-card">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center h-8 w-8 rounded-md bg-amber-500/20">
            <Shield className="h-4 w-4 text-amber-400" />
          </div>
          <div>
            <h1 className="text-sm font-semibold text-foreground">Constitutional Governance</h1>
            <p className="text-xs text-muted-foreground">
              Invariant Enforcement & Safety Systems
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
        {activeTab === 'profiles' && <ProfilesTab profiles={profiles} />}
        {activeTab === 'invariants' && <InvariantsTab />}
        {activeTab === 'safety' && <SafetyTab sparklines={sparklines} />}
        {activeTab === 'audit' && <AuditTab />}
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
          trend={sparklines.safety}
          compact
        />
        <MetricGrid
          title="Invariant Policies"
          value={metrics.invariantPolicies}
          icon={<Lock className="h-4 w-4" />}
          trend={sparklines.coherence}
          compact
        />
        <MetricGrid
          title="Safety Score"
          value={`${(metrics.safetyScore * 100).toFixed(1)}%`}
          icon={<Target className="h-4 w-4" />}
          trend={sparklines.safety}
          trendUp={true}
          compact
        />
        <MetricGrid
          title="Coherence"
          value={`${(metrics.coherenceScore * 100).toFixed(1)}%`}
          icon={<Activity className="h-4 w-4" />}
          trend={sparklines.coherence}
          trendUp={true}
          compact
        />
        <MetricGrid
          title="Violations"
          value={metrics.violations}
          icon={<AlertTriangle className="h-4 w-4" />}
          compact
        />
        <MetricGrid
          title="Critical"
          value={metrics.criticalViolations}
          icon={<AlertTriangle className="h-4 w-4" />}
          trendDown={true}
          compact
        />
      </div>

      {/* Safety Evolution Chart */}
      <ConsolePanel
        title="Safety Evolution"
        icon={<TrendingUp className="h-4 w-4" />}
      >
        <div className="h-40">
          <Sparkline
            data={sparklines.safety || []}
            height={140}
            color="var(--amber-500)"
          />
        </div>
        <div className="mt-2 text-xs text-muted-foreground">
          Last 12 cycles • Safety Target: 90% • Current: {(metrics.safetyScore * 100).toFixed(1)}%
        </div>
      </ConsolePanel>

      {/* Governance Overview */}
      <div className="grid grid-cols-2 gap-4">
        <ConsolePanel
          title="Constraint Severity Distribution"
          icon={<Lock className="h-4 w-4" />}
        >
          <div className="space-y-2">
            {[
              { label: 'Blocking', value: 0.05, color: 'bg-red-500' },
              { label: 'Critical', value: 0.12, color: 'bg-orange-500' },
              { label: 'High', value: 0.28, color: 'bg-amber-500' },
              { label: 'Moderate', value: 0.35, color: 'bg-yellow-500' },
              { label: 'Info', value: 0.20, color: 'bg-blue-500' },
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
          title="Governance Scope Distribution"
          icon={<Layers className="h-4 w-4" />}
        >
          <div className="space-y-2">
            {[
              { label: 'Global', count: 2, level: 100 },
              { label: 'Ecosystem', count: 5, level: 78 },
              { label: 'Domain', count: 12, level: 62 },
              { label: 'Session', count: 18, level: 45 },
              { label: 'Local', count: 24, level: 28 },
            ].map((item, i) => (
              <div key={item.label} className="flex items-center gap-2">
                <div className="flex items-center justify-center w-5 h-5 rounded bg-amber-500/20 text-[10px] text-amber-400">
                  {i + 1}
                </div>
                <span className="text-xs text-muted-foreground flex-1">{item.label}</span>
                <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                  {item.count}
                </Badge>
                <div className="w-20 h-1.5 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full bg-amber-500"
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

function ProfilesTab({ profiles }: { profiles: ProfileMetrics[] }) {
  const columns = [
    { key: 'profileId', label: 'Profile ID', width: 'w-36' },
    { key: 'scope', label: 'Scope', width: 'w-28' },
    { key: 'governanceScope', label: 'Gov Scope', width: 'w-28' },
    { key: 'cycleCount', label: 'Cycles', width: 'w-20', render: (v: number) => String(v) },
    { key: 'violations', label: 'Violations', width: 'w-24', render: (v: number) => String(v) },
    { key: 'isActive', label: 'Active', width: 'w-20', render: (v: boolean) => (
      <StatusDot status={v ? 'active' : 'idle'} size="sm" />
    )},
  ]

  return (
    <div className="space-y-4">
      <ConsolePanel title="Constitutional Profiles" icon={<Shield className="h-4 w-4" />}>
        <DataTable columns={columns} data={profiles} />
      </ConsolePanel>
    </div>
  )
}

function InvariantsTab() {
  const invariants = [
    { id: 'INV-001', name: 'Safety Checkpoint', type: 'safety', severity: 'high', status: 'active' },
    { id: 'INV-002', name: 'Coherence Threshold', type: 'coherence', severity: 'moderate', status: 'active' },
    { id: 'INV-003', name: 'Resource Limit', type: 'resource', severity: 'critical', status: 'active' },
    { id: 'INV-004', name: 'Semantic Integrity', type: 'integrity', severity: 'high', status: 'active' },
    { id: 'INV-005', name: 'Termination Guarantee', type: 'termination', severity: 'blocking', status: 'active' },
  ]

  return (
    <ConsolePanel title="Invariant Registry" icon={<Lock className="h-4 w-4" />}>
      <div className="space-y-2">
        {invariants.map((inv) => (
          <div
            key={inv.id}
            className="flex items-center gap-3 p-2 rounded border border-border bg-card"
          >
            <StatusDot status={inv.status === 'active' ? 'active' : 'idle'} size="sm" />
            <div className="flex-1">
              <div className="text-xs font-medium">{inv.name}</div>
              <div className="text-[10px] text-muted-foreground">{inv.id}</div>
            </div>
            <Badge variant="outline" className="text-[10px]">
              {inv.type}
            </Badge>
            <Badge
              variant={inv.severity === 'blocking' || inv.severity === 'critical' ? 'destructive' : 'outline'}
              className="text-[10px]"
            >
              {inv.severity}
            </Badge>
          </div>
        ))}
      </div>
    </ConsolePanel>
  )
}

function SafetyTab({ sparklines }: { sparklines: Record<string, number[]> }) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <ConsolePanel title="Recursive Safety State" icon={<Brain className="h-4 w-4" />}>
          <div className="h-32">
            <Sparkline
              data={sparklines.safety || []}
              height={112}
              color="var(--green-500)"
            />
          </div>
          <div className="mt-2 grid grid-cols-4 gap-2">
            <MetricValue label="Depth" value="7/10" />
            <MetricValue label="Risk" value="0.12" />
            <MetricValue label="Collapse" value="0.02" />
            <MetricValue label="State" value="NOMINAL" />
          </div>
        </ConsolePanel>

        <ConsolePanel title="Boundary Compliance" icon={<Target className="h-4 w-4" />}>
          <div className="space-y-2">
            {[
              { name: 'Recursion Depth', current: 0.7, max: 0.95 },
              { name: 'Stack Size', current: 0.45, max: 0.9 },
              { name: 'Iteration Count', current: 0.3, max: 0.85 },
              { name: 'Memory Usage', current: 0.6, max: 0.9 },
            ].map((boundary) => (
              <div key={boundary.name} className="flex items-center gap-2">
                <span className="text-[10px] text-muted-foreground w-28">{boundary.name}</span>
                <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${boundary.current > boundary.max * 0.9 ? 'bg-red-500' : boundary.current > boundary.max * 0.7 ? 'bg-yellow-500' : 'bg-green-500'}`}
                    style={{ width: `${Math.min(100, (boundary.current / boundary.max) * 100)}%` }}
                  />
                </div>
                <span className="text-[10px] font-mono w-12 text-right">
                  {(boundary.current * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </ConsolePanel>
      </div>
    </div>
  )
}

function AuditTab() {
  const audits = [
    { id: 'AUD-001', type: 'CONSTRAINT_VALIDATED', success: true, time: '12:45:32' },
    { id: 'AUD-002', type: 'POLICY_APPLIED', success: true, time: '12:45:18' },
    { id: 'AUD-003', type: 'BOUNDARY_CHECK', success: true, time: '12:45:05' },
    { id: 'AUD-004', type: 'VIOLATION_DETECTED', success: false, time: '12:44:52' },
    { id: 'AUD-005', type: 'REMEDIATION_APPLIED', success: true, time: '12:44:40' },
  ]

  return (
    <ConsolePanel title="Constitutional Audit Trail" icon={<Activity className="h-4 w-4" />}>
      <div className="space-y-1">
        {audits.map((audit) => (
          <div
            key={audit.id}
            className="flex items-center gap-3 py-1.5 px-2 rounded hover:bg-muted/50"
          >
            <StatusDot
              status={audit.success ? 'active' : 'error'}
              size="sm"
            />
            <span className="text-[10px] font-mono text-muted-foreground w-20">
              {audit.time}
            </span>
            <span className="text-xs font-medium flex-1">
              {audit.type}
            </span>
            <Badge variant={audit.success ? 'outline' : 'destructive'} className="text-[10px]">
              {audit.success ? 'SUCCESS' : 'FAILURE'}
            </Badge>
          </div>
        ))}
      </div>
    </ConsolePanel>
  )
}
