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
  Wand2,
  Archive,
  Database
} from 'lucide-react'
import IntelligencePanel from './IntelligencePanel'
import { cn } from '@/utils/cn'; // Assuming utility exists, or use string template

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
    { name: 'Overview', href: '/', icon: Home },
    { name: 'Knowledge Graph', href: '/dashboard/canvas', icon: Network },
    { name: 'Semantic Search', href: '/research/deep', icon: Search },
    { name: 'Note Vault', href: '/notes', icon: FileText },
    { name: 'Recent Activity', href: '/recents', icon: Clock },
    { name: 'Project Workspace', href: '/projects', icon: Briefcase },
    { name: 'Skill Lab', href: '/skills', icon: Code },
    { name: 'Audio Memory', href: '/audio', icon: Volume2 },
    { name: 'ZettelFlow', href: '/zettelflow', icon: Archive },
    { name: 'Apps Hub', href: '/apps-hub', icon: Globe },
    { name: 'Tests', href: '/tests', icon: FlaskConical },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  return (
    <aside className={`glass-sidebar relative flex flex-col transition-all duration-300 ${isCollapsed ? 'w-20' : 'w-64'}`}>
      {/* Header */}
      <div className="flex h-20 items-center px-6">
        <div className="flex items-center gap-3 font-bold text-slate-100">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center indigo-glow">
            <Database className="h-5 w-5 text-white" />
          </div>
          {!isCollapsed && <span className="text-lg font-bold gradient-text text-indigo-100/90 whitespace-nowrap">Advanced Memory</span>}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-1 scrollbar-thin">
        {navigation.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            className={({ isActive }) =>
              `nav-item ${isActive ? 'active' : ''} ${isCollapsed ? 'justify-center' : 'justify-start'}`
            }
          >
            <item.icon className="h-5 w-5" />
            {!isCollapsed && <span className="truncate">{item.name}</span>}
          </NavLink>
        ))}

        <div className="pt-4 mt-4 border-t border-white/[0.06] space-y-1">
          <button
            onClick={(e) => { e.preventDefault(); onOpenLogger(); }}
            className={`nav-item w-full ${isCollapsed ? 'justify-center' : 'justify-start'}`}
          >
            <Terminal className="h-5 w-5" />
            {!isCollapsed && <span>Logger</span>}
          </button>

          <button
            onClick={(e) => { e.preventDefault(); onOpenHelp(); }}
            className={`nav-item w-full ${isCollapsed ? 'justify-center' : 'justify-start'}`}
          >
            <HelpCircle className="h-5 w-5" />
            {!isCollapsed && <span>Help</span>}
          </button>
        </div>
      </nav>

      {/* Footer / Toggle */}
      <div className="p-4 border-t border-white/[0.06]">
        <button
          onClick={onToggleCollapse}
          className="flex w-full items-center justify-center rounded-xl p-2.5 text-slate-400 hover:text-white hover:bg-white/[0.05] transition-all"
        >
          {isCollapsed ? <ChevronRight size={20} /> : <div className="flex items-center w-full"><ChevronLeft size={20} className="mr-3" /><span>Collapse</span></div>}
        </button>
      </div>
    </aside>
  )
}
