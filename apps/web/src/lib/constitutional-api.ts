/**
 * 43V3R CORE - Constitutional Governance API Client
 * Typed client for constitutional governance, invariant enforcement, and safety systems.
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

// ---- Constitutional Profiles ----

export interface ConstitutionalProfile {
  profile_id: string
  profile_scope: string
  profile_key: string
  governance_scope: string
  max_violations_per_cycle: number
  total_violations: number
  critical_violations: number
  remediations: number
  is_active: boolean
}

export interface ConstitutionalDecision {
  approved: boolean
  action: string
  reason: string
  severity: string
  violations: string[]
  safety_state: string
}

// ---- Invariant Policies ----

export interface InvariantPolicy {
  policy_id: string
  policy_scope: string
  invariant_type: string
  invariant_name: string
  severity: string
  is_active: boolean
}

export interface InvariantValidation {
  is_valid: boolean
  constraint_id?: string
  violations: Array<{ type: string; key: string; message: string }>
  confidence: number
}

// ---- Cognition Boundaries ----

export interface CognitionBoundary {
  boundary_id: string
  boundary_scope: string
  boundary_type: string
  soft_limit: number
  hard_limit: number
  breach_count: number
  is_active: boolean
}

export interface BoundaryValidation {
  within_bounds: boolean
  limit_type: 'within_bounds' | 'soft' | 'hard' | 'critical'
  distance_from_limit: number
  violations: string[]
}

// ---- Safety Assessment ----

export interface SafetyAssessment {
  safety_state: 'nominal' | 'caution' | 'warning' | 'critical' | 'collapse'
  risk_score: number
  collapse_probability: number
  contributing_factors: string[]
  recommendations: string[]
  interventions_needed: boolean
}

// ---- Recursive Safety ----

export interface SafetyProfile {
  profile_id: string
  profile_scope: string
  protection_level: string
  collapse_threshold: number
  max_recursion_depth: number
  protection_count: number
  collapse_preventions: number
  is_active: boolean
}

export interface StabilitySession {
  session_id: string
  session_scope: string
  session_state: string
  safety_state: string
  stability_score: number
  started_at: string
}

export interface GovernanceConflict {
  conflict_id: string
  conflict_type: string
  conflicting_rules: string[]
  conflict_state: string
  resolution_strategy?: string
  occurred_at: string
}

// ---- Arbitration ----

export interface ArbitrationSession {
  session_id: string
  session_scope: string
  strategy: string
  recursion_depth: number
  session_state: string
  coherence_impact: number
  started_at: string
}

export interface ArbitrationDecision {
  decision_type: string
  selected_policy?: string
  rejected_policies: string[]
  coherence_impact: number
  success: boolean
}

export interface ReconciliationPolicy {
  policy_id: string
  policy_scope: string
  policy_type: string
  default_strategy: string
  reconciliation_count: number
  is_active: boolean
}

// ---- Ecosystem ----

export interface EcosystemCoherence {
  is_coherent: boolean
  coherence_score: number
  stability_score: number
  balance_score: number
  violations: string[]
}

export interface EcosystemSnapshot {
  snapshot_id: string
  coherence_score: number
  stability_score: number
  balance_score: number
  violations_detected: number
  captured_at: string
}

// ---- Audit ----

export interface ConstitutionalAudit {
  audit_id: string
  action_type: string
  success: boolean
  logged_at: string
  violation_detected: boolean
}

// =====================================================================
// Custom Hook
// =====================================================================

export function useConstitutionalApi() {
  // ---- Constitutional Profiles ----

  const createProfile = useCallback(async (data: {
    profile_scope: string
    profile_key: string
    governance_scope?: string
    max_violations?: number
    severity_cap?: string
  }) => {
    return fetchApi<{ profile_id: string; status: string }>('/constitutional/profiles', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const getProfile = useCallback(async (profileId: string) => {
    return fetchApi<ConstitutionalProfile>(`/constitutional/profiles/${profileId}`)
  }, [])

  const evaluateAction = useCallback(async (data: {
    scope: string
    action: Record<string, unknown>
    current_state: Record<string, unknown>
    profile_id?: string
  }) => {
    return fetchApi<ConstitutionalDecision>('/constitutional/evaluate', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  // ---- Invariant Policies ----

  const createInvariantPolicy = useCallback(async (data: {
    policy_scope: string
    invariant_type: string
    invariant_name: string
    invariant_expression: string
    constraint_type?: string
    severity?: string
  }) => {
    return fetchApi<{ policy_id: string; status: string }>('/constitutional/invariant-policies', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const validateInvariant = useCallback(async (data: {
    scope: string
    state: Record<string, unknown>
    policy_id?: string
  }) => {
    return fetchApi<InvariantValidation>('/constitutional/validate-invariant', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  // ---- Cognition Boundaries ----

  const createBoundary = useCallback(async (data: {
    boundary_scope: string
    boundary_type: string
    boundary_key: string
    boundary_limits: Record<string, number>
    soft_limit?: number
    hard_limit?: number
  }) => {
    return fetchApi<{ boundary_id: string; status: string }>('/constitutional/cognition-boundaries', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const validateBoundary = useCallback(async (data: {
    boundary_id: string
    current_value: number
  }) => {
    return fetchApi<BoundaryValidation>(`/constitutional/validate-boundary/${data.boundary_id}`, {
      method: 'POST',
      body: JSON.stringify({ current_value: data.current_value }),
    })
  }, [])

  // ---- Safety Assessment ----

  const assessSafety = useCallback(async (data: {
    scope: string
    recursion_depth: number
    current_metrics: Record<string, number>
  }) => {
    return fetchApi<SafetyAssessment>('/constitutional/safety-assessment', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const preventCollapse = useCallback(async (data: {
    scope: string
    current_state: Record<string, unknown>
  }) => {
    return fetchApi<{ prevented: boolean; actions_taken: string[] }>('/constitutional/prevent-collapse', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  // ---- Systemic Constraints ----

  const createConstraint = useCallback(async (data: {
    constraint_scope: string
    constraint_type: string
    constraint_key: string
    constraint_definition: Record<string, unknown>
    components: string[]
    severity?: string
  }) => {
    return fetchApi<{ constraint_id: string; status: string }>('/constitutional/systemic-constraints', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  // ---- Audit ----

  const getAuditTrail = useCallback(async (params?: {
    session_id?: string
    action_type?: string
    constraint_id?: string
    limit?: number
  }) => {
    const qs = new URLSearchParams()
    if (params?.session_id) qs.set('session_id', params.session_id)
    if (params?.action_type) qs.set('action_type', params.action_type)
    if (params?.constraint_id) qs.set('constraint_id', params.constraint_id)
    if (params?.limit) qs.set('limit', String(params.limit))
    const query = qs.toString() ? `?${qs}` : ''
    return fetchApi<{ audits: ConstitutionalAudit[]; count: number }>(`/constitutional/audit-trail${query}`)
  }, [])

  // ---- Invariant Runtime ----

  const registerInvariant = useCallback(async (data: {
    invariant_scope: string
    invariant_type: string
    invariant_name: string
    expression: string
  }) => {
    return fetchApi<{ invariant_id: string; status: string }>('/constitutional/invariants', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const validateInvariantRuntime = useCallback(async (data: {
    invariant_id: string
    state: Record<string, unknown>
  }) => {
    return fetchApi<{
      is_valid: boolean
      violations: Array<{ type: string; message: string }>
      confidence: number
    }>(`/constitutional/invariants/${data.invariant_id}/validate`, {
      method: 'POST',
      body: JSON.stringify({ state: data.state }),
    })
  }, [])

  const assessConsistency = useCallback(async (data: {
    session_id: string
    lineage_id: string
    component_states: Record<string, unknown>
    invariants: string[]
  }) => {
    return fetchApi<{
      is_consistent: boolean
      consistency_score: number
      violations: string[]
      recommendations: string[]
    }>('/constitutional/consistency-assessment', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  // ---- Recursive Safety ----

  const createSafetyProfile = useCallback(async (data: {
    profile_scope: string
    profile_key: string
    protection_level?: string
  }) => {
    return fetchApi<{ profile_id: string; status: string }>('/constitutional/safety-profiles', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const assessSafetyState = useCallback(async (data: {
    scope: string
    recursion_depth: number
    current_metrics: Record<string, number>
  }) => {
    return fetchApi<SafetyAssessment>('/constitutional/safety-assessment', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const createStabilitySession = useCallback(async (data: {
    session_scope: string
    scope_kind: string
  }) => {
    return fetchApi<{ session_id: string; started_at: string }>('/constitutional/stability-sessions', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const detectConflict = useCallback(async (data: {
    session_id: string
    lineage_id: string
    conflict_type: string
    conflicting_rules: string[]
    rule_priorities?: Record<string, number>
  }) => {
    return fetchApi<{ conflict_id: string; status: string }>('/constitutional/governance-conflicts', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  // ---- Arbitration ----

  const createArbitrationSession = useCallback(async (data: {
    session_scope: string
    scope_kind: string
    strategy?: string
    max_depth?: number
  }) => {
    return fetchApi<{ session_id: string; started_at: string }>('/constitutional/arbitration-sessions', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const arbitrate = useCallback(async (data: {
    session_id: string
    conflicting_policies: string[]
    policy_scores: Record<string, number>
  }) => {
    return fetchApi<ArbitrationDecision>(
      `/constitutional/arbitration-sessions/${data.session_id}/arbitrate`,
      { method: 'POST', body: JSON.stringify(data) }
    )
  }, [])

  const assessEcosystemCoherence = useCallback(async (data: {
    component_states: Record<string, string>
    policy_states: Record<string, boolean>
  }) => {
    return fetchApi<EcosystemCoherence>('/constitutional/ecosystem-coherence', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const createReconciliationPolicy = useCallback(async (data: {
    policy_scope: string
    policy_type: string
    policy_key: string
    default_strategy?: string
  }) => {
    return fetchApi<{ policy_id: string; status: string }>('/constitutional/reconciliation-policies', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  return {
    // Profiles
    createProfile,
    getProfile,
    evaluateAction,
    // Invariant Policies
    createInvariantPolicy,
    validateInvariant,
    // Boundaries
    createBoundary,
    validateBoundary,
    // Safety
    assessSafety,
    preventCollapse,
    // Constraints
    createConstraint,
    // Audit
    getAuditTrail,
    // Invariant Runtime
    registerInvariant,
    validateInvariantRuntime,
    assessConsistency,
    // Recursive Safety
    createSafetyProfile,
    assessSafetyState,
    createStabilitySession,
    detectConflict,
    // Arbitration
    createArbitrationSession,
    arbitrate,
    assessEcosystemCoherence,
    createReconciliationPolicy,
  }
}

export type UseConstitutionalApi = ReturnType<typeof useConstitutionalApi>
