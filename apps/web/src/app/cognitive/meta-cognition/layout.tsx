/**
 * Meta-Cognition Layout
 * Executive Intelligence Layer navigation and layout.
 */
'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Brain,
  Eye,
  GitBranch,
  Shield,
  AlertTriangle,
  TrendingUp,
  Network,
  ChevronRight,
} from 'lucide-react'

const navigation = [
  {
    title: 'Overview',
    href: '/cognitive/meta-cognition',
    icon: Brain,
    description: 'Meta-cognition control center',
  },
  {
    title: 'Runtime Self-Awareness',
    href: '/cognitive/meta-cognition/runtime-self-awareness',
    icon: Eye,
    description: 'Behavior analysis and introspection',
  },
  {
    title: 'Orchestration Introspection',
    href: '/cognitive/meta-cognition/orchestration-introspection',
    icon: GitBranch,
    description: 'Reasoning analysis and lineage',
  },
  {
    title: 'Semantic Consistency',
    href: '/cognitive/meta-cognition/semantic-consistency',
    icon: Shield,
    description: 'Validation and consistency auditing',
  },
  {
    title: 'Cognitive Reconciliation',
    href: '/cognitive/meta-cognition/cognitive-reconciliation',
    icon: Network,
    description: 'Distributed sync and conflicts',
  },
  {
    title: 'Predictive Cognition',
    href: '/cognitive/meta-cognition/predictive-cognition',
    icon: TrendingUp,
    description: 'Cognition drift forecasting',
  },
  {
    title: 'Distributed Governance',
    href: '/cognitive/meta-cognition/distributed-governance',
    icon: AlertTriangle,
    description: 'Multi-node governance and policies',
  },
]

export default function MetaCognitionLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()

  return (
    <div className="flex h-full">
      {/* Sidebar Navigation */}
      <aside className="w-56 border-r border-border bg-card flex flex-col">
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            <span className="text-sm font-semibold">Meta-Cognition</span>
          </div>
          <p className="text-[10px] text-muted-foreground mt-1">Executive Intelligence Layer</p>
        </div>

        <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            const Icon = item.icon

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 px-3 py-2 rounded text-xs transition-colors ${
                  isActive
                    ? 'bg-primary/10 text-primary border border-primary/20'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                }`}
              >
                <Icon className="h-4 w-4 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{item.title}</div>
                  <div className="text-[10px] text-muted-foreground truncate hidden group-hover:block">
                    {item.description}
                  </div>
                </div>
                {isActive && <ChevronRight className="h-3 w-3 flex-shrink-0" />}
              </Link>
            )
          })}
        </nav>

        <div className="p-3 border-t border-border">
          <div className="text-[10px] text-muted-foreground">
            <div>43V3R CORE v2.0</div>
            <div>Executive Intelligence</div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto p-4">
        {children}
      </main>
    </div>
  )
}
