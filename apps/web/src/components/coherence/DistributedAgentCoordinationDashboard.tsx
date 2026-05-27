/**
 * 43V3R CORE - Distributed Agent Coordination Dashboard
 * 
 * Multi-agent coordination with shared cognition fabric,
 * inter-agent context propagation, and consensus mechanisms.
 * 
 * Dense agent interface with authority synchronization,
 * execution diplomacy, and coordinated reasoning.
 */
'use client'

import { useState, useEffect } from 'react'
import {
  Users,
  MessageSquare,
  Handshake,
  Vote,
  ArrowRightLeft,
  Shield,
  Activity,
  CheckCircle2,
  Clock,
  Hash,
  User,
  RefreshCw,
  Plus,
  Network,
  Zap,
  Target,
} from 'lucide-react'
import { useCoherenceApi, type AgentConsensus, type AuthorityDelegation, type DistributedContextState } from '@/lib/coherence-api'
import { ConsolePanel, MetricGrid, MetricValue, StatusDot, ConfidenceBadge, DataTable, TabBar, IconButton, ProgressBar } from '@/components/cognitive/primitives'

// ---- Types ----

interface AgentOverview {
  totalAgents: number
  activeConsensus: number
  activeDelegations: number
  contextStates: number
  avgConfidence: number
}

// ---- Main Component ----

export default function DistributedAgentCoordinationDashboard() {
  const api = useCoherenceApi()
  const [activeTab, setActiveTab] = useState('agents')
  const [loading, setLoading] = useState(true)
  const [overview, setOverview] = useState<AgentOverview>({
    totalAgents: 0,
    activeConsensus: 0,
    activeDelegations: 0,
    contextStates: 0,
    avgConfidence: 0,
  })
  const [agents, setAgents] = useState<{ id: string; name: string; type: string; status: string; capabilities: string[] }[]>([])
  const [consensus, setConsensus] = useState<AgentConsensus[]>([])
  const [delegations, setDelegations] = useState<AuthorityDelegation[]>([])
  const [contextStates, setContextStates] = useState<DistributedContextState[]>([])
  const [selectedConsensus, setSelectedConsensus] = useState<AgentConsensus | null>(null)
  
  useEffect(() => {
    const loadData = async () => {
      try {
        const mockAgents = [
          { id: 'agent-001', name: 'Generator Alpha', type: 'generator', status: 'busy', capabilities: ['text_generation', 'image_generation'] },
          { id: 'agent-002', name: 'Optimizer Beta', type: 'optimizer', status: 'idle', capabilities: ['optimization', 'scheduling'] },
          { id: 'agent-003', name: 'Analyzer Gamma', type: 'analyzer', status: 'busy', capabilities: ['analysis', 'coordination'] },
          { id: 'agent-004', name: 'Orchestrator Prime', type: 'orchestrator', status: 'idle', capabilities: ['coordination', 'scheduling'] },
          { id: 'agent-005', name: 'Scheduler Delta', type: 'scheduler', status: 'busy', capabilities: ['scheduling', 'monitoring'] },
        ]
        
        const mockConsensus: AgentConsensus[] = [
          { consensus_id: 'con-001', topic_kind: 'resource_allocation', topic_key: 'render-resources', decision: 'allocated:generator-alpha', reason: 'Highest priority match', votes: [], consensus_state: 'consensus_reached', confidence: 0.92, gathered_votes: 3, required_votes: 3 },
          { consensus_id: 'con-002', topic_kind: 'task_priority', topic_key: 'priority-queue', decision: '', reason: '', votes: [], consensus_state: 'voting', confidence: 0, gathered_votes: 2, required_votes: 3 },
          { consensus_id: 'con-003', topic_kind: 'conflict_resolution', topic_key: 'agent-conflict-42', decision: 'resolved:analyzer-gamma', reason: 'Lowest contention', votes: [], consensus_state: 'consensus_reached', confidence: 0.85, gathered_votes: 3, required_votes: 3 },
        ]
        
        const mockDelegations: AuthorityDelegation[] = [
          { delegation_id: 'del-001', delegator_id: 'orchestrator-prime', delegate_id: 'optimizer-beta', authority_type: 'resource_allocation', scope: { max_value: 1000 }, constraints: {}, max_depth: 3, current_depth: 2, delegation_state: 'active', invocation_count: 15, created_at: new Date(Date.now() - 1800000).toISOString() },
          { delegation_id: 'del-002', delegator_id: 'scheduler-delta', delegate_id: 'generator-alpha', authority_type: 'execution_control', scope: { timeout: 300 }, constraints: {}, max_depth: 2, current_depth: 1, delegation_state: 'active', invocation_count: 8, created_at: new Date(Date.now() - 3600000).toISOString() },
        ]
        
        const mockContextStates: DistributedContextState[] = [
          { context_id: 'ctx-001', context_key: 'render_state', partition_key: 'partition-1', state: { status: 'running', progress: 0.65, current_agent: 'generator-alpha' }, version: 12, consensus_state: 'consensus_reached', participating_nodes: ['agent-001', 'agent-002', 'agent-003'], node_versions: {} },
          { context_id: 'ctx-002', context_key: 'queue_state', partition_key: 'partition-1', state: { depth: 23, processing: 5 }, version: 8, consensus_state: 'pending', participating_nodes: ['agent-004', 'agent-005'], node_versions: {} },
        ]
        
        setOverview({
          totalAgents: mockAgents.length,
          activeConsensus: mockConsensus.filter(c => c.consensus_state === 'voting').length,
          activeDelegations: mockDelegations.filter(d => d.delegation_state === 'active').length,
          contextStates: mockContextStates.length,
          avgConfidence: (mockConsensus.reduce((sum, c) => sum + c.confidence, 0) / mockConsensus.length) || 0,
        })
        
        setAgents(mockAgents)
        setConsensus(mockConsensus)
        setDelegations(mockDelegations)
        setContextStates(mockContextStates)
        
        if (mockConsensus.length > 0) {
          setSelectedConsensus(mockConsensus[0])
        }
      } catch {
        // Use defaults
      }
      setLoading(false)
    }
    
    loadData()
    const interval = setInterval(loadData, 20000)
    return () => clearInterval(interval)
  }, [api])
  
  const tabs = [
    { id: 'agents', label: 'Agents', icon: <Users className="h-3 w-3" /> },
    { id: 'consensus', label: 'Consensus', icon: <Vote className="h-3 w-3" /> },
    { id: 'delegations', label: 'Delegations', icon: <ArrowRightLeft className="h-3 w-3" /> },
    { id: 'context', label: 'Context States', icon: <Network className="h-3 w-3" /> },
  ]
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'busy': return 'bg-yellow-500'
      case 'idle': return 'bg-green-500'
      case 'error': return 'bg-red-500'
      default: return 'bg-muted'
    }
  }
  
  const getConsensusStateColor = (state: string) => {
    switch (state) {
      case 'consensus_reached': return 'bg-green-500/10 text-green-500'
      case 'voting': return 'bg-blue-500/10 text-blue-500'
      case 'conflict': return 'bg-red-500/10 text-red-500'
      default: return 'bg-muted text-muted-foreground'
    }
  }
  
  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-primary" />
            <span className="font-mono text-sm font-semibold tracking-tight">AGENT COORDINATION</span>
          </div>
          <div className="h-4 w-px bg-border/50" />
          <StatusDot status={overview.activeConsensus > 0 ? 'degraded' : 'healthy'} />
          <span className="text-[10px] font-mono text-muted-foreground uppercase">
            {overview.totalAgents} agents
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <IconButton icon={<Plus className="h-3 w-3" />} tooltip="New Consensus" />
          <IconButton icon={<RefreshCw className="h-3 w-3" />} onClick={() => setLoading(true)} />
        </div>
      </div>
      
      {/* Metrics Bar */}
      <div className="border-b border-border/50 bg-muted/20 px-4 py-2">
        <MetricGrid columns={5}>
          <MetricValue
            label="Total Agents"
            value={overview.totalAgents}
            icon={<Users className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Active Consensus"
            value={overview.activeConsensus}
            icon={<Vote className="h-3 w-3" />}
            trend={overview.activeConsensus > 0 ? 'up' : 'stable'}
          />
          <MetricValue
            label="Active Delegations"
            value={overview.activeDelegations}
            icon={<ArrowRightLeft className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Context States"
            value={overview.contextStates}
            icon={<Network className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Avg Confidence"
            value={`${Math.round(overview.avgConfidence * 100)}%`}
            icon={<Target className="h-3 w-3" />}
            trend={overview.avgConfidence > 0.85 ? 'up' : 'stable'}
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
        {activeTab === 'agents' && (
          <ConsolePanel
            title="Agent Registry"
            icon={<Users className="h-4 w-4" />}
            subtitle={`${agents.length} registered agents`}
          >
            <div className="grid grid-cols-5 gap-4">
              {agents.map(agent => (
                <div key={agent.id} className="p-4 rounded border border-border/50">
                  <div className="flex items-center gap-2 mb-3">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(agent.status)}`} />
                    <span className="text-sm font-medium">{agent.name}</span>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Type</span>
                      <span className="font-mono">{agent.type}</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Status</span>
                      <span className={`capitalize ${agent.status === 'busy' ? 'text-yellow-500' : 'text-green-500'}`}>
                        {agent.status}
                      </span>
                    </div>
                    <div className="pt-2 border-t border-border/50">
                      <div className="text-[10px] text-muted-foreground mb-1">Capabilities</div>
                      <div className="flex flex-wrap gap-1">
                        {agent.capabilities.map(cap => (
                          <span key={cap} className="text-[10px] px-1.5 py-0.5 rounded bg-muted">
                            {cap}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>
        )}
        
        {activeTab === 'consensus' && (
          <div className="grid gap-4 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <ConsolePanel
                title="Agent Consensus"
                icon={<Vote className="h-4 w-4" />}
                subtitle={`${consensus.length} consensus sessions`}
              >
                <div className="space-y-3">
                  {consensus.map(c => (
                    <div
                      key={c.consensus_id}
                      className={`p-4 rounded border transition-colors cursor-pointer ${
                        selectedConsensus?.consensus_id === c.consensus_id
                          ? 'border-primary/50 bg-primary/5'
                          : 'border-transparent hover:border-border hover:bg-muted/30'
                      }`}
                      onClick={() => setSelectedConsensus(c)}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-mono">{c.consensus_id}</span>
                            <span className={`text-[10px] px-1.5 py-0.5 rounded ${getConsensusStateColor(c.consensus_state)}`}>
                              {c.consensus_state.replace('_', ' ')}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 mt-1 text-[10px] text-muted-foreground">
                            <span>{c.topic_kind}</span>
                            <span>•</span>
                            <span>{c.topic_key}</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <ConfidenceBadge value={c.confidence} showLabel />
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-2 text-[10px]">
                        <div className="p-2 rounded bg-muted/50">
                          <div className="text-muted-foreground">Votes</div>
                          <div className="font-mono">{c.gathered_votes}/{c.required_votes}</div>
                        </div>
                        <div className="p-2 rounded bg-muted/50">
                          <div className="text-muted-foreground">State</div>
                          <div className="font-mono capitalize">{c.consensus_state.replace('_', ' ')}</div>
                        </div>
                        <div className="p-2 rounded bg-muted/50">
                          <div className="text-muted-foreground">Confidence</div>
                          <div className="font-mono">{Math.round(c.confidence * 100)}%</div>
                        </div>
                      </div>
                      
                      {c.decision && (
                        <div className="mt-3 pt-2 border-t border-border/50">
                          <div className="text-[10px] text-muted-foreground">Decision</div>
                          <div className="text-sm font-mono">{c.decision}</div>
                          <div className="text-xs text-muted-foreground mt-1">{c.reason}</div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </ConsolePanel>
            </div>
            
            <div>
              <ConsolePanel
                title="Consensus Details"
                icon={<Vote className="h-4 w-4" />}
                subtitle={selectedConsensus?.consensus_id || 'Select consensus'}
              >
                {selectedConsensus ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Topic</span>
                        <div className="text-sm font-mono">{selectedConsensus.topic_key}</div>
                      </div>
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">State</span>
                        <span className={`text-xs px-2 py-1 rounded ${getConsensusStateColor(selectedConsensus.consensus_state)}`}>
                          {selectedConsensus.consensus_state.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                    
                    {selectedConsensus.votes.length > 0 && (
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Votes</span>
                        <div className="space-y-2">
                          {selectedConsensus.votes.map((vote, idx) => (
                            <div key={idx} className="p-2 rounded bg-muted/50">
                              <div className="flex items-center justify-between">
                                <span className="text-xs font-mono">{vote.agent_id}</span>
                                <span className="text-xs font-mono">{vote.vote}</span>
                              </div>
                              <div className="text-[10px] text-muted-foreground mt-1">{vote.reason}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {selectedConsensus.decision && (
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Decision</span>
                        <div className="text-sm font-mono">{selectedConsensus.decision}</div>
                        <div className="text-xs text-muted-foreground">{selectedConsensus.reason}</div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground text-sm">
                    Select a consensus to view details
                  </div>
                )}
              </ConsolePanel>
            </div>
          </div>
        )}
        
        {activeTab === 'delegations' && (
          <ConsolePanel
            title="Authority Delegations"
            icon={<ArrowRightLeft className="h-4 w-4" />}
            subtitle={`${delegations.length} active delegations`}
          >
            <DataTable
              columns={[
                { key: 'id', label: 'Delegation ID', width: '15%' },
                { key: 'delegator', label: 'Delegator', width: '15%' },
                { key: 'delegate', label: 'Delegate', width: '15%' },
                { key: 'authority', label: 'Authority Type', width: '20%' },
                { key: 'depth', label: 'Depth', width: '10%' },
                { key: 'invocations', label: 'Invocations', width: '10%' },
                { key: 'state', label: 'State', width: '15%' },
              ]}
              rows={delegations.map(d => ({
                id: <span className="font-mono text-xs">{d.delegation_id}</span>,
                delegator: <span className="text-xs font-mono">{d.delegator_id}</span>,
                delegate: <span className="text-xs font-mono">{d.delegate_id}</span>,
                authority: <span className="text-xs">{d.authority_type}</span>,
                depth: (
                  <div className="flex items-center gap-1">
                    <ProgressBar value={(d.current_depth / d.max_depth) * 100} showValue={false} color="primary" />
                    <span className="font-mono text-xs">{d.current_depth}/{d.max_depth}</span>
                  </div>
                ),
                invocations: <span className="font-mono">{d.invocation_count}</span>,
                state: (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                    d.delegation_state === 'active' ? 'bg-green-500/10 text-green-500' :
                    'bg-muted text-muted-foreground'
                  }`}>
                    {d.delegation_state}
                  </span>
                ),
              }))}
            />
          </ConsolePanel>
        )}
        
        {activeTab === 'context' && (
          <ConsolePanel
            title="Distributed Context States"
            icon={<Network className="h-4 w-4" />}
            subtitle={`${contextStates.length} active states`}
          >
            <div className="grid grid-cols-2 gap-4">
              {contextStates.map(ctx => (
                <div key={ctx.context_id} className="p-4 rounded border border-border/50">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <span className="text-sm font-mono">{ctx.context_key}</span>
                      <span className="text-[10px] text-muted-foreground ml-2">v{ctx.version}</span>
                    </div>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                      ctx.consensus_state === 'consensus_reached' ? 'bg-green-500/10 text-green-500' :
                      ctx.consensus_state === 'voting' ? 'bg-blue-500/10 text-blue-500' :
                      'bg-muted text-muted-foreground'
                    }`}>
                      {ctx.consensus_state.replace('_', ' ')}
                    </span>
                  </div>
                  
                  <div className="p-3 rounded bg-muted/50 mb-3">
                    <pre className="text-[10px] font-mono overflow-auto">
                      {JSON.stringify(ctx.state, null, 2)}
                    </pre>
                  </div>
                  
                  <div className="text-[10px] text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <span>Partition:</span>
                      <span className="font-mono">{ctx.partition_key}</span>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span>Nodes:</span>
                      <div className="flex gap-1">
                        {ctx.participating_nodes.map(node => (
                          <span key={node} className="font-mono px-1 py-0.5 rounded bg-muted">
                            {node}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>
        )}
      </div>
    </div>
  )
}