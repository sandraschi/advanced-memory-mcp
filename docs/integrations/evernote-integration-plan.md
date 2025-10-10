# Evernote Integration Plan for Basic Memory

## Overview
Add comprehensive Evernote import/export capabilities to Basic Memory, allowing users to migrate from Evernote or work with Evernote-exported content.

## Evernote Export Format
Evernote primarily exports in **ENEX format** (.enex files):
- **ENEX (Evernote XML)**: Comprehensive XML format containing notes, metadata, tags, attachments
- **HTML Export**: Individual notes as HTML files (less common)
- **PDF Export**: Individual notes as PDF files

## Tools to Implement

### 1. load_evernote_export
**Purpose**: Import Evernote ENEX exports into Basic Memory

**Features**:
- Parse Evernote ENEX XML format
- Handle note content, titles, tags, and metadata
- Convert Evernote's HTML content to markdown
- Preserve creation/update dates
- Handle attachments and embedded images
- Support both single files and batch imports
- Convert Evernote notebooks to Basic Memory folders

**Input**: Path to .enex file or directory containing multiple .enex files
**Output**: Basic Memory entities with proper metadata

### 2. export_evernote_compatible
**Purpose**: Export Basic Memory content in Evernote-compatible format

**Features**:
- Generate ENEX XML format compatible with Evernote import
- Preserve entity metadata as Evernote note attributes
- Convert Basic Memory relations to Evernote tags
- Handle observations as note content sections
- Support folder structure conversion to Evernote notebooks

**Input**: Basic Memory entities to export
**Output**: .enex file that can be imported into Evernote

### 3. search_evernote_vault
**Purpose**: Search through Evernote export files

**Features**:
- Search across ENEX files and HTML exports
- Filter by notebooks, tags, dates
- Full-text search with highlighting
- Support for Evernote-specific metadata searches

**Input**: Search query with optional filters
**Output**: Matching Evernote notes with metadata

## Implementation Strategy

### Phase 1: Core Import (load_evernote_export)
1. Create ENEX XML parser
2. Handle basic note structure and content
3. Convert HTML to markdown
4. Add metadata preservation

### Phase 2: Enhanced Export (export_evernote_compatible)
1. Create ENEX XML generator
2. Handle entity relations and observations
3. Support attachments and media

### Phase 3: Search Integration (search_evernote_vault)
1. Implement ENEX file parsing for search
2. Add Evernote-specific filtering options

## Technical Considerations

### ENEX XML Structure
Evernote's ENEX format is complex XML with:
- `<note>` elements containing individual notes
- `<title>`, `<content>`, `<created>`, `<updated>` fields
- `<tag>` elements for categorization
- `<resource>` elements for attachments
- HTML content within `<content>` tags

### HTML to Markdown Conversion
Evernote content is HTML, requiring:
- Conversion of Evernote-specific HTML classes
- Handling of checklists, tables, and formatting
- Preservation of links and media references

### Attachment Handling
Evernote attachments in ENEX are base64 encoded and need:
- Decoding and saving as separate files
- Updating content references
- Maintaining file associations

## User Benefits
- **Migration Path**: Easy transition from Evernote to Basic Memory
- **Data Preservation**: Maintain note structure, tags, and attachments
- **Two-way Workflow**: Export back to Evernote if needed
- **Search Integration**: Find content across both systems

## Success Metrics
- Successful parsing of complex ENEX files
- Accurate HTML to markdown conversion
- Preservation of tags and metadata
- Seamless round-trip compatibility

## Risk Assessment
- **Medium**: ENEX XML parsing may require iterative refinement
- **Low**: Markdown export is straightforward
- **Medium**: Attachment handling adds complexity

## Timeline
- **Phase 1**: 3-4 days (core ENEX import functionality)
- **Phase 2**: 2-3 days (export capabilities)
- **Phase 3**: 1-2 days (search integration)
