/**
 * 43V3R CORE - Orchestration Arbitration Console
 * 
 * Real-time orchestration arbitration monitoring with conflict resolution,
 * negotiation tracking, and semantic policy reconciliation.
 */
'use client'

import { useState, useEffect } from 'react'
import {
  Shield,
  AlertTriangle,
  CheckCircle2,
  Clock,
  GitMerge,
  Users,
  Zap,
  RefreshCw,
  ChevronRight,
  BarChart3,
} from 'lucide-react'
import { useExecutiveApi } from '@/lib/executive-api'
import {
  ConsolePanel,
  StatusDot,
  ConfidenceBadge,
  DataTable,
  TabBar,
  IconButton,
  ProgressBar,
} from '@/components/cognitive/primitives'

interface ArbitrationItem {
  id: string
  arbitration_key: string
  scope: string
  conflict_type: string
  parties: string[]
  arbitration_state: string
  priority: number
  negotiation_rounds: number
  escalation_required: boolean
  detected_at: string
}

export default function OrchestrationArbitrationConsole() {
  const api = useExecutiveApi()
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('arbitrations')
  const [arbitrations, setArbitrations] = useState<ArbitrationItem[]>([])

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await api.listArbitrations({})
        setArbitrations(data as ArbitrationItem[])
      } catch {
        setArbitrations([
          {
            id: 'arb_001',
            arbitration_key: 'arb_8f3a21',
            scope: 'orchestration',
            conflict_type: 'resource_contention',
            parties: ['agent_alpha', 'agent_beta', 'agent_gamma'],
            arbitration_state: 'evaluating',
            priority: 7,
            negotiation_rounds: 2,
            escalation_required: false,
            detected_at: new Date(Date.now() - 120000).toISOString(),
          },
          {
            id: 'arb_002',
            arbitration_key: 'arb_4c7d18',
            scope: 'semantic',
            conflict_type: 'meaning_conflict',
            parties: ['cognitive_agent_1', 'cognitive_agent_2'],
            arbitration_state: 'arbitrating',
            priority: 5,
            negotiation_rounds: 4,
            escalation_required: false,
            detected_at: new Date(Date.now() - 300000).toISOString(),
          },
          {
            id: 'arb_003',
            arbitration_key: 'arb_9b2e67',
            scope: 'governance',
            conflict_type: 'policy_conflict',
            parties: ['governor_01', 'governor_02'],
            arbitration_state: 'reconciled',
            priority: 9,
            negotiation_rounds: 1,
            escalation_required: false,
            detected_at: new Date(Date.now() - 600000).toISOString(),
          },
        ])
      }
      setLoading(false)
    }
    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [api])

  const tabs = [
    { id: 'arbitrations', label: 'Arbitrations', icon: <Shield className="h-3 w-3" /> },
    { id: 'policies', label: 'Policies', icon: <BarChart3 className="h-3 w-3" /> },
    { id: 'metrics', label: 'Metrics', icon: <Zap className="h-3 w-3" /> },
  ]

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-3">
          <Shield className="h-5 w-5 text-primary" />
          <span className="font-mono text-sm font-semibold tracking-tight">ORCHESTRATION ARBITRATION</span>
          <div className="h-4 w-px bg-border/50" />
          <StatusDot status={arbitrations.some(a => a.arbitration_state === 'arbitrating') ? 'processing' : 'idle'} />
          <span className="text-[10px] font-mono text-muted-foreground uppercase">
            {arbitrations.length} active
          </span>
        </div>
        <div className="flex items-center gap-2">
          <IconButton icon={<RefreshCw className="h-3 w-3" />} onClick={() => setLoading(true)} />
        </div>
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
            {activeTab === 'arbitrations' && (
              <div className="space-y-4">
                <ConsolePanel
                  title="Active Arbitrations"
                  icon={<Shield className="h-4 w-4" />}
                  subtitle="Conflict resolution processes"
                >
                  <DataTable
                    columns={[
                      { key: 'key', label: 'Arb ID', width: '12%' },
                      { key: 'scope', label: 'Scope', width: '14%' },
                      { key: 'type', label: 'Type', width: '18%' },
                      { key: 'parties', label: 'Parties', width: '14%' },
                      { key: 'priority', label: 'Priority', width: '10%' },
                      { key: 'rounds', label: 'Rounds', width: '10%' },
                      { key: 'state', label: 'State', width: '12%' },
                      { key: 'escalate', label: '', width: '10%' },
                    ]}
                    rows={arbitrations.map(a => ({
                      key: a.id,
                      key: <span className="font-mono text-xs">{a.arbitration_key.slice(0, 12)}</span>,
                      scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{a.scope}</span>,
                      type: <span className="text-xs">{a.conflict_type}</span>,
                      parties: (
                        <div className="flex items-center gap-1">
                          <Users className="h-3 w-3 text-muted-foreground" />
                          <span className="font-mono text-xs">{a.parties.length}</span>
                        </div>
                      ),
                      priority: (
                        <div className="flex items-center gap-1">
                          <ProgressBar value={(a.priority / 10) * 100} showValue={false} size="sm" />
                          <span className="font-mono text-[10px] ml-1">{a.priority}</span>
                        </div>
                      ),
                      rounds: <span className="font-mono text-xs">{a.negotiation_rounds}</span>,
                      state: (
                        <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                          a.arbitration_state === 'reconciled' ? 'bg-green-500/10 text-green-500' :
                          a.arbitration_state === 'arbitrating' ? 'bg-yellow-500/10 text-yellow-500' :
                          a.arbitration_state === 'evaluating' ? 'bg-blue-500/10 text-blue-500' :
                          'bg-muted text-muted-foreground'
                        }`}>{a.arbitration_state}</span>
                      ),
                      escalate: a.escalation_required ? (
                        <AlertTriangle className="h-4 w-4 text-red-500" />
                      ) : (
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                      ),
                    }))}
                  />
                </ConsolePanel>

                {/* Resolution Strategies */}
                <div className="grid gap-4 lg:grid-cols-4">
                  <ConsolePanel
                    title="Priority Weighted"
                    icon={<Zap className="h-4 w-4" />}
                    subtitle="Authority-based resolution"
                  >
                    <div className="space-y-2">
                      <div className="text-2xl font-mono font-bold">1247</div>
                      <div className="text-[10px] text-muted-foreground">invocations</div>
                      <div className="pt-2 border-t border-border/30">
                        <div className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground">Success</span>
                          <span className="font-mono text-green-500">94%</span>
                        </div>
                      </div>
                    </div>
                  </ConsolePanel>

                  <ConsolePanel
                    title="Merge"
                    icon={<GitMerge className="h-4 w-4" />}
                    subtitle="Output combination"
                  >
                    <div className="space-y-2">
                      <div className="text-2xl font-mono font-bold">892</div>
                      <div className="text-[10px] text-muted-foreground">invocations</div>
                      <div className="pt-2 border-t border-border/30">
                        <div className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground">Success</span>
                          <span className="font-mono text-green-500">87%</span>
                        </div>
                      </div>
                    </div>
                  </ConsolePanel>

                  <ConsolePanel
                    title="First Claim"
                    icon={<Clock className="h-4 w-4" />}
                    subtitle="First-come resolution"
                  >
                    <div className="space-y-2">
                      <div className="text-2xl font-mono font-bold">456</div>
                      <div className="text-[10px] text-muted-foreground">invocations</div>
                      <div className="pt-2 border-t border-border/30">
                        <div className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground">Success</span>
                          <span className="font-mono text-green-500">99%</span>
                        </div>
                      </div>
                    </div>
                  </ConsolePanel>

                  <ConsolePanel
                    title="Weighted Vote"
                    icon={<Users className="h-4 w-4" />}
                    subtitle="Multi-agent voting"
                  >
                    <div className="space-y-2">
                      <div className="text-2xl font-mono font-bold">234</div>
                      <div className="text-[10px] text-muted-foreground">invocations</div>
                      <div className="pt-2 border-t border-border/30">
                        <div className="flex justify-between text-[10px]">
                          <span className="text-muted-foreground">Success</span>
                          <span className="font-mono text-green-500">91%</span>
                        </div>
                      </div>
                    </div>
                  </ConsolePanel>
                </div>
              </div>
            )}

            {activeTab === 'policies' && (
              <ConsolePanel
                title="Arbitration Policies"
                icon={<BarChart3 className="h-4 w-4" />}
                subtitle="Configured conflict resolution policies"
              >
                <DataTable
                  columns={[
                    { key: 'name', label: 'Policy Name', width: '25%' },
                    { key: 'scope', label: 'Scope', width: '15%' },
                    { key: 'strategy', label: 'Strategy', width: '20%' },
                    { key: 'priority', label: 'Priority', width: '15%' },
                    { key: 'usage', label: 'Usage', width: '15%' },
                    { key: 'active', label: 'Active', width: '10%' },
                  ]}
                  rows={[
                    {
                      name: 'Orchestration Priority',
                      scope: 'orchestration',
                      strategy: 'priority_weighted',
                      priority: '9',
                      usage: '1247',
                      active: <StatusDot status="active" size="sm" />,
                    },
                    {
                      name: 'Semantic Merge',
                      scope: 'semantic',
                      strategy: 'merge',
                      priority: '7',
                      usage: '892',
                      active: <StatusDot status="active" size="sm" />,
                    },
                    {
                      name: 'Quick Resolution',
                      scope: 'execution',
                      strategy: 'first_claim',
                      priority: '5',
                      usage: '456',
                      active: <StatusDot status="active" size="sm" />,
                    },
                  ].map((row, idx) => ({ key: String(idx), ...row }))}
                />
              </ConsolePanel>
            )}

            {activeTab === 'metrics' && (
              <div className="grid gap-4 lg:grid-cols-2">
                <ConsolePanel
                  title="Arbitration Metrics"
                  icon={<Zap className="h-4 w-4" />}
                  subtitle="Resolution performance"
                >
                  <div className="space-y-3">
                    {[
                      { label: 'Avg Resolution Time', value: '124', unit: 'ms', color: 'primary' },
                      { label: 'Escalation Rate', value: '2.3', unit: '%', color: 'warning' },
                      { label: 'Conflict Resolution Rate', value: '97.7', unit: '%', color: 'success' },
                      { label: 'Avg Negotiation Rounds', value: '2.4', unit: '', color: 'primary' },
                    ].map((m) => (
                      <div key={m.label} className="flex items-center justify-between py-2 border-b border-border/30 last:border-0">
                        <span className="text-xs text-muted-foreground">{m.label}</span>
                        <span className="font-mono text-sm">
                          {m.value}<span className="text-muted-foreground text-[10px]">{m.unit}</span>
                        </span>
                      </div>
                    ))}
                  </div>
                </ConsolePanel>

                <ConsolePanel
                  title="Conflict Distribution"
                  icon={<BarChart3 className="h-4 w-4" />}
                  subtitle="By type"
                >
                  <div className="space-y-2">
                    {[
                      { type: 'resource_contention', count: 456, pct: 35 },
                      { type: 'semantic_conflict', count: 312, pct: 24 },
                      { type: 'policy_conflict', count: 234, pct: 18 },
                      { type: 'execution_conflict', count: 189, pct: 14 },
                      { type: 'governance_conflict', count: 112, pct: 9 },
                    ].map((item) => (
                      <div key={item.type} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="font-mono text-muted-foreground">{item.type}</span>
                          <span className="font-mono">{item.count}</span>
                        </div>
                        <ProgressBar value={item.pct} showValue={false} />
                      </div>
                    ))}
                  </div>
                </ConsolePanel>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
