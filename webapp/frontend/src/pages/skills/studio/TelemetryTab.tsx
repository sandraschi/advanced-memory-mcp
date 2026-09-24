import { useCallback, useEffect, useState } from "react";
import { type StudioTelemetryData, apiService } from "../../../services/api";

export default function TelemetryTab({ skillId }: { skillId: string }) {
  const [data, setData] = useState<StudioTelemetryData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const res = await apiService.studioTelemetry(skillId || undefined);
    if (res.success && res.data) {
      setData(res.data);
      setError(null);
    } else {
      setError(res.error ?? "Could not load telemetry");
    }
  }, [skillId]);

  useEffect(() => {
    refresh();
    const t = window.setInterval(refresh, 15000);
    return () => window.clearInterval(t);
  }, [refresh]);

  const counts = data?.counts ?? {};
  const total = Object.values(counts).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-6" data-testid="studio-telemetry">
      <p className="text-sm text-slate-400">
        Door telemetry: which skills get activated and which sections get loaded. Identifiers only —
        no prompt content is ever logged. This is the raw material for trigger scoring and
        section-cost decisions.
      </p>

      {error && <div className="text-sm text-red-300">{error}</div>}
      {data?.disabled && (
        <div className="text-sm text-yellow-200">Telemetry disabled (ADN_SKILLS_TELEMETRY=0).</div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="rounded-xl border border-white/10 bg-black/30 p-4">
          <div className="text-xs text-slate-500">Total events</div>
          <div className="text-2xl font-bold text-white">{total}</div>
        </div>
        {(["activate", "load_section", "load_resource"] as const).map((k) => (
          <div key={k} className="rounded-xl border border-white/10 bg-black/30 p-4">
            <div className="text-xs text-slate-500 font-mono">{k}</div>
            <div className="text-2xl font-bold text-white">{counts[k] ?? 0}</div>
          </div>
        ))}
      </div>

      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-semibold text-white">Recent events</h3>
          <button
            type="button"
            onClick={refresh}
            className="text-xs text-slate-400 hover:text-white border border-white/10 rounded-lg px-3 py-1.5"
          >
            Refresh
          </button>
        </div>
        <div className="space-y-1.5">
          {(data?.events ?? []).slice(0, 60).map((e) => (
            <div
              key={e.id}
              className="flex items-center gap-3 rounded-lg border border-white/5 bg-black/20 px-3 py-2 text-xs font-mono"
            >
              <span className="text-slate-500">{e.created_at}</span>
              <span className="text-indigo-300">{e.event}</span>
              <span className="text-white truncate flex-1">{e.skill_id}</span>
              {e.section && <span className="text-amber-300 truncate">{e.section}</span>}
            </div>
          ))}
          {(data?.events ?? []).length === 0 && (
            <p className="text-sm text-slate-500">
              No events yet. Activate a skill or load a section, then refresh.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
