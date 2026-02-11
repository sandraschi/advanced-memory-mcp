# Advanced Memory MCP - User Interaction Guide

## How to Use Advanced Memory Effectively

Advanced Memory is a powerful knowledge management system that works seamlessly with Claude to help you organize, discover, and enhance your knowledge. This guide shows you how to get the most out of its capabilities.

## Getting Started

### 1. Project Setup
First, ensure you have a project set up:
```
Check current project: "What project am I currently working in?"
Switch projects: "Switch to my 'research' project"
Create new project: "Create a new project called 'book-notes' in ~/Documents"
```

### 2. Basic Knowledge Operations
Start with simple note creation and management:
```
Create a note: "Create a note about machine learning basics"
Read content: "Show me my note about machine learning"
Search knowledge: "Find all notes related to neural networks"
```

### 3. Advanced Features
As you become comfortable, explore advanced capabilities:
```
Build context: "Give me context about my current research project"
Analyze content: "Summarize my thoughts on AI ethics"
Enhance writing: "Improve this note about quantum computing"
```

## Tool Categories & Use Cases

### 📝 Content Management (`adn_content`)
**Best for**: Creating, reading, editing, and organizing notes. **Primary tool for note operations. Available in all modes.**

#### Common Patterns:
```
"Create a note about machine learning basics"   -> adn_content(operation="write", identifier="...", content="...", folder="...")
"Read my meeting notes"                         -> adn_content(operation="read", identifier="...")
"Create a quick capture"                        -> adn_content(operation="quick", content="...")
"Create today's daily journal entry"            -> adn_content(operation="daily", content="...")
"Append to this note"                           -> adn_content(operation="edit", identifier="...", edit_operation="append", content="...")
"Find and replace in this note"                 -> adn_content(operation="edit", identifier="...", edit_operation="find_replace", find_text="...", content="...")
"Move this note to archive"                     -> adn_content(operation="move", identifier="...", destination_path="...")
```

#### Advanced Usage:
```
"Create a note with title 'Project Planning' and content about quarterly goals"
"Replace the summary section of my research note"
"View this note as a formatted artifact"
```

### 🔍 Search & Discovery (`adn_knowledge` search, `adn_research`)
**Best for**: Finding specific information across your knowledge base

#### Common Patterns:
```
"Search for notes about climate change"           -> adn_knowledge(operation="search", query="climate change")
"Show me notes mentioning 'machine learning'"     -> adn_knowledge(operation="search", query="machine learning")
"Search the web for AI news"                      -> adn_research(operation="web_search", query="...")
```

#### Advanced Usage:
```
"Find notes about quantum physics"                -> adn_knowledge(operation="search", query="quantum physics")
"Search arXiv for papers"                         -> adn_research(operation="arxiv", query="...")
```

### 🧭 Navigation & Context (`adn_knowledge` navigate, context, activity, list)
**Best for**: Understanding relationships and building context

#### Common Patterns:
```
"Show me recent activity in my knowledge base"    -> adn_knowledge(operation="activity", timeframe="1 week")
"Build context around my current project"         -> adn_knowledge(operation="context", identifier="...", depth=2)
"List all folders in my workspace"                -> adn_knowledge(operation="list", path="")
"Show me what's changed in the last 24 hours"     -> adn_knowledge(operation="activity", timeframe="1d")
```

#### Advanced Usage:
```
"Build a 2-level context network around 'machine learning'"
"Navigate from my main research note"
"List directory contents with depth"
```

### 🧠 Research & Analysis (`adn_research`)
**Best for**: Web search, RAG, document ingestion, LLM generation, research orchestration

#### Common Patterns:
```
"Search the web for machine learning transformers"
"Generate content about AI safety considerations"
"Create a research plan for quantum computing"
"Ingest this document into my knowledge base"
```

#### Advanced Usage:
```
"Search arXiv for neural network papers"
"Query my RAG knowledge base"
"Configure LLM provider and generate content"
```

### 📊 Project Management (`adn_project`)
**Best for**: Organizing work across multiple projects

#### Common Patterns:
```
"Switch to my 'writing' project"
"Show me project statistics"
"Create a new project for 'home-improvement'"
"List all available projects"
```

#### Advanced Usage:
```
"Set 'research-paper' as my default project"
"Show detailed statistics for the current project"
"Clean up unused project folders"
```

### 🎯 Claude Skills (`adn_skills`)
**Best for**: Creating reusable AI capabilities

#### Common Patterns:
```
"Create a new skill for code review"
"List all my available skills"
"Update the documentation skill"
"Delete unused skills"
```

#### Advanced Usage:
```
"Create a skill for technical writing with examples"
"Export my skills to Claude Skills format"
"Import skills from a GitHub repository"
"Validate all my skills for compatibility"
```

### 🤖 LLM Integration (`adn_llm`)
**Best for**: AI-powered content enhancement

#### Common Patterns:
```
"Switch to GPT-4 for content generation"
"Check current LLM provider status"
"List available LLM providers"
"Configure API keys for providers"
```

#### Advanced Usage:
```
"Set up multiple LLM providers with fallbacks"
"Test LLM provider connectivity"
"Compare response quality between providers"
```

### 📥 File Ingestion (`adn_inbox`)
**Best for**: Processing external documents and files

#### Common Patterns:
```
"Process all files in my inbox"
"Check inbox status and pending files"
"Convert PDF documents to notes"
"Import images with OCR processing"
```

#### Advanced Usage:
```
"Set up automatic file watching"
"Configure custom file processing rules"
"Batch process documents with metadata extraction"
```

### 📤 Data Import/Export (`adn_import`, `adn_export`)
**Best for**: Moving knowledge between systems

#### Import Patterns:
```
"Import my Evernote notes"
"Import from Notion workspace"
"Import Obsidian vault"
"Import from JSON backup"
```

#### Export Patterns:
```
"Export project to HTML documentation"
"Export to PDF with table of contents"
"Export to Docsify site"
"Create archive backup"
```

## Workflow Examples

### Research Project Workflow
```
1. adn_project(operation="create", name="quantum-research", path="...")
2. adn_content(operation="write", identifier="Quantum Entanglement Basics", content="...", folder="research")
3. adn_knowledge(operation="search", query="quantum physics")
4. adn_knowledge(operation="context", identifier="quantum computing", depth=2)
5. adn_research(operation="research_orchestrate", topic="quantum computing")
6. adn_import_export(operation="export", format="html", destination="...")
```

### Content Creation Workflow
```
1. adn_content(operation="write", identifier="Technical Article Outline", content="...", folder="drafts")
2. adn_knowledge(operation="search", query="related topics")
3. adn_content(operation="edit", identifier="...", edit_operation="replace_section", section="...", content="...")
4. adn_import_export(operation="export", format="pdf", destination="...")
```

## Best Practices

### Organization
- **Consistent Naming**: Use clear, descriptive titles
- **Meaningful Tags**: Apply relevant tags for discovery
- **Folder Structure**: Organize by project/topic
- **Regular Maintenance**: Review and update old content

### Search & Discovery
- **Specific Queries**: Use precise search terms
- **Tag Combinations**: Combine tags for focused results
- **Date Filters**: Limit searches by time periods
- **Context Building**: Use relationships for deeper understanding

### AI Enhancement
- **Iterative Improvement**: Use AI suggestions as starting points
- **Quality Review**: Always review AI-generated content
- **Custom Skills**: Create domain-specific enhancement tools
- **Feedback Loop**: Learn from successful AI interactions

### Performance
- **Selective Indexing**: Choose appropriate indexing settings
- **Regular Cleanup**: Remove unused or outdated content
- **Efficient Searches**: Use specific filters to reduce results
- **Batch Operations**: Use bulk tools for large-scale changes

## Troubleshooting

### Common Issues
- **No Results**: Check search terms and filters
- **Slow Performance**: Review indexing settings
- **Missing Content**: Verify file sync status
- **Tool Errors**: Check project configuration

### Getting Help
- **Tool Reference**: Use `adn_help` for detailed tool information
- **Status Check**: Use `adn_status` to verify system health
- **Logs**: Check error logs for detailed diagnostics
- **Documentation**: Refer to project documentation for advanced usage

---

Advanced Memory adapts to your workflow, becoming more helpful as you use it more. Start simple, explore features gradually, and build sophisticated knowledge management practices over time.
