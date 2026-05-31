"""
Predictive Stability Analytics - Runtime forecasting and predictive analytics.

Enterprise-grade predictive analytics interface with:
- Runtime forecasting
- Stability predictions
- Anomaly forecasts
- Telemetry aggregation
- Model performance
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  Brain,
  Calendar,
  ChevronDown,
  Clock,
  Filter,
  LineChart,
  Plus,
  RefreshCw,
  Search,
  Target,
  TrendingDown,
  TrendingUp,
  Zap,
} from 'lucide-react'
import {
  ConsolePanel,
  DataTable,
  TabBar,
  IconButton,
  StatusDot,
  ConfidenceBadge,
  MetricValue,
  ProgressBar,
} from './primitives'
import { MetricCard, SparklineChart, StatusBar } from './primitives'

// ---- Types ----

interface Forecast {
  id: string
  forecast_type: string
  target_id: string
  predicted_value: number
  confidence: number
  horizon: 'short' | 'medium' | 'long'
  predicted_for: string
  status: 'pending' | 'active' | 'validated' | 'expired'
}

interface AnomalyForecast {
  id: string
  anomaly_type: string
  target_id: string
  probability: number
  severity: string
  predicted_time: string
  is_mitigated: boolean
  confidence: number
}

interface TelemetryMetric {
  name: string
  current: number
  min: number
  max: number
  trend: 'up' | 'down' | 'stable'
  sparkline: number[]
}

// ---- Main Component ----

export default function PredictiveStabilityAnalytics() {
  const [activeTab, setActiveTab] = useState('forecasts')
  const [forecasts, setForecasts] = useState<Forecast[]>([])
  const [anomalyForecasts, setAnomalyForecasts] = useState<AnomalyForecast[]>([])
  const [telemetryMetrics, setTelemetryMetrics] = useState<TelemetryMetric[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setForecasts([
      { id: 'fc-001', forecast_type: 'duration', target_id: 'render-job-1234', predicted_value: 245.7, confidence: 0.85, horizon: 'short', predicted_for: '10 min', status: 'active' },
      { id: 'fc-002', forecast_type: 'queue_time', target_id: 'workflow-alpha', predicted_value: 45.2, confidence: 0.78, horizon: 'short', predicted_for: '5 min', status: 'active' },
      { id: 'fc-003', forecast_type: 'failure_probability', target_id: 'Service-3', predicted_value: 0.12, confidence: 0.72, horizon: 'medium', predicted_for: '30 min', status: 'pending' },
      { id: 'fc-004', forecast_type: 'resource_usage', target_id: 'WorkerPool', predicted_value: 78.5, confidence: 0.91, horizon: 'short', predicted_for: '15 min', status: 'active' },
    ])

    setAnomalyForecasts([
      { id: 'af-001', anomaly_type: 'high_load', target_id: 'WorkerPool', probability: 0.67, severity: 'warning', predicted_time: '15 min', is_mitigated: false, confidence: 0.82 },
      { id: 'af-002', anomaly_type: 'memory_pressure', target_id: 'Service-3', probability: 0.45, severity: 'info', predicted_time: '30 min', is_mitigated: true, confidence: 0.78 },
      { id: 'af-003', anomaly_type: 'latency_spike', target_id: 'EventBus', probability: 0.23, severity: 'info', predicted_time: '60 min', is_mitigated: false, confidence: 0.85 },
    ])

    setTelemetryMetrics([
      { name: 'Throughput', current: 847, min: 720, max: 980, trend: 'up', sparkline: generateSparkline(0.8, 20) },
      { name: 'Latency P99', current: 45.2, min: 23.1, max: 89.4, trend: 'down', sparkline: generateSparkline(0.4, 20) },
      { name: 'Error Rate', current: 0.02, min: 0.01, max: 0.08, trend: 'stable', sparkline: generateSparkline(0.2, 20) },
      { name: 'CPU Usage', current: 67.4, min: 45.2, max: 89.1, trend: 'stable', sparkline: generateSparkline(0.65, 20) },
      { name: 'Memory Usage', current: 78.9, min: 56.3, max: 94.2, trend: 'up', sparkline: generateSparkline(0.75, 20) },
    ])

    setLoading(false)
  }, [])

  const tabs = [
    { id: 'forecasts', label: 'Forecasts', icon: <TrendingUp className="h-3 w-3" />, badge: forecasts.filter(f => f.status === 'active').length },
    { id: 'anomaly_predictions', label: 'Anomaly Predictions', icon: <AlertTriangle className="h-3 w-3" />, badge: anomalyForecasts.filter(a => !a.is_mitigated).length },
    { id: 'telemetry', label: 'Telemetry', icon: <Activity className="h-3 w-3" /> },
    { id: 'models', label: 'Models', icon: <Brain className="h-3 w-3" /> },
  ]

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <LineChart className="h-5 w-5 text-primary" />
          <h1 className="text-lg font-semibold">Predictive Stability Analytics</h1>
        </div>
        <div className="flex items-center gap-2">
          <IconButton icon={<Search className="h-4 w-4" />} title="Search" />
          <IconButton icon={<Filter className="h-4 w-4" />} title="Filter" />
          <IconButton icon={<Plus className="h-4 w-4" />} title="New Forecast" />
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
      ) : activeTab === 'forecasts' ? (
        <div className="space-y-4">
          {/* Forecast Summary */}
          <div className="grid gap-4 lg:grid-cols-3">
            <ConsolePanel
              title="Active Forecasts"
              icon={<TrendingUp className="h-4 w-4" />}
              subtitle="Current predictions"
            >
              <div className="text-center py-4">
                <div className="text-3xl font-mono font-bold">{forecasts.filter(f => f.status === 'active').length}</div>
                <div className="text-[10px] text-muted-foreground">ACTIVE FORECASTS</div>
              </div>
            </ConsolePanel>

            <ConsolePanel
              title="Avg Confidence"
              icon={<Target className="h-4 w-4" />}
              subtitle="Forecast accuracy"
            >
              <div className="text-center py-4">
                <div className="text-3xl font-mono font-bold">
                  {Math.round((forecasts.reduce((sum, f) => sum + f.confidence, 0) / forecasts.length) * 100)}%
                </div>
                <div className="text-[10px] text-muted-foreground">AVG CONFIDENCE</div>
              </div>
            </ConsolePanel>

            <ConsolePanel
              title="Horizon Distribution"
              icon={<Clock className="h-4 w-4" />}
              subtitle="Forecast time ranges"
            >
              <StatusBar
                segments={[
                  { label: 'Short', value: forecasts.filter(f => f.horizon === 'short').length, color: 'bg-green-500' },
                  { label: 'Medium', value: forecasts.filter(f => f.horizon === 'medium').length, color: 'bg-blue-500' },
                  { label: 'Long', value: forecasts.filter(f => f.horizon === 'long').length, color: 'bg-purple-500' },
                ]}
              />
            </ConsolePanel>
          </div>

          {/* Forecast Table */}
          <ConsolePanel
            title="Runtime Forecasts"
            subtitle="Active predictions and their status"
            icon={<TrendingUp className="h-4 w-4" />}
          >
            <DataTable
              columns={[
                { key: 'type', label: 'Type', width: '15%' },
                { key: 'target', label: 'Target', width: '15%' },
                { key: 'predicted', label: 'Predicted', width: '15%' },
                { key: 'confidence', label: 'Confidence', width: '15%' },
                { key: 'horizon', label: 'Horizon', width: '10%' },
                { key: 'for', label: 'For', width: '10%' },
                { key: 'status', label: 'Status', width: '20%' },
              ]}
              rows={forecasts.map(f => ({
                type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-primary/10">{f.forecast_type}</span>,
                target: <span className="font-mono text-xs">{f.target_id}</span>,
                predicted: <span className="font-mono text-xs">{f.predicted_value.toFixed(2)}</span>,
                confidence: <ConfidenceBadge value={f.confidence} />,
                horizon: <span className="text-xs capitalize">{f.horizon}</span>,
                for: <span className="font-mono text-xs text-muted-foreground">{f.predicted_for}</span>,
                status: (
                  <div className="flex items-center gap-1">
                    <StatusDot status={
                      f.status === 'active' ? 'active' :
                      f.status === 'pending' ? 'idle' :
                      f.status === 'validated' ? 'active' : 'warning'
                    } size="sm" />
                    <span className="text-xs capitalize">{f.status}</span>
                  </div>
                ),
              }))}
            />
          </ConsolePanel>

          {/* Forecast Sparklines */}
          <div className="grid gap-4 lg:grid-cols-3">
            <ConsolePanel
              title="Forecast Accuracy Trend"
              icon={<LineChart className="h-4 w-4" />}
              subtitle="Model accuracy over time"
            >
              <SparklineChart data={generateSparkline(0.85, 15)} color="#22c55e" height={48} />
              <div className="mt-3 flex justify-between text-[10px] text-muted-foreground">
                <span>7 days ago</span>
                <span className="font-mono">85.2%</span>
                <span>now</span>
              </div>
            </ConsolePanel>

            <ConsolePanel
              title="Prediction Volume"
              icon={<Activity className="h-4 w-4" />}
              subtitle="Forecasts generated"
            >
              <SparklineChart data={generateSparkline(0.65, 15)} color="#3b82f6" height={48} />
              <div className="mt-3 flex justify-between text-[10px] text-muted-foreground">
                <span>234</span>
                <span className="font-mono text-primary">456</span>
                <span>today</span>
              </div>
            </ConsolePanel>

            <ConsolePanel
              title="Error Distribution"
              icon={<AlertTriangle className="h-4 w-4" />}
              subtitle="Prediction errors by type"
            >
              <StatusBar
                segments={[
                  { label: 'Duration', value: 12, color: 'bg-green-500' },
                  { label: 'Resource', value: 8, color: 'bg-blue-500' },
                  { label: 'Failure', value: 5, color: 'bg-yellow-500' },
                  { label: 'Other', value: 3, color: 'bg-neutral-500' },
                ]}
              />
            </ConsolePanel>
          </div>
        </div>
      ) : activeTab === 'anomaly_predictions' ? (
        <div className="space-y-4">
          <ConsolePanel
            title="Anomaly Predictions"
            subtitle="Predicted anomalies and risk assessments"
            icon={<AlertTriangle className="h-4 w-4" />}
            status={anomalyForecasts.some(a => a.probability > 0.5 && !a.is_mitigated) ? 'warning' : 'nominal'}
          >
            <DataTable
              columns={[
                { key: 'type', label: 'Type', width: '15%' },
                { key: 'target', label: 'Target', width: '15%' },
                { key: 'probability', label: 'Probability', width: '15%' },
                { key: 'severity', label: 'Severity', width: '10%' },
                { key: 'time', label: 'Predicted Time', width: '15%' },
                { key: 'confidence', label: 'Confidence', width: '15%' },
                { key: 'status', label: 'Status', width: '15%' },
              ]}
              rows={anomalyForecasts.map(a => ({
                type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-500/10 text-red-500">{a.anomaly_type}</span>,
                target: <span className="font-mono text-xs">{a.target_id}</span>,
                probability: (
                  <div className="flex items-center gap-2">
                    <ProgressBar 
                      value={a.probability * 100} 
                      showValue={false} 
                      color={a.probability > 0.5 ? 'error' : a.probability > 0.3 ? 'warning' : 'primary'}
                    />
                    <span className="font-mono text-xs">{(a.probability * 100).toFixed(0)}%</span>
                  </div>
                ),
                severity: (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                    a.severity === 'critical' ? 'bg-red-500/10 text-red-500' :
                    a.severity === 'warning' ? 'bg-yellow-500/10 text-yellow-500' :
                    'bg-blue-500/10 text-blue-500'
                  }`}>
                    {a.severity}
                  </span>
                ),
                time: <span className="font-mono text-xs text-muted-foreground">{a.predicted_time}</span>,
                confidence: <ConfidenceBadge value={a.confidence} />,
                status: (
                  <div className="flex items-center gap-1">
                    {a.is_mitigated ? (
                      <>
                        <CheckCircle2 className="h-3 w-3 text-green-500" />
                        <span className="text-xs text-green-500">Mitigated</span>
                      </>
                    ) : (
                      <>
                        <StatusDot status="warning" size="sm" />
                        <span className="text-xs">Monitored</span>
                      </>
                    )}
                  </div>
                ),
              }))}
            />
          </ConsolePanel>

          <div className="grid gap-4 lg:grid-cols-2">
            <ConsolePanel
              title="Risk Assessment"
              icon={<Activity className="h-4 w-4" />}
              subtitle="Overall risk score"
            >
              <div className="text-center py-4">
                <div className="text-3xl font-mono font-bold text-yellow-500">MEDIUM</div>
                <div className="text-[10px] text-muted-foreground mt-1">RISK LEVEL</div>
              </div>
              <StatusBar
                segments={[
                  { label: 'Critical', value: 1, color: 'bg-red-600' },
                  { label: 'High', value: 2, color: 'bg-red-500' },
                  { label: 'Medium', value: 3, color: 'bg-yellow-500' },
                  { label: 'Low', value: 8, color: 'bg-green-500' },
                ]}
              />
            </ConsolePanel>

            <ConsolePanel
              title="Prediction Accuracy"
              icon={<Target className="h-4 w-4" />}
              subtitle="Anomaly prediction performance"
            >
              <div className="space-y-3">
                <MetricValue label="Precision" value="0.82" trend="up" />
                <MetricValue label="Recall" value="0.78" />
                <MetricValue label="F1 Score" value="0.80" />
              </div>
            </ConsolePanel>
          </div>
        </div>
      ) : activeTab === 'telemetry' ? (
        <ConsolePanel
          title="Telemetry Metrics"
          subtitle="Real-time system metrics"
          icon={<Activity className="h-4 w-4" />}
        >
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {telemetryMetrics.map(metric => (
              <div key={metric.name} className="rounded border border-border p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs text-muted-foreground">{metric.name}</span>
                  {metric.trend === 'up' ? (
                    <TrendingUp className="h-3 w-3 text-green-500" />
                  ) : metric.trend === 'down' ? (
                    <TrendingDown className="h-3 w-3 text-red-500" />
                  ) : (
                    <span className="h-3 w-3 text-muted-foreground">—</span>
                  )}
                </div>
                <div className="text-xl font-mono font-bold">{metric.current.toFixed(1)}</div>
                <div className="flex justify-between text-[10px] text-muted-foreground mt-1">
                  <span>min: {metric.min.toFixed(1)}</span>
                  <span>max: {metric.max.toFixed(1)}</span>
                </div>
                <div className="mt-3 h-12">
                  <SparklineChart data={metric.sparkline} color={metric.trend === 'up' ? '#22c55e' : metric.trend === 'down' ? '#ef4444' : '#3b82f6'} height={48} />
                </div>
              </div>
            ))}
          </div>
        </ConsolePanel>
      ) : activeTab === 'models' ? (
        <ConsolePanel
          title="Forecast Models"
          subtitle="Prediction models and their performance"
          icon={<Brain className="h-4 w-4" />}
        >
          <DataTable
            columns={[
              { key: 'model', label: 'Model', width: '20%' },
              { key: 'type', label: 'Type', width: '15%' },
              { key: 'accuracy', label: 'Accuracy', width: '15%' },
              { key: 'samples', label: 'Training Samples', width: '15%' },
              { key: 'last_used', label: 'Last Used', width: '15%' },
              { key: 'status', label: 'Status', width: '20%' },
            ]}
            rows={[
              { model: 'duration_forecast_v2', type: 'duration', accuracy: '89.2%', samples: '45,892', last_used: '2 min ago', status: <StatusDot status="active" size="sm" /> },
              { model: 'resource_predictor_v1', type: 'resource', accuracy: '92.5%', samples: '34,521', last_used: '5 min ago', status: <StatusDot status="active" size="sm" /> },
              { model: 'failure_detector_v3', type: 'failure', accuracy: '85.7%', samples: '28,934', last_used: '1 min ago', status: <StatusDot status="active" size="sm" /> },
              { model: 'queue_predictor_v1', type: 'queue', accuracy: '87.3%', samples: '19,234', last_used: '10 min ago', status: <StatusDot status="idle" size="sm" /> },
            ]}
          />
        </ConsolePanel>
      ) : null}
    </div>
  )
}

function generateSparkline(base: number, length: number): number[] {
  const data: number[] = []
  let current = base
  for (let i = 0; i < length; i++) {
    current = current + (Math.random() - 0.5) * 0.15
    data.push(Math.max(0, Math.min(1, current)))
  }
  return data
}