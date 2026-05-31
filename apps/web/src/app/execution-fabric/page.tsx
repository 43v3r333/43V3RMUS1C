"""
Execution Fabric Page - Unified execution fabric interface.

Central dashboard for:
- Event topology governance
- Distributed runtime propagation
- Cognition fabric
- Self-healing orchestration
- Semantic execution
- Predictive observability
- Real-time streaming
"""
'use client'

import ExecutionFabricControlCenter from '@/components/execution-fabric/ExecutionFabricControlCenter'
import { ExecutionFabricStreamProvider } from '@/components/execution-fabric/ExecutionFabricStreamProvider'

export default function ExecutionFabricPage() {
  return (
    <ExecutionFabricStreamProvider>
      <div className="min-h-screen bg-background">
        <div className="container mx-auto p-6">
          <ExecutionFabricControlCenter />
        </div>
      </div>
    </ExecutionFabricStreamProvider>
  )
}