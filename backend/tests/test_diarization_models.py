"""Real-model tests: run only with `make -C backend test-models` after `make -C backend models`."""

from __future__ import annotations

import os
import shutil
import subprocess
from itertools import pairwise
from pathlib import Path

import pytest

from app.inference.diarization import PyannoteDiarizer
from tests.audio import require_ffmpeg


def two_voices(tmp_path: Path) -> Path:
    """Six seconds of 16 kHz mono audio alternating two synthetic voices."""
    require_ffmpeg()
    target = tmp_path / "two-voices.wav"
    expression = "0.3*sin(2*PI*220*t)*lte(mod(t,2),1)+0.3*sin(2*PI*440*t)*gt(mod(t,2),1)"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            f"aevalsrc={expression}:s=16000:d=6",
            "-c:a",
            "pcm_s16le",
            str(target),
        ],
        check=True,
    )
    return target


@pytest.mark.models
def test_community1_returns_exclusive_turns_for_two_synthetic_voices(tmp_path: Path) -> None:
    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg not installed")
    audio = two_voices(tmp_path)
    diarizer = PyannoteDiarizer(models_dir=Path(os.getenv("MODELS_DIR", "data/models")))

    diarizer.load()
    try:
        turns = diarizer.diarize(audio, 2)
    finally:
        diarizer.close()

    assert turns
    assert all(turn.end_ms > turn.start_ms for turn in turns)
    assert len({turn.speaker_id for turn in turns}) <= 2
    assert all(previous.end_ms <= following.start_ms for previous, following in pairwise(turns))
