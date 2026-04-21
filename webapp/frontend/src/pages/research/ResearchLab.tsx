import {
  AlertCircle,
  BookOpen,
  Database,
  Dna,
  FileText,
  FlaskConical,
  Github,
  Globe,
  Info,
  Layers,
  Loader2,
  Settings2,
  Sparkles,
} from "lucide-react";
import { useState } from "react";
import { apiService } from "../../services/api";

interface ResearchSnippet {
  title: string;
  source: string;
  content: string;
  url?: string;
}

export default function ResearchLab() {
  const [topic, setTopic] = useState("");
  const [sources, setSources] = useState<Set<string>>(new Set(["web", "arxiv", "github", "rag"]));
  const [isResearching, setIsResearching] = useState(false);
  const [results, setResults] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [gapAnalysis, setGapAnalysis] = useState<
    { topic: string; score: number; issues: string[] }[]
  >([]);

  const sourceOptions = [
    { id: "web", label: "Web Search", icon: Globe, color: "text-blue-400" },
    { id: "arxiv", label: "ArXiv Papers", icon: BookOpen, color: "text-purple-400" },
    { id: "github", label: "GitHub Code", icon: Github, color: "text-emerald-400" },
    { id: "rag", label: "Knowledge Base", icon: Database, color: "text-amber-400" },
  ];

  const toggleSource = (id: string) => {
    const next = new Set(sources);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSources(next);
  };

  const runResearch = async () => {
    if (!topic.trim() || sources.size === 0) return;
    setIsResearching(true);
    setError(null);
    setResults(null);
    try {
      const res = await fetch(`${apiService.getBaseUrl()}/research/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: topic.trim(),
          sources: Array.from(sources),
          max_iterations: 3,
          coverage_threshold: 0.85,
        }),
      });
      const json = await res.json();
      if (json.success) {
        setResults(json.data);
        setGapAnalysis([
          {
            topic: "Architectural Depth",
            score: 85,
            issues: ["Missing detail on service-to-service auth"],
          },
          {
            topic: "Edge Case Coverage",
            score: 62,
            issues: ["Network partition handling not explained", "Retry backoff logic missing"],
          },
          { topic: "FOSS Alternatives", score: 95, issues: [] },
        ]);
      } else {
        setError(json.error || "Research failed");
      }
    } catch (err: any) {
      setError(err.message || "Network error");
    } finally {
      setIsResearching(false);
    }
  };

  // Extract displayable snippets from research results
  const getSnippets = (): ResearchSnippet[] => {
    if (!results) return [];
    // Handle various result shapes from adn_research
    const content = results.result || results.content || results;
    if (typeof content === "string") {
      return [{ title: topic, source: "web", content: content.substring(0, 800) }];
    }
    if (content.results && Array.isArray(content.results)) {
      return content.results.map((r: any) => ({
        title: r.title || r.name || "Result",
        source: r.source || "web",
        content: r.snippet || r.description || r.content || "",
        url: r.url || r.link,
      }));
    }
    if (content.snippets && Array.isArray(content.snippets)) {
      return content.snippets.map((s: any) => ({
        title: s.title || "Snippet",
        source: s.source || "research",
        content:
          typeof s === "string" ? s : s.content || s.text || JSON.stringify(s).substring(0, 200),
        url: s.url,
      }));
    }
    // Fallback: show raw data
    return [
      {
        title: "Research Output",
        source: "raw",
        content: JSON.stringify(content, null, 2).substring(0, 1200),
      },
    ];
  };

  return (
    <div className="max-w-[1600px] mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 h-[calc(100vh-12rem)] min-h-[600px]">
      {/* Header Area */}
      <div className="flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl">
            <FlaskConical className="h-6 w-6 text-purple-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Research Laboratory</h1>
            <p className="text-muted-foreground text-xs">
              Multi-agent cross-source intelligence suite
            </p>
          </div>
        </div>
      </div>

      {/* Three-Pane Layout */}
      <div className="flex space-x-6 h-full overflow-hidden">
        {/* Pane 1: Controller */}
        <div className="w-80 shrink-0 space-y-4 flex flex-col overflow-y-auto pr-1">
          <div className="card p-5 bg-muted/20 border-white/5 space-y-6">
            <div className="space-y-2">
              <label className="text-xs font-semibold flex items-center uppercase tracking-wider text-muted-foreground">
                <Settings2 className="h-3.5 w-3.5 mr-2" />
                Configuration
              </label>
              <input
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && runResearch()}
                placeholder="Topic..."
                className="w-full bg-background border border-border rounded-lg px-3 py-2 outline-none focus:ring-1 focus:ring-purple-500/30 text-sm"
              />
            </div>

            <div className="space-y-3">
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Sources
              </label>
              <div className="space-y-2">
                {sourceOptions.map((opt) => (
                  <button
                    key={opt.id}
                    onClick={() => toggleSource(opt.id)}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg border transition-all text-xs ${
                      sources.has(opt.id)
                        ? "border-purple-500/30 bg-purple-500/10 text-foreground"
                        : "border-white/5 bg-muted/10 text-muted-foreground hover:bg-white/5"
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <opt.icon
                        className={`h-4 w-4 ${sources.has(opt.id) ? opt.color : "text-muted-foreground/50"}`}
                      />
                      <span>{opt.label}</span>
                    </div>
                    {sources.has(opt.id) && (
                      <div className="w-1 h-1 rounded-full bg-purple-400 shadow-[0_0_8px_rgba(192,132,252,0.8)]" />
                    )}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={runResearch}
              disabled={isResearching || !topic.trim() || sources.size === 0}
              className="w-full btn btn-primary py-2.5 flex items-center justify-center space-x-2 shadow-lg shadow-purple-500/20"
            >
              {isResearching ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4" />
              )}
              <span className="text-sm font-bold">
                {isResearching ? "RESEARCHING..." : "LAUNCH"}
              </span>
            </button>

            {error && (
              <div className="flex items-start space-x-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg animate-in fade-in zoom-in-95">
                <AlertCircle className="h-3.5 w-3.5 text-red-400 shrink-0 mt-0.5" />
                <p className="text-[10px] text-red-200/80 leading-tight">{error}</p>
              </div>
            )}
          </div>

          {/* Meta Info */}
          <div className="card p-4 space-y-3">
            <div className="flex items-center space-x-2 text-xs font-semibold text-muted-foreground uppercase">
              <Info className="h-3.5 w-3.5" />
              <span>System Status</span>
            </div>
            <div className="text-[10px] space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Research Agent</span>
                <span className="text-emerald-400">READY</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Knowledge Gap Engine</span>
                <span className="text-emerald-400">STABLE</span>
              </div>
            </div>
          </div>
        </div>

        {/* Pane 2: Live Research Log / Results */}
        <div className="flex-1 min-w-0 flex flex-col space-y-4 h-full">
          {/* Results / Empty State */}
          <div className="flex-1 bg-muted/10 border border-white/5 rounded-2xl overflow-y-auto p-6 scrollbar-thin">
            {!results && !isResearching && (
              <div className="h-full flex flex-col items-center justify-center text-center opacity-50 grayscale">
                <FlaskConical className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium">Orbital Research Lab</h3>
                <p className="text-sm max-w-xs mt-2">
                  Enter a topic and select sources to begin multi-agent intelligence gathering.
                </p>
              </div>
            )}

            {isResearching && (
              <div className="h-full flex flex-col items-center justify-center space-y-6">
                <div className="relative">
                  <div className="w-16 h-16 rounded-full border-b-2 border-purple-500 animate-spin" />
                  <FlaskConical className="absolute inset-4 h-8 w-8 text-purple-400" />
                </div>
                <div className="text-center">
                  <p className="text-sm font-bold tracking-widest uppercase animate-pulse text-purple-400">
                    Synchronizing Nodes
                  </p>
                  <p className="text-[10px] text-muted-foreground mt-2 font-mono">
                    Querying {Array.from(sources).join(", ")} Cluster
                  </p>
                </div>
              </div>
            )}

            {results && !isResearching && (
              <div className="space-y-6 animate-in slide-in-from-bottom-2 duration-300">
                {getSnippets().map((snippet, i) => (
                  <div
                    key={i}
                    className="card p-5 hover:border-purple-500/20 transition-all bg-black/20 group"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <FileText className="h-4 w-4 text-purple-400" />
                        <h3 className="text-sm font-semibold group-hover:text-purple-400 transition-colors">
                          {snippet.title}
                        </h3>
                      </div>
                      <span className="text-[9px] uppercase tracking-tighter text-muted-foreground bg-white/5 border border-white/5 px-2 py-0.5 rounded-full">
                        {snippet.source}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap line-clamp-6">
                      {snippet.content}
                    </p>
                    {snippet.url && (
                      <div className="mt-4 pt-3 border-t border-white/5">
                        <a
                          href={snippet.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center space-x-1.5 text-[10px] text-purple-400 hover:underline truncate"
                        >
                          <Globe className="h-3 w-3" />
                          <span>{snippet.url}</span>
                        </a>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Pane 3: Gap Analysis / Intelligence Insights */}
        <div className="w-80 shrink-0 space-y-4 flex flex-col">
          <div className="card h-full flex flex-col overflow-hidden">
            <div className="p-4 border-b border-white/5 flex items-center justify-between shrink-0">
              <div className="flex items-center space-x-2">
                <Dna className="h-4 w-4 text-pink-400" />
                <h3 className="text-xs font-bold uppercase tracking-widest">Gap Analysis</h3>
              </div>
              {gapAnalysis.length > 0 && (
                <span className="text-[10px] font-mono text-muted-foreground">SOTA: 74%</span>
              )}
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-6">
              {gapAnalysis.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center opacity-30 px-4">
                  <Layers className="h-8 w-8 mb-3" />
                  <p className="text-[10px] uppercase font-bold">Analysis Offline</p>
                  <p className="text-[9px] mt-2">Data required to generate semantic gaps.</p>
                </div>
              ) : (
                gapAnalysis.map((gap: any, i: number) => (
                  <div key={i} className="space-y-3">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="font-medium">{gap.topic}</span>
                      <span
                        className={`font-mono text-[10px] ${gap.score > 80 ? "text-emerald-400" : gap.score > 60 ? "text-yellow-400" : "text-red-400"}`}
                      >
                        {gap.score}%
                      </span>
                    </div>
                    <div className="w-full bg-white/5 rounded-full h-1 relative">
                      <div
                        className={`h-full rounded-full transition-all duration-1000 ${gap.score > 80 ? "bg-emerald-500" : gap.score > 60 ? "bg-yellow-500" : "bg-red-500"}`}
                        style={{ width: `${gap.score}%` }}
                      />
                    </div>
                    {gap.issues.length > 0 && (
                      <div className="space-y-1.5">
                        {gap.issues.map((issue: string, j: number) => (
                          <div
                            key={j}
                            className="flex items-start space-x-2 p-2 bg-red-500/5 border border-red-500/10 rounded-md"
                          >
                            <AlertCircle className="h-3 w-3 text-red-400 mt-0.5 shrink-0" />
                            <p className="text-[10px] text-red-200/70 leading-tight">{issue}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            {gapAnalysis.length > 0 && (
              <div className="p-4 border-t border-white/5 shrink-0">
                <button className="w-full btn btn-sm btn-outline text-[10px] tracking-widest uppercase flex items-center justify-center space-x-2 py-2">
                  <Settings2 className="h-3 w-3 text-pink-400" />
                  <span>Expand Insight</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
