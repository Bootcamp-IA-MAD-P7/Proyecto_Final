"""`python -m app.worker` and `python -m app.maintenance`, stopped before they block."""

import os
import subprocess
import sys
import threading
from pathlib import Path

import pytest

import app.maintenance.__main__ as maintenance_main
import app.worker.__main__ as worker_main
from app.jobs import InMemoryJobStore

BACKEND = Path(__file__).resolve().parents[1]


def stopped() -> threading.Event:
    event = threading.Event()
    event.set()
    return event


def test_worker_needs_a_database():
    env = {k: v for k, v in os.environ.items() if k != "DATABASE_URL"}
    process = subprocess.run(
        [sys.executable, "-m", "app.worker"], cwd=BACKEND, env=env, capture_output=True, text=True
    )

    assert process.returncode != 0
    assert "DATABASE_URL is not set" in process.stderr


def test_worker_entry_point_builds_and_stops(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(worker_main, "open_store", lambda settings: InMemoryJobStore())
    monkeypatch.setattr(worker_main, "stop_on_signals", stopped)

    worker_main.main()


def test_maintenance_entry_point_builds_and_stops(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(maintenance_main, "stop_on_signals", stopped)

    maintenance_main.main()
