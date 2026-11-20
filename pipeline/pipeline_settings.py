"""Cau hinh pipeline, doc tu bien moi truong (.env) de de dang doi model size
giua dev (VRAM han che, xem docs/memory/dev-machine-rtx4050.md) va production.
"""

import os
from dataclasses import dataclass


def _detect_default_device() -> str:
    env_device = os.environ.get("PIPELINE_DEVICE", "").strip().lower()
    if env_device and not env_device.startswith("cuda"):
        return env_device

    cuda_error: Exception | None = None
    try:
        import torch

        cuda_available = torch.cuda.is_available()
    except (ImportError, OSError, RuntimeError) as exc:
        cuda_available = False
        cuda_error = exc

    if cuda_available:
        return env_device or "cuda"
    if env_device:
        reason = f" ({cuda_error})" if cuda_error else ""
        print(f"[config] CUDA không khả dụng{reason}; tự chuyển sang CPU.")
    return "cpu"


@dataclass
class PipelineConfig:
    whisper_model: str = "medium"
    whisper_compute_type: str = "int8_float16"
    device: str = "cpu"
    language: str = "vi"
    hf_token: str | None = None
    execution_mode: str = "CLOUD_FREE_API"  # "CLOUD_FREE_API" or "GPU_LOCAL"

    @classmethod
    def from_env(cls) -> "PipelineConfig":
        device = _detect_default_device()
        compute_type = os.environ.get("WHISPER_COMPUTE_TYPE", "int8_float16")
        if device == "cpu" and compute_type in {"float16", "int8_float16"}:
            compute_type = "int8"
        return cls(
            whisper_model=os.environ.get("WHISPER_MODEL", "medium"),
            whisper_compute_type=compute_type,
            device=device,
            language=os.environ.get("PIPELINE_LANGUAGE", "vi"),
            hf_token=os.environ.get("HF_TOKEN"),
            execution_mode=os.environ.get("EXECUTION_MODE", "CLOUD_FREE_API"),
        )
