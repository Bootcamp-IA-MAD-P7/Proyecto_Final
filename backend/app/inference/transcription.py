"""Faster-whisper transcription (Whisper small, CPU, int8) with word-level timestamps.

The library is imported only when the model is loaded, so the API, the tests with doubles and
the CI image do not need inference dependencies. The model is read from the prepared copy in
`MODELS_DIR`, never downloaded during processing.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
import tracemalloc
from collections.abc import Callable, Mapping
from pathlib import Path

from app.contract import JobErrorCode
from app.inference.models import ModelSpec, register
from app.inference.normalization import FfmpegNormalizer
from app.inference.pipeline import PipelineError
from app.inference.types import Phrase, Transcriber, Word
from app.settings import Settings

MODEL_ID = "Systran/faster-whisper-small"
MODEL_REVISION = "536b0662742c02347bc0e980a01041f333bce120"
UNAVAILABLE_MESSAGE = "El modelo de transcripción no está disponible."
INVALID_OUTPUT_MESSAGE = "La transcripción devuelta no es válida."
DEFAULT_MODELS_DIR = "data/models"


def _unavailable() -> PipelineError:
    return PipelineError(JobErrorCode.PROCESSING_UNAVAILABLE, UNAVAILABLE_MESSAGE, retryable=True)


def _invalid() -> PipelineError:
    return PipelineError(JobErrorCode.PROCESSING_FAILED, INVALID_OUTPUT_MESSAGE, retryable=False)


class FasterWhisperTranscriber(Transcriber):
    def __init__(
        self,
        *,
        model: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str = "",
        models_dir: Path | None = None,
        model_factory: Callable[[], object] | None = None,
    ) -> None:
        self._model = model
        self._device = device
        self._compute_type = compute_type
        self._language = language
        self._models_dir = models_dir or Path(os.getenv("MODELS_DIR", DEFAULT_MODELS_DIR))
        self._model_factory = model_factory
        self._engine: object | None = None

    def _local_model(self) -> object:
        local = self._models_dir / MODEL_ID
        if not local.is_dir():
            raise FileNotFoundError(str(local))
        from faster_whisper import WhisperModel

        return WhisperModel(str(local), device=self._device, compute_type=self._compute_type)

    def load(self) -> None:
        try:
            self._engine = (self._model_factory or self._local_model)()
        except PipelineError:
            raise
        except Exception as error:
            raise _unavailable() from error

    def close(self) -> None:
        self._engine = None

    def transcribe(self, wav_path: Path) -> list[Phrase]:
        if self._engine is None:
            raise _unavailable()
        try:
            segments, _ = self._engine.transcribe(  # type: ignore[attr-defined]
                str(wav_path),
                word_timestamps=True,
                vad_filter=True,
                language=self._language or None,
            )
            phrases = self._phrases(list(segments))
        except PipelineError:
            raise
        except (AttributeError, TypeError, ValueError, OverflowError) as error:
            raise _invalid() from error
        except Exception as error:
            raise _unavailable() from error
        return phrases

    @staticmethod
    def _phrases(segments: list[object]) -> list[Phrase]:
        phrases: list[Phrase] = []
        for segment in segments:
            words: list[Word] = []
            for item in segment.words:  # type: ignore[attr-defined]
                text = str(item.word).strip()
                if not text:
                    continue
                start = round(float(item.start) * 1000)
                end = max(round(float(item.end) * 1000), start + 1)
                if words and start < words[-1].end_ms:
                    start = words[-1].end_ms
                    end = max(end, start + 1)
                words.append(Word(text=text, start_ms=start, end_ms=end))
            if words:
                phrases.append(Phrase(words=words))
        return phrases


def download_whisper_small(
    *, models_dir: Path | None = None, snapshot: Callable[..., object] | None = None
) -> None:
    """Download the pinned CTranslate2 weights to the private models directory."""
    if snapshot is None:
        from huggingface_hub import snapshot_download

        snapshot = snapshot_download
    target = Path(models_dir or os.getenv("MODELS_DIR", DEFAULT_MODELS_DIR))
    snapshot(
        repo_id=MODEL_ID,
        revision=MODEL_REVISION,
        local_dir=str(target / MODEL_ID),
    )


def word_error_rate(reference: str, hypothesis: str) -> float:
    """Word-level Levenshtein distance divided by the number of reference words."""
    expected = reference.split()
    actual = hypothesis.split()
    if not expected:
        return 0.0 if not actual else 1.0
    previous = list(range(len(actual) + 1))
    for index, word in enumerate(expected, start=1):
        current = [index]
        for column, other in enumerate(actual, start=1):
            current.append(
                min(
                    previous[column] + 1,
                    current[column - 1] + 1,
                    previous[column - 1] + (word != other),
                )
            )
        previous = current
    return previous[-1] / len(expected)


def _peak_memory_mib() -> float:
    try:
        import resource

        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    except ImportError:
        return tracemalloc.get_traced_memory()[1] / (1024 * 1024)


def compare_language_detection(
    audio: Path, model_factory: Callable[[], object]
) -> Mapping[str, str]:
    """Compare whole-file language detection with a detection per transcribed phrase."""
    engine = model_factory()
    segments, info = engine.transcribe(str(audio), vad_filter=True)
    per_phrase: list[str] = []
    for segment in list(segments):
        start = getattr(segment, "start", None)
        end = getattr(segment, "end", None)
        if start is None or end is None:
            continue
        _, phrase_info = engine.transcribe(str(audio), clip_timestamps=[start, end])
        detected = getattr(phrase_info, "language", "")
        if detected and detected not in per_phrase:
            per_phrase.append(str(detected))
    return {
        "language_single": str(getattr(info, "language", "")),
        "language_per_phrase": ",".join(per_phrase),
    }


def measure_transcription(
    audio: Path,
    *,
    reference: Path | None = None,
    multilingual_sample: Path | None = None,
    model_factory: Callable[[], object] | None = None,
    settings: Settings | None = None,
) -> Mapping[str, str]:
    """Seconds per minute, peak memory, WER and the multilingual comparison."""
    import wave

    config = settings or Settings.from_env()

    transcriber = FasterWhisperTranscriber(
        model=config.asr_model,
        device=config.asr_device,
        compute_type=config.asr_compute_type,
        language=config.asr_language,
        models_dir=Path(config.models_dir),
        model_factory=model_factory,
    )
    if not tracemalloc.is_tracing():
        tracemalloc.start()
    with tempfile.TemporaryDirectory() as temporary:
        normalizer = FfmpegNormalizer()
        started = time.perf_counter()
        wav_path = normalizer.normalize(audio, Path(temporary))
        transcriber.load()
        try:
            phrases = transcriber.transcribe(wav_path)
        finally:
            transcriber.close()
        elapsed = time.perf_counter() - started

        with wave.open(str(wav_path), "rb") as wav:
            duration_minutes = wav.getnframes() / wav.getframerate() / 60
    if duration_minutes <= 0:
        raise ValueError("audio has no duration")

    result = {
        "model": MODEL_ID,
        "revision": MODEL_REVISION,
        "device": config.asr_device,
        "compute_type": config.asr_compute_type,
        "seconds_per_minute": f"{elapsed / duration_minutes:.2f}",
        "peak_memory_mib": f"{_peak_memory_mib():.1f}",
    }
    if reference is not None:
        expected = json.loads(reference.read_text(encoding="utf-8"))["text"]
        actual = " ".join(phrase.text for phrase in phrases)
        result["wer"] = f"{word_error_rate(expected, actual):.3f}"
    if multilingual_sample is not None:
        factory = model_factory or transcriber._local_model
        result.update(compare_language_detection(multilingual_sample, factory))
    return result


def measure_whisper() -> Mapping[str, str]:
    """Entry of `make measure`; needs ASR_MEASURE_AUDIO to be set."""
    raw = os.getenv("ASR_MEASURE_AUDIO")
    if not raw:
        return {"status": "no audio configured", "hint": "set ASR_MEASURE_AUDIO"}
    reference = os.getenv("ASR_REFERENCE")
    multilingual = os.getenv("ASR_MULTILINGUAL_SAMPLE")
    return measure_transcription(
        Path(raw),
        reference=Path(reference) if reference else None,
        multilingual_sample=Path(multilingual) if multilingual else None,
    )


register(
    ModelSpec(
        name=MODEL_ID,
        revision=MODEL_REVISION,
        download=download_whisper_small,
        measure=measure_whisper,
    )
)
