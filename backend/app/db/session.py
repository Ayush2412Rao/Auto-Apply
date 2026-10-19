import sys
from pathlib import Path
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, Session

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.config import settings

Base = declarative_base()

async_db_url = settings.DATABASE_URL
if async_db_url.startswith("sqlite:///"):
    async_db_url = async_db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
elif async_db_url.startswith("postgresql://"):
    async_db_url = async_db_url.replace("postgresql://", "postgresql+asyncpg:///")

sync_db_url = settings.SYNC_DATABASE_URL
if "aiosqlite" in sync_db_url:
    sync_db_url = sync_db_url.replace("+aiosqlite", "")
if "asyncpg" in sync_db_url:
    sync_db_url = sync_db_url.replace("+asyncpg", "")

connect_args = {"check_same_thread": False} if "sqlite" in async_db_url else {}

async_engine = create_async_engine(
    async_db_url,
    echo=False,
    connect_args=connect_args,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

sync_engine = create_engine(
    sync_db_url,
    echo=False,
    connect_args=connect_args,
    future=True
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_sync_db() -> Generator[Session, None, None]:
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
