"""
43V3R CORE - Cognitive Design Primitives

Production-grade UI primitives for orchestration consoles, runtime panels,
and cognitive analytics. Designed for enterprise runtime intelligence software.

Patterns:
  - Console panels: tight borders, monospace data, status indicators
  - Runtime panels: compact metrics, real-time indicators
  - Telemetry: dense data, sparklines, delta indicators
  - Cognitive: semantic labels, confidence badges, state indicators
"""
'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  Activity,
  Brain,
  Cpu,
  Gauge,
  Zap,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Target,
  Award,
  Settings,
  RefreshCw,
  ChevronRight,
  ChevronDown,
  Layers,
  GitBranch,
  Server,
  HardDrive,
  Database,
  Network,
  Shield,
  Sparkles,
  Terminal,
  Eye,
} from 'lucide-react'

// ============================================================================
// STATUS INDICATORS
// ============================================================================

interface StatusDotProps {
  status: 'active' | 'idle' | 'warning' | 'error' | 'processing'
  size?: 'sm' | 'md' | 'lg'
  pulse?: boolean
}

export function StatusDot({ status, size = 'md', pulse = false }: StatusDotProps) {
  const colors = {
    active: 'bg-green-500',
    idle: 'bg-neutral-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500',
    processing: 'bg-blue-500',
  }
  const sizes = { sm: 'h-1.5 w-1.5', md: 'h-2 w-2', lg: 'h-2.5 w-2.5' }

  return (
    <span className="relative flex items-center justify-center">
      <span className={`${sizes[size]} rounded-full ${colors[status]}`} />
      {pulse && status === 'processing' && (
        <span className={`absolute ${sizes[size]} rounded-full ${colors[status]} animate-ping opacity-75`} />
      )}
    </span>
  )
}

interface ConfidenceBadgeProps {
  value: number  // 0.0 - 1.0
  showLabel?: boolean
  size?: 'sm' | 'md'
}

export function ConfidenceBadge({ value, showLabel = true, size = 'sm' }: ConfidenceBadgeProps) {
  const color = value >= 0.8 ? 'text-green-500' : value >= 0.5 ? 'text-yellow-500' : 'text-red-500'
  const label = value >= 0.8 ? 'HIGH' : value >= 0.5 ? 'MED' : 'LOW'
  const pct = `${Math.round(value * 100)}%`

  return (
    <span className={`inline-flex items-center gap-1 font-mono ${color} ${size === 'sm' ? 'text-[10px]' : 'text-xs'}`}>
      <span className="font-medium">{pct}</span>
      {showLabel && <span className="text-muted-foreground/60">{label}</span>}
    </span>
  )
}

// ============================================================================
// DATA DISPLAYS
// ============================================================================

interface MetricValueProps {
  label: string
  value: string | number
  unit?: string
  delta?: number  // positive = up, negative = down, null = no delta
  trend?: 'up' | 'down' | 'stable'
  confidence?: number
}

export function MetricValue({ label, value, unit, delta, trend, confidence }: MetricValueProps) {
  return (
    <div className="flex items-center justify-between py-1">
      <span className="text-xs text-muted-foreground uppercase tracking-wider">{label}</span>
      <div className="flex items-center gap-2">
        <span className="font-mono text-sm font-medium tabular-nums">
          {value}{unit ? <span className="text-muted-foreground text-xs ml-0.5">{unit}</span> : null}
        </span>
        {delta !== undefined && (
          <span className={`text-[10px] font-mono ${delta >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {delta >= 0 ? '+' : ''}{delta.toFixed(1)}%
          </span>
        )}
        {trend && (
          trend === 'up' ? <TrendingUp className="h-3 w-3 text-green-500" />
          : trend === 'down' ? <TrendingDown className="h-3 w-3 text-red-500" />
          : null
        )}
        {confidence !== undefined && <ConfidenceBadge value={confidence} />}
      </div>
    </div>
  )
}

interface SparklineProps {
  data: number[]
  width?: number
  height?: number
  color?: string
  className?: string
}

export function Sparkline({ data, width = 80, height = 24, color = 'var(--primary)', className = '' }: SparklineProps) {
  if (!data || data.length < 2) return <div className={className} style={{ width, height }} />

  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1

  const points = data.map((v, i) => {
    const x = (i / (data.length - 1)) * width
    const y = height - ((v - min) / range) * height
    return `${x},${y}`
  }).join(' ')

  return (
    <svg width={width} height={height} className={className}>
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
// CONSOLE PANELS
// ============================================================================

interface ConsolePanelProps {
  title: string
  subtitle?: string
  icon?: React.ReactNode
  children: React.ReactNode
  status?: 'nominal' | 'warning' | 'critical'
  actions?: React.ReactNode
  className?: string
  compact?: boolean
}

export function ConsolePanel({ title, subtitle, icon, children, status = 'nominal', actions, className = '', compact = false }: ConsolePanelProps) {
  const statusColors = {
    nominal: 'border-l-neutral-600',
    warning: 'border-l-yellow-500',
    critical: 'border-l-red-500',
  }

  return (
    <div className={`rounded border border-border bg-card overflow-hidden border-l-2 ${statusColors[status]} ${className}`}>
      {/* Header */}
      <div className={`flex items-center justify-between px-3 py-2 border-b border-border ${compact ? 'py-1.5' : ''}`}>
        <div className="flex items-center gap-2">
          {icon && <span className="text-muted-foreground">{icon}</span>}
          <div>
            <h3 className={`font-medium text-foreground ${compact ? 'text-xs' : 'text-sm'}`}>{title}</h3>
            {subtitle && <p className="text-[10px] text-muted-foreground">{subtitle}</p>}
          </div>
        </div>
        {actions && <div className="flex items-center gap-1">{actions}</div>}
      </div>
      {/* Content */}
      <div className={compact ? 'p-2' : 'p-3'}>
        {children}
      </div>
    </div>
  )
}

interface DataTableProps {
  columns: { key: string; label: string; width?: string }[]
  rows: Record<string, React.ReactNode>[]
  emptyMessage?: string
}

export function DataTable({ columns, rows, emptyMessage = 'No data' }: DataTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-border">
            {columns.map(col => (
              <th key={col.key} className="px-2 py-1.5 text-left font-medium text-muted-foreground uppercase tracking-wider" style={{ width: col.width }}>
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-2 py-4 text-center text-muted-foreground">{emptyMessage}</td>
            </tr>
          ) : rows.map((row, i) => (
            <tr key={i} className="border-b border-border/50 hover:bg-accent/50">
              {columns.map(col => (
                <td key={col.key} className="px-2 py-1.5 font-mono">{row[col.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ============================================================================
// STATE INDICATORS
// ============================================================================

interface StateIndicatorProps {
  label: string
  state: string
  type?: 'status' | 'metric' | 'count'
}

export function StateIndicator({ label, state, type = 'status' }: StateIndicatorProps) {
  const getColorClass = (state: string) => {
    const s = state.toLowerCase()
    if (s.includes('active') || s.includes('running') || s.includes('ready')) return 'text-green-500'
    if (s.includes('idle') || s.includes('waiting')) return 'text-neutral-400'
    if (s.includes('processing') || s.includes('pending')) return 'text-blue-500'
    if (s.includes('error') || s.includes('failed') || s.includes('critical')) return 'text-red-500'
    if (s.includes('warning') || s.includes('degraded')) return 'text-yellow-500'
    return 'text-muted-foreground'
  }

  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="text-muted-foreground uppercase tracking-wider">{label}</span>
      <span className={`font-medium ${getColorClass(state)}`}>{state}</span>
    </div>
  )
}

// ============================================================================
// ICON BUTTONS
// ============================================================================

interface IconButtonProps {
  icon: React.ReactNode
  onClick?: () => void
  title?: string
  variant?: 'default' | 'ghost' | 'outline'
  size?: 'sm' | 'md'
  active?: boolean
}

export function IconButton({ icon, onClick, title, variant = 'ghost', size = 'md', active = false }: IconButtonProps) {
  const variants = {
    default: 'bg-primary/10 text-primary hover:bg-primary/20',
    ghost: 'hover:bg-accent text-muted-foreground hover:text-foreground',
    outline: 'border border-border hover:bg-accent text-muted-foreground hover:text-foreground',
  }
  const sizes = { sm: 'h-7 w-7', md: 'h-8 w-8' }
  const activeClasses = active ? 'bg-primary/10 text-primary' : ''

  return (
    <button
      onClick={onClick}
      title={title}
      className={`flex items-center justify-center rounded ${variants[variant]} ${sizes[size]} ${activeClasses} transition-colors`}
    >
      {icon}
    </button>
  )
}

// ============================================================================
// PROGRESS / LOADING
// ============================================================================

interface ProgressBarProps {
  value: number  // 0-100
  label?: string
  showValue?: boolean
  color?: 'primary' | 'success' | 'warning' | 'error'
}

export function ProgressBar({ value, label, showValue = false, color = 'primary' }: ProgressBarProps) {
  const colors = {
    primary: 'bg-primary',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500',
  }

  return (
    <div className="w-full">
      {(label || showValue) && (
        <div className="flex items-center justify-between mb-1">
          {label && <span className="text-[10px] text-muted-foreground">{label}</span>}
          {showValue && <span className="text-[10px] font-mono">{Math.round(value)}%</span>}
        </div>
      )}
      <div className="h-1 w-full bg-muted rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all ${colors[color]}`} style={{ width: `${Math.min(100, Math.max(0, value))}%` }} />
      </div>
    </div>
  )
}

// ============================================================================
// TABS
// ============================================================================

interface TabProps {
  tabs: { id: string; label: string; icon?: React.ReactNode; badge?: number }[]
  active: string
  onChange: (id: string) => void
}

export function TabBar({ tabs, active, onChange }: TabProps) {
  return (
    <div className="flex items-center gap-0.5 border-b border-border">
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium transition-colors relative ${
            active === tab.id
              ? 'text-foreground'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          {tab.icon}
          {tab.label}
          {tab.badge !== undefined && (
            <span className={`ml-1 px-1.5 py-0.5 rounded text-[10px] ${active === tab.id ? 'bg-primary/20 text-primary' : 'bg-muted text-muted-foreground'}`}>
              {tab.badge}
            </span>
          )}
          {active === tab.id && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
          )}
        </button>
      ))}
    </div>
  )
}

// ============================================================================
// COLLAPSE / EXPAND
// ============================================================================

interface CollapsibleSectionProps {
  title: string
  icon?: React.ReactNode
  defaultOpen?: boolean
  children: React.ReactNode
  badge?: string
}

export function CollapsibleSection({ title, icon, defaultOpen = true, children, badge }: CollapsibleSectionProps) {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <div className="border-b border-border">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center justify-between w-full px-3 py-2 hover:bg-accent/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          {icon && <span className="text-muted-foreground">{icon}</span>}
          <span className="text-xs font-medium">{title}</span>
          {badge && <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground">{badge}</span>}
        </div>
        {open ? <ChevronDown className="h-3 w-3 text-muted-foreground" /> : <ChevronRight className="h-3 w-3 text-muted-foreground" />}
      </button>
      {open && <div className="px-3 pb-3">{children}</div>}
    </div>
  )
}

// ============================================================================
// GRID / LAYOUT
// ============================================================================

interface MetricGridProps {
  items: { label: string; value: string | number; unit?: string; icon?: React.ReactNode; color?: string }[]
  columns?: number
}

export function MetricGrid({ items, columns = 4 }: MetricGridProps) {
  return (
    <div className={`grid gap-2`} style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
      {items.map((item, i) => (
        <div key={i} className="rounded border border-border bg-card p-2">
          <div className="flex items-center gap-1.5 mb-1">
            {item.icon && <span className={item.color || 'text-muted-foreground'}>{item.icon}</span>}
            <span className="text-[10px] text-muted-foreground uppercase tracking-wider">{item.label}</span>
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-lg font-mono font-semibold">{item.value}</span>
            {item.unit && <span className="text-xs text-muted-foreground">{item.unit}</span>}
          </div>
        </div>
      ))}
    </div>
  )
}

// ============================================================================
// ICON LIBRARY
// ============================================================================

export const CognitiveIcons = {
  Reasoning: <Brain className="h-4 w-4" />,
  Memory: <Database className="h-4 w-4" />,
  Forecast: <TrendingUp className="h-4 w-4" />,
  Governance: <Shield className="h-4 w-4" />,
  Feedback: <RefreshCw className="h-4 w-4" />,
  Optimization: <Zap className="h-4 w-4" />,
  Agent: <Server className="h-4 w-4" />,
  Prediction: <Target className="h-4 w-4" />,
  Activity: <Activity className="h-4 w-4" />,
  Cpu: <Cpu className="h-4 w-4" />,
  Network: <Network className="h-4 w-4" />,
  Terminal: <Terminal className="h-4 w-4" />,
  Eye: <Eye className="h-4 w-4" />,
  Layers: <Layers className="h-4 w-4" />,
  Sparkles: <Sparkles className="h-4 w-4" />,
  GitBranch: <GitBranch className="h-4 w-4" />,
  Gauge: <Gauge className="h-4 w-4" />,
}