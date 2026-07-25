import {
  Activity,
  Clock,
  Database,
  Info,
  Loader2,
  Rewind,
  Search,
  Trash2,
  Users,
  Zap,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import apiService from "../../services/api";

interface SnapshotItem {
  snapshot_id: string;
  label: string;
  created_at: string;
  entity_count: number;
  observation_count: number;
  relation_count: number;
}

export default function Checkpoints() {
  const [snapshots, setSnapshots] = useState<SnapshotItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [creating, setCreating] = useState(false);
  const [labelInput, setLabelInput] = useState("");
  const [status, setStatus] = useState<any>(null);

  const fetchSnapshots = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiService.callMCPTool("adn_checkpoint", { operation: "list" });
      if (response.success && response.data?.snapshots) {
        setSnapshots(response.data.snapshots);
      }
    } catch (error) {
      console.error("Failed to fetch snapshots:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchStatus = useCallback(async () => {
    try {
      const response = await apiService.callMCPTool("adn_checkpoint", { operation: "status" });
      if (response.success) {
        setStatus(response.data);
      }
    } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    fetchSnapshots();
    fetchStatus();
  }, [fetchSnapshots, fetchStatus]);

  const handleCreate = useCallback(async () => {
    if (!labelInput.trim()) return;
    setCreating(true);
    try {
      await apiService.callMCPTool("adn_checkpoint", { operation: "create", label: labelInput.trim() });
      setLabelInput("");
      await fetchSnapshots();
      await fetchStatus();
    } catch (error) {
      console.error("Failed to create snapshot:", error);
    } finally {
      setCreating(false);
    }
  }, [labelInput, fetchSnapshots, fetchStatus]);

  const handleRollback = useCallback(async (snapshotId: string) => {
    if (!confirm(`Roll back to snapshot "${snapshotId}"? A pre-rollback snapshot will be created automatically.`)) {
      return;
    }
    try {
      const response = await apiService.callMCPTool("adn_checkpoint", { operation: "rollback", snapshot_id: snapshotId });
      if (response.success) {
        await fetchSnapshots();
        await fetchStatus();
      }
    } catch (error) {
      console.error("Failed to rollback:", error);
    }
  }, [fetchSnapshots, fetchStatus]);

  const handleDelete = useCallback(async (snapshotId: string) => {
    if (!confirm(`Delete snapshot "${snapshotId}"?`)) return;
    try {
      await apiService.callMCPTool("adn_checkpoint", { operation: "delete", snapshot_id: snapshotId });
      await fetchSnapshots();
    } catch (error) {
      console.error("Failed to delete snapshot:", error);
    }
  }, [fetchSnapshots]);

  const selectedSnapshot = snapshots.find((s) => s.snapshot_id === selectedId);

  const filtered = snapshots.filter(
    (s) =>
      s.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.snapshot_id.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <div className="max-w-[1400px] mx-auto h-[calc(100vh-12rem)] flex flex-col space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header */}
      <div className="flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-gradient-to-br from-amber-500/20 to-orange-500/20 rounded-xl border border-amber-500/20">
            <Activity className="h-6 w-6 text-amber-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Checkpoints</h1>
            <p className="text-muted-foreground text-xs">
              Native knowledge graph snapshots &mdash; freeze, browse, and roll back
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {status && (
            <div className="flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-[10px] font-bold text-emerald-300 tracking-wider">
              <Database className="h-3 w-3" />
              <span>{status.snapshot_count} snapshots</span>
            </div>
          )}
          <div className="flex items-center space-x-2">
            <input
              value={labelInput}
              onChange={(e) => setLabelInput(e.target.value)}
              placeholder="snapshot label..."
              className="w-40 bg-background border border-border rounded-lg px-3 py-1.5 text-xs outline-none focus:ring-1 focus:ring-amber-500/30"
              onKeyDown={(e) => e.key === "Enter" && handleCreate()}
            />
            <button
              onClick={handleCreate}
              disabled={creating || !labelInput.trim()}
              className="btn btn-sm btn-primary text-[10px] uppercase tracking-wider py-1.5 px-3 flex items-center space-x-1.5"
            >
              {creating ? <Loader2 className="h-3 w-3 animate-spin" /> : <Zap className="h-3 w-3" />}
              <span>{creating ? "Saving..." : "Snapshot"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Layout */}
      <div className="flex-1 flex space-x-6 overflow-hidden min-h-0">
        {/* Left: Snapshot Timeline */}
        <div className="w-96 shrink-0 flex flex-col space-y-4">
          <div className="card p-4 bg-muted/20 border-white/5 space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
              <input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search snapshots..."
                className="w-full bg-background border border-border rounded-lg pl-9 pr-3 py-2 text-sm outline-none focus:ring-1 focus:ring-amber-500/30"
              />
            </div>

            <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-widest text-muted-foreground px-1">
              <span>Timeline</span>
              <span>{filtered.length} Snapshots</span>
            </div>

            <div className="space-y-2 overflow-y-auto max-h-[calc(100vh-28rem)] pr-1 scrollbar-thin">
              {loading ? (
                <div className="flex flex-col items-center justify-center py-12 space-y-3 opacity-40">
                  <Loader2 className="h-6 w-6 animate-spin text-amber-500" />
                  <span className="text-[10px] uppercase tracking-widest font-bold">Loading...</span>
                </div>
              ) : filtered.length > 0 ? (
                filtered.map((s) => (
                  <button
                    key={s.snapshot_id}
                    onClick={() => setSelectedId(s.snapshot_id)}
                    className={`w-full text-left p-4 rounded-xl border transition-all ${
                      selectedId === s.snapshot_id
                        ? "bg-amber-500/10 border-amber-500/30 ring-1 ring-amber-500/20"
                        : "bg-muted/10 border-white/5 hover:border-white/10"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <Database className={`h-3.5 w-3.5 ${selectedId === s.snapshot_id ? "text-amber-400" : "text-muted-foreground"}`} />
                        <code className="text-[10px] font-mono opacity-50">{s.snapshot_id}</code>
                      </div>
                      <span className="text-[9px] text-muted-foreground font-mono">{s.created_at}</span>
                    </div>
                    <p className="text-xs font-medium leading-tight line-clamp-2 mb-2">{s.label}</p>
                    <div className="flex items-center justify-between opacity-60">
                      <div className="flex items-center space-x-1">
                        <Users className="h-3 w-3" />
                        <span className="text-[9px]">{s.entity_count} entities</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Zap className="h-3 w-3 text-amber-400" />
                        <span className="text-[9px]">{s.observation_count + s.relation_count} relations</span>
                      </div>
                    </div>
                  </button>
                ))
              ) : (
                <div className="text-center py-12 opacity-40">
                  <p className="text-[10px] uppercase tracking-widest font-bold">No snapshots yet</p>
                  <p className="text-[9px] mt-1">Enter a label above and click Snapshot</p>
                </div>
              )}
            </div>
          </div>

          <div className="card p-4 bg-amber-500/5 border-amber-500/10">
            <div className="flex items-center space-x-2 text-[10px] font-bold uppercase tracking-widest text-amber-400 mb-3">
              <Info className="h-3.5 w-3.5" />
              <span>Native Snapshots</span>
            </div>
            <p className="text-[10px] text-amber-100/60 leading-relaxed">
              Snapshots freeze the full knowledge graph state (entities, observations, relations).
              Rollback restores to a previous state with automatic pre-rollback backup.
              No external CLI dependencies.
            </p>
          </div>
        </div>

        {/* Right: Inspection */}
        <div className="flex-1 flex flex-col min-w-0">
          {selectedId ? (
            <div className="h-full flex flex-col space-y-4">
              <div className="card flex-1 flex flex-col overflow-hidden p-0 bg-black/40">
                <div className="p-4 border-b border-white/5 flex items-center justify-between shrink-0 bg-white/5">
                  <div className="flex items-center space-x-3">
                    <Database className="h-4 w-4 text-amber-400" />
                    <h3 className="text-xs font-bold uppercase tracking-widest">Snapshot Detail</h3>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleRollback(selectedId)}
                      className="btn btn-sm btn-outline text-[9px] uppercase tracking-wider py-1.5 px-3 flex items-center space-x-1.5 border-red-500/30 text-red-400"
                    >
                      <Rewind className="h-3 w-3" />
                      <span>Rollback</span>
                    </button>
                    <button
                      onClick={() => handleDelete(selectedId)}
                      className="btn btn-sm btn-outline text-[9px] uppercase tracking-wider py-1.5 px-3 flex items-center space-x-1.5 border-red-500/30 text-red-400"
                    >
                      <Trash2 className="h-3 w-3" />
                      <span>Delete</span>
                    </button>
                  </div>
                </div>

                <div className="flex-1 overflow-y-auto p-6 space-y-8 scrollbar-thin">
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <div className="w-1 h-3 rounded-full bg-amber-500" />
                      <h4 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                        Summary
                      </h4>
                    </div>
                    <div className="bg-white/5 border border-white/5 p-5 rounded-2xl space-y-2">
                      <p className="text-sm">
                        <strong>Label:</strong> {selectedSnapshot?.label}
                      </p>
                      <p className="text-sm">
                        <strong>Snapshot ID:</strong> {selectedSnapshot?.snapshot_id}
                      </p>
                      <p className="text-sm">
                        <strong>Created:</strong> {selectedSnapshot?.created_at}
                      </p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <div className="w-1 h-3 rounded-full bg-amber-500" />
                      <h4 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                        Contents
                      </h4>
                    </div>
                    <div className="grid grid-cols-3 gap-3">
                      <div className="p-4 bg-white/5 border border-white/5 rounded-xl text-center">
                        <p className="text-2xl font-bold text-amber-400">{selectedSnapshot?.entity_count ?? 0}</p>
                        <p className="text-[10px] text-muted-foreground mt-1">Entities</p>
                      </div>
                      <div className="p-4 bg-white/5 border border-white/5 rounded-xl text-center">
                        <p className="text-2xl font-bold text-amber-400">{selectedSnapshot?.observation_count ?? 0}</p>
                        <p className="text-[10px] text-muted-foreground mt-1">Observations</p>
                      </div>
                      <div className="p-4 bg-white/5 border border-white/5 rounded-xl text-center">
                        <p className="text-2xl font-bold text-amber-400">{selectedSnapshot?.relation_count ?? 0}</p>
                        <p className="text-[10px] text-muted-foreground mt-1">Relations</p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <div className="w-1 h-3 rounded-full bg-amber-500" />
                      <h4 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                        Actions
                      </h4>
                    </div>
                    <div className="font-mono text-[10px] space-y-1 text-muted-foreground/60 bg-black/60 p-4 rounded-xl border border-white/5">
                      <div>[INFO] Snapshot stored as gzipped JSONL</div>
                      <div>[INFO] Rollback creates automatic pre-rollback backup</div>
                      <div className="text-amber-400/80">
                        [READY] Native snapshot system — no external CLI required
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full card flex flex-col items-center justify-center text-center opacity-40 select-none grayscale">
              <Clock className="h-16 w-16 text-muted-foreground mb-4" />
              <h3 className="text-xl font-bold">Snapshot Inspector</h3>
              <p className="text-sm max-w-sm mt-2">
                Select a snapshot from the timeline to inspect its contents or roll back.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
