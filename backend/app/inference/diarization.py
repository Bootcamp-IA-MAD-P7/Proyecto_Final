"""Community-1 diarization adapter (ADR-0003, section 3 of `add-diarized-transcription`).

Pyannote is imported only when the model is loaded, so the API and the tests with doubles do not
need the inference dependencies. The worker runs offline: the pipeline is loaded from the prepared
copy in `MODELS_DIR`, never downloaded during processing. A missing model is retryable, there is no
silent fallback, and nothing about the class is logged.
"""

from __future__ import annotations

import json
import os
import time
import tracemalloc
from collections.abc import Callable, Mapping
from pathlib import Path

from app.contract import JobErrorCode
from app.inference.models import ModelSpec, register
from app.inference.pipeline import PipelineError
from app.inference.types import Diarizer, Turn

MODEL_ID = "pyannote/speaker-diarization-community-1"
MODEL_REVISION = "3533c8cf8e369892e6b79ff1bf80f7b0286a54ee"
DEFAULT_MODELS_DIR = "data/models"
UNAVAILABLE_MESSAGE = "El modelo de diarización no está disponible."
INVALID_OUTPUT_MESSAGE = "La salida de la diarización no es válida."
DOWNLOAD_MESSAGE = "HF_TOKEN is required to download the Community-1 model"


def _unavailable(message: str = UNAVAILABLE_MESSAGE) -> PipelineError:
    return PipelineError(JobErrorCode.PROCESSING_UNAVAILABLE, message, retryable=True)


def _invalid(message: str = INVALID_OUTPUT_MESSAGE) -> PipelineError:
    return PipelineError(JobErrorCode.PROCESSING_FAILED, message, retryable=False)


class PyannoteDiarizer(Diarizer):
    """Adapter over the exclusive diarization of pyannote Community-1."""

    def __init__(
        self,
        *,
        models_dir: Path | None = None,
        pipeline_factory: Callable[[], object] | None = None,
    ) -> None:
        self._models_dir = models_dir or Path(os.getenv("MODELS_DIR", DEFAULT_MODELS_DIR))
        self._pipeline_factory = pipeline_factory
        self._pipeline: object | None = None

    def _local_pipeline(self) -> object:
        """Load the pinned pipeline from the prepared local copy, never from the network."""
        local = self._models_dir / MODEL_ID
        if not local.is_dir():
            raise FileNotFoundError(str(local))
        from pyannote.audio import Pipeline

        return Pipeline.from_pretrained(str(local))

    def load(self) -> None:
        try:
            self._pipeline = (self._pipeline_factory or self._local_pipeline)()
        except PipelineError:
            raise
        except (ImportError, OSError, RuntimeError, MemoryError) as error:
            raise _unavailable() from error
        except Exception as error:
            raise _invalid() from error

    def close(self) -> None:
        self._pipeline = None

    @staticmethod
    def _turns(output: object) -> list[Turn]:
        try:
            items = list(output.exclusive_speaker_diarization)  # type: ignore[attr-defined]
            turns = []
            for turn, speaker in items:
                start_ms = round(turn.start * 1000)
                end_ms = max(round(turn.end * 1000), start_ms + 1)
                turns.append(Turn(start_ms=start_ms, end_ms=end_ms, speaker_id=str(speaker)))
            return sorted(turns, key=lambda turn: (turn.start_ms, turn.end_ms))
        except (AttributeError, TypeError, ValueError, OverflowError) as error:
            raise _invalid() from error

    def diarize(self, wav_path: Path, max_speakers: int) -> list[Turn]:
        if self._pipeline is None:
            raise _unavailable()
        try:
            output = self._pipeline(str(wav_path), max_speakers=max_speakers)
        except PipelineError:
            raise
        except (ImportError, OSError, RuntimeError, MemoryError) as error:
            raise _unavailable() from error
        except Exception as error:
            raise _invalid() from error
        return self._turns(output)


def download_community1(
    *,
    token: str | None = None,
    models_dir: Path | None = None,
    snapshot: Callable[..., object] | None = None,
) -> None:
    """Download the pinned revision to the private models directory, using HF_TOKEN."""
    secret = os.getenv("HF_TOKEN") if token is None else token
    if not secret:
        raise RuntimeError(DOWNLOAD_MESSAGE)
    if snapshot is None:
        from huggingface_hub import snapshot_download

        snapshot = snapshot_download
    target = Path(models_dir or os.getenv("MODELS_DIR", DEFAULT_MODELS_DIR))
    snapshot(
        repo_id=MODEL_ID,
        revision=MODEL_REVISION,
        token=secret,
        local_dir=str(target / MODEL_ID),
    )


def _peak_memory_mib() -> float:
    """Peak RSS on Linux (CI), traced Python memory where `resource` does not exist."""
    try:
        import resource

        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    except ImportError:
        return tracemalloc.get_traced_memory()[1] / (1024 * 1024)


def _der(turns: list[Turn], reference: Path) -> float:
    """Diarization error rate against a JSON reference with seconds and speaker labels."""
    from pyannote.core import Annotation, Segment
    from pyannote.metrics.diarization import DiarizationErrorRate

    data = json.loads(reference.read_text(encoding="utf-8"))
    expected = Annotation()
    for item in data["turns"]:
        expected[Segment(float(item["start_s"]), float(item["end_s"]))] = str(item["speaker"])
    actual = Annotation()
    for turn in turns:
        actual[Segment(turn.start_ms / 1000, turn.end_ms / 1000)] = turn.speaker_id
    metric = DiarizationErrorRate(collar=0.0, skip_overlap=False)
    return abs(metric(expected, actual))


def measure_diarization(
    audio: Path,
    *,
    max_speakers: int = 2,
    reference: Path | None = None,
    diarizer: Diarizer | None = None,
) -> Mapping[str, str]:
    """Seconds per minute of audio, peak memory and optional DER, with no class data."""
    import wave

    with wave.open(str(audio), "rb") as wav:
        duration_minutes = wav.getnframes() / wav.getframerate() / 60
    if duration_minutes <= 0:
        raise ValueError("audio has no duration")

    adapter = diarizer or PyannoteDiarizer()
    if not tracemalloc.is_tracing():
        tracemalloc.start()
    started = time.perf_counter()
    adapter.load()
    try:
        turns = adapter.diarize(audio, max_speakers)
    finally:
        adapter.close()
    elapsed = time.perf_counter() - started

    result = {
        "model": MODEL_ID,
        "revision": MODEL_REVISION,
        "device": "cpu",
        "seconds_per_minute": f"{elapsed / duration_minutes:.2f}",
        "peak_memory_mib": f"{_peak_memory_mib():.1f}",
        "turns": str(len(turns)),
    }
    if reference is not None:
        result["der"] = f"{_der(turns, reference):.3f}"
    return result


def measure_community1() -> Mapping[str, str]:
    """Entry of `make measure`; needs DIARIZATION_MEASURE_AUDIO to be set."""
    raw = os.getenv("DIARIZATION_MEASURE_AUDIO")
    if not raw:
        return {"status": "no audio configured", "hint": "set DIARIZATION_MEASURE_AUDIO"}
    reference = os.getenv("DIARIZATION_REFERENCE")
    return measure_diarization(
        Path(raw),
        max_speakers=int(os.getenv("DIARIZATION_MAX_SPEAKERS", "2")),
        reference=Path(reference) if reference else None,
    )


register(
    ModelSpec(
        name=MODEL_ID,
        revision=MODEL_REVISION,
        download=download_community1,
        measure=measure_community1,
    )
)
