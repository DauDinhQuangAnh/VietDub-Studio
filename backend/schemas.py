"""Pydantic schema cho API - FE (frontend/src/lib/types.ts) phai khop cac
truong nay."""

from datetime import datetime

from pydantic import BaseModel

from app.db.models import CustomVoice, Job
from app.jobs.stages import stage_progress


class VideoAnalyzeIn(BaseModel):
    url: str


class QualityOptionOut(BaseModel):
    id: str
    label: str
    format: str


class VideoMetadataOut(BaseModel):
    url: str
    title: str
    thumbnail: str | None = None
    duration: int | None = None
    uploader: str | None = None
    source: str | None = None
    qualities: list[QualityOptionOut]


class JobOut(BaseModel):
    id: str
    filename: str
    status: str
    stage: str | None
    stage_label: str
    progress: float  # 0..1
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_job(cls, job: Job) -> "JobOut":
        fraction, label = stage_progress(job.stage)
        if job.status == "done":
            fraction, label = 1.0, "Hoàn thành"
        return cls(
            id=job.id,
            filename=job.filename,
            status=job.status.value,
            stage=job.stage,
            stage_label=label,
            progress=fraction,
            error_message=job.error_message,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )


class FileOut(BaseModel):
    name: str
    format: str
    size_bytes: int


class SubtitleGroupOut(BaseModel):
    language: str  # "goc" = phu de goc chua dich
    label: str
    files: list[FileOut]
    preview_text: str | None = None


class VideoOut(BaseModel):
    name: str
    language: str
    size_bytes: int


class JobFilesOut(BaseModel):
    videos: list[VideoOut]
    subtitles: list[SubtitleGroupOut]


class SubtitleSegmentOut(BaseModel):
    start: float
    end: float
    text: str
    speaker: str | None = None


class UpdateSubtitlesIn(BaseModel):
    segments: list[SubtitleSegmentOut]


class TranslateJobIn(BaseModel):
    target_language: str


class DubJobIn(BaseModel):
    target_language: str
    voice: str | None = None
    keep_original_audio: bool = False
    custom_voice_id: str | None = None


class CustomVoiceOut(BaseModel):
    id: str
    name: str
    created_at: datetime

    @classmethod
    def from_voice(cls, voice: CustomVoice) -> "CustomVoiceOut":
        return cls(id=voice.id, name=voice.name, created_at=voice.created_at)


class VoiceSampleIn(BaseModel):
    language: str
    voice: str
    rate_percent: int = 0
    pitch_hz: int = 0
