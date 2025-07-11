import asyncio
import os
import sys
from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Загрузка переменных
load_dotenv()

# Конфигурация Alembic
config = context.config
fileConfig(config.config_file_name)

# Сборка URL
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB")

config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database import Base 
import app.database

target_metadata = Base.metadata

from alembic.autogenerate import renderers
from pgvector.sqlalchemy import Vector

@renderers.dispatch_for(Vector)
def render_vector(type_, autogen_context):
    return f"Vector({type_.dimensions})"


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.begin() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
