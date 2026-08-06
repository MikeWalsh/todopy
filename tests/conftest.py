import os
import subprocess
import sys
from pathlib import Path
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
  AsyncConnection,
  AsyncSession,
  async_sessionmaker,
  create_async_engine
)

from app.db import Base, get_session
from app.main import app

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "postgresql+asyncpg://pgtest:pgtestfdsa@localhost:5443/todo_test"
)

# This is simple way - just bash the model into the db
# @pytest.fixture(scope="session")
# async def engine():
#     eng = create_async_engine(TEST_URL)
#     async with eng.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield eng
#     await eng.dispose()

# This is hard way, use alembic to run migrations
# When migrations accumulate, migrate into a template db and clone per test
# Important: Need to inject DATABASE_URL or will use the dev db
def _alembic(*args: str) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=PROJECT_ROOT,
        env={**os.environ, "DATABASE_URL": TEST_URL},
        #check=True # this option will just check the error code
        capture_output=True, # allows interrogating the result from alembic below
        text=True
        # alternatively wrap subprocess in try/except
        # or uv run pytest -s ???
    )
    if (result.returncode !=0):
        raise RuntimeError(
            f"alembic {' '.join(args)} failed (exit {result.returncode})\n"
            f"--- stdout ---\n{result.stdout}\n"
            f"--- stderr ---\n{result.stderr}"
        )

@pytest.fixture(scope="session")
async def engine():
    _alembic("upgrade", "head")
    eng = create_async_engine(TEST_URL)
    yield eng
    await eng.dispose()
    _alembic("downgrade", "base")

@pytest.fixture
async def connection(engine) -> AsyncGenerator[AsyncConnection]:
    """Single outer transaction per test, with rollback"""
    async with engine.connect() as conn:
        trans = await conn.begin()
        yield conn
        await trans.rollback()

@pytest.fixture
async def session(connection) -> AsyncGenerator[AsyncSession]:
    maker = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        # stops session.rollback() in tests unwinding the outer transaction?
        join_transaction_mode="create_savepoint" 
    )
    async with maker() as s:
        yield s

@pytest.fixture
async def client(session) -> AsyncGenerator[AsyncClient]:
    '''this works because the router session uses Depends instead of SessionLocal directly'''
    app.dependency_overrides[get_session] = lambda: session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()

