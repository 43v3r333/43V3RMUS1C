/**
 * 43V3R CORE - Recursive Supervision Workspace
 * 
 * Dedicated workspace for recursive cognition supervision with depth tracking,
 * session management, and artifact storage.
 * 
 * Enterprise orchestration intelligence interface.
 */
'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  Brain,
  Eye,
  GitBranch,
  Activity,
  Shield,
  Zap,
  Clock,
  AlertTriangle,
  CheckCircle2,
  Layers,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  FileText,
} from 'lucide-react'
import { useExecutiveApi } from '@/lib/executive-api'
import {
  ConsolePanel,
  StatusDot,
  ConfidenceBadge,
  DataTable,
  TabBar,
  IconButton,
  ProgressBar,
} from '@/components/cognitive/primitives'

// ---- Types ----

interface SupervisionSession {
  id: string
  session_key: string
  supervisor_id: string
  scope: string
  supervision_level: number
  target_id: string
  supervision_state: string
  confidence_score: number
  findings?: unknown[]
  recommendations?: string[]
  escalated: boolean
  started_at: string
  completed_at?: string
  duration_ms?: number
}

// ---- Main Component ----

export default function RecursiveSupervisionWorkspace() {
  const api = useExecutiveApi()
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('sessions')
  const [sessions, setSessions] = useState<SupervisionSession[]>([])
  const [expandedSession, setExpandedSession] = useState<string | null>(null)

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await api.listSupervisionSessions({ limit: 50 })
        setSessions(data as SupervisionSession[])
      } catch {
        // Mock data
        setSessions([
          {
            id: 'sess_001',
            session_key: 'sup_8a3f21',
            supervisor_id: 'orchestrator-01',
            scope: 'execution',
            supervision_level: 4,
            target_id: 'exec_render_001',
            supervision_state: 'active',
            confidence_score: 0.92,
            findings: [{ category: 'performance', severity: 'info', description: 'Memory usage within bounds' }],
            recommendations: ['Continue monitoring', 'Optimize batch sizes'],
            escalated: false,
            started_at: new Date(Date.now() - 300000).toISOString(),
            duration_ms: 300000,
          },
          {
            id: 'sess_002',
            session_key: 'sup_4c7d18',
            supervisor_id: 'supervisor-03',
            scope: 'governance',
            supervision_level: 5,
            target_id: 'policy_enforcement_01',
            supervision_state: 'reviewing',
            confidence_score: 0.88,
            findings: [],
            recommendations: ['Review escalation thresholds'],
            escalated: true,
            escalated_to: 'governor_level_6',
            started_at: new Date(Date.now() - 600000).toISOString(),
          },
        ])
      }
      setLoading(false)
    }

    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [api])

  const tabs = [
    { id: 'sessions', label: 'Sessions', icon: <Brain className="h-3 w-3" /> },
    { id: 'hierarchy', label: 'Hierarchy', icon: <GitBranch className="h-3 w-3" /> },
    { id: 'artifacts', label: 'Artifacts', icon: <FileText className="h-3 w-3" /> },
    { id: 'metrics', label: 'Metrics', icon: <Activity className="h-3 w-3" /> },
  ]

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-3">
          <Eye className="h-5 w-5 text-primary" />
          <span className="font-mono text-sm font-semibold tracking-tight">RECURSIVE SUPERVISION</span>
          <div className="h-4 w-px bg-border/50" />
          <StatusDot status={sessions.some(s => s.supervision_state === 'active') ? 'active' : 'idle'} />
          <span className="text-[10px] font-mono text-muted-foreground uppercase">
            {sessions.length} sessions
          </span>
        </div>
        <div className="flex items-center gap-2">
          <IconButton
            icon={<RefreshCw className="h-3 w-3" />}
            onClick={() => setLoading(true)}
          />
        </div>
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
            {activeTab === 'sessions' && (
              <div className="space-y-4">
                {/* Active Supervision Table */}
                <ConsolePanel
                  title="Supervision Sessions"
                  icon={<Brain className="h-4 w-4" />}
                  subtitle="Recursive cognition oversight"
                >
                  <DataTable
                    columns={[
                      { key: 'key', label: 'Session', width: '15%' },
                      { key: 'supervisor', label: 'Supervisor', width: '18%' },
                      { key: 'scope', label: 'Scope', width: '12%' },
                      { key: 'level', label: 'Level', width: '10%' },
                      { key: 'target', label: 'Target', width: '15%' },
                      { key: 'confidence', label: 'Confidence', width: '12%' },
                      { key: 'state', label: 'State', width: '10%' },
                      { key: 'actions', label: '', width: '8%' },
                    ]}
                    rows={sessions.map(s => ({
                      key: s.id,
                      key: <span className="font-mono text-xs">{s.session_key.slice(0, 12)}</span>,
                      supervisor: <span className="font-mono text-xs">{s.supervisor_id}</span>,
                      scope: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{s.scope}</span>,
                      level: (
                        <div className="flex items-center gap-1">
                          <div className="flex gap-0.5">
                            {Array.from({ length: 6 }).map((_, i) => (
                              <div
                                key={i}
                                className={`w-1.5 h-3 rounded-sm ${
                                  i < s.supervision_level ? 'bg-primary' : 'bg-muted'
                                }`}
                              />
                            ))}
                          </div>
                          <span className="text-[10px] font-mono ml-1">{s.supervision_level}</span>
                        </div>
                      ),
                      target: <span className="font-mono text-xs text-muted-foreground">{s.target_id.slice(0, 15)}</span>,
                      confidence: <ConfidenceBadge value={s.confidence_score} showLabel={false} />,
                      state: (
                        <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                          s.supervision_state === 'active' ? 'bg-green-500/10 text-green-500' :
                          s.supervision_state === 'reviewing' ? 'bg-blue-500/10 text-blue-500' :
                          s.supervision_state === 'escalated' ? 'bg-red-500/10 text-red-500' :
                          'bg-muted text-muted-foreground'
                        }`}>{s.supervision_state}</span>
                      ),
                      actions: (
                        <IconButton
                          icon={expandedSession === s.id ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
                          onClick={() => setExpandedSession(expandedSession === s.id ? null : s.id)}
                        />
                      ),
                    }))}
                  />
                </ConsolePanel>

                {/* Expanded Session Details */}
                {expandedSession && (
                  <ConsolePanel
                    title="Session Details"
                    icon={<FileText className="h-4 w-4" />}
                    subtitle={expandedSession}
                  >
                    {(() => {
                      const session = sessions.find(s => s.id === expandedSession)
                      if (!session) return null
                      return (
                        <div className="grid gap-4 lg:grid-cols-2">
                          <div className="space-y-3">
                            <div className="space-y-1">
                              <div className="text-[10px] text-muted-foreground uppercase">Session Key</div>
                              <div className="font-mono text-sm">{session.session_key}</div>
                            </div>
                            <div className="space-y-1">
                              <div className="text-[10px] text-muted-foreground uppercase">Supervisor</div>
                              <div className="font-mono text-sm">{session.supervisor_id}</div>
                            </div>
                            <div className="space-y-1">
                              <div className="text-[10px] text-muted-foreground uppercase">Target</div>
                              <div className="font-mono text-sm">{session.target_id}</div>
                            </div>
                            <div className="space-y-1">
                              <div className="text-[10px] text-muted-foreground uppercase">Started</div>
                              <div className="font-mono text-sm">{new Date(session.started_at).toLocaleString()}</div>
                            </div>
                          </div>
                          <div className="space-y-3">
                            <div className="space-y-1">
                              <div className="text-[10px] text-muted-foreground uppercase">Confidence Score</div>
                              <ConfidenceBadge value={session.confidence_score} />
                            </div>
                            {session.findings && session.findings.length > 0 && (
                              <div className="space-y-1">
                                <div className="text-[10px] text-muted-foreground uppercase">Findings ({session.findings.length})</div>
                                <div className="space-y-1">
                                  {session.findings.map((f: any, i: number) => (
                                    <div key={i} className="text-xs p-2 rounded bg-muted/50">
                                      <span className="font-medium">{f.category}</span>: {f.description}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            {session.recommendations && session.recommendations.length > 0 && (
                              <div className="space-y-1">
                                <div className="text-[10px] text-muted-foreground uppercase">Recommendations</div>
                                <ul className="text-xs space-y-1">
                                  {session.recommendations.map((r, i) => (
                                    <li key={i} className="flex items-center gap-2">
                                      <ChevronRight className="h-3 w-3 text-muted-foreground" />
                                      {r}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {session.escalated && (
                              <div className="flex items-center gap-2 p-2 rounded bg-red-500/10 border border-red-500/20">
                                <AlertTriangle className="h-4 w-4 text-red-500" />
                                <span className="text-xs text-red-500">Escalated to {session.escalated_to}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      )
                    })()}
                  </ConsolePanel>
                )}
              </div>
            )}

            {activeTab === 'hierarchy' && (
              <ConsolePanel
                title="Supervision Hierarchy"
                icon={<GitBranch className="h-4 w-4" />}
                subtitle="Recursive depth visualization"
              >
                <div className="space-y-2">
                  {[
                    { level: 6, name: 'MASTER', desc: 'Full recursive control', count: 2 },
                    { level: 5, name: 'GOVERNOR', desc: 'Governance oversight', count: 4 },
                    { level: 4, name: 'COORDINATOR', desc: 'Orchestration coordination', count: 8 },
                    { level: 3, name: 'REVIEWER', desc: 'Active review', count: 16 },
                    { level: 2, name: 'ADVISOR', desc: 'Advisory supervision', count: 32 },
                    { level: 1, name: 'OBSERVER', desc: 'Passive monitoring', count: 64 },
                    { level: 0, name: 'SURFACE', desc: 'Surface-level observation', count: 128 },
                  ].map((item) => (
                    <div key={item.level} className="flex items-center gap-4 p-3 rounded bg-muted/30 border border-border/30">
                      <div className="flex items-center gap-3 w-48">
                        <div
                          className="w-8 h-6 rounded bg-primary/20 border border-primary/40 flex items-center justify-center"
                        >
                          <span className="text-[10px] font-mono font-bold text-primary">{item.level}</span>
                        </div>
                        <div>
                          <span className="text-sm font-mono font-medium">{item.name}</span>
                          <div className="text-[10px] text-muted-foreground">{item.desc}</div>
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary rounded-full"
                            style={{ width: `${(item.count / 128) * 100}%` }}
                          />
                        </div>
                      </div>
                      <div className="w-16 text-right">
                        <span className="font-mono text-sm">{item.count}</span>
                        <div className="text-[10px] text-muted-foreground">sessions</div>
                      </div>
                    </div>
                  ))}
                </div>
              </ConsolePanel>
            )}

            {activeTab === 'artifacts' && (
              <ConsolePanel
                title="Supervision Artifacts"
                icon={<FileText className="h-4 w-4" />}
                subtitle="Stored supervision knowledge"
              >
                <div className="text-center py-8 text-muted-foreground">
                  <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No artifacts stored yet</p>
                  <p className="text-xs mt-1">Artifacts are created during supervision sessions</p>
                </div>
              </ConsolePanel>
            )}

            {activeTab === 'metrics' && (
              <div className="grid gap-4 lg:grid-cols-2">
                <ConsolePanel
                  title="Supervision Metrics"
                  icon={<Activity className="h-4 w-4" />}
                  subtitle="Session performance"
                >
                  <div className="space-y-3">
                    {[
                      { label: 'Avg Confidence', value: 0.89, color: 'success' },
                      { label: 'Escalation Rate', value: 0.08, color: 'warning' },
                      { label: 'Resolution Time', value: 240, unit: 'ms', color: 'primary' },
                      { label: 'Active Sessions', value: sessions.filter(s => s.supervision_state === 'active').length, color: 'primary' },
                    ].map((m) => (
                      <div key={m.label} className="flex items-center justify-between py-2 border-b border-border/30 last:border-0">
                        <span className="text-xs text-muted-foreground">{m.label}</span>
                        <span className="font-mono text-sm">
                          {m.value}{m.unit || '%'}
                        </span>
                      </div>
                    ))}
                  </div>
                </ConsolePanel>

                <ConsolePanel
                  title="Findings Distribution"
                  icon={<Layers className="h-4 w-4" />}
                  subtitle="By category"
                >
                  <div className="space-y-2">
                    {[
                      { category: 'performance', count: 45, pct: 38 },
                      { category: 'governance', count: 32, pct: 27 },
                      { category: 'semantic', count: 24, pct: 20 },
                      { category: 'execution', count: 17, pct: 14 },
                    ].map((item) => (
                      <div key={item.category} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="font-mono">{item.category}</span>
                          <span className="text-muted-foreground">{item.count}</span>
                        </div>
                        <ProgressBar value={item.pct} showValue={false} />
                      </div>
                    ))}
                  </div>
                </ConsolePanel>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
