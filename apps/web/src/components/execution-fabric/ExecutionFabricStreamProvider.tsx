"""
Execution Fabric WebSocket Provider - Real-time execution visibility.

Provides live streaming of:
- Lineage updates
- Topology changes
- Stability metrics
- Cognition pulses
"""
'use client'

import { useState, useEffect, useCallback, useRef } from 'react'

interface StreamMessage {
  type: string
  payload: Record<string, any>
  timestamp: string
  client_id?: string
}

interface UseExecutionFabricStreamOptions {
  url?: string
  autoConnect?: boolean
  streams?: string[]
}

interface UseExecutionFabricStreamReturn {
  isConnected: boolean
  isStreaming: boolean
  subscribe: (streamType: string) => void
  unsubscribe: (streamType: string) => void
  sendMessage: (message: Record<string, any>) => void
  latestMessages: Record<string, StreamMessage>
  connectionStats: {
    connected_at?: string
    messages_received: number
    subscriptions: number
  }
}

export function useExecutionFabricStream(
  options: UseExecutionFabricStreamOptions = {}
): UseExecutionFabricStreamReturn {
  const {
    url = 'ws://localhost:8000/api/v1/execution-fabric/ws',
    autoConnect = true,
    streams = [],
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [latestMessages, setLatestMessages] = useState<Record<string, StreamMessage>>({})
  const [subscriptions, setSubscriptions] = useState<Set<string>>(new Set(streams))
  const [stats, setStats] = useState({
    connected_at: undefined as string | undefined,
    messages_received: 0,
    subscriptions: streams.length,
  })

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    try {
      const ws = new WebSocket(url)

      ws.onopen = () => {
        setIsConnected(true)
        setStats(prev => ({
          ...prev,
          connected_at: new Date().toISOString(),
        }))

        // Subscribe to initial streams
        streams.forEach(stream => {
          ws.send(JSON.stringify({
            type: 'subscribe',
            payload: { stream_type: stream },
          }))
        })
      }

      ws.onmessage = (event) => {
        try {
          const message: StreamMessage = JSON.parse(event.data)
          
          setLatestMessages(prev => ({
            ...prev,
            [message.type]: message,
          }))

          setStats(prev => ({
            ...prev,
            messages_received: prev.messages_received + 1,
          }))
        } catch (e) {
          console.error('Failed to parse message:', e)
        }
      }

      ws.onclose = () => {
        setIsConnected(false)
        setIsStreaming(false)
        
        // Reconnect after 5 seconds
        reconnectTimeoutRef.current = setTimeout(connect, 5000)
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        ws.close()
      }

      wsRef.current = ws
    } catch (e) {
      console.error('Failed to connect:', e)
    }
  }, [url, streams])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    
    setIsConnected(false)
    setIsStreaming(false)
  }, [])

  const subscribe = useCallback((streamType: string) => {
    setSubscriptions(prev => {
      const next = new Set(prev)
      next.add(streamType)
      return next
    })
    
    setStats(prev => ({
      ...prev,
      subscriptions: prev.subscriptions + 1,
    }))

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'subscribe',
        payload: { stream_type: streamType },
      }))
    }
  }, [])

  const unsubscribe = useCallback((streamType: string) => {
    setSubscriptions(prev => {
      const next = new Set(prev)
      next.delete(streamType)
      return next
    })

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'unsubscribe',
        payload: { stream_type: streamType },
      }))
    }
  }, [])

  const sendMessage = useCallback((message: Record<string, any>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    }
  }, [])

  useEffect(() => {
    if (autoConnect) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [autoConnect, connect, disconnect])

  return {
    isConnected,
    isStreaming,
    subscribe,
    unsubscribe,
    sendMessage,
    latestMessages,
    connectionStats: stats,
  }
}

// ============================================================================
// REALTIME STREAM PROVIDER
// ============================================================================

interface StreamProviderProps {
  children: React.ReactNode
  streams?: string[]
}

export function ExecutionFabricStreamProvider({ children, streams = [] }: StreamProviderProps) {
  const [messages, setMessages] = useState<Record<string, StreamMessage>>({})
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('disconnected')

  // For demo purposes, generate mock messages
  useEffect(() => {
    const interval = setInterval(() => {
      const mockMessages: Record<string, StreamMessage> = {
        'lineage.update': {
          type: 'lineage.update',
          payload: {
            graph_id: `graph-${Math.random().toString(36).substring(7)}`,
            nodes: {
              total: Math.floor(Math.random() * 200) + 50,
              active: Math.floor(Math.random() * 50) + 10,
              completed: Math.floor(Math.random() * 150) + 30,
            },
          },
          timestamp: new Date().toISOString(),
        },
        'stability.metric': {
          type: 'stability.metric',
          payload: {
            overall_health: Math.random() * 0.3 + 0.7,
            components: Array.from({ length: 5 }, (_, i) => ({
              id: `comp-${i}`,
              health: Math.random() * 0.4 + 0.6,
            })),
          },
          timestamp: new Date().toISOString(),
        },
        'cognition.pulse': {
          type: 'cognition.pulse',
          payload: {
            active_memories: Math.floor(Math.random() * 150) + 50,
            pattern_matches: Math.floor(Math.random() * 40) + 10,
          },
          timestamp: new Date().toISOString(),
        },
        'topology.change': {
          type: 'topology.change',
          payload: {
            total_nodes: Math.floor(Math.random() * 100) + 20,
            total_edges: Math.floor(Math.random() * 500) + 100,
          },
          timestamp: new Date().toISOString(),
        },
      }

      // Randomly update one message type
      const messageTypes = Object.keys(mockMessages)
      const randomType = messageTypes[Math.floor(Math.random() * messageTypes.length)]
      
      setMessages(prev => ({
        ...prev,
        [randomType]: mockMessages[randomType],
      }))

      setConnectionStatus('connected')
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  return (
    <ExecutionFabricContext.Provider value={{ messages, connectionStatus }}>
      {children}
    </ExecutionFabricContext.Provider>
  )
}

import { createContext, useContext } from 'react'

interface ExecutionFabricContextValue {
  messages: Record<string, StreamMessage>
  connectionStatus: 'connected' | 'disconnected' | 'connecting'
}

const ExecutionFabricContext = createContext<ExecutionFabricContextValue>({
  messages: {},
  connectionStatus: 'disconnected',
})

export function useExecutionFabricContext() {
  return useContext(ExecutionFabricContext)
}