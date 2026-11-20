"""Test JobRepository bang SQLite in-memory - khong can Postgres that chay."""

from pathlib import Path

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import NoSuchModuleError

from worker.db import database
from worker.db.database import make_session_factory
from worker.db.database_models import JobStatus
from worker.jobs.job_repository import JobRepository


def _make_repo() -> JobRepository:
    return JobRepository(session_factory=make_session_factory("sqlite:///:memory:"))


def test_create_and_get_job():
    repo = _make_repo()

    job = repo.create(filename="video.mp4", input_path=Path("in.mp4"), output_dir=Path("out"))
    fetched = repo.get(job.id)

    assert fetched is not None
    assert fetched.filename == "video.mp4"
    assert fetched.status == JobStatus.QUEUED


def test_get_unknown_job_returns_none():
    repo = _make_repo()

    assert repo.get("does-not-exist") is None


def test_update_status_changes_stage_and_status():
    repo = _make_repo()
    job = repo.create(filename="video.mp4", input_path=Path("in.mp4"), output_dir=Path("out"))

    repo.update_status(job.id, status=JobStatus.RUNNING, stage="transcribe")

    fetched = repo.get(job.id)
    assert fetched.status == JobStatus.RUNNING
    assert fetched.stage == "transcribe"


def test_update_status_on_unknown_job_is_a_noop():
    repo = _make_repo()

    repo.update_status("does-not-exist", status=JobStatus.RUNNING)  # khong raise


def test_list_all_returns_created_jobs():
    repo = _make_repo()
    first = repo.create(filename="a.mp4", input_path=Path("a.mp4"), output_dir=Path("a"))
    second = repo.create(filename="b.mp4", input_path=Path("b.mp4"), output_dir=Path("b"))

    jobs = repo.list_all()

    assert {j.id for j in jobs} == {first.id, second.id}


def test_delete_removes_job():
    repo = _make_repo()
    job = repo.create(filename="video.mp4", input_path=Path("in.mp4"), output_dir=Path("out"))

    repo.delete(job.id)

    assert repo.get(job.id) is None


def test_delete_unknown_job_is_a_noop():
    repo = _make_repo()

    repo.delete("does-not-exist")  # khong raise


def test_default_database_is_a_persistent_sqlite_file(tmp_path, monkeypatch):
    database_path = tmp_path / "storage" / "app.db"
    monkeypatch.setattr(database, "DEFAULT_DATABASE_URL", f"sqlite:///{database_path.as_posix()}")
    monkeypatch.setenv("DATABASE_URL", "")

    factory = make_session_factory()
    engine = factory.kw["bind"]
    try:
        assert database_path.exists()
        assert {"jobs", "custom_voices"} <= set(sa.inspect(engine).get_table_names())
    finally:
        engine.dispose()


def test_invalid_configured_database_url_is_not_silently_replaced():
    with pytest.raises(NoSuchModuleError):
        make_session_factory("unknown+driver://localhost/test")
