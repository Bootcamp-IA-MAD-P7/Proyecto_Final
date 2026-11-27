"""Structured logs of the background processes, one JSON object per line (spec service-operation).

Only the event name and the fields passed in `extra` are written: never audio, transcripts,
names or tokens. Callers pass opaque identifiers and counts.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime

FIELDS = (
    "job_id",
    "class_id",
    "stage",
    "state",
    "attempt",
    "error_code",
    "error_type",
    "wait_seconds",
    "count",
)


class JsonFormatter(logging.Formatter):
    def __init__(self, process: str) -> None:
        super().__init__()
        self._process = process

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, object] = {
            "time": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname.lower(),
            "process": self._process,
            "event": record.getMessage(),
        }
        entry.update({name: getattr(record, name) for name in FIELDS if hasattr(record, name)})
        return json.dumps(entry, ensure_ascii=False)


def configure_logging(process: str, level: int = logging.INFO) -> None:
    """Send the logs of the process to stdout as JSON lines."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter(process))
    logging.basicConfig(level=level, handlers=[handler], force=True)
