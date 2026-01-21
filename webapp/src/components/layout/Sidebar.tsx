import { NavLink } from 'react-router-dom'
import {
  Home,
  Settings,
  HelpCircle,
  Terminal,
  Network,
  FileText,
  Code,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'

interface SidebarProps {
  isCollapsed: boolean
  onToggleCollapse: () => void
  onOpenLogger: () => void
  onOpenHelp: () => void
}

export default function Sidebar({
  isCollapsed,
  onToggleCollapse,
  onOpenLogger,
  onOpenHelp
}: SidebarProps) {
  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Notes', href: '/notes', icon: FileText },
    { name: 'Skills', href: '/skills', icon: Code },
    { name: 'Knowledge Graph', href: '/knowledge-graph', icon: Network },
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
    <div className={`
      bg-card border-r border-border flex flex-col transition-all duration-300 ease-in-out
      ${isCollapsed ? 'w-16' : 'w-64'}
    `}>
      {/* Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-border">
        {!isCollapsed && (
          <h1 className="text-lg font-semibold">Advanced Memory</h1>
        )}
        <button
          onClick={onToggleCollapse}
          className="p-2 rounded-md hover:bg-muted transition-colors ml-auto"
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? (
            <ChevronRight className="h-5 w-5" />
          ) : (
            <ChevronLeft className="h-5 w-5" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-2 py-4">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) => {
              const baseClasses = `group flex items-center ${isCollapsed ? 'justify-center px-2' : 'px-2'} py-2 text-sm font-medium rounded-md transition-colors`;
              const activeClasses = isActive
                ? 'bg-accent text-accent-foreground'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground';
              return `${baseClasses} ${activeClasses}`;
            }}
            title={isCollapsed ? item.name : undefined}
          >
            <item.icon className={`${isCollapsed ? '' : 'mr-3'} h-5 w-5 flex-shrink-0`} />
            {!isCollapsed && <span>{item.name}</span>}
          </NavLink>
        ))}

        {/* Action buttons */}
        <div className="pt-4 border-t border-border">
          <button
            onClick={handleLoggerClick}
            className={`w-full group flex items-center ${isCollapsed ? 'justify-center px-2' : 'px-2'} py-2 text-sm font-medium rounded-md text-muted-foreground hover:bg-muted hover:text-foreground transition-colors`}
            title={isCollapsed ? 'Logger' : undefined}
          >
            <Terminal className={`${isCollapsed ? '' : 'mr-3'} h-5 w-5 flex-shrink-0`} />
            {!isCollapsed && <span>Logger</span>}
          </button>

          <button
            onClick={handleHelpClick}
            className={`w-full group flex items-center ${isCollapsed ? 'justify-center px-2' : 'px-2'} py-2 text-sm font-medium rounded-md text-muted-foreground hover:bg-muted hover:text-foreground transition-colors`}
            title={isCollapsed ? 'Help' : undefined}
          >
            <HelpCircle className={`${isCollapsed ? '' : 'mr-3'} h-5 w-5 flex-shrink-0`} />
            {!isCollapsed && <span>Help</span>}
          </button>
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-border">
        {isCollapsed ? (
          <div className="text-center">
            <div className="text-xs text-muted-foreground font-medium">AM</div>
          </div>
        ) : (
          <div className="text-xs text-muted-foreground">
            <div className="font-medium">Advanced Memory MCP</div>
            <div>v1.3.0</div>
          </div>
        )}
      </div>
    </div>
  )
}
