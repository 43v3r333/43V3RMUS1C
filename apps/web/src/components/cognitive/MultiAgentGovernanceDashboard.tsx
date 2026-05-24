"""
Multi-Agent Governance Dashboard - Agent authority and arbitration interface.
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Shield,
  Server,
  Users,
  AlertTriangle,
  CheckCircle2,
  GitBranch,
  Activity,
  Scale,
  Lock,
  Eye,
  Cpu,
} from 'lucide-react'
import { useCognitiveApi, type GovernanceRule, type ConflictResolution } from '@/lib/cognitive-api'
import { ConsolePanel, DataTable, MetricGrid, StatusDot, ConfidenceBadge, IconButton, ProgressBar, TabBar } from './primitives'

interface AgentHealthData {
  id: string
  kind: string
  status: string
  authority_level: number
  tasks_completed: number
  tasks_failed: number
  current_load: number
}

interface AuthorityHierarchyData {
  agent_kind: string
  role_name: string
  level: number
  can_delegate: boolean
  can_escalate: boolean
}

export default function MultiAgentGovernanceDashboard() {
  const api = useCognitiveApi()
  const [activeTab, setActiveTab] = useState('overview')
  const [rules, setRules] = useState<GovernanceRule[]>([])
  const [conflicts, setConflicts] = useState<ConflictResolution[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const r = await api.listGovernanceRules().catch(() => [])
        const c = await api.listActiveConflicts().catch(() => [])
        setRules(r)
        setConflicts(c)
      } catch {
        setRules([
          { id: 'r1', name: 'deny_high_frequency', rule_type: 'rate_limit', conditions: { action_types: ['execute'] }, action: 'deny', agent_kind: 'generator', priority: 10, is_active: true, trigger_count: 23, success_count: 20, failure_count: 3, version: 1, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
          { id: 'r2', name: 'escalate_resource_request', rule_type: 'resource_check', conditions: { params: { memory: { min: 4096 } } }, action: 'escalate', agent_kind: null, priority: 5, is_active: true, trigger_count: 12, success_count: 12, failure_count: 0, version: 2, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
          { id: 'r3', name: 'allow_readonly', rule_type: 'permission', conditions: { action_types: ['read', 'query'] }, action: 'allow', agent_kind: null, priority: 1, is_active: true, trigger_count: 1523, success_count: 1523, failure_count: 0, version: 1, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
        ])
        setConflicts([])
      }
      setLoading(false)
    }
    load()
  }, [api])

  const agentHealth: AgentHealthData[] = [
    { id: 'agent-1', kind: 'orchestrator', status: 'active', authority_level: 20, tasks_completed: 342, tasks_failed: 3, current_load: 0.78 },
    { id: 'agent-2', kind: 'generator', status: 'active', authority_level: 10, tasks_completed: 891, tasks_failed: 12, current_load: 0.65 },
    { id: 'agent-3', kind: 'optimizer', status: 'idle', authority_level: 10, tasks_completed: 234, tasks_failed: 1, current_load: 0.22 },
    { id: 'agent-4', kind: 'analyzer', status: 'active', authority_level: 10, tasks_completed: 567, tasks_failed: 5, current_load: 0.91 },
    { id: 'agent-5', kind: 'scheduler', status: 'active', authority_level: 20, tasks_completed: 156, tasks_failed: 0, current_load: 0.44 },
  ]

  const hierarchy: AuthorityHierarchyData[] = [
    { agent_kind: 'orchestrator', role_name: 'coordinator', level: 20, can_delegate: true, can_escalate: true },
    { agent_kind: 'scheduler', role_name: 'coordinator', level: 20, can_delegate: true, can_escalate: true },
    { agent_kind: 'generator', role_name: 'executor', level: 10, can_delegate: false, can_escalate: true },
    { agent_kind: 'optimizer', role_name: 'executor', level: 10, can_delegate: false, can_escalate: true },
    { agent_kind: 'analyzer', role_name: 'executor', level: 10, can_delegate: false, can_escalate: true },
    { agent_kind: 'monitor', role_name: 'observer', level: 0, can_delegate: false, can_escalate: false },
  ]

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Shield className="h-3 w-3" /> },
    { id: 'agents', label: 'Agents', icon: <Server className="h-3 w-3" />, badge: agentHealth.filter(a => a.status === 'active').length },
    { id: 'rules', label: 'Rules', icon: <Lock className="h-3 w-3" />, badge: rules.length },
    { id: 'conflicts', label: 'Conflicts', icon: <AlertTriangle className="h-3 w-3" />, badge: conflicts.length },
    { id: 'hierarchy', label: 'Authority', icon: <Scale className="h-3 w-3" /> },
  ]

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 border border-primary/20">
            <Shield className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Multi-Agent Governance Dashboard</h1>
            <p className="text-xs text-muted-foreground">Agent authority hierarchy and orchestration arbitration</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs">
            <StatusDot status={conflicts.length === 0 ? 'active' : 'warning'} />
            <span>{conflicts.length === 0 ? 'No active conflicts' : `${conflicts.length} active conflicts`}</span>
          </div>
          <IconButton icon={<Scale className="h-3.5 w-3.5" />} title="View policies" />
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-6 gap-2">
        {[
          { label: 'Active Agents', value: agentHealth.filter(a => a.status === 'active').length, icon: <Server className="h-3.5 w-3.5" /> },
          { label: 'Total Tasks', value: agentHealth.reduce((s, a) => s + a.tasks_completed, 0), icon: <Activity className="h-3.5 w-3.5" /> },
          { label: 'Failed', value: agentHealth.reduce((s, a) => s + a.tasks_failed, 0), icon: <AlertTriangle className="h-3.5 w-3.5" /> },
          { label: 'Active Rules', value: rules.filter(r => r.is_active).length, icon: <Lock className="h-3.5 w-3.5" /> },
          { label: 'Triggers', value: rules.reduce((s, r) => s + r.trigger_count, 0), icon: <Cpu className="h-3.5 w-3.5" /> },
          { label: 'Authority Levels', value: new Set(hierarchy.map(h => h.level)).size, icon: <Scale className="h-3.5 w-3.5" /> },
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

      {activeTab === 'overview' && (
        <div className="grid gap-4 lg:grid-cols-3">
          {/* Agent Health */}
          <ConsolePanel title="Agent Health" icon={<Server className="h-4 w-4" />} subtitle="Current agent status">
            <div className="space-y-2">
              {agentHealth.map(a => (
                <div key={a.id} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                  <div className="flex items-center gap-2">
                    <StatusDot status={a.status as 'active' | 'idle'} size="sm" />
                    <div>
                      <span className="text-xs font-mono">{a.kind}</span>
                      <div className="text-[10px] text-muted-foreground">level {a.authority_level}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-xs font-mono">{a.tasks_completed}/{a.tasks_completed + a.tasks_failed}</div>
                      <div className="text-[10px] text-muted-foreground">tasks</div>
                    </div>
                    <div className="w-16">
                      <ProgressBar value={a.current_load * 100} color={a.current_load > 0.9 ? 'error' : a.current_load > 0.7 ? 'warning' : 'success'} showValue={false} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>

          {/* Rule Performance */}
          <ConsolePanel title="Rule Performance" icon={<Lock className="h-4 w-4" />} subtitle="Governance rule trigger stats">
            <div className="space-y-2">
              {rules.slice(0, 5).map(r => (
                <div key={r.id} className="py-2 border-b border-border/50 last:border-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-mono">{r.name}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${r.is_active ? 'bg-green-500/10 text-green-500' : 'bg-muted text-muted-foreground'}`}>{r.is_active ? 'ACTIVE' : 'INACTIVE'}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-[10px] text-muted-foreground">
                    <span>triggers: {r.trigger_count}</span>
                    <span>success: {r.success_count}</span>
                    <span>fail: {r.failure_count}</span>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>

          {/* Authority Chain */}
          <ConsolePanel title="Authority Levels" icon={<Scale className="h-4 w-4" />} subtitle="Agent hierarchy by authority">
            <div className="space-y-2">
              {[...new Set(hierarchy.map(h => h.level))].sort((a, b) => b - a).map(level => {
                const agents = hierarchy.filter(h => h.level === level)
                return (
                  <div key={level} className="flex items-center gap-3 py-2 border-b border-border/50 last:border-0">
                    <div className="flex h-6 w-6 items-center justify-center rounded border border-border bg-muted text-xs font-mono">{level}</div>
                    <div className="flex-1">
                      <div className="flex gap-1.5 flex-wrap">
                        {agents.map(a => (
                          <span key={a.agent_kind} className="text-[10px] px-1.5 py-0.5 rounded bg-secondary">{a.agent_kind}</span>
                        ))}
                      </div>
                    </div>
                    {agents[0]?.can_delegate && (
                      <span className="text-[9px] text-muted-foreground">CAN DELEGATE</span>
                    )}
                  </div>
                )
              })}
            </div>
          </ConsolePanel>

          {/* Conflict Resolution Stats */}
          <ConsolePanel title="Conflict Resolution" icon={<AlertTriangle className="h-4 w-4" />} subtitle="Resolution strategy usage">
            <div className="space-y-3">
              {[
                { strategy: 'priority', count: 45 },
                { strategy: 'weighted_vote', count: 23 },
                { strategy: 'first_commit', count: 12 },
                { strategy: 'mediated', count: 3 },
                { strategy: 'merge', count: 8 },
              ].map(s => (
                <div key={s.strategy} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-mono text-muted-foreground">{s.strategy}</span>
                    <span className="font-mono">{s.count}</span>
                  </div>
                  <ProgressBar value={(s.count / 91) * 100} showValue={false} />
                </div>
              ))}
            </div>
          </ConsolePanel>

          {/* Violations */}
          <ConsolePanel title="Recent Violations" icon={<Lock className="h-4 w-4" />} subtitle="Policy violation log">
            <div className="space-y-2">
              {[
                { rule: 'deny_high_frequency', agent: 'agent-2', severity: 'warning', time: '2m ago' },
                { rule: 'resource_check', agent: 'agent-4', severity: 'info', time: '15m ago' },
              ].map((v, i) => (
                <div key={i} className="flex items-center justify-between py-1.5 border-b border-border/50 last:border-0">
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] px-1 py-0.5 rounded ${
                      v.severity === 'warning' ? 'bg-yellow-500/10 text-yellow-500' : 'bg-blue-500/10 text-blue-500'
                    }`}>{v.severity}</span>
                    <span className="text-xs text-muted-foreground">{v.rule}</span>
                  </div>
                  <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                    <span>{v.agent}</span>
                    <span>{v.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>

          {/* Escalation Path */}
          <ConsolePanel title="Escalation Path" icon={<GitBranch className="h-4 w-4" />} subtitle="Authority escalation chain">
            <div className="space-y-1.5">
              {hierarchy.filter(h => h.can_escalate).slice(0, 5).map(h => (
                <div key={h.agent_kind} className="flex items-center gap-2 py-1">
                  <span className="text-xs font-mono">{h.agent_kind}</span>
                  <span className="text-muted-foreground">→</span>
                  <span className="text-xs text-primary">escalates to parent</span>
                </div>
              ))}
            </div>
          </ConsolePanel>
        </div>
      )}

      {activeTab === 'agents' && (
        <ConsolePanel title="Agent Registry" icon={<Server className="h-4 w-4" />} subtitle={`${agentHealth.length} registered agents`}>
          <DataTable
            columns={[
              { key: 'id', label: 'Agent ID', width: '15%' },
              { key: 'kind', label: 'Kind', width: '15%' },
              { key: 'status', label: 'Status', width: '12%' },
              { key: 'authority', label: 'Authority Level', width: '15%' },
              { key: 'tasks', label: 'Tasks', width: '15%' },
              { key: 'load', label: 'Load', width: '18%' },
              { key: 'health', label: 'Health', width: '10%' },
            ]}
            rows={agentHealth.map(a => ({
              id: <span className="font-mono text-xs">{a.id}</span>,
              kind: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{a.kind}</span>,
              status: <StatusDot status={a.status as 'active' | 'idle'} size="sm" />,
              authority: <span className="font-mono text-xs">{a.authority_level}</span>,
              tasks: <span className="font-mono text-xs">{a.tasks_completed}/{a.tasks_failed}</span>,
              load: <div className="w-20"><ProgressBar value={a.current_load * 100} showValue /></div>,
              health: <span className={`text-[10px] ${a.tasks_failed / (a.tasks_completed + a.tasks_failed) < 0.02 ? 'text-green-500' : 'text-yellow-500'}`}>
                {((a.tasks_completed / (a.tasks_completed + a.tasks_failed)) * 100).toFixed(0)}%
              </span>,
            }))}
          />
        </ConsolePanel>
      )}

      {activeTab === 'rules' && (
        <ConsolePanel title="Governance Rules" icon={<Lock className="h-4 w-4" />} subtitle={`${rules.length} configured rules`}>
          <DataTable
            columns={[
              { key: 'name', label: 'Name', width: '22%' },
              { key: 'type', label: 'Rule Type', width: '15%' },
              { key: 'action', label: 'Action', width: '10%' },
              { key: 'agent', label: 'Agent Kind', width: '12%' },
              { key: 'priority', label: 'Priority', width: '10%' },
              { key: 'triggers', label: 'Triggers', width: '10%' },
              { key: 'success', label: 'Success', width: '11%' },
              { key: 'status', label: 'Status', width: '10%' },
            ]}
            rows={rules.map(r => ({
              name: <span className="font-mono text-xs">{r.name}</span>,
              type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{r.rule_type}</span>,
              action: <span className={`text-xs font-medium ${r.action === 'allow' ? 'text-green-500' : r.action === 'deny' ? 'text-red-500' : 'text-yellow-500'}`}>{r.action.toUpperCase()}</span>,
              agent: <span className="text-xs text-muted-foreground">{r.agent_kind || 'ALL'}</span>,
              priority: <span className="font-mono text-xs">{r.priority}</span>,
              triggers: <span className="font-mono text-xs">{r.trigger_count}</span>,
              success: <span className="font-mono text-xs text-green-500">{r.success_count}</span>,
              status: r.is_active ? <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/10 text-green-500">ACTIVE</span> : <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">INACTIVE</span>,
            }))}
          />
        </ConsolePanel>
      )}

      {activeTab === 'conflicts' && (
        <ConsolePanel title="Active Conflicts" icon={<AlertTriangle className="h-4 w-4" />} subtitle={conflicts.length === 0 ? 'No active conflicts' : `${conflicts.length} unresolved`}>
          {conflicts.length === 0 ? (
            <div className="flex items-center gap-2 py-8">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              <span className="text-xs text-muted-foreground">No active conflicts - all agents operating within governance rules</span>
            </div>
          ) : (
            <DataTable
              columns={[
                { key: 'id', label: 'Conflict ID', width: '20%' },
                { key: 'domain', label: 'Domain', width: '15%' },
                { key: 'agents', label: 'Agents', width: '20%' },
                { key: 'strategy', label: 'Strategy', width: '15%' },
                { key: 'outcome', label: 'Outcome', width: '15%' },
                { key: 'detected', label: 'Detected', width: '15%' },
              ]}
              rows={conflicts.map(c => ({
                id: <span className="font-mono text-xs">{c.conflict_id}</span>,
                domain: <span className="text-xs">{c.domain}</span>,
                agents: <span className="text-xs font-mono">{c.agent_ids.join(', ')}</span>,
                strategy: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{c.strategy_used}</span>,
                outcome: <span className="text-xs">{c.resolution_outcome}</span>,
                detected: <span className="text-xs text-muted-foreground">{new Date(c.detected_at).toLocaleTimeString()}</span>,
              }))}
            />
          )}
        </ConsolePanel>
      )}

      {activeTab === 'hierarchy' && (
        <div className="grid gap-4 lg:grid-cols-2">
          <ConsolePanel title="Authority Hierarchy" icon={<Scale className="h-4 w-4" />} subtitle="Role-based authority levels">
            <DataTable
              columns={[
                { key: 'kind', label: 'Agent Kind', width: '25%' },
                { key: 'role', label: 'Role', width: '20%' },
                { key: 'level', label: 'Level', width: '15%' },
                { key: 'delegate', label: 'Can Delegate', width: '20%' },
                { key: 'escalate', label: 'Can Escalate', width: '20%' },
              ]}
              rows={hierarchy.map(h => ({
                kind: <span className="font-mono text-xs">{h.agent_kind}</span>,
                role: <span className="text-xs">{h.role_name}</span>,
                level: <span className="font-mono text-xs">{h.level}</span>,
                delegate: h.can_delegate ? <CheckCircle2 className="h-3.5 w-3.5 text-green-500" /> : <span className="text-muted-foreground">—</span>,
                escalate: h.can_escalate ? <CheckCircle2 className="h-3.5 w-3.5 text-green-500" /> : <span className="text-muted-foreground">—</span>,
              }))}
            />
          </ConsolePanel>

          <ConsolePanel title="Arbitration Policies" icon={<Activity className="h-4 w-4" />} subtitle="Conflict resolution strategies by domain">
            <div className="space-y-3">
              {[
                { domain: 'render', strategy: 'priority', threshold: 3 },
                { domain: 'generation', strategy: 'weighted_vote', threshold: 5 },
                { domain: 'composition', strategy: 'first_commit', threshold: 2 },
                { domain: 'storage', strategy: 'priority', threshold: 3 },
                { domain: 'scheduling', strategy: 'round_robin', threshold: 4 },
              ].map(p => (
                <div key={p.domain} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                  <div>
                    <span className="text-xs font-mono">{p.domain}</span>
                    <div className="text-[10px] text-muted-foreground mt-0.5">threshold: {p.threshold}</div>
                  </div>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted font-mono">{p.strategy}</span>
                </div>
              ))}
            </div>
          </ConsolePanel>
        </div>
      )}
    </div>
  )
}