"""
Analytics page
*/
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import {
  TrendingUp,
  TrendingDown,
  Users,
  Play,
  Heart,
  Share2,
  Music,
  Clock,
} from "lucide-react"

const overviewStats = [
  { label: "Total Plays", value: "1.2M", change: "+12%", up: true, icon: Play },
  { label: "Unique Listeners", value: "45.2K", change: "+8%", up: true, icon: Users },
  { label: "Engagement Rate", value: "4.8%", change: "-2%", up: false, icon: Heart },
  { label: "Shares", value: "8.3K", change: "+15%", up: true, icon: Share2 },
]

const topTracks = [
  { rank: 1, title: "Midnight Echoes", plays: "245K", change: "+12%", growth: 85 },
  { rank: 2, title: "Summer Dreams", plays: "198K", change: "+8%", growth: 72 },
  { rank: 3, title: "City Lights", plays: "156K", change: "+15%", growth: 65 },
  { rank: 4, title: "Ocean Waves", plays: "124K", change: "+5%", growth: 58 },
  { rank: 5, title: "Quiet Moments", plays: "98K", change: "+22%", growth: 45 },
]

const platformBreakdown = [
  { platform: "Spotify", percentage: 45, streams: "540K" },
  { platform: "Apple Music", percentage: 28, streams: "336K" },
  { platform: "YouTube", percentage: 15, streams: "180K" },
  { platform: "SoundCloud", percentage: 8, streams: "96K" },
  { platform: "Other", percentage: 4, streams: "48K" },
]

const geographicData = [
  { region: "United States", percentage: 42, listeners: "18.9K" },
  { region: "United Kingdom", percentage: 18, listeners: "8.1K" },
  { region: "Germany", percentage: 12, listeners: "5.4K" },
  { region: "Canada", percentage: 8, listeners: "3.6K" },
  { region: "Australia", percentage: 6, listeners: "2.7K" },
]

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Analytics</h1>
        <p className="text-sm text-muted-foreground">
          Track your performance across platforms
        </p>
      </div>

      {/* Overview Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {overviewStats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-muted-foreground">
                  {stat.label}
                </span>
                <stat.icon className="h-4 w-4 text-muted-foreground" />
              </div>
              <div className="flex items-end gap-2">
                <span className="text-2xl font-semibold">{stat.value}</span>
                <Badge variant={stat.up ? "success" : "destructive"} className="text-[10px]">
                  {stat.up ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                  {stat.change}
                </Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Analytics Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Top Tracks */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base font-medium">Top Tracks</CardTitle>
              <Tabs defaultValue="7d" className="w-auto">
                <TabsList className="h-7">
                  <TabsTrigger value="24h" className="text-xs">24h</TabsTrigger>
                  <TabsTrigger value="7d" className="text-xs">7d</TabsTrigger>
                  <TabsTrigger value="30d" className="text-xs">30d</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topTracks.map((track) => (
                <div key={track.rank} className="flex items-center gap-4">
                  <span className="w-6 text-center text-sm font-medium text-muted-foreground">
                    {track.rank}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{track.title}</p>
                    <p className="text-xs text-muted-foreground">{track.plays} plays</p>
                  </div>
                  <div className="w-24">
                    <Progress value={track.growth} className="h-1" />
                  </div>
                  <Badge variant="success" className="text-xs">
                    {track.change}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Platform Breakdown */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-medium">Platforms</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {platformBreakdown.map((item) => (
                <div key={item.platform}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">{item.platform}</span>
                    <span className="text-sm font-medium">{item.streams}</span>
                  </div>
                  <Progress value={item.percentage} className="h-1.5" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Geographic Distribution */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-medium">Geographic Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-5">
            {geographicData.map((item) => (
              <div key={item.region} className="text-center">
                <p className="text-lg font-semibold">{item.listeners}</p>
                <p className="text-xs text-muted-foreground mb-2">{item.region}</p>
                <div className="h-1 rounded-full bg-surface-3 overflow-hidden">
                  <div
                    className="h-full bg-primary"
                    style={{ width: `${item.percentage * 2}%` }}
                  />
                </div>
                <p className="text-[10px] text-muted-foreground mt-1">{item.percentage}%</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}