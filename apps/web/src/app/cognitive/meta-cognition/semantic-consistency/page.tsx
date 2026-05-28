/**
 * Semantic Consistency Dashboard
 * Semantic validation and consistency auditing interface.
 */
'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  GitBranch,
  AlertTriangle,
  CheckCircle2,
  Clock,
  RefreshCw,
  Play,
  Pause,
  Shield,
  TrendingUp,
  AlertCircle,
} from 'lucide-react'
import {
  useMetaCognitionApi,
  type SemanticConsistencyAudit,
} from '@/lib/meta-cognition-api'
import { ConsolePanel, DataTable, StatusDot, ConfidenceBadge, IconButton, ProgressBar, TabBar, Sparkline } from '@/components/cognitive/primitives'

// ==================== Mock Data ====================

const mockAudits: SemanticConsistencyAudit[] = [
  {
    audit_id: 'audit_001',
    audit_kind: 'reasoning_consistency',
    scope: 'global',
    audit_status: 'passed',
    severity: 'info',
    consistency_score: 0.95,
    divergence_detected: 0.02,
    resolution_required: false,
    audited_at: new Date(Date.now() - 600000).toISOString(),
  },
  {
    audit_id: 'audit_002',
    audit_kind: 'semantic_interpretation',
    scope: 'orchestration',
    audit_status: 'passed_with_warnings',
    severity: 'warning',
    consistency_score: 0.82,
    divergence_detected: 0.08,
    warnings: ['Inconsistent metric interpretation detected'],
    resolution_required: false,
    audited_at: new Date(Date.now() - 1200000).toISOString(),
  },
  {
    audit_id: 'audit_003',
    audit_kind: 'execution_semantics',
    scope: 'semantic',
    audit_status: 'passed',
    severity: 'info',
    consistency_score: 0.91,
    divergence_detected: 0.04,
    resolution_required: false,
    audited_at: new Date(Date.now() - 1800000).toISOString(),
  },
]

// ==================== Main Component ====================

export default function SemanticConsistencyDashboard() {
  const api = useMetaCognitionApi()
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [audits, setAudits] = useState<SemanticConsistencyAudit[]>([])
  const [selectedAudit, setSelectedAudit] = useState<string | null>(null)

  // Load data
  const loadData = useCallback(async () => {
    try {
      // Would load from API
      setAudits(mockAudits)
    } catch {
      setAudits(mockAudits)
    }
    setLoading(false)
  }, [api])

  useEffect(() => {
    loadData()
  }, [loadData])

  // Tabs
  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Shield className="h-3 w-3" /> },
    { id: 'audits', label: 'Audits', icon: <CheckCircle2 className="h-3 w-3" />, badge: audits.length },
    { id: 'violations', label: 'Violations', icon: <AlertTriangle className="h-3 w-3" /> },
  ]

  // Calculate metrics
  const avgConsistency = audits.length > 0
    ? audits.reduce((sum, a) => sum + a.consistency_score, 0) / audits.length
    : 0
  const passedAudits = audits.filter(a => a.audit_status === 'passed').length
  const warningAudits = audits.filter(a => a.audit_status === 'passed_with_warnings').length
  const failedAudits = audits.filter(a => a.audit_status === 'failed').length

  // Generate sparkline
  function generateSparkline(base: number, length = 12): number[] {
    const data: number[] = []
    let current = base
    for (let i = 0; i < length; i++) {
      current = current + (Math.random() - 0.5) * 0.08
      data.push(Math.max(0, Math.min(1, current)))
    }
    return data
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex items-center gap-2 text-muted-foreground">
          <RefreshCw className="h-4 w-4 animate-spin" />
          <span className="text-sm">Loading Semantic Consistency...</span>
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
            <Shield className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Semantic Consistency Dashboard</h1>
            <p className="text-xs text-muted-foreground">Semantic validation and consistency auditing</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <IconButton icon={<RefreshCw className="h-3.5 w-3.5" />} title="Refresh" onClick={loadData} />
        </div>
      </div>

      {/* Summary Grid */}
      <div className="grid grid-cols-5 gap-2">
        {[
          { label: 'Avg Consistency', value: `${(avgConsistency * 100).toFixed(1)}%`, icon: <TrendingUp className="h-3.5 w-3.5" /> },
          { label: 'Passed', value: passedAudits, icon: <CheckCircle2 className="h-3.5 w-3.5" /> },
          { label: 'Warnings', value: warningAudits, icon: <AlertCircle className="h-3.5 w-3.5" /> },
          { label: 'Failed', value: failedAudits, icon: <AlertTriangle className="h-3.5 w-3.5" /> },
          { label: 'Total Audits', value: audits.length, icon: <Shield className="h-3.5 w-3.5" /> },
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

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-4">
          {/* Consistency Metrics */}
          <div className="grid grid-cols-3 gap-4">
            {audits.slice(0, 3).map((audit) => (
              <ConsolePanel
                key={audit.audit_id}
                title={audit.audit_kind.replace(/_/g, ' ').toUpperCase()}
                icon={audit.audit_status === 'passed' ? <CheckCircle2 className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
                subtitle={`Score: ${(audit.consistency_score * 100).toFixed(1)}%`}
              >
                <div className="space-y-3">
                  <ProgressBar
                    value={audit.consistency_score * 100}
                    showValue
                    color={audit.consistency_score >= 0.9 ? 'success' : audit.consistency_score >= 0.7 ? 'warning' : 'error'}
                  />
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="text-muted-foreground">Divergence</span>
                    <span className="font-mono">{((audit.divergence_detected || 0) * 100).toFixed(2)}%</span>
                  </div>
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="text-muted-foreground">Status</span>
                    <span className={`px-1.5 py-0.5 rounded ${
                      audit.audit_status === 'passed' ? 'bg-green-500/10 text-green-500' :
                      audit.audit_status === 'passed_with_warnings' ? 'bg-yellow-500/10 text-yellow-500' :
                      'bg-red-500/10 text-red-500'
                    }`}>{audit.audit_status.replace(/_/g, ' ').toUpperCase()}</span>
                  </div>
                </div>
              </ConsolePanel>
            ))}
          </div>

          {/* Recent Audit History */}
          <ConsolePanel title="Recent Audit History" icon={<Clock className="h-4 w-4" />} subtitle="Latest consistency checks">
            <div className="space-y-2">
              {audits.map((audit) => (
                <div key={audit.audit_id} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                  <div className="flex items-center gap-3">
                    {audit.audit_status === 'passed' ? (
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                    ) : audit.audit_status === 'passed_with_warnings' ? (
                      <AlertCircle className="h-4 w-4 text-yellow-500" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-red-500" />
                    )}
                    <div>
                      <span className="text-xs font-medium">{audit.audit_kind.replace(/_/g, ' ')}</span>
                      <div className="text-[10px] text-muted-foreground">
                        {new Date(audit.audited_at).toLocaleTimeString()} | Scope: {audit.scope}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-[10px] text-muted-foreground">Consistency</div>
                      <div className="font-mono text-sm">{(audit.consistency_score * 100).toFixed(1)}%</div>
                    </div>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                      audit.severity === 'info' ? 'bg-blue-500/10 text-blue-500' :
                      audit.severity === 'warning' ? 'bg-yellow-500/10 text-yellow-500' :
                      'bg-red-500/10 text-red-500'
                    }`}>{audit.severity.toUpperCase()}</span>
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>
        </div>
      )}

      {/* Audits Tab */}
      {activeTab === 'audits' && (
        <ConsolePanel title="All Audits" icon={<CheckCircle2 className="h-4 w-4" />} subtitle={`${audits.length} total audits`}>
          <DataTable
            columns={[
              { key: 'audit_id', label: 'Audit ID', width: '15%' },
              { key: 'kind', label: 'Kind', width: '18%' },
              { key: 'scope', label: 'Scope', width: '12%' },
              { key: 'score', label: 'Score', width: '12%' },
              { key: 'divergence', label: 'Divergence', width: '12%' },
              { key: 'status', label: 'Status', width: '15%' },
              { key: 'audited', label: 'Audited', width: '16%' },
            ]}
            rows={audits.map(a => ({
              audit_id: <span className="font-mono text-xs">{a.audit_id.slice(0, 12)}...</span>,
              kind: <span className="text-xs">{a.audit_kind.replace(/_/g, ' ')}</span>,
              scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{a.scope}</span>,
              score: <div className="flex items-center gap-2"><ProgressBar value={a.consistency_score * 100} showValue={false} color={a.consistency_score >= 0.9 ? 'success' : 'warning'} className="w-16" /><span className="font-mono text-xs">{(a.consistency_score * 100).toFixed(0)}%</span></div>,
              divergence: <span className="font-mono text-xs">{((a.divergence_detected || 0) * 100).toFixed(2)}%</span>,
              status: <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                a.audit_status === 'passed' ? 'bg-green-500/10 text-green-500' :
                a.audit_status === 'passed_with_warnings' ? 'bg-yellow-500/10 text-yellow-500' :
                'bg-red-500/10 text-red-500'
              }`}>{a.audit_status.replace(/_/g, ' ').toUpperCase()}</span>,
              audited: <span className="text-xs text-muted-foreground">{new Date(a.audited_at).toLocaleString()}</span>,
            }))}
          />
        </ConsolePanel>
      )}

      {/* Violations Tab */}
      {activeTab === 'violations' && (
        <ConsolePanel title="Violations & Warnings" icon={<AlertTriangle className="h-4 w-4" />} subtitle="Semantic consistency violations">
          {audits.filter(a => a.warnings && a.warnings.length > 0).length === 0 ? (
            <div className="flex items-center gap-2 py-8">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              <span className="text-xs text-muted-foreground">No violations detected - all semantic checks passed</span>
            </div>
          ) : (
            <div className="space-y-3">
              {audits.filter(a => a.warnings && a.warnings.length > 0).map(audit => (
                <div key={audit.audit_id} className="p-3 rounded border border-yellow-500/20 bg-yellow-500/5">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <AlertCircle className="h-4 w-4 text-yellow-500" />
                      <span className="text-xs font-medium">{audit.audit_kind.replace(/_/g, ' ')}</span>
                    </div>
                    <span className="text-[10px] text-muted-foreground">{new Date(audit.audited_at).toLocaleTimeString()}</span>
                  </div>
                  <div className="space-y-1">
                    {audit.warnings?.map((warning, i) => (
                      <div key={i} className="text-xs text-yellow-500/80">• {warning}</div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </ConsolePanel>
      )}
    </div>
  )
}
