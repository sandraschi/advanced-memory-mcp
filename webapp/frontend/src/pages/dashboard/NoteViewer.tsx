import { useState, useEffect } from 'react'
import { Search, FileText, Eye, Download, Share, MoreVertical, Filter, X, Maximize2, Minimize2, List, Network, Folder, ChevronLeft, ChevronRight, ChevronDown } from 'lucide-react'
import { apiService } from '../../services/api'

interface Note {
  id: string
  title: string
  content: string
  tags: string[]
  created: string
  modified: string
  wordCount: number
  connections: number
}

interface NoteViewerProps {
  selectedNoteId?: string | undefined
  onNoteSelect?: (noteId: string) => void
}

export default function NoteViewer({ selectedNoteId, onNoteSelect }: NoteViewerProps) {
  const [notes, setNotes] = useState<Note[]>([])
  const [filteredNotes, setFilteredNotes] = useState<Note[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedNote, setSelectedNote] = useState<Note | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [serverStatus, setServerStatus] = useState<'checking' | 'running' | 'stopped' | 'starting'>('checking')
  const [serverError, setServerError] = useState<string>('')
  const [showFilters, setShowFilters] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)

  // View Mode State
  const [viewMode, setViewMode] = useState<'list' | 'tree'>('list')
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalNotes, setTotalNotes] = useState(0)

  // Filter state
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [dateCreatedFrom, setDateCreatedFrom] = useState('')
  const [dateCreatedTo, setDateCreatedTo] = useState('')
  const [dateModifiedFrom, setDateModifiedFrom] = useState('')
  const [dateModifiedTo, setDateModifiedTo] = useState('')
  const [availableTags, setAvailableTags] = useState<string[]>([])

  // State for notes and UI


  const checkServerStatus = async (): Promise<boolean> => {
    try {
      setServerStatus('checking')
      // Try to ping the bridge server
      const response = await fetch('http://localhost:10705/api/v1/health', {
        method: 'GET',
        signal: AbortSignal.timeout(2000) // 2 second timeout
      })
      const isRunning = response.ok
      setServerStatus(isRunning ? 'running' : 'stopped')
      return isRunning
    } catch (error) {
      console.log('Bridge server not responding:', error)
      setServerStatus('stopped')
      return false
    }
  }

  /*
    const _startServer = async (): Promise<boolean> => {
      try {
        setServerStatus('starting')
        setServerError('')

        console.log('Attempting to start ADN MCP server...')

        // Try to start the server by opening a terminal/command prompt
        // This will open a new terminal window with the server start command

        // For Windows PowerShell
        const _command = 'Start-Process powershell -ArgumentList "cd D:\\Dev\\repos\\advanced-memory-mcp; python -m advanced_memory.mcp.server" -WindowStyle Normal'

        // Execute the command (this opens a new PowerShell window)
        // Note: This is a simplified approach. In production, you'd want better error handling
        // and possibly use a service manager or background process

        if (typeof window !== 'undefined') {
          // Alternative approach: try to open a command prompt
          // This is more reliable for starting background processes
          const _shellCommand = `cmd.exe /c start cmd.exe /k "cd /d D:\\Dev\\repos\\advanced-memory-mcp && python -m advanced_memory.mcp.server && pause"`

          // Use a hidden iframe or similar to execute system commands
          // For now, we'll provide instructions to the user
          setServerError('Please start the ADN MCP server manually by running: python -m advanced_memory.mcp.server')

          // Wait a bit and check again
          setTimeout(async () => {
            const isRunning = await checkServerStatus()
            if (isRunning) {
              setServerError('')
              loadNotes() // Reload notes once server is running
            }
          }, 5000)

          return false // Indicate manual intervention needed
        }

        return false
      } catch (error) {
        console.error('Error starting server:', error)
        setServerError('Failed to start server. Please start it manually.')
        setServerStatus('stopped')
        return false
      }
    }
  */

  const checkStartupService = async (): Promise<boolean> => {
    try {
      const response = await fetch('http://localhost:10733/health', {
        method: 'GET',
        signal: AbortSignal.timeout(1000)
      })
      return response.ok
    } catch (error) {
      return false
    }
  }

  /*
    const _startStartupService = async (): Promise<boolean> => {
      try {
        console.log('Attempting to start startup service...')

        // Since we can't directly execute from browser, we'll try to use a web-based approach
        // For now, we'll assume the startup service should be running and proceed
        console.log('Startup service check/attempt completed')

        // Small delay to allow for any startup
        await new Promise(resolve => setTimeout(resolve, 500))

        return await checkStartupService()
      } catch (error) {
        console.error('Error checking startup service:', error)
        return false
      }
    }
  */

  const startAllServices = async (): Promise<boolean> => {
    try {
      setServerStatus('starting')
      setServerError('Starting all ADN services...')

      console.log('Attempting to auto-start all services...')

      // Try to start everything via the auto-start service
      const response = await fetch('http://localhost:10735/start-all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })

      if (response.ok) {
        console.log('All services start initiated')

        // Wait for services (incl. bridge via start-bridge) to start up
        await new Promise(resolve => setTimeout(resolve, 5000))

        let isRunning = await checkServerStatus()
        if (isRunning) {
          setServerError('')
          console.log('All services started successfully')
          return true
        }

        // Bridge may still be starting; try explicit start-bridge then retry
        console.log('Bridge not up after start-all, trying start-bridge...')
        isRunning = await startBridgeServer()
        if (isRunning) return true

        console.log('Services started but bridge server not responding')
        setServerError('Services started but bridge server not responding. Using demo data.')
        setServerStatus('stopped')
        return false
      } else {
        console.log('Auto-start service not available, trying manual startup...')
        return await startBridgeServer()
      }
    } catch (error) {
      console.error('Error starting all services:', error)
      setServerError('Could not start services automatically. Using demo data.')
      setServerStatus('stopped')
      return false
    }
  }

  const startBridgeServer = async (): Promise<boolean> => {
    try {
      setServerStatus('starting')
      setServerError('')
      console.log('Attempting manual bridge server startup...')

      // First ensure startup service is available
      let startupRunning = await checkStartupService()
      if (!startupRunning) {
        console.log('Startup service not running, attempting to start it...')
        // Try to use auto-start service for startup service
        try {
          await fetch('http://localhost:10735/start-all', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
          })
          await new Promise(resolve => setTimeout(resolve, 2000))
          startupRunning = await checkStartupService()
        } catch (autoStartError) {
          console.log('Auto-start service not available either')
        }
      }

      if (!startupRunning) {
        console.log('Could not start startup service, using mock data')
        setServerError('Could not start required services. Using demo data.')
        setServerStatus('stopped')
        return false
      }

      // Try to start the bridge server via the startup service
      const response = await fetch('http://localhost:10733/start-bridge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })

      if (response.ok) {
        console.log('Bridge server start initiated')

        // Wait for the bridge server to start up
        await new Promise(resolve => setTimeout(resolve, 3000))

        // Check if bridge server is now running
        const isRunning = await checkServerStatus()
        if (isRunning) {
          setServerError('')
          console.log('Bridge server started successfully')
          return true
        } else {
          console.log('Bridge server did not respond after startup attempt')
          setServerError('Bridge server started but not responding. Using demo data.')
          setServerStatus('stopped')
          return false
        }
      } else {
        console.log('Startup service responded with error, using mock data')
        setServerError('Could not start bridge server. Using demo data.')
        setServerStatus('stopped')
        return false
      }
    } catch (error) {
      console.error('Error starting bridge server:', error)
      setServerError('Could not start bridge server automatically. Using demo data.')
      setServerStatus('stopped')
      return false
    }
  }

  const loadNotes = async (page = 1) => {
    setIsLoading(true)
    try {
      // First check if bridge server is running
      let serverRunning = await checkServerStatus()

      if (!serverRunning) {
        console.log('Bridge server not running, attempting auto-start...')
        // Try to auto-start all services
        serverRunning = await startAllServices()
      }

      // Try to fetch real notes if server is now running
      if (serverRunning) {
        try {
          const response = await (searchQuery.trim() !== ''
            ? apiService.searchNotes(searchQuery, page, 50, selectedTags)
            : apiService.getNotes(page, 50))

          if (response.success && response.data?.notes) {
            const notesData = response.data.notes
            setNotes(notesData)
            setFilteredNotes(notesData)
            setCurrentPage(response.data.page || page)
            setTotalPages(response.data.pages || 1)
            setTotalNotes(response.data.total || notesData.length)

            // Extract available tags
            const allTags = new Set<string>()
            notesData.forEach(note => {
              if (Array.isArray(note.tags)) {
                note.tags.forEach(tag => allTags.add(tag))
              }
            })
            setAvailableTags(Array.from(allTags).sort())
            setIsLoading(false)
            return
          } else {
            setServerError(response.error || 'No notes found in knowledge base.')
          }
        } catch (apiError) {
          console.error('API call failed:', apiError)
          setServerError('Failed to fetch notes from server.')
        }
      }

      setNotes([])
      setFilteredNotes([])
      setAvailableTags([])
      setIsLoading(false)
    } catch (error) {
      console.error('Failed to load notes:', error)
      setServerError('An unexpected error occurred while loading notes.')
      setNotes([])
      setFilteredNotes([])
      setAvailableTags([])
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadNotes(currentPage)

    // Check server status periodically
    const interval = setInterval(() => {
      checkServerStatus()
    }, 10000) // Check every 10 seconds

    return () => clearInterval(interval)
  }, [])

  // Apply all filters (search, tags, dates)
  const applyFilters = (notesList: Note[]) => {
    let filtered = notesList

    // Search filter
    if (searchQuery.trim() !== '') {
      filtered = filtered.filter(note =>
        note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        note.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        note.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    }

    // Tag filter
    if (selectedTags.length > 0) {
      filtered = filtered.filter(note =>
        selectedTags.some(selectedTag => note.tags.includes(selectedTag))
      )
    }

    // Date filters
    if (dateCreatedFrom) {
      const fromDate = new Date(dateCreatedFrom)
      filtered = filtered.filter(note => new Date(note.created) >= fromDate)
    }
    if (dateCreatedTo) {
      const toDate = new Date(dateCreatedTo)
      toDate.setHours(23, 59, 59, 999) // End of day
      filtered = filtered.filter(note => new Date(note.created) <= toDate)
    }
    if (dateModifiedFrom) {
      const fromDate = new Date(dateModifiedFrom)
      filtered = filtered.filter(note => new Date(note.modified) >= fromDate)
    }
    if (dateModifiedTo) {
      const toDate = new Date(dateModifiedTo)
      toDate.setHours(23, 59, 59, 999) // End of day
      filtered = filtered.filter(note => new Date(note.modified) <= toDate)
    }

    return filtered
  }

  useEffect(() => {
    const filtered = applyFilters(notes)
    setFilteredNotes(filtered)
  }, [searchQuery, selectedTags, dateCreatedFrom, dateCreatedTo, dateModifiedFrom, dateModifiedTo, notes])

  useEffect(() => {
    // Select note based on selectedNoteId prop
    if (selectedNoteId) {
      const note = notes.find(n => n.id === selectedNoteId)
      if (note) {
        setSelectedNote(note)
      }
    }
  }, [selectedNoteId, notes])

  const handleNoteSelect = async (note: Note) => {
    setSelectedNote(note)
    onNoteSelect?.(note.id)

    // Try to fetch full note content from API
    try {
      const response = await apiService.getNote(note.id)
      if (response.success && response.data) {
        setSelectedNote(response.data)
      }
    } catch (error) {
      console.error('Failed to fetch full note content:', error)
      // Keep the basic note data if API call fails
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Tree building helper
  interface TreeNode {
    name: string
    path: string
    note?: Note
    children: Record<string, TreeNode>
  }

  const buildTree = (notesList: Note[]): TreeNode[] => {
    const root: Record<string, TreeNode> = {}

    notesList.forEach(note => {
      const permalink = (note as any).permalink || note.title || ''
      const pathParts = permalink.includes('/') ? permalink.split('/') : [note.title]

      let currentLevel = root
      let currentPath = ''

      pathParts.forEach((part: string, index: number) => {
        currentPath = currentPath ? `${currentPath}/${part}` : part
        if (!currentLevel[part]) {
          currentLevel[part] = {
            name: part,
            path: currentPath,
            children: {}
          }
        }
        if (index === pathParts.length - 1) {
          currentLevel[part].note = note
        }
        currentLevel = currentLevel[part].children
      })
    })

    const recursiveSort = (nodes: TreeNode[]): TreeNode[] => {
      const sorted = [...nodes].sort((a, b) => {
        const aIsFolder = Object.keys(a.children).length > 0 && !a.note
        const bIsFolder = Object.keys(b.children).length > 0 && !b.note
        if (aIsFolder !== bIsFolder) return aIsFolder ? -1 : 1
        return a.name.localeCompare(b.name)
      });
      sorted.forEach(node => {
        const sortedChildren = recursiveSort(Object.values(node.children))
        node.children = {}
        sortedChildren.forEach(c => { node.children[c.name] = c })
      });
      return sorted
    }

    return recursiveSort(Object.values(root))
  }

  const toggleNode = (path: string) => {
    const newExpanded = new Set(expandedNodes)
    if (newExpanded.has(path)) {
      newExpanded.delete(path)
    } else {
      newExpanded.add(path)
    }
    setExpandedNodes(newExpanded)
  }

  const renderTreeNodes = (nodes: TreeNode[], level = 0): React.ReactNode => {
    return nodes.map((node) => {
      const isExpanded = expandedNodes.has(node.path)
      const hasChildren = Object.keys(node.children).length > 0
      const isSelected = selectedNote?.id === node.note?.id

      return (
        <div key={node.path} className="w-full">
          <div
            className={`flex items-center py-1.5 px-2 cursor-pointer hover:bg-muted/50 text-sm ${isSelected ? 'bg-accent/10 border-l-2 border-accent text-accent font-medium' : 'text-foreground border-l-2 border-transparent'}`}
            style={{ paddingLeft: `${level * 12 + 8}px` }}
            onClick={() => {
              if (node.note) {
                handleNoteSelect(node.note)
              } else if (hasChildren) {
                toggleNode(node.path)
              }
            }}
          >
            {hasChildren && (
              <button
                onClick={(e) => { e.stopPropagation(); toggleNode(node.path) }}
                className="w-4 h-4 mr-1 flex items-center justify-center text-muted-foreground hover:text-foreground"
              >
                {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
              </button>
            )}
            {!hasChildren && <div className="w-5" />}

            {(hasChildren && !node.note) ? (
              <Folder className="w-3.5 h-3.5 mr-2 text-muted-foreground" />
            ) : (
              <FileText className="w-3.5 h-3.5 mr-2 text-muted-foreground shrink-0" />
            )}

            <span className="truncate">{node.name}</span>
          </div>

          {isExpanded && hasChildren && (
            <div className="w-full">
              {renderTreeNodes(Object.values(node.children), level + 1)}
            </div>
          )}
        </div>
      )
    })
  }

  return (
    <div className="h-full min-h-0 flex flex-col">
      {/* Search Header */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center space-x-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <input
              type="text"
              placeholder="Search notes... (press Enter)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && loadNotes(1)}
              className="input pl-10 w-full"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`btn btn-outline flex items-center ${showFilters ? 'bg-accent/10' : ''}`}
          >
            <Filter className="h-4 w-4 mr-2" />
            Filters
            {(selectedTags.length > 0 || dateCreatedFrom || dateCreatedTo || dateModifiedFrom || dateModifiedTo) && (
              <span className="ml-2 bg-accent text-accent-foreground rounded-full px-2 py-0.5 text-xs">
                {selectedTags.length + (dateCreatedFrom ? 1 : 0) + (dateCreatedTo ? 1 : 0) + (dateModifiedFrom ? 1 : 0) + (dateModifiedTo ? 1 : 0)}
              </span>
            )}
          </button>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-muted-foreground whitespace-nowrap">
              {filteredNotes.length > 0 ? `${(currentPage - 1) * 50 + 1} - ${Math.min(currentPage * 50, totalNotes)} of ${totalNotes}` : '0'} notes
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${serverStatus === 'running' ? 'bg-green-500' : serverStatus === 'starting' ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'}`}></div>
              <span className="text-xs text-muted-foreground capitalize">
                {serverStatus === 'checking' ? 'Checking...' : serverStatus}
              </span>
            </div>
          </div>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="mt-4 p-4 bg-muted/50 rounded-md border">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {/* Tags Filter */}
              <div>
                <label className="label">Tags</label>
                <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                  {availableTags.map(tag => (
                    <button
                      key={tag}
                      onClick={() => {
                        if (selectedTags.includes(tag)) {
                          setSelectedTags(selectedTags.filter(t => t !== tag))
                        } else {
                          setSelectedTags([...selectedTags, tag])
                        }
                      }}
                      className={`px-3 py-1 text-xs rounded-full border transition-colors ${selectedTags.includes(tag)
                        ? 'bg-accent text-accent-foreground border-accent'
                        : 'bg-background hover:bg-muted border-border'
                        }`}
                    >
                      {tag}
                    </button>
                  ))}
                  {availableTags.length === 0 && (
                    <span className="text-xs text-muted-foreground">No tags available</span>
                  )}
                </div>
              </div>

              {/* Date Created Filter */}
              <div>
                <label className="label">Date Created</label>
                <div className="space-y-2">
                  <input
                    type="date"
                    value={dateCreatedFrom}
                    onChange={(e) => setDateCreatedFrom(e.target.value)}
                    className="input w-full text-sm"
                    placeholder="From"
                  />
                  <input
                    type="date"
                    value={dateCreatedTo}
                    onChange={(e) => setDateCreatedTo(e.target.value)}
                    className="input w-full text-sm"
                    placeholder="To"
                  />
                </div>
              </div>

              {/* Date Modified Filter */}
              <div>
                <label className="label">Date Modified</label>
                <div className="space-y-2">
                  <input
                    type="date"
                    value={dateModifiedFrom}
                    onChange={(e) => setDateModifiedFrom(e.target.value)}
                    className="input w-full text-sm"
                    placeholder="From"
                  />
                  <input
                    type="date"
                    value={dateModifiedTo}
                    onChange={(e) => setDateModifiedTo(e.target.value)}
                    className="input w-full text-sm"
                    placeholder="To"
                  />
                </div>
              </div>
            </div>

            {/* Clear Filters */}
            <div className="mt-4 flex justify-end">
              <button
                onClick={() => {
                  setSelectedTags([])
                  setDateCreatedFrom('')
                  setDateCreatedTo('')
                  setDateModifiedFrom('')
                  setDateModifiedTo('')
                }}
                className="btn btn-outline btn-sm flex items-center"
              >
                <X className="h-4 w-4 mr-2" />
                Clear All Filters
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Notes List and Content - min-h-0 so this row gets bounded height and content can scroll */}
      <div className="flex-1 flex min-h-0 overflow-hidden relative">
        {/* Notes List */}
        {!isFullscreen && (
          <div className="w-80 min-h-0 border-r border-border flex flex-col animate-in slide-in-from-left duration-300">
            <div className="p-4 border-b border-border flex justify-between items-center">
              <h2 className="font-semibold flex items-center gap-2">Notes <span className="text-xs font-normal text-muted-foreground bg-muted px-1.5 py-0.5 rounded-full">{totalNotes}</span></h2>
              <div className="flex bg-muted/50 p-1 rounded-md">
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-1 rounded ${viewMode === 'list' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
                  title="List View"
                >
                  <List className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('tree')}
                  className={`p-1 rounded ${viewMode === 'tree' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
                  title="Tree View"
                >
                  <Network className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-auto">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-accent"></div>
                  <span className="ml-2 text-muted-foreground">
                    {serverStatus === 'starting' ? 'Starting server...' :
                      serverStatus === 'checking' ? 'Checking server status...' :
                        'Loading notes...'}
                  </span>
                </div>
              ) : (serverStatus === 'stopped' || serverStatus === 'starting') ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                      <span className="text-white font-bold text-sm">!</span>
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Advanced Memory Server Not Running</h3>
                  <p className="text-muted-foreground mb-4 max-w-md mx-auto">
                    The ADN MCP server is not running. Start it to access your knowledge base and notes.
                  </p>
                  {serverError && (
                    <div className="bg-red-500/10 border border-red-500/20 rounded-md p-3 mb-4 max-w-md mx-auto">
                      <p className="text-red-400 text-sm">{serverError}</p>
                    </div>
                  )}
                  <div className="space-y-2">
                    <button
                      onClick={async () => {
                        const ok = await startBridgeServer()
                        if (ok) loadNotes()
                      }}
                      disabled={serverStatus === 'starting'}
                      className="btn btn-primary"
                    >
                      {serverStatus === 'starting' ? 'Starting Bridge...' : 'Start Bridge'}
                    </button>
                    <button
                      onClick={async () => {
                        await checkServerStatus()
                        loadNotes()
                      }}
                      className="btn btn-outline"
                    >
                      Check Status
                    </button>
                  </div>
                  <div className="mt-4 p-3 bg-muted/50 rounded-md max-w-md mx-auto">
                    <p className="text-xs text-muted-foreground">
                      <strong>Start Bridge:</strong> Use the button above (via startup service on 10733).<br />
                      Or run <code className="bg-background px-1 py-0.5 rounded text-xs">node bridge-server.js</code> in the repo root.
                    </p>
                  </div>
                </div>
              ) : notes.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Notes Found</h3>
                  <p className="text-muted-foreground mb-4">
                    Your server is running but no notes were found. Create some notes to get started.
                  </p>
                  <button
                    onClick={() => loadNotes(1)}
                    className="btn btn-primary"
                  >
                    Refresh
                  </button>
                </div>
              ) : filteredNotes.length === 0 ? (
                <div className="text-center py-8">
                  <Search className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Matching Notes</h3>
                  <p className="text-muted-foreground mb-4">
                    No notes match your current search and filter criteria.
                  </p>
                  <button
                    onClick={() => {
                      setSearchQuery('')
                      setSelectedTags([])
                      setDateCreatedFrom('')
                      setDateCreatedTo('')
                      setDateModifiedFrom('')
                      setDateModifiedTo('')
                    }}
                    className="btn btn-outline"
                  >
                    Clear All Filters
                  </button>
                </div>
              ) : (
                <div className="flex-1 flex flex-col">
                  {viewMode === 'list' ? (
                    <div className="divide-y divide-border flex-1 overflow-auto">
                      {filteredNotes.map((note) => (
                        <div
                          key={note.id}
                          onClick={() => handleNoteSelect(note)}
                          className={`p-4 cursor-pointer hover:bg-muted/50 transition-colors ${selectedNote?.id === note.id ? 'bg-accent/10 border-l-4 border-accent' : ''
                            }`}
                        >
                          <h3 className="font-medium text-sm mb-2 line-clamp-2">{note.title}</h3>
                          <p className="text-xs text-muted-foreground mb-2 line-clamp-2">{note.content}</p>
                          <div className="flex items-center justify-between text-xs text-muted-foreground">
                            <span>{formatDate(note.modified)}</span>
                            <div className="flex items-center space-x-2">
                              <span>{note.wordCount} words</span>
                              <span>{note.connections} links</span>
                            </div>
                          </div>
                          {note.tags && note.tags.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {note.tags.slice(0, 3).map((tag) => (
                                <span key={tag} className="px-2 py-1 bg-accent/20 text-accent text-xs rounded-md">
                                  {tag}
                                </span>
                              ))}
                              {note.tags.length > 3 && (
                                <span className="text-xs text-muted-foreground">+{note.tags.length - 3}</span>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="py-2 flex-1 overflow-auto">
                      {renderTreeNodes(buildTree(filteredNotes))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="p-3 flex items-center justify-between border-t border-border bg-muted/20">
                <button
                  disabled={currentPage === 1}
                  onClick={() => loadNotes(currentPage - 1)}
                  className="btn btn-outline btn-sm p-1 disabled:opacity-50"
                  aria-label="Previous Page"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="text-xs text-muted-foreground">
                  Page <span className="text-foreground font-medium">{currentPage}</span> of {totalPages}
                </span>
                <button
                  disabled={currentPage === totalPages}
                  onClick={() => loadNotes(currentPage + 1)}
                  className="btn btn-outline btn-sm p-1 disabled:opacity-50"
                  aria-label="Next Page"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        )}

        {/* Note Content - min-h-0 so flex child can shrink and scroll */}
        <div className="flex-1 flex flex-col min-h-0">
          {selectedNote ? (
            <>
              {/* Note Header */}
              <div className="p-6 border-b border-border shrink-0">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h1 className="text-2xl font-bold mb-2">{selectedNote.title}</h1>
                    <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                      <span>Created: {formatDate(selectedNote.created)}</span>
                      <span>Modified: {formatDate(selectedNote.modified)}</span>
                      <span>{selectedNote.wordCount} words</span>
                    </div>
                    {selectedNote.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-3">
                        {selectedNote.tags.map((tag) => (
                          <span key={tag} className="px-3 py-1 bg-accent/20 text-accent text-sm rounded-full">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setIsFullscreen(!isFullscreen)}
                      className="p-2 rounded-md hover:bg-accent/10 text-accent transition-colors border border-accent/20"
                      title={isFullscreen ? "Exit Fullscreen" : "Fullscreen View"}
                    >
                      {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
                    </button>
                    <button className="p-2 rounded-md hover:bg-muted transition-colors" title="View">
                      <Eye className="h-4 w-4" />
                    </button>
                    <button className="p-2 rounded-md hover:bg-muted transition-colors" title="Export">
                      <Download className="h-4 w-4" />
                    </button>
                    <button className="p-2 rounded-md hover:bg-muted transition-colors" title="Share">
                      <Share className="h-4 w-4" />
                    </button>
                    <button className="p-2 rounded-md hover:bg-muted transition-colors" title="More">
                      <MoreVertical className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Note Content - fills remaining height and scrolls */}
              <div className="flex-1 min-h-0 overflow-auto p-6">
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">{selectedNote.content}</pre>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-center">
              <div>
                <FileText className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Select a Note</h3>
                <p className="text-muted-foreground">
                  Choose a note from the list to view its content and metadata.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
