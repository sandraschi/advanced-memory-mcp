import { Book, ExternalLink, Search, Settings, Zap } from "lucide-react";
import { Link } from "react-router-dom";

const REPO = "https://github.com/sandraschi/advanced-memory-mcp";

export default function Help() {
  const sections = [
    {
      icon: Book,
      title: "Getting started",
      content: `Advanced Memory stores your notes as Markdown on disk, indexes them for search, and exposes tools to AI clients over MCP.

What you can do:
• Write, move, and link notes in folders you control
• Search by keywords and by meaning (when embeddings are enabled)
• Export to Docsify, HTML, PDF, and other formats where supported
• Build reusable “skills” from text you already trust`,
    },
    {
      icon: Search,
      title: "Search and research",
      content: `From the desktop app or MCP tools you can combine vault search with optional web and document research, depending on how the server is configured.

Typical sources (when enabled):
• Web search via configured providers
• arXiv and similar academic APIs
• GitHub search for public repositories
• PDF and file ingestion where parsers are installed`,
    },
    {
      icon: Zap,
      title: "Skills",
      content: `Skills are markdown instructions your assistant loads for a task. Good skills describe scope, steps, and guardrails.

Workflow:
1. Capture a workflow you repeat (checklist, decision tree, review rubric).
2. Store it under your skills path or generate from curated notes.
3. Point the client at the skill file when that task comes up again.`,
    },
    {
      icon: Settings,
      title: "Configuration",
      content: `Project roots, default project, database path, and LLM endpoints are set outside this web UI (config files and environment).

In this app:
• Use Settings for client-side preferences where available.
• For server behavior, follow the repository README and MCP client setup docs.`,
    },
  ];

  return (
    <div className="h-full min-h-0 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10">
      <div className="max-w-5xl mx-auto px-6 py-8 space-y-10 pb-16">
        <header className="space-y-3 border-b border-white/10 pb-8">
          <h1 className="text-3xl font-bold tracking-tight text-white">Help</h1>
          <p className="text-lg text-slate-400 max-w-3xl">
            Advanced Memory is a local-first notes and search backend for MCP-capable assistants.
            This page summarizes how the pieces fit together; for authoritative detail use the
            repository documentation.
          </p>
        </header>

        <div className="grid gap-6 md:grid-cols-2">
          {sections.map((section, index) => (
            <article
              key={index}
              className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 shadow-sm shadow-black/20"
            >
              <div className="flex items-start gap-3">
                <div className="shrink-0 rounded-lg bg-indigo-500/15 p-2">
                  <section.icon className="h-5 w-5 text-indigo-300" />
                </div>
                <div className="min-w-0">
                  <h2 className="text-lg font-semibold text-white mb-3">{section.title}</h2>
                  <div className="text-sm text-slate-400 whitespace-pre-line leading-relaxed">
                    {section.content}
                  </div>
                </div>
              </div>
            </article>
          ))}
        </div>

        <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Shortcuts</h2>
          <div className="grid gap-3 sm:grid-cols-3">
            <Link
              to="/settings"
              className="rounded-xl border border-white/10 bg-black/30 p-4 text-left hover:border-indigo-400/40 hover:bg-white/[0.05] transition-colors"
            >
              <h3 className="font-medium text-white mb-1">Settings</h3>
              <p className="text-sm text-slate-500">App preferences</p>
            </Link>
            <Link
              to="/logs"
              className="rounded-xl border border-white/10 bg-black/30 p-4 text-left hover:border-indigo-400/40 hover:bg-white/[0.05] transition-colors"
            >
              <h3 className="font-medium text-white mb-1">System log</h3>
              <p className="text-sm text-slate-500">Recent server lines</p>
            </Link>
            <Link
              to="/notes"
              className="rounded-xl border border-white/10 bg-black/30 p-4 text-left hover:border-indigo-400/40 hover:bg-white/[0.05] transition-colors"
            >
              <h3 className="font-medium text-white mb-1">Notes</h3>
              <p className="text-sm text-slate-500">Open the vault</p>
            </Link>
          </div>
        </section>

        <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Repository</h2>
          <ul className="space-y-3">
            <li>
              <a
                href={`${REPO}#readme`}
                target="_blank"
                rel="noreferrer"
                className="flex items-center justify-between gap-4 rounded-xl border border-white/10 p-4 hover:bg-white/[0.05]"
              >
                <div>
                  <div className="font-medium text-white">README &amp; setup</div>
                  <div className="text-sm text-slate-500">
                    Install, configure, MCP client wiring
                  </div>
                </div>
                <ExternalLink className="h-4 w-4 text-slate-500 shrink-0" />
              </a>
            </li>
            <li>
              <a
                href={`${REPO}/issues`}
                target="_blank"
                rel="noreferrer"
                className="flex items-center justify-between gap-4 rounded-xl border border-white/10 p-4 hover:bg-white/[0.05]"
              >
                <div>
                  <div className="font-medium text-white">Issues</div>
                  <div className="text-sm text-slate-500">Bug reports and feature requests</div>
                </div>
                <ExternalLink className="h-4 w-4 text-slate-500 shrink-0" />
              </a>
            </li>
          </ul>
        </section>
      </div>
    </div>
  );
}
