import {
  ArrowDownLeft,
  ArrowUpRight,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  Copy,
  Download,
  FileText,
  Link,
  Tag,
  Trash2,
  Zap,
} from "lucide-react";
import { useEffect, useState } from "react";
import { apiService } from "../../services/api";
import { confirmAndDeleteNote } from "../notes/noteActions";
import { type ExportFormat, downloadNote, emitVault, extractWikiLinks } from "../notes/noteUtils";

interface NoteMetadata {
  id: string;
  title: string;
  tags?: string[];
  created: string;
  modified: string;
  wordCount: number;
  connections: number;
  backlinks: number;
  readingTime: number;
  fileSize: string;
  /** Raw markdown, needed here to list this note's own outgoing [[wikilinks]]. */
  content?: string;
}

interface MetadataSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  note?: NoteMetadata | null;
  onDelete?: (() => void) | undefined;
}

interface ConnectionRow {
  id: string;
  label: string;
  direction: "outgoing" | "incoming";
  /** "written" = a [[wikilink]] in this note's own text, not yet checked against the index.
   *  "relation" = a stored relation row. "backlink" = another note whose stored relation points here (exact, from the index). */
  kind: "written" | "relation" | "backlink";
}

export default function MetadataSidebar({
  isOpen,
  onToggle,
  note,
  onDelete,
}: MetadataSidebarProps) {
  const [activeTab, setActiveTab] = useState<"metadata" | "connections" | "actions">("metadata");
  const [exportMessage, setExportMessage] = useState<string>("");
  const [connections, setConnections] = useState<ConnectionRow[]>([]);
  const [connectionsLoading, setConnectionsLoading] = useState(false);
  const [connectionsError, setConnectionsError] = useState("");
  const [copyFeedback, setCopyFeedback] = useState("");
  const [deleting, setDeleting] = useState(false);

  // Load real connections whenever the selected note changes - a wikilink this
  // note's own text points at, a stored relation on either side, and (as a
  // best-effort fallback) other notes whose full text appears to mention this
  // one. There is no single "connections" endpoint on the backend, so this
  // merges three different, imperfect sources rather than faking one tidy list.
  useEffect(() => {
    const noteId = note?.id;
    const noteContent = note?.content ?? "";
    if (!noteId) {
      setConnections([]);
      setConnectionsError("");
      return;
    }
    let cancelled = false;
    setConnectionsLoading(true);
    setConnectionsError("");

    const written: ConnectionRow[] = extractWikiLinks(noteContent).map((link) => ({
      id: link.target,
      label: link.label,
      direction: "outgoing" as const,
      kind: "written" as const,
    }));

    (async () => {
      const [relRes, backRes] = await Promise.all([
        apiService.getNoteRelations(noteId),
        apiService.getBacklinks(noteId),
      ]);
      if (cancelled) return;

      const rows: ConnectionRow[] = [...written];
      let hadError = false;

      if (relRes.success && Array.isArray(relRes.data)) {
        for (const rel of relRes.data) {
          if (rel.from_id === noteId) {
            rows.push({
              id: rel.to_id,
              label: `${rel.relation_type} -> ${rel.to_id}`,
              direction: "outgoing",
              kind: "relation",
            });
          } else if (rel.to_id === noteId) {
            rows.push({
              id: rel.from_id,
              label: `${rel.from_id} ${rel.relation_type}`,
              direction: "incoming",
              kind: "relation",
            });
          }
        }
      } else {
        hadError = true;
      }

      if (backRes.success && Array.isArray(backRes.data)) {
        for (const b of backRes.data) {
          if (b.permalink === noteId) continue;
          rows.push({
            id: b.permalink,
            label: b.title || b.permalink,
            direction: "incoming",
            kind: "backlink",
          });
        }
      } else {
        hadError = true;
      }

      // De-dupe same id+direction (a relation and a mention can point at the same note).
      const seen = new Set<string>();
      const deduped = rows.filter((r) => {
        const key = `${r.direction}:${r.id}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });

      setConnections(deduped);
      setConnectionsError(
        hadError
          ? "Could not load all link data (is the API restarted with the backlinks route?); showing what is available."
          : "",
      );
      setConnectionsLoading(false);
    })();

    return () => {
      cancelled = true;
    };
  }, [note?.id, note?.content]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const exportFormats: Array<{ id: ExportFormat; label: string }> = [
    { id: "markdown", label: "Markdown (.md)" },
    { id: "html", label: "HTML (.html)" },
    { id: "pdf", label: "PDF (print dialog)" },
    { id: "json", label: "JSON (.json)" },
    { id: "txt", label: "Plain Text (.txt)" },
  ];

  const runExport = (format: (typeof exportFormats)[number]) => {
    if (!note) return;
    if (!note.content) {
      setExportMessage("Failed: note body is not loaded yet");
    } else {
      const err = downloadNote(format.id, {
        id: note.id,
        title: note.title,
        content: note.content,
        ...(note.tags ? { tags: note.tags } : {}),
        created: note.created,
        modified: note.modified,
      });
      setExportMessage(err ? `Failed: ${err}` : `Exported as ${format.label}`);
    }
    window.setTimeout(() => setExportMessage(""), 5000);
  };

  const handleCopyPermalink = async () => {
    if (!note) return;
    try {
      await navigator.clipboard.writeText(note.id);
      setCopyFeedback("Copied");
    } catch {
      setCopyFeedback("Copy failed");
    }
    window.setTimeout(() => setCopyFeedback(""), 1500);
  };

  const handleDelete = async () => {
    if (!note || deleting) return;
    setDeleting(true);
    try {
      const result = await confirmAndDeleteNote(note.id, note.title);
      if (result.deleted) {
        onDelete?.();
      } else if (result.error) {
        window.alert(result.error);
      }
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div
      className={`
      relative bg-card border-l border-border flex flex-col transition-all duration-300 ease-in-out
      ${isOpen ? "w-80" : "w-0"}
    `}
    >
      {/* Toggle Button */}
      <button
        type="button"
        onClick={onToggle}
        className="absolute top-20 -left-10 z-10 p-2 bg-card border border-border rounded-l-md hover:bg-muted transition-colors"
        title={isOpen ? "Close metadata panel" : "Open metadata panel"}
      >
        {isOpen ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
      </button>

      {isOpen && (
        <>
          {/* Header */}
          <div className="p-4 border-b border-border">
            <h2 className="font-semibold">Note Metadata</h2>
            {note && (
              <p className="text-sm text-muted-foreground mt-1 truncate" title={note.title}>
                {note.title}
              </p>
            )}
          </div>

          {/* Tabs */}
          <div className="flex border-b border-border">
            {[
              { id: "metadata", label: "Metadata", icon: FileText },
              { id: "connections", label: "Connections", icon: Link },
              { id: "actions", label: "Actions", icon: Zap },
            ].map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id as typeof activeTab)}
                className={`flex-1 flex items-center justify-center p-3 text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? "bg-accent text-accent-foreground border-b-2 border-accent"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                }`}
              >
                <tab.icon className="h-4 w-4 mr-2" />
                {tab.label}
              </button>
            ))}
          </div>

          {/* Content */}
          <div className="flex-1 overflow-auto">
            {activeTab === "metadata" && note && (
              <div className="p-4 space-y-6">
                {/* Basic Info */}
                <div>
                  <h3 className="font-medium mb-3 flex items-center">
                    <FileText className="h-4 w-4 mr-2" />
                    Basic Information
                  </h3>
                  <div className="space-y-3 text-sm">
                    <div>
                      <span className="text-muted-foreground">Created:</span>
                      <div className="font-medium">{formatDate(note.created)}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Modified:</span>
                      <div className="font-medium">{formatDate(note.modified)}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Word Count:</span>
                      <div className="font-medium">{note.wordCount.toLocaleString()}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">File Size:</span>
                      <div className="font-medium">{note.fileSize}</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Reading Time:</span>
                      <div className="font-medium">~{note.readingTime} min</div>
                    </div>
                  </div>
                </div>

                {/* Tags */}
                <div>
                  <h3 className="font-medium mb-3 flex items-center">
                    <Tag className="h-4 w-4 mr-2" />
                    Tags ({Array.isArray(note.tags) ? note.tags.length : 0})
                  </h3>
                  {Array.isArray(note.tags) && note.tags.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {note.tags.map((tag) => (
                        <span
                          key={tag}
                          className="px-2 py-1 bg-accent/20 text-accent text-xs rounded-md"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">No tags</p>
                  )}
                </div>

                {/* Statistics */}
                <div>
                  <h3 className="font-medium mb-3 flex items-center">
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Statistics
                  </h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="text-center p-3 bg-muted/50 rounded-md">
                      <div className="text-lg font-bold text-accent">
                        {connections.filter((c) => c.direction === "outgoing").length}
                      </div>
                      <div className="text-xs text-muted-foreground">Outgoing Links</div>
                    </div>
                    <div className="text-center p-3 bg-muted/50 rounded-md">
                      <div className="text-lg font-bold text-accent">
                        {connections.filter((c) => c.direction === "incoming").length}
                      </div>
                      <div className="text-xs text-muted-foreground">Backlinks</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "connections" && note && (
              <div className="p-4">
                <h3 className="font-medium mb-4 flex items-center">
                  <Link className="h-4 w-4 mr-2" />
                  Note Connections
                </h3>

                {connectionsLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-accent" />
                  </div>
                ) : (
                  <>
                    {connectionsError && (
                      <p className="text-xs text-amber-500 mb-3">{connectionsError}</p>
                    )}
                    <div className="space-y-2">
                      {connections.map((conn) => (
                        <button
                          type="button"
                          key={`${conn.direction}:${conn.id}`}
                          onClick={() => emitVault({ type: "open", id: conn.id })}
                          className="w-full text-left flex items-start gap-3 p-2 rounded-md hover:bg-muted/50"
                          title={`Open ${conn.id}`}
                        >
                          {conn.direction === "outgoing" ? (
                            <ArrowUpRight className="h-4 w-4 mt-0.5 text-green-500 shrink-0" />
                          ) : (
                            <ArrowDownLeft className="h-4 w-4 mt-0.5 text-blue-500 shrink-0" />
                          )}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{conn.label}</p>
                            <p className="text-xs text-muted-foreground capitalize">
                              {conn.direction}
                              {conn.kind === "written" ? " · link in this note" : ""}
                              {conn.kind === "backlink" ? " · backlink" : ""}
                            </p>
                          </div>
                        </button>
                      ))}
                    </div>

                    {connections.length === 0 && (
                      <p className="text-sm text-muted-foreground text-center py-8">
                        No connections found
                      </p>
                    )}
                  </>
                )}
              </div>
            )}

            {activeTab === "actions" && note && (
              <div className="p-4 space-y-6">
                {/* Quick Actions */}
                <div>
                  <h3 className="font-medium mb-3 flex items-center">
                    <Zap className="h-4 w-4 mr-2" />
                    Quick Actions
                  </h3>
                  <div className="space-y-2">
                    <button
                      type="button"
                      onClick={handleCopyPermalink}
                      className="w-full flex items-center space-x-2 p-2 rounded-md hover:bg-muted transition-colors text-left"
                    >
                      <Copy className="h-4 w-4" />
                      <span className="text-sm">{copyFeedback || "Copy Permalink"}</span>
                    </button>
                  </div>
                </div>

                {/* Export Options */}
                <div>
                  <h3 className="font-medium mb-3 flex items-center">
                    <Download className="h-4 w-4 mr-2" />
                    Export Note
                  </h3>
                  {exportMessage && (
                    <div
                      className={`mb-3 p-2 rounded-md text-sm ${
                        exportMessage.startsWith("Failed")
                          ? "bg-red-500/10 text-red-400 border border-red-500/20"
                          : "bg-green-500/10 text-green-400 border border-green-500/20"
                      }`}
                    >
                      {exportMessage}
                    </div>
                  )}
                  <div className="space-y-2">
                    {exportFormats.map((format) => (
                      <button
                        key={format.id}
                        type="button"
                        onClick={() => runExport(format)}
                        className="w-full flex items-center space-x-2 p-2 rounded-md hover:bg-muted transition-colors text-left disabled:opacity-50"
                      >
                        <span className="text-sm">{format.label}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Danger Zone */}
                <div className="border-t border-border pt-4">
                  <h3 className="font-medium mb-3 text-red-500 flex items-center">
                    <Trash2 className="h-4 w-4 mr-2" />
                    Danger Zone
                  </h3>
                  <button
                    type="button"
                    onClick={handleDelete}
                    disabled={deleting}
                    className="w-full flex items-center space-x-2 p-2 rounded-md hover:bg-red-500/10 hover:text-red-500 transition-colors text-left text-red-500 disabled:opacity-50"
                  >
                    <Trash2 className="h-4 w-4" />
                    <span className="text-sm">{deleting ? "Deleting..." : "Delete Note"}</span>
                  </button>
                </div>
              </div>
            )}

            {!note && (
              <div className="flex items-center justify-center h-full text-center p-8">
                <div>
                  <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="font-medium mb-2">No Note Selected</h3>
                  <p className="text-sm text-muted-foreground">
                    Select a note to view its metadata and connections.
                  </p>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
