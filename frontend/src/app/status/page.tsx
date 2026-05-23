"""
System Status page
"""
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import {
  Activity,
  Server,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Clock,
} from "lucide-react"

const services = [
  { name: "API Server", status: "healthy", latency: "12ms", uptime: "99.9%" },
  { name: "Database", status: "healthy", latency: "5ms", uptime: "99.9%" },
  { name: "Cache (Redis)", status: "healthy", latency: "1ms", uptime: "99.9%" },
  { name: "Render Workers", status: "healthy", latency: "-", uptime: "98.5%" },
  { name: "Queue System", status: "healthy", latency: "-", uptime: "99.7%" },
  { name: "AI Services", status: "healthy", latency: "234ms", uptime: "97.2%" },
]

const workers = [
  { id: "worker-01", status: "active", jobs: 12, cpu: 45, memory: 62 },
  { id: "worker-02", status: "active", jobs: 8, cpu: 38, memory: 55 },
  { id: "worker-03", status: "idle", jobs: 0, cpu: 5, memory: 28 },
  { id: "worker-04", status: "active", jobs: 15, cpu: 67, memory: 71 },
]

const recentLogs = [
  { time: "14:32:15", level: "info", message: "Render job completed successfully" },
  { time: "14:31:42", level: "info", message: "New user registration: john@example.com" },
  { time: "14:30:18", level: "warning", message: "High memory usage on worker-04" },
  { time: "14:28:55", level: "info", message: "Media asset uploaded: summer_vibes.mp3" },
  { time: "14:27:12", level: "error", message: "Failed to process render job" },
]

export default function StatusPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">System Status</h1>
          <p className="text-sm text-muted-foreground">
            Monitor infrastructure health and performance
          </p>
        </div>
        <Button variant="outline">
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh
        </Button>
      </div>

      {/* Overall Health */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3 mb-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-emerald-500/10">
                <CheckCircle2 className="h-5 w-5 text-emerald-500" />
              </div>
              <div>
                <p className="text-2xl font-semibold">All Systems</p>
                <p className="text-xs text-muted-foreground">Operational</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3 mb-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-surface-2">
                <Server className="h-5 w-5 text-muted-foreground" />
              </div>
              <div>
                <p className="text-2xl font-semibold">6/6</p>
                <p className="text-xs text-muted-foreground">Services Running</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3 mb-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-surface-2">
                <Activity className="h-5 w-5 text-muted-foreground" />
              </div>
              <div>
                <p className="text-2xl font-semibold">99.7%</p>
                <p className="text-xs text-muted-foreground">Uptime (30d)</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3 mb-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-surface-2">
                <Clock className="h-5 w-5 text-muted-foreground" />
              </div>
              <div>
                <p className="text-2xl font-semibold">23ms</p>
                <p className="text-xs text-muted-foreground">Avg Response</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Services Status */}
      <Card>
        <CardContent className="p-5">
          <h2 className="text-base font-medium mb-4">Service Status</h2>
          <div className="space-y-3">
            {services.map((service) => (
              <div key={service.name} className="flex items-center justify-between p-3 rounded-md border border-border">
                <div className="flex items-center gap-3">
                  <div className={`h-2 w-2 rounded-full ${service.status === "healthy" ? "bg-emerald-500" : "bg-amber-500"}`} />
                  <span className="text-sm font-medium">{service.name}</span>
                </div>
                <div className="flex items-center gap-6 text-xs text-muted-foreground">
                  {service.latency !== "-" && (
                    <span>Latency: {service.latency}</span>
                  )}
                  <span>Uptime: {service.uptime}</span>
                  <Badge variant={service.status === "healthy" ? "success" : "warning"} className="text-[10px]">
                    {service.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Worker Nodes */}
      <Card>
        <CardContent className="p-5">
          <h2 className="text-base font-medium mb-4">Worker Nodes</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {workers.map((worker) => (
              <div key={worker.id} className="p-4 rounded-md border border-border">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Badge variant={worker.status === "active" ? "success" : "default"} className="text-[10px]">
                      {worker.status}
                    </Badge>
                    <span className="text-sm font-medium font-mono">{worker.id}</span>
                  </div>
                  <span className="text-xs text-muted-foreground">{worker.jobs} jobs</span>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">CPU</span>
                    <span className="text-xs font-medium">{worker.cpu}%</span>
                  </div>
                  <Progress value={worker.cpu} className="h-1" />
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Memory</span>
                    <span className="text-xs font-medium">{worker.memory}%</span>
                  </div>
                  <Progress value={worker.memory} className="h-1" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Logs */}
      <Card>
        <CardContent className="p-5">
          <h2 className="text-base font-medium mb-4">Recent Activity</h2>
          <div className="space-y-2 font-mono text-xs">
            {recentLogs.map((log, i) => (
              <div key={i} className="flex items-start gap-4 p-2 hover:bg-surface-2 rounded">
                <span className="text-muted-foreground">{log.time}</span>
                <Badge variant={log.level === "error" ? "destructive" : log.level === "warning" ? "warning" : "default"} className="text-[10px] uppercase">
                  {log.level}
                </Badge>
                <span className="flex-1">{log.message}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}