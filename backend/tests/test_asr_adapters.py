"""Doubles for the normalizer and the faster-whisper transcriber (no inference deps)."""

import sys
import wave
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from app.contract import JobErrorCode
from app.inference import PipelineError
from app.inference.normalization import FfmpegNormalizer
from app.inference.transcription import (
    MODEL_ID,
    MODEL_REVISION,
    FasterWhisperTranscriber,
    compare_language_detection,
    download_whisper_small,
    measure_transcription,
    word_error_rate,
)
from tests.audio import make_audio, require_ffmpeg


def one_second_wav(directory: Path) -> Path:
    target = directory / "audio.wav"
    with wave.open(str(target), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\x00\x00" * 16000)
    return target


def test_normalizer_writes_16k_mono_wav_in_the_work_dir(tmp_path: Path) -> None:
    audio = make_audio(tmp_path, "ogg", seconds=2)
    work = tmp_path / "work"
    work.mkdir()
    normalizer = FfmpegNormalizer()

    result = normalizer.normalize(audio, work)

    assert result == work / "audio.wav"
    with wave.open(str(result), "rb") as wav:
        assert wav.getframerate() == 16000
        assert wav.getnchannels() == 1


def test_normalizer_rejects_an_undecodable_file(tmp_path: Path) -> None:
    require_ffmpeg()
    audio = tmp_path / "broken.ogg"
    audio.write_bytes(b"not audio")
    work = tmp_path / "work"
    work.mkdir()

    with pytest.raises(PipelineError) as error:
        FfmpegNormalizer().normalize(audio, work)

    assert error.value.error.code == JobErrorCode.INVALID_AUDIO
    assert error.value.error.retryable is False
    assert not (work / "audio.wav").exists()


class FakeWord:
    def __init__(self, word: str, start: float, end: float) -> None:
        self.word = word
        self.start = start
        self.end = end


class FakeSegment:
    def __init__(self, words: list[FakeWord]) -> None:
        self.words = words


class FakeInfo:
    language = "es"
    language_probability = 0.9


class FakeWhisperModel:
    def __init__(self, segments: list[FakeSegment] | None = None, error: Exception | None = None):
        self.segments = segments or [FakeSegment([FakeWord(" hola", 0.0, 0.4)])]
        self.error = error
        self.calls: list[dict[str, object]] = []

    def transcribe(self, audio: str, **kwargs: object) -> tuple[list[FakeSegment], FakeInfo]:
        self.calls.append({"audio": audio, **kwargs})
        if self.error is not None:
            raise self.error
        return self.segments, FakeInfo()


def make_transcriber(model: FakeWhisperModel) -> tuple[FasterWhisperTranscriber, list[str]]:
    calls: list[str] = []

    def factory() -> FakeWhisperModel:
        calls.append("load")
        return model

    return FasterWhisperTranscriber(model_factory=factory), calls


def test_transcriber_returns_phrases_with_word_timestamps(tmp_path: Path) -> None:
    model = FakeWhisperModel(
        [
            FakeSegment(
                [FakeWord(" hola", 0.0, 0.4), FakeWord(" clase", 0.4, 0.9)],
            )
        ]
    )
    transcriber, _ = make_transcriber(model)
    transcriber.load()

    phrases = transcriber.transcribe(tmp_path / "audio.wav")

    assert len(phrases) == 1
    assert [word.text for word in phrases[0].words] == ["hola", "clase"]
    assert (phrases[0].words[0].start_ms, phrases[0].words[0].end_ms) == (0, 400)
    assert model.calls[0]["word_timestamps"] is True
    assert model.calls[0]["vad_filter"] is True
    assert model.calls[0]["language"] is None
    transcriber.close()


@pytest.mark.parametrize("failure", [ImportError("missing"), MemoryError("oom"), OSError("disk")])
def test_model_failures_are_retryable(failure: Exception) -> None:
    def factory() -> object:
        raise failure

    with pytest.raises(PipelineError) as error:
        FasterWhisperTranscriber(model_factory=factory).load()

    assert error.value.error.code == JobErrorCode.PROCESSING_UNAVAILABLE
    assert error.value.error.retryable is True


def test_invalid_model_output_is_not_retryable(tmp_path: Path) -> None:
    class BrokenModel:
        def transcribe(self, audio: str, **kwargs: object) -> tuple[object, object]:
            return object(), FakeInfo()

    transcriber = FasterWhisperTranscriber(model_factory=BrokenModel)
    transcriber.load()

    with pytest.raises(PipelineError) as error:
        transcriber.transcribe(tmp_path / "audio.wav")

    assert error.value.error.code == JobErrorCode.PROCESSING_FAILED
    assert error.value.error.retryable is False


def test_download_pins_the_model_revision(tmp_path: Path, monkeypatch, caplog) -> None:
    calls: list[dict[str, object]] = []
    hub = ModuleType("huggingface_hub")

    def snapshot(**kwargs: object) -> str:
        calls.append(kwargs)
        return "ok"

    hub.snapshot_download = snapshot  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "huggingface_hub", hub)

    download_whisper_small(models_dir=tmp_path)

    assert calls[0]["repo_id"] == MODEL_ID
    assert calls[0]["revision"] == MODEL_REVISION
    assert "hf-" not in caplog.text


def test_word_error_rate_counts_substitutions_and_deletions() -> None:
    assert word_error_rate("hola clase", "hola clase") == 0.0
    assert word_error_rate("hola clase", "hola") == 0.5
    assert word_error_rate("hola clase", "hola clase nueva") == 0.5


def test_measurement_reports_seconds_per_minute_and_wer(tmp_path: Path) -> None:
    require_ffmpeg()
    model = FakeWhisperModel()
    reference = tmp_path / "reference.json"
    reference.write_text('{"text": "hola clase"}', encoding="utf-8")

    result = measure_transcription(
        one_second_wav(tmp_path), reference=reference, model_factory=lambda: model
    )

    assert result["model"] == MODEL_ID
    assert result["revision"] == MODEL_REVISION
    assert float(result["seconds_per_minute"]) >= 0
    assert "wer" in result


def test_local_model_is_loaded_from_the_prepared_directory(tmp_path: Path, monkeypatch) -> None:
    prepared = tmp_path / "Systran" / "faster-whisper-small"
    prepared.mkdir(parents=True)
    calls: list[tuple[str, dict[str, object]]] = []

    hub = ModuleType("faster_whisper")

    class LocalModel:
        def __init__(self, path: str, **kwargs: object) -> None:
            calls.append((path, kwargs))

    hub.WhisperModel = LocalModel  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "faster_whisper", hub)

    transcriber = FasterWhisperTranscriber(models_dir=tmp_path)
    transcriber.load()

    assert calls[0][0] == str(prepared)
    assert calls[0][1] == {"device": "cpu", "compute_type": "int8"}


def test_overlapping_words_are_clamped_inside_the_phrase(tmp_path: Path) -> None:
    model = FakeWhisperModel(
        [
            FakeSegment(
                [FakeWord("uno", 0.0, 1.0), FakeWord("dos", 0.5, 0.6), FakeWord("", 2.0, 2.1)]
            )
        ]
    )
    transcriber, _ = make_transcriber(model)
    transcriber.load()

    phrases = transcriber.transcribe(tmp_path / "audio.wav")

    assert [(word.start_ms, word.end_ms) for word in phrases[0].words] == [(0, 1000), (1000, 1001)]


def test_language_comparison_uses_multilingual_on_phrase_excerpts(tmp_path: Path) -> None:
    class TimedSegment:
        start = 0.0
        end = 1.0

    class LanguageModel:
        def __init__(self) -> None:
            self.calls: list[bool] = []
            self.closed = False

        def close(self) -> None:
            self.closed = True

        def transcribe(self, audio: str, **kwargs: object) -> tuple[list[TimedSegment], object]:
            multilingual = bool(kwargs.get("multilingual", False))
            self.calls.append(multilingual)
            segments = [] if multilingual else [TimedSegment()]
            language = "es" if multilingual else "en"
            return segments, SimpleNamespace(language=language)

    model = LanguageModel()
    result = compare_language_detection(one_second_wav(tmp_path), lambda: model)

    assert result == {"language_single": "en", "language_per_phrase": "es"}
    assert model.calls == [False, True]
    assert model.closed is True
