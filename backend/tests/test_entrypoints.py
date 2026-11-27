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
from app.main import create_app
from app.settings import DEVELOPMENT_AUTH_SECRET, MIN_AUTH_SECRET_LENGTH
from app.storage import DiskAudioStorage

BACKEND = Path(__file__).resolve().parents[1]
VALID_PRODUCTION_SECRET = "custom-production-secret-with-at-least-32-characters"


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
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.setattr(worker_main, "open_store", lambda settings: InMemoryJobStore())
    monkeypatch.setattr(worker_main, "stop_on_signals", stopped)

    worker_main.main()


def test_maintenance_entry_point_builds_and_stops(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.setattr(maintenance_main, "open_store", lambda settings: InMemoryJobStore())
    monkeypatch.setattr(
        maintenance_main, "DiskAudioStorage", lambda directory: DiskAudioStorage(tmp_path)
    )
    monkeypatch.setattr(maintenance_main, "stop_on_signals", stopped)

    maintenance_main.main()


@pytest.mark.parametrize(
    "secret",
    [None, "", "a" * (MIN_AUTH_SECRET_LENGTH - 1), DEVELOPMENT_AUTH_SECRET],
)
def test_entry_points_reject_an_invalid_production_secret(monkeypatch: pytest.MonkeyPatch, secret):
    monkeypatch.setenv("APP_ENV", "production")
    if secret is None:
        monkeypatch.delenv("AUTH_SECRET", raising=False)
    else:
        monkeypatch.setenv("AUTH_SECRET", secret)

    for entry_point in (create_app, worker_main.main, maintenance_main.main):
        with pytest.raises(ValueError) as error:
            entry_point()

        assert "AUTH_SECRET" in str(error.value)
        if secret:
            assert secret not in str(error.value)


@pytest.mark.parametrize(
    "entry_point",
    [create_app, worker_main.main, maintenance_main.main],
)
def test_entry_points_accept_a_valid_production_secret(
    monkeypatch: pytest.MonkeyPatch, tmp_path, entry_point
):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("AUTH_SECRET", VALID_PRODUCTION_SECRET)
    if entry_point is worker_main.main:
        monkeypatch.setattr(worker_main, "open_store", lambda settings: InMemoryJobStore())
        monkeypatch.setattr(worker_main, "stop_on_signals", stopped)
    if entry_point is maintenance_main.main:
        monkeypatch.setattr(maintenance_main, "open_store", lambda settings: InMemoryJobStore())
        monkeypatch.setattr(
            maintenance_main, "DiskAudioStorage", lambda directory: DiskAudioStorage(tmp_path)
        )
        monkeypatch.setattr(maintenance_main, "stop_on_signals", stopped)

    entry_point()
