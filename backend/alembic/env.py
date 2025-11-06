"""
Alembic environment configuration.
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import models base and settings
from app.core.config import settings
from app.models.base import Base

# Import all models so Alembic can detect them
from app.models.user import User  # noqa
from app.models.family import Family  # noqa
from app.models.child import ChildProfile  # noqa
from app.models.provider import Provider  # noqa
from app.models.venue import Venue  # noqa
from app.models.activity import Activity  # noqa
from app.models.recommendation import Recommendation  # noqa
from app.models.scraper_log import ScraperLog  # noqa

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the SQLAlchemy URL from settings
# Convert asyncpg URL to sync psycopg2 URL for Alembic
db_url = settings.database_url_str.replace("+asyncpg", "")
# Ensure we're using postgresql:// not postgresql+asyncpg://
if db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
config.set_main_option("sqlalchemy.url", db_url)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with a database connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    # Use sync engine for migrations (Alembic works better with sync)
    from sqlalchemy import create_engine
    url = config.get_main_option("sqlalchemy.url")
    sync_engine = create_engine(url, poolclass=pool.NullPool)

    with sync_engine.connect() as connection:
        do_run_migrations(connection)

    sync_engine.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
