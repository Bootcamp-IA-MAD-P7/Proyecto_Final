"""Settings of the backend, read from the environment (backend/.env.example lists them)."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

from app.auth.principal import Role

DEFAULT_DEV_USERS = "demo-teacher:teacher,demo-student:student,coteach-service:service"


def _flag(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _number(env: Mapping[str, str], name: str, default: float) -> float:
    value = float(env.get(name) or default)
    if value < 0:
        raise ValueError(f"{name} cannot be negative")
    return value


def _dev_users(value: str) -> dict[str, Role]:
    users: dict[str, Role] = {}
    for entry in filter(None, (item.strip() for item in value.split(","))):
        subject, _, role = entry.partition(":")
        users[subject.strip()] = Role(role.strip())
    return users


@dataclass(frozen=True)
class Settings:
    database_url: str | None = None
    """SQLAlchemy URL of PostgreSQL. Without it, /ready reports the database as unavailable."""
    auth_secret: str | None = None
    """Key of the tokens (HS256, 32+ characters). Without a valid one, /v1 always answers 401."""
    auth_audience: str = "coteach-ai-api"
    auth_issuer: str = "coteach-ai-dev-issuer"
    auth_dev_issuer: bool = False
    """Exposes POST /dev/token. Only for development and local demos (spec api-access)."""
    auth_dev_token_ttl_seconds: int = 3600
    auth_dev_users: Mapping[str, Role] = field(
        default_factory=lambda: _dev_users(DEFAULT_DEV_USERS)
    )
    frontend_origin: str | None = None
    """Only origin allowed by CORS. Without it, no cross-origin request is allowed."""
    review_period_hours: float = 24
    """Time the teacher has to review a result before it is published (PRD RF-05, provisional)."""
    fake_stage_seconds: float = 2
    """Wait of FakePipeline in each stage, to see the progress in the web."""
    worker_poll_seconds: float = 1
    """Wait of the worker when the queue is empty or the database is not available."""
    maintenance_interval_seconds: float = 60
    """Time between two maintenance cycles."""

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        env = os.environ if env is None else env
        defaults = cls()
        return cls(
            database_url=env.get("DATABASE_URL") or None,
            auth_secret=env.get("AUTH_SECRET") or None,
            auth_audience=env.get("AUTH_AUDIENCE") or defaults.auth_audience,
            auth_issuer=env.get("AUTH_ISSUER") or defaults.auth_issuer,
            auth_dev_issuer=_flag(env.get("AUTH_DEV_ISSUER")),
            auth_dev_token_ttl_seconds=int(
                env.get("AUTH_DEV_TOKEN_TTL_SECONDS") or defaults.auth_dev_token_ttl_seconds
            ),
            auth_dev_users=_dev_users(env.get("AUTH_DEV_USERS") or DEFAULT_DEV_USERS),
            frontend_origin=env.get("FRONTEND_ORIGIN") or None,
            review_period_hours=_number(env, "REVIEW_PERIOD_HOURS", defaults.review_period_hours),
            fake_stage_seconds=_number(env, "FAKE_STAGE_SECONDS", defaults.fake_stage_seconds),
            worker_poll_seconds=_number(env, "WORKER_POLL_SECONDS", defaults.worker_poll_seconds),
            maintenance_interval_seconds=_number(
                env, "MAINTENANCE_INTERVAL_SECONDS", defaults.maintenance_interval_seconds
            ),
        )
