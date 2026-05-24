"""
Workspace Shell - Professional workspace layout (DaVinci Resolve style)
"""
'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import {
  GripVertical,
  ChevronLeft,
  ChevronRight,
  Maximize2,
  Minimize2,
  MoreHorizontal,
  Clock,
  Activity,
  Cpu,
  HardDrive,
} from 'lucide-react'

interface PanelProps {
  title: string
  children: React.ReactNode
  defaultWidth?: number
  minWidth?: number
  maxWidth?: number
  resizable?: boolean
  collapsible?: boolean
  icon?: React.ReactNode
}

export function Panel({
  title,
  children,
  defaultWidth = 300,
  minWidth = 200,
  maxWidth = 500,
  resizable = true,
  collapsible = true,
  icon,
}: PanelProps) {
  const [width, setWidth] = useState(defaultWidth)
  const [collapsed, setCollapsed] = useState(false)
  const [isResizing, setIsResizing] = useState(false)
  const panelRef = useRef<HTMLDivElement>(null)

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (!resizable) return
    e.preventDefault()
    setIsResizing(true)

    const startX = e.clientX
    const startWidth = width

    const handleMouseMove = (e: MouseEvent) => {
      const delta = e.clientX - startX
      const newWidth = Math.min(maxWidth, Math.max(minWidth, startWidth + delta))
      setWidth(newWidth)
    }

    const handleMouseUp = () => {
      setIsResizing(false)
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  }, [width, minWidth, maxWidth, resizable])

  if (collapsed) {
    return (
      <div className="h-full flex flex-col bg-card border-r border-border w-10">
        <div className="flex items-center justify-center h-10 border-b border-border">
          <button
            onClick={() => setCollapsed(false)}
            className="p-2 hover:bg-accent rounded"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="writing-mode-vertical" style={{ writingMode: 'vertical-rl' }}>
            {title}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div
      ref={panelRef}
      className={`h-full flex flex-col bg-card border-r border-border ${isResizing ? 'select-none' : ''}`}
      style={{ width, minWidth }}
    >
      {/* Header */}
      <div className="flex items-center h-8 px-2 border-b border-border bg-card/50">
        {resizable && (
          <div
            className="w-1 h-4 mr-2 cursor-col-resize hover:bg-primary/50 rounded"
            onMouseDown={handleMouseDown}
          />
        )}
        {icon && <span className="mr-2">{icon}</span>}
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          {title}
        </span>
        <div className="flex-1" />
        {collapsible && (
          <button
            onClick={() => setCollapsed(true)}
            className="p-1 hover:bg-accent rounded"
          >
            <ChevronLeft className="w-3 h-3" />
          </button>
        )}
        <button className="p-1 hover:bg-accent rounded">
          <MoreHorizontal className="w-3 h-3" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {children}
      </div>
    </div>
  )
}

interface StatusIndicatorProps {
  label: string
  value: string | number
  status?: 'success' | 'warning' | 'error' | 'neutral'
  icon?: React.ReactNode
}

export function StatusIndicator({
  label,
  value,
  status = 'neutral',
  icon,
}: StatusIndicatorProps) {
  const statusColors = {
    success: 'text-green-500',
    warning: 'text-yellow-500',
    error: 'text-red-500',
    neutral: 'text-muted-foreground',
  }

  return (
    <div className="flex items-center gap-2">
      {icon && <span className={statusColors[status]}>{icon}</span>}
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className={`text-sm font-medium ${statusColors[status]}`}>{value}</p>
      </div>
    </div>
  )
}

interface MetricsBarProps {
  children?: React.ReactNode
}

export function MetricsBar({ children }: MetricsBarProps) {
  return (
    <div className="flex items-center gap-6 px-4 py-2 bg-card border-b border-border">
      {children || (
        <>
          <StatusIndicator
            label="CPU"
            value="23%"
            icon={<Cpu className="w-3 h-3" />}
          />
          <StatusIndicator
            label="Memory"
            value="4.2 GB"
            icon={<HardDrive className="w-3 h-3" />}
          />
          <StatusIndicator
            label="Workers"
            value="12/16"
            icon={<Activity className="w-3 h-3" />}
          />
          <StatusIndicator
            label="Queue"
            value="47 jobs"
            icon={<Clock className="w-3 h-3" />}
          />
        </>
      )}
    </div>
  )
}

interface WorkspaceShellProps {
  leftPanel?: React.ReactNode
  rightPanel?: React.ReactNode
  mainContent?: React.ReactNode
  bottomPanel?: React.ReactNode
}

export function WorkspaceShell({
  leftPanel,
  rightPanel,
  mainContent,
  bottomPanel,
}: WorkspaceShellProps) {
  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Main area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left panels */}
        {leftPanel && <div className="flex">{leftPanel}</div>}
        
        {/* Center content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Main content */}
          <div className="flex-1 overflow-hidden">
            {mainContent}
          </div>
          
          {/* Bottom panel */}
          {bottomPanel && (
            <div className="h-48 border-t border-border bg-card">
              {bottomPanel}
            </div>
          )}
        </div>
        
        {/* Right panels */}
        {rightPanel && <div className="flex">{rightPanel}</div>}
      </div>
    </div>
  )
}