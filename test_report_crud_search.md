
# Comprehensive CRUD and Search Test Report

**Generated:** 2026-04-21T08:14:03.739592
**Duration:** 254.60 seconds
**Total Tests:** 35
**Passed:** 16 (45.7%)
**Failed:** 19 (54.3%)

## Summary

**19 TEST(S) FAILED**

## Test Results by Category

### CRUD
**Passed:** 1/14

- [FAIL] CRUD - Create Basic Note
  - Error: assert ('Created note' in {'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions...', 'observations_count': 0, 'permalink': 'test/crud/test-note-basic', 'relations_count': 0, ...}, 'success': True, ...} or 'Updated note' in {'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions...', 'observations_count': 0, 'permalink': 'test/crud/test-note-basic', 'relations_count': 0, ...}, 'success': True, ...})
- [FAIL] CRUD - Create Note with Metadata
  - Error: 'dict' object has no attribute 'lower'
- [FAIL] CRUD - Read Note by Title
  - Error: assert 'Read Test' in {'operation': 'read', 'result': {'content': '---\r\ntitle: Read Test Note\r\ntype: note\r\npermalink: test/crud/read-t...t\r\n---\r\n\r\n# Read Test\r\n\r\nThis note will be read.'}, 'success': True, 'summary': "Read note 'Read Test Note'"}
- [FAIL] CRUD - Read Note by Permalink
  - Error: assert 'Permalink Test' in {'operation': 'read', 'result': {'content': '---\r\ntitle: Permalink Read Test\r\ntype: note\r\npermalink: test/crud/p...Permalink Test\r\n\r\nReading by permalink.'}, 'success': True, 'summary': "Read note 'test/crud/permalink-read-test'"}
- [FAIL] CRUD - Update Note Append
  - Error: assert ('Updated' in {'content': '\n\n## Added Section\n\nThis was appended.', 'file_path': 'test/crud/Update_Append_Test.md', 'note': 'Update Append Test', 'observations_count': 0, ...} or 'Edit' in {'content': '\n\n## Added Section\n\nThis was appended.', 'file_path': 'test/crud/Update_Append_Test.md', 'note': 'Update Append Test', 'observations_count': 0, ...})
- [FAIL] CRUD - Update Find Replace Simple
  - Error: assert ('Updated' in {'content': 'jason', 'file_path': 'test/crud/Find_Replace_Test.md', 'note': 'Find Replace Test', 'observations_count': 0, ...} or 'Edit' in {'content': 'jason', 'file_path': 'test/crud/Find_Replace_Test.md', 'note': 'Find Replace Test', 'observations_count': 0, ...})
- [FAIL] CRUD - Update Find Replace Not Regex
  - Error: assert 'Version 1.2.4' in {'operation': 'read', 'result': {'content': '---\r\ntitle: Find Replace Regex Test\r\ntype: note\r\npermalink: test/cr...r\nVersion 1.2.4 and version 2.3.4 are mentioned.'}, 'success': True, 'summary': "Read note 'Find Replace Regex Test'"}
- [FAIL] CRUD - Update Note Prepend
  - Error: assert ('Updated' in {'content': '## Prepended Section\n\nThis was prepended.\n\n', 'file_path': 'test/crud/Update_Prepend_Test.md', 'note': 'Update Prepend Test', 'observations_count': 0, ...} or 'Edit' in {'content': '## Prepended Section\n\nThis was prepended.\n\n', 'file_path': 'test/crud/Update_Prepend_Test.md', 'note': 'Update Prepend Test', 'observations_count': 0, ...})
- [FAIL] CRUD - Update Replace Section
  - Error: assert ('Updated' in {'content': '\n\nNew content here.', 'file_path': 'test/crud/Replace_Section_Test.md', 'note': 'Replace Section Test', 'observations_count': 0, ...} or 'Edit' in {'content': '\n\nNew content here.', 'file_path': 'test/crud/Replace_Section_Test.md', 'note': 'Replace Section Test', 'observations_count': 0, ...})
- [FAIL] CRUD - Update Tags Add
  - Error: assert ('Tag Edit Complete' in {'note': 'Tag Add Test', 'operation': 'edit_tags', 'permalink': 'test/crud/tag-add-test', 'success': True, ...} or 'Added' in {'note': 'Tag Add Test', 'operation': 'edit_tags', 'permalink': 'test/crud/tag-add-test', 'success': True, ...})
- [FAIL] CRUD - Update Tags Remove
  - Error: assert ('Tag Edit Complete' in {'note': 'Tag Remove Test', 'operation': 'edit_tags', 'permalink': 'test/crud/tag-remove-test', 'success': True, ...} or 'Removed' in {'note': 'Tag Remove Test', 'operation': 'edit_tags', 'permalink': 'test/crud/tag-remove-test', 'success': True, ...})
- [FAIL] CRUD - Update Tags Replace
  - Error: assert ('Tag Edit Complete' in {'note': 'Tag Replace Test', 'operation': 'edit_tags', 'permalink': 'test/crud/tag-replace-test', 'success': True, ...} or 'Replaced' in {'note': 'Tag Replace Test', 'operation': 'edit_tags', 'permalink': 'test/crud/tag-replace-test', 'success': True, ...})
- [FAIL] CRUD - Update Tags Clear
  - Error: assert ('Tag Edit Complete' in {'note': 'Tag Clear Test', 'operation': 'edit_tags', 'permalink': 'test/crud/tag-clear-test', 'success': True, ...} or 'Cleared' in {'note': 'Tag Clear Test', 'operation': 'edit_tags', 'permalink': 'test/crud/tag-clear-test', 'success': True, ...})
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
  - Error: assert 'Regex Test Note' in {'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions...'test', 'observations_count': 0, 'permalink': 'test/regex-test-note', 'relations_count': 0, ...}, 'success': True, ...}
- [FAIL] Update - Regex Backreferences
  - Error: assert 'Regex Backref Test' in {'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions...st', 'observations_count': 0, 'permalink': 'test/regex-backref-test', 'relations_count': 0, ...}, 'success': True, ...}
- [FAIL] Update - Regex Security (Pattern Length)
  - Error: assert 'Regex Security Test' in {'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions...t', 'observations_count': 0, 'permalink': 'test/regex-security-test', 'relations_count': 0, ...}, 'success': True, ...}
- [PASS] Update - Regex Invalid Pattern
- [FAIL] Update - Insert Mermaid Diagram
  - Error: assert 'Mermaid Test Note' in {'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions...est', 'observations_count': 0, 'permalink': 'test/mermaid-test-note', 'relations_count': 0, ...}, 'success': True, ...}
- [FAIL] Update - Insert ASCII Art
  - Error: assert 'ASCII Art Test' in {'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions... 'test', 'observations_count': 0, 'permalink': 'test/ascii-art-test', 'relations_count': 0, ...}, 'success': True, ...}
- [FAIL] Update - Insert Kilroy
  - Error: assert 'Kilroy Test' in {'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions...r': 'test', 'observations_count': 0, 'permalink': 'test/kilroy-test', 'relations_count': 0, ...}, 'success': True, ...}

## Detailed Failure Report

### CRUD - Create Basic Note
**Timestamp:** 2026-04-21T08:10:05.985315
**Error:** assert ('Created note' in {'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions...', 'observations_count': 0, 'permalink': 'test/crud/test-note-basic', 'relations_count': 0, ...}, 'success': True, ...} or 'Updated note' in {'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions...', 'observations_count': 0, 'permalink': 'test/crud/test-note-basic', 'relations_count': 0, ...}, 'success': True, ...})

### CRUD - Create Note with Metadata
**Timestamp:** 2026-04-21T08:10:06.990967
**Error:** 'dict' object has no attribute 'lower'

### CRUD - Read Note by Title
**Timestamp:** 2026-04-21T08:10:07.931031
**Error:** assert 'Read Test' in {'operation': 'read', 'result': {'content': '---\r\ntitle: Read Test Note\r\ntype: note\r\npermalink: test/crud/read-t...t\r\n---\r\n\r\n# Read Test\r\n\r\nThis note will be read.'}, 'success': True, 'summary': "Read note 'Read Test Note'"}

### CRUD - Read Note by Permalink
**Timestamp:** 2026-04-21T08:10:09.194928
**Error:** assert 'Permalink Test' in {'operation': 'read', 'result': {'content': '---\r\ntitle: Permalink Read Test\r\ntype: note\r\npermalink: test/crud/p...Permalink Test\r\n\r\nReading by permalink.'}, 'success': True, 'summary': "Read note 'test/crud/permalink-read-test'"}

### CRUD - Update Note Append
**Timestamp:** 2026-04-21T08:10:10.885408
**Error:** assert ('Updated' in {'content': '\n\n## Added Section\n\nThis was appended.', 'file_path': 'test/crud/Update_Append_Test.md', 'note': 'Update Append Test', 'observations_count': 0, ...} or 'Edit' in {'content': '\n\n## Added Section\n\nThis was appended.', 'file_path': 'test/crud/Update_Append_Test.md', 'note': 'Update Append Test', 'observations_count': 0, ...})

### CRUD - Update Find Replace Simple
**Timestamp:** 2026-04-21T08:10:12.147776
**Error:** assert ('Updated' in {'content': 'jason', 'file_path': 'test/crud/Find_Replace_Test.md', 'note': 'Find Replace Test', 'observations_count': 0, ...} or 'Edit' in {'content': 'jason', 'file_path': 'test/crud/Find_Replace_Test.md', 'note': 'Find Replace Test', 'observations_count': 0, ...})

### Update - Regex Pattern Matching
**Timestamp:** 2026-04-21T08:10:12.881602
**Error:** assert 'Regex Test Note' in {'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions...'test', 'observations_count': 0, 'permalink': 'test/regex-test-note', 'relations_count': 0, ...}, 'success': True, ...}

### Update - Regex Backreferences
**Timestamp:** 2026-04-21T08:10:13.503319
**Error:** assert 'Regex Backref Test' in {'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions...st', 'observations_count': 0, 'permalink': 'test/regex-backref-test', 'relations_count': 0, ...}, 'success': True, ...}

### Update - Regex Security (Pattern Length)
**Timestamp:** 2026-04-21T08:10:14.163678
**Error:** assert 'Regex Security Test' in {'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions...t', 'observations_count': 0, 'permalink': 'test/regex-security-test', 'relations_count': 0, ...}, 'success': True, ...}

### Update - Insert Mermaid Diagram
**Timestamp:** 2026-04-21T08:10:15.599889
**Error:** assert 'Mermaid Test Note' in {'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions...est', 'observations_count': 0, 'permalink': 'test/mermaid-test-note', 'relations_count': 0, ...}, 'success': True, ...}

### Update - Insert ASCII Art
**Timestamp:** 2026-04-21T08:10:16.332210
**Error:** assert 'ASCII Art Test' in {'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions... 'test', 'observations_count': 0, 'permalink': 'test/ascii-art-test', 'relations_count': 0, ...}, 'success': True, ...}

### Update - Insert Kilroy
**Timestamp:** 2026-04-21T08:10:17.095383
**Error:** assert 'Kilroy Test' in {'next_steps': ['Review the updated content', 'Add related notes or concepts', 'Consider enhancing with AI suggestions...r': 'test', 'observations_count': 0, 'permalink': 'test/kilroy-test', 'relations_count': 0, ...}, 'success': True, ...}

### CRUD - Update Find Replace Not Regex
**Timestamp:** 2026-04-21T08:10:18.977846
**Error:** assert 'Version 1.2.4' in {'operation': 'read', 'result': {'content': '---\r\ntitle: Find Replace Regex Test\r\ntype: note\r\npermalink: test/cr...r\nVersion 1.2.4 and version 2.3.4 are mentioned.'}, 'success': True, 'summary': "Read note 'Find Replace Regex Test'"}

### CRUD - Update Note Prepend
**Timestamp:** 2026-04-21T08:10:20.405200
**Error:** assert ('Updated' in {'content': '## Prepended Section\n\nThis was prepended.\n\n', 'file_path': 'test/crud/Update_Prepend_Test.md', 'note': 'Update Prepend Test', 'observations_count': 0, ...} or 'Edit' in {'content': '## Prepended Section\n\nThis was prepended.\n\n', 'file_path': 'test/crud/Update_Prepend_Test.md', 'note': 'Update Prepend Test', 'observations_count': 0, ...})

### CRUD - Update Replace Section
**Timestamp:** 2026-04-21T08:10:21.753359
**Error:** assert ('Updated' in {'content': '\n\nNew content here.', 'file_path': 'test/crud/Replace_Section_Test.md', 'note': 'Replace Section Test', 'observations_count': 0, ...} or 'Edit' in {'content': '\n\nNew content here.', 'file_path': 'test/crud/Replace_Section_Test.md', 'note': 'Replace Section Test', 'observations_count': 0, ...})

### CRUD - Update Tags Add
**Timestamp:** 2026-04-21T08:10:23.366940
**Error:** assert ('Tag Edit Complete' in {'note': 'Tag Add Test', 'operation': 'edit_tags', 'permalink': 'test/crud/tag-add-test', 'success': True, ...} or 'Added' in {'note': 'Tag Add Test', 'operation': 'edit_tags', 'permalink': 'test/crud/tag-add-test', 'success': True, ...})
**Details:**
```json
{
  "error_type": "AssertionError"
}
```

### CRUD - Update Tags Remove
**Timestamp:** 2026-04-21T08:10:24.984095
**Error:** assert ('Tag Edit Complete' in {'note': 'Tag Remove Test', 'operation': 'edit_tags', 'permalink': 'test/crud/tag-remove-test', 'success': True, ...} or 'Removed' in {'note': 'Tag Remove Test', 'operation': 'edit_tags', 'permalink': 'test/crud/tag-remove-test', 'success': True, ...})
**Details:**
```json
{
  "error_type": "AssertionError"
}
```

### CRUD - Update Tags Replace
**Timestamp:** 2026-04-21T08:10:26.631707
**Error:** assert ('Tag Edit Complete' in {'note': 'Tag Replace Test', 'operation': 'edit_tags', 'permalink': 'test/crud/tag-replace-test', 'success': True, ...} or 'Replaced' in {'note': 'Tag Replace Test', 'operation': 'edit_tags', 'permalink': 'test/crud/tag-replace-test', 'success': True, ...})
**Details:**
```json
{
  "error_type": "AssertionError"
}
```

### CRUD - Update Tags Clear
**Timestamp:** 2026-04-21T08:10:28.023569
**Error:** assert ('Tag Edit Complete' in {'note': 'Tag Clear Test', 'operation': 'edit_tags', 'permalink': 'test/crud/tag-clear-test', 'success': True, ...} or 'Cleared' in {'note': 'Tag Clear Test', 'operation': 'edit_tags', 'permalink': 'test/crud/tag-clear-test', 'success': True, ...})
**Details:**
```json
{
  "error_type": "AssertionError"
}
```

