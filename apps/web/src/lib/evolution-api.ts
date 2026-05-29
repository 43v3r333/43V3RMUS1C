/**
 * 43V3R CORE - Evolution API Client
 * Typed client for evolution governance, mutation tracking, and adaptive arbitration.
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

// ---- Evolution Profiles ----

export interface EvolutionProfile {
  profile_id: string
  profile_scope: string
  profile_key: string
  governance_level: string
  adaptation_strategy: string
  coherence_target: number
  coherence_threshold: number
  evolution_stage: string
  cycle_count: number
  total_mutations: number
  successful_adaptations: number
  failed_adaptations: number
  is_active: boolean
}

export interface EvolutionDecision {
  approved: boolean
  action: string
  reason: string
  severity: string
  governance_level: string
  warnings: string[]
  mutations_suggested: Array<{
    type: string
    mutation_id: string
    from: string
    to: string
    reason: string
  }>
}

// ---- Mutation Tracking ----

export interface OrchestrationMutation {
  mutation_id: string
  lineage_id: string
  subject_kind: string
  subject_key: string
  mutation_type: string
  mutation_category: string
  severity: string
  status: string
  impact_score: number
  risk_score: number
  lineage_depth: number
  is_reverted: boolean
  proposed_at: string
  applied_at?: string
  completed_at?: string
}

export interface MutationChain {
  mutations: OrchestrationMutation[]
  count: number
}

export interface MutationLineageGraph {
  graph_id: string
  lineage_id: string
  node_count: number
  edge_count: number
  max_depth: number
  graph_diameter: number
  branching_factor: number
  coherence_score: number
}

// ---- Cognition Evolution ----

export interface CognitionTrace {
  trace_id: string
  lineage_id: string
  reasoning_type: string
  domain: string
  adaptation_phase: string
  adaptation_trigger?: string
  coherence_before: number
  coherence_after: number
  coherence_delta: number
  insight_gain: number
  reasoning_efficiency: number
  trajectory: string
  traced_at: string
}

export interface EvolutionTrend {
  trend: 'improving' | 'declining' | 'stable' | 'unknown' | 'insufficient_data'
  stability: number
  count: number
  avg_coherence?: number
}

// ---- Recursive Sessions ----

export interface RecursiveEvolutionSession {
  session_id: string
  session_scope: string
  recursion_depth: number
  max_recursion_depth: number
  governance_level: string
  strategy: string
  session_state: string
  coherence_score: number
  adaptation_efficiency: number
  cycle_count: number
  mutations_applied: number
  mutations_successful: number
  started_at: string
  completed_at?: string
  duration_seconds?: number
}

// ---- Coherence ----

export interface CoherenceSnapshot {
  snapshot_id: string
  session_id?: string
  coherence_score: number
  drift_score: number
  coherence_state: string
  orchestration_health: number
  cognition_alignment: number
  semantic_stability: number
  distributed_sync: number
  component_states: Record<string, string>
  captured_at: string
}

export interface CoherenceAssessment {
  is_coherent: boolean
  coherence_score: number
  coherence_state: 'aligned' | 'drifting' | 'fragmented' | 'recovering' | 'collapsed'
  drift_sources: Array<{ snapshot: string; drift: number }>
  recommendations: string[]
}

// ---- Adaptation Arbitration ----

export interface ArbitrationSession {
  session_id: string
  arbitration_scope: string
  scope_kind: string
  balance_strategy: string
  recursion_depth: number
  session_state: string
  current_phase: string
  balance_score: number
  started_at: string
  completed_at?: string
}

export interface ArbitrationResult {
  decision: string
  selected_adaptations: string[]
  rejected_adaptations: string[]
  coherence_impact: number
  confidence: number
}

export interface BalanceSnapshot {
  balance_id: string
  session_id: string
  balance_scope: string
  imbalance_score: number
  component_states: Record<string, number>
  strategy_used: string
  captured_at: string
}

export interface BalanceAssessment {
  is_balanced: boolean
  imbalance_score: number
  deviation_sources: Array<{
    component: string
    deviation: number
    state: number
  }>
  redistribution_plan: Array<{
    from: string
    to: string
    amount: number
    rationale: string
  }>
  tolerance_met: boolean
}

// ---- Semantic Reconciliation ----

export interface SemanticReconciliation {
  reconciliation_id: string
  session_id: string
  subject_kind: string
  subject_key: string
  reconciliation_type: string
  reconciliation_state: 'pending' | 'in_progress' | 'reconciled' | 'failed' | 'deadlocked'
  convergence_achieved: boolean
  conflicts_resolved: number
  reconciled_at?: string
}

export interface OrchestrationAdaptation {
  adaptation_id: string
  session_id: string
  subject_kind: string
  subject_key: string
  adaptation_type: string
  impact_score: number
  risk_score: number
  coherence_impact: number
  governance_level: string
  approval_required: boolean
  approved_by?: string
  adaptation_state: string
  adapted_at: string
}

// ---- Stabilization ----

export interface SystemicStabilization {
  stabilization_id: string
  session_id: string
  stabilization_scope: string
  iteration: number
  max_iterations: number
  coherence_before: number
  coherence_after: number
  stability_delta: number
  stabilization_state: string
  stabilization_complete: boolean
  convergence_score: number
  started_at: string
  completed_at?: string
  duration_seconds?: number
}

// ---- Mutation Policy ----

export interface MutationPolicy {
  policy_id: string
  policy_domain: string
  policy_key: string
  allowed_mutations: string[]
  min_severity_threshold: string
  max_severity_threshold: string
  requires_approval: boolean
  is_active: boolean
}

export interface MutationEvaluation {
  mutation_id: string
  approved: boolean
  severity: string
  risk_score: number
  warnings: string[]
}

// ---- Semantic Continuity ----

export interface SemanticContinuityAssessment {
  is_coherent: boolean
  coherence_score: number
  coherence_state: string
  contract_violations: string[]
  recommendations: string[]
}

// =====================================================================
// Custom Hook
// =====================================================================

export function useEvolutionApi() {
  // ---- Evolution Profiles ----

  const createProfile = useCallback(async (data: {
    profile_scope: string
    profile_key: string
    governance_level?: string
    adaptation_strategy?: string
    coherence_target?: number
    mutation_severity_cap?: string
  }) => {
    return fetchApi<{ profile_id: string; status: string }>('/evolution/profiles', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const getProfile = useCallback(async (profileId: string) => {
    return fetchApi<EvolutionProfile>(`/evolution/profiles/${profileId}`)
  }, [])

  const evaluateEvolution = useCallback(async (data: {
    scope: string
    mutations: Array<Record<string, unknown>>
    coherence_snapshot?: Record<string, unknown>
  }) => {
    return fetchApi<EvolutionDecision>('/evolution/evaluate', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  // ---- Mutation Policies ----

  const createMutationPolicy = useCallback(async (data: {
    policy_domain: string
    policy_key: string
    allowed_mutations: string[]
    min_severity?: string
    max_severity?: string
    requires_approval?: boolean
  }) => {
    return fetchApi<{ policy_id: string; status: string }>('/evolution/mutation-policies', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const evaluateMutation = useCallback(async (data: {
    mutation: Record<string, unknown>
    domain: string
    kind?: string
  }) => {
    return fetchApi<MutationEvaluation>('/evolution/mutation-policies/evaluate', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  // ---- Cognition Adaptation ----

  const evaluateCognitionAdaptation = useCallback(async (data: {
    reasoning_type: string
    domain: string
    current_state: Record<string, unknown>
    target_state: Record<string, unknown>
  }) => {
    return fetchApi<{
      adaptation_id: string
      approved: boolean
      rollback_required: boolean
      coherence_impact: number
    }>('/evolution/cognition-adaptation/evaluate', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  // ---- Semantic Continuity ----

  const validateSemanticContinuity = useCallback(async (data: {
    scope: string
    state: Record<string, unknown>
    contracts?: string[]
  }) => {
    return fetchApi<SemanticContinuityAssessment>('/evolution/semantic-continuity/validate', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  // ---- Recursive Sessions ----

  const createRecursiveSession = useCallback(async (data: {
    session_scope: string
    governance_level?: string
    strategy?: string
    max_depth?: number
    parent_session_id?: string
  }) => {
    return fetchApi<{
      session_id: string
      recursion_depth: number
      session_state: string
    }>('/evolution/recursive-sessions', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const advanceRecursiveSession = useCallback(async (data: {
    session_id: string
    mutations: Array<Record<string, unknown>>
    metrics?: Record<string, number>
  }) => {
    return fetchApi<{
      session_id: string
      cycle_count: number
      mutations_applied: number
      coherence_score: number
    }>(`/evolution/recursive-sessions/${data.session_id}/advance`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const completeRecursiveSession = useCallback(async (data: {
    session_id: string
    final_metrics?: Record<string, number>
  }) => {
    return fetchApi<{
      session_id: string
      session_state: string
      duration_seconds: number
      mutations_successful: number
    }>(`/evolution/recursive-sessions/${data.session_id}/complete`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  // ---- Coherence ----

  const captureCoherenceSnapshot = useCallback(async (data: {
    snapshot_key: string
    coherence_metrics: Record<string, number>
    component_states: Record<string, string>
    session_id?: string
  }) => {
    return fetchApi<{ snapshot_id: string; coherence_score: number }>('/evolution/coherence-snapshots', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const assessSystemicCoherence = useCallback(async (params?: {
    scope?: string
    window_seconds?: number
  }) => {
    const qs = new URLSearchParams()
    if (params?.scope) qs.set('scope', params.scope)
    if (params?.window_seconds) qs.set('window_seconds', String(params.window_seconds))
    const query = qs.toString() ? `?${qs}` : ''
    return fetchApi<CoherenceAssessment>(`/evolution/coherence-assessment${query}`)
  }, [])

  // ---- Mutation Tracking ----

  const recordMutation = useCallback(async (data: {
    lineage_id: string
    subject_kind: string
    subject_key: string
    mutation_type: string
    pre_state: Record<string, unknown>
    post_state: Record<string, unknown>
    severity?: string
    parent_mutation_id?: string
  }) => {
    return fetchApi<{ mutation_id: string; status: string }>('/evolution/mutations', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const getMutation = useCallback(async (mutationId: string) => {
    return fetchApi<OrchestrationMutation>(`/evolution/mutations/${mutationId}`)
  }, [])

  const getLineage = useCallback(async (lineageId: string, includeReverted?: boolean) => {
    const qs = includeReverted ? '?include_reverted=true' : ''
    return fetchApi<MutationChain>(`/evolution/lineages/${lineageId}${qs}`)
  }, [])

  const updateMutationStatus = useCallback(async (data: {
    mutation_id: string
    status: string
  }) => {
    return fetchApi<{ mutation_id: string; status: string }>(
      `/evolution/mutations/${data.mutation_id}/update-status`,
      { method: 'POST', body: JSON.stringify(data) }
    )
  }, [])

  const revertMutation = useCallback(async (mutationId: string) => {
    return fetchApi<{ mutation_id: string; is_reverted: boolean }>(
      `/evolution/mutations/${mutationId}/revert`,
      { method: 'POST' }
    )
  }, [])

  const recordCognitionTrace = useCallback(async (data: {
    lineage_id: string
    reasoning_type: string
    domain: string
    cognition_state: Record<string, unknown>
    reasoning_context: Record<string, unknown>
    coherence_before?: number
    coherence_after?: number
    phase?: string
    session_id?: string
  }) => {
    return fetchApi<{ trace_id: string; trajectory: string }>('/evolution/cognition-traces', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const getCognitionTrend = useCallback(async (sessionId: string, windowMinutes?: number) => {
    const qs = windowMinutes ? `?window_minutes=${windowMinutes}` : ''
    return fetchApi<EvolutionTrend>(`/evolution/cognition-traces/session/${sessionId}/trend${qs}`)
  }, [])

  const buildLineageGraph = useCallback(async (data: {
    lineage_id: string
    subject_kind: string
    subject_key: string
  }) => {
    return fetchApi<MutationLineageGraph>('/evolution/lineage-graphs', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  // ---- Adaptation Arbitration ----

  const createArbitrationSession = useCallback(async (data: {
    scope_kind: string
    scope_id?: string
    strategy?: string
    max_depth?: number
    parent_session_id?: string
  }) => {
    return fetchApi<{
      session_id: string
      recursion_depth: number
      balance_strategy: string
    }>('/evolution/arbitration-sessions', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const arbitrate = useCallback(async (data: {
    session_id: string
    conflicting_adaptations: string[]
    session_state: Record<string, unknown>
  }) => {
    return fetchApi<ArbitrationResult>(
      `/evolution/arbitration-sessions/${data.session_id}/arbitrate`,
      { method: 'POST', body: JSON.stringify(data) }
    )
  }, [])

  const captureBalanceSnapshot = useCallback(async (data: {
    session_id: string
    lineage_id: string
    balance_scope: string
    component_states: Record<string, number>
    strategy?: string
    target_balance?: Record<string, number>
  }) => {
    return fetchApi<{ balance_id: string; imbalance_score: number }>('/evolution/balance-snapshots', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const assessBalance = useCallback(async (sessionId: string) => {
    return fetchApi<BalanceAssessment>(`/evolution/balance-assessment/${sessionId}`)
  }, [])

  const reconcileSemantic = useCallback(async (data: {
    session_id: string
    lineage_id: string
    subject_kind: string
    subject_key: string
    pre_state: Record<string, unknown>
    post_state: Record<string, unknown>
    reconciliation_type?: string
  }) => {
    return fetchApi<SemanticReconciliation>('/evolution/semantic-reconciliation', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const createOrchestrationAdaptation = useCallback(async (data: {
    session_id: string
    lineage_id: string
    subject_kind: string
    subject_key: string
    adaptation_type: string
    pre_state: Record<string, unknown>
    post_state: Record<string, unknown>
    governance_level?: string
    requires_approval?: boolean
  }) => {
    return fetchApi<{
      adaptation_id: string
      impact_score: number
      approval_required: boolean
    }>('/evolution/orchestration-adaptations', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  // ---- Stabilization ----

  const beginStabilization = useCallback(async (data: {
    session_scope: string
    lineage_id: string
    stabilization_scope: string
    affected_components: string[]
    pre_state: Record<string, unknown>
  }) => {
    return fetchApi<{ stabilization_id: string; iteration: number }>('/evolution/stabilization', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const applyIntervention = useCallback(async (data: {
    stabilization_id: string
    intervention: Record<string, unknown>
  }) => {
    return fetchApi<{
      stabilization_id: string
      iteration: number
      convergence_score: number
      stabilization_complete: boolean
    }>(`/evolution/stabilization/${data.stabilization_id}/intervention`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const completeStabilization = useCallback(async (data: {
    stabilization_id: string
    post_state: Record<string, unknown>
    success?: boolean
  }) => {
    return fetchApi<{
      stabilization_id: string
      stabilization_state: string
      duration_seconds: number
    }>(`/evolution/stabilization/${data.stabilization_id}/complete`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  return {
    // Profiles
    createProfile,
    getProfile,
    evaluateEvolution,
    // Mutation Policies
    createMutationPolicy,
    evaluateMutation,
    // Cognition Adaptation
    evaluateCognitionAdaptation,
    // Semantic Continuity
    validateSemanticContinuity,
    // Recursive Sessions
    createRecursiveSession,
    advanceRecursiveSession,
    completeRecursiveSession,
    // Coherence
    captureCoherenceSnapshot,
    assessSystemicCoherence,
    // Mutation Tracking
    recordMutation,
    getMutation,
    getLineage,
    updateMutationStatus,
    revertMutation,
    recordCognitionTrace,
    getCognitionTrend,
    buildLineageGraph,
    // Adaptation Arbitration
    createArbitrationSession,
    arbitrate,
    captureBalanceSnapshot,
    assessBalance,
    reconcileSemantic,
    createOrchestrationAdaptation,
    // Stabilization
    beginStabilization,
    applyIntervention,
    completeStabilization,
  }
}

export type UseEvolutionApi = ReturnType<typeof useEvolutionApi>
