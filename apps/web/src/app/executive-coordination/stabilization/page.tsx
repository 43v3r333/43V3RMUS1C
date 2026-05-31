/**
 * 43V3R CORE - Stabilization Page
 */
'use client'

import dynamic from 'next/dynamic'

const HierarchicalStabilizationDashboard = dynamic(
  () => import('@/components/executive/HierarchicalStabilizationDashboard'),
  { ssr: false }
)

export default function StabilizationPage() {
  return (
    <div className="h-full">
      <HierarchicalStabilizationDashboard />
    </div>
  )
}
