"""
Timeline View - Professional timeline workspace
"""
'use client'

import { useState, useRef, useCallback, useEffect } from 'react'
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
} from 'lucide-react'

interface TimelineTrack {
  id: string
  name: string
  type: 'video' | 'audio' | 'text' | 'effect'
  muted: boolean
  locked: boolean
  clips: TimelineClip[]
}

interface TimelineClip {
  id: string
  name: string
  start: number
  duration: number
  sourceStart: number
  sourceEnd: number
  color: string
}

interface TimelineViewProps {
  tracks: TimelineTrack[]
  duration: number
  frameRate: number
  currentTime: number
  onTimeChange: (time: number) => void
  onClipSelect?: (clipId: string) => void
  onClipMove?: (clipId: string, newStart: number) => void
  onAddTrack?: (type: string) => void
}

export function TimelineView({
  tracks,
  duration,
  frameRate,
  currentTime,
  onTimeChange,
  onClipSelect,
  onClipMove,
  onAddTrack,
}: TimelineViewProps) {
  const [zoom, setZoom] = useState(1)
  const [selectedClipId, setSelectedClipId] = useState<string | null>(null)
  const timelineRef = useRef<HTMLDivElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)

  const pixelsPerSecond = 100 * zoom
  const timelineWidth = duration * pixelsPerSecond

  const formatTimecode = (seconds: number) => {
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = Math.floor(seconds % 60)
    const f = Math.floor((seconds % 1) * frameRate)
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}:${f.toString().padStart(2, '0')}`
  }

  const handleTimelineClick = useCallback((e: React.MouseEvent) => {
    if (!timelineRef.current) return
    const rect = timelineRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const time = x / pixelsPerSecond
    onTimeChange(Math.max(0, Math.min(duration, time)))
  }, [pixelsPerSecond, duration, onTimeChange])

  const handleClipClick = useCallback((e: React.MouseEvent, clipId: string) => {
    e.stopPropagation()
    setSelectedClipId(clipId)
    onClipSelect?.(clipId)
  }, [onClipSelect])

  const handleZoom = (delta: number) => {
    setZoom((z) => Math.max(0.1, Math.min(10, z + delta)))
  }

  // Playback simulation
  useEffect(() => {
    if (!isPlaying) return
    const interval = setInterval(() => {
      onTimeChange((t) => {
        if (t >= duration) {
          setIsPlaying(false)
          return 0
        }
        return t + 1 / 30
      })
    }, 1000 / 30)
    return () => clearInterval(interval)
  }, [isPlaying, duration, onTimeChange])

  return (
    <div className="flex flex-col h-full bg-card">
      {/* Toolbar */}
      <div className="flex items-center gap-2 px-4 py-2 border-b border-border">
        <div className="flex items-center gap-1">
          <button
            onClick={() => onTimeChange(0)}
            className="p-2 hover:bg-accent rounded"
            title="Go to start"
          >
            <SkipBack className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-2 hover:bg-accent rounded"
            title={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? (
              <Pause className="w-4 h-4" />
            ) : (
              <Play className="w-4 h-4" />
            )}
          </button>
          <button
            onClick={() => onTimeChange(duration)}
            className="p-2 hover:bg-accent rounded"
            title="Go to end"
          >
            <SkipForward className="w-4 h-4" />
          </button>
        </div>

        <div className="w-px h-6 bg-border" />

        <div className="flex items-center gap-1">
          <button
            onClick={() => handleZoom(-0.5)}
            className="p-2 hover:bg-accent rounded"
            title="Zoom out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-xs text-muted-foreground w-12 text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={() => handleZoom(0.5)}
            className="p-2 hover:bg-accent rounded"
            title="Zoom in"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
        </div>

        <div className="w-px h-6 bg-border" />

        <div className="flex items-center gap-1">
          <button
            onClick={() => onAddTrack?.('video')}
            className="p-2 hover:bg-accent rounded"
            title="Add video track"
          >
            <Plus className="w-4 h-4" />
            <span className="text-xs ml-1">Video</span>
          </button>
          <button
            onClick={() => onAddTrack?.('audio')}
            className="p-2 hover:bg-accent rounded"
            title="Add audio track"
          >
            <Plus className="w-4 h-4" />
            <span className="text-xs ml-1">Audio</span>
          </button>
        </div>

        <div className="flex-1" />

        {/* Timecode display */}
        <div className="font-mono text-sm bg-muted px-3 py-1 rounded">
          {formatTimecode(currentTime)}
        </div>
      </div>

      {/* Timeline area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Track headers */}
        <div className="w-48 flex-shrink-0 border-r border-border overflow-y-auto">
          <div className="h-8 border-b border-border" /> {/* Time ruler space */}
          {tracks.map((track) => (
            <div
              key={track.id}
              className="h-16 px-2 border-b border-border flex items-center gap-2"
            >
              <div
                className={`w-1 h-8 rounded ${
                  track.type === 'video' ? 'bg-blue-500' :
                  track.type === 'audio' ? 'bg-green-500' :
                  track.type === 'text' ? 'bg-purple-500' :
                  'bg-orange-500'
                }`}
              />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{track.name}</p>
                <p className="text-xs text-muted-foreground capitalize">
                  {track.type}
                </p>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => {/* Toggle mute */}
                  }}
                  className={`p-1 rounded ${track.muted ? 'text-red-500' : 'text-muted-foreground'}`}
                >
                  {track.muted ? 'M' : ''}
                </button>
                <button
                  onClick={() => {/* Toggle lock */}
                  }}
                  className={`p-1 rounded ${track.locked ? 'text-yellow-500' : 'text-muted-foreground'}`}
                >
                  L
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Timeline content */}
        <div className="flex-1 overflow-auto">
          <div
            ref={timelineRef}
            className="relative"
            style={{ width: timelineWidth, minHeight: '100%' }}
            onClick={handleTimelineClick}
          >
            {/* Time ruler */}
            <div className="sticky top-0 h-8 bg-card border-b border-border z-10 flex">
              {Array.from({ length: Math.ceil(duration) }).map((_, i) => (
                <div
                  key={i}
                  className="flex-shrink-0 border-l border-border pl-1"
                  style={{ width: pixelsPerSecond }}
                >
                  <span className="text-xs text-muted-foreground">
                    {i}s
                  </span>
                </div>
              ))}
            </div>

            {/* Tracks and clips */}
            {tracks.map((track) => (
              <div
                key={track.id}
                className="h-16 border-b border-border relative"
              >
                {track.clips.map((clip) => (
                  <div
                    key={clip.id}
                    onClick={(e) => handleClipClick(e, clip.id)}
                    className={`absolute top-1 h-14 rounded cursor-pointer transition-colors ${
                      selectedClipId === clip.id
                        ? 'ring-2 ring-primary'
                        : 'hover:ring-1 hover:ring-border'
                    }`}
                    style={{
                      left: clip.start * pixelsPerSecond,
                      width: clip.duration * pixelsPerSecond,
                      backgroundColor: clip.color,
                    }}
                  >
                    <div className="px-2 py-1 overflow-hidden">
                      <p className="text-xs font-medium truncate text-white drop-shadow">
                        {clip.name}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ))}

            {/* Playhead */}
            <div
              className="absolute top-0 bottom-0 w-px bg-red-500 z-20 pointer-events-none"
              style={{ left: currentTime * pixelsPerSecond }}
            >
              <div className="w-3 h-3 bg-red-500 -translate-x-1/2" />
            </div>
          </div>
        </div>
      </div>

      {/* Status bar */}
      <div className="flex items-center justify-between px-4 py-1 border-t border-border bg-card/50">
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <span>{tracks.length} tracks</span>
          <span>{tracks.reduce((acc, t) => acc + t.clips.length, 0)} clips</span>
        </div>
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <span>{frameRate} fps</span>
          <span>{Math.round(duration)}s</span>
        </div>
      </div>
    </div>
  )
}