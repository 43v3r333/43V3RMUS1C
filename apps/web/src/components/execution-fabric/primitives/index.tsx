"""
Execution Fabric Primitives - UI primitives for orchestration consoles.

Production-grade primitives for:
- Event topology interfaces
- Runtime lineage visualization
- Distributed cognition panels
- Self-healing monitors
- Predictive analytics
- Semantic execution graphs
"""
'use client'

import React, { useState, useEffect } from 'react'
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Brain,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Circle,
  Clock,
  Cpu,
  Database,
  Download,
  Eye,
  GitBranch,
  Globe,
  Gauge,
  HardDrive,
  Layers,
  LineChart,
  Link2,
  List,
  Loader2,
  Map,
  Maximize2,
  Minus,
  Network,
  Plus,
  RefreshCw,
  Scalable,
  Server,
  Settings,
  Shield,
  Signal,
  Sparkles,
  Thermometer,
  Timer,
  ToggleLeft,
  ToggleRight,
  TrendingDown,
  TrendingUp,
  Workflow,
  X,
  Zap,
} from 'lucide-react'

// ============================================================================
// EXECUTION FABRIC PRIMITIVES
// ============================================================================

export interface FabricStatus {
  status: 'nominal' | 'degraded' | 'critical' | 'unknown'
  indicator?: 'active' | 'idle' | 'warning' | 'error' | 'processing'
  lastUpdate?: string
}

interface TopologyNodeProps {
  id: string
  label: string
  type?: 'service' | 'worker' | 'orchestrator' | 'storage' | 'network'
  status: FabricStatus
  position?: { x: number; y: number }
  onSelect?: (id: string) => void
}

export function TopologyNode({ id, label, type = 'service', status, onSelect }: TopologyNodeProps) {
  const statusColors = {
    nominal: 'border-green-500 bg-green-500/10',
    degraded: 'border-yellow-500 bg-yellow-500/10',
    critical: 'border-red-500 bg-red-500/10',
    unknown: 'border-neutral-500 bg-neutral-500/10',
  }

  const statusDots = {
    active: 'bg-green-500',
    idle: 'bg-neutral-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500',
    processing: 'bg-blue-500',
  }

  const TypeIcon = {
    service: <Server className="h-4 w-4" />,
    worker: <Cpu className="h-4 w-4" />,
    orchestrator: <Workflow className="h-4 w-4" />,
    storage: <Database className="h-4 w-4" />,
    network: <Network className="h-4 w-4" />,
  }

  return (
    <div
      className={`
        flex items-center gap-2 px-3 py-2 rounded border cursor-pointer
        transition-all hover:shadow-md
        ${statusColors[status.status]}
      `}
      onClick={() => onSelect?.(id)}
    >
      <div className="flex items-center gap-1.5">
        <span className="text-muted-foreground">{TypeIcon[type]}</span>
        {status.indicator && (
          <span className={`h-2 w-2 rounded-full ${statusDots[status.indicator]} animate-pulse`} />
        )}
      </div>
      <div>
        <span className="text-xs font-mono font-medium">{label}</span>
        <span className="text-[10px] text-muted-foreground ml-2">{type}</span>
      </div>
    </div>
  )
}

interface TopologyEdgeProps {
  source: string
  target: string
  type?: 'dependency' | 'data_flow' | 'control_flow' | 'event'
  weight?: number
}

export function TopologyEdge({ source, target, type = 'dependency', weight }: TopologyEdgeProps) {
  const edgeStyles = {
    dependency: { stroke: 'stroke-neutral-500', dash: '' },
    data_flow: { stroke: 'stroke-blue-500', dash: '5,5' },
    control_flow: { stroke: 'stroke-purple-500', dash: '' },
    event: { stroke: 'stroke-green-500', dash: '2,2' },
  }

  return (
    <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
      <span className="font-mono">{source}</span>
      <ArrowRight className="h-3 w-3" />
      <span className="font-mono">{target}</span>
      <span className={`ml-1 px-1 rounded ${edgeStyles[type].stroke.replace('stroke-', 'bg-')}`}>
        {type}
      </span>
      {weight !== undefined && (
        <span className="ml-1 font-mono opacity-60">{weight.toFixed(2)}</span>
      )}
    </div>
  )
}

// ============================================================================
// LINEAGE TRACKER
// ============================================================================

interface LineageNodeProps {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
  depth: number
  duration?: number
  onClick?: (id: string) => void
}

export function LineageNode({ id, name, status, depth, duration, onClick }: LineageNodeProps) {
  const statusConfig = {
    pending: { color: 'border-neutral-500 bg-neutral-500/5', text: 'text-neutral-500' },
    running: { color: 'border-blue-500 bg-blue-500/10', text: 'text-blue-500' },
    completed: { color: 'border-green-500 bg-green-500/10', text: 'text-green-500' },
    failed: { color: 'border-red-500 bg-red-500/10', text: 'text-red-500' },
    skipped: { color: 'border-yellow-500 bg-yellow-500/10', text: 'text-yellow-500' },
  }

  const config = statusConfig[status]

  return (
    <div
      className={`
        flex items-center gap-3 px-4 py-2 rounded border-l-2 cursor-pointer
        hover:bg-accent/50 transition-colors
        ${config.color}
      `}
      style={{ marginLeft: depth * 20 }}
      onClick={() => onClick?.(id)}
    >
      <div className={`flex items-center gap-2 ${config.text}`}>
        {status === 'running' ? (
          <Loader2 className="h-3 w-3 animate-spin" />
        ) : status === 'completed' ? (
          <CheckCircle2 className="h-3 w-3" />
        ) : status === 'failed' ? (
          <X className="h-3 w-3" />
        ) : (
          <Circle className="h-3 w-3" />
        )}
        <span className="text-xs font-mono">{id}</span>
      </div>
      <span className="text-xs">{name}</span>
      {duration !== undefined && (
        <span className="text-[10px] font-mono text-muted-foreground ml-auto">
          {duration.toFixed(1)}ms
        </span>
      )}
    </div>
  )
}

// ============================================================================
// METRIC DISPLAYS
// ============================================================================

interface MetricCardProps {
  label: string
  value: string | number
  unit?: string
  trend?: 'up' | 'down' | 'stable'
  delta?: number
  status?: 'nominal' | 'warning' | 'critical'
  sparkline?: number[]
}

export function MetricCard({ label, value, unit, trend, delta, status = 'nominal', sparkline }: MetricCardProps) {
  const statusColors = {
    nominal: 'border-l-neutral-600',
    warning: 'border-l-yellow-500',
    critical: 'border-l-red-500',
  }

  return (
    <div className={`rounded border border-border bg-card border-l-2 ${statusColors[status]} p-3`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] text-muted-foreground uppercase tracking-wider">{label}</span>
        {trend && (
          trend === 'up' ? <TrendingUp className="h-3 w-3 text-green-500" />
          : trend === 'down' ? <TrendingDown className="h-3 w-3 text-red-500" />
          : <Minus className="h-3 w-3 text-muted-foreground" />
        )}
      </div>
      <div className="flex items-baseline gap-1">
        <span className="text-xl font-mono font-semibold">{value}</span>
        {unit && <span className="text-xs text-muted-foreground">{unit}</span>}
        {delta !== undefined && (
          <span className={`text-[10px] font-mono ml-2 ${delta >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {delta >= 0 ? '+' : ''}{delta.toFixed(1)}%
          </span>
        )}
      </div>
      {sparkline && sparkline.length > 2 && (
        <div className="mt-2 h-8">
          <SparklineChart data={sparkline} color={status === 'critical' ? '#ef4444' : '#22c55e'} />
        </div>
      )}
    </div>
  )
}

interface SparklineChartProps {
  data: number[]
  color?: string
  height?: number
}

export function SparklineChart({ data, color = '#22c55e', height = 32 }: SparklineChartProps) {
  if (data.length < 2) return null

  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  const width = 100

  const points = data.map((v, i) => {
    const x = (i / (data.length - 1)) * width
    const y = height - ((v - min) / range) * height
    return `${x},${y}`
  }).join(' ')

  return (
    <svg width="100%" height={height} className="overflow-visible">
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  )
}

// ============================================================================
// PROGRESS INDICATORS
// ============================================================================

interface ExecutionProgressProps {
  current: number
  total: number
  label?: string
  showPercentage?: boolean
}

export function ExecutionProgress({ current, total, label, showPercentage = true }: ExecutionProgressProps) {
  const percentage = total > 0 ? (current / total) * 100 : 0

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-[10px]">
        {label && <span className="text-muted-foreground">{label}</span>}
        {showPercentage && (
          <span className="font-mono">{Math.round(percentage)}%</span>
        )}
      </div>
      <div className="h-1.5 bg-muted rounded-full overflow-hidden">
        <div
          className="h-full bg-primary transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
        <span>{current}</span>
        <span>/</span>
        <span>{total}</span>
      </div>
    </div>
  )
}

// ============================================================================
// TOPOLOGY GRID
// ============================================================================

interface TopologyGridProps {
  nodes: TopologyNodeProps[]
  edges: TopologyEdgeProps[]
  onNodeSelect?: (id: string) => void
}

export function TopologyGrid({ nodes, edges, onNodeSelect }: TopologyGridProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
        {nodes.map(node => (
          <TopologyNode key={node.id} {...node} onSelect={onNodeSelect} />
        ))}
      </div>
      {edges.length > 0 && (
        <div className="border-t border-border pt-4">
          <div className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2">
            Connections
          </div>
          <div className="space-y-1">
            {edges.slice(0, 10).map((edge, i) => (
              <TopologyEdge key={i} {...edge} />
            ))}
            {edges.length > 10 && (
              <div className="text-[10px] text-muted-foreground">
                +{edges.length - 10} more connections
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// ============================================================================
// STATUS BARS
// ============================================================================

interface StatusBarProps {
  segments: { label: string; value: number; color?: string }[]
  showLabels?: boolean
}

export function StatusBar({ segments, showLabels = true }: StatusBarProps) {
  const total = segments.reduce((sum, s) => sum + s.value, 0)

  return (
    <div className="space-y-2">
      <div className="flex h-2 rounded-full overflow-hidden bg-muted">
        {segments.map((segment, i) => (
          <div
            key={i}
            className={segment.color || 'bg-primary'}
            style={{ width: `${total > 0 ? (segment.value / total) * 100 : 0}%` }}
            title={`${segment.label}: ${segment.value}`}
          />
        ))}
      </div>
      {showLabels && (
        <div className="flex flex-wrap gap-2">
          {segments.map((segment, i) => (
            <div key={i} className="flex items-center gap-1 text-[10px]">
              <span className={`h-2 w-2 rounded-full ${segment.color || 'bg-primary'}`} />
              <span className="text-muted-foreground">{segment.label}</span>
              <span className="font-mono">{segment.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ============================================================================
// ANOMALY CARDS
// ============================================================================

interface AnomalyCardProps {
  title: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  description?: string
  target?: string
  detectedAt?: string
  onResolve?: () => void
}

export function AnomalyCard({ title, severity, description, target, detectedAt, onResolve }: AnomalyCardProps) {
  const severityConfig = {
    info: { border: 'border-blue-500', bg: 'bg-blue-500/10', icon: <AlertTriangle className="h-4 w-4 text-blue-500" /> },
    warning: { border: 'border-yellow-500', bg: 'bg-yellow-500/10', icon: <AlertTriangle className="h-4 w-4 text-yellow-500" /> },
    error: { border: 'border-red-500', bg: 'bg-red-500/10', icon: <X className="h-4 w-4 text-red-500" /> },
    critical: { border: 'border-red-600', bg: 'bg-red-600/20', icon: <X className="h-4 w-4 text-red-600 animate-pulse" /> },
  }

  const config = severityConfig[severity]

  return (
    <div className={`rounded border border-l-4 ${config.border} ${config.bg} p-3`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-2">
          {config.icon}
          <div>
            <div className="text-sm font-medium">{title}</div>
            {description && <div className="text-xs text-muted-foreground mt-1">{description}</div>}
            {target && <div className="text-[10px] font-mono text-muted-foreground mt-1">Target: {target}</div>}
            {detectedAt && <div className="text-[10px] text-muted-foreground mt-1">Detected: {detectedAt}</div>}
          </div>
        </div>
        {onResolve && (
          <button
            onClick={onResolve}
            className="text-[10px] px-2 py-1 rounded border border-border hover:bg-accent"
          >
            Resolve
          </button>
        )}
      </div>
    </div>
  )
}

// ============================================================================
// ICON LIBRARY
// ============================================================================

export const ExecutionFabricIcons = {
  Topology: <Map className="h-4 w-4" />,
  Lineage: <GitBranch className="h-4 w-4" />,
  Cognition: <Brain className="h-4 w-4" />,
  Stability: <Gauge className="h-4 w-4" />,
  Semantic: <Layers className="h-4 w-4" />,
  Analytics: <LineChart className="h-4 w-4" />,
  Execution: <Workflow className="h-4 w-4" />,
  Monitor: <Eye className="h-4 w-4" />,
  Recovery: <RefreshCw className="h-4 w-4" />,
  Prediction: <TrendingUp className="h-4 w-4" />,
  Health: <Activity className="h-4 w-4" />,
  Graph: <Network className="h-4 w-4" />,
  Node: <Circle className="h-4 w-4" />,
  Link: <Link2 className="h-4 w-4" />,
  Stream: <Signal className="h-4 w-4" />,
  Memory: <Database className="h-4 w-4" />,
}

// ============================================================================
// RE-EXPORTS FROM COGNITIVE PRIMITIVES
// ============================================================================

export { StatusDot, ConfidenceBadge, ConsolePanel, DataTable, ProgressBar, TabBar, MetricValue, Sparkline } from '../cognitive/primitives'