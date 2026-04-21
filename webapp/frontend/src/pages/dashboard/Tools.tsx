import {
  Activity,
  Box,
  ChevronRight,
  Cpu,
  Info,
  Loader2,
  Search,
  Shield,
  Sparkles,
  Terminal,
  Zap,
} from "lucide-react";
import { useEffect, useState } from "react";
import { apiService } from "../../services/api";

// ToolHelp and ToolCategory are actually parsed from helpContent markdown now

export default function Tools() {
  const [helpContent, setHelpContent] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTool, setSelectedTool] = useState<string | null>(null);

  const fetchHelp = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.callMCPTool("help", {
        topic: "tools",
        level: "intermediate",
      });
      if (response.success && response.data?.result?.help_content) {
        setHelpContent(response.data.result.help_content);
      }
    } catch (error) {
      console.error("Failed to fetch tool help:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHelp();
  }, []);

  const parseHelpContent = (content: string) => {
    // Simple parser for the markdown help content
    const sections: { title: string; content: string }[] = [];
    if (!content) return sections;

    const toolMatches = content.matchAll(/### (.*?)\n([\s\S]*?)(?=### |## |$)/g);

    for (const match of toolMatches) {
      if (match[1] && match[2]) {
        sections.push({
          title: match[1],
          content: match[2].trim(),
        });
      }
    }
    return sections;
  };

  const tools = parseHelpContent(helpContent);

  return (
    <div className="flex flex-col h-full bg-background overflow-hidden relative animate-in fade-in duration-700">
      {/* Header */}
      <div className="px-10 py-8 border-b border-white/5 bg-black/40 backdrop-blur-xl flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-white/5 border border-white/10 rounded-2xl shadow-indigo-500/10 shadow-2xl">
            <Terminal className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-white">
              Advanced Memory Tools
            </h1>
            <p className="text-sm text-white/40 mt-1">
              Interactive Command Documentation & System Insights
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <button
            onClick={fetchHelp}
            title="Refresh Documentation"
            aria-label="Refresh Documentation"
            className="p-2.5 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-all font-medium text-white/70"
          >
            <Activity className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          </button>
          <div className="h-8 w-px bg-white/10" />
          <div className="p-1 bg-white/5 border border-white/10 rounded-xl flex items-center text-xs font-medium">
            <span className="px-3 py-1.5 text-white/40 uppercase tracking-widest">
              SOTA Core 1.0
            </span>
          </div>
        </div>
      </div>

      {/* Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 border-r border-white/5 bg-black/20 flex flex-col">
          <div className="p-6">
            <div className="relative group">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition duration-1000 group-hover:duration-200" />
              <div className="relative flex items-center px-4 py-2 bg-white/2 overflow-hidden border border-white/5 rounded-xl">
                <Search className="h-4 w-4 text-white/30 mr-3" />
                <input
                  type="text"
                  placeholder="Filter tools..."
                  className="bg-transparent border-none focus:ring-0 text-sm placeholder:text-white/20 w-full text-white/80"
                />
              </div>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto px-4 pb-8 custom-scrollbar">
            <div className="space-y-1">
              {tools.map((tool) => (
                <button
                  key={tool.title}
                  onClick={() => setSelectedTool(tool.title)}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all group ${
                    selectedTool === tool.title
                      ? "bg-white/5 border border-white/10 text-white shadow-xl translate-x-1"
                      : "text-white/40 hover:text-white/80 hover:bg-white/2 border border-transparent"
                  }`}
                >
                  <div className="flex items-center">
                    <div
                      className={`p-1.5 rounded-lg mr-3 ${selectedTool === tool.title ? "bg-indigo-500/10" : "bg-white/5"}`}
                    >
                      <Loader2
                        className={`h-3.5 w-3.5 ${selectedTool === tool.title ? "text-indigo-400" : "text-white/20"}`}
                      />
                    </div>
                    <span className="text-sm font-medium">{tool.title}</span>
                  </div>
                  <ChevronRight
                    className={`h-3.5 w-3.5 transition-transform duration-300 ${selectedTool === tool.title ? "rotate-90 text-indigo-400" : "opacity-0 -translate-x-2"}`}
                  />
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto bg-black/10 custom-scrollbar relative">
          {selectedTool ? (
            <div className="max-w-4xl mx-auto p-12 animate-in slide-in-from-bottom-4 duration-500">
              <div className="mb-12">
                <div className="flex items-center space-x-2 text-indigo-400 text-xs font-bold uppercase tracking-widest mb-4">
                  <Sparkles className="h-4 w-4" />
                  <span>Advanced Memory Protocol Integration</span>
                </div>
                <h1 className="text-5xl font-bold text-white tracking-tight mb-6">
                  {selectedTool}
                </h1>
                <div className="prose prose-invert max-w-none text-white/60 leading-relaxed text-lg whitespace-pre-wrap">
                  {tools.find((t) => t.title === selectedTool)?.content}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6 pt-12 border-t border-white/5">
                <div className="p-8 rounded-3xl bg-white/3 border border-indigo-500/10 relative group overflow-hidden">
                  <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                    <Box className="h-24 w-24 text-white" />
                  </div>
                  <h3 className="text-white font-medium mb-3 flex items-center">
                    <Info className="h-4 w-4 mr-2 text-indigo-400" />
                    Technical Context
                  </h3>
                  <p className="text-sm text-white/30 leading-relaxed">
                    This tool is part of the core Advanced Memory portmanteau architecture,
                    optimized for high-performance knowledge retrieval and session persistence.
                  </p>
                </div>
                <div className="p-8 rounded-3xl bg-gradient-to-br from-indigo-500/5 to-purple-500/5 border border-white/5 relative group overflow-hidden">
                  <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                    <Cpu className="h-24 w-24 text-white" />
                  </div>
                  <h3 className="text-white font-medium mb-3 flex items-center">
                    <Zap className="h-4 w-4 mr-2 text-yellow-400" />
                    Performance Note
                  </h3>
                  <p className="text-sm text-white/30 leading-relaxed">
                    Optimized for Windows 11 Pro environments with AMD Ryzen 24-core processing
                    power. Sub-100ms latency execution target.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center p-12 text-center opacity-40">
              <div className="p-8 bg-white/5 border border-white/10 rounded-[2.5rem] mb-8 relative">
                <div className="absolute inset-0 bg-indigo-500/20 blur-3xl rounded-full" />
                <Shield className="h-16 w-16 text-white relative z-10" />
              </div>
              <h2 className="text-3xl font-light text-white tracking-tight mb-4">
                Select a tool to explore
              </h2>
              <p className="max-w-md text-white/40 leading-relaxed">
                Explore the complete Advanced Memory MCP command suite documentation. Select any
                module from the navigation to view parameters and examples.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
