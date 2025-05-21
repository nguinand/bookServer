import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from app.db.db_models.base import Base

from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# Get the Alembic Config object
config = context.config

# Override sqlalchemy.url from environment variable
database_url = os.environ.get("DATABASE_CONNECTION_STRING")
if not database_url:
    raise RuntimeError("DATABASE_CONNECTION_STRING is not set in the environment")

config.set_main_option("sqlalchemy.url", database_url)

# Set up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for 'autogenerate'
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
