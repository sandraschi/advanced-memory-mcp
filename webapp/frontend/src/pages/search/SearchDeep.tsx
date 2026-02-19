import { useState } from 'react'
import { Search, Filter, Folder, Target, ChevronRight, Bookmark, Clock, Share2, MoreVertical, Loader2, Sparkles, Brain, Database } from 'lucide-react'

interface SearchResult {
    id: string
    title: string
    snippet: string
    source: string
    project: string
    tags: string[]
    score: number
    date: string
}

export default function SearchDeep() {
    const [query, setQuery] = useState('')
    const [isSearching, setIsSearching] = useState(false)
    const [results, setResults] = useState<SearchResult[]>([])
    const [activeFilters, setActiveFilters] = useState<string[]>(['All Projects', 'Knowledge Base'])

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault()
        if (!query.trim()) return

        setIsSearching(true)
        // Simulate deep semantic search across multiple projects
        setTimeout(() => {
            setResults([
                {
                    id: '1',
                    title: 'Materialist Epistemology in AI Development',
                    snippet: 'The core architecture follows a reductionist approach where data constituents are the primary arbiters of truth. This aligns with the Sandra-SOTA protocols defined in v13.0...',
                    source: 'Zettelkasten',
                    project: 'Advanced Memory',
                    tags: ['philosophy', 'architecture', 'SOTA'],
                    score: 0.98,
                    date: '2026-02-17'
                },
                {
                    id: '2',
                    title: 'Robotics Control State Machine',
                    snippet: 'Wandering/Conversing/Performing states are managed via a nested state machine that prioritizes safe proximity behaviors and low-latency response cycles...',
                    source: 'Research Lab',
                    project: 'Robotics MCP',
                    tags: ['robotics', 'state-machine', 'kinematics'],
                    score: 0.85,
                    date: '2026-02-15'
                },
                {
                    id: '3',
                    title: 'ClawHub Security Audit Protocol',
                    snippet: 'Analysis of binary purges and static code analysis for Thermodynamic Villains. Recent malware trends (AMOS) require strict 5-point scrubbing before ingestion...',
                    source: 'Skills Depot',
                    project: 'Advanced Memory',
                    tags: ['security', 'malware', 'clawhub'],
                    score: 0.92,
                    date: '2026-02-16'
                }
            ])
            setIsSearching(false)
        }, 1500)
    }

    return (
        <div className="flex flex-col h-full bg-background">
            {/* Search Header */}
            <div className="border-b border-white/5 bg-black/20 backdrop-blur-xl px-10 py-12">
                <div className="max-w-4xl mx-auto space-y-8">
                    <div className="flex items-center justify-between">
                        <div className="space-y-1">
                            <h1 className="text-3xl font-bold tracking-tight">Deep Intelligence Search</h1>
                            <p className="text-sm text-muted-foreground">Cross-project semantic retrieval across your entire knowledge base.</p>
                        </div>
                        <div className="flex items-center space-x-2 bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 rounded-full">
                            <Brain className="h-4 w-4 text-amber-500" />
                            <span className="text-[10px] uppercase font-bold tracking-widest text-amber-500">RAG Engine v3.0</span>
                        </div>
                    </div>

                    <form onSubmit={handleSearch} className="relative group">
                        <div className="absolute inset-x-0 -inset-y-0.5 bg-gradient-to-r from-amber-500/20 via-blue-500/20 to-purple-500/20 rounded-2xl blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity duration-500" />
                        <div className="relative flex items-center bg-black/40 border border-white/10 rounded-2xl overflow-hidden shadow-2xl transition-all duration-300 group-focus-within:border-white/20 group-focus-within:bg-black/60">
                            <div className="pl-6 pr-4">
                                <Search className={`h-6 w-6 transition-colors ${isSearching ? 'text-amber-500 animate-pulse' : 'text-muted-foreground group-focus-within:text-white'}`} />
                            </div>
                            <input
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="Query the second brain..."
                                className="flex-1 bg-transparent border-none py-6 pr-6 text-xl focus:outline-none placeholder:text-muted-foreground/50 transition-all"
                            />
                            <div className="pr-4">
                                <button
                                    type="submit"
                                    disabled={!query.trim() || isSearching}
                                    className="bg-primary hover:bg-primary/90 disabled:opacity-50 text-primary-foreground px-6 py-3 rounded-xl font-bold text-sm transition-all"
                                >
                                    {isSearching ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Retrieve'}
                                </button>
                            </div>
                        </div>
                    </form>

                    <div className="flex flex-wrap gap-2">
                        {['All Projects', 'Knowledge Base', 'Research Lab', 'Skills Depot', 'Academic (arXiv)', 'Code Sites'].map(filter => (
                            <button
                                key={filter}
                                onClick={() => setActiveFilters(prev =>
                                    prev.includes(filter) ? prev.filter(f => f !== filter) : [...prev, filter]
                                )}
                                className={`px-4 py-1.5 rounded-full text-[10px] uppercase font-bold tracking-widest border transition-all ${activeFilters.includes(filter)
                                    ? 'bg-white text-black border-white'
                                    : 'bg-white/5 text-muted-foreground border-white/10 hover:border-white/20'
                                    }`}
                            >
                                {filter}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Results Area */}
            <div className="flex-1 overflow-y-auto px-10 py-12 scrollbar-thin">
                <div className="max-w-4xl mx-auto space-y-10">
                    {isSearching ? (
                        <div className="flex flex-col items-center justify-center py-20 space-y-4">
                            <div className="relative">
                                <Brain className="h-12 w-12 text-amber-500 animate-pulse" />
                                <div className="absolute inset-0 bg-amber-500/20 blur-2xl animate-pulse rounded-full" />
                            </div>
                            <div className="text-center space-y-2">
                                <p className="text-sm font-bold uppercase tracking-[0.3em]">Querying Semantic Index</p>
                                <p className="text-[10px] text-muted-foreground uppercase font-mono italic">Scanning 14,287 intelligence nodes...</p>
                            </div>
                        </div>
                    ) : results.length > 0 ? (
                        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                            <div className="flex items-center justify-between opacity-50">
                                <span className="text-[10px] uppercase font-bold tracking-widest leading-none flex items-center space-x-2">
                                    <Database className="h-3 w-3" />
                                    <span>{results.length} intelligence clusters identified</span>
                                </span>
                                <div className="flex items-center space-x-4">
                                    <button className="flex items-center space-x-2 text-[10px] uppercase font-bold tracking-widest hover:text-white transition-colors">
                                        <Filter className="h-3 w-3" />
                                        <span>Sort by Score</span>
                                    </button>
                                </div>
                            </div>

                            <div className="space-y-4">
                                {results.map(result => (
                                    <div key={result.id} className="group relative bg-white/2 border border-white/5 hover:border-white/10 p-8 rounded-3xl transition-all duration-300 hover:bg-white/[0.04] hover:-translate-y-1">
                                        <div className="flex items-start justify-between mb-4">
                                            <div className="space-y-2">
                                                <div className="flex items-center space-x-3">
                                                    <h3 className="text-lg font-bold group-hover:text-amber-500 transition-colors">{result.title}</h3>
                                                    <div className="px-2 py-0.5 bg-amber-500/10 border border-amber-500/20 rounded-md">
                                                        <span className="text-[9px] font-mono font-bold text-amber-500">{(result.score * 100).toFixed(0)}% Match</span>
                                                    </div>
                                                </div>
                                                <div className="flex items-center space-x-3 text-[10px] text-muted-foreground uppercase font-bold tracking-tight">
                                                    <div className="flex items-center space-x-1">
                                                        <Folder className="h-3 w-3" />
                                                        <span>{result.project}</span>
                                                    </div>
                                                    <div className="w-1 h-1 rounded-full bg-white/20" />
                                                    <div className="flex items-center space-x-1">
                                                        <Clock className="h-3 w-3" />
                                                        <span>{result.date}</span>
                                                    </div>
                                                    <div className="w-1 h-1 rounded-full bg-white/20" />
                                                    <div className="flex items-center space-x-1">
                                                        <Target className="h-3 w-3" />
                                                        <span>{result.source}</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <button className="p-2 hover:bg-white/10 rounded-xl transition-colors"><Bookmark className="h-4 w-4" /></button>
                                                <button className="p-2 hover:bg-white/10 rounded-xl transition-colors"><Share2 className="h-4 w-4" /></button>
                                                <button className="p-2 hover:bg-white/10 rounded-xl transition-colors"><MoreVertical className="h-4 w-4" /></button>
                                            </div>
                                        </div>
                                        <p className="text-sm text-muted-foreground leading-relaxed mb-6 line-clamp-2">{result.snippet}</p>
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-2">
                                                {result.tags.map(tag => (
                                                    <span key={tag} className="px-2 py-1 bg-white/5 border border-white/5 rounded-md text-[9px] font-mono text-muted-foreground">#{tag}</span>
                                                ))}
                                            </div>
                                            <button className="flex items-center space-x-2 text-[10px] uppercase font-bold tracking-widest text-amber-500 hover:text-amber-400 group/btn transition-colors">
                                                <span>Explore Cluster</span>
                                                <ChevronRight className="h-3 w-3 group-hover/btn:translate-x-1 transition-transform" />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center py-32 space-y-6 opacity-30">
                            <Brain className="h-16 w-16" />
                            <div className="text-center space-y-2">
                                <p className="text-lg font-bold uppercase tracking-[0.2em]">Ready for Inference</p>
                                <p className="text-sm">Semantic retrieval engine active on ports 10705/10706.</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Search Tips Footer */}
            <div className="border-t border-white/5 bg-black/40 p-6">
                <div className="max-w-4xl mx-auto flex items-center justify-between text-[10px] uppercase font-bold tracking-widest text-muted-foreground">
                    <div className="flex items-center space-x-6">
                        <div className="flex items-center space-x-2">
                            <span className="bg-white/10 px-1.5 py-0.5 rounded text-[8px]">/</span>
                            <span>Global Command</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <span className="bg-white/10 px-1.5 py-0.5 rounded text-[8px]">PROJ:</span>
                            <span>Project Filter</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <span className="bg-white/10 px-1.5 py-0.5 rounded text-[8px]">NEAR:</span>
                            <span>Semantic Proximity</span>
                        </div>
                    </div>
                    <div className="flex items-center space-x-2 text-amber-500/60">
                        <Sparkles className="h-3 w-3" />
                        <span>Vector Index: 98.4% Integrated</span>
                    </div>
                </div>
            </div>
        </div>
    )
}
