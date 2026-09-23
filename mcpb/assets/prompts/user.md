# Advanced Memory MCP — User Guide

## Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sandraschi/advanced-memory-mcp.git
   cd advanced-memory-mcp
   ```

2. **Install dependencies with uv:**
   ```bash
   uv sync
   ```

3. **Configure environment variables:**
   ```env
   AM_VAULT_PATH=C:\path\to\obsidian\vault
   AM_PROJECTS_DIR=C:\path\to\projects
   AM_LOG_LEVEL=INFO
   AM_MCP_TRANSPORT=stdio
   ```

4. **Run the MCP server:**
   ```bash
   uv run run_server.py
   ```

5. **Add to Claude Desktop:**
   ```json
   {
     "mcpServers": {
       "advanced-memory-mcp": {
         "command": "uv",
         "args": ["run", "--directory", "C:\\path\\to\\advanced-memory-mcp", "run_server.py"]
       }
     }
   }
   ```

### First Steps

1. Start with `adn_system(operation="status")` to check server health and configuration.
2. Create a note with `adn_notes(operation="write", title="My First Note", content="# Hello World", folder="inbox")`.
3. Search with `adn_search(operation="text", query="hello")`.
4. Use AI summarization with `adn_knowledge(operation="summarize", identifier="My First Note")`.

## Tutorials

### Tutorial 1: Write, Read, and Edit Notes

Full note lifecycle management.

```python
# Write
adn_notes(operation="write", title="Transformers", content="# Attention Is All You Need\n\nKey insights...", folder="research", tags="ai, transformers")

# Read
note = adn_notes(operation="read", identifier="Transformers")

# Edit a section
adn_notes(operation="edit", identifier="Transformers", mode="replace_section", section="Key Insights", content="## Key Insights\n- Self-attention\n- Parallel processing\n- Multi-head attention")
```

### Tutorial 2: Daily Notes

Maintain a daily journal with chronological entries.

```python
adn_notes(operation="daily", content="- Reviewed the portmanteau refactoring\n- Updated RAG chunk size to 512")
```

### Tutorial 3: AI Content Enrichment

Enhance notes with AI-powered improvements.

```python
# Summarize
adn_knowledge(operation="summarize", identifier="Transformers")

# Suggest tags
adn_knowledge(operation="suggest_tags", identifier="Transformers")

# Full enhancement
adn_knowledge(operation="enhance", identifier="Transformers", update_style=True, add_context=True)
```

### Tutorial 4: Quality Control

Find and fix low-quality notes.

```python
# Find runts
adn_knowledge(operation="qc", mode="find_runts", max_length=200, folder="research")

# Find junk
adn_knowledge(operation="qc", mode="find_junk", folder="inbox")
```

### Tutorial 5: Multi-Source Research

Orchestrate research across arXiv, GitHub, and web.

```python
# arXiv
adn_arxiv_research(operation="relevance", query="transformer attention", max_results=10)

# GitHub
adn_github_research(operation="stars", query="fastmcp mcp-server", max_results=10)

# Web search
adn_web_search(operation="auto", query="FastMCP 3.2 release notes")
```

### Tutorial 6: Create and Activate Skills

Use the staged skill loading pattern.

```python
# Create
adn_skills(operation="create", skill_name="Python Expert", description="Deep Python knowledge", category="developer", difficulty="advanced")

# Activate (loads table of contents only)
adn_skills(operation="activate", identifier="Python Expert", scope="session")

# Load specific section on demand
adn_skills(operation="load_section", identifier="Python Expert", section="Decorators")

# Deactivate when done
adn_skills(operation="deactivate", identifier="Python Expert")
```

### Tutorial 7: Generate Diagrams

Create visual documentation.

```python
# Flowchart
generate_mermaid_diagram(operation="flowchart", title="Process Flow")

# Sequence diagram
generate_mermaid_diagram(operation="sequence", title="API Flow")

# Mind map
generate_mermaid_diagram(operation="mindmap", title="Project Structure")
```

### Tutorial 8: External MCP Bridge

Call tools on other MCP servers.

```python
adn_system(operation="external_bridge", server="arxiv-mcp", tool="search_papers", args={"query": "transformer", "limit": 5})
```

### Tutorial 9: RAG Search

Search using different strategies.

```python
adn_rag_fixed(query="What is attention?")
adn_rag_semantic(query="How do transformers process sequences?")
adn_rag_sentence(query="self-attention mechanism")
```

### Tutorial 10: Audio Voice Commands

Use the voice pipeline for hands-free operation.

```python
wake_start()
wake_status()
dictated = dictate(duration=30)
adn_notes(operation="write", title="Dictated Note", content=dictated.get('text', ''), folder="inbox")
speak(text="Note captured successfully.")
wake_stop()
```

### Tutorial 11: Zettelkästen Workflow

Create interconnected atomic notes.

```python
zettel = adn_zettelmaker_generate(topic="Attention mechanisms")
adn_zettelmaker_connect(identifier=zettel['identifier'])
adn_zettelmaker_expand(identifier=zettel['identifier'])
```

### Tutorial 12: Import from External Sources

Ingest content from various platforms.

```python
ingest_obsidian(vault_path="C:\\path\\to\\vault")
ingest_archive(path="C:\\path\\to\\export.zip")
build_context(identifiers=["Note A", "Note B"])
```

### Tutorial 13: Knowledge Graph Visualization

Explore entity relationships.

```python
adn_visualize(operation="point_cloud", identifier="transformer")
adn_visualize(operation="hub_and_spoke", identifier="AI")
adn_visualize(operation="temporal", identifier="project-evolution")
```

### Tutorial 14: Batch Operations

Process multiple notes at once.

```python
# Bulk summarize
adn_knowledge_bulk(operation="summarize", identifiers=["Note A", "Note B", "Note C"])

# Batch import
import_batch(files=["paper1.pdf", "paper2.pdf", "notes.md"])
```

### Tutorial 15: Automation Workflow

Execute autonomous multi-step workflows.

```python
adn_system(operation="workflow", goal="Summarize all notes on Neural Networks and create a skill")
```

### Tutorial 16: Navigate the Graph (backlinks and context)

Find everything that references a note, then build a context map around it.

```python
# Who links to this note?
adn_nav(operation="backlinks", identifier="Transformers")

# 2-hop context map for grounding answers
ctx = adn_nav(operation="build_context", url="memory://main/transformers", depth=2, max_related=10)

# Chronological feed of the last week
adn_nav(operation="recent", timeframe="7d", page_size=20)
```

### Tutorial 17: Multi-Project Work

Keep research, work, and personal vaults separate and switch between them.

```python
adn_project(operation="ls")
adn_project(operation="create", name="phd", path="D:/vaults/phd", set_default=False)
adn_project(operation="switch", name="phd")

# One-off cross-project read without switching
adn_notes(operation="read", identifier="Transformers", project="main")

# Back to default
adn_project(operation="switch", name="main")
adn_project(operation="status", name="phd")
```

### Tutorial 18: Zettel Full Lifecycle

From seed idea to connected knowledge cluster.

```python
# 1. Generate an atomic note
z = adn_zettel(operation="generate", topic="Sparse attention", category="research", quality="standard")

# 2. Find gaps it could fill, and topics to write next
adn_zettel(operation="analyze", category="research")
adn_zettel(operation="suggest", category="research", count=5)

# 3. Grow it horizontally and link it up
adn_zettel(operation="expand", note_identifier="Sparse attention", depth=2)
adn_zettel(operation="connect", note_identifier="Sparse attention")
```

### Tutorial 19: Inbox Pipeline (documents to notes)

Turn a pile of PDFs and exports into vault notes.

```python
adn_inbox(operation="status")                       # what is waiting?
adn_inbox(operation="info")                         # is Pandoc healthy?
adn_inbox(operation="process")                      # convert + ingest everything
adn_inbox(operation="process", file_name="paper.pdf")  # or one file
adn_inbox(operation="watch")                        # keep watching the inbox
```

### Tutorial 20: Typora Co-Editing

Drive the visual editor without leaving the conversation.

```python
adn_typora(operation="open", file_path="D:/vault/research/Transformers.md")
adn_typora(operation="cursor")                      # where is the user?
adn_typora(operation="insert", text="## AI Summary\n- Self-attention wins", position="current cursor")
adn_typora(operation="analyze")                     # headings/links health
adn_typora(operation="save")
adn_typora(operation="export", format="pdf", path="D:/exports/transformers.pdf")
```

### Tutorial 21: LLM Lifecycle (local-first)

Manage models for enrichment jobs.

```python
adn_llm(operation="list_providers")
adn_llm(operation="list_models", provider="ollama")
adn_llm(operation="select_model", provider="ollama", model="llama3:8b")
adn_llm(operation="load_model", provider="ollama", model="llama3:8b")   # pre-warm before bulk jobs
adn_knowledge(operation="bulk", bulk_operation="bulk_update", filters={"topics": ["draft"]}, limit=50)
adn_llm(operation="unload_model", provider="ollama", model="llama3:8b")
adn_llm(operation="status")
```

### Tutorial 22: Batch Tag Maintenance

Clean up a messy tag space safely.

```python
adn_knowledge(operation="bulk", bulk_operation="tag_analytics", limit=200)
adn_knowledge(operation="bulk", bulk_operation="consolidate_tags", dry_run=True)
adn_knowledge(operation="bulk", bulk_operation="consolidate_tags", dry_run=False)
adn_knowledge(operation="bulk", bulk_operation="find_duplicates", limit=100)
```

### Tutorial 23: Gap Analysis and Clustering

Find what the vault is missing and how it groups.

```python
adn_knowledge(operation="analyze", analysis_type="find_gaps", filters={"topics": ["mlops"]}, limit=20)
adn_knowledge(operation="analyze", analysis_type="cluster_content", limit=50)
adn_knowledge(operation="analyze", analysis_type="suggest_relationships", filters={"note_id": "Transformers"})
adn_knowledge(operation="analyze", analysis_type="extract_insights", filters={"topics": ["attention"]}, limit=30)
```

### Tutorial 24: Canvas Knowledge Maps

Visualize a cluster for Obsidian.

```python
adn_knowledge(operation="canvas", title="Attention cluster", folder="maps",
              nodes=[{"id": "t", "type": "text", "text": "Attention mechanisms"},
                     {"id": "n1", "type": "file", "file": "Transformers.md"}],
              edges=[{"from": "t", "to": "n1", "label": "explains"}])
```

### Tutorial 25: Export Anywhere

Ship notes to the format the audience needs.

```python
export_docsify()
export_html_notes()
export_pdf_native()
export_pandoc()
export_to_archive()
export_evernote_compatible()
```

### Tutorial 26: Sync and Watch Status

Know whether the vault on disk matches the index.

```python
adn_system(operation="sync")
adn_nav(operation="sync")
sync_project()
get_file_sync_status()
adn_nav(operation="status")
```

### Tutorial 27: End-to-End Research Brief

One orchestrated call from question to grounded brief.

```python
adn_research(operation="research_orchestrate", query="Sparse attention for long-context LLMs",
             provider="ollama", model="llama3:8b")
```

Prefer this over manual fan-out when the deliverable is a summary, not raw hits.
Use single-source ops (Tutorial 5) when building datasets or comparing corpora.

### Tutorial 28: Distill a Skill from ArXiv

Turn papers into a reusable skill pack.

```python
adn_skills(operation="distill_from_arxiv", topic="Sparse attention",
           query="sparse attention long context", max_papers=5, category="research")
adn_skills(operation="list", category="research")
adn_skills(operation="activate", identifier="sparse-attention", scope="session")
```

Variants: `distill_from_wikipedia` (topic overviews), `distill_from_expert`
(`expert_name` + `focus_area`), `distill_from_textbook` (`pdf_path` + `chapters`),
`distill_from_text` (`text_path`), `import_from_github` (`repository`, `branch`).

### Tutorial 29: Automation Batch (tag everything new)

Apply one instruction across many notes.

```python
adn_automation(operation="batch",
               items=["Note A", "Note B", "Note C"],
               goal="Extract key dates and append them under a ## Timeline section.")
adn_automation(operation="status")
```

### Tutorial 30: Timers, Alarms, and Dictation Loop

A hands-free research session.

```python
adn_audio(operation="timer", duration="25 minutes")     # pomodoro
adn_audio(operation="dictate", record_duration=60, tags="session")
adn_audio(operation="weather", location="Vienna")
adn_audio(operation="music", command="play", query="Bach")
```

## Troubleshooting

### "Note not found"

Use `adn_search(operation="text", query="partial name")` to find the correct identifier.

### "RAG returns no results"

Run `reindex()` to rebuild the search index. Verify vault path is correct.

### "External API rate limited"

Increase delay configuration or reduce request frequency.

### "Vault looks empty but files exist on disk"

The server is running under an account whose home directory is not your vault
(e.g. a Windows service as LocalSystem without pinned USERPROFILE). Check project
status for the actual vault path, pin `USERPROFILE`/`ADVANCED_MEMORY_HOME`, restart.

### "Recent activity shows far fewer notes than the vault holds"

Recent feeds read the search index with a time window; stale index dates hide
everything older. Search without a date filter to confirm the notes exist, then run
a full reindex and wait for idle.

### "Batch edit touched the wrong notes"

Re-run with `dry_run=True` first and inspect the plan. Narrow `filters`
(topics/folders) before any destructive `bulk_operation` (`bulk_delete`,
`bulk_move`, `bulk_update`, `consolidate_tags`).

### "Skill activation floods context"

You read the whole skill. Use The Door: `activate` (TOC), then `load_section`
for exactly one section, then `deactivate`. Never paste SKILL.md into context.

### "Two processes fight over one database"

Run exactly one HTTP daemon per database. Stdio clients auto-proxy to it via
`ADVANCED_MEMORY_HTTP_PROXY`. Check for a second daemon before starting another.

### "Ollama model is slow or OOMs"

`adn_llm(operation="status")` shows what is loaded. Unload idle models, pick a
smaller quant, or move the quality pass to a hosted provider while keeping bulk
enrichment local.

### "Exported file has broken links"

Export from the vault root so relative links resolve, and prefer
`export_docsify`/`export_html_notes` (link-aware) over raw Pandoc for linked vaults.

## FAQ

**Q: What's a portmanteau tool?** A single function with an `operation` enum parameter grouping related operations to prevent tool explosion.

**Q: Can I use this with Obsidian?** Yes. Set `AM_VAULT_PATH` to your vault directory.

**Q: What is "The Door" pattern for skills?** Skills load in stages: activation loads the table of contents only, then sections are loaded on demand to prevent context flooding.

**Q: Can this call other MCP servers?** Yes — use `adn_system(operation="external_bridge")`.

**Q: Where do my notes actually live?** As Markdown files under your project folder. The database and indexes are derived; disk is the source of truth, so reinstalls never eat notes.

**Q: How do I work with several vaults?** `adn_project(operation="create")` per vault, `switch` between them, or pass `project=` per call for one-offs.

**Q: Keyword or semantic search — which?** Keyword (`query`) for exact terms, filenames, tags. Semantic (`rag`) for meaning ("notes about forgetting"). Use both when recall matters.

**Q: How do I fix a stale index?** `adn_system(operation="reindex", focus="all")` (or `adn_search(operation="reindex", mode="full")`), then verify totals before trusting counts.

**Q: What does `dry_run` do?** Prints the bulk plan without executing. Always dry-run destructive bulk ops first.

**Q: Which provider should enrichment use?** Local (Ollama) for bulk passes, hosted (OpenAI) for quality passes. Manage with `adn_llm`.

**Q: Can assistants reach my other MCP servers through this one?** Yes via `external_bridge` (`server`, `tool`, `args`).

**Q: How do I capture voice notes?** `dictate` (file or live), optionally behind `wake_start`/`wake_stop` for hands-free capture.

**Q: How do I turn papers into a skill?** `distill_from_arxiv` (or wikipedia/expert/textbook/text), then `activate` + `load_section` per The Door.

**Q: What if two daemons start?** Stop one. A second daemon against the same database causes lock contention and log rotation collisions.

**Q: How do I back up?** Back up the vault folder (source of truth). The database can always be rebuilt from disk via reindex.

## More Tutorials (31-40)

### Tutorial 31: Checkpoints Before Danger

Snapshot first, bulk second.

```python
# snapshot, then consolidate tags, then verify
adn_knowledge(operation="bulk", bulk_operation="tag_analytics", limit=200)
# ... snapshot via the checkpoints surface ...
adn_knowledge(operation="bulk", bulk_operation="consolidate_tags", dry_run=False)
adn_knowledge(operation="bulk", bulk_operation="project_stats")
```

### Tutorial 32: Skill Update and Retire

Keep the library fresh.

```python
adn_skills(operation="list")
adn_skills(operation="read", identifier="sparse-attention")
adn_skills(operation="update", identifier="sparse-attention",
           content="# Sparse Attention (v2)\n\nUpdated with 2026 results...")
adn_skills(operation="deactivate", identifier="sparse-attention", all=True)
```

### Tutorial 33: Canvas from Backlinks

Map what points at a hub note, then draw it.

```python
links = adn_nav(operation="backlinks", identifier="Transformers")
adn_knowledge(operation="canvas", title="Transformers backlinks", folder="maps",
              nodes=[{"id": "hub", "type": "text", "text": "Transformers"}] +
                    [{"id": b["permalink"], "type": "file", "file": b["permalink"]}
                     for b in links["notes"][:12]],
              edges=[{"from": "hub", "to": b["permalink"], "label": "cited by"}
                     for b in links["notes"][:12]])
```

### Tutorial 34: Search External Vaults

Query an Obsidian export without importing it.

```python
adn_search(operation="external", source="obsidian",
           path="D:/exports/old-vault", query="attention")
```

### Tutorial 35: Morning Briefing Combo

Weather, timer, and dictation in one flow.

```python
adn_audio(operation="weather", location="Vienna")
adn_audio(operation="timer", duration="25 minutes")
adn_audio(operation="dictate", record_duration=120, tags="morning-brief")
adn_notes(operation="daily", content="- Morning brief captured, see dictated note")
```

### Tutorial 36: Project Detect and Retire

Let the server pick, then clean up dead projects.

```python
adn_project(operation="detect")
adn_project(operation="status")
adn_project(operation="rm", name="old-experiment")
adn_project(operation="ls")
```

### Tutorial 37: LLM Health Triage

Find out why generation is slow.

```python
adn_llm(operation="health")
adn_llm(operation="status")
adn_system(operation="status", level="detailed", focus="memory")
```

### Tutorial 38: Inbox Watch Mode

Leave the pipeline running and check what arrived.

```python
adn_inbox(operation="watch")
# ... later ...
adn_inbox(operation="status")
adn_inbox(operation="process")
adn_search(operation="query", search_type="tag", text="inbox")
```

### Tutorial 39: Typora Export Pipeline

Edit visually, publish as PDF.

```python
adn_typora(operation="open", file_path="D:/vault/research/Transformers.md")
adn_typora(operation="get_content")
adn_typora(operation="insert", text="\n> Reviewed 2026-09-23 — still current.", position="current cursor")
adn_typora(operation="save")
adn_typora(operation="export", format="pdf", path="D:/exports/transformers.pdf")
```

### Tutorial 40: TV Tropes Deep Dive

Narrative research across media.

```python
adn_research(operation="tvtropes", query="time loop", category="film")
adn_research(operation="tvtropes", query="mentor archetype", category="literature")
adn_notes(operation="write", title="Time-loop films", folder="research",
           content="# Time-loop films\n\n tropes go here", tags="tropes, film")
```

## Prompt Cookbook (copy-paste starters)

**Start a literature review.** "Use research_orchestrate on QUERY, then write the
brief to FOLDER with citations, then suggest_tags for the new note." Fill QUERY and
FOLDER; the chain gathers, grounds, generates, and files.

**Clean the inbox.** "Process the inbox, then qc mode find_runts max_length 200 on
the new notes, then summarize anything longer than 500 words." Run weekly.

**Prepare a skill.** "Distill TOPIC from arXiv (max 5 papers) into category CAT,
activate it for the session, and load the section most relevant to TASK." Fill
TOPIC, CAT, TASK.

**Fix tag sprawl.** "Run tag_analytics, propose consolidations with dry_run, wait
for my approval, then execute and verify with project_stats." Never skip approval.

**Brief me on a note.** "Build a 2-hop context around IDENTIFIER and summarize it
in five bullets with open questions." Fill IDENTIFIER.

**Capture a meeting.** "Dictate 10 minutes tagged meeting, then append the
transcript summary to today's daily note under a ## Meetings section."

**Check system health.** "Report status detailed, LLM status, and sync state; flag
anything not idle or available."

**Migrate a vault.** "Ingest the Obsidian vault at PATH, reindex full, then
compare project_stats before and after." Fill PATH.

**Map a debate.** "Cluster content on TOPIC (limit 50), canvas the top cluster to
maps/, and list three gaps worth writing." Fill TOPIC.

**Retire a project.** "Show project status, list its notes count, then rm the
project after I confirm. Disk files must stay."

## More Tutorials (41-50)

### Tutorial 41: Move House (vault migration, verified)

Migrate without losing the index.

```python
adn_project(operation="status", name="main")          # record counts first
adn_inbox(operation="process")                        # flush pending docs
# ... copy the vault folder on disk ...
adn_project(operation="create", name="main2", path="D:/vaults/main2")
adn_system(operation="reindex", focus="all", project="main2")
adn_knowledge(operation="bulk", bulk_operation="project_stats")
```

### Tutorial 42: Weekly Review Ritual

Same pass every Friday.

```python
adn_nav(operation="recent", timeframe="7d", page_size=50)
adn_knowledge(operation="qc", mode="find_runts", max_length=200)
adn_knowledge(operation="analyze", analysis_type="find_gaps", limit=20)
adn_notes(operation="daily", content="## Weekly review\n- Reviewed N notes\n- Gaps: ...")
```

### Tutorial 43: Compare Two Corpora

ArXiv versus GitHub on one question.

```python
a = adn_research(operation="arxiv", query="retrieval augmented generation", limit=10)
g = adn_research(operation="github", query="retrieval augmented generation", limit=10)
adn_notes(operation="write", title="RAG corpora compared", folder="research",
           content="# RAG: papers vs code\n\n...", tags="rag, comparison")
```

### Tutorial 44: Skill Import from GitHub

Adopt a community skill properly.

```python
adn_skills(operation="import_from_github", repository="owner/repo",
           branch="main", category="developer")
adn_skills(operation="list", category="developer")
adn_skills(operation="read", identifier="imported-skill")
adn_skills(operation="activate", identifier="imported-skill", scope="message")
```

### Tutorial 45: Alarm-Driven Writing Sprint

Timebox with audio cues.

```python
adn_audio(operation="alarm", time_str="09:00 AM")
adn_audio(operation="timer", duration="45 minutes")
# ... write ...
adn_audio(operation="dictate", record_duration=120, tags="sprint-retro")
```

### Tutorial 46: Export Round-Trip Check

Prove the export is faithful.

```python
export_html_notes()
# open the HTML, spot-check three notes with heavy links
adn_search(operation="query", search_type="tag", text="export-check")
```

### Tutorial 47: Relationship Audit

Find orphans and over-connectors.

```python
adn_nav(operation="status")
adn_knowledge(operation="analyze", analysis_type="suggest_relationships", limit=30)
adn_nav(operation="backlinks", identifier="index")
```

### Tutorial 48: Provider Failover Drill

Practice the local-to-hosted switch.

```python
adn_llm(operation="health")
adn_llm(operation="select_model", provider="openai", model="gpt-4o-mini")
adn_knowledge(operation="summarize", identifier="Transformers")
adn_llm(operation="select_model", provider="ollama", model="llama3:8b")
```

### Tutorial 49: Transcript to Skill

Turn a dictated brain-dump into a reusable pack.

```python
adn_audio(operation="dictate", record_duration=180, tags="raw")
adn_knowledge(operation="enhance", identifier="dictated-note", update_style=True)
adn_skills(operation="distill_from_text", text_path="vault/inbox/dictated-note.md",
           topic="session insights", category="general")
```

### Tutorial 50: Full Vault Census

Count everything, verify the index agrees.

```python
adn_project(operation="status")
adn_knowledge(operation="bulk", bulk_operation="project_stats")
adn_search(operation="query", search_type="text", text="*")
adn_system(operation="sync")
```

## Glossary

**Permalink:** stable note address used as identifier. **Corpus:** one searchable
source (vault, arXiv slice, GitHub slice). **Runt:** note shorter than the quality
threshold. **The Door:** staged skill loading (TOC, section, resource).
**Portmanteau:** one tool, many operations via an enum. **Ambient project:** the
default project for calls without an explicit override. **Dry run:** a bulk plan
printed but not executed. **Envelope:** the standard success/message/data response
shape. **Daemon:** the persistent HTTP process owning the database. **Proxy mode:**
a stdio instance forwarding to a live daemon instead of opening the database.

## Error Message Index

**"Note not found"** — wrong identifier; search by partial title first.
**"RAG returns no results"** — stale or empty vector index; reindex, verify vault path.
**"External API rate limited"** — back off, lower limits, prefer duckduckgo.
**"Project not found"** — typo in name or wrong ambient project; list projects.
**"Model not loaded"** — run load_model first, or pick a hosted provider.
**"Inbox empty"** — nothing pending; check the inbox path with info first.
**"Skill flooding context"** — use The Door; deactivate when done.
**"Database is locked"** — a second daemon is running; stop it, keep one owner.
**"Permission denied on log rotation"** — two processes share one log sink;
give each process its own file.

## Advanced Patterns

**Research-then-distill pipeline.** Run `research_orchestrate` on a question,
write the brief with `adn_notes write`, enrich it (`enhance`, `suggest_tags`),
then `distill_from_text` on the brief's path to mint a skill. Four calls,
question to reusable pack, with the brief as audit trail.

**Progressive disclosure reading.** For a new domain: `rag` query for the five
most relevant notes, `build_context` depth 1 around the best hit, read those,
then `expand` the weakest one with `adn_zettel`. You go from zero to a written
note in one pass, and every claim links back to a source note.

**Inbox zero routine.** `inbox status`, `process` what arrived, `qc find_runts`
on the fresh notes, `summarize` the long ones, `bulk tag_maintenance` to file
them, `daily` to log the session. Fifteen minutes, repeatable daily.

**Pre-publish checklist.** `validate_content` for frontmatter and links,
`analyze_quality` on the changed notes, `canvas` a map of the affected cluster,
`export_html_notes` for a faithful preview, read the preview, then publish.
Catches broken links and runt sections before readers do.

**Model rotation for big jobs.** `list_models`, `load_model` the small local
model, run the `batch` pass, `unload_model`, then `select_model` hosted for the
quality review of a sample. Keeps VRAM free and quality high without babysitting.

**Skill library hygiene (monthly).** `list` everything, `read` the stale ones,
`update` what changed, `deactivate all`, `find_duplicates` via bulk to catch
overlapping packs, `rm` nothing (archive by moving to an archive folder so links
survive). A small current library beats a large stale one.

**Debate mapping.** Pick a contested topic, `cluster_content` on it, `canvas`
each cluster separately, `extract_insights` per cluster, then write one note per
position with `backlinks` wired between them. Readers can traverse the whole
disagreement from any entry point.

**Incident response notes.** When something breaks: `quick` capture symptoms,
`backlinks` on the failing component, `recent` 7d for what changed, `daily`
append the timeline, write a postmortem note, `suggest_tags` so the next
incident finds it. Future you will thank present you.

**Conference prep.** `arxiv submittedDate` for the last month in the track,
`github best-match` for implementations, `research_orchestrate` for the brief,
`mindmap` diagram for the talk arc, `export_pdf_native` for handouts. One
afternoon, talk-ready.

**Legacy vault rescue.** `external` search the old export to scope it,
`ingest_obsidian` to import, `reindex full`, `project_stats` to verify counts,
`find_junk` to triage, `bulk_move` to file the keepers, `daily` to log what was
rescued and what was left behind.

## Scenario Scripts (worked end to end)

**Scenario A: thesis background chapter.** Ask `research_orchestrate` for
"contrastive learning in vision transformers" and file the brief under
`research/contrastive-background`. Read it, then `backlinks` on the two most
cited papers to find related vault notes. `build_context` depth 2 around the
brief, `extract_insights` for claims, and rewrite the chapter note with
`replace_section` per section. Finish with `suggest_tags` and a `canvas` map of
the chapter filed under `maps/`. Expected output: one chapter note, one map,
five or more new backlinks.

**Scenario B: codebase onboarding.** `github best-match` for the framework,
`distill_from_github` on the winner into `developer/`, `activate` it for the
session, and `load_section` on architecture only. Ask `rag` for the vault's own
notes on the framework, `connect` the new skill note to them, and `daily` log
the onboarding. Expected output: one skill, three or more links, one log entry.

**Scenario C: conference talk in a day.** Morning: `arxiv submittedDate` for the
track plus `github stars` for demos. Midday: `research_orchestrate` the brief,
`mindmap` the talk arc, `flowchart` the demo path. Afternoon: `write` the
speaker notes, `enhance` them, `export_pdf_native` handouts, `timer` 25-minute
rehearsal blocks with `dictate` retros between takes. Expected output: brief,
arc map, speaker notes, handout PDF.

**Scenario D: tag bankruptcy recovery.** `tag_analytics` to see the damage,
`consolidate_tags` dry_run to preview merges, `bulk_move` strays into folders
first so merges stay small, execute consolidation, `find_duplicates` to catch
twins the merge exposed, `project_stats` to confirm totals unchanged, `daily`
to record the new tag canon. Expected output: fewer tags, same note count, a
canon note.

**Scenario E: incident postmortem.** `quick` capture symptoms with timestamps,
`recent` 7d for what changed, `backlinks` on the failing component, `rag` for
past incidents with similar signatures, `daily` append the timeline, `write`
the postmortem under `ops/`, `suggest_tags` so the next incident surfaces it,
and `canvas` the failure chain for the review. Expected output: timeline,
postmortem note, failure map, tags that will find it next time.

## Operation Quick Index (every operation, one line)

**adn_notes:** write (new note with metadata), read (full note by title/permalink),
edit (append/prepend/replace_section/find_replace), delete (remove note),
move (change folder), quick (rapid capture with auto-title), daily (append to
today's log).

**adn_search:** query (Boolean full-text, text/title/permalink/tag scopes),
rag (semantic retrieval by prompt), external (Obsidian/Notion/Joplin/Evernote
vaults), reindex (full or incremental rebuild).

**adn_knowledge:** suggest_tags (propose tags), summarize (executive summary),
enhance (style/context/expand upgrades), qc (find_runts/find_junk),
canvas (Obsidian visual maps), analyze (quality/relationships/gaps/clusters/
insights), bulk (tag_analytics/consolidate_tags/tag_maintenance/bulk_update/
validate_content/project_stats/find_duplicates/bulk_move/bulk_delete).

**adn_nav:** ls (directory listing), recent (chronological feed), backlinks
(notes linking to a target), build_context (relation walk), status (graph
health), sync (indexing progress).

**adn_project:** ls (list projects), create (register name+path), switch
(change ambient context), rm (unregister, files kept), status (stats+health),
detect (auto-select).

**adn_zettel:** generate (atomic note, quick/standard/comprehensive/expert),
suggest (next topics), expand (horizontal growth, depth 1-5), analyze (vault
maturity), connect (auto-link relations), collect (rapid capture), customize
(tune pipeline).

**adn_skills:** create/read/update/delete/list (lifecycle), activate (TOC only),
deactivate (unload), active (what is open), load_section (one section),
load_resource (script/reference), distill_from_arxiv/wikipedia/expert/textbook/
text (research to skill), import_from_github (repo to skill).

**adn_audio:** dictate (speech to note), speak (text to speech), listen (voice
command window), wake_start/wake_stop/wake_status (hands-free listener),
weather (location report), timer (countdown), alarm (time trigger), music
(play/pause/next/previous with query).

**adn_automation:** workflow (multi-step goal, capped iterations), batch (one
instruction across items), status (engine health).

**adn_inbox:** status (pending files), process (convert+ingest all or one file),
info (Pandoc/pypdf health), watch (background monitoring).

**adn_typora:** open (load file), save, insert (text at anchor), get_content
(read document), set_content (replace document), cursor (telemetry), analyze
(headings/links health), export (pdf/html/docx/odt).

**adn_llm:** list_providers, list_models, select_model (persist default),
load_model/unload_model (VRAM), status (active model), health (all providers).

**adn_research:** web_search, arxiv, github, document_ingest, rag_query,
llm_config, llm_generate, research_orchestrate, tvtropes.

**adn_system:** status (basic/detailed/expert), help (docs), workflow
(autonomous goal), external_bridge (call other servers), sync (file engine),
reindex (rag/db/all).

**adn_arxiv_research:** relevance, lastUpdatedDate, submittedDate.
**adn_github_research:** stars, forks, updated, best-match.
**adn_web_search:** duckduckgo, serpapi, bing, auto.
**adn_tvtropes_research:** all, film, literature, tv, video_games, webcomics, music.
**adn_visualize:** point_cloud, hub_and_spoke, temporal.
**generate_mermaid_diagram:** flowchart, sequence, gantt, mindmap, er.
**Ingest:** ingest_obsidian/notion/joplin/evernote/onenote/archive,
build_context. **Zettel Ancient:** generate, suggest, expand, connect, collect.
**Memory:** build_context, recent, ls, backlinks, sync. **Projects (alt):**
list_memory_projects, create_memory_project, create, switch, rm, detect.
**Search (alt):** query_text/title/permalink/tag, rag, external.

## Migration, Limits, and More Answers

**Upgrading the bundle.** Data lives outside the bundle, so reinstall freely.
After upgrading, run one full reindex: index schemas migrate on first run and
the search surface may lag until it completes. Verify with project_stats.

**Rate limits and quotas.** SerpAPI and Bing enforce daily quotas; DuckDuckGo
is unlimited but slower. GitHub API allows generous anonymous use, higher with
a token. arXiv asks for polite pacing (seconds between bursts). On 429 errors,
halve max_results and retry; the orchestrator does this automatically.

**How large can a vault get?** SQLite handles hundreds of thousands of notes;
LanceDB vectors dominate disk. Reindex time scales with note count and embedding
model speed. Archive cold folders out of the watched tree when scans slow down.

**Can two assistants share one vault?** Yes through one daemon; never through
two daemons or direct file writes while the watcher runs. Concurrent edits to
one note last-write-wins; coordinate via daily notes instead.

**Which operations are destructive?** delete, move, bulk_delete, bulk_move,
bulk_update, consolidate_tags, project rm (registration only, files kept).
Everything else is additive. Snapshot before destructive runs.

**How do I audit what automation did?** Workflows log progress notes to the
vault; batch runs echo affected identifiers. Read those before re-running.

**Why do two searches disagree?** Different indexes (keyword FTS vs vectors)
and different windows (recent vs all-time). Run the same query in both modes
before concluding content is missing.

**When should I restart the daemon?** After upgrades, after changing providers
or embedding models, and when sync status stays non-idle with an empty queue.
Check the health endpoint for the new build marker after restart.
