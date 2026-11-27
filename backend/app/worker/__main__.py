"""Entry point of the worker: `python -m app.worker`."""

from __future__ import annotations

import logging
from datetime import timedelta
from pathlib import Path

from app.inference.build import build_pipeline, stage_models
from app.logs import configure_logging
from app.processes import open_store, stop_on_signals
from app.settings import Settings
from app.storage import DiskAudioStorage
from app.worker import Worker

logger = logging.getLogger("app.worker")


def log_stage_models(settings: Settings) -> None:
    """Record the model, revision and device of each stage, never class data (ADR-0003)."""
    for item in stage_models(settings):
        logger.info(
            "stage model",
            extra={
                "pipeline": settings.inference_pipeline,
                "stage": item.stage,
                "model": item.model,
                "revision": item.revision,
                "device": item.device,
                "compute_type": item.compute_type,
            },
        )


def main() -> None:
    configure_logging("worker")
    settings = Settings.from_env()
    log_stage_models(settings)
    worker = Worker(
        open_store(settings),
        build_pipeline(settings),
        review_period=timedelta(hours=settings.review_period_hours),
        audio_storage=DiskAudioStorage(settings.audio_storage_dir),
        work_dir=Path(settings.work_dir),
        max_attempts=settings.max_attempts,
        retry_delay=timedelta(seconds=settings.retry_delay_seconds),
    )
    worker.run(stop_on_signals(), poll_seconds=settings.worker_poll_seconds)


if __name__ == "__main__":
    main()
