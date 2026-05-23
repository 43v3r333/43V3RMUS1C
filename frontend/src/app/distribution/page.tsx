"""
Distribution page for social media management
"""
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import {
  Share2,
  Plus,
  Upload,
  Clock,
  BarChart3,
  Instagram,
  Youtube,
  Twitter,
  Spotify,
  CheckCircle2,
  ExternalLink,
} from "lucide-react"

const platforms = [
  { name: "Instagram", icon: Instagram, connected: true, followers: "45.2K" },
  { name: "YouTube", icon: Youtube, connected: true, followers: "12.5K" },
  { name: "Twitter", icon: Twitter, connected: true, followers: "8.3K" },
  { name: "Spotify", icon: Spotify, connected: true, followers: "23.1K" },
]

const scheduledPosts = [
  {
    id: 1,
    content: "New single dropping next Friday!",
    platform: "Instagram",
    scheduledAt: "Today, 3:00 PM",
    status: "scheduled",
  },
  {
    id: 2,
    content: "Studio session recap coming soon...",
    platform: "YouTube",
    scheduledAt: "Tomorrow, 10:00 AM",
    status: "scheduled",
  },
  {
    id: 3,
    content: "Behind the scenes from today's shoot",
    platform: "Twitter",
    scheduledAt: "In 2 hours",
    status: "scheduled",
  },
]

const recentPosts = [
  {
    id: 1,
    content: "Album release day!",
    platform: "Instagram",
    publishedAt: "2 days ago",
    status: "published",
    metrics: { likes: 1245, comments: 89, shares: 45 },
  },
  {
    id: 2,
    content: "Check out the new track!",
    platform: "Twitter",
    publishedAt: "5 days ago",
    status: "published",
    metrics: { likes: 567, comments: 23, shares: 12 },
  },
]

export default function DistributionPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Distribution</h1>
          <p className="text-sm text-muted-foreground">
            Manage your social media presence
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Upload className="mr-2 h-4 w-4" />
            Upload Media
          </Button>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Post
          </Button>
        </div>
      </div>

      {/* Platform Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        {platforms.map((platform) => (
          <Card key={platform.name}>
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-md bg-surface-2">
                  <platform.icon className="h-5 w-5 text-muted-foreground" />
                </div>
                <Badge variant={platform.connected ? "success" : "default"}>
                  {platform.connected ? "Connected" : "Disconnected"}
                </Badge>
              </div>
              <h3 className="text-sm font-semibold mb-1">{platform.name}</h3>
              <p className="text-xs text-muted-foreground">{platform.followers} followers</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Content Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Scheduled Posts */}
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-medium">Scheduled Posts</h2>
              <Button variant="outline" size="sm">View Calendar</Button>
            </div>
            <div className="space-y-4">
              {scheduledPosts.map((post) => (
                <div key={post.id} className="flex items-start gap-4 p-4 rounded-md border border-border">
                  <div className="flex h-10 w-10 items-center justify-center rounded-md bg-surface-2">
                    {post.platform === "Instagram" && <Instagram className="h-5 w-5 text-muted-foreground" />}
                    {post.platform === "YouTube" && <Youtube className="h-5 w-5 text-muted-foreground" />}
                    {post.platform === "Twitter" && <Twitter className="h-5 w-5 text-muted-foreground" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm mb-2">{post.content}</p>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {post.scheduledAt}
                      </span>
                      <Badge variant="default" className="text-[10px]">{post.platform}</Badge>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <ExternalLink className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Posts */}
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-medium">Recent Posts</h2>
              <Button variant="outline" size="sm">View All</Button>
            </div>
            <div className="space-y-4">
              {recentPosts.map((post) => (
                <div key={post.id} className="p-4 rounded-md border border-border">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      {post.platform === "Instagram" && <Instagram className="h-4 w-4 text-muted-foreground" />}
                      {post.platform === "Twitter" && <Twitter className="h-4 w-4 text-muted-foreground" />}
                      <span className="text-xs text-muted-foreground">{post.publishedAt}</span>
                    </div>
                    <Badge variant="success" className="text-[10px]">
                      <CheckCircle2 className="h-3 w-3 mr-1" />
                      Published
                    </Badge>
                  </div>
                  <p className="text-sm mb-3">{post.content}</p>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <span>{post.metrics.likes.toLocaleString()} likes</span>
                    <span>{post.metrics.comments} comments</span>
                    <span>{post.metrics.shares} shares</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Analytics Summary */}
      <Card>
        <CardContent className="p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-medium">This Week Performance</h2>
            <Button variant="outline" size="sm">
              <BarChart3 className="h-3 w-3 mr-2" />
              Full Analytics
            </Button>
          </div>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="text-center p-4 rounded-md bg-surface-2">
              <p className="text-2xl font-semibold text-primary">12</p>
              <p className="text-xs text-muted-foreground">Posts Published</p>
            </div>
            <div className="text-center p-4 rounded-md bg-surface-2">
              <p className="text-2xl font-semibold">45.2K</p>
              <p className="text-xs text-muted-foreground">Total Reach</p>
            </div>
            <div className="text-center p-4 rounded-md bg-surface-2">
              <p className="text-2xl font-semibold text-emerald-500">8.7K</p>
              <p className="text-xs text-muted-foreground">Engagements</p>
            </div>
            <div className="text-center p-4 rounded-md bg-surface-2">
              <p className="text-2xl font-semibold">3.2%</p>
              <p className="text-xs text-muted-foreground">Engagement Rate</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}