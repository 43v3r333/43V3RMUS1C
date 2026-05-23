"""
Skeleton component for loading states
"""
import { cn } from "@/lib/utils"

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "text" | "circular"
}

function Skeleton({ className, variant = "default", ...props }: SkeletonProps) {
  return (
    <div
      className={cn(
        "bg-surface-3 animate-pulse",
        variant === "default" && "rounded-md",
        variant === "text" && "rounded h-4 w-full",
        variant === "circular" && "rounded-full",
        className
      )}
      {...props}
    />
  )
}

export { Skeleton }