# CLI Tools Roadmap - Future Enhancements

**Comprehensive roadmap for new CLI tools to enhance Advanced Memory**

---

## Table of Contents

1. [Import Tools](#import-tools)
2. [Export Tools](#export-tools)
3. [Batch Operations](#batch-operations)
4. [Analytics & Visualization](#analytics--visualization)
5. [Backup & Recovery](#backup--recovery)
6. [Migration & Integration](#migration--integration)
7. [Quality & Maintenance](#quality--maintenance)
8. [Advanced Features](#advanced-features)
9. [Priority Matrix](#priority-matrix)

---

## Import Tools

### 1. `advanced-memory import cursor`

**Purpose**: Import Cursor IDE memories

**Status**: 📋 Proposed (see `docs/integrations/cursor-memory-import.md`)

**Usage**:
```bash
advanced-memory import cursor
advanced-memory import cursor --workspace-only
advanced-memory import cursor --file ~/.cursor/memories.json --folder cursor-memories
```

**Value**:
- **High**: Cursor users can preserve AI memories
- **Synergy**: Cursor + Advanced Memory = comprehensive AI memory system
- **Use case**: "Remember my Cursor learnings in my knowledge base"

---

### 2. `advanced-memory import obsidian`

**Purpose**: Import Obsidian vault

**Usage**:
```bash
advanced-memory import obsidian /path/to/vault
advanced-memory import obsidian /path/to/vault --preserve-structure
advanced-memory import obsidian /path/to/vault --exclude "Daily Notes/*"
```

**What it does**:
- Import entire Obsidian vault
- Convert Obsidian-specific syntax (dataview, etc.)
- Preserve folder structure
- Handle attachments (images, PDFs)
- Convert Obsidian canvas files

**Value**:
- **Critical**: Many PKM users start with Obsidian
- **Migration path**: Easy transition to Advanced Memory
- **Use case**: "I have 5 years of Obsidian notes"

**Implementation**:
- Parse Obsidian markdown (slightly different from standard)
- Handle dataview queries → observations
- Handle templates
- Handle daily notes

---

### 3. `advanced-memory import notion`

**Purpose**: Import Notion workspace

**Usage**:
```bash
advanced-memory import notion /path/to/export.zip
advanced-memory import notion /path/to/export.zip --page-prefix "Notion/"
```

**What it does**:
- Parse Notion export (markdown + CSV + HTML)
- Convert Notion databases → tagged entities
- Handle nested pages
- Preserve properties → YAML frontmatter
- Handle images and attachments

**Value**:
- **High**: Notion is very popular
- **Use case**: "Export my Notion workspace to self-hosted"

---

### 4. `advanced-memory import evernote`

**Purpose**: Import Evernote notebooks

**Usage**:
```bash
advanced-memory import evernote /path/to/export.enex
advanced-memory import evernote /path/to/export.enex --notebook "Work"
```

**What it does**:
- Parse ENEX format (Evernote export)
- Convert to markdown
- Handle attachments
- Preserve tags → YAML tags
- Handle notebooks → folders

**Value**:
- **Medium**: Evernote is declining but many users still have data
- **Use case**: "I have 10 years of Evernote notes"

---

### 5. `advanced-memory import roam`

**Purpose**: Import Roam Research

**Usage**:
```bash
advanced-memory import roam /path/to/export.json
```

**What it does**:
- Parse Roam JSON export
- Convert block references → wikilinks
- Handle daily pages
- Preserve graph structure

**Value**:
- **Medium**: Roam users are early adopters of networked thought
- **Use case**: "Migrate from Roam to self-hosted"

---

### 6. `advanced-memory import markdown`

**Purpose**: Bulk import markdown files from any source

**Usage**:
```bash
advanced-memory import markdown /path/to/directory
advanced-memory import markdown /path/to/directory --recursive
advanced-memory import markdown /path/to/directory --add-frontmatter
advanced-memory import markdown /path/to/directory --tag "imported"
```

**What it does**:
- Import markdown files without specific importer
- Auto-add YAML frontmatter if missing
- Add creation timestamps
- Auto-tag imported files
- Handle nested directories

**Value**:
- **Critical**: Universal fallback for any markdown source
- **Use case**: "I have markdown files from various sources"

---

### 7. `advanced-memory import github`

**Purpose**: Import GitHub issues, PRs, discussions

**Usage**:
```bash
advanced-memory import github owner/repo --type issues
advanced-memory import github owner/repo --type prs
advanced-memory import github owner/repo --type discussions
```

**What it does**:
- Use GitHub API to fetch issues/PRs/discussions
- Convert to markdown entities
- Preserve labels → tags
- Handle comments → observations
- Link related issues → relations

**Value**:
- **High**: Many developers want to track GitHub discussions
- **Use case**: "Keep all project discussions in one place"

---

## Export Tools

### 1. `advanced-memory export obsidian`

**Purpose**: Export to Obsidian-compatible vault

**Usage**:
```bash
advanced-memory export obsidian /path/to/vault
advanced-memory export obsidian /path/to/vault --include-canvas
```

**What it does**:
- Export all notes to Obsidian format
- Generate canvas files for knowledge graphs
- Preserve wikilinks
- Copy attachments

**Value**:
- **High**: Obsidian is popular, good exit strategy
- **Use case**: "Try Advanced Memory, keep Obsidian as backup"

---

### 2. `advanced-memory export hugo`

**Purpose**: Export to Hugo static site

**Usage**:
```bash
advanced-memory export hugo /path/to/hugo-site
advanced-memory export hugo /path/to/hugo-site --theme minimal
```

**What it does**:
- Generate Hugo-compatible markdown
- Create index pages
- Generate tag pages
- Copy images to static folder

**Value**:
- **Medium**: Digital gardening, personal wiki websites
- **Use case**: "Publish my knowledge base as a website"

---

### 3. `advanced-memory export pdf`

**Purpose**: Export notes to PDF

**Usage**:
```bash
advanced-memory export pdf report.pdf --query "tag:project-alpha"
advanced-memory export pdf book.pdf --folder "research" --toc
```

**What it does**:
- Convert markdown → PDF via Pandoc
- Generate table of contents
- Include images
- Support filters (tags, folders, queries)

**Value**:
- **Medium**: Sharing, archiving, printing
- **Use case**: "Export research notes as PDF book"

---

### 4. `advanced-memory export json`

**Purpose**: Export as structured JSON

**Usage**:
```bash
advanced-memory export json data.json
advanced-memory export json data.json --include-content
advanced-memory export json data.json --query "updated:7d"
```

**What it does**:
- Export entities, relations, observations as JSON
- Optionally include full content
- Support filters
- Machine-readable format

**Value**:
- **High**: Data portability, integrations
- **Use case**: "Analyze my knowledge base with Python"

---

## Batch Operations

### 1. `advanced-memory batch delete`

**Purpose**: Bulk delete entities

**Usage**:
```bash
advanced-memory batch delete --query "tag:temp"
advanced-memory batch delete --query "type:note AND updated:<30d"
advanced-memory batch delete --folder "old-notes" --dry-run
```

**Options**:
- `--query`: Search query to select entities
- `--folder`: Select by folder
- `--tag`: Select by tag
- `--dry-run`: Show what would be deleted (don't actually delete)
- `--yes`: Skip confirmation

**Value**:
- **High**: Cleanup, maintenance
- **Use case**: "Delete all temp notes from last year"

---

### 2. `advanced-memory batch rename`

**Purpose**: Bulk rename entities

**Usage**:
```bash
advanced-memory batch rename --query "tag:python" --prefix "Python: "
advanced-memory batch rename --folder "old" --find "Notes" --replace "Reference"
```

**Options**:
- `--query`: Select entities
- `--prefix`: Add prefix to titles
- `--suffix`: Add suffix to titles
- `--find`: Find string in title
- `--replace`: Replace with string
- `--regex`: Use regex for find/replace

**Value**:
- **Medium**: Organization, consistency
- **Use case**: "Rename all notes to follow new naming convention"

---

### 3. `advanced-memory batch tag`

**Purpose**: Bulk add/remove tags

**Usage**:
```bash
advanced-memory batch tag --query "folder:research" --add "research"
advanced-memory batch tag --query "tag:old-tag" --remove "old-tag" --add "new-tag"
advanced-memory batch tag --folder "projects" --add "active"
```

**Options**:
- `--query`: Select entities
- `--folder`: Select by folder
- `--add`: Add tags
- `--remove`: Remove tags
- `--replace`: Replace tags

**Value**:
- **High**: Organization, bulk re-tagging
- **Use case**: "Tag all research notes with 'research'"

---

### 4. `advanced-memory batch move`

**Purpose**: Bulk move entities to different folder

**Usage**:
```bash
advanced-memory batch move --query "tag:archived" --to "archive/"
advanced-memory batch move --folder "temp" --to "completed/"
```

**Value**:
- **Medium**: Reorganization
- **Use case**: "Move completed projects to archive folder"

---

### 5. `advanced-memory batch link`

**Purpose**: Bulk create relations

**Usage**:
```bash
advanced-memory batch link --query "tag:python" --to "Python" --type "about"
advanced-memory batch link --file links.csv
```

**File format** (`links.csv`):
```csv
from,to,relation_type
"Python Fundamentals","Python","about"
"Flask Tutorial","Python","uses"
```

**Value**:
- **High**: Knowledge graph construction
- **Use case**: "Link all Python notes to main Python entity"

---

## Analytics & Visualization

### 1. `advanced-memory stats`

**Purpose**: Show knowledge base statistics

**Usage**:
```bash
advanced-memory stats
advanced-memory stats --detailed
advanced-memory stats --json > stats.json
```

**What it shows**:
- Total entities, observations, relations
- Entity type breakdown
- Tag distribution
- Folder sizes
- Growth over time
- Most connected entities
- Orphan entities (no connections)
- Tag co-occurrence

**Value**:
- **High**: Understanding your knowledge base
- **Use case**: "How much have I written this year?"

---

### 2. `advanced-memory graph`

**Purpose**: Generate knowledge graph visualization

**Usage**:
```bash
advanced-memory graph output.html
advanced-memory graph output.html --query "tag:ai"
advanced-memory graph output.html --depth 2 --center "Python"
```

**Output formats**:
- HTML (interactive, D3.js)
- SVG (static)
- Graphviz DOT
- Mermaid diagram
- Obsidian Canvas

**Value**:
- **High**: Visualization, presentations
- **Use case**: "Show my knowledge graph to colleagues"

---

### 3. `advanced-memory timeline`

**Purpose**: Generate timeline of activity

**Usage**:
```bash
advanced-memory timeline
advanced-memory timeline --query "tag:project-alpha"
advanced-memory timeline --format html > timeline.html
```

**What it shows**:
- Notes created over time
- Edit activity heatmap
- Tag evolution
- Project milestones

**Value**:
- **Medium**: Reflection, progress tracking
- **Use case**: "Show my learning journey"

---

### 4. `advanced-memory report`

**Purpose**: Generate comprehensive report

**Usage**:
```bash
advanced-memory report monthly.pdf --period "last-month"
advanced-memory report yearly.pdf --period "2024"
```

**Includes**:
- Statistics
- Most active areas
- Growth charts
- Tag clouds
- Recent highlights
- Goals vs. progress

**Value**:
- **Medium**: Reviews, reflection
- **Use case**: "Generate monthly knowledge work report"

---

## Backup & Recovery

### 1. `advanced-memory backup`

**Purpose**: Create full backup

**Usage**:
```bash
advanced-memory backup backup.tar.gz
advanced-memory backup backup.tar.gz --include-db
advanced-memory backup backup.tar.gz --encrypt --password-file key.txt
```

**What it includes**:
- All markdown files
- Database (optional)
- Configuration
- Attachments

**Value**:
- **Critical**: Data safety
- **Use case**: "Daily automated backups"

---

### 2. `advanced-memory restore`

**Purpose**: Restore from backup

**Usage**:
```bash
advanced-memory restore backup.tar.gz
advanced-memory restore backup.tar.gz --target /new/location
```

**Value**:
- **Critical**: Disaster recovery
- **Use case**: "Restore after disk failure"

---

### 3. `advanced-memory snapshot`

**Purpose**: Create git-based snapshot

**Usage**:
```bash
advanced-memory snapshot "Monthly checkpoint"
advanced-memory snapshot "Before major reorganization"
```

**What it does**:
- Creates git commit (if project is git repo)
- Tags with date
- Records statistics

**Value**:
- **High**: Version control, rollback
- **Use case**: "Checkpoint before major changes"

---

## Migration & Integration

### 1. `advanced-memory migrate`

**Purpose**: Migrate between Advanced Memory versions

**Usage**:
```bash
advanced-memory migrate --from 0.9.0 --to 1.0.0
```

**What it does**:
- Database schema migrations
- Format conversions
- Frontmatter updates

**Value**:
- **Critical**: Smooth upgrades
- **Use case**: "Upgrade to new version"

---

### 2. `advanced-memory doctor`

**Purpose**: Diagnose and fix issues

**Usage**:
```bash
advanced-memory doctor
advanced-memory doctor --fix
advanced-memory doctor --report doctor-report.txt
```

**Checks**:
- Database integrity
- Broken wikilinks
- Missing files
- Orphan database entries
- Malformed YAML
- Duplicate permalinks
- Encoding issues

**Value**:
- **Critical**: Maintenance, troubleshooting
- **Use case**: "Fix issues after manual edits"

---

### 3. `advanced-memory watch`

**Purpose**: Watch for changes and auto-sync

**Usage**:
```bash
advanced-memory watch
advanced-memory watch --daemon
advanced-memory watch --log watch.log
```

**What it does**:
- Monitor file changes
- Auto-sync on change
- Report sync status
- Run as background service

**Value**:
- **High**: Convenience, real-time sync
- **Use case**: "Always keep database in sync"

---

### 4. `advanced-memory index rebuild`

**Purpose**: Rebuild search index from scratch

**Usage**:
```bash
advanced-memory index rebuild
advanced-memory index rebuild --vacuum
```

**What it does**:
- Drop search index
- Re-scan all files
- Rebuild FTS5 index
- Optimize database

**Value**:
- **High**: Fix search issues
- **Use case**: "Search is returning wrong results"

---

## Quality & Maintenance

### 1. `advanced-memory lint`

**Purpose**: Check for quality issues

**Usage**:
```bash
advanced-memory lint
advanced-memory lint --fix
advanced-memory lint --report lint-report.txt
```

**Checks**:
- Broken wikilinks
- Missing YAML frontmatter
- Duplicate titles
- Empty notes
- Orphan notes (no links)
- Over-long notes (readability)
- Inconsistent formatting
- Missing tags

**Value**:
- **High**: Quality assurance
- **Use case**: "Maintain high-quality knowledge base"

---

### 2. `advanced-memory dedupe`

**Purpose**: Find and remove duplicates

**Usage**:
```bash
advanced-memory dedupe
advanced-memory dedupe --similarity 0.9
advanced-memory dedupe --merge
```

**What it does**:
- Find duplicate/similar notes
- Calculate similarity score
- Optionally merge duplicates
- Preserve all content

**Value**:
- **Medium**: Cleanup
- **Use case**: "Remove duplicate imports"

---

### 3. `advanced-memory orphans`

**Purpose**: Find orphan entities (no connections)

**Usage**:
```bash
advanced-memory orphans
advanced-memory orphans --suggest-links
```

**What it does**:
- Find entities with no relations
- Suggest potential links (using embeddings)
- Export list for review

**Value**:
- **Medium**: Knowledge graph completeness
- **Use case**: "Connect isolated notes"

---

## Advanced Features

### 1. `advanced-memory embed`

**Purpose**: Generate embeddings for semantic search

**Usage**:
```bash
advanced-memory embed
advanced-memory embed --model sentence-transformers
advanced-memory embed --update
```

**What it does**:
- Generate vector embeddings for all notes
- Store in database
- Enable semantic search

**Value**:
- **High**: Better search, AI features
- **Use case**: "Find similar notes semantically"

---

### 2. `advanced-memory suggest`

**Purpose**: AI-powered suggestions

**Usage**:
```bash
advanced-memory suggest links "Python Fundamentals"
advanced-memory suggest tags "My New Note"
advanced-memory suggest related "AI Research"
```

**What it does**:
- Use embeddings/LLM to suggest:
  - Related notes
  - Potential links
  - Tags
  - Observations

**Value**:
- **High**: AI augmentation
- **Use case**: "What should I link this to?"

---

### 3. `advanced-memory merge`

**Purpose**: Merge two entities

**Usage**:
```bash
advanced-memory merge "Python" "python-lang" --keep "Python"
```

**What it does**:
- Combine two entities into one
- Merge content
- Update all references
- Preserve history

**Value**:
- **Medium**: Cleanup, consolidation
- **Use case**: "Merge duplicate concept notes"

---

### 4. `advanced-memory split`

**Purpose**: Split entity into multiple

**Usage**:
```bash
advanced-memory split "Big Note" --by-headers
```

**What it does**:
- Split large note by headers
- Create separate entities
- Link related notes

**Value**:
- **Medium**: Refactoring
- **Use case**: "Break up large monolithic note"

---

## Priority Matrix

### High Priority (Implement First)

**Tier 1** (Critical, high value):
1. ✅ `import markdown` - Universal markdown import
2. ✅ `batch delete` - Essential cleanup
3. ✅ `batch tag` - Essential organization
4. ✅ `stats` - Understanding usage
5. ✅ `doctor` - Troubleshooting
6. ✅ `backup` - Data safety

**Tier 2** (High value):
7. `import cursor` - Cursor IDE integration
8. `import obsidian` - Migration from Obsidian
9. `export json` - Data portability
10. `graph` - Visualization
11. `lint` - Quality assurance
12. `watch` - Convenience

### Medium Priority (Implement Later)

**Tier 3** (Valuable enhancements):
13. `import notion` - Migration
14. `export obsidian` - Exit strategy
15. `batch rename` - Organization
16. `batch move` - Organization
17. `timeline` - Reflection
18. `restore` - Recovery
19. `orphans` - Quality

**Tier 4** (Nice to have):
20. `import github` - Developer use case
21. `export hugo` - Publishing
22. `export pdf` - Sharing
23. `embed` - Advanced search
24. `dedupe` - Cleanup

### Low Priority (Future)

**Tier 5** (Specialized):
25. `import roam` - Niche
26. `import evernote` - Legacy
27. `suggest` - AI augmentation
28. `merge` - Advanced
29. `split` - Advanced
30. `batch link` - Advanced

---

## Implementation Strategy

### Phase 1: Essential Tools (Q1 2025)
- `import markdown`
- `batch delete`
- `batch tag`
- `stats`
- `doctor`
- `backup`

**Goal**: Core functionality, safety, quality

---

### Phase 2: Integration (Q2 2025)
- `import cursor`
- `import obsidian`
- `export json`
- `graph`
- `lint`
- `watch`

**Goal**: Ecosystem integration, visualization

---

### Phase 3: Enhancement (Q3 2025)
- `import notion`
- `export obsidian`
- `batch rename/move`
- `timeline`
- `restore`
- `orphans`

**Goal**: Full-featured tool suite

---

### Phase 4: Advanced (Q4 2025)
- `embed`
- `suggest`
- `merge/split`
- Other advanced features

**Goal**: AI-powered knowledge management

---

## Success Metrics

**Adoption**:
- CLI tool usage vs. MCP tool usage
- Most popular commands
- User feedback

**Quality**:
- Bug reports per tool
- Data loss incidents (should be zero)
- Performance (execution time)

**Value**:
- User workflows enabled
- Time saved
- Pain points solved

---

## Conclusion

This roadmap provides a comprehensive vision for CLI tool expansion. Key insights:

1. **Import tools** are critical for adoption (migration paths)
2. **Batch operations** are essential for power users
3. **Analytics** help users understand their knowledge base
4. **Quality tools** (`doctor`, `lint`) prevent issues
5. **Backup** is non-negotiable for data safety

**Next steps**:
1. Prioritize based on user feedback
2. Implement Phase 1 (essential tools)
3. Iterate based on usage data

---

*Roadmap created: 2025-10-17*
*Last updated: 2025-10-17*

