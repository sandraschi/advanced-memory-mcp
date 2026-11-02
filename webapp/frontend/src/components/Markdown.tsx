import { marked } from "marked";
import { useEffect, useMemo } from "react";
import { slugify } from "./notes/noteUtils";

export interface MarkdownHeading {
  id: string;
  level: number;
  text: string;
}

interface MarkdownProps {
  content: string;
  /** Called when a [[wikilink]] is clicked with the raw link target. */
  onWikiLink?: (target: string) => void;
  /** "compact" keeps the dense dashboard look; "reader" is the long-form note style. */
  variant?: "compact" | "reader";
  /** Receives h1-h4 headings (with anchor ids) after each render, for outlines. */
  onHeadings?: (headings: MarkdownHeading[]) => void;
}

/** [[target]] and [[target|alias]] become <a data-wiki="target"> (pre-marked). */
function linkifyWikilinks(src: string): string {
  return src.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_m, target: string, alias?: string) => {
    const t = String(target).trim().replace(/"/g, "&quot;");
    const label = (alias ?? target).trim();
    return `<a href="#" data-wiki="${t}" class="wikilink">${label}</a>`;
  });
}

const COPY_BTN =
  '<button type="button" data-copy class="md-copy absolute right-2 top-2 rounded-md border border-white/10 bg-zinc-900/90 px-2 py-0.5 text-[11px] text-slate-400 opacity-0 transition-opacity hover:text-white group-hover:opacity-100 focus:opacity-100">Copy</button>';

/** Adds heading ids, code copy buttons, scrollable tables and safe external links. */
function decorate(html: string): { html: string; headings: MarkdownHeading[] } {
  const headings: MarkdownHeading[] = [];
  const used = new Map<string, number>();
  let out = html.replace(/<h([1-4])>([\s\S]*?)<\/h\1>/g, (_m, lvl: string, inner: string) => {
    const base = slugify(inner);
    const n = used.get(base) ?? 0;
    used.set(base, n + 1);
    const id = n === 0 ? base : `${base}-${n}`;
    const text = inner
      .replace(/<[^>]+>/g, "")
      .replace(/&amp;/g, "&")
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'");
    headings.push({ id, level: Number(lvl), text });
    return `<h${lvl} id="${id}" class="scroll-mt-4">${inner}</h${lvl}>`;
  });
  out = out
    .replace(/<pre>/g, `<div class="group relative">${COPY_BTN}<pre>`)
    .replace(/<\/pre>/g, "</pre></div>")
    .replace(/<table>/g, '<div class="md-table overflow-x-auto"><table>')
    .replace(/<\/table>/g, "</table></div>")
    .replace(
      /<a href="(https?:\/\/[^"]+)"/g,
      '<a href="$1" target="_blank" rel="noopener noreferrer"',
    );
  return { html: out, headings };
}

const SHARED = `max-w-none [overflow-wrap:anywhere]
  [&_a]:text-amber-400 [&_a:hover]:text-amber-300 [&_a]:underline [&_a]:decoration-amber-400/40 [&_a]:underline-offset-2 [&_a]:cursor-pointer
  [&_a.wikilink]:no-underline [&_a.wikilink]:rounded [&_a.wikilink]:bg-amber-400/10 [&_a.wikilink]:px-1
  [&_code]:rounded [&_code]:bg-black/50 [&_code]:border [&_code]:border-white/10
  [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:font-mono [&_code]:text-indigo-200
  [&_pre]:rounded-xl [&_pre]:bg-black/60 [&_pre]:border [&_pre]:border-white/10 [&_pre]:overflow-x-auto
  [&_pre_code]:bg-transparent [&_pre_code]:border-0 [&_pre_code]:p-0 [&_pre_code]:text-slate-200
  [&_blockquote]:border-l-2 [&_blockquote]:border-amber-400/50 [&_blockquote]:pl-4 [&_blockquote]:text-slate-400
  [&_ul]:list-disc [&_ol]:list-decimal [&_li]:marker:text-slate-500
  [&_table]:w-full [&_th]:text-left [&_th]:font-semibold [&_th]:text-white [&_th]:border-b [&_th]:border-white/15
  [&_td]:border-b [&_td]:border-white/5 [&_td]:align-top
  [&_hr]:border-white/10 [&_strong]:text-white [&_strong]:font-semibold
  [&_img]:rounded-lg [&_img]:max-w-full [&_input]:mr-2 [&_input]:accent-amber-400`;

const COMPACT = `text-sm leading-relaxed text-slate-300 space-y-3
  [&_h1]:text-2xl [&_h1]:font-bold [&_h1]:text-white [&_h1]:mt-2
  [&_h2]:text-xl [&_h2]:font-bold [&_h2]:text-white [&_h2]:mt-4
  [&_h3]:text-lg [&_h3]:font-semibold [&_h3]:text-white [&_h3]:mt-3
  [&_p]:my-2 [&_ul]:pl-6 [&_ul]:space-y-1 [&_ul]:my-2 [&_ol]:pl-6 [&_ol]:space-y-1 [&_ol]:my-2
  [&_code]:text-[13px] [&_pre]:p-4 [&_pre]:my-3 [&_blockquote]:italic [&_blockquote]:my-3
  [&_table]:text-sm [&_table]:my-3 [&_th]:pb-2 [&_th]:pr-4 [&_td]:py-2 [&_td]:pr-4 [&_hr]:my-4`;

const READER = `text-[15px] leading-7 text-slate-300
  [&>*:first-child]:mt-0
  [&_h1]:text-3xl [&_h1]:font-bold [&_h1]:tracking-tight [&_h1]:text-white [&_h1]:mt-10 [&_h1]:mb-4
  [&_h2]:text-[1.4rem] [&_h2]:font-semibold [&_h2]:tracking-tight [&_h2]:text-white [&_h2]:mt-10 [&_h2]:mb-3
  [&_h2]:pb-2 [&_h2]:border-b [&_h2]:border-white/[0.07]
  [&_h3]:text-lg [&_h3]:font-semibold [&_h3]:text-slate-100 [&_h3]:mt-8 [&_h3]:mb-2
  [&_h4]:text-base [&_h4]:font-semibold [&_h4]:text-slate-200 [&_h4]:mt-6 [&_h4]:mb-2
  [&_p]:my-4 [&_ul]:pl-6 [&_ul]:my-4 [&_ul]:space-y-1.5 [&_ol]:pl-6 [&_ol]:my-4 [&_ol]:space-y-1.5
  [&_li>ul]:my-1.5 [&_li>ol]:my-1.5
  [&_code]:text-[13.5px] [&_pre]:p-4 [&_pre]:leading-6
  [&_.group]:my-5 [&_blockquote]:my-5 [&_blockquote]:py-1
  [&_.md-table]:my-5 [&_table]:text-sm [&_th]:py-2 [&_th]:pr-6 [&_td]:py-2 [&_td]:pr-6 [&_hr]:my-8`;

export default function Markdown({
  content,
  onWikiLink,
  variant = "compact",
  onHeadings,
}: MarkdownProps) {
  const { html, headings } = useMemo(() => {
    const withWiki = linkifyWikilinks(content ?? "");
    // Synchronous parse (no async extensions registered); cast off the Promise union.
    return decorate(marked.parse(withWiki, { breaks: true, gfm: true }) as string);
  }, [content]);

  useEffect(() => {
    onHeadings?.(headings);
  }, [headings, onHeadings]);

  return (
    // Delegated click handles [data-wiki] anchors and [data-copy] buttons; both are
    // native focusable elements, so keyboard activation works without a key handler.
    // biome-ignore lint/a11y/useKeyWithClickEvents: native anchor/button keyboard behavior covers Enter
    <div
      className={`${SHARED} ${variant === "reader" ? READER : COMPACT}`}
      onClick={(e) => {
        const el = e.target as HTMLElement;
        const copyBtn = el.closest?.("[data-copy]");
        if (copyBtn) {
          e.preventDefault();
          const code = copyBtn.parentElement?.querySelector("pre")?.textContent ?? "";
          void navigator.clipboard?.writeText(code).then(
            () => {
              copyBtn.textContent = "Copied";
              window.setTimeout(() => {
                copyBtn.textContent = "Copy";
              }, 1500);
            },
            () => {
              copyBtn.textContent = "Copy failed";
            },
          );
          return;
        }
        if (!onWikiLink) return;
        const anchor = el.closest?.("[data-wiki]");
        if (anchor) {
          e.preventDefault();
          onWikiLink(anchor.getAttribute("data-wiki") ?? "");
        }
      }}
      // Local-first vault markdown rendered as HTML; same trust boundary as the
      // source file itself (previously a hand-rolled regex renderer, same sink).
      // biome-ignore lint/security/noDangerouslySetInnerHtml: local vault content, no remote input
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
