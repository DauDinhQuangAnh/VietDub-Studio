"""Chay THAT `alembic upgrade head` tren SQLite file tam - xac nhan baseline
tao du bang tren DB moi, idempotent khi chay lai, va "nhan nuoi" duoc DB co
san do create_all tao truoc khi du an co Alembic (kich ban may dev that)."""

from pathlib import Path

import sqlalchemy as sa
from alembic import command
from alembic.config import Config

from api.main import _run_database_migrations
from worker.db.database_models import Base

REPO_ROOT = Path(__file__).resolve().parents[1]


def _upgrade_head(db_url: str, monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", db_url)
    command.upgrade(Config(str(REPO_ROOT / "alembic.ini")), "head")


def _table_names(db_url: str) -> set[str]:
    engine = sa.create_engine(db_url)
    try:
        return set(sa.inspect(engine).get_table_names())
    finally:
        engine.dispose()


def _sqlite_url(tmp_path: Path, name: str) -> str:
    return f"sqlite:///{(tmp_path / name).as_posix()}"


def test_upgrade_creates_all_tables_on_fresh_db(tmp_path, monkeypatch):
    db_url = _sqlite_url(tmp_path, "fresh.db")

    _upgrade_head(db_url, monkeypatch)

    assert {"jobs", "custom_voices", "alembic_version"} <= _table_names(db_url)


def test_upgrade_twice_is_idempotent(tmp_path, monkeypatch):
    db_url = _sqlite_url(tmp_path, "twice.db")

    _upgrade_head(db_url, monkeypatch)
    _upgrade_head(db_url, monkeypatch)  # khong duoc loi "table already exists"

    assert "jobs" in _table_names(db_url)


def test_upgrade_adopts_db_created_by_create_all(tmp_path, monkeypatch):
    db_url = _sqlite_url(tmp_path, "existing.db")
    engine = sa.create_engine(db_url)
    Base.metadata.create_all(engine)
    engine.dispose()

    _upgrade_head(db_url, monkeypatch)

    assert "alembic_version" in _table_names(db_url)


def test_upgrade_removes_legacy_auth_columns(tmp_path, monkeypatch):
    db_url = _sqlite_url(tmp_path, "legacy-auth.db")
    engine = sa.create_engine(db_url)
    sa.MetaData()
    with engine.begin() as connection:
        connection.execute(
            sa.text(
                "CREATE TABLE users "
                "(id VARCHAR(36) PRIMARY KEY, email VARCHAR(255), "
                "password_hash VARCHAR(255), created_at DATETIME)"
            )
        )
        connection.execute(
            sa.text(
                "CREATE TABLE jobs "
                "(id VARCHAR(36) PRIMARY KEY, user_id VARCHAR(36), filename VARCHAR(255), "
                "input_path VARCHAR(1024), output_dir VARCHAR(1024), "
                "status VARCHAR(20), stage VARCHAR(64), error_message TEXT, "
                "created_at DATETIME, updated_at DATETIME)"
            )
        )
        connection.execute(
            sa.text(
                "CREATE TABLE custom_voices "
                "(id VARCHAR(36) PRIMARY KEY, user_id VARCHAR(36), name VARCHAR(255), "
                "ref_audio_path VARCHAR(1024), created_at DATETIME)"
            )
        )
    engine.dispose()

    _upgrade_head(db_url, monkeypatch)

    engine = sa.create_engine(db_url)
    try:
        inspector = sa.inspect(engine)
        assert "users" not in inspector.get_table_names()
        assert "user_id" not in {column["name"] for column in inspector.get_columns("jobs")}
        assert "user_id" not in {
            column["name"] for column in inspector.get_columns("custom_voices")
        }
    finally:
        engine.dispose()


def test_migration_schema_matches_orm_models(tmp_path, monkeypatch):
    """Cot do migration tao phai khop cot ORM khai bao - lech nghia la quen
    cap nhat 1 trong 2 phia khi doi schema."""
    db_url = _sqlite_url(tmp_path, "parity.db")

    _upgrade_head(db_url, monkeypatch)

    engine = sa.create_engine(db_url)
    try:
        inspector = sa.inspect(engine)
        for table_name, table in Base.metadata.tables.items():
            migrated_columns = {col["name"] for col in inspector.get_columns(table_name)}
            orm_columns = {col.name for col in table.columns}
            assert migrated_columns == orm_columns, f"Lech cot o bang {table_name}"
    finally:
        engine.dispose()


def test_api_startup_applies_migrations_to_sqlite(tmp_path, monkeypatch):
    database_url = _sqlite_url(tmp_path, "api-startup.db")
    monkeypatch.setenv("DATABASE_URL", database_url)

    _run_database_migrations()

    engine = sa.create_engine(database_url)
    try:
        assert {"jobs", "custom_voices", "alembic_version"} <= set(
            sa.inspect(engine).get_table_names()
        )
        with engine.connect() as connection:
            version = connection.exec_driver_sql(
                "SELECT version_num FROM alembic_version"
            ).scalar_one()
        assert version == "0002_remove_auth"
    finally:
        engine.dispose()
