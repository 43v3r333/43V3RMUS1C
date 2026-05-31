import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Workflows | 43V3R CORE',
  description: 'Automated pipeline management',
}

export default function WorkflowsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Workflows</h1>
          <p className="text-sm text-muted-foreground">
            Create and manage automated pipelines
          </p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
          Create Workflow
        </button>
      </div>

      {/* Workflow List */}
      <div className="space-y-4">
        {[
          { name: 'Auto-distribute to Spotify', type: 'Distribution', status: 'active', runs: 234 },
          { name: 'Generate Social Preview', type: 'Generation', status: 'active', runs: 89 },
          { name: 'Weekly Analytics Report', type: 'Automation', status: 'active', runs: 12 },
          { name: 'Backup to Archive', type: 'Maintenance', status: 'paused', runs: 56 },
        ].map((workflow, i) => (
          <div
            key={i}
            className="rounded-lg border border-border bg-card p-4"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-md bg-muted">
                  ⚡
                </div>
                <div>
                  <h3 className="font-medium">{workflow.name}</h3>
                  <p className="text-xs text-muted-foreground">{workflow.type} • {workflow.runs} runs</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs ${
                  workflow.status === 'active' ? 'bg-green-500/10 text-green-500' :
                  'bg-yellow-500/10 text-yellow-500'
                }`}>
                  {workflow.status}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}