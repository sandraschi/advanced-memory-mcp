import { useState, useEffect } from 'react'
import { Search, FileText, Eye, Download, Share, MoreVertical, Filter, X } from 'lucide-react'
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

  // Filter state
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [dateCreatedFrom, setDateCreatedFrom] = useState('')
  const [dateCreatedTo, setDateCreatedTo] = useState('')
  const [dateModifiedFrom, setDateModifiedFrom] = useState('')
  const [dateModifiedTo, setDateModifiedTo] = useState('')
  const [availableTags, setAvailableTags] = useState<string[]>([])

  // Mock data for demonstration - will be replaced with real API calls
  const mockNotes: Note[] = [
    {
      id: '1',
      title: 'Brain Tumor Treatment Research',
      content: `# Brain Tumor Treatment Research

## Overview
This research covers the latest developments in glioblastoma treatment protocols, focusing on multimodal approaches that combine traditional and novel therapies.

## Current Treatment Landscape

### Surgical Approaches
- **Gross Total Resection**: Complete removal of visible tumor mass
- **Awake Craniotomy**: Maximizes tumor removal while preserving function
- **Fluorescence-guided Surgery**: Using 5-ALA for better tumor visualization

### Radiation Therapy
- **Standard External Beam Radiation**: 60 Gy over 6 weeks post-surgery
- **Stereotactic Radiosurgery**: For small recurrent tumors
- **Proton Beam Therapy**: Reduced damage to healthy brain tissue

## Clinical Trials Status
- Phase III trials for novel immunotherapy combinations
- Early phase studies for targeted molecular therapies
- Long-term survival data analysis ongoing

## Conclusion
The field is rapidly evolving with significant improvements in survival rates and quality of life.`,
      tags: ['medical', 'research', 'brain-tumor', 'treatment'],
      created: '2026-01-20 14:30:00',
      modified: '2026-01-20 15:45:00',
      wordCount: 247,
      connections: 8
    },
    {
      id: '2',
      title: 'Quantum Computing Fundamentals',
      content: `# Quantum Computing Fundamentals

## Core Concepts

### Qubits
Unlike classical bits that can be in state 0 or 1, qubits can exist in superposition:
- **Superposition**: |ψ⟩ = α|0⟩ + β|1⟩
- **Measurement**: Collapses superposition to definite state
- **Entanglement**: Quantum correlation between particles

### Quantum Gates
- **Pauli Gates**: X, Y, Z rotations
- **Hadamard Gate**: Creates superposition
- **CNOT Gate**: Entangling operation

## Key Algorithms
- **Shor's Algorithm**: Factors large numbers efficiently
- **Grover's Algorithm**: Quadratic speedup for search

## Hardware Platforms
- **Superconducting Qubits**: IBM, Google (scalable, fast)
- **Trapped Ions**: IonQ, Honeywell (high fidelity)
- **Photonic**: Xanadu (room temperature)

## Current Status
- **NISQ Era**: Noisy Intermediate-Scale Quantum devices
- **Quantum Advantage**: Demonstrated for specific problems
- **Error Correction**: Surface code approach emerging`,
      tags: ['quantum', 'computing', 'physics', 'technology'],
      created: '2026-01-19 09:15:00',
      modified: '2026-01-19 11:20:00',
      wordCount: 178,
      connections: 12
    },
    {
      id: '3',
      title: 'Machine Learning Algorithms',
      content: `# Machine Learning Algorithms Overview

## Supervised Learning

### Linear Models
- **Linear Regression**: Predict continuous values
- **Logistic Regression**: Binary classification
- **Support Vector Machines**: Maximum margin classification

### Tree-Based Methods
- **Decision Trees**: Interpretable hierarchical models
- **Random Forest**: Ensemble of decision trees
- **XGBoost**: Optimized gradient boosting

### Neural Networks
- **Feedforward Networks**: Universal function approximators
- **CNN**: Image processing
- **RNN**: Sequential data
- **Transformers**: Attention-based architectures

## Unsupervised Learning

### Clustering
- **K-Means**: Centroid-based clustering
- **DBSCAN**: Density-based clustering
- **Gaussian Mixture Models**: Probabilistic clustering

### Dimensionality Reduction
- **PCA**: Linear projection
- **t-SNE**: Nonlinear embedding for visualization

## Reinforcement Learning
- **Q-Learning**: Value-based learning
- **Policy Gradient**: Direct policy optimization
- **PPO**: Stable policy updates

## Key Metrics
- **Accuracy, Precision, Recall, F1-Score**
- **MSE, MAE, R²** for regression
- **AUC-ROC** for classification`,
      tags: ['ml', 'ai', 'algorithms', 'data-science'],
      created: '2026-01-18 16:45:00',
      modified: '2026-01-18 18:30:00',
      wordCount: 234,
      connections: 15
    },
    {
      id: '4',
      title: 'Sustainable Energy Solutions',
      content: `# Sustainable Energy Solutions

## Renewable Energy Technologies

### Solar Energy
- **Photovoltaic Systems**: Direct conversion of sunlight to electricity
- **Concentrated Solar Power**: Thermal energy storage and generation
- **Building-Integrated PV**: Architectural integration
- **Floating Solar Farms**: Utilize water surfaces

### Wind Energy
- **Onshore Wind Farms**: Cost-effective large-scale generation
- **Offshore Wind**: Higher capacity factors, less visual impact
- **Distributed Wind**: Small-scale urban installations
- **Vertical Axis Turbines**: Alternative design for urban environments

### Hydroelectric Power
- **Large-Scale Dams**: High capacity, long-term storage
- **Run-of-River Systems**: Minimal environmental impact
- **Pumped Storage**: Energy storage and grid stabilization
- **Micro-Hydro**: Small-scale community solutions

## Energy Storage Technologies

### Battery Storage
- **Lithium-Ion Batteries**: Current standard technology
- **Solid-State Batteries**: Next-generation chemistry
- **Flow Batteries**: Scalable long-duration storage
- **Sodium-Ion Batteries**: Lower-cost alternative

### Alternative Storage
- **Compressed Air Energy Storage**: Large-scale grid storage
- **Flywheel Energy Storage**: High-power, short-duration
- **Hydrogen Storage**: Long-term seasonal storage
- **Thermal Energy Storage**: Heat/cold storage systems

## Grid Integration and Smart Systems

### Smart Grid Technologies
- **Demand Response**: Dynamic load management
- **Microgrids**: Localized energy systems
- **Vehicle-to-Grid**: Electric vehicle integration
- **Energy Management Systems**: Optimization platforms

### Policy and Economics
- **Feed-in Tariffs**: Guaranteed payments for renewable generation
- **Net Metering**: Credit systems for excess generation
- **Carbon Pricing**: Economic incentives for emissions reduction
- **Green Bonds**: Financing sustainable energy projects

## Environmental Impact Assessment

### Life Cycle Analysis
- **Manufacturing Impact**: Resource extraction and processing
- **Operational Emissions**: Direct and indirect emissions
- **End-of-Life Management**: Recycling and disposal
- **Carbon Footprint**: Full lifecycle emissions

### Ecosystem Considerations
- **Land Use**: Space requirements and competing uses
- **Biodiversity Impact**: Effects on local ecosystems
- **Water Usage**: Consumption in energy production
- **Waste Management**: Byproducts and disposal

## Future Trends and Challenges

### Emerging Technologies
- **Advanced Nuclear**: Small modular reactors
- **Fusion Energy**: Theoretical unlimited clean energy
- **Ocean Energy**: Tidal and wave power systems
- **Artificial Photosynthesis**: Direct solar fuel production

### Challenges
- **Energy Storage**: Cost and efficiency improvements needed
- **Grid Modernization**: Infrastructure upgrades required
- **Policy Stability**: Consistent regulatory frameworks
- **Public Acceptance**: Community engagement and education

## Global Implementation

### Regional Examples
- **Europe**: Leading in wind and solar adoption
- **China**: Rapid deployment of renewable capacity
- **United States**: Diverse regional approaches
- **Developing Nations**: Leapfrogging traditional infrastructure

### International Cooperation
- **Paris Agreement**: Global climate commitments
- **IRENA**: International renewable energy cooperation
- **Technology Transfer**: Knowledge sharing between nations
- **Financial Mechanisms**: Green Climate Fund initiatives

## Conclusion
Sustainable energy transition requires coordinated efforts across technology, policy, and society. The current momentum in renewable energy deployment, combined with rapid cost reductions, positions us well for achieving climate goals while meeting growing energy demands.`,
      tags: ['energy', 'sustainability', 'renewable', 'climate'],
      created: '2026-01-17 13:20:00',
      modified: '2026-01-17 14:55:00',
      wordCount: 1876,
      connections: 6
    },
    {
      id: '5',
      title: 'Ancient Philosophy Notes',
      content: `# Ancient Greek Philosophy

## Pre-Socratic Philosophers
- **Thales**: Everything is made of water
- **Anaximander**: The boundless (apeiron) as fundamental substance
- **Heraclitus**: "Everything flows" - constant change
- **Parmenides**: Only being exists, change is illusion

## The Classical Period
### Socrates
- **Socratic Method**: Questioning to stimulate critical thinking
- **Ethical Focus**: "Know thyself" and virtue ethics

### Plato
- **Theory of Forms**: Ideal forms exist in a separate realm
- **The Allegory of the Cave**: Reality vs. perception
- **The Republic**: Ideal state and justice

### Aristotle
- **Empirical Method**: Observation and classification
- **The Golden Mean**: Virtue as the mean between extremes
- **Four Causes**: Material, formal, efficient, final

## Hellenistic Philosophy
### Stoicism
- **Zeno of Citium**: Founder of Stoicism
- **Marcus Aurelius**: Meditations as practical philosophy
- **Key Concepts**: Virtue, acceptance

### Epicureanism
- **Epicurus**: "Death is nothing to us"
- **Hedonic Calculus**: Pleasure as the highest good

## Major Themes
- **Metaphysics**: Nature of reality and change
- **Epistemology**: What can we truly know?
- **Ethics**: The good life and virtue

## Legacy
- Foundation of Western philosophy
- Influenced medieval, renaissance, and modern thought
- Contemporary relevance in ethics and education`,
      tags: ['philosophy', 'ancient', 'greek', 'history'],
      created: '2026-01-16 10:30:00',
      modified: '2026-01-16 12:15:00',
      wordCount: 267,
      connections: 9
    }
  ]

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

  const loadNotes = async () => {
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
          const response = await apiService.getNotes()
          if (response.success && response.data?.notes && response.data.notes.length > 0) {
            const notesData = response.data.notes
            setNotes(notesData)
            setFilteredNotes(notesData)

            // Extract available tags
            const allTags = new Set<string>()
            notesData.forEach(note => {
              note.tags.forEach(tag => allTags.add(tag))
            })
            setAvailableTags(Array.from(allTags).sort())
            setIsLoading(false)
            return
          }
        } catch (apiError) {
          console.log('API call failed, will use mock data:', apiError)
        }
      }

      // Fall back to mock data
      console.log('Using mock data for demonstration')
      setTimeout(() => {
        setNotes(mockNotes)
        setFilteredNotes(mockNotes)

        // Extract tags from mock data
        const allTags = new Set<string>()
        mockNotes.forEach(note => {
          note.tags.forEach(tag => allTags.add(tag))
        })
        setAvailableTags(Array.from(allTags).sort())
        setIsLoading(false)
      }, 500)
    } catch (error) {
      console.error('Failed to load notes, using mock data:', error)
      // Show mock data as final fallback
      setTimeout(() => {
        setNotes(mockNotes)
        setFilteredNotes(mockNotes)

        // Extract tags from mock data
        const allTags = new Set<string>()
        mockNotes.forEach(note => {
          note.tags.forEach(tag => allTags.add(tag))
        })
        setAvailableTags(Array.from(allTags).sort())
        setIsLoading(false)
      }, 500)
    }
  }

  useEffect(() => {
    loadNotes()

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

  return (
    <div className="h-full flex flex-col">
      {/* Search Header */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center space-x-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <input
              type="text"
              placeholder="Search notes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
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
            <div className="text-sm text-muted-foreground">
              {filteredNotes.length} of {notes.length} notes
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${serverStatus === 'running' ? 'bg-green-500' :
                serverStatus === 'starting' ? 'bg-yellow-500 animate-pulse' :
                  'bg-red-500'
                }`}></div>
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

      {/* Notes List and Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Notes List */}
        <div className="w-80 border-r border-border flex flex-col">
          <div className="p-4 border-b border-border">
            <h2 className="font-semibold">Notes</h2>
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
                  onClick={loadNotes}
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
              <div className="divide-y divide-border">
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
                    {note.tags.length > 0 && (
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
            )}
          </div>
        </div>

        {/* Note Content */}
        <div className="flex-1 flex flex-col">
          {selectedNote ? (
            <>
              {/* Note Header */}
              <div className="p-6 border-b border-border">
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

              {/* Note Content */}
              <div className="flex-1 overflow-auto p-6">
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
