import { marked } from "marked";
import { useMemo } from "react";

interface MarkdownProps {
  content: string;
  /** Called when a [[wikilink]] is clicked with the raw link target. */
  onWikiLink?: (target: string) => void;
}

/** [[target]] and [[target|alias]] become <a data-wiki="target"> (pre-marked). */
function linkifyWikilinks(src: string): string {
  return src.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_m, target: string, alias?: string) => {
    const t = String(target).trim().replace(/"/g, "&quot;");
    const label = (alias ?? target).trim();
    return `<a href="#" data-wiki="${t}">${label}</a>`;
  });
}

export default function Markdown({ content, onWikiLink }: MarkdownProps) {
  const html = useMemo(() => {
    const withWiki = linkifyWikilinks(content ?? "");
    // Synchronous parse (no async extensions registered) — cast off the Promise union.
    return marked.parse(withWiki, { breaks: true, gfm: true }) as string;
  }, [content]);

  return (
    // Delegated click only handles [data-wiki] anchors; keyboard users activate
    // the same anchors with Enter (native link behavior), so no extra key handler.
    // biome-ignore lint/a11y/useKeyWithClickEvents: native anchor keyboard behavior covers Enter
    <div
      className="max-w-none text-sm leading-relaxed text-slate-300 space-y-3
        [&_h1]:text-2xl [&_h1]:font-bold [&_h1]:text-white [&_h1]:mt-2
        [&_h2]:text-xl [&_h2]:font-bold [&_h2]:text-white [&_h2]:mt-4
        [&_h3]:text-lg [&_h3]:font-semibold [&_h3]:text-white [&_h3]:mt-3
        [&_p]:my-2
        [&_ul]:list-disc [&_ul]:pl-6 [&_ul]:space-y-1 [&_ul]:my-2
        [&_ol]:list-decimal [&_ol]:pl-6 [&_ol]:space-y-1 [&_ol]:my-2
        [&_li]:leading-relaxed
        [&_a]:text-amber-400 [&_a]:hover:text-amber-300 [&_a]:underline [&_a]:cursor-pointer
        [&_code]:rounded [&_code]:bg-black/60 [&_code]:border [&_code]:border-white/10
        [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:font-mono [&_code]:text-[13px] [&_code]:text-indigo-200
        [&_pre]:rounded-xl [&_pre]:bg-black/60 [&_pre]:border [&_pre]:border-white/10
        [&_pre]:p-4 [&_pre]:overflow-x-auto [&_pre]:my-3
        [&_pre_code]:bg-transparent [&_pre_code]:border-0 [&_pre_code]:p-0
        [&_blockquote]:border-l-2 [&_blockquote]:border-indigo-400/50 [&_blockquote]:pl-4
        [&_blockquote]:text-slate-400 [&_blockquote]:italic [&_blockquote]:my-3
        [&_table]:w-full [&_table]:text-sm [&_table]:my-3
        [&_th]:text-left [&_th]:font-semibold [&_th]:text-white
        [&_th]:border-b [&_th]:border-white/15 [&_th]:pb-2 [&_th]:pr-4
        [&_td]:border-b [&_td]:border-white/5 [&_td]:py-2 [&_td]:pr-4
        [&_hr]:border-white/10 [&_hr]:my-4
        [&_strong]:text-white [&_strong]:font-semibold"
      onClick={(e) => {
        if (!onWikiLink) return;
        const anchor = (e.target as HTMLElement).closest?.("[data-wiki]");
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
