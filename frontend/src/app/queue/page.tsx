"""
Render Queue page
*/
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import {
  Play,
  Pause,
  RotateCcw,
  Trash2,
  Search,
  Filter,
  Clock,
  Zap,
  CheckCircle2,
  AlertCircle,
} from "lucide-react"

const jobs = [
  {
    id: 1,
    name: "Album Cover Animation",
    type: "video",
    status: "processing",
    progress: 67,
    startedAt: "10:32 AM",
    eta: "2 min",
    worker: "worker-01",
  },
  {
    id: 2,
    name: "Social Clip 16:9",
    type: "video",
    status: "queued",
    progress: 0,
    startedAt: null,
    eta: "5 min",
    worker: null,
  },
  {
    id: 3,
    name: "Audio Mastering",
    type: "audio",
    status: "completed",
    progress: 100,
    startedAt: "10:15 AM",
    eta: null,
    worker: "worker-02",
  },
  {
    id: 4,
    name: "Podcast Intro",
    type: "audio",
    status: "failed",
    progress: 45,
    startedAt: "9:45 AM",
    eta: null,
    worker: "worker-01",
    error: "Insufficient storage space",
  },
  {
    id: 5,
    name: "Lyric Video",
    type: "video",
    status: "processing",
    progress: 23,
    startedAt: "10:45 AM",
    eta: "8 min",
    worker: "worker-03",
  },
]

const statusConfig = {
  processing: { variant: "primary" as const, icon: Zap },
  queued: { variant: "default" as const, icon: Clock },
  completed: { variant: "success" as const, icon: CheckCircle2 },
  failed: { variant: "destructive" as const, icon: AlertCircle },
}

export default function QueuePage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Render Queue</h1>
          <p className="text-sm text-muted-foreground">
            Monitor and manage render jobs
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Pause className="mr-2 h-4 w-4" />
            Pause Queue
          </Button>
          <Button>
            <Play className="mr-2 h-4 w-4" />
            Add Job
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-xs font-medium text-muted-foreground mb-1">Active Jobs</div>
            <div className="text-2xl font-semibold">3</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-xs font-medium text-muted-foreground mb-1">Queued</div>
            <div className="text-2xl font-semibold">2</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-xs font-medium text-muted-foreground mb-1">Completed Today</div>
            <div className="text-2xl font-semibold">12</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-xs font-medium text-muted-foreground mb-1">Failed</div>
            <div className="text-2xl font-semibold text-destructive">1</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder="Search jobs..." className="pl-9" />
        </div>
        <Button variant="outline" size="icon">
          <Filter className="h-4 w-4" />
        </Button>
      </div>

      {/* Job List */}
      <Card>
        <CardContent className="p-0">
          <div className="divide-y divide-border">
            {jobs.map((job) => {
              const config = statusConfig[job.status as keyof typeof statusConfig]
              const StatusIcon = config.icon

              return (
                <div key={job.id} className="flex items-center gap-4 p-4 hover:bg-surface-2 transition-colors">
                  {/* Status Icon */}
                  <div className={`flex h-10 w-10 items-center justify-center rounded-md ${
                    job.status === "processing" ? "bg-primary/10" :
                    job.status === "completed" ? "bg-emerald-500/10" :
                    job.status === "failed" ? "bg-destructive/10" :
                    "bg-surface-3"
                  }`}>
                    <StatusIcon className={`h-5 w-5 ${
                      job.status === "processing" ? "text-primary" :
                      job.status === "completed" ? "text-emerald-500" :
                      job.status === "failed" ? "text-destructive" :
                      "text-muted-foreground"
                    }`} />
                  </div>

                  {/* Job Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-sm font-medium truncate">{job.name}</p>
                      <Badge variant={config.variant} className="text-[10px]">
                        {job.status}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span className="uppercase">{job.type}</span>
                      {job.startedAt && <span>Started {job.startedAt}</span>}
                      {job.eta && <span>ETA {job.eta}</span>}
                      {job.worker && <span>Worker: {job.worker}</span>}
                    </div>
                  </div>

                  {/* Progress */}
                  {job.status === "processing" && (
                    <div className="w-32">
                      <Progress value={job.progress} className="h-1.5" />
                    </div>
                  )}

                  {/* Error */}
                  {job.status === "failed" && job.error && (
                    <span className="text-xs text-destructive">{job.error}</span>
                  )}

                  {/* Actions */}
                  <div className="flex items-center gap-1">
                    {job.status === "failed" && (
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <RotateCcw className="h-4 w-4" />
                      </Button>
                    )}
                    {job.status === "queued" && (
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <Play className="h-4 w-4" />
                      </Button>
                    )}
                    {job.status === "completed" && (
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                    {job.status === "processing" && (
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <Pause className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}