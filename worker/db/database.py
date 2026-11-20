"""Tao session factory cho SQLAlchemy."""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from worker.db.database_models import Base

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_URL = f"sqlite:///{(PROJECT_ROOT / 'storage' / 'app.db').as_posix()}"


def make_session_factory(database_url: str | None = None) -> sessionmaker:
    url = database_url or os.environ.get("DATABASE_URL") or DEFAULT_DATABASE_URL
    is_sqlite = url.startswith("sqlite")
    if is_sqlite:
        database_path = url.removeprefix("sqlite:///")
        if database_path and database_path != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    connect_args = {"check_same_thread": False} if is_sqlite else {}
    engine = create_engine(url, connect_args=connect_args)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
