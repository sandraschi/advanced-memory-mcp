import {
  Activity,
  AlertTriangle,
  Book,
  Brain,
  FolderSync,
  Globe,
  RefreshCw,
  Search,
  Terminal,
  TrendingUp,
  Zap,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiService, type WatchStatusPayload } from "../../services/api";
import ResearchCard from "./ResearchCard";
import SkillCard from "./SkillCard";

function timeAgo(iso: string | null): string {
  if (!iso) return "never";
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return iso;
  const seconds = Math.max(0, Math.floor((Date.now() - then) / 1000));
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  return `${(seconds / 3600).toFixed(1)}h ago`;
}

interface ResearchItem {
  id: string;
  title: string;
  sources: string[];
  status: "completed" | "in_progress" | "failed";
  timestamp: string;
}

interface SkillItem {
  id: string;
  title: string;
  description: string;
  sources: number;
  created: string;
}

export default function Dashboard() {
  const [recentResearch, setRecentResearch] = useState<ResearchItem[]>([]);
  const [recentSkills, setRecentSkills] = useState<SkillItem[]>([]);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [watchStatus, setWatchStatus] = useState<WatchStatusPayload | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadData = async () => {
    setIsRefreshing(true);
    try {
      const [researchResponse, skillsResponse, statusResponse, watchResponse] = await Promise.all([
        apiService.getRecentResearch(),
        apiService.getRecentSkills(),
        apiService.getSystemStatus(),
        apiService.getWatchStatus(),
      ]);

      if (researchResponse?.success) {
        setRecentResearch(researchResponse.data || []);
      }

      if (skillsResponse?.success) {
        setRecentSkills(skillsResponse.data || []);
      }

      if (statusResponse?.success) {
        setSystemStatus(statusResponse.data);
      }

      if (watchResponse?.success && watchResponse.data) {
        setWatchStatus(watchResponse.data);
      }
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
    // Index sync state can go stale between full dashboard reloads; poll it on
    // its own so a wedged watcher shows up here without a manual refresh.
    const t = setInterval(async () => {
      const res = await apiService.getWatchStatus();
      if (res.success && res.data) setWatchStatus(res.data);
    }, 30_000);
    return () => clearInterval(t);
  }, []);

  const handleRefresh = () => {
    loadData();
  };

  return (
    <div className="space-y-8 page-enter overflow-y-auto h-full pr-2 scrollbar-thin scrollbar-thumb-white/10">
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-900/40 via-black to-black border border-white/10 p-8 mb-8 indigo-glow">
        <div className="relative z-10 max-w-2xl">
          <h1 className="text-4xl font-bold tracking-tight text-white mb-4">
            Notes, research, and retrieval
          </h1>
          <p className="text-lg text-indigo-200/70 mb-6 max-w-2xl">
            Work in Markdown on your machine, find material quickly with full-text and meaning-based
            search, and link notes when connections help you move between topics. Turn stable
            checklists and write-ups into skills your assistant can load.
          </p>
          <div className="flex gap-4 flex-wrap">
            <Link to="/notes" className="px-6 py-2.5 rounded-xl bg-indigo-600 text-white font-medium hover:bg-indigo-500 transition-all shadow-lg shadow-indigo-500/20 active:scale-95">
              Browse Notes
            </Link>
            <Link to="/skills" className="px-6 py-2.5 rounded-xl bg-white/5 text-slate-300 font-medium border border-white/10 hover:bg-white/10 transition-all active:scale-95">
              View Skills
            </Link>
            <Link to="/recents" className="px-6 py-2.5 rounded-xl bg-white/5 text-slate-300 font-medium border border-white/10 hover:bg-white/10 transition-all active:scale-95">
              Recent Activity
            </Link>
          </div>
        </div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/20 blur-[120px] rounded-full -mr-20 -mt-20"></div>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Link to="/notes" className="block">
          <div className="glass-card p-6 text-center cursor-pointer group h-full">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Search className="h-6 w-6 text-indigo-400" />
            </div>
            <h3 className="font-bold text-white mb-1">Notes</h3>
            <p className="text-xs text-slate-500">Browse and search all notes</p>
          </div>
        </Link>

        <Link to="/skills" className="block">
          <div className="glass-card p-6 text-center cursor-pointer group h-full">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Zap className="h-6 w-6 text-indigo-400" />
            </div>
            <h3 className="font-bold text-white mb-1">Skills</h3>
            <p className="text-xs text-slate-500">Expert skill library</p>
          </div>
        </Link>

        <Link to="/recents" className="block">
          <div className="glass-card p-6 text-center cursor-pointer group h-full">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Book className="h-6 w-6 text-indigo-400" />
            </div>
            <h3 className="font-bold text-white mb-1">Recents</h3>
            <p className="text-xs text-slate-500">Recent activity feed</p>
          </div>
        </Link>

        <Link to="/dashboard/canvas" className="block">
          <div className="glass-card p-6 text-center cursor-pointer group h-full">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Brain className="h-6 w-6 text-indigo-400" />
            </div>
            <h3 className="font-bold text-white mb-1">Knowledge Map</h3>
            <p className="text-xs text-slate-500">Graph-based visualization</p>
          </div>
        </Link>
      </div>

      {/* Recent Activity */}
      <div className="grid gap-8 lg:grid-cols-7">
        <div className="col-span-4 glass-card p-6">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-indigo-500/10">
                <TrendingUp className="h-4 w-4 text-indigo-400" />
              </div>
              <h2 className="text-lg font-bold tracking-tight text-white">Recent research</h2>
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                aria-label="Refresh"
                className="p-1.5 rounded-lg hover:bg-white/5 text-slate-500 hover:text-white transition-all disabled:opacity-30"
              >
                <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
              </button>
            </div>
          </div>

          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 animate-pulse">
              <RefreshCw className="h-8 w-8 animate-spin text-indigo-500 mb-4" />
              <span className="text-sm font-medium text-slate-500">Loading...</span>
            </div>
          ) : (
            <div className="space-y-4">
              {recentResearch.length === 0 ? (
                <div className="text-center py-12 bg-white/[0.02] border border-dashed border-white/10 rounded-2xl">
                  <p className="text-sm text-slate-500">No research entries yet.</p>
                </div>
              ) : (
                recentResearch.map((research) => (
                  <ResearchCard key={research.id} research={research} />
                ))
              )}
            </div>
          )}
        </div>

        <div className="col-span-3 glass-card p-6">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-indigo-500/10">
                <Brain className="h-4 w-4 text-indigo-400" />
              </div>
              <h2 className="text-lg font-bold tracking-tight text-white">Skill Library</h2>
            </div>
          </div>

          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 animate-pulse">
              <RefreshCw className="h-8 w-8 animate-spin text-indigo-500 mb-4" />
              <span className="text-sm font-medium text-slate-500">Loading...</span>
            </div>
          ) : (
            <div className="space-y-4">
              {recentSkills.length === 0 ? (
                <div className="text-center py-12 bg-white/[0.02] border border-dashed border-white/10 rounded-2xl">
                  <p className="text-sm text-slate-500">No skills yet.</p>
                </div>
              ) : (
                recentSkills.map((skill) => <SkillCard key={skill.id} skill={skill} />)
              )}
            </div>
          )}
        </div>
      </div>

      {/* Engine Status */}
      <div className="glass-card p-6">
        <div className="flex items-center space-x-3 mb-8">
          <div className="p-2 rounded-lg bg-emerald-500/10">
            <Activity className="h-4 w-4 text-emerald-400" />
          </div>
          <h2 className="text-lg font-bold tracking-tight text-white">Core Connectivity Status</h2>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-6">
            <RefreshCw className="h-5 w-5 animate-spin text-slate-500" />
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
            <div className="flex items-center justify-between p-5 bg-white/[0.03] border border-white/[0.06] rounded-2xl hover:bg-white/[0.05] transition-all">
              <div className="flex items-center">
                <Globe className="h-5 w-5 text-indigo-400 mr-4" />
                <div>
                  <p className="text-sm font-bold text-slate-100">LLM Engine</p>
                  <p className="text-xs text-slate-500 mt-1 font-mono uppercase tracking-wider">
                    {systemStatus?.llm_model || "—"}
                  </p>
                </div>
              </div>
              <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
            </div>

            <div className="flex items-center justify-between p-5 bg-white/[0.03] border border-white/[0.06] rounded-2xl hover:bg-white/[0.05] transition-all">
              <div className="flex items-center">
                <Terminal className="h-5 w-5 text-indigo-400 mr-4" />
                <div>
                  <p className="text-sm font-bold text-slate-100">Knowledge Base</p>
                  <p className="text-xs text-slate-500 mt-1 uppercase tracking-wider">
                    {systemStatus?.knowledge_base_size ? `${systemStatus.knowledge_base_size} Notes Integrated` : "—"}
                  </p>
                </div>
              </div>
              <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
            </div>

            <div className="flex items-center justify-between p-5 bg-white/[0.03] border border-white/[0.06] rounded-2xl hover:bg-white/[0.05] transition-all">
              <div className="flex items-center">
                <Activity className="h-5 w-5 text-indigo-400 mr-4" />
                <div>
                  <p className="text-sm font-bold text-slate-100">Backend</p>
                  <p className="text-xs text-slate-500 mt-1 uppercase tracking-wider">
                    {systemStatus?.status || "—"}
                  </p>
                </div>
              </div>
              <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
            </div>

            <Link
              to="/vault/sync"
              className="flex items-center justify-between p-5 bg-white/[0.03] border border-white/[0.06] rounded-2xl hover:bg-white/[0.05] transition-all"
            >
              <div className="flex items-center">
                {watchStatus?.stale ? (
                  <AlertTriangle className="h-5 w-5 text-amber-400 mr-4" />
                ) : (
                  <FolderSync className="h-5 w-5 text-indigo-400 mr-4" />
                )}
                <div>
                  <p className="text-sm font-bold text-slate-100">Index Sync</p>
                  <p
                    className={`text-xs mt-1 uppercase tracking-wider ${
                      watchStatus?.stale ? "text-amber-400" : "text-slate-500"
                    }`}
                  >
                    {watchStatus == null
                      ? "—"
                      : watchStatus.stale
                        ? `Stalled - last scan ${timeAgo(watchStatus.last_scan)}`
                        : watchStatus.running
                          ? `Last scan ${timeAgo(watchStatus.last_scan)}`
                          : "Watcher stopped"}
                  </p>
                </div>
              </div>
              <div
                className={`w-2.5 h-2.5 rounded-full ${
                  watchStatus == null
                    ? "bg-slate-600"
                    : watchStatus.stale
                      ? "bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.6)]"
                      : watchStatus.running
                        ? "bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]"
                        : "bg-slate-500"
                }`}
              ></div>
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
