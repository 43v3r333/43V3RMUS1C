"""
Event Topology Workspace - Event contract registry and topology visualization.

Enterprise-grade topology management interface with:
- Contract registry management
- Topology visualization
- Schema versioning
- Propagation policies
- Event lineage tracking
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Database,
  Edit2,
  FileText,
  Filter,
  GitBranch,
  Globe,
  History,
  Link2,
  Network,
  Plus,
  RefreshCw,
  Search,
  Settings,
  Shield,
  TreePine,
  Trash2,
  View,
} from 'lucide-react'
import {
  ConsolePanel,
  DataTable,
  TabBar,
  IconButton,
  StatusDot,
  ConfidenceBadge,
} from './primitives'
import { TopologyNode, TopologyEdge, StatusBar } from './primitives'

// ---- Types ----

interface EventContract {
  id: string
  name: string
  version: string
  contract_type: string
  status: 'draft' | 'active' | 'deprecated' | 'archived'
  publish_count: number
  consume_count: number
  schema: Record<string, any>
  owner_team?: string
  created_at: string
}

interface TopologyNodeData {
  id: string
  name: string
  type: string
  status: string
  endpoint?: string
  capabilities: string[]
  health_score: number
}

interface PropagationPolicy {
  id: string
  name: string
  event_type?: string
  propagation_mode: string
  priority: number
  is_active: boolean
  execution_count: number
}

// ---- Main Component ----

export default function EventTopologyWorkspace() {
  const [activeTab, setActiveTab] = useState('contracts')
  const [contracts, setContracts] = useState<EventContract[]>([])
  const [topologyNodes, setTopologyNodes] = useState<TopologyNodeData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate data loading
    setContracts([
      {
        id: 'contract-001',
        name: 'render.completed',
        version: '1.2.0',
        contract_type: 'event',
        status: 'active',
        publish_count: 45892,
        consume_count: 89234,
        schema: { type: 'object', properties: { job_id: { type: 'string' } } },
        owner_team: 'rendering',
        created_at: '2024-01-15',
      },
      {
        id: 'contract-002',
        name: 'workflow.execute',
        version: '2.0.0',
        contract_type: 'command',
        status: 'active',
        publish_count: 2341,
        consume_count: 1892,
        schema: { type: 'object', properties: { workflow_id: { type: 'string' } } },
        owner_team: 'orchestration',
        created_at: '2024-02-20',
      },
      {
        id: 'contract-003',
        name: 'asset.created',
        version: '1.0.0',
        contract_type: 'event',
        status: 'draft',
        publish_count: 0,
        consume_count: 0,
        schema: { type: 'object', properties: { asset_id: { type: 'string' } } },
        owner_team: 'media',
        created_at: '2024-03-01',
      },
    ])

    setTopologyNodes([
      { id: 'node-001', name: 'RenderService', type: 'service', status: 'active', endpoint: 'https://render.internal', capabilities: ['render', 'transcode'], health_score: 0.98 },
      { id: 'node-002', name: 'Orchestrator', type: 'orchestrator', status: 'active', capabilities: ['coordinate', 'schedule'], health_score: 0.95 },
      { id: 'node-003', name: 'WorkerPool', type: 'worker', status: 'active', capabilities: ['execute', 'process'], health_score: 0.92 },
      { id: 'node-004', name: 'AssetStore', type: 'storage', status: 'active', capabilities: ['store', 'retrieve'], health_score: 0.99 },
      { id: 'node-005', name: 'EventBus', type: 'network', status: 'active', capabilities: ['publish', 'subscribe'], health_score: 0.97 },
    ])

    setLoading(false)
  }, [])

  const tabs = [
    { id: 'contracts', label: 'Contracts', icon: <FileText className="h-3 w-3" /> },
    { id: 'topology', label: 'Topology', icon: <Network className="h-3 w-3" /> },
    { id: 'propagation', label: 'Propagation', icon: <GitBranch className="h-3 w-3" /> },
    { id: 'lineage', label: 'Lineage', icon: <TreePine className="h-3 w-3" /> },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-500'
      case 'draft': return 'text-yellow-500'
      case 'deprecated': return 'text-orange-500'
      case 'archived': return 'text-neutral-500'
      default: return 'text-muted-foreground'
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Globe className="h-5 w-5 text-primary" />
          <h1 className="text-lg font-semibold">Event Topology Workspace</h1>
        </div>
        <div className="flex items-center gap-2">
          <IconButton icon={<Search className="h-4 w-4" />} title="Search" />
          <IconButton icon={<Filter className="h-4 w-4" />} title="Filter" />
          <IconButton icon={<Plus className="h-4 w-4" />} title="New Contract" />
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
      ) : activeTab === 'contracts' ? (
        <div className="space-y-4">
          <ConsolePanel
            title="Event Contract Registry"
            subtitle="Schema contracts and versioning"
            icon={<Database className="h-4 w-4" />}
          >
            <DataTable
              columns={[
                { key: 'name', label: 'Contract', width: '25%' },
                { key: 'version', label: 'Version', width: '10%' },
                { key: 'type', label: 'Type', width: '10%' },
                { key: 'status', label: 'Status', width: '10%' },
                { key: 'publish', label: 'Publish', width: '10%' },
                { key: 'consume', label: 'Consume', width: '10%' },
                { key: 'team', label: 'Team', width: '15%' },
                { key: 'actions', label: '', width: '10%' },
              ]}
              rows={contracts.map(c => ({
                name: <span className="font-mono text-xs">{c.name}</span>,
                version: <span className="font-mono text-xs text-muted-foreground">{c.version}</span>,
                type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{c.contract_type}</span>,
                status: (
                  <div className="flex items-center gap-1">
                    <StatusDot status={c.status === 'active' ? 'active' : c.status === 'draft' ? 'idle' : 'warning'} size="sm" />
                    <span className={`text-xs capitalize ${getStatusColor(c.status)}`}>{c.status}</span>
                  </div>
                ),
                publish: <span className="font-mono text-xs">{c.publish_count.toLocaleString()}</span>,
                consume: <span className="font-mono text-xs">{c.consume_count.toLocaleString()}</span>,
                team: <span className="text-xs text-muted-foreground">{c.owner_team || '-'}</span>,
                actions: (
                  <div className="flex items-center gap-1">
                    <IconButton icon={<View className="h-3 w-3" />} size="sm" title="View" />
                    <IconButton icon={<Edit2 className="h-3 w-3" />} size="sm" title="Edit" />
                  </div>
                ),
              }))}
            />
          </ConsolePanel>

          <div className="grid gap-4 lg:grid-cols-2">
            <ConsolePanel
              title="Contract Types Distribution"
              icon={<TreePine className="h-4 w-4" />}
              subtitle="Contracts by type"
            >
              <StatusBar
                segments={[
                  { label: 'Event', value: 24, color: 'bg-blue-500' },
                  { label: 'Command', value: 12, color: 'bg-purple-500' },
                  { label: 'Query', value: 8, color: 'bg-green-500' },
                  { label: 'Integration', value: 6, color: 'bg-yellow-500' },
                ]}
              />
            </ConsolePanel>

            <ConsolePanel
              title="Version Status"
              icon={<History className="h-4 w-4" />}
              subtitle="Contract versions"
            >
              <DataTable
                columns={[
                  { key: 'contract', label: 'Contract', width: '40%' },
                  { key: 'active', label: 'Active', width: '20%' },
                  { key: 'deprecated', label: 'Deprecated', width: '20%' },
                  { key: 'draft', label: 'Draft', width: '20%' },
                ]}
                rows={[
                  { contract: 'render.completed', active: '1.2.0', deprecated: '1.1.0', draft: '1.3.0' },
                  { contract: 'workflow.execute', active: '2.0.0', deprecated: '1.0.0', draft: '-' },
                  { contract: 'asset.created', active: '-', deprecated: '-', draft: '1.0.0' },
                ]}
              />
            </ConsolePanel>
          </div>
        </div>
      ) : activeTab === 'topology' ? (
        <div className="grid gap-4 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <ConsolePanel
              title="Topology Nodes"
              subtitle="Service registry and health"
              icon={<Network className="h-4 w-4" />}
            >
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {topologyNodes.map(node => (
                  <div
                    key={node.id}
                    className="rounded border border-border p-3 hover:bg-accent/50 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-mono">{node.name}</span>
                      <StatusDot status={node.status === 'active' ? 'active' : 'warning'} size="sm" />
                    </div>
                    <div className="flex items-center gap-2 text-[10px] text-muted-foreground mb-2">
                      <span className="px-1 py-0.5 rounded bg-muted">{node.type}</span>
                      <span className="font-mono">{node.health_score.toFixed(2)}</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {node.capabilities.map(cap => (
                        <span key={cap} className="text-[10px] px-1 py-0.5 rounded bg-primary/10 text-primary">
                          {cap}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </ConsolePanel>
          </div>

          <ConsolePanel
            title="Connection Matrix"
            icon={<Link2 className="h-4 w-4" />}
            subtitle="Node interconnections"
          >
            <div className="space-y-2">
              <TopologyEdge source="RenderService" target="AssetStore" type="data_flow" weight={0.95} />
              <TopologyEdge source="Orchestrator" target="WorkerPool" type="control_flow" weight={0.88} />
              <TopologyEdge source="EventBus" target="RenderService" type="event" weight={0.92} />
              <TopologyEdge source="EventBus" target="Orchestrator" type="event" weight={0.91} />
              <TopologyEdge source="WorkerPool" target="AssetStore" type="dependency" weight={0.85} />
            </div>
          </ConsolePanel>
        </div>
      ) : activeTab === 'propagation' ? (
        <ConsolePanel
          title="Propagation Policies"
          subtitle="Event distribution rules"
          icon={<GitBranch className="h-4 w-4" />}
        >
          <DataTable
            columns={[
              { key: 'name', label: 'Policy', width: '25%' },
              { key: 'event', label: 'Event Type', width: '15%' },
              { key: 'mode', label: 'Mode', width: '10%' },
              { key: 'priority', label: 'Priority', width: '10%' },
              { key: 'status', label: 'Status', width: '10%' },
              { key: 'executions', label: 'Executions', width: '15%' },
              { key: 'actions', label: '', width: '15%' },
            ]}
            rows={[
              {
                name: 'sync_propagation',
                event: 'render.*',
                mode: 'sync',
                priority: '10',
                status: <StatusDot status="active" size="sm" />,
                executions: '45,892',
                actions: <IconButton icon={<Settings className="h-3 w-3" />} size="sm" />,
              },
              {
                name: 'async_fanout',
                event: 'workflow.*',
                mode: 'async',
                priority: '5',
                status: <StatusDot status="active" size="sm" />,
                executions: '12,341',
                actions: <IconButton icon={<Settings className="h-3 w-3" />} size="sm" />,
              },
              {
                name: 'pipeline_execution',
                event: 'asset.*',
                mode: 'pipeline',
                priority: '3',
                status: <StatusDot status="idle" size="sm" />,
                executions: '2,891',
                actions: <IconButton icon={<Settings className="h-3 w-3" />} size="sm" />,
              },
            ]}
          />
        </ConsolePanel>
      ) : activeTab === 'lineage' ? (
        <ConsolePanel
          title="Event Lineage"
          subtitle="Event tracing through the system"
          icon={<TreePine className="h-4 w-4" />}
        >
          <DataTable
            columns={[
              { key: 'event_id', label: 'Event ID', width: '20%' },
              { key: 'type', label: 'Type', width: '15%' },
              { key: 'source', label: 'Source', width: '15%' },
              { key: 'trace', label: 'Trace ID', width: '15%' },
              { key: 'correlation', label: 'Correlation', width: '15%' },
              { key: 'time', label: 'Time', width: '20%' },
            ]}
            rows={[
              {
                event_id: 'evt-001',
                type: 'render.completed',
                source: 'RenderService',
                trace: 'trace-abc123',
                correlation: 'corr-xyz789',
                time: '2.34ms',
              },
              {
                event_id: 'evt-002',
                type: 'workflow.executed',
                source: 'Orchestrator',
                trace: 'trace-def456',
                correlation: 'corr-xyz789',
                time: '1.89ms',
              },
              {
                event_id: 'evt-003',
                type: 'asset.created',
                source: 'AssetStore',
                trace: 'trace-ghi789',
                correlation: 'corr-uvw123',
                time: '0.45ms',
              },
            ]}
          />
        </ConsolePanel>
      ) : null}
    </div>
  )
}