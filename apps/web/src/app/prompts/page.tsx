import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Prompts | 43V3R CORE',
  description: 'AI prompt template library',
}

export default function PromptsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">AI Prompts</h1>
          <p className="text-sm text-muted-foreground">
            Reusable prompt templates for AI generation
          </p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
          New Prompt
        </button>
      </div>

      {/* Prompt Categories */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[
          { name: 'Text-to-Speech', count: 8, icon: '🎤' },
          { name: 'Music Generation', count: 12, icon: '🎵' },
          { name: 'Image Generation', count: 15, icon: '🖼️' },
          { name: 'Video Generation', count: 6, icon: '🎬' },
          { name: 'Content Writing', count: 10, icon: '✍️' },
        ].map((category, i) => (
          <div
            key={i}
            className="rounded-lg border border-border bg-card p-4 hover:border-primary/50 transition-colors cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">{category.icon}</span>
              <div>
                <h3 className="font-medium">{category.name}</h3>
                <p className="text-xs text-muted-foreground">{category.count} templates</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}