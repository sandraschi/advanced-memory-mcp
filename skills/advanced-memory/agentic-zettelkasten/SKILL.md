---
name: agentic-zettelkasten
description: Structured Zettelkasten workflow for AMD — observe, draft, enrich, retrieve, decide, preview, write, verify. Produces high-quality atomic knowledge cards with deliberate linking.
whenToUse: >
  After completing meaningful work that produced reusable insights. This skill
  provides a disciplined Zettelkasten protocol (inspired by Luhmann's method
  and the A-MEM memory model) for creating atomic cards that survive sessions.
  Use this INSTEAD of raw adn_notes(operation="write") for any insight worth
  keeping. Do NOT use for throwaway notes or session-state capture.
---

# Agentic Zettelkasten Skill

A structured Zettelkasten protocol for Advanced Memory that produces
high-quality atomic knowledge cards through deliberate retrieval,
enrichment, and explicit link decisions.

**This skill replaces ad-hoc note-taking.** Every card written through
this workflow is an atomic insight in your own words, with `[[wikilinks]]`
embedded in sentences explaining the relationship — not a bare tag list.

## Core Principles (Luhmann's Method)

1. **Atomicity** — One insight per card. If you have two ideas, write two cards.
2. **Own words** — Distill and rephrase. Copy-paste = no understanding (Feynman test).
3. **Links in context** — `[[links]]` must appear in sentences explaining the relationship.
   Good: "This contradicts [[jwt-migration]] — stateless tokens can't be revoked."
   Bad: "Related: [[jwt-migration]]"
4. **Retrieve before write** — Always search for existing cards first. Never create duplicates.
5. **Preview before mutate** — Show planned changes before writing anything.

## Tools Available

| Action | AMD Tool |
|--------|----------|
| Search existing knowledge | `adn_search(operation="rag", prompt="...")` or `adn_search(operation="query", text="...")` |
| Read a card | `adn_notes(operation="read", identifier="...")` |
| Write a new card | `adn_notes(operation="write", title="...", content="...", folder="...")` |
| Edit existing card | `adn_notes(operation="edit", identifier="...", mode="append", content="...")` |
| Check recent activity | `adn_nav(operation="recent", timeframe="7d")` |
| Analyze knowledge gaps | `adn_zettel(operation="analyze")` |
| Get link suggestions | `adn_zettel(operation="connect")` |

## Workflow

### Step 1: Observe — What did we learn?

After completing a task, identify reusable insights. Skip if the content is:
- Temporary or session-specific (in-progress work, task state)
- Obvious or well-known (standard library usage, common patterns)
- Not reusable across future sessions

If nothing is worth remembering, stop here. This is a quality gate, not a formality.

### Step 2: Draft — One atomic card per insight

For each insight, draft exactly one card:

- **Title**: Short noun phrase (≤60 chars, kebab-case slug). Descriptive, not clever.
- **Body**: One atomic insight in your own words. 3-8 sentences. Include:
  - What the insight IS
  - Why it matters (context)
  - When it applies (boundary conditions)
  - A concrete example or counterexample

If you need more than 8 sentences, you probably have two insights. Split them.

### Step 3: Enrich — Proposed metadata

```yaml
---
title: <Short Noun Phrase>
created: <YYYY-MM-DD>
category: <one category: developer|researcher|writer|knowledge-worker|etc.>
tags: [<3-5 comma-separated categories>]
keywords: [<3-8 salient terms>]
---
```

### Step 4: Retrieve — Search before writing

Search for related existing cards using at least TWO queries:

```
adn_search(operation="rag", prompt="<topic keywords>", limit=5)
adn_search(operation="query", text="<exact term>", search_type="title")
```

Read the top candidates that look relevant:
```
adn_notes(operation="read", identifier="<slug>")
```

**Limits to avoid runaway retrieval:**
- Max candidate searches: 3
- Max cards read: 10

### Step 5: Decide — create, update, or skip

Choose exactly one action per insight:

| Action | When |
|--------|------|
| **create** | No existing card covers this insight. Embed `[[wikilinks]]` to related cards. |
| **update** | Existing card covers the same insight but lacks new detail. |
| **skip** | Insight is duplicate, too obvious, or not durable. |

Rules:
- Links must be chosen by reading candidate cards, not from embedding scores.
- Updating is allowed only after preview (Step 6).
- If in doubt between create and update: create. It's safer to have two cards than to corrupt one.

### Step 6: Preview — Show planned changes

Before writing, produce a preview:

```
Planned memory changes:
- CREATE: python-asyncio-gotcha (title: "Asyncio gather() doesn't guarantee order")
  → links: [[task-queue-pattern]] because tasks run concurrently, not sequentially
  → metadata: category=developer, tags=python,async,concurrency
- UPDATE: task-queue-pattern — add note about gather() ordering pitfall
  → append: "Note: asyncio.gather() starts all tasks concurrently; results
    may arrive out of order. Use asyncio.as_completed() for ordered results."
```

### Step 7: Write

**Create new card:**
```
adn_notes(operation="write",
  title="Asyncio gather() doesn't guarantee order",
  content="...",
  folder="developer",
  tags="python,async,concurrency")
```

**Update existing card:**
```
adn_notes(operation="edit",
  identifier="task-queue-pattern",
  mode="append",
  content="...")
```

**Rules for writing:**
- Wikilinks go in body text, not just frontmatter
- Every link has a "because" clause
- Title must match slug (kebab-case)
- Content is markdown with at least one `[[wikilink]]`

### Step 8: Verify — Readback check

After writing, read the card back:
```
adn_notes(operation="read", identifier="<slug>")
```

Confirm:
- Title and body match what was intended
- All `[[wikilinks]]` are syntactically valid
- Metadata frontmatter is complete (title, created, category, tags)
- Body is in your own words (not copy-pasted)

## Anti-Patterns

| Don't | Do instead |
|-------|-----------|
| Write 5 cards at once without retrieval | One card at a time, retrieve between each |
| Add `[[links]]` based on keyword overlap | Read the target card, decide if the relationship is meaningful |
| Update a card without preview | Preview first, then update |
| Use AI-generated content verbatim | Distill and rephrase in your own words |
| Skip the verify step | Always readback after writing |
| Create a "note dump" with 3 ideas in one card | Split into atomic cards, one insight each |
| Use bare links like "See also: [[X]]" | Embed in sentence: "This relates to [[X]] because..." |
