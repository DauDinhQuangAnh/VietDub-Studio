from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from api.database import job_repo
from api.public_download_links import ShareLinkError, verify_file_share_token

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/jobs/{job_id}/files/{name}")
def download_shared_file(job_id: str, name: str, token: str = Query(...)) -> FileResponse:
    try:
        verify_file_share_token(token, job_id=job_id, filename=name)
    except ShareLinkError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    job = job_repo().get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy tác vụ.")

    output_dir = Path(job.output_dir)
    target = next((f for f in output_dir.glob("*.*") if f.name == name and f.is_file()), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy tệp.")

    media_type = "video/mp4" if target.suffix.lower() in (".mp4", ".mkv") else None
    return FileResponse(target, media_type=media_type, filename=target.name)
