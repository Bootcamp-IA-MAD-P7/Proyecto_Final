"""Synthetic audio for the tests, generated with ffmpeg when they run: no audio is versioned.

Tests that need it use the `synthetic_audio` fixture, which skips them with a warning when ffmpeg
is not installed. The backend image installs it, so `make ci` always runs them.
"""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

ENCODERS = {
    "ogg": ["-c:a", "libopus", "-b:a", "16k"],
    "webm": ["-c:a", "libopus", "-b:a", "16k"],
    "mp3": ["-c:a", "libmp3lame", "-b:a", "32k"],
    "m4a": ["-c:a", "aac", "-b:a", "32k"],
    "mp4": ["-c:a", "aac", "-b:a", "32k"],
    "wav": ["-c:a", "pcm_s16le"],
    "flac": ["-c:a", "flac"],
}
"""Container (file extension) and encoder of each kind of synthetic audio."""

SyntheticAudio = Callable[..., Path]


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def require_ffmpeg() -> None:
    if not ffmpeg_available():
        pytest.skip(
            "ffmpeg/ffprobe not installed: audio validation tests skipped (make ci runs them)"
        )


def make_audio(
    directory: Path, kind: str = "ogg", seconds: float = 2, *, video: bool = False
) -> Path:
    """A tone of `seconds` in the container and codec of `kind`, optionally with a video track."""
    require_ffmpeg()
    target = directory / f"synthetic-{kind}-{seconds:g}{'-video' if video else ''}.{kind}"
    if target.exists():
        return target
    inputs = ["-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}"]
    video_args: list[str] = []
    if video:
        inputs += ["-f", "lavfi", "-i", f"color=size=16x16:rate=1:duration={seconds}"]
        video_args = ["-c:v", "libvpx" if kind == "webm" else "mpeg4"]
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", *inputs, *ENCODERS[kind], *video_args, str(target)],
        check=True,
        timeout=60,
    )
    return target


@pytest.fixture(scope="session")
def synthetic_audio(tmp_path_factory: pytest.TempPathFactory) -> SyntheticAudio:
    directory = tmp_path_factory.mktemp("synthetic-audio")

    def make(kind: str = "ogg", seconds: float = 2, *, video: bool = False) -> Path:
        return make_audio(directory, kind, seconds, video=video)

    require_ffmpeg()
    return make
