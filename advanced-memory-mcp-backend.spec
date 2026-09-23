# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — produce advanced-memory-mcp-backend.exe for Tauri NSIS embedding.
# Fleet standard: strip=False, upx=False, noarchive=True (see tauri_nsis_building.md).
# Usage (from repo root):
#   uv run pyinstaller advanced-memory-mcp-backend.spec --distpath dist --clean --noconfirm

block_cipher = None

from PyInstaller.utils.hooks import collect_submodules

_pkg_all = []
try:
    _pkg_all = collect_submodules("advanced_memory")
except Exception:
    _pkg_all = []

a = Analysis(
    ["src/advanced_memory/__main__.py"],
    pathex=["src"],
    binaries=[],
    datas=[("src/advanced_memory", "advanced_memory")],
    hiddenimports=[
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.asyncio",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "h11",
        "beartype",
        "websockets",
        "sqlite3",
        "_strptime",
        "_datetime",
        "cachetools",
        "pytz",
        "jsonschema",
        "joserfc",
        "joserfc.jwk",
        "joserfc.jwt",
        "jwt",
        "key_value",
        # setuptools/pkg_resources runtime deps (frozen exe crashes in
        # pyi_rth_pkgres without them; resolved via setuptools _vendor alias).
        "jaraco.text",
        "jaraco.functools",
        "jaraco.context",
        "jaraco.collections",
    ]
    + _pkg_all,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "setuptools", "pip", "wheel", "test", "tests", "unittest", "_distutils_hack"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,
)
# Strip .dist-info but preserve metadata for packages that need it at runtime.
# Match on path-separator-prefixed names only: a bare 'mcp-' substring also
# matches fastmcp-*.dist-info DIRECTORY entries, and PyInstaller then fails
# opening the directory as a file (PermissionError, fleet pitfall).
_keep_dist = ["\\fastmcp-", "/fastmcp-", "\\mcp-", "/mcp-", "\\prefab_ui-", "/prefab_ui-", "\\opentelemetry-", "/opentelemetry-", "\\email_validator-", "/email_validator-"]
def _want_dist(entry_name: str) -> bool:
    if ".dist-info" not in entry_name:
        return False
    if any(k in entry_name for k in _keep_dist):
        return True
    # Dest-name-only TOC entries (no path separator to match on).
    return entry_name.startswith("mcp-")


_saved = [e for e in a.datas if isinstance(e, tuple) and _want_dist(str(e[0]))]
for _list in [a.datas, a.binaries, a.zipfiles, a.scripts]:
    _list[:] = [e for e in _list if not (isinstance(e, tuple) and ".dist-info" in str(e[0]))]
a.datas.extend(_saved)
SKIP = [
    "torch",
    "playwright",
    "bitsandbytes",
    "llvmlite",
    "pyarrow",
    "pymupdf",
    "grpc",
    "numba",
    "Cython",
    "google",
    "azure",
    "boto3",
    "botocore",
    "matplotlib",
    "PIL",
    "pandas",
    "scipy",
    "sklearn",
    "onnxruntime",
]
a.binaries = [b for b in a.binaries if not any(s in b[0].lower() for s in SKIP)]
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="advanced-memory-mcp-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
