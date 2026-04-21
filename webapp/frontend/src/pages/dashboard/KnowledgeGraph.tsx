import { Loader2, Maximize2, Network, RefreshCw } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { Link } from "react-router-dom";
import { apiService } from "../../services/api";

interface GraphData {
  nodes: any[];
  links: any[];
}

export default function KnowledgeGraph() {
  const [data, setData] = useState<GraphData>({ nodes: [], links: [] });
  const [isLoading, setIsLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [centerInput, setCenterInput] = useState("");
  const [depth, setDepth] = useState(2);
  const [maxNodes, setMaxNodes] = useState(400);
  const [meta, setMeta] = useState<Record<string, unknown> | null>(null);
  const [loadMessage, setLoadMessage] = useState<string | null>(null);
  const fgRef = useRef<any>();

  const fetchGraphData = useCallback(async () => {
    setIsLoading(true);
    setLoadMessage(null);
    setMeta(null);
    try {
      await apiService.getProjects();
      const trimmed = centerInput.trim();
      const center: string | null = trimmed === "" ? null : trimmed;
      const response = await apiService.getGraphSubgraph({
        center,
        depth,
        max_nodes: maxNodes,
        max_edges: Math.min(maxNodes * 2, 2000),
        include_unresolved: true,
      });
      const m =
        response.success && response.data?.meta
          ? (response.data.meta as Record<string, unknown>)
          : null;
      setMeta(m);
      if (m?.error === "center_not_found") {
        setLoadMessage(`No note found for center “${String(m.center)}”. Check the permalink.`);
        setData({ nodes: [], links: [] });
        return;
      }
      if (m?.empty_project) {
        setLoadMessage(
          "No markdown notes in this project yet. Import or create notes, then refresh.",
        );
        setData({ nodes: [], links: [] });
        return;
      }
      const nodes = response.success && response.data?.nodes ? response.data.nodes : [];
      const links = response.success && response.data?.links ? response.data.links : [];
      if (response.success) {
        setData({ nodes, links });
        if (nodes.length === 0) {
          setLoadMessage(
            "No graph edges in this neighborhood. Try another center or increase depth.",
          );
        }
      } else {
        setLoadMessage(response.error || "Could not load graph.");
        setData({ nodes: [], links: [] });
      }
    } catch (err) {
      console.error("Failed to fetch graph data:", err);
      setLoadMessage("Network error loading graph.");
      setData({ nodes: [], links: [] });
    } finally {
      setIsLoading(false);
    }
  }, [centerInput, depth, maxNodes]);

  useEffect(() => {
    fetchGraphData();
  }, []);

  const handleNodeClick = (node: any) => {
    setSelectedNode(node);
    if (fgRef.current) {
      fgRef.current.centerAt(node.x, node.y, 1000);
      fgRef.current.zoom(2, 1000);
    }
  };

  const stats =
    meta && typeof meta.node_count === "number"
      ? `${meta.node_count} nodes · ${meta.edge_count ?? 0} links · depth ${meta.depth ?? depth}`
      : null;

  return (
    <div className="h-full flex flex-col space-y-4 animate-in fade-in duration-500">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">PointCloud Explorer</h1>
          <p className="text-muted-foreground text-sm">
            Link graph from your vault (same relations as Obsidian-style notes). Large vaults stay
            fast by loading a <strong>bounded neighborhood</strong> only.
          </p>
        </div>
        <div className="flex flex-wrap items-end gap-2">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-muted-foreground">Center (permalink, optional)</label>
            <input
              type="text"
              value={centerInput}
              onChange={(e) => setCenterInput(e.target.value)}
              placeholder="e.g. notes/my-topic"
              className="rounded-md border border-border bg-background px-3 py-2 text-sm w-56 min-w-[12rem]"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-muted-foreground">Depth</label>
            <select
              value={depth}
              onChange={(e) => setDepth(Number(e.target.value))}
              className="rounded-md border border-border bg-background px-2 py-2 text-sm"
            >
              {[1, 2, 3, 4, 5].map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-muted-foreground">Max nodes</label>
            <select
              value={maxNodes}
              onChange={(e) => setMaxNodes(Number(e.target.value))}
              className="rounded-md border border-border bg-background px-2 py-2 text-sm"
            >
              {[200, 400, 800, 1200].map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </div>
          <button
            type="button"
            onClick={() => fetchGraphData()}
            className="inline-flex items-center gap-2 rounded-md border border-border bg-muted/40 px-3 py-2 text-sm hover:bg-muted"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
            Load graph
          </button>
          <button
            type="button"
            onClick={() => fgRef.current?.zoomToFit(400)}
            className="p-2 hover:bg-muted rounded-full transition-colors border border-border"
            title="Fit to screen"
          >
            <Maximize2 className="h-5 w-5" />
          </button>
        </div>
      </div>

      {stats && (
        <p className="text-xs text-muted-foreground font-mono">
          Project <span className="text-foreground">{apiService.activeProject}</span> · {stats}
        </p>
      )}

      {loadMessage && (
        <div
          className={`rounded-lg border px-3 py-2 text-sm ${
            loadMessage.includes("No note found") || loadMessage.includes("Network")
              ? "border-red-500/40 bg-red-950/40 text-red-100"
              : "border-amber-500/40 bg-amber-950/50 text-amber-100"
          }`}
        >
          {loadMessage}
        </div>
      )}

      <div className="flex-1 relative card overflow-hidden border-accent/20 bg-background/50 min-h-[600px]">
        {isLoading && (
          <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-background/60 backdrop-blur-sm">
            <Loader2 className="h-12 w-12 text-accent animate-spin mb-4" />
            <p className="font-medium animate-pulse">Loading link graph…</p>
          </div>
        )}

        <ForceGraph2D
          ref={fgRef}
          graphData={data}
          nodeLabel="label"
          nodeColor={(node) => {
            if (selectedNode && node.id === selectedNode.id) return "#ff00ff";
            switch (node.type) {
              case "entity":
                return "#3b82f6";
              case "unresolved":
                return "#94a3b8";
              case "observation":
                return "#a855f7";
              case "skill":
                return "#22c55e";
              default:
                return "#64748b";
            }
          }}
          nodeRelSize={5}
          linkColor={() => "rgba(255, 255, 255, 0.12)"}
          linkDirectionalParticles={1}
          linkDirectionalParticleSpeed={0.005}
          backgroundColor="rgba(0,0,0,0)"
          onNodeClick={handleNodeClick}
          width={typeof window !== "undefined" ? window.innerWidth - 300 : 800}
          height={600}
        />

        {selectedNode && (
          <div className="absolute bottom-6 left-6 right-6 lg:right-auto lg:w-96 card p-6 bg-background/90 backdrop-blur-md border-accent/30 shadow-2xl animate-in slide-in-from-left-4 duration-300">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-2 min-w-0">
                <Network className="h-5 w-5 text-accent shrink-0" />
                <h3 className="font-bold text-lg truncate">{selectedNode.label}</h3>
              </div>
              <button
                type="button"
                onClick={() => setSelectedNode(null)}
                className="text-muted-foreground hover:text-foreground shrink-0"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3">
              <div className="flex items-center space-x-2 text-xs uppercase tracking-widest font-bold text-muted-foreground">
                <span
                  className={`w-2 h-2 rounded-full ${
                    selectedNode.type === "entity"
                      ? "bg-blue-500"
                      : selectedNode.type === "unresolved"
                        ? "bg-slate-400"
                        : "bg-purple-500"
                  }`}
                />
                <span>{selectedNode.type}</span>
              </div>

              <p className="text-sm text-muted-foreground break-all">
                Id: <code className="bg-muted px-1 rounded text-xs">{selectedNode.id}</code>
              </p>

              {selectedNode.type === "entity" && (
                <div className="pt-4 flex border-t border-white/5">
                  <Link
                    className="btn btn-primary btn-sm w-full text-center"
                    to={`/notes?id=${encodeURIComponent(selectedNode.id)}`}
                  >
                    Open in vault
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="absolute top-4 left-4 flex flex-col space-y-2 p-3 bg-background/50 backdrop-blur-sm rounded-lg border border-white/5 text-[10px] uppercase font-bold tracking-wider">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-blue-500" />
            <span>Notes</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-slate-400" />
            <span>Unresolved link</span>
          </div>
        </div>
      </div>
    </div>
  );
}
