"""
Self-Healing Runtime Monitor - Runtime stabilization and recovery monitoring.

Enterprise-grade self-healing interface with:
- Health monitoring
- Anomaly detection
- Recovery actions
- Stabilization loops
- Failure predictions
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  CheckCircle2,
  Clock,
  Gauge,
  Heart,
  Link2,
  Monitor,
  Plus,
  RefreshCw,
  Shield,
  Timer,
  TrendingUp,
  X,
  Zap,
} from 'lucide-react'
import {
  ConsolePanel,
  DataTable,
  TabBar,
  IconButton,
  StatusDot,
  ProgressBar,
  MetricValue,
} from './primitives'
import { MetricCard, AnomalyCard, StatusBar, ExecutionProgress } from './primitives'

// ---- Types ----

interface Anomaly {
  id: string
  title: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  target_id: string
  deviation?: number
  detected_at: string
}

interface RecoveryAction {
  id: string
  action_type: string
  target_id: string
  state: 'pending' | 'running' | 'completed' | 'failed'
  attempts: number
  started_at: string
  duration_ms?: number
}

interface ComponentHealth {
  id: string
  name: string
  health_score: number
  status: string
  error_rate: number
  latency_p99: number
}

// ---- Main Component ----

export default function SelfHealingRuntimeMonitor() {
  const [activeTab, setActiveTab] = useState('health')
  const [anomalies, setAnomalies] = useState<Anomaly[]>([])
  const [recoveries, setRecoveries] = useState<RecoveryAction[]>([])
  const [components, setComponents] = useState<ComponentHealth[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setAnomalies([
      { id: 'anom-001', title: 'High Latency Detected', severity: 'warning', target_id: 'Service-3', deviation: 0.34, detected_at: '2 min ago' },
      { id: 'anom-002', title: 'Memory Pressure', severity: 'info', target_id: 'Worker-5', detected_at: '5 min ago' },
      { id: 'anom-003', title: 'Error Rate Spike', severity: 'critical', target_id: 'RenderService', deviation: 0.67, detected_at: '1 min ago' },
    ])

    setRecoveries([
      { id: 'rec-001', action_type: 'retry', target_id: 'Job-1234', state: 'completed', attempts: 1, started_at: '10:45:23', duration_ms: 234 },
      { id: 'rec-002', action_type: 'restart', target_id: 'Worker-5', state: 'running', attempts: 2, started_at: '10:47:12' },
      { id: 'rec-003', action_type: 'failover', target_id: 'Service-3', state: 'pending', attempts: 0, started_at: '10:48:00' },
    ])

    setComponents([
      { id: 'comp-001', name: 'RenderService', health_score: 0.94, status: 'healthy', error_rate: 0.02, latency_p99: 45 },
      { id: 'comp-002', name: 'Orchestrator', health_score: 0.98, status: 'healthy', error_rate: 0.01, latency_p99: 23 },
      { id: 'comp-003', name: 'WorkerPool', health_score: 0.89, status: 'degraded', error_rate: 0.08, latency_p99: 89 },
      { id: 'comp-004', name: 'AssetStore', health_score: 0.99, status: 'healthy', error_rate: 0.00, latency_p99: 12 },
      { id: 'comp-005', name: 'EventBus', health_score: 0.96, status: 'healthy', error_rate: 0.02, latency_p99: 34 },
    ])

    setLoading(false)
  }, [])

  const tabs = [
    { id: 'health', label: 'Health', icon: <Heart className="h-3 w-3" />, badge: anomalies.length },
    { id: 'anomalies', label: 'Anomalies', icon: <AlertTriangle className="h-3 w-3" />, badge: anomalies.filter(a => a.severity === 'critical' || a.severity === 'error').length },
    { id: 'recoveries', label: 'Recoveries', icon: <RefreshCw className="h-3 w-3" />, badge: recoveries.filter(r => r.state === 'running' || r.state === 'pending').length },
    { id: 'loops', label: 'Stabilization', icon: <Gauge className="h-3 w-3" /> },
    { id: 'predictions', label: 'Predictions', icon: <TrendingUp className="h-3 w-3" /> },
  ]

  const getHealthColor = (score: number) => {
    if (score >= 0.9) return 'text-green-500'
    if (score >= 0.7) return 'text-yellow-500'
    return 'text-red-500'
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Shield className="h-5 w-5 text-primary" />
          <h1 className="text-lg font-semibold">Self-Healing Runtime Monitor</h1>
        </div>
        <div className="flex items-center gap-2">
          <IconButton icon={<Plus className="h-4 w-4" />} title="Create Recovery Action" />
          <IconButton icon={<RefreshCw className="h-4 w-4" />} title="Refresh" />
        </div>
      </div>

      {/* Tabs */}
      <TabBar tabs={tabs} active={activeTab} onChange={setActiveTab} />

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : activeTab === 'health' ? (
        <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
          {/* Overall Health */}
          <ConsolePanel
            title="System Health"
            icon={<Heart className="h-4 w-4" />}
            subtitle="Overall health status"
            status={anomalies.some(a => a.severity === 'critical') ? 'critical' : 'nominal'}
          >
            <div className="text-center py-4">
              <div className="text-4xl font-mono font-bold">94.2%</div>
              <div className="text-xs text-muted-foreground mt-1">HEALTH SCORE</div>
            </div>
            <StatusBar
              segments={[
                { label: 'Healthy', value: 142, color: 'bg-green-500' },
                { label: 'Degraded', value: 12, color: 'bg-yellow-500' },
                { label: 'Critical', value: 2, color: 'bg-red-500' },
              ]}
            />
          </ConsolePanel>

          {/* Recovery Metrics */}
          <ConsolePanel
            title="Recovery Metrics"
            icon={<RefreshCw className="h-4 w-4" />}
            subtitle="Self-healing performance"
          >
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-3xl font-mono font-bold">98.7%</div>
                <div className="text-[10px] text-muted-foreground">RECOVERY SUCCESS</div>
              </div>
              <MetricValue label="Active Loops" value={3} />
              <MetricValue label="Pending Actions" value={recoveries.filter(r => r.state === 'pending').length} />
              <MetricValue label="Avg Recovery Time" value="1.2s" unit="ms" />
            </div>
          </ConsolePanel>

          {/* Anomaly Summary */}
          <ConsolePanel
            title="Anomaly Summary"
            icon={<AlertTriangle className="h-4 w-4" />}
            subtitle="Recent anomalies"
            status={anomalies.length > 0 ? 'warning' : 'nominal'}
          >
            <div className="space-y-2">
              {anomalies.slice(0, 3).map(anomaly => (
                <div key={anomaly.id} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className={`h-4 w-4 ${
                      anomaly.severity === 'critical' ? 'text-red-500' :
                      anomaly.severity === 'warning' ? 'text-yellow-500' :
                      'text-blue-500'
                    }`} />
                    <span className="text-xs">{anomaly.title}</span>
                  </div>
                  <span className="text-[10px] text-muted-foreground">{anomaly.detected_at}</span>
                </div>
              ))}
            </div>
          </ConsolePanel>

          {/* Component Health */}
          <ConsolePanel
            title="Component Health"
            icon={<Monitor className="h-4 w-4" />}
            subtitle="Individual component status"
            className="lg:col-span-2"
          >
            <DataTable
              columns={[
                { key: 'name', label: 'Component', width: '20%' },
                { key: 'health', label: 'Health', width: '15%' },
                { key: 'status', label: 'Status', width: '15%' },
                { key: 'error_rate', label: 'Error Rate', width: '15%' },
                { key: 'latency', label: 'Latency P99', width: '15%' },
                { key: 'actions', label: 'Actions', width: '20%' },
              ]}
              rows={components.map(c => ({
                name: <span className="font-mono text-xs">{c.name}</span>,
                health: (
                  <div className="flex items-center gap-2">
                    <ProgressBar 
                      value={c.health_score * 100} 
                      showValue={false} 
                      color={c.health_score >= 0.9 ? 'success' : c.health_score >= 0.7 ? 'warning' : 'error'}
                    />
                    <span className={`font-mono text-xs ${getHealthColor(c.health_score)}`}>
                      {(c.health_score * 100).toFixed(0)}%
                    </span>
                  </div>
                ),
                status: (
                  <div className="flex items-center gap-1">
                    <StatusDot status={c.status === 'healthy' ? 'active' : c.status === 'degraded' ? 'warning' : 'error'} size="sm" />
                    <span className="text-xs capitalize">{c.status}</span>
                  </div>
                ),
                error_rate: <span className={`font-mono text-xs ${c.error_rate > 0.05 ? 'text-red-500' : 'text-muted-foreground'}`}>{(c.error_rate * 100).toFixed(2)}%</span>,
                latency: <span className="font-mono text-xs">{c.latency_p99}ms</span>,
                actions: (
                  <div className="flex items-center gap-1">
                    <IconButton icon={<Zap className="h-3 w-3" />} size="sm" title="Recovery" />
                    <IconButton icon={<Activity className="h-3 w-3" />} size="sm" title="Diagnostics" />
                  </div>
                ),
              }))}
            />
          </ConsolePanel>
        </div>
      ) : activeTab === 'anomalies' ? (
        <div className="space-y-4">
          <ConsolePanel
            title="Active Anomalies"
            subtitle="Detected anomalies requiring attention"
            icon={<AlertTriangle className="h-4 w-4" />}
            status={anomalies.some(a => a.severity === 'critical') ? 'critical' : anomalies.length > 0 ? 'warning' : 'nominal'}
          >
            <div className="space-y-3">
              {anomalies.map(anomaly => (
                <AnomalyCard
                  key={anomaly.id}
                  title={anomaly.title}
                  severity={anomaly.severity}
                  target={anomaly.target_id}
                  detectedAt={anomaly.detected_at}
                  description={anomaly.deviation ? `Deviation: ${(anomaly.deviation * 100).toFixed(0)}%` : undefined}
                  onResolve={() => console.log('Resolve:', anomaly.id)}
                />
              ))}
            </div>
          </ConsolePanel>

          <div className="grid gap-4 lg:grid-cols-2">
            <ConsolePanel
              title="Anomaly Distribution"
              icon={<Activity className="h-4 w-4" />}
              subtitle="By severity"
            >
              <StatusBar
                segments={[
                  { label: 'Critical', value: anomalies.filter(a => a.severity === 'critical').length, color: 'bg-red-600' },
                  { label: 'Error', value: anomalies.filter(a => a.severity === 'error').length, color: 'bg-red-500' },
                  { label: 'Warning', value: anomalies.filter(a => a.severity === 'warning').length, color: 'bg-yellow-500' },
                  { label: 'Info', value: anomalies.filter(a => a.severity === 'info').length, color: 'bg-blue-500' },
                ]}
              />
            </ConsolePanel>

            <ConsolePanel
              title="Detection Methods"
              icon={<Gauge className="h-4 w-4" />}
              subtitle="Anomaly detection techniques"
            >
              <DataTable
                columns={[
                  { key: 'method', label: 'Method', width: '40%' },
                  { key: 'count', label: 'Detections', width: '30%' },
                  { key: 'accuracy', label: 'Accuracy', width: '30%' },
                ]}
                rows={[
                  { method: 'Threshold', count: '45', accuracy: '94.2%' },
                  { method: 'Statistical', count: '23', accuracy: '89.7%' },
                  { method: 'Pattern', count: '12', accuracy: '91.3%' },
                ]}
              />
            </ConsolePanel>
          </div>
        </div>
      ) : activeTab === 'recoveries' ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <ConsolePanel
            title="Recovery Actions"
            subtitle="Active and recent recovery operations"
            icon={<RefreshCw className="h-4 w-4" />}
          >
            <DataTable
              columns={[
                { key: 'action', label: 'Action', width: '20%' },
                { key: 'target', label: 'Target', width: '15%' },
                { key: 'state', label: 'State', width: '15%' },
                { key: 'attempts', label: 'Attempts', width: '10%' },
                { key: 'duration', label: 'Duration', width: '15%' },
                { key: 'time', label: 'Started', width: '25%' },
              ]}
              rows={recoveries.map(r => ({
                action: <span className="text-xs px-1.5 py-0.5 rounded bg-primary/10">{r.action_type}</span>,
                target: <span className="font-mono text-xs">{r.target_id}</span>,
                state: (
                  <div className="flex items-center gap-1">
                    <StatusDot status={
                      r.state === 'completed' ? 'active' :
                      r.state === 'running' ? 'processing' :
                      r.state === 'pending' ? 'idle' : 'error'
                    } size="sm" />
                    <span className="text-xs capitalize">{r.state}</span>
                  </div>
                ),
                attempts: <span className="font-mono text-xs">{r.attempts}</span>,
                duration: <span className="font-mono text-xs">{r.duration_ms ? `${r.duration_ms}ms` : '-'}</span>,
                time: <span className="font-mono text-xs text-muted-foreground">{r.started_at}</span>,
              }))}
            />
          </ConsolePanel>

          <ConsolePanel
            title="Recovery Policies"
            icon={<Shield className="h-4 w-4" />}
            subtitle="Configured recovery rules"
          >
            <DataTable
              columns={[
                { key: 'name', label: 'Policy', width: '30%' },
                { key: 'type', label: 'Type', width: '20%' },
                { key: 'priority', label: 'Priority', width: '15%' },
                { key: 'enabled', label: 'Enabled', width: '15%' },
                { key: 'success', label: 'Success', width: '20%' },
              ]}
              rows={[
                { name: 'retry_policy', type: 'retry', priority: '10', enabled: 'Yes', success: '94.2%' },
                { name: 'restart_policy', type: 'restart', priority: '8', enabled: 'Yes', success: '89.7%' },
                { name: 'failover_policy', type: 'failover', priority: '5', enabled: 'Yes', success: '91.3%' },
              ]}
            />
          </ConsolePanel>
        </div>
      ) : activeTab === 'loops' ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <ConsolePanel
            title="Active Stabilization Loops"
            icon={<Gauge className="h-4 w-4" />}
            subtitle="Adaptive stabilization cycles"
          >
            <div className="space-y-4">
              <div className="rounded border border-border p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-medium">Memory Optimization</span>
                  <StatusDot status="processing" size="md" pulse />
                </div>
                <ExecutionProgress current={7} total={10} label="Iterations" showPercentage={false} />
                <div className="mt-2 flex justify-between text-[10px] text-muted-foreground">
                  <span>Target: 95%</span>
                  <span>Current: 89%</span>
                </div>
              </div>
              <div className="rounded border border-border p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-medium">Latency Reduction</span>
                  <StatusDot status="active" size="md" />
                </div>
                <ExecutionProgress current={4} total={8} label="Iterations" showPercentage={false} />
                <div className="mt-2 flex justify-between text-[10px] text-muted-foreground">
                  <span>Target: 50ms</span>
                  <span>Current: 67ms</span>
                </div>
              </div>
            </div>
          </ConsolePanel>

          <ConsolePanel
            title="Loop Performance"
            icon={<TrendingUp className="h-4 w-4" />}
            subtitle="Stabilization metrics"
          >
            <div className="space-y-3">
              <MetricValue label="Active Loops" value={3} />
              <MetricValue label="Completed Today" value={12} />
              <MetricValue label="Avg Convergence Time" value="45.2s" unit="ms" />
              <MetricValue label="Success Rate" value="96.8" unit="%" trend="up" />
            </div>
          </ConsolePanel>
        </div>
      ) : activeTab === 'predictions' ? (
        <div className="space-y-4">
          <ConsolePanel
            title="Failure Predictions"
            subtitle="Predicted failures and risk assessment"
            icon={<TrendingUp className="h-4 w-4" />}
          >
            <DataTable
              columns={[
                { key: 'prediction', label: 'Prediction', width: '20%' },
                { key: 'target', label: 'Target', width: '15%' },
                { key: 'probability', label: 'Probability', width: '15%' },
                { key: 'horizon', label: 'Horizon', width: '15%' },
                { key: 'confidence', label: 'Confidence', width: '15%' },
                { key: 'status', label: 'Status', width: '20%' },
              ]}
              rows={[
                { prediction: 'High Load', target: 'WorkerPool', probability: '67%', horizon: '15 min', confidence: '82%', status: 'Monitored' },
                { prediction: 'Memory Exhaustion', target: 'Service-3', probability: '45%', horizon: '30 min', confidence: '78%', status: 'Mitigated' },
                { prediction: 'Network Latency', target: 'EventBus', probability: '23%', horizon: '60 min', confidence: '85%', status: 'Watch' },
              ]}
            />
          </ConsolePanel>
        </div>
      ) : null}
    </div>
  )
}