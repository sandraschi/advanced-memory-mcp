import { useState } from 'react'
import Sidebar from './Sidebar'
import Topbar from './Topbar'
import MetadataSidebar from './MetadataSidebar'
import LoggerModal from '../modals/LoggerModal'
import HelpModal from '../modals/HelpModal'

interface LayoutProps {
  children: React.ReactNode
  showMetadataSidebar?: boolean
  selectedNoteMetadata?: any
  onMetadataExport?: (format: string, noteId: string) => Promise<void>
  onMetadataEdit?: () => void
  onMetadataDelete?: () => void
}

export default function Layout({
  children,
  showMetadataSidebar = false,
  selectedNoteMetadata,
  onMetadataExport,
  onMetadataEdit,
  onMetadataDelete
}: LayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [metadataSidebarOpen, setMetadataSidebarOpen] = useState(false)
  const [loggerOpen, setLoggerOpen] = useState(false)
  const [helpOpen, setHelpOpen] = useState(false)

  return (
    <div className="h-screen min-h-0 bg-[#020205] text-slate-50 font-inter selection:bg-indigo-500/30 flex overflow-hidden">
      {/* Left Sidebar */}
      <Sidebar
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        onOpenLogger={() => setLoggerOpen(true)}
        onOpenHelp={() => setHelpOpen(true)}
      />

      {/* Main Content Area - min-h-0 so flex child can shrink and fill viewport */}
      <div className="flex-1 flex flex-col min-w-0 min-h-0">
        {/* Topbar */}
        <Topbar
          onMenuClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          onLoggerClick={() => setLoggerOpen(true)}
          onHelpClick={() => setHelpOpen(true)}
          sidebarCollapsed={sidebarCollapsed}
        />

        {/* Page Content - fills remaining height so NoteViewer etc. can use full space */}
        <main className="flex-1 min-h-0 overflow-hidden flex flex-col">
          <div className="flex-1 min-h-0 flex flex-col">
            {children}
          </div>
        </main>
      </div>

      {/* Right Metadata Sidebar */}
      {showMetadataSidebar && (
        <MetadataSidebar
          isOpen={metadataSidebarOpen}
          onToggle={() => setMetadataSidebarOpen(!metadataSidebarOpen)}
          note={selectedNoteMetadata}
          onExport={onMetadataExport}
          onEdit={onMetadataEdit}
          onDelete={onMetadataDelete}
        />
      )}

      {/* Modals */}
      <LoggerModal
        isOpen={loggerOpen}
        onClose={() => setLoggerOpen(false)}
      />

      <HelpModal
        isOpen={helpOpen}
        onClose={() => setHelpOpen(false)}
      />
    </div>
  )
}
