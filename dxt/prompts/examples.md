# Advanced Memory MCP - Usage Examples

## 📝 Content Management Examples

### Basic Note Creation
```python
# Simple note
adn_content("write", identifier="Simple Note", content="This is a simple note.", folder="examples")

# Note with tags
adn_content("write", identifier="Tagged Note", content="# Tagged Note\n\nThis note has tags.", folder="examples", tags=["example", "demo"])

# Complex note with structure
adn_content("write", 
    identifier="Project Planning", 
    content="""
# Project Planning

## Overview
This is a complex project planning document.

## Goals
- [ ] Complete feature A
- [ ] Test feature B
- [ ] Deploy to production

## Timeline
- Week 1: Design
- Week 2: Development
- Week 3: Testing
- Week 4: Deployment

## Resources
- [[Team Member 1]] - Developer
- [[Team Member 2]] - Designer
- [[External Consultant]] - Advisor
""",
    folder="projects",
    tags=["planning", "urgent", "2024"]
)
```

### Reading and Viewing Notes
```python
# Read note content
content = adn_content("read", identifier="Project Planning")

# View formatted note
formatted = adn_content("view", identifier="Project Planning")

# Read with pagination
page1 = adn_content("read", identifier="Long Document", page=1, page_size=10)
```

### Editing Notes
```python
# Append content
adn_content("edit", 
    identifier="Project Planning", 
    edit_operation="append", 
    content="\n\n## Update 2024-01-15\n- Completed: Feature A design\n- Next: Begin development"
)

# Prepend content
adn_content("edit", 
    identifier="Project Planning", 
    edit_operation="prepend", 
    content="# UPDATED: "
)

# Find and replace
adn_content("edit", 
    identifier="Project Planning", 
    edit_operation="find_replace", 
    find_text="Week 1: Design",
    content="Week 1: Design (COMPLETED)",
    expected_replacements=1
)

# Replace section
adn_content("edit", 
    identifier="Project Planning", 
    edit_operation="replace_section", 
    section="## Timeline",
    content="## Timeline\n- Week 1: Design ✅\n- Week 2: Development (In Progress)\n- Week 3: Testing\n- Week 4: Deployment"
)
```

### Moving and Deleting Notes
```python
# Move note
adn_content("move", 
    identifier="Project Planning", 
    destination_path="archive/completed-projects/project-planning.md"
)

# Delete note
adn_content("delete", identifier="Old Meeting Notes")
```

## 🗂️ Project Management Examples

### Project Operations
```python
# List all projects
projects = adn_project("list")

# Create new project
adn_project("create", 
    project_name="personal-notes", 
    project_path="/Users/me/Documents/personal-notes",
    set_default=False
)

# Switch to project
adn_project("switch", project_name="personal-notes")

# Set default project
adn_project("set_default", project_name="personal-notes")

# Get current project info
current = adn_project("get_current")

# Delete project (removes from management, keeps files)
adn_project("delete", project_name="old-project")
```

## 📤 Export Examples

### Document Export
```python
# Export to PDF
adn_export("pandoc", 
    export_path="output/project-docs.pdf", 
    format_type="pdf", 
    source_folder="/projects",
    toc=True,
    highlight_style="tango"
)

# Export to HTML
adn_export("html", 
    export_path="html-docs/", 
    source_folder="/projects",
    include_index=True
)

# Export to Word document
adn_export("pandoc", 
    export_path="project-report.docx", 
    format_type="docx", 
    source_folder="/projects"
)
```

### Website Generation
```python
# Create Docsify website
adn_export("docsify", 
    export_path="website/", 
    source_folder="/projects",
    site_title="My Knowledge Base",
    site_description="Personal knowledge management system",
    enable_pagination=True,
    enable_toc=True,
    enable_theme_toggle=True
)
```

### Book Creation
```python
# Create PDF book
adn_export("pdf_book", 
    book_title="My Research Collection", 
    source_folder="/research",
    author="Your Name",
    tag_filter="research",
    toc_depth=3,
    paper_size="a4"
)
```

### Archive Creation
```python
# Create backup archive
adn_export("archive", 
    archive_path="backup-2024-01-15.zip", 
    include_projects=["work-notes", "personal-notes"],
    since_date="30d",
    compress=True
)
```

## 📥 Import Examples

### Obsidian Import
```python
# Import Obsidian vault
adn_import("obsidian", 
    source_path="/path/to/obsidian-vault", 
    destination_folder="imported/obsidian",
    preserve_structure=True,
    convert_links=True,
    include_attachments=False
)
```

### Joplin Import
```python
# Import Joplin export
adn_import("joplin", 
    source_path="/path/to/joplin-export", 
    destination_folder="imported/joplin",
    preserve_structure=True,
    convert_links=True,
    skip_existing=True
)
```

### Notion Import
```python
# Import Notion export
adn_import("notion", 
    source_path="/path/to/notion-export.zip", 
    destination_folder="imported/notion",
    preserve_hierarchy=True
)
```

### Evernote Import
```python
# Import Evernote export
adn_import("evernote", 
    source_path="/path/to/notes.enex", 
    destination_folder="imported/evernote",
    preserve_notebooks=True,
    include_attachments=True
)
```

### Archive Import
```python
# Import from archive
adn_import("archive", 
    source_path="backup.zip", 
    destination_folder="restored/",
    restore_mode="merge",
    backup_existing=True
)
```

## 🔍 Search Examples

### Basic Search
```python
# Search notes
results = adn_search("notes", 
    query="machine learning", 
    search_type="full_text",
    page=1, 
    page_size=10
)

# Search by tags
results = adn_search("notes", 
    query="tag:urgent", 
    search_type="tags",
    page=1, 
    page_size=5
)

# Search by identifier
results = adn_search("notes", 
    query="Project Planning", 
    search_type="identifier"
)
```

### External System Search
```python
# Search Obsidian vault
results = adn_search("obsidian", 
    query="project notes", 
    source_path="/path/to/vault",
    max_results=20
)

# Search Joplin export
results = adn_search("joplin", 
    query="meeting", 
    source_path="/path/to/joplin-export",
    search_type="combined",
    include_content=True
)

# Search Notion export
results = adn_search("notion", 
    query="research", 
    source_path="/path/to/notion-export",
    case_sensitive=False
)
```

## 🧠 Knowledge Management Examples

### Tag Analytics
```python
# Analyze tag usage
analytics = adn_knowledge("tag_analytics", 
    action={"analyze_usage": True}
)

# Consolidate similar tags
adn_knowledge("consolidate_tags", 
    semantic_groups=[
        ["mcp", "mcp-server", "model-context-protocol"],
        ["ai", "artificial-intelligence", "machine-learning"],
        ["notes", "note-taking", "knowledge-management"]
    ]
)
```

### Content Validation
```python
# Validate content quality
validation = adn_knowledge("validate_content", 
    checks=["broken_links", "formatting", "duplicates"],
    limit=100
)

# Find duplicates
duplicates = adn_knowledge("find_duplicates", 
    limit=50
)
```

### Research Orchestration
```python
# Create research plan
plan = adn_knowledge("research_plan", 
    topic="quantum computing applications", 
    research_type="technical"
)

# Generate research questions
questions = adn_knowledge("research_questions", 
    topic="quantum computing applications", 
    research_type="technical"
)

# Get research methodology
methodology = adn_knowledge("research_methodology", 
    topic_type="technical"
)

# Design note blueprint
blueprint = adn_knowledge("note_blueprint", 
    research_type="analysis"
)
```

### Bulk Operations
```python
# Bulk update tags
adn_knowledge("bulk_update", 
    filters={"tags": ["draft"]}, 
    action={"add_tags": ["reviewed"]},
    limit=100
)

# Get project statistics
stats = adn_knowledge("project_stats", 
    filters={"project": "work-notes"}
)
```

## 🧭 Navigation Examples

### Context Building
```python
# Build context from memory URL
context = adn_navigation("build_context", 
    url="memory://projects/ai", 
    depth=2, 
    timeframe="7d",
    max_related=10
)

# Build context from folder pattern
context = adn_navigation("build_context", 
    url="memory://research/*", 
    depth=1, 
    timeframe="30d"
)
```

### Recent Activity
```python
# Recent activity today
recent = adn_navigation("recent_activity", 
    timeframe="today", 
    type_filter="notes",
    page=1, 
    page_size=10
)

# Recent activity this week
recent = adn_navigation("recent_activity", 
    timeframe="7d", 
    type_filter=["notes", "projects"]
)
```

### Directory Listing
```python
# List directory contents
contents = adn_navigation("list_directory", 
    dir_name="/projects", 
    depth=2,
    file_name_glob="*.md"
)

# List with filtering
contents = adn_navigation("list_directory", 
    dir_name="/research", 
    depth=1,
    file_name_glob="*2024*"
)
```

### System Status
```python
# Basic status
status = adn_navigation("status", level="basic")

# Detailed status
status = adn_navigation("status", 
    level="detailed", 
    focus="health"
)

# Sync status
sync_status = adn_navigation("sync_status")
```

## ✏️ Editor Integration Examples

### Notepad++ Integration
```python
# Edit note in Notepad++
adn_editor("notepadpp_edit", 
    note_identifier="Meeting Notes", 
    workspace_path="temp/notepadpp-workspace",
    create_backup=True
)

# Import edited content back
adn_editor("notepadpp_import", 
    note_identifier="Meeting Notes", 
    workspace_path="temp/notepadpp-workspace",
    keep_workspace=False
)
```

### Typora Control
```python
# Export current document
adn_editor("typora_control", 
    typora_operation="export", 
    typora_format="pdf", 
    output_path="export.pdf"
)

# Open file in Typora
adn_editor("typora_control", 
    typora_operation="open", 
    file_path="/path/to/document.md"
)

# Get document content
content = adn_editor("typora_control", 
    typora_operation="get_content"
)

# Insert text
adn_editor("typora_control", 
    typora_operation="insert_text", 
    text="## New Section\n\nContent here"
)
```

### Canvas Creation
```python
# Create simple canvas
adn_editor("canvas_create", 
    nodes=[
        {"id": "main", "text": "Main Topic", "x": 100, "y": 100},
        {"id": "sub1", "text": "Sub Topic 1", "x": 200, "y": 200},
        {"id": "sub2", "text": "Sub Topic 2", "x": 200, "y": 300}
    ],
    edges=[
        {"from": "main", "to": "sub1"},
        {"from": "main", "to": "sub2"}
    ],
    title="My Knowledge Map",
    folder="visualizations"
)
```

### Content Reading
```python
# Read raw file content
content = adn_editor("read_content", 
    path="/path/to/document.md"
)

# Read with specific encoding
content = adn_editor("read_content", 
    path="/path/to/document.txt",
    encoding="utf-8"
)
```

## 🔄 Complete Workflow Examples

### Daily Knowledge Management
```python
from datetime import date

# 1. Check recent activity
recent = adn_navigation("recent_activity", timeframe="today")

# 2. Create daily note
adn_content("write", 
    identifier=f"Daily Note {date.today()}", 
    content=f"""
# Daily Note {date.today()}

## Tasks
- [ ] Review yesterday's work
- [ ] Plan today's priorities
- [ ] Update project status

## Notes
- Note 1
- Note 2

## Reflection
What went well today?
What could be improved?
""", 
    folder="daily",
    tags=["daily", "planning"]
)

# 3. Search for relevant information
results = adn_search("notes", query="project status", page=1, page_size=5)

# 4. Update project notes
adn_content("edit", 
    identifier="Project Status", 
    edit_operation="append", 
    content=f"\n\n## {date.today()}\n- Reviewed: Yesterday's work\n- Planned: Today's priorities\n- Updated: Project status"
)
```

### Research Project Workflow
```python
# 1. Create research plan
plan = adn_knowledge("research_plan", 
    topic="artificial intelligence ethics", 
    research_type="academic"
)

# 2. Generate research questions
questions = adn_knowledge("research_questions", 
    topic="artificial intelligence ethics", 
    research_type="academic"
)

# 3. Create research notes for each question
for i, question in enumerate(questions):
    adn_content("write", 
        identifier=f"Research Q{i+1}: {question}", 
        content=f"""
# Research Question: {question}

## Hypothesis
Initial hypothesis here...

## Research Notes
- Note 1
- Note 2

## Sources
- Source 1
- Source 2

## Analysis
Analysis of findings...

## Conclusions
Preliminary conclusions...
""", 
        folder="research",
        tags=["research", "ai-ethics", f"question-{i+1}"]
    )

# 4. Create overview note
adn_content("write", 
    identifier="AI Ethics Research Overview", 
    content="""
# AI Ethics Research Overview

## Research Questions
{questions_list}

## Progress
- [ ] Question 1: Research phase
- [ ] Question 2: Analysis phase
- [ ] Question 3: Writing phase

## Next Steps
1. Complete literature review
2. Analyze findings
3. Write conclusions
""".format(questions_list="\n".join([f"- {q}" for q in questions])),
    folder="research",
    tags=["research", "overview", "ai-ethics"]
)

# 5. Export research as PDF book
adn_export("pdf_book", 
    book_title="AI Ethics Research Collection", 
    source_folder="/research",
    author="Researcher Name",
    tag_filter="research",
    toc_depth=2
)
```

### Project Management Workflow
```python
# 1. Create project
adn_project("create", 
    project_name="new-product-launch", 
    project_path="/Users/me/Documents/projects/new-product-launch"
)

# 2. Switch to project
adn_project("switch", project_name="new-product-launch")

# 3. Create project structure
adn_content("write", 
    identifier="Project Overview", 
    content="""
# New Product Launch - Project Overview

## Goals
- Launch new product by Q2 2024
- Achieve 10K users in first month
- Establish market presence

## Timeline
- Q1 2024: Development
- Q2 2024: Testing and Launch
- Q3 2024: Marketing and Growth

## Team
- [[Product Manager]] - Project lead
- [[Developer Team]] - Technical implementation
- [[Marketing Team]] - Launch strategy
- [[Design Team]] - User experience

## Resources
- Budget: $100K
- Timeline: 6 months
- Team: 8 people
""", 
    folder="docs",
    tags=["project", "overview", "2024"]
)

adn_content("write", 
    identifier="Meeting Notes Template", 
    content="""
# Meeting Notes - {date}

## Attendees
- Person 1
- Person 2

## Agenda
1. Topic 1
2. Topic 2

## Discussion
Key discussion points...

## Decisions
- Decision 1
- Decision 2

## Action Items
- [ ] Task 1 - Assignee - Due Date
- [ ] Task 2 - Assignee - Due Date

## Next Meeting
- Date: TBD
- Agenda: TBD
""", 
    folder="meetings",
    tags=["template", "meetings"]
)

# 4. Create initial meeting notes
adn_content("write", 
    identifier="Kickoff Meeting 2024-01-15", 
    content="""
# Kickoff Meeting - 2024-01-15

## Attendees
- [[Product Manager]] - Project lead
- [[Developer Team Lead]] - Technical lead
- [[Marketing Manager]] - Launch strategy

## Agenda
1. Project overview and goals
2. Timeline and milestones
3. Team roles and responsibilities
4. Next steps

## Discussion
- Discussed project scope and requirements
- Reviewed timeline and identified potential risks
- Clarified team roles and communication channels

## Decisions
- Use Agile methodology with 2-week sprints
- Weekly team standups on Mondays
- Monthly stakeholder reviews

## Action Items
- [ ] Create detailed project plan - Product Manager - 2024-01-22
- [ ] Set up development environment - Developer Team Lead - 2024-01-20
- [ ] Create marketing strategy draft - Marketing Manager - 2024-01-25

## Next Meeting
- Date: 2024-01-22
- Agenda: Review project plan and development setup
""", 
    folder="meetings",
    tags=["meeting", "kickoff", "2024-01-15"]
)

# 5. Export project documentation
adn_export("docsify", 
    export_path="project-docs/", 
    site_title="New Product Launch - Documentation",
    source_folder="/docs"
)
```

---

*These examples demonstrate the full range of Advanced Memory MCP capabilities. Start with simple operations and gradually incorporate more advanced features as you become familiar with the system.*
