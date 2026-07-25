import {
  BookOpen,
  CheckCircle2,
  Compass,
  FileText,
  Globe,
  Loader2,
  RefreshCw,
  Search,
  Settings2,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import Markdown from "../../components/Markdown";
import { getApiBaseUrl } from "../../config/apiBase";

interface WikiIndexPage {
  title: string;
  permalink: string;
  entity_type: string;
  link_count: number;
}

interface WikiIndex {
  compiled_at: string;
  entity_count: number;
  page_count: number;
  pages: WikiIndexPage[];
}

interface WikiPageContent {
  permalink: string;
  content: string;
}

interface WikiStatus {
  compiled: boolean;
  page_count: number;
  entity_count: number;
  compiled_at: string;
  total_size_bytes: number;
}

const API = getApiBaseUrl();

export default function WikiPage() {
  const [index, setIndex] = useState<WikiIndex | null>(null);
  const [page, setPage] = useState<WikiPageContent | null>(null);
  const [status, setStatus] = useState<WikiStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [compiling, setCompiling] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedPermalink, setSelectedPermalink] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const r = await fetch(`${API}/api/v1/wiki/status`);
      if (r.ok) setStatus(await r.json());
    } catch { /* ignore */ }
  }, []);

  const fetchIndex = useCallback(async () => {
    try {
      const r = await fetch(`${API}/api/v1/wiki/index`);
      if (r.ok) setIndex(await r.json());
    } catch { /* ignore */ }
  }, []);

  const fetchPage = useCallback(async (permalink: string) => {
    try {
      const r = await fetch(`${API}/api/v1/wiki/page/${encodeURIComponent(permalink)}`);
      if (r.ok) setPage(await r.json());
    } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    (async () => {
      setLoading(true);
      await fetchStatus();
      await fetchIndex();
      setLoading(false);
    })();
  }, [fetchStatus, fetchIndex]);

  const handleSelect = useCallback(async (permalink: string) => {
    setSelectedPermalink(permalink);
    setPage(null);
    await fetchPage(permalink);
  }, [fetchPage]);

  const handleCompile = useCallback(async () => {
    setCompiling(true);
    try {
      const resp = await fetch(`${API}/mcp/tools/adn_wiki`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ arguments: { operation: "compile" } }),
      });
      const result = await resp.json();
      if (result.success) {
        await fetchStatus();
        await fetchIndex();
      }
    } catch { /* ignore */ }
    setCompiling(false);
  }, [fetchStatus, fetchIndex]);

  const filteredPages = useMemo(() => {
    if (!index?.pages) return [];
    if (!searchQuery) return index.pages;
    const q = searchQuery.toLowerCase();
    return index.pages.filter(
      (p) => p.title.toLowerCase().includes(q) || p.entity_type.toLowerCase().includes(q),
    );
  }, [index, searchQuery]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-12rem)]">
        <Loader2 className="h-8 w-8 animate-spin text-amber-500" />
      </div>
    );
  }

  return (
    <div className="max-w-[1400px] mx-auto h-[calc(100vh-12rem)] flex flex-col space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header */}
      <div className="flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-gradient-to-br from-amber-500/20 to-orange-500/20 rounded-xl border border-amber-500/20">
            <BookOpen className="h-6 w-6 text-amber-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Compiled Wiki</h1>
            <p className="text-muted-foreground text-xs">
              Auto-generated knowledge graph wiki &mdash; compiled from entities and their links
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {status && (
            <div className="flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-[10px] font-bold text-emerald-300 tracking-wider">
              <CheckCircle2 className="h-3 w-3" />
              <span>{status.page_count} pages</span>
            </div>
          )}
          <button
            onClick={handleCompile}
            disabled={compiling}
            className="btn btn-sm btn-outline text-[10px] uppercase tracking-wider py-1.5 px-3 flex items-center space-x-1.5"
            data-testid="wiki-recompile"
          >
            {compiling ? <Loader2 className="h-3 w-3 animate-spin" /> : <RefreshCw className="h-3 w-3" />}
            <span>{compiling ? "Compiling..." : "Recompile"}</span>
          </button>
        </div>
      </div>

      {/* Layout */}
      <div className="flex-1 flex space-x-6 overflow-hidden min-h-0">
        {/* Left: Page Tree */}
        <div className="w-80 shrink-0 flex flex-col space-y-4" data-testid="wiki-tree">
          <div className="card p-4 bg-muted/20 border-white/5 space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
              <input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search pages..."
                className="w-full bg-background border border-border rounded-lg pl-9 pr-3 py-2 text-sm outline-none focus:ring-1 focus:ring-amber-500/30"
              />
            </div>

            <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-widest text-muted-foreground px-1">
              <span>Pages</span>
              <span>{filteredPages.length} total</span>
            </div>

            <div className="space-y-1 overflow-y-auto max-h-[calc(100vh-28rem)] pr-1 scrollbar-thin">
              {filteredPages.length > 0 ? (
                filteredPages.map((p) => (
                  <button
                    key={p.permalink}
                    onClick={() => handleSelect(p.permalink)}
                    className={`w-full text-left p-3 rounded-xl border transition-all ${
                      selectedPermalink === p.permalink
                        ? "bg-amber-500/10 border-amber-500/30 ring-1 ring-amber-500/20"
                        : "bg-muted/10 border-white/5 hover:border-white/10"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 min-w-0">
                        <FileText className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                        <span className="text-xs font-medium truncate">{p.title}</span>
                      </div>
                      <span className="text-[9px] text-muted-foreground shrink-0 ml-2">{p.entity_type}</span>
                    </div>
                    {p.link_count > 0 && (
                      <div className="flex items-center space-x-1 mt-1.5 ml-5.5">
                        <Globe className="h-2.5 w-2.5 text-amber-400/60" />
                        <span className="text-[9px] text-amber-400/60">{p.link_count} links</span>
                      </div>
                    )}
                  </button>
                ))
              ) : (
                <div className="text-center py-8 opacity-40">
                  <Compass className="h-8 w-8 mx-auto mb-2" />
                  <p className="text-[10px] uppercase tracking-widest font-bold">
                    {index ? "No pages match" : "No wiki compiled"}
                  </p>
                  {!index && (
                    <p className="text-[9px] mt-1">Run adn_wiki(operation="compile") to generate</p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right: Page Content */}
        <div className="flex-1 flex flex-col min-w-0" data-testid="wiki-content">
          {selectedPermalink ? (
            <div className="h-full card flex flex-col overflow-hidden p-0 bg-black/40">
              <div className="p-4 border-b border-white/5 flex items-center justify-between shrink-0 bg-white/5">
                <div className="flex items-center space-x-3">
                  <FileText className="h-4 w-4 text-amber-400" />
                  <h3 className="text-xs font-bold uppercase tracking-widest">{selectedPermalink}</h3>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-6 scrollbar-thin">
                {page ? (
                  <Markdown content={page.content} />
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <Loader2 className="h-6 w-6 animate-spin text-amber-500" />
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="h-full card flex flex-col items-center justify-center text-center opacity-40 select-none grayscale">
              <Settings2 className="h-16 w-16 text-muted-foreground mb-4" />
              <h3 className="text-xl font-bold">Wiki Page Viewer</h3>
              <p className="text-sm max-w-sm mt-2">
                Select a page from the tree to view its compiled content.
              </p>
              {!index && (
                <button
                  onClick={handleCompile}
                  disabled={compiling}
                  className="mt-4 btn btn-sm btn-primary flex items-center space-x-1.5"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${compiling ? "animate-spin" : ""}`} />
                  <span>{compiling ? "Compiling..." : "Compile Wiki Now"}</span>
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
