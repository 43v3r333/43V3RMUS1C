/**
 * 43V3R CORE - Semantic Execution Graph Viewer
 * 
 * Platform-wide semantic coordination with intelligent dependency mapping,
 * workflow cognition relationships, and execution topology.
 * 
 * Dense graph visualization with semantic relationship rendering,
 * node exploration, and path analysis.
 */
'use client'

import { useState, useEffect } from 'react'
import {
  Network,
  GitBranch,
  Link2,
  Eye,
  ZoomIn,
  ZoomOut,
  Move,
  Target,
  Plus,
  Minus,
  RefreshCw,
  Layers,
  Hash,
  ArrowRight,
  CornerDownRight,
} from 'lucide-react'
import { useCoherenceApi, type SemanticGraph, type SemanticNode, type SemanticEdge } from '@/lib/coherence-api'
import { ConsolePanel, MetricGrid, MetricValue, StatusDot, DataTable, TabBar, IconButton } from '@/components/cognitive/primitives'

// ---- Types ----

interface GraphOverview {
  totalGraphs: number
  totalNodes: number
  totalEdges: number
  avgDepth: number
  semanticDensity: number
}

// ---- Mock Data ----

function generateMockGraph(): SemanticGraph {
  return {
    graph_id: 'graph-001',
    name: 'Main Orchestration Graph',
    description: 'Primary execution topology for the orchestration system',
    nodes: [
      { node_id: 'node-001', node_key: 'start', node_type: 'trigger', semantic_key: 'execution.start', label: 'Workflow Start', properties: {}, tags: ['init'], position_x: 100, position_y: 200 },
      { node_id: 'node-002', node_key: 'validate', node_type: 'validation', semantic_key: 'execution.validate', label: 'Input Validation', properties: {}, tags: ['check'], position_x: 250, position_y: 150 },
      { node_id: 'node-003', node_key: 'process', node_type: 'execution', semantic_key: 'execution.process', label: 'Data Processing', properties: {}, tags: ['compute'], position_x: 250, position_y: 250 },
      { node_id: 'node-004', node_key: 'optimize', node_type: 'optimization', semantic_key: 'execution.optimize', label: 'Resource Optimization', properties: {}, tags: ['tuning'], position_x: 400, position_y: 200 },
      { node_id: 'node-005', node_key: 'generate', node_type: 'ai_generation', semantic_key: 'execution.generate', label: 'AI Generation', properties: {}, tags: ['create'], position_x: 550, position_y: 200 },
      { node_id: 'node-006', node_key: 'render', node_type: 'rendering', semantic_key: 'execution.render', label: 'Media Rendering', properties: {}, tags: ['produce'], position_x: 700, position_y: 200 },
      { node_id: 'node-007', node_key: 'end', node_type: 'completion', semantic_key: 'execution.end', label: 'Workflow End', properties: {}, tags: ['final'], position_x: 850, position_y: 200 },
    ],
    edges: [
      { edge_id: 'edge-001', source_key: 'start', target_key: 'validate', relation_type: 'depends_on', weight: 1.0, confidence: 0.95 },
      { edge_id: 'edge-002', source_key: 'start', target_key: 'process', relation_type: 'depends_on', weight: 1.0, confidence: 0.95 },
      { edge_id: 'edge-003', source_key: 'validate', target_key: 'optimize', relation_type: 'depends_on', weight: 0.8, confidence: 0.9 },
      { edge_id: 'edge-004', source_key: 'process', target_key: 'optimize', relation_type: 'depends_on', weight: 0.8, confidence: 0.9 },
      { edge_id: 'edge-005', source_key: 'optimize', target_key: 'generate', relation_type: 'produces', weight: 1.0, confidence: 0.98 },
      { edge_id: 'edge-006', source_key: 'generate', target_key: 'render', relation_type: 'depends_on', weight: 1.0, confidence: 0.97 },
      { edge_id: 'edge-007', source_key: 'render', target_key: 'end', relation_type: 'succeeds', weight: 1.0, confidence: 1.0 },
    ],
    node_count: 7,
    edge_count: 7,
    semantic_depth: 4,
    lifecycle_state: 'active',
  }
}

// ---- Main Component ----

export default function SemanticExecutionGraphViewer() {
  const api = useCoherenceApi()
  const [activeTab, setActiveTab] = useState('graph')
  const [loading, setLoading] = useState(true)
  const [overview, setOverview] = useState<GraphOverview>({
    totalGraphs: 0,
    totalNodes: 0,
    totalEdges: 0,
    avgDepth: 0,
    semanticDensity: 0,
  })
  const [graphs, setGraphs] = useState<SemanticGraph[]>([])
  const [selectedGraph, setSelectedGraph] = useState<SemanticGraph | null>(null)
  const [selectedNode, setSelectedNode] = useState<SemanticNode | null>(null)
  const [selectedEdge, setSelectedEdge] = useState<SemanticEdge | null>(null)
  const [zoomLevel, setZoomLevel] = useState(1)
  
  useEffect(() => {
    const loadData = async () => {
      try {
        const mockGraph = generateMockGraph()
        
        setOverview({
          totalGraphs: 3,
          totalNodes: mockGraph.node_count,
          totalEdges: mockGraph.edge_count,
          avgDepth: mockGraph.semantic_depth,
          semanticDensity: (mockGraph.edge_count / mockGraph.node_count).toFixed(2) as unknown as number,
        })
        
        setGraphs([mockGraph])
        setSelectedGraph(mockGraph)
      } catch {
        // Use defaults
      }
      setLoading(false)
    }
    
    loadData()
  }, [api])
  
  const tabs = [
    { id: 'graph', label: 'Graph View', icon: <Network className="h-3 w-3" /> },
    { id: 'nodes', label: 'Nodes', icon: <Target className="h-3 w-3" /> },
    { id: 'paths', label: 'Path Analysis', icon: <GitBranch className="h-3 w-3" /> },
    { id: 'dependencies', label: 'Dependencies', icon: <Link2 className="h-3 w-3" /> },
  ]
  
  const getNodeColor = (nodeType: string) => {
    const colors: Record<string, string> = {
      trigger: 'bg-green-500',
      validation: 'bg-blue-500',
      execution: 'bg-purple-500',
      optimization: 'bg-yellow-500',
      ai_generation: 'bg-pink-500',
      rendering: 'bg-orange-500',
      completion: 'bg-gray-500',
    }
    return colors[nodeType] || 'bg-muted'
  }
  
  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Network className="h-5 w-5 text-primary" />
            <span className="font-mono text-sm font-semibold tracking-tight">SEMANTIC EXECUTION</span>
          </div>
          <div className="h-4 w-px bg-border/50" />
          <StatusDot status="healthy" />
          <span className="text-[10px] font-mono text-muted-foreground uppercase">
            {graphs.length} graphs
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 border border-border rounded">
            <button
              onClick={() => setZoomLevel(z => Math.max(0.5, z - 0.25))}
              className="p-1 hover:bg-muted transition-colors"
            >
              <Minus className="h-3 w-3" />
            </button>
            <span className="px-2 text-[10px] font-mono">{Math.round(zoomLevel * 100)}%</span>
            <button
              onClick={() => setZoomLevel(z => Math.min(2, z + 0.25))}
              className="p-1 hover:bg-muted transition-colors"
            >
              <Plus className="h-3 w-3" />
            </button>
          </div>
          <IconButton icon={<RefreshCw className="h-3 w-3" />} onClick={() => setLoading(true)} />
        </div>
      </div>
      
      {/* Metrics Bar */}
      <div className="border-b border-border/50 bg-muted/20 px-4 py-2">
        <MetricGrid columns={5}>
          <MetricValue
            label="Total Graphs"
            value={overview.totalGraphs}
            icon={<Network className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Total Nodes"
            value={overview.totalNodes}
            icon={<Target className="h-3 w-3" />}
            trend="up"
          />
          <MetricValue
            label="Total Edges"
            value={overview.totalEdges}
            icon={<Link2 className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Max Depth"
            value={overview.avgDepth}
            icon={<Layers className="h-3 w-3" />}
            trend="stable"
          />
          <MetricValue
            label="Graph Density"
            value={overview.semanticDensity}
            icon={<Hash className="h-3 w-3" />}
            trend="stable"
          />
        </MetricGrid>
      </div>
      
      {/* Tabs */}
      <div className="border-b border-border/50 px-4">
        <TabBar
          tabs={tabs}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />
      </div>
      
      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {activeTab === 'graph' && selectedGraph && (
          <div className="grid gap-4 lg:grid-cols-3">
            {/* Graph Visualization */}
            <div className="lg:col-span-2">
              <ConsolePanel
                title="Execution Graph"
                icon={<Network className="h-4 w-4" />}
                subtitle={selectedGraph.name}
                headerContent={
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-muted-foreground">
                      {selectedGraph.node_count} nodes, {selectedGraph.edge_count} edges
                    </span>
                  </div>
                }
              >
                <div 
                  className="relative bg-muted/30 rounded border overflow-hidden"
                  style={{ height: 400, transform: `scale(${zoomLevel})`, transformOrigin: 'top left' }}
                >
                  {/* SVG for edges */}
                  <svg className="absolute inset-0 w-full h-full">
                    {selectedGraph.edges.map(edge => {
                      const sourceNode = selectedGraph.nodes.find(n => n.node_key === edge.source_key)
                      const targetNode = selectedGraph.nodes.find(n => n.node_key === edge.target_key)
                      
                      if (!sourceNode || !targetNode) return null
                      
                      return (
                        <g key={edge.edge_id}>
                          <line
                            x1={sourceNode.position_x}
                            y1={sourceNode.position_y}
                            x2={targetNode.position_x}
                            y2={targetNode.position_y}
                            stroke="var(--border)"
                            strokeWidth={2 * edge.weight}
                            opacity={edge.confidence}
                          />
                          <polygon
                            points={`${targetNode.position_x - 8},${targetNode.position_y} ${targetNode.position_x},${targetNode.position_y - 5} ${targetNode.position_x},${targetNode.position_y + 5}`}
                            fill="var(--border)"
                            opacity={edge.confidence}
                          />
                        </g>
                      )
                    })}
                  </svg>
                  
                  {/* Nodes */}
                  {selectedGraph.nodes.map(node => (
                    <div
                      key={node.node_id}
                      className={`absolute w-12 h-12 rounded-full border-2 flex items-center justify-center cursor-pointer transition-transform hover:scale-110 ${
                        selectedNode?.node_id === node.node_id
                          ? 'border-primary bg-primary/10'
                          : 'border-border bg-background'
                      }`}
                      style={{ 
                        left: node.position_x - 24, 
                        top: node.position_y - 24,
                        borderColor: selectedNode?.node_id === node.node_id ? 'var(--primary)' : undefined
                      }}
                      onClick={() => setSelectedNode(node)}
                    >
                      <span className={`w-8 h-8 rounded-full flex items-center justify-center text-[10px] text-white ${getNodeColor(node.node_type)}`}>
                        {node.label.charAt(0)}
                      </span>
                    </div>
                  ))}
                  
                  {/* Node Labels */}
                  {selectedGraph.nodes.map(node => (
                    <div
                      key={`label-${node.node_id}`}
                      className="absolute text-[10px] font-mono text-muted-foreground whitespace-nowrap"
                      style={{ 
                        left: node.position_x - 30, 
                        top: node.position_y + 20,
                        width: 60,
                        textAlign: 'center'
                      }}
                    >
                      {node.label}
                    </div>
                  ))}
                </div>
              </ConsolePanel>
            </div>
            
            {/* Node/Edge Details */}
            <div>
              {selectedNode ? (
                <ConsolePanel
                  title="Node Details"
                  icon={<Target className="h-4 w-4" />}
                  subtitle={selectedNode.label}
                >
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Node Key</span>
                        <div className="text-sm font-mono">{selectedNode.node_key}</div>
                      </div>
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Type</span>
                        <div className="text-sm font-mono">{selectedNode.node_type}</div>
                      </div>
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Position</span>
                        <div className="text-sm font-mono">
                          ({selectedNode.position_x.toFixed(0)}, {selectedNode.position_y.toFixed(0)})
                        </div>
                      </div>
                      <div className="space-y-1">
                        <span className="text-[10px] text-muted-foreground uppercase">Tags</span>
                        <div className="flex gap-1">
                          {selectedNode.tags.map(tag => (
                            <span key={tag} className="text-[10px] px-1 py-0.5 rounded bg-muted">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-1">
                      <span className="text-[10px] text-muted-foreground uppercase">Semantic Key</span>
                      <div className="text-xs font-mono break-all">{selectedNode.semantic_key}</div>
                    </div>
                    
                    {/* Dependencies */}
                    <div className="space-y-1">
                      <span className="text-[10px] text-muted-foreground uppercase">Dependencies</span>
                      <div className="space-y-1">
                        {selectedGraph.edges
                          .filter(e => e.target_key === selectedNode.node_key)
                          .map(edge => {
                            const sourceNode = selectedGraph.nodes.find(n => n.node_key === edge.source_key)
                            return (
                              <div key={edge.edge_id} className="flex items-center gap-2 text-xs">
                                <CornerDownRight className="h-3 w-3 text-muted-foreground" />
                                <span className="font-mono">{sourceNode?.label || edge.source_key}</span>
                                <span className="text-muted-foreground">({edge.relation_type})</span>
                              </div>
                            )
                          })}
                      </div>
                    </div>
                  </div>
                </ConsolePanel>
              ) : (
                <ConsolePanel
                  title="Node Details"
                  icon={<Target className="h-4 w-4" />}
                  subtitle="Select a node"
                >
                  <div className="text-center py-8 text-muted-foreground text-sm">
                    Click on a node to view details
                  </div>
                </ConsolePanel>
              )}
            </div>
          </div>
        )}
        
        {activeTab === 'nodes' && selectedGraph && (
          <ConsolePanel
            title="Graph Nodes"
            icon={<Target className="h-4 w-4" />}
            subtitle={`${selectedGraph.node_count} nodes`}
          >
            <DataTable
              columns={[
                { key: 'key', label: 'Node Key', width: '20%' },
                { key: 'type', label: 'Type', width: '15%' },
                { key: 'label', label: 'Label', width: '25%' },
                { key: 'tags', label: 'Tags', width: '20%' },
                { key: 'position', label: 'Position', width: '20%' },
              ]}
              rows={selectedGraph.nodes.map(node => ({
                key: <span className="font-mono text-xs">{node.node_key}</span>,
                type: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{node.node_type}</span>,
                label: <span className="text-sm">{node.label}</span>,
                tags: (
                  <div className="flex gap-1">
                    {node.tags.map(tag => (
                      <span key={tag} className="text-[10px] px-1 py-0.5 rounded bg-muted">{tag}</span>
                    ))}
                  </div>
                ),
                position: <span className="font-mono text-xs text-muted-foreground">({node.position_x.toFixed(0)}, {node.position_y.toFixed(0)})</span>,
              }))}
            />
          </ConsolePanel>
        )}
        
        {activeTab === 'paths' && selectedGraph && (
          <ConsolePanel
            title="Path Analysis"
            icon={<GitBranch className="h-4 w-4" />}
            subtitle="Critical path analysis"
          >
            <div className="space-y-4">
              {/* Critical Path */}
              <div className="p-4 rounded border border-border/50">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Critical Path</span>
                  <span className="text-[10px] font-mono text-muted-foreground">7 nodes, 6 edges</span>
                </div>
                <div className="flex items-center gap-2">
                  {selectedGraph.nodes.map((node, idx) => (
                    <div key={node.node_id} className="flex items-center">
                      <span className="text-xs font-mono px-2 py-1 rounded bg-muted">{node.label}</span>
                      {idx < selectedGraph.nodes.length - 1 && (
                        <ArrowRight className="h-3 w-3 text-muted-foreground mx-1" />
                      )}
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Alternative Paths */}
              <div className="space-y-2">
                <span className="text-xs text-muted-foreground uppercase">Alternative Paths</span>
                {[
                  { path: ['start', 'validate', 'optimize', 'generate', 'end'], weight: 0.92 },
                  { path: ['start', 'process', 'optimize', 'generate', 'end'], weight: 0.88 },
                  { path: ['start', 'validate', 'process', 'optimize', 'generate', 'end'], weight: 0.75 },
                ].map((alt, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 rounded bg-muted/30">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono text-muted-foreground">#{idx + 1}</span>
                      <span className="text-xs">{alt.path.join(' → ')}</span>
                    </div>
                    <span className="text-xs font-mono">{(alt.weight * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>
          </ConsolePanel>
        )}
        
        {activeTab === 'dependencies' && selectedGraph && (
          <ConsolePanel
            title="Dependency Relationships"
            icon={<Link2 className="h-4 w-4" />}
            subtitle={`${selectedGraph.edge_count} edges`}
          >
            <DataTable
              columns={[
                { key: 'source', label: 'Source', width: '25%' },
                { key: 'relation', label: 'Relation', width: '20%' },
                { key: 'target', label: 'Target', width: '25%' },
                { key: 'weight', label: 'Weight', width: '15%' },
                { key: 'confidence', label: 'Confidence', width: '15%' },
              ]}
              rows={selectedGraph.edges.map(edge => {
                const sourceNode = selectedGraph.nodes.find(n => n.node_key === edge.source_key)
                const targetNode = selectedGraph.nodes.find(n => n.node_key === edge.target_key)
                
                return {
                  source: <span className="font-mono text-xs">{sourceNode?.label || edge.source_key}</span>,
                  relation: <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{edge.relation_type}</span>,
                  target: <span className="font-mono text-xs">{targetNode?.label || edge.target_key}</span>,
                  weight: <span className="font-mono">{edge.weight.toFixed(2)}</span>,
                  confidence: <span className="font-mono">{Math.round(edge.confidence * 100)}%</span>,
                }
              })}
            />
          </ConsolePanel>
        )}
      </div>
    </div>
  )
}