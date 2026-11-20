"""Cau hinh va quan ly may local: cookie tai video va danh sach job."""

import asyncio
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

from api.api_schemas import JobOut
from api.database import job_repo
from pipeline.infrastructure.browser_cookie_manager import (
    DEFAULT_COOKIES_PATH,
    refresh_cookies,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/jobs", response_model=list[JobOut])
def list_all_jobs() -> list[JobOut]:
    return [JobOut.from_job(j) for j in job_repo().list_all()]


@router.post("/refresh-cookies")
async def refresh_cookies_endpoint() -> dict:
    """Chay AN (headless) lai profile trinh duyet da dang nhap tu truoc
    (`python -m pipeline.infrastructure.browser_cookie_manager --setup` -
    phai chay 1 lan thu cong truoc, script nay khong the tu dang nhap).
    Chay trong thread rieng (asyncio.to_thread) vi Playwright sync API chan
    (blocking), tranh treo event loop cua FastAPI.
    """
    cookies_path = Path(os.environ.get("YTDLP_COOKIES_FILE", str(DEFAULT_COOKIES_PATH)))
    try:
        count = await asyncio.to_thread(refresh_cookies, cookies_path)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Khong lam moi duoc cookie: {exc}. Neu chua tung chay setup, "
                "hay chay tren may chu (khong qua API): "
                "python -m pipeline.infrastructure.browser_cookie_manager --setup"
            ),
        ) from exc
    return {"cookie_count": count, "path": str(cookies_path)}
