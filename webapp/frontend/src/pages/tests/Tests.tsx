import { AlertCircle, CheckCircle, Loader2, Play, XCircle } from "lucide-react";
import { useState } from "react";
import { apiService } from "../../services/api";

export default function Tests() {
  const [running, setRunning] = useState(false);
  const [target, setTarget] = useState("tests");
  const [result, setResult] = useState<{
    success: boolean;
    exit_code: number;
    stdout: string;
    stderr: string;
    duration_seconds: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async () => {
    setRunning(true);
    setResult(null);
    setError(null);
    try {
      const response = await apiService.runTests({
        target: target.trim() || "tests",
        timeout_seconds: 300,
      });
      if (response.success && response.data) {
        setResult(response.data);
      } else {
        setError(response.error ?? "Run failed");
        if (response.data) setResult(response.data);
      }
    } catch (e: any) {
      setError(e?.message ?? "Request failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-background">
      <div className="border-b border-white/5 bg-black/20 backdrop-blur-xl px-10 py-8">
        <div className="max-w-4xl mx-auto space-y-4">
          <h1 className="text-2xl font-bold tracking-tight">Tests</h1>
          <p className="text-sm text-muted-foreground">
            Run the project test suite (pytest) from the webapp. Backend must be started with
            ENABLE_WEBAPP_TESTS=1.
          </p>
          <div className="flex flex-wrap items-center gap-4">
            <input
              type="text"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="tests"
              className="bg-black/40 border border-white/10 rounded-xl px-4 py-2 text-sm font-mono w-48 focus:outline-none focus:border-white/20"
            />
            <button
              type="button"
              onClick={handleRun}
              disabled={running}
              className="inline-flex items-center gap-2 bg-primary hover:bg-primary/90 disabled:opacity-50 text-primary-foreground px-5 py-2.5 rounded-xl font-medium text-sm transition-all"
            >
              {running ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Play className="h-4 w-4" />
              )}
              {running ? "Running…" : "Run tests"}
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-10 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {error && (
            <div className="flex items-center gap-3 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {result && (
            <>
              <div className="flex flex-wrap items-center gap-4">
                {result.success ? (
                  <span className="inline-flex items-center gap-2 text-green-400">
                    <CheckCircle className="h-5 w-5" />
                    Passed
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-2 text-red-400">
                    <XCircle className="h-5 w-5" />
                    Failed (exit code {result.exit_code})
                  </span>
                )}
                <span className="text-muted-foreground text-sm">
                  Duration: {result.duration_seconds}s
                </span>
              </div>

              <div className="space-y-2">
                <div className="rounded-xl bg-black/40 border border-white/10 overflow-hidden">
                  <div className="px-4 py-2 border-b border-white/5 text-xs font-mono text-muted-foreground">
                    stdout
                  </div>
                  <pre className="p-4 text-xs font-mono text-slate-300 whitespace-pre-wrap overflow-x-auto max-h-[50vh] overflow-y-auto">
                    {result.stdout || "(empty)"}
                  </pre>
                </div>
                {result.stderr && (
                  <div className="rounded-xl bg-black/40 border border-white/10 overflow-hidden">
                    <div className="px-4 py-2 border-b border-white/5 text-xs font-mono text-muted-foreground">
                      stderr
                    </div>
                    <pre className="p-4 text-xs font-mono text-amber-200/90 whitespace-pre-wrap overflow-x-auto max-h-[30vh] overflow-y-auto">
                      {result.stderr}
                    </pre>
                  </div>
                )}
              </div>
            </>
          )}

          {!result && !error && !running && (
            <p className="text-sm text-muted-foreground">
              Click &quot;Run tests&quot; to run pytest in the repo.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
