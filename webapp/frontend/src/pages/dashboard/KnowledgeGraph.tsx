import { useState, useEffect, useRef } from 'react'
import { Network, Layers, ZoomIn, ZoomOut, Maximize2, RefreshCw, Loader2 } from 'lucide-react'
import ForceGraph2D from 'react-force-graph-2d'
import { apiService } from '../../services/api'

interface GraphData {
  nodes: any[]
  links: any[]
}

export default function KnowledgeGraph() {
  const [data, setData] = useState<GraphData>({ nodes: [], links: [] })
  const [isLoading, setIsLoading] = useState(true)
  const [selectedNode, setSelectedNode] = useState<any | null>(null)
  const fgRef = useRef<any>()

  useEffect(() => {
    fetchGraphData()
  }, [])

  const fetchGraphData = async () => {
    setIsLoading(true)
    try {
      const response = await apiService.getGraphData()
      if (response.success && response.data) {
        setData(response.data)
      }
    } catch (err) {
      console.error('Failed to fetch graph data:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleNodeClick = (node: any) => {
    setSelectedNode(node)
    // Center view on node
    if (fgRef.current) {
      fgRef.current.centerAt(node.x, node.y, 1000)
      fgRef.current.zoom(2, 1000)
    }
  }

  return (
    <div className="h-full flex flex-col space-y-4 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">PointCloud Explorer</h1>
          <p className="text-muted-foreground text-sm">Interactive visualization of your semantic neuro-grid</p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => fetchGraphData()}
            className="p-2 hover:bg-muted rounded-full transition-colors"
            title="Refresh Graph"
          >
            <RefreshCw className={`h-5 w-5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => fgRef.current?.zoomToFit(400)}
            className="p-2 hover:bg-muted rounded-full transition-colors"
            title="Fit to Screen"
          >
            <Maximize2 className="h-5 w-5" />
          </button>
        </div>
      </div>

      <div className="flex-1 relative card overflow-hidden border-accent/20 bg-background/50 min-h-[600px]">
        {isLoading && (
          <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-background/60 backdrop-blur-sm">
            <Loader2 className="h-12 w-12 text-accent animate-spin mb-4" />
            <p className="font-medium animate-pulse">Calculating graph topology...</p>
          </div>
        )}

        <ForceGraph2D
          ref={fgRef}
          graphData={data}
          nodeLabel="label"
          nodeColor={node => {
            if (selectedNode && node.id === selectedNode.id) return '#ff00ff' // Highlight selected
            switch (node.type) {
              case 'entity': return '#3b82f6' // blue
              case 'observation': return '#a855f7' // purple
              case 'skill': return '#22c55e' // green
              default: return '#64748b' // slate
            }
          }}
          nodeRelSize={6}
          linkColor={() => 'rgba(255, 255, 255, 0.1)'}
          linkDirectionalParticles={1}
          linkDirectionalParticleSpeed={0.005}
          backgroundColor="rgba(0,0,0,0)"
          onNodeClick={handleNodeClick}
          width={window.innerWidth - 300} // Approximate with sidebar
          height={600}
        />

        {/* Selected Node Info Overlay */}
        {selectedNode && (
          <div className="absolute bottom-6 left-6 right-6 lg:right-auto lg:w-96 card p-6 bg-background/90 backdrop-blur-md border-accent/30 shadow-2xl animate-in slide-in-from-left-4 duration-300">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Network className="h-5 w-5 text-accent" />
                <h3 className="font-bold text-lg">{selectedNode.label}</h3>
              </div>
              <button onClick={() => setSelectedNode(null)} className="text-muted-foreground hover:text-foreground">✕</button>
            </div>

            <div className="space-y-3">
              <div className="flex items-center space-x-2 text-xs uppercase tracking-widest font-bold text-muted-foreground">
                <span className={`w-2 h-2 rounded-full ${selectedNode.type === 'entity' ? 'bg-blue-500' : 'bg-purple-500'}`} />
                <span>{selectedNode.type}</span>
              </div>

              <p className="text-sm text-muted-foreground">
                Identifier: <code className="bg-muted px-1 rounded">{selectedNode.id}</code>
              </p>

              <div className="pt-4 flex border-t border-white/5">
                <button
                  className="btn btn-primary btn-sm w-full"
                  onClick={() => window.location.href = `/notes?id=${selectedNode.id}`}
                >
                  Open Note
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Legend */}
        <div className="absolute top-4 left-4 flex flex-col space-y-2 p-3 bg-background/50 backdrop-blur-sm rounded-lg border border-white/5 text-[10px] uppercase font-bold tracking-wider">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-blue-500" />
            <span>Entities</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-purple-500" />
            <span>Observations</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            <span>Skills</span>
          </div>
        </div>
      </div>
    </div>
  )
}
