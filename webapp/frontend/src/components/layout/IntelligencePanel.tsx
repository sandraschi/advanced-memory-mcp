import { Activity, Zap } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import apiService from "../../services/api";

interface HardwareStats {
  gpu: {
    model: string;
    utilization: string;
    vram_used: string;
    vram_total: string;
    temperature: string;
  };
  cpu: {
    utilization: string;
    cores: number;
  };
  memory: {
    used: string;
    total: string;
  };
}

export default function IntelligencePanel() {
  const [stats, setStats] = useState<HardwareStats | null>(null);

  const fetchStats = useCallback(async () => {
    const response = await apiService.detectHardware();
    if (response.success && response.data) {
      setStats(response.data as HardwareStats);
    }
  }, []);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, [fetchStats]);

  if (!stats) {
    return (
      <div className="hardware-panel h-64 flex items-center justify-center">
        <div className="flex flex-col items-center gap-2 opacity-40">
          <Activity className="animate-spin text-indigo-500" size={20} />
          <span className="text-[10px] uppercase font-bold tracking-widest">
            Initialising Hardware...
          </span>
        </div>
      </div>
    );
  }

  // Parse numeric values for progress bars
  const gpuUtil = Number.parseInt(stats.gpu.utilization) || 0;
  const cpuUtil = Number.parseInt(stats.cpu.utilization) || 0;

  // Memory percent calculation
  const memUsed = Number.parseFloat(stats.memory.used) || 0;
  const memTotal = Number.parseFloat(stats.memory.total) || 1;
  const memPercent = Math.round((memUsed / memTotal) * 100);

  return (
    <div className="hardware-panel">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded-md bg-indigo-500/10">
            <Activity size={12} className="text-indigo-400" />
          </div>
          <h3 className="hardware-label">Hardware Status</h3>
        </div>
        <div className="hardware-live-badge">
          <div className="w-1 h-1 bg-green-500 rounded-full animate-pulse" />
          <span className="hardware-live-text">Live Telemetry</span>
        </div>
      </div>

      <div className="space-y-6">
        {/* GPU Capability */}
        <div className="space-y-2">
          <div className="hardware-stat-title">
            <span>Graphics Processing (GPU)</span>
            <span className="text-blue-400 font-mono">{stats.gpu.utilization}</span>
          </div>
          <div className="hardware-progress-container text-blue-500">
            <div
              className="hardware-progress-bar hardware-progress-bar-gpu"
              style={{ "--progress": `${gpuUtil}%` } as React.CSSProperties}
            />
          </div>
          <div className="hardware-stat-footer">
            <span className="truncate max-w-[150px]">{stats.gpu.model}</span>
            <span>
              {stats.gpu.vram_used} / {stats.gpu.vram_total} VRAM
            </span>
          </div>
        </div>

        {/* CPU Load */}
        <div className="space-y-2">
          <div className="hardware-stat-title">
            <span>Central Processing (CPU)</span>
            <span className="text-purple-400 font-mono">{stats.cpu.utilization}</span>
          </div>
          <div className="hardware-progress-container text-purple-500">
            <div
              className="hardware-progress-bar hardware-progress-bar-cpu"
              style={{ "--progress": `${cpuUtil}%` } as React.CSSProperties}
            />
          </div>
          <div className="hardware-stat-footer">
            <span>{stats.cpu.cores} Logical Cores</span>
            <span>Health: Optimal</span>
          </div>
        </div>

        {/* Memory Usage */}
        <div className="space-y-2">
          <div className="hardware-stat-title">
            <span>System Memory (RAM)</span>
            <span className="text-amber-400 font-mono">{memPercent}%</span>
          </div>
          <div className="hardware-progress-container text-amber-500">
            <div
              className="hardware-progress-bar hardware-progress-bar-mem"
              style={{ "--progress": `${memPercent}%` } as React.CSSProperties}
            />
          </div>
          <div className="hardware-stat-footer">
            <span>Physical Memory</span>
            <span>
              {stats.memory.used} / {stats.memory.total}
            </span>
          </div>
        </div>
      </div>

      <div className="pt-6 mt-2 border-t border-white/[0.03]">
        <div className="p-3 rounded-xl bg-indigo-500/5 border border-indigo-500/10 transition-all hover:bg-indigo-500/10 group cursor-default">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 group-hover:scale-110 transition-transform">
              <Zap size={14} />
            </div>
            <div>
              <p className="text-[10px] font-bold text-indigo-300 uppercase tracking-wider mb-0.5">
                System Optimization
              </p>
              <p className="text-[10px] text-indigo-200/60 leading-relaxed">
                Hardware detected. Local inference parameters adjusted for system capacity.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
