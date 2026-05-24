/**
 * 43V3R CORE - Cognitive API Client
 * Typed client for all cognitive operating core endpoints.
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

export interface KnowledgeNode {
  id: string
  node_kind: string
  node_key: string
  label: string
  summary?: string
  properties: Record<string, unknown>
  tags: string[]
  relevance_score: number
  centrality: number
  lifecycle_state: string
  last_seen_at: string
  seen_count: number
  source_domain?: string
  correlation_id?: string
  created_at: string
  updated_at: string
}

export interface DependencyEdge {
  id: string
  source_node_id: string
  target_node_id: string
  edge_kind: string
  label?: string
  weight: number
  confidence: number
  evidence_count: number
  lifecycle_state: string
  created_at: string
}

export interface GraphNeighborhood {
  root: KnowledgeNode
  nodes: KnowledgeNode[]
  edges: DependencyEdge[]
  depth: number
}

export interface SemanticRelationship {
  id: string
  subject_kind: string
  subject_key: string
  predicate: string
  object_kind: string
  object_key: string
  confidence: number
  weight: number
  is_active: boolean
  created_at: string
}

export interface OrchestrationMemory {
  id: string
  scope: string
  memory_kind: string
  subject: string
  title: string
  content: Record<string, unknown>
  importance: number
  recency: number
  confidence: number
  access_count: number
  last_accessed_at?: string
  correlation_id?: string
  workflow_id?: string
  agent_id?: string
  is_pinned: boolean
  created_at: string
}

export interface ExecutionForecast {
  id: string
  subject_kind: string
  subject_key: string
  forecast_kind: string
  horizon: string
  predicted_value: number
  lower_bound?: number
  upper_bound?: number
  confidence: number
  predicted_for: string
  generated_at: string
  actual_value?: number
  realized_at?: string
  error_pct?: number
  lifecycle_state: string
}

export interface MultiStageGraph {
  id: string
  subject_kind: string
  subject_key: string
  plan_label: string
  stages: Record<string, unknown>[]
  edges: Record<string, unknown>[]
  stage_count: number
  parallelism_factor: number
  estimated_duration: number
  estimated_cost: number
  risk_score: number
  selected_strategy?: string
  lifecycle_state: string
  created_at: string
}

export interface StrategyDecision {
  strategy: string
  rationale: string
  expected_improvement: number
  confidence: number
  scores: Record<string, number>
}

export interface CreativeProfile {
  id: string
  name: string
  campaign_id?: string
  artist_id?: string
  narrative_structure: string
  emotional_arc: string
  pacing_profile: string
  visual_keywords: string[]
  audio_keywords: string[]
  color_palette: string[]
  target_segments: string[]
  attention_span_seconds: number
  completion_rate_target: number
  engagement_rate_target: number
  is_active: boolean
  version: number
  created_at: string
}

export interface NarrativeSequence {
  id: string
  name: string
  profile_id?: string
  campaign_id?: string
  structure: string
  emotional_arc: string
  beats: Record<string, unknown>[]
  beat_count: number
  target_duration: number
  target_bpm?: number
  target_key?: string
  creative_score: number
  confidence: number
  is_locked: boolean
  version: number
  created_at: string
}

export interface GovernanceRule {
  id: string
  name: string
  rule_type: string
  conditions: Record<string, unknown>
  action: string
  agent_kind?: string
  priority: number
  is_active: boolean
  trigger_count: number
  success_count: number
  failure_count: number
  version: number
  created_at: string
}

export interface GovernanceDecision {
  action: string
  reason: string
  triggered_rules: string[]
  escalation_agent?: string
  confidence: number
}

export interface ConflictResolution {
  id: string
  conflict_id: string
  domain: string
  agent_ids: string[]
  authority_levels: number[]
  conflict_type: string
  strategy_used: string
  resolution_outcome: string
  winning_agent_id?: string
  resolution_state: string
  escalation_required: boolean
  human_review: boolean
  detected_at: string
  resolved_at?: string
}

export interface OrchestrationFeedback {
  id: string
  subject_kind: string
  subject_key: string
  feedback_type: string
  actual_value?: number
  expected_value?: number
  delta_pct?: number
  quality_score?: number
  error_rate?: number
  workflow_id?: string
  agent_id?: string
  observed_at: string
}

export interface TuningCycle {
  id: string
  cycle_id: string
  context_key: string
  target_metric: string
  target_improvement: number
  max_iterations: number
  iteration: number
  cycle_state: string
  best_score?: number
  started_at: string
  completed_at?: string
}

export interface TuningRecommendation {
  parameter_name: string
  current_value: number
  recommended_value: number
  action: string
  reason: string
  expected_improvement: number
  confidence: number
}

// =====================================================================
// Hook
// =====================================================================

export function useCognitiveApi() {
  // ---- Knowledge Graph -----------------------------------------------

  const getGraphSummary = useCallback(async () => {
    return fetchApi<{ nodes: number; edges: number; relationships: number; by_kind: Record<string, number> }>('/cognitive/graph/summary')
  }, [])

  const upsertNode = useCallback(async (data: Partial<KnowledgeNode>) => {
    return fetchApi<KnowledgeNode>('/cognitive/graph/nodes', { method: 'POST', body: JSON.stringify(data) })
  }, [])

  const listNodes = useCallback(async (params: { kind?: string; limit?: number; offset?: number } = {}) => {
    const qs = new URLSearchParams()
    if (params.kind) qs.set('kind', params.kind)
    if (params.limit) qs.set('limit', String(params.limit))
    if (params.offset) qs.set('offset', String(params.offset))
    return fetchApi<KnowledgeNode[]>(`/cognitive/graph/nodes?${qs}`)
  }, [])

  const getNeighborhood = useCallback(async (kind: string, key: string, depth = 2) => {
    return fetchApi<GraphNeighborhood>(`/cognitive/graph/neighborhood?kind=${kind}&key=${key}&depth=${depth}`)
  }, [])

  const createSnapshot = useCallback(async (kind: string, key: string, depth = 2, purpose = 'decision') => {
    return fetchApi<{ snapshot_id: string; node_count: number; edge_count: number }>(
      '/cognitive/graph/snapshot',
      { method: 'POST', body: JSON.stringify({ kind, key, depth, purpose }) }
    )
  }, [])

  // ---- Orchestration Memory ------------------------------------------

  const remember = useCallback(async (data: Partial<OrchestrationMemory>) => {
    return fetchApi<OrchestrationMemory>('/cognitive/memory', { method: 'POST', body: JSON.stringify(data) })
  }, [])

  const recall = useCallback(async (params: { scope?: string; memory_kind?: string; limit?: number } = {}) => {
    const qs = new URLSearchParams()
    if (params.scope) qs.set('scope', params.scope)
    if (params.memory_kind) qs.set('memory_kind', params.memory_kind)
    if (params.limit) qs.set('limit', String(params.limit))
    return fetchApi<OrchestrationMemory[]>(`/cognitive/memory?${qs}`)
  }, [])

  // ---- Forecasting ---------------------------------------------------

  const createForecast = useCallback(async (data: { subject_kind: string; subject_key: string; forecast_kind: string }) => {
    return fetchApi<ExecutionForecast>('/cognitive/forecast', { method: 'POST', body: JSON.stringify(data) })
  }, [])

  const listActiveForecasts = useCallback(async (params: { limit?: number } = {}) => {
    const qs = new URLSearchParams()
    if (params.limit) qs.set('limit', String(params.limit))
    return fetchApi<ExecutionForecast[]>(`/cognitive/forecast/active?${qs}`)
  }, [])

  const selectStrategy = useCallback(async (data: { subject_kind: string; subject_key: string; context: Record<string, unknown> }) => {
    return fetchApi<StrategyDecision>('/cognitive/forecast/strategy', { method: 'POST', body: JSON.stringify(data) })
  }, [])

  const createMultiStageGraph = useCallback(async (data: { subject_kind: string; subject_key: string; plan_label: string; steps: Record<string, unknown>[] }) => {
    return fetchApi<MultiStageGraph>('/cognitive/forecast/multi-stage', { method: 'POST', body: JSON.stringify(data) })
  }, [])

  // ---- Creative ------------------------------------------------------

  const listCreativeProfiles = useCallback(async (campaignId?: string) => {
    const qs = campaignId ? `?campaign_id=${campaignId}` : ''
    return fetchApi<CreativeProfile[]>(`/cognitive/creative/profiles${qs}`)
  }, [])

  const listNarrativeSequences = useCallback(async (params: { campaign_id?: string; profile_id?: string; limit?: number } = {}) => {
    const qs = new URLSearchParams()
    if (params.campaign_id) qs.set('campaign_id', params.campaign_id)
    if (params.profile_id) qs.set('profile_id', params.profile_id)
    if (params.limit) qs.set('limit', String(params.limit))
    return fetchApi<NarrativeSequence[]>(`/cognitive/creative/sequences?${qs}`)
  }, [])

  const predictEngagement = useCallback(async (audienceSegment: string, contentDuration: number, contentType = 'short_form') => {
    return fetchApi<{
      expected_completion_rate: number
      expected_engagement_score: number
      first_drop_seconds: number
      confidence: number
    }>(`/cognitive/creative/engagement-prediction?audience_segment=${audienceSegment}&content_duration=${contentDuration}&content_type=${contentType}`)
  }, [])

  // ---- Governance ---------------------------------------------------

  const listGovernanceRules = useCallback(async (agentKind?: string) => {
    const qs = agentKind ? `?agent_kind=${agentKind}` : ''
    return fetchApi<GovernanceRule[]>(`/cognitive/governance/rules${qs}`)
  }, [])

  const evaluateAction = useCallback(async (data: { agent_id: string; agent_kind: string; action_type: string; action_params: Record<string, unknown> }) => {
    return fetchApi<GovernanceDecision>('/cognitive/governance/evaluate', { method: 'POST', body: JSON.stringify(data) })
  }, [])

  const listActiveConflicts = useCallback(async (domain?: string) => {
    const qs = domain ? `?domain=${domain}` : ''
    return fetchApi<ConflictResolution[]>(`/cognitive/governance/conflicts${qs}`)
  }, [])

  // ---- Feedback -----------------------------------------------------

  const ingestFeedback = useCallback(async (data: {
    subject_kind: string; subject_key: string; feedback_type: string; actual_value: number; workflow_id?: string; execution_start: string
  }) => {
    return fetchApi<OrchestrationFeedback>('/cognitive/feedback', { method: 'POST', body: JSON.stringify(data) })
  }, [])

  const analyzeFeedbackOutcomes = useCallback(async (params: { subject_kind?: string; feedback_type?: string } = {}) => {
    const qs = new URLSearchParams()
    if (params.subject_kind) qs.set('subject_kind', params.subject_kind)
    if (params.feedback_type) qs.set('feedback_type', params.feedback_type)
    return fetchApi<Record<string, number>>(`/cognitive/feedback/analysis?${qs}`)
  }, [])

  const listTuningCycles = useCallback(async (contextKey?: string) => {
    const qs = contextKey ? `?context_key=${contextKey}` : ''
    return fetchApi<TuningCycle[]>(`/cognitive/feedback/tuning-cycles${qs}`)
  }, [])

  const getTuningRecommendations = useCallback(async (
    contextKey: string, parameters: string, currentValues: Record<string, number>
  ) => {
    return fetchApi<TuningRecommendation[]>(
      `/cognitive/feedback/tuning-recommendations?context_key=${contextKey}&parameters=${parameters}&current_values=${JSON.stringify(currentValues)}`
    )
  }, [])

  // ---- WebSocket ----------------------------------------------------

  const createCognitiveSocket = useCallback(() => {
    if (typeof window === 'undefined') return null
    const token = localStorage.getItem('access_token') || ''
    const wsUrl = (process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000').replace('http', 'ws') + '/ws/cognitive'
    const ws = new WebSocket(`${wsUrl}${token ? `?token=${token}` : ''}`)

    const subscribe = (channels: string[]) => {
      ws.send(JSON.stringify({ action: 'subscribe', channels }))
    }
    const unsubscribe = (channels: string[]) => {
      ws.send(JSON.stringify({ action: 'unsubscribe', channels }))
    }

    return { socket: ws, subscribe, unsubscribe }
  }, [])

  return {
    // Graph
    getGraphSummary,
    upsertNode,
    listNodes,
    getNeighborhood,
    createSnapshot,
    // Memory
    remember,
    recall,
    // Forecast
    createForecast,
    listActiveForecasts,
    selectStrategy,
    createMultiStageGraph,
    // Creative
    listCreativeProfiles,
    listNarrativeSequences,
    predictEngagement,
    // Governance
    listGovernanceRules,
    evaluateAction,
    listActiveConflicts,
    // Feedback
    ingestFeedback,
    analyzeFeedbackOutcomes,
    listTuningCycles,
    getTuningRecommendations,
    // WebSocket
    createCognitiveSocket,
  }
}