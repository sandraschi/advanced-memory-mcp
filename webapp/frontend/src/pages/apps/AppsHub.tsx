import { useState, useEffect } from 'react'
import { LayoutGrid, RefreshCw, ExternalLink, Activity, Shield, Zap, Globe, Cpu, Server, Search, AlertCircle } from 'lucide-react'
import { apiService } from '../../services/api'

interface AppCard {
    port: number
    name: string
    status: 'online' | 'offline' | 'warning'
    type: 'MCP Server' | 'Web App' | 'API'
    description: string
    latency?: string
}

export default function AppsHub() {
    const [apps, setApps] = useState<AppCard[]>([])
    const [isScanning, setIsScanning] = useState(false)
    const [searchTerm, setSearchTerm] = useState('')

    const scanFleet = async () => {
        setIsScanning(true)
        try {
            const response = await apiService.getApps();
            if (response.success && response.data) {
                setApps(response.data as AppCard[]);
            }
        } catch (error) {
            console.error('Fleet discovery failed:', error);
        } finally {
            setIsScanning(false);
        }
    }

    useEffect(() => {
        scanFleet()
    }, [])

    const filteredApps = apps.filter(app =>
        app.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        app.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        app.port.toString().includes(searchTerm)
    )

    return (
        <div className="flex flex-col h-full bg-background overflow-hidden animate-in fade-in duration-700">
            {/* Hub Header */}
            <div className="px-12 py-12 border-b border-white/5 bg-black/20 backdrop-blur-xl">
                <div className="max-w-6xl mx-auto space-y-8">
                    <div className="flex items-center justify-between">
                        <div className="space-y-1">
                            <h1 className="text-4xl font-bold tracking-tight">Fleet Discovery</h1>
                            <p className="text-sm text-muted-foreground">Monitoring active MCP instances across the reserved port grid (10700–10800+).</p>
                        </div>
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2 bg-green-500/10 border border-green-500/20 px-4 py-2 rounded-full">
                                <Activity className="h-4 w-4 text-green-500" />
                                <span className="text-[10px] uppercase font-bold tracking-widest text-green-500">Fleet Healthy</span>
                            </div>
                            <button
                                onClick={scanFleet}
                                disabled={isScanning}
                                className="p-3 bg-white/5 border border-white/10 rounded-2xl hover:bg-white/10 transition-all disabled:opacity-50"
                            >
                                <RefreshCw className={`h-5 w-5 ${isScanning ? 'animate-spin text-amber-500' : ''}`} />
                            </button>
                        </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-6">
                        <div className="flex-1 relative group">
                            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-amber-500 transition-colors" />
                            <input
                                type="text"
                                placeholder="Search active fleet..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-2xl py-3 pl-12 pr-6 focus:outline-none focus:ring-1 focus:ring-amber-500/50 transition-all text-sm"
                            />
                        </div>
                        <div className="flex items-center space-x-2">
                            {['All', 'MCP Servers', 'Web Apps', 'APIs'].map(f => (
                                <button key={f} className="px-5 py-2.5 bg-white/5 border border-white/5 rounded-xl text-[10px] uppercase font-bold tracking-widest hover:border-white/20 transition-all">
                                    {f}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Grid Area */}
            <div className="flex-1 overflow-y-auto px-12 py-12 scrollbar-thin">
                <div className="max-w-6xl mx-auto">
                    {isScanning && apps.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-32 space-y-6">
                            <div className="relative">
                                <Server className="h-16 w-16 text-amber-500 animate-pulse" />
                                <div className="absolute inset-0 bg-amber-500/20 blur-3xl animate-pulse rounded-full" />
                            </div>
                            <div className="text-center space-y-2">
                                <p className="text-sm font-bold uppercase tracking-[0.4em]">Scanning Local Substrate</p>
                                <p className="text-[10px] text-muted-foreground uppercase font-mono italic">Polling ports 10700 through 10800...</p>
                            </div>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
                            {filteredApps.map(app => (
                                <div key={app.port} className="group relative bg-white/2 border border-white/5 hover:border-white/10 p-8 rounded-3xl transition-all duration-300 hover:bg-white/[0.04] hover:-translate-y-1">
                                    <div className="flex items-start justify-between mb-6">
                                        <div className="p-3 bg-white/5 rounded-2xl group-hover:bg-amber-500/10 transition-colors">
                                            {app.type === 'MCP Server' ? <Cpu className="h-6 w-6 text-blue-500" /> :
                                                app.type === 'Web App' ? <Globe className="h-6 w-6 text-purple-500" /> :
                                                    <Zap className="h-6 w-6 text-amber-500" />}
                                        </div>
                                        <div className="flex flex-col items-end space-y-2">
                                            <div className={`px-2 py-0.5 rounded-full text-[8px] uppercase font-bold tracking-widest border ${app.status === 'online' ? 'bg-green-500/10 text-green-500 border-green-500/20' :
                                                app.status === 'warning' ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' :
                                                    'bg-red-500/10 text-red-500 border-red-500/20'
                                                }`}>
                                                {app.status}
                                            </div>
                                            <span className="text-[10px] font-mono text-muted-foreground opacity-50">PORT: {app.port}</span>
                                        </div>
                                    </div>

                                    <div className="space-y-2 mb-6">
                                        <h3 className="text-lg font-bold group-hover:text-white transition-colors">{app.name}</h3>
                                        <p className="text-xs text-muted-foreground leading-relaxed line-clamp-2">{app.description}</p>
                                    </div>

                                    <div className="pt-6 border-t border-white/5 flex items-center justify-between">
                                        <div className="flex items-center space-x-2">
                                            <Shield className="h-3.5 w-3.5 text-muted-foreground opacity-50" />
                                            <span className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground opacity-50">Encrypted</span>
                                        </div>
                                        <button className="flex items-center space-x-2 text-[10px] uppercase font-bold tracking-widest text-amber-500 hover:text-amber-400 group/btn transition-colors">
                                            <span>Connect</span>
                                            <ExternalLink className="h-3 w-3 group-hover/btn:translate-x-1 group-hover/btn:-translate-y-1 transition-transform" />
                                        </button>
                                    </div>
                                </div>
                            ))}

                            {/* Manual Add Card */}
                            <div className="border-2 border-dashed border-white/5 rounded-3xl flex flex-col items-center justify-center p-8 hover:border-white/10 hover:bg-white/2 transition-all cursor-pointer group">
                                <div className="p-4 bg-white/5 rounded-full mb-4 group-hover:bg-white/10 transition-all">
                                    <LayoutGrid className="h-6 w-6 text-muted-foreground" />
                                </div>
                                <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Register App</span>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Footer Stats */}
            <div className="border-t border-white/5 bg-black/40 px-12 py-6">
                <div className="max-w-6xl mx-auto flex items-center justify-between">
                    <div className="flex items-center space-x-8 text-[10px] uppercase font-bold tracking-widest text-muted-foreground">
                        <div className="flex items-center space-x-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
                            <span>{apps.filter(a => a.status === 'online').length} Active</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                            <span>{apps.filter(a => a.status === 'warning').length} Warning</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <Server className="h-3 w-3" />
                            <span>Grid Range: 10700 - 10800</span>
                        </div>
                    </div>
                    <div className="flex items-center space-x-2 text-blue-500/60">
                        <AlertCircle className="h-3.5 w-3.5" />
                        <span className="text-[10px] font-bold uppercase tracking-widest">Auto-discovery Active</span>
                    </div>
                </div>
            </div>
        </div>
    )
}
