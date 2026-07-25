import {
  Activity,
  Cuboid,
  FileText,
  Globe,
  Info,
  Layers,
  RefreshCw,
  Search,
  SlidersHorizontal,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import ForceGraph2D from "react-force-graph-2d";
import ForceGraph3D from "react-force-graph-3d";
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

const nodeColor = (group: string) =>
  group === "core" ? "#f59e0b" : group === "topic" ? "#3b82f6" : "#a855f7";

export default function GraphCanvas() {
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; links: GraphLink[] }>({
    nodes: [],
    links: [],
  });
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [mode3d, setMode3d] = useState(false);
  const [seedSize, setSeedSize] = useState(500);
  const [showSeedSlider, setShowSeedSlider] = useState(false);
  const fgRef = useRef<any>();

  const fetchGraph = useCallback(async (seed: number) => {
    setLoading(true);
    try {
      await apiService.getProjects();
      const response = await apiService.getGraphSubgraph({
        depth: 3,
        max_nodes: 5000,
        max_edges: 10000,
        seed_size: seed,
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
  }, []);

  useEffect(() => {
    fetchGraph(seedSize);
  }, []); // only on mount

  const filteredNodes = useMemo(() => {
    if (!searchTerm.trim()) return graphData.nodes;
    const q = searchTerm.toLowerCase();
    return graphData.nodes.filter((n) => n.name.toLowerCase().includes(q));
  }, [graphData.nodes, searchTerm]);

  const filteredLinks = useMemo(() => {
    if (!searchTerm.trim()) return graphData.links;
    const validIds = new Set(filteredNodes.map((n) => n.id));
    return graphData.links.filter(
      (l) => validIds.has(typeof l.source === "string" ? l.source : (l.source as any).id) &&
        validIds.has(typeof l.target === "string" ? l.target : (l.target as any).id),
    );
  }, [graphData.links, filteredNodes, searchTerm]);

  const filteredGraphData = useMemo(
    () => ({ nodes: filteredNodes, links: filteredLinks }),
    [filteredNodes, filteredLinks],
  );

  const handleNodeClick = (node: any) => {
    setSelectedNode(node);
    if (fgRef.current) {
      if (mode3d) {
        fgRef.current.cameraPosition(
          { x: node.x * 1.5, y: node.y * 1.5, z: node.z ? node.z * 1.5 : 200 },
          node,
          2000,
        );
      } else {
        fgRef.current.centerAt(node.x, node.y, 1000);
        fgRef.current.zoom(8, 2000);
      }
    }
  };

  const handleResetView = () => {
    setSelectedNode(null);
    if (fgRef.current) {
      if (mode3d) {
        fgRef.current.cameraPosition({ x: 0, y: 0, z: 400 }, { x: 0, y: 0, z: 0 }, 1000);
      } else {
        fgRef.current.centerAt(0, 0, 1000);
        fgRef.current.zoom(2.5, 1000);
      }
    }
  };

  const neighborCount = useMemo(() => {
    if (!selectedNode) return 0;
    return graphData.links.filter(
      (l) =>
        (typeof l.source === "string" ? l.source : (l.source as any).id) === selectedNode.id ||
        (typeof l.target === "string" ? l.target : (l.target as any).id) === selectedNode.id,
    ).length;
  }, [selectedNode, graphData.links]);

  return (
    <div className="flex flex-col h-full bg-background overflow-hidden relative">
      {/* Header / Stats Overlay */}
      <div className="absolute top-6 left-6 z-10 space-y-4 pointer-events-none" style={{ width: "240px" }}>
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 p-5 rounded-2xl pointer-events-auto">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-amber-500/20 rounded-lg">
              <Globe className="h-5 w-5 text-amber-500" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight">Knowledge Graph</h1>
              <p className="text-[10px] text-muted-foreground uppercase tracking-widest font-bold">
                {graphData.nodes.length} nodes, {graphData.links.length} links
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
              placeholder="Filter nodes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-xl py-2 pl-9 pr-4 text-xs focus:outline-none focus:ring-1 focus:ring-amber-500/50 transition-all"
            />
            {searchTerm && (
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-muted-foreground">
                {filteredNodes.length} / {graphData.nodes.length}
              </span>
            )}
          </div>
        </div>

        {/* Viewport Controls */}
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 p-2 rounded-xl flex items-center space-x-1 pointer-events-auto">
          <button
            onClick={handleResetView}
            className="p-2 hover:bg-white/5 rounded-lg transition-colors text-muted-foreground hover:text-white"
            title="Reset View"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
          <div className="w-px h-4 bg-white/10 mx-1" />
          <button
            onClick={() => { setSeedSize(500); fetchGraph(500); }}
            className="p-2 hover:bg-white/5 rounded-lg transition-colors text-muted-foreground hover:text-white"
            title="Reload 500"
          >
            <FileText className="h-4 w-4" />
          </button>
          <div className="w-px h-4 bg-white/10 mx-1" />
          <button
            onClick={() => setShowSeedSlider(!showSeedSlider)}
            className={`p-2 rounded-lg transition-colors ${
              showSeedSlider
                ? "bg-amber-500/20 text-amber-400"
                : "text-muted-foreground hover:text-white hover:bg-white/5"
            }`}
            title="Adjust seed size"
          >
            <SlidersHorizontal className="h-4 w-4" />
          </button>
          <div className="w-px h-4 bg-white/10 mx-1" />
          <button
            onClick={() => setMode3d(!mode3d)}
            className={`p-2 rounded-lg transition-colors ${
              mode3d
                ? "bg-amber-500/20 text-amber-400"
                : "text-muted-foreground hover:text-white hover:bg-white/5"
            }`}
            title={mode3d ? "Switch to 2D" : "Switch to 3D"}
          >
            <Cuboid className="h-4 w-4" />
          </button>
        </div>

        {/* Seed Size Slider */}
        {showSeedSlider && (
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 p-4 rounded-2xl pointer-events-auto">
            <label className="text-[10px] uppercase tracking-widest font-bold text-muted-foreground block mb-2">
              Seed Size: {seedSize}
            </label>
            <input
              type="range"
              min={50}
              max={2000}
              step={50}
              value={seedSize}
              onChange={(e) => setSeedSize(Number(e.target.value))}
              className="w-full accent-amber-500"
            />
            <div className="flex justify-between text-[9px] text-muted-foreground mt-1">
              <span>50</span>
              <span>2000</span>
            </div>
            <button
              onClick={() => fetchGraph(seedSize)}
              disabled={loading}
              className="mt-3 w-full py-1.5 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/20 rounded-lg text-[10px] uppercase font-bold tracking-wider text-amber-400 transition-colors flex items-center justify-center gap-1.5 disabled:opacity-40"
            >
              {loading ? (
                <Activity className="h-3 w-3 animate-spin" />
              ) : (
                <RefreshCw className="h-3 w-3" />
              )}
              Reload Graph
            </button>
          </div>
        )}
      </div>

      {/* Legend / Status Overlay */}
      <div className="absolute bottom-6 left-6 z-10 flex items-center space-x-6 bg-black/40 backdrop-blur-xl border border-white/10 px-6 py-3 rounded-full pointer-events-auto">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-amber-500" />
          <span className="text-[10px] uppercase font-bold tracking-tight">Core</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-blue-500" />
          <span className="text-[10px] uppercase font-bold tracking-tight">Topic</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-purple-500" />
          <span className="text-[10px] uppercase font-bold tracking-tight">Research</span>
        </div>
        <div className="w-px h-3 bg-white/20" />
        <span className="text-[10px] text-muted-foreground">{mode3d ? "3D" : "2D"}</span>
        <div className="w-px h-3 bg-white/20" />
        <span className="text-[10px] text-muted-foreground">seed: {seedSize}</span>
        <div className="w-px h-3 bg-white/20" />
        <Link
          to="/notes"
          className="flex items-center space-x-1.5 text-amber-500/80 hover:text-amber-400 transition-colors"
        >
          <FileText className="h-3 w-3" />
          <span className="text-[10px]">Open Notes</span>
        </Link>
      </div>

      {/* Main Graph Viewport */}
      <div className={`flex-1 w-full h-full ${mode3d ? "" : "cursor-grab active:cursor-grabbing"}`}>
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="flex flex-col items-center space-y-4 opacity-50">
              <Activity className="h-12 w-12 text-amber-500 animate-pulse" />
              <p className="text-xs uppercase tracking-[0.3em] font-bold">
                Loading graph...
              </p>
            </div>
          </div>
        ) : mode3d ? (
          <ForceGraph3D
            ref={fgRef}
            graphData={filteredGraphData}
            nodeLabel="name"
            nodeAutoColorBy="group"
            nodeColor={(n: any) => nodeColor(n.group)}
            linkColor={() => "rgba(255, 255, 255, 0.12)"}
            linkDirectionalParticles={2}
            linkDirectionalParticleSpeed={0.005}
            backgroundColor="#09090b"
            onNodeClick={handleNodeClick}
          />
        ) : (
          <ForceGraph2D
            ref={fgRef}
            graphData={filteredGraphData}
            nodeLabel="name"
            nodeAutoColorBy="group"
            nodeColor={(n: any) => nodeColor(n.group)}
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

              const isSelected = selectedNode?.id === node.id;
              const radius = isSelected ? 6 : 4;

              ctx.beginPath();
              ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
              ctx.fillStyle = nodeColor(node.group);
              ctx.fill();

              if (isSelected) {
                ctx.strokeStyle = "rgba(255,255,255,0.6)";
                ctx.lineWidth = 2;
                ctx.stroke();
              }

              ctx.shadowBlur = 15;
              ctx.shadowColor = ctx.fillStyle;

              if (globalScale > 2) {
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillStyle = isSelected ? "rgba(255,255,255,1)" : "rgba(255,255,255,0.8)";
                ctx.fillText(label, node.x, node.y + 12);
              }
            }}
          />
        )}
      </div>

      {/* Node Info Panel */}
      <div className="absolute top-6 right-6 z-10 w-72">
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-5 overflow-hidden pointer-events-auto">
          <div className="flex items-center space-x-2 mb-4 opacity-60">
            <Info className="h-4 w-4" />
            <span className="text-[10px] uppercase font-bold tracking-widest">Node Details</span>
          </div>

          {selectedNode ? (
            <div className="space-y-3">
              <div>
                <h3 className="text-sm font-bold truncate">{selectedNode.name}</h3>
                <span className="text-[10px] text-muted-foreground uppercase tracking-wider">
                  {selectedNode.group}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-white/5 rounded-lg p-2">
                  <span className="text-[9px] text-muted-foreground uppercase font-bold block">
                    Connections
                  </span>
                  <span className="text-sm font-mono font-bold text-amber-500">{neighborCount}</span>
                </div>
                <div className="bg-white/5 rounded-lg p-2">
                  <span className="text-[9px] text-muted-foreground uppercase font-bold block">
                    Type
                  </span>
                  <span className="text-sm font-mono font-bold text-blue-500 truncate block">
                    {selectedNode.group}
                  </span>
                </div>
              </div>
              <Link
                to={`/notes?id=${encodeURIComponent(selectedNode.id)}`}
                className="flex items-center justify-center space-x-1.5 w-full py-2 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/20 rounded-lg text-[10px] uppercase font-bold tracking-wider text-amber-400 transition-colors"
              >
                <FileText className="h-3 w-3" />
                <span>Open Note</span>
              </Link>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center border-2 border-dashed border-white/5 rounded-xl bg-white/2">
              <Layers className="h-8 w-8 text-muted-foreground mb-3 opacity-20" />
              <p className="text-[10px] text-muted-foreground">
                Click a node to inspect
                <br />
                its connections
              </p>
            </div>
          )}

          {searchTerm && (
            <div className="mt-4 pt-3 border-t border-white/5">
              <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                <span>Filter</span>
                <span>{filteredNodes.length} matching</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
