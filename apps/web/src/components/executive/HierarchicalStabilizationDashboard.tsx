/**
 * 43V3R CORE - Hierarchical Stabilization Dashboard
 * 
 * Runtime stabilization monitoring with tier tracking, recovery governance,
 * and adaptive escalation visualization.
 */
'use client'

import { useState, useEffect } from 'react'
import {
  Gauge,
  Activity,
  Shield,
  AlertTriangle,
  CheckCircle2,
  Clock,
  RefreshCw,
  TrendingUp,
  TrendingDown,
} from 'lucide-react'
import { useExecutiveApi } from '@/lib/executive-api'
import {
  ConsolePanel,
  StatusDot,
  DataTable,
  TabBar,
  IconButton,
  ProgressBar,
} from '@/components/cognitive/primitives'

interface StabilizationProfile {
  id: string
  profile_key: string
  name: string
  scope: string
  tier: string
  priority: number
  state: string
  activation_count: number
  success_count: number
}

interface StabilizationEvent {
  id: string
  event_key: string
  target_id: string
  action: string
  tier_before: string
  tier_after: string
  success: boolean
  coherence_delta: number
  detected_at: string
}

export default function HierarchicalStabilizationDashboard() {
  const api = useExecutiveApi()
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('tiers')
  const [profiles, setProfiles] = useState<StabilizationProfile[]>([])
  const [events, setEvents] = useState<StabilizationEvent[]>([])

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await api.listStabilizationProfiles({})
        setProfiles(data as StabilizationProfile[])
      } catch {
        setProfiles([
          { id: 'p1', profile_key: 'stab_exec_01', name: 'Execution Stabilizer', scope: 'execution', tier: 'tier_0_healthy', priority: 9, state: 'active', activation_count: 47, success_count: 46 },
          { id: 'p2', profile_key: 'stab_orch_01', name: 'Orchestration Stabilizer', scope: 'orchestration', tier: 'tier_1_marginal', priority: 7, state: 'active', activation_count: 23, success_count: 21 },
          { id: 'p3', profile_key: 'stab_cog_01', name: 'Cognition Stabilizer', scope: 'cognition', tier: 'tier_0_healthy', priority: 8, state: 'active', activation_count: 12, success_count: 12 },
        ])
        setEvents([
          { id: 'e1', event_key: 'evt_8a3f21', target_id: 'render_pipeline', action: 'balance', tier_before: 'tier_1_marginal', tier_after: 'tier_0_healthy', success: true, coherence_delta: 0.12, detected_at: new Date(Date.now() - 60000).toISOString() },
          { id: 'e2', event_key: 'evt_4c7d18', target_id: 'memory_controller', action: 'restrict', tier_before: 'tier_2_degrading', tier_after: 'tier_1_marginal', success: true, coherence_delta: 0.08, detected_at: new Date(Date.now() - 180000).toISOString() },
        ])
      }
      setLoading(false)
    }
    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [api])

  const tabs = [
    { id: 'tiers', label: 'Tiers', icon: <Gauge className="h-3 w-3" /> },
    { id: 'profiles', label: 'Profiles', icon: <Shield className="h-3 w-3" /> },
    { id: 'events', label: 'Events', icon: <Activity className="h-3 w-3" /> },
  ]

  const tiers = [
    { name: 'TIER_0_HEALTHY', label: 'Healthy', threshold: 0.9, color: 'success' },
    { name: 'tier_1_marginal', label: 'Marginal', threshold: 0.7, color: 'primary' },
    { name: 'tier_2_degrading', label: 'Degrading', threshold: 0.5, color: 'warning' },
    { name: 'tier_3_unstable', label: 'Unstable', threshold: 0.3, color: 'error' },
    { name: 'tier_4_critical', label: 'Critical', threshold: 0.1, color: 'error' },
    { name: 'tier_5_collapse', label: 'Collapse', threshold: 0.0, color: 'error' },
  ]

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-3">
          <Gauge className="h-5 w-5 text-primary" />
          <span className="font-mono text-sm font-semibold tracking-tight">STABILIZATION HIERARCHY</span>
          <div className="h-4 w-px bg-border/50" />
          <StatusDot status="active" />
          <span className="text-[10px] font-mono text-muted-foreground uppercase">
            {profiles.length} profiles
          </span>
        </div>
        <IconButton icon={<RefreshCw className="h-3 w-3" />} onClick={() => setLoading(true)} />
      </div>

      {/* Tab Bar */}
      <div className="px-4 py-2 border-b border-border/30">
        <TabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <>
            {activeTab === 'tiers' && (
              <div className="grid gap-4 lg:grid-cols-3">
                {tiers.map((tier) => {
                  const tierProfiles = profiles.filter(p => p.tier === tier.name)
                  return (
                    <ConsolePanel
                      key={tier.name}
                      title={tier.label}
                      icon={tier.color === 'success' ? <CheckCircle2 className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
                      subtitle={`Threshold: ${Math.round(tier.threshold * 100)}%`}
                    >
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-mono text-muted-foreground">{tier.name}</span>
                          <StatusDot status={tierProfiles.length > 0 ? 'active' : 'idle'} />
                        </div>
                        <ProgressBar
                          value={tier.threshold * 100}
                          showValue={false}
                          color={tier.color as 'success' | 'primary' | 'warning' | 'error'}
                        />
                        <div className="flex justify-between text-[10px] text-muted-foreground">
                          <span>Profiles:</span>
                          <span className="font-mono">{tierProfiles.length}</span>
                        </div>
                      </div>
                    </ConsolePanel>
                  )
                })}
              </div>
            )}

            {activeTab === 'profiles' && (
              <ConsolePanel
                title="Stabilization Profiles"
                icon={<Shield className="h-4 w-4" />}
                subtitle="Runtime coherence profiles"
              >
                <DataTable
                  columns={[
                    { key: 'name', label: 'Profile', width: '25%' },
                    { key: 'scope', label: 'Scope', width: '15%' },
                    { key: 'tier', label: 'Tier', width: '15%' },
                    { key: 'priority', label: 'Priority', width: '15%' },
                    { key: 'activations', label: 'Activations', width: '15%' },
                    { key: 'success', label: 'Success', width: '15%' },
                  ]}
                  rows={profiles.map(p => ({
                    key: p.id,
                    name: <span className="text-xs font-medium">{p.name}</span>,
                    scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{p.scope}</span>,
                    tier: (
                      <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                        p.tier === 'tier_0_healthy' ? 'bg-green-500/10 text-green-500' :
                        p.tier === 'tier_1_marginal' ? 'bg-blue-500/10 text-blue-500' :
                        p.tier === 'tier_2_degrading' ? 'bg-yellow-500/10 text-yellow-500' :
                        'bg-red-500/10 text-red-500'
                      }`}>{p.tier.replace('tier_', 'TIER_').replace('_', ' ')}</span>
                    ),
                    priority: (
                      <div className="flex items-center gap-1">
                        <ProgressBar value={(p.priority / 10) * 100} showValue={false} size="sm" />
                        <span className="font-mono text-[10px] ml-1">{p.priority}</span>
                      </div>
                    ),
                    activations: <span className="font-mono text-xs">{p.activation_count}</span>,
                    success: (
                      <span className="font-mono text-xs text-green-500">
                        {Math.round((p.success_count / p.activation_count) * 100)}%
                      </span>
                    ),
                  }))}
                />
              </ConsolePanel>
            )}

            {activeTab === 'events' && (
              <ConsolePanel
                title="Stabilization Events"
                icon={<Activity className="h-4 w-4" />}
                subtitle="Recent stabilization actions"
              >
                <DataTable
                  columns={[
                    { key: 'time', label: 'Time', width: '15%' },
                    { key: 'target', label: 'Target', width: '20%' },
                    { key: 'action', label: 'Action', width: '15%' },
                    { key: 'transition', label: 'Transition', width: '25%' },
                    { key: 'delta', label: 'Delta', width: '15%' },
                    { key: 'status', label: 'Status', width: '10%' },
                  ]}
                  rows={events.map(e => ({
                    key: e.id,
                    time: <span className="font-mono text-xs text-muted-foreground">{new Date(e.detected_at).toLocaleTimeString()}</span>,
                    target: <span className="font-mono text-xs">{e.target_id.slice(0, 20)}</span>,
                    action: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{e.action}</span>,
                    transition: (
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] px-1 py-0.5 rounded bg-red-500/10 text-red-500">{e.tier_before}</span>
                        <TrendingUp className="h-3 w-3 text-green-500" />
                        <span className="text-[10px] px-1 py-0.5 rounded bg-green-500/10 text-green-500">{e.tier_after}</span>
                      </div>
                    ),
                    delta: (
                      <span className={`font-mono text-xs ${e.coherence_delta >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {e.coherence_delta >= 0 ? '+' : ''}{Math.round(e.coherence_delta * 100)}%
                      </span>
                    ),
                    status: e.success ? <CheckCircle2 className="h-4 w-4 text-green-500" /> : <AlertTriangle className="h-4 w-4 text-red-500" />,
                  }))}
                />
              </ConsolePanel>
            )}
          </>
        )}
      </div>
    </div>
  )
}
