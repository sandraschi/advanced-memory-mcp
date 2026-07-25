import type { LucideIcon } from "lucide-react";
import {
  Archive,
  BarChart2,
  BookOpen,
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

type NavItem = { name: string; href: string; icon: LucideIcon };
type NavGroup = { label?: string; items: NavItem[] };

const navGroups: NavGroup[] = [
  { items: [{ name: "Overview", href: "/", icon: Home }] },
  {
    label: "Notes & structure",
    items: [
      { name: "Note Vault", href: "/notes", icon: FileText },
      { name: "Knowledge Graph", href: "/dashboard/canvas", icon: Network },
      { name: "Recent Activity", href: "/recents", icon: Clock },
    ],
  },
  {
    label: "Search & indexing",
    items: [
      { name: "Semantic Search", href: "/research/deep", icon: Search },
      { name: "Vault sync", href: "/vault/sync", icon: RefreshCw },
      { name: "Vault stats", href: "/vault/stats", icon: BarChart2 },
    ],
  },
  {
    label: "Workspace & tools",
    items: [
      { name: "Project Workspace", href: "/projects", icon: Briefcase },
      { name: "Skill Lab", href: "/skills", icon: Code },
      { name: "Audio Memory", href: "/audio", icon: Volume2 },
      { name: "ZettelFlow", href: "/zettelflow", icon: Archive },
      { name: "Compiled Wiki", href: "/wiki", icon: BookOpen },
      { name: "Apps Hub", href: "/apps-hub", icon: Globe },
      { name: "Tests", href: "/tests", icon: FlaskConical },
      { name: "Settings", href: "/settings", icon: Settings },
    ],
  },
];

export default function Sidebar({ isCollapsed, onToggleCollapse }: SidebarProps) {
  return (
    <aside
      className={`glass-sidebar relative flex h-full min-h-0 shrink-0 flex-col overflow-hidden transition-all duration-300 ${isCollapsed ? "w-20" : "w-64"}`}
    >
      {/* Header */}
      <div className="flex h-20 shrink-0 items-center px-6">
        <div className="flex items-center gap-3 font-bold text-slate-100 flex-1">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center indigo-glow">
            <Database className="h-5 w-5 text-white" />
          </div>
          {!isCollapsed && (
            <span className="text-lg font-bold gradient-text text-indigo-100/90 whitespace-nowrap">
              Advanced Memory
            </span>
          )}
        </div>
        <button type="button" onClick={onToggleCollapse} className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.05] transition-all" title={isCollapsed ? "Expand" : "Collapse"}>
          {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      {/* Navigation — min-h-0 so flex-1 can shrink and overflow-y-auto scrolls */}
      <nav className="app-scroll min-h-0 flex-1 overflow-y-auto overflow-x-hidden p-3 space-y-1">
        {navGroups.map((group, gi) => (
          <div
            key={group.label ?? `g-${gi}`}
            className={gi > 0 ? "space-y-1 border-t border-white/[0.06] pt-3 mt-2" : "space-y-1"}
          >
            {!isCollapsed && group.label ? (
              <p className="px-2 pb-1 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                {group.label}
              </p>
            ) : null}
            {group.items.map((item) => (
              <NavLink
                key={item.href}
                to={item.href}
                title={isCollapsed ? item.name : undefined}
                className={({ isActive }) =>
                  `nav-item ${isActive ? "active" : ""} ${isCollapsed ? "justify-center" : "justify-start"}`
                }
              >
                <item.icon className="h-5 w-5 shrink-0" />
                {!isCollapsed && <span className="truncate">{item.name}</span>}
              </NavLink>
            ))}
          </div>
        ))}

        <div className="pt-4 mt-4 border-t border-white/[0.06] space-y-1">
          <NavLink
            to="/logs"
            title={isCollapsed ? "System log" : undefined}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""} ${isCollapsed ? "justify-center" : "justify-start"}`
            }
          >
            <Terminal className="h-5 w-5 shrink-0" />
            {!isCollapsed && <span>System log</span>}
          </NavLink>

          <NavLink
            to="/help"
            title={isCollapsed ? "Help" : undefined}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""} ${isCollapsed ? "justify-center" : "justify-start"}`
            }
          >
            <HelpCircle className="h-5 w-5 shrink-0" />
            {!isCollapsed && <span>Help</span>}
          </NavLink>
        </div>
      </nav>

    </aside>
  );
}
