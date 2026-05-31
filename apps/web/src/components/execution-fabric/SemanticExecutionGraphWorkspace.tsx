"""
Semantic Execution Graph Workspace - Semantic orchestration and execution graphs.

Enterprise-grade semantic execution interface with:
- Execution graph visualization
- Dependency intelligence
- Topology analysis
- Pattern recognition
- Adaptive coordination
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Activity,
  ArrowRight,
  Box,
  Circle,
  GitBranch,
  Globe,
  Layers,
  LineChart,
  Link2,
  Map,
  Network,
  Plus,
  RefreshCw,
  Search,
  Settings,
  Target,
  TrendingUp,
} from 'lucide-react'
import {
  ConsolePanel,
  DataTable,
  TabBar,
  IconButton,
  StatusDot,
  MetricValue,
  ConfidenceBadge,
  ProgressBar,
} from './primitives'
import { MetricCard, StatusBar, SparklineChart } from './primitives'

// ---- Types ----

interface ExecutionGraph {
  graph_id: string
  name: string
  node_count: number
  edge_count: number
  complexity_score: number
  parallelization_potential: number
  status: 'draft' | 'validated' | 'active' | 'completed'
}

interface DependencyInfo {
  target_id: string
  target_type: string
  depends_on: string[]
  fan_out: number
  fan_in: number
  critical_path: boolean
}

interface TopologyNode {
  id: string
  name: string
  type: string
  semantic_role: string
  understanding_level: number
}

interface TopologyEdge {
  source: string
  target: string
  semantic_relation: string
}

// ---- Main Component ----

export default function SemanticExecutionGraphWorkspace() {
  const [activeTab, setActiveTab] = useState('graphs')
  const [graphs, setGraphs] = useState<ExecutionGraph[]>([])
  const [dependencies, setDependencies] = useState<DependencyInfo[]>([])
  const [topology, setTopology] = useState<{ nodes: TopologyNode[]; edges: TopologyEdge[] }>({ nodes: [], edges: [] })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setGraphs([
      { graph_id: 'graph-001', name: 'Render Pipeline', node_count: 24, edge_count: 45, complexity_score: 0.78, parallelization_potential: 0.65, status: 'active' },
      { graph_id: 'graph-002', name: 'Composition Flow', node_count: 18, edge_count: 32, complexity_score: 0.56, parallelization_potential: 0.82, status: 'active' },
      { graph_id: 'graph-003', name: 'Asset Processing', node_count: 31, edge_count: 67, complexity_score: 0.89, parallelization_potential: 0.45, status: 'validated' },
      { graph_id: 'graph-004', name: 'Workflow Orchestration', node_count: 42, edge_count: 98, complexity_score: 0.92, parallelization_potential: 0.38, status: 'draft' },
    ])

    setDependencies([
      { target_id: 'node-001', target_type: 'service', depends_on: ['node-002', 'node-003'], fan_out: 2, fan_in: 5, critical_path: true },
      { target_id: 'node-002', target_type: 'transformer', depends_on: ['node-004'], fan_out: 1, fan_in: 3, critical_path: false },
      { target_id: 'node-003', target_type: 'aggregator', depends_on: ['node-005', 'node-006'], fan_out: 2, fan_in: 4, critical_path: true },
      { target_id: 'node-004', target_type: 'processor', depends_on: [], fan_out: 3, fan_in: 1, critical_path: false },
    ])

    setTopology({
      nodes: [
        { id: 'node-001', name: 'Input Source', type: 'service', semantic_role: 'source', understanding_level: 0.92 },
        { id: 'node-002', name: 'Transformer A', type: 'transformer', semantic_role: 'processor', understanding_level: 0.85 },
        { id: 'node-003', name: 'Transformer B', type: 'transformer', semantic_role: 'processor', understanding_level: 0.88 },
        { id: 'node-004', name: 'Aggregator', type: 'aggregator', semantic_role: 'controller', understanding_level: 0.78 },
        { id: 'node-005', name: 'Output Sink', type: 'service', semantic_role: 'sink', understanding_level: 0.95 },
      ],
      edges: [
        { source: 'node-001', target: 'node-002', semantic_relation: 'data_flow' },
        { source: 'node-001', target: 'node-003', semantic_relation: 'data_flow' },
        { source: 'node-002', target: 'node-004', semantic_relation: 'dependency' },
        { source: 'node-003', target: 'node-004', semantic_relation: 'dependency' },
        { source: 'node-004', target: 'node-005', semantic_relation: 'control_flow' },
      ],
    })

    setLoading(false)
  }, [])

  const tabs = [
    { id: 'graphs', label: 'Execution Graphs', icon: <GitBranch className="h-3 w-3" /> },
    { id: 'dependencies', label: 'Dependencies', icon: <Link2 className="h-3 w-3" /> },
    { id: 'topology', label: 'Topology', icon: <Network className="h-3 w-3" /> },
    { id: 'patterns', label: 'Patterns', icon: <Layers className="h-3 w-3" /> },
    { id: 'analysis', label: 'Analysis', icon: <LineChart className="h-3 w-3" /> },
  ]

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Layers className="h-5 w-5 text-primary" />
          <h1 className="text-lg font-semibold">Semantic Execution Graph Workspace</h1>
        </div>
        <div className="flex items-center gap-2">
          <IconButton icon={<Search className="h-4 w-4" />} title="Search" />
          <IconButton icon={<Plus className="h-4 w-4" />} title="New Graph" />
          <IconButton icon={<Settings className="h-4 w-4" />} title="Settings" />
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
      ) : activeTab === 'graphs' ? (
        <div className="space-y-4">
          <ConsolePanel
            title="Execution Graphs"
            subtitle="Semantic execution graph registry"
            icon={<GitBranch className="h-4 w-4" />}
          >
            <DataTable
              columns={[
                { key: 'name', label: 'Name', width: '20%' },
                { key: 'graph_id', label: 'Graph ID', width: '15%' },
                { key: 'nodes', label: 'Nodes', width: '10%' },
                { key: 'edges', label: 'Edges', width: '10%' },
                { key: 'complexity', label: 'Complexity', width: '15%' },
                { key: 'parallelization', label: 'Parallelization', width: '15%' },
                { key: 'status', label: 'Status', width: '15%' },
              ]}
              rows={graphs.map(g => ({
                name: <span className="text-xs font-medium">{g.name}</span>,
                graph_id: <span className="font-mono text-xs text-muted-foreground">{g.graph_id}</span>,
                nodes: <span className="font-mono text-xs">{g.node_count}</span>,
                edges: <span className="font-mono text-xs">{g.edge_count}</span>,
                complexity: (
                  <div className="flex items-center gap-2">
                    <ProgressBar 
                      value={g.complexity_score * 100} 
                      showValue={false}
                      color={g.complexity_score > 0.8 ? 'warning' : 'primary'}
                    />
                    <span className="font-mono text-xs">{g.complexity_score.toFixed(2)}</span>
                  </div>
                ),
                parallelization: (
                  <div className="flex items-center gap-2">
                    <ProgressBar 
                      value={g.parallelization_potential * 100} 
                      showValue={false}
                      color={g.parallelization_potential > 0.6 ? 'success' : 'primary'}
                    />
                    <span className="font-mono text-xs">{g.parallelization_potential.toFixed(2)}</span>
                  </div>
                ),
                status: (
                  <div className="flex items-center gap-1">
                    <StatusDot status={
                      g.status === 'active' ? 'active' :
                      g.status === 'validated' ? 'processing' :
                      g.status === 'draft' ? 'idle' : 'warning'
                    } size="sm" />
                    <span className="text-xs capitalize">{g.status}</span>
                  </div>
                ),
              }))}
            />
          </ConsolePanel>

          <div className="grid gap-4 lg:grid-cols-3">
            <ConsolePanel
              title="Graph Statistics"
              icon={<Activity className="h-4 w-4" />}
              subtitle="Overall graph metrics"
            >
              <div className="space-y-3">
                <MetricValue label="Total Graphs" value={graphs.length} />
                <MetricValue label="Total Nodes" value={graphs.reduce((sum, g) => sum + g.node_count, 0)} />
                <MetricValue label="Total Edges" value={graphs.reduce((sum, g) => sum + g.edge_count, 0)} />
              </div>
            </ConsolePanel>

            <ConsolePanel
              title="Complexity Distribution"
              icon={<Box className="h-4 w-4" />}
              subtitle="Graph complexity analysis"
            >
              <StatusBar
                segments={[
                  { label: 'Low', value: graphs.filter(g => g.complexity_score < 0.5).length, color: 'bg-green-500' },
                  { label: 'Medium', value: graphs.filter(g => g.complexity_score >= 0.5 && g.complexity_score < 0.8).length, color: 'bg-yellow-500' },
                  { label: 'High', value: graphs.filter(g => g.complexity_score >= 0.8).length, color: 'bg-red-500' },
                ]}
              />
            </ConsolePanel>

            <ConsolePanel
              title="Parallelization Potential"
              icon={<TrendingUp className="h-4 w-4" />}
              subtitle="Execution optimization"
            >
              <SparklineChart 
                data={graphs.map(g => g.parallelization_potential)} 
                color="#22c55e" 
                height={48}
              />
              <div className="mt-3 flex justify-between text-[10px] text-muted-foreground">
                <span>Avg</span>
                <span className="font-mono">{(graphs.reduce((sum, g) => sum + g.parallelization_potential, 0) / graphs.length).toFixed(2)}</span>
              </div>
            </ConsolePanel>
          </div>
        </div>
      ) : activeTab === 'dependencies' ? (
        <ConsolePanel
          title="Dependency Intelligence"
          subtitle="Runtime dependency analysis"
          icon={<Link2 className="h-4 w-4" />}
        >
          <DataTable
            columns={[
              { key: 'target', label: 'Target', width: '15%' },
              { key: 'type', label: 'Type', width: '10%' },
              { key: 'depends_on', label: 'Depends On', width: '20%' },
              { key: 'fan_out', label: 'Fan Out', width: '10%' },
              { key: 'fan_in', label: 'Fan In', width: '10%' },
              { key: 'critical', label: 'Critical Path', width: '10%' },
              { key: 'depth', label: 'Depth', width: '10%' },
              { key: 'analysis', label: 'Analysis', width: '15%' },
            ]}
            rows={dependencies.map(d => ({
              target: <span className="font-mono text-xs">{d.target_id}</span>,
              type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{d.target_type}</span>,
              depends_on: (
                <div className="flex items-center gap-1 flex-wrap">
                  {d.depends_on.length > 0 ? d.depends_on.map(dep => (
                    <span key={dep} className="text-[10px] px-1 py-0.5 rounded bg-primary/10">{dep}</span>
                  )) : <span className="text-muted-foreground">—</span>}
                </div>
              ),
              fan_out: <span className="font-mono text-xs">{d.fan_out}</span>,
              fan_in: <span className="font-mono text-xs">{d.fan_in}</span>,
              critical: d.critical_path ? (
                <div className="flex items-center gap-1">
                  <StatusDot status="warning" size="sm" />
                  <span className="text-xs text-yellow-500">Critical</span>
                </div>
              ) : <span className="text-muted-foreground">—</span>,
              depth: <span className="font-mono text-xs">{d.depends_on.length}</span>,
              analysis: (
                <div className="flex items-center gap-1">
                  <ConfidenceBadge value={0.85} showLabel={false} />
                </div>
              ),
            }))}
          />
        </ConsolePanel>
      ) : activeTab === 'topology' ? (
        <div className="grid gap-4 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <ConsolePanel
              title="Cognitive Topology"
              subtitle="Workflow cognition mapping"
              icon={<Network className="h-4 w-4" />}
            >
              <div className="space-y-3">
                <div className="text-xs text-muted-foreground mb-2">NODES</div>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {topology.nodes.map(node => (
                    <div key={node.id} className="rounded border border-border p-3 hover:bg-accent/50 transition-colors">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-mono text-xs">{node.name}</span>
                        <StatusDot status="active" size="sm" />
                      </div>
                      <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                        <span className="px-1 py-0.5 rounded bg-muted">{node.type}</span>
                        <span className="px-1 py-0.5 rounded bg-primary/10">{node.semantic_role}</span>
                      </div>
                      <div className="mt-2 flex items-center justify-between">
                        <span className="text-[10px] text-muted-foreground">Understanding</span>
                        <span className="font-mono text-xs">{(node.understanding_level * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="text-xs text-muted-foreground mb-2 mt-4">EDGES</div>
                <div className="space-y-1">
                  {topology.edges.map((edge, i) => (
                    <div key={i} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs">{edge.source}</span>
                        <ArrowRight className="h-3 w-3 text-muted-foreground" />
                        <span className="font-mono text-xs">{edge.target}</span>
                      </div>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{edge.semantic_relation}</span>
                    </div>
                  ))}
                </div>
              </div>
            </ConsolePanel>
          </div>

          <ConsolePanel
            title="Topology Metrics"
            icon={<Map className="h-4 w-4" />}
            subtitle="Topology analysis"
          >
            <div className="space-y-3">
              <MetricValue label="Nodes" value={topology.nodes.length} />
              <MetricValue label="Edges" value={topology.edges.length} />
              <MetricValue label="Avg Connections" value={(topology.edges.length / topology.nodes.length).toFixed(2)} />
              <MetricValue label="Coverage" value="87" unit="%" />
            </div>
          </ConsolePanel>
        </div>
      ) : activeTab === 'patterns' ? (
        <ConsolePanel
          title="Execution Patterns"
          subtitle="Recognized execution patterns"
          icon={<Layers className="h-4 w-4" />}
        >
          <DataTable
            columns={[
              { key: 'pattern', label: 'Pattern', width: '25%' },
              { key: 'type', label: 'Type', width: '15%' },
              { key: 'frequency', label: 'Frequency', width: '15%' },
              { key: 'success_rate', label: 'Success Rate', width: '15%' },
              { key: 'avg_duration', label: 'Avg Duration', width: '15%' },
              { key: 'confidence', label: 'Confidence', width: '15%' },
            ]}
            rows={[
              { pattern: 'parallel_execution', type: 'execution', frequency: '156', success_rate: '94.2%', avg_duration: '234ms', confidence: '0.89' },
              { pattern: 'data_aggregation', type: 'composition', frequency: '89', success_rate: '97.8%', avg_duration: '156ms', confidence: '0.92' },
              { pattern: 'sequential_pipeline', type: 'execution', frequency: '67', success_rate: '98.5%', avg_duration: '412ms', confidence: '0.95' },
              { pattern: 'failover_recovery', type: 'resilience', frequency: '23', success_rate: '91.3%', avg_duration: '89ms', confidence: '0.85' },
            ]}
          />
        </ConsolePanel>
      ) : activeTab === 'analysis' ? (
        <div className="space-y-4">
          <ConsolePanel
            title="Topology Analysis"
            subtitle="Execution topology analysis"
            icon={<Activity className="h-4 w-4" />}
          >
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <MetricCard label="Complexity" value={0.78} status="warning" />
              <MetricCard label="Density" value={0.45} status="nominal" />
              <MetricCard label="Centrality" value={0.62} status="nominal" />
              <MetricCard label="Connectivity" value={0.89} status="nominal" />
            </div>
          </ConsolePanel>

          <div className="grid gap-4 lg:grid-cols-2">
            <ConsolePanel
              title="Optimization Hints"
              icon={<Target className="h-4 w-4" />}
              subtitle="Execution optimization recommendations"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between py-2 border-b border-border/50">
                  <div className="flex items-center gap-2">
                    <Layers className="h-4 w-4 text-green-500" />
                    <span className="text-xs">High parallelization potential</span>
                  </div>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/10 text-green-500">High Priority</span>
                </div>
                <div className="flex items-center justify-between py-2 border-b border-border/50">
                  <div className="flex items-center gap-2">
                    <Globe className="h-4 w-4 text-yellow-500" />
                    <span className="text-xs">Critical path detected</span>
                  </div>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-yellow-500/10 text-yellow-500">Medium Priority</span>
                </div>
                <div className="flex items-center justify-between py-2">
                  <div className="flex items-center gap-2">
                    <Box className="h-4 w-4 text-blue-500" />
                    <span className="text-xs">Node consolidation possible</span>
                  </div>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-500">Low Priority</span>
                </div>
              </div>
            </ConsolePanel>

            <ConsolePanel
              title="Coordination Metrics"
              icon={<Network className="h-4 w-4" />}
              subtitle="Adaptive coordination performance"
            >
              <div className="space-y-3">
                <MetricValue label="Active Coordinations" value={12} />
                <MetricValue label="Completed" value={89} />
                <MetricValue label="Avg Duration" value="156ms" />
                <MetricValue label="Success Rate" value="98.2" unit="%" />
              </div>
            </ConsolePanel>
          </div>
        </div>
      ) : null}
    </div>
  )
}