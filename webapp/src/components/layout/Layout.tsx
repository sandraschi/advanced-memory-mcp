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
    <div className="min-h-screen bg-background text-foreground flex">
      {/* Left Sidebar */}
      <Sidebar
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        onOpenLogger={() => setLoggerOpen(true)}
        onOpenHelp={() => setHelpOpen(true)}
      />

      {/* Main Content Area - no ml; sidebar already reserves space in flex flow */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Topbar */}
        <Topbar
          onMenuClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          onLoggerClick={() => setLoggerOpen(true)}
          onHelpClick={() => setHelpOpen(true)}
          sidebarCollapsed={sidebarCollapsed}
        />

        {/* Page Content */}
        <main className="flex-1 overflow-hidden">
          <div className="h-full">
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
