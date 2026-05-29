/**
 * 43V3R CORE - Supervision Page
 */
'use client'

import dynamic from 'next/dynamic'

const RecursiveSupervisionWorkspace = dynamic(
  () => import('@/components/executive/RecursiveSupervisionWorkspace'),
  { ssr: false }
)

export default function SupervisionPage() {
  return (
    <div className="h-full">
      <RecursiveSupervisionWorkspace />
    </div>
  )
}
