import json
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, make_url, text

from app.auth.principal import Principal, Role
from app.auth.tokens import issue_token
from app.db import make_engine
from app.db.migrate import upgrade
from app.jobs import InMemoryJobStore
from app.main import create_app
from app.settings import Settings

FIXTURES = Path(__file__).parent / "fixtures" / "contract"
SETTINGS = Settings(auth_secret="test-secret-with-enough-length-for-hs256")


def load_fixture(relative: str) -> Any:
    return json.loads((FIXTURES / relative).read_text(encoding="utf-8"))


def token(subject: str, role: Role | str, settings: Settings = SETTINGS, **kwargs: Any) -> str:
    return issue_token(settings, Principal(subject, Role(role)), **kwargs)


def auth(subject: str = "demo-teacher", role: Role | str = Role.TEACHER) -> dict[str, str]:
    return {"Authorization": f"Bearer {token(subject, role)}"}


@pytest.fixture
def store() -> InMemoryJobStore:
    return InMemoryJobStore()


@pytest.fixture
def client(store: InMemoryJobStore) -> TestClient:
    return TestClient(create_app(SETTINGS, store=store))


# --- PostgreSQL ------------------------------------------------------------------------------


@pytest.fixture(scope="session")
def pg_engine() -> Iterator[Engine]:
    """Migrated test database from TEST_DATABASE_URL, created if missing. Never DATABASE_URL."""
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is not set: PostgreSQL integration tests skipped")
    _create_database(url)
    upgrade(url)
    engine = make_engine(url)
    yield engine
    engine.dispose()


@pytest.fixture
def pg(pg_engine: Engine) -> Engine:
    with pg_engine.begin() as connection:
        connection.execute(text("TRUNCATE classes CASCADE"))
    return pg_engine


def _create_database(url: str) -> None:
    target = make_url(url)
    server = create_engine(
        target.set(database="postgres"), isolation_level="AUTOCOMMIT", pool_pre_ping=True
    )
    with server.connect() as connection:
        exists = connection.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": target.database}
        ).first()
        if not exists:
            connection.execute(text(f'CREATE DATABASE "{target.database}"'))
    server.dispose()
