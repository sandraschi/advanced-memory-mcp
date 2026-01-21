import { NavLink } from 'react-router-dom'
import {
  Home,
  Settings,
  HelpCircle,
  Terminal,
  X
} from 'lucide-react'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
  onOpenLogger: () => void
  onOpenHelp: () => void
}

export default function Sidebar({
  isOpen,
  onClose,
  onOpenLogger,
  onOpenHelp
}: SidebarProps) {
  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  const handleLoggerClick = (e: React.MouseEvent) => {
    e.preventDefault()
    onOpenLogger()
  }

  const handleHelpClick = (e: React.MouseEvent) => {
    e.preventDefault()
    onOpenHelp()
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose} />
        </div>
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-card border-r border-border transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:inset-0
      `}>
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex h-16 items-center justify-between px-4 border-b border-border">
            <h1 className="text-lg font-semibold">Advanced Memory</h1>
            <button
              onClick={onClose}
              className="lg:hidden p-2 rounded-md hover:bg-muted transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-2 py-4">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) => `
                  group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors
                  ${isActive
                    ? 'bg-accent text-accent-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                  }
                `}
                onClick={onClose}
              >
                <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                {item.name}
              </NavLink>
            ))}

            {/* Action buttons */}
            <div className="pt-4 border-t border-border">
              <button
                onClick={handleLoggerClick}
                className="w-full group flex items-center px-2 py-2 text-sm font-medium rounded-md text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
              >
                <Terminal className="mr-3 h-5 w-5 flex-shrink-0" />
                Logger
              </button>

              <button
                onClick={handleHelpClick}
                className="w-full group flex items-center px-2 py-2 text-sm font-medium rounded-md text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
              >
                <HelpCircle className="mr-3 h-5 w-5 flex-shrink-0" />
                Help
              </button>
            </div>
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-border">
            <div className="text-xs text-muted-foreground">
              <div className="font-medium">Advanced Memory MCP</div>
              <div>v1.2.0</div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
