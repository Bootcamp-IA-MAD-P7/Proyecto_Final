from pathlib import Path
from types import SimpleNamespace

import pytest

from app.contract import JobErrorCode
from app.inference import PipelineError, Turn
from app.inference.diarization import (
    MODEL_ID,
    MODEL_REVISION,
    PyannoteDiarizer,
    download_community1,
    measure_diarization,
)


class FakeTurn:
    def __init__(self, start: float, end: float) -> None:
        self.start = start
        self.end = end


class FakePipeline:
    def __init__(self, output: object | None = None, error: Exception | None = None) -> None:
        self.output = output
        self.error = error
        self.calls: list[tuple[str, int | None]] = []

    def __call__(self, audio: str, max_speakers: int | None = None) -> object:
        self.calls.append((audio, max_speakers))
        if self.error is not None:
            raise self.error
        return self.output


def exclusive_output() -> object:
    return SimpleNamespace(
        exclusive_speaker_diarization=[
            (FakeTurn(0.0, 1.234), "SPEAKER_00"),
            (FakeTurn(1.5, 2.0), "SPEAKER_01"),
        ]
    )


def make_diarizer(pipeline: FakePipeline) -> tuple[PyannoteDiarizer, list[str]]:
    calls: list[str] = []

    def factory() -> FakePipeline:
        calls.append("load")
        return pipeline

    return PyannoteDiarizer(pipeline_factory=factory), calls


def test_loads_the_prepared_model_once_and_releases_it(tmp_path: Path) -> None:
    diarizer, calls = make_diarizer(FakePipeline(exclusive_output()))

    diarizer.load()
    turns = diarizer.diarize(tmp_path / "audio.wav", 2)

    assert calls == ["load"]
    assert len(turns) == 2
    diarizer.close()
    with pytest.raises(PipelineError) as error:
        diarizer.diarize(tmp_path / "audio.wav", 2)
    assert error.value.error.code == JobErrorCode.PROCESSING_UNAVAILABLE


def test_turns_are_exclusive_and_in_milliseconds(tmp_path: Path) -> None:
    diarizer, _ = make_diarizer(FakePipeline(exclusive_output()))
    diarizer.load()

    assert diarizer.diarize(tmp_path / "audio.wav", 2) == [
        Turn(start_ms=0, end_ms=1234, speaker_id="SPEAKER_00"),
        Turn(start_ms=1500, end_ms=2000, speaker_id="SPEAKER_01"),
    ]


def test_participant_count_is_passed_as_max_speakers(tmp_path: Path) -> None:
    pipeline = FakePipeline(exclusive_output())
    diarizer, _ = make_diarizer(pipeline)
    diarizer.load()

    diarizer.diarize(tmp_path / "audio.wav", 3)

    assert pipeline.calls == [(str(tmp_path / "audio.wav"), 3)]


def test_no_fallback_when_the_model_is_missing(tmp_path: Path) -> None:
    attempts: list[str] = []

    def factory() -> object:
        attempts.append("load")
        raise FileNotFoundError("model not prepared")

    diarizer = PyannoteDiarizer(pipeline_factory=factory)

    with pytest.raises(PipelineError) as error:
        diarizer.load()

    assert error.value.error.code == JobErrorCode.PROCESSING_UNAVAILABLE
    assert error.value.error.retryable is True
    assert attempts == ["load"]


@pytest.mark.parametrize(
    "failure",
    [RuntimeError("oom"), OSError("disk"), ImportError("missing"), ValueError("bad config")],
)
def test_model_failures_are_retryable(failure: Exception) -> None:
    def factory() -> object:
        raise failure

    with pytest.raises(PipelineError) as error:
        PyannoteDiarizer(pipeline_factory=factory).load()

    assert error.value.error.code == JobErrorCode.PROCESSING_UNAVAILABLE
    assert error.value.error.retryable is True


def test_unexpected_adapter_error_is_not_retryable(tmp_path: Path) -> None:
    diarizer, _ = make_diarizer(FakePipeline(error=ValueError("secret detail")))
    diarizer.load()

    with pytest.raises(PipelineError) as error:
        diarizer.diarize(tmp_path / "audio.wav", 2)

    assert error.value.error.code == JobErrorCode.PROCESSING_FAILED
    assert error.value.error.retryable is False
    assert "secret detail" not in error.value.error.message


def test_invalid_output_is_not_retryable(tmp_path: Path) -> None:
    diarizer, _ = make_diarizer(FakePipeline(output=SimpleNamespace()))
    diarizer.load()

    with pytest.raises(PipelineError) as error:
        diarizer.diarize(tmp_path / "audio.wav", 2)

    assert error.value.error.code == JobErrorCode.PROCESSING_FAILED
    assert error.value.error.retryable is False


def test_download_uses_the_pinned_revision_and_never_logs_the_token(tmp_path: Path, caplog) -> None:
    calls: list[dict[str, object]] = []

    def snapshot(**kwargs: object) -> str:
        calls.append(kwargs)
        return "ok"

    download_community1(token="hf-secret", models_dir=tmp_path, snapshot=snapshot)

    assert calls[0]["repo_id"] == MODEL_ID
    assert calls[0]["revision"] == MODEL_REVISION
    assert calls[0]["token"] == "hf-secret"
    assert "hf-secret" not in caplog.text


def test_download_uses_huggingface_hub_without_an_injected_callback(
    tmp_path: Path, monkeypatch, caplog
) -> None:
    import sys
    from types import ModuleType

    calls: list[dict[str, object]] = []

    def snapshot(**kwargs: object) -> str:
        calls.append(kwargs)
        return "ok"

    hub = ModuleType("huggingface_hub")
    hub.snapshot_download = snapshot  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "huggingface_hub", hub)

    download_community1(token="hf-secret", models_dir=tmp_path)

    assert calls[0]["revision"] == MODEL_REVISION
    assert "hf-secret" not in caplog.text


def test_download_without_a_token_fails_before_any_download(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # backend/.env may hold a real HF_TOKEN (README): the test must not depend on it.
    monkeypatch.delenv("HF_TOKEN", raising=False)

    def snapshot(**kwargs: object) -> str:
        raise AssertionError("must not download without a token")

    with pytest.raises(RuntimeError, match="HF_TOKEN"):
        download_community1(token=None, models_dir=tmp_path, snapshot=snapshot)


def test_measurement_without_configured_audio_reports_its_status() -> None:
    from app.inference.diarization import measure_community1

    result = measure_community1()

    assert result["status"] == "no audio configured"


class StubDiarizer:
    def load(self) -> None:
        return None

    def close(self) -> None:
        return None

    def diarize(self, wav_path: Path, max_speakers: int) -> list[Turn]:
        return [Turn(start_ms=0, end_ms=60000, speaker_id="SPEAKER_00")]


def wav_of_one_second(tmp_path: Path) -> Path:
    import wave

    audio = tmp_path / "audio.wav"
    with wave.open(str(audio), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\x00\x00" * 16000)
    return audio


def test_measurement_computes_seconds_per_minute(tmp_path: Path) -> None:
    result = measure_diarization(wav_of_one_second(tmp_path), diarizer=StubDiarizer())

    assert result["model"] == MODEL_ID
    assert result["revision"] == MODEL_REVISION
    assert float(result["seconds_per_minute"]) >= 0
    assert float(result["peak_memory_mib"]) >= 0
    assert "der" not in result


def test_measurement_includes_der_when_a_reference_is_given(tmp_path: Path, monkeypatch) -> None:
    import sys
    from types import ModuleType

    class FakeAnnotation(dict):
        pass

    class FakeSegment:
        def __init__(self, start: float, end: float) -> None:
            self.start = start
            self.end = end

    class FakeErrorRate:
        def __init__(self, **kwargs: object) -> None:
            self.kwargs = kwargs

        def __call__(self, expected: object, actual: object) -> float:
            return 0.25

    core = ModuleType("pyannote.core")
    core.Annotation = FakeAnnotation  # type: ignore[attr-defined]
    core.Segment = FakeSegment  # type: ignore[attr-defined]
    metrics = ModuleType("pyannote.metrics.diarization")
    metrics.DiarizationErrorRate = FakeErrorRate  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "pyannote.core", core)
    monkeypatch.setitem(sys.modules, "pyannote.metrics.diarization", metrics)

    reference = tmp_path / "reference.json"
    reference.write_text(
        '{"turns": [{"start_s": 0, "end_s": 1, "speaker": "A"}]}', encoding="utf-8"
    )

    result = measure_diarization(
        wav_of_one_second(tmp_path), reference=reference, diarizer=StubDiarizer()
    )

    assert result["der"] == "0.250"
