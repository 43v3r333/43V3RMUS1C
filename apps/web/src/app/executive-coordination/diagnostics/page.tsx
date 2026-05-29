/**
 * 43V3R CORE - Diagnostics Page
 */
'use client'

import dynamic from 'next/dynamic'

const PredictiveRecursiveDiagnostics = dynamic(
  () => import('@/components/executive/PredictiveRecursiveDiagnostics'),
  { ssr: false }
)

export default function DiagnosticsPage() {
  return (
    <div className="h-full">
      <PredictiveRecursiveDiagnostics />
    </div>
  )
}
