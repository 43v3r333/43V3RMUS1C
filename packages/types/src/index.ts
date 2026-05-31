// Shared type definitions for 43V3R CORE

export interface BaseEntity {
  id: string
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

export interface PaginationParams {
  page?: number
  per_page?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  has_more: boolean
}

export interface ApiError {
  detail: string
  code?: string
  field?: string
}

export type Status = 'pending' | 'active' | 'inactive' | 'deleted'
export type AssetType = 'audio' | 'video' | 'image' | 'document'
export type ProjectStatus = 'draft' | 'in_progress' | 'completed' | 'archived'
export type RenderJobStatus = 'pending' | 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled'
export type RenderJobPriority = 'low' | 'normal' | 'high' | 'urgent'
export type CampaignStatus = 'draft' | 'scheduled' | 'active' | 'paused' | 'completed'

export interface TimeStamped {
  created_at: string
  updated_at: string
}

export interface SoftDeletable extends TimeStamped {
  deleted_at?: string | null
}

export interface UserBrief {
  id: string
  username: string
  email: string
}

export interface ArtistBrief {
  id: string
  name: string
  slug: string
}

export interface ProjectBrief {
  id: string
  name: string
}

export interface MediaAssetBrief {
  id: string
  name: string
  asset_type: AssetType
}

export interface TrackBrief {
  id: string
  title: string
  artist_name?: string
}

export interface WorkflowBrief {
  id: string
  name: string
  workflow_type: string
}

export interface CampaignBrief {
  id: string
  name: string
  status: CampaignStatus
}

// Event types for analytics
export type EventType = 'page_view' | 'click' | 'form_submit' | 'render_complete' | 'upload' | 'download' | 'api_call'

export interface AnalyticsEvent {
  id: string
  event_type: EventType
  event_name: string
  user_id?: string
  session_id?: string
  properties?: Record<string, unknown>
  traits?: Record<string, unknown>
  ip_address?: string
  user_agent?: string
  timestamp: string
}

// Platform integration types
export type Platform = 'spotify' | 'apple_music' | 'youtube' | 'soundcloud' | 'instagram' | 'tiktok' | 'twitter' | 'facebook'

export interface SocialMetrics {
  followers?: number
  following?: number
  posts?: number
  engagement_rate?: number
}

export interface PlatformCredentials {
  access_token: string
  refresh_token?: string
  expires_at?: string
  token_type?: string
}

// Media processing types
export interface MediaMetadata {
  duration?: number
  width?: number
  height?: number
  bitrate?: number
  codec?: string
  sample_rate?: number
  channels?: number
}

export interface RenderParameters {
  format: string
  quality: 'low' | 'medium' | 'high' | 'ultra'
  codec?: string
  bitrate?: number
  resolution?: string
}

export interface GenerationParameters {
  model?: string
  style?: string
  seed?: number
  steps?: number
  guidance_scale?: number
}

export interface WorkflowDefinition {
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
}

export interface WorkflowNode {
  id: string
  type: string
  position: { x: number; y: number }
  data: Record<string, unknown>
}

export interface WorkflowEdge {
  id: string
  source: string
  target: string
  label?: string
}

// =============================================================================
// Executive Coordination Types
// =============================================================================

// Enums
export type SupervisionLevel = 'surface' | 'observer' | 'advisor' | 'reviewer' | 'coordinator' | 'governor' | 'master'
export type SupervisionState = 'pending' | 'active' | 'paused' | 'recovering' | 'stabilized' | 'completed' | 'failed' | 'escalated'
export type ArbitrationScope = 'atomic' | 'composite' | 'semantic' | 'governor' | 'systemic'
export type ArbitrationState = 'detected' | 'evaluating' | 'arbitrating' | 'resolving' | 'reconciled' | 'escalated' | 'dismissed'
export type StabilizationTier = 'tier_0_healthy' | 'tier_1_marginal' | 'tier_2_degrading' | 'tier_3_unstable' | 'tier_4_critical' | 'tier_5_collapse'
export type StabilizationAction = 'monitor' | 'balance' | 'restrict' | 'isolate' | 'rollback' | 'reset' | 'emergency'
export type CoordinationTopology = 'hierarchical' | 'mesh' | 'federated' | 'hybrid' | 'adaptive'
export type CoordinationState = 'disconnected' | 'syncing' | 'synchronized' | 'conflicting' | 'coherent'
export type CoherenceMetric = 'semantic' | 'execution' | 'governance' | 'orchestration' | 'distribution' | 'temporal'
export type BalanceStrategy = 'equalize' | 'prioritize' | 'weight' | 'distribute' | 'consolidate'
export type DiagnosticsHorizon = 'instantaneous' | 'near' | 'short' | 'medium' | 'long'
export type AnomalySeverity = 'info' | 'notice' | 'warning' | 'error' | 'critical' | 'emergency'
export type ReconciliationState = 'aligned' | 'deviating' | 'conflicting' | 'reconciling' | 'balanced'

// Recursive Supervision
export interface SupervisionSession {
  id: string
  session_key: string
  supervisor_id: string
  scope: string
  supervision_level: number
  parent_session_id?: string
  root_session_id?: string
  recursion_depth: number
  target_id: string
  target_type: string
  target_snapshot: Record<string, unknown>
  supervision_state: SupervisionState
  confidence_score: number
  findings?: SupervisionFinding[]
  recommendations?: string[]
  violations?: PolicyViolation[]
  metrics_evaluated: number
  issues_detected: number
  escalated: boolean
  escalated_at?: string
  escalated_to?: string
  started_at: string
  completed_at?: string
  duration_ms?: number
  correlation_id?: string
}

export interface SupervisionFinding {
  finding_id: string
  category: string
  severity: AnomalySeverity
  description: string
  evidence: Record<string, unknown>
  recommendation?: string
  confidence: number
}

export interface SupervisionArtifact {
  id: string
  artifact_key: string
  artifact_type: string
  scope: string
  title: string
  content: Record<string, unknown>
  importance: number
  confidence: number
  state: string
  access_count: number
  created_at: string
}

// Orchestration Arbitration
export interface ArbitrationState {
  id: string
  arbitration_key: string
  scope: string
  arbitration_scope: ArbitrationScope
  priority: number
  arbitration_state: ArbitrationState
  parties: string[]
  party_count: number
  conflict_type: string
  conflict_description?: string
  conflicting_claims: ConflictingClaim[]
  resolution_strategy?: string
  winning_party?: string
  merge_output?: Record<string, unknown>
  negotiation_rounds: number
  escalation_required: boolean
  detected_at: string
  resolved_at?: string
  resolution_time_ms?: number
}

export interface ConflictingClaim {
  party: string
  priority: number
  score: number
  data: Record<string, unknown>
}

export interface ArbitrationPolicy {
  id: string
  policy_key: string
  name: string
  scope: string
  strategy: string
  priority: number
  max_rounds: number
  timeout_ms: number
  escalation_threshold: number
  is_active: boolean
  invocation_count: number
  success_count: number
}

// Stabilization Hierarchy
export interface StabilizationProfile {
  id: string
  profile_key: string
  name: string
  scope: string
  tier: StabilizationTier
  priority: number
  parent_profile_id?: string
  child_profile_ids: string[]
  hierarchy_depth: number
  state: string
  thresholds: Record<string, number>
  recovery_strategy: StabilizationAction
  activation_count: number
  success_count: number
  last_activated?: string
}

export interface StabilizationEvent {
  id: string
  event_key: string
  profile_id: string
  target_id: string
  target_type: string
  tier_before: StabilizationTier
  tier_after: StabilizationTier
  action: StabilizationAction
  success: boolean
  coherence_score_before: number
  coherence_score_after: number
  detected_at: string
  duration_ms?: number
}

// Coordination Topology
export interface CoordinationTopology {
  id: string
  topology_key: string
  name: string
  scope: string
  topology_type: CoordinationTopology
  nodes: TopologyNode[]
  edges: TopologyEdge[]
  node_count: number
  edge_count: number
  coordinator_ids: string[]
  primary_coordinator_id?: string
  topology_state: CoordinationState
  coherence_score: number
  message_throughput: number
  sync_latency_ms: number
  conflict_rate: number
  created_at: string
  last_sync?: string
}

export interface TopologyNode {
  node_id: string
  node_type: string
  capabilities: string[]
  metadata: Record<string, unknown>
}

export interface TopologyEdge {
  source_id: string
  target_id: string
  edge_type: string
  bandwidth: number
}

export interface CoordinationEdge {
  id: string
  edge_key: string
  source_id: string
  target_id: string
  edge_type: string
  is_active: boolean
  message_count: number
  last_message_at?: string
}

// Diagnostics
export interface DiagnosticsForecast {
  id: string
  forecast_key: string
  target_id: string
  target_type: string
  scope: string
  forecast_kind: string
  horizon: DiagnosticsHorizon
  predicted_value: number
  confidence: number
  probability: number
  severity: AnomalySeverity
  risk_level: 'low' | 'medium' | 'high' | 'critical'
  recommended_actions?: string[]
  indicators?: ForecastIndicator[]
  validated: boolean
  generated_at: string
  predicted_for: string
}

export interface ForecastIndicator {
  value: number
  weight: number
  confidence: number
  source?: string
}

export interface AnomalyDetection {
  id: string
  anomaly_key: string
  target_id: string
  target_type: string
  anomaly_type: string
  severity: AnomalySeverity
  scope: string
  affected_components: string[]
  cascade_risk: number
  baseline: Record<string, number>
  observed: Record<string, number>
  deviation: number
  status: string
  resolved: boolean
  detected_at: string
}

export interface PolicyViolation {
  finding_id: string
  severity: string
  description: string
}

// Balancing
export interface HierarchyBalancing {
  id: string
  balancing_key: string
  scope: string
  balance_strategy: BalanceStrategy
  balance_score_before: number
  balance_score_after: number
  nodes: string[]
  node_weights?: Record<string, number>
  improvement_score: number
  timestamp: string
}

// Reconciliation
export interface ReconciliationMetrics {
  id: string
  metrics_key: string
  scope: string
  reconciliation_state: ReconciliationState
  policy_alignment_score: number
  semantic_alignment_score: number
  execution_alignment_score: number
  deviation_detected: boolean
  deviation_magnitude: number
  conflicts_detected: number
  policies_violated: number
  policies_corrected: number
  timestamp: string
}

// Coherence Lineage
export interface CoherenceLineage {
  id: string
  lineage_key: string
  scope: string
  coherence_metric: CoherenceMetric
  source_id: string
  source_type: string
  coherence_value: number
  coherence_trend: 'stable' | 'improving' | 'declining' | 'critical'
  event_type: string
  event_description?: string
  chain_id: string
  chain_position: number
  timestamp: string
}

// Executive Overview
export interface ExecutiveOverview {
  active_supervision_sessions: number
  active_arbitrations: number
  stabilization_profiles: number
  coordination_topologies: number
  active_forecasts: number
  active_anomalies: number
  overall_coherence_score: number
  system_health: 'healthy' | 'stable' | 'degraded' | 'unstable' | 'critical'
}