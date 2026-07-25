import { ArrowLeft, Clock, Download, Filter, RefreshCw, Search, Trash2 } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";

import { getApiBaseUrl } from "../../config/apiBase";

const logLevelColors: Record<string, string> = {
  ERROR: "text-red-400",
  WARNING: "text-yellow-400",
  INFO: "text-blue-400",
  SUCCESS: "text-green-400",
  DEBUG: "text-gray-400",
};

function logsApiUrl(): string {
  const base = getApiBaseUrl();
  return `${base}/system/logs?limit=500`;
}

export default function LoggerPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [showFilters, setShowFilters] = useState(false);
  const [levelFilters, setLevelFilters] = useState<Record<string, boolean>>({
    ERROR: true,
    WARNING: true,
    INFO: true,
    SUCCESS: true,
    DEBUG: true,
  });
  const [searchQuery, setSearchQuery] = useState("");
  const [timeFilter, setTimeFilter] = useState<"all" | "1h" | "6h" | "24h" | "custom">("all");
  const logContainerRef = useRef<HTMLDivElement>(null);

  const fetchLogs = async () => {
    try {
      setLoadError(null);
      const response = await fetch(logsApiUrl());
      if (!response.ok) {
        setLoadError(
          `Could not load logs (HTTP ${response.status}). Start the FastAPI backend on port 10705 (run webapp/start.ps1 from the repo) or set VITE_API_URL. Request URL: ${logsApiUrl()}`,
        );
        return;
      }
      const result = await response.json();
      if (result.success && result.data) {
        setLogs(result.data);
      } else {
        setLogs([]);
      }
    } catch {
      setLoadError(
        `Could not reach the Advanced Memory HTTP API. From the webapp folder run .\\start.ps1 (starts uvicorn on 127.0.0.1:10705 and Vite on 10704). Tried: ${logsApiUrl()}`,
      );
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 4000);
    return () => clearInterval(interval);
  }, []);

  const filteredLogs = useMemo(() => {
    let filtered = logs.filter((log) => levelFilters[log.level]);

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (log) =>
          log.message.toLowerCase().includes(query) || log.level.toLowerCase().includes(query),
      );
    }

    if (timeFilter !== "all") {
      const now = new Date();
      const filterTime = new Date();
      switch (timeFilter) {
        case "1h":
          filterTime.setHours(now.getHours() - 1);
          break;
        case "6h":
          filterTime.setHours(now.getHours() - 6);
          break;
        case "24h":
        case "custom":
          filterTime.setDate(now.getDate() - 1);
          break;
      }
      filtered = filtered.filter((log) => {
        const logTime = new Date(String(log.timestamp).replace(" ", "T"));
        return logTime >= filterTime;
      });
    }

    return filtered;
  }, [logs, levelFilters, searchQuery, timeFilter]);

  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [filteredLogs, autoScroll]);

  const handleLevelFilterChange = (level: string, checked: boolean) => {
    setLevelFilters((prev) => ({ ...prev, [level]: checked }));
  };

  const handleClearFilters = () => {
    setLevelFilters({
      ERROR: true,
      WARNING: true,
      INFO: true,
      SUCCESS: true,
      DEBUG: true,
    });
    setSearchQuery("");
    setTimeFilter("all");
  };

  const handleDownloadLogs = () => {
    const logText = filteredLogs
      .map((log) => `[${log.timestamp}] ${log.level} (${log.source || "system"}): ${log.message}`)
      .join("\n");
    const blob = new Blob([logText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `advanced-memory-logs-${new Date().toISOString().split("T")[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col h-full min-h-0 bg-[#020205] text-slate-100">
      <div className="shrink-0 border-b border-white/10 px-6 py-4 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <Link
              to="/"
              className="inline-flex items-center gap-1.5 text-sm text-indigo-300 hover:text-indigo-200 shrink-0"
            >
              <ArrowLeft className="h-4 w-4" />
              Dashboard
            </Link>
            <h1 className="text-xl font-semibold tracking-tight truncate">System log</h1>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => fetchLogs()}
              className="inline-flex items-center gap-2 rounded-lg border border-white/15 bg-white/5 px-3 py-2 text-sm hover:bg-white/10"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>
            <button
              type="button"
              onClick={() => setShowFilters((v) => !v)}
              className={`inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm ${
                showFilters
                  ? "border-indigo-400 bg-indigo-500/20"
                  : "border-white/15 bg-white/5 hover:bg-white/10"
              }`}
            >
              <Filter className="h-4 w-4" />
              Filters
            </button>
            <button
              type="button"
              onClick={handleDownloadLogs}
              disabled={filteredLogs.length === 0}
              className="inline-flex items-center gap-2 rounded-lg border border-white/15 bg-white/5 px-3 py-2 text-sm hover:bg-white/10 disabled:opacity-40"
            >
              <Download className="h-4 w-4" />
              Download
            </button>
            <button
              type="button"
              onClick={() => setLogs([])}
              disabled={logs.length === 0}
              className="inline-flex items-center gap-2 rounded-lg border border-white/15 bg-white/5 px-3 py-2 text-sm hover:bg-white/10 disabled:opacity-40"
            >
              <Trash2 className="h-4 w-4" />
              Clear view
            </button>
          </div>
        </div>
        {loadError && (
          <p className="text-sm text-amber-200/90 rounded-lg bg-amber-500/10 border border-amber-500/25 px-3 py-2">
            {loadError}
          </p>
        )}
        <div className="flex flex-wrap items-center gap-4 text-sm text-slate-400">
          <label className="inline-flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded border-white/20 bg-black/40"
            />
            Auto-scroll
          </label>
          <span>
            Showing {filteredLogs.length} of {logs.length} entries
          </span>
        </div>
      </div>

      {showFilters && (
        <div className="shrink-0 border-b border-white/10 px-6 py-4 bg-white/[0.03]">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl">
            <div>
              <h2 className="text-sm font-medium text-slate-200 mb-2 flex items-center gap-2">
                <Filter className="h-4 w-4" />
                Log levels
              </h2>
              <div className="space-y-2">
                {Object.entries(levelFilters).map(([level, checked]) => (
                  <label key={level} className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={(e) => handleLevelFilterChange(level, e.target.checked)}
                      className="rounded border-white/20 bg-black/40"
                    />
                    <span className={logLevelColors[level] || "text-slate-300"}>{level}</span>
                  </label>
                ))}
              </div>
            </div>
            <div>
              <h2 className="text-sm font-medium text-slate-200 mb-2 flex items-center gap-2">
                <Search className="h-4 w-4" />
                Search
              </h2>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 h-4 w-4" />
                <input
                  type="search"
                  placeholder="Filter by message or level…"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full rounded-lg border border-white/15 bg-black/40 pl-9 pr-3 py-2 text-sm text-slate-100 placeholder:text-slate-500"
                />
              </div>
            </div>
            <div>
              <h2 className="text-sm font-medium text-slate-200 mb-2 flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Time range
              </h2>
              <select
                value={timeFilter}
                onChange={(e) => setTimeFilter(e.target.value as typeof timeFilter)}
                className="w-full rounded-lg border border-white/15 bg-black/40 px-3 py-2 text-sm text-slate-100"
              >
                <option value="all">All time</option>
                <option value="1h">Last hour</option>
                <option value="6h">Last 6 hours</option>
                <option value="24h">Last 24 hours</option>
                <option value="custom">Last 24 hours (custom)</option>
              </select>
              <button
                type="button"
                onClick={handleClearFilters}
                className="mt-2 w-full rounded-lg border border-white/15 bg-white/5 py-1.5 text-xs hover:bg-white/10"
              >
                Reset filters
              </button>
            </div>
          </div>
        </div>
      )}

      <div
        ref={logContainerRef}
        className="flex-1 min-h-0 overflow-auto px-6 py-4 font-mono text-sm leading-relaxed bg-black/50"
      >
        {filteredLogs.length === 0 ? (
          <p className="text-center text-slate-500 py-12 max-w-xl mx-auto">
            {logs.length === 0
              ? "No log lines captured yet. Start the backend (uvicorn advanced_memory.server:app on port 10705, or use webapp/start.ps1), then refresh. Logs are served from GET /api/v1/system/logs."
              : "No lines match the current filters."}
          </p>
        ) : (
          <div className="max-w-6xl space-y-1">
            {filteredLogs.map((log, index) => (
              <div key={`${log.timestamp}-${index}`} className="break-words">
                <span className="text-slate-500">[{log.timestamp}]</span>{" "}
                <span className={logLevelColors[log.level] || "text-slate-200"}>{log.level}:</span>{" "}
                <span className="text-slate-200">{log.message}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
