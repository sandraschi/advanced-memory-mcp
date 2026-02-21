import { useState, useEffect } from 'react'
import { Terminal, Shield, Zap, Search, Activity, BookOpen, Cpu, Settings, ChevronRight, Loader2, Sparkles, Box, Info } from 'lucide-react'
import { apiService } from '../../services/api'

interface ToolHelp {
    title: string
    summary: string
    params: { name: string; type: string; description: string }[]
    examples: string[]
}

interface ToolCategory {
    name: string
    tools: string[]
}

export default function Tools() {
    const [helpContent, setHelpContent] = useState<string>('')
    const [isLoading, setIsLoading] = useState(true)
    const [selectedTool, setSelectedTool] = useState<string | null>(null)

    const fetchHelp = async () => {
        setIsLoading(true)
        try {
            const response = await apiService.callMCPTool('help', { topic: 'tools', level: 'intermediate' })
            if (response.success && response.result?.help_content) {
                setHelpContent(response.result.help_content)
            }
        } catch (error) {
            console.error('Failed to fetch tool help:', error)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        fetchHelp()
    }, [])

    const parseHelpContent = (content: string) => {
        // Simple parser for the markdown help content
        const sections: { title: string; content: string }[] = []
        const toolMatches = content.matchAll(/### (.*?)\n([\s\S]*?)(?=### |## |$)/g)

        for (const match of toolMatches) {
            sections.push({
                title: match[1],
                content: match[2].trim()
            })
        }
        return sections
    }

    const tools = parseHelpContent(helpContent)

    return (
        <div className="flex flex-col h-full bg-background overflow-hidden relative animate-in fade-in duration-700">
            {/* Header */}
            <div className="px-10 py-8 border-b border-white/5 bg-black/40 backdrop-blur-xl flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    <div className="p-3 bg-blue-500/20 rounded-2xl">
                        <Cpu className="h-6 w-6 text-blue-500" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight">MCP Tool Orchestration</h1>
                        <p className="text-[10px] text-muted-foreground uppercase tracking-[0.2em] font-bold">Dynamic Docstring Substrate v2.0</p>
                    </div>
                </div>

                <div className="flex items-center space-x-4">
                    <button
                        onClick={fetchHelp}
                        className="p-2.5 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-all"
                    >
                        <Activity className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                    </button>
                    <div className="flex items-center space-x-2 bg-blue-500/10 border border-blue-500/20 px-4 py-2 rounded-full">
                        <Sparkles className="h-3 w-3 text-blue-500" />
                        <span className="text-[10px] uppercase font-bold tracking-widest text-blue-500">SOTA Documentation</span>
                    </div>
                </div>
            </div>

            <div className="flex-1 flex overflow-hidden">
                {/* Left Panel: Tool List */}
                <div className="w-80 border-r border-white/5 flex flex-col bg-black/20 overflow-hidden">
                    <div className="p-6 border-b border-white/5">
                        <div className="relative group">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground group-focus-within:text-blue-500 transition-colors" />
                            <input
                                type="text"
                                placeholder="Filter tools..."
                                className="w-full bg-white/5 border border-white/10 rounded-xl py-2 pl-9 pr-4 text-xs focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all text-white/80"
                            />
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 space-y-2 scrollbar-thin">
                        {isLoading ? (
                            <div className="flex flex-col items-center justify-center h-full space-y-4 opacity-50">
                                <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                                <span className="text-[10px] uppercase font-bold tracking-widest">Hydrating Substrate</span>
                            </div>
                        ) : (
                            tools.map(tool => (
                                <button
                                    key={tool.title}
                                    onClick={() => setSelectedTool(tool.title)}
                                    className={`w-full text-left p-4 rounded-2xl border transition-all group relative ${selectedTool === tool.title
                                        ? 'bg-blue-500/10 border-blue-500/30'
                                        : 'bg-white/2 border-white/5 hover:border-white/10 hover:bg-white/5'
                                        }`}
                                >
                                    <div className="flex items-center justify-between">
                                        <span className={`text-xs font-bold transition-colors ${selectedTool === tool.title ? 'text-blue-500' : 'text-white/60 group-hover:text-white'}`}>
                                            {tool.title.split('(')[0]}
                                        </span>
                                        <ChevronRight className={`h-3 w-3 transition-all ${selectedTool === tool.title ? 'translate-x-1 opacity-100' : 'opacity-0'}`} />
                                    </div>
                                    <div className="mt-1 text-[9px] text-muted-foreground line-clamp-1 opacity-60">
                                        Externalized Logic
                                    </div>
                                </button>
                            ))
                        )}
                    </div>
                </div>

                {/* Right Panel: Tool Details */}
                <div className="flex-1 flex flex-col overflow-hidden bg-black/40 relative">
                    {selectedTool ? (
                        <div className="flex-1 overflow-y-auto p-12 space-y-12 scrollbar-thin animate-in fade-in slide-in-from-right-4 duration-500">
                            {/* Tool Detail Header */}
                            <div className="space-y-4">
                                <div className="flex items-center space-x-3">
                                    <Box className="h-5 w-5 text-blue-500" />
                                    <h2 className="text-3xl font-bold tracking-tight text-white">{selectedTool}</h2>
                                </div>
                                <div className="flex items-center space-x-4">
                                    <div className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-[10px] font-mono text-muted-foreground uppercase tracking-widest">
                                        Portmanteau Tool
                                    </div>
                                    <div className="px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full text-[10px] font-bold text-green-500 uppercase tracking-widest">
                                        Production Ready
                                    </div>
                                </div>
                            </div>

                            {/* Tool Content Partition */}
                            <div className="grid grid-cols-1 gap-8">
                                <div className="bg-white/2 border border-white/5 rounded-3xl p-8 space-y-6">
                                    <div className="flex items-center space-x-2 text-blue-500">
                                        <Info className="h-4 w-4" />
                                        <h3 className="text-xs font-bold uppercase tracking-widest">Operational Logic</h3>
                                    </div>
                                    <div className="prose prose-invert prose-sm max-w-none prose-pre:bg-black/60 prose-pre:border prose-pre:border-white/10 prose-pre:rounded-2xl">
                                        <div className="text-white/80 leading-relaxed whitespace-pre-wrap font-sans">
                                            {tools.find(t => t.title === selectedTool)?.content}
                                        </div>
                                    </div>
                                </div>

                                <div className="bg-blue-500/5 border border-blue-500/10 rounded-3xl p-8 space-y-6">
                                    <div className="flex items-center space-x-2 text-blue-500">
                                        <Zap className="h-4 w-4" />
                                        <h3 className="text-xs font-bold uppercase tracking-widest">Execution Example</h3>
                                    </div>
                                    <div className="bg-black/40 rounded-2xl p-6 font-mono text-xs text-blue-400 border border-blue-500/10">
                                        await callMCPTool('{selectedTool.split('(')[0]}', &#123; ...params &#125;)
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center opacity-20 space-y-6">
                            <div className="relative">
                                <Box className="h-20 w-20" />
                                <div className="absolute inset-0 bg-blue-500 blur-3xl opacity-20 animate-pulse" />
                            </div>
                            <div className="text-center space-y-2">
                                <p className="text-sm font-bold uppercase tracking-[0.4em]">Select Tool for Logic Analysis</p>
                                <p className="text-[10px] text-muted-foreground uppercase font-mono italic">Hydrating documentation from backend substrate...</p>
                            </div>
                        </div>
                    )}

                    {/* Background Detail */}
                    <div className="absolute bottom-10 right-10 pointer-events-none opacity-5">
                        <Cpu className="h-64 w-64" />
                    </div>
                </div>
            </div>

            {/* Substrate Footer */}
            <div className="border-t border-white/5 bg-black/40 px-10 py-4 flex items-center justify-between">
                <div className="flex items-center space-x-6 text-[10px] uppercase font-bold tracking-widest text-muted-foreground">
                    <div className="flex items-center space-x-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
                        <span>{tools.length} Tools Discovered</span>
                    </div>
                    <span>Latency: 14ms</span>
                </div>
                <div className="flex items-center space-x-2 text-muted-foreground/40">
                    <Shield className="h-3.5 w-3.5" />
                    <span className="text-[10px] font-bold uppercase tracking-widest">Audit Trails Active</span>
                </div>
            </div>
        </div>
    )
}
