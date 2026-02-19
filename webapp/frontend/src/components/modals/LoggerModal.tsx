import { useState, useEffect, useRef, useMemo } from 'react'
import { X, Download, Trash2, Filter, Search, Clock } from 'lucide-react'

interface LoggerModalProps {
  isOpen: boolean
  onClose: () => void
}

// Mock log data - would be connected to actual logging service
const mockLogs = [
  { timestamp: '2026-01-20 14:30:15', level: 'INFO', message: 'Application started successfully' },
  { timestamp: '2026-01-20 14:30:16', level: 'INFO', message: 'Connected to Advanced Memory MCP server' },
  { timestamp: '2026-01-20 14:30:17', level: 'INFO', message: 'LLM provider detected: Ollama (llama3:8b)' },
  { timestamp: '2026-01-20 14:31:22', level: 'INFO', message: 'Research request initiated: brain tumor treatments' },
  { timestamp: '2026-01-20 14:31:23', level: 'INFO', message: 'Searching web sources...' },
  { timestamp: '2026-01-20 14:31:25', level: 'INFO', message: 'Found 15 relevant articles from NIH and Mayo Clinic' },
  { timestamp: '2026-01-20 14:31:28', level: 'INFO', message: 'Querying arXiv for recent publications...' },
  { timestamp: '2026-01-20 14:31:30', level: 'INFO', message: 'Retrieved 8 academic papers on glioblastoma' },
  { timestamp: '2026-01-20 14:31:32', level: 'INFO', message: 'Analyzing GitHub repositories for treatment algorithms' },
  { timestamp: '2026-01-20 14:31:35', level: 'INFO', message: 'Synthesizing research findings...' },
  { timestamp: '2026-01-20 14:31:40', level: 'SUCCESS', message: 'Skill creation completed: Brain Tumor Treatment Expert' },
]

const logLevelColors = {
  ERROR: 'text-red-400',
  WARNING: 'text-yellow-400',
  INFO: 'text-blue-400',
  SUCCESS: 'text-green-400',
  DEBUG: 'text-gray-400'
}

export default function LoggerModal({ isOpen, onClose }: LoggerModalProps) {
  const [logs, setLogs] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [autoScroll, setAutoScroll] = useState(true)
  const [showFilters, setShowFilters] = useState(false)
  const [levelFilters, setLevelFilters] = useState<Record<string, boolean>>({
    ERROR: true,
    WARNING: true,
    INFO: true,
    SUCCESS: true,
    DEBUG: true
  })
  const [searchQuery, setSearchQuery] = useState('')
  const [timeFilter, setTimeFilter] = useState<'all' | '1h' | '6h' | '24h' | 'custom'>('all')
  const logContainerRef = useRef<HTMLDivElement>(null)

  // Fetch logs from backend
  const fetchLogs = async () => {
    try {
      const response = await fetch('http://localhost:10705/api/v1/system/logs?limit=500')
      const result = await response.json()
      if (result.success && result.data) {
        setLogs(result.data)
      }
    } catch (error) {
      console.error('Failed to fetch logs:', error)
    }
  }

  // Initial fetch and polling when open
  useEffect(() => {
    if (isOpen) {
      fetchLogs()
      const interval = setInterval(fetchLogs, 2000)
      return () => clearInterval(interval)
    }
  }, [isOpen])

  // Filter logs based on current filters
  const filteredLogs = useMemo(() => {
    let filtered = logs.filter(log => levelFilters[log.level])

    // Text search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(log =>
        log.message.toLowerCase().includes(query) ||
        log.level.toLowerCase().includes(query)
      )
    }

    // Time filter
    if (timeFilter !== 'all') {
      const now = new Date()
      const filterTime = new Date()

      switch (timeFilter) {
        case '1h':
          filterTime.setHours(now.getHours() - 1)
          break
        case '6h':
          filterTime.setHours(now.getHours() - 6)
          break
        case '24h':
          filterTime.setDate(now.getDate() - 1)
          break
        case 'custom':
          // For now, just filter last 24h as default custom
          filterTime.setDate(now.getDate() - 1)
          break
      }

      filtered = filtered.filter(log => {
        // Handle format: 2026-02-17 01:04:55
        // Convert to ISO: 2026-02-17T01:04:55
        const logTime = new Date(log.timestamp.replace(' ', 'T'))
        return logTime >= filterTime
      })
    }

    return filtered
  }, [logs, levelFilters, searchQuery, timeFilter])

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [filteredLogs, autoScroll])

  const handleClearLogs = () => {
    // Currently clearing only locally, could be extended to server
    setLogs([])
  }

  const handleLevelFilterChange = (level: string, checked: boolean) => {
    setLevelFilters(prev => ({
      ...prev,
      [level]: checked
    }))
  }

  const handleClearFilters = () => {
    setLevelFilters({
      ERROR: true,
      WARNING: true,
      INFO: true,
      SUCCESS: true,
      DEBUG: true
    })
    setSearchQuery('')
    setTimeFilter('all')
  }

  const handleDownloadLogs = () => {
    const logText = filteredLogs.map(log =>
      `[${log.timestamp}] ${log.level} (${log.source || 'system'}): ${log.message}`
    ).join('\n')

    const blob = new Blob([logText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `advanced-memory-logs-${new Date().toISOString().split('T')[0]}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay">
      <div className="modal-content max-w-4xl max-h-[80vh]">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border pb-4">
          <h2 className="text-lg font-semibold">Application Logger</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-md hover:bg-muted transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between py-4 border-b border-border">
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={autoScroll}
                onChange={(e) => setAutoScroll(e.target.checked)}
                className="rounded border-border"
              />
              <span className="text-sm">Auto-scroll</span>
            </label>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`btn btn-outline btn-sm ${showFilters ? 'bg-accent' : ''}`}
            >
              <Filter className="h-4 w-4 mr-2" />
              Filters
            </button>
            <span className="text-sm text-muted-foreground">
              {filteredLogs.length} of {logs.length} log entries
            </span>
          </div>

          <div className="flex space-x-2">
            <button
              onClick={handleDownloadLogs}
              className="btn btn-outline btn-sm"
              disabled={filteredLogs.length === 0}
            >
              <Download className="h-4 w-4 mr-2" />
              Download
            </button>
            <button
              onClick={handleClearLogs}
              className="btn btn-outline btn-sm"
              disabled={logs.length === 0}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Clear
            </button>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="py-4 border-b border-border bg-muted/20 rounded-md">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Log Level Filters */}
              <div>
                <h4 className="text-sm font-medium mb-2 flex items-center">
                  <Filter className="h-4 w-4 mr-2" />
                  Log Levels
                </h4>
                <div className="space-y-2">
                  {Object.entries(levelFilters).map(([level, checked]) => (
                    <label key={level} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={(e) => handleLevelFilterChange(level, e.target.checked)}
                        className="rounded border-border"
                      />
                      <span className={`text-xs px-2 py-1 rounded ${logLevelColors[level as keyof typeof logLevelColors]} bg-muted`}>
                        {level}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Search Filter */}
              <div>
                <h4 className="text-sm font-medium mb-2 flex items-center">
                  <Search className="h-4 w-4 mr-2" />
                  Search
                </h4>
                <div className="relative">
                  <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                  <input
                    type="text"
                    placeholder="Search logs..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="input pl-8 text-sm w-full"
                  />
                </div>
              </div>

              {/* Time Filter */}
              <div>
                <h4 className="text-sm font-medium mb-2 flex items-center">
                  <Clock className="h-4 w-4 mr-2" />
                  Time Range
                </h4>
                <select
                  value={timeFilter}
                  onChange={(e) => setTimeFilter(e.target.value as any)}
                  className="input text-sm w-full"
                >
                  <option value="all">All Time</option>
                  <option value="1h">Last Hour</option>
                  <option value="6h">Last 6 Hours</option>
                  <option value="24h">Last 24 Hours</option>
                  <option value="custom">Custom Range</option>
                </select>
                <button
                  onClick={handleClearFilters}
                  className="btn btn-outline btn-xs mt-2 w-full"
                >
                  Clear All Filters
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Log content */}
        <div
          ref={logContainerRef}
          className="flex-1 overflow-auto bg-muted/50 rounded-md p-4 font-mono text-sm max-h-96"
        >
          {filteredLogs.length === 0 ? (
            <div className="text-muted-foreground text-center py-8">
              {logs.length === 0 ? 'No log entries available' : 'No logs match current filters'}
            </div>
          ) : (
            filteredLogs.map((log, index) => (
              <div key={index} className="mb-1 leading-relaxed">
                <span className="text-muted-foreground">[{log.timestamp}]</span>{' '}
                <span className={logLevelColors[log.level as keyof typeof logLevelColors] || 'text-foreground'}>
                  {log.level}:
                </span>{' '}
                <span className="text-foreground">{log.message}</span>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end pt-4 border-t border-border">
          <button onClick={onClose} className="btn btn-primary">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
