import { useState, useEffect } from 'react'
import { Clock, FileText, Calendar, Tag, ChevronRight, Loader2, Search } from 'lucide-react'
import { apiService } from '../../services/api'
import { Link } from 'react-router-dom'

interface RecentNote {
    identifier: string
    title: string
    timestamp: string
    type: string
    summary?: string
    tags?: string[]
}

export default function Recents() {
    const [recents, setRecents] = useState<RecentNote[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [timeframe, setTimeframe] = useState('7d')
    const [searchQuery, setSearchQuery] = useState('')

    useEffect(() => {
        fetchRecents()
    }, [timeframe])

    const fetchRecents = async () => {
        setIsLoading(true)
        try {
            // Use activity tool call via API
            const response = await apiService.callMCPTool('adn_knowledge', {
                operation: 'activity',
                timeframe: timeframe,
                depth: 1
            })

            const responseData = response.data as any;
            if (response.success && responseData?.result?.results) {
                // Map activity results to our note format
                // The tool returns a list of ContextResult objects, each with a primary_result
                const notes = responseData.result.results
                    .map((item: any) => item.primary_result)
                    .filter((primary: any) => primary && (primary.type === 'entity' || primary.type === 'observation'))
                    .map((primary: any) => ({
                        identifier: primary.permalink || primary.title,
                        title: primary.title || primary.permalink,
                        timestamp: primary.created_at,
                        type: primary.type,
                        summary: primary.content?.substring(0, 150) + '...',
                        tags: primary.tags || []
                    }))
                setRecents(notes)
            }
        } catch (err) {
            console.error('Failed to fetch recents:', err)
        } finally {
            setIsLoading(false)
        }
    }

    const filteredRecents = recents.filter(note =>
        note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        note.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    )

    return (
        <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-700">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center space-x-3">
                    <div className="p-2 bg-accent/20 rounded-lg">
                        <Clock className="h-8 w-8 text-accent" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Recent Activity</h1>
                        <p className="text-muted-foreground text-sm">Review your most recent thoughts and updates</p>
                    </div>
                </div>

                <div className="flex items-center space-x-2">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <input
                            type="text"
                            placeholder="Filter recents..."
                            value={searchQuery}
                            onChange={e => setSearchQuery(e.target.value)}
                            className="bg-muted/50 border border-border rounded-full pl-10 pr-4 py-2 text-sm focus:ring-2 focus:ring-accent/50 outline-none w-64"
                        />
                    </div>

                    <select
                        value={timeframe}
                        onChange={e => setTimeframe(e.target.value)}
                        className="bg-muted/50 border border-border rounded-md px-3 py-2 text-sm outline-none cursor-pointer"
                    >
                        <option value="24h">Last 24 Hours</option>
                        <option value="7d">Last 7 Days</option>
                        <option value="30d">Last 30 Days</option>
                        <option value="90d">Last 3 Months</option>
                    </select>
                </div>
            </div>

            {isLoading ? (
                <div className="flex flex-col items-center justify-center py-20">
                    <Loader2 className="h-12 w-12 text-accent animate-spin mb-4" />
                    <p className="text-muted-foreground">Retrieving history...</p>
                </div>
            ) : filteredRecents.length === 0 ? (
                <div className="card p-12 text-center border-dashed">
                    <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4 opacity-20" />
                    <h3 className="text-xl font-semibold opacity-50">No recent activity found</h3>
                    <p className="text-muted-foreground mt-2 max-w-sm mx-auto">
                        Try expanding your timeframe or start creating new notes to see them here.
                    </p>
                </div>
            ) : (
                <div className="space-y-4">
                    {filteredRecents.map((note, index) => (
                        <Link
                            to={`/notes?id=${note.identifier}`}
                            key={`${note.identifier}-${index}`}
                            className="card group hover:border-accent/50 hover:bg-accent/5 transition-all duration-300 block overflow-hidden"
                        >
                            <div className="p-5 flex items-start gap-4">
                                <div className="p-3 bg-muted rounded-xl group-hover:bg-accent/10 transition-colors">
                                    <FileText className="h-6 w-6 text-muted-foreground group-hover:text-accent" />
                                </div>

                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between mb-1">
                                        <h3 className="font-bold text-lg group-hover:text-accent transition-colors truncate">
                                            {note.title}
                                        </h3>
                                        <div className="flex items-center text-xs text-muted-foreground bg-background px-2 py-1 rounded-full whitespace-nowrap">
                                            <Calendar className="h-3 w-3 mr-1" />
                                            {new Date(note.timestamp).toLocaleDateString()}
                                        </div>
                                    </div>

                                    <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                                        {note.summary || 'No summary available for this note.'}
                                    </p>

                                    <div className="flex items-center justify-between">
                                        <div className="flex gap-2">
                                            {note.tags?.slice(0, 3).map(tag => (
                                                <span key={tag} className="flex items-center text-[10px] px-2 py-0.5 bg-muted rounded text-muted-foreground uppercase tracking-wider font-semibold">
                                                    <Tag className="h-2 w-2 mr-1" />
                                                    {tag}
                                                </span>
                                            ))}
                                            {note.tags && note.tags.length > 3 && (
                                                <span className="text-[10px] text-muted-foreground pt-0.5 font-medium">+{note.tags.length - 3} more</span>
                                            )}
                                        </div>

                                        <div className="flex items-center text-xs font-bold text-accent opacity-0 group-hover:opacity-100 transition-opacity">
                                            <span>View details</span>
                                            <ChevronRight className="h-3 w-3 ml-1" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    )
}
