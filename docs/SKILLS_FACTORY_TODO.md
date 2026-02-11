# Skills Factory Implementation TODO

**Date:** 2026-02-10
**Handoff:** Antigravity/Gemini can continue from this plan if Cursor credits run out.
**Reference:** mcp-central-docs/docs/skills/SKILLS_FACTORY_RESEARCH_DARK_APP_PATTERN.md

---

## Phase 1: ResearchChainService

- [x] Create `src/advanced_memory/services/skill_research_chain.py`
  - [ ] Define `ResearchBundle` dataclass (topic, snippets, citations, synthesis, gaps_remaining, coverage_score, iteration_count, sources_used)
  - [ ] Define `ResearchGapAnalysis` Pydantic model (synthesis, gaps, next_sources, coverage_score, should_continue)
  - [ ] Implement `ResearchChainService.run_chain(topic, sources, max_iterations, coverage_threshold)` -> ResearchBundle
  - [ ] Call existing tools: adn_arxiv_research, adn_github_research, adn_rag, adn_web_search, adn_document_ingest
  - [ ] After each batch: LLMClient.generate() with gap-analysis prompt -> ResearchGapAnalysis
  - [ ] Loop until coverage >= threshold or max_iterations
- [ ] Add unit tests for ResearchChainService

---

## Phase 2: adn_skills_research Tool

- [x] Create `src/advanced_memory/mcp/tools/adn_skills_research.py`
  - [ ] Parameters: topic, sources (list), max_iterations, coverage_threshold, output_format (bundle|skill_draft)
  - [ ] Call ResearchChainService.run_chain()
  - [ ] If output_format="skill_draft": pass bundle to LLM for SKILL.md skeleton
  - [ ] Return structured dict (success, research_bundle, skill_draft?)
- [x] Register tool in portmanteau_skills (operation "research") and __init__.py (FULL mode)
- [ ] Update docs (PORTMANTEAU_TOOLS_REFERENCE.md, TOOLS_REFERENCE.md)

---

## Phase 3: Reference Scaffolding

- [x] Create `src/advanced_memory/services/skill_creator/reference_scaffolder.py`
  - [x] `scaffold_references_from_research(skill_path: Path, research_bundle: ResearchBundle) -> Path`
  - [x] Create `skill_path/references/`
  - [x] Write `references/REFERENCE.md` with synthesis, gaps, citations
  - [x] Write `references/SOURCES.md` (bib-style, optional via include_sources_md)
- [x] Integrate: adn_skills_research(output_format="skill_draft", output_path=...) scaffolds references/

---

## Phase 4: Spec Validation

- [x] Add validate_skill_agentskills() in validator.py
  - [x] Name checks (1-64 chars, lowercase, hyphens, matches directory)
  - [x] Description checks (1-1024 chars, non-empty)
  - [x] agentskills_checks dict (per-field pass/fail)
  - [x] Returns spec_compliant bool, warnings list
- [x] Integrate into adn_skills_creator(operation="validate"); backward-compatible

---

## Phase 5: research_first_create Operation

- [x] Add operation `research_first_create` to `make_skill_advanced` in `src/advanced_memory/mcp/tools/make_skill_advanced.py`
  - [x] Step 1: Run run_chain(topic) -> ResearchBundle
  - [x] Step 2: LLM generates SKILL.md from bundle (LLMClient)
  - [x] Step 3: scaffold skill dir, references/ via scaffold_skill + scaffold_references_from_research
  - [x] Step 4: Run spec validation (validate_skill_agentskills)
  - [x] Step 5: LLM review loop (optional, enable_review_loop param)
  - [x] Step 6: Finalize SKILL.md + references/*
- [x] Parameters: topic, skill_name?, research_sources, max_research_iterations, enable_review_loop, output_path
- [x] Document in RESEARCH_DRIVEN_SKILLS.md

---

## Implementation Order

1. Phase 1 (ResearchChainService) – foundation
2. Phase 2 (adn_skills_research tool) – MCP exposure
3. Phase 3 (Reference scaffolding) – output enrichment
4. Phase 4 (Spec validation) – quality gate
5. Phase 5 (research_first_create) – end-to-end workflow

---

## Rules (DO NOT VIOLATE)

- **No emojis** in Python source, logger messages, PowerShell scripts
- **PowerShell:** No `&&`, use `;` or separate lines
- **Existing tools:** Import adn_arxiv_research, adn_github_research, adn_rag, adn_web_search, adn_document_ingest; do not duplicate
- **LLM:** Use `advanced_memory.services.llm_client.LLMClient`
- **Paths:** Use pathlib.Path, cross-platform
