import { useMemo } from "react";

export default function Markdown({ content }: { content: string }) {
  const html = useMemo(() => {
    let result = content
      .replace(/^### (.+)$/gm, "<h3>$1</h3>")
      .replace(/^## (.+)$/gm, "<h2>$1</h2>")
      .replace(/^# (.+)$/gm, "<h1>$1</h1>")
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>")
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/^- (.+)$/gm, "<li>$1</li>")
      .replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-amber-400 hover:text-amber-300 underline">$1</a>')
      .replace(/\n\n/g, "</p><p>")
      .replace(/^(.+)$/gm, (m) => {
        if (m.startsWith("<h") || m.startsWith("<li") || m.startsWith("<ul") || m.startsWith("</p")) return m;
        if (m.startsWith("<p")) return m;
        return m;
      });
    return `<p>${result}</p>`;
  }, [content]);
  return (
    <div
      className="prose prose-invert max-w-none text-sm leading-relaxed space-y-2"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
