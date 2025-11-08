# Known Gaps & Validation Tasks

## Critical gaps
- ❌ Ongoing: schedule quarterly research refresh to capture upstream changes from Anthropic.
- ❌ Packaging manifest could include checksum or version tag (future enhancement).
- ❌ Domain expert review pending for large-team workflows.
- ❌ Validation automation not yet wired into CI (`scripts/pre_commit_check.py` TODO).

## TODOs
1. Run research checklist quarterly; log outcomes in this module and update `metadata.sources`.
2. Enhance packager manifest to include checksum/version (backlog item).
3. Gather field feedback from teams using the tool and document insights in `modules/core-guidance.md`.
4. Integrate validation call into `scripts/pre_commit_check.py` (see TODO 5 in automation section).
5. After peer review, raise `metadata.confidence` to `high` and update status banner.

## Notes
- Document production usage patterns (team feedback, failure scenarios) in a future `modules/field-notes.md`.
