import { useCallback, useEffect, useState } from "react";
import { type StudioDistillJob, apiService } from "../../../services/api";

export default function DistillTab({ skillId }: { skillId: string }) {
  const [source, setSource] = useState("");
  const [draft, setDraft] = useState("");
  const [jobId, setJobId] = useState<number | null>(null);
  const [sourceTitle, setSourceTitle] = useState("");
  const [jobs, setJobs] = useState<StudioDistillJob[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<string | null>(null);

  const refreshJobs = useCallback(async () => {
    const res = await apiService.studioDistillJobs();
    if (res.success && res.data) setJobs(res.data.jobs);
  }, []);

  useEffect(() => {
    refreshJobs();
  }, [refreshJobs]);

  const preview = async () => {
    if (!skillId || !source.trim()) return;
    setBusy(true);
    setError(null);
    setDone(null);
    const res = await apiService.studioDistillPreview(skillId, source.trim());
    setBusy(false);
    if (res.success && res.data) {
      setDraft(res.data.draft_md);
      setJobId(res.data.job_id);
      setSourceTitle(res.data.source_title);
    } else {
      setError(res.error ?? "Preview failed");
    }
  };

  const apply = async () => {
    if (jobId === null) return;
    setBusy(true);
    setError(null);
    const res = await apiService.studioDistillApply(jobId, draft);
    setBusy(false);
    if (res.success && res.data) {
      setDone(`Applied to ${res.data.path} (backup kept).`);
      setDraft("");
      setJobId(null);
      refreshJobs();
    } else {
      setError(res.error ?? "Apply failed");
    }
  };

  return (
    <div className="space-y-6" data-testid="studio-distill">
      <p className="text-sm text-slate-400">
        Turn answered discussions, issues, or notes into skill sections. Preview drafts freely —
        nothing writes without your approval, and every apply keeps a timestamped backup.
      </p>

      <div className="flex gap-2">
        <input
          value={source}
          onChange={(e) => setSource(e.target.value)}
          placeholder="discussion:22, issue:15, or note:/abs/path.md"
          className="flex-1 rounded-xl border border-white/10 bg-black/30 px-4 py-2.5 text-sm text-white placeholder:text-slate-600 outline-none focus:border-amber-400/50 font-mono"
        />
        <button
          type="button"
          data-testid="studio-preview"
          onClick={preview}
          disabled={!skillId || !source.trim() || busy}
          className="px-4 py-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-40 text-white text-sm font-medium rounded-xl"
        >
          {busy ? "Working…" : "Preview draft"}
        </button>
      </div>

      {error && <div className="text-sm text-red-300">{error}</div>}
      {done && <div className="text-sm text-emerald-300">{done}</div>}

      {draft && (
        <div className="space-y-2">
          <div className="text-xs text-slate-500">
            Draft from <span className="text-slate-300">{sourceTitle}</span> (job #{jobId}) — edit
            freely, then approve.
          </div>
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            rows={14}
            className="w-full rounded-xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-slate-200 font-mono outline-none focus:border-amber-400/50"
          />
          <div className="flex gap-2">
            <button
              type="button"
              data-testid="studio-apply"
              onClick={apply}
              disabled={busy}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white text-sm font-medium rounded-xl"
            >
              Approve and write to skill
            </button>
            <button
              type="button"
              onClick={() => {
                setDraft("");
                setJobId(null);
              }}
              className="px-4 py-2 bg-white/10 hover:bg-white/15 text-sm text-white rounded-xl"
            >
              Discard
            </button>
          </div>
        </div>
      )}

      <div>
        <h3 className="text-sm font-semibold text-white mb-2">Job history</h3>
        <div className="space-y-2">
          {jobs.map((j) => (
            <div
              key={j.id}
              className="flex items-center gap-3 rounded-xl border border-white/10 bg-black/30 px-4 py-2.5 text-sm"
            >
              <span className="text-slate-500 font-mono">#{j.id}</span>
              <span className="text-white font-mono text-xs">{j.skill_id}</span>
              <span className="text-slate-400 font-mono text-xs truncate flex-1">{j.source}</span>
              <span
                className={`text-xs font-bold px-2 py-0.5 rounded ${
                  j.state === "applied"
                    ? "bg-emerald-500/20 text-emerald-300"
                    : "bg-amber-500/20 text-amber-300"
                }`}
              >
                {j.state.toUpperCase()}
              </span>
            </div>
          ))}
          {jobs.length === 0 && <p className="text-sm text-slate-500">No distill jobs yet.</p>}
        </div>
      </div>
    </div>
  );
}
