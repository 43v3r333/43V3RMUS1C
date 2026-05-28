/**
 * Orchestration Introspection Console
 * Execution reasoning analyzer and lineage tracking.
 */
'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  GitBranch,
  Brain,
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  RefreshCw,
  Play,
  Pause,
  Eye,
  TrendingUp,
  Zap,
  Layers,
} from 'lucide-react'
import {
  useMetaCognitionApi,
  type OrchestrationReasoningLineage,
} from '@/lib/meta-cognition-api'
import { ConsolePanel, DataTable, StatusDot, ConfidenceBadge, IconButton, ProgressBar, TabBar } from '@/components/cognitive/primitives'

// ==================== Mock Data ====================

const mockLineages: OrchestrationReasoningLineage[] = [
  {
    lineage_id: 'lineage_001',
    execution_id: 'exec_render_001',
    reasoning_type: 'deductive',
    inference_pattern: 'chain',
    lineage_chain: 'exec_render_001_chain',
    chain_position: 0,
    premise: 'Render pipeline requires GPU allocation',
    inference: 'Check GPU availability and queue state',
    conclusion: 'Allocate GPU for render job',
    evidence: [{ type: 'metric_check', value: 0.95 }],
    confidence: 0.92,
    reasoning_depth: 1,
    verified: true,
    created_at: new Date(Date.now() - 300000).toISOString(),
  },
  {
    lineage_id: 'lineage_002',
    execution_id: 'exec_render_001',
    reasoning_type: 'causal',
    inference_pattern: 'chain',
    lineage_chain: 'exec_render_001_chain',
    chain_position: 1,
    premise: 'GPU allocated successfully',
    inference: 'Dispatch render tasks with priority ordering',
    conclusion: 'Execute render tasks in parallel',
    evidence: [{ type: 'resource_state', gpu_available: true }],
    confidence: 0.88,
    reasoning_depth: 2,
    verified: true,
    created_at: new Date(Date.now() - 250000).toISOString(),
  },
  {
    lineage_id: 'lineage_003',
    execution_id: 'exec_render_001',
    reasoning_type: 'abductive',
    inference_pattern: 'chain',
    lineage_chain: 'exec_render_001_chain',
    chain_position: 2,
    premise: 'Partial render output detected',
    inference: 'Analyze error patterns for root cause',
    conclusion: 'Retry failed frames with adjusted parameters',
    evidence: [{ type: 'error_analysis', frames_failed: 3 }],
    confidence: 0.75,
    reasoning_depth: 3,
    verified: false,
    created_at: new Date(Date.now() - 180000).toISOString(),
  },
]

// ==================== Main Component ====================

export default function OrchestrationIntrospectionConsole() {
  const api = useMetaCognitionApi()
  const [activeTab, setActiveTab] = useState('lineage')
  const [loading, setLoading] = useState(true)
  const [lineages, setLineages] = useState<OrchestrationReasoningLineage[]>([])
  const [selectedExecution, setSelectedExecution] = useState<string>('exec_render_001')

  // Load data
  const loadData = useCallback(async () => {
    try {
      try {
        const data = await api.getReasoningLineage(selectedExecution)
        setLineages(data)
      } catch {
        setLineages(mockLineages)
      }
    } catch {
      setLineages(mockLineages)
    }
    setLoading(false)
  }, [api, selectedExecution])

  useEffect(() => {
    loadData()
  }, [loadData])

  // Tabs
  const tabs = [
    { id: 'lineage', label: 'Lineage', icon: <GitBranch className="h-3 w-3" /> },
    { id: 'reasoning', label: 'Reasoning', icon: <Brain className="h-3 w-3" /> },
    { id: 'validation', label: 'Validation', icon: <CheckCircle2 className="h-3 w-3" /> },
  ]

  // Calculate metrics
  const avgConfidence = lineages.length > 0
    ? lineages.reduce((sum, l) => sum + l.confidence, 0) / lineages.length
    : 0
  const verifiedCount = lineages.filter(l => l.verified).length
  const avgDepth = lineages.length > 0
    ? lineages.reduce((sum, l) => sum + l.reasoning_depth, 0) / lineages.length
    : 0

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex items-center gap-2 text-muted-foreground">
          <RefreshCw className="h-4 w-4 animate-spin" />
          <span className="text-sm">Loading Orchestration Introspection...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 border border-primary/20">
            <GitBranch className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Orchestration Introspection Console</h1>
            <p className="text-xs text-muted-foreground">Execution reasoning analysis and lineage tracking</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <IconButton icon={<RefreshCw className="h-3.5 w-3.5" />} title="Refresh" onClick={loadData} />
        </div>
      </div>

      {/* Summary Grid */}
      <div className="grid grid-cols-5 gap-2">
        {[
          { label: 'Total Lineages', value: lineages.length, icon: <GitBranch className="h-3.5 w-3.5" /> },
          { label: 'Avg Confidence', value: `${(avgConfidence * 100).toFixed(1)}%`, icon: <Activity className="h-3.5 w-3.5" /> },
          { label: 'Verified', value: verifiedCount, icon: <CheckCircle2 className="h-3.5 w-3.5" /> },
          { label: 'Avg Depth', value: avgDepth.toFixed(1), icon: <Layers className="h-3.5 w-3.5" /> },
          { label: 'Pending Verify', value: lineages.length - verifiedCount, icon: <AlertTriangle className="h-3.5 w-3.5" /> },
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

      {/* Lineage Tab */}
      {activeTab === 'lineage' && (
        <div className="space-y-4">
          <ConsolePanel title="Reasoning Lineage Chain" icon={<GitBranch className="h-4 w-4" />} subtitle={`Execution: ${selectedExecution}`}>
            <DataTable
              columns={[
                { key: 'position', label: 'Pos', width: '8%' },
                { key: 'lineage_id', label: 'Lineage ID', width: '14%' },
                { key: 'reasoning_type', label: 'Type', width: '12%' },
                { key: 'premise', label: 'Premise', width: '20%' },
                { key: 'conclusion', label: 'Conclusion', width: '20%' },
                { key: 'confidence', label: 'Confidence', width: '12%' },
                { key: 'verified', label: 'Verified', width: '14%' },
              ]}
              rows={lineages.map(l => ({
                position: <span className="font-mono text-xs bg-primary/10 px-1.5 py-0.5 rounded">{l.chain_position}</span>,
                lineage_id: <span className="font-mono text-xs">{l.lineage_id.slice(0, 12)}...</span>,
                reasoning_type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{l.reasoning_type}</span>,
                premise: <span className="text-xs truncate block max-w-48" title={l.premise}>{l.premise}</span>,
                conclusion: <span className="text-xs truncate block max-w-48" title={l.conclusion}>{l.conclusion}</span>,
                confidence: <ConfidenceBadge value={l.confidence} showLabel={false} />,
                verified: l.verified
                  ? <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/10 text-green-500 flex items-center gap-1"><CheckCircle2 className="h-3 w-3" />VERIFIED</span>
                  : <span className="text-[10px] px-1.5 py-0.5 rounded bg-yellow-500/10 text-yellow-500 flex items-center gap-1"><AlertTriangle className="h-3 w-3" />PENDING</span>,
              }))}
            />
          </ConsolePanel>

          {/* Visual Lineage Chain */}
          <ConsolePanel title="Lineage Visualization" icon={<Eye className="h-4 w-4" />} subtitle="Reasoning flow">
            <div className="space-y-2">
              {lineages.map((lineage, i) => (
                <div key={lineage.lineage_id} className="flex items-center gap-3">
                  {/* Position */}
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 border border-primary/30">
                    <span className="font-mono text-xs">{lineage.chain_position}</span>
                  </div>
                  
                  {/* Connector */}
                  {i < lineages.length - 1 && (
                    <div className="h-6 w-0.5 bg-border ml-4" />
                  )}
                  
                  {/* Content */}
                  <div className="flex-1 flex items-center gap-4 p-3 rounded border border-border/50 bg-card">
                    <div className="flex-1">
                      <div className="text-xs font-medium">{lineage.conclusion}</div>
                      <div className="text-[10px] text-muted-foreground mt-0.5">{lineage.reasoning_type} reasoning</div>
                    </div>
                    <div className="flex items-center gap-3">
                      <ConfidenceBadge value={lineage.confidence} showLabel />
                      {lineage.verified ? (
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                      ) : (
                        <AlertTriangle className="h-4 w-4 text-yellow-500" />
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>
        </div>
      )}

      {/* Reasoning Tab */}
      {activeTab === 'reasoning' && (
        <ConsolePanel title="Reasoning Analysis" icon={<Brain className="h-4 w-4" />} subtitle="Detailed reasoning breakdown">
          <div className="space-y-4">
            {lineages.map((lineage) => (
              <div key={lineage.lineage_id} className="p-4 rounded border border-border bg-card">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{lineage.reasoning_type}</span>
                    <span className="text-xs text-muted-foreground">Chain position: {lineage.chain_position}</span>
                  </div>
                  <ConfidenceBadge value={lineage.confidence} showLabel />
                </div>
                
                <div className="space-y-2">
                  <div>
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">PREMISE</div>
                    <div className="text-sm">{lineage.premise}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-0.5 flex-1 bg-border" />
                    <Zap className="h-3 w-3 text-muted-foreground" />
                    <div className="h-0.5 flex-1 bg-border" />
                  </div>
                  <div>
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">INFERENCE</div>
                    <div className="text-sm">{lineage.inference}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-0.5 flex-1 bg-primary/30" />
                    <TrendingUp className="h-3 w-3 text-primary" />
                    <div className="h-0.5 flex-1 bg-primary/30" />
                  </div>
                  <div>
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">CONCLUSION</div>
                    <div className="text-sm font-medium">{lineage.conclusion}</div>
                  </div>
                </div>

                {lineage.evidence && lineage.evidence.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border">
                    <div className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2">EVIDENCE</div>
                    <div className="flex flex-wrap gap-2">
                      {lineage.evidence.map((e, i) => (
                        <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-primary/10 text-primary">
                          {typeof e === 'object' ? Object.entries(e).map(([k, v]) => `${k}: ${v}`).join(', ') : String(e)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </ConsolePanel>
      )}

      {/* Validation Tab */}
      {activeTab === 'validation' && (
        <ConsolePanel title="Reasoning Validation" icon={<CheckCircle2 className="h-4 w-4" />} subtitle="Verify reasoning chain integrity">
          <div className="space-y-3">
            {lineages.map((lineage, i) => (
              <div key={lineage.lineage_id} className="flex items-center justify-between py-3 border-b border-border/50 last:border-0">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">#{lineage.chain_position}</span>
                  <div>
                    <div className="text-xs font-medium">{lineage.lineage_id.slice(0, 16)}...</div>
                    <div className="text-[10px] text-muted-foreground">{lineage.reasoning_type} reasoning</div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-[10px] text-muted-foreground">Confidence</div>
                    <div className="font-mono text-sm">{lineage.confidence.toFixed(3)}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] text-muted-foreground">Depth</div>
                    <div className="font-mono text-sm">{lineage.reasoning_depth}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] text-muted-foreground">Status</div>
                    {lineage.verified ? (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/10 text-green-500">VERIFIED</span>
                    ) : (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-yellow-500/10 text-yellow-500">PENDING</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ConsolePanel>
      )}
    </div>
  )
}
