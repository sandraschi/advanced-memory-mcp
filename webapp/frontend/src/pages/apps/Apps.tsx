import {
  Activity,
  BookOpen,
  Bot,
  ExternalLink,
  Film,
  HardDrive,
  LayoutGrid,
  Loader2,
  Monitor,
  Shield,
  Smartphone,
} from "lucide-react";
import { useEffect, useState } from "react";
import { apiService } from "../../services/api";

interface AppConfig {
  id: string;
  name: string;
  description: string;
  port: number;
  icon: any;
  repo: string;
}

const APPS: AppConfig[] = [
  {
    id: "plex",
    name: "Plex MCP",
    description: "Media server orchestration, collections management, and playback control.",
    port: 10741,
    icon: Film,
    repo: "plex-mcp",
  },
  {
    id: "calibre",
    name: "Calibre MCP",
    description: "Digital library management, e-book conversion, and metadata enrichment.",
    port: 10721,
    icon: BookOpen,
    repo: "calibre-mcp",
  },
  {
    id: "filesystem",
    name: "Filesystem MCP",
    description: "Agentic file operations, project organization, and system monitoring.",
    port: 10743,
    icon: HardDrive,
    repo: "filesystem-mcp",
  },
  {
    id: "virtualization",
    name: "Virtualization MCP",
    description: "Docker container lifecycle, compose orchestration, and infra management.",
    port: 10700,
    icon: Monitor,
    repo: "virtualization-mcp",
  },
  {
    id: "devices",
    name: "Devices MCP",
    description: "iOS/macOS ecosystem integration and unified device communication.",
    port: 10716,
    icon: Smartphone,
    repo: "devices-mcp",
  },
  {
    id: "ring",
    name: "Ring MCP",
    description: "Security camera monitoring, event analysis, and home safety automation.",
    port: 10728,
    icon: Shield,
    repo: "ring-mcp",
  },
  {
    id: "robotics",
    name: "Robotics MCP",
    description: "Unitree humanoid control, ROS bridge, and virtual robotics synchronization.",
    port: 10706,
    icon: Bot,
    repo: "robotics-mcp",
  },
];

export default function Apps() {
  const [health, setHealth] = useState<Record<number, "online" | "offline" | "checking">>({});

  const checkHealth = async (port: number) => {
    setHealth((prev) => ({ ...prev, [port]: "checking" }));
    try {
      const response = await apiService.checkAppHealth(port);
      setHealth((prev) => ({ ...prev, [port]: response.success ? "online" : "offline" }));
    } catch {
      setHealth((prev) => ({ ...prev, [port]: "offline" }));
    }
  };

  useEffect(() => {
    // Initial health check
    APPS.forEach((app) => checkHealth(app.port));
  }, []);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-3">
          <LayoutGrid className="h-8 w-8 text-accent" />
          <h1 className="text-3xl font-bold tracking-tight">Sibling Webapps</h1>
        </div>
        <button
          onClick={() => APPS.forEach((app) => checkHealth(app.port))}
          className="btn btn-secondary flex items-center space-x-2 py-2"
        >
          <Activity className="h-4 w-4" />
          <span>Refresh Status</span>
        </button>
      </div>

      <p className="text-muted-foreground max-w-2xl">
        Centralized launchpad for the entire MCP ecosystem. Each specialized agent-server exposes
        its own web interface on distinct ports for parallel operation and distributed intelligence.
      </p>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {APPS.map((app) => {
          const status = health[app.port] || "checking";
          const AppIcon = app.icon;

          return (
            <div
              key={app.id}
              className="card group hover:shadow-glow transition-all flex flex-col h-full border border-white/5 hover:border-accent/30 overflow-hidden"
            >
              <div className="p-6 flex-1 flex flex-col">
                <div className="flex items-start justify-between mb-4">
                  <div
                    className={`p-3 rounded-xl ${
                      status === "online"
                        ? "bg-accent/10 text-accent"
                        : "bg-muted text-muted-foreground"
                    }`}
                  >
                    <AppIcon className="h-8 w-8" />
                  </div>
                  <div className="flex items-center space-x-2 bg-black/20 px-3 py-1 rounded-full border border-white/5">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        status === "online"
                          ? "bg-green-500 animate-pulse"
                          : status === "checking"
                            ? "bg-yellow-500 animate-bounce"
                            : "bg-red-500"
                      }`}
                    />
                    <span className="text-[10px] font-bold tracking-widest uppercase opacity-70">
                      {status === "online"
                        ? "Online"
                        : status === "checking"
                          ? "Checking"
                          : "Offline"}
                    </span>
                  </div>
                </div>

                <h3 className="text-xl font-bold mb-2 group-hover:text-accent transition-colors">
                  {app.name}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                  {app.description}
                </p>
                <div className="mt-4 pt-4 border-t border-white/5 flex items-center justify-between text-[10px] font-mono opacity-50">
                  <span>PORT: {app.port}</span>
                  <span>{app.repo}</span>
                </div>
              </div>

              <a
                href={`http://localhost:${app.port}`}
                target="_blank"
                rel="noopener noreferrer"
                className={`flex items-center justify-center space-x-2 py-4 px-6 font-bold tracking-tight transition-all ${
                  status === "online"
                    ? "bg-accent/20 text-accent hover:bg-accent text-accent-foreground"
                    : "bg-muted/50 text-muted-foreground cursor-not-allowed grayscale"
                }`}
                onClick={(e) => {
                  if (status !== "online") e.preventDefault();
                }}
              >
                <span>Launch App</span>
                {status === "checking" ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <ExternalLink className="h-4 w-4" />
                )}
              </a>
            </div>
          );
        })}
      </div>

      <div className="card p-8 bg-gold/5 border border-gold/10 rounded-2xl">
        <div className="flex items-start space-x-4">
          <Activity className="h-6 w-6 text-gold mt-1" />
          <div>
            <h3 className="text-lg font-bold text-gold mb-2">Network Topology Note</h3>
            <p className="text-sm text-gold/80 leading-relaxed max-w-3xl">
              These sibling webapps share a FastMCP-style tool surface. Each server keeps its own
              SQLite database and Markdown vault under the same authorization rules. When a tool
              needs data from another server, it uses the documented{" "}
              <code className="text-gold">inter_server</code> MCP calls instead of sharing files
              directly.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
