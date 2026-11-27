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


def test_load_dotenv_fills_values_exported_empty(tmp_path: Path, monkeypatch) -> None:
    # Compose exports HF_TOKEN="" to the worker; `make models` takes the token from backend/.env.
    monkeypatch.setenv("HF_TOKEN", "")
    env_file = tmp_path / ".env"
    env_file.write_text("HF_TOKEN=fake-token\n", encoding="utf-8")

    load_dotenv(env_file)

    assert os.environ["HF_TOKEN"] == "fake-token"


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


def test_registry_lists_the_models_not_prepared() -> None:
    registry = ModelRegistry()
    registry.add(ModelSpec("whisper", "rev-1", lambda: None, lambda: {}, ready=lambda: True))
    registry.add(ModelSpec("diarization", "rev-1", lambda: None, lambda: {}, ready=lambda: False))

    assert registry.missing() == ["diarization"]


def test_check_fails_when_a_model_is_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MODELS_DIR", str(tmp_path / "models"))
    monkeypatch.setenv("INFERENCE_PIPELINE", "models")

    with pytest.raises(SystemExit, match=r"models not downloaded: .*community-1"):
        main("check")


def test_check_passes_when_every_model_is_prepared(tmp_path: Path, monkeypatch) -> None:
    from app.inference import diarization, transcription

    models = tmp_path / "models"
    (models / transcription.MODEL_ID).mkdir(parents=True)
    (models / transcription.MODEL_ID / "model.bin").write_bytes(b"weights")
    (models / diarization.MODEL_ID).mkdir(parents=True)
    (models / diarization.MODEL_ID / "config.yaml").write_text("pipeline: {}", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MODELS_DIR", str(models))
    monkeypatch.setenv("INFERENCE_PIPELINE", "models")

    main("check")


def test_check_fails_when_the_worker_runs_the_fake_pipeline(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("INFERENCE_PIPELINE", "fake")

    with pytest.raises(SystemExit, match="INFERENCE_PIPELINE"):
        main("check")


def test_the_command_line_sees_the_registered_models(tmp_path: Path) -> None:
    backend = Path(__file__).resolve().parents[1]
    env = {**os.environ, "MODELS_DIR": str(tmp_path), "INFERENCE_PIPELINE": "models"}
    result = subprocess.run(
        [sys.executable, "-m", "app.inference.models", "check"],
        cwd=backend,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "faster-whisper-small" in result.stderr
