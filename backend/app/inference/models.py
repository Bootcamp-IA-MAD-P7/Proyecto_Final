"""Registry of the models each adapter downloads and measures (ADR-0003).

Adapters add their entry in sections 2 and 3. Downloading is separate from processing so the
worker can run offline, and measurements never include class data.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    name: str
    revision: str
    download: Callable[[], None]
    measure: Callable[[], Mapping[str, str]]


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


registry = ModelRegistry()


def register(spec: ModelSpec) -> None:
    registry.add(spec)


def download_all() -> None:
    registry.download_all()


def measure_all() -> dict[str, Mapping[str, str]]:
    return registry.measure_all()


def main(command: str) -> None:
    if command == "download":
        download_all()
    elif command == "measure":
        print(json.dumps(measure_all(), sort_keys=True))
    else:
        raise SystemExit("usage: python -m app.inference.models download|measure")


if __name__ == "__main__":
    import sys

    main(sys.argv[1] if len(sys.argv) > 1 else "")
