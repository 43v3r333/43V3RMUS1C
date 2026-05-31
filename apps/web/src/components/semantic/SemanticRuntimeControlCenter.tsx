/**
 * 43V3R CORE - Semantic Runtime Control Center
 * 
 * Production-grade semantic ontology control interface.
 * Centralized semantic runtime management, concept registry,
 * and execution meaning governance.
 */
'use client'

import { useState, useEffect } from 'react'
import {
  Network,
  Database,
  GitBranch,
  Link2,
  BookOpen,
  ArrowUpRight,
  RefreshCw,
  Plus,
  Search,
  Filter,
  ChevronRight,
  Layers,
  Hash,
  Globe,
  Clock,
  Shield,
  Activity,
} from 'lucide-react'
import { ConsolePanel, MetricGrid, MetricValue, StatusDot, DataTable, TabBar, IconButton, ProgressBar, ConfidenceBadge } from '@/components/cognitive/primitives'

// ---- Types ----

interface ConceptSummary {
  totalConcepts: number
  activeConcepts: number
  relationships: number
  contracts: number
  propagationState: 'synced' | 'Propagating' | 'pending'
}

interface RuntimeConcept {
  concept_id: string
  concept_key: string
  concept_type: string
  category: string
  name: string
  status: string
  version: number
  propagation_state: string
  created_at: string
}

interface ConceptRelationship {
  relationship_id: string
  source_key: string
  target_key: string
  relationship_type: string
  weight: number
  confidence: number
}

interface SemanticContract {
  contract_id: string
  contract_key: string
  version: string
  name: string
  scope: string
  status: string
  created_at: string
}

// ---- Mock Data Generators ----

function generateMockConcepts(): RuntimeConcept[] {
  return [
    { concept_id: 'c1', concept_key: 'workflow.execution.start', concept_type: 'execution', category: 'orchestration', name: 'Workflow Start', status: 'active', version: 1, propagation_state: 'synced', created_at: new Date().toISOString() },
    { concept_id: 'c2', concept_key: 'workflow.execution.validate', concept_type: 'execution', category: 'orchestration', name: 'Input Validation', status: 'active', version: 1, propagation_state: 'synced', created_at: new Date().toISOString() },
    { concept_id: 'c3', concept_key: 'workflow.execution.process', concept_type: 'execution', category: 'orchestration', name: 'Data Processing', status: 'active', version: 2, propagation_state: 'synced', created_at: new Date().toISOString() },
    { concept_id: 'c4', concept_key: 'ai.generation.create', concept_type: 'semantic', category: 'ai_runtime', name: 'AI Generation', status: 'active', version: 1, propagation_state: 'synced', created_at: new Date().toISOString() },
    { concept_id: 'c5', concept_key: 'media.render.produce', concept_type: 'execution', category: 'media', name: 'Media Rendering', status: 'active', version: 1, propagation_state: 'pending', created_at: new Date().toISOString() },
    { concept_id: 'c6', concept_key: 'telemetry.observe.collect', concept_type: 'telemetry', category: 'observability', name: 'Telemetry Collection', status: 'active', version: 1, propagation_state: 'synced', created_at: new Date().toISOString() },
    { concept_id: 'c7', concept_key: 'cognition.reason.analyze', concept_type: 'cognition', category: 'cognitive', name: 'Cognitive Analysis', status: 'active', version: 1, propagation_state: 'synced', created_at: new Date().toISOString() },
    { concept_id: 'c8', concept_key: 'policy.govern.apply', concept_type: 'policy', category: 'governance', name: 'Policy Application', status: 'deprecated', version: 3, propagation_state: 'synced', created_at: new Date(Date.now() - 86400000).toISOString() },
  ]
}

function generateMockRelationships(): ConceptRelationship[] {
  return [
    { relationship_id: 'r1', source_key: 'workflow.execution.start', target_key: 'workflow.execution.validate', relationship_type: 'depends_on', weight: 1.0, confidence: 0.95 },
    { relationship_id: 'r2', source_key: 'workflow.execution.start', target_key: 'workflow.execution.process', relationship_type: 'depends_on', weight: 1.0, confidence: 0.95 },
    { relationship_id: 'r3', source_key: 'workflow.execution.validate', target_key: 'workflow.execution.process', relationship_type: 'enables', weight: 0.8, confidence: 0.9 },
    { relationship_id: 'r4', source_key: 'workflow.execution.process', target_key: 'ai.generation.create', relationship_type: 'produces', weight: 1.0, confidence: 0.98 },
    { relationship_id: 'r5', source_key: 'ai.generation.create', target_key: 'media.render.produce', relationship_type: 'depends_on', weight: 1.0, confidence: 0.97 },
    { relationship_id: 'r6', source_key: 'workflow.execution.process', target_key: 'telemetry.observe.collect', relationship_type: 'composes', weight: 0.7, confidence: 0.85 },
    { relationship_id: 'r7', source_key: 'cognition.reason.analyze', target_key: 'workflow.execution.process', relationship_type: 'relates_to', weight: 0.5, confidence: 0.75 },
  ]
}

function generateMockContracts(): SemanticContract[] {
  return [
    { contract_id: 'sc1', contract_key: 'contract.execution.standard', version: '2.1.0', name: 'Standard Execution Contract', scope: 'execution', status: 'active', created_at: new Date().toISOString() },
    { contract_id: 'sc2', contract_key: 'contract.telemetry.standard', version: '1.0.0', name: 'Telemetry Capture Contract', scope: 'telemetry', status: 'active', created_at: new Date().toISOString() },
    { contract_id: 'sc3', contract_key: 'contract.policy.standard', version: '1.5.0', name: 'Governance Policy Contract', scope: 'policy', status: 'active', created_at: new Date().toISOString() },
    { contract_id: 'sc4', contract_key: 'contract.orchestration.standard', version: '1.2.0', name: 'Orchestration Flow Contract', scope: 'orchestration', status: 'suspended', created_at: new Date(Date.now() - 172800000).toISOString() },
  ]
}

// ---- Main Component ----

export default function SemanticRuntimeControlCenter() {
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState<ConceptSummary>({
    totalConcepts: 0, activeConcepts: 0, relationships: 0, contracts: 0, propagationState: 'synced',
  })
  const [concepts, setConcepts] = useState<RuntimeConcept[]>([])
  const [relationships, setRelationships] = useState<ConceptRelationship[]>([])
  const [contracts, setContracts] = useState<SemanticContract[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState<string>('all')

  useEffect(() => {
    const loadData = async () => {
      try {
        // Load mock data
        const mockConcepts = generateMockConcepts()
        const mockRelationships = generateMockRelationships()
        const mockContracts = generateMockContracts()

        setSummary({
          totalConcepts: mockConcepts.length,
          activeConcepts: mockConcepts.filter(c => c.status === 'active').length,
          relationships: mockRelationships.length,
          contracts: mockContracts.filter(c => c.status === 'active').length,
          propagationState: 'synced',
        })

        setConcepts(mockConcepts)
        setRelationships(mockRelationships)
        setContracts(mockContracts)
      } catch {
        // Use defaults
      }
      setLoading(false)
    }

    loadData()
  }, [])

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Network className="h-3 w-3" /> },
    { id: 'concepts', label: 'Concepts', icon: <Database className="h-3 w-3" />, badge: concepts.length },
    { id: 'relationships', label: 'Relationships', icon: <Link2 className="h-3 w-3" />, badge: relationships.length },
    { id: 'contracts', label: 'Contracts', icon: <Shield className="h-3 w-3" />, badge: contracts.length },
  ]

  const filteredConcepts = concepts.filter(c => {
    const matchesSearch = !searchQuery || 
      c.concept_key.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filterType === 'all' || c.concept_type === filterType
    return matchesSearch && matchesFilter
  })

  const getStatusColor = (status: string) => {
    if (status === 'active') return 'text-green-500'
    if (status === 'deprecated') return 'text-yellow-500'
    if (status === 'archived') return 'text-neutral-400'
    return 'text-muted-foreground'
  }

  const getPropagationIcon = (state: string) => {
    if (state === 'synced') return <StatusDot status="active" size="sm" />
    if (state === 'propagating') return <StatusDot status="processing" size="sm" pulse />
    return <StatusDot status="idle" size="sm" />
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Globe className="h-5 w-5 text-primary" />
            <span className="font-mono text-sm font-semibold tracking-tight">SEMANTIC RUNTIME</span>
          </div>
          <div className="h-4 w-px bg-border/50" />
          <StatusDot status="active" size="sm" />
          <span className="text-[10px] font-mono text-muted-foreground uppercase">
            {summary.propagationState}
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
            label="Total Concepts"
            value={summary.totalConcepts}
            icon={<Database className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Active"
            value={summary.activeConcepts}
            icon={<Activity className="h-3 w-3" />}
            trend="up"
          />
          <MetricValue
            label="Relationships"
            value={summary.relationships}
            icon={<Link2 className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Contracts"
            value={summary.contracts}
            icon={<Shield className="h-3 w-3" />}
            trend="up"
          />
          <MetricValue
            label="Propagation"
            value={summary.propagationState}
            icon={<ArrowUpRight className="h-3 w-3" />}
            confidence={0.95}
          />
        </MetricGrid>
      </div>

      {/* Tabs */}
      <TabBar tabs={tabs} active={activeTab} onChange={setActiveTab} />

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {activeTab === 'overview' && (
          <div className="grid gap-4 lg:grid-cols-2">
            <ConsolePanel title="Concept Distribution" icon={<Layers className="h-4 w-4" />} subtitle="By type">
              <div className="space-y-3">
                {['execution', 'semantic', 'telemetry', 'policy', 'cognition'].map(type => {
                  const count = concepts.filter(c => c.concept_type === type).length
                  const total = concepts.length || 1
                  return (
                    <div key={type} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-muted-foreground font-mono">{type}</span>
                        <span className="font-mono">{count}</span>
                      </div>
                      <ProgressBar value={(count / total) * 100} showValue={false} color={count > 0 ? 'primary' : 'warning'} />
                    </div>
                  )
                })}
              </div>
            </ConsolePanel>

            <ConsolePanel title="Recent Concepts" icon={<Hash className="h-4 w-4" />} subtitle="Latest additions">
              <DataTable
                columns={[
                  { key: 'key', label: 'Concept Key', width: '50%' },
                  { key: 'type', label: 'Type', width: '25%' },
                  { key: 'state', label: 'State', width: '25%' },
                ]}
                rows={concepts.slice(0, 5).map(c => ({
                  key: <span className="font-mono text-xs truncate block max-w-[150px]">{c.concept_key}</span>,
                  type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{c.concept_type}</span>,
                  state: (
                    <div className="flex items-center gap-1">
                      {getPropagationIcon(c.propagation_state)}
                      <span className="text-[10px]">{c.propagation_state}</span>
                    </div>
                  ),
                }))}
              />
            </ConsolePanel>

            <ConsolePanel title="Relationship Network" icon={<Network className="h-4 w-4" />} subtitle="Graph topology">
              <div className="space-y-2">
                <div className="text-xs text-muted-foreground mb-2">Top Relationships</div>
                {relationships.slice(0, 5).map(rel => (
                  <div key={rel.relationship_id} className="flex items-center justify-between text-xs py-1 border-b border-border/30">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-[10px] text-muted-foreground truncate max-w-[80px]">{rel.source_key.split('.').pop()}</span>
                      <ArrowUpRight className="h-3 w-3 text-muted-foreground" />
                      <span className="font-mono text-[10px] text-muted-foreground truncate max-w-[80px]">{rel.target_key.split('.').pop()}</span>
                    </div>
                    <span className="text-[10px] px-1 py-0.5 rounded bg-muted">{rel.relationship_type}</span>
                  </div>
                ))}
              </div>
            </ConsolePanel>

            <ConsolePanel title="Contract Registry" icon={<Shield className="h-4 w-4" />} subtitle="Active contracts">
              <DataTable
                columns={[
                  { key: 'name', label: 'Contract', width: '40%' },
                  { key: 'version', label: 'Ver', width: '15%' },
                  { key: 'scope', label: 'Scope', width: '25%' },
                  { key: 'status', label: 'Status', width: '20%' },
                ]}
                rows={contracts.map(c => ({
                  name: <span className="text-xs truncate">{c.name}</span>,
                  version: <span className="font-mono text-[10px]">{c.version}</span>,
                  scope: <span className="text-[10px] px-1 py-0.5 rounded bg-muted">{c.scope}</span>,
                  status: <span className={`text-[10px] ${getStatusColor(c.status)}`}>{c.status}</span>,
                }))}
              />
            </ConsolePanel>
          </div>
        )}

        {activeTab === 'concepts' && (
          <div className="space-y-4">
            {/* Search and Filter */}
            <div className="flex items-center gap-2">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3 w-3 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Search concepts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full h-8 pl-9 pr-3 text-xs border border-border rounded bg-background"
                />
              </div>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="h-8 px-2 text-xs border border-border rounded bg-background"
              >
                <option value="all">All Types</option>
                <option value="execution">Execution</option>
                <option value="semantic">Semantic</option>
                <option value="telemetry">Telemetry</option>
                <option value="policy">Policy</option>
                <option value="cognition">Cognition</option>
              </select>
            </div>

            <ConsolePanel title="Concept Registry" icon={<Database className="h-4 w-4" />} subtitle={`${filteredConcepts.length} concepts`}>
              <DataTable
                columns={[
                  { key: 'key', label: 'Concept Key', width: '30%' },
                  { key: 'name', label: 'Name', width: '20%' },
                  { key: 'type', label: 'Type', width: '15%' },
                  { key: 'category', label: 'Category', width: '15%' },
                  { key: 'status', label: 'Status', width: '10%' },
                  { key: 'propagation', label: 'State', width: '10%' },
                ]}
                rows={filteredConcepts.map(c => ({
                  key: <span className="font-mono text-xs">{c.concept_key}</span>,
                  name: <span className="text-xs truncate">{c.name}</span>,
                  type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{c.concept_type}</span>,
                  category: <span className="text-[10px] text-muted-foreground">{c.category}</span>,
                  status: <span className={`text-[10px] ${getStatusColor(c.status)}`}>{c.status}</span>,
                  propagation: (
                    <div className="flex items-center gap-1">
                      {getPropagationIcon(c.propagation_state)}
                    </div>
                  ),
                }))}
              />
            </ConsolePanel>
          </div>
        )}

        {activeTab === 'relationships' && (
          <ConsolePanel title="Relationship Graph" icon={<Link2 className="h-4 w-4" />} subtitle={`${relationships.length} relationships`}>
            <DataTable
              columns={[
                { key: 'source', label: 'Source', width: '25%' },
                { key: 'type', label: 'Relation', width: '20%' },
                { key: 'target', label: 'Target', width: '25%' },
                { key: 'weight', label: 'Weight', width: '15%' },
                { key: 'confidence', label: 'Confidence', width: '15%' },
              ]}
              rows={relationships.map(r => ({
                source: <span className="font-mono text-xs truncate block max-w-[150px]">{r.source_key}</span>,
                type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{r.relationship_type}</span>,
                target: <span className="font-mono text-xs truncate block max-w-[150px]">{r.target_key}</span>,
                weight: <span className="font-mono">{r.weight.toFixed(2)}</span>,
                confidence: <ConfidenceBadge value={r.confidence} showLabel={false} />,
              }))}
            />
          </ConsolePanel>
        )}

        {activeTab === 'contracts' && (
          <div className="space-y-4">
            <ConsolePanel title="Semantic Contracts" icon={<Shield className="h-4 w-4" />} subtitle="Contract registry">
              <DataTable
                columns={[
                  { key: 'key', label: 'Contract Key', width: '25%' },
                  { key: 'name', label: 'Name', width: '25%' },
                  { key: 'version', label: 'Version', width: '15%' },
                  { key: 'scope', label: 'Scope', width: '15%' },
                  { key: 'status', label: 'Status', width: '10%' },
                  { key: 'created', label: 'Created', width: '10%' },
                ]}
                rows={contracts.map(c => ({
                  key: <span className="font-mono text-xs">{c.contract_key}</span>,
                  name: <span className="text-xs">{c.name}</span>,
                  version: <span className="font-mono text-xs">{c.version}</span>,
                  scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{c.scope}</span>,
                  status: <span className={`text-[10px] ${getStatusColor(c.status)}`}>{c.status}</span>,
                  created: <span className="text-[10px] text-muted-foreground">{new Date(c.created_at).toLocaleDateString()}</span>,
                }))}
              />
            </ConsolePanel>
          </div>
        )}
      </div>
    </div>
  )
}
