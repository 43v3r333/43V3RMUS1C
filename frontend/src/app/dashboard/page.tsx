"""
Dashboard page - Command Center
*/
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Activity,
  TrendingUp,
  Layers,
  PlayCircle,
  Clock,
  Zap,
  Music,
  Image,
  FileVideo,
} from "lucide-react"

const stats = [
  {
    label: "Active Projects",
    value: "12",
    change: "+2",
    icon: Layers,
  },
  {
    label: "Render Queue",
    value: "47",
    change: "+5",
    icon: PlayCircle,
  },
  {
    label: "This Week",
    value: "2.4k",
    change: "+12%",
    icon: Activity,
  },
  {
    label: "AI Tasks",
    value: "156",
    change: "+23",
    icon: Zap,
  },
]

const recentActivity = [
  { id: 1, type: "render", name: "Album Cover v3", status: "processing", progress: 67 },
  { id: 2, type: "ai", name: "TTS Generation", status: "completed", time: "2m ago" },
  { id: 3, type: "upload", name: "Studio Session.mp4", status: "ready", time: "5m ago" },
  { id: 4, type: "render", name: "Social Clip", status: "queued", time: "8m ago" },
]

const quickActions = [
  { label: "New Project", icon: Layers },
  { label: "Upload Media", icon: FileVideo },
  { label: "Generate Assets", icon: Image },
  { label: "Start Render", icon: PlayCircle },
]

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Command Center</h1>
        <p className="text-sm text-muted-foreground">
          Overview of your media operations
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-muted-foreground">
                  {stat.label}
                </span>
                <stat.icon className="h-4 w-4 text-muted-foreground" />
              </div>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-2xl font-semibold">{stat.value}</span>
                <Badge variant="success" className="text-[10px]">
                  {stat.change}
                </Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Recent Activity */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-medium">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center gap-4 rounded-md border border-border p-3"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-md bg-surface-2">
                    {item.type === "render" && (
                      <PlayCircle className="h-5 w-5 text-primary" />
                    )}
                    {item.type === "ai" && <Zap className="h-5 w-5 text-amber-500" />}
                    {item.type === "upload" && (
                      <FileVideo className="h-5 w-5 text-emerald-500" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{item.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {item.status === "processing" ? (
                        <span className="text-primary">{item.progress}% complete</span>
                      ) : (
                        item.time
                      )}
                    </p>
                  </div>
                  <Badge
                    variant={
                      item.status === "completed"
                        ? "success"
                        : item.status === "processing"
                        ? "primary"
                        : "default"
                    }
                  >
                    {item.status}
                  </Badge>
                  {item.status === "processing" && (
                    <Progress value={item.progress} className="w-16" />
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-medium">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-2">
              {quickActions.map((action) => (
                <button
                  key={action.label}
                  className="flex flex-col items-center gap-2 rounded-md border border-border p-4 transition-colors hover:bg-surface-2"
                >
                  <action.icon className="h-5 w-5 text-muted-foreground" />
                  <span className="text-xs font-medium">{action.label}</span>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System Status */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-medium">System Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="flex items-center gap-3">
              <div className="h-2 w-2 rounded-full bg-emerald-500" />
              <div>
                <p className="text-sm font-medium">API Server</p>
                <p className="text-xs text-muted-foreground">12ms latency</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="h-2 w-2 rounded-full bg-emerald-500" />
              <div>
                <p className="text-sm font-medium">Database</p>
                <p className="text-xs text-muted-foreground">Connected</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="h-2 w-2 rounded-full bg-emerald-500" />
              <div>
                <p className="text-sm font-medium">Render Workers</p>
                <p className="text-xs text-muted-foreground">4/4 active</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="h-2 w-2 rounded-full bg-amber-500" />
              <div>
                <p className="text-sm font-medium">Storage</p>
                <p className="text-xs text-muted-foreground">67% used</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}