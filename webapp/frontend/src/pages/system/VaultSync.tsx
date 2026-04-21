import {
  ArrowLeft,
  Eye,
  EyeOff,
  FolderOpen,
  FolderSync,
  HardDrive,
  Library,
  RefreshCw,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { KnowledgeModelExplainer } from "../../components/KnowledgeModelExplainer";
import { apiService } from "../../services/api";

type ProjectRow = { name: string; path: string; is_default?: boolean };

type SyncProjectStatus = {
  project_name: string;
  status: string;
  message: string;
  files_processed: number;
  files_total: number;
  percent: number | null;
  error: string | null;
};

type SyncStatusPayload = {
  global_status: string;
  is_syncing: boolean;
  projects: SyncProjectStatus[];
};

export default function VaultSync() {
  const [projects, setProjects] = useState<ProjectRow[]>([]);
  const [targetName, setTargetName] = useState("");
  const [watchRunning, setWatchRunning] = useState<boolean | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [syncStatus, setSyncStatus] = useState<SyncStatusPayload | null>(null);
  const [reindexSeconds, setReindexSeconds] = useState(0);
  const [ragExtraPaths, setRagExtraPaths] = useState<string[]>([]);
  const [ragDraft, setRagDraft] = useState("");
  const [ragBusy, setRagBusy] = useState(false);
  const [ragPickerNote, setRagPickerNote] = useState<string | null>(null);
  const syncPollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const reindexTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refreshRagRoots = useCallback(async () => {
    const res = await apiService.getRagExtraRoots();
    if (res.success && res.data) {
      setRagExtraPaths(res.data.paths);
    }
  }, []);

  const refreshProjects = useCallback(async () => {
    const res = await apiService.getProjects();
    if (res.success && Array.isArray(res.data)) {
      setProjects(res.data as ProjectRow[]);
      const def = (res.data as ProjectRow[]).find((p) => p.is_default)?.name;
      const pick = def || (res.data as ProjectRow[])[0]?.name || apiService.activeProject;
      setTargetName(pick);
      if (pick) apiService.activeProject = pick;
    }
  }, []);

  const pollWatch = useCallback(async () => {
    const res = await apiService.getWatchStatus();
    if (res.success && res.data) {
      setWatchRunning(res.data.running);
    } else {
      setWatchRunning(null);
    }
  }, []);

  useEffect(() => {
    void refreshProjects();
  }, [refreshProjects]);

  useEffect(() => {
    void refreshRagRoots();
  }, [refreshRagRoots]);

  useEffect(() => {
    void pollWatch();
    const t = setInterval(() => void pollWatch(), 4000);
    return () => clearInterval(t);
  }, [pollWatch]);

  const clearSyncPoll = () => {
    if (syncPollRef.current) {
      clearInterval(syncPollRef.current);
      syncPollRef.current = null;
    }
  };

  const startSyncPoll = () => {
    clearSyncPoll();
    const tick = async () => {
      const s = await apiService.getSyncOperationStatus();
      if (s.success && s.data) {
        setSyncStatus(s.data as SyncStatusPayload);
      }
    };
    void tick();
    syncPollRef.current = setInterval(() => void tick(), 400);
  };

  const run = async (
    label: string,
    fn: () => Promise<{ success: boolean; error?: string; data?: unknown }>,
  ) => {
    setBusy(label);
    setError(null);
    setMessage(null);
    try {
      const out = await fn();
      if (out.success) {
        setMessage(
          typeof out.data === "object"
            ? JSON.stringify(out.data, null, 2)
            : String(out.data ?? "Done"),
        );
      } else {
        setError(out.error || "Request failed");
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(null);
      void pollWatch();
    }
  };

  const runVaultScan = async () => {
    setBusy("vault-scan");
    setError(null);
    setMessage(null);
    setSyncStatus(null);
    startSyncPoll();
    try {
      apiService.activeProject = targetName;
      const out = await apiService.syncVaultFiles(targetName);
      if (out.success) {
        setMessage(JSON.stringify(out.data, null, 2));
      } else {
        setError(out.error || "Vault sync failed");
      }
    } catch (e) {
      setError(String(e));
    } finally {
      clearSyncPoll();
      const s = await apiService.getSyncOperationStatus();
      if (s.success && s.data) {
        setSyncStatus(s.data as SyncStatusPayload);
      }
      setBusy(null);
      void pollWatch();
    }
  };

  const pickRagFolderHint = async () => {
    const w = window as Window & {
      showDirectoryPicker?: () => Promise<FileSystemDirectoryHandle>;
    };
    if (!w.showDirectoryPicker) {
      setRagPickerNote(
        "This browser cannot turn a folder pick into a drive path. Enter the full server path manually (e.g. D:\\Dev\\repos\\mcp-central-docs).",
      );
      return;
    }
    try {
      const handle = await w.showDirectoryPicker();
      setRagPickerNote(
        `Folder name: "${handle.name}". Paste the full path the API machine uses (Explorer address bar, or Shift+Right-click → Copy as path), then Add.`,
      );
    } catch {
      setRagPickerNote(null);
    }
  };

  const saveRagRoots = async () => {
    setRagBusy(true);
    setError(null);
    setMessage(null);
    try {
      const out = await apiService.setRagExtraRoots(ragExtraPaths);
      if (out.success) {
        setMessage(JSON.stringify(out.data, null, 2));
        await refreshRagRoots();
      } else {
        setError(out.error || "Save failed");
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setRagBusy(false);
    }
  };

  const validateRagRoots = async () => {
    setRagBusy(true);
    setError(null);
    setMessage(null);
    try {
      const out = await apiService.validateRagExtraRoots(ragExtraPaths);
      if (out.success && out.data) {
        setMessage(JSON.stringify(out.data, null, 2));
      } else {
        setError(out.error || "Validate failed");
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setRagBusy(false);
    }
  };

  const runReindex = async () => {
    setBusy("reindex");
    setError(null);
    setMessage(null);
    setReindexSeconds(0);
    const t0 = Date.now();
    reindexTimerRef.current = setInterval(() => {
      setReindexSeconds(Math.floor((Date.now() - t0) / 1000));
    }, 500);
    try {
      apiService.activeProject = targetName;
      const out = await apiService.reindexSearch(targetName);
      if (out.success) {
        setMessage(JSON.stringify(out.data, null, 2));
      } else {
        setError(out.error || "Reindex failed");
      }
    } catch (e) {
      setError(String(e));
    } finally {
      if (reindexTimerRef.current) {
        clearInterval(reindexTimerRef.current);
        reindexTimerRef.current = null;
      }
      setBusy(null);
      void pollWatch();
    }
  };

  useEffect(() => {
    return () => {
      clearSyncPoll();
      if (reindexTimerRef.current) {
        clearInterval(reindexTimerRef.current);
      }
    };
  }, []);

  const scanRow = syncStatus?.projects?.find((p) => p.project_name === targetName);
  const scanPct =
    scanRow?.percent != null
      ? Math.min(100, Math.max(0, scanRow.percent))
      : scanRow && scanRow.files_total > 0
        ? Math.min(100, Math.round((100 * scanRow.files_processed) / scanRow.files_total))
        : null;

  return (
    <div className="mx-auto max-w-3xl space-y-8 p-6">
      <div>
        <Link
          to="/"
          className="mb-3 inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Overview
        </Link>
        <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight">
          <FolderSync className="h-7 w-7 text-accent" />
          Vault sync
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          These actions run on the FastAPI backend (same process as{" "}
          <code className="rounded bg-muted px-1 text-xs">start.ps1</code>). They do not replace
          starting the backend itself.
        </p>
        <KnowledgeModelExplainer className="mt-4" />
      </div>

      <section className="rounded-xl border border-border bg-card/40 p-5 space-y-4">
        <h2 className="text-sm font-semibold">Target project</h2>
        <p className="text-xs text-muted-foreground">
          Filesystem sync uses the project <strong>name</strong> (config / DB). URL routes may use
          permalink; pick the row you want to scan.
        </p>
        <select
          className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
          value={targetName}
          onChange={(e) => {
            const n = e.target.value;
            setTargetName(n);
            apiService.activeProject = n;
          }}
        >
          {projects.map((p) => (
            <option key={p.name} value={p.name} title={p.path}>
              {p.name}
              {p.is_default ? " (default)" : ""} — {p.path}
            </option>
          ))}
        </select>
        {(() => {
          const sel = projects.find((p) => p.name === targetName);
          return sel ? (
            <p className="rounded-md border border-border/60 bg-muted/20 px-3 py-2 text-xs leading-relaxed">
              <span className="font-medium text-foreground">Vault folder: </span>
              <code className="break-all text-muted-foreground">{sel.path}</code>
            </p>
          ) : null;
        })()}
      </section>

      <section className="rounded-xl border border-border bg-card/40 p-5 space-y-4">
        <h2 className="flex items-center gap-2 text-sm font-semibold">
          <FolderOpen className="h-4 w-4" />
          Extra RAG folders (LanceDB)
        </h2>
        <p className="text-xs text-muted-foreground">
          Absolute folders on the <strong className="text-foreground/90">machine running the API</strong> whose{" "}
          <code className="rounded bg-muted/80 px-1">.md</code>,{" "}
          <code className="rounded bg-muted/80 px-1">.mdx</code>, and{" "}
          <code className="rounded bg-muted/80 px-1">.txt</code> files are chunked into the vector index on{" "}
          <strong className="text-foreground/90">Rebuild search index</strong>. These chunks are included in semantic
          search for every vault project.
        </p>
        {ragPickerNote ? (
          <p className="rounded-md border border-border/60 bg-muted/20 px-3 py-2 text-xs text-muted-foreground">
            {ragPickerNote}
          </p>
        ) : null}
        <ul className="space-y-2">
          {ragExtraPaths.map((p) => (
            <li
              key={p}
              className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-border/60 bg-muted/10 px-3 py-2 text-xs"
            >
              <code className="break-all text-muted-foreground">{p}</code>
              <button
                type="button"
                disabled={ragBusy}
                onClick={() => setRagExtraPaths(ragExtraPaths.filter((x) => x !== p))}
                className="shrink-0 rounded border border-border px-2 py-1 text-[11px] hover:bg-muted disabled:opacity-50"
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
        <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
          <input
            type="text"
            className="min-w-0 flex-1 rounded-lg border border-border bg-background px-3 py-2 text-sm font-mono"
            placeholder="D:\Dev\repos\mcp-central-docs"
            value={ragDraft}
            onChange={(e) => setRagDraft(e.target.value)}
            disabled={ragBusy}
          />
          <button
            type="button"
            disabled={ragBusy}
            onClick={() => {
              const t = ragDraft.trim();
              if (!t) return;
              if (ragExtraPaths.includes(t)) {
                setRagDraft("");
                return;
              }
              setRagExtraPaths([...ragExtraPaths, t]);
              setRagDraft("");
            }}
            className="rounded-lg border border-border bg-background px-4 py-2 text-sm hover:bg-muted disabled:opacity-50"
          >
            Add path
          </button>
          <button
            type="button"
            disabled={ragBusy}
            onClick={() => void pickRagFolderHint()}
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-border bg-background px-4 py-2 text-sm hover:bg-muted disabled:opacity-50"
          >
            <FolderOpen className="h-4 w-4" />
            Folder hint
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            disabled={ragBusy}
            onClick={() => void saveRagRoots()}
            className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground hover:opacity-90 disabled:opacity-50"
          >
            Save to config
          </button>
          <button
            type="button"
            disabled={ragBusy}
            onClick={() => void validateRagRoots()}
            className="rounded-lg border border-border bg-background px-4 py-2 text-sm hover:bg-muted disabled:opacity-50"
          >
            Validate on server
          </button>
          <button
            type="button"
            disabled={ragBusy}
            onClick={() => void refreshRagRoots()}
            className="text-sm text-muted-foreground underline"
          >
            Reload from server
          </button>
        </div>
      </section>

      <section className="rounded-xl border border-border bg-card/40 p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="flex items-center gap-2 text-sm font-semibold">
            <Eye className="h-4 w-4" />
            File watch
          </h2>
          <span className="text-xs text-muted-foreground">
            Status:{" "}
            {watchRunning === null ? (
              "unknown"
            ) : watchRunning ? (
              <span className="text-green-600 dark:text-green-400">running</span>
            ) : (
              <span className="text-amber-700 dark:text-amber-400">stopped</span>
            )}
          </span>
        </div>
        <p className="text-xs text-muted-foreground">
          Watches the vault folder and applies changes into the database while the API process stays
          up.
        </p>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            disabled={!!busy}
            onClick={() => void run("start-watch", () => apiService.startWatch())}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground hover:opacity-90 disabled:opacity-50"
          >
            <Eye className="h-4 w-4" />
            Start watch
          </button>
          <button
            type="button"
            disabled={!!busy}
            onClick={() => void run("stop-watch", () => apiService.stopWatch())}
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-4 py-2 text-sm hover:bg-muted disabled:opacity-50"
          >
            <EyeOff className="h-4 w-4" />
            Stop watch
          </button>
          <button
            type="button"
            disabled={!!busy}
            onClick={() => void pollWatch()}
            className="text-sm text-muted-foreground underline"
          >
            Refresh status
          </button>
        </div>
      </section>

      <section className="rounded-xl border border-border bg-card/40 p-5 space-y-4">
        <h2 className="flex items-center gap-2 text-sm font-semibold">
          <HardDrive className="h-4 w-4" />
          Index and registry
        </h2>
        <ul className="list-disc space-y-2 pl-5 text-xs text-muted-foreground">
          <li>
            <strong>Scan vault files</strong> — walk markdown on disk, create/update/delete entities
            (heavy on large vaults).
          </li>
          <li>
            <strong>Rebuild search index</strong> — rebuilds SQLite FTS <em>and</em> the LanceDB
            vector store used for semantic / hybrid search (long-running).
          </li>
          <li>
            <strong>Sync project registry</strong> — align configured projects with the database
            only (quick).
          </li>
        </ul>
        <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
          <button
            type="button"
            disabled={!!busy || !targetName}
            onClick={() => void runVaultScan()}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground hover:opacity-90 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${busy === "vault-scan" ? "animate-spin" : ""}`} />
            Scan vault files
          </button>
          <button
            type="button"
            disabled={!!busy}
            onClick={() => void runReindex()}
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-border bg-background px-4 py-2 text-sm hover:bg-muted disabled:opacity-50"
          >
            <Library className={`h-4 w-4 ${busy === "reindex" ? "animate-spin" : ""}`} />
            Rebuild search index
          </button>
          <button
            type="button"
            disabled={!!busy}
            onClick={() => void run("registry", () => apiService.syncProjectsRegistry())}
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-border bg-background px-4 py-2 text-sm hover:bg-muted disabled:opacity-50"
          >
            Sync project registry
          </button>
        </div>
      </section>

      {(busy === "vault-scan" || busy === "reindex") && (
        <section
          className="rounded-xl border border-border bg-card/40 p-5 space-y-3"
          aria-live="polite"
        >
          <h3 className="text-sm font-semibold">Activity</h3>
          {busy === "vault-scan" && (
            <div className="space-y-2 text-sm">
              <p className="text-muted-foreground">
                <span className="font-medium text-foreground">{targetName}</span>
                {scanRow?.message ? ` — ${scanRow.message}` : " — scanning…"}
              </p>
              {scanRow?.error ? <p className="text-red-400 text-xs">{scanRow.error}</p> : null}
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>
                  {scanRow != null
                    ? `${scanRow.files_processed} / ${scanRow.files_total || "—"} files`
                    : "Waiting for status…"}
                </span>
                {scanPct != null ? (
                  <span>{scanPct}%</span>
                ) : busy === "vault-scan" ? (
                  <span className="animate-pulse">…</span>
                ) : null}
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-primary transition-[width] duration-300 ease-out"
                  style={{ width: scanPct != null ? `${scanPct}%` : "8%" }}
                />
              </div>
            </div>
          )}
          {busy === "reindex" && (
            <div className="space-y-2 text-sm">
              <p className="text-muted-foreground">
                Rebuilding search index for{" "}
                <span className="font-medium text-foreground">{targetName}</span> —{" "}
                <span className="tabular-nums">{reindexSeconds}s</span> elapsed (no per-file
                progress from API).
              </p>
              <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                <div className="h-full w-1/3 animate-pulse rounded-full bg-primary" />
              </div>
            </div>
          )}
        </section>
      )}

      {busy && busy !== "vault-scan" && busy !== "reindex" && (
        <p className="text-sm text-muted-foreground">Running: {busy}…</p>
      )}
      {error && (
        <div className="rounded-lg border border-red-500/40 bg-red-950/30 px-4 py-3 text-sm text-red-200">
          {error}
        </div>
      )}
      {message && (
        <pre className="max-h-64 overflow-auto rounded-lg border border-border bg-muted/30 p-4 text-xs font-mono">
          {message}
        </pre>
      )}

      <p className="text-center text-sm">
        <Link to="/vault/stats" className="text-accent underline-offset-2 hover:underline">
          View vault stats
        </Link>
      </p>
    </div>
  );
}
