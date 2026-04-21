import {
  BarChart3,
  ChevronLeft,
  ChevronRight,
  Download,
  Edit,
  Eye,
  FileText,
  Link,
  Share,
  Tag,
  Trash2,
  Zap,
} from "lucide-react";
import { useState } from "react";

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
}

interface MetadataSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  note?: NoteMetadata | null;
  onExport?: ((format: string, noteId: string) => Promise<void>) | undefined;
  onEdit?: (() => void) | undefined;
  onDelete?: (() => void) | undefined;
}

export default function MetadataSidebar({
  isOpen,
  onToggle,
  note,
  onExport,
  onEdit,
  onDelete,
}: MetadataSidebarProps) {
  const [activeTab, setActiveTab] = useState<"metadata" | "connections" | "actions">("metadata");
  const [exportLoading, setExportLoading] = useState<string | null>(null);
  const [exportMessage, setExportMessage] = useState<string>("");

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const exportFormats = [
    { id: "markdown", label: "Markdown (.md)", icon: "📝" },
    { id: "html", label: "HTML (.html)", icon: "🌐" },
    { id: "pdf", label: "PDF (.pdf)", icon: "📄" },
    { id: "json", label: "JSON (.json)", icon: "💾" },
    { id: "txt", label: "Plain Text (.txt)", icon: "📄" },
  ];

  const mockConnections = [
    { id: "1", title: "Brain Surgery Techniques", type: "outgoing" },
    { id: "2", title: "Chemotherapy Protocols", type: "outgoing" },
    { id: "3", title: "Patient Recovery Notes", type: "incoming" },
    { id: "4", title: "Clinical Trial Data", type: "outgoing" },
    { id: "5", title: "Medical Research Papers", type: "incoming" },
  ];

  return (
    <div
      className={`
      bg-card border-l border-border flex flex-col transition-all duration-300 ease-in-out
      ${isOpen ? "w-80" : "w-0"}
    `}
    >
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className="absolute top-4 -left-10 z-10 p-2 bg-card border border-border rounded-l-md hover:bg-muted transition-colors"
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
                      <div className="text-lg font-bold text-accent">{note.connections}</div>
                      <div className="text-xs text-muted-foreground">Outgoing Links</div>
                    </div>
                    <div className="text-center p-3 bg-muted/50 rounded-md">
                      <div className="text-lg font-bold text-accent">{note.backlinks}</div>
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

                <div className="space-y-3">
                  {mockConnections.map((connection) => (
                    <div
                      key={connection.id}
                      className="flex items-center space-x-3 p-2 rounded-md hover:bg-muted/50 cursor-pointer"
                    >
                      <div
                        className={`w-2 h-2 rounded-full ${
                          connection.type === "outgoing" ? "bg-green-500" : "bg-blue-500"
                        }`}
                      />
                      <div className="flex-1">
                        <p className="text-sm font-medium truncate">{connection.title}</p>
                        <p className="text-xs text-muted-foreground capitalize">
                          {connection.type}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                {mockConnections.length === 0 && (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    No connections found
                  </p>
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
                      onClick={onEdit}
                      className="w-full flex items-center space-x-2 p-2 rounded-md hover:bg-muted transition-colors text-left"
                    >
                      <Edit className="h-4 w-4" />
                      <span className="text-sm">Edit Note</span>
                    </button>
                    <button className="w-full flex items-center space-x-2 p-2 rounded-md hover:bg-muted transition-colors text-left">
                      <Eye className="h-4 w-4" />
                      <span className="text-sm">View Raw</span>
                    </button>
                    <button className="w-full flex items-center space-x-2 p-2 rounded-md hover:bg-muted transition-colors text-left">
                      <Share className="h-4 w-4" />
                      <span className="text-sm">Share Link</span>
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
                        exportMessage.includes("Failed") || exportMessage.includes("Error")
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
                        onClick={async () => {
                          if (!note) return;
                          setExportLoading(format.id);
                          setExportMessage("");
                          try {
                            await onExport?.(format.id, note.id);
                            setExportMessage(`Successfully exported as ${format.label}`);
                            setTimeout(() => setExportMessage(""), 5000);
                          } catch (error) {
                            setExportMessage(`Failed to export as ${format.label}`);
                            setTimeout(() => setExportMessage(""), 5000);
                          } finally {
                            setExportLoading(null);
                          }
                        }}
                        disabled={exportLoading === format.id}
                        className="w-full flex items-center space-x-2 p-2 rounded-md hover:bg-muted transition-colors text-left disabled:opacity-50"
                      >
                        <span className="text-sm">{format.icon}</span>
                        <span className="text-sm">{format.label}</span>
                        {exportLoading === format.id && (
                          <div className="ml-auto animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                        )}
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
                    onClick={onDelete}
                    className="w-full flex items-center space-x-2 p-2 rounded-md hover:bg-red-500/10 hover:text-red-500 transition-colors text-left text-red-500"
                  >
                    <Trash2 className="h-4 w-4" />
                    <span className="text-sm">Delete Note</span>
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
