import json

import pytest

from app.inference.models import ModelRegistry, ModelSpec, main


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


@pytest.mark.models
def test_real_model_tests_are_selected_only_by_their_marker() -> None:
    """This test needs no model; it proves the marker can be selected with make test-models."""
