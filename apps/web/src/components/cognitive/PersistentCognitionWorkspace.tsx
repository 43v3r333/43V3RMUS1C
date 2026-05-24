"""
Persistent Cognition Workspace

Orchestration memory interface with recall, pattern analysis,
and adaptive reasoning context.
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Brain,
  Database,
  Clock,
  Search,
  Pin,
  Trash2,
  RefreshCw,
  Layers,
  GitBranch,
  Filter,
} from 'lucide-react'
import { useCognitiveApi, type OrchestrationMemory, type MemoryStatistics, type ExecutionPattern } from '@/lib/cognitive-api'
import { ConsolePanel, DataTable, TabBar, IconButton, ProgressBar, ConfidenceBadge, CollapsibleSection } from './primitives'

type MemoryScope = 'episodic' | 'semantic' | 'procedural' | 'evaluative' | 'strategic'

interface MemoryWithIndex extends OrchestrationMemory {
  index: number
}

export default function PersistentCognitionWorkspace() {
  const api = useCognitiveApi()
  const [activeTab, setActiveTab] = useState('memories')
  const [loading, setLoading] = useState(true)
  const [memories, setMemories] = useState<OrchestrationMemory[]>([])
  const [stats, setStats] = useState<MemoryStatistics | null>(null)
  const [patterns, setPatterns] = useState<ExecutionPattern[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [scopeFilter, setScopeFilter] = useState<string>('')

  useEffect(() => {
    const loadData = async () => {
      try {
        const [memoriesData, statsData, patternsData] = await Promise.all([
          api.recall({ limit: 50 }),
          api.getMemoryStats(),
          api.analyzePatterns({ days: 7 }),
        ])
        setMemories(memoriesData.items)
        setStats(statsData)
        setPatterns(patternsData.patterns)
      } catch {
        // Mock data
        setMemories([
          {
            id: 'm1', scope: 'semantic', memory_kind: 'execution_insight', title: 'Parallel optimization applied',
            subject: 'render-alpha-001', content: { insight: 'Sequential steps can be parallelized' },
            importance: 0.85, recency: 0.72, confidence: 0.9, access_count: 12, is_pinned: true,
            created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
          },
          {
            id: 'm2', scope: 'episodic', memory_kind: 'workflow_audit', title: 'Heuristic hit: priority_weight',
            subject: 'compose-music-v3', content: { heuristic: 'priority_weight', hit_count: 156 },
            importance: 0.78, recency: 0.9, confidence: 0.89, access_count: 3, is_pinned: false,
            created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
          },
          {
            id: 'm3', scope: 'procedural', memory_kind: 'pattern_recognition', title: 'Render queue pattern',
            subject: 'render-pipeline', content: { pattern: 'batch_optimal_size', value: 32 },
            importance: 0.65, recency: 0.55, confidence: 0.82, access_count: 7, is_pinned: false,
            created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
          },
        ])
        setStats({
          total_memories: 89, by_scope: { episodic: 35, semantic: 28, procedural: 15, evaluative: 8, strategic: 3 },
          by_kind: { execution_insight: 42, workflow_audit: 25, pattern_recognition: 15, agent_decision: 7 },
          avg_importance: 0.72, avg_access_count: 4.2, pinned_count: 12, high_confidence_count: 67,
        })
        setPatterns([
          { subject: 'render-alpha-001', memory_kind: 'execution_insight', frequency: 8, avg_importance: 0.82, avg_confidence: 0.91, significance: 6.56 },
          { subject: 'compose-music-v3', memory_kind: 'workflow_audit', frequency: 5, avg_importance: 0.75, avg_confidence: 0.88, significance: 3.75 },
        ])
      }
      setLoading(false)
    }

    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [api])

  const tabs = [
    { id: 'memories', label: 'Memories', icon: <Database className="h-3 w-3" />, badge: memories.length },
    { id: 'patterns', label: 'Patterns', icon: <GitBranch className="h-3 w-3" />, badge: patterns.length },
    { id: 'scopes', label: 'Scopes', icon: <Layers className="h-3 w-3" /> },
  ]

  const filteredMemories = memories.filter(m => {
    if (scopeFilter && m.scope !== scopeFilter) return false
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      return m.title.toLowerCase().includes(query) || 
             m.subject?.toLowerCase().includes(query) ||
             m.memory_kind.toLowerCase().includes(query)
    }
    return true
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Persistent Cognition Workspace
          </h2>
          <p className="text-xs text-muted-foreground">
            Long-term orchestration memory and pattern analysis
          </p>
        </div>
      </div>

      <TabBar tabs={tabs} active={activeTab} onChange={setActiveTab} />

      {/* Search and Filter */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search memories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-sm border border-border rounded bg-card focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
        <div className="flex items-center gap-1">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <select
            value={scopeFilter}
            onChange={(e) => setScopeFilter(e.target.value)}
            className="text-xs border border-border rounded px-2 py-1.5 bg-card"
          >
            <option value="">All Scopes</option>
            <option value="episodic">Episodic</option>
            <option value="semantic">Semantic</option>
            <option value="procedural">Procedural</option>
            <option value="evaluative">Evaluative</option>
            <option value="strategic">Strategic</option>
          </select>
        </div>
        <IconButton icon={<RefreshCw className="h-4 w-4" />} title="Refresh" />
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid gap-4 lg:grid-cols-4">
          <ConsolePanel title="Total Memories" icon={<Database className="h-4 w-4" />} subtitle="Stored recollections">
            <div className="text-2xl font-mono font-bold">{stats.total_memories}</div>
          </ConsolePanel>

          <ConsolePanel title="By Scope" icon={<Layers className="h-4 w-4" />} subtitle="Distribution">
            <div className="space-y-1">
              {Object.entries(stats.by_scope).slice(0, 4).map(([scope, count]) => (
                <div key={scope} className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground capitalize">{scope}</span>
                  <span className="font-mono">{count}</span>
                </div>
              ))}
            </div>
          </ConsolePanel>

          <ConsolePanel title="Avg Importance" icon={<Brain className="h-4 w-4" />} subtitle="Significance">
            <div className="text-2xl font-mono font-bold">{Math.round(stats.avg_importance * 100)}%</div>
          </ConsolePanel>

          <ConsolePanel title="High Confidence" icon={<Clock className="h-4 w-4" />} subtitle="Reliable memories">
            <div className="text-2xl font-mono font-bold text-green-500">{stats.high_confidence_count}</div>
            <div className="text-xs text-muted-foreground mt-1">with 90%+ confidence</div>
          </ConsolePanel>
        </div>
      )}

      {/* Memory Content */}
      {activeTab === 'memories' && (
        <ConsolePanel title="Orchestration Memories" icon={<Database className="h-4 w-4" />} subtitle="Execution recollection">
          <DataTable
            columns={[
              { key: 'title', label: 'Memory', width: '25%' },
              { key: 'scope', label: 'Scope', width: '12%' },
              { key: 'kind', label: 'Kind', width: '15%' },
              { key: 'subject', label: 'Subject', width: '15%' },
              { key: 'importance', label: 'Importance', width: '12%' },
              { key: 'confidence', label: 'Confidence', width: '10%' },
              { key: 'actions', label: '', width: '11%' },
            ]}
            rows={filteredMemories.map(m => ({
              title: (
                <div className="flex items-center gap-2">
                  {m.is_pinned && <Pin className="h-3 w-3 text-yellow-500" />}
                  <span className="truncate font-medium">{m.title}</span>
                </div>
              ),
              scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted capitalize">{m.scope}</span>,
              kind: <span className="text-xs text-muted-foreground truncate">{m.memory_kind}</span>,
              subject: <span className="text-xs font-mono text-muted-foreground truncate">{m.subject || '—'}</span>,
              importance: (
                <div className="w-16">
                  <ProgressBar value={m.importance * 100} showValue={false} color={m.importance >= 0.7 ? 'success' : 'primary'} />
                </div>
              ),
              confidence: <ConfidenceBadge value={m.confidence} />,
              actions: (
                <div className="flex items-center gap-1">
                  <IconButton icon={<Pin className="h-3 w-3" />} title={m.is_pinned ? 'Unpin' : 'Pin'} size="sm" />
                  <IconButton icon={<Trash2 className="h-3 w-3" />} title="Delete" size="sm" />
                </div>
              ),
            }))}
          />
        </ConsolePanel>
      )}

      {activeTab === 'patterns' && (
        <ConsolePanel title="Execution Patterns" icon={<GitBranch className="h-4 w-4" />} subtitle="Recurring correlations">
          <DataTable
            columns={[
              { key: 'subject', label: 'Subject', width: '20%' },
              { key: 'kind', label: 'Memory Kind', width: '20%' },
              { key: 'frequency', label: 'Frequency', width: '15%' },
              { key: 'avg_importance', label: 'Avg Importance', width: '15%' },
              { key: 'significance', label: 'Significance', width: '15%' },
              { key: 'confidence', label: 'Avg Confidence', width: '15%' },
            ]}
            rows={patterns.map(p => ({
              subject: <span className="font-mono text-xs">{p.subject}</span>,
              kind: <span className="text-xs text-muted-foreground">{p.memory_kind}</span>,
              frequency: <span className="font-mono">{p.frequency}x</span>,
              avg_importance: (
                <div className="w-12">
                  <ProgressBar value={p.avg_importance * 100} showValue={false} />
                </div>
              ),
              significance: <span className="font-mono text-green-500">{p.significance.toFixed(2)}</span>,
              confidence: <ConfidenceBadge value={p.avg_confidence} />,
            }))}
          />
        </ConsolePanel>
      )}

      {activeTab === 'scopes' && stats && (
        <div className="space-y-4">
          {(['episodic', 'semantic', 'procedural', 'evaluative', 'strategic'] as MemoryScope[]).map(scope => {
            const count = stats.by_scope[scope] || 0
            const percentage = stats.total_memories > 0 ? (count / stats.total_memories) * 100 : 0
            
            return (
              <ConsolePanel key={scope} title={scope.charAt(0).toUpperCase() + scope.slice(1)} subtitle={`${count} memories`}>
                <div className="space-y-2">
                  <ProgressBar value={percentage} showValue label={`${count} items (${percentage.toFixed(1)}%)`} />
                  <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground mt-2">
                    <div>Access count: {Math.round(stats.avg_access_count * (percentage / 100) * 100) / 100}</div>
                    <div>High confidence: {Math.round(count * 0.75)}</div>
                  </div>
                </div>
              </ConsolePanel>
            )
          })}
        </div>
      )}
    </div>
  )
}