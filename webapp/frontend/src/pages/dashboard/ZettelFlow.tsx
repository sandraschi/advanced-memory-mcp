import {
  Archive,
  ArrowUpRight,
  FileText,
  Hash,
  Inbox,
  Link as LinkIcon,
  Loader2,
  Plus,
  Trash2,
} from "lucide-react";
import { useEffect, useState } from "react";
import { devError } from "../../devConsole";
import { apiService } from "../../services/api";

interface Note {
  name: string;
  path: string;
  identifier?: string; // Sometimes name is identifier
  content?: string;
}

export default function ZettelFlow() {
  const [inboxNotes, setInboxNotes] = useState<Note[]>([]);
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [noteContent, setNoteContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [linkTarget, setLinkTarget] = useState("");
  const [zettelId, setZettelId] = useState("");

  useEffect(() => {
    fetchInbox();
  }, []);

  const fetchInbox = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiService.getBaseUrl()}/zettel/inbox`);
      const data = await res.json();
      if (data.success && Array.isArray(data.data)) {
        // Handle different return shapes from adn_knowledge list
        const notes = data.data.map((item: any) => ({
          name: item.name || item.t || item,
          path: item.path || "",
          identifier: item.identifier || item.name || item,
        }));
        setInboxNotes(notes);
      }
    } catch (e) {
      devError("Failed to fetch inbox", e);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectNote = async (note: Note) => {
    setSelectedNote(note);
    setProcessing(true);
    try {
      const res = await apiService.getNote(note.identifier || note.name);
      if (res.success && res.data) {
        setNoteContent(res.data.content ?? "");
      }
    } catch (e) {
      console.error("Failed to load note content", e);
    } finally {
      setProcessing(false);
    }
  };

  const generateZettelId = () => {
    const now = new Date();
    const id = now
      .toISOString()
      .replace(/[-:T.]/g, "")
      .slice(0, 14);
    setZettelId(id);
  };

  const handlePromote = async () => {
    if (!selectedNote) return;
    setProcessing(true);
    try {
      const res = await fetch(`${apiService.getBaseUrl()}/zettel/promote`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          identifier: selectedNote.identifier || selectedNote.name,
          destination: "Zettelkasten",
        }),
      });
      const data = await res.json();
      if (data.success) {
        // Remove from local list and clear selection
        setInboxNotes((prev) => prev.filter((n) => n.name !== selectedNote.name));
        setSelectedNote(null);
        setNoteContent("");
      }
    } catch (e) {
      console.error("Failed to promote note", e);
    } finally {
      setProcessing(false);
    }
  };

  const handleLink = async () => {
    if (!selectedNote || !linkTarget) return;
    setProcessing(true);
    try {
      const res = await fetch(`${apiService.getBaseUrl()}/zettel/link`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_id: selectedNote.identifier || selectedNote.name,
          target_id: linkTarget,
          type: "bidirectional",
        }),
      });
      const data = await res.json();
      if (data.success) {
        // Refresh content to show new link
        handleSelectNote(selectedNote);
        setLinkTarget("");
      }
    } catch (e) {
      console.error("Failed to link note", e);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="h-[calc(100vh-6rem)] grid grid-cols-12 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Inbox Panel (Left) */}
      <div className="col-span-4 bg-[#111] rounded-xl border border-white/10 flex flex-col overflow-hidden">
        <div className="p-4 border-b border-white/10 flex justify-between items-center bg-[#161616]">
          <div className="flex items-center gap-2 text-emerald-400">
            <Inbox className="w-5 h-5" />
            <h2 className="font-semibold">Inbox</h2>
          </div>
          <span className="text-xs text-zinc-500 bg-zinc-900 px-2 py-1 rounded-full">
            {inboxNotes.length} notes
          </span>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {loading ? (
            <div className="flex justify-center p-8 text-zinc-500">
              <Loader2 className="w-6 h-6 animate-spin" />
            </div>
          ) : inboxNotes.length === 0 ? (
            <div className="text-center p-8 text-zinc-600 italic">Inbox is empty</div>
          ) : (
            inboxNotes.map((note) => (
              <button
                key={note.name}
                onClick={() => handleSelectNote(note)}
                className={`w-full text-left p-3 rounded-lg border transition-all duration-200 group relative
                  ${
                    selectedNote?.name === note.name
                      ? "bg-emerald-500/10 border-emerald-500/50 text-emerald-100"
                      : "bg-zinc-900/50 border-white/5 text-zinc-400 hover:bg-zinc-800 hover:border-white/10"
                  }`}
              >
                <div className="flex items-start gap-3">
                  <FileText
                    className={`w-4 h-4 mt-1 ${selectedNote?.name === note.name ? "text-emerald-400" : "text-zinc-600"}`}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">{note.name}</div>
                    <div className="text-xs text-zinc-600 truncate mt-1 font-mono">
                      ID: {note.identifier || note.name.replace(/\.md$/, "")}
                    </div>
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Main Workspace (Center/Right) */}
      <div className="col-span-8 bg-[#111] rounded-xl border border-white/10 flex flex-col overflow-hidden">
        {selectedNote ? (
          <>
            <div className="p-4 border-b border-white/10 flex justify-between items-center bg-[#161616]">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-400">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="font-semibold text-white">{selectedNote.name}</h2>
                  <div className="text-xs text-zinc-500 flex items-center gap-2">
                    <span>Inbox Note</span>
                    <span>•</span>
                    <span className="font-mono">{selectedNote.identifier}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handlePromote}
                  disabled={processing}
                  className="flex items-center gap-2 px-3 py-1.5 bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 border border-indigo-500/30 rounded-lg transition-colors text-sm font-medium"
                  aria-label="Promote to Zettelkasten"
                >
                  {processing ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Archive className="w-4 h-4" />
                  )}
                  Promote to Zettelkasten
                </button>
                <button
                  className="p-2 text-zinc-400 hover:text-white hover:bg-white/10 rounded-lg"
                  aria-label="Delete Note"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 gap-6">
              {/* Content Preview */}
              <div className="space-y-2">
                <label className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">
                  Note Content
                </label>
                <div className="bg-zinc-900/50 border border-white/5 rounded-lg p-4 font-mono text-sm text-zinc-300 whitespace-pre-wrap min-h-[200px]">
                  {noteContent || <span className="text-zinc-600 italic">Loading content...</span>}
                </div>
              </div>

              {/* Linking Engine */}
              <div className="grid grid-cols-2 gap-6">
                {/* Zettel ID Generator */}
                <div className="space-y-3 p-4 bg-zinc-900/30 rounded-xl border border-white/5">
                  <label className="text-xs font-semibold text-zinc-500 uppercase tracking-wider flex items-center gap-2">
                    <Hash className="w-3 h-3" /> Zettel Identification
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={zettelId}
                      readOnly
                      placeholder="Generate ID..."
                      className="flex-1 bg-black/50 border border-white/10 rounded-lg px-3 py-2 text-sm font-mono text-emerald-400"
                    />
                    <button
                      onClick={generateZettelId}
                      className="px-3 py-2 bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 border border-emerald-500/30 rounded-lg transition-colors"
                      aria-label="Generate Zettel ID"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                  <p className="text-xs text-zinc-600">
                    Standardized Zettel ID based on current timestamp (YYYYMMDDHHMMSS)
                  </p>
                </div>

                {/* Linker */}
                <div className="space-y-3 p-4 bg-zinc-900/30 rounded-xl border border-white/5">
                  <label className="text-xs font-semibold text-zinc-500 uppercase tracking-wider flex items-center gap-2">
                    <LinkIcon className="w-3 h-3" /> Bidirectional Linking
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={linkTarget}
                      onChange={(e) => setLinkTarget(e.target.value)}
                      placeholder="Target Note ID..."
                      className="flex-1 bg-black/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-zinc-700 focus:outline-none focus:border-emerald-500/50"
                    />
                    <button
                      onClick={handleLink}
                      disabled={!linkTarget || processing}
                      className="px-3 py-2 bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 border border-blue-500/30 rounded-lg transition-colors disabled:opacity-50"
                      aria-label="Create Link"
                    >
                      <ArrowUpRight className="w-4 h-4" />
                    </button>
                  </div>
                  <p className="text-xs text-zinc-600">
                    Creates a `[[link]]` in both this note and the target note.
                  </p>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-zinc-500 space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-zinc-900 border border-white/5 flex items-center justify-center">
              <Inbox className="w-8 h-8 text-zinc-700" />
            </div>
            <p>Select a note from the inbox to begin processing</p>
            <button
              onClick={fetchInbox}
              className="text-sm text-emerald-500 hover:text-emerald-400 flex items-center gap-2"
              aria-label="Refresh Inbox"
            >
              Refresh Inbox
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
