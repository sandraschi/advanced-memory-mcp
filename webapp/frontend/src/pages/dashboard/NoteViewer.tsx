import {
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Copy,
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
import { Link, useSearchParams } from "react-router-dom";
import { getApiBaseUrl } from "../../config/apiBase";
import { devError } from "../../devConsole";
import { useBackendAutoReconnect } from "../../hooks/useBackendAutoReconnect";
import Markdown from "../../components/Markdown";
import { apiService } from "../../services/api";
import {
  copyRecoveryCommand,
  UVICORN_RESTART_LINE,
  WEBAPP_START_FROM_ROOT,
} from "../../utils/backendRecovery";

const DEBUG = import.meta.env.DEV;

/** API / list state may still carry non-array tags; never assume `.tags` is an array. */
function noteTags(note: { tags?: unknown }): string[] {
  if (Array.isArray(note.tags)) {
    return note.tags as string[];
  }
  if (typeof note.tags === "string" && note.tags.trim()) {
    try {
      const p = JSON.parse(note.tags) as unknown;
      if (Array.isArray(p)) {
        return p.map((x) => String(x)).filter((t) => t.length > 0);
      }
    } catch {
      return [note.tags.trim()];
    }
    return [note.tags.trim()];
  }
  return [];
}

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
  const [searchParams] = useSearchParams();
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
  const [sortBy, setSortBy] = useState<"modified_desc" | "modified_asc" | "title_asc" | "title_desc">("modified_desc");
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
  const [recoveryCopied, setRecoveryCopied] = useState<null | "uvicorn" | "start">(null);

  /** Bumps on effect cleanup (Strict Mode remount, /notes unmount) so stale loadNotes cannot clear a good list. */
  const listFetchGen = useRef(0);
  const notesRef = useRef<Note[]>([]);
  const totalNotesRef = useRef(0);
  const currentPageRef = useRef(1);
  notesRef.current = notes;
  totalNotesRef.current = totalNotes;
  currentPageRef.current = currentPage;

  /** Background polls must not flip the UI offline on one slow or dropped /health (common under load). */
  const HEALTH_TIMEOUT_MS = 10_000;

  const probeBackend = async (opts?: { silent?: boolean }): Promise<boolean> => {
    const silent = Boolean(opts?.silent);
    try {
      if (!silent) {
        setBackendReachable("checking");
      }
      const healthUrl = `${getApiBaseUrl()}/health`;
      const response = await fetch(healthUrl, {
        method: "GET",
        signal: AbortSignal.timeout(HEALTH_TIMEOUT_MS),
      });
      const ok = response.ok;
      if (ok) {
        setBackendReachable("online");
        return true;
      }
      if (!silent) {
        setBackendReachable("offline");
      }
      return false;
    } catch (error) {
      DEBUG && devError("Backend health check failed:", error);
      if (!silent) {
        setBackendReachable("offline");
      }
      return false;
    }
  };

  const mapRecentToNote = (primary: Record<string, unknown>): Note | null => {
    const title = String(primary.title ?? primary.permalink ?? "Untitled");
    const permalink = String(primary.permalink ?? "");
    if (!permalink) return null;
    const content = typeof primary.content === "string" ? primary.content : "";
    const tags = Array.isArray(primary.tags) ? (primary.tags as string[]) : [];
    const created = typeof primary.created_at === "string" ? primary.created_at : new Date().toISOString();
    const modified = typeof primary.updated_at === "string" ? primary.updated_at : created;
    return {
      id: permalink,
      title,
      content,
      tags,
      created,
      modified,
      wordCount: Math.max(0, Math.round(content.length / 5)),
      connections: 0,
    };
  };

  const loadRecentNotes = async (page = 1) => {
    const response = await apiService.getMemoryRecent({
      timeframe: "90d",
      depth: 2,
      page,
      pageSize: 100,
    });
    if (!response.success || !response.data) {
      return { error: response.error || "Could not load recent notes" };
    }
    const rows = response.data.results;
    if (!Array.isArray(rows)) {
      return { error: "Unexpected response from memory/recent" };
    }
    const notesData: Note[] = [];
    const allTags = new Set<string>();
    for (const item of rows) {
      const primary = item.primary_result;
      if (!primary || typeof primary !== "object") continue;
      const t = primary.type;
      if (t !== "entity" && t !== "observation") continue;
      const note = mapRecentToNote(primary as Record<string, unknown>);
      if (note) {
        notesData.push(note);
        note.tags.forEach((tag) => allTags.add(tag));
      }
    }
    const total = typeof response.data.metadata?.total === "number" ? response.data.metadata.total : notesData.length;
    return { notesData, allTags, total };
  };

  const loadNotes = async (page = 1, opts?: { skipHealthProbe?: boolean }) => {
    const myGen = ++listFetchGen.current;
    const stillCurrent = () => myGen === listFetchGen.current;
    const skipHealth = Boolean(opts?.skipHealthProbe);

    setIsLoading(true);
    setListError("");
    try {
      if (!skipHealth) {
        const apiUp = await probeBackend();
        if (!stillCurrent()) {
          return;
        }
        if (!apiUp) {
          if (!stillCurrent()) {
            return;
          }
          const preserveCache =
            notesRef.current.length > 0 || totalNotesRef.current > 0;
          if (preserveCache) {
            setBackendReachable("offline");
            setListError("Health check failed; showing the last loaded list.");
            setIsLoading(false);
            return;
          }
          setNotes([]);
          setFilteredNotes([]);
          setAvailableTags([]);
          setTotalNotes(0);
          setTotalPages(1);
          setCurrentPage(1);
          setIsLoading(false);
          return;
        }
      }

      const pageSize = 100;
      const hasSearch = searchQuery.trim() !== "";

      try {
        if (!hasSearch) {
          // Use recents API for default view (newest first)
          const recent = await loadRecentNotes(page);
          if (!stillCurrent()) return;

          if (recent.error) {
            setListError(recent.error);
          } else if (recent.notesData) {
            setNotes(recent.notesData);
            setFilteredNotes(recent.notesData);
            setCurrentPage(page);
            setTotalPages(Math.ceil(recent.total / pageSize) || 1);
            setTotalNotes(recent.total);
            setBackendReachable("online");
            setAvailableTags(Array.from(recent.allTags).sort());
            setIsLoading(false);
            return;
          }
        } else {
          // Use search API when query is active
          const response = await apiService.searchNotes(searchQuery, page, pageSize, selectedTags);

          if (!stillCurrent()) return;

          if (response.success && Array.isArray(response.data?.notes)) {
            const notesData = response.data.notes;
            setNotes(notesData);
            setFilteredNotes(notesData);
            setCurrentPage(response.data.page || page);
            setTotalPages(response.data.pages || 1);
            setTotalNotes(response.data.total ?? notesData.length);
            setBackendReachable("online");

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
        }
      } catch (apiError) {
        devError("API call failed:", apiError);
        setListError("Could not load notes from the API.");
      }

      if (!stillCurrent()) {
        return;
      }
      const preserveAfterApiFailure =
        skipHealth && (notesRef.current.length > 0 || totalNotesRef.current > 0);
      if (preserveAfterApiFailure) {
        setBackendReachable("offline");
        setListError("Notes API still unreachable; cached list kept.");
        setIsLoading(false);
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
      const preserveUnexpected =
        skipHealth && (notesRef.current.length > 0 || totalNotesRef.current > 0);
      if (preserveUnexpected) {
        setBackendReachable("offline");
        setListError("Unexpected error while refreshing; cached list kept.");
        setIsLoading(false);
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

  const loadNotesRef = useRef(loadNotes);
  loadNotesRef.current = loadNotes;

  useBackendAutoReconnect(
    backendReachable === "offline" && !isLoading,
    async () => {
      await loadNotesRef.current(currentPageRef.current, { skipHealthProbe: true });
    },
  );

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
    }, 45_000);

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
        const tags = noteTags(note);
        return (
          title.includes(q) ||
          body.includes(q) ||
          tags.some((tag) => String(tag).toLowerCase().includes(q))
        );
      });
    }

    // Tag filter
    if (selectedTags.length > 0) {
      filtered = filtered.filter((note) => {
        const tags = noteTags(note);
        return selectedTags.some((selectedTag) => tags.includes(selectedTag));
      });
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
    const sorted = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case "modified_desc":
          return new Date(b.modified).getTime() - new Date(a.modified).getTime();
        case "modified_asc":
          return new Date(a.modified).getTime() - new Date(b.modified).getTime();
        case "title_asc":
          return (a.title || "").localeCompare(b.title || "");
        case "title_desc":
          return (b.title || "").localeCompare(a.title || "");
        default:
          return 0;
      }
    });
    setFilteredNotes(sorted);
  }, [
    searchQuery,
    selectedTags,
    dateCreatedFrom,
    dateCreatedTo,
    dateModifiedFrom,
    dateModifiedTo,
    notes,
    sortBy,
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
        const payload = response.data as { content?: string; title?: string };
        const body = typeof payload.content === "string" ? payload.content : "";
        const title = typeof payload.title === "string" ? payload.title : undefined;
        // Merge full content into existing note object to preserve tags, date, etc.
        setSelectedNote((prev) =>
          prev && prev.id === note.id
            ? {
                ...prev,
                content: body,
                title: title || prev.title,
              }
            : prev,
        );
      }
    } catch (error) {
      // Keep the basic note data if API call fails
    }
  };

  const handleNoteSelectRef = useRef(handleNoteSelect);
  handleNoteSelectRef.current = handleNoteSelect;
  /** ``project:decodedId`` so we re-open after vault project switch. */
  const lastUrlOpenKey = useRef<string | null>(null);

  /** Open note from ``/notes?id=<permalink>`` (e.g. Recent Activity links). */
  useEffect(() => {
    if (!vaultProject) {
      return;
    }
    const raw = searchParams.get("id");
    if (raw === null || raw === "") {
      lastUrlOpenKey.current = null;
      return;
    }
    let id: string;
    try {
      id = decodeURIComponent(raw);
    } catch {
      devError("Invalid id query parameter", raw);
      return;
    }
    const trimmed = id.trim();
    if (!trimmed) {
      return;
    }
    const openKey = `${vaultProject}:${trimmed}`;
    if (lastUrlOpenKey.current === openKey) {
      return;
    }
    lastUrlOpenKey.current = openKey;

    const fromList = notesRef.current.find((n) => n.id === trimmed);
    const stub: Note = {
      id: trimmed,
      title: trimmed,
      content: "",
      tags: [],
      created: new Date().toISOString(),
      modified: new Date().toISOString(),
      wordCount: 0,
      connections: 0,
    };
    void handleNoteSelectRef.current(fromList ?? stub);
  }, [searchParams, vaultProject]);

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
      const fallbackId = String(note.id ?? "untitled");
      const permalink = String(
        (note as { permalink?: string }).permalink || note.title || note.id || "untitled",
      );
      const pathParts = permalink.includes("/")
        ? permalink.split("/").filter((p) => p.length > 0)
        : [permalink || fallbackId];

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
        return String(a.name).localeCompare(String(b.name));
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

  const hasCachedVaultList = notes.length > 0 || totalNotes > 0;
  const showHardOfflinePanel = !isLoading && backendReachable === "offline" && !hasCachedVaultList;
  const showStaleConnectionBanner =
    !isLoading && backendReachable === "offline" && hasCachedVaultList;

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
              className="w-full bg-zinc-900 border border-zinc-700 rounded-lg pl-10 pr-3 py-2 text-sm text-white placeholder-zinc-500 outline-none focus:ring-1 focus:ring-amber-500/30"
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
                    className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white placeholder-zinc-500 outline-none focus:ring-1 focus:ring-amber-500/30"
                    placeholder="From"
                  />
                  <input
                    type="date"
                    value={dateCreatedTo}
                    onChange={(e) => setDateCreatedTo(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white placeholder-zinc-500 outline-none focus:ring-1 focus:ring-amber-500/30"
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
                    className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white placeholder-zinc-500 outline-none focus:ring-1 focus:ring-amber-500/30"
                    placeholder="From"
                  />
                  <input
                    type="date"
                    value={dateModifiedTo}
                    onChange={(e) => setDateModifiedTo(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white placeholder-zinc-500 outline-none focus:ring-1 focus:ring-amber-500/30"
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
            <div className="p-4 border-b border-border flex justify-between items-center gap-2">
              <h2 className="font-semibold flex items-center gap-2 flex-wrap shrink-0">
                Notes{" "}
                <span
                  className="text-xs font-normal text-muted-foreground bg-muted px-1.5 py-0.5 rounded-full tabular-nums"
                  title="Listed in the sidebar (after any local filters) / total in the search index for this project and query."
                >
                  {filteredNotes.length} / {totalNotes}
                </span>
              </h2>
              <div className="flex items-center gap-1.5">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
                  className="bg-muted/50 border border-border rounded px-1.5 py-1 text-[10px] uppercase tracking-wider outline-none cursor-pointer"
                  title="Sort notes"
                >
                  <option value="modified_desc">Newest</option>
                  <option value="modified_asc">Oldest</option>
                  <option value="title_asc">A-Z</option>
                  <option value="title_desc">Z-A</option>
                </select>
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
            </div>

            <div className="flex-1 overflow-auto">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-accent"></div>
                  <span className="ml-2 text-muted-foreground">Loading notes…</span>
                </div>
              ) : showHardOfflinePanel ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                      <span className="text-white font-bold text-sm">!</span>
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Cannot reach the vault API</h3>
                  <p className="text-muted-foreground mb-3 max-w-md mx-auto">
                    This page does not start the backend. Run{" "}
                    <code className="text-xs bg-muted px-1 rounded">.\start.ps1</code> from the{" "}
                    <code className="text-xs bg-muted px-1 rounded">webapp</code> folder (it starts
                    FastAPI on port 10705 and Vite on 10704), or run uvicorn from the repo root. If
                    you opened the UI from another device, set{" "}
                    <code className="text-xs bg-muted px-1 rounded">VITE_API_URL</code> to a
                    reachable base ending in{" "}
                    <code className="text-xs bg-muted px-1 rounded">/api/v1</code>.
                  </p>
                  <p className="text-xs text-muted-foreground mb-3 max-w-md mx-auto">
                    A browser cannot restart the API after a process crash. After you start it
                    again in a terminal, this page polls <code className="text-xs">/health</code>{" "}
                    about every 12 seconds and reloads notes when it responds.
                  </p>
                  <div className="flex flex-wrap justify-center gap-2 mb-2">
                    <button
                      type="button"
                      className="btn btn-outline btn-sm inline-flex items-center gap-1"
                      onClick={async () => {
                        const ok = await copyRecoveryCommand(UVICORN_RESTART_LINE);
                        if (ok) {
                          setRecoveryCopied("uvicorn");
                          window.setTimeout(() => setRecoveryCopied(null), 2500);
                        }
                      }}
                    >
                      <Copy className="h-4 w-4" />
                      Copy uvicorn
                    </button>
                    <button
                      type="button"
                      className="btn btn-outline btn-sm inline-flex items-center gap-1"
                      onClick={async () => {
                        const ok = await copyRecoveryCommand(WEBAPP_START_FROM_ROOT);
                        if (ok) {
                          setRecoveryCopied("start");
                          window.setTimeout(() => setRecoveryCopied(null), 2500);
                        }
                      }}
                    >
                      <Copy className="h-4 w-4" />
                      Copy start.ps1
                    </button>
                  </div>
                  {recoveryCopied ? (
                    <p className="text-xs text-green-600 dark:text-green-400 mb-3">Copied.</p>
                  ) : null}
                  <button
                    type="button"
                    onClick={async () => {
                      await probeBackend();
                      void loadNotes(1);
                    }}
                    className="btn btn-primary"
                  >
                    Try again
                  </button>
                </div>
              ) : (
                <>
                  {showStaleConnectionBanner ? (
                    <div className="m-3 rounded-lg border border-amber-500/40 bg-amber-950/25 px-3 py-2 text-xs text-amber-100">
                      <p className="font-medium text-amber-50">Could not reach /health just now</p>
                      <p className="mt-1 text-amber-100/90">
                        Showing the last loaded list. The API may be busy; try again if actions fail.
                      </p>
                      <button
                        type="button"
                        className="btn btn-outline btn-sm mt-2 border-amber-500/50 text-amber-50 hover:bg-amber-900/40"
                        onClick={() => void loadNotes(currentPage)}
                      >
                        Retry connection
                      </button>
                    </div>
                  ) : null}
              {notes.length === 0 ? (
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
                      {filteredNotes.map((note) => {
                        const rowTags = noteTags(note);
                        return (
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
                          {rowTags.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {rowTags.slice(0, 3).map((tag) => (
                                <span
                                  key={tag}
                                  className="px-2 py-1 bg-accent/20 text-accent text-xs rounded-md"
                                >
                                  {tag}
                                </span>
                              ))}
                              {rowTags.length > 3 && (
                                <span className="text-xs text-muted-foreground">
                                  +{rowTags.length - 3}
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="py-2 flex-1 overflow-auto">
                      {renderTreeNodes(buildTree(filteredNotes))}
                    </div>
                  )}
                </div>
              )}
                </>
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
                    {noteTags(selectedNote).length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-3">
                        {noteTags(selectedNote).map((tag) => (
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
                <Markdown content={selectedNote.content} />
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
