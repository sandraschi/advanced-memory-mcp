
# Comprehensive CRUD and Search Test Report

**Generated:** 2026-04-26T05:19:20.019294
**Duration:** 166.19 seconds
**Total Tests:** 35
**Passed:** 16 (45.7%)
**Failed:** 19 (54.3%)

## Summary

**19 TEST(S) FAILED**

## Test Results by Category

### CRUD
**Passed:** 1/14

- [FAIL] CRUD - Create Basic Note
  - Error: assert ('Created note' in {'success': True, 'operation': 'write', 'summary': "Note 'Test Note Basic' updated successfully", 'result': {'title': 'Test Note Basic', 'permalink': 'test/crud/test-note-basic', 'folder': 'test/crud', 'observations_count': 0, 'relations_count': 0, 'resolved_relations': 0, 'unresolved_relations': 0, 'tags': ['test', 'crud']}, 'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions']} or 'Updated note' in {'success': True, 'operation': 'write', 'summary': "Note 'Test Note Basic' updated successfully", 'result': {'title': 'Test Note Basic', 'permalink': 'test/crud/test-note-basic', 'folder': 'test/crud', 'observations_count': 0, 'relations_count': 0, 'resolved_relations': 0, 'unresolved_relations': 0, 'tags': ['test', 'crud']}, 'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions']})
- [FAIL] CRUD - Create Note with Metadata
  - Error: 'dict' object has no attribute 'lower'
- [FAIL] CRUD - Read Note by Title
  - Error: assert 'Read Test' in {'success': True, 'operation': 'read', 'summary': "Read note 'Read Test Note'", 'result': {'content': '---\r\ntitle: Read Test Note\r\ntype: note\r\npermalink: test/crud/read-test-note\r\ntags:\r\n- read-test\r\n---\r\n\r\n# Read Test\r\n\r\nThis note will be read.'}}
- [FAIL] CRUD - Read Note by Permalink
  - Error: assert 'Permalink Test' in {'success': True, 'operation': 'read', 'summary': "Read note 'test/crud/permalink-read-test'", 'result': {'content': '---\r\ntitle: Permalink Read Test\r\ntype: note\r\npermalink: test/crud/permalink-read-test\r\ntags:\r\n- permalink-test\r\n---\r\n\r\n# Permalink Test\r\n\r\nReading by permalink.'}}
- [FAIL] CRUD - Update Note Append
  - Error: assert ('Updated' in {'success': True, 'operation': 'edit_note', 'summary': '# Edited note (append)\nproject: test-project\nfile_path: test/crud/Update_Append_Test.md\npermalink: test/crud/update-append-test\nchecksum: e986056f\noperation: Added 5 lines to end of note', 'note': 'Update Append Test', 'permalink': 'test/crud/update-append-test', 'file_path': 'test/crud/Update_Append_Test.md', 'observations_count': 0, 'relations_count': 0, 'content': '\n\n## Added Section\n\nThis was appended.'} or 'Edit' in {'success': True, 'operation': 'edit_note', 'summary': '# Edited note (append)\nproject: test-project\nfile_path: test/crud/Update_Append_Test.md\npermalink: test/crud/update-append-test\nchecksum: e986056f\noperation: Added 5 lines to end of note', 'note': 'Update Append Test', 'permalink': 'test/crud/update-append-test', 'file_path': 'test/crud/Update_Append_Test.md', 'observations_count': 0, 'relations_count': 0, 'content': '\n\n## Added Section\n\nThis was appended.'})
- [FAIL] CRUD - Update Find Replace Simple
  - Error: assert ('Updated' in {'success': True, 'operation': 'edit_note', 'summary': '# Edited note (find_replace)\nproject: test-project\nfile_path: test/crud/Find_Replace_Test.md\npermalink: test/crud/find-replace-test\nchecksum: b8618b75\noperation: Find and replace operation completed', 'note': 'Find Replace Test', 'permalink': 'test/crud/find-replace-test', 'file_path': 'test/crud/Find_Replace_Test.md', 'observations_count': 0, 'relations_count': 0, 'content': 'jason'} or 'Edit' in {'success': True, 'operation': 'edit_note', 'summary': '# Edited note (find_replace)\nproject: test-project\nfile_path: test/crud/Find_Replace_Test.md\npermalink: test/crud/find-replace-test\nchecksum: b8618b75\noperation: Find and replace operation completed', 'note': 'Find Replace Test', 'permalink': 'test/crud/find-replace-test', 'file_path': 'test/crud/Find_Replace_Test.md', 'observations_count': 0, 'relations_count': 0, 'content': 'jason'})
- [FAIL] CRUD - Update Find Replace Not Regex
  - Error: assert 'Version 1.2.4' in {'success': True, 'operation': 'read', 'summary': "Read note 'Find Replace Regex Test'", 'result': {'content': '---\r\ntitle: Find Replace Regex Test\r\ntype: note\r\npermalink: test/crud/find-replace-regex-test\r\ntags:\r\n- regex-test\r\n---\r\n\r\n# Regex Test\r\n\r\nVersion 1.2.4 and version 2.3.4 are mentioned.'}}
- [FAIL] CRUD - Update Note Prepend
  - Error: assert ('Updated' in {'success': True, 'operation': 'edit_note', 'summary': '# Edited note (prepend)\nproject: test-project\nfile_path: test/crud/Update_Prepend_Test.md\npermalink: test/crud/update-prepend-test\nchecksum: f8fe6517\noperation: Added 5 lines to beginning of note', 'note': 'Update Prepend Test', 'permalink': 'test/crud/update-prepend-test', 'file_path': 'test/crud/Update_Prepend_Test.md', 'observations_count': 0, 'relations_count': 0, 'content': '## Prepended Section\n\nThis was prepended.\n\n'} or 'Edit' in {'success': True, 'operation': 'edit_note', 'summary': '# Edited note (prepend)\nproject: test-project\nfile_path: test/crud/Update_Prepend_Test.md\npermalink: test/crud/update-prepend-test\nchecksum: f8fe6517\noperation: Added 5 lines to beginning of note', 'note': 'Update Prepend Test', 'permalink': 'test/crud/update-prepend-test', 'file_path': 'test/crud/Update_Prepend_Test.md', 'observations_count': 0, 'relations_count': 0, 'content': '## Prepended Section\n\nThis was prepended.\n\n'})
- [FAIL] CRUD - Update Replace Section
  - Error: assert ('Updated' in {'success': True, 'operation': 'edit_note', 'summary': "# Edited note (replace_section)\nproject: test-project\nfile_path: test/crud/Replace_Section_Test.md\npermalink: test/crud/replace-section-test\nchecksum: beb18052\noperation: Replaced content under section '## Old Section'", 'note': 'Replace Section Test', 'permalink': 'test/crud/replace-section-test', 'file_path': 'test/crud/Replace_Section_Test.md', 'observations_count': 0, 'relations_count': 0, 'content': '\n\nNew content here.'} or 'Edit' in {'success': True, 'operation': 'edit_note', 'summary': "# Edited note (replace_section)\nproject: test-project\nfile_path: test/crud/Replace_Section_Test.md\npermalink: test/crud/replace-section-test\nchecksum: beb18052\noperation: Replaced content under section '## Old Section'", 'note': 'Replace Section Test', 'permalink': 'test/crud/replace-section-test', 'file_path': 'test/crud/Replace_Section_Test.md', 'observations_count': 0, 'relations_count': 0, 'content': '\n\nNew content here.'})
- [FAIL] CRUD - Update Tags Add
  - Error: assert ('Tag Edit Complete' in {'success': True, 'operation': 'edit_tags', 'summary': '# Tag Edit Complete\n\n**Project:** test-project\n**Note:** Tag Add Test\n**Permalink:** test/crud/tag-add-test\n\n## Operation\n**Action:** add\n**Summary:** Added 2 tag(s): added, test-tag\n\n## Tags\n**Before:** initial\n**After:** initial, added, test-tag\n**Total tags:** 3', 'note': 'Tag Add Test', 'permalink': 'test/crud/tag-add-test', 'tags_before': ['initial'], 'tags_after': ['initial', 'added', 'test-tag']} or 'Added' in {'success': True, 'operation': 'edit_tags', 'summary': '# Tag Edit Complete\n\n**Project:** test-project\n**Note:** Tag Add Test\n**Permalink:** test/crud/tag-add-test\n\n## Operation\n**Action:** add\n**Summary:** Added 2 tag(s): added, test-tag\n\n## Tags\n**Before:** initial\n**After:** initial, added, test-tag\n**Total tags:** 3', 'note': 'Tag Add Test', 'permalink': 'test/crud/tag-add-test', 'tags_before': ['initial'], 'tags_after': ['initial', 'added', 'test-tag']})
- [FAIL] CRUD - Update Tags Remove
  - Error: assert ('Tag Edit Complete' in {'success': True, 'operation': 'edit_tags', 'summary': '# Tag Edit Complete\n\n**Project:** test-project\n**Note:** Tag Remove Test\n**Permalink:** test/crud/tag-remove-test\n\n## Operation\n**Action:** remove\n**Summary:** Removed 1 tag(s): remove-me\n\n## Tags\n**Before:** keep-me, remove-me\n**After:** keep-me\n**Total tags:** 1', 'note': 'Tag Remove Test', 'permalink': 'test/crud/tag-remove-test', 'tags_before': ['keep-me', 'remove-me'], 'tags_after': ['keep-me']} or 'Removed' in {'success': True, 'operation': 'edit_tags', 'summary': '# Tag Edit Complete\n\n**Project:** test-project\n**Note:** Tag Remove Test\n**Permalink:** test/crud/tag-remove-test\n\n## Operation\n**Action:** remove\n**Summary:** Removed 1 tag(s): remove-me\n\n## Tags\n**Before:** keep-me, remove-me\n**After:** keep-me\n**Total tags:** 1', 'note': 'Tag Remove Test', 'permalink': 'test/crud/tag-remove-test', 'tags_before': ['keep-me', 'remove-me'], 'tags_after': ['keep-me']})
- [FAIL] CRUD - Update Tags Replace
  - Error: assert ('Tag Edit Complete' in {'success': True, 'operation': 'edit_tags', 'summary': '# Tag Edit Complete\n\n**Project:** test-project\n**Note:** Tag Replace Test\n**Permalink:** test/crud/tag-replace-test\n\n## Operation\n**Action:** replace\n**Summary:** Replaced all tags with 2 new tag(s)\n\n## Tags\n**Before:** old-tag1, old-tag2\n**After:** new-tag1, new-tag2\n**Total tags:** 2', 'note': 'Tag Replace Test', 'permalink': 'test/crud/tag-replace-test', 'tags_before': ['old-tag1', 'old-tag2'], 'tags_after': ['new-tag1', 'new-tag2']} or 'Replaced' in {'success': True, 'operation': 'edit_tags', 'summary': '# Tag Edit Complete\n\n**Project:** test-project\n**Note:** Tag Replace Test\n**Permalink:** test/crud/tag-replace-test\n\n## Operation\n**Action:** replace\n**Summary:** Replaced all tags with 2 new tag(s)\n\n## Tags\n**Before:** old-tag1, old-tag2\n**After:** new-tag1, new-tag2\n**Total tags:** 2', 'note': 'Tag Replace Test', 'permalink': 'test/crud/tag-replace-test', 'tags_before': ['old-tag1', 'old-tag2'], 'tags_after': ['new-tag1', 'new-tag2']})
- [FAIL] CRUD - Update Tags Clear
  - Error: assert ('Tag Edit Complete' in {'success': True, 'operation': 'edit_tags', 'summary': '# Tag Edit Complete\n\n**Project:** test-project\n**Note:** Tag Clear Test\n**Permalink:** test/crud/tag-clear-test\n\n## Operation\n**Action:** clear\n**Summary:** Cleared all 3 tag(s)\n\n## Tags\n**Before:** tag1, tag2, tag3\n**After:** (no tags)\n**Total tags:** 0', 'note': 'Tag Clear Test', 'permalink': 'test/crud/tag-clear-test', 'tags_before': ['tag1', 'tag2', 'tag3'], 'tags_after': []} or 'Cleared' in {'success': True, 'operation': 'edit_tags', 'summary': '# Tag Edit Complete\n\n**Project:** test-project\n**Note:** Tag Clear Test\n**Permalink:** test/crud/tag-clear-test\n\n## Operation\n**Action:** clear\n**Summary:** Cleared all 3 tag(s)\n\n## Tags\n**Before:** tag1, tag2, tag3\n**After:** (no tags)\n**Total tags:** 0', 'note': 'Tag Clear Test', 'permalink': 'test/crud/tag-clear-test', 'tags_before': ['tag1', 'tag2', 'tag3'], 'tags_after': []})
- [PASS] CRUD - Delete Note

### Edge Case
**Passed:** 3/3

- [PASS] Edge Case - Read Nonexistent Note
- [PASS] Edge Case - Empty Search Query
- [PASS] Edge Case - Invalid Search Operation

### Search
**Passed:** 11/11

- [PASS] Search - Basic Text Search
- [PASS] Search - Tags Parameter (List Format)
- [PASS] Search - Tags Parameter (String Format)
- [PASS] Search - Entity Types Parameter (List Format)
- [PASS] Search - Types Parameter (List Format)
- [PASS] Search - Date Range Filter
- [PASS] Search - Search Type Title
- [PASS] Search - Search Type Permalink
- [PASS] Search - Pagination
- [PASS] Search - Complex Parameter Combination
- [PASS] Search - Results Per Page Alias

### Update
**Passed:** 1/7

- [FAIL] Update - Regex Pattern Matching
  - Error: assert 'Regex Test Note' in {'success': True, 'operation': 'write', 'summary': "Note 'Regex Test Note' updated successfully", 'result': {'title': 'Regex Test Note', 'permalink': 'test/regex-test-note', 'folder': 'test', 'observations_count': 0, 'relations_count': 0, 'resolved_relations': 0, 'unresolved_relations': 0, 'tags': []}, 'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions']}
- [FAIL] Update - Regex Backreferences
  - Error: assert 'Regex Backref Test' in {'success': True, 'operation': 'write', 'summary': "Note 'Regex Backref Test' updated successfully", 'result': {'title': 'Regex Backref Test', 'permalink': 'test/regex-backref-test', 'folder': 'test', 'observations_count': 0, 'relations_count': 0, 'resolved_relations': 0, 'unresolved_relations': 0, 'tags': []}, 'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions']}
- [FAIL] Update - Regex Security (Pattern Length)
  - Error: assert 'Regex Security Test' in {'success': True, 'operation': 'write', 'summary': "Note 'Regex Security Test' updated successfully", 'result': {'title': 'Regex Security Test', 'permalink': 'test/regex-security-test', 'folder': 'test', 'observations_count': 0, 'relations_count': 0, 'resolved_relations': 0, 'unresolved_relations': 0, 'tags': []}, 'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions']}
- [PASS] Update - Regex Invalid Pattern
- [FAIL] Update - Insert Mermaid Diagram
  - Error: assert 'Mermaid Test Note' in {'success': True, 'operation': 'write', 'summary': "Note 'Mermaid Test Note' updated successfully", 'result': {'title': 'Mermaid Test Note', 'permalink': 'test/mermaid-test-note', 'folder': 'test', 'observations_count': 0, 'relations_count': 0, 'resolved_relations': 0, 'unresolved_relations': 0, 'tags': []}, 'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions']}
- [FAIL] Update - Insert ASCII Art
  - Error: assert 'ASCII Art Test' in {'success': True, 'operation': 'write', 'summary': "Note 'ASCII Art Test' updated successfully", 'result': {'title': 'ASCII Art Test', 'permalink': 'test/ascii-art-test', 'folder': 'test', 'observations_count': 0, 'relations_count': 0, 'resolved_relations': 0, 'unresolved_relations': 0, 'tags': []}, 'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions']}
- [FAIL] Update - Insert Kilroy
  - Error: assert 'Kilroy Test' in {'success': True, 'operation': 'write', 'summary': "Note 'Kilroy Test' updated successfully", 'result': {'title': 'Kilroy Test', 'permalink': 'test/kilroy-test', 'folder': 'test', 'observations_count': 0, 'relations_count': 0, 'resolved_relations': 0, 'unresolved_relations': 0, 'tags': []}, 'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions']}

## Detailed Failure Report

### CRUD - Create Basic Note
**Timestamp:** 2026-04-26T05:16:44.418429
**Error:** assert ('Created note' in {'success': True, 'operation': 'write', 'summary': "Note 'Test Note Basic' updated successfully", 'result': {'title': 'Test Note Basic', 'permalink': 'test/crud/test-note-basic', 'folder': 'test/crud', 'observations_count': 0, 'relations_count': 0, 'resolved_relations': 0, 'unresolved_relations': 0, 'tags': ['test', 'crud']}, 'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions']} or 'Updated note' in {'success': True, 'operation': 'write', 'summary': "Note 'Test Note Basic' updated successfully", 'result': {'title': 'Test Note Basic', 'permalink': 'test/crud/test-note-basic', 'folder': 'test/crud', 'observations_count': 0, 'relations_count': 0, 'resolved_relations': 0, 'unresolved_relations': 0, 'tags': ['test', 'crud']}, 'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions']})

### CRUD - Create Note with Metadata
**Timestamp:** 2026-04-26T05:16:45.405782
**Error:** 'dict' object has no attribute 'lower'

### CRUD - Read Note by Title
**Timestamp:** 2026-04-26T05:16:45.965206
**Error:** assert 'Read Test' in {'success': True, 'operation': 'read', 'summary': "Read note 'Read Test Note'", 'result': {'content': '---\r\ntitle: Read Test Note\r\ntype: note\r\npermalink: test/crud/read-test-note\r\ntags:\r\n- read-test\r\n---\r\n\r\n# Read Test\r\n\r\nThis note will be read.'}}

### CRUD - Read Note by Permalink
**Timestamp:** 2026-04-26T05:16:46.518997
**Error:** assert 'Permalink Test' in {'success': True, 'operation': 'read', 'summary': "Read note 'test/crud/permalink-read-test'", 'result': {'content': '---\r\ntitle: Permalink Read Test\r\ntype: note\r\npermalink: test/crud/permalink-read-test\r\ntags:\r\n- permalink-test\r\n---\r\n\r\n# Permalink Test\r\n\r\nReading by permalink.'}}

### CRUD - Update Note Append
**Timestamp:** 2026-04-26T05:16:47.591210
**Error:** assert ('Updated' in {'success': True, 'operation': 'edit_note', 'summary': '# Edited note (append)\nproject: test-project\nfile_path: test/crud/Update_Append_Test.md\npermalink: test/crud/update-append-test\nchecksum: e986056f\noperation: Added 5 lines to end of note', 'note': 'Update Append Test', 'permalink': 'test/crud/update-append-test', 'file_path': 'test/crud/Update_Append_Test.md', 'observations_count': 0, 'relations_count': 0, 'content': '\n\n## Added Section\n\nThis was appended.'} or 'Edit' in {'success': True, 'operation': 'edit_note', 'summary': '# Edited note (append)\nproject: test-project\nfile_path: test/crud/Update_Append_Test.md\npermalink: test/crud/update-append-test\nchecksum: e986056f\noperation: Added 5 lines to end of note', 'note': 'Update Append Test', 'permalink': 'test/crud/update-append-test', 'file_path': 'test/crud/Update_Append_Test.md', 'observations_count': 0, 'relations_count': 0, 'content': '\n\n## Added Section\n\nThis was appended.'})

### CRUD - Update Find Replace Simple
**Timestamp:** 2026-04-26T05:16:48.491522
**Error:** assert ('Updated' in {'success': True, 'operation': 'edit_note', 'summary': '# Edited note (find_replace)\nproject: test-project\nfile_path: test/crud/Find_Replace_Test.md\npermalink: test/crud/find-replace-test\nchecksum: b8618b75\noperation: Find and replace operation completed', 'note': 'Find Replace Test', 'permalink': 'test/crud/find-replace-test', 'file_path': 'test/crud/Find_Replace_Test.md', 'observations_count': 0, 'relations_count': 0, 'content': 'jason'} or 'Edit' in {'success': True, 'operation': 'edit_note', 'summary': '# Edited note (find_replace)\nproject: test-project\nfile_path: test/crud/Find_Replace_Test.md\npermalink: test/crud/find-replace-test\nchecksum: b8618b75\noperation: Find and replace operation completed', 'note': 'Find Replace Test', 'permalink': 'test/crud/find-replace-test', 'file_path': 'test/crud/Find_Replace_Test.md', 'observations_count': 0, 'relations_count': 0, 'content': 'jason'})

### Update - Regex Pattern Matching
**Timestamp:** 2026-04-26T05:16:49.376034
**Error:** assert 'Regex Test Note' in {'success': True, 'operation': 'write', 'summary': "Note 'Regex Test Note' updated successfully", 'result': {'title': 'Regex Test Note', 'permalink': 'test/regex-test-note', 'folder': 'test', 'observations_count': 0, 'relations_count': 0, 'resolved_relations': 0, 'unresolved_relations': 0, 'tags': []}, 'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions']}

### Update - Regex Backreferences
**Timestamp:** 2026-04-26T05:16:49.926998
**Error:** assert 'Regex Backref Test' in {'success': True, 'operation': 'write', 'summary': "Note 'Regex Backref Test' updated successfully", 'result': {'title': 'Regex Backref Test', 'permalink': 'test/regex-backref-test', 'folder': 'test', 'observations_count': 0, 'relations_count': 0, 'resolved_relations': 0, 'unresolved_relations': 0, 'tags': []}, 'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions']}

### Update - Regex Security (Pattern Length)
**Timestamp:** 2026-04-26T05:16:50.531380
**Error:** assert 'Regex Security Test' in {'success': True, 'operation': 'write', 'summary': "Note 'Regex Security Test' updated successfully", 'result': {'title': 'Regex Security Test', 'permalink': 'test/regex-security-test', 'folder': 'test', 'observations_count': 0, 'relations_count': 0, 'resolved_relations': 0, 'unresolved_relations': 0, 'tags': []}, 'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions']}

### Update - Insert Mermaid Diagram
**Timestamp:** 2026-04-26T05:16:51.636154
**Error:** assert 'Mermaid Test Note' in {'success': True, 'operation': 'write', 'summary': "Note 'Mermaid Test Note' updated successfully", 'result': {'title': 'Mermaid Test Note', 'permalink': 'test/mermaid-test-note', 'folder': 'test', 'observations_count': 0, 'relations_count': 0, 'resolved_relations': 0, 'unresolved_relations': 0, 'tags': []}, 'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions']}

### Update - Insert ASCII Art
**Timestamp:** 2026-04-26T05:16:52.121183
**Error:** assert 'ASCII Art Test' in {'success': True, 'operation': 'write', 'summary': "Note 'ASCII Art Test' updated successfully", 'result': {'title': 'ASCII Art Test', 'permalink': 'test/ascii-art-test', 'folder': 'test', 'observations_count': 0, 'relations_count': 0, 'resolved_relations': 0, 'unresolved_relations': 0, 'tags': []}, 'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions']}

### Update - Insert Kilroy
**Timestamp:** 2026-04-26T05:16:52.664943
**Error:** assert 'Kilroy Test' in {'success': True, 'operation': 'write', 'summary': "Note 'Kilroy Test' updated successfully", 'result': {'title': 'Kilroy Test', 'permalink': 'test/kilroy-test', 'folder': 'test', 'observations_count': 0, 'relations_count': 0, 'resolved_relations': 0, 'unresolved_relations': 0, 'tags': []}, 'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions']}

### CRUD - Update Find Replace Not Regex
**Timestamp:** 2026-04-26T05:16:53.718193
**Error:** assert 'Version 1.2.4' in {'success': True, 'operation': 'read', 'summary': "Read note 'Find Replace Regex Test'", 'result': {'content': '---\r\ntitle: Find Replace Regex Test\r\ntype: note\r\npermalink: test/crud/find-replace-regex-test\r\ntags:\r\n- regex-test\r\n---\r\n\r\n# Regex Test\r\n\r\nVersion 1.2.4 and version 2.3.4 are mentioned.'}}

### CRUD - Update Note Prepend
**Timestamp:** 2026-04-26T05:16:54.689501
**Error:** assert ('Updated' in {'success': True, 'operation': 'edit_note', 'summary': '# Edited note (prepend)\nproject: test-project\nfile_path: test/crud/Update_Prepend_Test.md\npermalink: test/crud/update-prepend-test\nchecksum: f8fe6517\noperation: Added 5 lines to beginning of note', 'note': 'Update Prepend Test', 'permalink': 'test/crud/update-prepend-test', 'file_path': 'test/crud/Update_Prepend_Test.md', 'observations_count': 0, 'relations_count': 0, 'content': '## Prepended Section\n\nThis was prepended.\n\n'} or 'Edit' in {'success': True, 'operation': 'edit_note', 'summary': '# Edited note (prepend)\nproject: test-project\nfile_path: test/crud/Update_Prepend_Test.md\npermalink: test/crud/update-prepend-test\nchecksum: f8fe6517\noperation: Added 5 lines to beginning of note', 'note': 'Update Prepend Test', 'permalink': 'test/crud/update-prepend-test', 'file_path': 'test/crud/Update_Prepend_Test.md', 'observations_count': 0, 'relations_count': 0, 'content': '## Prepended Section\n\nThis was prepended.\n\n'})

### CRUD - Update Replace Section
**Timestamp:** 2026-04-26T05:16:55.956438
**Error:** assert ('Updated' in {'success': True, 'operation': 'edit_note', 'summary': "# Edited note (replace_section)\nproject: test-project\nfile_path: test/crud/Replace_Section_Test.md\npermalink: test/crud/replace-section-test\nchecksum: beb18052\noperation: Replaced content under section '## Old Section'", 'note': 'Replace Section Test', 'permalink': 'test/crud/replace-section-test', 'file_path': 'test/crud/Replace_Section_Test.md', 'observations_count': 0, 'relations_count': 0, 'content': '\n\nNew content here.'} or 'Edit' in {'success': True, 'operation': 'edit_note', 'summary': "# Edited note (replace_section)\nproject: test-project\nfile_path: test/crud/Replace_Section_Test.md\npermalink: test/crud/replace-section-test\nchecksum: beb18052\noperation: Replaced content under section '## Old Section'", 'note': 'Replace Section Test', 'permalink': 'test/crud/replace-section-test', 'file_path': 'test/crud/Replace_Section_Test.md', 'observations_count': 0, 'relations_count': 0, 'content': '\n\nNew content here.'})

### CRUD - Update Tags Add
**Timestamp:** 2026-04-26T05:16:57.213858
**Error:** assert ('Tag Edit Complete' in {'success': True, 'operation': 'edit_tags', 'summary': '# Tag Edit Complete\n\n**Project:** test-project\n**Note:** Tag Add Test\n**Permalink:** test/crud/tag-add-test\n\n## Operation\n**Action:** add\n**Summary:** Added 2 tag(s): added, test-tag\n\n## Tags\n**Before:** initial\n**After:** initial, added, test-tag\n**Total tags:** 3', 'note': 'Tag Add Test', 'permalink': 'test/crud/tag-add-test', 'tags_before': ['initial'], 'tags_after': ['initial', 'added', 'test-tag']} or 'Added' in {'success': True, 'operation': 'edit_tags', 'summary': '# Tag Edit Complete\n\n**Project:** test-project\n**Note:** Tag Add Test\n**Permalink:** test/crud/tag-add-test\n\n## Operation\n**Action:** add\n**Summary:** Added 2 tag(s): added, test-tag\n\n## Tags\n**Before:** initial\n**After:** initial, added, test-tag\n**Total tags:** 3', 'note': 'Tag Add Test', 'permalink': 'test/crud/tag-add-test', 'tags_before': ['initial'], 'tags_after': ['initial', 'added', 'test-tag']})
**Details:**
```json
{
  "error_type": "AssertionError"
}
```

### CRUD - Update Tags Remove
**Timestamp:** 2026-04-26T05:16:58.368149
**Error:** assert ('Tag Edit Complete' in {'success': True, 'operation': 'edit_tags', 'summary': '# Tag Edit Complete\n\n**Project:** test-project\n**Note:** Tag Remove Test\n**Permalink:** test/crud/tag-remove-test\n\n## Operation\n**Action:** remove\n**Summary:** Removed 1 tag(s): remove-me\n\n## Tags\n**Before:** keep-me, remove-me\n**After:** keep-me\n**Total tags:** 1', 'note': 'Tag Remove Test', 'permalink': 'test/crud/tag-remove-test', 'tags_before': ['keep-me', 'remove-me'], 'tags_after': ['keep-me']} or 'Removed' in {'success': True, 'operation': 'edit_tags', 'summary': '# Tag Edit Complete\n\n**Project:** test-project\n**Note:** Tag Remove Test\n**Permalink:** test/crud/tag-remove-test\n\n## Operation\n**Action:** remove\n**Summary:** Removed 1 tag(s): remove-me\n\n## Tags\n**Before:** keep-me, remove-me\n**After:** keep-me\n**Total tags:** 1', 'note': 'Tag Remove Test', 'permalink': 'test/crud/tag-remove-test', 'tags_before': ['keep-me', 'remove-me'], 'tags_after': ['keep-me']})
**Details:**
```json
{
  "error_type": "AssertionError"
}
```

### CRUD - Update Tags Replace
**Timestamp:** 2026-04-26T05:16:59.514008
**Error:** assert ('Tag Edit Complete' in {'success': True, 'operation': 'edit_tags', 'summary': '# Tag Edit Complete\n\n**Project:** test-project\n**Note:** Tag Replace Test\n**Permalink:** test/crud/tag-replace-test\n\n## Operation\n**Action:** replace\n**Summary:** Replaced all tags with 2 new tag(s)\n\n## Tags\n**Before:** old-tag1, old-tag2\n**After:** new-tag1, new-tag2\n**Total tags:** 2', 'note': 'Tag Replace Test', 'permalink': 'test/crud/tag-replace-test', 'tags_before': ['old-tag1', 'old-tag2'], 'tags_after': ['new-tag1', 'new-tag2']} or 'Replaced' in {'success': True, 'operation': 'edit_tags', 'summary': '# Tag Edit Complete\n\n**Project:** test-project\n**Note:** Tag Replace Test\n**Permalink:** test/crud/tag-replace-test\n\n## Operation\n**Action:** replace\n**Summary:** Replaced all tags with 2 new tag(s)\n\n## Tags\n**Before:** old-tag1, old-tag2\n**After:** new-tag1, new-tag2\n**Total tags:** 2', 'note': 'Tag Replace Test', 'permalink': 'test/crud/tag-replace-test', 'tags_before': ['old-tag1', 'old-tag2'], 'tags_after': ['new-tag1', 'new-tag2']})
**Details:**
```json
{
  "error_type": "AssertionError"
}
```

### CRUD - Update Tags Clear
**Timestamp:** 2026-04-26T05:17:00.518960
**Error:** assert ('Tag Edit Complete' in {'success': True, 'operation': 'edit_tags', 'summary': '# Tag Edit Complete\n\n**Project:** test-project\n**Note:** Tag Clear Test\n**Permalink:** test/crud/tag-clear-test\n\n## Operation\n**Action:** clear\n**Summary:** Cleared all 3 tag(s)\n\n## Tags\n**Before:** tag1, tag2, tag3\n**After:** (no tags)\n**Total tags:** 0', 'note': 'Tag Clear Test', 'permalink': 'test/crud/tag-clear-test', 'tags_before': ['tag1', 'tag2', 'tag3'], 'tags_after': []} or 'Cleared' in {'success': True, 'operation': 'edit_tags', 'summary': '# Tag Edit Complete\n\n**Project:** test-project\n**Note:** Tag Clear Test\n**Permalink:** test/crud/tag-clear-test\n\n## Operation\n**Action:** clear\n**Summary:** Cleared all 3 tag(s)\n\n## Tags\n**Before:** tag1, tag2, tag3\n**After:** (no tags)\n**Total tags:** 0', 'note': 'Tag Clear Test', 'permalink': 'test/crud/tag-clear-test', 'tags_before': ['tag1', 'tag2', 'tag3'], 'tags_after': []})
**Details:**
```json
{
  "error_type": "AssertionError"
}
```

