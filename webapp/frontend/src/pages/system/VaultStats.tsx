import { Activity, ArrowLeft, BarChart2, Database, FolderOpen, RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiService } from "../../services/api";

type ProjectRow = { name: string; path: string; is_default?: boolean };

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-border bg-card/50 p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="mt-1 text-2xl font-semibold tabular-nums">{value}</p>
    </div>
  );
}

export default function VaultStats() {
  const [projects, setProjects] = useState<ProjectRow[]>([]);
  const [targetName, setTargetName] = useState("");
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const pr = await apiService.getProjects();
      if (pr.success && Array.isArray(pr.data)) {
        setProjects(pr.data as ProjectRow[]);
        const def = (pr.data as ProjectRow[]).find((p) => p.is_default)?.name;
        const pick =
          targetName || def || (pr.data as ProjectRow[])[0]?.name || apiService.activeProject;
        if (pick) {
          setTargetName(pick);
          apiService.activeProject = pick;
        }
      }
      const res = await apiService.getProjectStats();
      if (res.success && res.data) {
        setData(res.data);
      } else {
        setError(res.error || "Could not load stats");
        setData(null);
      }
    } catch (e) {
      setError(String(e));
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [targetName]);

  useEffect(() => {
    void load();
  }, [load]);

  const stats = (data?.statistics as Record<string, unknown> | undefined) || {};
  const activity = (data?.activity as Record<string, unknown> | undefined) || {};
  const system = (data?.system as Record<string, unknown> | undefined) || {};

  const entityTypes = (stats.entity_types as Record<string, number> | undefined) || {};
  const relTypes = (stats.relation_types as Record<string, number> | undefined) || {};

  return (
    <div className="mx-auto max-w-5xl space-y-8 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link
            to="/"
            className="mb-3 inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            Overview
          </Link>
          <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight">
            <BarChart2 className="h-7 w-7 text-accent" />
            Vault stats
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Live counts from the project info API.
          </p>
          <select
            className="mt-3 max-w-md rounded-lg border border-border bg-background px-3 py-2 text-sm"
            value={targetName}
            onChange={(e) => setTargetName(e.target.value)}
          >
            {projects.map((p) => (
              <option key={p.name} value={p.name}>
                {p.name}
                {p.is_default ? " (default)" : ""}
              </option>
            ))}
          </select>
        </div>
        <button
          type="button"
          onClick={() => void load()}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg border border-border bg-muted/40 px-4 py-2 text-sm hover:bg-muted disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/40 bg-red-950/30 px-4 py-3 text-sm text-red-200">
          {error}
        </div>
      )}

      {loading && !data ? (
        <p className="text-sm text-muted-foreground">Loading statistics…</p>
      ) : data ? (
        <>
          <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Entities" value={Number(stats.total_entities ?? 0)} />
            <StatCard label="Observations" value={Number(stats.total_observations ?? 0)} />
            <StatCard label="Relations" value={Number(stats.total_relations ?? 0)} />
            <StatCard
              label="Unresolved links"
              value={Number(stats.total_unresolved_relations ?? 0)}
            />
          </section>

          <section className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-border bg-card/30 p-5">
              <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold">
                <FolderOpen className="h-4 w-4" />
                Project
              </h2>
              <dl className="space-y-2 text-sm">
                <div className="flex justify-between gap-4">
                  <dt className="text-muted-foreground">Name</dt>
                  <dd className="font-mono text-right">{String(data.project_name ?? "")}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-muted-foreground">Path</dt>
                  <dd className="max-w-[70%] break-all text-right font-mono text-xs">
                    {String(data.project_path ?? "")}
                  </dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-muted-foreground">Default</dt>
                  <dd className="text-right">{String(data.default_project ?? "")}</dd>
                </div>
              </dl>
            </div>

            <div className="rounded-xl border border-border bg-card/30 p-5">
              <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold">
                <Database className="h-4 w-4" />
                System
              </h2>
              <dl className="space-y-2 text-sm">
                <div className="flex justify-between gap-4">
                  <dt className="text-muted-foreground">Version</dt>
                  <dd className="font-mono text-right">{String(system.version ?? "")}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-muted-foreground">Database size</dt>
                  <dd className="text-right">{String(system.database_size ?? "")}</dd>
                </div>
                <div className="flex flex-col gap-1">
                  <dt className="text-muted-foreground">Database path</dt>
                  <dd className="break-all font-mono text-xs">
                    {String(system.database_path ?? "")}
                  </dd>
                </div>
              </dl>
            </div>
          </section>

          <section className="rounded-xl border border-border bg-card/30 p-5">
            <h2 className="mb-3 text-sm font-semibold">Entities by type</h2>
            <div className="max-h-48 overflow-auto">
              <table className="w-full text-sm">
                <tbody>
                  {Object.entries(entityTypes)
                    .sort((a, b) => b[1] - a[1])
                    .map(([k, v]) => (
                      <tr key={k} className="border-b border-border/60 last:border-0">
                        <td className="py-1.5 font-mono text-xs">{k}</td>
                        <td className="py-1.5 text-right tabular-nums">{v}</td>
                      </tr>
                    ))}
                </tbody>
              </table>
              {Object.keys(entityTypes).length === 0 && (
                <p className="text-xs text-muted-foreground">No breakdown</p>
              )}
            </div>
          </section>

          <section className="rounded-xl border border-border bg-card/30 p-5">
            <h2 className="mb-3 text-sm font-semibold">Relations by type (top)</h2>
            <div className="max-h-48 overflow-auto">
              <table className="w-full text-sm">
                <tbody>
                  {Object.entries(relTypes)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 24)
                    .map(([k, v]) => (
                      <tr key={k} className="border-b border-border/60 last:border-0">
                        <td className="py-1.5 font-mono text-xs">{k}</td>
                        <td className="py-1.5 text-right tabular-nums">{v}</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="rounded-xl border border-border bg-card/30 p-5">
            <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold">
              <Activity className="h-4 w-4" />
              Recent (sample)
            </h2>
            <ul className="space-y-2 text-xs font-mono text-muted-foreground">
              {((activity.recently_updated as unknown[]) || [])
                .slice(0, 6)
                .map((row: any, i: number) => (
                  <li key={i}>
                    {row?.title || row?.permalink || JSON.stringify(row).slice(0, 80)}
                  </li>
                ))}
            </ul>
          </section>

          <p className="text-center text-xs text-muted-foreground">
            Need to refresh the index?{" "}
            <Link to="/vault/sync" className="text-accent underline-offset-2 hover:underline">
              Vault sync
            </Link>
          </p>
        </>
      ) : null}
    </div>
  );
}
