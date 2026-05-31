import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Projects | 43V3R CORE',
  description: 'Creative project organization',
}

export default function ProjectsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Projects</h1>
          <p className="text-sm text-muted-foreground">
            Organize and manage your creative work
          </p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
          New Project
        </button>
      </div>

      {/* Project Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[
          { name: 'Summer Release 2024', status: 'in_progress', type: 'Album', tracks: 8 },
          { name: 'Tour Visuals', status: 'draft', type: 'Video', tracks: 3 },
          { name: 'Social Campaign', status: 'completed', type: 'Marketing', tracks: 12 },
          { name: 'Remix Project', status: 'in_progress', type: 'Single', tracks: 1 },
          { name: 'EP Production', status: 'draft', type: 'Album', tracks: 5 },
          { name: 'Music Video', status: 'in_progress', type: 'Video', tracks: 2 },
        ].map((project, i) => (
          <div
            key={i}
            className="rounded-lg border border-border bg-card p-4 hover:border-primary/50 transition-colors cursor-pointer"
          >
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-medium">{project.name}</h3>
                <p className="text-xs text-muted-foreground">{project.type}</p>
              </div>
              <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs ${
                project.status === 'completed' ? 'bg-green-500/10 text-green-500' :
                project.status === 'in_progress' ? 'bg-primary/10 text-primary' :
                'bg-muted text-muted-foreground'
              }`}>
                {project.status}
              </span>
            </div>
            <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
              <span>{project.tracks} items</span>
              <span>Updated 2d ago</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}