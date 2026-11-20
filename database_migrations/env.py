"""Alembic env: doc DATABASE_URL tu .env/bien moi truong (nhat quan voi
worker/db/session.py) thay vi hardcode URL trong alembic.ini - doi DB chi can
sua 1 cho duy nhat."""

import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import make_url

from worker.db.database import DEFAULT_DATABASE_URL
from worker.db.database_models import Base

load_dotenv()

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ConfigParser hieu "%" la ky tu interpolation - escape de password/query
# string chua "%" khong lam vo config.
database_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
parsed_database_url = make_url(database_url)
if (
    parsed_database_url.get_backend_name() == "sqlite"
    and parsed_database_url.database
    and parsed_database_url.database != ":memory:"
):
    Path(parsed_database_url.database).parent.mkdir(parents=True, exist_ok=True)
config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
