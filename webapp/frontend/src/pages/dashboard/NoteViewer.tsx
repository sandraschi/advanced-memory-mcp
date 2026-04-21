import {
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Download,
  Eye,
  FileText,
  Filter,
  Folder,
  List,
  Maximize2,
  Minimize2,
  MoreVertical,
  Network,
  Search,
  Share,
  X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { getApiBaseUrl } from "../../config/apiBase";
import { devError } from "../../devConsole";
import { apiService } from "../../services/api";

const DEBUG = import.meta.env.DEV;

interface Note {
  id: string;
  title: string;
  content: string;
  tags: string[];
  created: string;
  modified: string;
  wordCount: number;
  connections: number;
}

interface NoteViewerProps {
  selectedNoteId?: string | undefined;
  onNoteSelect?: (noteId: string) => void;
}

type ProjectRow = { name: string; path: string; is_default?: boolean };

export default function NoteViewer({ selectedNoteId, onNoteSelect }: NoteViewerProps) {
  const [notes, setNotes] = useState<Note[]>([]);
  const [filteredNotes, setFilteredNotes] = useState<Note[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  /** FastAPI (from start.ps1 / uvicorn) — this page does not start it. */
  const [backendReachable, setBackendReachable] = useState<"checking" | "online" | "offline">(
    "checking",
  );
  const [listError, setListError] = useState<string>("");
  const [showFilters, setShowFilters] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // View Mode State
  const [viewMode, setViewMode] = useState<"list" | "tree">("list");
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalNotes, setTotalNotes] = useState(0);

  // Filter state
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [dateCreatedFrom, setDateCreatedFrom] = useState("");
  const [dateCreatedTo, setDateCreatedTo] = useState("");
  const [dateModifiedFrom, setDateModifiedFrom] = useState("");
  const [dateModifiedTo, setDateModifiedTo] = useState("");
  const [availableTags, setAvailableTags] = useState<string[]>([]);
  const [projects, setProjects] = useState<ProjectRow[]>([]);
  const [vaultProject, setVaultProject] = useState("");

  /** Bumps on effect cleanup (Strict Mode remount, /notes unmount) so stale loadNotes cannot clear a good list. */
  const listFetchGen = useRef(0);

  const probeBackend = async (opts?: { silent?: boolean }): Promise<boolean> => {
    try {
      if (!opts?.silent) {
        setBackendReachable("checking");
      }
      const healthUrl = `${getApiBaseUrl()}/health`;
      const response = await fetch(healthUrl, {
        method: "GET",
        signal: AbortSignal.timeout(2000),
      });
      const ok = response.ok;
      setBackendReachable(ok ? "online" : "offline");
      return ok;
    } catch (error) {
      DEBUG && devError("Backend health check failed:", error);
      setBackendReachable("offline");
      return false;
    }
  };

  const loadNotes = async (page = 1) => {
    const myGen = ++listFetchGen.current;
    const stillCurrent = () => myGen === listFetchGen.current;

    setIsLoading(true);
    setListError("");
    try {
      const apiUp = await probeBackend();
      if (!stillCurrent()) {
        return;
      }

      if (apiUp) {
        try {
          const response = await (searchQuery.trim() !== ""
            ? apiService.searchNotes(searchQuery, page, 50, selectedTags)
            : apiService.getNotes(page, 50));

          if (!stillCurrent()) {
            return;
          }

          if (response.success && Array.isArray(response.data?.notes)) {
            const notesData = response.data.notes;
            setNotes(notesData);
            setFilteredNotes(notesData);
            setCurrentPage(response.data.page || page);
            setTotalPages(response.data.pages || 1);
            setTotalNotes(response.data.total ?? notesData.length);

            // Extract available tags
            const allTags = new Set<string>();
            notesData.forEach((note) => {
              if (Array.isArray(note.tags)) {
                note.tags.forEach((tag) => allTags.add(tag));
              }
            });
            setAvailableTags(Array.from(allTags).sort());
            setIsLoading(false);
            return;
          } else {
            setListError(response.error || "Could not load notes from the API.");
          }
        } catch (apiError) {
          devError("API call failed:", apiError);
          setListError("Could not load notes from the API.");
        }
      }

      if (!stillCurrent()) {
        return;
      }
      setNotes([]);
      setFilteredNotes([]);
      setAvailableTags([]);
      setTotalNotes(0);
      setTotalPages(1);
      setCurrentPage(1);
      setIsLoading(false);
    } catch (error) {
      devError("Failed to load notes:", error);
      if (!stillCurrent()) {
        return;
      }
      setListError("An unexpected error occurred while loading notes.");
      setNotes([]);
      setFilteredNotes([]);
      setAvailableTags([]);
      setTotalNotes(0);
      setTotalPages(1);
      setCurrentPage(1);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const pr = await apiService.getProjects();
      if (cancelled) {
        return;
      }
      if (pr.success && Array.isArray(pr.data) && pr.data.length > 0) {
        const rows = pr.data as ProjectRow[];
        setProjects(rows);
        const first = rows[0];
        const def = rows.find((p) => p.is_default)?.name ?? first?.name ?? "";
        if (def) {
          setVaultProject(def);
          apiService.activeProject = def;
        }
      } else if (!pr.success && pr.error) {
        setListError(pr.error);
      }
      await loadNotes(1);
    })();

    const interval = setInterval(() => {
      void probeBackend({ silent: true });
    }, 10000);

    return () => {
      cancelled = true;
      listFetchGen.current++;
      clearInterval(interval);
    };
  }, []);

  const handleVaultProjectChange = async (name: string) => {
    setVaultProject(name);
    setSelectedNote(null);
    onNoteSelect?.("");
    apiService.activeProject = name;
    const sw = await apiService.switchProject(name);
    if (!sw.success) {
      setListError(sw.error || "Could not switch default project");
      return;
    }
    setListError("");
    setCurrentPage(1);
    await loadNotes(1);
  };

  // Apply all filters (search, tags, dates)
  const applyFilters = (notesList: Note[]) => {
    let filtered = notesList;

    // Search filter
    if (searchQuery.trim() !== "") {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter((note) => {
        const title = String(note.title ?? "").toLowerCase();
        const body = String(note.content ?? "").toLowerCase();
        return (
          title.includes(q) ||
          body.includes(q) ||
          note.tags.some((tag) => String(tag).toLowerCase().includes(q))
        );
      });
    }

    // Tag filter
    if (selectedTags.length > 0) {
      filtered = filtered.filter((note) =>
        selectedTags.some((selectedTag) => note.tags.includes(selectedTag)),
      );
    }

    // Date filters
    if (dateCreatedFrom) {
      const fromDate = new Date(dateCreatedFrom);
      filtered = filtered.filter((note) => new Date(note.created) >= fromDate);
    }
    if (dateCreatedTo) {
      const toDate = new Date(dateCreatedTo);
      toDate.setHours(23, 59, 59, 999); // End of day
      filtered = filtered.filter((note) => new Date(note.created) <= toDate);
    }
    if (dateModifiedFrom) {
      const fromDate = new Date(dateModifiedFrom);
      filtered = filtered.filter((note) => new Date(note.modified) >= fromDate);
    }
    if (dateModifiedTo) {
      const toDate = new Date(dateModifiedTo);
      toDate.setHours(23, 59, 59, 999); // End of day
      filtered = filtered.filter((note) => new Date(note.modified) <= toDate);
    }

    return filtered;
  };

  useEffect(() => {
    const filtered = applyFilters(notes);
    setFilteredNotes(filtered);
  }, [
    searchQuery,
    selectedTags,
    dateCreatedFrom,
    dateCreatedTo,
    dateModifiedFrom,
    dateModifiedTo,
    notes,
  ]);

  useEffect(() => {
    // Select note based on selectedNoteId prop
    if (selectedNoteId) {
      const note = notes.find((n) => n.id === selectedNoteId);
      if (note) {
        setSelectedNote(note);
      }
    }
  }, [selectedNoteId, notes]);

  const handleNoteSelect = async (note: Note) => {
    setSelectedNote(note);
    onNoteSelect?.(note.id);

    // Try to fetch full note content from API
    try {
      const response = await apiService.getNote(note.id);
      if (response.success && response.data) {
        // Merge full content into existing note object to preserve tags, date, etc.
        setSelectedNote((prev) =>
          prev && prev.id === note.id
            ? {
                ...prev,
                content: response.data!.content,
                title: response.data!.title || prev.title,
              }
            : prev,
        );
      }
    } catch (error) {
      // Keep the basic note data if API call fails
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Tree building helper
  interface TreeNode {
    name: string;
    path: string;
    note?: Note;
    children: Record<string, TreeNode>;
  }

  const buildTree = (notesList: Note[]): TreeNode[] => {
    const root: Record<string, TreeNode> = {};

    notesList.forEach((note) => {
      const permalink = (note as any).permalink || note.title || "";
      const pathParts = permalink.includes("/") ? permalink.split("/") : [note.title];

      let currentLevel = root;
      let currentPath = "";

      pathParts.forEach((part: string, index: number) => {
        currentPath = currentPath ? `${currentPath}/${part}` : part;
        if (!currentLevel[part]) {
          currentLevel[part] = {
            name: part,
            path: currentPath,
            children: {},
          };
        }
        if (index === pathParts.length - 1) {
          currentLevel[part].note = note;
        }
        currentLevel = currentLevel[part].children;
      });
    });

    const recursiveSort = (nodes: TreeNode[]): TreeNode[] => {
      const sorted = [...nodes].sort((a, b) => {
        const aIsFolder = Object.keys(a.children).length > 0 && !a.note;
        const bIsFolder = Object.keys(b.children).length > 0 && !b.note;
        if (aIsFolder !== bIsFolder) return aIsFolder ? -1 : 1;
        return a.name.localeCompare(b.name);
      });
      sorted.forEach((node) => {
        const sortedChildren = recursiveSort(Object.values(node.children));
        node.children = {};
        sortedChildren.forEach((c) => {
          node.children[c.name] = c;
        });
      });
      return sorted;
    };

    return recursiveSort(Object.values(root));
  };

  const toggleNode = (path: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedNodes(newExpanded);
  };

  const renderTreeNodes = (nodes: TreeNode[], level = 0): React.ReactNode => {
    return nodes.map((node) => {
      const isExpanded = expandedNodes.has(node.path);
      const hasChildren = Object.keys(node.children).length > 0;
      const isSelected = selectedNote?.id === node.note?.id;

      return (
        <div key={node.path} className="w-full">
          <div
            className={`flex items-center py-1.5 px-2 cursor-pointer hover:bg-muted/50 text-sm ${isSelected ? "bg-accent/10 border-l-2 border-accent text-accent font-medium" : "text-foreground border-l-2 border-transparent"}`}
            style={{ paddingLeft: `${level * 12 + 8}px` }}
            onClick={() => {
              if (node.note) {
                handleNoteSelect(node.note);
              } else if (hasChildren) {
                toggleNode(node.path);
              }
            }}
          >
            {hasChildren && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  toggleNode(node.path);
                }}
                className="w-4 h-4 mr-1 flex items-center justify-center text-muted-foreground hover:text-foreground"
              >
                {isExpanded ? (
                  <ChevronDown className="w-3 h-3" />
                ) : (
                  <ChevronRight className="w-3 h-3" />
                )}
              </button>
            )}
            {!hasChildren && <div className="w-5" />}

            {hasChildren && !node.note ? (
              <Folder className="w-3.5 h-3.5 mr-2 text-muted-foreground" />
            ) : (
              <FileText className="w-3.5 h-3.5 mr-2 text-muted-foreground shrink-0" />
            )}

            <span className="truncate">{node.name}</span>
          </div>

          {isExpanded && hasChildren && (
            <div className="w-full">{renderTreeNodes(Object.values(node.children), level + 1)}</div>
          )}
        </div>
      );
    });
  };

  return (
    <div className="h-full min-h-0 flex flex-col">
      {/* Search Header */}
      <div className="p-6 border-b border-border space-y-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-center gap-2 min-w-0">
            <Folder className="h-4 w-4 text-muted-foreground shrink-0" />
            <label htmlFor="vault-project" className="text-sm text-muted-foreground shrink-0">
              Project
            </label>
            <select
              id="vault-project"
              className="rounded-md border border-border bg-background px-3 py-2 text-sm min-w-[10rem] max-w-[20rem]"
              value={vaultProject}
              disabled={projects.length === 0}
              onChange={(e) => void handleVaultProjectChange(e.target.value)}
            >
              {projects.map((p) => (
                <option key={p.name} value={p.name}>
                  {p.name}
                  {p.is_default ? " (default)" : ""}
                </option>
              ))}
            </select>
            <span className="text-xs text-muted-foreground hidden md:inline">
              Path: {projects.find((p) => p.name === vaultProject)?.path || "—"}
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-3 text-xs">
            <Link to="/vault/sync" className="text-accent hover:underline">
              Sync and index
            </Link>
            <span className="text-muted-foreground">·</span>
            <Link to="/vault/stats" className="text-accent hover:underline">
              Stats
            </Link>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <input
              type="text"
              placeholder="Search notes... (press Enter)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && loadNotes(1)}
              className="input pl-10 w-full"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`btn btn-outline flex items-center ${showFilters ? "bg-accent/10" : ""}`}
          >
            <Filter className="h-4 w-4 mr-2" />
            Filters
            {(selectedTags.length > 0 ||
              dateCreatedFrom ||
              dateCreatedTo ||
              dateModifiedFrom ||
              dateModifiedTo) && (
              <span className="ml-2 bg-accent text-accent-foreground rounded-full px-2 py-0.5 text-xs">
                {selectedTags.length +
                  (dateCreatedFrom ? 1 : 0) +
                  (dateCreatedTo ? 1 : 0) +
                  (dateModifiedFrom ? 1 : 0) +
                  (dateModifiedTo ? 1 : 0)}
              </span>
            )}
          </button>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-muted-foreground whitespace-nowrap">
              {filteredNotes.length > 0
                ? `${(currentPage - 1) * 50 + 1} - ${Math.min(currentPage * 50, totalNotes)} of ${totalNotes}`
                : "0"}{" "}
              notes
            </div>
            <div className="flex items-center space-x-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  backendReachable === "online"
                    ? "bg-green-500"
                    : backendReachable === "checking"
                      ? "bg-amber-500 animate-pulse"
                      : "bg-red-500"
                }`}
              />
              <span className="text-xs text-muted-foreground">
                {backendReachable === "checking"
                  ? "Checking backend…"
                  : backendReachable === "online"
                    ? "Backend online"
                    : "Backend offline"}
              </span>
            </div>
          </div>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="mt-4 p-4 bg-muted/50 rounded-md border">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {/* Tags Filter */}
              <div>
                <label className="label">Tags</label>
                <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                  {availableTags.map((tag) => (
                    <button
                      key={tag}
                      onClick={() => {
                        if (selectedTags.includes(tag)) {
                          setSelectedTags(selectedTags.filter((t) => t !== tag));
                        } else {
                          setSelectedTags([...selectedTags, tag]);
                        }
                      }}
                      className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                        selectedTags.includes(tag)
                          ? "bg-accent text-accent-foreground border-accent"
                          : "bg-background hover:bg-muted border-border"
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                  {availableTags.length === 0 && (
                    <span className="text-xs text-muted-foreground">No tags available</span>
                  )}
                </div>
              </div>

              {/* Date Created Filter */}
              <div>
                <label className="label">Date Created</label>
                <div className="space-y-2">
                  <input
                    type="date"
                    value={dateCreatedFrom}
                    onChange={(e) => setDateCreatedFrom(e.target.value)}
                    className="input w-full text-sm"
                    placeholder="From"
                  />
                  <input
                    type="date"
                    value={dateCreatedTo}
                    onChange={(e) => setDateCreatedTo(e.target.value)}
                    className="input w-full text-sm"
                    placeholder="To"
                  />
                </div>
              </div>

              {/* Date Modified Filter */}
              <div>
                <label className="label">Date Modified</label>
                <div className="space-y-2">
                  <input
                    type="date"
                    value={dateModifiedFrom}
                    onChange={(e) => setDateModifiedFrom(e.target.value)}
                    className="input w-full text-sm"
                    placeholder="From"
                  />
                  <input
                    type="date"
                    value={dateModifiedTo}
                    onChange={(e) => setDateModifiedTo(e.target.value)}
                    className="input w-full text-sm"
                    placeholder="To"
                  />
                </div>
              </div>
            </div>

            {/* Clear Filters */}
            <div className="mt-4 flex justify-end">
              <button
                onClick={() => {
                  setSelectedTags([]);
                  setDateCreatedFrom("");
                  setDateCreatedTo("");
                  setDateModifiedFrom("");
                  setDateModifiedTo("");
                }}
                className="btn btn-outline btn-sm flex items-center"
              >
                <X className="h-4 w-4 mr-2" />
                Clear All Filters
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Notes List and Content - min-h-0 so this row gets bounded height and content can scroll */}
      <div className="flex-1 flex min-h-0 overflow-hidden relative">
        {/* Notes List */}
        {!isFullscreen && (
          <div className="w-80 min-h-0 border-r border-border flex flex-col animate-in slide-in-from-left duration-300">
            <div className="p-4 border-b border-border flex justify-between items-center">
              <h2 className="font-semibold flex items-center gap-2 flex-wrap">
                Notes{" "}
                <span
                  className="text-xs font-normal text-muted-foreground bg-muted px-1.5 py-0.5 rounded-full tabular-nums"
                  title="Listed in the sidebar (after any local filters) / total in the search index for this project and query."
                >
                  {filteredNotes.length} / {totalNotes}
                </span>
              </h2>
              <div className="flex bg-muted/50 p-1 rounded-md">
                <button
                  onClick={() => setViewMode("list")}
                  className={`p-1 rounded ${viewMode === "list" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}
                  title="List View"
                >
                  <List className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode("tree")}
                  className={`p-1 rounded ${viewMode === "tree" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}
                  title="Tree View"
                >
                  <Network className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-auto">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-accent"></div>
                  <span className="ml-2 text-muted-foreground">Loading notes…</span>
                </div>
              ) : backendReachable === "offline" ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                      <span className="text-white font-bold text-sm">!</span>
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Cannot reach the vault API</h3>
                  <p className="text-muted-foreground mb-4 max-w-md mx-auto">
                    This page does not start the backend. Run{" "}
                    <code className="text-xs bg-muted px-1 rounded">.\start.ps1</code> from the{" "}
                    <code className="text-xs bg-muted px-1 rounded">webapp</code> folder (it starts
                    FastAPI on port 10705 and Vite on 10704), or run uvicorn from the repo root:{" "}
                    <code className="text-xs bg-muted px-1 rounded">
                      uv run uvicorn advanced_memory.server:app --host 127.0.0.1 --port 10705
                    </code>
                    . If you opened the UI from another device, set{" "}
                    <code className="text-xs bg-muted px-1 rounded">VITE_API_URL</code> to a
                    reachable base ending in{" "}
                    <code className="text-xs bg-muted px-1 rounded">/api/v1</code>.
                  </p>
                  <button
                    type="button"
                    onClick={async () => {
                      await probeBackend();
                      loadNotes();
                    }}
                    className="btn btn-primary"
                  >
                    Try again
                  </button>
                </div>
              ) : notes.length === 0 ? (
                <div className="text-center py-8">
                  {searchQuery.trim() === "" ? (
                    <Search className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  ) : (
                    <FileText className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  )}
                  <h3 className="text-lg font-semibold mb-2">
                    {searchQuery.trim() === "" ? "No notes in this view" : "No Notes Found"}
                  </h3>
                  <p className="text-muted-foreground mb-4">
                    {searchQuery.trim() === ""
                      ? "The list is driven by the search index for the active project. If you expect thousands of notes here, confirm the webapp is using the same project as your synced vault (project switcher), then refresh."
                      : "No notes matched your search and filters."}
                  </p>
                  {listError ? (
                    <p className="text-sm text-red-400 mb-4 max-w-md mx-auto">{listError}</p>
                  ) : null}
                  <button onClick={() => loadNotes(1)} className="btn btn-primary">
                    Refresh
                  </button>
                </div>
              ) : filteredNotes.length === 0 ? (
                <div className="text-center py-8">
                  <Search className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Matching Notes</h3>
                  <p className="text-muted-foreground mb-4">
                    No notes match your current search and filter criteria.
                  </p>
                  <button
                    onClick={() => {
                      setSearchQuery("");
                      setSelectedTags([]);
                      setDateCreatedFrom("");
                      setDateCreatedTo("");
                      setDateModifiedFrom("");
                      setDateModifiedTo("");
                    }}
                    className="btn btn-outline"
                  >
                    Clear All Filters
                  </button>
                </div>
              ) : (
                <div className="flex-1 flex flex-col">
                  {viewMode === "list" ? (
                    <div className="divide-y divide-border flex-1 overflow-auto">
                      {filteredNotes.map((note) => (
                        <div
                          key={note.id}
                          onClick={() => handleNoteSelect(note)}
                          className={`p-4 cursor-pointer hover:bg-muted/50 transition-colors ${
                            selectedNote?.id === note.id
                              ? "bg-accent/10 border-l-4 border-accent"
                              : ""
                          }`}
                        >
                          <h3 className="font-medium text-sm mb-2 line-clamp-2">{note.title}</h3>
                          <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
                            {note.content}
                          </p>
                          <div className="flex items-center justify-between text-xs text-muted-foreground">
                            <span>{formatDate(note.modified)}</span>
                            <div className="flex items-center space-x-2">
                              <span>{note.wordCount} words</span>
                              <span>{note.connections} links</span>
                            </div>
                          </div>
                          {note.tags && note.tags.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {note.tags.slice(0, 3).map((tag) => (
                                <span
                                  key={tag}
                                  className="px-2 py-1 bg-accent/20 text-accent text-xs rounded-md"
                                >
                                  {tag}
                                </span>
                              ))}
                              {note.tags.length > 3 && (
                                <span className="text-xs text-muted-foreground">
                                  +{note.tags.length - 3}
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="py-2 flex-1 overflow-auto">
                      {renderTreeNodes(buildTree(filteredNotes))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="p-3 flex items-center justify-between border-t border-border bg-muted/20">
                <button
                  disabled={currentPage === 1}
                  onClick={() => loadNotes(currentPage - 1)}
                  className="btn btn-outline btn-sm p-1 disabled:opacity-50"
                  aria-label="Previous Page"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="text-xs text-muted-foreground">
                  Page <span className="text-foreground font-medium">{currentPage}</span> of{" "}
                  {totalPages}
                </span>
                <button
                  disabled={currentPage === totalPages}
                  onClick={() => loadNotes(currentPage + 1)}
                  className="btn btn-outline btn-sm p-1 disabled:opacity-50"
                  aria-label="Next Page"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        )}

        {/* Note Content - min-h-0 so flex child can shrink and scroll */}
        <div className="flex-1 flex flex-col min-h-0">
          {selectedNote ? (
            <>
              {/* Note Header */}
              <div className="p-6 border-b border-border shrink-0">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h1 className="text-2xl font-bold mb-2">{selectedNote.title}</h1>
                    <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                      <span>Created: {formatDate(selectedNote.created)}</span>
                      <span>Modified: {formatDate(selectedNote.modified)}</span>
                      <span>{selectedNote.wordCount} words</span>
                    </div>
                    {selectedNote.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-3">
                        {selectedNote.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-3 py-1 bg-accent/20 text-accent text-sm rounded-full"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setIsFullscreen(!isFullscreen)}
                      className="p-2 rounded-md hover:bg-accent/10 text-accent transition-colors border border-accent/20"
                      title={isFullscreen ? "Exit Fullscreen" : "Fullscreen View"}
                    >
                      {isFullscreen ? (
                        <Minimize2 className="h-4 w-4" />
                      ) : (
                        <Maximize2 className="h-4 w-4" />
                      )}
                    </button>
                    <button
                      className="p-2 rounded-md hover:bg-muted transition-colors"
                      title="View"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    <button
                      className="p-2 rounded-md hover:bg-muted transition-colors"
                      title="Export"
                    >
                      <Download className="h-4 w-4" />
                    </button>
                    <button
                      className="p-2 rounded-md hover:bg-muted transition-colors"
                      title="Share"
                    >
                      <Share className="h-4 w-4" />
                    </button>
                    <button
                      className="p-2 rounded-md hover:bg-muted transition-colors"
                      title="More"
                    >
                      <MoreVertical className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Note Content - fills remaining height and scrolls */}
              <div className="flex-1 min-h-0 overflow-auto p-6">
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
                    {selectedNote.content}
                  </pre>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-center">
              <div>
                <FileText className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Select a Note</h3>
                <p className="text-muted-foreground">
                  Choose a note from the list to view its content and metadata.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
