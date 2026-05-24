'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  Image,
  FolderKanban,
  Layers,
  BarChart3,
  Sparkles,
  Settings,
  ChevronLeft,
  ChevronRight,
  Play,
  Brain,
  Network,
  TrendingUp,
  Gauge,
  Shield,
  Zap,
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Media Library', href: '/media', icon: Image },
  { name: 'Projects', href: '/projects', icon: FolderKanban },
  { name: 'Render Queue', href: '/queue', icon: Play },
  { name: 'Workflows', href: '/workflows', icon: Layers },
  { name: 'Prompts', href: '/prompts', icon: Sparkles },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
]

const cognitiveNavigation = [
  { name: 'Cognitive Operating Center', href: '/cognitive', icon: Brain },
  { name: 'Knowledge Graph', href: '/cognitive/graph', icon: Network },
  { name: 'Predictive Console', href: '/cognitive/predictive', icon: TrendingUp },
  { name: 'Creative Monitor', href: '/cognitive/creative', icon: Sparkles },
  { name: 'Governance', href: '/cognitive/governance', icon: Shield },
  { name: 'Optimization', href: '/cognitive/optimization', icon: Gauge },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const pathname = usePathname()

  // Check if we're in the cognitive section
  const isCognitive = pathname.startsWith('/cognitive')
  const [cognitiveExpanded, setCognitiveExpanded] = useState(isCognitive)

  return (
    <aside
      className={`relative flex h-screen flex-col border-r border-border bg-card transition-all duration-300 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Logo */}
      <div className="flex h-14 items-center border-b border-border px-4">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary">
            <span className="text-sm font-bold text-primary-foreground">V3</span>
          </div>
          {!collapsed && (
            <span className="font-semibold tracking-tight">43V3R CORE</span>
          )}
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-2">
        {/* Main navigation */}
        <ul className="space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
            const Icon = item.icon

            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-primary/10 text-primary'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                  }`}
                >
                  <Icon className="h-4 w-4 flex-shrink-0" />
                  {!collapsed && <span>{item.name}</span>}
                </Link>
              </li>
            )
          })}
        </ul>

        {/* Cognitive section */}
        {!collapsed && (
          <div className="mt-4">
            <button
              onClick={() => setCognitiveExpanded(!cognitiveExpanded)}
              className="flex items-center gap-2 w-full px-3 py-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground hover:text-foreground"
            >
              <Brain className="h-3.5 w-3.5" />
              <span>Cognitive Core</span>
              {cognitiveExpanded ? (
                <ChevronLeft className="h-3 w-3 ml-auto" />
              ) : (
                <ChevronRight className="h-3 w-3 ml-auto" />
              )}
            </button>

            {cognitiveExpanded && (
              <ul className="mt-1 space-y-0.5">
                {cognitiveNavigation.map((item) => {
                  const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
                  const Icon = item.icon

                  return (
                    <li key={item.name}>
                      <Link
                        href={item.href}
                        className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                          isActive
                            ? 'bg-primary/10 text-primary'
                            : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                        }`}
                      >
                        <Icon className="h-4 w-4 flex-shrink-0" />
                        <span>{item.name}</span>
                      </Link>
                    </li>
                  )
                })}
              </ul>
            )}
          </div>
        )}

        {collapsed && (
          <div className="mt-4 pt-4 border-t border-border">
            <div className="flex flex-col items-center gap-1">
              <Brain className="h-4 w-4 text-muted-foreground" />
              {cognitiveNavigation.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`flex h-8 w-8 items-center justify-center rounded-md transition-colors ${
                      isActive ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                    }`}
                    title={item.name}
                  >
                    <Icon className="h-4 w-4" />
                  </Link>
                )
              })}
            </div>
          </div>
        )}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-20 flex h-6 w-6 items-center justify-center rounded-full border border-border bg-background hover:bg-accent"
      >
        {collapsed ? (
          <ChevronRight className="h-3 w-3" />
        ) : (
          <ChevronLeft className="h-3 w-3" />
        )}
      </button>
    </aside>
  )
}

export function Header() {
  return (
    <header className="flex h-14 items-center border-b border-border bg-card px-6">
      <div className="flex flex-1 items-center gap-4">
        {/* Search */}
        <div className="relative w-96">
          <input
            type="text"
            placeholder="Search..."
            className="h-9 w-full rounded-md border border-input bg-background pl-9 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>
      </div>
      <div className="flex items-center gap-4">
        {/* Status indicator */}
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-green-500" />
          <span className="text-xs text-muted-foreground">System Online</span>
        </div>
      </div>
    </header>
  )
}

export default function AppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto bg-background p-6">
          {children}
        </main>
      </div>
    </div>
  )
}