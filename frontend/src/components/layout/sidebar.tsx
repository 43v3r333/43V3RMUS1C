"""
Sidebar navigation component
"""
"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import {
  LayoutDashboard,
  FolderOpen,
  Layers,
  Cpu,
  PlayCircle,
  BarChart3,
  Palette,
  Share2,
  MessageSquare,
  Settings,
  ChevronLeft,
  ChevronRight,
  Activity,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from "@/components/ui/tooltip"
import { Separator } from "@/components/ui/separator"

interface NavItem {
  label: string
  href: string
  icon: React.ElementType
  badge?: string
}

const mainNav: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Media Library", href: "/media", icon: FolderOpen },
  { label: "Projects", href: "/projects", icon: Layers },
  { label: "AI Agents", href: "/agents", icon: Cpu },
  { label: "Render Queue", href: "/queue", icon: PlayCircle },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "Brand DNA", href: "/brand", icon: Palette },
  { label: "Distribution", href: "/distribution", icon: Share2 },
  { label: "Prompts", href: "/prompts", icon: MessageSquare },
]

const bottomNav: NavItem[] = [
  { label: "System Status", href: "/status", icon: Activity },
  { label: "Settings", href: "/settings", icon: Settings },
]

interface SidebarProps {
  collapsed?: boolean
  onToggle?: () => void
}

export function Sidebar({ collapsed = false, onToggle }: SidebarProps) {
  const pathname = usePathname()

  return (
    <TooltipProvider delayDuration={0}>
      <motion.aside
        initial={false}
        animate={{ width: collapsed ? 64 : 260 }}
        transition={{ duration: 0.2, ease: "easeOut" }}
        className="flex h-screen flex-col border-r border-border bg-surface-1"
      >
        {/* Logo */}
        <div className="flex h-14 items-center border-b border-border px-4">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary">
              <span className="text-sm font-bold text-primary-foreground">43</span>
            </div>
            <AnimatePresence>
              {!collapsed && (
                <motion.span
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: "auto" }}
                  exit={{ opacity: 0, width: 0 }}
                  className="text-sm font-semibold tracking-tight"
                >
                  43V3R
                </motion.span>
              )}
            </AnimatePresence>
          </Link>
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 overflow-y-auto p-3">
          <div className="space-y-1">
            {mainNav.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + "/")
              const Icon = item.icon

              const linkContent = (
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-surface-3 text-foreground"
                      : "text-muted-foreground hover:bg-surface-2 hover:text-foreground"
                  )}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  {!collapsed && (
                    <>
                      <span className="flex-1">{item.label}</span>
                      {item.badge && (
                        <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-medium text-primary">
                          {item.badge}
                        </span>
                      )}
                    </>
                  )}
                </Link>
              )

              if (collapsed) {
                return (
                  <Tooltip key={item.href}>
                    <TooltipTrigger asChild>
                      {linkContent}
                    </TooltipTrigger>
                    <TooltipContent side="right">
                      {item.label}
                    </TooltipContent>
                  </Tooltip>
                )
              }

              return <div key={item.href}>{linkContent}</div>
            })}
          </div>
        </nav>

        {/* Bottom Navigation */}
        <div className="border-t border-border p-3">
          <div className="space-y-1">
            {bottomNav.map((item) => {
              const isActive = pathname === item.href
              const Icon = item.icon

              const linkContent = (
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-surface-3 text-foreground"
                      : "text-muted-foreground hover:bg-surface-2 hover:text-foreground"
                  )}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  {!collapsed && <span>{item.label}</span>}
                </Link>
              )

              if (collapsed) {
                return (
                  <Tooltip key={item.href}>
                    <TooltipTrigger asChild>
                      {linkContent}
                    </TooltipTrigger>
                    <TooltipContent side="right">
                      {item.label}
                    </TooltipContent>
                  </Tooltip>
                )
              }

              return <div key={item.href}>{linkContent}</div>
            })}
          </div>

          <Separator className="my-3" />

          {/* Collapse Toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="w-full justify-center"
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <>
                <ChevronLeft className="h-4 w-4 mr-2" />
                <span>Collapse</span>
              </>
            )}
          </Button>
        </div>
      </motion.aside>
    </TooltipProvider>
  )
}