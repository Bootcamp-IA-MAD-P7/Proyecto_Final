"""Real-model tests: run only with `make -C backend test-models` after `make -C backend models`."""

from __future__ import annotations

import os
import subprocess
from itertools import pairwise
from pathlib import Path

import pytest

from app.inference.diarization import PyannoteDiarizer
from tests.audio import require_ffmpeg


def two_voices(tmp_path: Path) -> Path:
    """Two synthetic speech voices (flite) in one 16 kHz mono WAV, generated at run time."""
    require_ffmpeg()
    target = tmp_path / "two-voices.wav"
    result = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            "flite=text='Hello class today':voice=slt",
            "-f",
            "lavfi",
            "-i",
            "flite=text='Good morning teacher':voice=rms",
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


@pytest.mark.models
def test_community1_returns_exclusive_turns_for_two_synthetic_voices(tmp_path: Path) -> None:
    audio = two_voices(tmp_path)
    diarizer = PyannoteDiarizer(models_dir=Path(os.getenv("MODELS_DIR", "data/models")))

    diarizer.load()
    try:
        turns = diarizer.diarize(audio, 2)
    finally:
        diarizer.close()

    assert turns
    assert all(turn.end_ms > turn.start_ms for turn in turns)
    assert len({turn.speaker_id for turn in turns}) == 2
    assert all(previous.end_ms <= following.start_ms for previous, following in pairwise(turns))
