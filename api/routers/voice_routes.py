"""CRUD giong long tieng da clone - nguoi dung upload/ghi am 1 doan mau, luu
lai file tham chieu de dung lai nhieu lan (xem
pipeline/infrastructure/tts_vieneu.py + HANDOFF.md muc 6p). KHONG
luu speaker embedding vao DB - `VieNeuCloneSynthesizer` tu ma hoa lai
`ref_audio_path` moi lan long tieng (1 lan/job, khong phai 1 lan/segment).
"""

import subprocess
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from api.api_schemas import CustomVoiceOut
from api.database import custom_voice_repo
from pipeline.infrastructure.vieneu_tts import (
    MIN_REFERENCE_SECONDS,
    probe_reference_seconds,
)
from worker.config import AppConfig

router = APIRouter(prefix="/voices", tags=["voices"])

MAX_FILE_SIZE_MB = 20


def _voices_dir() -> Path:
    return AppConfig.from_env().storage_dir / "custom_voices"


def get_voice(voice_id: str):
    voice = custom_voice_repo().get(voice_id)
    if voice is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy giọng đã tạo.")
    return voice


@router.post("", response_model=CustomVoiceOut)
def create_voice(
    name: str = Form(...),
    file: UploadFile = File(...),
) -> CustomVoiceOut:
    if not name.strip():
        raise HTTPException(status_code=400, detail="Vui lòng đặt tên cho giọng.")
    data = file.file.read()
    if len(data) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"Tệp vượt quá giới hạn {MAX_FILE_SIZE_MB} MB.")

    voice_id = str(uuid.uuid4())
    voice_dir = _voices_dir()
    voice_dir.mkdir(parents=True, exist_ok=True)
    upload_suffix = Path(file.filename or "audio.webm").suffix or ".webm"
    raw_path = voice_dir / f"{voice_id}_raw{upload_suffix}"
    raw_path.write_bytes(data)

    ref_path = voice_dir / f"{voice_id}.wav"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(raw_path), "-ar", "24000", "-ac", "1", str(ref_path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Không xử lý được tệp âm thanh. Chi tiết kỹ thuật: {exc.stderr}",
        ) from exc
    finally:
        raw_path.unlink(missing_ok=True)

    duration = probe_reference_seconds(ref_path)
    if duration < MIN_REFERENCE_SECONDS:
        ref_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail=(
                f"Bản ghi quá ngắn ({duration:.1f} giây). Cần thu âm tối thiểu "
                f"{MIN_REFERENCE_SECONDS:.0f} giây."
            ),
        )

    voice = custom_voice_repo().create(name=name.strip(), ref_audio_path=str(ref_path))
    return CustomVoiceOut.from_voice(voice)


@router.get("", response_model=list[CustomVoiceOut])
def list_voices() -> list[CustomVoiceOut]:
    return [CustomVoiceOut.from_voice(v) for v in custom_voice_repo().list_all()]


@router.delete("/{voice_id}")
def delete_voice(voice_id: str) -> dict:
    voice = get_voice(voice_id)
    Path(voice.ref_audio_path).unlink(missing_ok=True)
    custom_voice_repo().delete(voice_id)
    return {"deleted": voice_id}
