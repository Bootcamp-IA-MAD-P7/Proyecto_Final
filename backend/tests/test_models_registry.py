import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.inference.models import ModelRegistry, ModelSpec, load_dotenv, main


def spec(name: str, calls: list[str]) -> ModelSpec:
    return ModelSpec(
        name=name,
        revision="rev-1",
        download=lambda: calls.append(f"{name}.download"),
        measure=lambda: {"revision": "rev-1", "device": "cpu"},
    )


def test_registry_keeps_fixed_revisions_sorted_by_name() -> None:
    registry = ModelRegistry()
    calls: list[str] = []
    registry.add(spec("whisper", calls))
    registry.add(spec("diarization", calls))

    assert [entry.name for entry in registry.entries()] == ["diarization", "whisper"]
    registry.download_all()
    assert calls == ["diarization.download", "whisper.download"]
    assert registry.measure_all() == {
        "diarization": {"revision": "rev-1", "device": "cpu"},
        "whisper": {"revision": "rev-1", "device": "cpu"},
    }


def test_registry_refuses_to_replace_a_model() -> None:
    registry = ModelRegistry()
    registry.add(spec("whisper", []))

    with pytest.raises(ValueError, match="already registered"):
        registry.add(spec("whisper", []))


def test_measure_command_prints_json_without_class_data(capsys) -> None:
    import app.inference.models as models

    original = models.registry
    registry = ModelRegistry()
    registry.add(spec("whisper", []))
    models.registry = registry
    try:
        main("measure")
    finally:
        models.registry = original

    assert json.loads(capsys.readouterr().out) == {
        "whisper": {"revision": "rev-1", "device": "cpu"}
    }


def test_load_dotenv_exports_only_missing_values(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.setenv("MODELS_DIR", "/already/exported")
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# a comment\nHF_TOKEN=fake-token\nMODELS_DIR=/from/file\nNOT_A_VALUE\n",
        encoding="utf-8",
    )

    load_dotenv(env_file)

    assert os.environ["HF_TOKEN"] == "fake-token"
    assert os.environ["MODELS_DIR"] == "/already/exported"


def test_default_suite_excludes_the_models_marker() -> None:
    backend = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-m", "not models"],
        cwd=backend,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "test_model_tests_are_selected_by_their_marker" not in result.stdout


@pytest.mark.models
def test_model_tests_are_selected_by_their_marker(request) -> None:
    assert any(marker.name == "models" for marker in request.node.iter_markers())
