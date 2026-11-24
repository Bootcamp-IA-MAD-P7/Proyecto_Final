"""Export the API contract to backend/openapi.json, or check that it is up to date.

`python -m app.openapi_export` writes the file; with `--check` it exits with 1 if the file
differs from the declared API.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from app.main import create_app

OPENAPI_PATH = Path(__file__).resolve().parent.parent / "openapi.json"


def render() -> str:
    """The OpenAPI document of the declared API, as it is versioned."""
    return json.dumps(create_app().openapi(), indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str]) -> int:
    expected = render()
    if "--check" in argv:
        current = OPENAPI_PATH.read_text(encoding="utf-8") if OPENAPI_PATH.exists() else ""
        if current != expected:
            print(
                f"{OPENAPI_PATH.name} is out of date: run `make -C backend openapi`.",
                file=sys.stderr,
            )
            return 1
        print(f"{OPENAPI_PATH.name} is up to date.")
        return 0
    OPENAPI_PATH.write_text(expected, encoding="utf-8")
    print(f"Wrote {OPENAPI_PATH.name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
