/**
 * 43V3R CORE - Adaptive Optimization Monitor
 * 
 * Self-optimizing execution infrastructure with adaptive runtime tuning,
 * predictive scaling, and performance analytics.
 * 
 * Dense optimization interface with tuning cycles, parameter evolution,
 * and self-healing orchestration visualizations.
 */
'use client'

import { useState, useEffect } from 'react'
import {
  Gauge,
  TrendingUp,
  Zap,
  Settings,
  Target,
  Activity,
  RefreshCw,
  Clock,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  ChevronRight,
  Play,
  Pause,
  RotateCcw,
} from 'lucide-react'
import { useCoherenceApi, type AdaptiveProfile, type OptimizationMetric } from '@/lib/coherence-api'
import { ConsolePanel, MetricGrid, MetricValue, StatusDot, ConfidenceBadge, Sparkline, DataTable, TabBar, IconButton, ProgressBar } from '@/components/cognitive/primitives'

// ---- Types ----

interface OptimizationOverview {
  activeProfiles: number
  tuningCycles: number
  bestImprovement: number
  avgScore: number
  parameterChanges: number
}

interface TuningCycle {
  cycle_id: string
  context_key: string
  target_metric: string
  progress: number
  current_score: number
  best_score: number
  state: string
}

// ---- Main Component ----

export default function AdaptiveOptimizationMonitor() {
  const api = useCoherenceApi()
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [overview, setOverview] = useState<OptimizationOverview>({
    activeProfiles: 0,
    tuningCycles: 0,
    bestImprovement: 0,
    avgScore: 0,
    parameterChanges: 0,
  })
  const [profiles, setProfiles] = useState<AdaptiveProfile[]>([])
  const [tuningCycles, setTuningCycles] = useState<TuningCycle[]>([])
  const [selectedProfile, setSelectedProfile] = useState<AdaptiveProfile | null>(null)
  const [optimizationHistory, setOptimizationHistory] = useState<{ iteration: number; score: number; parameters: Record<string, number> }[]>([])
  
  useEffect(() => {
    const loadData = async () => {
      try {
        const mockProfiles: AdaptiveProfile[] = [
          { profile_id: 'prof-001', profile_key: 'render_pipeline', context_key: 'render_queue', parameters: { batch_size: 48, worker_pool: 12, queue_depth: 32 }, baseline_metrics: { throughput: 100, latency: 50 }, current_metrics: { throughput: 142, latency: 23 }, best_score: 0.89, optimization_iterations: 24, profile_state: 'active' },
          { profile_id: 'prof-002', profile_key: 'ai_generation', context_key: 'model_serving', parameters: { max_tokens: 2048, temperature: 0.7 }, baseline_metrics: { quality: 0.75 }, current_metrics: { quality: 0.82 }, best_score: 0.82, optimization_iterations: 18, profile_state: 'active' },
          { profile_id: 'prof-003', profile_key: 'memory_decay', context_key: 'orchestration', parameters: { decay_rate: 0.05, retention_threshold: 0.6 }, baseline_metrics: { recall_rate: 0.7 }, current_metrics: { recall_rate: 0.85 }, best_score: 0.85, optimization_iterations: 12, profile_state: 'active' },
        ]
        
        const mockTuningCycles: TuningCycle[] = [
          { cycle_id: 'cycle_001', context_key: 'render_pipeline', target_metric: 'throughput', progress: 40, current_score: 0.72, best_score: 0.89, state: 'running' },
          { cycle_id: 'cycle_002', context_key: 'ai_generation', target_metric: 'quality', progress: 87, current_score: 0.78, best_score: 0.82, state: 'running' },
          { cycle_id: 'cycle_003', context_key: 'memory_decay', target_metric: 'recall_rate', progress: 100, current_score: 0.85, best_score: 0.85, state: 'completed' },
        ]
        
        // Generate optimization history
        const history: { iteration: number; score: number; parameters: Record<string, number> }[] = []
        let currentScore = 0.5
        let batchSize = 32
        for (let i = 1; i <= 24; i++) {
          currentScore += (Math.random() - 0.3) * 0.05
          currentScore = Math.max(0.3, Math.min(0.95, currentScore))
          batchSize += Math.floor((Math.random() - 0.4) * 8)
          batchSize = Math.max(16, Math.min(64, batchSize))
          history.push({
            iteration: i,
            score: currentScore,
            parameters: { batch_size: batchSize },
          })
        }
        
        setOverview({
          activeProfiles: mockProfiles.length,
          tuningCycles: mockTuningCycles.filter(c => c.state === 'running').length,
          bestImprovement: 0.15,
          avgScore: history.reduce((sum, h) => sum + h.score, 0) / history.length,
          parameterChanges: history.length,
        })
        
        setProfiles(mockProfiles)
        setTuningCycles(mockTuningCycles)
        setOptimizationHistory(history)
        
        if (mockProfiles.length > 0) {
          setSelectedProfile(mockProfiles[0])
        }
      } catch {
        // Use defaults
      }
      setLoading(false)
    }
    
    loadData()
    const interval = setInterval(loadData, 15000)
    return () => clearInterval(interval)
  }, [api])
  
  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Gauge className="h-3 w-3" /> },
    { id: 'profiles', label: 'Profiles', icon: <Settings className="h-3 w-3" /> },
    { id: 'cycles', label: 'Tuning Cycles', icon: <Target className="h-3 w-3" /> },
    { id: 'evolution', label: 'Evolution', icon: <TrendingUp className="h-3 w-3" /> },
  ]
  
  // Generate sparkline data
  const generateSparkline = (data: number[], length = 20): number[] => {
    const start = Math.max(0, data.length - length)
    return data.slice(start, start + length)
  }
  
  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Gauge className="h-5 w-5 text-primary" />
            <span className="font-mono text-sm font-semibold tracking-tight">ADAPTIVE OPTIMIZATION</span>
          </div>
          <div className="h-4 w-px bg-border/50" />
          <StatusDot status={overview.tuningCycles > 0 ? 'degraded' : 'healthy'} />
          <span className="text-[10px] font-mono text-muted-foreground uppercase">
            {overview.tuningCycles} active cycles
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <IconButton icon={<Play className="h-3 w-3" />} tooltip="Start Cycle" />
          <IconButton icon={<Pause className="h-3 w-3" />} tooltip="Pause" />
          <IconButton icon={<RotateCcw className="h-3 w-3" />} tooltip="Reset" />
          <IconButton icon={<RefreshCw className="h-3 w-3" />} onClick={() => setLoading(true)} />
        </div>
      </div>
      
      {/* Metrics Bar */}
      <div className="border-b border-border/50 bg-muted/20 px-4 py-2">
        <MetricGrid columns={5}>
          <MetricValue
            label="Active Profiles"
            value={overview.activeProfiles}
            icon={<Settings className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Tuning Cycles"
            value={overview.tuningCycles}
            icon={<Target className="h-3 w-3" />}
            trend={overview.tuningCycles > 0 ? 'up' : 'stable'}
          />
          <MetricValue
            label="Best Improvement"
            value={`${Math.round(overview.bestImprovement * 100)}%`}
            icon={<Zap className="h-3 w-3" />}
            trend={overview.bestImprovement > 0.1 ? 'up' : 'stable'}
          />
          <MetricValue
            label="Avg Score"
            value={`${Math.round(overview.avgScore * 100)}%`}
            icon={<Gauge className="h-3 w-3" />}
            trend={overview.avgScore > 0.8 ? 'up' : 'stable'}
          />
          <MetricValue
            label="Parameter Changes"
            value={overview.parameterChanges}
            icon={<Activity className="h-3 w-3" />}
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
            <div className="lg:col-span-2">
              <ConsolePanel
                title="Optimization Performance"
                icon={<TrendingUp className="h-4 w-4" />}
                subtitle="Score evolution over iterations"
              >
                <div className="h-64 flex items-center justify-center">
                  <Sparkline
                    data={generateSparkline(optimizationHistory.map(h => h.score), 24)}
                    color="primary"
                    height={200}
                    showLabels
                  />
                </div>
                <div className="grid grid-cols-4 gap-4 mt-4">
                  {[
                    { label: 'Initial Score', value: '50%', icon: <Clock className="h-3 w-3" /> },
                    { label: 'Current Score', value: `${Math.round(optimizationHistory[optimizationHistory.length - 1]?.score * 100 || 0)}%`, icon: <Activity className="h-3 w-3" /> },
                    { label: 'Peak Score', value: `${Math.round(Math.max(...optimizationHistory.map(h => h.score)) * 100)}%`, icon: <Target className="h-3 w-3" /> },
                    { label: 'Improvement', value: `+${Math.round((optimizationHistory[optimizationHistory.length - 1]?.score - optimizationHistory[0]?.score) * 100 || 0)}%`, icon: <Zap className="h-3 w-3" /> },
                  ].map((stat, idx) => (
                    <div key={idx} className="p-3 rounded border border-border/50 text-center">
                      <div className="flex items-center justify-center gap-1 text-muted-foreground mb-1">
                        {stat.icon}
                        <span className="text-[10px]">{stat.label}</span>
                      </div>
                      <div className="text-lg font-mono">{stat.value}</div>
                    </div>
                  ))}
                </div>
              </ConsolePanel>
            </div>
            
            <div>
              <ConsolePanel
                title="Active Tuning Cycles"
                icon={<Target className="h-4 w-4" />}
                subtitle="Optimization progress"
              >
                <div className="space-y-3">
                  {tuningCycles.map(cycle => (
                    <div key={cycle.cycle_id} className="p-4 rounded border border-border/50">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-mono">{cycle.cycle_id}</span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                          cycle.state === 'running' ? 'bg-blue-500/10 text-blue-500' :
                          cycle.state === 'completed' ? 'bg-green-500/10 text-green-500' :
                          'bg-muted text-muted-foreground'
                        }`}>
                          {cycle.state}
                        </span>
                      </div>
                      
                      <div className="space-y-2 text-xs">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Target</span>
                          <span className="font-mono">{cycle.target_metric}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Context</span>
                          <span className="font-mono">{cycle.context_key}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Best Score</span>
                          <span className="font-mono text-green-500">{Math.round(cycle.best_score * 100)}%</span>
                        </div>
                      </div>
                      
                      <div className="mt-3">
                        <div className="flex items-center justify-between text-[10px] mb-1">
                          <span className="text-muted-foreground">Progress</span>
                          <span className="font-mono">{Math.round(cycle.progress)}%</span>
                        </div>
                        <ProgressBar value={cycle.progress} showValue={false} color={cycle.state === 'completed' ? 'success' : 'primary'} />
                      </div>
                    </div>
                  ))}
                </div>
              </ConsolePanel>
            </div>
          </div>
        )}
        
        {activeTab === 'profiles' && (
          <div className="grid gap-4 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <ConsolePanel
                title="Adaptive Profiles"
                icon={<Settings className="h-4 w-4" />}
                subtitle={`${profiles.length} profiles`}
              >
                <div className="space-y-3">
                  {profiles.map(profile => (
                    <div
                      key={profile.profile_id}
                      className={`p-4 rounded border transition-colors cursor-pointer ${
                        selectedProfile?.profile_id === profile.profile_id
                          ? 'border-primary/50 bg-primary/5'
                          : 'border-transparent hover:border-border hover:bg-muted/30'
                      }`}
                      onClick={() => setSelectedProfile(profile)}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="text-sm font-medium">{profile.profile_key}</h4>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">
                              {profile.context_key}
                            </span>
                            <span className="text-[10px] text-muted-foreground">
                              {profile.optimization_iterations} iterations
                            </span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-mono text-green-500">
                            {Math.round(profile.best_score * 100)}%
                          </div>
                          <div className="text-[10px] text-muted-foreground">best score</div>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-2 text-[10px]">
                        {Object.entries(profile.parameters).slice(0, 3).map(([key, value]) => (
                          <div key={key} className="p-2 rounded bg-muted/50">
                            <div className="text-muted-foreground capitalize">{key.replace('_', ' ')}</div>
                            <div className="font-mono">{String(value)}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </ConsolePanel>
            </div>
            
            <div>
              <ConsolePanel
                title="Profile Parameters"
                icon={<Settings className="h-4 w-4" />}
                subtitle={selectedProfile?.profile_key || 'Select profile'}
              >
                {selectedProfile ? (
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <span className="text-[10px] text-muted-foreground uppercase">Current Parameters</span>
                      {Object.entries(selectedProfile.parameters).map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between p-2 rounded bg-muted/50">
                          <span className="text-xs capitalize">{key.replace('_', ' ')}</span>
                          <span className="text-sm font-mono">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                    
                    <div className="pt-2 border-t border-border/50">
                      <span className="text-[10px] text-muted-foreground uppercase">Performance</span>
                      <div className="grid grid-cols-2 gap-2 mt-2">
                        <div className="text-center p-2 rounded bg-muted/50">
                          <div className="text-lg font-mono text-green-500">
                            {Math.round(selectedProfile.best_score * 100)}%
                          </div>
                          <div className="text-[10px] text-muted-foreground">Best Score</div>
                        </div>
                        <div className="text-center p-2 rounded bg-muted/50">
                          <div className="text-lg font-mono">
                            {selectedProfile.optimization_iterations}
                          </div>
                          <div className="text-[10px] text-muted-foreground">Iterations</div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="pt-2 border-t border-border/50">
                      <span className="text-[10px] text-muted-foreground uppercase">Suggested Parameters</span>
                      <div className="mt-2 space-y-1">
                        {[
                          { param: 'batch_size', current: 48, suggested: 56 },
                          { param: 'worker_pool', current: 12, suggested: 14 },
                        ].map((sug, idx) => (
                          <div key={idx} className="flex items-center justify-between p-2 rounded bg-green-500/10">
                            <span className="text-xs font-mono">{sug.param}</span>
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] text-muted-foreground line-through">{sug.current}</span>
                              <ArrowRight className="h-3 w-3" />
                              <span className="text-xs font-mono text-green-500">{sug.suggested}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground text-sm">
                    Select a profile to view parameters
                  </div>
                )}
              </ConsolePanel>
            </div>
          </div>
        )}
        
        {activeTab === 'cycles' && (
          <ConsolePanel
            title="Tuning Cycles"
            icon={<Target className="h-4 w-4" />}
            subtitle="Optimization cycle management"
          >
            <div className="space-y-4">
              {tuningCycles.map(cycle => (
                <div key={cycle.cycle_id} className="p-4 rounded border border-border/50">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h4 className="text-sm font-mono">{cycle.cycle_id}</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{cycle.context_key}</span>
                        <span className="text-[10px] text-muted-foreground">→</span>
                        <span className="text-[10px] font-mono text-green-500">{cycle.target_metric}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {cycle.state === 'running' ? (
                        <button className="p-1 rounded hover:bg-muted transition-colors">
                          <Pause className="h-4 w-4" />
                        </button>
                      ) : (
                        <button className="p-1 rounded hover:bg-muted transition-colors">
                          <Play className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-4 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-lg font-mono">{Math.round(cycle.progress)}%</div>
                      <div className="text-[10px] text-muted-foreground">Progress</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-mono">{cycle.current_score.toFixed(2)}</div>
                      <div className="text-[10px] text-muted-foreground">Current</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-mono text-green-500">{cycle.best_score.toFixed(2)}</div>
                      <div className="text-[10px] text-muted-foreground">Best</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-mono">{cycle.iterations || 24}</div>
                      <div className="text-[10px] text-muted-foreground">Iterations</div>
                    </div>
                  </div>
                  
                  <ProgressBar
                    value={cycle.progress}
                    showValue
                    color={cycle.state === 'completed' ? 'success' : 'primary'}
                  />
                </div>
              ))}
            </div>
          </ConsolePanel>
        )}
        
        {activeTab === 'evolution' && (
          <ConsolePanel
            title="Parameter Evolution"
            icon={<TrendingUp className="h-4 w-4" />}
            subtitle="Parameter changes over iterations"
          >
            <div className="space-y-4">
              {Object.keys(optimizationHistory[0]?.parameters || {}).map(param => (
                <div key={param} className="p-4 rounded border border-border/50">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-medium capitalize">{param.replace('_', ' ')}</span>
                    <span className="text-xs font-mono">
                      {optimizationHistory[0]?.parameters[param]} → {optimizationHistory[optimizationHistory.length - 1]?.parameters[param]}
                    </span>
                  </div>
                  <Sparkline
                    data={generateSparkline(optimizationHistory.map(h => h.parameters[param] || 0))}
                    color={param === 'batch_size' ? 'primary' : 'success'}
                    height={60}
                  />
                </div>
              ))}
            </div>
          </ConsolePanel>
        )}
      </div>
    </div>
  )
}