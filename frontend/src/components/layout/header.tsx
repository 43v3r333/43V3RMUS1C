"""
Top command bar component
"""
"use client"

import { useState } from "react"
import { Search, Bell, Command, User, LogOut, Settings, ChevronDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface HeaderProps {
  title?: string
  subtitle?: string
}

export function Header({ title, subtitle }: HeaderProps) {
  const [searchFocused, setSearchFocused] = useState(false)

  return (
    <header className="flex h-14 items-center gap-4 border-b border-border bg-surface-1 px-6">
      {/* Page Title */}
      {title && (
        <div className="flex flex-col">
          <h1 className="text-sm font-semibold">{title}</h1>
          {subtitle && (
            <span className="text-xs text-muted-foreground">{subtitle}</span>
          )}
        </div>
      )}

      {/* Spacer */}
      <div className="flex-1" />

      {/* Search */}
      <div
        className={cn(
          "relative flex items-center transition-all duration-200",
          searchFocused ? "w-80" : "w-64"
        )}
      >
        <Search className="absolute left-3 h-4 w-4 text-muted-foreground" />
        <Input
          type="search"
          placeholder="Search..."
          className="pl-9 pr-12"
          onFocus={() => setSearchFocused(true)}
          onBlur={() => setSearchFocused(false)}
        />
        <kbd className="absolute right-3 flex items-center gap-1 rounded border border-border bg-surface-2 px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground">
          <Command className="h-3 w-3" />K
        </kbd>
      </div>

      {/* Notifications */}
      <Button variant="ghost" size="icon" className="relative">
        <Bell className="h-4 w-4" />
        <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-primary" />
      </Button>

      {/* User Menu */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="flex items-center gap-2 px-2">
            <Avatar className="h-7 w-7">
              <AvatarImage src="/avatars/user.png" />
              <AvatarFallback>JD</AvatarFallback>
            </Avatar>
            <span className="text-sm font-medium">John Doe</span>
            <ChevronDown className="h-3 w-3 text-muted-foreground" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel>
            <div className="flex flex-col">
              <span>John Doe</span>
              <span className="text-xs font-normal text-muted-foreground">
                john@example.com
              </span>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem>
            <User className="mr-2 h-4 w-4" />
            Profile
          </DropdownMenuItem>
          <DropdownMenuItem>
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem className="text-destructive">
            <LogOut className="mr-2 h-4 w-4" />
            Log out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  )
}