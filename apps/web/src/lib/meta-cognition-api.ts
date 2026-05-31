/**
 * 43V3R CORE - Meta-Cognition API Client
 * Typed client for executive intelligence layer endpoints.
 */
'use client'

import { useCallback } from 'react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

// =====================================================================
// Types
// =====================================================================

// ---- Cognition Diagnostics ----

export interface CognitionDiagnostics {
  diagnostic_id: string
  scope: string
  domain: string
  cognition_state: 'healthy' | 'drifting' | 'conflicted' | 'degraded' | 'recovering' | 'unknown'
  reasoning_quality: number
  coherence_score: number
  consistency_score: number
  adaptation_efficiency: number
  distribution_alignment: number
  sync_health: number
  conflict_rate: number
  detected_anomalies?: Array<{
    type: string
    severity?: string
    [key: string]: unknown
  }>
  anomaly_severity?: 'info' | 'warning' | 'error' | 'critical'
  recommendations?: Array<{
    type: string
    priority: string
    action: string
    expected_impact: string
  }>
  assessed_at: string
  correlation_id?: string
}

export interface CognitionDiagnosticsCreate {
  scope: string
  domain: string
  diagnostic_types?: string[]
}

// ---- Introspection Session ----

export interface IntrospectionSession {
  session_id: string
  execution_id?: string
  workflow_id?: string
  scope: string
  phase: 'initializing' | 'observing' | 'analyzing' | 'synthesizing' | 'reporting' | 'completed' | 'failed'
  introspection_type: string
  focus_areas: string[]
  findings?: Array<Record<string, unknown>>
  insights?: string[]
  confidence: number
  depth_achieved: number
  breadth_achieved: number
  is_active: boolean
  error?: string
  started_at: string
  completed_at?: string
  duration_ms?: number
}

export interface IntrospectionSessionCreate {
  scope: string
  introspection_type: string
  execution_id?: string
  workflow_id?: string
  focus_areas?: string[]
}

// ---- Semantic Consistency Audit ----

export interface SemanticConsistencyAudit {
  audit_id: string
  audit_kind: string
  scope: string
  audit_status: 'passed' | 'passed_with_warnings' | 'failed'
  severity: 'info' | 'warning' | 'error' | 'critical'
  consistency_score: number
  divergence_detected?: number
  violations?: Array<Record<string, unknown>>
  warnings?: string[]
  target_entities?: string[]
  resolution_required: boolean
  resolution_applied?: string
  audited_at: string
  correlation_id?: string
}

export interface SemanticAuditCreate {
  audit_kind: string
  scope: string
  target_entities?: string[]
}

// ---- Adaptive Governance Profile ----

export interface AdaptiveGovernanceProfile {
  profile_id: string
  profile_key: string
  scope: string
  domain: string
  validation_thresholds: Record<string, number>
  alignment_requirements: Record<string, unknown>
  enforcement_rules: Array<Record<string, unknown>>
  policy_mode: string
  intervention_level: string
  is_active: boolean
  alignment_status: 'aligned' | 'misaligned' | 'deviating' | 'pending_review'
  trigger_count: number
  violation_count: number
  last_triggered?: string
  version: number
  updated_at?: string
}

export interface GovernanceProfileCreate {
  profile_key: string
  scope: string
  domain: string
  validation_thresholds?: Record<string, number>
  enforcement_rules?: Array<Record<string, unknown>>
}

// ---- Cognition Reconciliation State ----

export interface CognitionReconciliationState {
  state_id: string
  node_id: string
  scope: string
  reconciliation_status: 'synced' | 'pending' | 'conflicting' | 'resolving'
  last_sync_at?: string
  sync_version: number
  pending_updates: number
  active_conflicts?: Array<Record<string, unknown>>
  resolved_conflicts?: number
  sync_health_score: number
  latency_ms?: number
  created_at: string
  updated_at?: string
}

export interface ReconciliationRequest {
  node_id: string
  scope: string
  sync_version?: number
}

// ---- Predictive Cognition Forecast ----

export interface PredictiveCognitionForecast {
  forecast_id: string
  target_id: string
  target_type: string
  scope: string
  forecast_kind: string
  horizon: 'immediate' | 'near_term' | 'short' | 'medium'
  predicted_value: number
  confidence: number
  probability: number
  min_value?: number
  max_value?: number
  indicators?: Array<Record<string, unknown>>
  risk_factors?: string[]
  recommended_actions?: string[]
  risk_level: 'low' | 'medium' | 'high'
  actual_value?: number
  predicted: boolean
  predicted_for: string
  generated_at: string
}

export interface ForecastRequest {
  target_id: string
  target_type: string
  scope: string
  horizon?: string
}

// ---- Reasoning Lineage ----

export interface OrchestrationReasoningLineage {
  lineage_id: string
  execution_id: string
  session_id?: string
  reasoning_type: string
  inference_pattern: string
  lineage_chain: string
  chain_position: number
  premise: string
  inference: string
  conclusion: string
  evidence?: Array<Record<string, unknown>>
  confidence: number
  reasoning_depth: number
  decision_context?: Record<string, unknown>
  validation_result?: string
  verified: boolean
  parent_lineage_id?: string
  created_at: string
}

export interface ReasoningStepCreate {
  execution_id: string
  reasoning_type: string
  premise: string
  inference: string
  conclusion: string
  evidence?: Array<Record<string, unknown>>
  parent_lineage_id?: string
  session_id?: string
}

// ---- Cognition Anomaly ----

export interface CognitionAnomaly {
  anomaly_id: string
  anomaly_type: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  target_id: string
  target_type: string
  scope: string
  detection_method: string
  detection_signals?: Array<Record<string, unknown>>
  expected_value?: number
  actual_value?: number
  deviation?: number
  impact_scope?: string
  impact_severity?: string
  status: 'detected' | 'resolved'
  remediation_action?: string
  resolved_at?: string
  correlation_id?: string
  detected_at: string
}

export interface CognitionAnomalyCreate {
  anomaly_type: string
  target_id: string
  target_type: string
  scope: string
  detection_method: string
  detection_signals?: Array<Record<string, unknown>>
  severity?: string
  expected_value?: number
  actual_value?: number
  correlation_id?: string
}

// ---- Meta-Cognition Summary ----

export interface MetaCognitionSummary {
  cognition_state: string
  active_sessions: number
  active_anomalies: number
  pending_reconciliations: number
  active_forecasts: number
  governance_alignment: string
  last_diagnostics?: CognitionDiagnostics
}

export interface MetaCognitionHealth {
  engine_status: string
  active_sessions: number
  queued_processes: number
  cache_size: number
  uptime_seconds: number
}

// ---- Runtime Self-Awareness Metrics ----

export interface RuntimeSelfAwarenessMetrics {
  metric_id: string
  session_id?: string
  execution_id?: string
  scope: string
  introspection_depth: number
  reflection_accuracy: number
  self_model_accuracy: number
  introspection_latency_ms: number
  processing_overhead: number
  insight_relevance: number
  finding_accuracy: number
  metric_type: string
  metadata?: Record<string, unknown>
  timestamp: string
}

// =====================================================================
// API Hook
// =====================================================================

export function useMetaCognitionApi() {
  // ---- Diagnostics ----

  const runDiagnostics = useCallback(async (data: CognitionDiagnosticsCreate) => {
    return fetchApi<CognitionDiagnostics>('/meta-cognition/diagnostics', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const getDiagnosticsHistory = useCallback(async (params: {
    scope: string
    since?: string
    limit?: number
  }) => {
    const qs = new URLSearchParams()
    qs.set('scope', params.scope)
    if (params.since) qs.set('since', params.since)
    if (params.limit) qs.set('limit', String(params.limit))
    return fetchApi<CognitionDiagnostics[]>(`/meta-cognition/diagnostics/history?${qs}`)
  }, [])

  // ---- Introspection Sessions ----

  const startIntrospectionSession = useCallback(async (data: IntrospectionSessionCreate) => {
    return fetchApi<IntrospectionSession>('/meta-cognition/introspection', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const getIntrospectionSession = useCallback(async (sessionId: string) => {
    return fetchApi<IntrospectionSession>(`/meta-cognition/introspection/${sessionId}`)
  }, [])

  // ---- Semantic Audits ----

  const conductSemanticAudit = useCallback(async (data: SemanticAuditCreate) => {
    return fetchApi<SemanticConsistencyAudit>('/meta-cognition/audits', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const getSemanticAudit = useCallback(async (auditId: string) => {
    return fetchApi<SemanticConsistencyAudit>(`/meta-cognition/audits/${auditId}`)
  }, [])

  // ---- Governance Profiles ----

  const createGovernanceProfile = useCallback(async (data: GovernanceProfileCreate) => {
    return fetchApi<AdaptiveGovernanceProfile>('/meta-cognition/governance/profiles', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const listGovernanceProfiles = useCallback(async (params: {
    scope?: string
    active_only?: boolean
  } = {}) => {
    const qs = new URLSearchParams()
    if (params.scope) qs.set('scope', params.scope)
    qs.set('active_only', String(params.active_only ?? true))
    return fetchApi<AdaptiveGovernanceProfile[]>(`/meta-cognition/governance/profiles?${qs}`)
  }, [])

  const updateGovernanceProfile = useCallback(async (
    profileId: string,
    data: { validation_thresholds?: Record<string, number>; enforcement_rules?: Array<Record<string, unknown>>; is_active?: boolean }
  ) => {
    return fetchApi<{ status: string; profile_id: string }>(`/meta-cognition/governance/profiles/${profileId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }, [])

  // ---- Cognitive Reconciliation ----

  const reconcileCognition = useCallback(async (data: ReconciliationRequest) => {
    return fetchApi<CognitionReconciliationState>('/meta-cognition/reconciliation', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const getCognitionConflicts = useCallback(async (scope: string) => {
    return fetchApi<Array<Record<string, unknown>>>(`/meta-cognition/reconciliation/conflicts?scope=${scope}`)
  }, [])

  // ---- Predictive Cognition ----

  const forecastCognitionDrift = useCallback(async (data: ForecastRequest) => {
    return fetchApi<PredictiveCognitionForecast>('/meta-cognition/forecasts', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const getForecasts = useCallback(async (targetId: string, limit = 10) => {
    return fetchApi<PredictiveCognitionForecast[]>(`/meta-cognition/forecasts/${targetId}?limit=${limit}`)
  }, [])

  // ---- Reasoning Lineage ----

  const recordReasoningStep = useCallback(async (data: ReasoningStepCreate) => {
    return fetchApi<OrchestrationReasoningLineage>('/meta-cognition/reasoning', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const getReasoningLineage = useCallback(async (executionId: string) => {
    return fetchApi<OrchestrationReasoningLineage[]>(`/meta-cognition/reasoning/${executionId}`)
  }, [])

  // ---- Anomaly Registry ----

  const registerAnomaly = useCallback(async (data: CognitionAnomalyCreate) => {
    return fetchApi<CognitionAnomaly>('/meta-cognition/anomalies', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const getActiveAnomalies = useCallback(async (params: {
    scope?: string
    severity?: string
  } = {}) => {
    const qs = new URLSearchParams()
    if (params.scope) qs.set('scope', params.scope)
    if (params.severity) qs.set('severity', params.severity)
    return fetchApi<CognitionAnomaly[]>(`/meta-cognition/anomalies?${qs}`)
  }, [])

  const resolveAnomaly = useCallback(async (anomalyId: string, remediationAction: string) => {
    return fetchApi<{ status: string; anomaly_id: string }>(
      `/meta-cognition/anomalies/${anomalyId}/resolve?remediation_action=${encodeURIComponent(remediationAction)}`,
      { method: 'POST' }
    )
  }, [])

  // ---- Summary & Health ----

  const getMetaCognitionSummary = useCallback(async (scope = 'global') => {
    return fetchApi<MetaCognitionSummary>(`/meta-cognition/summary?scope=${scope}`)
  }, [])

  const getMetaCognitionHealth = useCallback(async () => {
    return fetchApi<MetaCognitionHealth>('/meta-cognition/health')
  }, [])

  // ---- WebSocket ----

  const createMetaCognitionSocket = useCallback((streamType = 'default') => {
    if (typeof window === 'undefined') return null
    const token = localStorage.getItem('access_token') || ''
    const wsUrl = (process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000').replace('http', 'ws') + `/ws/meta-cognition/stream`
    const ws = new WebSocket(`${wsUrl}?stream_type=${streamType}${token ? `&token=${token}` : ''}`)

    const subscribe = (channels: string[]) => {
      ws.send(JSON.stringify({ type: 'subscribe', channels }))
    }

    const sendPing = () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }))
      }
    }

    return { socket: ws, subscribe, sendPing }
  }, [])

  return {
    // Diagnostics
    runDiagnostics,
    getDiagnosticsHistory,
    // Introspection
    startIntrospectionSession,
    getIntrospectionSession,
    // Semantic Audits
    conductSemanticAudit,
    getSemanticAudit,
    // Governance
    createGovernanceProfile,
    listGovernanceProfiles,
    updateGovernanceProfile,
    // Reconciliation
    reconcileCognition,
    getCognitionConflicts,
    // Forecasts
    forecastCognitionDrift,
    getForecasts,
    // Reasoning
    recordReasoningStep,
    getReasoningLineage,
    // Anomalies
    registerAnomaly,
    getActiveAnomalies,
    resolveAnomaly,
    // Summary
    getMetaCognitionSummary,
    getMetaCognitionHealth,
    // WebSocket
    createMetaCognitionSocket,
  }
}
