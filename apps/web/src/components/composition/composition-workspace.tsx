"""
Composition Workspace - Cinematic composition editor
"""
'use client'

import { useState, useEffect, useRef } from 'react'
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Plus,
  Trash2,
  Layers,
  Scissors,
  Magnet,
  ZoomIn,
  ZoomOut,
  Film,
  Music,
  Type,
  Image,
  Clock,
  Volume2,
  Move,
  RotateCcw,
  Maximize2,
} from 'lucide-react'

interface SceneData {
  id: string
  name: string
  type: 'intro' | 'verse' | 'chorus' | 'bridge' | 'outro' | 'interlude' | 'transition'
  start_time: number
  duration: number
  color: string
  clips: ClipData[]
}

interface ClipData {
  id: string
  name: string
  type: 'video' | 'audio' | 'image'
  start_time: number
  duration: number
  track_index: number
  source_id?: string
}

interface OverlayData {
  id: string
  type: 'text' | 'image' | 'shape'
  content: string
  start_time: number
  duration: number
  position_x: number
  position_y: number
}

interface CompositionWorkspaceProps {
  graphId?: string
}

export function CompositionWorkspace({ graphId }: CompositionWorkspaceProps) {
  const [scenes, setScenes] = useState<SceneData[]>([])
  const [clips, setClips] = useState<ClipData[]>([])
  const [overlays, setOverlays] = useState<OverlayData[]>([])
  const [currentTime, setCurrentTime] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [zoom, setZoom] = useState(1)
  const [selectedScene, setSelectedScene] = useState<string | null>(null)
  const [bpm, setBpm] = useState(120)
  const timelineRef = useRef<HTMLDivElement>(null)

  // Initialize with sample data
  useEffect(() => {
    setScenes([
      { id: 'scene-1', name: 'Intro', type: 'intro', start_time: 0, duration: 8, color: '#3b82f6', clips: [] },
      { id: 'scene-2', name: 'Verse 1', type: 'verse', start_time: 8, duration: 16, color: '#8b5cf6', clips: [] },
      { id: 'scene-3', name: 'Chorus', type: 'chorus', start_time: 24, duration: 16, color: '#ec4899', clips: [] },
      { id: 'scene-4', name: 'Verse 2', type: 'verse', start_time: 40, duration: 16, color: '#8b5cf6', clips: [] },
      { id: 'scene-5', name: 'Bridge', type: 'bridge', start_time: 56, duration: 8, color: '#06b6d4', clips: [] },
      { id: 'scene-6', name: 'Chorus 2', type: 'chorus', start_time: 64, duration: 16, color: '#ec4899', clips: [] },
      { id: 'scene-7', name: 'Outro', type: 'outro', start_time: 80, duration: 8, color: '#3b82f6', clips: [] },
    ])

    setClips([
      { id: 'clip-1', name: 'Drums', type: 'audio', start_time: 0, duration: 88, track_index: 0 },
      { id: 'clip-2', name: 'Bass', type: 'audio', start_time: 0, duration: 88, track_index: 1 },
      { id: 'clip-3', name: 'Vocals', type: 'audio', start_time: 8, duration: 72, track_index: 2 },
      { id: 'clip-4', name: 'Synth Lead', type: 'audio', start_time: 24, duration: 64, track_index: 3 },
    ])
  }, [])

  const totalDuration = scenes.reduce((sum, s) => Math.max(sum, s.start_time + s.duration), 0)
  const pixelsPerSecond = 50 * zoom

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60)
    const s = Math.floor(seconds % 60)
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  const handleTimelineClick = (e: React.MouseEvent) => {
    if (!timelineRef.current) return
    const rect = timelineRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left + timelineRef.current.scrollLeft
    const time = x / pixelsPerSecond
    setCurrentTime(Math.max(0, Math.min(totalDuration, time)))
  }

  const handleZoom = (delta: number) => {
    setZoom((z) => Math.max(0.25, Math.min(4, z + delta)))
  }

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-card">
        <div className="flex items-center gap-2">
          <Film className="w-5 h-5 text-primary" />
          <span className="text-sm font-medium">Composition Editor</span>
          {graphId && (
            <span className="text-xs text-muted-foreground ml-2">Graph: {graphId}</span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Playback controls */}
          <div className="flex items-center gap-1">
            <button
              onClick={() => setCurrentTime(0)}
              className="p-2 hover:bg-accent rounded"
              title="Go to start"
            >
              <SkipBack className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="p-2 hover:bg-accent rounded"
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </button>
            <button
              onClick={() => setCurrentTime(totalDuration)}
              className="p-2 hover:bg-accent rounded"
              title="Go to end"
            >
              <SkipForward className="w-4 h-4" />
            </button>
          </div>

          <div className="w-px h-6 bg-border mx-2" />

          {/* Zoom controls */}
          <div className="flex items-center gap-1">
            <button onClick={() => handleZoom(-0.25)} className="p-2 hover:bg-accent rounded">
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="text-xs w-12 text-center">{Math.round(zoom * 100)}%</span>
            <button onClick={() => handleZoom(0.25)} className="p-2 hover:bg-accent rounded">
              <ZoomIn className="w-4 h-4" />
            </button>
          </div>

          <div className="w-px h-6 bg-border mx-2" />

          {/* Add buttons */}
          <button className="flex items-center gap-1 px-2 py-1 text-xs hover:bg-accent rounded" title="Add Scene">
            <Plus className="w-3 h-3" />
            <Film className="w-3 h-3" />
          </button>
          <button className="flex items-center gap-1 px-2 py-1 text-xs hover:bg-accent rounded" title="Add Clip">
            <Plus className="w-3 h-3" />
            <Layers className="w-3 h-3" />
          </button>
          <button className="flex items-center gap-1 px-2 py-1 text-xs hover:bg-accent rounded" title="Add Overlay">
            <Plus className="w-3 h-3" />
            <Type className="w-3 h-3" />
          </button>
        </div>

        <div className="flex items-center gap-4">
          {/* BPM control */}
          <div className="flex items-center gap-2">
            <Music className="w-4 h-4 text-muted-foreground" />
            <input
              type="number"
              value={bpm}
              onChange={(e) => setBpm(Number(e.target.value))}
              className="w-16 text-sm bg-transparent border border-border rounded px-2 py-1 text-center"
            />
            <span className="text-xs text-muted-foreground">BPM</span>
          </div>

          {/* Timecode */}
          <div className="font-mono text-sm bg-muted px-3 py-1 rounded">
            {formatTime(currentTime)} / {formatTime(totalDuration)}
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Scene list sidebar */}
        <div className="w-64 border-r border-border overflow-y-auto bg-card">
          <div className="p-3 border-b border-border">
            <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Scenes</h3>
          </div>
          <div className="divide-y divide-border">
            {scenes.map((scene) => (
              <div
                key={scene.id}
                onClick={() => setSelectedScene(scene.id)}
                className={`px-4 py-3 cursor-pointer hover:bg-card/50 ${
                  selectedScene === scene.id ? 'bg-card' : ''
                }`}
              >
                <div className="flex items-center gap-2">
                  <div
                    className="w-2 h-8 rounded"
                    style={{ backgroundColor: scene.color }}
                  />
                  <div className="flex-1">
                    <p className="text-sm font-medium">{scene.name}</p>
                    <p className="text-xs text-muted-foreground capitalize">{scene.type}</p>
                  </div>
                  <span className="text-xs text-muted-foreground">{formatTime(scene.duration)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Timeline */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Track headers */}
          <div className="flex border-b border-border bg-card">
            <div className="w-32 flex-shrink-0 border-r border-border">
              <div className="h-8 px-2 flex items-center text-xs text-muted-foreground uppercase tracking-wider border-b border-border">
                Time
              </div>
            </div>
            <div className="flex-1 overflow-x-auto">
              <div className="flex" style={{ width: totalDuration * pixelsPerSecond }}>
                <div className="h-8 flex-shrink-0 px-2 flex items-center text-xs text-muted-foreground border-r border-border" style={{ width: pixelsPerSecond }}>
                  0s
                </div>
              </div>
            </div>
          </div>

          {/* Tracks */}
          <div className="flex-1 overflow-auto" ref={timelineRef} onClick={handleTimelineClick}>
            {/* Scene markers */}
            <div className="relative h-12 border-b border-border" style={{ width: totalDuration * pixelsPerSecond }}>
              {scenes.map((scene) => (
                <div
                  key={scene.id}
                  onClick={(e) => { e.stopPropagation(); setCurrentTime(scene.start_time); }}
                  className="absolute top-0 bottom-0 cursor-pointer group"
                  style={{
                    left: scene.start_time * pixelsPerSecond,
                    width: scene.duration * pixelsPerSecond,
                    backgroundColor: `${scene.color}20`,
                    borderLeft: `3px solid ${scene.color}`,
                  }}
                >
                  <div className="px-2 py-1">
                    <span className="text-xs font-medium opacity-60 group-hover:opacity-100">
                      {scene.name}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Audio tracks */}
            {[
              { name: 'Drums', icon: Volume2, color: '#ef4444' },
              { name: 'Bass', icon: Volume2, color: '#f97316' },
              { name: 'Vocals', icon: Volume2, color: '#eab308' },
              { name: 'Synth', icon: Volume2, color: '#22c55e' },
            ].map((track, idx) => (
              <div
                key={track.name}
                className="relative h-16 border-b border-border"
                style={{ width: totalDuration * pixelsPerSecond }}
              >
                {/* Track header */}
                <div className="absolute left-0 top-0 w-32 h-full bg-card border-r border-border flex items-center px-3">
                  <track.icon className="w-4 h-4 mr-2" style={{ color: track.color }} />
                  <span className="text-sm">{track.name}</span>
                </div>
                
                {/* Track clips */}
                <div className="absolute left-32 right-0 top-0 h-full">
                  {clips.filter(c => c.track_index === idx).map((clip) => (
                    <div
                      key={clip.id}
                      className="absolute top-2 h-12 rounded cursor-pointer hover:ring-2 ring-primary transition-all"
                      style={{
                        left: clip.start_time * pixelsPerSecond,
                        width: clip.duration * pixelsPerSecond,
                        backgroundColor: track.color,
                      }}
                    >
                      <div className="px-2 py-1 overflow-hidden">
                        <p className="text-xs text-white truncate font-medium">{clip.name}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {/* Playhead */}
            <div
              className="absolute top-0 bottom-0 w-px bg-red-500 pointer-events-none"
              style={{ left: currentTime * pixelsPerSecond + 128 }}
            >
              <div className="w-3 h-3 bg-red-500 -translate-x-1/2 rounded-sm" />
            </div>
          </div>
        </div>
      </div>

      {/* Bottom panel - Scene details */}
      {selectedScene && (
        <div className="h-32 border-t border-border bg-card">
          <div className="flex items-center justify-between px-4 py-2 border-b border-border">
            <span className="text-sm font-medium">
              Scene Details: {scenes.find(s => s.id === selectedScene)?.name}
            </span>
            <button className="p-1 hover:bg-accent rounded">
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
          <div className="px-4 py-2 flex items-center gap-6">
            <div className="text-xs">
              <span className="text-muted-foreground">Start: </span>
              <span className="font-mono">
                {formatTime(scenes.find(s => s.id === selectedScene)?.start_time || 0)}
              </span>
            </div>
            <div className="text-xs">
              <span className="text-muted-foreground">Duration: </span>
              <span className="font-mono">
                {formatTime(scenes.find(s => s.id === selectedScene)?.duration || 0)}
              </span>
            </div>
            <div className="text-xs">
              <span className="text-muted-foreground">Clips: </span>
              <span className="font-mono">
                {clips.filter(c => 
                  scenes.find(s => s.id === selectedScene) &&
                  c.start_time >= (scenes.find(s => s.id === selectedScene)?.start_time || 0) &&
                  c.start_time < (scenes.find(s => s.id === selectedScene)?.start_time || 0) + (scenes.find(s => s.id === selectedScene)?.duration || 0)
                ).length}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}