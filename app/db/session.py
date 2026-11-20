"""Tao session factory cho SQLAlchemy.

KHONG tao engine/session o module-level (khong co bien global ket noi san) de
tranh ket noi DB that ngay khi module nay duoc import - quan trong cho test
(tests/test_job_repository.py dung SQLite in-memory qua make_session_factory,
khong dung DEFAULT_DATABASE_URL/Postgres that).
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base

load_dotenv()

# Port 15432 (khong phai 5432 mac dinh) de khop docker-compose.yml - may dev co
# san Postgres native chiem 5432 (xem HANDOFF.md nhat ky 2026-07-03 lan 7).
DEFAULT_DATABASE_URL = (
    "postgresql+psycopg2://subtitle_studio:subtitle_studio@localhost:15432/subtitle_studio"
)


from pathlib import Path

def make_session_factory(database_url: str | None = None) -> sessionmaker:
    url = database_url or os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    try:
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        engine = create_engine(url, connect_args=connect_args)
        # Thử kết nối kiểm tra (đặc biệt khi dùng Postgres)
        with engine.connect():
            pass
    except Exception as exc:
        print(f"[db] Không thể kết nối tới {url} ({exc}). Tự động chuyển sang SQLite cục bộ.")
        storage_dir = Path("storage")
        storage_dir.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{storage_dir.resolve() / 'app.db'}"
        engine = create_engine(url, connect_args={"check_same_thread": False})

    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
