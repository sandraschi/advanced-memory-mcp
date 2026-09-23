import {
  AlertTriangle,
  Book,
  Database,
  ExternalLink,
  FileQuestion,
  HelpCircle,
  Layers,
  Network,
  Search,
  Wrench,
  Zap,
} from "lucide-react";
import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import { Link } from "react-router-dom";

const REPO = "https://github.com/sandraschi/advanced-memory-mcp";

type HelpTab =
  | "overview"
  | "wrappee"
  | "vault"
  | "search"
  | "skills"
  | "api"
  | "troubleshoot"
  | "faq";

const TABS: Array<{ id: HelpTab; name: string; description: string }> = [
  { id: "overview", name: "Overview", description: "What this app is and how it fits together" },
  {
    id: "wrappee",
    name: "Backend & Data",
    description: "State owners, data locations, verification signals",
  },
  { id: "vault", name: "Vault & Projects", description: "Notes on disk, projects, sync and watch" },
  {
    id: "search",
    name: "Search & Research",
    description: "Keyword, semantic and research sources",
  },
  { id: "skills", name: "Skills", description: "Reusable instruction packs for assistants" },
  { id: "api", name: "API & Ports", description: "Ports, services, env vars and endpoints" },
  { id: "troubleshoot", name: "Error fix", description: "Symptoms, causes and exact fixes" },
  { id: "faq", name: "FAQ", description: "Frequently asked questions" },
];

function Card({
  children,
  testid,
}: {
  children: ReactNode;
  testid?: string;
}) {
  return (
    <section
      data-testid={testid}
      className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 shadow-sm shadow-black/20"
    >
      {children}
    </section>
  );
}

function H2({ children }: { children: ReactNode }) {
  return <h2 className="text-lg font-semibold text-white mb-3">{children}</h2>;
}

function P({ children }: { children: ReactNode }) {
  return <p className="text-sm text-slate-400 leading-relaxed mb-3">{children}</p>;
}

function List({ items }: { items: string[] }) {
  return (
    <ul className="text-sm text-slate-400 leading-relaxed space-y-1.5 list-none">
      {items.map((item) => (
        <li key={item} className="flex gap-2">
          <span className="text-indigo-300 shrink-0">•</span>
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

function Code({ children }: { children: ReactNode }) {
  return (
    <code className="rounded bg-black/50 border border-white/10 px-1.5 py-0.5 text-[13px] text-indigo-200 font-mono whitespace-nowrap">
      {children}
    </code>
  );
}

function OverviewTab() {
  return (
    <div className="space-y-6">
      <Card testid="help-arch">
        <H2>Architecture</H2>
        <P>
          Advanced Memory is a local-first notes backend. Your notes live as plain Markdown files on
          disk, get indexed into SQLite (FTS keyword index) plus an optional LanceDB vector index,
          and are served to this web UI and to AI assistants over MCP.
        </P>
        <div className="grid gap-3 md:grid-cols-3 text-sm">
          <div className="rounded-xl border border-white/10 bg-black/30 p-4">
            <div className="font-medium text-white mb-1">Web UI — :10704</div>
            <p className="text-slate-500">
              This Vite app. Notes, sync, skills, chat, logs, settings. Same-origin{" "}
              <Code>/api/v1</Code> proxy to the backend.
            </p>
          </div>
          <div className="rounded-xl border border-white/10 bg-black/30 p-4">
            <div className="font-medium text-white mb-1">HTTP API — :10705</div>
            <p className="text-slate-500">
              FastAPI/uvicorn. Everything the UI shows comes from here. NSSM service{" "}
              <Code>advanced-memory-mcp</Code>.
            </p>
          </div>
          <div className="rounded-xl border border-white/10 bg-black/30 p-4">
            <div className="font-medium text-white mb-1">MCP daemon — :10732</div>
            <p className="text-slate-500">
              Owns the database for AI clients (Claude Desktop, Cursor). NSSM service{" "}
              <Code>advanced-memory-mcp-daemon</Code>. Never run a second copy.
            </p>
          </div>
        </div>
      </Card>
      <Card testid="help-pages">
        <H2>Pages in this app</H2>
        <List
          items={[
            "Dashboard — vault KPIs, recent activity, quick actions.",
            "Notes — browse, search and read the vault (default list is recent activity).",
            "Vault Sync — projects, file watcher, vault scan, search reindex, RAG roots.",
            "Skills — local skill library plus marketplace.",
            "Research — web / academic / GitHub assisted research.",
            "Chat — assistant chat with personalities and local models.",
            "Tools — live MCP tool surface of the backend.",
            "System log — recent backend log lines.",
            "Settings — LLM providers, research and export preferences.",
          ]}
        />
      </Card>
    </div>
  );
}

function WrappeeTab() {
  return (
    <div className="space-y-6">
      <Card testid="help-wrappee-owners">
        <H2>Who owns your data</H2>
        <P>
          This server is not a wrapper around a third-party app — the backend and its stores{" "}
          <em>are</em> the wrappee. Two processes share one SQLite database and one LanceDB index,
          so they must never run twice:
        </P>
        <List
          items={[
            "advanced-memory-mcp (API, :10705) — serves this UI; owns file sync and the search index.",
            "advanced-memory-mcp-daemon (MCP, :10732) — serves AI clients; owns the DB connection for MCP traffic.",
            "Markdown on disk is the source of truth; SQLite + indexes are derived and rebuildable.",
          ]}
        />
      </Card>
      <Card testid="help-wrappee-verify">
        <H2>How to verify it is healthy</H2>
        <List
          items={[
            "Topbar health dot: green means GET /api/v1/health answered.",
            "Vault Sync page: watcher running, sync status idle, project totals matching the Dashboard.",
            "Daemon: http://127.0.0.1:10732/health shows version, git_sha and uptime.",
            "After any code change restart the matching service (elevated) and confirm a NEW pid owns the port.",
          ]}
        />
      </Card>
      <Card testid="help-wrappee-unreachable">
        <H2>When it is unreachable</H2>
        <List
          items={[
            "Red panel on Notes: backend restarting, or a stale tab (see Error fix). Hard-refresh first.",
            "Both NSSM services must run pinned with USERPROFILE=C:\\Users\\sandr — unpinned, the service runs as LocalSystem and serves a phantom vault that looks empty.",
            "Never start a second uvicorn or a second daemon by hand while the services run; check Get-Service first.",
          ]}
        />
      </Card>
    </div>
  );
}

function VaultTab() {
  return (
    <div className="space-y-6">
      <Card testid="help-vault-storage">
        <H2>Where notes live</H2>
        <P>
          One folder per project on disk. The <Code>main</Code> vault defaults to{" "}
          <Code>C:\Users\sandr\.advanced-memory\vault</Code>. The index database is{" "}
          <Code>C:\Users\sandr\.advanced-memory\memory.db</Code>. Safe-deleted files go to the trash
          at <Code>C:\Users\sandr\.advanced-memory-mcp\trash</Code>.
        </P>
        <List
          items={[
            "Markdown on disk is the source of truth; the DB/index is derived.",
            "Switch projects from the dropdown on Notes or from Vault Sync.",
            "Switching the default project is a server call (PUT /projects/{name}/default) — it sticks across reloads.",
          ]}
        />
      </Card>
      <Card testid="help-vault-sync">
        <H2>Sync, watch and reindex</H2>
        <List
          items={[
            "File watcher (Vault Sync page) follows disk changes into the DB. If it is off, new files stay invisible until a scan.",
            "Vault scan walks the folders and imports new/changed Markdown (slow on large vaults, up to ~20 min).",
            "Search reindex rebuilds the FTS + vector index. Needed after index rot (see Error fix).",
            "Sync progress is polled on the Vault Sync page; do not restart the backend mid-scan.",
          ]}
        />
      </Card>
    </div>
  );
}

function SearchTab() {
  return (
    <div className="space-y-6">
      <Card testid="help-search-modes">
        <H2>Three ways to find things</H2>
        <List
          items={[
            "Keyword search — FTS over titles and content. Fast, exact, typo-intolerant.",
            "Semantic search — vector similarity over chunks. Finds meaning, needs embeddings.",
            "Recent activity (the Notes default list) — entities created/edited inside a time window. It reads the search index, not the entity table.",
          ]}
        />
      </Card>
      <Card testid="help-search-gotchas">
        <H2>Gotchas that look like bugs</H2>
        <List
          items={[
            "Typing in the Notes search box uses keyword search and can return thousands of hits while the default recent list shows a handful — that is expected, the windows differ.",
            "Recent activity with a 90-day window hides everything older. Old but valid notes are not lost; search for them.",
            "If recent counts disagree with the Dashboard entity totals, the index is stale — run a reindex from Vault Sync.",
          ]}
        />
      </Card>
      <Card testid="help-research">
        <H2>Research sources</H2>
        <P>
          The Research page combines vault search with optional external providers (web search,
          arXiv, GitHub, document ingestion) depending on server configuration. Results can be saved
          back into the vault as notes.
        </P>
      </Card>
    </div>
  );
}

function SkillsTab() {
  return (
    <div className="space-y-6">
      <Card testid="help-skills-what">
        <H2>What skills are</H2>
        <P>
          Skills are Markdown instruction packs (Anthropic-style <Code>SKILL.md</Code>) an assistant
          loads for a task. Good skills state scope, steps and guardrails — checklists, decision
          trees, review rubrics you repeat.
        </P>
        <List
          items={[
            "Browse local skills and the marketplace on the Skills page.",
            "Generate a skill from curated notes, or write SKILL.md by hand.",
            "Point the client at the skill file when the task comes up again.",
          ]}
        />
      </Card>
    </div>
  );
}

function ApiTab() {
  const ports = [
    { port: "10704", owner: "Vite dev (this UI)", notes: "Same-origin /api/v1 proxy to :10705" },
    { port: "10705", owner: "FastAPI backend", notes: "NSSM: advanced-memory-mcp" },
    {
      port: "10732",
      owner: "MCP daemon",
      notes: "NSSM: advanced-memory-mcp-daemon. /mcp + /health",
    },
  ];
  const env = [
    {
      name: "VITE_API_URL",
      effect:
        "Overrides the API base. Unset = same-origin proxy (correct for local). A stale value (e.g. :8001) breaks every page — hard-refresh (Ctrl+Shift+R).",
    },
    {
      name: "ADVANCED_MEMORY_HTTP_PROXY",
      effect: "Stdio MCP clients probe this for the daemon (default http://127.0.0.1:10732/mcp).",
    },
    {
      name: "USERPROFILE / ADVANCED_MEMORY_HOME",
      effect:
        "Pinned on both NSSM services. Without the pin the service runs as LocalSystem and serves a phantom vault.",
    },
  ];
  const endpoints = [
    "GET /api/v1/health — liveness probe used by every page",
    "GET /api/v1/projects — project list",
    "PUT /api/v1/projects/{name}/default — switch default project",
    "GET /api/v1/{project}/project/info — entity/observation/relation stats",
    "GET /api/v1/{project}/memory/recent?timeframe=90d&depth=2 — recent activity feed",
    "POST /api/v1/{project}/search/ — keyword search ({permalink_match: *} lists all)",
    "GET /api/v1/management/watch/status — file watcher state",
    "GET /api/v1/management/sync/status — scan/reindex progress",
    "POST /api/v1/{project}/search/reindex — rebuild the search index (slow)",
  ];
  return (
    <div className="space-y-6">
      <Card testid="help-ports">
        <H2>Ports</H2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 border-b border-white/10">
                <th className="py-2 pr-4 font-medium">Port</th>
                <th className="py-2 pr-4 font-medium">Owner</th>
                <th className="py-2 font-medium">Notes</th>
              </tr>
            </thead>
            <tbody>
              {ports.map((r) => (
                <tr key={r.port} className="border-b border-white/5 text-slate-400">
                  <td className="py-2 pr-4 font-mono text-indigo-200">{r.port}</td>
                  <td className="py-2 pr-4">{r.owner}</td>
                  <td className="py-2">{r.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <P>
          Port 8001 is a dead legacy backend port — it only appears if your browser tab predates the
          current frontend (see Error fix). Nothing should listen there.
        </P>
      </Card>
      <Card testid="help-env">
        <H2>Environment</H2>
        <div className="space-y-3">
          {env.map((e) => (
            <div key={e.name} className="rounded-xl border border-white/10 bg-black/30 p-4 text-sm">
              <div className="font-mono text-indigo-200 mb-1">{e.name}</div>
              <div className="text-slate-400">{e.effect}</div>
            </div>
          ))}
        </div>
      </Card>
      <Card testid="help-endpoints">
        <H2>Key endpoints</H2>
        <ul className="space-y-1.5">
          {endpoints.map((e) => (
            <li key={e} className="font-mono text-[13px] text-slate-400">
              {e}
            </li>
          ))}
        </ul>
      </Card>
      <Card testid="help-start">
        <H2>Starting and restarting</H2>
        <List
          items={[
            "Webapp: from the webapp folder run .\\start.ps1 (uvicorn :10705 + Vite :10704).",
            "Backend code changes need a service restart: elevated Restart-Service advanced-memory-mcp -Force, then confirm a NEW pid owns :10705.",
            "Daemon code changes: elevated Restart-Service advanced-memory-mcp-daemon -Force, then check :10732/health shows the new git_sha.",
            "Never restart by killing the child process — NSSM owns the lifecycle.",
          ]}
        />
      </Card>
    </div>
  );
}

type FixRow = { symptom: string; cause: string; fix: string };

const FIXES: FixRow[] = [
  {
    symptom: 'Red panel: "Cannot reach the vault API"',
    cause: "Backend was restarting (service restart = ~6 s gap), or the tab is stale.",
    fix: "Hard-refresh with Ctrl+Shift+R. The panel heals on the next poll; refresh is instant. If it persists, open /api/v1/health in the same browser.",
  },
  {
    symptom: "Pages try http://localhost:8001/...",
    cause:
      "Stale tab from before the fleet-port migration. VITE_API_URL=:8001 is baked into the loaded bundle; nothing listens on 8001.",
    fix: "Ctrl+Shift+R (or close the tab and reopen). Do not set VITE_API_URL for local use.",
  },
  {
    symptom: "Notes shows 2 notes (or none) but Dashboard counts thousands",
    cause:
      "The default list is recent activity over the search index (90 d window), not the entity table. Stale index dates hide everything.",
    fix: "Type in the search box (keyword path, no date filter) to confirm notes exist, then run Search reindex from Vault Sync.",
  },
  {
    symptom: "Project dropdown empty / cannot select project",
    cause: "Same fetch path as the red panel: /projects never loaded in this tab.",
    fix: "Hard-refresh. If the API answers (check /api/v1/projects directly) but the UI stays empty, it is the stale tab again.",
  },
  {
    symptom: "PermissionError WinError 32 on file_operations.log",
    cause:
      "Fixed 2026-09-23: API and daemon shared one rotating loguru file. Rotation rename collides on Windows.",
    fix: "Already fixed — sinks are per-PID (file_operations_<pid>.log). If you see it again, both services are not on the fixed build; restart them.",
  },
  {
    symptom: "Vault shows a handful of notes after running fine (e.g. 4 of ~3000)",
    cause:
      "Index rot: FTS docs far below entity count, and recents reads the index. Past triggers: stale Docker squat on :10704, NSSM running as LocalSystem with a phantom vault.",
    fix: "Full search reindex from Vault Sync and wait for 100%. Verify services run pinned (USERPROFILE=C:\\Users\\sandr) and no container squats on fleet ports.",
  },
  {
    symptom: "Search finds nothing / totals disagree with Dashboard",
    cause: "Stale or partially built search index (interrupted scan, crashed reindex).",
    fix: "Vault Sync → reindex, wait for idle, compare Dashboard totals with a permalink_match * search.",
  },
];

function TroubleshootTab({ query }: { query: string }) {
  const q = query.trim().toLowerCase();
  const rows = useMemo(() => {
    if (!q) return FIXES;
    return FIXES.filter((f) => `${f.symptom} ${f.cause} ${f.fix}`.toLowerCase().includes(q));
  }, [q]);
  return (
    <div className="space-y-4" data-testid="help-fixes">
      {rows.length === 0 && (
        <Card>
          <P>No fixes match “{query}”. Try fewer words, or ask on the repository issues page.</P>
        </Card>
      )}
      {rows.map((f) => (
        <Card key={f.symptom} testid="help-fix-card">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-yellow-300 shrink-0 mt-0.5" />
            <div className="min-w-0">
              <h3 className="font-medium text-white mb-1">{f.symptom}</h3>
              <p className="text-sm text-slate-400 mb-1.5">
                <span className="text-slate-500">Cause: </span>
                {f.cause}
              </p>
              <p className="text-sm text-slate-300">
                <span className="text-green-300/80">Fix: </span>
                {f.fix}
              </p>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}

const FAQS: Array<{ q: string; a: string }> = [
  {
    q: "Where are my notes stored?",
    a: "As Markdown files under your project folder (main defaults to C:\\Users\\sandr\\.advanced-memory\\vault). The SQLite DB and indexes are derived from those files — disk is the source of truth.",
  },
  {
    q: "How do I add another project?",
    a: "Vault Sync → create project with a name and an absolute folder path. Switching the default is a server call and persists across reloads.",
  },
  {
    q: "Why does Notes show fewer items than the Dashboard totals?",
    a: "Notes defaults to recent activity (time-windowed, index-backed). Dashboard totals count all entities. Use the search box or widen the window for the full set.",
  },
  {
    q: "How do I rebuild search?",
    a: "Vault Sync → search reindex. It can take many minutes on large vaults; do not restart the backend until sync status is idle.",
  },
  {
    q: "How do AI assistants connect?",
    a: "Over MCP via the daemon on :10732 (streamable-http /mcp), or stdio clients that proxy to it. The HTTP API on :10705 is for this web UI.",
  },
  {
    q: "Backend is up but the UI says offline?",
    a: "Your tab is stale (pre-restart bundle, possibly with a fossil VITE_API_URL). Ctrl+Shift+R. Same-origin /api/v1 proxy needs no env var locally.",
  },
  {
    q: "Which service do I restart after a code change?",
    a: "Backend change → advanced-memory-mcp. MCP/daemon change → advanced-memory-mcp-daemon. Both need an elevated shell; verify a new pid owns the port afterwards.",
  },
  {
    q: "Where are the logs?",
    a: "System log page in this UI, plus logs/ in the repo (service-stdout/stderr with rotation), per-PID file-operation logs in the trash dir, and daemon-service logs.",
  },
];

function FaqTab({ query }: { query: string }) {
  const q = query.trim().toLowerCase();
  const items = useMemo(() => {
    if (!q) return FAQS;
    return FAQS.filter((f) => `${f.q} ${f.a}`.toLowerCase().includes(q));
  }, [q]);
  return (
    <div className="space-y-3" data-testid="help-faq">
      {items.length === 0 && (
        <Card>
          <P>No FAQ matches “{query}”.</P>
        </Card>
      )}
      {items.map((f) => (
        <details
          key={f.q}
          data-testid="faq-item"
          className="group rounded-2xl border border-white/10 bg-white/[0.03] px-5 py-4"
        >
          <summary className="cursor-pointer list-none flex items-center gap-3 text-sm font-medium text-white">
            <FileQuestion className="h-4 w-4 text-indigo-300 shrink-0" />
            <span className="flex-1">{f.q}</span>
            <span className="text-slate-500 group-open:rotate-90 transition-transform">›</span>
          </summary>
          <p className="mt-2.5 text-sm text-slate-400 leading-relaxed pl-7">{f.a}</p>
        </details>
      ))}
    </div>
  );
}

const TAB_ICONS: Record<HelpTab, typeof Book> = {
  overview: Book,
  wrappee: Database,
  vault: Layers,
  search: Search,
  skills: Zap,
  api: Network,
  troubleshoot: Wrench,
  faq: HelpCircle,
};

export default function Help() {
  const [activeTab, setActiveTab] = useState<HelpTab>("overview");
  const [query, setQuery] = useState("");
  const showSearch = activeTab === "troubleshoot" || activeTab === "faq";

  return (
    <div className="h-full min-h-0 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10">
      <div className="max-w-5xl mx-auto px-6 py-8 pb-16">
        <header className="space-y-3 border-b border-white/10 pb-6">
          <h1 className="text-3xl font-bold tracking-tight text-white">Help</h1>
          <p className="text-lg text-slate-400 max-w-3xl">
            Architecture, vault handling, API/ports, error fixes and FAQ for the Advanced Memory
            webapp and backend.
          </p>
          {showSearch && (
            <div className="pt-2">
              <input
                data-testid="help-search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={
                  activeTab === "faq" ? "Filter questions…" : "Filter by symptom or error…"
                }
                className="w-full max-w-md rounded-xl border border-white/10 bg-black/30 px-4 py-2.5 text-sm text-white placeholder:text-slate-600 outline-none focus:border-indigo-400/50"
              />
            </div>
          )}
        </header>

        <div className="border-b border-white/10 overflow-x-auto" data-testid="help-tabs">
          <nav className="flex space-x-6 min-w-max">
            {TABS.map((tab) => {
              const Icon = TAB_ICONS[tab.id];
              const active = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  type="button"
                  data-testid={`help-tab-${tab.id}`}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors flex items-center gap-2 ${
                    active
                      ? "border-indigo-400 text-white"
                      : "border-transparent text-slate-500 hover:text-slate-200 hover:border-white/20"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span className="text-left">
                    <span className="block">{tab.name}</span>
                    <span className="block text-xs opacity-70 mt-0.5 font-normal">
                      {tab.description}
                    </span>
                  </span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="py-6">
          {activeTab === "overview" && <OverviewTab />}
          {activeTab === "wrappee" && <WrappeeTab />}
          {activeTab === "vault" && <VaultTab />}
          {activeTab === "search" && <SearchTab />}
          {activeTab === "skills" && <SkillsTab />}
          {activeTab === "api" && <ApiTab />}
          {activeTab === "troubleshoot" && <TroubleshootTab query={query} />}
          {activeTab === "faq" && <FaqTab query={query} />}
        </div>

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
            <li>
              <Link
                to="/logs"
                className="flex items-center justify-between gap-4 rounded-xl border border-white/10 p-4 hover:bg-white/[0.05]"
              >
                <div>
                  <div className="font-medium text-white">System log</div>
                  <div className="text-sm text-slate-500">Recent backend lines for debugging</div>
                </div>
                <ExternalLink className="h-4 w-4 text-slate-500 shrink-0" />
              </Link>
            </li>
          </ul>
        </section>
      </div>
    </div>
  );
}
