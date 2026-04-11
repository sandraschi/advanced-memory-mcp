# Advanced Memory MCP - Practical Usage Guide

## Getting Started: The Thinking Persona

Advanced Memory is not just a database; it is a **Thinking Substrate**. To get the most out of it, treat it as a collaborator that stores your logic and architectural decisions.

### Scenario 1: Developing a New Feature (Industrialized)

When starting a project, use the **Entity Engine** to prime your workspace.

1. **Initialize Project**:
   ```bash
   # Create a dedicated context for your new project
   adn_content("write", "Project Zero-G", "Initializing the quantum-gravity research branch.", "#milestone #science")
   ```
2. **Retrieve Context**:
   When you return to work, ask your AI:
   *"Retrieve the latest milestones for Project Zero-G and summarize our architectural consensus."*
   The AI will use semantic search to fetch relevant notes.

### Scenario 2: Documentation Synthesis (Deep Research)

If you have a collection of PDFs or Markdown files, use the ingestion pipeline.

1. **Ingest Content**:
   Use the `ingest_file` or `ingest_folder` tools.
2. **Execute RAG**:
   Ask: *"Based on the Gormenghast trilogy, map the relationship between Steerpike and Fuchsia using a Mermaid diagram."*
   Advanced Memory will retrieve the passages, rerank them for relevance, and feed them into the model.

### Scenario 3: Fleet-Wide Milestones

If you are working across many repositories, use the **Global Tagging** system.

- Use `#tech-debt` to track issues across your fleet.
- Use `adn_status("fleet")` to see the health and versioning of all registered nodes.

## Tips for High-Fidelity Results

> [!TIP]
> **Semantic Precision**: Use rich descriptive text for milestone summaries. Instead of "Fix bug", write "Remediated race condition in the async port listener by introducing a PID-aware lock file."

> [!IMPORTANT]
> **Benny Protocol**: If you encounter an unrecoverable failure or a security anomaly, tag it with `#benny-interrupt`. This signals to the fleet that a manual investigation is required.

---

[Back to README](../README.md) | [Architecture Overview](ARCHITECTURE.md) | [Fleet Setup](FLEET.md)
