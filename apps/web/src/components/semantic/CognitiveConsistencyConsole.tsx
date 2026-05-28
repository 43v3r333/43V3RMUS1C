/**
 * 43V3R CORE - Cognitive Consistency Console
 * 
 * Production-grade cognition consistency monitoring interface.
 * Unified cognitive awareness, reasoning standards, and semantic memory visualization.
 */
'use client'

import { useState, useEffect } from 'react'
import {
  Brain,
  Database,
  Network,
  GitBranch,
  RefreshCw,
  Search,
  Filter,
  TrendingUp,
  TrendingDown,
  Activity,
  Clock,
  Shield,
  Target,
  Layers,
  MemoryStick,
  Gauge,
  AlertTriangle,
  CheckCircle2,
} from 'lucide-react'
import { ConsolePanel, MetricGrid, MetricValue, StatusDot, DataTable, TabBar, IconButton, ProgressBar, ConfidenceBadge } from '@/components/cognitive/primitives'

// ---- Types ----

interface ConsistencyMetrics {
  totalMemories: number
  activeConsistency: number
  alignmentScore: number
  coherenceScore: number
  reasoningStandards: number
  cognitionNodes: number
}

interface SemanticMemory {
  memory_id: string
  memory_key: string
  scope: 'semantic' | 'episodic' | 'procedural' | 'evaluative' | 'strategic'
  memory_type: string
  subject: string
  title: string
  importance: number
  confidence: number
  access_count: number
  is_pinned: boolean
  created_at: string
}

interface ConsistencyState {
  state_id: string
  scope: string
  domain: string
  consistency_state: 'aligned' | 'deviating' | 'reconciling' | 'conflicted' | 'stabilized'
  alignment_score: number
  coherence_score: number
  last_assessed_at: string
}

interface SharedReasoning {
  reasoning_id: string
  reasoning_key: string
  reasoning_type: string
  name: string
  confidence_threshold: number
  is_active: boolean
}

// ---- Mock Data Generators ----

function generateMockMemories(): SemanticMemory[] {
  return [
    { memory_id: 'm1', memory_key: 'mem.workflow.rendersuccess', scope: 'episodic', memory_type: 'workflow_audit', subject: 'render-alpha-001', title: 'Pipeline optimization success', importance: 0.85, confidence: 0.92, access_count: 24, is_pinned: true, created_at: new Date().toISOString() },
    { memory_id: 'm2', memory_key: 'mem.semantic.execution规律', scope: 'semantic', memory_type: 'execution_pattern', subject: 'ai-generation-v2', title: 'Generation pattern recognized', importance: 0.78, confidence: 0.88, access_count: 12, is_pinned: false, created_at: new Date(Date.now() - 3600000).toISOString() },
    { memory_id: 'm3', memory_key: 'mem.procedural.render步骤', scope: 'procedural', memory_type: 'render_workflow', subject: 'compose-music-v3', title: 'Multi-pass rendering sequence', importance: 0.72, confidence: 0.95, access_count: 8, is_pinned: false, created_at: new Date(Date.now() - 7200000).toISOString() },
    { memory_id: 'm4', memory_key: 'mem.evaluative.quality评分', scope: 'evaluative', memory_type: 'quality_metric', subject: 'batch-render-42', title: 'Quality threshold patterns', importance: 0.65, confidence: 0.81, access_count: 5, is_pinned: false, created_at: new Date(Date.now() - 14400000).toISOString() },
    { memory_id: 'm5', memory_key: 'mem.strategic.resource分配', scope: 'strategic', memory_type: 'optimization_policy', subject: 'resource-allocation', title: 'GPU utilization strategy', importance: 0.90, confidence: 0.94, access_count: 31, is_pinned: true, created_at: new Date(Date.now() - 28800000).toISOString() },
    { memory_id: 'm6', memory_key: 'mem.episodic.failover事件', scope: 'episodic', memory_type: 'incident_report', subject: 'node-failover-17', title: 'Automatic failover recovery', importance: 0.82, confidence: 0.97, access_count: 15, is_pinned: false, created_at: new Date(Date.now() - 43200000).toISOString() },
  ]
}

function generateMockStates(): ConsistencyState[] {
  return [
    { state_id: 'cs1', scope: 'semantic', domain: 'orchestration', consistency_state: 'aligned', alignment_score: 0.95, coherence_score: 0.92, last_assessed_at: new Date().toISOString() },
    { state_id: 'cs2', scope: 'episodic', domain: 'execution_tracking', consistency_state: 'stabilized', alignment_score: 0.88, coherence_score: 0.85, last_assessed_at: new Date(Date.now() - 300000).toISOString() },
    { state_id: 'cs3', scope: 'procedural', domain: 'workflow_steps', consistency_state: 'aligned', alignment_score: 0.97, coherence_score: 0.94, last_assessed_at: new Date(Date.now() - 600000).toISOString() },
    { state_id: 'cs4', scope: 'evaluative', domain: 'quality_metrics', consistency_state: 'deviating', alignment_score: 0.72, coherence_score: 0.68, last_assessed_at: new Date(Date.now() - 900000).toISOString() },
    { state_id: 'cs5', scope: 'strategic', domain: 'resource_optimization', consistency_state: 'reconciling', alignment_score: 0.65, coherence_score: 0.70, last_assessed_at: new Date(Date.now() - 1200000).toISOString() },
  ]
}

function generateMockReasoning(): SharedReasoning[] {
  return [
    { reasoning_id: 'sr1', reasoning_key: 'reason.deductive.workflow', reasoning_type: 'deductive', name: 'Deductive Workflow Reasoning', confidence_threshold: 0.85, is_active: true },
    { reasoning_id: 'sr2', reasoning_key: 'reason.inductive.pattern', reasoning_type: 'inductive', name: 'Inductive Pattern Recognition', confidence_threshold: 0.80, is_active: true },
    { reasoning_id: 'sr3', reasoning_key: 'reason.abductive.diagnosis', reasoning_type: 'abductive', name: 'Abductive Diagnostics', confidence_threshold: 0.75, is_active: true },
    { reasoning_id: 'sr4', reasoning_key: 'reason.analogical.transfer', reasoning_type: 'analogical', name: 'Analogical Transfer Learning', confidence_threshold: 0.70, is_active: false },
    { reasoning_id: 'sr5', reasoning_key: 'reason.causal.propagation', reasoning_type: 'causal', name: 'Causal Effect Propagation', confidence_threshold: 0.88, is_active: true },
  ]
}

// ---- Main Component ----

export default function CognitiveConsistencyConsole() {
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [metrics, setMetrics] = useState<ConsistencyMetrics>({
    totalMemories: 0, activeConsistency: 0, alignmentScore: 0, coherenceScore: 0, reasoningStandards: 0, cognitionNodes: 0,
  })
  const [memories, setMemories] = useState<SemanticMemory[]>([])
  const [states, setStates] = useState<ConsistencyState[]>([])
  const [reasoning, setReasoning] = useState<SharedReasoning[]>([])
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    const loadData = async () => {
      try {
        const mockMemories = generateMockMemories()
        const mockStates = generateMockStates()
        const mockReasoning = generateMockReasoning()

        const stableStates = mockStates.filter(s => s.consistency_state === 'aligned' || s.consistency_state === 'stabilized')
        const avgAlignment = mockStates.reduce((sum, s) => sum + s.alignment_score, 0) / mockStates.length
        const avgCoherence = mockStates.reduce((sum, s) => sum + s.coherence_score, 0) / mockStates.length

        setMetrics({
          totalMemories: mockMemories.length,
          activeConsistency: stableStates.length,
          alignmentScore: avgAlignment,
          coherenceScore: avgCoherence,
          reasoningStandards: mockReasoning.filter(r => r.is_active).length,
          cognitionNodes: mockStates.length,
        })

        setMemories(mockMemories)
        setStates(mockStates)
        setReasoning(mockReasoning)
      } catch {
        // Use defaults
      }
      setLoading(false)
    }

    loadData()
  }, [])

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Brain className="h-3 w-3" /> },
    { id: 'memories', label: 'Memory', icon: <Database className="h-3 w-3" />, badge: memories.length },
    { id: 'consistency', label: 'Consistency', icon: <Shield className="h-3 w-3" />, badge: states.length },
    { id: 'reasoning', label: 'Reasoning', icon: <Target className="h-3 w-3" />, badge: reasoning.length },
  ]

  const filteredMemories = memories.filter(m =>
    !searchQuery ||
    m.memory_key.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.subject.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const getStateColor = (state: string) => {
    if (state === 'aligned' || state === 'stabilized') return 'text-green-500'
    if (state === 'deviating') return 'text-yellow-500'
    if (state === 'reconciling') return 'text-blue-500'
    if (state === 'conflicted') return 'text-red-500'
    return 'text-muted-foreground'
  }

  const getScopeIcon = (scope: string) => {
    const icons: Record<string, React.ReactNode> = {
      semantic: <Database className="h-3 w-3" />,
      episodic: <Clock className="h-3 w-3" />,
      procedural: <GitBranch className="h-3 w-3" />,
      evaluative: <Gauge className="h-3 w-3" />,
      strategic: <Target className="h-3 w-3" />,
    }
    return icons[scope] || <Layers className="h-3 w-3" />
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            <span className="font-mono text-sm font-semibold tracking-tight">COGNITIVE CONSISTENCY</span>
          </div>
          <div className="h-4 w-px bg-border/50" />
          <StatusDot status="active" size="sm" />
          <span className="text-[10px] font-mono text-muted-foreground uppercase">
            {metrics.activeConsistency}/{metrics.cognitionNodes} aligned
          </span>
        </div>

        <div className="flex items-center gap-2">
          <IconButton icon={<RefreshCw className="h-3 w-3" />} onClick={() => setLoading(true)} />
        </div>
      </div>

      {/* Metrics Bar */}
      <div className="border-b border-border/50 bg-muted/20 px-4 py-2">
        <MetricGrid columns={6}>
          <MetricValue
            label="Total Memory"
            value={metrics.totalMemories}
            icon={<Database className="h-3 w-3" />}
            trend="up"
          />
          <MetricValue
            label="Alignment"
            value={`${(metrics.alignmentScore * 100).toFixed(0)}%`}
            icon={<Shield className="h-3 w-3" />}
            trend={metrics.alignmentScore > 0.85 ? 'up' : metrics.alignmentScore > 0.7 ? 'stable' : 'down'}
            confidence={metrics.alignmentScore}
          />
          <MetricValue
            label="Coherence"
            value={`${(metrics.coherenceScore * 100).toFixed(0)}%`}
            icon={<Network className="h-3 w-3" />}
            trend={metrics.coherenceScore > 0.85 ? 'up' : 'stable'}
            confidence={metrics.coherenceScore}
          />
          <MetricValue
            label="Reasoning"
            value={metrics.reasoningStandards}
            icon={<Target className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Nodes"
            value={metrics.cognitionNodes}
            icon={<GitBranch className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Stability"
            value={`${((metrics.alignmentScore + metrics.coherenceScore) / 2 * 100).toFixed(0)}%`}
            icon={<Activity className="h-3 w-3" />}
            trend="stable"
          />
        </MetricGrid>
      </div>

      {/* Tabs */}
      <TabBar tabs={tabs} active={activeTab} onChange={setActiveTab} />

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {activeTab === 'overview' && (
          <div className="grid gap-4 lg:grid-cols-2">
            <ConsolePanel title="Memory Scope Distribution" icon={<MemoryStick className="h-4 w-4" />} subtitle="By cognitive scope">
              <div className="space-y-3">
                {['semantic', 'episodic', 'procedural', 'evaluative', 'strategic'].map(scope => {
                  const count = memories.filter(m => m.scope === scope).length
                  const total = memories.length || 1
                  return (
                    <div key={scope} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          {getScopeIcon(scope)}
                          <span className="text-muted-foreground capitalize">{scope}</span>
                        </div>
                        <span className="font-mono">{count}</span>
                      </div>
                      <ProgressBar value={(count / total) * 100} showValue={false} color={count > 0 ? 'primary' : 'warning'} />
                    </div>
                  )
                })}
              </div>
            </ConsolePanel>

            <ConsolePanel title="Consistency States" icon={<Shield className="h-4 w-4" />} subtitle="Current alignment">
              <DataTable
                columns={[
                  { key: 'domain', label: 'Domain', width: '30%' },
                  { key: 'state', label: 'State', width: '25%' },
                  { key: 'alignment', label: 'Alignment', width: '25%' },
                  { key: 'coherence', label: 'Coherence', width: '20%' },
                ]}
                rows={states.map(s => ({
                  domain: <span className="text-xs font-mono">{s.domain}</span>,
                  state: (
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${s.consistency_state === 'aligned' || s.consistency_state === 'stabilized' ? 'bg-green-500/10 text-green-500' : s.consistency_state === 'deviating' ? 'bg-yellow-500/10 text-yellow-500' : s.consistency_state === 'reconciling' ? 'bg-blue-500/10 text-blue-500' : 'bg-red-500/10 text-red-500'}`}>
                      {s.consistency_state}
                    </span>
                  ),
                  alignment: <ConfidenceBadge value={s.alignment_score} showLabel={false} />,
                  coherence: <ConfidenceBadge value={s.coherence_score} showLabel={false} />,
                }))}
              />
            </ConsolePanel>

            <ConsolePanel title="Recent Memories" icon={<Database className="h-4 w-4" />} subtitle="High importance">
              <DataTable
                columns={[
                  { key: 'title', label: 'Memory', width: '35/' },
                  { key: 'scope', label: 'Scope', width: '20%' },
                  { key: 'importance', label: 'Importance', width: '20%' },
                  { key: 'confidence', label: 'Confidence', width: '25%' },
                ]}
                rows={memories.filter(m => m.importance > 0.7).slice(0, 5).map(m => ({
                  title: (
                    <div className="flex items-center gap-2">
                      {m.is_pinned && <span className="text-yellow-500 text-xs">★</span>}
                      <span className="text-xs truncate">{m.title}</span>
                    </div>
                  ),
                  scope: (
                    <div className="flex items-center gap-1">
                      {getScopeIcon(m.scope)}
                      <span className="text-[10px] capitalize">{m.scope}</span>
                    </div>
                  ),
                  importance: <ProgressBar value={m.importance * 100} showValue={false} color={m.importance >= 0.8 ? 'success' : 'primary'} />,
                  confidence: <ConfidenceBadge value={m.confidence} showLabel={false} />,
                }))}
              />
            </ConsolePanel>

            <ConsolePanel title="Reasoning Standards" icon={<Target className="h-4 w-4" />} subtitle="Active reasoning">
              <DataTable
                columns={[
                  { key: 'name', label: 'Standard', width: '40%' },
                  { key: 'type', label: 'Type', width: '25%' },
                  { key: 'threshold', label: 'Threshold', width: '20%' },
                  { key: 'active', label: 'Status', width: '15%' },
                ]}
                rows={reasoning.slice(0, 5).map(r => ({
                  name: <span className="text-xs truncate block max-w-[120px]">{r.name}</span>,
                  type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{r.reasoning_type}</span>,
                  threshold: <span className="font-mono text-xs">{Math.round(r.confidence_threshold * 100)}%</span>,
                  active: r.is_active ? <StatusDot status="active" size="sm" /> : <StatusDot status="idle" size="sm" />,
                }))}
              />
            </ConsolePanel>
          </div>
        )}

        {activeTab === 'memories' && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3 w-3 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Search memories..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full h-8 pl-9 pr-3 text-xs border border-border rounded bg-background"
                />
              </div>
            </div>

            <ConsolePanel title="Semantic Memory Registry" icon={<Database className="h-4 w-4" />} subtitle={`${filteredMemories.length} memories`}>
              <DataTable
                columns={[
                  { key: 'memory_key', label: 'Memory Key', width: '25%' },
                  { key: 'title', label: 'Title', width: '25%' },
                  { key: 'scope', label: 'Scope', width: '15%' },
                  { key: 'importance', label: 'Importance', width: '15%' },
                  { key: 'confidence', label: 'Confidence', width: '10%' },
                  { key: 'access', label: 'Access', width: '10%' },
                ]}
                rows={filteredMemories.map(m => ({
                  memory_key: <span className="font-mono text-xs truncate block max-w-[150px]">{m.memory_key}</span>,
                  title: (
                    <div className="flex items-center gap-1">
                      {m.is_pinned && <span className="text-yellow-500">★</span>}
                      <span className="text-xs truncate">{m.title}</span>
                    </div>
                  ),
                  scope: (
                    <div className="flex items-center gap-1">
                      {getScopeIcon(m.scope)}
                      <span className="text-[10px] capitalize">{m.scope}</span>
                    </div>
                  ),
                  importance: <ProgressBar value={m.importance * 100} showValue={false} color={m.importance >= 0.8 ? 'success' : 'primary'} />,
                  confidence: <ConfidenceBadge value={m.confidence} showLabel={false} />,
                  access: <span className="font-mono text-xs text-muted-foreground">{m.access_count}</span>,
                }))}
              />
            </ConsolePanel>
          </div>
        )}

        {activeTab === 'consistency' && (
          <ConsolePanel title="Consistency State Monitor" icon={<Shield className="h-4 w-4" />} subtitle="Real-time alignment tracking">
            <DataTable
              columns={[
                { key: 'domain', label: 'Domain', width: '20%' },
                { key: 'scope', label: 'Scope', width: '15%' },
                { key: 'state', label: 'State', width: '15%' },
                { key: 'alignment', label: 'Alignment', width: '20%' },
                { key: 'coilience', label: 'Coherence', width: '20%' },
                { key: 'assessed', label: 'Last Assessed', width: '10%' },
              ]}
              rows={states.map(s => ({
                domain: <span className="font-mono text-xs">{s.domain}</span>,
                scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted capitalize">{s.scope}</span>,
                state: <span className={`text-xs ${getStateColor(s.consistency_state)}`}>{s.consistency_state}</span>,
                alignment: <ProgressBar value={s.alignment_score * 100} showValue color={s.alignment_score >= 0.8 ? 'success' : s.alignment_score >= 0.6 ? 'warning' : 'error'} />,
                coherg: <ProgressBar value={s.coherence_score * 100} showValue color={s.coherence_score >= 0.8 ? 'success' : s.coherence_score >= 0.6 ? 'warning' : 'error'} />,
                assessed: <span className="text-[10px] text-muted-foreground">{new Date(s.last_assessed_at).toLocaleTimeString()}</span>,
              }))}
            />
          </ConsolePanel>
        )}

        {activeTab === 'reasoning' && (
          <ConsolePanel title="Shared Reasoning Standards" icon={<Target className="h-4 w-4" />} subtitle={`${reasoning.filter(r => r.is_active).length} active`}>
            <DataTable
              columns={[
                { key: 'name', label: 'Standard', width: '35%' },
                { key: 'key', label: 'Key', width: '25%' },
                { key: 'type', label: 'Type', width: '15%' },
                { key: 'threshold', label: 'Threshold', width: '15%' },
                { key: 'status', label: 'Status', width: '10%' },
              ]}
              rows={reasoning.map(r => ({
                name: <span className="text-xs">{r.name}</span>,
                key: <span className="font-mono text-xs truncate block max-w-[120px]">{r.reasoning_key}</span>,
                type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{r.reasoning_type}</span>,
                threshold: <span className="font-mono">{Math.round(r.confidence_threshold * 100)}%</span>,
                status: r.is_active ? <StatusDot status="active" size="sm" /> : <StatusDot status="idle" size="sm" />,
              }))}
            />
          </ConsolePanel>
        )}
      </div>
    </div>
  )
}
