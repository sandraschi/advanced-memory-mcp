import {
  AlignLeft,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Copy,
  Download,
  Eye,
  FileText,
  Filter,
  Folder,
  GripVertical,
  List,
  Maximize2,
  Minimize2,
  MoreVertical,
  Network,
  PanelRightOpen,
  Pencil,
  Plus,
  Search,
  Share,
  Trash2,
  X,
} from "lucide-react";
import {
  type MouseEvent as ReactMouseEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { Link, useSearchParams } from "react-router-dom";
import Markdown, { type MarkdownHeading } from "../../components/Markdown";
import NoteEditor from "../../components/notes/NoteEditor";
import { confirmAndDeleteNote, copyText, noteDeepLink } from "../../components/notes/noteActions";
import {
  type ExportFormat,
  VAULT_EVENT,
  type VaultEvent,
  downloadNote,
  folderOf,
  fullDate as formatDate,
  loadPref,
  noteTags,
  savePref,
  snippet,
  wordCount,
} from "../../components/notes/noteUtils";
import { getApiBaseUrl } from "../../config/apiBase";
import { devError } from "../../devConsole";
import { useBackendAutoReconnect } from "../../hooks/useBackendAutoReconnect";
import { type NoteSort, apiService } from "../../services/api";
import {
  UVICORN_RESTART_LINE,
  WEBAPP_START_FROM_ROOT,
  copyRecoveryCommand,
} from "../../utils/backendRecovery";

const DEBUG = import.meta.env.DEV;
/** List-page standard (WEBAPP_SOTA_STANDARDS.md): 20 rows per page by default. */
const PAGE_SIZE = 20;
const LIST_WIDTH_KEY = "am.notes.listWidth";
const READER_WIDTH_KEY = "am.notes.readerWidth";
const LIST_WIDTH_MIN = 240;
const LIST_WIDTH_MAX = 560;

const EXPORT_FORMATS: ReadonlyArray<{ id: ExportFormat; label: string }> = [
  { id: "markdown", label: "Markdown (.md)" },
  { id: "html", label: "HTML (.html)" },
  { id: "pdf", label: "PDF (print dialog)" },
  { id: "json", label: "JSON (.json)" },
  { id: "txt", label: "Plain text (.txt)" },
];

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
  const [backendReachable, setBackendReachable] = useState<
    "checking" | "retrying" | "online" | "offline"
  >("checking");
  const [listError, setListError] = useState<string>("");
  const [showFilters, setShowFilters] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // View Mode State
  const [viewMode, setViewMode] = useState<"list" | "tree">("list");
  const [sortBy, setSortBy] = useState<NoteSort>("modified_desc");
  /** Until the user picks a sort, a text search ranks by relevance and browsing by newest. */
  const [sortChosen, setSortChosen] = useState(false);
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

  // Reader layout: resizable list width, a wide/comfortable reader toggle, and the
  // live outline for the note currently open (populated by Markdown's onHeadings).
  const [listWidth, setListWidth] = useState(() => loadPref(LIST_WIDTH_KEY, 320));
  const [readerWide, setReaderWide] = useState(() => loadPref(READER_WIDTH_KEY, false));
  const [showOutline, setShowOutline] = useState(false);
  const [headings, setHeadings] = useState<MarkdownHeading[]>([]);

  // Editor, source view, header menus, and the transient status toast.
  const [editorMode, setEditorMode] = useState<null | "edit" | "create">(null);
  const [rawView, setRawView] = useState(false);
  const [menu, setMenu] = useState<null | "export" | "more">(null);
  const [notice, setNotice] = useState("");
  /** Id whose full body has been fetched; selectedNote.content is only a snippet until then. */
  const [bodyLoadedId, setBodyLoadedId] = useState<string | null>(null);
  const editorDirtyRef = useRef(false);
  const noticeTimer = useRef<number | undefined>(undefined);
  const selectedNoteRef = useRef<Note | null>(null);
  selectedNoteRef.current = selectedNote;
  const onNoteSelectRef = useRef(onNoteSelect);
  onNoteSelectRef.current = onNoteSelect;

  const flash = (message: string) => {
    setNotice(message);
    window.clearTimeout(noticeTimer.current);
    noticeTimer.current = window.setTimeout(() => setNotice(""), 2800);
  };

  /** What the backend is actually asked for: explicit pick, else relevance when searching. */
  const effectiveSort: NoteSort = sortChosen ? sortBy : searchQuery.trim() ? "relevance" : sortBy;

  /** Bumps on effect cleanup (Strict Mode remount, /notes unmount) so stale loadNotes cannot clear a good list. */
  const listFetchGen = useRef(0);
  const notesRef = useRef<Note[]>([]);
  const totalNotesRef = useRef(0);
  const currentPageRef = useRef(1);
  const listWidthRef = useRef(listWidth);
  notesRef.current = notes;
  totalNotesRef.current = totalNotes;
  currentPageRef.current = currentPage;
  listWidthRef.current = listWidth;

  // Notes-list / reader divider drag. Tracked with refs (not state) so the global
  // mousemove listener below is registered once, not re-subscribed on every pixel.
  const isResizingList = useRef(false);
  const dragStartX = useRef(0);
  const dragStartWidth = useRef(listWidth);

  const handleListResizeStart = (e: ReactMouseEvent) => {
    e.preventDefault();
    isResizingList.current = true;
    dragStartX.current = e.clientX;
    dragStartWidth.current = listWidthRef.current;
    document.body.style.cursor = "col-resize";
  };

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (!isResizingList.current) return;
      const delta = e.clientX - dragStartX.current;
      const next = Math.min(
        LIST_WIDTH_MAX,
        Math.max(LIST_WIDTH_MIN, dragStartWidth.current + delta),
      );
      setListWidth(next);
    };
    const onUp = () => {
      if (!isResizingList.current) return;
      isResizingList.current = false;
      document.body.style.cursor = "";
      savePref(LIST_WIDTH_KEY, listWidthRef.current);
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, []);

  /** Background polls must not flip the UI offline on one slow or dropped /health (common under load). */
  const HEALTH_TIMEOUT_MS = 10_000;

  /** Attempts (ms) between /health retries. Covers a backend restart gap (~6 s)
      before the UI declares offline, so a restart no longer latches the red panel. */
  const PROBE_RETRY_DELAYS_MS = [0, 2_000, 5_000];

  const probeBackend = async (opts?: { silent?: boolean }): Promise<boolean> => {
    const silent = Boolean(opts?.silent);
    if (!silent) {
      setBackendReachable("checking");
    }
    const healthUrl = `${getApiBaseUrl()}/health`;
    for (let attempt = 0; attempt < PROBE_RETRY_DELAYS_MS.length; attempt += 1) {
      if (attempt > 0) {
        if (!silent) {
          setBackendReachable("retrying");
        }
        const delay = PROBE_RETRY_DELAYS_MS[attempt] ?? 0;
        await new Promise((resolve) => {
          window.setTimeout(resolve, delay);
        });
      }
      try {
        const response = await fetch(healthUrl, {
          method: "GET",
          signal: AbortSignal.timeout(HEALTH_TIMEOUT_MS),
        });
        if (response.ok) {
          setBackendReachable("online");
          return true;
        }
      } catch (error) {
        DEBUG && devError("Backend health check failed:", error);
      }
    }
    if (!silent) {
      setBackendReachable("offline");
    }
    return false;
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
          const preserveCache = notesRef.current.length > 0 || totalNotesRef.current > 0;
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

      // Search, tags, date bounds and sort are all applied by the backend over the whole
      // matching set, so page N of "oldest first" really is the Nth slice of every match.
      // An empty query lists every note; there is no recency window.
      try {
        const response = await apiService.searchNotes(searchQuery, page, PAGE_SIZE, {
          tags: selectedTags,
          sort: effectiveSort,
          createdFrom: dateCreatedFrom,
          createdTo: dateCreatedTo,
          modifiedFrom: dateModifiedFrom,
          modifiedTo: dateModifiedTo,
        });

        if (!stillCurrent()) return;

        if (response.success && Array.isArray(response.data?.notes)) {
          const notesData = response.data.notes;
          setNotes(notesData);
          setFilteredNotes(notesData);
          setCurrentPage(response.data.page || page);
          setTotalPages(response.data.pages || 1);
          setTotalNotes(response.data.total ?? notesData.length);
          setBackendReachable("online");

          // Tag choices accumulate across pages and filters (the API has no tag list).
          setAvailableTags((prev) => {
            const allTags = new Set<string>(prev);
            for (const note of notesData) {
              for (const tag of noteTags(note)) allTags.add(tag);
            }
            return Array.from(allTags).sort();
          });
          setIsLoading(false);
          return;
        }
        setListError(response.error || "Could not load notes from the API.");
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
  const probeBackendRef = useRef(probeBackend);
  probeBackendRef.current = probeBackend;

  useBackendAutoReconnect(backendReachable === "offline" && !isLoading, async () => {
    await loadNotesRef.current(currentPageRef.current, { skipHealthProbe: true });
  });

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
      await loadNotesRef.current(1);
    })();

    const interval = setInterval(() => {
      void probeBackendRef.current({ silent: true });
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

  // Search text, tags, date bounds and sort are all applied by the backend, so any change
  // reloads page 1 (debounced). Nothing is filtered or re-sorted in the browser: that would
  // only ever reorder the single page that happens to be loaded.
  const filterKey = JSON.stringify([
    searchQuery,
    selectedTags,
    dateCreatedFrom,
    dateCreatedTo,
    dateModifiedFrom,
    dateModifiedTo,
    effectiveSort,
  ]);
  const lastFilterKey = useRef(filterKey);
  useEffect(() => {
    if (lastFilterKey.current === filterKey) return;
    lastFilterKey.current = filterKey;
    const timer = window.setTimeout(() => {
      void loadNotesRef.current(1, { skipHealthProbe: true });
    }, 300);
    return () => window.clearTimeout(timer);
  }, [filterKey]);

  useEffect(() => {
    // Select note based on selectedNoteId prop
    if (selectedNoteId) {
      const note = notes.find((n) => n.id === selectedNoteId);
      if (note) {
        // Keep the open note (it carries the full body); a list reload only has snippets.
        setSelectedNote((prev) => (prev && prev.id === note.id ? prev : note));
      }
    }
  }, [selectedNoteId, notes]);

  const handleNoteSelect = async (note: Note) => {
    const switching = selectedNoteRef.current?.id !== note.id;
    if (switching && editorMode && editorDirtyRef.current) {
      if (!window.confirm("Discard your unsaved edits?")) return;
    }
    if (switching) {
      setEditorMode(null);
      editorDirtyRef.current = false;
      setRawView(false);
      setBodyLoadedId(null);
      setMenu(null);
    }
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
        setBodyLoadedId(note.id);
      }
    } catch (error) {
      // Keep the basic note data if API call fails
    }
  };

  const handleNoteSelectRef = useRef(handleNoteSelect);
  handleNoteSelectRef.current = handleNoteSelect;

  /**
   * Open a note by permalink, file path or title. Looks in the loaded page first, then asks
   * the backend, so links work for notes that are not on the current page.
   */
  const openById = async (identifier: string) => {
    const wanted = identifier.split("#")[0]?.trim() ?? "";
    if (!wanted) return;
    const lower = wanted.toLowerCase();
    const local =
      notesRef.current.find((n) => n.id.toLowerCase() === lower) ??
      notesRef.current.find((n) => n.title.toLowerCase() === lower);
    const found = local ?? (await apiService.findNote(wanted));
    if (found) {
      await handleNoteSelectRef.current(found);
    } else {
      flash(`No note found for "${wanted}"`);
    }
  };
  const openByIdRef = useRef(openById);
  openByIdRef.current = openById;

  /** Follow a [[wikilink]] clicked inside the reading panel. */
  const handleWikiLink = (target: string) => {
    void openById(target);
  };

  // The sidebar, editor and header menus announce changes on a window event so the list,
  // the open note and the sidebar stay consistent without prop drilling.
  useEffect(() => {
    const onVault = (e: Event) => {
      const d = (e as CustomEvent<VaultEvent>).detail;
      if (!d) return;
      if (d.type === "open") {
        void openByIdRef.current(d.id);
        return;
      }
      void loadNotesRef.current(currentPageRef.current, { skipHealthProbe: true });
      const cur = selectedNoteRef.current;
      if (d.type === "deleted" && cur && cur.id === d.id) {
        setSelectedNote(null);
        setEditorMode(null);
        editorDirtyRef.current = false;
        onNoteSelectRef.current?.("");
      } else if (d.type === "saved" && cur && cur.id === d.id) {
        void handleNoteSelectRef.current(cur);
      }
    };
    window.addEventListener(VAULT_EVENT, onVault);
    return () => window.removeEventListener(VAULT_EVENT, onVault);
  }, []);

  // Close the export / more menus on outside click or Escape.
  useEffect(() => {
    if (!menu) return;
    const onDown = (e: MouseEvent) => {
      if (!(e.target as HTMLElement | null)?.closest?.("[data-menu-root]")) setMenu(null);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setMenu(null);
    };
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [menu]);

  const bodyReady = selectedNote != null && bodyLoadedId === selectedNote.id;

  const runExport = (format: ExportFormat) => {
    setMenu(null);
    if (!selectedNote) return;
    if (!bodyReady) {
      flash("Still loading the full note, try again in a moment");
      return;
    }
    const error = downloadNote(format, selectedNote);
    flash(error ?? `Exported as ${format === "markdown" ? "Markdown" : format.toUpperCase()}`);
  };

  const copyWithFlash = async (text: string, okMessage: string) => {
    setMenu(null);
    flash((await copyText(text)) ? okMessage : "Copy failed: clipboard not available");
  };

  const deleteSelected = async () => {
    setMenu(null);
    if (!selectedNote) return;
    const result = await confirmAndDeleteNote(selectedNote.id, selectedNote.title);
    if (result.error) flash(result.error);
  };

  const startNewNote = () => {
    if (editorMode && editorDirtyRef.current && !window.confirm("Discard your unsaved edits?")) {
      return;
    }
    editorDirtyRef.current = false;
    setEditorMode("create");
  };

  const selectedNoteIndex =
    selectedNote != null ? filteredNotes.findIndex((n) => n.id === selectedNote.id) : -1;
  const canGoPrevNote = selectedNoteIndex > 0;
  const canGoNextNote = selectedNoteIndex >= 0 && selectedNoteIndex < filteredNotes.length - 1;

  const navigateNote = useCallback(
    (delta: -1 | 1) => {
      if (selectedNoteIndex < 0) {
        return;
      }
      const target = filteredNotes[selectedNoteIndex + delta];
      if (target) {
        void handleNoteSelectRef.current(target);
      }
    },
    [filteredNotes, selectedNoteIndex],
  );

  useEffect(() => {
    if (!isFullscreen || !selectedNote) {
      return;
    }
    const onKeyDown = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement | null)?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") {
        return;
      }
      if (e.key === "ArrowLeft" || e.key === "k") {
        e.preventDefault();
        navigateNote(-1);
      } else if (e.key === "ArrowRight" || e.key === "j") {
        e.preventDefault();
        navigateNote(1);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [isFullscreen, selectedNote, navigateNote]);
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

    void openByIdRef.current(trimmed);
  }, [searchParams, vaultProject]);

  // Tree building helper
  interface TreeNode {
    name: string;
    path: string;
    note?: Note;
    children: Record<string, TreeNode>;
  }

  const buildTree = (notesList: Note[]): TreeNode[] => {
    const root: Record<string, TreeNode> = {};

    for (const note of notesList) {
      const fallbackId = String(note.id ?? "untitled");
      const permalink = String(
        (note as { permalink?: string }).permalink || note.title || note.id || "untitled",
      );
      const pathParts = permalink.includes("/")
        ? permalink.split("/").filter((p) => p.length > 0)
        : [permalink || fallbackId];

      let currentLevel = root;
      let currentPath = "";

      for (const [index, part] of pathParts.entries()) {
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
      }
    }

    const recursiveSort = (nodes: TreeNode[]): TreeNode[] => {
      const sorted = [...nodes].sort((a, b) => {
        const aIsFolder = Object.keys(a.children).length > 0 && !a.note;
        const bIsFolder = Object.keys(b.children).length > 0 && !b.note;
        if (aIsFolder !== bIsFolder) return aIsFolder ? -1 : 1;
        return String(a.name).localeCompare(String(b.name));
      });
      for (const node of sorted) {
        const sortedChildren = recursiveSort(Object.values(node.children));
        node.children = {};
        for (const c of sortedChildren) {
          node.children[c.name] = c;
        }
      }
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

  const activateTreeNode = (node: TreeNode, hasChildren: boolean) => {
    if (node.note) {
      void handleNoteSelect(node.note);
    } else if (hasChildren) {
      toggleNode(node.path);
    }
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
            onClick={() => activateTreeNode(node, hasChildren)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                activateTreeNode(node, hasChildren);
              }
            }}
          >
            {hasChildren && (
              <button
                type="button"
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
              placeholder="Search notes (updates as you type)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && loadNotes(1, { skipHealthProbe: true })}
              className="w-full bg-zinc-900 border border-zinc-700 rounded-lg pl-10 pr-3 py-2 text-sm text-white placeholder-zinc-500 outline-none focus:ring-1 focus:ring-amber-500/30"
            />
          </div>
          <button
            type="button"
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
                ? `${(currentPage - 1) * PAGE_SIZE + 1} - ${Math.min(currentPage * PAGE_SIZE, totalNotes)} of ${totalNotes}`
                : "0"}{" "}
              notes
            </div>
            <div className="flex items-center space-x-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  backendReachable === "online"
                    ? "bg-green-500"
                    : backendReachable === "offline"
                      ? "bg-red-500"
                      : "bg-amber-500 animate-pulse"
                }`}
              />
              <span className="text-xs text-muted-foreground">
                {backendReachable === "online"
                  ? "Backend online"
                  : backendReachable === "offline"
                    ? "Backend offline"
                    : backendReachable === "retrying"
                      ? "Retrying backend…"
                      : "Checking backend…"}
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
                <span className="label">Tags (notes must have all selected)</span>
                <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                  {availableTags.map((tag) => (
                    <button
                      key={tag}
                      type="button"
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
                <span className="label">Date Created</span>
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
                <span className="label">Date Modified</span>
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
                type="button"
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
        {notice && (
          <output className="absolute top-3 right-4 z-40 rounded-md border border-border bg-card px-3 py-2 text-sm shadow-lg">
            {notice}
          </output>
        )}
        {/* Notes List */}
        {!isFullscreen && (
          <div
            className="min-h-0 border-r border-border flex flex-col shrink-0 animate-in slide-in-from-left duration-300"
            style={{ width: listWidth }}
          >
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
                <button
                  type="button"
                  onClick={startNewNote}
                  className="p-1.5 rounded-md bg-accent/10 text-accent border border-accent/20 hover:bg-accent/20 transition-colors"
                  title="New note"
                  aria-label="New note"
                >
                  <Plus className="w-4 h-4" />
                </button>
                <select
                  value={effectiveSort}
                  onChange={(e) => {
                    setSortBy(e.target.value as NoteSort);
                    setSortChosen(true);
                  }}
                  className="bg-muted/50 border border-border rounded px-1.5 py-1 text-xs outline-none cursor-pointer max-w-[9.5rem]"
                  title="Sorts every matching note, not just this page"
                  aria-label="Sort notes"
                >
                  <option value="relevance" disabled={!searchQuery.trim()}>
                    Best match
                  </option>
                  <option value="modified_desc">Modified: newest</option>
                  <option value="modified_asc">Modified: oldest</option>
                  <option value="created_desc">Created: newest</option>
                  <option value="created_asc">Created: oldest</option>
                  <option value="title_asc">Title: A-Z</option>
                  <option value="title_desc">Title: Z-A</option>
                </select>
                <div className="flex bg-muted/50 p-1 rounded-md">
                  <button
                    type="button"
                    onClick={() => setViewMode("list")}
                    className={`p-1 rounded ${viewMode === "list" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}
                    title="List View"
                  >
                    <List className="w-4 h-4" />
                  </button>
                  <button
                    type="button"
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
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-accent" />
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
                    A browser cannot restart the API after a process crash. After you start it again
                    in a terminal, this page polls <code className="text-xs">/health</code> about
                    every 12 seconds and reloads notes when it responds.
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
                        Showing the last loaded list. The API may be busy; try again if actions
                        fail.
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
                      <button
                        type="button"
                        onClick={() => loadNotes(1)}
                        className="btn btn-primary"
                      >
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
                        type="button"
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
                              <button
                                key={note.id}
                                type="button"
                                onClick={() => handleNoteSelect(note)}
                                className={`block w-full text-left p-4 cursor-pointer hover:bg-muted/50 transition-colors ${
                                  selectedNote?.id === note.id
                                    ? "bg-accent/10 border-l-4 border-accent"
                                    : ""
                                }`}
                              >
                                <h3 className="font-medium text-sm mb-2 line-clamp-2">
                                  {note.title}
                                </h3>
                                <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
                                  {snippet(note.content)}
                                </p>
                                <div className="flex items-center justify-between text-xs text-muted-foreground">
                                  <span>{formatDate(note.modified)}</span>
                                  <div className="flex items-center space-x-2">
                                    <span className="truncate max-w-[9rem]" title={note.id}>
                                      {folderOf(note.id) || "(top level)"}
                                    </span>
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
                              </button>
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
                  type="button"
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
                  type="button"
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

        {/* Drag handle between the notes list and the reader. */}
        {!isFullscreen && (
          <button
            type="button"
            onMouseDown={handleListResizeStart}
            aria-label="Resize notes list"
            title="Drag to resize"
            className="w-1.5 shrink-0 cursor-col-resize bg-transparent hover:bg-accent/30 active:bg-accent/40 transition-colors relative group"
          >
            <GripVertical className="h-4 w-4 text-muted-foreground/40 group-hover:text-muted-foreground absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
          </button>
        )}

        {/* Note Content - min-h-0 so flex child can shrink and scroll */}
        <div className="flex-1 flex flex-col min-h-0">
          {editorMode ? (
            <NoteEditor
              key={editorMode === "create" ? "new-note" : selectedNote?.id}
              noteId={editorMode === "edit" ? selectedNote?.id : undefined}
              noteTitle={editorMode === "edit" ? selectedNote?.title : undefined}
              onDirtyChange={(d) => {
                editorDirtyRef.current = d;
              }}
              onSaved={(id) => {
                // Edits stay open after a save; a freshly created note switches to reading it.
                if (editorMode === "create") {
                  setEditorMode(null);
                  editorDirtyRef.current = false;
                  void openByIdRef.current(id);
                }
              }}
              onClose={() => {
                setEditorMode(null);
                editorDirtyRef.current = false;
              }}
            />
          ) : selectedNote ? (
            <>
              {/* Note Header */}
              <div className="p-6 border-b border-border shrink-0">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h1 className="text-2xl font-bold mb-2">{selectedNote.title}</h1>
                    <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                      <span>Created: {formatDate(selectedNote.created)}</span>
                      <span>Modified: {formatDate(selectedNote.modified)}</span>
                      {bodyReady && <span>{wordCount(selectedNote.content)} words</span>}
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
                    {filteredNotes.length > 1 && selectedNoteIndex >= 0 && (
                      <div
                        className={`flex items-center gap-1 rounded-md border border-border ${
                          isFullscreen ? "bg-muted/40 px-1" : ""
                        }`}
                      >
                        <button
                          type="button"
                          onClick={() => navigateNote(-1)}
                          disabled={!canGoPrevNote}
                          className="p-2 rounded-md hover:bg-muted transition-colors disabled:opacity-30 disabled:pointer-events-none"
                          title="Previous note (← or K)"
                          aria-label="Previous note"
                        >
                          <ChevronLeft className="h-4 w-4" />
                        </button>
                        <span
                          className="text-xs text-muted-foreground tabular-nums px-1 min-w-[4.5rem] text-center"
                          title="Position in filtered list"
                        >
                          {selectedNoteIndex + 1} / {filteredNotes.length}
                        </span>
                        <button
                          type="button"
                          onClick={() => navigateNote(1)}
                          disabled={!canGoNextNote}
                          className="p-2 rounded-md hover:bg-muted transition-colors disabled:opacity-30 disabled:pointer-events-none"
                          title="Next note (→ or J)"
                          aria-label="Next note"
                        >
                          <ChevronRight className="h-4 w-4" />
                        </button>
                      </div>
                    )}
                    <button
                      type="button"
                      onClick={() => setShowOutline((v) => !v)}
                      className={`p-2 rounded-md transition-colors border ${
                        showOutline
                          ? "bg-accent/10 text-accent border-accent/20"
                          : "border-transparent hover:bg-muted"
                      }`}
                      title={showOutline ? "Hide outline" : "Show outline"}
                      aria-pressed={showOutline}
                    >
                      <AlignLeft className="h-4 w-4" />
                    </button>
                    <button
                      type="button"
                      onClick={() =>
                        setReaderWide((w) => {
                          const next = !w;
                          savePref(READER_WIDTH_KEY, next);
                          return next;
                        })
                      }
                      className={`p-2 rounded-md transition-colors border ${
                        readerWide
                          ? "bg-accent/10 text-accent border-accent/20"
                          : "border-transparent hover:bg-muted"
                      }`}
                      title={readerWide ? "Comfortable width" : "Full width"}
                      aria-pressed={readerWide}
                    >
                      <PanelRightOpen className="h-4 w-4" />
                    </button>
                    <button
                      type="button"
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
                      type="button"
                      onClick={() => setEditorMode("edit")}
                      className="p-2 rounded-md hover:bg-accent/10 text-accent transition-colors border border-accent/20"
                      title="Edit note"
                      aria-label="Edit note"
                    >
                      <Pencil className="h-4 w-4" />
                    </button>
                    <button
                      type="button"
                      onClick={() => setRawView((v) => !v)}
                      aria-pressed={rawView}
                      className={`p-2 rounded-md transition-colors border ${
                        rawView
                          ? "bg-accent/10 text-accent border-accent/20"
                          : "border-transparent hover:bg-muted"
                      }`}
                      title={rawView ? "Show rendered note" : "Show markdown source"}
                      aria-label={rawView ? "Show rendered note" : "Show markdown source"}
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    <div className="relative" data-menu-root>
                      <button
                        type="button"
                        onClick={() => setMenu((m) => (m === "export" ? null : "export"))}
                        aria-haspopup="menu"
                        aria-expanded={menu === "export"}
                        className="p-2 rounded-md hover:bg-muted transition-colors"
                        title="Export"
                        aria-label="Export"
                      >
                        <Download className="h-4 w-4" />
                      </button>
                      {menu === "export" && (
                        <div
                          role="menu"
                          className="absolute right-0 top-full mt-1 z-30 w-48 rounded-md border border-border bg-card shadow-lg py-1"
                        >
                          {EXPORT_FORMATS.map((f) => (
                            <button
                              key={f.id}
                              type="button"
                              role="menuitem"
                              onClick={() => runExport(f.id)}
                              className="w-full text-left px-3 py-1.5 text-sm hover:bg-muted"
                            >
                              {f.label}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() =>
                        void copyWithFlash(
                          noteDeepLink(selectedNote.id),
                          "Link copied to clipboard",
                        )
                      }
                      className="p-2 rounded-md hover:bg-muted transition-colors"
                      title="Copy link to this note"
                      aria-label="Copy link to this note"
                    >
                      <Share className="h-4 w-4" />
                    </button>
                    <div className="relative" data-menu-root>
                      <button
                        type="button"
                        onClick={() => setMenu((m) => (m === "more" ? null : "more"))}
                        aria-haspopup="menu"
                        aria-expanded={menu === "more"}
                        className="p-2 rounded-md hover:bg-muted transition-colors"
                        title="More"
                        aria-label="More actions"
                      >
                        <MoreVertical className="h-4 w-4" />
                      </button>
                      {menu === "more" && (
                        <div
                          role="menu"
                          className="absolute right-0 top-full mt-1 z-30 w-56 rounded-md border border-border bg-card shadow-lg py-1"
                        >
                          <button
                            type="button"
                            role="menuitem"
                            onClick={() => void copyWithFlash(selectedNote.id, "Permalink copied")}
                            className="w-full text-left px-3 py-1.5 text-sm hover:bg-muted"
                          >
                            Copy permalink
                          </button>
                          <button
                            type="button"
                            role="menuitem"
                            onClick={() =>
                              void copyWithFlash(`[[${selectedNote.title}]]`, "Wikilink copied")
                            }
                            className="w-full text-left px-3 py-1.5 text-sm hover:bg-muted"
                          >
                            Copy as [[wikilink]]
                          </button>
                          <button
                            type="button"
                            role="menuitem"
                            disabled={!bodyReady}
                            onClick={() =>
                              void copyWithFlash(selectedNote.content, "Markdown copied")
                            }
                            className="w-full text-left px-3 py-1.5 text-sm hover:bg-muted disabled:opacity-40"
                          >
                            Copy markdown
                          </button>
                          <div className="my-1 border-t border-border" />
                          <button
                            type="button"
                            role="menuitem"
                            onClick={() => void deleteSelected()}
                            className="w-full text-left px-3 py-1.5 text-sm text-red-500 hover:bg-red-500/10 flex items-center gap-2"
                          >
                            <Trash2 className="h-4 w-4" />
                            Delete note
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Note Content - fills remaining height and scrolls */}
              <div className="flex-1 min-h-0 overflow-auto p-6 scrollbar-thin scrollbar-thumb-white/10">
                <div className={readerWide ? "" : "max-w-3xl mx-auto"}>
                  {rawView ? (
                    <pre className="whitespace-pre-wrap break-words font-mono text-[13px] leading-6 text-slate-300">
                      {selectedNote.content}
                    </pre>
                  ) : (
                    <Markdown
                      content={selectedNote.content}
                      onWikiLink={handleWikiLink}
                      variant="reader"
                      onHeadings={setHeadings}
                    />
                  )}
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

        {/* Outline - headings of the open note, click to jump. */}
        {showOutline && selectedNote && !editorMode && !rawView && !isFullscreen && (
          <div className="w-56 shrink-0 border-l border-border overflow-auto p-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">
              Outline
            </h4>
            {headings.length === 0 ? (
              <p className="text-xs text-muted-foreground">No headings in this note.</p>
            ) : (
              <nav className="space-y-0.5">
                {headings.map((h) => (
                  <button
                    key={h.id}
                    type="button"
                    onClick={() =>
                      document.getElementById(h.id)?.scrollIntoView({
                        behavior: "smooth",
                        block: "start",
                      })
                    }
                    className={`block w-full text-left text-xs truncate rounded px-2 py-1 text-muted-foreground hover:bg-muted/60 hover:text-foreground ${
                      h.level >= 3 ? "pl-5" : h.level === 2 ? "pl-2.5" : ""
                    }`}
                    title={h.text}
                  >
                    {h.text}
                  </button>
                ))}
              </nav>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
