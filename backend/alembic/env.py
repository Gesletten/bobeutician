"""Alembic environment configuration."""

import os
import sys
from logging.config import fileConfig
from typing import cast

from dotenv import load_dotenv
from alembic.config import Config
from alembic import context
from sqlalchemy import engine_from_config, pool

from app.db.models import Base

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


database_url = os.environ.get("DATABASE_URL")
# Use `getattr` for runtime attribute access on `alembic.context` so static
# analyzers (pylint/mypy) don't flag missing members. Annotate `config` as
# `Config` to provide helpful type information downstream.
config = cast(Config, getattr(context, "config"))

if database_url:
    config.set_main_option("sqlalchemy.url", database_url)
else:
    ini_url = config.get_main_option("sqlalchemy.url")
    if not ini_url:
        raise ValueError(
            "DATABASE_URL environment variable not set and sqlalchemy.url not in alembic.ini"
        )

if config.attributes.get("fileConfig", None):
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Configures context with just a URL
    Allows use without DBAPI available
    """
    url = config.get_main_option("sqlalchemy.url")
    getattr(context, "configure")(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with getattr(context, "begin_transaction")():
        getattr(context, "run_migrations")()


def run_migrations_online() -> None:
    """Creates an engine and associates connection with the context"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        getattr(context, "configure")(
            connection=connection, target_metadata=target_metadata
        )

        with getattr(context, "begin_transaction")():
            getattr(context, "run_migrations")()


if getattr(context, "is_offline_mode")():
    run_migrations_offline()
else:
    run_migrations_online()
