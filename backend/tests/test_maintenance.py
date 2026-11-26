import json
import logging
import os
import threading
from datetime import UTC, datetime

from app.contract import ClassMetadata, JobState, Result
from app.jobs import AudioAsset, InMemoryJobStore
from app.logs import JsonFormatter
from app.maintenance import Maintenance
from app.storage import DiskAudioStorage
from tests.conftest import load_fixture

NOW = datetime(2026, 11, 27, 12, tzinfo=UTC)
EXPIRED = datetime(2026, 11, 26, 12, tzinfo=UTC)


def make_store(expires_at: datetime = EXPIRED, key: str = "audio-01"):
    store = InMemoryJobStore()
    metadata = ClassMetadata.model_validate(load_fixture("valid/class-metadata.json"))
    audio = AudioAsset(
        audio_id=key,
        storage_key=key,
        format="opus",
        size_bytes=1024,
        duration_seconds=60,
        sha256="a" * 64,
        received_at=datetime(2026, 11, 25, 12, tzinfo=UTC),
        expires_at=expires_at,
    )
    return store, store.create_class(metadata, "demo-teacher", audio=audio)


class FailingOnceStorage:
    """Fails the first physical deletion, as a busy disk could."""

    def __init__(self, inner: DiskAudioStorage) -> None:
        self.inner = inner
        self.fail = True

    def delete(self, key: str) -> None:
        if self.fail:
            self.fail = False
            raise OSError("disk busy")
        self.inner.delete(key)

    def list(self):
        return self.inner.list()


def test_runs_a_cycle_each_interval_until_stopped(caplog):
    maintenance = Maintenance()
    stop = threading.Event()
    original = maintenance.run_cycle

    def cycle():
        original()
        if maintenance.cycles == 3:
            stop.set()

    maintenance.run_cycle = cycle

    with caplog.at_level(logging.INFO, logger="app.maintenance"):
        thread = threading.Thread(target=maintenance.run, args=(stop, 0.01))
        thread.start()
        thread.join(timeout=5)

    assert not thread.is_alive()
    events = [record.message for record in caplog.records]
    assert events[0] == "maintenance ready"
    assert events.count("maintenance cycle completed") == 3
    assert events[-1] == "maintenance stopped"


def test_a_cycle_is_logged_as_a_json_line():
    record = logging.LogRecord("app.maintenance", logging.INFO, __file__, 1, "cycle", None, None)
    record.count = 2

    entry = json.loads(JsonFormatter("maintenance").format(record))

    assert entry["process"] == "maintenance"
    assert entry["event"] == "cycle"
    assert entry["count"] == 2


def test_expired_audio_is_purged_and_its_job_expires(tmp_path):
    storage = DiskAudioStorage(tmp_path / "audio")
    temporary = storage.write_temporary(iter([b"audio"]))
    storage.commit(temporary, "audio-01")
    store, stored = make_store()

    Maintenance(store, storage, clock=lambda: NOW).run_cycle()

    assert store.get_job(stored.job_id).state is JobState.EXPIRED
    assert not storage.path("audio-01").exists()
    assert store.get_audio(stored.class_id).deleted_at == NOW


def test_a_failed_deletion_is_retried_in_the_next_cycle(tmp_path, caplog):
    storage = FailingOnceStorage(DiskAudioStorage(tmp_path / "audio"))
    temporary = storage.inner.write_temporary(iter([b"audio"]))
    storage.inner.commit(temporary, "audio-01")
    store, stored = make_store()
    maintenance = Maintenance(store, storage, clock=lambda: NOW)

    with caplog.at_level(logging.WARNING, logger="app.maintenance"):
        maintenance.run_cycle()

    assert store.get_audio(stored.class_id).deleted_at is None
    assert storage.inner.path("audio-01").exists()
    assert [record.message for record in caplog.records] == ["audio deletion failed"]
    assert "audio-01" not in caplog.text

    maintenance.run_cycle()

    assert store.get_audio(stored.class_id).deleted_at == NOW
    assert not storage.inner.path("audio-01").exists()


def test_orphans_older_than_the_grace_are_removed(tmp_path):
    storage = DiskAudioStorage(tmp_path / "audio")
    old = storage.write_temporary(iter([b"old"]))
    fresh = storage.write_temporary(iter([b"fresh"]))
    old_file = storage.path(old)
    fresh_file = storage.path(fresh)
    os.utime(old_file, (NOW.timestamp() - 7200, NOW.timestamp() - 7200))
    os.utime(fresh_file, (NOW.timestamp(), NOW.timestamp()))
    store, _ = make_store(expires_at=datetime(2027, 1, 1, tzinfo=UTC))

    Maintenance(store, storage, clock=lambda: NOW).run_cycle()

    assert not old_file.exists()
    assert fresh_file.exists()


def test_a_finished_job_keeps_its_result_when_its_audio_is_purged(tmp_path):
    storage = DiskAudioStorage(tmp_path / "audio")
    temporary = storage.write_temporary(iter([b"audio"]))
    storage.commit(temporary, "audio-01")
    store, stored = make_store()
    job = store.claim_next()
    result = Result.model_validate(
        {**load_fixture("valid/result-draft.json"), "class_id": stored.class_id}
    )
    store.complete(job.job_id, result)

    Maintenance(store, storage, clock=lambda: NOW).run_cycle()

    assert store.get_job(job.job_id).state is JobState.READY_FOR_REVIEW
    assert store.get_result(stored.class_id) == result
    assert not storage.path("audio-01").exists()


def test_a_cycle_runs_before_the_first_wait():
    maintenance = Maintenance(clock=lambda: NOW)
    stop = threading.Event()
    stop.set()

    maintenance.run(stop, 60)

    assert maintenance.cycles == 1
