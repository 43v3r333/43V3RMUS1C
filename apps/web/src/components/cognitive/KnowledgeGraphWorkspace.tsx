"""
Knowledge Graph Workspace - Interactive semantic memory explorer.
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Database,
  GitBranch,
  Network,
  Plus,
  Search,
  Filter,
  RefreshCw,
  ChevronRight,
  Layers,
  Target,
  Eye,
  Activity,
} from 'lucide-react'
import { useCognitiveApi, type KnowledgeNode, type GraphNeighborhood, type SemanticRelationship } from '@/lib/cognitive-api'
import { ConsolePanel, DataTable, MetricGrid, StatusDot, ConfidenceBadge, IconButton, TabBar, Sparkline } from './primitives'

interface GraphStats {
  nodes: number
  edges: number
  relationships: number
  byKind: Record<string, number>
}

export default function KnowledgeGraphWorkspace() {
  const api = useCognitiveApi()
  const [activeTab, setActiveTab] = useState('nodes')
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<GraphStats>({ nodes: 0, edges: 0, relationships: 0, byKind: {} })
  const [nodes, setNodes] = useState<KnowledgeNode[]>([])
  const [relationships, setRelationships] = useState<SemanticRelationship[]>([])
  const [selectedNode, setSelectedNode] = useState<GraphNeighborhood | null>(null)
  const [searchKind, setSearchKind] = useState('')
  const [searchKey, setSearchKey] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        const summary = await api.getGraphSummary().catch(() => ({ nodes: 0, edges: 0, relationships: 0, by_kind: {} }))
        setStats({ nodes: summary.nodes || 0, edges: summary.edges || 0, relationships: summary.relationships || 0, byKind: summary.by_kind || {} })
        const nodeList = await api.listNodes({ limit: 50 }).catch(() => [])
        setNodes(nodeList)
        const relList = await api.listRelationships({ limit: 50 }).catch(() => [])
        setRelationships(relList)
      } catch {
        // mock data
        setStats({ nodes: 247, edges: 1842, relationships: 156, byKind: { workflow: 89, execution: 67, agent: 45, asset: 32, render_job: 14 } })
        setNodes([
          { id: 'n1', node_kind: 'workflow', node_key: 'render-alpha-001', label: 'Alpha Render Pipeline', properties: {}, tags: ['render', 'production'], relevance_score: 0.92, centrality: 0.78, lifecycle_state: 'active', last_seen_at: new Date().toISOString(), seen_count: 23, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
          { id: 'n2', node_kind: 'execution', node_key: 'exec-001', label: 'Execution 001', properties: {}, tags: ['orchestration'], relevance_score: 0.85, centrality: 0.65, lifecycle_state: 'active', last_seen_at: new Date().toISOString(), seen_count: 12, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
          { id: 'n3', node_kind: 'agent', node_key: 'agent-gen-1', label: 'Generator Agent', properties: {}, tags: ['generation', 'ai'], relevance_score: 0.79, centrality: 0.45, lifecycle_state: 'active', last_seen_at: new Date().toISOString(), seen_count: 8, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
          { id: 'n4', node_kind: 'render_job', node_key: 'job-42', label: 'Render Job 42', properties: {}, tags: ['render'], relevance_score: 0.71, centrality: 0.34, lifecycle_state: 'active', last_seen_at: new Date().toISOString(), seen_count: 5, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
        ])
        setRelationships([
          { id: 'r1', subject_kind: 'workflow', subject_key: 'render-alpha-001', predicate: 'governs', object_kind: 'execution', object_key: 'exec-001', confidence: 0.95, weight: 1.0, is_active: true, created_at: new Date().toISOString() },
          { id: 'r2', subject_kind: 'execution', subject_key: 'exec-001', predicate: 'depends_on', object_kind: 'render_job', object_key: 'job-42', confidence: 0.89, weight: 0.8, is_active: true, created_at: new Date().toISOString() },
        ])
      }
      setLoading(false)
    }
    load()
  }, [api])

  const handleNodeClick = async (node: KnowledgeNode) => {
    try {
      const neighborhood = await api.getNeighborhood(node.node_kind, node.node_key, 2).catch(() => null)
      setSelectedNode(neighborhood)
    } catch {
      setSelectedNode(null)
    }
  }

  const filteredNodes = nodes.filter(n => {
    if (searchKind && n.node_kind !== searchKind) return false
    if (searchKey && !n.node_key.toLowerCase().includes(searchKey.toLowerCase())) return false
    return true
  })

  const tabs = [
    { id: 'nodes', label: 'Nodes', icon: <GitBranch className="h-3 w-3" />, badge: stats.nodes },
    { id: 'relationships', label: 'Relationships', icon: <Network className="h-3 w-3" />, badge: stats.relationships },
    { id: 'explorer', label: 'Explorer', icon: <Target className="h-3 w-3" /> },
  ]

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 border border-primary/20">
            <Network className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Knowledge Graph Workspace</h1>
            <p className="text-xs text-muted-foreground">Semantic orchestration memory explorer</p>
          </div>
        </div>
        <IconButton icon={<RefreshCw className="h-3.5 w-3.5" />} title="Refresh" />
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-4 gap-2">
        {[
          { label: 'Nodes', value: stats.nodes, icon: <GitBranch className="h-3.5 w-3.5" /> },
          { label: 'Edges', value: stats.edges, icon: <Activity className="h-3.5 w-3.5" /> },
          { label: 'Relationships', value: stats.relationships, icon: <Network className="h-3.5 w-3.5" /> },
          { label: 'Kinds', value: Object.keys(stats.byKind).length, icon: <Layers className="h-3.5 w-3.5" /> },
        ].map((stat, i) => (
          <div key={i} className="rounded border border-border bg-card px-3 py-2">
            <div className="flex items-center gap-1.5 mb-0.5">
              <span className="text-muted-foreground">{stat.icon}</span>
              <span className="text-[10px] text-muted-foreground uppercase tracking-wider">{stat.label}</span>
            </div>
            <div className="text-lg font-mono font-semibold">{stat.value}</div>
          </div>
        ))}
      </div>

      <TabBar tabs={tabs} active={activeTab} onChange={setActiveTab} />

      {activeTab === 'nodes' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex items-center gap-3">
            <select
              className="h-8 rounded border border-border bg-card px-2 text-xs"
              value={searchKind}
              onChange={e => setSearchKind(e.target.value)}
            >
              <option value="">All kinds</option>
              {Object.keys(stats.byKind).map(k => (
                <option key={k} value={k}>{k} ({stats.byKind[k]})</option>
              ))}
            </select>
            <div className="relative flex-1 max-w-64">
              <Search className="absolute left-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search by key..."
                value={searchKey}
                onChange={e => setSearchKey(e.target.value)}
                className="h-8 w-full rounded border border-border bg-card pl-8 pr-3 text-xs placeholder:text-muted-foreground"
              />
            </div>
            <span className="text-xs text-muted-foreground">{filteredNodes.length} results</span>
          </div>

          {/* Nodes table */}
          <ConsolePanel title="Graph Nodes" icon={<GitBranch className="h-4 w-4" />} subtitle={`${stats.nodes} total nodes`}>
            <DataTable
              columns={[
                { key: 'kind', label: 'Kind', width: '12%' },
                { key: 'key', label: 'Key', width: '25%' },
                { key: 'label', label: 'Label', width: '20%' },
                { key: 'tags', label: 'Tags', width: '15%' },
                { key: 'relevance', label: 'Relevance', width: '10%' },
                { key: 'centrality', label: 'Centrality', width: '10%' },
                { key: 'seen', label: 'Seen', width: '8%' },
              ]}
              rows={filteredNodes.map(n => ({
                kind: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{n.node_kind}</span>,
                key: <button onClick={() => handleNodeClick(n)} className="text-xs font-mono text-primary hover:underline truncate max-w-32">{n.node_key}</button>,
                label: <span className="truncate text-xs">{n.label}</span>,
                tags: <div className="flex gap-1">{n.tags.slice(0, 2).map(t => <span key={t} className="text-[9px] px-1 py-0.5 rounded bg-secondary">{t}</span>)}</div>,
                relevance: (
                  <div className="w-12">
                    <div className="h-1 w-full rounded-full bg-muted overflow-hidden">
                      <div className="h-full bg-primary" style={{ width: `${n.relevance_score * 100}%` }} />
                    </div>
                  </div>
                ),
                centrality: <span className="font-mono text-xs">{n.centrality.toFixed(2)}</span>,
                seen: <span className="font-mono text-muted-foreground">{n.seen_count}</span>,
              }))}
            />
          </ConsolePanel>

          {/* Kind distribution */}
          <ConsolePanel title="Kind Distribution" icon={<Layers className="h-4 w-4" />} subtitle="Nodes by kind">
            <div className="space-y-2">
              {Object.entries(stats.byKind).sort((a, b) => b[1] - a[1]).map(([kind, count]) => (
                <div key={kind} className="flex items-center gap-3">
                  <span className="text-xs font-mono w-20">{kind}</span>
                  <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
                    <div className="h-full bg-primary" style={{ width: `${(count / stats.nodes) * 100}%` }} />
                  </div>
                  <span className="font-mono text-xs w-8 text-right">{count}</span>
                </div>
              ))}
            </div>
          </ConsolePanel>
        </div>
      )}

      {activeTab === 'relationships' && (
        <ConsolePanel title="Semantic Relationships" icon={<Network className="h-4 w-4" />} subtitle={`${stats.relationships} curated relationships`}>
          <DataTable
            columns={[
              { key: 'subject', label: 'Subject', width: '20%' },
              { key: 'predicate', label: 'Predicate', width: '15%' },
              { key: 'object', label: 'Object', width: '20%' },
              { key: 'confidence', label: 'Confidence', width: '15%' },
              { key: 'weight', label: 'Weight', width: '10%' },
              { key: 'derived', label: 'Derived', width: '20%' },
            ]}
            rows={relationships.map(r => ({
              subject: <div className="flex items-center gap-1"><span className="text-[10px] px-1 py-0.5 rounded bg-muted">{r.subject_kind}</span><span className="font-mono text-xs truncate">{r.subject_key}</span></div>,
              predicate: <span className="text-[10px] px-1.5 py-0.5 rounded bg-secondary font-mono">{r.predicate}</span>,
              object: <div className="flex items-center gap-1"><span className="text-[10px] px-1 py-0.5 rounded bg-muted">{r.object_kind}</span><span className="font-mono text-xs truncate">{r.object_key}</span></div>,
              confidence: <ConfidenceBadge value={r.confidence} />,
              weight: <span className="font-mono text-xs">{r.weight.toFixed(2)}</span>,
              derived: <span className="text-muted-foreground text-xs">{r.derived_from || '-'}</span>,
            }))}
          />
        </ConsolePanel>
      )}

      {activeTab === 'explorer' && (
        <div className="grid gap-4 lg:grid-cols-2">
          <ConsolePanel title="Neighborhood Explorer" icon={<Eye className="h-4 w-4" />} subtitle="Click a node to explore its graph neighborhood">
            <DataTable
              columns={[
                { key: 'kind', label: 'Kind', width: '15%' },
                { key: 'key', label: 'Key', width: '35%' },
                { key: 'relevance', label: 'Relevance', width: '20%' },
                { key: 'centrality', label: 'Centrality', width: '20%' },
                { key: 'explore', label: '', width: '10%' },
              ]}
              rows={filteredNodes.slice(0, 10).map(n => ({
                kind: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{n.node_kind}</span>,
                key: <span className="font-mono text-xs truncate">{n.node_key}</span>,
                relevance: (
                  <div className="w-16">
                    <div className="h-1 w-full rounded-full bg-muted overflow-hidden">
                      <div className="h-full bg-primary" style={{ width: `${n.relevance_score * 100}%` }} />
                    </div>
                  </div>
                ),
                centrality: <span className="font-mono text-xs">{n.centrality.toFixed(2)}</span>,
                explore: <IconButton icon={<ChevronRight className="h-3 w-3" />} title="Explore neighborhood" onClick={() => handleNodeClick(n)} />,
              }))}
            />
          </ConsolePanel>

          <ConsolePanel title="Selected Neighborhood" icon={<Target className="h-4 w-4" />} subtitle={selectedNode ? `${selectedNode.nodes.length} nodes, ${selectedNode.edges.length} edges` : 'select a node'}>
            {selectedNode ? (
              <div className="space-y-3">
                <div className="flex items-center gap-2 py-2 border-b border-border">
                  <span className="text-xs font-medium">Root: {selectedNode.root.label}</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{selectedNode.root.node_kind}</span>
                </div>
                <div className="text-xs text-muted-foreground mb-2">Connected nodes (depth {selectedNode.depth})</div>
                {selectedNode.nodes.filter(n => n.id !== selectedNode.root.id).slice(0, 8).map(n => (
                  <div key={n.id} className="flex items-center justify-between py-1.5 border-b border-border/50">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] px-1 py-0.5 rounded bg-muted">{n.node_kind}</span>
                      <span className="text-xs font-mono truncate max-w-36">{n.node_key}</span>
                    </div>
                    <ConfidenceBadge value={n.relevance_score} showLabel={false} />
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground text-center py-8">Select a node from the explorer table to view its neighborhood</p>
            )}
          </ConsolePanel>
        </div>
      )}
    </div>
  )
}