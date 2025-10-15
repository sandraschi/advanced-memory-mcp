"""
Advanced Memory Megatest Suite
===============================

Multi-level comprehensive integration testing from smoke tests to full validation.

Test Levels:
------------

LEVEL 1: SMOKE TEST (2 minutes) ⚡
    - Quick sanity check
    - Basic CRUD operations only
    - No imports/exports
    - Run: pytest tests/megatest/ -m megatest_smoke

LEVEL 2: STANDARD TEST (10 minutes) 🔧
    - Core functionality validation
    - Multi-project operations
    - Tag operations
    - Basic edge cases
    - Run: pytest tests/megatest/ -m megatest_standard

LEVEL 3: ADVANCED TEST (20 minutes) 🚀
    - Advanced search & relationships
    - Knowledge graph traversal
    - Performance metrics
    - Extended edge cases
    - Run: pytest tests/megatest/ -m megatest_advanced

LEVEL 4: INTEGRATION TEST (45 minutes) 📦
    - All export formats tested
    - All import formats tested
    - Round-trip integrity verification
    - Run: pytest tests/megatest/ -m megatest_integration

LEVEL 5: FULL BLAST (90 minutes) 💥
    - Everything tested
    - Stress testing
    - Working Docsify site validation
    - Working HTML site validation
    - Complete system certification
    - Run: pytest tests/megatest/ -m megatest_full

Safety:
-------
ALL levels use ISOLATED test environment:
- Temp directory only (/tmp/megatest_*)
- Separate test database
- Production data NEVER touched
- Checksum verified before/after

Quick Start:
-----------
# Level 1 - Quick check (2 min)
pytest tests/megatest/ -v -m megatest_smoke

# Level 2 - Standard check (10 min)
pytest tests/megatest/ -v -m megatest_standard

# Level 5 - Full validation (90 min)
pytest tests/megatest/ -v -m megatest_full
"""

__all__ = [
    "MegatestContext",
    "PhaseResult",
    "MetricsCollector",
]
