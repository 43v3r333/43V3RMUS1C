/**
 * 43V3R CORE - Semantic Recovery Monitor
 * 
 * Production-grade semantic self-healing and reconciliation interface.
 * Orchestration recovery, conflict resolution, and adaptive stabilization.
 */
'use client'

import { useState, useEffect } from 'react'
import {
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Activity,
  Shield,
  GitBranch,
  Clock,
  Zap,
  Warning,
  XCircle,
  Play,
  Pause,
  Settings,
  Database,
  Network,
  Target,
  TrendingUp,
} from 'lucide-react'
import { ConsolePanel, MetricGrid, MetricValue, StatusDot, DataTable, TabBar, IconButton, ProgressBar, ConfidenceBadge } from '@/components/cognitive/primitives'

// ---- Types ----

interface RecoveryMetrics {
  activeConflicts: number
  resolvedConflicts: number
  recoveryActions: number
  stabilizationLoops: number
  avgRecoveryTime: number
  recoveryRate: number
}

interface SemanticConflict {
  conflict_id: string
  conflict_type: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  entity_type: string
  entity_id: string
  description: string
  divergence_score: number
  state: 'idle' | 'detecting' | 'diagnosing' | 'reconciling' | 'verifying' | 'completed' | 'failed'
  is_resolved: boolean
  detected_at: string
  resolved_at?: string
}

interface RecoveryAction {
  action_id: string
  action_type: string
  target_entity_id: string
  target_entity_type: string
  state: string
  attempts: number
  success: boolean
  created_at: string
  completed_at?: string
  error_message?: string
}

interface StabilizationLoop {
  loop_id: string
  loop_type: string
  target_entity_id: string
  target_metric: string
  target_threshold: number
  current_value: number
  state: string
  iteration_count: number
  max_iterations: number
}

// ---- Mock Data Generators ----

function generateMockConflicts(): SemanticConflict[] {
  return [
    { conflict_id: 'cf1', conflict_type: 'semantic_drift', severity: 'warning', entity_type: 'workflow', entity_id: 'wf-alpha-42', description: 'Semantic keys updated in workflow execution', divergence_score: 0.15, state: 'completed', is_resolved: true, detected_at: new Date(Date.now() - 3600000).toISOString(), resolved_at: new Date(Date.now() - 3500000).toISOString() },
    { conflict_id: 'cf2', conflict_type: 'interpretation_mismatch', severity: 'error', entity_type: 'execution', entity_id: 'exec-bridge-17', description: 'Interpretation conflict between nodes', divergence_score: 0.35, state: 'reconciling', is_resolved: false, detected_at: new Date(Date.now() - 1800000).toISOString() },
    { conflict_id: 'cf3', conflict_type: 'consistency_breach', severity: 'warning', entity_type: 'cognition', entity_id: 'cog-state-8', description: 'Cognition consistency score below threshold', divergence_score: 0.22, state: 'verifying', is_resolved: false, detected_at: new Date(Date.now() - 900000).toISOString() },
    { conflict_id: 'cf4', conflict_type: 'contract_violation', severity: 'critical', entity_type: 'semantic', entity_id: 'sem-contract-3', description: 'Contract validation failed', divergence_score: 0.55, state: 'diagnosing', is_resolved: false, detected_at: new Date(Date.now() - 600000).toISOString() },
    { conflict_id: 'cf5', conflict_type: 'dependency_cycle', severity: 'error', entity_type: 'workflow', entity_id: 'wf-composite-9', description: 'Circular dependency detected', divergence_score: 0.40, state: 'completed', is_resolved: true, detected_at: new Date(Date.now() - 7200000).toISOString(), resolved_at: new Date(Date.now() - 7100000).toISOString() },
  ]
}

function generateMockActions(): RecoveryAction[] {
  return [
    { action_id: 'ra1', action_type: 'realign', target_entity_id: 'exec-bridge-17', target_entity_type: 'execution', state: 'completed', attempts: 1, success: true, created_at: new Date(Date.now() - 1200000).toISOString(), completed_at: new Date(Date.now() - 1190000).toISOString() },
    { action_id: 'ra2', action_type: 'propagate', target_entity_id: 'cog-state-8', target_entity_type: 'cognition', state: 'reconciling', attempts: 2, success: false, created_at: new Date(Date.now() - 600000).toISOString() },
    { action_id: 'ra3', action_type: 'rollback', target_entity_id: 'wf-alpha-42', target_entity_type: 'workflow', state: 'completed', attempts: 1, success: true, created_at: new Date(Date.now() - 4000000).toISOString(), completed_at: new Date(Date.now() - 3950000).toISOString() },
    { action_id: 'ra4', action_type: 'merge', target_entity_id: 'sem-contract-3', target_entity_type: 'semantic', state: 'idle', attempts: 0, success: false, created_at: new Date(Date.now() - 300000).toISOString() },
  ]
}

function generateMockLoops(): StabilizationLoop[] {
  return [
    { loop_id: 'sl1', loop_type: 'adaptive', target_entity_id: 'cog-state-8', target_metric: 'alignment_score', target_threshold: 0.90, current_value: 0.72, state: 'running', iteration_count: 4, max_iterations: 10 },
    { loop_id: 'sl2', loop_type: 'predictive', target_entity_id: 'exec-bridge-17', target_metric: 'consistency_score', target_threshold: 0.85, current_value: 0.88, state: 'completed', iteration_count: 6, max_iterations: 6 },
    { loop_id: 'sl3', loop_type: 'active', target_entity_id: 'wf-composite-9', target_metric: 'dependency_validity', target_threshold: 0.95, current_value: 0.95, state: 'running', iteration_count: 8, max_iterations: 10 },
    { loop_id: 'sl4', loop_type: 'passive', target_entity_id: 'sem-contract-3', target_metric: 'validation_score', target_threshold: 0.80, current_value: 0.65, state: 'running', iteration_count: 2, max_iterations: 15 },
  ]
}

// ---- Main Component ----

export default function SemanticRecoveryMonitor() {
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [metrics, setMetrics] = useState<RecoveryMetrics>({
    activeConflicts: 0, resolvedConflicts: 0, recoveryActions: 0, stabilizationLoops: 0, avgRecoveryTime: 0, recoveryRate!: 0.0,
  })
  const [conflicts, setConflicts] = useState<SemanticConflict[]>([])
  const [actions, setActions] = useState<RecoveryAction[]>([])
  const [loops, setLoops] = useState<StabilizationLoop[]>([])
  const [autoRefresh, setAutoRefresh] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        const mockConflicts = generateMockConflicts()
        const mockActions = generateMockActions()
        const mockLoops = generateMockLoops()

        const activeCount = mockConflicts.filter(c => !c.is_resolved).length
        const resolvedCount = mockConflicts.filter(c => c.is_resolved).length
        const recoveryRate = resolvedCount / (mockConflicts.length || 1)
        const avgTime = 2.5 // minutes

        setMetrics({
          activeConflicts: activeCount,
          resolvedConflicts: resolvedCount,
          recoveryActions: mockActions.filter(a => a.success).length,
          stabilizationLoops: mockLoops.filter(l => l.state === 'running').length,
          avgRecoveryTime: avgTime,
          recoveryRate: recoveryRate,
        })

        setConflicts(mockConflicts)
        setActions(mockActions)
        setLoops(mockLoops)
      } catch {
        // Use defaults
      }
      setLoading(false)
    }

    loadData()

    if (autoRefresh) {
      const interval = setInterval(loadData, 30000)
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Shield className="h-3 w-3" /> },
    { id: 'conflicts', label: 'Conflicts', icon: <AlertTriangle className="h-3 w-3" />, badge: metrics.activeConflicts },
    { id: 'actions', label: 'Actions', icon: <Zap className="h-3 w-3" />, badge: actions.filter(a => a.state === 'reconciling').length },
    { id: 'stabilization', label: 'Stabilization', icon: <Activity className="h-3 w-3" />, badge: metrics.stabilizationLoops },
  ]

  const getSeverityColor = (severity: string) => {
    if (severity === 'critical') return 'text-red-500 bg-red-500/10'
    if (severity === 'error') return 'text-orange-500 bg-orange-500/10'
    if (severity === 'warning') return 'text-yellow-500 bg-yellow-500/10'
    return 'text-blue-500 bg-blue-500/10'
  }

  const getStateColor = (state: string) => {
    if (state === 'completed') return 'text-green-500'
    if (state === 'reconciling' || state === 'verifying') return 'text-blue-500'
    if (state === 'failed') return 'text-red-500'
    return 'text-muted-foreground'
  }

  const getActionIcon = (type: string) => {
    const icons: Record<string, React.ReactNode> = {
      realign: <GitBranch className="h-3 w-3" />,
      propagate: <Network className="h-3 w-3" />,
      rollback: <RefreshCw className="h-3 w-3" />,
      merge: <Target className="h-3 w-3" />,
    }
    return icons[type] || <Zap className="h-3 w-3" />
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            <span className="font-mono text-sm font-semibold tracking-tight">SEMANTIC RECOVERY</span>
          </div>
          <div className="h-4 w-px bg-border/50" />
          <StatusDot status={metrics.activeConflicts > 0 ? 'warning' : 'active'} size="sm" />
          <span className="text-[10px] font-mono text-muted-foreground uppercase">
            {metrics.activeConflicts} active
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center gap-1.5 h-7 px-2 text-[10px] rounded border transition-colors ${autoRefresh ? 'bg-primary/10 text-primary border-primary/30' : 'border-border text-muted-foreground'}`}
          >
            {autoRefresh ? <Play className="h-3 w-3" /> : <Pause className="h-3 w-3" />}
            AUTO
          </button>
          <IconButton icon={<RefreshCw className="h-3 w-3" />} onClick={() => setLoading(true)} />
        </div>
      </div>

      {/* Metrics Bar */}
      <div className="border-b border-border/50 bg-muted/20 px-4 py-2">
        <MetricGrid columns={6}>
          <MetricValue
            label="Active Conflicts"
            value={metrics.activeConflicts}
            icon={<AlertTriangle className="h-3 w-3" />}
            trend={metrics.activeConflicts > 2 ? 'up' : 'stable'}
          />
          <MetricValue
            label="Resolved"
            value={metrics.resolvedConflicts}
            icon={<CheckCircle2 className="h-3 w-3" />}
            trend="up"
          />
          <MetricValue
            label="Recovery Actions"
            value={metrics.recoveryActions}
            icon={<Zap className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Stabilization Loops"
            value={metrics.stabilizationLoops}
            icon={<Activity className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Avg Recovery Time"
            value={metrics.avgRecoveryTime}
            unit="min"
            icon={<Clock className="h-3 w-3" />}
            trend="down"
          />
          <MetricValue
            label="Recovery Rate"
            value={`${(metrics.recoveryRate * 100).toFixed(0)}%`}
            icon={<TrendingUp className="h-3 w-3" />}
            trend={metrics.recoveryRate > 0.8 ? 'up' : 'stable'}
            confidence={metrics.recoveryRate}
          />
        </MetricGrid>
      </div>

      {/* Tabs */}
      <TabBar tabs={tabs} active={activeTab} onChange={setActiveTab} />

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {activeTab === 'overview' && (
          <div className="grid gap-4 lg:grid-cols-2">
            <ConsolePanel title="Active Conflicts" icon={<AlertTriangle className="h-4 w-4" />} subtitle="Requires attention" status={metrics.activeConflicts > 0 ? 'warning' : 'nominal'}>
              <div className="space-y-2">
                {conflicts.filter(c => !c.is_resolved).map(conflict => (
                  <div key={conflict.conflict_id} className="flex items-center justify-between p-2 rounded border border-border/50">
                    <div className="flex items-center gap-2">
                      <span className={`text-[10px] px-1.5 py-0.5 rounded ${getSeverityColor(conflict.severity)}`}>
                        {conflict.severity.toUpperCase()}
                      </span>
                      <div>
                        <span className="text-xs font-medium">{conflict.conflict_type.replace(/_/g, ' ')}</span>
                        <div className="text-[10px] text-muted-foreground">{conflict.entity_type}: {conflict.entity_id}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`text-[10px] ${getStateColor(conflict.state)}`}>{conflict.state}</span>
                      <div className="text-[10px] text-muted-foreground">
                        {((Date.now() - new Date(conflict.detected_at).getTime()) / 60000).toFixed(0)}m ago
                      </div>
                    </div>
                  </div>
                ))}
                {conflicts.filter(c => !c.is_resolved).length === 0 && (
                  <div className="text-center py-4 text-muted-foreground text-sm">
                    <CheckCircle2 className="h-8 w-8 mx-auto mb-2 text-green-500" />
                    All conflicts resolved
                  </div>
                )}
              </div>
            </ConsolePanel>

            <ConsolePanel title="Stabilization Loops" icon={<Activity className="h-4 w-4" />} subtitle="Active stabilization">
              <div className="space-y-3">
                {loops.filter(l => l.state === 'running').map(loop => (
                  <div key={loop.loop_id} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-mono text-muted-foreground">{loop.target_entity_id}</span>
                      <span className="font-mono">{loop.current_value.toFixed(2)}/ {loop.target_threshold}</span>
                    </div>
                    <ProgressBar 
                      value={(loop.current_value / loop.target_threshold) * 100} 
                      showValue={false}
                      color={loop.current_value >= loop.target_threshold ? 'success' : 'warning'} 
                    />
                    <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                      <span>{loop.target_metric}</span>
                      <span>{loop.iteration_count}/{loop.max_iterations}</span>
                    </div>
                  </div>
                ))}
              </div>
            </ConsolePanel>

            <ConsolePanel title="Recent Recovery Actions" icon={<Zap className="h-4 w-4" />} subtitle="Action history">
              <DataTable
                columns={[
                  { key: 'type', label: 'Type', width: '20%' },
                  { key: 'target', label: 'Target', width: '30%' },
                  { key: 'state', label: 'State', width: '25%' },
                  { key: 'attempts', label: 'Attempts', width: '25%' },
                ]}
                rows={actions.slice(0, 5).map(a => ({
                  type: (
                    <div className="flex items-center gap-1">
                      {getActionIcon(a.action_type)}
                      <span className="text-xs">{a.action_type}</span>
                    </div>
                  ),
                  target: <span className="font-mono text-xs truncate block max-w-[100px]">{a.target_entity_id}</span>,
                  state: <span className={`text-[10px] ${getStateColor(a.state)}`}>{a.state}</span>,
                  attempts: <span className="font-mono text-xs">{a.attempts}</span>,
                }))}
              />
            </ConsolePanel>

            <ConsolePanel title="Recovery Metrics" icon={<TrendingUp className="h-4 w-4" />} subtitle="Performance tracking">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Success Rate</span>
                  <span className="font-mono text-green-500">{Math.round(metrics.recoveryRate * 100)}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Avg Recovery Time</span>
                  <span className="font-mono">{metrics.avgRecoveryTime}m</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Active Stabilization</span>
                  <span className="font-mono">{metrics.stabilizationLoops}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Actions / Conflict</span>
                  <span className="font-mono">{actions.length}/{conflicts.length}</span>
                </div>
              </div>
            </ConsolePanel>
          </div>
        )}

        {activeTab === 'conflicts' && (
          <ConsolePanel title="Conflict Registry" icon={<AlertTriangle className="h-4 w-4" />} subtitle={`${conflicts.length} total, ${metrics.activeConflicts} active`}>
            <DataTable
              columns={[
                { key: 'severity', label: 'Severity', width: '15%' },
                { key: 'type', label: 'Type', width: '20%' },
                { key: 'entity', label: 'Entity', width: '20%' },
                { key: 'divergence', label: 'Divergence', width: '15%' },
                { key: 'state', label: 'State', width: '15%' },
                { key: 'detected', label: 'Detected', width: '15%' },
              ]}
              rows={conflicts.map(c => ({
                severity: <span className={`text-[10px] px-1.5 py-0.5 rounded ${getSeverityColor(c.severity)}`}>{c.severity.toUpperCase()}</span>,
                type: <span className="text-xs font-mono">{c.conflict_type.replace(/_/g, ' ')}</span>,
                entity: (
                  <div>
                    <span className="text-[10px] text-muted-foreground">{c.entity_type}</span>
                    <div className="font-mono text-xs">{c.entity_id}</div>
                  </div>
                ),
                divergence: <ProgressBar value={c.divergence_score * 100} showValue color={c.divergence_score > 0.4 ? 'error' : c.divergence_score > 0.2 ? 'warning' : 'primary'} />,
                state: <span className={`text-[10px] ${getStateColor(c.state)}`}>{c.state}</span>,
                detected: <span className="text-[10px] text-muted-foreground">{new Date(c.detected_at).toLocaleTimeString()}</span>,
              }))}
            />
          </ConsolePanel>
        )}

        {activeTab === 'actions' && (
          <ConsolePanel title="Recovery Actions" icon={<Zap className="h-4 w-4" />} subtitle={`${actions.filter(a => a.success).length} successful`}>
            <DataTable
              columns={[
                { key: 'type', label: 'Type', width: '15%' },
                { key: 'target', label: 'Target', width: '20%' },
                { key: 'state', label: 'State', width: '15%' },
                { key: 'attempts', label: 'Attempts', width: '15%' },
                { key: 'result', label: 'Result', width: '15%' },
                { key: 'created', label: 'Created', width: '20%' },
              ]}
              rows={actions.map(a => ({
                type: (
                  <div className="flex items-center gap-1">
                    {getActionIcon(a.action_type)}
                    <span className="text-xs">{a.action_type}</span>
                  </div>
                ),
                target: <span className="font-mono text-xs truncate block max-w-[100px]">{a.target_entity_id}</span>,
                state: <span className={`text-xs ${getStateColor(a.state)}`}>{a.state}</span>,
                attempts: <span className="font-mono text-xs">{a.attempts}/{a.success ? '∞' : 3}</span>,
                result: a.success ? <StatusDot status="active" size="sm" /> : <XCircle className="h-3 w-3 text-red-500" />,
                created: <span className="text-[10px] text-muted-foreground">{new Date(a.created_at).toLocaleTimeString()}</span>,
              }))}
            />
          </ConsolePanel>
        )}

        {activeTab === 'stabilization' && (
          <ConsolePanel title="Stabilization Loops" icon={<Activity className="h-4 w-4" />} subtitle={`${loops.filter(l => l.state === 'running').length} running`}>
            <DataTable
              columns={[
                { key: 'target', label: 'Target', width: '20%' },
                { key: 'type', label: 'Type', width: '15%' },
                { key: 'metric', label: 'Metric', width: '20%' },
                { key: 'progress', label: 'Progress', width: '25%' },
                { key: 'iterations', label: 'Iterations', width: '10%' },
                { key: 'state', label: 'State', width: '10%' },
              ]}
              rows={loops.map(l => ({
                target: <span className="font-mono text-xs">{l.target_entity_id}</span>,
                type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{l.loop_type}</span>,
                metric: <span className="text-xs">{l.target_metric}</span>,
                progress: (
                  <div className="space-y-1">
                    <ProgressBar 
                      value={(l.current_value / l.target_threshold) * 100}
                      showValue
                      color={l.current_value >= l.target_threshold ? 'success' : 'warning'}
                    />
                    <span className="text-[10px] text-muted-foreground">target: {l.target_threshold}</span>
                  </div>
                ),
                iterations: <span className="font-mono text-xs">{l.iteration_count}/{l.max_iterations}</span>,
                state: <span className={`text-[10px] ${getStateColor(l.state)}`}>{l.state}</span>,
              }))}
            />
          </ConsolePanel>
        )}
      </div>
    </div>
  )
}
