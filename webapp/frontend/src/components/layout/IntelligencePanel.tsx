import { useState, useEffect, useCallback } from 'react'
import { Cpu, Activity, Zap, Database, AlertCircle, Thermometer, Box } from 'lucide-react'
import apiService from '../../services/api'

interface SubstrateStats {
    gpu: {
        model: string
        utilization: string
        vram_used: string
        vram_total: string
        temperature: string
    }
    cpu: {
        utilization: string
        cores: number
    }
    memory: {
        used: string
        total: string
    }
}

export default function IntelligencePanel() {
    const [stats, setStats] = useState<SubstrateStats | null>(null)

    const fetchStats = useCallback(async () => {
        const response = await apiService.detectHardware()
        if (response.success && response.data) {
            setStats(response.data as SubstrateStats)
        }
    }, [])

    useEffect(() => {
        fetchStats()
        const interval = setInterval(fetchStats, 5000)
        return () => clearInterval(interval)
    }, [fetchStats])

    if (!stats) return null

    return (
        <div className="p-4 bg-black/40 border-t border-white/5 space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                    <div className="relative">
                        <Activity className="h-3.5 w-3.5 text-amber-500" />
                        <div className="absolute inset-0 bg-amber-500/20 blur-sm animate-pulse rounded-full" />
                    </div>
                    <span className="text-[10px] uppercase font-bold tracking-[0.22em] text-muted-foreground">Substrate</span>
                </div>
                <div className="flex items-center space-x-1.5 px-2 py-0.5 bg-green-500/10 border border-green-500/20 rounded-full">
                    <div className="w-1 h-1 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-[8px] uppercase font-bold tracking-widest text-green-500">Live</span>
                </div>
            </div>

            <div className="space-y-4">
                {/* GPU Section */}
                <div className="space-y-2">
                    <div className="flex items-center justify-between text-[9px] uppercase font-bold tracking-widest opacity-60">
                        <div className="flex items-center space-x-1.5">
                            <Cpu className="h-3 w-3 text-blue-500" />
                            <span>GPU: RTX 4090</span>
                        </div>
                        <span className="text-blue-500">{stats.gpu.utilization}</span>
                    </div>
                    <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-blue-500 transition-all duration-1000"
                            style={{ width: stats.gpu.utilization }}
                        />
                    </div>
                    <div className="flex items-center justify-between text-[8px] font-mono opacity-40">
                        <div className="flex items-center space-x-1">
                            <Thermometer className="h-2.5 w-2.5" />
                            <span>{stats.gpu.temperature}</span>
                        </div>
                        <span>VRAM: {stats.gpu.vram_used} / {stats.gpu.vram_total}</span>
                    </div>
                </div>

                {/* CPU Section */}
                <div className="space-y-2">
                    <div className="flex items-center justify-between text-[9px] uppercase font-bold tracking-widest opacity-60">
                        <div className="flex items-center space-x-1.5">
                            <Box className="h-3 w-3 text-purple-500" />
                            <span>CPU: {stats.cpu.cores} Cores</span>
                        </div>
                        <span className="text-purple-500">{stats.cpu.utilization}</span>
                    </div>
                    <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-purple-500 transition-all duration-1000"
                            style={{ width: stats.cpu.utilization }}
                        />
                    </div>
                </div>

                {/* Memory Section */}
                <div className="space-y-2">
                    <div className="flex items-center justify-between text-[9px] uppercase font-bold tracking-widest opacity-60">
                        <div className="flex items-center space-x-1.5" title="System RAM">
                            <Database className="h-3 w-3 text-amber-500" />
                            <span>System RAM</span>
                        </div>
                        <span className="text-amber-500">{(parseInt(stats.memory.used) / parseInt(stats.memory.total) * 100).toFixed(0)}%</span>
                    </div>
                    <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-amber-500 transition-all duration-1000"
                            style={{ width: `${(parseInt(stats.memory.used) / parseInt(stats.memory.total) * 100)}%` }}
                        />
                    </div>
                </div>
            </div>

            <div className="pt-2 flex items-center justify-between opacity-50 hover:opacity-100 transition-opacity">
                <div className="flex items-center space-x-1.5">
                    <AlertCircle className="h-3 w-3 text-blue-400" />
                    <span className="text-[8px] uppercase font-bold tracking-[0.1em]">Ollama optimization active</span>
                </div>
                <Zap className="h-3 w-3 text-amber-500" />
            </div>
        </div>
    )
}
