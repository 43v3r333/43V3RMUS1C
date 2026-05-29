/**
 * 43V3R CORE - Executive Coordination API Client
 * Typed client for all executive coordination layer endpoints.
 * 
 * Implements:
 * - Recursive Cognition Supervision Engine
 * - Orchestration Arbitration System
 * - Hierarchical Stabilization Systems
 * - Executive Coordination Fabric
 * - Predictive Recursive Diagnostics
 */
'use client'

import { useCallback } from 'react'
import type {
  ExecutiveOverview,
  SupervisionSession,
  SupervisionFinding,
  SupervisionArtifact,
  ArbitrationState,
  ArbitrationPolicy,
  ConflictingClaim,
  StabilizationProfile,
  StabilizationEvent,
  CoordinationTopology,
  TopologyNode,
  TopologyEdge,
  CoordinationEdge,
  DiagnosticsForecast,
  ForecastIndicator,
  AnomalyDetection,
  HierarchyBalancing,
  ReconciliationMetrics,
  CoherenceLineage,
  SupervisionLevel,
  ArbitrationScope,
  StabilizationTier,
  StabilizationAction,
  DiagnosticsHorizon,
  BalanceStrategy,
  CoordinationTopology as CoordTopo,
  AnomalySeverity,
} from '@ui/types'

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

// ============================================================================
// Custom Hook
// ============================================================================

export function useExecutiveApi() {
  // ---- Overview -------------------------------------------------

  const getOverview = useCallback(async () => {
    return fetchApi<ExecutiveOverview>('/executive/overview')
  }, [])

  // ---- Recursive Supervision ------------------------------------

  const createSupervisionSession = useCallback(async (data: {
    supervisor_id: string
    scope: string
    target_id: string
    target_type: string
    supervision_level?: number
    parent_session_id?: string
    target_snapshot?: Record<string, unknown>
  }) => {
    return fetchApi<{ session_id: string; session_key: string; supervision_state: string; recursion_depth: number }>(
      '/executive/supervision/sessions',
      { method: 'POST', body: JSON.stringify(data) }
    )
  }, [])

  const listSupervisionSessions = useCallback(async (params: {
    scope?: string
    state?: string
    limit?: number
  } = {}) => {
    const qs = new URLSearchParams()
    if (params.scope) qs.set('scope', params.scope)
    if (params.state) qs.set('state', params.state)
    if (params.limit) qs.set('limit', String(params.limit))
    const query = qs.toString() ? `?${qs}` : ''
    return fetchApi<SupervisionSession[]>(`/executive/supervision/sessions${query}`)
  }, [])

  const getSupervisionSession = useCallback(async (sessionId: string) => {
    return fetchApi<SupervisionSession>(`/executive/supervision/sessions/${sessionId}`)
  }, [])

  const evaluateSupervisionSession = useCallback(async (data: {
    session_id: string
    metrics: Array<{
      category: string
      value: number
      threshold?: number
      severity?: string
      description?: string
      recommendation?: string
      confidence?: number
      is_violation?: boolean
    }>
  }) => {
    return fetchApi<{
      session_id: string
      state: string
      confidence_score: number
      findings: SupervisionFinding[]
      violations: unknown[]
      recommendations: string[]
      escalated: boolean
      escalated_to?: string
      duration_ms?: number
    }>(`/executive/supervision/sessions/${data.session_id}/evaluate`, {
      method: 'POST',
      body: JSON.stringify({ 
        session_id: data.session_id, 
        metrics: data.metrics.map(m => ({ ...m })) 
      }),
    })
  }, [])

  const createSupervisionArtifact = useCallback(async (data: {
    session_id: string
    artifact_type: string
    scope: string
    title: string
    content: Record<string, unknown>
    importance?: number
    summary?: string
  }) => {
    return fetchApi<{ artifact_id: string; artifact_key: string; artifact_type: string }>(
      '/executive/supervision/artifacts',
      { method: 'POST', body: JSON.stringify(data) }
    )
  }, [])

  // ---- Orchestration Arbitration -------------------------------

  const createArbitrationPolicy = useCallback(async (data: {
    policy_key: string
    name: string
    scope: string
    strategy?: string
    priority?: number
    max_rounds?: number
    timeout_ms?: number
    escalation_threshold?: number
  }) => {
    return fetchApi<{ policy_id: string; policy_key: string; name: string }>(
      '/executive/arbitration/policies',
      { method: 'POST', body: JSON.stringify(data) }
    )
  }, [])

  const createArbitration = useCallback(async (data: {
    scope: string
    conflict_type: string
    parties: string[]
    conflicting_claims: Array<{
      party: string
      priority?: number
      score?: number
      data?: Record<string, unknown>
    }>
    priority?: number
    description?: string
  }) => {
    return fetchApi<{ arbitration_id: string; arbitration_key: string; arbitration_state: string }>(
      '/executive/arbitration',
      { method: 'POST', body: JSON.stringify(data) }
    )
  }, [])

  const listArbitrations = useCallback(async (params: {
    scope?: string
    state?: string
    limit?: number
  } = {}) => {
    const qs = new URLSearchParams()
    if (params.scope) qs.set('scope', params.scope)
    if (params.state) qs.set('state', params.state)
    if (params.limit) qs.set('limit', String(params.limit))
    const query = qs.toString() ? `?${qs}` : ''
    return fetchApi<ArbitrationState[]>(`/executive/arbitration${query}`)
  }, [])

  const resolveArbitration = useCallback(async (data: {
    arbitration_id: string
    strategy?: string
  }) => {
    return fetchApi<{
      arbitration_id: string
      state: string
      confidence_score: number
      winning_party?: string
      resolution_strategy?: string
      negotiation_rounds: number
      escalation_required: boolean
      resolution_time_ms?: number
    }>(`/executive/arbitration/${data.arbitration_id}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ arbitration_id: data.arbitration_id, strategy: data.strategy }),
    })
  }, [])

  // ---- Stabilization Hierarchy ---------------------------------

  const createStabilizationProfile = useCallback(async (data: {
    name: string
    scope: string
    tier?: string
    thresholds?: Record<string, number>
    action_thresholds?: Record<string, unknown>
    parent_profile_id?: string
  }) => {
    return fetchApi<{ profile_id: string; profile_key: string; name: string; tier: string }>(
      '/executive/stabilization/profiles',
      { method: 'POST', body: JSON.stringify(data) }
    )
  }, [])

  const listStabilizationProfiles = useCallback(async (params: {
    scope?: string
    tier?: string
    limit?: number
  } = {}) => {
    const qs = new URLSearchParams()
    if (params.scope) qs.set('scope', params.scope)
    if (params.tier) qs.set('tier', params.tier)
    if (params.limit) qs.set('limit', String(params.limit))
    const query = qs.toString() ? `?${qs}` : ''
    return fetchApi<StabilizationProfile[]>(`/executive/stabilization/profiles${query}`)
  }, [])

  const executeStabilization = useCallback(async (data: {
    profile_id: string
    target_id: string
    target_type: string
    coherence_score_before: number
    action?: string
  }) => {
    return fetchApi<{
      event_id: string
      action: string
      tier_before: string
      tier_after: string
      success: boolean
      coherence_delta: number
      duration_ms?: number
    }>('/executive/stabilization/execute', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  // ---- Coordination Topology -----------------------------------

  const createTopology = useCallback(async (data: {
    name: string
    scope: string
    topology_type?: string
    nodes?: Array<{ node_id: string; node_type: string; capabilities?: string[]; metadata?: Record<string, unknown> }>
    coordinator_ids?: string[]
  }) => {
    return fetchApi<{
      topology_id: string
      topology_key: string
      name: string
      topology_type: string
      node_count: number
    }>('/executive/coordination/topology', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const listTopologies = useCallback(async (params: {
    scope?: string
    limit?: number
  } = {}) => {
    const qs = new URLSearchParams()
    if (params.scope) qs.set('scope', params.scope)
    if (params.limit) qs.set('limit', String(params.limit))
    const query = qs.toString() ? `?${qs}` : ''
    return fetchApi<CoordinationTopology[]>(`/executive/coordination/topology${query}`)
  }, [])

  const addTopologyEdge = useCallback(async (data: {
    topology_id: string
    source_id: string
    target_id: string
    edge_type?: string
    bandwidth?: number
  }) => {
    return fetchApi<{
      edge_id: string
      edge_key: string
      source_id: string
      target_id: string
    }>(`/executive/coordination/topology/${data.topology_id}/edges`, {
      method: 'POST',
      body: JSON.stringify({
        source_id: data.source_id,
        target_id: data.target_id,
        edge_type: data.edge_type || 'communication',
        bandwidth: data.bandwidth || 1.0,
      }),
    })
  }, [])

  const syncTopology = useCallback(async (data: {
    topology_id: string
    message_throughput?: number
    sync_latency_ms?: number
    conflict_rate?: number
  }) => {
    return fetchApi<{
      topology_id: string
      topology_state: string
      coherence_score: number
      conflict_rate: number
    }>(`/executive/coordination/topology/${data.topology_id}/sync`, {
      method: 'POST',
      body: JSON.stringify({
        topology_id: data.topology_id,
        message_throughput: data.message_throughput || 0,
        sync_latency_ms: data.sync_latency_ms || 0,
        conflict_rate: data.conflict_rate || 0,
      }),
    })
  }, [])

  // ---- Diagnostics -------------------------------------------

  const createForecast = useCallback(async (data: {
    target_id: string
    target_type: string
    scope: string
    forecast_kind: string
    horizon?: string
    indicators?: Array<{ value: number; weight?: number; confidence?: number; source?: string }>
    risk_factors?: string[]
  }) => {
    return fetchApi<{
      forecast_id: string
      forecast_key: string
      target_id: string
      forecast_kind: string
      horizon: string
      predicted_value: number
      confidence: number
      probability: number
      severity: string
      risk_level: string
    }>('/executive/diagnostics/forecasts', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const listForecasts = useCallback(async (params: {
    target_id?: string
    scope?: string
    horizon?: string
    not_validated?: boolean
    limit?: number
  } = {}) => {
    const qs = new URLSearchParams()
    if (params.target_id) qs.set('target_id', params.target_id)
    if (params.scope) qs.set('scope', params.scope)
    if (params.horizon) qs.set('horizon', params.horizon)
    if (params.not_validated !== undefined) qs.set('not_validated', String(params.not_validated))
    if (params.limit) qs.set('limit', String(params.limit))
    const query = qs.toString() ? `?${qs}` : ''
    return fetchApi<DiagnosticsForecast[]>(`/executive/diagnostics/forecasts${query}`)
  }, [])

  const createAnomalyDetection = useCallback(async (data: {
    target_id: string
    target_type: string
    scope: string
    anomaly_type: string
    baseline: Record<string, number>
    observed: Record<string, number>
    detection_method?: string
  }) => {
    return fetchApi<{
      anomaly_id: string
      anomaly_key: string
      target_id: string
      anomaly_type: string
      severity: string
      deviation: number
      status: string
      detected_at: string
    }>('/executive/diagnostics/anomalies', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const listAnomalies = useCallback(async (params: {
    scope?: string
    severity?: string
    limit?: number
  } = {}) => {
    const qs = new URLSearchParams()
    if (params.scope) qs.set('scope', params.scope)
    if (params.severity) qs.set('severity', params.severity)
    if (params.limit) qs.set('limit', String(params.limit))
    const query = qs.toString() ? `?${qs}` : ''
    return fetchApi<AnomalyDetection[]>(`/executive/diagnostics/anomalies${query}`)
  }, [])

  // ---- Balancing --------------------------------------------

  const calculateBalance = useCallback(async (data: {
    scope: string
    nodes: string[]
    weights?: Record<string, number>
  }) => {
    return fetchApi<{
      balancing_id: string
      balancing_key: string
      scope: string
      balance_strategy: string
      balance_score_before: number
      balance_score_after: number
    }>('/executive/balancing/calculate', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  // ---- Reconciliation ----------------------------------------

  const recordReconciliationMetrics = useCallback(async (data: {
    scope: string
    policy_alignment_score?: number
    semantic_alignment_score?: number
    execution_alignment_score?: number
    conflicts_detected?: number
    policies_evaluated?: number
    policies_violated?: number
  }) => {
    return fetchApi<{
      metrics_id: string
      metrics_key: string
      scope: string
      reconciliation_state: string
      policy_alignment_score: number
    }>('/executive/reconciliation/metrics', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const getReconciliationMetrics = useCallback(async (params: {
    scope?: string
    limit?: number
  } = {}) => {
    const qs = new URLSearchParams()
    if (params.scope) qs.set('scope', params.scope)
    if (params.limit) qs.set('limit', String(params.limit))
    const query = qs.toString() ? `?${qs}` : ''
    return fetchApi<ReconciliationMetrics[]>(`/executive/reconciliation/metrics${query}`)
  }, [])

  // ---- Coherence Lineage -------------------------------------

  const recordCoherenceLineage = useCallback(async (data: {
    scope: string
    source_id: string
    source_type: string
    coherence_metric: string
    coherence_value: number
    event_type: string
    event_description?: string
    event_data?: Record<string, unknown>
    parent_lineage_id?: string
  }) => {
    return fetchApi<{
      lineage_id: string
      lineage_key: string
      coherence_metric: string
      coherence_value: number
      coherence_trend: string
      chain_id: string
      chain_position: number
    }>('/executive/coherence/lineage', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const getCoherenceLineage = useCallback(async (params: {
    chain_id?: string
    source_id?: string
    limit?: number
  } = {}) => {
    const qs = new URLSearchParams()
    if (params.chain_id) qs.set('chain_id', params.chain_id)
    if (params.source_id) qs.set('source_id', params.source_id)
    if (params.limit) qs.set('limit', String(params.limit))
    const query = qs.toString() ? `?${qs}` : ''
    return fetchApi<CoherenceLineage[]>(`/executive/coherence/lineage${query}`)
  }, [])

  // ---- Status -------------------------------------------------

  const getStatus = useCallback(async () => {
    return fetchApi<{
      service: string
      status: string
      capabilities: string[]
      timestamp: string
    }>('/executive/status')
  }, [])

  // ---- WebSocket ----------------------------------------------

  const createExecutiveSocket = useCallback(() => {
    if (typeof window === 'undefined') return null
    const token = localStorage.getItem('access_token') || ''
    const wsUrl = (process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000').replace('http', 'ws') + '/ws/executive'
    const ws = new WebSocket(`${wsUrl}${token ? `?token=${token}` : ''}`)

    const subscribe = (channels: string[]) => {
      ws.send(JSON.stringify({ action: 'subscribe', channels }))
    }
    const unsubscribe = (channels: string[]) => {
      ws.send(JSON.stringify({ action: 'unsubscribe', channels }))
    }

    return { socket: ws, subscribe, unsubscribe }
  }, [])

  // ---- Return API Interface -----------------------------------

  return {
    // Overview
    getOverview,
    // Supervision
    createSupervisionSession,
    listSupervisionSessions,
    getSupervisionSession,
    evaluateSupervisionSession,
    createSupervisionArtifact,
    // Arbitration
    createArbitrationPolicy,
    createArbitration,
    listArbitrations,
    resolveArbitration,
    // Stabilization
    createStabilizationProfile,
    listStabilizationProfiles,
    executeStabilization,
    // Topology
    createTopology,
    listTopologies,
    addTopologyEdge,
    syncTopology,
    // Diagnostics
    createForecast,
    listForecasts,
    createAnomalyDetection,
    listAnomalies,
    // Balancing
    calculateBalance,
    // Reconciliation
    recordReconciliationMetrics,
    getReconciliationMetrics,
    // Lineage
    recordCoherenceLineage,
    getCoherenceLineage,
    // Status
    getStatus,
    // WebSocket
    createExecutiveSocket,
  }
}

// ============================================================================
// Re-export types for convenience
// ============================================================================

export type {
  ExecutiveOverview,
  SupervisionSession,
  SupervisionFinding,
  SupervisionArtifact,
  ArbitrationState,
  ArbitrationPolicy,
  ConflictingClaim,
  StabilizationProfile,
  StabilizationEvent,
  CoordinationTopology,
  TopologyNode,
  TopologyEdge,
  CoordinationEdge,
  DiagnosticsForecast,
  ForecastIndicator,
  AnomalyDetection,
  HierarchyBalancing,
  ReconciliationMetrics,
  CoherenceLineage,
}
