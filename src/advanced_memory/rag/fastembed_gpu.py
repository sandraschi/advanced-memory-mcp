"""Fleet-standard FastEmbed GPU bootstrap."""

from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

EMBED_BATCH_SIZE_CPU = 64
EMBED_BATCH_SIZE_GPU = 256


def _env_flag(name: str) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    return raw in ("1", "true", "yes", "on")


def repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[3]


def embed_use_gpu(repo_root: Path | None = None) -> bool:
    if _env_flag("RAG_GPU") or _env_flag("MCD_RAG_GPU"):
        return True
    root = repo_root or repo_root_from_here()
    if (root / ".venv" / "rag-gpu-mode").is_file():
        return True
    return False


_dll_dirs_registered = False


def _register_nvidia_dll_dirs(repo_root: Path | None = None) -> None:
    """Make the pip-installed nvidia-*-cu12 packages' bin/ dirs resolvable by
    Windows' DLL loader.

    onnxruntime-gpu's CUDAExecutionProvider needs cublasLt64_12.dll, cudart64_12.dll,
    cufft64_11.dll, cudnn64_9.dll, etc. at runtime. These ship inside the nvidia-*-cu12
    pip wheels under .venv/Lib/site-packages/nvidia/<pkg>/bin, but pip does not add
    that to PATH or the DLL search path, so CUDA session creation silently falls back
    to CPU with no hard error unless the whole chain (cublas -> cufft -> cudart -> ...)
    happens to already be resolvable.

    os.add_dll_directory() alone is NOT sufficient here in testing -- it does not
    reliably cover the transitive dependency chain that onnxruntime's own provider
    DLL resolves internally (cublasLt64_12.dll -> cufft64_11.dll -> cudart64_12.dll).
    Prepending the actual process PATH is what empirically works, so we do both:
    add_dll_directory for the safe/modern loader path, and prepend PATH as the
    proven-working fallback. This makes the fix durable across however the process
    is launched (webapp uvicorn, nssm service, CLI), instead of depending on a
    shell's PATH being set up correctly at launch time.
    """
    global _dll_dirs_registered
    if _dll_dirs_registered or os.name != "nt":
        return

    root = repo_root or repo_root_from_here()
    nvidia_root = root / ".venv" / "Lib" / "site-packages" / "nvidia"
    if not nvidia_root.is_dir():
        return

    bin_dirs: list[str] = []
    for pkg_dir in nvidia_root.iterdir():
        bin_dir = pkg_dir / "bin"
        if bin_dir.is_dir():
            bin_dirs.append(str(bin_dir))
            try:
                os.add_dll_directory(str(bin_dir))
            except (OSError, AttributeError) as exc:  # pragma: no cover
                logger.warning("Could not register DLL dir %s: %s", bin_dir, exc)

    if bin_dirs:
        os.environ["PATH"] = os.pathsep.join(bin_dirs) + os.pathsep + os.environ.get("PATH", "")

    _dll_dirs_registered = True


def create_text_embedding(
    model_name: str,
    cache_dir: str,
    *,
    repo_root: Path | None = None,
    batch_cpu: int = EMBED_BATCH_SIZE_CPU,
    batch_gpu: int = EMBED_BATCH_SIZE_GPU,
):
    from fastembed import TextEmbedding

    root = repo_root or repo_root_from_here()
    if embed_use_gpu(root):
        _register_nvidia_dll_dirs(root)
        try:
            model = TextEmbedding(
                model_name=model_name,
                cache_dir=cache_dir,
                providers=["CUDAExecutionProvider"],
            )
            providers = model.model.model.get_providers()
            if "CUDAExecutionProvider" in providers:
                logger.info("FastEmbed providers: %s", providers)
                return model, "cuda", batch_gpu
            logger.warning("CUDAExecutionProvider unavailable (%s); using CPU", providers)
        except Exception as exc:
            logger.warning("GPU embed init failed (%s); using CPU", exc)

    model = TextEmbedding(model_name=model_name, cache_dir=cache_dir)
    logger.info("FastEmbed providers: %s", model.model.model.get_providers())
    return model, "cpu", batch_cpu
