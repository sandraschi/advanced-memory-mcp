import { useState, useEffect, useRef } from 'react'
import { X, Download, Trash2 } from 'lucide-react'

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
  const [logs, setLogs] = useState(mockLogs)
  const [autoScroll, setAutoScroll] = useState(true)
  const logContainerRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  const handleClearLogs = () => {
    setLogs([])
  }

  const handleDownloadLogs = () => {
    const logText = logs.map(log =>
      `[${log.timestamp}] ${log.level}: ${log.message}`
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
            <span className="text-sm text-muted-foreground">
              {logs.length} log entries
            </span>
          </div>

          <div className="flex space-x-2">
            <button
              onClick={handleDownloadLogs}
              className="btn btn-outline btn-sm"
              disabled={logs.length === 0}
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

        {/* Log content */}
        <div
          ref={logContainerRef}
          className="flex-1 overflow-auto bg-muted/50 rounded-md p-4 font-mono text-sm max-h-96"
        >
          {logs.length === 0 ? (
            <div className="text-muted-foreground text-center py-8">
              No log entries available
            </div>
          ) : (
            logs.map((log, index) => (
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
