import { Bold, Code, Heading2, Italic, Link as LinkIcon, List, Quote, Save, X } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { apiService } from "../../services/api";
import Markdown from "../Markdown";
import { emitVault, wordCount } from "./noteUtils";

type PaneMode = "write" | "split" | "preview";

interface NoteEditorProps {
  /** Existing note to edit. Omit to create a new note. */
  noteId?: string | undefined;
  /** Display title for an existing note (shown while its content loads). */
  noteTitle?: string | undefined;
  /** Called after a successful save or create, with the note's id. */
  onSaved: (id: string) => void;
  /** Called when the editor should close (after save-and-close, or discard). */
  onClose: () => void;
  /** Reports whether there are unsaved edits, so the host can guard navigation. */
  onDirtyChange?: ((dirty: boolean) => void) | undefined;
}

const CREATE_SEED = "# New note\n\n";

const PANE_KEY = "am.notes.editorPane";

function readPane(): PaneMode {
  try {
    const v = window.localStorage.getItem(PANE_KEY);
    if (v === "write" || v === "split" || v === "preview") return v;
  } catch {
    /* storage unavailable */
  }
  return "split";
}

export default function NoteEditor({
  noteId,
  noteTitle,
  onSaved,
  onClose,
  onDirtyChange,
}: NoteEditorProps) {
  const isCreate = !noteId;
  const [loading, setLoading] = useState(!isCreate);
  const [loadError, setLoadError] = useState("");
  const [draft, setDraft] = useState("");
  /** Text as last loaded from or written to the server; dirty = draft differs from this. */
  const [baseline, setBaseline] = useState("");
  const [title, setTitle] = useState("");
  const [folder, setFolder] = useState("notes");
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState("");
  const [statusIsError, setStatusIsError] = useState(false);
  const [pane, setPane] = useState<PaneMode>(readPane);
  const areaRef = useRef<HTMLTextAreaElement | null>(null);

  const dirty = draft !== baseline || (isCreate && title.trim() !== "");

  useEffect(() => {
    onDirtyChange?.(dirty);
  }, [dirty, onDirtyChange]);
  // Closing the editor must not leave the host believing there are unsaved edits.
  useEffect(() => () => onDirtyChange?.(false), [onDirtyChange]);

  // Load the full body fresh from the API. The list only holds a search snippet,
  // so saving anything derived from it would truncate the note.
  useEffect(() => {
    if (!noteId) {
      setDraft(CREATE_SEED);
      setBaseline(CREATE_SEED);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setLoadError("");
    (async () => {
      const res = await apiService.getNote(noteId);
      if (cancelled) return;
      const body = (res.data as { content?: unknown } | undefined)?.content;
      if (res.success && typeof body === "string") {
        setDraft(body);
        setBaseline(body);
      } else {
        setLoadError(res.error || "Could not load the note body. Editing is disabled.");
      }
      setLoading(false);
    })();
    return () => {
      cancelled = true;
    };
  }, [noteId]);

  // Warn on tab close / reload with unsaved edits.
  useEffect(() => {
    if (!dirty) return;
    const onBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      e.returnValue = "";
    };
    window.addEventListener("beforeunload", onBeforeUnload);
    return () => window.removeEventListener("beforeunload", onBeforeUnload);
  }, [dirty]);

  const choosePane = (next: PaneMode) => {
    setPane(next);
    try {
      window.localStorage.setItem(PANE_KEY, next);
    } catch {
      /* storage unavailable */
    }
  };

  const setMessage = useCallback((text: string, isError = false) => {
    setStatus(text);
    setStatusIsError(isError);
  }, []);

  const save = useCallback(
    async (closeAfter: boolean) => {
      if (saving || loading || loadError) return;
      setSaving(true);
      setMessage("");
      try {
        if (isCreate) {
          const t = title.trim();
          if (!t) {
            setMessage("Give the note a title first.", true);
            return;
          }
          const res = await apiService.createNote({
            title: t,
            folder: folder.trim().replace(/^\/+|\/+$/g, ""),
            content: draft,
          });
          if (!res.success || !res.data) {
            setMessage(res.error || "Create failed.", true);
            return;
          }
          const id = res.data.permalink || t;
          setBaseline(draft);
          emitVault({ type: "created", id });
          onSaved(id);
          if (closeAfter) onClose();
          return;
        }

        // Overwrite guard: the sync watcher and other tools write to this vault too.
        const current = await apiService.getNote(noteId as string);
        const onServer = (current.data as { content?: unknown } | undefined)?.content;
        if (current.success && typeof onServer === "string" && onServer !== baseline) {
          const overwrite = window.confirm(
            "This note changed on disk since you opened it.\n\nOK = overwrite with your version\nCancel = keep editing (copy your text first if you want to merge)",
          );
          if (!overwrite) {
            setMessage("Save cancelled: the note changed elsewhere.", true);
            return;
          }
        }
        const res = await apiService.updateNoteBody(noteId as string, draft);
        if (!res.success) {
          setMessage(res.error || "Save failed.", true);
          return;
        }
        setBaseline(draft);
        setMessage(`Saved ${new Date().toLocaleTimeString()}`);
        emitVault({ type: "saved", id: noteId as string });
        onSaved(noteId as string);
        if (closeAfter) onClose();
      } finally {
        setSaving(false);
      }
    },
    [
      saving,
      loading,
      loadError,
      isCreate,
      title,
      folder,
      draft,
      noteId,
      baseline,
      onSaved,
      onClose,
      setMessage,
    ],
  );

  const requestClose = () => {
    if (dirty && !window.confirm("Discard your unsaved changes?")) return;
    onClose();
  };

  // --- toolbar helpers: operate on the textarea selection ---------------------------------
  const edit = (
    apply: (
      sel: string,
      before: string,
      after: string,
    ) => { text: string; from: number; to: number },
  ) => {
    const el = areaRef.current;
    if (!el) return;
    const start = el.selectionStart;
    const end = el.selectionEnd;
    const before = draft.slice(0, start);
    const sel = draft.slice(start, end);
    const after = draft.slice(end);
    const out = apply(sel, before, after);
    const next = before + out.text + after;
    setDraft(next);
    requestAnimationFrame(() => {
      el.focus();
      el.setSelectionRange(start + out.from, start + out.to);
    });
  };

  const wrap = (left: string, right: string, placeholder: string) =>
    edit((sel) => {
      const inner = sel || placeholder;
      return { text: `${left}${inner}${right}`, from: left.length, to: left.length + inner.length };
    });

  const linePrefix = (prefix: string) =>
    edit((sel, before) => {
      const atLineStart = before === "" || before.endsWith("\n");
      const lead = atLineStart ? "" : "\n";
      const body = (sel || "text")
        .split("\n")
        .map((l) => `${prefix}${l}`)
        .join("\n");
      return { text: `${lead}${body}`, from: lead.length, to: lead.length + body.length };
    });

  const toolbar: Array<{ key: string; title: string; run: () => void; icon: React.ReactNode }> = [
    {
      key: "h2",
      title: "Heading",
      run: () => linePrefix("## "),
      icon: <Heading2 className="h-4 w-4" />,
    },
    {
      key: "b",
      title: "Bold",
      run: () => wrap("**", "**", "bold"),
      icon: <Bold className="h-4 w-4" />,
    },
    {
      key: "i",
      title: "Italic",
      run: () => wrap("*", "*", "italic"),
      icon: <Italic className="h-4 w-4" />,
    },
    {
      key: "c",
      title: "Inline code",
      run: () => wrap("`", "`", "code"),
      icon: <Code className="h-4 w-4" />,
    },
    {
      key: "l",
      title: "Link",
      run: () => wrap("[", "](https://)", "text"),
      icon: <LinkIcon className="h-4 w-4" />,
    },
    {
      key: "w",
      title: "Wikilink to another note",
      run: () => wrap("[[", "]]", "Note title"),
      icon: <span className="text-xs font-mono leading-none">[[ ]]</span>,
    },
    {
      key: "ul",
      title: "Bullet list",
      run: () => linePrefix("- "),
      icon: <List className="h-4 w-4" />,
    },
    { key: "q", title: "Quote", run: () => linePrefix("> "), icon: <Quote className="h-4 w-4" /> },
  ];

  const segBtn = (mode: PaneMode, label: string) => (
    <button
      key={mode}
      type="button"
      onClick={() => choosePane(mode)}
      aria-pressed={pane === mode}
      className={`px-3 py-1 text-xs rounded ${
        pane === mode
          ? "bg-background shadow-sm text-foreground"
          : "text-muted-foreground hover:text-foreground"
      }`}
    >
      {label}
    </button>
  );

  const showWrite = pane !== "preview";
  const showPreview = pane !== "write";
  const disabled = loading || Boolean(loadError);

  return (
    <div className="flex-1 min-h-0 flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-border flex flex-wrap items-center gap-3 shrink-0">
        <div className="flex-1 min-w-[12rem]">
          {isCreate ? (
            <div className="flex flex-wrap gap-2">
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Title"
                aria-label="New note title"
                className="flex-1 min-w-[10rem] bg-muted/40 border border-border rounded px-2 py-1 text-sm outline-none focus:border-accent"
              />
              <input
                value={folder}
                onChange={(e) => setFolder(e.target.value)}
                placeholder="folder"
                aria-label="Folder"
                className="w-40 bg-muted/40 border border-border rounded px-2 py-1 text-sm outline-none focus:border-accent font-mono"
              />
            </div>
          ) : (
            <div className="min-w-0">
              <div className="text-sm font-semibold truncate" title={noteTitle}>
                Editing: {noteTitle || noteId}
              </div>
              <div className="text-xs text-muted-foreground truncate font-mono" title={noteId}>
                {noteId}
              </div>
            </div>
          )}
        </div>
        <span
          className={`text-xs ${statusIsError ? "text-red-400" : dirty ? "text-amber-400" : "text-muted-foreground"}`}
          aria-live="polite"
        >
          {status || (dirty ? "Unsaved changes" : "")}
        </span>
        <div className="flex bg-muted/50 p-0.5 rounded-md">
          {segBtn("write", "Write")}
          {segBtn("split", "Split")}
          {segBtn("preview", "Preview")}
        </div>
        <button
          type="button"
          onClick={() => void save(false)}
          disabled={disabled || saving || (!isCreate && !dirty)}
          className="btn btn-primary btn-sm inline-flex items-center gap-1 disabled:opacity-50"
          title="Save (Ctrl+S)"
        >
          <Save className="h-4 w-4" />
          {saving ? "Saving..." : isCreate ? "Create" : "Save"}
        </button>
        <button
          type="button"
          onClick={requestClose}
          className="btn btn-outline btn-sm inline-flex items-center gap-1"
          title="Close editor"
        >
          <X className="h-4 w-4" />
          Close
        </button>
      </div>

      {/* Toolbar */}
      {showWrite && (
        <div className="px-4 py-1.5 border-b border-border flex items-center gap-1 shrink-0">
          {toolbar.map((t) => (
            <button
              key={t.key}
              type="button"
              title={t.title}
              aria-label={t.title}
              onClick={t.run}
              disabled={disabled}
              className="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground disabled:opacity-40 inline-flex items-center justify-center min-w-[2rem]"
            >
              {t.icon}
            </button>
          ))}
        </div>
      )}

      {/* Body */}
      {loading ? (
        <div className="flex-1 flex items-center justify-center text-muted-foreground text-sm">
          Loading note body...
        </div>
      ) : loadError ? (
        <div className="flex-1 flex items-center justify-center text-red-400 text-sm p-6 text-center">
          {loadError}
        </div>
      ) : (
        <div className="flex-1 min-h-0 flex">
          {showWrite && (
            <textarea
              ref={areaRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => {
                if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
                  e.preventDefault();
                  void save(false);
                }
              }}
              spellCheck
              aria-label="Markdown source"
              className={`${showPreview ? "w-1/2 border-r border-border" : "w-full"} h-full resize-none bg-transparent p-5 font-mono text-[13.5px] leading-6 outline-none`}
            />
          )}
          {showPreview && (
            <div className={`${showWrite ? "w-1/2" : "w-full"} h-full overflow-auto p-6`}>
              <div className={showWrite ? "" : "max-w-3xl mx-auto"}>
                {/* Preview only: wikilinks are inert while editing. */}
                <Markdown content={draft} variant="reader" onWikiLink={() => undefined} />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="px-4 py-1.5 border-t border-border text-xs text-muted-foreground flex gap-4 shrink-0">
        <span>{wordCount(draft).toLocaleString()} words</span>
        <span>{draft.length.toLocaleString()} chars</span>
        <span className="ml-auto">Ctrl+S to save</span>
      </div>
    </div>
  );
}
