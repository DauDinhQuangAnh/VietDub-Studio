"""FastAPI tests for the local-only backend."""

import io
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

import backend.db as backend_db
from app.db.models import Base
from backend.main import app
from backend.share_links import create_file_share_token


@pytest.fixture()
def client(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    backend_db.set_session_factory(sessionmaker(bind=engine, expire_on_commit=False))
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path / "storage"))

    enqueued = []
    monkeypatch.setattr(
        "backend.routers.jobs.process_video_job",
        type("FakeTask", (), {"delay": staticmethod(lambda *args: enqueued.append(args))}),
    )

    test_client = TestClient(app)
    test_client.enqueued = enqueued
    test_client.storage_dir = tmp_path / "storage"
    yield test_client
    backend_db.set_session_factory(None)


def _create_job(client: TestClient) -> dict:
    response = client.post(
        "/api/jobs",
        data={"options": json.dumps({"dubbing": {"enabled": False}})},
        files={"file": ("video.mp4", io.BytesIO(b"fake-video"), "video/mp4")},
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_auth_routes_are_not_exposed(client):
    assert client.post("/api/auth/register", json={}).status_code == 404
    assert client.post("/api/auth/login", json={}).status_code == 404
    assert client.get("/api/auth/me").status_code == 404


def test_create_job_is_immediately_available_without_token(client):
    job = _create_job(client)

    assert job["status"] == "queued"
    assert "user_id" not in job
    assert client.get("/api/jobs").json()[0]["id"] == job["id"]
    assert client.get(f"/api/jobs/{job['id']}").status_code == 200
    assert client.enqueued and client.enqueued[0][0] == job["id"]


def test_delete_job_without_token(client):
    job = _create_job(client)

    response = client.delete(f"/api/jobs/{job['id']}")

    assert response.status_code == 200
    assert client.get("/api/jobs").json() == []


def test_refresh_cookies_is_local_endpoint(client, monkeypatch, tmp_path):
    cookies_path = tmp_path / "cookies.txt"
    monkeypatch.setenv("YTDLP_COOKIES_FILE", str(cookies_path))
    monkeypatch.setattr("backend.routers.admin.refresh_cookies", lambda path: 7)

    response = client.post("/api/admin/refresh-cookies")

    assert response.status_code == 200
    assert response.json() == {"cookie_count": 7, "path": str(cookies_path)}


def test_create_and_delete_custom_voice_without_token(client, monkeypatch):
    monkeypatch.setattr(
        "backend.routers.voices.subprocess.run",
        lambda cmd, **kwargs: __import__("pathlib").Path(cmd[-1]).write_bytes(b"fake wav"),
    )
    monkeypatch.setattr(
        "backend.routers.voices.probe_reference_seconds",
        lambda path: 5.0,
    )

    created = client.post(
        "/api/voices",
        data={"name": "Giong local"},
        files={"file": ("sample.webm", io.BytesIO(b"fake audio"), "audio/webm")},
    )

    assert created.status_code == 200
    voice_id = created.json()["id"]
    assert client.get("/api/voices").json()[0]["id"] == voice_id
    assert client.delete(f"/api/voices/{voice_id}").status_code == 200


def test_public_download_still_requires_signed_file_token(client):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("PUBLIC_LINK_SECRET", "test-public-secret")
    job = _create_job(client)
    output_dir = client.storage_dir / job["id"] / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = "video.vi.dubbed.mp4"
    (output_dir / filename).write_bytes(b"video")
    share_token = create_file_share_token(job["id"], filename)

    accepted = client.get(f"/api/public/jobs/{job['id']}/files/{filename}?token={share_token}")
    denied = client.get(f"/api/public/jobs/{job['id']}/files/{filename}?token=bad")

    assert accepted.status_code == 200
    assert accepted.content == b"video"
    assert denied.status_code == 403
    monkeypatch.undo()
