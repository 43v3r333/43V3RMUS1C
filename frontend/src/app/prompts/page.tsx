"""
Prompts page for AI prompt management
*/
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import {
  Plus,
  Search,
  MoreHorizontal,
  MessageSquare,
  Sparkles,
  Music,
  Image,
  FileText,
  Copy,
  Edit,
  Trash2,
} from "lucide-react"

const prompts = [
  {
    id: 1,
    name: "TTS - Professional Voice",
    type: "tts",
    template: "Generate a professional voice over for: {text}. Style: {style}",
    variables: ["text", "style"],
    category: "Voice",
    useCount: 156,
  },
  {
    id: 2,
    name: "Album Art Generation",
    type: "visual",
    template: "Create an album cover for {album_name} in {style} style, featuring {theme}",
    variables: ["album_name", "style", "theme"],
    category: "Visual",
    useCount: 89,
  },
  {
    id: 3,
    name: "Social Caption",
    type: "text",
    template: "Generate an engaging social media caption for {content_type} about {topic}",
    variables: ["content_type", "topic"],
    category: "Marketing",
    useCount: 234,
  },
  {
    id: 4,
    name: "Music Description",
    type: "music",
    template: "Describe this track: {track_description}. Include mood: {mood}, genre: {genre}",
    variables: ["track_description", "mood", "genre"],
    category: "Music",
    useCount: 67,
  },
]

const categories = [
  { name: "All", count: 12 },
  { name: "Voice", count: 3 },
  { name: "Visual", count: 4 },
  { name: "Marketing", count: 3 },
  { name: "Music", count: 2 },
]

const typeIcons = {
  tts: MessageSquare,
  visual: Image,
  text: FileText,
  music: Music,
}

export default function PromptsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Prompt Library</h1>
          <p className="text-sm text-muted-foreground">
            Manage your AI prompt templates
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Prompt
        </Button>
      </div>

      {/* Search and Filter */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder="Search prompts..." className="pl-9" />
        </div>
        <Button variant="outline">Import</Button>
      </div>

      {/* Categories */}
      <div className="flex gap-2">
        {categories.map((cat) => (
          <Badge
            key={cat.name}
            variant={cat.name === "All" ? "primary" : "default"}
            className="cursor-pointer"
          >
            {cat.name} ({cat.count})
          </Badge>
        ))}
      </div>

      {/* Prompts Grid */}
      <div className="grid gap-4 md:grid-cols-2">
        {prompts.map((prompt) => {
          const TypeIcon = typeIcons[prompt.type as keyof typeof typeIcons] || MessageSquare

          return (
            <Card key={prompt.id} className="hover:bg-surface-2 transition-colors">
              <CardContent className="p-5">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-md bg-surface-2">
                      <TypeIcon className="h-5 w-5 text-muted-foreground" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold">{prompt.name}</h3>
                      <Badge variant="default" className="mt-1 text-[10px]">
                        {prompt.category}
                      </Badge>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>

                <p className="text-xs text-muted-foreground mb-4 line-clamp-2 font-mono bg-surface-2 p-2 rounded">
                  {prompt.template}
                </p>

                <div className="flex items-center justify-between">
                  <div className="flex gap-1">
                    {prompt.variables.map((v) => (
                      <Badge key={v} variant="outline" className="text-[10px]">
                        {v}
                      </Badge>
                    ))}
                  </div>
                  <span className="text-xs text-muted-foreground">
                    Used {prompt.useCount}x
                  </span>
                </div>

                <div className="flex gap-2 mt-4 pt-4 border-t border-border">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Copy className="mr-2 h-3 w-3" />
                    Duplicate
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    <Edit className="mr-2 h-3 w-3" />
                    Edit
                  </Button>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}