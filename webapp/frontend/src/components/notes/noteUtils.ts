import { marked } from "marked";

/** Shared helpers for the Note Vault reader. No React; browser-only where noted. */

/** API / list state may still carry non-array tags; never assume `.tags` is an array. */
export function noteTags(note: { tags?: unknown }): string[] {
  if (Array.isArray(note.tags)) {
    return (note.tags as unknown[]).map((t) => String(t)).filter((t) => t.length > 0);
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

export interface Frontmatter {
  props: Array<[string, string]>;
  body: string;
}

/** Split a leading YAML frontmatter block off the markdown body (shallow key: value parse). */
export function splitFrontmatter(src: string): Frontmatter {
  const text = src ?? "";
  const m = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/.exec(text);
  if (!m) return { props: [], body: text };
  const props: Array<[string, string]> = [];
  for (const line of (m[1] ?? "").split(/\r?\n/)) {
    const kv = /^([A-Za-z0-9_.-]+):\s*(.*)$/.exec(line);
    if (kv?.[1] && kv[2] !== undefined && kv[2].trim() !== "") {
      props.push([kv[1], kv[2].trim().replace(/^["']|["']$/g, "")]);
    }
  }
  return { props, body: text.slice(m[0].length) };
}

/** Plain-text snippet for list cards: drops frontmatter, markdown syntax and the leading H1. */
export function snippet(src: string, max = 180): string {
  const { body } = splitFrontmatter(src);
  const plain = body
    .replace(/^#\s+.*$/m, "")
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`([^`]*)`/g, "$1")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
    .replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_m, t: string, a?: string) => a ?? t)
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/^[>\-*+]\s+|^\d+\.\s+|^#{1,6}\s+/gm, "")
    .replace(/[*_~|]/g, "")
    .replace(/\s+/g, " ")
    .trim();
  return plain.length > max ? `${plain.slice(0, max).trimEnd()}...` : plain;
}

export interface WikiLink {
  target: string;
  label: string;
}

/** Unique [[target]] / [[target|alias]] links in document order. */
export function extractWikiLinks(src: string): WikiLink[] {
  const seen = new Set<string>();
  const out: WikiLink[] = [];
  for (const m of (src ?? "").matchAll(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g)) {
    const target = (m[1] ?? "").trim();
    const key = target.toLowerCase();
    if (!target || seen.has(key)) continue;
    seen.add(key);
    out.push({ target, label: (m[2] ?? target).trim() });
  }
  return out;
}

export function wordCount(src: string): number {
  const words = splitFrontmatter(src).body.match(/[\p{L}\p{N}]+(?:['-][\p{L}\p{N}]+)*/gu);
  return words ? words.length : 0;
}

/** "notes/sub/x" -> "notes/sub"; "" for top-level permalinks. */
export function folderOf(permalink: string): string {
  const i = permalink.lastIndexOf("/");
  return i > 0 ? permalink.slice(0, i) : "";
}

const RTF = new Intl.RelativeTimeFormat("en", { numeric: "auto" });

export function relativeTime(iso: string): string {
  const t = new Date(iso).getTime();
  if (Number.isNaN(t)) return "";
  const diffSec = Math.round((t - Date.now()) / 1000);
  const abs = Math.abs(diffSec);
  if (abs < 60) return RTF.format(diffSec, "second");
  if (abs < 3600) return RTF.format(Math.round(diffSec / 60), "minute");
  if (abs < 86400) return RTF.format(Math.round(diffSec / 3600), "hour");
  if (abs < 86400 * 30) return RTF.format(Math.round(diffSec / 86400), "day");
  return new Date(t).toLocaleDateString("en-GB", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function fullDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "unknown";
  return d.toLocaleString("en-GB", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** Stable heading slug used for outline anchors. */
export function slugify(text: string): string {
  return (
    text
      .toLowerCase()
      .replace(/<[^>]+>/g, "")
      .replace(/&[a-z#0-9]+;/gi, "")
      .replace(/[^\p{L}\p{N}\s-]/gu, "")
      .trim()
      .replace(/\s+/g, "-")
      .slice(0, 80) || "section"
  );
}

/** Browser-local persisted setting; never throws (private windows, blocked storage). */
export function loadPref<T>(key: string, fallback: T): T {
  try {
    const raw = window.localStorage.getItem(key);
    return raw === null ? fallback : (JSON.parse(raw) as T);
  } catch {
    return fallback;
  }
}

export function savePref(key: string, value: unknown): void {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* storage unavailable: setting stays in memory only */
  }
}

/* ------------------------------------------------------------------ */
/* Vault events: lets the sidebar, editor and list stay in sync        */
/* without threading callbacks through Layout / App.                   */
/* ------------------------------------------------------------------ */

export const VAULT_EVENT = "vault:event";

export type VaultEvent =
  | { type: "saved"; id: string }
  | { type: "created"; id: string }
  | { type: "deleted"; id: string }
  /** Ask the Note Vault to open a note by permalink, file path or title. */
  | { type: "open"; id: string };

export function emitVault(detail: VaultEvent): void {
  window.dispatchEvent(new CustomEvent<VaultEvent>(VAULT_EVENT, { detail }));
}

/* ------------------------------------------------------------------ */
/* Export: everything is built in the browser from the loaded note.    */
/* ------------------------------------------------------------------ */

export type ExportFormat = "markdown" | "html" | "pdf" | "json" | "txt";

export interface ExportableNote {
  id: string;
  title: string;
  content: string;
  tags?: string[];
  created?: string;
  modified?: string;
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function fileStem(title: string): string {
  const stem = title
    .replace(/[<>:"/\\|?*]/g, "-")
    .split("")
    .map((ch) => (ch.charCodeAt(0) < 32 ? "-" : ch))
    .join("")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 80);
  return stem || "note";
}

function saveBlob(name: string, mime: string, data: string): void {
  const url = URL.createObjectURL(new Blob([data], { type: `${mime};charset=utf-8` }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/** Standalone HTML page for a note (used by the HTML and PDF exports). */
export function noteToHtml(note: ExportableNote): string {
  const body = marked.parse(splitFrontmatter(note.content).body, {
    gfm: true,
    breaks: true,
  }) as string;
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>${escapeHtml(note.title)}</title>
<style>
body{font:16px/1.65 system-ui,sans-serif;max-width:46rem;margin:2.5rem auto;padding:0 1rem;color:#1a1a1a}
h1,h2,h3{line-height:1.25}h2{border-bottom:1px solid #ddd;padding-bottom:.2em}
pre{background:#f4f4f5;padding:1rem;overflow:auto;border-radius:6px}code{background:#f4f4f5;padding:.1em .3em;border-radius:3px}
pre code{background:none;padding:0}blockquote{border-left:3px solid #ccc;margin-left:0;padding-left:1rem;color:#555}
table{border-collapse:collapse}td,th{border:1px solid #ddd;padding:.35rem .6rem}
</style></head><body>
<h1>${escapeHtml(note.title)}</h1>
${body}
</body></html>`;
}

/**
 * Export a note. Returns an error string on failure, or null on success.
 * "pdf" opens the browser print dialog on the rendered page (choose "Save as PDF");
 * there is no server-side PDF renderer behind this.
 */
export function downloadNote(format: ExportFormat, note: ExportableNote): string | null {
  const stem = fileStem(note.title);
  switch (format) {
    case "markdown":
      saveBlob(`${stem}.md`, "text/markdown", note.content);
      return null;
    case "txt":
      saveBlob(`${stem}.txt`, "text/plain", splitFrontmatter(note.content).body);
      return null;
    case "json":
      saveBlob(
        `${stem}.json`,
        "application/json",
        JSON.stringify(
          {
            id: note.id,
            title: note.title,
            tags: note.tags ?? [],
            created: note.created ?? null,
            modified: note.modified ?? null,
            content: note.content,
          },
          null,
          2,
        ),
      );
      return null;
    case "html":
      saveBlob(`${stem}.html`, "text/html", noteToHtml(note));
      return null;
    case "pdf": {
      const w = window.open("", "_blank");
      if (!w) return "Popup blocked: allow popups for this page to print or save as PDF.";
      w.document.open();
      w.document.write(noteToHtml(note));
      w.document.close();
      w.focus();
      window.setTimeout(() => w.print(), 300);
      return null;
    }
    default:
      return "Unknown export format";
  }
}
