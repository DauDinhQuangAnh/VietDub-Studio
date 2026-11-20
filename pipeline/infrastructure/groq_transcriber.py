"""Cloud-based Speech-To-Text adapter using Groq's free Whisper Large-v3 API.

Groq API cung cấp whisper-large-v3 miễn phí với tốc độ cực nhanh (hàng trăm từ/s)
và KHÔNG tốn VRAM GPU local. Khi file audio lớn hơn 20MB, adapter tự động nén sang
file MP3 nhẹ trước khi upload để không bị vượt quá giới hạn 25MB của Groq.
Khi không có GROQ_API_KEY hoặc quá trình gọi API gặp lỗi, adapter tự động fallback
sang FasterWhisperTranscriber chạy trên CPU.
"""

from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from contextlib import suppress
from pathlib import Path

from pipeline.domain.subtitle_types import TranscriptSegment
from pipeline.infrastructure.faster_whisper_transcriber import FasterWhisperTranscriber

GROQ_TRANSCRIPTION_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
DEFAULT_GROQ_MODEL = "whisper-large-v3"
MAX_GROQ_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB safety limit


def _encode_multipart_formdata(
    fields: dict[str, str], files: dict[str, tuple[str, bytes, str]]
) -> tuple[bytes, str]:
    boundary = "----WebKitFormBoundary" + os.urandom(16).hex()
    body = bytearray()

    for key, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
        body.extend(f"{value}\r\n".encode())

    for key, (filename, content, content_type) in files.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(
            f'Content-Disposition: form-data; name="{key}"; filename="{filename}"\r\n'.encode()
        )
        body.extend(f"Content-Type: {content_type}\r\n\r\n".encode())
        body.extend(content)
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode())
    content_type_header = f"multipart/form-data; boundary={boundary}"
    return bytes(body), content_type_header


def _compress_audio_if_needed(audio_path: Path) -> tuple[Path, bool]:
    """Khái quát nén audio WAV sang MP3 nhẹ (16kHz mono 48k) nếu dung lượng > 20MB.

    Trả vềE(path_file_can_dung, is_temp).
    """
    if (
        audio_path.stat().st_size <= MAX_GROQ_FILE_SIZE_BYTES
        and audio_path.suffix.lower() == ".mp3"
    ):
        return audio_path, False

    try:
        temp_mp3 = audio_path.parent / f"_groq_compressed_{audio_path.stem}.mp3"
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(audio_path),
            "-ac",
            "1",
            "-ar",
            "16000",
            "-b:a",
            "48k",
            str(temp_mp3),
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if temp_mp3.exists() and temp_mp3.stat().st_size > 0:
            return temp_mp3, True
    except Exception:
        pass

    return audio_path, False


class CloudGroqTranscriber:
    def __init__(
        self,
        model_name: str = DEFAULT_GROQ_MODEL,
        api_key: str | None = None,
        language: str | None = None,
    ):
        self._model_name = model_name
        self._api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self._language = language

    def __enter__(self) -> CloudGroqTranscriber:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass

    def transcribe(self, audio_path: Path) -> tuple[list[TranscriptSegment], str]:
        if self._api_key:
            try:
                return self._transcribe_via_groq(audio_path)
            except Exception as exc:
                print(f"[transcribe] Groq API lỗi ({exc}) - chuyển sang CPU Faster-Whisper")

        # Fallback to CPU Faster-Whisper if GROQ_API_KEY is not configured or fails
        fallback = FasterWhisperTranscriber(
            model_size="base", compute_type="int8", device="cpu", language=self._language
        )
        with fallback as tr:
            return tr.transcribe(audio_path)

    def _transcribe_via_groq(self, audio_path: Path) -> tuple[list[TranscriptSegment], str]:
        file_to_send, is_temp = _compress_audio_if_needed(audio_path)
        try:
            file_bytes = file_to_send.read_bytes()
            fields = {
                "model": self._model_name,
                "response_format": "verbose_json",
            }
            if self._language:
                fields["language"] = self._language

            content_type_file = (
                "audio/mpeg" if file_to_send.suffix.lower() == ".mp3" else "audio/wav"
            )
            files = {
                "file": (file_to_send.name, file_bytes, content_type_file),
            }

            body, content_type = _encode_multipart_formdata(fields, files)
            req = urllib.request.Request(
                GROQ_TRANSCRIPTION_URL,
                data=body,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": content_type,
                },
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            segments_raw = data.get("segments") or []
            detected_language = data.get("language") or self._language or "vi"

            result = []
            for seg in segments_raw:
                text = (seg.get("text") or "").strip()
                if text:
                    result.append(
                        TranscriptSegment(
                            start=float(seg.get("start", 0.0)),
                            end=float(seg.get("end", 0.0)),
                            text=text,
                        )
                    )

            if not result and data.get("text"):
                result.append(
                    TranscriptSegment(
                        start=0.0,
                        end=float(data.get("duration", 10.0)),
                        text=data["text"].strip(),
                    )
                )

            return result, detected_language
        finally:
            if is_temp and file_to_send.exists():
                with suppress(OSError):
                    file_to_send.unlink()
