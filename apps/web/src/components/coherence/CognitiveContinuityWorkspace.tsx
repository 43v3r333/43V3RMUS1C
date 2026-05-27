/**
 * 43V3R CORE - Cognitive Continuity Workspace
 * 
 * Persistent orchestration cognition with long-term memory,
 * semantic recall, and intelligent retrieval systems.
 * 
 * Dense memory interface with semantic search, importance ranking,
 * and contextual recall capabilities.
 */
'use client'

import { useState, useEffect } from 'react'
import {
  Brain,
  Database,
  Search,
  Sparkles,
  Clock,
  Star,
  Hash,
  TrendingUp,
  Filter,
  Archive,
  RefreshCw,
  ChevronDown,
  Zap,
} from 'lucide-react'
import { useCoherenceApi, type CognitiveMemoryItem, type MemoryRetrievalResult } from '@/lib/coherence-api'
import { ConsolePanel, MetricGrid, MetricValue, StatusDot, ConfidenceBadge, DataTable, TabBar, IconButton, ProgressBar } from '@/components/cognitive/primitives'

// ---- Types ----

interface MemoryOverview {
  totalItems: number
  byScope: Record<string, number>
  avgImportance: number
  avgConfidence: number
  pinnedCount: number
}

type RetrievalMode = 'semantic' | 'episodic' | 'procedural' | 'mixed' | 'contextual'

// ---- Main Component ----

export default function CognitiveContinuityWorkspace() {
  const api = useCoherenceApi()
  const [activeTab, setActiveTab] = useState('memory')
  const [loading, setLoading] = useState(true)
  const [overview, setOverview] = useState<MemoryOverview>({
    totalItems: 0,
    byScope: {},
    avgImportance: 0,
    avgConfidence: 0,
    pinnedCount: 0,
  })
  const [memories, setMemories] = useState<CognitiveMemoryItem[]>([])
  const [selectedMemory, setSelectedMemory] = useState<CognitiveMemoryItem | null>(null)
  const [retrievalMode, setRetrievalMode] = useState<RetrievalMode>('mixed')
  const [searchQuery, setSearchQuery] = useState('')
  const [scopeFilter, setScopeFilter] = useState<string | null>(null)
  
  useEffect(() => {
    const loadData = async () => {
      try {
        // Mock data
        const mockMemories: CognitiveMemoryItem[] = [
          {
            id: 'mem-001',
            identity_id: 'id-001',
            scope: 'semantic',
            memory_kind: 'execution_insight',
            subject: 'render-alpha-001',
            title: 'Parallel optimization applied',
            content: { insight: 'Sequential steps 3-5 can be parallelized', improvement: 0.15 },
            importance: 0.85,
            recency: 0.72,
            confidence: 0.9,
            access_count: 12,
            created_at: new Date(Date.now() - 300000).toISOString(),
          },
          {
            id: 'mem-002',
            identity_id: 'id-001',
            scope: 'episodic',
            memory_kind: 'workflow_audit',
            subject: 'compose-music-v3',
            title: 'Heuristic hit: priority_weight',
            content: { heuristic: 'priority_weight', hit_count: 156 },
            importance: 0.78,
            recency: 0.9,
            confidence: 0.89,
            access_count: 3,
            created_at: new Date(Date.now() - 600000).toISOString(),
          },
          {
            id: 'mem-003',
            identity_id: 'id-001',
            scope: 'procedural',
            memory_kind: 'optimization_pattern',
            subject: 'render-pipeline',
            title: 'Batch size optimization discovered',
            content: { parameter: 'batch_size', optimal: 48, range: [32, 64] },
            importance: 0.92,
            recency: 0.65,
            confidence: 0.95,
            access_count: 28,
            is_pinned: true,
            created_at: new Date(Date.now() - 1800000).toISOString(),
          },
          {
            id: 'mem-004',
            identity_id: 'id-001',
            scope: 'evaluative',
            memory_kind: 'outcome_assessment',
            subject: 'campaign-summer-2024',
            title: 'Engagement rate above target',
            content: { metric: 'engagement_rate', target: 0.15, actual: 0.18 },
            importance: 0.88,
            recency: 0.55,
            confidence: 0.92,
            access_count: 7,
            created_at: new Date(Date.now() - 3600000).toISOString(),
          },
          {
            id: 'mem-005',
            identity_id: 'id-001',
            scope: 'strategic',
            memory_kind: 'planning_context',
            subject: 'q4-strategy',
            title: 'Resource allocation priorities',
            content: { priority_1: 'ai_generation', priority_2: 'render_farm' },
            importance: 0.75,
            recency: 0.88,
            confidence: 0.85,
            access_count: 5,
            created_at: new Date(Date.now() - 7200000).toISOString(),
          },
        ]
        
        const byScope: Record<string, number> = {}
        mockMemories.forEach(m => {
          byScope[m.scope] = (byScope[m.scope] || 0) + 1
        })
        
        setOverview({
          totalItems: mockMemories.length,
          byScope,
          avgImportance: mockMemories.reduce((sum, m) => sum + m.importance, 0) / mockMemories.length,
          avgConfidence: mockMemories.reduce((sum, m) => sum + m.confidence, 0) / mockMemories.length,
          pinnedCount: mockMemories.filter(m => m.is_pinned).length,
        })
        
        setMemories(mockMemories)
      } catch {
        // Use defaults
      }
      setLoading(false)
    }
    
    loadData()
    const interval = setInterval(loadData, 45000)
    return () => clearInterval(interval)
  }, [api])
  
  const filteredMemories = memories.filter(m => {
    if (scopeFilter && m.scope !== scopeFilter) return false
    if (searchQuery && !m.title.toLowerCase().includes(searchQuery.toLowerCase()) && 
        !m.subject.toLowerCase().includes(searchQuery.toLowerCase())) return false
    return true
  })
  
  const tabs = [
    { id: 'memory', label: 'Memory', icon: <Brain className="h-3 w-3" /> },
    { id: 'recall', label: 'Recall', icon: <Search className="h-3 w-3" /> },
    { id: 'patterns', label: 'Patterns', icon: <TrendingUp className="h-3 w-3" /> },
    { id: 'archives', label: 'Archives', icon: <Archive className="h-3 w-3" /> },
  ]
  
  const retrievalModes: { id: RetrievalMode; label: string; description: string }[] = [
    { id: 'semantic', label: 'Semantic', description: 'Rank by importance' },
    { id: 'episodic', label: 'Episodic', description: 'Rank by recency' },
    { id: 'procedural', label: 'Procedural', description: 'Rank by access' },
    { id: 'mixed', label: 'Mixed', description: 'Composite ranking' },
    { id: 'contextual', label: 'Contextual', description: 'Context-aware' },
  ]
  
  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            <span className="font-mono text-sm font-semibold tracking-tight">COGNITIVE CONTINUITY</span>
          </div>
          <div className="h-4 w-px bg-border/50" />
          <StatusDot status={overview.avgConfidence > 0.8 ? 'healthy' : 'degraded'} />
          <span className="text-[10px] font-mono text-muted-foreground uppercase">
            {overview.totalItems} items
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <IconButton icon={<RefreshCw className="h-3 w-3" />} onClick={() => setLoading(true)} />
        </div>
      </div>
      
      {/* Metrics Bar */}
      <div className="border-b border-border/50 bg-muted/20 px-4 py-2">
        <MetricGrid columns={5}>
          <MetricValue
            label="Total Memories"
            value={overview.totalItems}
            icon={<Database className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Avg Importance"
            value={`${Math.round(overview.avgImportance * 100)}%`}
            icon={<Star className="h-3 w-3" />}
            trend={overview.avgImportance > 0.7 ? 'up' : 'stable'}
          />
          <MetricValue
            label="Avg Confidence"
            value={`${Math.round(overview.avgConfidence * 100)}%`}
            icon={<Sparkles className="h-3 w-3" />}
            trend={overview.avgConfidence > 0.85 ? 'up' : 'stable'}
          />
          <MetricValue
            label="Pinned"
            value={overview.pinnedCount}
            icon={<Hash className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Scopes"
            value={Object.keys(overview.byScope).length}
            icon={<Filter className="h-3 w-3" />}
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
        {activeTab === 'memory' && (
          <div className="grid gap-4 lg:grid-cols-3">
            {/* Memory List */}
            <div className="lg:col-span-2">
              <ConsolePanel
                title="Memory Registry"
                icon={<Database className="h-4 w-4" />}
                subtitle={`${filteredMemories.length} items`}
                headerContent={
                  <div className="flex items-center gap-2">
                    <div className="relative">
                      <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3 w-3 text-muted-foreground" />
                      <input
                        type="text"
                        placeholder="Search memories..."
                        value={searchQuery}
                        onChange={e => setSearchQuery(e.target.value)}
                        className="pl-7 pr-3 py-1 text-xs bg-muted/50 border border-border rounded focus:outline-none focus:border-primary/50 w-48"
                      />
                    </div>
                    <select
                      value={scopeFilter || ''}
                      onChange={e => setScopeFilter(e.target.value || null)}
                      className="px-2 py-1 text-xs bg-muted/50 border border-border rounded focus:outline-none focus:border-primary/50"
                    >
                      <option value="">All Scopes</option>
                      <option value="episodic">Episodic</option>
                      <option value="semantic">Semantic</option>
                      <option value="procedural">Procedural</option>
                      <option value="evaluative">Evaluative</option>
                      <option value="strategic">Strategic</option>
                    </select>
                  </div>
                }
              >
                <div className="space-y-2">
                  {filteredMemories.map(memory => (
                    <div
                      key={memory.id}
                      className={`p-3 rounded border transition-colors cursor-pointer ${
                        selectedMemory?.id === memory.id
                          ? 'border-primary/50 bg-primary/5'
                          : 'border-transparent hover:border-border hover:bg-muted/30'
                      }`}
                      onClick={() => setSelectedMemory(memory)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                            memory.scope === 'episodic' ? 'bg-blue-500/10 text-blue-500' :
                            memory.scope === 'semantic' ? 'bg-purple-500/10 text-purple-500' :
                            memory.scope === 'procedural' ? 'bg-green-500/10 text-green-500' :
                            memory.scope === 'evaluative' ? 'bg-orange-500/10 text-orange-500' :
                            'bg-muted text-muted-foreground'
                          }`}>
                            {memory.scope}
                          </span>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">
                            {memory.memory_kind}
                          </span>
                          {memory.is_pinned && (
                            <Star className="h-3 w-3 text-yellow-500 fill-yellow-500" />
                          )}
                        </div>
                        <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                          <span className="font-mono">{(memory.importance * 100).toFixed(0)}%</span>
                          <span className="font-mono">×{memory.access_count}</span>
                        </div>
                      </div>
                      
                      <h4 className="text-sm font-medium mb-1">{memory.title}</h4>
                      <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                        <span className="font-mono">{memory.subject}</span>
                        <span>•</span>
                        <span>{new Date(memory.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </ConsolePanel>
            </div>
            
            {/* Memory Details */}
            <div>
              <ConsolePanel
                title="Memory Details"
                icon={<Sparkles className="h-4 w-4" />}
                subtitle={selectedMemory?.title || 'Select memory'}
              >
                {selectedMemory ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Importance</span>
                        <div className="flex items-center gap-2">
                          <ProgressBar value={selectedMemory.importance * 100} showValue={false} color="primary" />
                          <span className="text-xs font-mono">{Math.round(selectedMemory.importance * 100)}%</span>
                        </div>
                      </div>
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Recency</span>
                        <div className="flex items-center gap-2">
                          <ProgressBar value={selectedMemory.recency * 100} showValue={false} color="success" />
                          <span className="text-xs font-mono">{Math.round(selectedMemory.recency * 100)}%</span>
                        </div>
                      </div>
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Confidence</span>
                        <ConfidenceBadge value={selectedMemory.confidence} showLabel />
                      </div>
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Access Count</span>
                        <div className="text-sm font-mono">{selectedMemory.access_count}</div>
                      </div>
                    </div>
                    
                    <div className="space-y-1">
                      <span className="text-[10px] text-muted-foreground uppercase">Subject</span>
                      <div className="text-sm font-mono">{selectedMemory.subject}</div>
                    </div>
                    
                    <div className="space-y-1">
                      <span className="text-[10px] text-muted-foreground uppercase">Created</span>
                      <div className="text-xs font-mono">
                        {new Date(selectedMemory.created_at).toLocaleString()}
                      </div>
                    </div>
                    
                    <div className="space-y-1">
                      <span className="text-[10px] text-muted-foreground uppercase">Content</span>
                      <div className="p-3 rounded bg-muted/50">
                        <pre className="text-[10px] font-mono overflow-auto">
                          {JSON.stringify(selectedMemory.content, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground text-sm">
                    Select a memory to view details
                  </div>
                )}
              </ConsolePanel>
            </div>
          </div>
        )}
        
        {activeTab === 'recall' && (
          <div className="grid gap-4 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <ConsolePanel
                title="Memory Recall"
                icon={<Search className="h-4 w-4" />}
                subtitle="Intelligent retrieval system"
              >
                <div className="space-y-4">
                  {/* Retrieval Mode Selection */}
                  <div className="grid grid-cols-5 gap-2">
                    {retrievalModes.map(mode => (
                      <button
                        key={mode.id}
                        onClick={() => setRetrievalMode(mode.id)}
                        className={`p-3 rounded border text-center transition-colors ${
                          retrievalMode === mode.id
                            ? 'border-primary/50 bg-primary/5 text-primary'
                            : 'border-border hover:border-primary/30'
                        }`}
                      >
                        <span className="text-xs font-medium">{mode.label}</span>
                        <div className="text-[10px] text-muted-foreground mt-1">{mode.description}</div>
                      </button>
                    ))}
                  </div>
                  
                  {/* Search Input */}
                  <div className="flex gap-2">
                    <div className="flex-1 relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <input
                        type="text"
                        placeholder="Query memory with natural language..."
                        className="w-full pl-10 pr-4 py-3 text-sm bg-muted/50 border border-border rounded focus:outline-none focus:border-primary/50"
                      />
                    </div>
                    <button className="px-4 py-3 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors">
                      <Zap className="h-4 w-4" />
                    </button>
                  </div>
                  
                  {/* Results */}
                  <div className="space-y-2">
                    {filteredMemories.slice(0, 5).map((memory, idx) => (
                      <div
                        key={memory.id}
                        className="p-4 rounded border border-border/50 hover:border-primary/30 transition-colors"
                      >
                        <div className="flex items-start gap-3">
                          <span className="text-[10px] font-mono text-muted-foreground w-6">
                            #{idx + 1}
                          </span>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-sm font-medium">{memory.title}</span>
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">
                                {memory.scope}
                              </span>
                            </div>
                            <p className="text-xs text-muted-foreground">
                              {memory.subject}
                            </p>
                          </div>
                          <div className="text-right">
                            <div className="text-sm font-mono">
                              {(memory.importance * memory.recency * 100).toFixed(0)}%
                            </div>
                            <div className="text-[10px] text-muted-foreground">relevance</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </ConsolePanel>
            </div>
            
            <div>
              <ConsolePanel
                title="Scope Distribution"
                icon={<Database className="h-4 w-4" />}
                subtitle="Memory by scope"
              >
                <div className="space-y-3">
                  {Object.entries(overview.byScope).map(([scope, count]) => (
                    <div key={scope} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="capitalize">{scope}</span>
                        <span className="font-mono">{count}</span>
                      </div>
                      <ProgressBar
                        value={(count / overview.totalItems) * 100}
                        showValue={false}
                        color={scope === 'semantic' ? 'primary' : 'default'}
                      />
                    </div>
                  ))}
                </div>
              </ConsolePanel>
            </div>
          </div>
        )}
        
        {activeTab === 'patterns' && (
          <ConsolePanel
            title="Memory Patterns"
            icon={<TrendingUp className="h-4 w-4" />}
            subtitle="Execution pattern analysis"
          >
            <div className="grid grid-cols-3 gap-4">
              {[
                { pattern: 'Parallel Execution', frequency: 45, avg_importance: 0.82 },
                { pattern: 'Batch Processing', frequency: 38, avg_importance: 0.78 },
                { pattern: 'Priority Scheduling', frequency: 32, avg_importance: 0.85 },
                { pattern: 'Resource Allocation', frequency: 28, avg_importance: 0.71 },
                { pattern: 'Cache Optimization', frequency: 24, avg_importance: 0.89 },
                { pattern: 'Failure Recovery', frequency: 19, avg_importance: 0.92 },
              ].map((pattern, idx) => (
                <div key={idx} className="p-4 rounded border border-border/50">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">{pattern.pattern}</span>
                    <span className="text-[10px] font-mono text-muted-foreground">×{pattern.frequency}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <ProgressBar value={pattern.avg_importance * 100} showValue={false} color="primary" />
                    <span className="text-xs font-mono">{Math.round(pattern.avg_importance * 100)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>
        )}
        
        {activeTab === 'archives' && (
          <ConsolePanel
            title="Memory Archives"
            icon={<Archive className="h-4 w-4" />}
            subtitle="Decayed and archived memories"
          >
            <div className="text-center py-12 text-muted-foreground">
              <Archive className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No archived memories</p>
              <p className="text-xs mt-1">Memories are archived when recency drops below threshold</p>
            </div>
          </ConsolePanel>
        )}
      </div>
    </div>
  )
}