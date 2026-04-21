import {
  Archive,
  BarChart2,
  Briefcase,
  ChevronLeft,
  ChevronRight,
  Clock,
  Code,
  Database,
  FileText,
  FlaskConical,
  Globe,
  HelpCircle,
  Home,
  Network,
  RefreshCw,
  Search,
  Settings,
  Terminal,
  Volume2,
} from "lucide-react";
import { NavLink } from "react-router-dom";
interface SidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export default function Sidebar({ isCollapsed, onToggleCollapse }: SidebarProps) {
  const navigation = [
    { name: "Overview", href: "/", icon: Home },
    { name: "Knowledge Graph", href: "/dashboard/canvas", icon: Network },
    { name: "Semantic Search", href: "/research/deep", icon: Search },
    { name: "Note Vault", href: "/notes", icon: FileText },
    { name: "Recent Activity", href: "/recents", icon: Clock },
    { name: "Project Workspace", href: "/projects", icon: Briefcase },
    { name: "Vault sync", href: "/vault/sync", icon: RefreshCw },
    { name: "Vault stats", href: "/vault/stats", icon: BarChart2 },
    { name: "Skill Lab", href: "/skills", icon: Code },
    { name: "Audio Memory", href: "/audio", icon: Volume2 },
    { name: "ZettelFlow", href: "/zettelflow", icon: Archive },
    { name: "Apps Hub", href: "/apps-hub", icon: Globe },
    { name: "Tests", href: "/tests", icon: FlaskConical },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <aside
      className={`glass-sidebar relative flex h-full min-h-0 shrink-0 flex-col overflow-hidden transition-all duration-300 ${isCollapsed ? "w-20" : "w-64"}`}
    >
      {/* Header */}
      <div className="flex h-20 shrink-0 items-center px-6">
        <div className="flex items-center gap-3 font-bold text-slate-100">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center indigo-glow">
            <Database className="h-5 w-5 text-white" />
          </div>
          {!isCollapsed && (
            <span className="text-lg font-bold gradient-text text-indigo-100/90 whitespace-nowrap">
              Advanced Memory
            </span>
          )}
        </div>
      </div>

      {/* Navigation — min-h-0 so flex-1 can shrink and overflow-y-auto scrolls */}
      <nav className="app-scroll min-h-0 flex-1 overflow-y-auto overflow-x-hidden p-3 space-y-1">
        {navigation.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""} ${isCollapsed ? "justify-center" : "justify-start"}`
            }
          >
            <item.icon className="h-5 w-5" />
            {!isCollapsed && <span className="truncate">{item.name}</span>}
          </NavLink>
        ))}

        <div className="pt-4 mt-4 border-t border-white/[0.06] space-y-1">
          <NavLink
            to="/logs"
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""} ${isCollapsed ? "justify-center" : "justify-start"}`
            }
          >
            <Terminal className="h-5 w-5" />
            {!isCollapsed && <span>System log</span>}
          </NavLink>

          <NavLink
            to="/help"
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""} ${isCollapsed ? "justify-center" : "justify-start"}`
            }
          >
            <HelpCircle className="h-5 w-5" />
            {!isCollapsed && <span>Help</span>}
          </NavLink>
        </div>
      </nav>

      {/* Footer / Toggle */}
      <div className="shrink-0 border-t border-white/[0.06] p-4">
        <button
          onClick={onToggleCollapse}
          className="flex w-full items-center justify-center rounded-xl p-2.5 text-slate-400 hover:text-white hover:bg-white/[0.05] transition-all"
        >
          {isCollapsed ? (
            <ChevronRight size={20} />
          ) : (
            <div className="flex items-center w-full">
              <ChevronLeft size={20} className="mr-3" />
              <span>Collapse</span>
            </div>
          )}
        </button>
      </div>
    </aside>
  );
}
