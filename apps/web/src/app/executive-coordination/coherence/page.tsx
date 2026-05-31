/**
 * 43V3R CORE - Coherence Page
 */
'use client'

import dynamic from 'next/dynamic'

const SystemicCoherenceVisualization = dynamic(
  () => import('@/components/executive/SystemicCoherenceVisualization'),
  { ssr: false }
)

export default function CoherencePage() {
  return (
    <div className="h-full">
      <SystemicCoherenceVisualization />
    </div>
  )
}
