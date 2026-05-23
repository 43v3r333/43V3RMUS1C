import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Render Queue | 43V3R CORE',
  description: 'Video and audio processing management',
}

export default function QueuePage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Render Queue</h1>
          <p className="text-sm text-muted-foreground">
            Monitor and manage render jobs
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-xs text-primary">
            <span className="h-2 w-2 rounded-full bg-primary animate-pulse" />
            3 Active
          </span>
        </div>
      </div>

      {/* Queue Table */}
      <div className="rounded-lg border border-border bg-card">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Name</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Type</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Progress</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Priority</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">Actions</th>
            </tr>
          </thead>
          <tbody>
            {[
              { name: 'Final Mix - Track 05', type: 'Audio', status: 'processing', progress: 67, priority: 'high' },
              { name: 'Album Cover Animation', type: 'Video', status: 'queued', progress: 0, priority: 'normal' },
              { name: 'Lyric Video Export', type: 'Video', status: 'processing', progress: 23, priority: 'normal' },
              { name: 'Podcast Intro', type: 'Audio', status: 'completed', progress: 100, priority: 'low' },
              { name: 'Social Clips', type: 'Video', status: 'queued', progress: 0, priority: 'high' },
            ].map((job, i) => (
              <tr key={i} className="border-b border-border last:border-0">
                <td className="px-4 py-3 text-sm">{job.name}</td>
                <td className="px-4 py-3 text-sm text-muted-foreground">{job.type}</td>
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs ${
                    job.status === 'completed' ? 'bg-green-500/10 text-green-500' :
                    job.status === 'processing' ? 'bg-blue-500/10 text-blue-500' :
                    'bg-muted text-muted-foreground'
                  }`}>
                    {job.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-24 rounded-full bg-muted">
                      <div
                        className="h-full rounded-full bg-primary transition-all"
                        style={{ width: `${job.progress}%` }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground">{job.progress}%</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs ${
                    job.priority === 'high' ? 'text-red-500' :
                    job.priority === 'low' ? 'text-muted-foreground' :
                    'text-foreground'
                  }`}>
                    {job.priority}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  <button className="text-xs text-muted-foreground hover:text-foreground">
                    Cancel
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}