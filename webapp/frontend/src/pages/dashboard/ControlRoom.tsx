import { useState, useEffect } from 'react'
import { Terminal, Shield, Zap, Search, Clock, Cpu, Database, Activity, History, Rewind, Pause, Square, ChevronRight, Loader2, Sparkles } from 'lucide-react'

interface AgentSession {
    id: string
    agent: string
    status: 'active' | 'completed' | 'failed'
    startTime: string
    duration: string
    toolsCalled: number
    tokens: string
    summary: string
}

export default function ControlRoom() {
    const [sessions, setSessions] = useState<AgentSession[]>([])
    const [activeSession, setActiveSession] = useState<AgentSession | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [terminalLines] = useState<string[]>([
        '[SYSTEM] Initializing Entire.io observability layer...',
        '[SYSTEM] Mapping local substrate (RTX 4090 detected)',
        '[SYSTEM] Subscribing to stdio event bus on port 10705',
        '[BRIDGE] Agent session a1f2-7b8c-9d0e started',
        '[TOOL] adn_research(operation="search", query="materialist reductionism")',
        '[LLM] Requesting Gemini 3 Pro reasoning cycle...',
        '[LLM] Content generated (1,247 tokens)',
        '[TOOL] adn_content(operation="write", path="notes/philosophy_v1.md")',
        '[SYSTEM] Syncing checkpoint to local git repo...'
    ])

    useEffect(() => {
        setIsLoading(true)
        // Mock session data
        setTimeout(() => {
            const data: AgentSession[] = [
                { id: '1', agent: 'Advanced Memory Agent', status: 'active', startTime: '19:12:18', duration: '12m 45s', toolsCalled: 14, tokens: '14,287', summary: 'Researching materialist epistemology and implementing Phase 4 components.' },
                { id: '2', agent: 'Robotics Orchestrator', status: 'completed', startTime: '18:05:22', duration: '45m 12s', toolsCalled: 32, tokens: '42,102', summary: 'Optimizing inverse kinematics for Unitree G1 platform.' },
                { id: '3', agent: 'ClawHub Auditor', status: 'completed', startTime: '17:30:10', duration: '8m 15s', toolsCalled: 6, tokens: '3,450', summary: 'Scrubbing external skill: "quantum-physics-expert" for Thermodynamic villains.' }
            ]
            setSessions(data)
            if (data.length > 0) {
                const firstSession = data[0]
                setActiveSession(firstSession ?? null)
            }
            setIsLoading(false)
        }, 1500)
    }, [])

    return (
        <div className="flex flex-col h-full bg-background overflow-hidden relative animate-in fade-in duration-700">
            {/* Control Room Header */}
            <div className="px-10 py-8 border-b border-white/5 bg-black/40 backdrop-blur-xl flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    <div className="p-3 bg-red-500/20 rounded-2xl animate-pulse">
                        <Terminal className="h-6 w-6 text-red-500" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight">Agent Control Room</h1>
                        <p className="text-[10px] text-muted-foreground uppercase tracking-[0.2em] font-bold">Observability & Audit Layer v1.4.0</p>
                    </div>
                </div>

                <div className="flex items-center space-x-6">
                    <div className="flex flex-col items-end">
                        <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest">Active Sessions</span>
                        <span className="text-xl font-mono font-bold text-amber-500">01</span>
                    </div>
                    <div className="w-px h-8 bg-white/10" />
                    <div className="flex flex-col items-end">
                        <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest">Substrate Load</span>
                        <span className="text-xl font-mono font-bold text-blue-500">22%</span>
                    </div>
                    <div className="w-px h-8 bg-white/10" />
                    <button className="bg-white/5 hover:bg-white/10 px-6 py-2.5 rounded-xl border border-white/10 text-xs font-bold transition-all flex items-center space-x-2">
                        <History className="h-4 w-4" />
                        <span>Audit Logs</span>
                    </button>
                </div>
            </div>

            <div className="flex-1 flex overflow-hidden">
                {/* Left Panel: Session List */}
                <div className="w-96 border-r border-white/5 flex flex-col bg-black/20 overflow-hidden">
                    <div className="p-6 border-b border-white/5">
                        <div className="relative group">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground group-focus-within:text-amber-500 transition-colors" />
                            <input
                                type="text"
                                placeholder="Filter agent sessions..."
                                className="w-full bg-white/5 border border-white/10 rounded-xl py-2 pl-9 pr-4 text-xs focus:outline-none focus:ring-1 focus:ring-amber-500/50 transition-all"
                            />
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin">
                        {isLoading ? (
                            <div className="flex items-center justify-center h-full opacity-50">
                                <Loader2 className="h-8 w-8 animate-spin text-amber-500" />
                            </div>
                        ) : (
                            sessions.map(s => (
                                <div
                                    key={s.id}
                                    onClick={() => setActiveSession(s)}
                                    className={`p-5 rounded-2xl border transition-all cursor-pointer group ${activeSession?.id === s.id
                                        ? 'bg-amber-500/10 border-amber-500/30'
                                        : 'bg-white/2 border-white/5 hover:border-white/10 hover:bg-white/5'
                                        }`}
                                >
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="flex items-center space-x-2">
                                            <div className={`w-2 h-2 rounded-full ${s.status === 'active' ? 'bg-green-500 animate-pulse' : 'bg-white/20'}`} />
                                            <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">{s.agent}</span>
                                        </div>
                                        <span className="text-[9px] font-mono text-muted-foreground opacity-50">{s.startTime}</span>
                                    </div>
                                    <h4 className="text-xs font-bold mb-2 group-hover:text-amber-500 transition-colors line-clamp-1">{s.summary}</h4>
                                    <div className="flex items-center justify-between opacity-60">
                                        <div className="flex items-center space-x-3 text-[9px] font-bold uppercase tracking-tighter">
                                            <span className="flex items-center space-x-1">
                                                <Zap className="h-2.5 w-2.5" />
                                                <span>{s.toolsCalled} Tools</span>
                                            </span>
                                            <span className="flex items-center space-x-1 text-blue-500">
                                                <Database className="h-2.5 w-2.5" />
                                                <span>{s.tokens} Tokens</span>
                                            </span>
                                        </div>
                                        <ChevronRight className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-all" />
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Right Panel: Live View & Terminal */}
                <div className="flex-1 flex flex-col overflow-hidden bg-black/40">
                    {activeSession ? (
                        <>
                            {/* Session Detail Stats */}
                            <div className="p-8 grid grid-cols-4 gap-6 bg-white/2 border-b border-white/5">
                                <div className="space-y-1">
                                    <span className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground flex items-center space-x-1">
                                        <Activity className="h-3 w-3" />
                                        <span>Current Status</span>
                                    </span>
                                    <div className="flex items-center space-x-2">
                                        <div className="w-2 h-2 rounded-full bg-green-500" />
                                        <span className="text-sm font-bold uppercase">{activeSession.status}</span>
                                    </div>
                                </div>
                                <div className="space-y-1">
                                    <span className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground flex items-center space-x-1">
                                        <Clock className="h-3 w-3" />
                                        <span>Elapsed Time</span>
                                    </span>
                                    <span className="text-sm font-mono font-bold tracking-tight">{activeSession.duration}</span>
                                </div>
                                <div className="space-y-1">
                                    <span className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground flex items-center space-x-1">
                                        <Cpu className="h-3 w-3" />
                                        <span>Substrate</span>
                                    </span>
                                    <span className="text-sm font-bold">RTX 4090 (Local)</span>
                                </div>
                                <div className="space-y-1">
                                    <span className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground flex items-center space-x-1">
                                        <Shield className="h-3 w-3" />
                                        <span>Integrity</span>
                                    </span>
                                    <span className="text-sm font-bold text-green-500">Verified</span>
                                </div>
                            </div>

                            {/* Live Terminal Feed */}
                            <div className="flex-1 p-8 flex flex-col overflow-hidden">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center space-x-3">
                                        <Terminal className="h-4 w-4 text-amber-500" />
                                        <h3 className="text-[10px] uppercase font-bold tracking-[0.2em]">Material Execution Stream</h3>
                                    </div>
                                    <div className="flex items-center space-x-2 bg-black/60 border border-white/10 rounded-lg p-1">
                                        <button className="p-1.5 hover:bg-white/5 rounded transition-colors" title="Rewind Step"><Rewind className="h-3.3 w-3.5" /></button>
                                        <button className="p-1.5 hover:bg-amber-500/20 text-amber-500 rounded transition-colors" title="Pause Stream"><Pause className="h-3.3 w-3.5" /></button>
                                        <button className="p-1.5 hover:bg-white/5 rounded transition-colors" title="Terminate Session"><Square className="h-3.3 w-3.5" /></button>
                                    </div>
                                </div>

                                <div className="flex-1 bg-black/80 rounded-2xl border border-white/10 p-6 font-mono text-[11px] overflow-y-auto scrollbar-thin text-muted-foreground space-y-2 relative group uppercase tracking-tight">
                                    <div className="absolute top-4 right-4 animate-pulse">
                                        <div className="w-2 h-2 rounded-full bg-amber-500 opacity-50" />
                                    </div>
                                    {terminalLines.map((line, i) => (
                                        <div key={i} className="flex space-x-3">
                                            <span className="opacity-20 select-none">[{i.toString().padStart(3, '0')}]</span>
                                            <span className={`${line.includes('[TOOL]') ? 'text-blue-500' : line.includes('[LLM]') ? 'text-purple-500' : line.includes('[ERROR]') ? 'text-red-500' : ''}`}>
                                                {line}
                                            </span>
                                        </div>
                                    ))}
                                    <div className="flex space-x-3 animate-pulse">
                                        <span className="opacity-20">[{terminalLines.length.toString().padStart(3, '0')}]</span>
                                        <span className="text-white">_</span>
                                    </div>
                                </div>

                                <div className="mt-6 flex items-center justify-between">
                                    <div className="flex items-center space-x-4 opacity-50">
                                        <div className="flex items-center space-x-2 text-[10px] font-bold uppercase tracking-widest">
                                            <Sparkles className="h-3 w-3 text-amber-500" />
                                            <span>Entire.io Sync Active</span>
                                        </div>
                                        <div className="w-px h-3 bg-white/20" />
                                        <span className="text-[10px] font-mono italic">Observability Socket: 10706</span>
                                    </div>
                                    <button className="text-[10px] font-bold uppercase tracking-widest text-amber-500 hover:text-white transition-colors flex items-center space-x-2">
                                        <span>Download Full Audit</span>
                                        <ChevronRight className="h-3 w-3" />
                                    </button>
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center opacity-20 space-y-4">
                            <Activity className="h-16 w-16" />
                            <p className="text-sm font-bold uppercase tracking-[0.4em]">Standby for agentic signal...</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
