import { useState } from 'react'
import { Network, Layers, Eye, Download, ZoomIn, ZoomOut } from 'lucide-react'

interface Node {
  id: string
  label: string
  type: 'research' | 'skill' | 'content' | 'reference'
  x: number
  y: number
  connections: number
}

interface Link {
  source: string
  target: string
  strength: number
}

// Mock data for demonstration
const mockNodes: Node[] = [
  { id: '1', label: 'Brain Tumors', type: 'research', x: 100, y: 100, connections: 8 },
  { id: '2', label: 'Glioblastoma', type: 'research', x: 200, y: 80, connections: 12 },
  { id: '3', label: 'Treatment Methods', type: 'content', x: 150, y: 200, connections: 6 },
  { id: '4', label: 'Clinical Trials', type: 'research', x: 300, y: 150, connections: 15 },
  { id: '5', label: 'Immunotherapy', type: 'skill', x: 250, y: 250, connections: 9 },
  { id: '6', label: 'Radiation Therapy', type: 'content', x: 400, y: 200, connections: 7 },
  { id: '7', label: 'Medical Research', type: 'reference', x: 350, y: 50, connections: 20 },
  { id: '8', label: 'Oncology', type: 'skill', x: 450, y: 100, connections: 11 },
]

const mockLinks: Link[] = [
  { source: '1', target: '2', strength: 0.8 },
  { source: '2', target: '3', strength: 0.6 },
  { source: '2', target: '4', strength: 0.9 },
  { source: '3', target: '5', strength: 0.7 },
  { source: '4', target: '6', strength: 0.5 },
  { source: '5', target: '6', strength: 0.4 },
  { source: '1', target: '7', strength: 0.8 },
  { source: '7', target: '8', strength: 0.6 },
  { source: '4', target: '8', strength: 0.7 },
]

export default function KnowledgeGraph() {
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [viewMode, setViewMode] = useState<'2d' | '3d'>('2d')
  const [zoom, setZoom] = useState(1)

  const nodeColors = {
    research: 'bg-blue-500',
    skill: 'bg-green-500',
    content: 'bg-purple-500',
    reference: 'bg-orange-500'
  }

  const nodeLabels = {
    research: 'Research',
    skill: 'Skill',
    content: 'Content',
    reference: 'Reference'
  }

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.2, 2))
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.2, 0.5))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Knowledge Graph Explorer</h1>
          <p className="text-muted-foreground">
            Visualize and explore your zettelkasten knowledge network
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleZoomOut}
            className="btn btn-outline btn-sm"
            disabled={zoom <= 0.5}
          >
            <ZoomOut className="h-4 w-4" />
          </button>

          <span className="text-sm text-muted-foreground min-w-[3rem] text-center">
            {Math.round(zoom * 100)}%
          </span>

          <button
            onClick={handleZoomIn}
            className="btn btn-outline btn-sm"
            disabled={zoom >= 2}
          >
            <ZoomIn className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium">View:</span>
            <button
              onClick={() => setViewMode('2d')}
              className={`btn btn-sm ${viewMode === '2d' ? 'btn-primary' : 'btn-outline'}`}
            >
              <Network className="h-4 w-4 mr-2" />
              2D Graph
            </button>
            <button
              onClick={() => setViewMode('3d')}
              className={`btn btn-sm ${viewMode === '3d' ? 'btn-primary' : 'btn-outline'}`}
            >
              <Layers className="h-4 w-4 mr-2" />
              3D Pointcloud
            </button>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button className="btn btn-outline btn-sm">
            <Eye className="h-4 w-4 mr-2" />
            Focus
          </button>
          <button className="btn btn-outline btn-sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 p-4 bg-muted/50 rounded-md">
        <span className="text-sm font-medium">Node Types:</span>
        {Object.entries(nodeLabels).map(([type, label]) => (
          <div key={type} className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${nodeColors[type as keyof typeof nodeColors]}`}></div>
            <span className="text-sm">{label}</span>
          </div>
        ))}
      </div>

      {/* Graph Visualization */}
      <div className="card p-6">
        <div className="relative bg-muted/20 rounded-md overflow-hidden" style={{ height: '600px' }}>
          {/* Mock visualization - in real implementation this would be D3.js or Three.js */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <Network className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">
                {viewMode === '2d' ? '2D Knowledge Graph' : '3D Pointcloud View'}
              </h3>
              <p className="text-muted-foreground mb-4">
                {viewMode === '2d'
                  ? 'Interactive graph showing note relationships and connections'
                  : '3D visualization of knowledge clusters and connectivity patterns'
                }
              </p>
              <div className="text-sm text-muted-foreground">
                {mockNodes.length} nodes • {mockLinks.length} connections
              </div>
            </div>
          </div>

          {/* Mock nodes for demonstration */}
          <div className="absolute inset-0 pointer-events-none">
            {mockNodes.map((node) => (
              <div
                key={node.id}
                className={`absolute w-4 h-4 rounded-full cursor-pointer pointer-events-auto transform -translate-x-2 -translate-y-2 transition-all hover:scale-125 ${nodeColors[node.type]}`}
                style={{
                  left: `${node.x * zoom}px`,
                  top: `${node.y * zoom}px`,
                }}
                onClick={() => setSelectedNode(node)}
                title={`${node.label} (${nodeLabels[node.type]}) - ${node.connections} connections`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Node Details Panel */}
      {selectedNode && (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Node Details</h2>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-muted-foreground hover:text-foreground"
            >
              ✕
            </button>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <h3 className="font-medium mb-2">{selectedNode.label}</h3>
              <div className="flex items-center space-x-2 mb-2">
                <div className={`w-3 h-3 rounded-full ${nodeColors[selectedNode.type]}`}></div>
                <span className="text-sm">{nodeLabels[selectedNode.type]}</span>
              </div>
              <div className="text-sm text-muted-foreground">
                Position: ({selectedNode.x}, {selectedNode.y})
              </div>
            </div>

            <div>
              <div className="text-sm">
                <strong>Connections:</strong> {selectedNode.connections}
              </div>
              <div className="text-sm text-muted-foreground mt-2">
                This node is connected to {selectedNode.connections} other concepts in your knowledge base.
              </div>
            </div>
          </div>

          {/* Connected nodes preview */}
          <div className="mt-4">
            <h4 className="font-medium mb-2">Connected Concepts</h4>
            <div className="flex flex-wrap gap-2">
              {mockNodes
                .filter(node => node.id !== selectedNode.id)
                .slice(0, 5)
                .map(node => (
                  <span
                    key={node.id}
                    className="text-xs px-2 py-1 bg-accent/10 text-accent rounded-md cursor-pointer hover:bg-accent/20"
                  >
                    {node.label}
                  </span>
                ))}
              {mockNodes.length > 6 && (
                <span className="text-xs px-2 py-1 text-muted-foreground">
                  +{mockNodes.length - 6} more
                </span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="grid gap-4 md:grid-cols-4">
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-accent">{mockNodes.length}</div>
          <div className="text-sm text-muted-foreground">Total Nodes</div>
        </div>

        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-accent">{mockLinks.length}</div>
          <div className="text-sm text-muted-foreground">Connections</div>
        </div>

        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-accent">
            {Math.round(mockNodes.reduce((sum, node) => sum + node.connections, 0) / mockNodes.length)}
          </div>
          <div className="text-sm text-muted-foreground">Avg Connections</div>
        </div>

        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-accent">
            {new Set(mockNodes.map(node => node.type)).size}
          </div>
          <div className="text-sm text-muted-foreground">Node Types</div>
        </div>
      </div>
    </div>
  )
}
