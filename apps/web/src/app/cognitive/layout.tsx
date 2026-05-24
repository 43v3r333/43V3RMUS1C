import { Suspense } from 'react'
import { Providers } from '../providers'
import AppLayout from '@/components/layout/app-layout'

export default function CognitiveLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <Providers>
      <AppLayout>
        <Suspense fallback={<div className="p-6">Loading...</div>}>
          {children}
        </Suspense>
      </AppLayout>
    </Providers>
  )
}