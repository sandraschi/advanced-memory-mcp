/**
 * Short map of how Advanced Memory layers work together (wikilinks vs FTS vs vectors).
 * Shown on vault/search surfaces so users are not bounced between pages without context.
 */
export function KnowledgeModelExplainer({ className = "" }: { className?: string }) {
  return (
    <div
      className={`rounded-lg border border-border/80 bg-muted/15 px-4 py-3 text-xs leading-relaxed text-muted-foreground ${className}`}
    >
      <p className="mb-2 font-medium text-foreground">How this app keeps three things straight</p>
      <ul className="list-disc space-y-1.5 pl-4">
        <li>
          <span className="font-medium text-foreground">Links between notes</span> —{" "}
          <code className="rounded bg-muted/80 px-1">[[wikilinks]]</code> in markdown and the{" "}
          <strong className="text-foreground/90">Knowledge Graph</strong>. That is the classic
          “basic memory” note-web pattern (structure you author).
        </li>
        <li>
          <span className="font-medium text-foreground">Keyword search (FTS)</span> — SQLite
          full-text index. Powers quick filtering in the <strong className="text-foreground/90">Note Vault</strong>{" "}
          list and text-style API search.
        </li>
        <li>
          <span className="font-medium text-foreground">Semantic search (LanceDB)</span> — vector
          chunks for “meaning” retrieval and hybrid search. Use <strong className="text-foreground/90">Semantic Search</strong>{" "}
          to try it; use <strong className="text-foreground/90">Vault sync → Rebuild search index</strong> to
          refresh FTS <em>and</em> vectors after big imports.
        </li>
        <li>
          <span className="font-medium text-foreground">Extra RAG folders</span> — optional absolute paths on the
          API host (e.g. a central docs repo) listed under{" "}
          <strong className="text-foreground/90">Vault sync → Extra RAG folders</strong>; they are chunked into
          LanceDB on the next full reindex and searched alongside your vault.
        </li>
      </ul>
    </div>
  );
}
