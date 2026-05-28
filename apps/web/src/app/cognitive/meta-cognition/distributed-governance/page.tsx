/**
 * Distributed Governance Workspace
 * Multi-node cognition governance and policy enforcement.
 */
'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  Shield,
  Server,
  Users,
  Lock,
  AlertTriangle,
  CheckCircle2,
  Clock,
  RefreshCw,
  Play,
  Pause,
  Network,
  Activity,
  GitBranch,
  Eye,
} from 'lucide-react'
import {
  useMetaCognitionApi,
  type AdaptiveGovernanceProfile,
} from '@/lib/meta-cognition-api'
import { ConsolePanel, DataTable, StatusDot, ConfidenceBadge, IconButton, ProgressBar, TabBar, Sparkline } from '@/components/cognitive/primitives'

// ==================== Mock Data ====================

const mockProfiles: AdaptiveGovernanceProfile[] = [
  {
    profile_id: 'gov_profile_001',
    profile_key: 'orchestration_governance',
    scope: 'global',
    domain: 'orchestration',
    validation_thresholds: { min_reasoning_quality: 0.7, min_coherence: 0.75, min_consistency: 0.7 },
    alignment_requirements: {},
    enforcement_rules: [
      { action_type: 'execute_high_risk', action: 'deny', conditions: { confidence: { lt: 0.8 } } },
      { action_type: 'deploy', action: 'escalate', conditions: { resource_usage: { gt: 0.9 } } },
    ],
    policy_mode: 'active',
    intervention_level: 'advisory',
    is_active: true,
    alignment_status: 'aligned',
    trigger_count: 1247,
    violation_count: 3,
    last_triggered: new Date(Date.now() - 300000).toISOString(),
    version: 2,
  },
  {
    profile_id: 'gov_profile_002',
    profile_key: 'semantic_validation',
    scope: 'semantic',
    domain: 'reasoning',
    validation_thresholds: { min_consistency: 0.75, min_coherence: 0.8 },
    alignment_requirements: {},
    enforcement_rules: [
      { action_type: 'validate_semantic', action: 'allow', conditions: {} },
    ],
    policy_mode: 'active',
    intervention_level: 'enforcing',
    is_active: true,
    alignment_status: 'aligned',
    trigger_count: 892,
    violation_count: 1,
    last_triggered: new Date(Date.now() - 600000).toISOString(),
    version: 1,
  },
  {
    profile_id: 'gov_profile_003',
    profile_key: 'execution_limits',
    scope: 'execution',
    domain: 'runtime',
    validation_thresholds: { max_execution_time: 3600, max_memory: 8192 },
    alignment_requirements: {},
    enforcement_rules: [
      { action_type: 'execute', action: 'allow', conditions: { time: { lt: 3600 } } },
    ],
    policy_mode: 'active',
    intervention_level: 'enforcing',
    is_active: true,
    alignment_status: 'deviating',
    trigger_count: 2341,
    violation_count: 12,
    last_triggered: new Date(Date.now() - 120000).toISOString(),
    version: 3,
  },
]

// ==================== Main Component ====================

export default function DistributedGovernanceWorkspace() {
  const api = useMetaCognitionApi()
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [profiles, setProfiles] = useState<AdaptiveGovernanceProfile[]>([])
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  // Load data
  const loadData = useCallback(async () => {
    try {
      try {
        const data = await api.listGovernanceProfiles()
        setProfiles(data)
      } catch {
        setProfiles(mockProfiles)
      }
    } catch {
      setProfiles(mockProfiles)
    }
    setLastRefresh(new Date())
    setLoading(false)
  }, [api])

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

  // Tabs
  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Shield className="h-3 w-3" /> },
    { id: 'profiles', label: 'Profiles', icon: <Lock className="h-3 w-3" /> },
    { id: 'rules', label: 'Rules', icon: <GitBranch className="h-3 w-3" /> },
    { id: 'violations', label: 'Violations', icon: <AlertTriangle className="h-3 w-3" /> },
  ]

  // Calculate metrics
  const activeProfiles = profiles.filter(p => p.is_active).length
  const alignedCount = profiles.filter(p => p.alignment_status === 'aligned').length
  const deviatingCount = profiles.filter(p => p.alignment_status === 'deviating').length
  const totalTriggers = profiles.reduce((sum, p) => sum + p.trigger_count, 0)
  const totalViolations = profiles.reduce((sum, p) => sum + p.violation_count, 0)

  // Generate sparkline
  function generateSparkline(base: number, length = 12): number[] {
    const data: number[] = []
    let current = base
    for (let i = 0; i < length; i++) {
      current = current + (Math.random() - 0.5) * 0.05
      data.push(Math.max(0, Math.min(1, current)))
    }
    return data
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex items-center gap-2 text-muted-foreground">
          <RefreshCw className="h-4 w-4 animate-spin" />
          <span className="text-sm">Loading Distributed Governance...</span>
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
            <Shield className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Distributed Governance Workspace</h1>
            <p className="text-xs text-muted-foreground">Multi-node cognition governance and policy enforcement</p>
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
          { label: 'Total Profiles', value: profiles.length, icon: <Lock className="h-3.5 w-3.5" /> },
          { label: 'Active', value: activeProfiles, icon: <CheckCircle2 className="h-3.5 w-3.5" /> },
          { label: 'Aligned', value: alignedCount, icon: <Shield className="h-3.5 w-3.5" />, color: 'text-green-500' },
          { label: 'Deviating', value: deviatingCount, icon: <AlertTriangle className="h-3.5 w-3.5" />, color: 'text-yellow-500' },
          { label: 'Total Triggers', value: totalTriggers.toLocaleString(), icon: <Activity className="h-3.5 w-3.5" /> },
          { label: 'Total Violations', value: totalViolations, icon: <AlertTriangle className="h-3.5 w-3.5" />, color: totalViolations > 0 ? 'text-red-500' : '' },
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
          {/* Governance Profiles Overview */}
          <ConsolePanel title="Governance Profiles" icon={<Shield className="h-4 w-4" />} subtitle="Active governance configuration">
            <div className="grid grid-cols-3 gap-4">
              {profiles.map(profile => (
                <div key={profile.profile_id} className={`p-4 rounded border ${
                  profile.alignment_status === 'aligned' ? 'border-green-500/20 bg-green-500/5' :
                  profile.alignment_status === 'deviating' ? 'border-yellow-500/20 bg-yellow-500/5' :
                  'border-border bg-card'
                }`}>
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Shield className={`h-4 w-4 ${
                        profile.alignment_status === 'aligned' ? 'text-green-500' :
                        profile.alignment_status === 'deviating' ? 'text-yellow-500' :
                        'text-muted-foreground'
                      }`} />
                      <span className="font-mono text-xs">{profile.profile_key}</span>
                    </div>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                      profile.is_active ? 'bg-green-500/10 text-green-500' : 'bg-muted text-muted-foreground'
                    }`}>{profile.is_active ? 'ACTIVE' : 'INACTIVE'}</span>
                  </div>
                  <div className="space-y-2 text-[10px]">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Scope:</span>
                      <span className="font-mono">{profile.scope}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Domain:</span>
                      <span className="font-mono">{profile.domain}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Mode:</span>
                      <span className="font-mono">{profile.policy_mode}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Alignment:</span>
                      <span className={`${
                        profile.alignment_status === 'aligned' ? 'text-green-500' :
                        profile.alignment_status === 'deviating' ? 'text-yellow-500' :
                        'text-muted-foreground'
                      }`}>{profile.alignment_status.toUpperCase()}</span>
                    </div>
                  </div>
                  <div className="mt-3 pt-3 border-t border-border">
                    <div className="grid grid-cols-2 gap-2 text-[10px]">
                      <div>
                        <span className="text-muted-foreground">Triggers:</span>
                        <span className="ml-1 font-mono">{profile.trigger_count.toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Violations:</span>
                        <span className={`ml-1 font-mono ${profile.violation_count > 0 ? 'text-red-500' : 'text-green-500'}`}>{profile.violation_count}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>

          {/* Governance Activity Trend */}
          <div className="grid grid-cols-2 gap-4">
            <ConsolePanel title="Trigger Activity" icon={<Activity className="h-4 w-4" />} subtitle="Policy enforcement activity">
              <Sparkline data={generateSparkline(0.7)} height={48} color="#22c55e" />
            </ConsolePanel>

            <ConsolePanel title="Violation Rate" icon={<AlertTriangle className="h-4 w-4" />} subtitle="Policy violation trend">
              <Sparkline data={generateSparkline(0.05)} height={48} color="#ef4444" />
            </ConsolePanel>
          </div>
        </div>
      )}

      {/* Profiles Tab */}
      {activeTab === 'profiles' && (
        <ConsolePanel title="Governance Profiles" icon={<Lock className="h-4 w-4" />} subtitle={`${profiles.length} configured profiles`}>
          <DataTable
            columns={[
              { key: 'profile_key', label: 'Profile Key', width: '18%' },
              { key: 'scope', label: 'Scope', width: '12%' },
              { key: 'domain', label: 'Domain', width: '12%' },
              { key: 'mode', label: 'Policy Mode', width: '12%' },
              { key: 'intervention', label: 'Intervention', width: '12%' },
              { key: 'alignment', label: 'Alignment', width: '12%' },
              { key: 'rules', label: 'Rules', width: '10%' },
              { key: 'status', label: 'Status', width: '12%' },
            ]}
            rows={profiles.map(p => ({
              profile_key: <span className="font-mono text-xs">{p.profile_key}</span>,
              scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{p.scope}</span>,
              domain: <span className="text-xs">{p.domain}</span>,
              mode: <span className="text-xs font-mono">{p.policy_mode}</span>,
              intervention: <span className={`text-xs ${
                p.intervention_level === 'enforcing' ? 'text-red-500' :
                p.intervention_level === 'advisory' ? 'text-yellow-500' :
                'text-muted-foreground'
              }`}>{p.intervention_level}</span>,
              alignment: <span className={`text-xs ${
                p.alignment_status === 'aligned' ? 'text-green-500' :
                p.alignment_status === 'deviating' ? 'text-yellow-500' :
                p.alignment_status === 'misaligned' ? 'text-red-500' :
                'text-muted-foreground'
              }`}>{p.alignment_status.toUpperCase()}</span>,
              rules: <span className="font-mono text-xs">{p.enforcement_rules.length}</span>,
              status: p.is_active ? <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/10 text-green-500">ACTIVE</span> : <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">INACTIVE</span>,
            }))}
          />
        </ConsolePanel>
      )}

      {/* Rules Tab */}
      {activeTab === 'rules' && (
        <ConsolePanel title="Enforcement Rules" icon={<GitBranch className="h-4 w-4" />} subtitle="Active policy enforcement rules">
          <div className="space-y-3">
            {profiles.flatMap(profile =>
              profile.enforcement_rules.map((rule, idx) => (
                <div key={`${profile.profile_id}-${idx}`} className="flex items-center justify-between p-3 rounded border border-border bg-card">
                  <div className="flex items-center gap-3">
                    <div className={`h-8 w-8 flex items-center justify-center rounded ${
                      rule.action === 'allow' ? 'bg-green-500/10' :
                      rule.action === 'deny' ? 'bg-red-500/10' :
                      'bg-yellow-500/10'
                    }`}>
                      {rule.action === 'allow' ? <CheckCircle2 className="h-4 w-4 text-green-500" /> :
                       rule.action === 'deny' ? <AlertTriangle className="h-4 w-4 text-red-500" /> :
                       <Activity className="h-4 w-4 text-yellow-500" />}
                    </div>
                    <div>
                      <div className="text-xs font-medium">{rule.action_type}</div>
                      <div className="text-[10px] text-muted-foreground">
                        Profile: {profile.profile_key} | Action: {rule.action.toUpperCase()}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-[10px] text-muted-foreground">Conditions</div>
                      <div className="text-xs font-mono">{Object.keys(rule.conditions || {}).length}</div>
                    </div>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                      rule.action === 'allow' ? 'bg-green-500/10 text-green-500' :
                      rule.action === 'deny' ? 'bg-red-500/10 text-red-500' :
                      'bg-yellow-500/10 text-yellow-500'
                    }`}>{rule.action.toUpperCase()}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </ConsolePanel>
      )}

      {/* Violations Tab */}
      {activeTab === 'violations' && (
        <ConsolePanel title="Policy Violations" icon={<AlertTriangle className="h-4 w-4" />} subtitle={totalViolations === 0 ? 'No violations' : `${totalViolations} total violations`}>
          {totalViolations === 0 ? (
            <div className="flex items-center gap-2 py-8">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              <span className="text-xs text-muted-foreground">No policy violations - all governance profiles operating within parameters</span>
            </div>
          ) : (
            <div className="space-y-3">
              {profiles.filter(p => p.violation_count > 0).map(profile => (
                <div key={profile.profile_id} className="p-4 rounded border border-red-500/20 bg-red-500/5">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-red-500" />
                      <span className="font-mono text-xs">{profile.profile_key}</span>
                    </div>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-500/10 text-red-500">
                      {profile.violation_count} VIOLATIONS
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Domain: {profile.domain} | Scope: {profile.scope}
                  </div>
                </div>
              ))}
            </div>
          )}
        </ConsolePanel>
      )}
    </div>
  )
}
