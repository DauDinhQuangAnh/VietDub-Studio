"""Cau hinh Celery.

worker_concurrency = 1 vi may dev VRAM han che (6GB), khong the chay 2 job AI
pipeline dong thoi tren GPU - xem docs/memory/dev-machine-rtx4050.md.

Chay worker bang: python -m celery -A app.jobs.celery_app worker --loglevel=info
(dung `python -m celery`, KHONG dung lenh `celery` truc tiep, de dam bao thu muc
goc repo nam trong sys.path va cac import app.*/subtitle_pipeline.* hoat dong
dung khi Celery nap task tu app.jobs.tasks).
"""

import os
import socket
from pathlib import Path

from celery import Celery
from dotenv import load_dotenv

load_dotenv()


def _resolve_broker_url() -> tuple[str, str]:
    configured = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    if configured.startswith("redis://localhost") or configured.startswith("redis://127.0.0.1"):
        try:
            with socket.create_connection(("localhost", 6379), timeout=0.3):
                return configured, configured
        except Exception:
            print(
                "[celery] Không tìm thấy Redis trên localhost:6379. "
                "Tự động dùng SQLite broker cục bộ."
            )
            storage_dir = Path("storage").resolve()
            storage_dir.mkdir(parents=True, exist_ok=True)
            db_path = storage_dir / "celery.db"
            return f"sqla+sqlite:///{db_path}", f"db+sqlite:///{db_path}"
    return configured, configured


broker_url, result_backend = _resolve_broker_url()
celery_app = Celery("subtitle_studio", broker=broker_url, backend=result_backend)
celery_app.conf.worker_concurrency = 1
celery_app.conf.task_track_started = True

celery_app.autodiscover_tasks(["app.jobs"])
