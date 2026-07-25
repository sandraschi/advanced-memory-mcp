import { ChevronRight, Clock, FileText, Loader2, Search, Tag } from "lucide-react";
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

function toApiTimeframe(ui: string): string {
  if (ui === "24h") return "1d";
  if (ui === "7d") return "7d";
  if (ui === "30d") return "30 days ago";
  if (ui === "90d") return "90 days ago";
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
        if (pick) apiService.activeProject = pick;
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
          if (!primary || typeof primary !== "object") return false;
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
        if (snippet) base.summary = snippet;
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
    <div className="max-w-5xl mx-auto space-y-3 animate-in fade-in duration-700 px-4 py-4">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-accent/20 rounded-lg">
            <Clock className="h-5 w-5 text-accent" />
          </div>
          <h1 className="text-lg font-bold tracking-tight">Recent Activity</h1>
        </div>

        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3 w-3 text-muted-foreground" />
            <input
              type="text"
              placeholder="Filter..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-muted/50 border border-border rounded-full pl-7 pr-3 py-1.5 text-xs focus:ring-2 focus:ring-accent/50 outline-none w-48"
            />
          </div>
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className="bg-muted/50 border border-border rounded-md px-2 py-1.5 text-xs outline-none cursor-pointer"
          >
            <option value="24h">24h</option>
            <option value="7d">7 days</option>
            <option value="30d">30 days</option>
            <option value="90d">3 months</option>
          </select>
        </div>
      </div>

      {fetchError && (
        <div className="rounded-lg border border-red-500/40 bg-red-950/30 px-3 py-2 text-xs text-red-200">
          {fetchError}
        </div>
      )}

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-10">
          <Loader2 className="h-8 w-8 text-accent animate-spin mb-2" />
          <p className="text-xs text-muted-foreground">Loading...</p>
        </div>
      ) : filteredRecents.length === 0 ? (
        <div className="card p-8 text-center border-dashed">
          <FileText className="h-8 w-8 text-muted-foreground mx-auto mb-2 opacity-20" />
          <p className="text-sm text-muted-foreground">
            {searchQuery ? "No matches" : "No recent activity found. Try a wider timeframe."}
          </p>
        </div>
      ) : (
        <div className="space-y-1">
          {filteredRecents.map((note, index) => (
            <Link
              to={`/notes?id=${encodeURIComponent(note.identifier)}`}
              key={`${note.identifier}-${index}`}
              className="block group hover:bg-accent/5 transition-colors rounded-lg -mx-2 px-2 py-2"
            >
              <div className="flex items-start gap-2.5">
                <div className="p-1.5 bg-muted rounded-lg mt-0.5 shrink-0">
                  <FileText className="h-3.5 w-3.5 text-muted-foreground" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="text-sm font-medium truncate group-hover:text-accent transition-colors">
                      {note.title}
                    </h3>
                    <div className="flex items-center gap-1.5 shrink-0">
                      <span className="text-[10px] text-muted-foreground whitespace-nowrap">
                        {new Date(note.timestamp).toLocaleDateString()}
                      </span>
                      <ChevronRight className="h-3 w-3 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  </div>
                  {note.summary && (
                    <p className="text-xs text-muted-foreground line-clamp-1 mt-0.5">
                      {note.summary}
                    </p>
                  )}
                  {note.tags && note.tags.length > 0 && (
                    <div className="flex gap-1 mt-1">
                      {note.tags.slice(0, 3).map((tag) => (
                        <span
                          key={tag}
                          className="inline-flex items-center text-[9px] px-1.5 py-0.5 bg-muted rounded text-muted-foreground uppercase tracking-wider"
                        >
                          <Tag className="h-2 w-2 mr-0.5" />
                          {tag}
                        </span>
                      ))}
                      {note.tags.length > 3 && (
                        <span className="text-[9px] text-muted-foreground">
                          +{note.tags.length - 3}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
