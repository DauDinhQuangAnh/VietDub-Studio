"""FastAPI api cho UI React (web/). Chay:

    python -m uvicorn api.main:app --port 8000 --reload

Mac dinh dung SQLite trong storage/; Redis/Postgres qua Docker la tuy chon.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from api.routers import (  # noqa: E402
    catalog_routes,
    job_routes,
    media_routes,
    public_download_routes,
    settings_routes,
    voice_routes,
)


def _run_database_migrations() -> None:
    """Nang schema len ban moi nhat truoc khi nhan request."""
    from alembic import command
    from alembic.config import Config

    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    command.upgrade(config, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _run_database_migrations()
    yield


app = FastAPI(title="AI Subtitle Studio API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    # Vite dev server (web/) - dev dung proxy /api nen thuong khong can
    # CORS, nhung van mo cho truong hop goi thang cong 8000.
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(job_routes.router, prefix="/api")
app.include_router(media_routes.router, prefix="/api")
app.include_router(catalog_routes.router, prefix="/api")
app.include_router(settings_routes.router, prefix="/api")
app.include_router(public_download_routes.router, prefix="/api")
app.include_router(voice_routes.router, prefix="/api")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
