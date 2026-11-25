"""What the background processes share: stopping on a signal and opening the JobStore."""

from __future__ import annotations

import signal
import threading

from app.db import make_engine
from app.jobs import JobStore, PostgresJobStore
from app.settings import Settings


def stop_on_signals() -> threading.Event:
    """Event set by SIGTERM (docker stop) or SIGINT (Ctrl+C), so the process ends cleanly."""
    stop = threading.Event()
    for signum in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, lambda *_: stop.set())
    return stop


def open_store(settings: Settings) -> JobStore:
    """PostgreSQL JobStore from DATABASE_URL. Background processes have no in-memory fallback."""
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is not set")
    return PostgresJobStore(make_engine(settings.database_url))
