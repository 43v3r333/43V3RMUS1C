import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Dashboard | 43V3R CORE',
  description: 'Command Center - Real-time overview of operations',
}

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Command Center</h1>
          <p className="text-sm text-muted-foreground">
            Real-time overview of your media operations
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">Last updated: just now</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Active Projects', value: '12', change: '+2' },
          { label: 'Media Assets', value: '847', change: '+23' },
          { label: 'Render Queue', value: '5', change: '-3' },
          { label: 'Automation Jobs', value: '128', change: '+15' },
        ].map((stat, i) => (
          <div
            key={i}
            className="rounded-lg border border-border bg-card p-4"
          >
            <div className="text-sm text-muted-foreground">{stat.label}</div>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-2xl font-semibold">{stat.value}</span>
              <span className="text-xs text-green-500">{stat.change}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Activity */}
        <div className="rounded-lg border border-border bg-card">
          <div className="border-b border-border p-4">
            <h2 className="font-medium">Recent Activity</h2>
          </div>
          <div className="p-4">
            <div className="space-y-4">
              {[
                { time: '2m ago', action: 'Render job completed', detail: 'Project Alpha - Final Cut.mp4' },
                { time: '15m ago', action: 'Media uploaded', detail: 'audio_master_v3.wav' },
                { time: '1h ago', action: 'Workflow executed', detail: 'Auto-post to Spotify' },
                { time: '2h ago', action: 'Campaign launched', detail: 'Summer Release 2024' },
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-3">
                  <div className="h-2 w-2 rounded-full bg-primary" />
                  <div className="flex-1">
                    <p className="text-sm">{item.action}</p>
                    <p className="text-xs text-muted-foreground">{item.detail}</p>
                  </div>
                  <span className="text-xs text-muted-foreground">{item.time}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="rounded-lg border border-border bg-card">
          <div className="border-b border-border p-4">
            <h2 className="font-medium">System Status</h2>
          </div>
          <div className="p-4 space-y-3">
            {[
              { name: 'API Server', status: 'operational', latency: '23ms' },
              { name: 'Database', status: 'operational', latency: '12ms' },
              { name: 'Render Workers', status: 'operational', latency: '8ms' },
              { name: 'Storage', status: 'operational', latency: '45ms' },
            ].map((service, i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`h-2 w-2 rounded-full ${
                    service.status === 'operational' ? 'bg-green-500' : 'bg-yellow-500'
                  }`} />
                  <span className="text-sm">{service.name}</span>
                </div>
                <span className="text-xs text-muted-foreground">{service.latency}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="rounded-lg border border-border bg-card p-4">
        <h2 className="mb-4 font-medium">Quick Actions</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: 'New Project', icon: '+' },
            { label: 'Upload Media', icon: '↑' },
            { label: 'Create Workflow', icon: '⚡' },
            { label: 'View Queue', icon: '▶' },
          ].map((action, i) => (
            <button
              key={i}
              className="flex items-center gap-3 rounded-md border border-border bg-background px-4 py-3 text-sm hover:bg-accent transition-colors"
            >
              <span className="text-lg">{action.icon}</span>
              {action.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}