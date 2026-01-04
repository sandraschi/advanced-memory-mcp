# Tool Coverage Audit - Portmanteau Completeness

**Audit Date**: 2024-10-20

**Goal**: Ensure ALL individual tools are covered by portmanteau tools.

---

## Individual Tools → Portmanteau Mapping

### ✅ Covered by `adn_content`
- `write_note` ✅
- `read_note` ✅
- `view_note` ✅
- `edit_note` ✅
- `move_note` ✅
- `delete_note` ✅
- `view_note_rendered` ⚠️ **MISSING - NEEDS ADD**

### ✅ Covered by `adn_project`
- `create_memory_project` ✅
- `switch_project` ✅
- `delete_project` ✅
- `set_default_project` ✅
- `get_current_project` ✅
- `list_memory_projects` ✅

### ✅ Covered by `adn_export`
- `export_pandoc` ✅
- `export_docsify` ✅
- `export_html_notes` ✅
- `export_joplin_notes` ✅
- `make_pdf_book` ✅
- `export_to_archive` ✅

### ✅ Covered by `adn_import`
- `load_obsidian_vault` ✅
- `load_joplin_vault` ✅
- `load_notion_export` ✅
- `load_evernote_export` ✅
- `import_from_archive` ✅
- `load_obsidian_canvas` ✅

### ✅ Covered by `adn_search`
- `search_notes` ✅
- `search_obsidian_vault` ✅
- `search_joplin_vault` ✅
- `search_notion_vault` ✅
- `search_evernote_vault` ✅

### ✅ Covered by `adn_knowledge`
- `knowledge_operations` ✅
- `research_orchestrator` ✅

### ✅ Covered by `adn_navigation`
- `build_context` ✅
- `recent_activity` ✅
- `list_directory` ✅
- `status` ✅
- `sync_status` ✅

### ✅ Covered by `adn_editor`
- `edit_in_notepadpp` ✅
- `import_from_notepadpp` ✅
- `typora_control` ✅
- `canvas` ✅
- `read_content` ✅

### ✅ Covered by `adn_inbox`
- Inbox operations (no individual tools) ✅

### ✅ Covered by `adn_zettelmaker`
- Zettelkasten generation (no individual tools) ✅

### ⚠️ Standalone Tools (NOT in portmanteau)
- `help` - Meta tool, should remain standalone
- `view_note_rendered` - **NEEDS TO BE ADDED TO ADN_CONTENT**

---

## Action Required

### 1. Add `view_note_rendered` to `adn_content`

**Current `adn_content` operations**:
- `write`
- `read`
- `view`
- `edit`
- `move`
- `delete`

**Need to add**:
- `view_rendered` - View note with rendered Mermaid diagrams

### 2. Update Documentation

**`adn_content` description should mention**:
- Consolidates: write_note, read_note, view_note, **view_note_rendered**, edit_note, move_note, delete_note

---

## Verification

After implementation:

**Portmanteau tools (11)**:
1. `adn_content` (7 operations) ← **Add view_rendered**
2. `adn_project` (8 operations)
3. `adn_zettelmaker` (6 operations)
4. `adn_inbox` (4 operations)
5. `adn_export` (9 operations)
6. `adn_import` (6 operations)
7. `adn_search` (5 operations)
8. `adn_knowledge` (9 operations)
9. `adn_navigation` (5 operations)
10. `adn_editor` (5 operations)
11. `help` (standalone meta-tool)

**Total individual tools covered**: 46
**Total standalone**: 1 (help)
**Total**: 47 tools

✅ **100% coverage** (after adding view_rendered to adn_content)
