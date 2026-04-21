import {
  BookOpen,
  ChevronRight,
  Hash,
  Layers,
  Link as LinkIcon,
  Plus,
  Save,
  Search,
  Tag,
  Trash2,
} from "lucide-react";
import { useState } from "react";

interface Zettel {
  id: string;
  title: string;
  content: string;
  tags: string[];
  links: string[];
  timestamp: string;
}

export default function ZettelMaster() {
  const [zettels, setZettels] = useState<Zettel[]>([
    {
      id: "1",
      title: "The Materialist Approach to Memory",
      content:
        "Memory is not a ghostly storage but a physical reconfiguration of neural substrates.",
      tags: ["philosophy", "neuroscience"],
      links: ["2"],
      timestamp: "2026-02-17",
    },
    {
      id: "2",
      title: "MCP Implementation in Rust",
      content: "FastMCP provides the necessary abstractions for high-performance agentic tools.",
      tags: ["dev", "mcp", "rust"],
      links: ["1"],
      timestamp: "2026-02-16",
    },
  ]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editContent, setEditContent] = useState("");
  const [editTags, setEditTags] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  const selectedZettel = zettels.find((z) => z.id === selectedId);

  const handleSelect = (z: Zettel) => {
    setSelectedId(z.id);
    setEditTitle(z.title);
    setEditContent(z.content);
    setEditTags(z.tags.join(", "));
  };

  const handleNew = () => {
    const newZ: Zettel = {
      id: Date.now().toString(),
      title: "New Zettel",
      content: "",
      tags: [],
      links: [],
      timestamp: new Date().toISOString().slice(0, 10),
    };
    setZettels([newZ, ...zettels]);
    handleSelect(newZ);
  };

  const handleSave = () => {
    if (!selectedId) return;
    setZettels((prev) =>
      prev.map((z) =>
        z.id === selectedId
          ? {
              ...z,
              title: editTitle,
              content: editContent,
              tags: editTags
                .split(",")
                .map((t) => t.trim())
                .filter(Boolean),
            }
          : z,
      ),
    );
  };

  const handleDelete = (id: string) => {
    setZettels((prev) => prev.filter((z) => z.id !== id));
    if (selectedId === id) setSelectedId(null);
  };

  const filteredZettels = zettels.filter(
    (z) =>
      z.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      z.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      z.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase())),
  );

  return (
    <div className="max-w-[1400px] mx-auto h-[calc(100vh-12rem)] flex flex-col space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header */}
      <div className="flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-gradient-to-br from-emerald-500/20 to-teal-500/20 rounded-xl">
            <BookOpen className="h-6 w-6 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Zettelkasten Workflow</h1>
            <p className="text-muted-foreground text-xs">
              Structured note-making with bidirectional semantic mapping
            </p>
          </div>
        </div>
        <button
          onClick={handleNew}
          className="btn btn-primary flex items-center space-x-2 shadow-lg shadow-emerald-500/20"
        >
          <Plus className="h-4 w-4" />
          <span>Create Zettel</span>
        </button>
      </div>

      {/* Main Content Areas */}
      <div className="flex-1 flex space-x-6 overflow-hidden min-h-0">
        {/* Sidebar: Note List */}
        <div className="w-80 shrink-0 flex flex-col space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Find zettels..."
              className="w-full bg-muted/20 border border-white/5 rounded-lg pl-9 pr-3 py-2 text-sm outline-none focus:ring-1 focus:ring-emerald-500/30"
            />
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 pr-1 scrollbar-thin">
            {filteredZettels.map((z) => (
              <button
                key={z.id}
                onClick={() => handleSelect(z)}
                className={`w-full text-left p-4 rounded-xl border transition-all group ${
                  selectedId === z.id
                    ? "bg-emerald-500/10 border-emerald-500/30"
                    : "bg-muted/10 border-white/5 hover:border-white/10 hover:bg-white/5"
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3
                    className={`font-semibold text-sm truncate ${selectedId === z.id ? "text-emerald-400" : "text-foreground"}`}
                  >
                    {z.title}
                  </h3>
                  <span className="text-[9px] text-muted-foreground font-mono">{z.timestamp}</span>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2 mb-3 leading-relaxed">
                  {z.content}
                </p>
                <div className="flex flex-wrap gap-1">
                  {z.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="text-[9px] px-1.5 py-0.5 rounded-full bg-white/5 border border-white/5 text-muted-foreground"
                    >
                      #{tag}
                    </span>
                  ))}
                  {z.tags.length > 3 && (
                    <span className="text-[9px] text-muted-foreground/50">
                      +{z.tags.length - 3}
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Editor Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {selectedId ? (
            <div className="h-full flex flex-col space-y-4">
              <div className="card flex-1 flex flex-col overflow-hidden p-0">
                {/* Title Editor */}
                <div className="p-6 border-b border-white/5 flex items-center justify-between shrink-0">
                  <input
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    placeholder="Zettel Title..."
                    className="bg-transparent text-xl font-bold outline-none flex-1 min-w-0"
                  />
                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      onClick={handleSave}
                      className="p-2 hover:bg-emerald-500/10 text-emerald-400 rounded-lg transition-colors"
                      title="Save changes"
                    >
                      <Save className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => handleDelete(selectedId)}
                      className="p-2 hover:bg-red-500/10 text-red-400 rounded-lg transition-colors"
                      title="Delete zettel"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>

                {/* content Editor */}
                <div className="flex-1 flex flex-col min-h-0">
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    placeholder="Start mapping your thoughts..."
                    className="flex-1 w-full bg-transparent p-6 outline-none resize-none font-serif text-lg leading-relaxed text-muted-foreground/90 scrollbar-thin"
                  />
                </div>

                {/* Tag Editor Footer */}
                <div className="p-4 bg-muted/5 border-t border-white/5 flex items-center space-x-3 shrink-0">
                  <Tag className="h-4 w-4 text-muted-foreground" />
                  <input
                    value={editTags}
                    onChange={(e) => setEditTags(e.target.value)}
                    placeholder="Add tags separated by commas..."
                    className="bg-transparent text-xs text-muted-foreground flex-1 outline-none"
                  />
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full card flex flex-col items-center justify-center text-center opacity-50 grayscale select-none">
              <Layers className="h-16 w-16 text-muted-foreground mb-4" />
              <h3 className="text-xl font-bold">Loom of Thoughts</h3>
              <p className="text-sm max-w-sm mt-2">
                Select a zettel to edit or create a new one to begin your semantic journey.
              </p>
            </div>
          )}
        </div>

        {/* Right Pane: Bi-links & Graph Meta (Placeholder) */}
        <div className="w-80 shrink-0 space-y-4 flex flex-col">
          <div className="card flex-1 flex flex-col overflow-hidden">
            <div className="p-4 border-b border-white/5 flex items-center justify-between shrink-0">
              <div className="flex items-center space-x-2">
                <LinkIcon className="h-4 w-4 text-emerald-400" />
                <h3 className="text-xs font-bold uppercase tracking-widest">Bi-links</h3>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {selectedId && selectedZettel?.links.length ? (
                selectedZettel.links.map((linkId) => {
                  const linkedZ = zettels.find((z) => z.id === linkId);
                  if (!linkedZ) return null;
                  return (
                    <button
                      key={linkId}
                      onClick={() => handleSelect(linkedZ)}
                      className="w-full text-left p-3 bg-white/5 border border-white/5 rounded-lg hover:border-emerald-500/20 transition-all group"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] uppercase font-bold text-emerald-400">
                          Linked Note
                        </span>
                        <ChevronRight className="h-3 w-3 text-muted-foreground group-hover:translate-x-1 transition-transform" />
                      </div>
                      <h4 className="text-xs font-semibold truncate">{linkedZ.title}</h4>
                    </button>
                  );
                })
              ) : (
                <div className="h-full flex flex-col items-center justify-center opacity-30 text-center">
                  <Hash className="h-8 w-8 mb-2" />
                  <p className="text-[10px] uppercase font-bold">No Connections</p>
                  <p className="text-[9px] mt-2">Add [[links]] to create bidirectional mapping.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
