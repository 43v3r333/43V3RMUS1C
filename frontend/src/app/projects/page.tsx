"""
Projects page
*/
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import {
  Plus,
  Search,
  MoreHorizontal,
  Calendar,
  Folder,
  Clock,
  Layers,
} from "lucide-react"

const projects = [
  {
    id: 1,
    name: "Summer Album 2024",
    description: "New summer release with 12 tracks",
    status: "in_progress",
    progress: 67,
    tracks: 8,
    totalTracks: 12,
    dueDate: "2024-06-15",
    updatedAt: "2 hours ago",
  },
  {
    id: 2,
    name: "Single Release - Echoes",
    description: "Standalone single with music video",
    status: "completed",
    progress: 100,
    tracks: 1,
    totalTracks: 1,
    dueDate: "2024-05-01",
    updatedAt: "1 day ago",
  },
  {
    id: 3,
    name: "EP - Midnight Sessions",
    description: "Acoustic EP with 5 tracks",
    status: "draft",
    progress: 20,
    tracks: 1,
    totalTracks: 5,
    dueDate: "2024-07-01",
    updatedAt: "3 days ago",
  },
  {
    id: 4,
    name: "Social Campaign - Q2",
    description: "Marketing assets for Q2 release",
    status: "in_progress",
    progress: 45,
    tracks: 0,
    totalTracks: 0,
    dueDate: "2024-04-30",
    updatedAt: "5 hours ago",
  },
]

const statusColors = {
  draft: "default",
  in_progress: "primary",
  completed: "success",
  archived: "default",
} as const

export default function ProjectsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Projects</h1>
          <p className="text-sm text-muted-foreground">
            Manage your creative projects
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Project
        </Button>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input placeholder="Search projects..." className="pl-9" />
      </div>

      {/* Projects Grid */}
      <div className="grid gap-4 md:grid-cols-2">
        {projects.map((project) => (
          <Card key={project.id} className="hover:bg-surface-2 transition-colors cursor-pointer">
            <CardContent className="p-5">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-base font-semibold">{project.name}</h3>
                    <Badge variant={statusColors[project.status as keyof typeof statusColors]}>
                      {project.status.replace("_", " ")}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-4">
                    {project.description}
                  </p>
                </div>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>

              {/* Progress */}
              {project.totalTracks > 0 && (
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-muted-foreground">
                      {project.tracks}/{project.totalTracks} tracks
                    </span>
                    <span className="text-xs font-medium">{project.progress}%</span>
                  </div>
                  <Progress value={project.progress} />
                </div>
              )}

              {/* Meta */}
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5" />
                  <span>Due {project.dueDate}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  <span>Updated {project.updatedAt}</span>
                </div>
                {project.tracks > 0 && (
                  <div className="flex items-center gap-1">
                    <Layers className="h-3.5 w-3.5" />
                    <span>{project.tracks} tracks</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}