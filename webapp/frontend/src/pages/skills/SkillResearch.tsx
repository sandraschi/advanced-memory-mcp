import { useState } from 'react'
import {
    Search,
    Loader2,
    BookOpen,
    ExternalLink,
    Globe,
    Github,
    AlertCircle,
    Sparkles
} from 'lucide-react'
import { apiService } from '../../services/api'

interface ResearchResult {
    id: string
    title: string
    url?: string
    snippet: string
    source: 'web' | 'github' | 'arxiv'
}

export default function SkillResearch() {
    const [query, setQuery] = useState('')
    const [isSearching, setIsSearching] = useState(false)
    const [results, setResults] = useState<ResearchResult[]>([])
    const [selectedResults, setSelectedResults] = useState<Set<string>>(new Set())
    const [isCreating, setIsCreating] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [activeSource, setActiveSource] = useState<'web' | 'github' | 'arxiv'>('web')

    const sourceConfig = {
        web: { icon: Globe, label: 'Web Search', operation: 'web_search' },
        github: { icon: Github, label: 'GitHub', operation: 'github' },
        arxiv: { icon: BookOpen, label: 'arXiv', operation: 'arxiv' },
    }

    const handleSearch = async () => {
        if (!query.trim()) return
        setIsSearching(true)
        setError(null)
        setResults([])

        try {
            const config = sourceConfig[activeSource]
            const response = await apiService.callMCPTool('adn_research', {
                operation: config.operation,
                query: query.trim(),
                limit: 15,
            })

            if (response.success && response.data) {
                const data = response.data
                const raw = data.results || data.data || data.result?.results || []
                const mapped: ResearchResult[] = Array.isArray(raw)
                    ? raw.map((r: any, i: number) => ({
                        id: r.id || `${activeSource}-${i}`,
                        title: r.title || r.name || r.full_name || 'Untitled',
                        url: r.url || r.html_url || r.link || undefined,
                        snippet: r.snippet || r.description || r.abstract || r.summary || '',
                        source: activeSource,
                    }))
                    : []
                setResults(mapped)
            } else {
                setError(response.error || 'No results found')
            }
        } catch (err: any) {
            setError(err.message || 'Search failed')
        } finally {
            setIsSearching(false)
        }
    }

    const toggleSelect = (id: string) => {
        setSelectedResults(prev => {
            const next = new Set(prev)
            if (next.has(id)) next.delete(id)
            else next.add(id)
            return next
        })
    }

    const handleCreateSkill = async () => {
        if (selectedResults.size === 0) return
        setIsCreating(true)
        setError(null)

        try {
            const selected = results.filter(r => selectedResults.has(r.id))
            const content = selected.map(r => `## ${r.title}\n${r.snippet}\n${r.url ? `Source: ${r.url}` : ''}`).join('\n\n')
            const response = await apiService.callMCPTool('adn_skills', {
                operation: 'creator',
                content: `Create a skill based on:\n\n${content}`,
            })

            if (response.success) {
                setSelectedResults(new Set())
                setResults([])
                setQuery('')
            } else {
                setError(response.error || 'Skill creation failed')
            }
        } catch (err: any) {
            setError(err.message || 'Skill creation failed')
        } finally {
            setIsCreating(false)
        }
    }

    const SourceIcon = sourceConfig[activeSource].icon

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold flex items-center">
                    <Search className="h-6 w-6 mr-2 text-accent" />
                    Skill Research
                </h1>
                <p className="text-sm text-muted-foreground mt-1">
                    Search the web, GitHub, and arXiv — then turn results into skills
                </p>
            </div>

            {/* Source Tabs + Search Bar */}
            <div className="space-y-3">
                <div className="flex space-x-1">
                    {(Object.entries(sourceConfig) as [typeof activeSource, typeof sourceConfig['web']][]).map(([key, cfg]) => {
                        const Icon = cfg.icon
                        return (
                            <button
                                key={key}
                                onClick={() => setActiveSource(key)}
                                className={`flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${activeSource === key
                                    ? 'bg-accent text-accent-foreground'
                                    : 'text-muted-foreground hover:bg-muted'
                                    }`}
                            >
                                <Icon className="h-4 w-4 mr-2" />
                                {cfg.label}
                            </button>
                        )
                    })}
                </div>

                <div className="flex space-x-3">
                    <input
                        type="text"
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleSearch()}
                        placeholder={`Search ${sourceConfig[activeSource].label}...`}
                        className="flex-1 px-4 py-3 bg-card border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent"
                    />
                    <button
                        onClick={handleSearch}
                        disabled={isSearching || !query.trim()}
                        className="px-6 py-3 bg-accent text-accent-foreground rounded-lg text-sm font-medium hover:bg-accent/90 transition-colors disabled:opacity-50 flex items-center"
                    >
                        {isSearching ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Search className="h-4 w-4 mr-2" />}
                        Search
                    </button>
                </div>
            </div>

            {/* Error */}
            {error && (
                <div className="flex items-center p-4 bg-destructive/10 text-destructive rounded-lg text-sm">
                    <AlertCircle className="h-4 w-4 mr-2 flex-shrink-0" />
                    {error}
                </div>
            )}

            {/* Results */}
            {results.length > 0 && (
                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-semibold">
                            Found {results.length} results
                        </h2>
                        {selectedResults.size > 0 && (
                            <button
                                onClick={handleCreateSkill}
                                disabled={isCreating}
                                className="flex items-center px-4 py-2 bg-accent text-accent-foreground text-sm font-medium rounded-lg hover:bg-accent/90 transition-colors disabled:opacity-50"
                            >
                                {isCreating
                                    ? <Loader2 className="h-4 w-4 animate-spin mr-2" />
                                    : <Sparkles className="h-4 w-4 mr-2" />}
                                Create Skill from {selectedResults.size} selected
                            </button>
                        )}
                    </div>

                    {results.map(result => (
                        <div
                            key={result.id}
                            onClick={() => toggleSelect(result.id)}
                            className={`bg-card border rounded-lg p-4 transition-all cursor-pointer ${selectedResults.has(result.id)
                                ? 'border-accent ring-1 ring-accent'
                                : 'border-border hover:border-accent/50'
                                }`}
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center space-x-2">
                                        <SourceIcon className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                                        <h3 className="font-medium truncate">{result.title}</h3>
                                    </div>
                                    <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{result.snippet}</p>
                                </div>
                                {result.url && (
                                    <a
                                        href={result.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        onClick={e => e.stopPropagation()}
                                        className="ml-3 p-1 text-muted-foreground hover:text-foreground"
                                    >
                                        <ExternalLink className="h-4 w-4" />
                                    </a>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Empty State */}
            {!isSearching && results.length === 0 && !error && (
                <div className="text-center py-16 text-muted-foreground">
                    <Search className="h-12 w-12 mx-auto mb-4 opacity-30" />
                    <p className="text-lg font-medium">Search for research material</p>
                    <p className="text-sm mt-1">Select results and turn them into skills automatically</p>
                </div>
            )}
        </div>
    )
}
