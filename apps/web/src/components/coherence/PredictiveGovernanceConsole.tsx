/**
 * 43V3R CORE - Predictive Governance Console
 * 
 * Autonomous governance with policy enforcement, orchestration arbitration,
 * and conflict prevention systems.
 * 
 * Dense governance interface with policy management, violation tracking,
 * and predictive anomaly prevention.
 */
'use client'

import { useState, useEffect } from 'react'
import {
  Shield,
  AlertTriangle,
  Scale,
  Gavel,
  Eye,
  CheckCircle2,
  XCircle,
  Clock,
  Hash,
  AlertCircle,
  RefreshCw,
  Plus,
  Filter,
  Zap,
  ChevronRight,
} from 'lucide-react'
import { useCoherenceApi, type GovernancePolicy, type PolicyViolation, type ArbitrationRecord } from '@/lib/coherence-api'
import { ConsolePanel, MetricGrid, MetricValue, StatusDot, ConfidenceBadge, DataTable, TabBar, IconButton, ProgressBar } from '@/components/cognitive/primitives'

// ---- Types ----

interface GovernanceOverview {
  activePolicies: number
  violations24h: number
  activeConflicts: number
  avgResolutionTime: string
  arbitrationCount: number
}

// ---- Main Component ----

export default function PredictiveGovernanceConsole() {
  const api = useCoherenceApi()
  const [activeTab, setActiveTab] = useState('policies')
  const [loading, setLoading] = useState(true)
  const [overview, setOverview] = useState<GovernanceOverview>({
    activePolicies: 0,
    violations24h: 0,
    activeConflicts: 0,
    avgResolutionTime: '0m',
    arbitrationCount: 0,
  })
  const [policies, setPolicies] = useState<GovernancePolicy[]>([])
  const [violations, setViolations] = useState<PolicyViolation[]>([])
  const [selectedPolicy, setSelectedPolicy] = useState<GovernancePolicy | null>(null)
  const [severityFilter, setSeverityFilter] = useState<string | null>(null)
  
  useEffect(() => {
    const loadData = async () => {
      try {
        const mockPolicies: GovernancePolicy[] = [
          {
            policy_id: 'pol-001',
            policy_key: 'resource_allocation_limit',
            name: 'Resource Allocation Limit',
            policy_scope: 'execution',
            conditions: { 'resource_usage': { op: 'gt', value: 0.9 } },
            enforcement_action: 'throttle',
            severity: 'warning',
            priority: 85,
            trigger_count: 127,
            violation_count: 8,
            lifecycle_state: 'active',
          },
          {
            policy_id: 'pol-002',
            policy_key: 'execution_timeout',
            name: 'Execution Timeout Policy',
            policy_scope: 'execution',
            conditions: { 'duration_ms': { op: 'gt', value: 300000 } },
            enforcement_action: 'terminate',
            severity: 'critical',
            priority: 95,
            trigger_count: 45,
            violation_count: 3,
            lifecycle_state: 'active',
          },
          {
            policy_id: 'pol-003',
            policy_key: 'agent_capability_match',
            name: 'Agent Capability Match',
            policy_scope: 'agent',
            conditions: { 'capability_score': { op: 'lt', value: 0.7 } },
            enforcement_action: 'delegate',
            severity: 'violation',
            priority: 75,
            trigger_count: 89,
            violation_count: 12,
            lifecycle_state: 'active',
          },
          {
            policy_id: 'pol-004',
            policy_key: 'priority_inversion_prevention',
            name: 'Priority Inversion Prevention',
            policy_scope: 'orchestration',
            conditions: { 'priority_conflict': true },
            enforcement_action: 'arbitrate',
            severity: 'warning',
            priority: 80,
            trigger_count: 23,
            violation_count: 2,
            lifecycle_state: 'active',
          },
        ]
        
        const mockViolations: PolicyViolation[] = [
          { id: 'v-001', violation_id: 'v-001', severity: 'critical', violation_type: 'execution_timeout', description: 'Execution exceeded 300s timeout', detected_at: new Date(Date.now() - 600000).toISOString(), resolved: false },
          { id: 'v-002', violation_id: 'v-002', severity: 'violation', violation_type: 'agent_capability_match', description: 'Agent capability below threshold', detected_at: new Date(Date.now() - 1200000).toISOString(), resolved: true },
          { id: 'v-003', violation_id: 'v-003', severity: 'warning', violation_type: 'resource_allocation_limit', description: 'Resource usage exceeded 90%', detected_at: new Date(Date.now() - 1800000).toISOString(), resolved: true },
          { id: 'v-004', violation_id: 'v-004', severity: 'warning', violation_type: 'priority_inversion_prevention', description: 'Priority conflict detected in queue', detected_at: new Date(Date.now() - 2400000).toISOString(), resolved: false },
        ]
        
        setOverview({
          activePolicies: mockPolicies.length,
          violations24h: mockViolations.filter(v => !v.resolved).length,
          activeConflicts: 2,
          avgResolutionTime: '4m 23s',
          arbitrationCount: 7,
        })
        
        setPolicies(mockPolicies)
        setViolations(mockViolations)
      } catch {
        // Use defaults
      }
      setLoading(false)
    }
    
    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [api])
  
  const filteredViolations = violations.filter(v => {
    if (severityFilter && v.severity !== severityFilter) return false
    return true
  })
  
  const tabs = [
    { id: 'policies', label: 'Policies', icon: <Shield className="h-3 w-3" /> },
    { id: 'violations', label: 'Violations', icon: <AlertTriangle className="h-3 w-3" /> },
    { id: 'arbitration', label: 'Arbitration', icon: <Scale className="h-3 w-3" /> },
    { id: 'rules', label: 'Rules', icon: <Gavel className="h-3 w-3" /> },
  ]
  
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500/10 text-red-500 border-red-500/20'
      case 'violation': return 'bg-orange-500/10 text-orange-500 border-orange-500/20'
      case 'warning': return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'
      case 'info': return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
      default: return 'bg-muted text-muted-foreground'
    }
  }
  
  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            <span className="font-mono text-sm font-semibold tracking-tight">PREDICTIVE GOVERNANCE</span>
          </div>
          <div className="h-4 w-px bg-border/50" />
          <StatusDot status={overview.violations24h > 0 ? 'degraded' : 'healthy'} />
          <span className="text-[10px] font-mono text-muted-foreground uppercase">
            {overview.activePolicies} active policies
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <IconButton icon={<Plus className="h-3 w-3" />} tooltip="Create Policy" />
          <IconButton icon={<RefreshCw className="h-3 w-3" />} onClick={() => setLoading(true)} />
        </div>
      </div>
      
      {/* Metrics Bar */}
      <div className="border-b border-border/50 bg-muted/20 px-4 py-2">
        <MetricGrid columns={5}>
          <MetricValue
            label="Active Policies"
            value={overview.activePolicies}
            icon={<Shield className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Unresolved Violations"
            value={overview.violations24h}
            icon={<AlertTriangle className="h-3 w-3" />}
            trend={overview.violations24h > 0 ? 'up' : 'stable'}
          />
          <MetricValue
            label="Active Conflicts"
            value={overview.activeConflicts}
            icon={<AlertCircle className="h-3 w-3" />}
            trend={overview.activeConflicts > 0 ? 'up' : 'stable'}
          />
          <MetricValue
            label="Avg Resolution"
            value={overview.avgResolutionTime}
            icon={<Clock className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Arbitrations"
            value={overview.arbitrationCount}
            icon={<Scale className="h-3 w-3" />}
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
        {activeTab === 'policies' && (
          <div className="grid gap-4 lg:grid-cols-3">
            {/* Policy List */}
            <div className="lg:col-span-2">
              <ConsolePanel
                title="Active Policies"
                icon={<Shield className="h-4 w-4" />}
                subtitle={`${policies.length} policies`}
              >
                <div className="space-y-2">
                  {policies.map(policy => (
                    <div
                      key={policy.policy_id}
                      className={`p-4 rounded border transition-colors cursor-pointer ${
                        selectedPolicy?.policy_id === policy.policy_id
                          ? 'border-primary/50 bg-primary/5'
                          : 'border-transparent hover:border-border hover:bg-muted/30'
                      }`}
                      onClick={() => setSelectedPolicy(policy)}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="text-sm font-medium">{policy.name}</h4>
                          <div className="flex items-center gap-2 mt-1">
                            <span className={`text-[10px] px-1.5 py-0.5 rounded border ${getSeverityColor(policy.severity)}`}>
                              {policy.severity}
                            </span>
                            <span className="text-[10px] text-muted-foreground">
                              Priority: {policy.priority}
                            </span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-mono">{policy.trigger_count}</div>
                          <div className="text-[10px] text-muted-foreground">triggers</div>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-4 gap-2 text-[10px]">
                        <div className="p-2 rounded bg-muted/50">
                          <div className="text-muted-foreground">Scope</div>
                          <div className="font-mono">{policy.policy_scope}</div>
                        </div>
                        <div className="p-2 rounded bg-muted/50">
                          <div className="text-muted-foreground">Action</div>
                          <div className="font-mono">{policy.enforcement_action}</div>
                        </div>
                        <div className="p-2 rounded bg-muted/50">
                          <div className="text-muted-foreground">Triggers</div>
                          <div className="font-mono">{policy.trigger_count}</div>
                        </div>
                        <div className="p-2 rounded bg-muted/50">
                          <div className="text-muted-foreground">Violations</div>
                          <div className="font-mono">{policy.violation_count}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </ConsolePanel>
            </div>
            
            {/* Policy Details */}
            <div>
              <ConsolePanel
                title="Policy Details"
                icon={<Eye className="h-4 w-4" />}
                subtitle={selectedPolicy?.name || 'Select policy'}
              >
                {selectedPolicy ? (
                  <div className="space-y-4">
                    <div className="space-y-1">
                      <span className="text-[10px] text-muted-foreground uppercase">Policy Key</span>
                      <div className="text-sm font-mono">{selectedPolicy.policy_key}</div>
                    </div>
                    
                    <div className="space-y-1">
                      <span className="text-[10px] text-muted-foreground uppercase">Conditions</span>
                      <div className="p-3 rounded bg-muted/50">
                        <pre className="text-[10px] font-mono overflow-auto">
                          {JSON.stringify(selectedPolicy.conditions, null, 2)}
                        </pre>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Severity</span>
                        <span className={`text-xs px-2 py-1 rounded border ${getSeverityColor(selectedPolicy.severity)}`}>
                          {selectedPolicy.severity}
                        </span>
                      </div>
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Priority</span>
                        <div className="text-sm font-mono">{selectedPolicy.priority}</div>
                      </div>
                    </div>
                    
                    <div className="space-y-1">
                      <span className="text-[10px] text-muted-foreground uppercase">Enforcement Action</span>
                      <div className="text-sm font-mono">{selectedPolicy.enforcement_action}</div>
                    </div>
                    
                    <div className="pt-2 border-t border-border/50">
                      <div className="grid grid-cols-2 gap-2">
                        <div className="text-center p-2 rounded bg-muted/50">
                          <div className="text-lg font-mono text-green-500">{selectedPolicy.trigger_count}</div>
                          <div className="text-[10px] text-muted-foreground">Total Triggers</div>
                        </div>
                        <div className="text-center p-2 rounded bg-muted/50">
                          <div className="text-lg font-mono text-red-500">{selectedPolicy.violation_count}</div>
                          <div className="text-[10px] text-muted-foreground">Violations</div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground text-sm">
                    Select a policy to view details
                  </div>
                )}
              </ConsolePanel>
            </div>
          </div>
        )}
        
        {activeTab === 'violations' && (
          <ConsolePanel
            title="Policy Violations"
            icon={<AlertTriangle className="h-4 w-4" />}
            subtitle={`${filteredViolations.length} violations`}
            headerContent={
              <div className="flex items-center gap-2">
                <select
                  value={severityFilter || ''}
                  onChange={e => setSeverityFilter(e.target.value || null)}
                  className="px-2 py-1 text-xs bg-muted/50 border border-border rounded focus:outline-none focus:border-primary/50"
                >
                  <option value="">All Severities</option>
                  <option value="critical">Critical</option>
                  <option value="violation">Violation</option>
                  <option value="warning">Warning</option>
                  <option value="info">Info</option>
                </select>
              </div>
            }
          >
            <DataTable
              columns={[
                { key: 'id', label: 'Violation ID', width: '15%' },
                { key: 'type', label: 'Type', width: '20%' },
                { key: 'severity', label: 'Severity', width: '15%' },
                { key: 'description', label: 'Description', width: '30%' },
                { key: 'detected', label: 'Detected', width: '15%' },
                { key: 'status', label: 'Status', width: '15%' },
              ]}
              rows={filteredViolations.map(v => ({
                id: <span className="font-mono text-xs">{v.violation_id}</span>,
                type: <span className="text-xs">{v.violation_type}</span>,
                severity: (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded border ${getSeverityColor(v.severity)}`}>
                    {v.severity}
                  </span>
                ),
                description: <span className="text-xs text-muted-foreground">{v.description}</span>,
                detected: <span className="text-xs font-mono text-muted-foreground">
                  {new Date(v.detected_at).toLocaleTimeString()}
                </span>,
                status: (
                  <div className="flex items-center gap-1">
                    {v.resolved ? (
                      <>
                        <CheckCircle2 className="h-3 w-3 text-green-500" />
                        <span className="text-xs text-green-500">Resolved</span>
                      </>
                    ) : (
                      <>
                        <XCircle className="h-3 w-3 text-red-500" />
                        <span className="text-xs text-red-500">Active</span>
                      </>
                    )}
                  </div>
                ),
              }))}
            />
          </ConsolePanel>
        )}
        
        {activeTab === 'arbitration' && (
          <div className="grid gap-4 lg:grid-cols-2">
            <ConsolePanel
              title="Recent Arbitrations"
              icon={<Scale className="h-4 w-4" />}
              subtitle="Orchestration decisions"
            >
              <div className="space-y-3">
                {[
                  { record_id: 'arb-001', arbitration_type: 'resource_allocation', decision: 'resource_allocated:optimizer-beta', reason: 'Lowest current load', confidence: 0.85 },
                  { record_id: 'arb-002', arbitration_type: 'task_priority', decision: 'priority_assigned:generator-alpha', reason: 'Highest capability match', confidence: 0.88 },
                  { record_id: 'arb-003', arbitration_type: 'conflict_resolution', decision: 'conflict_resolved:scheduler-primary', reason: 'Highest priority', confidence: 0.82 },
                ].map(arb => (
                  <div key={arb.record_id} className="p-4 rounded border border-border/50">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <span className="text-sm font-mono">{arb.record_id}</span>
                        <span className="text-xs text-muted-foreground ml-2">{arb.arbitration_type}</span>
                      </div>
                      <ConfidenceBadge value={arb.confidence} showLabel />
                    </div>
                    <div className="space-y-1 text-xs">
                      <div className="flex items-center gap-2">
                        <span className="text-muted-foreground">Decision:</span>
                        <span className="font-mono">{arb.decision}</span>
                      </div>
                      <div className="text-muted-foreground">{arb.reason}</div>
                    </div>
                  </div>
                ))}
              </div>
            </ConsolePanel>
            
            <ConsolePanel
              title="Conflict Resolution"
              icon={<AlertCircle className="h-4 w-4" />}
              subtitle="Active conflicts"
            >
              <div className="space-y-3">
                {[
                  { conflict: 'Resource Contention', agents: ['gen-alpha', 'opt-beta'], status: 'resolving' },
                  { conflict: 'Priority Inversion', agents: ['scheduler-1', 'scheduler-2'], status: 'pending' },
                ].map((conflict, idx) => (
                  <div key={idx} className="p-4 rounded border border-border/50">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">{conflict.conflict}</span>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                        conflict.status === 'resolving' ? 'bg-blue-500/10 text-blue-500' : 'bg-yellow-500/10 text-yellow-500'
                      }`}>
                        {conflict.status}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>Agents:</span>
                      {conflict.agents.map(agent => (
                        <span key={agent} className="font-mono px-1 py-0.5 rounded bg-muted">{agent}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </ConsolePanel>
          </div>
        )}
        
        {activeTab === 'rules' && (
          <ConsolePanel
            title="Governance Rules"
            icon={<Gavel className="h-4 w-4" />}
            subtitle="Active rule definitions"
          >
            <div className="text-center py-12 text-muted-foreground">
              <Gavel className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Rule editor coming soon</p>
            </div>
          </ConsolePanel>
        )}
      </div>
    </div>
  )
}