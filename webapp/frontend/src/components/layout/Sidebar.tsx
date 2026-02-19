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
  ChevronRight,
  BookOpen,
  Briefcase,
  Clock,
  Store,
  FlaskConical,
  Volume2,
  Activity,
  Search,
  Globe,
  Wand2
} from 'lucide-react'
import IntelligencePanel from './IntelligencePanel'

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
    { name: 'Recent Notes', href: '/recents', icon: Clock },
    { name: 'Notes', href: '/notes', icon: FileText },
    { name: 'Zettelkasten', href: '/dashboard/zettelkasten', icon: BookOpen },
    { name: 'Graph Canvas', href: '/dashboard/canvas', icon: Network },
    { name: 'Audio Hub', href: '/audio', icon: Volume2 },
    { name: 'Checkpoints', href: '/checkpoints', icon: Activity },
    { name: 'Projects', href: '/projects', icon: Briefcase },
    { name: 'Skills', href: '/skills', icon: Code },
    { name: 'Skill Studio', href: '/skills/studio', icon: Wand2 },
    { name: 'Skill Research', href: '/skills/research', icon: BookOpen },
    { name: 'Marketplace', href: '/marketplace', icon: Store },
    { name: 'Research Lab', href: '/research', icon: FlaskConical },
    { name: 'Deep Search', href: '/research/deep', icon: Search },
    { name: 'Chat', href: '/chat', icon: Wand2 },
    { name: 'Apps Hub', href: '/apps-hub', icon: Globe },
    { name: 'Control Room', href: '/control-room', icon: Terminal },
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
    <div className={`flex flex-col h-full bg-card border-r border-border transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-64'}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        {!isCollapsed && <span className="text-lg font-bold truncate">Advanced Memory</span>}
        <button
          onClick={onToggleCollapse}
          className="p-1 rounded-md hover:bg-muted transition-colors"
          title={isCollapsed ? 'Expand' : 'Collapse'}
        >
          {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto overflow-x-hidden p-2 space-y-1 scrollbar-thin">
        {navigation.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center ${isCollapsed ? 'justify-center px-2' : 'px-3'} py-2 text-sm font-medium rounded-md transition-colors ${isActive
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              }`
            }
            title={isCollapsed ? item.name : undefined}
          >
            <item.icon className={`${isCollapsed ? '' : 'mr-3'} h-5 w-5 flex-shrink-0`} />
            {!isCollapsed && <span className="truncate">{item.name}</span>}
          </NavLink>
        ))}

        <div className="pt-4 mt-4 border-t border-border space-y-1">
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

      {/* Footer / Intelligence Panel */}
      <div className="border-t border-border">
        {isCollapsed ? (
          <div className="p-4 text-center">
            <div className="text-xs text-muted-foreground font-medium">AM</div>
          </div>
        ) : (
          <IntelligencePanel />
        )}
      </div>
    </div>
  )
}
