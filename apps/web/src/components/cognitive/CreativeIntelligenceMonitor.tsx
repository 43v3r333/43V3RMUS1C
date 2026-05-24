"""
Creative Intelligence Monitor - Cinematic creative cognition interface.
"""
'use client'

import { useState, useEffect } from 'react'
import {
  Layers,
  Music,
  Film,
  Target,
  TrendingUp,
  Clock,
  Sparkles,
  Eye,
  Gauge,
  BarChart3,
} from 'lucide-react'
import { useCognitiveApi, type CreativeProfile, type NarrativeSequence } from '@/lib/cognitive-api'
import { ConsolePanel, DataTable, MetricGrid, StatusDot, ConfidenceBadge, IconButton, ProgressBar, Sparkline, TabBar } from './primitives'

interface EmotionCurvePoint {
  t: number
  energy: number
}

interface BeatData {
  beat_id: string
  position: number
  duration: number
  energy: number
  type: string
}

export default function CreativeIntelligenceMonitor() {
  const api = useCognitiveApi()
  const [activeTab, setActiveTab] = useState('profiles')
  const [profiles, setProfiles] = useState<CreativeProfile[]>([])
  const [sequences, setSequences] = useState<NarrativeSequence[]>([])
  const [selectedProfile, setSelectedProfile] = useState<CreativeProfile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const profs = await api.listCreativeProfiles().catch(() => [])
        const seqs = await api.listNarrativeSequences({}).catch(() => [])
        setProfiles(profs)
        setSequences(seqs)
        if (profs.length > 0) setSelectedProfile(profs[0])
      } catch {
        setProfiles([
          { id: 'p1', name: 'Summer Campaign 2024', campaign_id: 'sc-2024', narrative_structure: 'three_act', emotional_arc: 'rags_to_riches', pacing_profile: 'rollercoaster', visual_keywords: ['sunset', 'high-energy', 'vibrant'], audio_keywords: ['electronic', 'bass-heavy', 'driving'], color_palette: ['#ff6b35', '#f7c59f', '#2a9d8f'], target_segments: ['gen_z', 'millennial'], attention_span_seconds: 45, completion_rate_target: 0.65, engagement_rate_target: 0.18, is_active: true, version: 1, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
          { id: 'p2', name: 'Acoustic Sessions', campaign_id: 'ac-2024', narrative_structure: 'linear', emotional_arc: 'steady', pacing_profile: 'minimalist', visual_keywords: ['warm', 'intimate', 'natural'], audio_keywords: ['acoustic', 'vocal', 'minimal'], color_palette: ['#e9c46a', '#f4a261', '#264653'], target_segments: ['millennial', 'music_superfan'], attention_span_seconds: 120, completion_rate_target: 0.82, engagement_rate_target: 0.35, is_active: true, version: 2, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
        ])
        setSequences([
          { id: 's1', name: 'arc_20240115_001', campaign_id: 'sc-2024', structure: 'three_act', emotional_arc: 'rags_to_riches', beats: [], beat_count: 8, target_duration: 240, target_bpm: 128, creative_score: 0.82, confidence: 0.88, is_locked: false, version: 1, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
          { id: 's2', name: 'arc_20240114_002', campaign_id: 'ac-2024', structure: 'linear', emotional_arc: 'steady', beats: [], beat_count: 5, target_duration: 180, target_bpm: 95, creative_score: 0.79, confidence: 0.85, is_locked: true, version: 1, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
        ])
        setSelectedProfile({
          id: 'p1', name: 'Summer Campaign 2024', campaign_id: 'sc-2024', narrative_structure: 'three_act', emotional_arc: 'rags_to_riches', pacing_profile: 'rollercoaster', visual_keywords: ['sunset', 'high-energy', 'vibrant'], audio_keywords: ['electronic', 'bass-heavy', 'driving'], color_palette: ['#ff6b35', '#f7c59f', '#2a9d8f'], target_segments: ['gen_z', 'millennial'], attention_span_seconds: 45, completion_rate_target: 0.65, engagement_rate_target: 0.18, is_active: true, version: 1, created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
        })
      }
      setLoading(false)
    }
    load()
  }, [api])

  const generateBeats = (count: number, structure: string): BeatData[] => {
    const types = structure === 'three_act' ? ['intro', 'verse', 'chorus', 'bridge', 'outro'] : ['intro', 'verse', 'chorus', 'outro']
    return Array.from({ length: count }, (_, i) => ({
      beat_id: `beat_${i}`,
      position: (i + 1) / count,
      duration: 4 + Math.random() * 3,
      energy: Math.sin((i / count) * Math.PI * 2) * 0.3 + 0.6,
      type: types[Math.floor((i / count) * types.length)] || 'interlude',
    }))
  }

  const generateEmotionCurve = (arc: string): EmotionCurvePoint[] => {
    if (arc === 'rags_to_riches') {
      return Array.from({ length: 10 }, (_, i) => ({ t: i / 9, energy: 0.1 + (i / 9) * 0.9 }))
    } else if (arc === 'man_in_hole') {
      return Array.from({ length: 10 }, (_, i) => ({ t: i / 9, energy: i < 5 ? 0.8 - (i / 5) * 0.5 : 0.3 + ((i - 5) / 5) * 0.7 }))
    } else {
      return Array.from({ length: 10 }, (_, i) => ({ t: i / 9, energy: 0.5 + Math.sin((i / 9) * Math.PI * 1.5) * 0.3 }))
    }
  }

  const beats = selectedProfile ? generateBeats(8, selectedProfile.narrative_structure) : []
  const emotionCurve = selectedProfile ? generateEmotionCurve(selectedProfile.emotional_arc) : []

  const tabs = [
    { id: 'profiles', label: 'Profiles', icon: <Layers className="h-3 w-3" />, badge: profiles.length },
    { id: 'sequences', label: 'Sequences', icon: <Film className="h-3 w-3" />, badge: sequences.length },
    { id: 'emotion', label: 'Emotion', icon: <Music className="h-3 w-3" /> },
    { id: 'audience', label: 'Audience', icon: <Target className="h-3 w-3" /> },
  ]

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 border border-primary/20">
            <Layers className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Creative Intelligence Monitor</h1>
            <p className="text-xs text-muted-foreground">Cinematic creative cognition and narrative sequencing</p>
          </div>
        </div>
        <IconButton icon={<Sparkles className="h-3.5 w-3.5" />} title="Generate Arc" />
      </div>

      {/* Summary */}
      <div className="grid grid-cols-5 gap-2">
        {[
          { label: 'Active Profiles', value: profiles.length, icon: <Layers className="h-3.5 w-3.5" /> },
          { label: 'Sequences', value: sequences.length, icon: <Film className="h-3.5 w-3.5" /> },
          { label: 'Avg Creative Score', value: '81%', icon: <Sparkles className="h-3.5 w-3.5" /> },
          { label: 'Avg Engagement', value: '26%', icon: <Target className="h-3.5 w-3.5" /> },
          { label: 'Locked', value: sequences.filter(s => s.is_locked).length, icon: <Gauge className="h-3.5 w-3.5" /> },
        ].map((stat, i) => (
          <div key={i} className="rounded border border-border bg-card px-3 py-2">
            <div className="flex items-center gap-1.5 mb-0.5">
              <span className="text-muted-foreground">{stat.icon}</span>
              <span className="text-[10px] text-muted-foreground uppercase tracking-wider">{stat.label}</span>
            </div>
            <div className="text-lg font-mono font-semibold">{stat.value}</div>
          </div>
        ))}
      </div>

      <TabBar tabs={tabs} active={activeTab} onChange={setActiveTab} />

      {activeTab === 'profiles' && (
        <div className="grid gap-4 lg:grid-cols-3">
          {/* Profile list */}
          <ConsolePanel title="Creative Profiles" icon={<Layers className="h-4 w-4" />} subtitle={`${profiles.length} profiles`}>
            <div className="space-y-1">
              {profiles.map(p => (
                <button
                  key={p.id}
                  onClick={() => setSelectedProfile(p)}
                  className={`w-full text-left px-3 py-2 rounded border transition-colors ${selectedProfile?.id === p.id ? 'border-primary bg-primary/5' : 'border-transparent hover:bg-accent'}`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium">{p.name}</span>
                    {p.is_active && <StatusDot status="active" size="sm" />}
                  </div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-[10px] px-1 py-0.5 rounded bg-muted">{p.narrative_structure}</span>
                    <span className="text-[10px] text-muted-foreground">{p.emotional_arc}</span>
                  </div>
                </button>
              ))}
            </div>
          </ConsolePanel>

          {/* Profile details */}
          <ConsolePanel title="Profile Details" icon={<Eye className="h-4 w-4" />} subtitle={selectedProfile?.name}>
            {selectedProfile && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { label: 'Structure', value: selectedProfile.narrative_structure },
                    { label: 'Emotional Arc', value: selectedProfile.emotional_arc },
                    { label: 'Pacing', value: selectedProfile.pacing_profile },
                    { label: 'Target BPM', value: selectedProfile.target_bpm?.toString() || '-' },
                  ].map(field => (
                    <div key={field.label}>
                      <div className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">{field.label}</div>
                      <div className="text-xs font-medium capitalize">{field.value}</div>
                    </div>
                  ))}
                </div>
                <div>
                  <div className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2">Color Palette</div>
                  <div className="flex gap-1.5">
                    {selectedProfile.color_palette.map((c, i) => (
                      <div key={i} className="h-6 w-6 rounded" style={{ backgroundColor: c }} title={c} />
                    ))}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2">Target Segments</div>
                  <div className="flex gap-1.5">
                    {selectedProfile.target_segments.map((s, i) => (
                      <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{s}</span>
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3 pt-2 border-t border-border">
                  <div>
                    <div className="text-[10px] text-muted-foreground mb-1">Completion Target</div>
                    <div className="text-sm font-mono font-semibold">{Math.round(selectedProfile.completion_rate_target * 100)}%</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-muted-foreground mb-1">Engagement Target</div>
                    <div className="text-sm font-mono font-semibold">{Math.round(selectedProfile.engagement_rate_target * 100)}%</div>
                  </div>
                </div>
              </div>
            )}
          </ConsolePanel>

          {/* Keywords */}
          <ConsolePanel title="Style Keywords" icon={<Sparkles className="h-4 w-4" />} subtitle="Visual, audio, and tonal descriptors">
            {selectedProfile && (
              <div className="space-y-4">
                <div>
                  <div className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2">Visual</div>
                  <div className="flex flex-wrap gap-1">
                    {selectedProfile.visual_keywords.map((k, i) => (
                      <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-secondary border border-border">{k}</span>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] text-muted-foreground uppercase tracking-wider mb-2">Audio</div>
                  <div className="flex flex-wrap gap-1">
                    {selectedProfile.audio_keywords.map((k, i) => (
                      <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{k}</span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </ConsolePanel>
        </div>
      )}

      {activeTab === 'sequences' && (
        <div className="grid gap-4 lg:grid-cols-2">
          <ConsolePanel title="Narrative Sequences" icon={<Film className="h-4 w-4" />} subtitle="Scene/story arc plans">
            <DataTable
              columns={[
                { key: 'name', label: 'Name', width: '25%' },
                { key: 'structure', label: 'Structure', width: '15%' },
                { key: 'arc', label: 'Emotion Arc', width: '15%' },
                { key: 'beats', label: 'Beats', width: '10%' },
                { key: 'duration', label: 'Duration', width: '15%' },
                { key: 'score', label: 'Score', width: '10%' },
                { key: 'locked', label: 'Status', width: '10%' },
              ]}
              rows={sequences.map(s => ({
                name: <span className="font-mono text-xs">{s.name}</span>,
                structure: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{s.structure}</span>,
                arc: <span className="text-xs">{s.emotional_arc}</span>,
                beats: <span className="font-mono">{s.beat_count}</span>,
                duration: <span className="font-mono">{s.target_duration.toFixed(0)}s</span>,
                score: <ConfidenceBadge value={s.creative_score} showLabel={false} />,
                locked: s.is_locked ? <span className="text-[10px] px-1.5 py-0.5 rounded bg-yellow-500/10 text-yellow-500">LOCKED</span> : <span className="text-[10px] text-muted-foreground">DRAFT</span>,
              }))}
            />
          </ConsolePanel>

          <ConsolePanel title="Beat Timeline" icon={<BarChart3 className="h-4 w-4" />} subtitle="Visual timeline of narrative beats">
            <div className="space-y-1">
              {beats.map((beat, i) => (
                <div key={beat.beat_id} className="flex items-center gap-3 py-1.5 border-b border-border/50 last:border-0">
                  <span className="text-[10px] font-mono text-muted-foreground w-6">{i + 1}</span>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-0.5">
                      <span className="text-xs font-medium">{beat.type}</span>
                      <span className="text-[10px] font-mono text-muted-foreground">{beat.duration.toFixed(1)}s</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                      <div className="h-full bg-primary" style={{ width: `${beat.energy * 100}%` }} />
                    </div>
                  </div>
                  <span className="text-[10px] font-mono w-8 text-right text-muted-foreground">{(beat.position * 100).toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </ConsolePanel>
        </div>
      )}

      {activeTab === 'emotion' && (
        <div className="grid gap-4 lg:grid-cols-2">
          <ConsolePanel title="Emotional Arc" icon={<Music className="h-4 w-4" />} subtitle="Energy curve visualization">
            <div className="h-40 relative">
              <svg width="100%" height="100%" className="overflow-visible">
                {emotionCurve.length > 1 && (
                  <polyline
                    points={emotionCurve.map((p, i) => {
                      const x = (i / (emotionCurve.length - 1)) * 100
                      const y = (1 - p.energy) * 100
                      return `${x}%,${y}%`
                    }).join(' ')}
                    fill="none"
                    stroke="var(--primary)"
                    strokeWidth="2"
                    strokeLinejoin="round"
                    strokeLinecap="round"
                  />
                )}
              </svg>
              <div className="absolute bottom-0 left-0 right-0 flex justify-between text-[9px] text-muted-foreground px-1">
                <span>0%</span>
                <span>25%</span>
                <span>50%</span>
                <span>75%</span>
                <span>100%</span>
              </div>
            </div>
            <div className="flex items-center justify-between mt-2 text-[10px] text-muted-foreground">
              <span>Start</span>
              <span>Middle</span>
              <span>End</span>
            </div>
          </ConsolePanel>

          <ConsolePanel title="Pacing Profile" icon={<Clock className="h-4 w-4" />} subtitle="Tempo and energy distribution">
            <div className="space-y-3">
              {['bruiser', 'rollercoaster', 'building', 'minimalist'].map(pacing => {
                const mockData = Array.from({ length: 10 }, (_, i) => {
                  if (pacing === 'bruiser') return 0.75 + Math.random() * 0.15
                  if (pacing === 'rollercoaster') return Math.sin((i / 9) * Math.PI * 2) * 0.3 + 0.5
                  if (pacing === 'building') return 0.2 + (i / 9) * 0.7
                  return 0.4 + Math.random() * 0.1
                })
                return (
                  <div key={pacing} className="flex items-center gap-3">
                    <span className="text-[10px] font-mono w-20 text-muted-foreground capitalize">{pacing}</span>
                    <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
                      <div className="h-full bg-primary" style={{ width: `${(mockData.reduce((a, b) => a + b, 0) / mockData.length) * 100}%`, opacity: selectedProfile?.pacing_profile === pacing ? 1 : 0.4 }} />
                    </div>
                  </div>
                )
              })}
            </div>
          </ConsolePanel>
        </div>
      )}

      {activeTab === 'audience' && (
        <div className="grid gap-4 lg:grid-cols-2">
          <ConsolePanel title="Audience Segments" icon={<Target className="h-4 w-4" />} subtitle="Target engagement profiles">
            <DataTable
              columns={[
                { key: 'segment', label: 'Segment', width: '20%' },
                { key: 'content_type', label: 'Content Type', width: '15%' },
                { key: 'completion', label: 'Completion', width: '20%' },
                { key: 'engagement', label: 'Engagement', width: '20%' },
                { key: 'drop_off', label: 'First Drop', width: '15%' },
              ]}
              rows={[
                { segment: 'gen_z', content_type: 'short_form', completion: '72%', engagement: '18%', drop_off: '3s' },
                { segment: 'millennial', content_type: 'music_video', completion: '81%', engagement: '22%', drop_off: '5s' },
                { segment: 'music_superfan', content_type: 'long_form', completion: '89%', engagement: '35%', drop_off: '8s' },
                { segment: 'tiktok_native', content_type: 'short_form', completion: '78%', engagement: '24%', drop_off: '2s' },
              ].map(row => ({
                segment: <span className="text-xs font-mono">{row.segment}</span>,
                content_type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{row.content_type}</span>,
                completion: <span className="font-mono">{row.completion}</span>,
                engagement: <span className="font-mono">{row.engagement}</span>,
                drop_off: <span className="font-mono text-muted-foreground">{row.drop_off}</span>,
              }))}
            />
          </ConsolePanel>

          <ConsolePanel title="Retention Curve" icon={<TrendingUp className="h-4 w-4" />} subtitle="Expected retention over time">
            <div className="space-y-3">
              {[
                { segment: 'Gen Z', data: [1, 0.95, 0.88, 0.75, 0.65, 0.55, 0.48, 0.42, 0.38, 0.35] },
                { segment: 'Millennial', data: [1, 0.98, 0.92, 0.84, 0.78, 0.72, 0.68, 0.64, 0.61, 0.58] },
                { segment: 'Superfan', data: [1, 0.99, 0.96, 0.92, 0.88, 0.85, 0.82, 0.80, 0.78, 0.76] },
              ].map(seg => (
                <div key={seg.segment} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">{seg.segment}</span>
                    <span className="font-mono">{Math.round(seg.data[seg.data.length - 1] * 100)}%</span>
                  </div>
                  <div className="flex gap-0.5">
                    {seg.data.map((v, i) => (
                      <div key={i} className="h-6 flex-1 rounded-sm bg-muted overflow-hidden">
                        <div className="h-full bg-primary" style={{ height: `${v * 100}%`, opacity: i === seg.data.length - 1 ? 1 : 0.5 }} />
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </ConsolePanel>
        </div>
      )}
    </div>
  )
}