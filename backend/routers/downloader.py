"""Router tải video/audio trực tiếp không qua pipeline dịch/lồng tiếng.
"""

import uuid
from pathlib import Path
from pydantic import BaseModel, HttpUrl
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from backend.security import AuthUser, get_current_user
from subtitle_pipeline.infrastructure.downloader_ytdlp import (
    analyze_video,
    download_video,
    VideoMetadata,
    sanitize_filename,
)

router = APIRouter(prefix="/downloader", tags=["downloader"])

DOWNLOAD_DIR = Path("storage/downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


class VideoInfoRequest(BaseModel):
    url: str


class VideoDownloadRequest(BaseModel):
    url: str
    quality: str = "best"
    extract_audio_only: bool = False


@router.post("/info")
def get_video_info(body: VideoInfoRequest, user: AuthUser = Depends(get_current_user)) -> dict:
    try:
        meta = analyze_video(body.url)
        return {
            "url": meta.url,
            "title": meta.title,
            "thumbnail": meta.thumbnail,
            "duration": meta.duration,
            "uploader": meta.uploader,
            "source": meta.source,
            "qualities": [
                {"id": q.id, "label": q.label, "format": q.format} for q in meta.qualities
            ],
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/download")
def download_direct(body: VideoDownloadRequest, user: AuthUser = Depends(get_current_user)):
    try:
        meta = analyze_video(body.url)
        clean_title = sanitize_filename(meta.title)
        file_id = uuid.uuid4().hex[:8]

        if body.extract_audio_only:
            output_name = f"{clean_title}_{file_id}.mp3"
            output_path = DOWNLOAD_DIR / output_name
            raw_video = DOWNLOAD_DIR / f"_temp_{file_id}.mp4"
            download_video(body.url, body.quality, raw_video)

            # Convert to MP3 via ffmpeg
            import subprocess

            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(raw_video),
                "-vn",
                "-acodec",
                "libmp3lame",
                "-q:a",
                "2",
                str(output_path),
            ]
            subprocess.run(cmd, check=True)
            if raw_video.exists():
                raw_video.unlink()
            media_type = "audio/mpeg"
        else:
            output_name = f"{clean_title}_{file_id}.mp4"
            output_path = DOWNLOAD_DIR / output_name
            download_video(body.url, body.quality, output_path)
            media_type = "video/mp4"

        return FileResponse(
            output_path,
            media_type=media_type,
            filename=output_name,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Lỗi tải video: {exc}") from exc
