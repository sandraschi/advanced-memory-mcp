"""
Megatest Configuration and Safety Fixtures
===========================================

CRITICAL: This test suite must NEVER touch production data!

All fixtures ensure complete isolation from production database and MD folders.
"""

import hashlib
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from advanced_memory.config import AdvancedMemoryConfig, ConfigManager

# ============================================================================
# SAFETY CONSTANTS - DO NOT MODIFY
# ============================================================================

PRODUCTION_PATHS_TO_PROTECT = [
    Path.home() / ".advanced-memory",
    Path.home() / "Documents" / "advanced-memory",
    Path.home() / "Documents" / "knowledge-base",
    # Add other common production paths
]


# ============================================================================
# SAFETY FUNCTIONS
# ============================================================================


def is_production_path(path: Path) -> bool:
    """Check if a path is in production directories."""
    path = path.resolve()

    # Check against known production paths
    for prod_path in PRODUCTION_PATHS_TO_PROTECT:
        if path == prod_path or path.is_relative_to(prod_path):
            return True

    # Check for common production indicators
    if ".advanced-memory" in str(path) and "test" not in str(path).lower():
        return True

    return False


def is_safe_test_path(path: Path) -> bool:
    """Verify path is safe for testing."""
    path = path.resolve()

    # Must be in temp, test_data, or tests directory
    safe_indicators = [
        "test_data",
        "megatest",
        tempfile.gettempdir(),
        "tests/",
        "/tmp/",
        "temp/",
    ]

    path_str = str(path).lower()
    return any(indicator.lower() in path_str for indicator in safe_indicators)


def verify_production_untouched(prod_db_path: Path, initial_checksum: str | None):
    """Verify production database was not modified."""
    if prod_db_path.exists() and initial_checksum:
        current_checksum = compute_checksum_file(prod_db_path)
        if current_checksum != initial_checksum:
            raise RuntimeError(
                f"CRITICAL ERROR: Production database was modified!\n"
                f"Path: {prod_db_path}\n"
                f"Initial: {initial_checksum}\n"
                f"Current: {current_checksum}"
            )


def compute_checksum_file(file_path: Path) -> str:
    """Compute file checksum for integrity verification."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


# ============================================================================
# SAFETY FIXTURES
# ============================================================================


@pytest.fixture(scope="session", autouse=True)
def verify_not_production():
    """
    Session-level safety check - runs BEFORE any tests.

    This fixture ensures we're not accidentally running tests
    against production data.
    """
    # Get current config (if any)
    try:
        config = ConfigManager().config

        # Check if config points to production
        if config.database_path and is_production_path(Path(config.database_path)):
            pytest.exit(
                "FATAL: Current config uses production database! "
                "Megatest cannot run with production configuration.",
                returncode=1,
            )

        for project in config.projects.values():
            if is_production_path(Path(project.home)):
                pytest.exit(
                    f"FATAL: Project '{project.name}' uses production path! "
                    f"Megatest cannot run with production projects.",
                    returncode=1,
                )
    except Exception:
        # No config yet - safe to proceed
        pass

    print("\n" + "=" * 60)
    print("🛡️  MEGATEST SAFETY CHECK: PASSED")
    print("=" * 60 + "\n")


@pytest.fixture(scope="module")
def isolated_test_env() -> Generator[dict, None, None]:
    """
    Create completely isolated test environment.

    Returns:
        dict with:
        - test_dir: Path to test MD folder
        - test_db: Path to test database
        - config: Test configuration object
    """
    # Create isolated temp directory
    temp_base = Path(tempfile.mkdtemp(prefix="megatest_"))
    test_dir = temp_base / "md_files"
    test_db = temp_base / "test.db"

    # Create directories
    test_dir.mkdir(parents=True, exist_ok=True)

    # CRITICAL: Verify paths are safe
    assert is_safe_test_path(test_dir), f"Unsafe test dir: {test_dir}"
    assert is_safe_test_path(test_db), f"Unsafe test db: {test_db}"
    assert not is_production_path(test_dir), f"Test dir is production: {test_dir}"
    assert not is_production_path(test_db), f"Test db is production: {test_db}"

    # Get production paths for monitoring
    try:
        prod_config = ConfigManager().config
        prod_db = Path(prod_config.database_path) if prod_config.database_path else None
        prod_checksum = compute_checksum_file(prod_db) if prod_db and prod_db.exists() else None
    except Exception:
        prod_db = None
        prod_checksum = None

    # Create test configuration
    test_config = AdvancedMemoryConfig(
        database_path=str(test_db),
        projects={
            "test_personal": {
                "name": "test_personal",
                "home": str(test_dir / "test_personal"),
                "is_default": True,
            },
            "test_work": {
                "name": "test_work",
                "home": str(test_dir / "test_work"),
            },
            "test_archive": {
                "name": "test_archive",
                "home": str(test_dir / "test_archive"),
            },
        },
    )

    # Display test environment
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "MEGATEST ENVIRONMENT - ISOLATED" + " " * 12 + "║")
    print("╠" + "═" * 58 + "╣")
    if prod_db:
        print(f"║ Production DB:   {str(prod_db):<40} [PROTECTED] ║")
    print(f"║ Test DB:         {str(test_db):<40} [TEST ONLY] ║")
    print(f"║ Test Home:       {str(test_dir):<40} [TEST ONLY] ║")
    print("║                                                            ║")
    print("║ Status: ✅ ISOLATED - Safe to proceed                      ║")
    print("╚" + "═" * 58 + "╝\n")

    # Yield test environment
    yield {
        "test_dir": test_dir,
        "test_db": test_db,
        "config": test_config,
        "temp_base": temp_base,
    }

    # CLEANUP: Verify production untouched, then delete test data
    if prod_db and prod_checksum:
        verify_production_untouched(prod_db, prod_checksum)
        print("✅ Production database verified: UNTOUCHED")

    # Remove test data
    try:
        shutil.rmtree(temp_base)
        print(f"✅ Test data cleaned up: {temp_base}")
    except Exception as e:
        print(f"⚠️  Warning: Could not clean up test data: {e}")


@pytest.fixture(scope="module")
def megatest_context(isolated_test_env):
    """
    Megatest context with all necessary setup.

    Provides high-level interface to test environment.
    """
    from .test_megatest_runner import MegatestContext

    context = MegatestContext(
        test_dir=isolated_test_env["test_dir"],
        test_db=isolated_test_env["test_db"],
        config=isolated_test_env["config"],
    )

    # Initialize (creates DB, sets up projects)
    context.initialize()

    yield context

    # Cleanup handled by isolated_test_env fixture


@pytest.fixture
def assert_production_safe():
    """
    Fixture that provides production safety assertion function.

    Use in tests that perform destructive operations.
    """

    def _assert_safe(test_path: Path):
        """Assert path is not production."""
        if is_production_path(test_path):
            pytest.fail(f"FATAL: Test attempted to use production path: {test_path}")
        if not is_safe_test_path(test_path):
            pytest.fail(f"FATAL: Test path is not safe: {test_path}")

    return _assert_safe


# ============================================================================
# SAFETY MARKERS
# ============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "megatest: Comprehensive integration test (90+ minutes, ISOLATED environment)"
    )
    config.addinivalue_line(
        "markers", "megatest_quick: Quick validation (10 minutes, ISOLATED environment)"
    )
    config.addinivalue_line(
        "markers", "destructive: Test performs destructive operations (MUST be isolated)"
    )


# ============================================================================
# SAFETY VALIDATION
# ============================================================================


@pytest.fixture(autouse=True)
def validate_test_isolation(request):
    """
    Auto-runs before EVERY test to ensure isolation.

    This is the last line of defense against production data corruption.
    """
    # Skip for non-megatest tests
    if "megatest" not in request.node.name.lower():
        return

    # Get isolated_test_env if available
    if "isolated_test_env" in request.fixturenames:
        env = request.getfixturevalue("isolated_test_env")

        # Verify test paths are still safe
        assert is_safe_test_path(env["test_dir"])
        assert is_safe_test_path(env["test_db"])
        assert not is_production_path(env["test_dir"])
        assert not is_production_path(env["test_db"])
