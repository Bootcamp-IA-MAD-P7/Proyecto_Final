"""Settings of the backend, read from the environment (backend/.env.example lists them)."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

from app.auth.principal import Role

DEFAULT_DEV_USERS = "demo-teacher:teacher,demo-student:student,coteach-service:service"


def _flag(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


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
        )
