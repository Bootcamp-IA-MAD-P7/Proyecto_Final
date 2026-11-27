"""Registry of the models each adapter downloads and measures (ADR-0003).

Adapters add their entry in sections 2 and 3. Downloading is separate from processing so the
worker can run offline, and measurements never include class data.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from app.settings import Settings


@dataclass(frozen=True)
class ModelSpec:
    name: str
    revision: str
    download: Callable[[], None]
    measure: Callable[[], Mapping[str, str]]
    ready: Callable[[], bool] = lambda: False
    """Whether the prepared copy is in MODELS_DIR, without loading it. Unknown means missing."""


class ModelRegistry:
    """Fixed revisions with a download and a measurement function per model."""

    def __init__(self) -> None:
        self._specs: dict[str, ModelSpec] = {}

    def add(self, spec: ModelSpec) -> None:
        if spec.name in self._specs:
            raise ValueError(f"model already registered: {spec.name}")
        self._specs[spec.name] = spec

    def entries(self) -> list[ModelSpec]:
        return sorted(self._specs.values(), key=lambda spec: spec.name)

    def download_all(self) -> None:
        for spec in self.entries():
            spec.download()

    def measure_all(self) -> dict[str, Mapping[str, str]]:
        return {spec.name: spec.measure() for spec in self.entries()}

    def missing(self) -> list[str]:
        return [spec.name for spec in self.entries() if not spec.ready()]


registry = ModelRegistry()


def register(spec: ModelSpec) -> None:
    registry.add(spec)


def download_all() -> None:
    registry.download_all()


def measure_all() -> dict[str, Mapping[str, str]]:
    return registry.measure_all()


def missing() -> list[str]:
    return registry.missing()


def check() -> None:
    """Exit with an error unless the worker runs the real models and all of them are prepared."""
    if Settings.from_env().inference_pipeline != "models":
        raise SystemExit("INFERENCE_PIPELINE is not 'models' in backend/.env")
    absent = missing()
    if absent:
        raise SystemExit("models not downloaded: " + ", ".join(absent))


def load_dotenv(path: Path = Path(".env")) -> None:
    """Export the local .env values missing or empty in the environment (secrets included).

    Compose gives the worker an empty HF_TOKEN, so `make models` reads it from backend/.env.
    """
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if not os.environ.get(key.strip()):
            os.environ[key.strip()] = value.strip().strip('"').strip("'")


def main(command: str) -> None:
    load_dotenv()
    if command == "download":
        download_all()
    elif command == "check":
        check()
    elif command == "measure":
        print(json.dumps(measure_all(), sort_keys=True))
    else:
        raise SystemExit("usage: python -m app.inference.models download|check|measure")


if __name__ == "__main__":
    import sys

    # `python -m` runs this file as `__main__`, a second copy with an empty registry: the adapters
    # registered their models in `app.inference.models` when the package was imported.
    from app.inference.models import main as registered_main

    registered_main(sys.argv[1] if len(sys.argv) > 1 else "")
