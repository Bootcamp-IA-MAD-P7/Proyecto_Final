"""Entry point of maintenance: `python -m app.maintenance`."""

from __future__ import annotations

from app.logs import configure_logging
from app.maintenance import Maintenance
from app.processes import stop_on_signals
from app.settings import Settings


def main() -> None:
    configure_logging("maintenance")
    settings = Settings.from_env()
    Maintenance().run(stop_on_signals(), settings.maintenance_interval_seconds)


if __name__ == "__main__":
    main()
