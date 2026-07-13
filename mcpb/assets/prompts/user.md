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

## Troubleshooting

### "Note not found"

Use `adn_search(operation="text", query="partial name")` to find the correct identifier.

### "RAG returns no results"

Run `reindex()` to rebuild the search index. Verify vault path is correct.

### "External API rate limited"

Increase delay configuration or reduce request frequency.

## FAQ

**Q: What's a portmanteau tool?** A single function with an `operation` enum parameter grouping related operations to prevent tool explosion.

**Q: Can I use this with Obsidian?** Yes. Set `AM_VAULT_PATH` to your vault directory.

**Q: What is "The Door" pattern for skills?** Skills load in stages: activation loads the table of contents only, then sections are loaded on demand to prevent context flooding.

**Q: Can this call other MCP servers?** Yes — use `adn_system(operation="external_bridge")`.
