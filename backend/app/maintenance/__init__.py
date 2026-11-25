"""Maintenance: periodic tasks of the service.

For now its cycle only records activity. Automatic publication when the review period ends
arrives in E5, and the purge of the audio in E2.
"""

from __future__ import annotations

import logging
import threading

logger = logging.getLogger("app.maintenance")


class Maintenance:
    def __init__(self) -> None:
        self.cycles = 0

    def run_cycle(self) -> None:
        self.cycles += 1
        logger.info("maintenance cycle completed", extra={"count": self.cycles})

    def run(self, stop: threading.Event, interval_seconds: float) -> None:
        """Run a cycle every `interval_seconds` until `stop` is set."""
        logger.info("maintenance ready")
        while not stop.wait(interval_seconds):
            self.run_cycle()
        logger.info("maintenance stopped")
