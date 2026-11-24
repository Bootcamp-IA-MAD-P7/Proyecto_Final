"""Engine of PostgreSQL and the readiness check of the database."""

from __future__ import annotations

import logging

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT_SECONDS = 3


def make_engine(database_url: str) -> Engine:
    return create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": CONNECT_TIMEOUT_SECONDS},
    )


def database_available(engine: Engine | None) -> bool:
    if engine is None:
        return False
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as error:
        # Only the type: the message can carry the host, the user or the connection string.
        logger.warning("database not available: %s", type(error).__name__)
        return False
