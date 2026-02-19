import { useState, useEffect } from 'react'
import { Activity, Shield, Clock, GitCommit, Search, ChevronRight, Play, Rewind, Info, Zap, Terminal, FileCode, Users, Loader2 } from 'lucide-react'
import apiService from '../../services/api'

interface Checkpoint {
    id: string
    commitHash: string
    agentName: string
    summary: string
    tokens: number
    files: string[]
    timestamp: string
}

export default function Checkpoints() {
    const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([])
    const [loading, setLoading] = useState(true)
    const [selectedId, setSelectedId] = useState<string | null>(null)
    const [searchQuery, setSearchQuery] = useState('')

    useEffect(() => {
        const fetchCheckpoints = async () => {
            setLoading(true)
            try {
                const response = await apiService.callMCPTool('adn_observability', { operation: 'list' })
                if (response.success && response.data?.checkpoints) {
                    setCheckpoints(response.data.checkpoints)
                }
            } catch (error) {
                console.error('Failed to fetch checkpoints:', error)
            } finally {
                setLoading(false)
            }
        }
        fetchCheckpoints()
    }, [])

    const selectedCheckpoint = checkpoints.find(c => c.id === selectedId)

    const filteredCheckpoints = checkpoints.filter(c =>
        c.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.agentName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.commitHash.toLowerCase().includes(searchQuery.toLowerCase())
    )

    return (
        <div className="max-w-[1400px] mx-auto h-[calc(100vh-12rem)] flex flex-col space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Header */}
            <div className="flex items-center justify-between shrink-0">
                <div className="flex items-center space-x-3">
                    <div className="p-2.5 bg-gradient-to-br from-amber-500/20 to-orange-500/20 rounded-xl border border-amber-500/20">
                        <Activity className="h-6 w-6 text-amber-400" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight">Agent Checkpoints</h1>
                        <p className="text-muted-foreground text-xs">Observability and provenance audit for autonomous sessions</p>
                    </div>
                </div>
                <div className="flex items-center space-x-2">
                    <div className="flex items-center space-x-1.5 px-3 py-1.5 bg-amber-500/5 border border-amber-500/20 rounded-full">
                        <Shield className="h-3.5 w-3.5 text-amber-400" />
                        <span className="text-[10px] font-bold text-amber-200/70 tracking-wider">ENTIRE.IO PROTOCOL ACTIVE</span>
                    </div>
                </div>
            </div>

            {/* Layout */}
            <div className="flex-1 flex space-x-6 overflow-hidden min-h-0">
                {/* Left: Session Timeline */}
                <div className="w-96 shrink-0 flex flex-col space-y-4">
                    <div className="card p-4 bg-muted/20 border-white/5 space-y-4">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
                            <input
                                value={searchQuery}
                                onChange={e => setSearchQuery(e.target.value)}
                                placeholder="Search sessions..."
                                className="w-full bg-background border border-border rounded-lg pl-9 pr-3 py-2 text-sm outline-none focus:ring-1 focus:ring-amber-500/30"
                            />
                        </div>

                        <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-widest text-muted-foreground px-1">
                            <span>Timeline</span>
                            <span>{filteredCheckpoints.length} Sessions</span>
                        </div>

                        <div className="space-y-2 overflow-y-auto max-h-[calc(100vh-28rem)] pr-1 scrollbar-thin">
                            {loading ? (
                                <div className="flex flex-col items-center justify-center py-12 space-y-3 opacity-40">
                                    <Loader2 className="h-6 w-6 animate-spin text-amber-500" />
                                    <span className="text-[10px] uppercase tracking-widest font-bold">Syncing Provenance...</span>
                                </div>
                            ) : filteredCheckpoints.length > 0 ? (
                                filteredCheckpoints.map(c => (
                                    <button
                                        key={c.id}
                                        onClick={() => setSelectedId(c.id)}
                                        className={`w-full text-left p-4 rounded-xl border transition-all ${selectedId === c.id
                                            ? 'bg-amber-500/10 border-amber-500/30 ring-1 ring-amber-500/20'
                                            : 'bg-muted/10 border-white/5 hover:border-white/10'
                                            }`}
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <div className="flex items-center space-x-2">
                                                <GitCommit className={`h-3.5 w-3.5 ${selectedId === c.id ? 'text-amber-400' : 'text-muted-foreground'}`} />
                                                <code className="text-[10px] font-mono opacity-50">{c.commitHash}</code>
                                            </div>
                                            <span className="text-[9px] text-muted-foreground font-mono">{c.timestamp}</span>
                                        </div>
                                        <p className="text-xs font-medium leading-tight line-clamp-2 mb-2">{c.summary}</p>
                                        <div className="flex items-center justify-between opacity-60">
                                            <div className="flex items-center space-x-1">
                                                <Users className="h-3 w-3" />
                                                <span className="text-[9px]">{c.agentName}</span>
                                            </div>
                                            <div className="flex items-center space-x-1">
                                                <Zap className="h-3 w-3 text-amber-400" />
                                                <span className="text-[9px]">{c.tokens.toLocaleString()} tok</span>
                                            </div>
                                        </div>
                                    </button>
                                ))
                            ) : (
                                <div className="text-center py-12 opacity-40">
                                    <p className="text-[10px] uppercase tracking-widest font-bold">No checkpoints found</p>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="card p-4 bg-amber-500/5 border-amber-500/10">
                        <div className="flex items-center space-x-2 text-[10px] font-bold uppercase tracking-widest text-amber-400 mb-3">
                            <Info className="h-3.5 w-3.5" />
                            <span>Provenance Engine</span>
                        </div>
                        <p className="text-[10px] text-amber-100/60 leading-relaxed">
                            Every code change is linked to the agent's internal reasoning and session context via `entire-checkpoints`.
                        </p>
                    </div>
                </div>

                {/* Right: Inspection & Tooling */}
                <div className="flex-1 flex flex-col min-w-0">
                    {selectedId ? (
                        <div className="h-full flex flex-col space-y-4">
                            {/* Inspection Pane */}
                            <div className="card flex-1 flex flex-col overflow-hidden p-0 bg-black/40">
                                <div className="p-4 border-b border-white/5 flex items-center justify-between shrink-0 bg-white/5">
                                    <div className="flex items-center space-x-3">
                                        <Terminal className="h-4 w-4 text-amber-400" />
                                        <h3 className="text-xs font-bold uppercase tracking-widest">Session Audit</h3>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <button className="btn btn-sm btn-outline text-[9px] uppercase tracking-wider py-1.5 px-3 flex items-center space-x-1.5 border-amber-500/30 text-amber-400">
                                            <Rewind className="h-3 w-3" />
                                            <span>Rewind Workspace</span>
                                        </button>
                                        <button className="btn btn-sm btn-primary text-[9px] uppercase tracking-wider py-1.5 px-3 flex items-center space-x-1.5">
                                            <Play className="h-3 w-3" />
                                            <span>Replay Thoughts</span>
                                        </button>
                                    </div>
                                </div>

                                <div className="flex-1 overflow-y-auto p-6 space-y-8 scrollbar-thin">
                                    {/* Summary & Reasoning */}
                                    <div className="space-y-3">
                                        <div className="flex items-center space-x-2">
                                            <div className="w-1 h-3 rounded-full bg-amber-500" />
                                            <h4 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Agent Reasoning</h4>
                                        </div>
                                        <div className="bg-white/5 border border-white/5 p-5 rounded-2xl">
                                            <p className="text-sm leading-relaxed text-balance italic text-muted-foreground/80">
                                                "{selectedCheckpoint?.summary}"
                                            </p>
                                        </div>
                                    </div>

                                    {/* Artifacts Impacted */}
                                    <div className="space-y-3">
                                        <div className="flex items-center space-x-2">
                                            <div className="w-1 h-3 rounded-full bg-amber-500" />
                                            <h4 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Impacted Files</h4>
                                        </div>
                                        <div className="grid grid-cols-2 gap-3">
                                            {selectedCheckpoint?.files.map(file => (
                                                <div key={file} className="flex items-center justify-between p-3 bg-white/5 border border-white/5 rounded-xl group hover:border-amber-500/20 transition-all cursor-pointer">
                                                    <div className="flex items-center space-x-3">
                                                        <FileCode className="h-4 w-4 text-amber-400/70" />
                                                        <span className="text-xs font-mono">{file}</span>
                                                    </div>
                                                    <ChevronRight className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Mock Session Log */}
                                    <div className="space-y-3">
                                        <div className="flex items-center space-x-2">
                                            <div className="w-1 h-3 rounded-full bg-amber-500" />
                                            <h4 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Trace Log</h4>
                                        </div>
                                        <div className="font-mono text-[10px] space-y-1 text-muted-foreground/60 bg-black/60 p-4 rounded-xl border border-white/5 whitespace-pre overflow-x-auto">
                                            <div>[SYSTEM] Session initialized for commit {selectedCheckpoint?.commitHash}</div>
                                            <div>[AGENT] Reading workspace context...</div>
                                            <div>[TOOL] list_dir("src/pages") returned 12 files</div>
                                            <div>[AGENT] Rationale: Identified missing gap analysis visualization in ResearchLab.</div>
                                            <div>[TOOL] write_file("src/pages/research/ResearchLab.tsx") SUCCESS</div>
                                            <div className="text-amber-400/80">[ENTIRE] Checkpoint captured and linked to Git.</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full card flex flex-col items-center justify-center text-center opacity-40 select-none grayscale">
                            <Clock className="h-16 w-16 text-muted-foreground mb-4" />
                            <h3 className="text-xl font-bold">Provenance Inspector</h3>
                            <p className="text-sm max-w-sm mt-2">Select a session from the timeline to verify agent intent and trace codebase evolution.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
