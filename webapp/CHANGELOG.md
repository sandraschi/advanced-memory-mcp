# ADN Webapp Changelog

All notable changes to the Advanced Memory Webapp component are documented here.

## [1.2.0] - 2026-02-19

### Added
- Unified `start.ps1` and `start.bat` scripts for port-clean orchestration.
- Integration with the new `file_safety.py` recovery layer.
- Comprehensive root documentation (`README.md` and `CHANGELOG.md`).

### Fixed
- Improved port handling to prevent "zombie" processes on 10704/10705.
- Fixed dependency resolution issues between frontend and backend.

### Improved
- SOTA UI/UX Alignment: Reinforced dark-themed aesthetics and glassmorphic elements.
- Cleaned up legacy "runt" configuration files from root webapp directory.

## [1.1.0] - 2026-02-11

### Added
- Multi-pane research dashboard implementation.
- Real-time logging console integration.

### Changed
- Refactored frontend to use Vite for improved performance.

## [1.0.0] - 2026-02-05

### Added
- Initial release of the React interface.
- Basic Express bridge for MCP connectivity.
