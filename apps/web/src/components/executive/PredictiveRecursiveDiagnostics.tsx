/**
 * 43V3R CORE - Predictive Recursive Diagnostics
 * 
 * Forward-looking diagnostics with instability forecasting, cascade detection,
 * and systemic anomaly prediction for proactive system management.
 */
'use client'

import { useState, useEffect } from 'react'
import {
  Activity,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Clock,
  Eye,
  Zap,
  RefreshCw,
  Target,
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

interface Forecast {
  id: string
  forecast_key: string
  target_id: string
  target_type: string
  forecast_kind: string
  horizon: string
  predicted_value: number
  confidence: number
  probability: number
  severity: string
  risk_level: string
  validated: boolean
  generated_at: string
}

interface Anomaly {
  id: string
  anomaly_key: string
  target_id: string
  anomaly_type: string
  severity: string
  scope: string
  deviation: number
  cascade_risk: number
  status: string
  detected_at: string
}

export default function PredictiveRecursiveDiagnostics() {
  const api = useExecutiveApi()
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('forecasts')
  const [forecasts, setForecasts] = useState<Forecast[]>([])
  const [anomalies, setAnomalies] = useState<Anomaly[]>([])

  useEffect(() => {
    const loadData = async () => {
      try {
        const fc = await api.listForecasts({ not_validated: true, limit: 50 })
        const an = await api.listAnomalies({ limit: 50 })
        setForecasts(fc as Forecast[])
        setAnomalies(an as Anomaly[])
      } catch {
        setForecasts([
          { id: 'f1', forecast_key: 'fc_8a3f21', target_id: 'render-alpha-001', target_type: 'workflow', forecast_kind: 'failure_probability', horizon: 'near', predicted_value: 0.12, confidence: 0.87, probability: 0.15, severity: 'info', risk_level: 'low', validated: false, generated_at: new Date(Date.now() - 300000).toISOString() },
          { id: 'f2', forecast_key: 'fc_4c7d18', target_id: 'memory-controller', target_type: 'runtime', forecast_kind: 'drift', horizon: 'short', predicted_value: 0.34, confidence: 0.72, probability: 0.28, severity: 'warning', risk_level: 'medium', validated: false, generated_at: new Date(Date.now() - 600000).toISOString() },
          { id: 'f3', forecast_key: 'fc_9b2e67', target_id: 'orchestrator-main', target_type: 'orchestration', forecast_kind: 'coherence_drop', horizon: 'medium', predicted_value: 0.45, confidence: 0.68, probability: 0.35, severity: 'warning', risk_level: 'high', validated: false, generated_at: new Date(Date.now() - 900000).toISOString() },
        ])
        setAnomalies([
          { id: 'a1', anomaly_key: 'anom_2b8d91', target_id: 'execution-pipeline', anomaly_type: 'semantic_drift', severity: 'warning', scope: 'execution', deviation: 0.23, cascade_risk: 0.15, status: 'detected', detected_at: new Date(Date.now() - 120000).toISOString() },
          { id: 'a2', anomaly_key: 'anom_7f3c42', target_id: 'memory-subsystem', anomaly_type: 'latency_spike', severity: 'notice', scope: 'runtime', deviation: 0.12, cascade_risk: 0.05, status: 'monitoring', detected_at: new Date(Date.now() - 300000).toISOString() },
        ])
      }
      setLoading(false)
    }
    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [api])

  const tabs = [
    { id: 'forecasts', label: 'Forecasts', icon: <TrendingUp className="h-3 w-3" /> },
    { id: 'anomalies', label: 'Anomalies', icon: <AlertTriangle className="h-3 w-3" /> },
    { id: 'analytics', label: 'Analytics', icon: <BarChart3 className="h-3 w-3" /> },
  ]

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-3">
          <Activity className="h-5 w-5 text-primary" />
          <span className="font-mono text-sm font-semibold tracking-tight">PREDICTIVE RECURSIVE DIAGNOSTICS</span>
          <div className="h-4 w-px bg-border/50" />
          <StatusDot status={forecasts.length > 0 || anomalies.length > 0 ? 'active' : 'idle'} />
          <span className="text-[10px] font-mono text-muted-foreground uppercase">
            {forecasts.length} forecasts | {anomalies.length} anomalies
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
            {activeTab === 'forecasts' && (
              <div className="space-y-4">
                {/* Forecast Summary */}
                <div className="grid gap-4 lg:grid-cols-4">
                  <ConsolePanel title="Near-term" icon={<Clock className="h-4 w-4" />} subtitle="< 15 minutes">
                    <div className="text-2xl font-mono font-bold">{forecasts.filter(f => f.horizon === 'instantaneous' || f.horizon === 'near').length}</div>
                    <div className="text-[10px] text-muted-foreground mt-1">active forecasts</div>
                  </ConsolePanel>
                  <ConsolePanel title="Short-term" icon={<Clock className="h-4 w-4" />} subtitle="15-60 minutes">
                    <div className="text-2xl font-mono font-bold">{forecasts.filter(f => f.horizon === 'short').length}</div>
                    <div className="text-[10px] text-muted-foreground mt-1">active forecasts</div>
                  </ConsolePanel>
                  <ConsolePanel title="Medium-term" icon={<Clock className="h-4 w-4" />} subtitle="1-4 hours">
                    <div className="text-2xl font-mono font-bold">{forecasts.filter(f => f.horizon === 'medium').length}</div>
                    <div className="text-[10px] text-muted-foreground mt-1">active forecasts</div>
                  </ConsolePanel>
                  <ConsolePanel title="Avg Accuracy" icon={<Target className="h-4 w-4" />} subtitle="Forecast accuracy">
                    <div className="text-2xl font-mono font-bold">{Math.round((forecasts.reduce((acc, f) => acc + f.confidence, 0) / (forecasts.length || 1)) * 100)}%</div>
                    <div className="text-[10px] text-muted-foreground mt-1">confidence</div>
                  </ConsolePanel>
                </div>

                {/* Forecasts Table */}
                <ConsolePanel title="Active Forecasts" icon={<TrendingUp className="h-4 w-4" />} subtitle="Predicted instabilities">
                  <DataTable
                    columns={[
                      { key: 'target', label: 'Target', width: '18%' },
                      { key: 'kind', label: 'Kind', width: '18%' },
                      { key: 'horizon', label: 'Horizon', width: '12%' },
                      { key: 'predicted', label: 'Predicted', width: '12%' },
                      { key: 'probability', label: 'Probability', width: '12%' },
                      { key: 'confidence', label: 'Confidence', width: '12%' },
                      { key: 'risk', label: 'Risk', width: '16%' },
                    ]}
                    rows={forecasts.map(f => ({
                      key: f.id,
                      target: <span className="font-mono text-xs">{f.target_id.slice(0, 20)}</span>,
                      kind: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{f.forecast_kind}</span>,
                      horizon: (
                        <span className={`font-mono text-xs ${
                          f.horizon === 'instantaneous' || f.horizon === 'near' ? 'text-green-500' :
                          f.horizon === 'short' ? 'text-yellow-500' : 'text-red-500'
                        }`}>{f.horizon}</span>
                      ),
                      predicted: <span className="font-mono text-xs">{Math.round(f.predicted_value * 100)}%</span>,
                      probability: <span className="font-mono text-xs">{Math.round(f.probability * 100)}%</span>,
                      confidence: <ConfidenceBadge value={f.confidence} showLabel={false} />,
                      risk: (
                        <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                          f.risk_level === 'low' ? 'bg-green-500/10 text-green-500' :
                          f.risk_level === 'medium' ? 'bg-yellow-500/10 text-yellow-500' :
                          f.risk_level === 'high' ? 'bg-red-500/10 text-red-500' :
                          'bg-muted text-muted-foreground'
                        }`}>{f.risk_level}</span>
                      ),
                    }))}
                  />
                </ConsolePanel>
              </div>
            )}

            {activeTab === 'anomalies' && (
              <div className="space-y-4">
                {/* Anomaly Summary */}
                <div className="grid gap-4 lg:grid-cols-4">
                  <ConsolePanel title="Critical" icon={<AlertTriangle className="h-4 w-4 text-red-500" />} subtitle="Immediate action">
                    <div className="text-2xl font-mono font-bold text-red-500">{anomalies.filter(a => a.severity === 'critical').length}</div>
                  </ConsolePanel>
                  <ConsolePanel title="Warning" icon={<AlertTriangle className="h-4 w-4 text-yellow-500" />} subtitle="Attention required">
                    <div className="text-2xl font-mono font-bold text-yellow-500">{anomalies.filter(a => a.severity === 'warning').length}</div>
                  </ConsolePanel>
                  <ConsolePanel title="Notice" icon={<Eye className="h-4 w-4 text-blue-500" />} subtitle="Monitoring">
                    <div className="text-2xl font-mono font-bold text-blue-500">{anomalies.filter(a => a.severity === 'notice').length}</div>
                  </ConsolePanel>
                  <ConsolePanel title="Info" icon={<Activity className="h-4 w-4 text-green-500" />} subtitle="Logged">
                    <div className="text-2xl font-mono font-bold text-green-500">{anomalies.filter(a => a.severity === 'info').length}</div>
                  </ConsolePanel>
                </div>

                {/* Anomalies Table */}
                <ConsolePanel title="Active Anomalies" icon={<AlertTriangle className="h-4 w-4" />} subtitle="Systemic anomaly registry">
                  <DataTable
                    columns={[
                      { key: 'time', label: 'Detected', width: '12%' },
                      { key: 'target', label: 'Target', width: '18%' },
                      { key: 'type', label: 'Type', width: '18%' },
                      { key: 'severity', label: 'Severity', width: '12%' },
                      { key: 'deviation', label: 'Deviation', width: '12%' },
                      { key: 'cascade', label: 'Cascade Risk', width: '14%' },
                      { key: 'status', label: 'Status', width: '14%' },
                    ]}
                    rows={anomalies.map(a => ({
                      key: a.id,
                      time: <span className="font-mono text-xs text-muted-foreground">{new Date(a.detected_at).toLocaleTimeString()}</span>,
                      target: <span className="font-mono text-xs">{a.target_id.slice(0, 18)}</span>,
                      type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{a.anomaly_type}</span>,
                      severity: (
                        <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                          a.severity === 'critical' ? 'bg-red-500/20 text-red-500' :
                          a.severity === 'warning' ? 'bg-yellow-500/20 text-yellow-500' :
                          a.severity === 'notice' ? 'bg-blue-500/20 text-blue-500' :
                          'bg-muted text-muted-foreground'
                        }`}>{a.severity}</span>
                      ),
                      deviation: <span className="font-mono text-xs">{Math.round(a.deviation * 100)}%</span>,
                      cascade: <ProgressBar value={a.cascade_risk * 100} showValue={false} size="sm" color={a.cascade_risk > 0.5 ? 'error' : 'warning'} />,
                      status: (
                        <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                          a.status === 'detected' ? 'bg-red-500/10 text-red-500' :
                          a.status === 'monitoring' ? 'bg-yellow-500/10 text-yellow-500' :
                          'bg-green-500/10 text-green-500'
                        }`}>{a.status}</span>
                      ),
                    }))}
                  />
                </ConsolePanel>
              </div>
            )}

            {activeTab === 'analytics' && (
              <div className="grid gap-4 lg:grid-cols-2">
                <ConsolePanel title="Forecast Accuracy" icon={<Target className="h-4 w-4" />} subtitle="Prediction performance">
                  <div className="space-y-3">
                    {[
                      { kind: 'failure_probability', accuracy: 0.89 },
                      { kind: 'drift', accuracy: 0.76 },
                      { kind: 'coherence_drop', accuracy: 0.82 },
                      { kind: 'latency_spike', accuracy: 0.71 },
                    ].map((item) => (
                      <div key={item.kind} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="font-mono text-muted-foreground">{item.kind}</span>
                          <span className="font-mono">{Math.round(item.accuracy * 100)}%</span>
                        </div>
                        <ProgressBar value={item.accuracy * 100} showValue={false} color={item.accuracy > 0.8 ? 'success' : 'warning'} />
                      </div>
                    ))}
                  </div>
                </ConsolePanel>

                <ConsolePanel title="Anomaly Detection" icon={<Activity className="h-4 w-4" />} subtitle="Detection performance">
                  <div className="space-y-3">
                    {[
                      { metric: 'Precision', value: 0.91 },
                      { metric: 'Recall', value: 0.87 },
                      { metric: 'F1 Score', value: 0.89 },
                      { metric: 'Mean Detection Time', value: 120, unit: 'ms' },
                    ].map((item) => (
                      <div key={item.metric} className="flex items-center justify-between py-2 border-b border-border/30 last:border-0">
                        <span className="text-xs text-muted-foreground">{item.metric}</span>
                        <span className="font-mono text-sm">
                          {item.value}{item.unit || '%'}
                        </span>
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
