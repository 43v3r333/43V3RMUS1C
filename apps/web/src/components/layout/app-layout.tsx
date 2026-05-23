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

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const pathname = usePathname()

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