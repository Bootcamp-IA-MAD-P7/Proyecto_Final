"""Entry point of maintenance: `python -m app.maintenance`."""

from __future__ import annotations

from app.jobs import JobStore
from app.logs import configure_logging
from app.maintenance import Maintenance
from app.processes import open_store, stop_on_signals
from app.settings import Settings
from app.storage import AudioStorage, DiskAudioStorage


def main() -> None:
    configure_logging("maintenance")
    settings = Settings.from_env()
    store: JobStore = open_store(settings)
    storage: AudioStorage = DiskAudioStorage(settings.audio_storage_dir)
    Maintenance(store, storage).run(stop_on_signals(), settings.maintenance_interval_seconds)


if __name__ == "__main__":
    main()
