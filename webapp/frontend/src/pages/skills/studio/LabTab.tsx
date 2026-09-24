import { useCallback, useEffect, useState } from "react";
import { type StudioLabResult, type StudioScenario, apiService } from "../../../services/api";

export default function LabTab({ skillId }: { skillId: string }) {
  const [scenarios, setScenarios] = useState<StudioScenario[]>([]);
  const [history, setHistory] = useState<StudioLabResult[]>([]);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newPrompt, setNewPrompt] = useState("");
  const [newShouldFire, setNewShouldFire] = useState(true);

  const refresh = useCallback(async () => {
    if (!skillId) return;
    const [sc, hist] = await Promise.all([
      apiService.studioScenarios(skillId),
      apiService.studioLabHistory(skillId, 10),
    ]);
    if (sc.success && sc.data) setScenarios(sc.data.scenarios);
    if (hist.success && hist.data) {
      setHistory(
        hist.data.runs.map((r) => ({
          skill_id: r.skill_id,
          model: r.model,
          precision: r.precision,
          recall: r.recall,
          run_id: r.id,
          verdicts: r.verdicts,
        })),
      );
    }
  }, [skillId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const addScenario = async () => {
    if (!newPrompt.trim()) return;
    const res = await apiService.studioScenarioCreate(skillId, newPrompt.trim(), newShouldFire);
    if (res.success) {
      setNewPrompt("");
      refresh();
    } else {
      setError(res.error ?? "Could not create scenario");
    }
  };

  const removeScenario = async (id: number) => {
    await apiService.studioScenarioDelete(id);
    refresh();
  };

  const runLab = async () => {
    setRunning(true);
    setError(null);
    const res = await apiService.studioLabRun(skillId);
    setRunning(false);
    if (res.success && res.data) {
      refresh();
    } else {
      setError(res.error ?? "Lab run failed");
    }
  };

  const latest = history[0];
  const previous = history[1];

  return (
    <div className="space-y-6" data-testid="studio-lab">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">
          Grade <span className="text-white font-mono">{skillId || "no skill selected"}</span>{" "}
          against its scenario suite. Precision = fired-correct / fired-total. Recall =
          fired-correct / should-fire-total.
        </p>
        <button
          type="button"
          data-testid="studio-run"
          onClick={runLab}
          disabled={!skillId || running}
          className="px-4 py-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-40 text-white text-sm font-medium rounded-xl"
        >
          {running ? "Judging…" : "Run eval"}
        </button>
      </div>

      {error && <div className="text-sm text-red-300">{error}</div>}

      {latest && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="studio-scores">
          <ScoreCard label="Precision" value={latest.precision} prev={previous?.precision} />
          <ScoreCard label="Recall" value={latest.recall} prev={previous?.recall} />
          <div className="rounded-xl border border-white/10 bg-black/30 p-4">
            <div className="text-xs text-slate-500">Model</div>
            <div className="text-sm text-white font-mono truncate">{latest.model}</div>
          </div>
          <div className="rounded-xl border border-white/10 bg-black/30 p-4">
            <div className="text-xs text-slate-500">Scenarios judged</div>
            <div className="text-sm text-white">{latest.verdicts.length}</div>
          </div>
        </div>
      )}

      {latest?.verdicts.some((v) => v.fired !== v.should_fire) && (
        <div className="rounded-xl border border-yellow-500/30 bg-yellow-500/5 p-4 text-sm text-yellow-200">
          Misfires detected — rewrite the skill description from the failing prompts below, then
          re-run. That delta is the whole point of this tab.
        </div>
      )}

      <div>
        <h3 className="text-sm font-semibold text-white mb-2">Verdicts (latest run)</h3>
        <div className="space-y-2">
          {(latest?.verdicts ?? []).map((v) => (
            <div
              key={v.scenario_id}
              className={`rounded-xl border p-3 text-sm ${
                v.fired === v.should_fire
                  ? "border-emerald-500/20 bg-emerald-500/5"
                  : "border-red-500/30 bg-red-500/5"
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span
                  className={`text-xs font-bold px-2 py-0.5 rounded ${
                    v.fired === v.should_fire
                      ? "bg-emerald-500/20 text-emerald-300"
                      : "bg-red-500/20 text-red-300"
                  }`}
                >
                  {v.fired === v.should_fire ? "HIT" : v.fired ? "FALSE FIRE" : "MISS"}
                </span>
                <span className="text-xs text-slate-500">
                  expected {v.should_fire ? "FIRE" : "SKIP"}, judged {v.fired ? "FIRE" : "SKIP"}
                </span>
              </div>
              <div className="text-slate-300">{v.prompt}</div>
            </div>
          ))}
          {(!latest || latest.verdicts.length === 0) && (
            <p className="text-sm text-slate-500">No runs yet. Add scenarios, then Run eval.</p>
          )}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-white mb-2">Scenarios ({scenarios.length})</h3>
        <div className="space-y-2 mb-3">
          {scenarios.map((s) => (
            <div
              key={s.id}
              className="flex items-start gap-3 rounded-xl border border-white/10 bg-black/30 p-3"
            >
              <span
                className={`text-xs font-bold px-2 py-0.5 rounded mt-0.5 ${
                  s.should_fire
                    ? "bg-indigo-500/20 text-indigo-300"
                    : "bg-slate-500/20 text-slate-300"
                }`}
              >
                {s.should_fire ? "FIRE" : "SKIP"}
              </span>
              <div className="flex-1 text-sm text-slate-300">{s.prompt}</div>
              <button
                type="button"
                onClick={() => removeScenario(s.id)}
                className="text-xs text-slate-500 hover:text-red-300"
                aria-label="Delete scenario"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            value={newPrompt}
            onChange={(e) => setNewPrompt(e.target.value)}
            placeholder="New scenario prompt…"
            className="flex-1 rounded-xl border border-white/10 bg-black/30 px-4 py-2.5 text-sm text-white placeholder:text-slate-600 outline-none focus:border-amber-400/50"
          />
          <button
            type="button"
            onClick={() => setNewShouldFire(!newShouldFire)}
            className={`px-3 py-2 rounded-xl text-xs font-bold border ${
              newShouldFire
                ? "border-indigo-400/50 text-indigo-300"
                : "border-white/10 text-slate-400"
            }`}
          >
            {newShouldFire ? "FIRE" : "SKIP"}
          </button>
          <button
            type="button"
            onClick={addScenario}
            className="px-4 py-2 bg-white/10 hover:bg-white/15 text-sm text-white rounded-xl"
          >
            Add
          </button>
        </div>
      </div>
    </div>
  );
}

function ScoreCard({
  label,
  value,
  prev,
}: { label: string; value: number; prev: number | undefined }) {
  const delta = prev === undefined ? null : value - prev;
  return (
    <div className="rounded-xl border border-white/10 bg-black/30 p-4">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="text-2xl font-bold text-white">{(value * 100).toFixed(0)}%</div>
      {delta !== null && (
        <div className={`text-xs ${delta >= 0 ? "text-emerald-300" : "text-red-300"}`}>
          {delta >= 0 ? "+" : ""}
          {(delta * 100).toFixed(0)}pp vs previous
        </div>
      )}
    </div>
  );
}
