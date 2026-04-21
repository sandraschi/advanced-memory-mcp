import {
  Activity,
  Filter,
  Globe,
  Info,
  Layers,
  Maximize2,
  RefreshCw,
  Search,
  Zap,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import apiService from "../../services/api";

interface GraphNode {
  id: string;
  name: string;
  group: string;
  val: number;
}

interface GraphLink {
  source: string;
  target: string;
}

export default function GraphCanvas() {
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] }>({
    nodes: [],
    links: [],
  });
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const fgRef = useRef<any>();

  useEffect(() => {
    const fetchGraph = async () => {
      setLoading(true);
      try {
        await apiService.getProjects();
        const response = await apiService.getGraphSubgraph({
          depth: 2,
          max_nodes: 300,
          max_edges: 600,
        });
        if (response.success && response.data?.nodes && response.data?.links) {
          const nodes: GraphNode[] = response.data.nodes.map((n: any) => ({
            id: n.id,
            name: n.label ?? n.id,
            group:
              n.type === "unresolved" ? "research" : n.entity_type === "note" ? "topic" : "core",
            val: 6,
          }));
          const links: GraphLink[] = response.data.links.map((l: any) => ({
            source: l.source,
            target: l.target,
          }));
          setGraphData({ nodes, links });
        } else {
          setGraphData({ nodes: [], links: [] });
        }
      } catch (error) {
        console.error("Failed to fetch graph data:", error);
        setGraphData({ nodes: [], links: [] });
      } finally {
        setLoading(false);
      }
    };
    fetchGraph();
  }, []);

  const handleNodeClick = (node: any) => {
    // Center on node
    fgRef.current.centerAt(node.x, node.y, 1000);
    fgRef.current.zoom(8, 2000);
  };

  return (
    <div className="flex flex-col h-full bg-background overflow-hidden relative">
      {/* Header / Stats Overlay */}
      <div className="absolute top-6 left-6 z-10 space-y-4 pointer-events-none">
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 p-5 rounded-2xl pointer-events-auto">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-amber-500/20 rounded-lg">
              <Globe className="h-5 w-5 text-amber-500" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight">Knowledge Graph</h1>
              <p className="text-[10px] text-muted-foreground uppercase tracking-widest font-bold">
                Zettelkasten Graph v1.3.0
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="bg-white/5 p-3 rounded-xl border border-white/5">
              <span className="text-[9px] text-muted-foreground uppercase font-bold block mb-1">
                Total Nodes
              </span>
              <span className="text-xl font-mono font-bold text-amber-500">
                {graphData.nodes.length}
              </span>
            </div>
            <div className="bg-white/5 p-3 rounded-xl border border-white/5">
              <span className="text-[9px] text-muted-foreground uppercase font-bold block mb-1">
                Relations
              </span>
              <span className="text-xl font-mono font-bold text-blue-500">
                {graphData.links.length}
              </span>
            </div>
          </div>

          <div className="relative group pointer-events-auto">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground group-focus-within:text-amber-500 transition-colors" />
            <input
              type="text"
              placeholder="Locate intelligence node..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-xl py-2 pl-9 pr-4 text-xs focus:outline-none focus:ring-1 focus:ring-amber-500/50 transition-all"
            />
          </div>
        </div>

        {/* Viewport Controls */}
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 p-2 rounded-xl flex items-center space-x-1 pointer-events-auto">
          <button
            className="p-2 hover:bg-white/5 rounded-lg transition-colors text-muted-foreground hover:text-white"
            title="Reset View"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
          <button
            className="p-2 hover:bg-white/5 rounded-lg transition-colors text-muted-foreground hover:text-white"
            title="Auto Layout"
          >
            <Activity className="h-4 w-4" />
          </button>
          <button
            className="p-2 hover:bg-white/5 rounded-lg transition-colors text-muted-foreground hover:text-white"
            title="Toggle 3D View"
          >
            <Maximize2 className="h-4 w-4" />
          </button>
          <div className="w-px h-4 bg-white/10 mx-1" />
          <button
            className="p-2 hover:bg-white/5 rounded-lg transition-colors text-muted-foreground hover:text-white"
            title="Graph Filters"
          >
            <Filter className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Legend / Status Overlay */}
      <div className="absolute bottom-6 left-6 z-10 flex items-center space-x-6 bg-black/40 backdrop-blur-xl border border-white/10 px-6 py-3 rounded-full pointer-events-auto">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-amber-500" />
          <span className="text-[10px] uppercase font-bold tracking-tight">Core Node</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-blue-500" />
          <span className="text-[10px] uppercase font-bold tracking-tight">Active Topic</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-purple-500" />
          <span className="text-[10px] uppercase font-bold tracking-tight">Research Node</span>
        </div>
        <div className="w-px h-3 bg-white/20" />
        <div className="flex items-center space-x-2 text-amber-500/80">
          <Zap className="h-3 w-3" />
          <span className="text-[10px] font-mono italic">Physics: D3 Force-Directed v3.0</span>
        </div>
      </div>

      {/* Main Graph Viewport */}
      <div className="flex-1 w-full h-full cursor-grab active:cursor-grabbing">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="flex flex-col items-center space-y-4 opacity-50">
              <Activity className="h-12 w-12 text-amber-500 animate-pulse" />
              <p className="text-xs uppercase tracking-[0.3em] font-bold">
                Simulating Neural Topography...
              </p>
            </div>
          </div>
        ) : (
          <ForceGraph2D
            ref={fgRef}
            graphData={graphData}
            nodeLabel="name"
            nodeAutoColorBy="group"
            nodeColor={(n: any) => {
              if (n.group === "core") return "#f59e0b";
              if (n.group === "topic") return "#3b82f6";
              return "#a855f7";
            }}
            linkColor={() => "rgba(255, 255, 255, 0.08)"}
            nodeRelSize={6}
            linkDirectionalParticles={2}
            linkDirectionalParticleSpeed={0.005}
            backgroundColor="transparent"
            onNodeClick={handleNodeClick}
            nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
              const label = node.name;
              const fontSize = 12 / globalScale;
              ctx.font = `${fontSize}px Inter, system-ui, sans-serif`;

              // Draw circle
              ctx.beginPath();
              ctx.arc(node.x, node.y, 4, 0, 2 * Math.PI, false);
              ctx.fillStyle =
                node.group === "core" ? "#f59e0b" : node.group === "topic" ? "#3b82f6" : "#a855f7";
              ctx.fill();

              // Draw glow
              ctx.shadowBlur = 15;
              ctx.shadowColor = ctx.fillStyle;

              // Draw label
              if (globalScale > 2) {
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
                ctx.fillText(label, node.x, node.y + 10);
              }
            }}
          />
        )}
      </div>

      {/* Info Panel Overlay */}
      <div className="absolute top-6 right-6 z-10 w-64">
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-5 overflow-hidden">
          <div className="flex items-center space-x-2 mb-4 opacity-60">
            <Info className="h-4 w-4" />
            <span className="text-[10px] uppercase font-bold tracking-widest">Node Analysis</span>
          </div>

          <div className="flex flex-col items-center justify-center py-12 text-center border-2 border-dashed border-white/5 rounded-xl bg-white/2">
            <Layers className="h-8 w-8 text-muted-foreground mb-3 opacity-20" />
            <p className="text-[10px] text-muted-foreground">
              Select a node to inspect
              <br />
              semantic relationships
            </p>
          </div>

          <div className="mt-6 space-y-3">
            <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-tight opacity-40">
              <span>Analysis Engine</span>
              <span>Active</span>
            </div>
            <div className="h-1 bg-white/5 rounded-full overflow-hidden">
              <div className="h-full w-2/3 bg-amber-500/50" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
