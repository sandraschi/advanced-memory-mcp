---
title: "Tag Edit Bugfix 2025-11-09"
tags:
  - adn-content
  - bugfix
  - metadata
  - claude
  - tooling
created: 2025-11-09
updated: 2025-11-09
---

# Tag Edit Bugfix (adn_content edit_tags)

## What broke
- Calling `adn_content("edit_tags", …)` with `tag_operation="add"` threw `TypeError: can only concatenate str (not "list") to str`.
- `tag_operation="remove"` returned `AttributeError: 'EntityResponse' object has no attribute 'content'`.
- Net effect: API attempted to write metadata updates with bad payloads and would have blanked note bodies if the server accepted them.

## Root causes
1. **Mixed tag metadata** — some notes store `entity_metadata["tags"]` as a single string instead of an array; concatenating existing tags with new ones failed.
2. **Missing content round-trip** — the knowledge API response omits `content`, and we forwarded `None` back in the PUT, effectively nuking the file.

## Fix
- Normalize `existing_tags_raw` to `list[str]` before performing add/remove/replace operations.
- Retrieve the current markdown via `/resource/{permalink}` and include that text in the update payload, ensuring the note body survives.
- Added friendly error handling if the content fetch ever fails, rather than overwriting.

## Follow-up ideas
- Audit other metadata mutations for similar “missing body” hazards.
- Add regression coverage to the tool exercisers so `edit_tags` is tested alongside other operations.
