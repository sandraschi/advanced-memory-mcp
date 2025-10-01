# Advanced Memory and Claude Integration

This document explains how Advanced Memory interacts with Claude and the structure of the depot system.

## Table of Contents
- [Overview](#overview)
- [Advanced Memory Projects](#advanced-memory-projects)
  - [Project Lifecycle](#project-lifecycle)
  - [Project Structure](#project-structure)
- [Depot System](#depot-system)
  - [Depot Structure](#depot-structure)
  - [Folder Organization](#folder-organization)
- [Claude Integration](#claude-integration)
  - [MCP Tools for Claude](#mcp-tools-for-claude)
  - [Knowledge Graph Navigation](#knowledge-graph-navigation)
  - [Context Management](#context-management)
- [Best Practices](#best-practices)

## Overview

Advanced Memory is a sophisticated knowledge management system that enables seamless interaction between Claude and your personal or project knowledge base. It extends the capabilities of the original Basic Memory with enhanced project management, advanced search, and deeper Claude integration.

## Advanced Memory Projects

### Project Lifecycle

1. **Project Creation**
   - Projects can be created via CLI: `advanced-memory create-project <name> --path <path>`
   - Or through Claude using the `create_memory_project` MCP tool
   - Each project gets its own database and search index

2. **Project Activation**
   - The active project determines which knowledge base Claude can access
   - Switch projects with `advanced-memory switch <project-name>` or via Claude
   - The current project is maintained in the MCP session

3. **Project Synchronization**
   - Projects sync markdown files with the knowledge graph
   - Run `advanced-memory sync` to perform a one-time sync
   - Use `advanced-memory sync --watch` for continuous syncing

### Project Structure

Each project contains:

```
project-root/
├── .basic-memory/       # Project metadata and database
│   ├── memory.db        # SQLite database
│   └── search_index/    # Full-text search index
├── notes/               # Default directory for markdown files
├── assets/              # Media and other files
└── .gitignore          # Standard git ignore file
```

## Depot System

The depot is the central storage system for Advanced Memory projects, designed to handle knowledge in a structured yet flexible way.

### Depot Structure

```
~/.advanced-memory/         # Global configuration
├── config.toml         # User preferences and default project
├── projects/           # Managed projects
│   └── project1/       # Individual project
│       ├── memory.db   # Project database
│       └── index/      # Search index
└── trash/              # Safe deletion storage
```

### Folder Organization

Advanced Memory uses a flexible folder system that balances structure and ease of use:

1. **Automatic Organization**
   - Files can be automatically organized by type, date, or tags
   - Custom folder templates can be defined in project settings

2. **Smart Folders**
   - Virtual folders that dynamically collect content based on queries
   - Example: `recent/` shows recently modified files
   - Example: `from:claude/` shows files created through Claude

3. **Custom Organization**
   - Users can create their own folder structure
   - The system maintains links and relationships regardless of physical location

## Claude Integration

### MCP Tools for Claude

Advanced Memory exposes several MCP tools that Claude can use:

1. **Content Management**
   - `write_note()`: Create or update markdown notes
   - `read_note()`: Read notes with knowledge graph awareness
   - `edit_note()`: Make incremental changes to notes
   - `move_note()`: Reorganize notes while preserving relationships

2. **Project Management**
   - `list_memory_projects()`: Show available projects
   - `switch_project()`: Change the active project
   - `create_memory_project()`: Start a new project
   - `sync_status()`: Check sync status

3. **Knowledge Navigation**
   - `build_context()`: Load relevant context from the knowledge graph
   - `recent_activity()`: Find recently updated information
   - `list_directory()`: Browse the project structure

### Knowledge Graph Navigation

Claude can navigate the knowledge graph using:

1. **Memory URLs**
   - `memory://project/note-title` - Direct link to a note
   - `memory://search?q=query` - Search results
   - `memory://recent/1d` - Recent changes

2. **Graph Traversal**
   - Follow links between notes
   - Explore related concepts
   - Discover connections between ideas

### Context Management

Advanced Memory helps Claude maintain context by:

1. **Session Persistence**
   - Project context is maintained across conversations
   - Recent interactions are automatically linked

2. **Automatic Context Loading**
   - Relevant notes are pre-loaded based on conversation topic
   - Related information is suggested as the conversation progresses

3. **Context Summarization**
   - Long conversations are summarized and linked
   - Important details are extracted and stored as observations

## Best Practices

1. **For Users**
   - Keep project scopes focused and well-defined
   - Use meaningful titles and tags for notes
   - Regularly review and organize your knowledge base

2. **For Claude**
   - Always check the current project context
   - Use the full capabilities of the MCP tools
   - Maintain clean, well-structured markdown
   - Create meaningful links between related concepts

3. **For Developers**
   - Follow the project's code style guidelines
   - Maintain backward compatibility in the MCP API
   - Document new features and changes

## Troubleshooting

1. **Sync Issues**
   - Run `advanced-memory sync --force` to rebuild indexes
   - Check file permissions in the project directory

2. **Performance Problems**
   - Large projects may need optimization
   - Consider splitting very large projects

3. **Integration Problems**
   - Ensure the MCP server is running
   - Check project configuration files for errors
