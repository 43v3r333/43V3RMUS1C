/**
 * 43V3R CORE - Unified Cognitive Coherence API Client
 * Typed client for unified runtime identity and cognitive continuity.
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

// ---- Identity & Lineage ----

export interface RuntimeIdentity {
  id: string
  identity_scope: string
  identity_key: string
  name: string
  description?: string
  parent_id?: string
  root_id?: string
  properties: Record<string, unknown>
  capabilities: string[]
  lifecycle_state: string
  version: number
  correlation_id?: string
  trace_id?: string
  created_at: string
  last_accessed_at?: string
}

export interface OrchestrationLineage {
  id: string
  root_identity_id: string
  lineage_type: string
  status: string
  total_nodes: number
  total_events: number
  depth: number
  started_at: string
  completed_at?: string
}

export interface LineageNode {
  node_id: string
  event_type: string
  depth: number
  timestamp: string
  duration_ms?: number
  correlation_id?: string
}

export interface LineageResponse {
  lineage: OrchestrationLineage
  nodes: LineageNode[]
}

// ---- Context ----

export interface RuntimeContext {
  id: string
  identity_id: string
  context_key: string
  context_scope: string
  value: Record<string, unknown>
  version: number
  correlation_id?: string
}

// ---- Cognitive Memory ----

export interface CognitiveMemoryItem {
  id: string
  identity_id: string
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
  created_at: string
}

export interface MemoryRetrievalResult {
  items: CognitiveMemoryItem[]
  fragments: MemoryFragment[]
  relevance_scores: Record<string, number>
  total_importance: number
}

export interface MemoryFragment {
  id: string
  memory_id: string
  fragment_id: string
  fragment_type: string
  relevance_score: number
}

// ---- Semantic Graph ----

export interface SemanticGraph {
  graph_id: string
  name: string
  description?: string
  nodes: SemanticNode[]
  edges: SemanticEdge[]
  node_count: number
  edge_count: number
  semantic_depth: number
  lifecycle_state: string
}

export interface SemanticNode {
  node_id: string
  node_key: string
  node_type: string
  semantic_key: string
  label: string
  properties: Record<string, unknown>
  tags: string[]
  position_x: number
  position_y: number
}

export interface SemanticEdge {
  edge_id: string
  source_key: string
  target_key: string
  relation_type: string
  weight: number
  confidence: number
}

export interface SemanticPath {
  nodes: string[]
  edges: string[]
  total_weight: number
  confidence: number
}

// ---- Adaptive Runtime ----

export interface AdaptiveProfile {
  profile_id: string
  profile_key: string
  context_key: string
  parameters: Record<string, unknown>
  baseline_metrics: Record<string, number>
  current_metrics: Record<string, number>
  best_score?: number
  optimization_iterations: number
  profile_state: string
  last_tuned_at?: string
}

export interface TuningHistory {
  tuning_id: string
  parameters_before: Record<string, unknown>
  parameters_after: Record<string, unknown>
  score_before?: number
  score_after?: number
  improvement_percent?: number
  strategy: string
  trigger_reason: string
  started_at: string
  completed_at?: string
}

export interface TuningRecommendation {
  parameter: string
  current_value: number
  suggested_value: number
  improvement_percent: number
  confidence: number
}

// ---- Governance ----

export interface GovernancePolicy {
  policy_id: string
  policy_key: string
  name: string
  description?: string
  policy_scope: string
  conditions: Record<string, unknown>
  enforcement_action: string
  severity: string
  priority: number
  trigger_count: number
  violation_count: number
  lifecycle_state: string
}

export interface PolicyViolation {
  id: string
  violation_id: string
  severity: string
  violation_type: string
  description: string
  detected_at: string
  resolved: boolean
}

export interface PolicyEvaluationResult {
  triggered: boolean
  policy: {
    id: string
    name: string
    enforcement_action: string
  } | null
  violations: PolicyViolation[]
  reason: string
}

export interface ArbitrationRecord {
  record_id: string
  arbitration_type: string
  decision: string
  reason: string
  confidence: number
  decided_at: string
}

// ---- Stability & Prediction ----

export interface StabilityMetrics {
  stability_id: string
  stability_status: string
  stability_score: number
  health_score: number
  throughput: number
  latency_p50?: number
  latency_p95?: number
  latency_p99?: number
  error_rate: number
  failure_count: number
  recorded_at: string
}

export interface StabilityAssessment {
  status: string
  score: number
  health_score: number
  issues: string[]
  recommendations: string[]
}

export interface ExecutionForecast {
  forecast_id: string
  subject_kind: string
  subject_key: string
  forecast_kind: string
  horizon: string
  predicted_value: number
  predicted_unit?: string
  confidence: number
  min_value?: number
  max_value?: number
  predicted_for: string
  forecast_state: string
}

export interface AnomalyDetection {
  anomaly_id: string
  anomaly_type: string
  severity: string
  description: string
  deviation: number
  detected_at: string
  is_resolved: boolean
}

// ---- Distributed Coordination ----

export interface DistributedContextState {
  context_id: string
  context_key: string
  partition_key: string
  state: Record<string, unknown>
  version: number
  consensus_state: string
  participating_nodes: string[]
  node_versions: Record<string, number>
}

export interface AgentConsensus {
  consensus_id: string
  topic_kind: string
  topic_key: string
  decision: string
  reason: string
  votes: ConsensusVote[]
  consensus_state: string
  confidence: number
  gathered_votes: number
  required_votes: number
}

export interface ConsensusVote {
  agent_id: string
  vote: string
  reason: string
  timestamp: string
}

export interface AuthorityDelegation {
  delegation_id: string
  delegator_id: string
  delegate_id: string
  authority_type: string
  scope: Record<string, unknown>
  constraints: Record<string, unknown>
  max_depth: number
  current_depth: number
  delegation_state: string
  invocation_count: number
  created_at: string
  expires_at?: string
}

// ---- System Status ----

export interface CoherenceSystemStatus {
  service: string
  status: string
  capabilities: string[]
  timestamp: string
}

// ---- Identity Creation ----

export interface IdentityCreationRequest {
  identity_scope: string
  identity_key: string
  name: string
  description?: string
  parent_id?: string
  correlation_id?: string
  properties?: Record<string, unknown>
  capabilities?: string[]
  owner_id?: string
}

export interface IdentityCreationResult {
  identity: {
    id: string
    identity_scope: string
    identity_key: string
    name: string
    trace_id: string
  }
  lineage: {
    id: string
    started_at: string
  }
  context: {
    id: string
    context_key: string
  }
}

// =====================================================================
// API Hook
// =====================================================================

export interface UseCoherenceApi {
  // Identity Management
  createIdentity: (request: IdentityCreationRequest) => Promise<IdentityCreationResult>
  getIdentity: (scope: string, key: string) => Promise<RuntimeIdentity>
  getIdentityById: (identityId: string) => Promise<RuntimeIdentity>
  updateIdentity: (identityId: string, updates: { properties?: Record<string, unknown>; lifecycle_state?: string }) => Promise<RuntimeIdentity>
  propagateContext: (identityId: string, contextKey: string, value: Record<string, unknown>) => Promise<{ contexts: { id: string; context_key: string; propagation_depth: number }[] }>
  
  // Lineage
  getLineage: (identityId: string, eventTypes?: string, limit?: number) => Promise<LineageResponse>
  
  // Context
  setContext: (identityId: string, contextKey: string, value: Record<string, unknown>) => Promise<RuntimeContext>
  getContext: (identityId: string, contextKey: string) => Promise<RuntimeContext>
  getContextsByScope: (identityId: string, scope?: string) => Promise<RuntimeContext[]>
  
  // Memory
  storeMemory: (identityId: string, memory: {
    scope: string
    memory_kind: string
    subject: string
    title: string
    content: Record<string, unknown>
    importance?: number
    confidence?: number
    workflow_id?: string
    agent_id?: string
    is_pinned?: boolean
    expires_at?: string
  }) => Promise<CognitiveMemoryItem>
  recallMemory: (identityId: string, params?: {
    scope?: string
    memory_kind?: string
    subject?: string
    retrieval_mode?: string
    min_importance?: number
    limit?: number
  }) => Promise<MemoryRetrievalResult>
  
  // Semantic Graphs
  createGraph: (graph: {
    graph_id: string
    name: string
    description?: string
    owner_id?: string
  }) => Promise<{ graph_id: string; name: string; node_count: number; edge_count: number }>
  getGraph: (graphId: string) => Promise<SemanticGraph>
  addNode: (graphId: string, node: {
    node_key: string
    node_type: string
    semantic_key: string
    label: string
    properties?: Record<string, unknown>
    tags?: string[]
    position_x?: number
    position_y?: number
  }) => Promise<SemanticNode>
  addEdge: (graphId: string, edge: {
    source_key: string
    target_key: string
    relation_type: string
    label?: string
    weight?: number
    confidence?: number
  }) => Promise<SemanticEdge>
  findPath: (graphId: string, sourceKey: string, targetKey: string, maxDepth?: number) => Promise<{ nodes: string[]; edges: string[]; total_weight: number; confidence: number } | { path: null; message: string }>
  
  // Adaptive Profiles
  createProfile: (profile: {
    profile_key: string
    context_key: string
    parameters?: Record<string, unknown>
    baseline_metrics?: Record<string, number>
    tuning_strategy?: string
  }) => Promise<{ profile_id: string; optimization_iterations: number }>
  getProfile: (profileKey: string, contextKey: string) => Promise<AdaptiveProfile>
  updateParameters: (profileId: string, parameters: Record<string, unknown>, recordTuning?: boolean) => Promise<{ profile_id: string; parameters: Record<string, unknown>; optimization_iterations: number }>
  recordMetrics: (profileId: string, metrics: Record<string, number>, iteration?: number) => Promise<{ metric_name: string; value: number; iteration: number }>
  getSuggestions: (profileId: string) => Promise<{ suggested_parameters: Record<string, unknown> }>
  
  // Governance
  createPolicy: (policy: {
    policy_key: string
    name: string
    policy_scope: string
    conditions: Record<string, unknown>
    enforcement_action: string
    description?: string
    severity?: string
    action_config?: Record<string, unknown>
    priority?: number
  }) => Promise<{ policy_id: string; trigger_count: number }>
  evaluatePolicies: (identityId: string, context: Record<string, unknown>, scopeFilter?: string[]) => Promise<PolicyEvaluationResult>
  arbitrate: (identityId: string, arbitration: {
    arbitration_type: string
    parties: string[]
    context: Record<string, unknown>
  }) => Promise<ArbitrationRecord>
  getViolations: (params?: { policy_id?: string; severity?: string; limit?: number }) => Promise<PolicyViolation[]>
  
  // Stability
  recordStability: (identityId: string, metrics: {
    throughput?: number
    latency_p50?: number
    latency_p95?: number
    latency_p99?: number
    error_rate?: number
    failure_count?: number
    cpu_usage?: number
    memory_usage?: number
    health_score?: number
  }) => Promise<StabilityMetrics>
  assessStability: (identityId: string, windowSeconds?: number) => Promise<StabilityAssessment>
  
  // Forecasting
  createForecast: (forecast: {
    subject_kind: string
    subject_key: string
    forecast_kind: string
    horizon: string
    predicted_value: number
    predicted_unit?: string
    confidence?: number
    min_value?: number
    max_value?: number
  }) => Promise<ExecutionForecast>
  getActiveForecasts: (params?: { subject_key?: string; forecast_kind?: string; limit?: number }) => Promise<ExecutionForecast[]>
  
  // Anomaly Detection
  detectAnomaly: (identityId: string, anomaly: {
    anomaly_type: string
    description: string
    baseline: Record<string, number>
    observed: Record<string, number>
    metric_name: string
    severity?: string
    threshold?: number
  }) => Promise<AnomalyDetection>
  getAnomalies: (params?: { identity_id?: string; is_resolved?: boolean; limit?: number }) => Promise<AnomalyDetection[]>
  
  // Distributed Coordination
  createContextState: (identityId: string, context: {
    context_key: string
    partition_key: string
    state: Record<string, unknown>
    participating_nodes?: string[]
  }) => Promise<{ context_id: string; consensus_state: string }>
  updateContextState: (contextKey: string, partitionKey: string, state: Record<string, unknown>, nodeId: string) => Promise<{ version: number; consensus_state: string }>
  getContextState: (contextKey: string, partitionKey: string) => Promise<DistributedContextState>
  
  // Consensus
  initiateConsensus: (topic: {
    topic_kind: string
    topic_key: string
    required_votes?: number
  }) => Promise<{ consensus_id: string; consensus_state: string }>
  castVote: (consensusId: string, vote: { agent_id: string; vote: string; reason: string }) => Promise<AgentConsensus>
  getConsensus: (consensusId: string) => Promise<AgentConsensus>
  
  // Authority Delegation
  delegateAuthority: (delegatorId: string, delegation: {
    delegate_id: string
    authority_type: string
    scope?: Record<string, unknown>
    constraints?: Record<string, unknown>
    max_depth?: number
  }) => Promise<AuthorityDelegation>
  invokeDelegation: (delegationId: string) => Promise<{ current_depth: number; invocation_count: number }>
  revokeDelegation: (delegationId: string, reason: string) => Promise<AuthorityDelegation>
  
  // System
  getSystemStatus: () => Promise<CoherenceSystemStatus>
}

export function useCoherenceApi(): UseCoherenceApi {
  // ---- Identity Management ----
  
  const createIdentity = useCallback(async (request: IdentityCreationRequest) => {
    return fetchApi<IdentityCreationResult>('/coherence/identities', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }, [])
  
  const getIdentity = useCallback(async (scope: string, key: string) => {
    return fetchApi<RuntimeIdentity>(`/coherence/identities/${scope}/${key}`)
  }, [])
  
  const getIdentityById = useCallback(async (identityId: string) => {
    return fetchApi<RuntimeIdentity>(`/coherence/identities/by-id/${identityId}`)
  }, [])
  
  const updateIdentity = useCallback(async (identityId: string, updates: { properties?: Record<string, unknown>; lifecycle_state?: string }) => {
    return fetchApi<RuntimeIdentity>(`/coherence/identities/${identityId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    })
  }, [])
  
  const propagateContext = useCallback(async (identityId: string, contextKey: string, value: Record<string, unknown>) => {
    return fetchApi<{ contexts: { id: string; context_key: string; propagation_depth: number }[] }>(`/coherence/identities/${identityId}/context`, {
      method: 'POST',
      body: JSON.stringify({ context_key: contextKey, value }),
    })
  }, [])
  
  // ---- Lineage ----
  
  const getLineage = useCallback(async (identityId: string, eventTypes?: string, limit = 100) => {
    const qs = eventTypes ? `?event_types=${eventTypes}&limit=${limit}` : `?limit=${limit}`
    return fetchApi<LineageResponse>(`/coherence/identities/${identityId}/lineage${qs}`)
  }, [])
  
  // ---- Context ----
  
  const setContext = useCallback(async (identityId: string, contextKey: string, value: Record<string, unknown>) => {
    return fetchApi<RuntimeContext>(`/coherence/contexts/${identityId}`, {
      method: 'POST',
      body: JSON.stringify({ context_key: contextKey, value }),
    })
  }, [])
  
  const getContext = useCallback(async (identityId: string, contextKey: string) => {
    return fetchApi<RuntimeContext>(`/coherence/contexts/${identityId}/${contextKey}`)
  }, [])
  
  const getContextsByScope = useCallback(async (identityId: string, scope?: string) => {
    const qs = scope ? `?scope=${scope}` : ''
    return fetchApi<RuntimeContext[]>(`/coherence/contexts/${identityId}${qs}`)
  }, [])
  
  // ---- Memory ----
  
  const storeMemory = useCallback(async (identityId: string, memory: {
    scope: string
    memory_kind: string
    subject: string
    title: string
    content: Record<string, unknown>
    importance?: number
    confidence?: number
    workflow_id?: string
    agent_id?: string
    is_pinned?: boolean
    expires_at?: string
  }) => {
    return fetchApi<CognitiveMemoryItem>(`/coherence/memory/${identityId}`, {
      method: 'POST',
      body: JSON.stringify(memory),
    })
  }, [])
  
  const recallMemory = useCallback(async (identityId: string, params?: {
    scope?: string
    memory_kind?: string
    subject?: string
    retrieval_mode?: string
    min_importance?: number
    limit?: number
  }) => {
    const searchParams = new URLSearchParams()
    if (params?.scope) searchParams.set('scope', params.scope)
    if (params?.memory_kind) searchParams.set('memory_kind', params.memory_kind)
    if (params?.subject) searchParams.set('subject', params.subject)
    if (params?.retrieval_mode) searchParams.set('retrieval_mode', params.retrieval_mode)
    if (params?.min_importance !== undefined) searchParams.set('min_importance', String(params.min_importance))
    if (params?.limit) searchParams.set('limit', String(params.limit))
    
    const qs = searchParams.toString()
    return fetchApi<MemoryRetrievalResult>(`/coherence/memory/${identityId}${qs ? `?${qs}` : ''}`)
  }, [])
  
  // ---- Semantic Graphs ----
  
  const createGraph = useCallback(async (graph: {
    graph_id: string
    name: string
    description?: string
    owner_id?: string
  }) => {
    return fetchApi<{ graph_id: string; name: string; node_count: number; edge_count: number }>('/coherence/graphs', {
      method: 'POST',
      body: JSON.stringify(graph),
    })
  }, [])
  
  const getGraph = useCallback(async (graphId: string) => {
    return fetchApi<SemanticGraph>(`/coherence/graphs/${graphId}`)
  }, [])
  
  const addNode = useCallback(async (graphId: string, node: {
    node_key: string
    node_type: string
    semantic_key: string
    label: string
    properties?: Record<string, unknown>
    tags?: string[]
    position_x?: number
    position_y?: number
  }) => {
    return fetchApi<SemanticNode>(`/coherence/graphs/${graphId}/nodes`, {
      method: 'POST',
      body: JSON.stringify(node),
    })
  }, [])
  
  const addEdge = useCallback(async (graphId: string, edge: {
    source_key: string
    target_key: string
    relation_type: string
    label?: string
    weight?: number
    confidence?: number
  }) => {
    return fetchApi<SemanticEdge>(`/coherence/graphs/${graphId}/edges`, {
      method: 'POST',
      body: JSON.stringify(edge),
    })
  }, [])
  
  const findPath = useCallback(async (graphId: string, sourceKey: string, targetKey: string, maxDepth = 10) => {
    return fetchApi<{ nodes: string[]; edges: string[]; total_weight: number; confidence: number } | { path: null; message: string }>(
      `/coherence/graphs/${graphId}/path?source_key=${sourceKey}&target_key=${targetKey}&max_depth=${maxDepth}`
    )
  }, [])
  
  // ---- Adaptive Profiles ----
  
  const createProfile = useCallback(async (profile: {
    profile_key: string
    context_key: string
    parameters?: Record<string, unknown>
    baseline_metrics?: Record<string, number>
    tuning_strategy?: string
  }) => {
    return fetchApi<{ profile_id: string; optimization_iterations: number }>('/coherence/profiles', {
      method: 'POST',
      body: JSON.stringify(profile),
    })
  }, [])
  
  const getProfile = useCallback(async (profileKey: string, contextKey: string) => {
    return fetchApi<AdaptiveProfile>(`/coherence/profiles/${profileKey}/${contextKey}`)
  }, [])
  
  const updateParameters = useCallback(async (profileId: string, parameters: Record<string, unknown>, recordTuning = true) => {
    return fetchApi<{ profile_id: string; parameters: Record<string, unknown>; optimization_iterations: number }>(`/coherence/profiles/${profileId}`, {
      method: 'PATCH',
      body: JSON.stringify({ parameters, record_tuning: recordTuning }),
    })
  }, [])
  
  const recordMetrics = useCallback(async (profileId: string, metrics: Record<string, number>, iteration?: number) => {
    return fetchApi<{ metric_name: string; value: number; iteration: number }>(`/coherence/profiles/${profileId}/metrics`, {
      method: 'POST',
      body: JSON.stringify({ metrics, iteration }),
    })
  }, [])
  
  const getSuggestions = useCallback(async (profileId: string) => {
    return fetchApi<{ suggested_parameters: Record<string, unknown> }>(`/coherence/profiles/${profileId}/suggestions`)
  }, [])
  
  // ---- Governance ----
  
  const createPolicy = useCallback(async (policy: {
    policy_key: string
    name: string
    policy_scope: string
    conditions: Record<string, unknown>
    enforcement_action: string
    description?: string
    severity?: string
    action_config?: Record<string, unknown>
    priority?: number
  }) => {
    return fetchApi<{ policy_id: string; trigger_count: number }>('/coherence/policies', {
      method: 'POST',
      body: JSON.stringify(policy),
    })
  }, [])
  
  const evaluatePolicies = useCallback(async (identityId: string, context: Record<string, unknown>, scopeFilter?: string[]) => {
    return fetchApi<PolicyEvaluationResult>(`/coherence/evaluate/${identityId}`, {
      method: 'POST',
      body: JSON.stringify({ context, scope_filter: scopeFilter }),
    })
  }, [])
  
  const arbitrate = useCallback(async (identityId: string, arbitration: {
    arbitration_type: string
    parties: string[]
    context: Record<string, unknown>
  }) => {
    return fetchApi<ArbitrationRecord>(`/coherence/arbitrate/${identityId}`, {
      method: 'POST',
      body: JSON.stringify(arbitration),
    })
  }, [])
  
  const getViolations = useCallback(async (params?: { policy_id?: string; severity?: string; limit?: number }) => {
    const searchParams = new URLSearchParams()
    if (params?.policy_id) searchParams.set('policy_id', params.policy_id)
    if (params?.severity) searchParams.set('severity', params.severity)
    if (params?.limit) searchParams.set('limit', String(params.limit))
    
    const qs = searchParams.toString()
    return fetchApi<PolicyViolation[]>(`/coherence/violations${qs ? `?${qs}` : ''}`)
  }, [])
  
  // ---- Stability ----
  
  const recordStability = useCallback(async (identityId: string, metrics: {
    throughput?: number
    latency_p50?: number
    latency_p95?: number
    latency_p99?: number
    error_rate?: number
    failure_count?: number
    cpu_usage?: number
    memory_usage?: number
    health_score?: number
  }) => {
    return fetchApi<StabilityMetrics>(`/coherence/stability/${identityId}`, {
      method: 'POST',
      body: JSON.stringify({ metrics }),
    })
  }, [])
  
  const assessStability = useCallback(async (identityId: string, windowSeconds = 300) => {
    return fetchApi<StabilityAssessment>(`/coherence/stability/${identityId}/assessment?window_seconds=${windowSeconds}`)
  }, [])
  
  // ---- Forecasting ----
  
  const createForecast = useCallback(async (forecast: {
    subject_kind: string
    subject_key: string
    forecast_kind: string
    horizon: string
    predicted_value: number
    predicted_unit?: string
    confidence?: number
    min_value?: number
    max_value?: number
  }) => {
    return fetchApi<ExecutionForecast>('/coherence/forecasts', {
      method: 'POST',
      body: JSON.stringify(forecast),
    })
  }, [])
  
  const getActiveForecasts = useCallback(async (params?: { subject_key?: string; forecast_kind?: string; limit?: number }) => {
    const searchParams = new URLSearchParams()
    if (params?.subject_key) searchParams.set('subject_key', params.subject_key)
    if (params?.forecast_kind) searchParams.set('forecast_kind', params.forecast_kind)
    if (params?.limit) searchParams.set('limit', String(params.limit))
    
    const qs = searchParams.toString()
    return fetchApi<ExecutionForecast[]>(`/coherence/forecasts${qs ? `?${qs}` : ''}`)
  }, [])
  
  // ---- Anomaly Detection ----
  
  const detectAnomaly = useCallback(async (identityId: string, anomaly: {
    anomaly_type: string
    description: string
    baseline: Record<string, number>
    observed: Record<string, number>
    metric_name: string
    severity?: string
    threshold?: number
  }) => {
    return fetchApi<AnomalyDetection>(`/coherence/anomalies/${identityId}`, {
      method: 'POST',
      body: JSON.stringify(anomaly),
    })
  }, [])
  
  const getAnomalies = useCallback(async (params?: { identity_id?: string; is_resolved?: boolean; limit?: number }) => {
    const searchParams = new URLSearchParams()
    if (params?.identity_id) searchParams.set('identity_id', params.identity_id)
    if (params?.is_resolved !== undefined) searchParams.set('is_resolved', String(params.is_resolved))
    if (params?.limit) searchParams.set('limit', String(params.limit))
    
    const qs = searchParams.toString()
    return fetchApi<AnomalyDetection[]>(`/coherence/anomalies${qs ? `?${qs}` : ''}`)
  }, [])
  
  // ---- Distributed Coordination ----
  
  const createContextState = useCallback(async (identityId: string, context: {
    context_key: string
    partition_key: string
    state: Record<string, unknown>
    participating_nodes?: string[]
  }) => {
    return fetchApi<{ context_id: string; consensus_state: string }>(`/coherence/distributed-contexts`, {
      method: 'POST',
      body: JSON.stringify({ identity_id: identityId, ...context }),
    })
  }, [])
  
  const updateContextState = useCallback(async (contextKey: string, partitionKey: string, state: Record<string, unknown>, nodeId: string) => {
    return fetchApi<{ version: number; consensus_state: string }>(`/coherence/distributed-contexts/${contextKey}/${partitionKey}`, {
      method: 'PATCH',
      body: JSON.stringify({ state, node_id: nodeId }),
    })
  }, [])
  
  const getContextState = useCallback(async (contextKey: string, partitionKey: string) => {
    return fetchApi<DistributedContextState>(`/coherence/distributed-contexts/${contextKey}/${partitionKey}`)
  }, [])
  
  // ---- Consensus ----
  
  const initiateConsensus = useCallback(async (topic: {
    topic_kind: string
    topic_key: string
    required_votes?: number
  }) => {
    return fetchApi<{ consensus_id: string; consensus_state: string }>('/coherence/consensus', {
      method: 'POST',
      body: JSON.stringify(topic),
    })
  }, [])
  
  const castVote = useCallback(async (consensusId: string, vote: { agent_id: string; vote: string; reason: string }) => {
    return fetchApi<AgentConsensus>(`/coherence/consensus/${consensusId}/vote`, {
      method: 'POST',
      body: JSON.stringify(vote),
    })
  }, [])
  
  const getConsensus = useCallback(async (consensusId: string) => {
    return fetchApi<AgentConsensus>(`/coherence/consensus/${consensusId}`)
  }, [])
  
  // ---- Authority Delegation ----
  
  const delegateAuthority = useCallback(async (delegatorId: string, delegation: {
    delegate_id: string
    authority_type: string
    scope?: Record<string, unknown>
    constraints?: Record<string, unknown>
    max_depth?: number
  }) => {
    return fetchApi<AuthorityDelegation>(`/coherence/delegation/${delegatorId}`, {
      method: 'POST',
      body: JSON.stringify(delegation),
    })
  }, [])
  
  const invokeDelegation = useCallback(async (delegationId: string) => {
    return fetchApi<{ current_depth: number; invocation_count: number }>(`/coherence/delegation/${delegationId}/invoke`, {
      method: 'POST',
    })
  }, [])
  
  const revokeDelegation = useCallback(async (delegationId: string, reason: string) => {
    return fetchApi<AuthorityDelegation>(`/coherence/delegation/${delegationId}/revoke?reason=${encodeURIComponent(reason)}`, {
      method: 'POST',
    })
  }, [])
  
  // ---- System ----
  
  const getSystemStatus = useCallback(async () => {
    return fetchApi<CoherenceSystemStatus>('/coherence/status')
  }, [])
  
  return {
    // Identity
    createIdentity,
    getIdentity,
    getIdentityById,
    updateIdentity,
    propagateContext,
    
    // Lineage
    getLineage,
    
    // Context
    setContext,
    getContext,
    getContextsByScope,
    
    // Memory
    storeMemory,
    recallMemory,
    
    // Semantic Graphs
    createGraph,
    getGraph,
    addNode,
    addEdge,
    findPath,
    
    // Adaptive Profiles
    createProfile,
    getProfile,
    updateParameters,
    recordMetrics,
    getSuggestions,
    
    // Governance
    createPolicy,
    evaluatePolicies,
    arbitrate,
    getViolations,
    
    // Stability
    recordStability,
    assessStability,
    
    // Forecasting
    createForecast,
    getActiveForecasts,
    
    // Anomaly Detection
    detectAnomaly,
    getAnomalies,
    
    // Distributed Coordination
    createContextState,
    updateContextState,
    getContextState,
    
    // Consensus
    initiateConsensus,
    castVote,
    getConsensus,
    
    // Authority Delegation
    delegateAuthority,
    invokeDelegation,
    revokeDelegation,
    
    // System
    getSystemStatus,
  }
}