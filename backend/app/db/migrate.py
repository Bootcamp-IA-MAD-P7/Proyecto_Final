"""Apply the Alembic migrations: `python -m app.db.migrate` (`make migrate`)."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"


def upgrade(database_url: str | None = None) -> None:
    config = Config(str(ALEMBIC_INI))
    if database_url:
        config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
        config.attributes["configure_logger"] = False
    command.upgrade(config, "head")


if __name__ == "__main__":
    upgrade()
