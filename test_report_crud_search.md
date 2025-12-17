
# Comprehensive CRUD and Search Test Report

**Generated:** 2025-11-17T12:42:07.382816
**Duration:** 308.92 seconds
**Total Tests:** 35
**Passed:** 29 (82.9%)
**Failed:** 6 (17.1%)

## Summary

**6 TEST(S) FAILED**

## Test Results by Category

### CRUD
**Passed:** 14/14

- [PASS] CRUD - Create Basic Note
- [PASS] CRUD - Create Note with Metadata
- [PASS] CRUD - Read Note by Title
- [PASS] CRUD - Read Note by Permalink
- [PASS] CRUD - Update Note Append
- [PASS] CRUD - Update Find Replace Simple
- [PASS] CRUD - Update Find Replace Not Regex
- [PASS] CRUD - Update Note Prepend
- [PASS] CRUD - Update Replace Section
- [PASS] CRUD - Update Tags Add
- [PASS] CRUD - Update Tags Remove
- [PASS] CRUD - Update Tags Replace
- [PASS] CRUD - Update Tags Clear
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
  - Error: assert 'Regex Test Note' in '# Created note\nproject: test-project\nfile_path: test/Regex_Test_Note.md\npermalink: test/regex-test-note\nchecksum: 7e02718b'
- [FAIL] Update - Regex Backreferences
  - Error: assert 'Regex Backref Test' in '# Created note\nproject: test-project\nfile_path: test/Regex_Backref_Test.md\npermalink: test/regex-backref-test\nchecksum: b2a458f6'
- [FAIL] Update - Regex Security (Pattern Length)
  - Error: assert 'Regex Security Test' in '# Created note\nproject: test-project\nfile_path: test/Regex_Security_Test.md\npermalink: test/regex-security-test\nchecksum: e80704fa'
- [PASS] Update - Regex Invalid Pattern
- [FAIL] Update - Insert Mermaid Diagram
  - Error: assert 'Mermaid Test Note' in '# Created note\nproject: test-project\nfile_path: test/Mermaid_Test_Note.md\npermalink: test/mermaid-test-note\nchecksum: 56384a94'
- [FAIL] Update - Insert ASCII Art
  - Error: assert 'ASCII Art Test' in '# Created note\nproject: test-project\nfile_path: test/ASCII_Art_Test.md\npermalink: test/ascii-art-test\nchecksum: 0781f067'
- [FAIL] Update - Insert Kilroy
  - Error: assert 'Kilroy Test' in '# Created note\nproject: test-project\nfile_path: test/Kilroy_Test.md\npermalink: test/kilroy-test\nchecksum: 5f617fc1'

## Detailed Failure Report

### Update - Regex Pattern Matching
**Timestamp:** 2025-11-17T12:38:50.720866
**Error:** assert 'Regex Test Note' in '# Created note\nproject: test-project\nfile_path: test/Regex_Test_Note.md\npermalink: test/regex-test-note\nchecksum: 7e02718b'

### Update - Regex Backreferences
**Timestamp:** 2025-11-17T12:38:51.063419
**Error:** assert 'Regex Backref Test' in '# Created note\nproject: test-project\nfile_path: test/Regex_Backref_Test.md\npermalink: test/regex-backref-test\nchecksum: b2a458f6'

### Update - Regex Security (Pattern Length)
**Timestamp:** 2025-11-17T12:38:51.405206
**Error:** assert 'Regex Security Test' in '# Created note\nproject: test-project\nfile_path: test/Regex_Security_Test.md\npermalink: test/regex-security-test\nchecksum: e80704fa'

### Update - Insert Mermaid Diagram
**Timestamp:** 2025-11-17T12:38:52.038005
**Error:** assert 'Mermaid Test Note' in '# Created note\nproject: test-project\nfile_path: test/Mermaid_Test_Note.md\npermalink: test/mermaid-test-note\nchecksum: 56384a94'

### Update - Insert ASCII Art
**Timestamp:** 2025-11-17T12:38:52.292907
**Error:** assert 'ASCII Art Test' in '# Created note\nproject: test-project\nfile_path: test/ASCII_Art_Test.md\npermalink: test/ascii-art-test\nchecksum: 0781f067'

### Update - Insert Kilroy
**Timestamp:** 2025-11-17T12:38:52.601073
**Error:** assert 'Kilroy Test' in '# Created note\nproject: test-project\nfile_path: test/Kilroy_Test.md\npermalink: test/kilroy-test\nchecksum: 5f617fc1'
