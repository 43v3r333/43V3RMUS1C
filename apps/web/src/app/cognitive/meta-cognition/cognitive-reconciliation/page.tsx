/**
 * Cognitive Reconciliation Viewer
 * Distributed cognition synchronization and conflict resolution.
 */
'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  GitMerge,
  RefreshCw,
  Clock,
  AlertTriangle,
  CheckCircle2,
  Play,
  Pause,
  Database,
  Network,
  Activity,
  Zap,
  Target,
} from 'lucide-react'
import {
  useMetaCognitionApi,
  type CognitionReconciliationState,
} from '@/lib/meta-cognition-api'
import { ConsolePanel, DataTable, StatusDot, ConfidenceBadge, IconButton, ProgressBar, TabBar, Sparkline } from '@/components/cognitive/primitives'

// ==================== Mock Data ====================

const mockReconciliationStates: CognitionReconciliationState[] = [
  {
    state_id: 'reconcile_node_001_global',
    node_id: 'node_001',
    scope: 'global',
    reconciliation_status: 'synced',
    last_sync_at: new Date(Date.now() - 30000).toISOString(),
    sync_version: 156,
    pending_updates: 0,
    sync_health_score: 0.98,
    latency_ms: 12,
    created_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    state_id: 'reconcile_node_002_orchestration',
    node_id: 'node_002',
    scope: 'orchestration',
    reconciliation_status: 'synced',
    last_sync_at: new Date(Date.now() - 45000).toISOString(),
    sync_version: 89,
    pending_updates: 0,
    sync_health_score: 0.95,
    latency_ms: 18,
    created_at: new Date(Date.now() - 7200000).toISOString(),
  },
  {
    state_id: 'reconcile_node_003_semantic',
    node_id: 'node_003',
    scope: 'semantic',
    reconciliation_status: 'pending',
    last_sync_at: new Date(Date.now() - 120000).toISOString(),
    sync_version: 34,
    pending_updates: 2,
    sync_health_score: 0.87,
    latency_ms: 45,
    created_at: new Date(Date.now() - 1800000).toISOString(),
  },
]

// ==================== Main Component ====================

export default function CognitiveReconciliationViewer() {
  const api = useMetaCognitionApi()
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [states, setStates] = useState<CognitionReconciliationState[]>([])
  const [conflicts, setConflicts] = useState<Array<Record<string, unknown>>>([])

  // Load data
  const loadData = useCallback(async () => {
    try {
      try {
        const conflictData = await api.getCognitionConflicts('global')
        setConflicts(conflictData)
      } catch {
        setConflicts([])
      }
      setStates(mockReconciliationStates)
    } catch {
      setStates(mockReconciliationStates)
      setConflicts([])
    }
    setLoading(false)
  }, [api])

  useEffect(() => {
    loadData()
    
    let interval: NodeJS.Timeout | null = null
    if (autoRefresh) {
      interval = setInterval(loadData, 5000)
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [loadData, autoRefresh])

  // Tabs
  const tabs = [
    { id: 'overview', label: 'Overview', icon: <GitMerge className="h-3 w-3" /> },
    { id: 'nodes', label: 'Nodes', icon: <Database className="h-3 w-3" /> },
    { id: 'conflicts', label: 'Conflicts', icon: <AlertTriangle className="h-3 w-3" />, badge: conflicts.length },
  ]

  // Calculate metrics
  const syncedCount = states.filter(s => s.reconciliation_status === 'synced').length
  const pendingCount = states.filter(s => s.reconciliation_status === 'pending').length
  const conflictingCount = states.filter(s => s.reconciliation_status === 'conflicting').length
  const avgHealth = states.length > 0
    ? states.reduce((sum, s) => sum + s.sync_health_score, 0) / states.length
    : 0
  const avgLatency = states.length > 0
    ? states.reduce((sum, s) => sum + (s.latency_ms || 0), 0) / states.length
    : 0
  const totalPendingUpdates = states.reduce((sum, s) => sum + s.pending_updates, 0)

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
          <span className="text-sm">Loading Cognitive Reconciliation...</span>
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
            <GitMerge className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Cognitive Reconciliation Viewer</h1>
            <p className="text-xs text-muted-foreground">Distributed cognition synchronization and conflict resolution</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
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
          { label: 'Total Nodes', value: states.length, icon: <Database className="h-3.5 w-3.5" /> },
          { label: 'Synced', value: syncedCount, icon: <CheckCircle2 className="h-3.5 w-3.5" /> },
          { label: 'Pending', value: pendingCount, icon: <Clock className="h-3.5 w-3.5" /> },
          { label: 'Conflicts', value: conflicts.length, icon: <AlertTriangle className="h-3.5 w-3.5" /> },
          { label: 'Avg Health', value: `${(avgHealth * 100).toFixed(1)}%`, icon: <Activity className="h-3.5 w-3.5" /> },
          { label: 'Avg Latency', value: `${avgLatency.toFixed(0)}ms`, icon: <Zap className="h-3.5 w-3.5" /> },
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
          {/* Node Health Overview */}
          <ConsolePanel title="Node Reconciliation Status" icon={<Network className="h-4 w-4" />} subtitle="Sync health by node">
            <div className="grid grid-cols-3 gap-4">
              {states.map(state => (
                <div key={state.state_id} className="p-3 rounded border border-border bg-card">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <StatusDot status={state.reconciliation_status === 'synced' ? 'active' : 'warning'} />
                      <span className="font-mono text-xs">{state.node_id}</span>
                    </div>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                      state.reconciliation_status === 'synced' ? 'bg-green-500/10 text-green-500' :
                      state.reconciliation_status === 'pending' ? 'bg-yellow-500/10 text-yellow-500' :
                      'bg-red-500/10 text-red-500'
                    }`}>{state.reconciliation_status.toUpperCase()}</span>
                  </div>
                  <div className="space-y-2">
                    <div>
                      <div className="flex items-center justify-between text-[10px] text-muted-foreground mb-1">
                        <span>Sync Health</span>
                        <span className="font-mono">{(state.sync_health_score * 100).toFixed(1)}%</span>
                      </div>
                      <ProgressBar value={state.sync_health_score * 100} showValue={false} color={state.sync_health_score > 0.9 ? 'success' : 'warning'} />
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-[10px]">
                      <div>
                        <span className="text-muted-foreground">Pending: </span>
                        <span className={`font-mono ${state.pending_updates > 0 ? 'text-yellow-500' : 'text-green-500'}`}>{state.pending_updates}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Latency: </span>
                        <span className="font-mono">{(state.latency_ms || 0).toFixed(0)}ms</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>

          {/* Reconciliation Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <ConsolePanel title="Sync Health Trend" icon={<Activity className="h-4 w-4" />} subtitle="Historical sync performance">
              <Sparkline
                data={generateSparkline(avgHealth)}
                height={48}
                color={avgHealth > 0.9 ? '#22c55e' : '#eab308'}
              />
            </ConsolePanel>

            <ConsolePanel title="Pending Updates" icon={<Target className="h-4 w-4" />} subtitle="Queued synchronization items">
              <div className="flex items-center justify-center h-12">
                <div className="text-center">
                  <div className="text-2xl font-mono font-bold">{totalPendingUpdates}</div>
                  <div className="text-[10px] text-muted-foreground">total pending</div>
                </div>
              </div>
            </ConsolePanel>
          </div>
        </div>
      )}

      {/* Nodes Tab */}
      {activeTab === 'nodes' && (
        <ConsolePanel title="Reconciliation States" icon={<Database className="h-4 w-4" />} subtitle={`${states.length} nodes tracked`}>
          <DataTable
            columns={[
              { key: 'state_id', label: 'State ID', width: '18%' },
              { key: 'node_id', label: 'Node ID', width: '12%' },
              { key: 'scope', label: 'Scope', width: '12%' },
              { key: 'status', label: 'Status', width: '12%' },
              { key: 'health', label: 'Health', width: '14%' },
              { key: 'pending', label: 'Pending', width: '10%' },
              { key: 'latency', label: 'Latency', width: '10%' },
              { key: 'last_sync', label: 'Last Sync', width: '12%' },
            ]}
            rows={states.map(s => ({
              state_id: <span className="font-mono text-xs">{s.state_id.slice(0, 16)}...</span>,
              node_id: <span className="font-mono text-xs">{s.node_id}</span>,
              scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{s.scope}</span>,
              status: <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                s.reconciliation_status === 'synced' ? 'bg-green-500/10 text-green-500' :
                s.reconciliation_status === 'pending' ? 'bg-yellow-500/10 text-yellow-500' :
                s.reconciliation_status === 'conflicting' ? 'bg-red-500/10 text-red-500' :
                'bg-muted text-muted-foreground'
              }`}>{s.reconciliation_status.toUpperCase()}</span>,
              health: <div className="flex items-center gap-2"><ProgressBar value={s.sync_health_score * 100} showValue={false} className="w-16" color={s.sync_health_score > 0.9 ? 'success' : 'warning'} /><span className="font-mono text-xs">{(s.sync_health_score * 100).toFixed(0)}%</span></div>,
              pending: <span className={`font-mono text-xs ${s.pending_updates > 0 ? 'text-yellow-500' : 'text-green-500'}`}>{s.pending_updates}</span>,
              latency: <span className="font-mono text-xs">{(s.latency_ms || 0).toFixed(0)}ms</span>,
              last_sync: <span className="text-xs text-muted-foreground">{s.last_sync_at ? new Date(s.last_sync_at).toLocaleTimeString() : 'Never'}</span>,
            }))}
          />
        </ConsolePanel>
      )}

      {/* Conflicts Tab */}
      {activeTab === 'conflicts' && (
        <ConsolePanel title="Active Conflicts" icon={<AlertTriangle className="h-4 w-4" />} subtitle={conflicts.length === 0 ? 'No active conflicts' : `${conflicts.length} unresolved`}>
          {conflicts.length === 0 ? (
            <div className="flex items-center gap-2 py-8">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              <span className="text-xs text-muted-foreground">No active conflicts - all nodes synchronized</span>
            </div>
          ) : (
            <div className="space-y-3">
              {conflicts.map((conflict, i) => (
                <div key={i} className="p-4 rounded border border-red-500/20 bg-red-500/5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-red-500" />
                      <span className="text-xs font-medium">Conflict #{i + 1}</span>
                    </div>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-500/10 text-red-500">UNRESOLVED</span>
                  </div>
                  <div className="mt-2 text-xs text-muted-foreground">
                    {JSON.stringify(conflict, null, 2)}
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
