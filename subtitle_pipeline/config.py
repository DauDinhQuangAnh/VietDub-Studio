"""Cau hinh pipeline, doc tu bien moi truong (.env) de de dang doi model size
giua dev (VRAM han che, xem docs/memory/dev-machine-rtx4050.md) va production.
"""

import os
from dataclasses import dataclass


def _detect_default_device() -> str:
    env_device = os.environ.get("PIPELINE_DEVICE")
    if env_device:
        return env_device
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
    except Exception:
        pass
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
        return cls(
            whisper_model=os.environ.get("WHISPER_MODEL", "medium"),
            whisper_compute_type=os.environ.get("WHISPER_COMPUTE_TYPE", "int8_float16"),
            device=_detect_default_device(),
            language=os.environ.get("PIPELINE_LANGUAGE", "vi"),
            hf_token=os.environ.get("HF_TOKEN"),
            execution_mode=os.environ.get("EXECUTION_MODE", "CLOUD_FREE_API"),
        )
