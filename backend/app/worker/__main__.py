"""Entry point of the worker: `python -m app.worker`."""

from __future__ import annotations

from datetime import timedelta

from app.inference.fake import FakePipeline
from app.logs import configure_logging
from app.processes import open_store, stop_on_signals
from app.settings import Settings
from app.worker import Worker


def main() -> None:
    configure_logging("worker")
    settings = Settings.from_env()
    worker = Worker(
        open_store(settings),
        FakePipeline(settings.fake_stage_seconds),
        review_period=timedelta(hours=settings.review_period_hours),
    )
    worker.run(stop_on_signals(), poll_seconds=settings.worker_poll_seconds)


if __name__ == "__main__":
    main()
