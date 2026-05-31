"""
Cognitive Runtime Center - Adaptive orchestration dashboard
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Activity,
  Brain,
  Cpu,
  Zap,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Target,
  Award,
  RefreshCw,
  Settings,
} from 'lucide-react'

interface PredictionData {
  id: string
  type: 'duration' | 'queue_time' | 'failure' | 'resource_need'
  predicted_value: number
  confidence: number
  predicted_for: string
}

interface InsightData {
  id: string
  title: string
  description: string
  impact_score: number
  type: string
  is_applied: boolean
}

interface HeuristicData {
  name: string
  type: string
  hit_rate: number
  success_rate: number
  last_used: string
}

interface PolicyData {
  name: string
  type: string
  is_active: boolean
  trigger_count: number
}

export function CognitiveDashboard() {
  const [activeTab, setActiveTab] = useState<'overview' | 'predictions' | 'insights' | 'heuristics' | 'policies'>('overview')
  const [predictions, setPredictions] = useState<PredictionData[]>([])
  const [insights, setInsights] = useState<InsightData[]>([])
  const [heuristics, setHeuristics] = useState<HeuristicData[]>([])
  const [policies, setPolicies] = useState<PolicyData[]>([])

  useEffect(() => {
    setPredictions([
      { id: 'pred-1', type: 'duration', predicted_value: 245, confidence: 0.85, predicted_for: new Date(Date.now() + 245000).toISOString() },
      { id: 'pred-2', type: 'queue_time', predicted_value: 45, confidence: 0.78, predicted_for: new Date(Date.now() + 45000).toISOString() },
      { id: 'pred-3', type: 'failure', predicted_value: 0.12, confidence: 0.72, predicted_for: new Date(Date.now() + 600000).toISOString() },
      { id: 'pred-4', type: 'resource_need', predicted_value: 2048, confidence: 0.91, predicted_for: new Date(Date.now() + 300000).toISOString() },
    ])

    setInsights([
      { id: 'ins-1', title: 'Parallelize rendering steps', description: 'Sequential steps 3-5 can be parallelized', impact_score: 0.85, type: 'optimization', is_applied: false },
      { id: 'ins-2', title: 'Increase batch size', description: 'Current batch size is suboptimal for throughput', impact_score: 0.72, type: 'performance', is_applied: true },
      { id: 'ins-3', title: 'Route to faster workers', description: 'Workers 4-6 have lower latency', impact_score: 0.68, type: 'scheduling', is_applied: false },
      { id: 'ins-4', title: 'Pre-cache media assets', description: 'Common assets can be pre-cached', impact_score: 0.61, type: 'resource', is_applied: false },
    ])

    setHeuristics([
      { name: 'priority_weight', type: 'scheduling', hit_rate: 156, success_rate: 0.89, last_used: new Date(Date.now() - 300000).toISOString() },
      { name: 'size_optimization', type: 'scheduling', hit_rate: 89, success_rate: 0.76, last_used: new Date(Date.now() - 600000).toISOString() },
      { name: 'energy_curve', type: 'composition', hit_rate: 45, success_rate: 0.82, last_used: new Date(Date.now() - 1200000).toISOString() },
      { name: 'beat_alignment', type: 'composition', hit_rate: 67, success_rate: 0.94, last_used: new Date(Date.now() - 900000).toISOString() },
    ])

    setPolicies([
      { name: 'auto_scale', type: 'scaling', is_active: true, trigger_count: 23 },
      { name: 'failover_route', type: 'failover', is_active: true, trigger_count: 8 },
      { name: 'priority_bump', type: 'scheduling', is_active: true, trigger_count: 45 },
      { name: 'optimize_batch', type: 'optimization', is_active: false, trigger_count: 12 },
    ])
  }, [])

  const getPredictionIcon = (type: string) => {
    switch (type) {
      case 'duration': return <Clock className="w-4 h-4" />
      case 'queue_time': return <Activity className="w-4 h-4" />
      case 'failure': return <AlertTriangle className="w-4 h-4" />
      case 'resource_need': return <Cpu className="w-4 h-4" />
      default: return <Target className="w-4 h-4" />
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.85) return 'text-green-500'
    if (confidence >= 0.7) return 'text-yellow-500'
    return 'text-red-500'
  }

  const formatValue = (type: string, value: number) => {
    switch (type) {
      case 'duration': return `${value}s`
      case 'queue_time': return `${value}s`
      case 'failure': return `${(value * 100).toFixed(1)}%`
      case 'resource_need': return `${value}MB`
      default: return value.toString()
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-card">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-primary" />
            <h1 className="text-lg font-semibold">Cognitive Runtime</h1>
          </div>
          <div className="flex items-center gap-4 ml-8">
            <MetricDisplay icon={<Target className="w-4 h-4" />} label="Active Predictions" value={predictions.filter(p => p.confidence > 0.7).length.toString()} />
            <MetricDisplay icon={<Zap className="w-4 h-4" />} label="Insights" value={insights.filter(i => !i.is_applied).length.toString()} />
            <MetricDisplay icon={<Award className="w-4 h-4" />} label="Heuristics" value={heuristics.length.toString()} />
            <MetricDisplay icon={<Settings className="w-4 h-4" />} label="Policies" value={policies.filter(p => p.is_active).length.toString()} />
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1 px-3 py-1.5 text-sm hover:bg-accent rounded">
            <RefreshCw className="w-4 h-4" />Refresh
          </button>
        </div>
      </div>

      <div className="flex border-b border-border px-4">
        {(['overview', 'predictions', 'insights', 'heuristics', 'policies'] as const).map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)} className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === tab ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}`}>
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-auto p-4">
        {activeTab === 'overview' && (
          <div className="space-y-4">
            <div className="grid grid-cols-4 gap-4">
              <MetricCard label="Prediction Accuracy" value="84.5%" icon={<Target className="w-5 h-5" />} trend="up" />
              <MetricCard label="Insights Applied" value={insights.filter(i => i.is_applied).length.toString()} icon={<Zap className="w-5 h-5" />} trend="stable" />
              <MetricCard label="Heuristic Success" value={`${Math.round(heuristics.reduce((sum, h) => sum + h.success_rate, 0) / heuristics.length * 100)}%`} icon={<Award className="w-5 h-5" />} trend="up" />
              <MetricCard label="Policy Triggers" value={policies.reduce((sum, p) => sum + p.trigger_count, 0).toString()} icon={<Activity className="w-5 h-5" />} trend="stable" />
            </div>

            <div className="border border-border rounded-lg overflow-hidden">
              <div className="px-4 py-3 border-b border-border bg-card"><h3 className="text-sm font-medium">Recent Predictions</h3></div>
              <div className="divide-y divide-border">
                {predictions.slice(0, 3).map((pred) => (
                  <div key={pred.id} className="flex items-center justify-between px-4 py-3">
                    <div className="flex items-center gap-3">
                      <span className="text-muted-foreground">{getPredictionIcon(pred.type)}</span>
                      <div>
                        <p className="text-sm font-medium capitalize">{pred.type.replace('_', ' ')}</p>
                        <p className="text-xs text-muted-foreground">Predicted: {formatValue(pred.type, pred.predicted_value)}</p>
                      </div>
                    </div>
                    <span className={`text-sm font-mono ${getConfidenceColor(pred.confidence)}`}>{Math.round(pred.confidence * 100)}%</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="border border-border rounded-lg overflow-hidden">
              <div className="px-4 py-3 border-b border-border bg-card"><h3 className="text-sm font-medium">Actionable Insights</h3></div>
              <div className="divide-y divide-border">
                {insights.filter(i => !i.is_applied).map((insight) => (
                  <div key={insight.id} className="px-4 py-3 hover:bg-card/50 cursor-pointer">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium">{insight.title}</p>
                        <p className="text-xs text-muted-foreground">{insight.description}</p>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${insight.impact_score > 0.8 ? 'bg-green-500/10 text-green-500' : insight.impact_score > 0.6 ? 'bg-yellow-500/10 text-yellow-500' : 'bg-gray-500/10 text-gray-400'}`}>
                        {(insight.impact_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'predictions' && (
          <div className="border border-border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-card">
                <tr className="text-left text-xs text-muted-foreground uppercase tracking-wider">
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Predicted Value</th>
                  <th className="px-4 py-3">Confidence</th>
                  <th className="px-4 py-3">Predicted For</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((pred) => (
                  <tr key={pred.id} className="border-t border-border">
                    <td className="px-4 py-3"><div className="flex items-center gap-2">{getPredictionIcon(pred.type)}<span className="text-sm capitalize">{pred.type.replace('_', ' ')}</span></div></td>
                    <td className="px-4 py-3 font-mono">{formatValue(pred.type, pred.predicted_value)}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-muted rounded-full overflow-hidden"><div className={`h-full ${getConfidenceColor(pred.confidence).replace('text-', 'bg-')}`} style={{ width: `${pred.confidence * 100}%` }} /></div>
                        <span className={`text-sm ${getConfidenceColor(pred.confidence)}`}>{(pred.confidence * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{new Date(pred.predicted_for).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="space-y-4">
            {insights.map((insight) => (
              <div key={insight.id} className={`border rounded-lg p-4 ${insight.is_applied ? 'opacity-60' : ''}`}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {insight.is_applied ? <CheckCircle2 className="w-4 h-4 text-green-500" /> : <Zap className="w-4 h-4 text-yellow-500" />}
                    <h3 className="text-sm font-medium">{insight.title}</h3>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${insight.impact_score > 0.8 ? 'bg-green-500/10 text-green-500' : insight.impact_score > 0.6 ? 'bg-yellow-500/10 text-yellow-500' : 'bg-gray-500/10 text-gray-400'}`}>
                    {(insight.impact_score * 100).toFixed(0)}% impact
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">{insight.description}</p>
                <div className="flex items-center gap-4 mt-3">
                  <span className="text-xs text-muted-foreground capitalize">{insight.type}</span>
                  {!insight.is_applied && <button className="text-xs text-primary hover:underline">Apply Insight</button>}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'heuristics' && (
          <div className="border border-border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-card">
                <tr className="text-left text-xs text-muted-foreground uppercase tracking-wider">
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Hits</th>
                  <th className="px-4 py-3">Success Rate</th>
                  <th className="px-4 py-3">Last Used</th>
                </tr>
              </thead>
              <tbody>
                {heuristics.map((h) => (
                  <tr key={h.name} className="border-t border-border">
                    <td className="px-4 py-3 font-mono text-sm">{h.name}</td>
                    <td className="px-4 py-3 text-sm capitalize">{h.type}</td>
                    <td className="px-4 py-3 font-mono text-sm">{h.hit_rate}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-muted rounded-full overflow-hidden"><div className="h-full bg-primary" style={{ width: `${h.success_rate * 100}%` }} /></div>
                        <span className="text-sm">{(h.success_rate * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{new Date(h.last_used).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'policies' && (
          <div className="border border-border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-card">
                <tr className="text-left text-xs text-muted-foreground uppercase tracking-wider">
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Triggers</th>
                </tr>
              </thead>
              <tbody>
                {policies.map((policy) => (
                  <tr key={policy.name} className="border-t border-border">
                    <td className="px-4 py-3 font-mono text-sm">{policy.name}</td>
                    <td className="px-4 py-3 text-sm capitalize">{policy.type}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${policy.is_active ? 'bg-green-500/10 text-green-500' : 'bg-gray-500/10 text-gray-400'}`}>
                        {policy.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-sm">{policy.trigger_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

function MetricDisplay({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-muted-foreground">{icon}</span>
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="text-sm font-semibold">{value}</p>
      </div>
    </div>
  )
}

function MetricCard({ label, value, icon, trend }: { label: string; value: string; icon: React.ReactNode; trend?: 'up' | 'down' | 'stable' }) {
  return (
    <div className="bg-card border border-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="text-muted-foreground">{icon}</span>
      </div>
      <p className="text-2xl font-semibold">{value}</p>
      {trend && <div className="mt-2">{trend === 'up' && <TrendingUp className="w-4 h-4 text-green-500" />}{trend === 'down' && <TrendingUp className="w-4 h-4 text-red-500 transform rotate-180" />}{trend === 'stable' && <span className="text-xs text-muted-foreground">stable</span>}</div>}
    </div>
  )
}