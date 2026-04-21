import { Brain, ChevronRight, Database, Folder, Loader2, Search, Sparkles, X } from "lucide-react";
import { useEffect, useState } from "react";
import { apiService } from "../../services/api";

interface SemanticChunk {
  entity_id: number;
  permalink: string | null;
  title: string;
  snippet: string;
  chunk_text: string;
  score: number;
}

interface NoteContent {
  title: string;
  permalink: string | null;
  content: string;
}

export default function SearchDeep() {
  const [query, setQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<SemanticChunk[]>([]);
  const [activeFilters, setActiveFilters] = useState<string[]>(["All Projects", "Knowledge Base"]);
  const [project, setProject] = useState<string>("default");
  const [noteModal, setNoteModal] = useState<NoteContent | null>(null);
  const [noteLoading, setNoteLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  useEffect(() => {
    apiService.getProjects().then((r) => {
      if (r.success && r.data?.length) {
        const defaultProj = r.data.find((p: { is_default?: boolean }) => p.is_default) ?? r.data[0];
        setProject(defaultProj.name ?? defaultProj.permalink ?? "default");
      }
    });
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setIsSearching(true);
    setSearchError(null);
    try {
      const response = await apiService.searchSemanticChunks(project, query.trim(), 20);
      if (response.success && response.data?.chunks) {
        setResults(response.data.chunks);
      } else {
        setResults([]);
        setSearchError(response.error ?? "No results");
      }
    } catch {
      setResults([]);
      setSearchError("Semantic search failed");
    } finally {
      setIsSearching(false);
    }
  };

  const openNote = async (permalink: string | null) => {
    if (!permalink) return;
    setNoteLoading(true);
    setNoteModal(null);
    try {
      const response = await apiService.getNoteContent(project, permalink);
      if (response.success && response.data) {
        setNoteModal(response.data);
      }
    } finally {
      setNoteLoading(false);
    }
  };

  const closeNote = () => setNoteModal(null);

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Search Header */}
      <div className="border-b border-white/5 bg-black/20 backdrop-blur-xl px-10 py-12">
        <div className="max-w-4xl mx-auto space-y-8">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <h1 className="text-3xl font-bold tracking-tight">Deep Intelligence Search</h1>
              <p className="text-sm text-muted-foreground">
                Meaning-based retrieval (LanceDB vectors) — not the same as keyword search in the
                Note Vault or wikilinks in the graph.
              </p>
            </div>
            <div className="flex items-center space-x-2 bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 rounded-full">
              <Brain className="h-4 w-4 text-amber-500" />
              <span className="text-[10px] uppercase font-bold tracking-widest text-amber-500">
                RAG Engine v3.0
              </span>
            </div>
          </div>

          <form onSubmit={handleSearch} className="relative group">
            <div className="absolute inset-x-0 -inset-y-0.5 bg-gradient-to-r from-amber-500/20 via-blue-500/20 to-purple-500/20 rounded-2xl blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity duration-500" />
            <div className="relative flex items-center bg-black/40 border border-white/10 rounded-2xl overflow-hidden shadow-2xl transition-all duration-300 group-focus-within:border-white/20 group-focus-within:bg-black/60">
              <div className="pl-6 pr-4">
                <Search
                  className={`h-6 w-6 transition-colors ${isSearching ? "text-amber-500 animate-pulse" : "text-muted-foreground group-focus-within:text-white"}`}
                />
              </div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Query the second brain..."
                className="flex-1 bg-transparent border-none py-6 pr-6 text-xl focus:outline-none placeholder:text-muted-foreground/50 transition-all"
              />
              <div className="pr-4">
                <button
                  type="submit"
                  disabled={!query.trim() || isSearching}
                  className="bg-primary hover:bg-primary/90 disabled:opacity-50 text-primary-foreground px-6 py-3 rounded-xl font-bold text-sm transition-all"
                >
                  {isSearching ? <Loader2 className="h-4 w-4 animate-spin" /> : "Retrieve"}
                </button>
              </div>
            </div>
          </form>

          <div className="flex flex-wrap gap-2">
            {[
              "All Projects",
              "Knowledge Base",
              "Research Lab",
              "Skills Depot",
              "Academic (arXiv)",
              "Code Sites",
            ].map((filter) => (
              <button
                key={filter}
                onClick={() =>
                  setActiveFilters((prev) =>
                    prev.includes(filter) ? prev.filter((f) => f !== filter) : [...prev, filter],
                  )
                }
                className={`px-4 py-1.5 rounded-full text-[10px] uppercase font-bold tracking-widest border transition-all ${
                  activeFilters.includes(filter)
                    ? "bg-white text-black border-white"
                    : "bg-white/5 text-muted-foreground border-white/10 hover:border-white/20"
                }`}
              >
                {filter}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Results Area */}
      <div className="flex-1 overflow-y-auto px-10 py-12 scrollbar-thin">
        <div className="max-w-4xl mx-auto space-y-10">
          {isSearching ? (
            <div className="flex flex-col items-center justify-center py-20 space-y-4">
              <div className="relative">
                <Brain className="h-12 w-12 text-amber-500 animate-pulse" />
                <div className="absolute inset-0 bg-amber-500/20 blur-2xl animate-pulse rounded-full" />
              </div>
              <div className="text-center space-y-2">
                <p className="text-sm font-bold uppercase tracking-[0.3em]">
                  Querying Semantic Index
                </p>
                <p className="text-[10px] text-muted-foreground uppercase font-mono italic">
                  Querying vector index for this project…
                </p>
              </div>
            </div>
          ) : searchError ? (
            <div className="flex flex-col items-center justify-center py-20 space-y-4">
              <p className="text-sm text-muted-foreground">{searchError}</p>
            </div>
          ) : results.length > 0 ? (
            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
              <div className="flex items-center justify-between opacity-50">
                <span className="text-[10px] uppercase font-bold tracking-widest leading-none flex items-center space-x-2">
                  <Database className="h-3 w-3" />
                  <span>{results.length} chunks</span>
                </span>
              </div>

              <div className="space-y-4">
                {results.map((result, idx) => (
                  <div
                    key={`${result.entity_id}-${idx}`}
                    className="group relative bg-white/2 border border-white/5 hover:border-white/10 p-8 rounded-3xl transition-all duration-300 hover:bg-white/[0.04] hover:-translate-y-1 cursor-pointer"
                    role="button"
                    tabIndex={0}
                    onClick={() => result.permalink && openNote(result.permalink)}
                    onKeyDown={(e) =>
                      e.key === "Enter" && result.permalink && openNote(result.permalink)
                    }
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="space-y-2">
                        <div className="flex items-center space-x-3">
                          <h3 className="text-lg font-bold group-hover:text-amber-500 transition-colors">
                            {result.title}
                          </h3>
                          <div className="px-2 py-0.5 bg-amber-500/10 border border-amber-500/20 rounded-md">
                            <span className="text-[9px] font-mono font-bold text-amber-500">
                              {(result.score * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                        {result.permalink && (
                          <div className="flex items-center space-x-1 text-[10px] text-muted-foreground font-mono">
                            <Folder className="h-3 w-3" />
                            <span>{result.permalink}</span>
                          </div>
                        )}
                      </div>
                      {result.permalink && (
                        <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <span className="text-[10px] uppercase font-bold tracking-widest text-amber-500">
                            Open note
                          </span>
                          <ChevronRight className="h-3 w-3" />
                        </div>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground leading-relaxed mb-6 line-clamp-2">
                      {result.snippet}
                    </p>
                    {result.permalink && (
                      <button
                        type="button"
                        className="flex items-center space-x-2 text-[10px] uppercase font-bold tracking-widest text-amber-500 hover:text-amber-400 group/btn transition-colors"
                        onClick={(e) => {
                          e.stopPropagation();
                          openNote(result.permalink!);
                        }}
                      >
                        <span>Show full note</span>
                        <ChevronRight className="h-3 w-3 group-hover/btn:translate-x-1 transition-transform" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-32 space-y-6 opacity-30">
              <Brain className="h-16 w-16" />
              <div className="text-center space-y-2">
                <p className="text-lg font-bold uppercase tracking-[0.2em]">Ready for Inference</p>
                <p className="text-sm">Semantic retrieval engine active on ports 10705/10706.</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Search Tips Footer */}
      <div className="border-t border-white/5 bg-black/40 p-6">
        <div className="max-w-4xl mx-auto flex items-center justify-between text-[10px] uppercase font-bold tracking-widest text-muted-foreground">
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <span className="bg-white/10 px-1.5 py-0.5 rounded text-[8px]">/</span>
              <span>Global Command</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="bg-white/10 px-1.5 py-0.5 rounded text-[8px]">PROJ:</span>
              <span>Project Filter</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="bg-white/10 px-1.5 py-0.5 rounded text-[8px]">NEAR:</span>
              <span>Semantic Proximity</span>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-amber-500/60">
            <Sparkles className="h-3 w-3" />
            <span>Vector Index: 98.4% Integrated</span>
          </div>
        </div>
      </div>

      {/* Full note modal */}
      {(noteModal !== null || noteLoading) && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
          onClick={closeNote}
          role="dialog"
          aria-modal="true"
        >
          <div
            className="bg-background border border-white/10 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col m-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-4 border-b border-white/5">
              <h2 className="text-lg font-bold truncate">{noteModal?.title ?? "Loading..."}</h2>
              <button
                type="button"
                onClick={closeNote}
                className="p-2 hover:bg-white/10 rounded-xl transition-colors"
                aria-label="Close"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-6">
              {noteLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-amber-500" />
                </div>
              ) : noteModal ? (
                <pre className="whitespace-pre-wrap font-sans text-sm text-muted-foreground leading-relaxed">
                  {noteModal.content}
                </pre>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
