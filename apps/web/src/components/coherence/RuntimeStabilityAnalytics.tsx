/**
 * 43V3R CORE - Runtime Stability Analytics
 * 
 * Predictive stability monitoring, anomaly detection,
 * and orchestration diagnostics for self-healing.
 * 
 * Dense telemetry interface with real-time metrics,
 * predictive forecasting, and health visualization.
 */
'use client'

import { useState, useEffect } from 'react'
import {
  Activity,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle2,
  Gauge,
  Clock,
  Zap,
  RefreshCw,
  BarChart3,
  LineChart,
  Thermometer,
  Cpu,
  HardDrive,
  Network,
  AlertCircle,
} from 'lucide-react'
import { useCoherenceApi, type StabilityAssessment, type AnomalyDetection, type ExecutionForecast } from '@/lib/coherence-api'
import { ConsolePanel, MetricGrid, MetricValue, StatusDot, ConfidenceBadge, Sparkline, DataTable, TabBar, IconButton, ProgressBar } from '@/components/cognitive/primitives'

// ---- Types ----

interface StabilityOverview {
  stabilityScore: number
  healthScore: number
  throughput: number
  errorRate: number
  latencyP50: number
  latencyP95: number
  uptime: string
}

interface MetricTrend {
  label: string
  values: number[]
  trend: 'up' | 'down' | 'stable'
}

// ---- Main Component ----

export default function RuntimeStabilityAnalytics() {
  const api = useCoherenceApi()
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [overview, setOverview] = useState<StabilityOverview>({
    stabilityScore: 0,
    healthScore: 0,
    throughput: 0,
    errorRate: 0,
    latencyP50: 0,
    latencyP95: 0,
    uptime: '0s',
  })
  const [assessment, setAssessment] = useState<StabilityAssessment | null>(null)
  const [anomalies, setAnomalies] = useState<AnomalyDetection[]>([])
  const [forecasts, setForecasts] = useState<ExecutionForecast[]>([])
  const [metricTrends, setMetricTrends] = useState<Record<string, MetricTrend>>({})
  
  useEffect(() => {
    const startTime = Date.now()
    
    const loadData = async () => {
      try {
        // Mock data
        const mockAnomalies: AnomalyDetection[] = [
          { anomaly_id: 'ano-001', anomaly_type: 'latency_spike', severity: 'warning', description: 'P99 latency exceeded threshold', deviation: 0.35, detected_at: new Date(Date.now() - 300000).toISOString(), is_resolved: false },
          { anomaly_id: 'ano-002', anomaly_type: 'error_rate_increase', severity: 'info', description: 'Error rate slightly elevated', deviation: 0.12, detected_at: new Date(Date.now() - 1200000).toISOString(), is_resolved: true },
          { anomaly_id: 'ano-003', anomaly_type: 'resource_contention', severity: 'violation', description: 'CPU contention detected', deviation: 0.45, detected_at: new Date(Date.now() - 1800000).toISOString(), is_resolved: false },
        ]
        
        const mockForecasts: ExecutionForecast[] = [
          { forecast_id: 'fc-001', subject_kind: 'workflow', subject_key: 'render-alpha-001', forecast_kind: 'duration', horizon: 'near_term', predicted_value: 245, confidence: 0.85, predicted_for: new Date(Date.now() + 600000).toISOString(), forecast_state: 'pending' },
          { forecast_id: 'fc-002', subject_kind: 'render_job', subject_key: 'job-bridge-42', forecast_kind: 'queue_time', horizon: 'short', predicted_value: 45, confidence: 0.78, predicted_for: new Date(Date.now() + 1200000).toISOString(), forecast_state: 'pending' },
          { forecast_id: 'fc-003', subject_kind: 'workflow', subject_key: 'compose-music-v3', forecast_kind: 'failure_probability', horizon: 'extended', predicted_value: 0.12, confidence: 0.72, predicted_for: new Date(Date.now() + 3600000).toISOString(), forecast_state: 'pending' },
        ]
        
        const mockAssessment: StabilityAssessment = {
          status: 'stable',
          score: 0.94,
          health_score: 0.96,
          issues: [],
          recommendations: ['System is healthy', 'Continue monitoring'],
        }
        
        // Generate sparkline data
        const generateSparkline = (base: number, length = 20): number[] => {
          const values: number[] = []
          let current = base
          for (let i = 0; i < length; i++) {
            current = current + (Math.random() - 0.5) * 0.1
            values.push(Math.max(0, Math.min(1, current)))
          }
          return values
        }
        
        const uptimeSecs = Math.floor((Date.now() - startTime) / 1000)
        setOverview({
          stabilityScore: 0.94 + Math.random() * 0.05,
          healthScore: 0.96 + Math.random() * 0.03,
          throughput: 142 + Math.floor(Math.random() * 20),
          errorRate: 0.003 + Math.random() * 0.002,
          latencyP50: 18 + Math.floor(Math.random() * 8),
          latencyP95: 45 + Math.floor(Math.random() * 15),
          uptime: `${Math.floor(uptimeSecs / 60)}m ${uptimeSecs % 60}s`,
        })
        
        setAssessment(mockAssessment)
        setAnomalies(mockAnomalies)
        setForecasts(mockForecasts)
        
        setMetricTrends({
          stability: { label: 'Stability', values: generateSparkline(0.9), trend: 'stable' },
          health: { label: 'Health', values: generateSparkline(0.95), trend: 'up' },
          throughput: { label: 'Throughput', values: generateSparkline(0.7), trend: 'up' },
          errorRate: { label: 'Error Rate', values: generateSparkline(0.1), trend: 'down' },
        })
      } catch {
        // Use defaults
      }
      setLoading(false)
    }
    
    loadData()
    const interval = setInterval(loadData, 10000)
    return () => clearInterval(interval)
  }, [api])
  
  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Activity className="h-3 w-3" /> },
    { id: 'metrics', label: 'Metrics', icon: <BarChart3 className="h-3 w-3" /> },
    { id: 'anomalies', label: 'Anomalies', icon: <AlertTriangle className="h-3 w-3" /> },
    { id: 'forecasts', label: 'Forecasts', icon: <TrendingUp className="h-3 w-3" /> },
  ]
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'stable': return 'text-green-500'
      case 'marginal': return 'text-yellow-500'
      case 'degrading': return 'text-orange-500'
      case 'unstable': return 'text-red-500'
      default: return 'text-muted-foreground'
    }
  }
  
  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            <span className="font-mono text-sm font-semibold tracking-tight">RUNTIME STABILITY</span>
          </div>
          <div className="h-4 w-px bg-border/50" />
          <StatusDot status={assessment?.status === 'stable' ? 'healthy' : 'degraded'} />
          <span className={`text-[10px] font-mono uppercase ${getStatusColor(assessment?.status || 'stable')}`}>
            {assessment?.status || 'unknown'}
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <div className="text-[10px] font-mono text-muted-foreground">
            <Clock className="h-3 w-3 inline mr-1" />
            {overview.uptime}
          </div>
          <IconButton icon={<RefreshCw className="h-3 w-3" />} onClick={() => setLoading(true)} />
        </div>
      </div>
      
      {/* Metrics Bar */}
      <div className="border-b border-border/50 bg-muted/20 px-4 py-2">
        <MetricGrid columns={6}>
          <MetricValue
            label="Stability Score"
            value={`${Math.round(overview.stabilityScore * 100)}%`}
            icon={<Gauge className="h-3 w-3" />}
            trend={overview.stabilityScore > 0.9 ? 'up' : 'stable'}
          />
          <MetricValue
            label="Health Score"
            value={`${Math.round(overview.healthScore * 100)}%`}
            icon={<CheckCircle2 className="h-3 w-3" />}
            trend={overview.healthScore > 0.95 ? 'up' : 'stable'}
          />
          <MetricValue
            label="Throughput"
            value={overview.throughput}
            icon={<Zap className="h-3 w-3" />}
            unit="jobs/s"
            trend="up"
          />
          <MetricValue
            label="Error Rate"
            value={`${(overview.errorRate * 100).toFixed(2)}%`}
            icon={<AlertCircle className="h-3 w-3" />}
            trend={overview.errorRate < 0.01 ? 'down' : 'stable'}
          />
          <MetricValue
            label="Latency P50"
            value={`${overview.latencyP50}ms`}
            icon={<Clock className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Latency P95"
            value={`${overview.latencyP95}ms`}
            icon={<Clock className="h-3 w-3" />}
            trend="stable"
          />
        </MetricGrid>
      </div>
      
      {/* Tabs */}
      <div className="border-b border-border/50 px-4">
        <TabBar
          tabs={tabs}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />
      </div>
      
      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {activeTab === 'overview' && (
          <div className="grid gap-4 lg:grid-cols-3">
            {/* Sparklines */}
            <div className="lg:col-span-2">
              <ConsolePanel
                title="Stability Trends"
                icon={<LineChart className="h-4 w-4" />}
                subtitle="Real-time metric visualization"
              >
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(metricTrends).map(([key, trend]) => (
                    <div key={key} className="p-4 rounded border border-border/50">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-sm font-medium">{trend.label}</span>
                        <div className="flex items-center gap-1">
                          {trend.trend === 'up' && <TrendingUp className="h-3 w-3 text-green-500" />}
                          {trend.trend === 'down' && <TrendingDown className="h-3 w-3 text-red-500" />}
                          {trend.trend === 'stable' && <Activity className="h-3 w-3 text-muted-foreground" />}
                        </div>
                      </div>
                      <Sparkline data={trend.values} color={
                        key === 'errorRate' 
                          ? (trend.trend === 'down' ? 'green' : 'red')
                          : (trend.trend === 'up' ? 'green' : 'primary')
                      } />
                    </div>
                  ))}
                </div>
              </ConsolePanel>
            </div>
            
            {/* Assessment */}
            <div>
              <ConsolePanel
                title="Stability Assessment"
                icon={<Gauge className="h-4 w-4" />}
                subtitle="Current health evaluation"
              >
                <div className="space-y-4">
                  <div className="text-center p-6 rounded border border-border/50">
                    <div className={`text-4xl font-mono font-bold ${getStatusColor(assessment?.status || 'stable')}`}>
                      {Math.round((assessment?.score || 0) * 100)}%
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">Overall Stability</div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Health Score</span>
                      <div className="flex items-center gap-2">
                        <ProgressBar value={(assessment?.health_score || 0) * 100} showValue={false} color="success" />
                        <span className="font-mono">{Math.round((assessment?.health_score || 0) * 100)}%</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="pt-2 border-t border-border/50">
                    <span className="text-[10px] text-muted-foreground uppercase">Recommendations</span>
                    <div className="space-y-1 mt-2">
                      {(assessment?.recommendations || ['No recommendations']).map((rec, idx) => (
                        <div key={idx} className="flex items-center gap-2 text-xs">
                          <CheckCircle2 className="h-3 w-3 text-green-500" />
                          <span>{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {(assessment?.issues?.length || 0) > 0 && (
                    <div className="pt-2 border-t border-border/50">
                      <span className="text-[10px] text-muted-foreground uppercase">Issues</span>
                      <div className="space-y-1 mt-2">
                        {assessment?.issues?.map((issue, idx) => (
                          <div key={idx} className="flex items-center gap-2 text-xs text-orange-500">
                            <AlertTriangle className="h-3 w-3" />
                            <span>{issue}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </ConsolePanel>
            </div>
          </div>
        )}
        
        {activeTab === 'metrics' && (
          <ConsolePanel
            title="Performance Metrics"
            icon={<BarChart3 className="h-4 w-4" />}
            subtitle="Detailed telemetry"
          >
            <div className="grid grid-cols-4 gap-4">
              {[
                { icon: <Cpu className="h-4 w-4" />, label: 'CPU Usage', value: '45%', trend: 'stable' },
                { icon: <HardDrive className="h-4 w-4" />, label: 'Memory', value: '62%', trend: 'stable' },
                { icon: <Network className="h-4 w-4" />, label: 'Network I/O', value: '128 MB/s', trend: 'up' },
                { icon: <Thermometer className="h-4 w-4" />, label: 'Queue Depth', value: '23', trend: 'stable' },
              ].map((metric, idx) => (
                <div key={idx} className="p-4 rounded border border-border/50">
                  <div className="flex items-center gap-2 mb-3">
                    {metric.icon}
                    <span className="text-sm">{metric.label}</span>
                  </div>
                  <div className="text-2xl font-mono">{metric.value}</div>
                  <div className="flex items-center gap-1 mt-2 text-[10px] text-muted-foreground">
                    {metric.trend === 'up' && <TrendingUp className="h-3 w-3 text-green-500" />}
                    {metric.trend === 'down' && <TrendingDown className="h-3 w-3 text-red-500" />}
                    {metric.trend === 'stable' && <Activity className="h-3 w-3" />}
                    <span>{metric.trend}</span>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>
        )}
        
        {activeTab === 'anomalies' && (
          <ConsolePanel
            title="Anomaly Detection"
            icon={<AlertTriangle className="h-4 w-4" />}
            subtitle={`${anomalies.length} detected`}
          >
            <DataTable
              columns={[
                { key: 'id', label: 'Anomaly ID', width: '15%' },
                { key: 'type', label: 'Type', width: '20%' },
                { key: 'severity', label: 'Severity', width: '15%' },
                { key: 'description', label: 'Description', width: '30%' },
                { key: 'deviation', label: 'Deviation', width: '10%' },
                { key: 'status', label: 'Status', width: '10%' },
              ]}
              rows={anomalies.map(a => ({
                id: <span className="font-mono text-xs">{a.anomaly_id}</span>,
                type: <span className="text-xs">{a.anomaly_type}</span>,
                severity: (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                    a.severity === 'critical' ? 'bg-red-500/10 text-red-500' :
                    a.severity === 'violation' ? 'bg-orange-500/10 text-orange-500' :
                    a.severity === 'warning' ? 'bg-yellow-500/10 text-yellow-500' :
                    'bg-blue-500/10 text-blue-500'
                  }`}>
                    {a.severity}
                  </span>
                ),
                description: <span className="text-xs text-muted-foreground">{a.description}</span>,
                deviation: <span className="font-mono">{Math.round(a.deviation * 100)}%</span>,
                status: (
                  <div className="flex items-center gap-1">
                    {a.is_resolved ? (
                      <CheckCircle2 className="h-3 w-3 text-green-500" />
                    ) : (
                      <XCircle className="h-3 w-3 text-red-500" />
                    )}
                  </div>
                ),
              }))}
            />
          </ConsolePanel>
        )}
        
        {activeTab === 'forecasts' && (
          <ConsolePanel
            title="Execution Forecasts"
            icon={<TrendingUp className="h-4 w-4" />}
            subtitle={`${forecasts.length} active predictions`}
          >
            <div className="grid grid-cols-3 gap-4">
              {forecasts.map(forecast => (
                <div key={forecast.forecast_id} className="p-4 rounded border border-border/50">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-mono">{forecast.subject_key}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                      forecast.horizon === 'near_term' ? 'bg-green-500/10 text-green-500' :
                      forecast.horizon === 'short' ? 'bg-blue-500/10 text-blue-500' :
                      'bg-muted text-muted-foreground'
                    }`}>
                      {forecast.horizon}
                    </span>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">{forecast.forecast_kind}</span>
                      <span className="text-lg font-mono">{forecast.predicted_value}{forecast.predicted_unit || ''}</span>
                    </div>
                    <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                      <span>Confidence</span>
                      <ConfidenceBadge value={forecast.confidence} showLabel />
                    </div>
                    <div className="text-[10px] text-muted-foreground text-right">
                      Predicts: {new Date(forecast.predicted_for).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>
        )}
      </div>
    </div>
  )
}