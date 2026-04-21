import { Calendar, ChevronRight, Clock, FileText, Loader2, Search, Tag } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { devError } from "../../devConsole";
import { apiService } from "../../services/api";

interface RecentNote {
  identifier: string;
  title: string;
  timestamp: string;
  type: string;
  summary?: string;
  tags?: string[];
}

/** Map UI timeframe to strings the API timeframe validator accepts reliably. */
function toApiTimeframe(ui: string): string {
  if (ui === "24h") {
    return "1d";
  }
  if (ui === "7d") {
    return "7d";
  }
  if (ui === "30d") {
    return "30 days ago";
  }
  if (ui === "90d") {
    return "90 days ago";
  }
  return "7d";
}

export default function Recents() {
  const [recents, setRecents] = useState<RecentNote[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [timeframe, setTimeframe] = useState("7d");
  const [searchQuery, setSearchQuery] = useState("");
  const [fetchError, setFetchError] = useState<string | null>(null);

  const fetchRecents = useCallback(async () => {
    setIsLoading(true);
    setFetchError(null);
    try {
      const pr = await apiService.getProjects();
      if (pr.success && Array.isArray(pr.data) && pr.data.length > 0) {
        const def = (pr.data as { name: string; is_default?: boolean }[]).find((p) => p.is_default)?.name;
        const pick = def || pr.data[0]?.name;
        if (pick) {
          apiService.activeProject = pick;
        }
      }

      const response = await apiService.getMemoryRecent({
        timeframe: toApiTimeframe(timeframe),
        depth: 1,
        page: 1,
        pageSize: 50,
      });

      if (!response.success || !response.data) {
        setRecents([]);
        setFetchError(response.error || "Could not load recent activity");
        return;
      }

      const rows = response.data.results;
      if (!Array.isArray(rows)) {
        setRecents([]);
        setFetchError("Unexpected response from memory/recent");
        return;
      }

      const primaries = rows
        .map((item) => item.primary_result)
        .filter((primary): primary is Record<string, unknown> => {
          if (!primary || typeof primary !== "object") {
            return false;
          }
          const t = primary.type;
          return t === "entity" || t === "observation";
        });

      const notes: RecentNote[] = primaries.map((primary) => {
        const content = typeof primary.content === "string" ? primary.content : "";
        const snippet = content.length > 150 ? `${content.slice(0, 150)}…` : content;
        const tags = Array.isArray(primary.tags) ? (primary.tags as string[]) : [];
        const ts = primary.created_at;
        const base: RecentNote = {
          identifier: String(primary.permalink ?? primary.title ?? ""),
          title: String(primary.title ?? primary.permalink ?? "Untitled"),
          timestamp: typeof ts === "string" ? ts : new Date().toISOString(),
          type: String(primary.type ?? "entity"),
          tags,
        };
        if (snippet) {
          base.summary = snippet;
        }
        return base;
      });
      setRecents(notes);
    } catch (err) {
      devError("Failed to fetch recents:", err);
      setRecents([]);
      setFetchError(String(err));
    } finally {
      setIsLoading(false);
    }
  }, [timeframe]);

  useEffect(() => {
    void fetchRecents();
  }, [fetchRecents]);

  const filteredRecents = recents.filter(
    (note) =>
      note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      note.tags?.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase())),
  );

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-accent/20 rounded-lg">
            <Clock className="h-8 w-8 text-accent" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Recent Activity</h1>
            <p className="text-muted-foreground text-sm">
              Review your most recent thoughts and updates
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Filter recents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-muted/50 border border-border rounded-full pl-10 pr-4 py-2 text-sm focus:ring-2 focus:ring-accent/50 outline-none w-64"
            />
          </div>

          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className="bg-muted/50 border border-border rounded-md px-3 py-2 text-sm outline-none cursor-pointer"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 3 Months</option>
          </select>
        </div>
      </div>

      {fetchError && (
        <div className="rounded-lg border border-red-500/40 bg-red-950/30 px-4 py-3 text-sm text-red-200">
          {fetchError}
        </div>
      )}

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <Loader2 className="h-12 w-12 text-accent animate-spin mb-4" />
          <p className="text-muted-foreground">Retrieving history...</p>
        </div>
      ) : filteredRecents.length === 0 ? (
        <div className="card p-12 text-center border-dashed">
          <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4 opacity-20" />
          <h3 className="text-xl font-semibold opacity-50">No recent activity found</h3>
          <p className="text-muted-foreground mt-2 max-w-sm mx-auto">
            Try expanding your timeframe or start creating new notes to see them here.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredRecents.map((note, index) => (
            <Link
              to={`/notes?id=${encodeURIComponent(note.identifier)}`}
              key={`${note.identifier}-${index}`}
              className="card group hover:border-accent/50 hover:bg-accent/5 transition-all duration-300 block overflow-hidden"
            >
              <div className="p-5 flex items-start gap-4">
                <div className="p-3 bg-muted rounded-xl group-hover:bg-accent/10 transition-colors">
                  <FileText className="h-6 w-6 text-muted-foreground group-hover:text-accent" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-bold text-lg group-hover:text-accent transition-colors truncate">
                      {note.title}
                    </h3>
                    <div className="flex items-center text-xs text-muted-foreground bg-background px-2 py-1 rounded-full whitespace-nowrap">
                      <Calendar className="h-3 w-3 mr-1" />
                      {new Date(note.timestamp).toLocaleDateString()}
                    </div>
                  </div>

                  <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                    {note.summary || "No summary available for this note."}
                  </p>

                  <div className="flex items-center justify-between">
                    <div className="flex gap-2">
                      {note.tags?.slice(0, 3).map((tag) => (
                        <span
                          key={tag}
                          className="flex items-center text-[10px] px-2 py-0.5 bg-muted rounded text-muted-foreground uppercase tracking-wider font-semibold"
                        >
                          <Tag className="h-2 w-2 mr-1" />
                          {tag}
                        </span>
                      ))}
                      {note.tags && note.tags.length > 3 && (
                        <span className="text-[10px] text-muted-foreground pt-0.5 font-medium">
                          +{note.tags.length - 3} more
                        </span>
                      )}
                    </div>

                    <div className="flex items-center text-xs font-bold text-accent opacity-0 group-hover:opacity-100 transition-opacity">
                      <span>View details</span>
                      <ChevronRight className="h-3 w-3 ml-1" />
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
