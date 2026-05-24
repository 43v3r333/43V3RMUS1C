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

// ---- Knowledge Graph ----

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

// ---- Orchestration Memory ----

export interface OrchestrationMemory {
  id: string
  scope: string
  memory_kind: string
  subject?: string
  subject_kind?: string
  title: string
  content: Record<string, unknown>
  importance: number
  recency: number
  confidence: number
  access_count: number
  last_accessed_at?: string
  is_pinned: boolean
  tags?: string[]
  execution_context?: Record<string, unknown>
  outcome?: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface MemoryStatistics {
  total_memories: number
  by_scope: Record<string, number>
  by_kind: Record<string, number>
  avg_importance: number
  avg_access_count: number
  pinned_count: number
  high_confidence_count: number
}

export interface ExecutionPattern {
  subject: string
  memory_kind: string
  frequency: number
  avg_importance: number
  avg_confidence: number
  significance: number
}

// ---- Strategic Planning ----

export interface StrategicPlan {
  id: string
  name: string
  description?: string
  plan_type: string
  status: string
  horizon: string
  strategy_kind: string
  objectives: Record<string, unknown>[]
  dependencies?: Record<string, unknown>[]
  constraints?: Record<string, unknown>
  required_resources?: Record<string, unknown>
  allocated_resources?: Record<string, unknown>
  estimated_start?: string
  estimated_end?: string
  actual_start?: string
  actual_end?: string
  confidence_score: number
  priority: number
  created_at: string
}

export interface PlanningStatistics {
  total_plans: number
  by_status: Record<string, number>
  by_strategy: Record<string, number>
  avg_confidence: number
  active_count: number
  completed_count: number
}

// ---- Forecasting ----

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

export interface ForecastAccuracy {
  count: number
  avg_error: number | null
  avg_accuracy: number | null
  by_forecast_kind: Record<string, { count: number; avg_accuracy: number }>
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

// ---- Creative Reasoning ----

export interface CreativeProfile {
  id: string
  name: string
  profile_type: string
  campaign_id?: string
  narrative_structure: string
  emotional_arc: string
  pacing_profile: string
  pacing_intensity?: number
  visual_keywords: string[]
  audio_keywords: string[]
  color_palette: string[]
  target_segments: string[]
  attention_span_seconds: number
  completion_rate_target: number
  engagement_rate_target: number
  max_duration?: number
  min_duration?: number
  content_guidelines?: Record<string, unknown>
  visual_style?: string
  music_mood?: string
  is_active: boolean
  version: number
  created_at: string
  updated_at: string
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

export interface EngagementPrediction {
  predicted_completion_rate: number
  predicted_engagement_rate: number
  attention_span_fit: number
  duration_fit: number
  visual_alignment: number
  audio_alignment: number
  overall_score: number
  recommendations: string[]
}

export interface NarrativeAnalysis {
  structure_compliance: number
  emotional_arc_compliance: number
  pacing_score: number
  segment_assessments: Record<string, unknown>[]
}

// ---- Multi-Agent Governance ----

export interface GovernanceSession {
  id: string
  name: string
  session_type: string
  status: string
  coordinator_id?: string
  participant_ids: string[]
  authority_level: string
  scope_kind?: string
  scope_id?: string
  actions_taken?: Record<string, unknown>[]
  decisions_made?: Record<string, unknown>[]
  negotiation_rounds: number
  consensus_reached: boolean
  disagreements?: Record<string, unknown>[]
  resolution?: Record<string, unknown>
  execution_plan?: Record<string, unknown>
  efficiency_score: number
  session_start?: string
  session_end?: string
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

export interface GovernanceStatistics {
  total_sessions: number
  by_status: Record<string, number>
  by_type: Record<string, number>
  avg_efficiency: number
  consensus_rate: number
  active_sessions: number
  total_decisions: number
  validated_decisions: number
}

// ---- Self-Evolution ----

export interface TuningCycle {
  id: string
  cycle_id: string
  name?: string
  context_key: string
  target_metric: string
  target_improvement: number
  parameter_space?: Record<string, unknown>
  current_parameters?: Record<string, number>
  best_parameters?: Record<string, number>
  max_iterations: number
  iteration: number
  current_score?: number
  best_score?: number
  baseline_score?: number
  cycle_state: string
  exploration_history?: Record<string, unknown>[]
  exploitation_history?: Record<string, unknown>[]
  improvements_found?: Record<string, unknown>[]
  started_at?: string
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

export interface RuntimeMetric {
  id: string
  metric_type: string
  metric_name: string
  value: number
  subject_kind?: string
  subject_id?: string
  delta?: number
  delta_percentage?: number
  change_direction?: string
  context?: Record<string, unknown>
  recorded_at: string
}

export interface MetricTrend {
  count: number
  trend: string
  current: number | null
  min: number
  max: number
  avg: number
  values: number[]
  timestamps: string[]
}

export interface EvolutionStatistics {
  total_cycles: number
  by_state: Record<string, number>
  by_context: Record<string, number>
  best_score_achieved?: number
  active_cycles: number
  converged_cycles: number
  total_metrics_recorded: number
}

// ---- Semantic Archives ----

export interface SemanticArchive {
  id: string
  name: string
  archive_type: string
  domain?: string
  entities?: Record<string, unknown>
  relationships?: Record<string, unknown>[]
  semantic_tags?: string[]
  use_count: number
  completeness: number
  archive_state: string
}

// ---- Feedback ----

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

// ---- Cognitive Summary ----

export interface CognitiveSummary {
  orchestration_memory: MemoryStatistics
  strategic_planning: PlanningStatistics
  creative_reasoning: Record<string, unknown>
  multi_agent_governance: GovernanceStatistics
  self_evolution: EvolutionStatistics
  timestamp: string
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

  const remember = useCallback(async (data: {
    scope: string;
    memory_kind: string;
    title: string;
    content: Record<string, unknown>;
    subject?: string;
    subject_kind?: string;
    importance?: number;
    confidence?: number;
    tags?: string[];
  }) => {
    return fetchApi<{ id: string; status: string }>('/cognitive/memories', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const recall = useCallback(async (params: {
    subject?: string;
    scope?: string;
    memory_kind?: string;
    subject_kind?: string;
    min_importance?: number;
    min_confidence?: number;
    tags?: string;
    search_text?: string;
    limit?: number;
    offset?: number;
  } = {}) => {
    const qs = new URLSearchParams()
    if (params.subject) qs.set('subject', params.subject)
    if (params.scope) qs.set('scope', params.scope)
    if (params.memory_kind) qs.set('memory_kind', params.memory_kind)
    if (params.subject_kind) qs.set('subject_kind', params.subject_kind)
    if (params.min_importance) qs.set('min_importance', String(params.min_importance))
    if (params.min_confidence) qs.set('min_confidence', String(params.min_confidence))
    if (params.tags) qs.set('tags', params.tags)
    if (params.search_text) qs.set('search_text', params.search_text)
    if (params.limit) qs.set('limit', String(params.limit))
    if (params.offset) qs.set('offset', String(params.offset))
    return fetchApi<{ items: OrchestrationMemory[]; total: number }>(`/cognitive/memories?${qs}`)
  }, [])

  const getMemoryStats = useCallback(async () => {
    return fetchApi<MemoryStatistics>('/cognitive/memories/stats')
  }, [])

  const analyzePatterns = useCallback(async (params: { subject_kind?: string; days?: number; min_frequency?: number } = {}) => {
    const qs = new URLSearchParams()
    if (params.subject_kind) qs.set('subject_kind', params.subject_kind)
    if (params.days) qs.set('days', String(params.days))
    if (params.min_frequency) qs.set('min_frequency', String(params.min_frequency))
    return fetchApi<{ patterns: ExecutionPattern[] }>(`/cognitive/memories/patterns?${qs}`)
  }, [])

  // ---- Strategic Planning ------------------------------------------

  const listPlans = useCallback(async (params: {
    status?: string;
    strategy_kind?: string;
    horizon?: string;
    min_priority?: number;
    limit?: number;
    offset?: number;
  } = {}) => {
    const qs = new URLSearchParams()
    if (params.status) qs.set('status', params.status)
    if (params.strategy_kind) qs.set('strategy_kind', params.strategy_kind)
    if (params.horizon) qs.set('horizon', params.horizon)
    if (params.min_priority) qs.set('min_priority', String(params.min_priority))
    if (params.limit) qs.set('limit', String(params.limit))
    if (params.offset) qs.set('offset', String(params.offset))
    return fetchApi<{ items: StrategicPlan[]; total: number }>(`/cognitive/plans?${qs}`)
  }, [])

  const getPlan = useCallback(async (planId: string) => {
    return fetchApi<StrategicPlan>(`/cognitive/plans/${planId}`)
  }, [])

  const activatePlan = useCallback(async (planId: string, allocatedResources?: Record<string, unknown>) => {
    return fetchApi<{ status: string; id: string }>(`/cognitive/plans/${planId}/activate`, {
      method: 'POST',
      body: JSON.stringify({ allocated_resources: allocatedResources }),
    })
  }, [])

  const getPlanningStats = useCallback(async () => {
    return fetchApi<PlanningStatistics>('/cognitive/plans/stats')
  }, [])

  // ---- Forecasting ---------------------------------------------------

  const createForecast = useCallback(async (data: {
    subject_kind: string;
    subject_key: string;
    forecast_kind: string;
    predicted_value: number;
    horizon: string;
    predicted_for: string;
    confidence?: number;
  }) => {
    return fetchApi<{ id: string; status: string }>('/cognitive/forecasts', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }, [])

  const listActiveForecasts = useCallback(async (params: { limit?: number } = {}) => {
    const qs = new URLSearchParams()
    if (params.limit) qs.set('limit', String(params.limit))
    return fetchApi<{ items: ExecutionForecast[]; total: number }>(`/cognitive/forecasts?${qs}`)
  }, [])

  const getForecastAccuracy = useCallback(async (params: { subject_kind?: string; days?: number } = {}) => {
    const qs = new URLSearchParams()
    if (params.subject_kind) qs.set('subject_kind', params.subject_kind)
    if (params.days) qs.set('days', String(params.days))
    return fetchApi<ForecastAccuracy>(`/cognitive/forecasts/accuracy?${qs}`)
  }, [])

  const selectStrategy = useCallback(async (data: { subject_kind: string; subject_key: string; context: Record<string, unknown> }) => {
    return fetchApi<StrategyDecision>('/cognitive/forecast/strategy', { method: 'POST', body: JSON.stringify(data) })
  }, [])

  const createMultiStageGraph = useCallback(async (data: { subject_kind: string; subject_key: string; plan_label: string; steps: Record<string, unknown>[] }) => {
    return fetchApi<MultiStageGraph>('/cognitive/forecast/multi-stage', { method: 'POST', body: JSON.stringify(data) })
  }, [])

  // ---- Creative ------------------------------------------------------

  const listCreativeProfiles = useCallback(async (params: { profile_type?: string; is_active?: boolean; limit?: number } = {}) => {
    const qs = new URLSearchParams()
    if (params.profile_type) qs.set('profile_type', params.profile_type)
    if (params.is_active !== undefined) qs.set('is_active', String(params.is_active))
    if (params.limit) qs.set('limit', String(params.limit))
    return fetchApi<{ items: CreativeProfile[]; total: number }>(`/cognitive/profiles?${qs}`)
  }, [])

  const getCreativeProfile = useCallback(async (profileId: string) => {
    return fetchApi<CreativeProfile>(`/cognitive/profiles/${profileId}`)
  }, [])

  const analyzeNarrative = useCallback(async (profileId: string, contentSegments: Record<string, unknown>[]) => {
    return fetchApi<NarrativeAnalysis>(`/cognitive/profiles/${profileId}/analyze`, {
      method: 'POST',
      body: JSON.stringify({ content_segments: contentSegments }),
    })
  }, [])

  const predictEngagement = useCallback(async (profileId: string, contentData: Record<string, unknown>) => {
    return fetchApi<EngagementPrediction>(`/cognitive/profiles/${profileId}/predict`, {
      method: 'POST',
      body: JSON.stringify(contentData),
    })
  }, [])

  const listNarrativeSequences = useCallback(async (params: { campaign_id?: string; profile_id?: string; limit?: number } = {}) => {
    const qs = new URLSearchParams()
    if (params.campaign_id) qs.set('campaign_id', params.campaign_id)
    if (params.profile_id) qs.set('profile_id', params.profile_id)
    if (params.limit) qs.set('limit', String(params.limit))
    return fetchApi<NarrativeSequence[]>(`/cognitive/creative/sequences?${qs}`)
  }, [])

  // ---- Governance ---------------------------------------------------

  const listSessions = useCallback(async (params: {
    status?: string;
    session_type?: string;
    coordinator_id?: string;
    scope_kind?: string;
    limit?: number;
    offset?: number;
  } = {}) => {
    const qs = new URLSearchParams()
    if (params.status) qs.set('status', params.status)
    if (params.session_type) qs.set('session_type', params.session_type)
    if (params.coordinator_id) qs.set('coordinator_id', params.coordinator_id)
    if (params.scope_kind) qs.set('scope_kind', params.scope_kind)
    if (params.limit) qs.set('limit', String(params.limit))
    if (params.offset) qs.set('offset', String(params.offset))
    return fetchApi<{ items: GovernanceSession[]; total: number }>(`/cognitive/sessions?${qs}`)
  }, [])

  const getSession = useCallback(async (sessionId: string) => {
    return fetchApi<GovernanceSession>(`/cognitive/sessions/${sessionId}`)
  }, [])

  const addSessionAction = useCallback(async (sessionId: string, actionType: string, agentId: string, actionData: Record<string, unknown>) => {
    return fetchApi<{ status: string }>(`/cognitive/sessions/${sessionId}/action`, {
      method: 'POST',
      body: JSON.stringify({ action_type: actionType, agent_id: agentId, action_data: actionData }),
    })
  }, [])

  const reachConsensus = useCallback(async (sessionId: string, consensusData: Record<string, unknown>) => {
    return fetchApi<{ status: string }>(`/cognitive/sessions/${sessionId}/consensus`, {
      method: 'POST',
      body: JSON.stringify(consensusData),
    })
  }, [])

  const endSession = useCallback(async (sessionId: string, resolution?: Record<string, unknown>, executionPlan?: Record<string, unknown>) => {
    return fetchApi<{ status: string; efficiency_score: number }>(`/cognitive/sessions/${sessionId}/end`, {
      method: 'POST',
      body: JSON.stringify({ resolution, execution_plan: executionPlan }),
    })
  }, [])

  const getGovernanceStats = useCallback(async () => {
    return fetchApi<GovernanceStatistics>('/cognitive/sessions/stats')
  }, [])

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

  // ---- Self-Evolution ----------------------------------------------

  const listTuningCycles = useCallback(async (params: { cycle_state?: string; context_key?: string; limit?: number } = {}) => {
    const qs = new URLSearchParams()
    if (params.cycle_state) qs.set('cycle_state', params.cycle_state)
    if (params.context_key) qs.set('context_key', params.context_key)
    if (params.limit) qs.set('limit', String(params.limit))
    return fetchApi<{ items: TuningCycle[]; total: number }>(`/cognitive/optimization/cycles?${qs}`)
  }, [])

  const getTuningCycle = useCallback(async (cycleId: string) => {
    return fetchApi<TuningCycle>(`/cognitive/optimization/cycles/${cycleId}`)
  }, [])

  const startTuningCycle = useCallback(async (cycleId: string) => {
    return fetchApi<{ cycle_id: string; status: string }>(`/cognitive/optimization/cycles/${cycleId}/start`, {
      method: 'POST',
    })
  }, [])

  const recordIteration = useCallback(async (cycleId: string, parameters: Record<string, number>, score: number) => {
    return fetchApi<{
      cycle_id: string;
      iteration: number;
      current_score: number;
      best_score: number;
      state: string;
    }>(`/cognitive/optimization/cycles/${cycleId}/iteration`, {
      method: 'POST',
      body: JSON.stringify({ parameters, score }),
    })
  }, [])

  const getTuningRecommendations = useCallback(async (
    contextKey: string, parameters: string, currentValues: Record<string, number>
  ) => {
    return fetchApi<TuningRecommendation[]>(
      `/cognitive/feedback/tuning-recommendations?context_key=${contextKey}&parameters=${parameters}&current_values=${JSON.stringify(currentValues)}`
    )
  }, [])

  const listMetrics = useCallback(async (params: {
    metric_name?: string;
    subject_kind?: string;
    subject_id?: string;
    metric_type?: string;
    hours?: number;
    limit?: number;
  } = {}) => {
    const qs = new URLSearchParams()
    if (params.metric_name) qs.set('metric_name', params.metric_name)
    if (params.subject_kind) qs.set('subject_kind', params.subject_kind)
    if (params.subject_id) qs.set('subject_id', params.subject_id)
    if (params.metric_type) qs.set('metric_type', params.metric_type)
    if (params.hours) qs.set('hours', String(params.hours))
    if (params.limit) qs.set('limit', String(params.limit))
    return fetchApi<{ items: RuntimeMetric[]; total: number }>(`/cognitive/metrics?${qs}`)
  }, [])

  const getMetricTrend = useCallback(async (metricName: string, subjectId?: string, periodHours = 24) => {
    const qs = new URLSearchParams()
    qs.set('metric_name', metricName)
    if (subjectId) qs.set('subject_id', subjectId)
    qs.set('period_hours', String(periodHours))
    return fetchApi<MetricTrend>(`/cognitive/metrics/${metricName}/trend?${qs}`)
  }, [])

  const getEvolutionStats = useCallback(async () => {
    return fetchApi<EvolutionStatistics>('/cognitive/optimization/stats')
  }, [])

  // ---- Semantic Archives -------------------------------------------

  const searchArchives = useCallback(async (params: {
    query: string;
    archive_type?: string;
    domain?: string;
    tags?: string;
    limit?: number;
  }) => {
    const qs = new URLSearchParams()
    qs.set('query', params.query)
    if (params.archive_type) qs.set('archive_type', params.archive_type)
    if (params.domain) qs.set('domain', params.domain)
    if (params.tags) qs.set('tags', params.tags)
    if (params.limit) qs.set('limit', String(params.limit))
    return fetchApi<{ items: SemanticArchive[]; total: number }>(`/cognitive/archives/search?${qs}`)
  }, [])

  // ---- Cognitive Summary -------------------------------------------

  const getCognitiveSummary = useCallback(async () => {
    return fetchApi<CognitiveSummary>('/cognitive/cognitive/summary')
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
    getMemoryStats,
    analyzePatterns,
    // Strategic Planning
    listPlans,
    getPlan,
    activatePlan,
    getPlanningStats,
    // Forecast
    createForecast,
    listActiveForecasts,
    getForecastAccuracy,
    selectStrategy,
    createMultiStageGraph,
    // Creative
    listCreativeProfiles,
    getCreativeProfile,
    analyzeNarrative,
    predictEngagement,
    listNarrativeSequences,
    // Governance
    listSessions,
    getSession,
    addSessionAction,
    reachConsensus,
    endSession,
    getGovernanceStats,
    listGovernanceRules,
    evaluateAction,
    listActiveConflicts,
    // Self-Evolution
    listTuningCycles,
    getTuningCycle,
    startTuningCycle,
    recordIteration,
    getTuningRecommendations,
    listMetrics,
    getMetricTrend,
    getEvolutionStats,
    // Archives
    searchArchives,
    // Summary
    getCognitiveSummary,
    // WebSocket
    createCognitiveSocket,
  }
}