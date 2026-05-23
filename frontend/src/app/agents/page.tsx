"""
AI Agents page for workflow orchestration
"""
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import {
  Activity,
  Play,
  Settings,
  Zap,
  Clock,
  CheckCircle2,
  Bot,
  Sparkles,
  Plus,
} from "lucide-react"

const agents = [
  {
    id: 1,
    name: "Content Generator",
    description: "Generates marketing content and social posts",
    status: "active",
    tasks: 156,
    completed: 148,
    failure: 2,
    lastRun: "5 min ago",
  },
  {
    id: 2,
    name: "Audio Processor",
    description: "Processes and masters audio files",
    status: "active",
    tasks: 45,
    completed: 42,
    failure: 1,
    lastRun: "12 min ago",
  },
  {
    id: 3,
    name: "Visual Generator",
    description: "Creates album art and visual assets",
    status: "idle",
    tasks: 23,
    completed: 23,
    failure: 0,
    lastRun: "1 hour ago",
  },
  {
    id: 4,
    name: "Distribution Agent",
    description: "Distributes content to platforms",
    status: "active",
    tasks: 89,
    completed: 87,
    failure: 1,
    lastRun: "3 min ago",
  },
]

const workflows = [
  {
    id: 1,
    name: "New Release Pipeline",
    description: "Generate assets and distribute for new releases",
    steps: ["Generate Artwork", "Master Audio", "Create Social", "Distribute"],
    status: "active",
    trigger: "Manual",
  },
  {
    id: 2,
    name: "Social Automation",
    description: "Auto-post to social platforms on schedule",
    steps: ["Monitor Trends", "Generate Caption", "Create Media", "Post"],
    status: "active",
    trigger: "Scheduled",
  },
  {
    id: 3,
    name: "Quality Check",
    description: "Check audio quality and metadata",
    steps: ["Validate Audio", "Check Metadata", "Verify Assets"],
    status: "draft",
    trigger: "Event",
  },
]

export default function AgentsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">AI Agent Orchestration</h1>
          <p className="text-sm text-muted-foreground">
            Manage AI agents and automated workflows
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Plus className="mr-2 h-4 w-4" />
            New Agent
          </Button>
          <Button>
            <Sparkles className="mr-2 h-4 w-4" />
            Create Workflow
          </Button>
        </div>
      </div>

      {/* Agents Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {agents.map((agent) => (
          <Card key={agent.id} className="hover:bg-surface-2 transition-colors">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10">
                  <Bot className="h-5 w-5 text-primary" />
                </div>
                <Badge variant={agent.status === "active" ? "success" : "default"}>
                  {agent.status}
                </Badge>
              </div>
              <h3 className="text-sm font-semibold mb-1">{agent.name}</h3>
              <p className="text-xs text-muted-foreground mb-4">{agent.description}</p>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Tasks</span>
                  <span className="font-medium">{agent.tasks}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Completed</span>
                  <span className="font-medium text-emerald-500">{agent.completed}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Failed</span>
                  <span className="font-medium text-destructive">{agent.failure}</span>
                </div>
                <div className="flex items-center justify-between text-xs pt-2 border-t border-border">
                  <span className="text-muted-foreground">Last run</span>
                  <span>{agent.lastRun}</span>
                </div>
              </div>

              <div className="flex gap-2 mt-4">
                <Button variant="outline" size="sm" className="flex-1">
                  <Play className="h-3 w-3 mr-1" />
                  Run
                </Button>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Settings className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Workflows */}
      <Card>
        <CardContent className="p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-medium">Active Workflows</h2>
            <Button variant="outline" size="sm">View All</Button>
          </div>
          <div className="space-y-4">
            {workflows.map((workflow) => (
              <div key={workflow.id} className="flex items-center gap-4 p-4 rounded-md border border-border hover:bg-surface-2 transition-colors">
                <div className="flex h-12 w-12 items-center justify-center rounded-md bg-surface-2">
                  <Activity className="h-6 w-6 text-muted-foreground" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="text-sm font-semibold">{workflow.name}</h4>
                    <Badge variant={workflow.status === "active" ? "success" : "default"}>
                      {workflow.status}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mb-3">{workflow.description}</p>
                  <div className="flex items-center gap-2">
                    {workflow.steps.map((step, i) => (
                      <div key={i} className="flex items-center">
                        <span className="text-[10px] font-medium text-muted-foreground">
                          {step}
                        </span>
                        {i < workflow.steps.length - 1 && (
                          <span className="mx-2 text-muted-foreground">→</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
                <div className="text-right">
                  <Badge variant="outline" className="text-[10px]">{workflow.trigger}</Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* System Metrics */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-emerald-500/10">
                <CheckCircle2 className="h-5 w-5 text-emerald-500" />
              </div>
              <div>
                <p className="text-2xl font-semibold">98.5%</p>
                <p className="text-xs text-muted-foreground">Success Rate</p>
              </div>
            </div>
            <Progress value={98.5} className="h-1" />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10">
                <Zap className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-semibold">2.3s</p>
                <p className="text-xs text-muted-foreground">Avg Response Time</p>
              </div>
            </div>
            <Progress value={75} className="h-1" />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-amber-500/10">
                <Clock className="h-5 w-5 text-amber-500" />
              </div>
              <div>
                <p className="text-2xl font-semibold">1,247</p>
                <p className="text-xs text-muted-foreground">Tasks Today</p>
              </div>
            </div>
            <Progress value={60} className="h-1" />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}