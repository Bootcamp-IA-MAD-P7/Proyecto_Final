"""Maintenance: periodic tasks of the service.

Each cycle expires jobs whose audio passed its retention date, deletes that audio and removes
orphan files of failed uploads. It also runs once at startup, before jobs can be resumed
(ADR-0004). Keys and paths never reach the logs.
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from app.jobs import JobStore
from app.storage import AudioStorage

logger = logging.getLogger("app.maintenance")

ORPHAN_GRACE = timedelta(hours=1)
"""Margin before a file with no audio row is treated as an orphan of a failed upload."""


def _now() -> datetime:
    return datetime.now(UTC)


class Maintenance:
    def __init__(
        self,
        store: JobStore | None = None,
        storage: AudioStorage | None = None,
        clock: Callable[[], datetime] = _now,
        orphan_grace: timedelta = ORPHAN_GRACE,
    ) -> None:
        self._store = store
        self._storage = storage
        self._clock = clock
        self._orphan_grace = orphan_grace
        self.cycles = 0

    def run_cycle(self) -> None:
        """Expire jobs, purge their audio and clean up orphans, with the current time."""
        now = self._clock()
        if self._store is not None:
            self._store.expire_jobs(now)
        self._purge_expired_audio(now)
        self._remove_orphans(now)
        self.cycles += 1
        logger.info("maintenance cycle completed", extra={"count": self.cycles})

    def _purge_expired_audio(self, now: datetime) -> int:
        if self._store is None or self._storage is None:
            return 0
        purged = 0
        for audio in self._store.audios_to_purge(now):
            try:
                self._storage.delete(audio.storage_key)
            except OSError:
                # Do not mark it: the next cycle retries and the audio is already unusable.
                logger.warning("audio deletion failed", extra={"count": 1})
                continue
            self._store.mark_audio_purged(audio.audio_id, now)
            purged += 1
        return purged

    def _remove_orphans(self, now: datetime) -> int:
        if self._store is None or self._storage is None:
            return 0
        known = self._store.stored_audio_keys()
        cutoff = now - self._orphan_grace
        removed = 0
        for stored in self._storage.list():
            if stored.key in known or stored.modified_at >= cutoff:
                continue
            try:
                self._storage.delete(stored.key)
            except OSError:
                logger.warning("orphan deletion failed", extra={"count": 1})
                continue
            removed += 1
        return removed

    def run(self, stop: threading.Event, interval_seconds: float) -> None:
        """Purge at startup and then every `interval_seconds` until `stop` is set."""
        logger.info("maintenance ready")
        self.run_cycle()
        while not stop.wait(interval_seconds):
            self.run_cycle()
        logger.info("maintenance stopped")
