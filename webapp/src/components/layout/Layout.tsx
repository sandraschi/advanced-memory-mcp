import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Topbar from './Topbar'
import LoggerModal from './LoggerModal'
import HelpModal from './HelpModal'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [loggerOpen, setLoggerOpen] = useState(false)
  const [helpOpen, setHelpOpen] = useState(false)

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onOpenLogger={() => setLoggerOpen(true)}
        onOpenHelp={() => setHelpOpen(true)}
      />

      {/* Topbar */}
      <Topbar
        onMenuClick={() => setSidebarOpen(true)}
        onLoggerClick={() => setLoggerOpen(true)}
        onHelpClick={() => setHelpOpen(true)}
      />

      {/* Main content */}
      <main className="lg:pl-64">
        <div className="px-4 py-8 lg:px-8">
          {children}
        </div>
      </main>

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
