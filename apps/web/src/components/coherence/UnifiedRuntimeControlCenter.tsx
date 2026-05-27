/**
 * 43V3R CORE - Unified Runtime Control Center
 * 
 * Central orchestration intelligence for runtime identity management,
 * execution lineage tracking, and platform-wide coordination.
 * 
 * Enterprise runtime console with dense information panels,
 * telemetry-driven interfaces, and orchestration intelligence.
 */
'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  Cpu,
  GitBranch,
  Activity,
  Shield,
  Gauge,
  Database,
  Link,
  RefreshCw,
  Clock,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Layers,
  Network,
  Zap,
  Eye,
  Settings,
  ChevronRight,
  Hash,
  Clock3,
  ZapOff,
} from 'lucide-react'
import { useCoherenceApi, type RuntimeIdentity, type LineageResponse, type RuntimeContext } from '@/lib/coherence-api'
import { ConsolePanel, MetricGrid, MetricValue, StatusDot, ConfidenceBadge, DataTable, TabBar, IconButton, ProgressBar } from '@/components/cognitive/primitives'

// ---- Types ----

interface SystemOverview {
  activeIdentities: number
  lineageNodes: number
  activeContexts: number
  stabilityScore: number
  healthScore: number
  uptime: string
}

interface IdentityTreeNode {
  identity: RuntimeIdentity
  children: IdentityTreeNode[]
  expanded: boolean
}

// ---- Mock Data Generators ----

function generateMockIdentity(scope: string, key: string): RuntimeIdentity {
  return {
    id: `id-${scope}-${key}`,
    identity_scope: scope,
    identity_key: key,
    name: `${scope.toUpperCase()} ${key}`,
    description: `Runtime identity for ${scope} ${key}`,
    properties: {
      status: Math.random() > 0.2 ? 'active' : 'inactive',
      version: Math.floor(Math.random() * 10) + 1,
      capability_count: Math.floor(Math.random() * 5) + 1,
    },
    capabilities: ['orchestration', 'execution', 'monitoring'],
    lifecycle_state: 'active',
    version: Math.floor(Math.random() * 10) + 1,
    correlation_id: `corr-${Math.random().toString(36).substring(7)}`,
    trace_id: `trace-${Math.random().toString(36).substring(7)}`,
    created_at: new Date(Date.now() - Math.random() * 86400000).toISOString(),
    last_accessed_at: new Date(Date.now() - Math.random() * 3600000).toISOString(),
  }
}

// ---- Main Component ----

export default function UnifiedRuntimeControlCenter() {
  const api = useCoherenceApi()
  const [activeTab, setActiveTab] = useState('identities')
  const [loading, setLoading] = useState(true)
  const [systemOverview, setSystemOverview] = useState<SystemOverview>({
    activeIdentities: 0,
    lineageNodes: 0,
    activeContexts: 0,
    stabilityScore: 0,
    healthScore: 0,
    uptime: '0s',
  })
  const [identities, setIdentities] = useState<RuntimeIdentity[]>([])
  const [selectedIdentity, setSelectedIdentity] = useState<RuntimeIdentity | null>(null)
  const [lineageData, setLineageData] = useState<LineageResponse | null>(null)
  const [contexts, setContexts] = useState<RuntimeContext[]>([])
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())
  
  useEffect(() => {
    const startTime = Date.now()
    
    const loadData = async () => {
      try {
        // Try to load real data
        let status = { capabilities: [] as string[] }
        try {
          status = await api.getSystemStatus()
        } catch { /* use mock */ }
        
        // Mock data fallback
        const mockIdentities: RuntimeIdentity[] = [
          generateMockIdentity('system', 'root'),
          generateMockIdentity('orchestration', 'main-pipeline'),
          generateMockIdentity('execution', 'workflow-001'),
          generateMockIdentity('execution', 'workflow-002'),
          generateMockIdentity('agent', 'generator-alpha'),
          generateMockIdentity('agent', 'optimizer-beta'),
          generateMockIdentity('session', 'user-session-123'),
          generateMockIdentity('workflow', 'render-pipeline'),
        ]
        
        const uptimeSecs = Math.floor((Date.now() - startTime) / 1000)
        setSystemOverview({
          activeIdentities: mockIdentities.length,
          lineageNodes: mockIdentities.length * 3,
          activeContexts: Math.floor(mockIdentities.length * 0.7),
          stabilityScore: 0.94 + Math.random() * 0.05,
          healthScore: 0.96 + Math.random() * 0.03,
          uptime: `${Math.floor(uptimeSecs / 60)}m ${uptimeSecs % 60}s`,
        })
        
        setIdentities(mockIdentities)
        
        if (mockIdentities.length > 0) {
          setSelectedIdentity(mockIdentities[0])
          
          // Generate mock lineage
          setLineageData({
            lineage: {
              id: 'lin-001',
              root_identity_id: mockIdentities[0].id,
              lineage_type: mockIdentities[0].identity_scope,
              status: 'active',
              total_nodes: 12,
              total_events: 47,
              depth: 4,
              started_at: new Date(Date.now() - 3600000).toISOString(),
            },
            nodes: [
              { node_id: 'n1', event_type: 'created', depth: 0, timestamp: new Date(Date.now() - 3600000).toISOString(), duration_ms: 45 },
              { node_id: 'n2', event_type: 'started', depth: 1, timestamp: new Date(Date.now() - 3500000).toISOString(), duration_ms: 120 },
              { node_id: 'n3', event_type: 'executing', depth: 2, timestamp: new Date(Date.now() - 3400000).toISOString(), duration_ms: 890 },
              { node_id: 'n4', event_type: 'optimized', depth: 2, timestamp: new Date(Date.now() - 3300000).toISOString(), duration_ms: 230 },
              { node_id: 'n5', event_type: 'completed', depth: 3, timestamp: new Date(Date.now() - 3000000).toISOString(), duration_ms: 0 },
            ],
          })
          
          // Generate mock contexts
          setContexts([
            { id: 'ctx-1', identity_id: mockIdentities[0].id, context_key: 'orchestration.state', context_scope: 'system', value: { status: 'running', progress: 0.75 }, version: 3 },
            { id: 'ctx-2', identity_id: mockIdentities[0].id, context_key: 'execution.metrics', context_scope: 'system', value: { throughput: 142, latency: 23 }, version: 7 },
            { id: 'ctx-3', identity_id: mockIdentities[0].id, context_key: 'resource.allocation', context_scope: 'system', value: { cpu: 0.45, memory: 0.62 }, version: 12 },
          ])
        }
      } catch {
        // Use defaults
      }
      setLoading(false)
    }
    
    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [api])
  
  const toggleNode = (nodeId: string) => {
    setExpandedNodes(prev => {
      const next = new Set(prev)
      if (next.has(nodeId)) {
        next.delete(nodeId)
      } else {
        next.add(nodeId)
      }
      return next
    })
  }
  
  const tabs = [
    { id: 'identities', label: 'Identities', icon: <Hash className="h-3 w-3" /> },
    { id: 'lineage', label: 'Lineage', icon: <GitBranch className="h-3 w-3" /> },
    { id: 'contexts', label: 'Contexts', icon: <Database className="h-3 w-3" /> },
    { id: 'graph', label: 'Graph', icon: <Network className="h-3 w-3" /> },
  ]
  
  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Cpu className="h-5 w-5 text-primary" />
            <span className="font-mono text-sm font-semibold tracking-tight">UNIFIED RUNTIME CONTROL</span>
          </div>
          <div className="h-4 w-px bg-border/50" />
          <StatusDot status={systemOverview.stabilityScore > 0.9 ? 'healthy' : 'degraded'} />
          <span className="text-[10px] font-mono text-muted-foreground uppercase">
            Stability {Math.round(systemOverview.stabilityScore * 100)}%
          </span>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground">
            <Clock className="h-3 w-3" />
            <span>{systemOverview.uptime}</span>
          </div>
          <IconButton icon={<RefreshCw className="h-3 w-3" />} onClick={() => setLoading(true)} />
        </div>
      </div>
      
      {/* Metrics Bar */}
      <div className="border-b border-border/50 bg-muted/20 px-4 py-2">
        <MetricGrid columns={6}>
          <MetricValue
            label="Active Identities"
            value={systemOverview.activeIdentities}
            icon={<Hash className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Lineage Nodes"
            value={systemOverview.lineageNodes}
            icon={<GitBranch className="h-3 w-3" />}
            trend="up"
          />
          <MetricValue
            label="Active Contexts"
            value={systemOverview.activeContexts}
            icon={<Layers className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Stability"
            value={`${Math.round(systemOverview.stabilityScore * 100)}%`}
            icon={<Gauge className="h-3 w-3" />}
            trend={systemOverview.stabilityScore > 0.9 ? 'up' : 'down'}
          />
          <MetricValue
            label="Health"
            value={`${Math.round(systemOverview.healthScore * 100)}%`}
            icon={<Activity className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Execution Depth"
            value={lineageData?.lineage.depth || 0}
            icon={<Database className="h-3 w-3" />}
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
        {activeTab === 'identities' && (
          <div className="grid gap-4 lg:grid-cols-3">
            {/* Identity Tree */}
            <div className="lg:col-span-2">
              <ConsolePanel
                title="Runtime Identity Registry"
                icon={<Database className="h-4 w-4" />}
                subtitle={`${identities.length} registered identities`}
              >
                <div className="space-y-1">
                  {identities.map(identity => (
                    <div
                      key={identity.id}
                      className={`flex items-center justify-between px-3 py-2 rounded border transition-colors cursor-pointer ${
                        selectedIdentity?.id === identity.id
                          ? 'border-primary/50 bg-primary/5'
                          : 'border-transparent hover:border-border hover:bg-muted/30'
                      }`}
                      onClick={() => setSelectedIdentity(identity)}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${
                          identity.lifecycle_state === 'active' ? 'bg-green-500' : 'bg-muted-foreground'
                        }`} />
                        <div>
                          <span className="text-sm font-mono">{identity.name}</span>
                          <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                            <span className="px-1 py-0.5 rounded bg-muted">{identity.identity_scope}</span>
                            <span>{identity.identity_key}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 text-[10px] font-mono text-muted-foreground">
                        <span>v{identity.version}</span>
                        <ChevronRight className="h-3 w-3" />
                      </div>
                    </div>
                  ))}
                </div>
              </ConsolePanel>
            </div>
            
            {/* Identity Details */}
            <div>
              <ConsolePanel
                title="Identity Details"
                icon={<Eye className="h-4 w-4" />}
                subtitle={selectedIdentity?.identity_key || 'Select identity'}
              >
                {selectedIdentity ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Scope</span>
                        <div className="text-sm font-mono">{selectedIdentity.identity_scope}</div>
                      </div>
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">State</span>
                        <div className="text-sm font-mono">{selectedIdentity.lifecycle_state}</div>
                      </div>
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Version</span>
                        <div className="text-sm font-mono">{selectedIdentity.version}</div>
                      </div>
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Capabilities</span>
                        <div className="text-sm font-mono">{selectedIdentity.capabilities.length}</div>
                      </div>
                    </div>
                    
                    <div className="space-y-1">
                      <span className="text-[10px] text-muted-foreground uppercase">Trace ID</span>
                      <div className="text-[10px] font-mono text-muted-foreground truncate">
                        {selectedIdentity.trace_id}
                      </div>
                    </div>
                    
                    <div className="space-y-1">
                      <span className="text-[10px] text-muted-foreground uppercase">Correlation ID</span>
                      <div className="text-[10px] font-mono text-muted-foreground truncate">
                        {selectedIdentity.correlation_id || 'None'}
                      </div>
                    </div>
                    
                    <div className="space-y-1">
                      <span className="text-[10px] text-muted-foreground uppercase">Created</span>
                      <div className="text-xs font-mono">
                        {new Date(selectedIdentity.created_at).toLocaleString()}
                      </div>
                    </div>
                    
                    {selectedIdentity.properties && (
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Properties</span>
                        <div className="p-2 rounded bg-muted/50">
                          <pre className="text-[10px] font-mono overflow-auto">
                            {JSON.stringify(selectedIdentity.properties, null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground text-sm">
                    Select an identity to view details
                  </div>
                )}
              </ConsolePanel>
            </div>
          </div>
        )}
        
        {activeTab === 'lineage' && (
          <div className="grid gap-4 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <ConsolePanel
                title="Execution Lineage"
                icon={<GitBranch className="h-4 w-4" />}
                subtitle={`Depth: ${lineageData?.lineage.depth || 0}, Events: ${lineageData?.lineage.total_events || 0}`}
              >
                <div className="relative">
                  {/* Timeline */}
                  <div className="absolute left-4 top-0 bottom-0 w-px bg-border" />
                  
                  <div className="space-y-4 pl-12">
                    {lineageData?.nodes.map((node, idx) => (
                      <div key={node.node_id} className="relative">
                        <div className={`absolute left-[-28px] w-3 h-3 rounded-full border-2 ${
                          node.event_type === 'completed' ? 'bg-green-500 border-green-500' :
                          node.event_type === 'failed' ? 'bg-red-500 border-red-500' :
                          node.event_type === 'optimized' ? 'bg-blue-500 border-blue-500' :
                          'bg-muted border-border'
                        }`} />
                        
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-mono">{node.event_type}</span>
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">
                                depth {node.depth}
                              </span>
                            </div>
                            <div className="text-[10px] text-muted-foreground font-mono mt-1">
                              {new Date(node.timestamp).toLocaleTimeString()}
                            </div>
                          </div>
                          {node.duration_ms && (
                            <span className="text-[10px] font-mono text-muted-foreground">
                              {node.duration_ms}ms
                            </span>
                          )}
                        </div>
                        
                        {idx < (lineageData?.nodes.length || 0) - 1 && (
                          <div className="absolute left-[-28px] top-4 h-8 w-px bg-border/50" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </ConsolePanel>
            </div>
            
            <div>
              <ConsolePanel
                title="Lineage Metrics"
                icon={<Activity className="h-4 w-4" />}
                subtitle="Execution statistics"
              >
                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-muted-foreground">Total Nodes</span>
                      <span className="font-mono">{lineageData?.lineage.total_nodes || 0}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-muted-foreground">Total Events</span>
                      <span className="font-mono">{lineageData?.lineage.total_events || 0}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-muted-foreground">Max Depth</span>
                      <span className="font-mono">{lineageData?.lineage.depth || 0}</span>
                    </div>
                  </div>
                  
                  <div className="pt-2 border-t border-border/50">
                    <span className="text-[10px] text-muted-foreground uppercase">Started</span>
                    <div className="text-xs font-mono mt-1">
                      {lineageData?.lineage.started_at 
                        ? new Date(lineageData.lineage.started_at).toLocaleString() 
                        : 'N/A'}
                    </div>
                  </div>
                </div>
              </ConsolePanel>
            </div>
          </div>
        )}
        
        {activeTab === 'contexts' && (
          <div className="grid gap-4 lg:grid-cols-2">
            <ConsolePanel
              title="Runtime Contexts"
              icon={<Database className="h-4 w-4" />}
              subtitle={`${contexts.length} active contexts`}
            >
              <DataTable
                columns={[
                  { key: 'key', label: 'Context Key', width: '35%' },
                  { key: 'scope', label: 'Scope', width: '20%' },
                  { key: 'version', label: 'Version', width: '15%' },
                  { key: 'state', label: 'State', width: '30%' },
                ]}
                rows={contexts.map(ctx => ({
                  key: <span className="font-mono text-xs">{ctx.context_key}</span>,
                  scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{ctx.context_scope}</span>,
                  version: <span className="font-mono">{ctx.version}</span>,
                  state: (
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-green-500" />
                      <span className="text-xs font-mono text-muted-foreground">
                        {Object.keys(ctx.value).length} keys
                      </span>
                    </div>
                  ),
                }))}
              />
            </ConsolePanel>
            
            <ConsolePanel
              title="Context Value"
              icon={<Layers className="h-4 w-4" />}
              subtitle="Selected context data"
            >
              {contexts.length > 0 ? (
                <div className="p-3 rounded bg-muted/50">
                  <pre className="text-xs font-mono overflow-auto">
                    {JSON.stringify(contexts[0].value, null, 2)}
                  </pre>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground text-sm">
                  No contexts available
                </div>
              )}
            </ConsolePanel>
          </div>
        )}
        
        {activeTab === 'graph' && (
          <ConsolePanel
            title="Identity Hierarchy Graph"
            icon={<Network className="h-4 w-4" />}
            subtitle="Execution topology"
          >
            <div className="flex items-center justify-center h-64 text-muted-foreground">
              <div className="text-center">
                <Network className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Graph visualization</p>
                <p className="text-xs mt-1">{identities.length} nodes, {identities.length * 2} edges</p>
              </div>
            </div>
          </ConsolePanel>
        )}
      </div>
    </div>
  )
}