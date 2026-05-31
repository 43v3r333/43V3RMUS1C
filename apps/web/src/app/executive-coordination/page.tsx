/**
 * 43V3R CORE - Executive Coordination Page
 * 
 * Main entry point for the Executive Coordination Control Center,
 * providing centralized access to all executive coordination features.
 */
'use client'

import dynamic from 'next/dynamic'

// Dynamic import to avoid SSR issues with Lucide icons
const ExecutiveCoordinationControlCenter = dynamic(
  () => import('@/components/executive/ExecutiveCoordinationControlCenter'),
  { ssr: false }
)

export default function ExecutiveCoordinationPage() {
  return (
    <div className="h-full">
      <ExecutiveCoordinationControlCenter />
    </div>
  )
}
