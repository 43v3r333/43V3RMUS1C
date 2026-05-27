"""
Runtime Lineage Viewer - Execution lineage tracking and visualization.

Enterprise-grade lineage visualization interface with:
- Execution tree visualization
- Node tracing
- Dependency tracking
- Cross-service coordination
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  ChevronRight,
  Circle,
  Clock,
  Download,
  Filter,
  GitBranch,
  History,
  Loader2,
  Map,
  Plus,
  RefreshCw,
  Search,
  Settings,
  Timer,
  X,
} from 'lucide-react'
import {
  ConsolePanel,
  DataTable,
  TabBar,
  IconButton,
  StatusDot,
  MetricValue,
  ProgressBar,
} from './primitives'
import { LineageNode, ExecutionProgress, StatusBar } from './primitives'

// ---- Types ----

interface LineageEntry {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
  depth: number
  duration_ms?: number
  input_hash?: string
  output_hash?: string
  depends_on: string[]
  execution_id: string
  timestamp: string
}

interface GraphSnapshot {
  graph_id: string
  total_nodes: number
  completed_nodes: number
  active_nodes: number
  failed_nodes: number
  avg_duration_ms: number
  throughput: number
}

// ---- Main Component ----

export default function RuntimeLineageViewer() {
  const [activeTab, setActiveTab] = useState('lineage')
  const [lineageTree, setLineageTree] = useState<LineageEntry[]>([])
  const [graphs, setGraphs] = useState<GraphSnapshot[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLineageTree([
      { id: 'exec-001', name: 'Initialize Workflow', status: 'completed', depth: 0, duration_ms: 45.2, depends_on: [], execution_id: 'wf-123', timestamp: '10:45:00' },
      { id: 'exec-002', name: 'Load Configuration', status: 'completed', depth: 1, duration_ms: 12.8, depends_on: ['exec-001'], execution_id: 'wf-123', timestamp: '10:45:01' },
      { id: 'exec-003', name: 'Validate Input', status: 'completed', depth: 1, duration_ms: 8.4, depends_on: ['exec-001'], execution_id: 'wf-123', timestamp: '10:45:01' },
      { id: 'exec-004', name: 'Process Data', status: 'running', depth: 2, duration_ms: 234.5, depends_on: ['exec-002', 'exec-003'], execution_id: 'wf-123', timestamp: '10:45:02' },
      { id: 'exec-005', name: 'Transform Stage 1', status: 'pending', depth: 3, duration_ms: undefined, depends_on: ['exec-004'], execution_id: 'wf-123', timestamp: '10:45:02' },
      { id: 'exec-006', name: 'Transform Stage 2', status: 'pending', depth: 3, duration_ms: undefined, depends_on: ['exec-004'], execution_id: 'wf-123', timestamp: '10:45:02' },
      { id: 'exec-007', name: 'Aggregate Results', status: 'pending', depth: 2, duration_ms: undefined, depends_on: ['exec-005', 'exec-006'], execution_id: 'wf-123', timestamp: '10:45:02' },
      { id: 'exec-008', name: 'Finalize Output', status: 'pending', depth: 1, duration_ms: undefined, depends_on: ['exec-007'], execution_id: 'wf-123', timestamp: '10:45:02' },
    ])

    setGraphs([
      { graph_id: 'graph-001', total_nodes: 127, completed_nodes: 98, active_nodes: 12, failed_nodes: 2, avg_duration_ms: 156.7, throughput: 847.3 },
      { graph_id: 'graph-002', total_nodes: 89, completed_nodes: 89, active_nodes: 0, failed_nodes: 1, avg_duration_ms: 234.2, throughput: 412.8 },
      { graph_id: 'graph-003', total_nodes: 156, completed_nodes: 45, active_nodes: 23, failed_nodes: 0, avg_duration_ms: 89.5, throughput: 1024.6 },
    ])

    setLoading(false)
  }, [])

  const tabs = [
    { id: 'lineage', label: 'Lineage Tree', icon: <GitBranch className="h-3 w-3" /> },
    { id: 'graphs', label: 'Graphs', icon: <Map className="h-3 w-3" /> },
    { id: 'dependencies', label: 'Dependencies', icon: <Activity className="h-3 w-3" /> },
    { id: 'history', label: 'History', icon: <History className="h-3 w-3" /> },
  ]

  const completedCount = lineageTree.filter(n => n.status === 'completed').length
  const runningCount = lineageTree.filter(n => n.status === 'running').length
  const pendingCount = lineageTree.filter(n => n.status === 'pending').length
  const totalDuration = lineageTree.reduce((sum, n) => sum + (n.duration_ms || 0), 0)

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <GitBranch className="h-5 w-5 text-primary" />
          <h1 className="text-lg font-semibold">Runtime Lineage Viewer</h1>
        </div>
        <div className="flex items-center gap-2">
          <IconButton icon={<Search className="h-4 w-4" />} title="Search" />
          <IconButton icon={<Filter className="h-4 w-4" />} title="Filter" />
          <IconButton icon={<Download className="h-4 w-4" />} title="Export" />
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
      ) : activeTab === 'lineage' ? (
        <div className="grid gap-4 lg:grid-cols-4">
          {/* Lineage Tree */}
          <div className="lg:col-span-3">
            <ConsolePanel
              title="Execution Lineage Tree"
              subtitle="Real-time execution trace"
              icon={<GitBranch className="h-4 w-4" />}
            >
              <div className="space-y-1">
                {lineageTree.map(entry => (
                  <LineageNode
                    key={entry.id}
                    id={entry.id}
                    name={entry.name}
                    status={entry.status}
                    depth={entry.depth}
                    duration={entry.duration_ms}
                    onClick={(id) => console.log('Selected:', id)}
                  />
                ))}
              </div>
            </ConsolePanel>
          </div>

          {/* Lineage Metrics */}
          <ConsolePanel
            title="Lineage Metrics"
            subtitle="Execution statistics"
            icon={<Activity className="h-4 w-4" />}
          >
            <div className="space-y-4">
              <ExecutionProgress
                current={completedCount}
                total={lineageTree.length}
                label="Completion"
              />
              <div className="grid grid-cols-2 gap-3">
                <div className="text-center p-3 rounded border border-border">
                  <div className="text-xl font-mono font-bold text-green-500">{completedCount}</div>
                  <div className="text-[10px] text-muted-foreground">COMPLETED</div>
                </div>
                <div className="text-center p-3 rounded border border-border">
                  <div className="text-xl font-mono font-bold text-blue-500">{runningCount}</div>
                  <div className="text-[10px] text-muted-foreground">RUNNING</div>
                </div>
                <div className="text-center p-3 rounded border border-border">
                  <div className="text-xl font-mono font-bold text-neutral-500">{pendingCount}</div>
                  <div className="text-[10px] text-muted-foreground">PENDING</div>
                </div>
                <div className="text-center p-3 rounded border border-border">
                  <div className="text-xl font-mono font-bold">{totalDuration.toFixed(1)}ms</div>
                  <div className="text-[10px] text-muted-foreground">TOTAL</div>
                </div>
              </div>
            </div>
          </ConsolePanel>
        </div>
      ) : activeTab === 'graphs' ? (
        <ConsolePanel
          title="Active Lineage Graphs"
          subtitle="Execution graph status"
          icon={<Map className="h-4 w-4" />}
        >
          <DataTable
            columns={[
              { key: 'graph_id', label: 'Graph ID', width: '15%' },
              { key: 'total', label: 'Total', width: '10%' },
              { key: 'completed', label: 'Completed', width: '10%' },
              { key: 'active', label: 'Active', width: '10%' },
              { key: 'failed', label: 'Failed', width: '10%' },
              { key: 'progress', label: 'Progress', width: '20%' },
              { key: 'avg_duration', label: 'Avg Duration', width: '10%' },
              { key: 'throughput', label: 'Throughput', width: '15%' },
            ]}
            rows={graphs.map(g => ({
              graph_id: <span className="font-mono text-xs">{g.graph_id}</span>,
              total: <span className="font-mono text-xs">{g.total_nodes}</span>,
              completed: <span className="font-mono text-xs text-green-500">{g.completed_nodes}</span>,
              active: <span className="font-mono text-xs text-blue-500">{g.active_nodes}</span>,
              failed: <span className={`font-mono text-xs ${g.failed_nodes > 0 ? 'text-red-500' : 'text-muted-foreground'}`}>{g.failed_nodes}</span>,
              progress: <ProgressBar value={(g.completed_nodes / g.total_nodes) * 100} showValue={false} />,
              avg_duration: <span className="font-mono text-xs">{g.avg_duration_ms.toFixed(1)}ms</span>,
              throughput: <span className="font-mono text-xs">{g.throughput.toFixed(1)}/s</span>,
            }))}
          />
        </ConsolePanel>
      ) : activeTab === 'dependencies' ? (
        <ConsolePanel
          title="Dependency Graph"
          subtitle="Node dependencies and relationships"
          icon={<Activity className="h-4 w-4" />}
        >
          <DataTable
            columns={[
              { key: 'node', label: 'Node', width: '20%' },
              { key: 'depends_on', label: 'Depends On', width: '30%' },
              { key: 'dependents', label: 'Dependents', width: '30%' },
              { key: 'depth', label: 'Depth', width: '10%' },
              { key: 'critical', label: 'Critical Path', width: '10%' },
            ]}
            rows={lineageTree.map(n => ({
              node: <span className="font-mono text-xs">{n.id}</span>,
              depends_on: (
                <div className="flex items-center gap-1 flex-wrap">
                  {n.depends_on.length > 0 ? n.depends_on.map(dep => (
                    <span key={dep} className="text-[10px] px-1 py-0.5 rounded bg-muted">{dep}</span>
                  )) : <span className="text-muted-foreground">—</span>}
                </div>
              ),
              dependents: (
                <div className="flex items-center gap-1 flex-wrap">
                  {lineageTree.filter(n2 => n2.depends_on.includes(n.id)).map(dep => (
                    <span key={dep.id} className="text-[10px] px-1 py-0.5 rounded bg-primary/10">{dep.id}</span>
                  ))}
                </div>
              ),
              depth: <span className="font-mono text-xs">{n.depth}</span>,
              critical: n.depth >= 3 ? <StatusDot status="active" size="sm" /> : <span className="text-muted-foreground">—</span>,
            }))}
          />
        </ConsolePanel>
      ) : activeTab === 'history' ? (
        <ConsolePanel
          title="Execution History"
          subtitle="Historical execution data"
          icon={<History className="h-4 w-4" />}
        >
          <DataTable
            columns={[
              { key: 'execution_id', label: 'Execution ID', width: '15%' },
              { key: 'timestamp', label: 'Timestamp', width: '20%' },
              { key: 'nodes', label: 'Nodes', width: '10%' },
              { key: 'status', label: 'Status', width: '10%' },
              { key: 'duration', label: 'Duration', width: '15%' },
              { key: 'errors', label: 'Errors', width: '10%' },
              { key: 'actions', label: '', width: '20%' },
            ]}
            rows={[
              { execution_id: 'wf-120', timestamp: '10:30:00', nodes: '8', status: 'completed', duration: '1.2s', errors: '0', actions: <IconButton icon={<Search className="h-3 w-3" />} size="sm" /> },
              { execution_id: 'wf-119', timestamp: '10:15:00', nodes: '12', status: 'completed', duration: '2.1s', errors: '0', actions: <IconButton icon={<Search className="h-3 w-3" />} size="sm" /> },
              { execution_id: 'wf-118', timestamp: '10:00:00', nodes: '6', status: 'failed', duration: '0.8s', errors: '2', actions: <IconButton icon={<Search className="h-3 w-3" />} size="sm" /> },
            ]}
          />
        </ConsolePanel>
      ) : null}
    </div>
  )
}