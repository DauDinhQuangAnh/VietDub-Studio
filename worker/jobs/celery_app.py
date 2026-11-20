"""Cau hinh Celery cho Redis hoac queue SQLite local."""

import os
import socket
from pathlib import Path
from urllib.parse import urlsplit

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

LOCAL_QUEUE_DB_PATH = Path(__file__).resolve().parents[2] / "storage" / "celery.db"


def _resolve_broker_url() -> tuple[str, str]:
    configured = os.environ.get("REDIS_URL", "").strip()
    if configured.startswith("sqla+sqlite:"):
        return configured, configured.replace("sqla+sqlite:", "db+sqlite:", 1)

    if not configured:
        LOCAL_QUEUE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        database_path = LOCAL_QUEUE_DB_PATH.as_posix()
        return f"sqla+sqlite:///{database_path}", f"db+sqlite:///{database_path}"

    parsed_url = urlsplit(configured)
    if parsed_url.scheme in {"redis", "rediss"} and parsed_url.hostname in {
        "localhost",
        "127.0.0.1",
    }:
        try:
            with socket.create_connection(
                (parsed_url.hostname, parsed_url.port or 6379), timeout=0.3
            ):
                return configured, configured
        except OSError:
            print("[celery] Redis cục bộ chưa sẵn sàng; dùng queue SQLite trong storage/.")
            LOCAL_QUEUE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            database_path = LOCAL_QUEUE_DB_PATH.as_posix()
            return f"sqla+sqlite:///{database_path}", f"db+sqlite:///{database_path}"

    return configured, configured


broker_url, result_backend = _resolve_broker_url()
celery_app = Celery("subtitle_studio", broker=broker_url, backend=result_backend)
celery_app.conf.worker_concurrency = 1
celery_app.conf.task_track_started = True

celery_app.autodiscover_tasks(["worker.jobs"])
