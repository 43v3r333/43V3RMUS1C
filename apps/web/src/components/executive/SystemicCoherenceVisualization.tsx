/**
 * 43V3R CORE - Systemic Coherence Visualization Center
 * 
 * Central visualization for systemic coherence lineage, coordination topology,
 * and executive orchestration synchronization across all platform layers.
 */
'use client'

import { useState, useEffect } from 'react'
import {
  GitBranch,
  Network,
  Activity,
  Layers,
  TrendingUp,
  TrendingDown,
  Clock,
  RefreshCw,
  Circle,
  ArrowRight,
} from 'lucide-react'
import { useExecutiveApi } from '@/lib/executive-api'
import {
  ConsolePanel,
  StatusDot,
  DataTable,
  TabBar,
  IconButton,
  ProgressBar,
} from '@/components/cognitive/primitives'

interface CoherenceLineage {
  id: string
  lineage_key: string
  coherence_metric: string
  source_id: string
  coherence_value: number
  coherence_trend: string
  event_type: string
  chain_id: string
  chain_position: number
  timestamp: string
}

interface TopologyNode {
  node_id: string
  node_type: string
  capabilities: string[]
}

interface Topology {
  id: string
  topology_key: string
  name: string
  scope: string
  topology_type: string
  node_count: number
  edge_count: number
  topology_state: string
  coherence_score: number
  sync_latency_ms: number
  message_throughput: number
  conflict_rate: number
}

export default function SystemicCoherenceVisualization() {
  const api = useExecutiveApi()
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('lineage')
  const [lineage, setLineage] = useState<CoherenceLineage[]>([])
  const [topologies, setTopologies] = useState<Topology[]>([])

  useEffect(() => {
    const loadData = async () => {
      try {
        const lin = await api.getCoherenceLineage({ limit: 50 })
        const topo = await api.listTopologies({ limit: 10 })
        setLineage(lin as CoherenceLineage[])
        setTopologies(topo as Topology[])
      } catch {
        setLineage([
          { id: 'l1', lineage_key: 'lin_8a3f21', coherence_metric: 'orchestration', source_id: 'exec_001', coherence_value: 0.95, coherence_trend: 'stable', event_type: 'supervision_completed', chain_id: 'chain_1', chain_position: 1, timestamp: new Date(Date.now() - 60000).toISOString() },
          { id: 'l2', lineage_key: 'lin_4c7d18', coherence_metric: 'execution', source_id: 'exec_002', coherence_value: 0.88, coherence_trend: 'improving', event_type: 'optimization_applied', chain_id: 'chain_1', chain_position: 2, timestamp: new Date(Date.now() - 120000).toISOString() },
          { id: 'l3', lineage_key: 'lin_9b2e67', coherence_metric: 'governance', source_id: 'exec_003', coherence_value: 0.92, coherence_trend: 'stable', event_type: 'policy_enforced', chain_id: 'chain_2', chain_position: 1, timestamp: new Date(Date.now() - 180000).toISOString() },
        ])
        setTopologies([
          { id: 't1', topology_key: 'topo_main', name: 'Main Orchestration', scope: 'execution', topology_type: 'hierarchical', node_count: 24, edge_count: 48, topology_state: 'synchronized', coherence_score: 0.94, sync_latency_ms: 12, message_throughput: 1420, conflict_rate: 0.02 },
          { id: 't2', topology_key: 'topo_cog', name: 'Cognition Fabric', scope: 'cognition', topology_type: 'mesh', node_count: 16, edge_count: 64, topology_state: 'synchronized', coherence_score: 0.91, sync_latency_ms: 8, message_throughput: 890, conflict_rate: 0.01 },
        ])
      }
      setLoading(false)
    }
    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [api])

  const tabs = [
    { id: 'lineage', label: 'Lineage', icon: <GitBranch className="h-3 w-3" /> },
    { id: 'topology', label: 'Topology', icon: <Network className="h-3 w-3" /> },
    { id: 'metrics', label: 'Metrics', icon: <Activity className="h-3 w-3" /> },
  ]

  // Group lineage by chain
  const chains = lineage.reduce((acc, item) => {
    if (!acc[item.chain_id]) acc[item.chain_id] = []
    acc[item.chain_id].push(item)
    return acc
  }, {} as Record<string, CoherenceLineage[]>)

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-3">
          <Layers className="h-5 w-5 text-primary" />
          <span className="font-mono text-sm font-semibold tracking-tight">SYSTEMIC COHERENCE</span>
          <div className="h-4 w-px bg-border/50" />
          <StatusDot status={topologies.some(t => t.topology_state === 'synchronized') ? 'active' : 'warning'} />
          <span className="text-[10px] font-mono text-muted-foreground uppercase">
            {Object.keys(chains).length} chains
          </span>
        </div>
        <IconButton icon={<RefreshCw className="h-3 w-3" />} onClick={() => setLoading(true)} />
      </div>

      {/* Tab Bar */}
      <div className="px-4 py-2 border-b border-border/30">
        <TabBar tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <>
            {activeTab === 'lineage' && (
              <div className="grid gap-4 lg:grid-cols-2">
                {/* Lineage Chain Visualization */}
                {Object.entries(chains).map(([chainId, events]) => (
                  <ConsolePanel
                    key={chainId}
                    title={`Chain: ${chainId}`}
                    icon={<GitBranch className="h-4 w-4" />}
                    subtitle={`${events.length} events`}
                  >
                    <div className="relative">
                      {/* Timeline */}
                      <div className="absolute left-4 top-0 bottom-0 w-px bg-border" />
                      
                      <div className="space-y-4 pl-12">
                        {events.sort((a, b) => a.chain_position - b.chain_position).map((event, idx) => (
                          <div key={event.id} className="relative">
                            <div className={`absolute left-[-28px] w-3 h-3 rounded-full border-2 ${
                              event.coherence_trend === 'stable' ? 'bg-green-500 border-green-500' :
                              event.coherence_trend === 'improving' ? 'bg-blue-500 border-blue-500' :
                              'bg-yellow-500 border-yellow-500'
                            }`} />
                            
                            <div className="flex items-start justify-between">
                              <div>
                                <div className="flex items-center gap-2">
                                  <span className="text-sm font-mono">{event.coherence_metric}</span>
                                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">pos {event.chain_position}</span>
                                </div>
                                <div className="text-[10px] text-muted-foreground mt-1">{event.event_type}</div>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className={`font-mono text-sm ${
                                  event.coherence_trend === 'stable' ? 'text-green-500' :
                                  event.coherence_trend === 'improving' ? 'text-blue-500' :
                                  'text-yellow-500'
                                }`}>
                                  {Math.round(event.coherence_value * 100)}%
                                </span>
                                {event.coherence_trend === 'stable' ? (
                                  <TrendingUp className="h-3 w-3 text-green-500" />
                                ) : event.coherence_trend === 'improving' ? (
                                  <TrendingUp className="h-3 w-3 text-blue-500" />
                                ) : (
                                  <TrendingDown className="h-3 w-3 text-yellow-500" />
                                )}
                              </div>
                            </div>
                            
                            {idx < events.length - 1 && (
                              <div className="absolute left-[-28px] top-4 h-8 w-px bg-border/50" />
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </ConsolePanel>
                ))}

                {/* Coherence Metrics Summary */}
                <ConsolePanel
                  title="Coherence Metrics"
                  icon={<Activity className="h-4 w-4" />}
                  subtitle="Across all domains"
                >
                  <div className="space-y-3">
                    {['orchestration', 'execution', 'governance', 'semantic', 'distribution'].map((metric) => {
                      const relevantLineage = lineage.filter(l => l.coherence_metric === metric)
                      const avgValue = relevantLineage.length > 0
                        ? relevantLineage.reduce((acc, l) => acc + l.coherence_value, 0) / relevantLineage.length
                        : 0.9
                      return (
                        <div key={metric} className="space-y-1">
                          <div className="flex justify-between text-xs">
                            <span className="font-mono uppercase">{metric}</span>
                            <span className="font-mono">{Math.round(avgValue * 100)}%</span>
                          </div>
                          <ProgressBar value={avgValue * 100} showValue={false} />
                        </div>
                      )
                    })}
                  </div>
                </ConsolePanel>
              </div>
            )}

            {activeTab === 'topology' && (
              <div className="grid gap-4 lg:grid-cols-2">
                {/* Topology List */}
                <ConsolePanel
                  title="Coordination Topologies"
                  icon={<Network className="h-4 w-4" />}
                  subtitle="Distributed orchestration graphs"
                >
                  <DataTable
                    columns={[
                      { key: 'name', label: 'Name', width: '25%' },
                      { key: 'type', label: 'Type', width: '15%' },
                      { key: 'nodes', label: 'Nodes', width: '15%' },
                      { key: 'edges', label: 'Edges', width: '15%' },
                      { key: 'state', label: 'State', width: '15%' },
                      { key: 'coherence', label: 'Coherence', width: '15%' },
                    ]}
                    rows={topologies.map(t => ({
                      key: t.id,
                      name: <span className="text-xs font-medium">{t.name}</span>,
                      type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{t.topology_type}</span>,
                      nodes: <span className="font-mono text-xs">{t.node_count}</span>,
                      edges: <span className="font-mono text-xs">{t.edge_count}</span>,
                      state: (
                        <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                          t.topology_state === 'synchronized' ? 'bg-green-500/10 text-green-500' :
                          t.topology_state === 'syncing' ? 'bg-blue-500/10 text-blue-500' :
                          'bg-yellow-500/10 text-yellow-500'
                        }`}>{t.topology_state}</span>
                      ),
                      coherence: (
                        <span className={`font-mono text-xs ${
                          t.coherence_score > 0.9 ? 'text-green-500' :
                          t.coherence_score > 0.7 ? 'text-yellow-500' : 'text-red-500'
                        }`}>{Math.round(t.coherence_score * 100)}%</span>
                      ),
                    }))}
                  />
                </ConsolePanel>

                {/* Topology Metrics */}
                <ConsolePanel
                  title="Topology Metrics"
                  icon={<Activity className="h-4 w-4" />}
                  subtitle="Synchronization performance"
                >
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <div className="text-[10px] text-muted-foreground uppercase">Avg Latency</div>
                      <div className="text-xl font-mono font-bold">
                        {Math.round(topologies.reduce((acc, t) => acc + t.sync_latency_ms, 0) / (topologies.length || 1))}
                        <span className="text-xs text-muted-foreground ml-1">ms</span>
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-[10px] text-muted-foreground uppercase">Throughput</div>
                      <div className="text-xl font-mono font-bold">
                        {Math.round(topologies.reduce((acc, t) => acc + t.message_throughput, 0) / (topologies.length || 1))}
                        <span className="text-xs text-muted-foreground ml-1">msg/s</span>
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-[10px] text-muted-foreground uppercase">Conflict Rate</div>
                      <div className="text-xl font-mono font-bold">
                        {Math.round((topologies.reduce((acc, t) => acc + t.conflict_rate, 0) / (topologies.length || 1)) * 100)}
                        <span className="text-xs text-muted-foreground ml-1">%</span>
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-[10px] text-muted-foreground uppercase">Total Nodes</div>
                      <div className="text-xl font-mono font-bold">
                        {topologies.reduce((acc, t) => acc + t.node_count, 0)}
                      </div>
                    </div>
                  </div>
                </ConsolePanel>

                {/* Graph Visualization Placeholder */}
                <ConsolePanel
                  title="Topology Graph"
                  icon={<GitBranch className="h-4 w-4" />}
                  subtitle={topologies[0]?.name || 'Select a topology'}
                >
                  <div className="flex items-center justify-center h-64 text-muted-foreground">
                    <div className="text-center">
                      <Network className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">Graph Visualization</p>
                      <p className="text-xs mt-1">
                        {topologies[0]?.node_count || 0} nodes, {topologies[0]?.edge_count || 0} edges
                      </p>
                    </div>
                  </div>
                </ConsolePanel>

                {/* Node List */}
                <ConsolePanel
                  title="Active Nodes"
                  icon={<Circle className="h-4 w-4" />}
                  subtitle="In coordination topology"
                >
                  <div className="space-y-2">
                    {[
                      { id: 'node_001', type: 'orchestrator', state: 'active', connections: 8 },
                      { id: 'node_002', type: 'executor', state: 'active', connections: 4 },
                      { id: 'node_003', type: 'supervisor', state: 'active', connections: 6 },
                      { id: 'node_004', type: 'governor', state: 'active', connections: 3 },
                    ].map((node) => (
                      <div key={node.id} className="flex items-center justify-between py-2 border-b border-border/30 last:border-0">
                        <div className="flex items-center gap-2">
                          <Circle className={`h-2 w-2 ${node.state === 'active' ? 'fill-green-500 text-green-500' : 'text-muted-foreground'}`} />
                          <span className="text-xs font-mono">{node.id}</span>
                        </div>
                        <div className="flex items-center gap-4 text-[10px] text-muted-foreground">
                          <span>{node.type}</span>
                          <span className="font-mono">{node.connections} conn</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </ConsolePanel>
              </div>
            )}

            {activeTab === 'metrics' && (
              <div className="grid gap-4 lg:grid-cols-3">
                {[
                  { metric: 'ORCHESTRATION', value: 0.95, trend: 'stable' },
                  { metric: 'EXECUTION', value: 0.88, trend: 'improving' },
                  { metric: 'GOVERNANCE', value: 0.92, trend: 'stable' },
                  { metric: 'SEMANTIC', value: 0.85, trend: 'declining' },
                  { metric: 'DISTRIBUTION', value: 0.91, trend: 'stable' },
                  { metric: 'TEMPORAL', value: 0.87, trend: 'improving' },
                ].map((item) => (
                  <ConsolePanel
                    key={item.metric}
                    title={item.metric}
                    icon={<Activity className="h-4 w-4" />}
                    subtitle={item.trend}
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-2xl font-mono font-bold">
                          {Math.round(item.value * 100)}%
                        </span>
                        {item.trend === 'stable' ? (
                          <TrendingUp className="h-4 w-4 text-green-500" />
                        ) : item.trend === 'improving' ? (
                          <TrendingUp className="h-4 w-4 text-blue-500" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-yellow-500" />
                        )}
                      </div>
                      <ProgressBar value={item.value * 100} showValue={false} />
                    </div>
                  </ConsolePanel>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
