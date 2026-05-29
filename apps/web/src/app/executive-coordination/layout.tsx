/**
 * 43V3R CORE - Executive Coordination Layout
 * 
 * Layout wrapper for executive coordination pages with persistent navigation.
 */
'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Brain,
  Eye,
  Shield,
  Gauge,
  Activity,
  Layers,
  GitBranch,
  Cpu,
} from 'lucide-react'

const navigation = [
  { name: 'Control Center', href: '/executive-coordination', icon: Cpu },
  { name: 'Supervision', href: '/executive-coordination/supervision', icon: Eye },
  { name: 'Arbitration', href: '/executive-coordination/arbitration', icon: Shield },
  { name: 'Stabilization', href: '/executive-coordination/stabilization', icon: Gauge },
  { name: 'Diagnostics', href: '/executive-coordination/diagnostics', icon: Activity },
  { name: 'Coherence', href: '/executive-coordination/coherence', icon: Layers },
]

export default function ExecutiveCoordinationLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()

  return (
    <div className="h-full flex">
      {/* Sidebar Navigation */}
      <nav className="w-48 border-r border-border/50 bg-muted/30">
        <div className="p-4 border-b border-border/30">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            <span className="font-mono text-sm font-semibold">EXECUTIVE</span>
          </div>
        </div>
        <ul className="py-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={`flex items-center gap-3 px-4 py-2 text-sm ${
                    isActive
                      ? 'bg-primary/10 text-primary border-r-2 border-primary'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                  }`}
                >
                  <item.icon className="h-4 w-4" />
                  {item.name}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {children}
      </div>
    </div>
  )
}
