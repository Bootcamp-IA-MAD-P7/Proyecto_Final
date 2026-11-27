"""Real-model tests: run only with `make -C backend test-models` after `make -C backend models`."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from app.inference.transcription import FasterWhisperTranscriber, compare_language_detection
from tests.audio import require_ffmpeg
from tests.test_diarization_models import two_voices


def mixed_languages(tmp_path: Path) -> Path:
    """Synthetic speech in two languages, generated at run time."""
    require_ffmpeg()
    target = tmp_path / "mixed.wav"
    result = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "flite=text='Good morning teacher':voice=rms",
            "-f",
            "lavfi",
            "-i",
            "flite=text='Buenos dias clase':voice=slt",
            "-filter_complex",
            "[0:a][1:a]concat=n=2:v=0:a=1,aresample=16000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(target),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip("ffmpeg without libflite: no synthetic speech available")
    return target


def loaded_transcriber() -> FasterWhisperTranscriber:
    transcriber = FasterWhisperTranscriber(models_dir=Path(os.getenv("MODELS_DIR", "data/models")))
    transcriber.load()
    return transcriber


@pytest.mark.models
def test_whisper_small_transcribes_synthetic_speech(tmp_path: Path) -> None:
    audio = two_voices(tmp_path)
    transcriber = loaded_transcriber()
    try:
        phrases = transcriber.transcribe(audio)
    finally:
        transcriber.close()

    assert phrases
    assert all(phrase.words for phrase in phrases)
    assert all(0 <= word.start_ms < word.end_ms for phrase in phrases for word in phrase.words)


@pytest.mark.models
def test_language_detection_compares_single_and_per_phrase(tmp_path: Path) -> None:
    audio = mixed_languages(tmp_path)
    transcriber = loaded_transcriber()
    try:
        result = compare_language_detection(audio, lambda: transcriber._engine)
    finally:
        transcriber.close()

    assert result["language_single"]
    assert result["language_per_phrase"]
