import { Activity, Cpu, Database, HardDrive, Loader2, Terminal, Timer } from "lucide-react";
import { useEffect, useState } from "react";
import { getApiBaseUrl } from "../../config/apiBase";

interface SystemStatus {
  status: string;
  server: string;
  version: string;
  uptime_seconds: number;
  cpu_percent: number;
  memory: { total: number; available: number; percent: number };
  disk: { total: number; free: number; percent: number };
}

function fmtBytes(b: number): string {
  const gb = b / 1024 ** 3;
  return `${gb.toFixed(1)} GB`;
}

function fmtUptime(s: number): string {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  return `${h}h ${m}m`;
}

export default function ControlRoom() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchStatus = async () => {
    setIsLoading(true);
    setError("");
    try {
      const r = await fetch(`${getApiBaseUrl()}/system/status`);
      if (!r.ok) { setError(`HTTP ${r.status}`); return; }
      const d = await r.json();
      setStatus(d);
    } catch (e) {
      setError(String(e));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { fetchStatus(); }, []);

  return (
    <div className="flex flex-col h-full bg-background overflow-hidden relative animate-in fade-in duration-700">
      <div className="px-10 py-8 border-b border-white/5 bg-black/40 backdrop-blur-xl flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-red-500/20 rounded-2xl">
            <Terminal className="h-6 w-6 text-red-500" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">System Status</h1>
            <p className="text-[10px] text-muted-foreground uppercase tracking-[0.2em] font-bold">
              Server health and resource monitoring
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-8">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="h-8 w-8 animate-spin text-amber-500" />
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center opacity-40 max-w-md">
              <Activity className="h-12 w-12 mx-auto mb-4" />
              <h3 className="text-lg font-bold mb-2">Could not reach backend</h3>
              <p className="text-sm text-muted-foreground">{error}</p>
            </div>
          </div>
        ) : status ? (
          <div className="max-w-4xl mx-auto space-y-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
                <div className="flex items-center space-x-2 text-emerald-400 mb-3">
                  <Activity className="h-4 w-4" />
                  <span className="text-[10px] uppercase font-bold tracking-widest">Server</span>
                </div>
                <p className="text-lg font-bold">{status.server}</p>
                <p className="text-xs text-muted-foreground">v{status.version}</p>
              </div>
              <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
                <div className="flex items-center space-x-2 text-amber-400 mb-3">
                  <Timer className="h-4 w-4" />
                  <span className="text-[10px] uppercase font-bold tracking-widest">Uptime</span>
                </div>
                <p className="text-lg font-bold">{fmtUptime(status.uptime_seconds)}</p>
              </div>
              <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
                <div className="flex items-center space-x-2 text-blue-400 mb-3">
                  <Cpu className="h-4 w-4" />
                  <span className="text-[10px] uppercase font-bold tracking-widest">CPU</span>
                </div>
                <p className="text-lg font-bold">{status.cpu_percent}%</p>
              </div>
              <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
                <div className="flex items-center space-x-2 text-purple-400 mb-3">
                  <Database className="h-4 w-4" />
                  <span className="text-[10px] uppercase font-bold tracking-widest">Memory</span>
                </div>
                <p className="text-lg font-bold">{status.memory.percent}%</p>
                <p className="text-xs text-muted-foreground">
                  {fmtBytes(status.memory.available)} free
                </p>
              </div>
            </div>
            <div className="bg-white/5 rounded-2xl border border-white/10 p-6">
              <div className="flex items-center space-x-2 text-indigo-400 mb-4">
                <HardDrive className="h-4 w-4" />
                <span className="text-[10px] uppercase font-bold tracking-widest">Disk</span>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-indigo-500 rounded-full transition-all"
                    style={{ width: `${status.disk.percent}%` }}
                  />
                </div>
                <span className="text-sm font-mono">{status.disk.percent}%</span>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                {fmtBytes(status.disk.free)} free
              </p>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
