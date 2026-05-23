"""
Brand DNA page for visual identity management
"""
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Palette,
  Plus,
  Eye,
  Edit,
  Copy,
} from "lucide-react"

const brandProfiles = [
  {
    id: 1,
    name: "Main Brand",
    description: "Primary brand identity for all content",
    colors: ["#0ea5e9", "#ffffff", "#18181b", "#3f3f46"],
    fonts: ["Inter", "JetBrains Mono"],
    status: "active",
    assets: 24,
  },
  {
    id: 2,
    name: "Summer Campaign",
    description: "Summer 2024 release campaign",
    colors: ["#f59e0b", "#fef3c7", "#1f2937"],
    fonts: ["Outfit", "Space Grotesk"],
    status: "active",
    assets: 8,
  },
  {
    id: 3,
    name: "Acoustic Series",
    description: "Acoustic EP visual identity",
    colors: ["#10b981", "#f0fdf4", "#064e3b"],
    fonts: ["Playfair Display", "Source Sans Pro"],
    status: "draft",
    assets: 3,
  },
]

const colorPalettes = [
  { name: "Primary", hex: "#0ea5e9", label: "Electric Blue" },
  { name: "Secondary", hex: "#18181b", label: "Slate" },
  { name: "Accent", hex: "#ffffff", label: "White" },
  { name: "Muted", hex: "#3f3f46", label: "Gray" },
]

export default function BrandPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Brand DNA</h1>
          <p className="text-sm text-muted-foreground">
            Manage your visual identity and brand assets
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Brand Profile
        </Button>
      </div>

      {/* Brand Profiles */}
      <div className="grid gap-4 md:grid-cols-3">
        {brandProfiles.map((profile) => (
          <Card key={profile.id} className="hover:bg-surface-2 transition-colors cursor-pointer">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-md bg-surface-2">
                  <Palette className="h-6 w-6 text-muted-foreground" />
                </div>
                <Badge variant={profile.status === "active" ? "success" : "default"}>
                  {profile.status}
                </Badge>
              </div>
              <h3 className="text-sm font-semibold mb-1">{profile.name}</h3>
              <p className="text-xs text-muted-foreground mb-4">{profile.description}</p>
              
              {/* Color Preview */}
              <div className="flex gap-1 mb-4">
                {profile.colors.map((color, i) => (
                  <div
                    key={i}
                    className="h-6 w-6 rounded-sm border border-border"
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>

              {/* Fonts */}
              <div className="flex gap-2 mb-4">
                {profile.fonts.map((font, i) => (
                  <Badge key={i} variant="outline" className="text-[10px]">
                    {font}
                  </Badge>
                ))}
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-border">
                <span className="text-xs text-muted-foreground">{profile.assets} assets</span>
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" className="h-7 w-7">
                    <Eye className="h-3.5 w-3.5" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-7 w-7">
                    <Edit className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Color System */}
      <Card>
        <CardContent className="p-5">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-base font-medium">Color System</h2>
            <Button variant="outline" size="sm">Add Color</Button>
          </div>
          <div className="grid gap-6 md:grid-cols-4">
            {colorPalettes.map((color) => (
              <div key={color.name} className="text-center">
                <div
                  className="h-16 w-16 rounded-lg mx-auto mb-3 border border-border"
                  style={{ backgroundColor: color.hex }}
                />
                <p className="text-sm font-medium">{color.name}</p>
                <p className="text-xs text-muted-foreground font-mono">{color.hex}</p>
                <p className="text-xs text-muted-foreground">{color.label}</p>
                <div className="flex justify-center gap-2 mt-3">
                  <Button variant="ghost" size="sm">
                    <Copy className="h-3 w-3 mr-1" />
                    Copy
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Typography System */}
      <Card>
        <CardContent className="p-5">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-base font-medium">Typography</h2>
            <Button variant="outline" size="sm">Manage Fonts</Button>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-md border border-border">
              <div>
                <p className="text-lg font-semibold">Inter</p>
                <p className="text-xs text-muted-foreground">Primary font for all UI</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-semibold">Aa Bb Cc</p>
              </div>
            </div>
            <div className="flex items-center justify-between p-4 rounded-md border border-border">
              <div>
                <p className="text-lg font-semibold font-mono">JetBrains Mono</p>
                <p className="text-xs text-muted-foreground">Code and technical content</p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-mono font-semibold">Aa Bb Cc</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}