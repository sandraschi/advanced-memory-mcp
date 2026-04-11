from typing import Any

import psutil
from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel

try:
    import pynvml

    PNVML_AVAILABLE = True
except ImportError:
    PNVML_AVAILABLE = False

router = APIRouter(prefix="/hardware", tags=["hardware"])
model_router = APIRouter(prefix="/model", tags=["model"])


class GPUMetrics(BaseModel):
    model: str
    utilization: str
    vram_used: str
    vram_total: str
    temperature: str


class CPUMetrics(BaseModel):
    utilization: str
    cores: int


class MemoryMetrics(BaseModel):
    used: str
    total: str


class HardwareStats(BaseModel):
    gpu: GPUMetrics
    cpu: CPUMetrics
    memory: MemoryMetrics


@router.get("/detect", response_model=HardwareStats)
async def detect_hardware() -> HardwareStats:
    """Detect current hardware status and utilization."""

    # 1. CPU Metrics
    cpu_util = psutil.cpu_percent(interval=None)
    cpu_cores = psutil.cpu_count(logical=True) or 0

    # 2. Memory Metrics
    mem = psutil.virtual_memory()
    mem_used_gb = mem.used / (1024**3)
    mem_total_gb = mem.total / (1024**3)

    # 3. GPU Metrics (NVIDIA)
    gpu_metrics = {
        "model": "Unknown GPU",
        "utilization": "0%",
        "vram_used": "0 GB",
        "vram_total": "0 GB",
        "temperature": "0\u00b0C",
    }

    if PNVML_AVAILABLE:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count > 0:
                # Use the first GPU by default
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                name = pynvml.nvmlDeviceGetName(handle)
                # Handle bytes returned in some versions
                if isinstance(name, bytes):
                    name = name.decode("utf-8")

                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)

                gpu_metrics = {
                    "model": name,
                    "utilization": f"{util.gpu}%",
                    "vram_used": f"{mem_info.used / (1024**3):.1f} GB",
                    "vram_total": f"{mem_info.total / (1024**3):.1f} GB",
                    "temperature": f"{temp}\u00b0C",
                }
            pynvml.nvmlShutdown()
        except Exception as e:
            logger.warning(f"Failed to query NVIDIA GPU: {e}")
            gpu_metrics["model"] = "No NVIDIA GPU detected"

    return HardwareStats(
        gpu=GPUMetrics(**gpu_metrics),
        cpu=CPUMetrics(utilization=f"{cpu_util:.0f}%", cores=cpu_cores),
        memory=MemoryMetrics(used=f"{mem_used_gb:.1f} GB", total=f"{mem_total_gb:.1f} GB"),
    )


@model_router.post("/optimize")
async def optimize_model_params(params: dict[str, Any]) -> dict[str, Any]:
    """
    Optimize model parameters based on current hardware capacity.
    Provides recommendations for Ollama/Local LLM.
    """
    # Handle both flat and nested structures for compatibility
    actual_params = params.get("params", params) if "params" in params and len(params) == 1 else params

    # 1. System RAM check
    mem = psutil.virtual_memory()
    available_gb = mem.available / (1024**3)

    # 2. VRAM check
    vram_available_gb = 0.0
    gpu_detected = False

    if PNVML_AVAILABLE:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count > 0:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                vram_available_gb = (mem_info.total - mem_info.used) / (1024**3)
                gpu_detected = True
            pynvml.nvmlShutdown()
        except Exception:
            pass

    recommendations = []
    optimized_params = actual_params.copy()

    # Optimization logic for Ollama parameters
    if gpu_detected:
        if vram_available_gb > 2.0:
            recommendations.append(
                f"GPU detected with {vram_available_gb:.1f}GB free VRAM. Enabling metal/cuda acceleration."
            )
            # Suggest high num_gpu for small models, or partial for large ones
            optimized_params["num_gpu"] = 35  # Default high to push layers to GPU
        else:
            recommendations.append("GPU memory is nearly full. Suggesting CPU fallback for some layers.")
            optimized_params["num_gpu"] = 0
    else:
        recommendations.append("No specialized GPU detected. Optimizing for multi-threaded CPU inference.")
        optimized_params["num_gpu"] = 0
        optimized_params["num_thread"] = psutil.cpu_count(logical=False) or 4

    if available_gb < 4.0:
        recommendations.append(
            "System RAM is critically low. Use 4-bit quantization or smaller models (e.g. Phi-3, Gemma-2B)."
        )
        optimized_params["num_ctx"] = 2048  # Reduce context window
    elif available_gb < 12.0:
        recommendations.append("System RAM is moderate. Balanced context window (4096) recommended.")
        optimized_params["num_ctx"] = 4096
    else:
        recommendations.append("Plenty of system RAM available. High context window (8192+) supported.")
        optimized_params["num_ctx"] = 8192

    return {
        "success": True,
        "recommendations": recommendations,
        "optimized_params": optimized_params,
        "message": "Model parameters optimized for detected hardware capacity.",
    }
