"""Seconds per minute of audio and peak memory of each stage (task 6.4, RNF-04).

Usage, inside the worker image with the models prepared (root `make measure-stages AUDIO=...`):

    python scripts/measure-stages.py <audio>

Each stage runs in its own process, so its peak memory is its own: FFmpeg normalizes the file to
a private temporary WAV, then faster-whisper and Community-1 process that WAV with the adapters
of the worker. Only numbers are printed, one JSON line per stage: never text, turns or names.
"""

from __future__ import annotations

import json
import os
import resource
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path


def _peak_mib(who: int) -> float:
    return resource.getrusage(who).ru_maxrss / 1024  # KiB on Linux


def _report(stage: str, seconds: float, minutes: float, peak: float) -> None:
    print(
        json.dumps(
            {
                "stage": stage,
                "audio_minutes": round(minutes, 2),
                "seconds": round(seconds, 1),
                "seconds_per_minute": round(seconds / minutes, 2),
                "peak_memory_mib": round(peak, 1),
            }
        ),
        flush=True,
    )


def run_stage(stage: str, wav: Path) -> None:
    """One stage in this process: load its model, process the WAV and release it."""
    from app.inference.diarization import PyannoteDiarizer
    from app.inference.transcription import FasterWhisperTranscriber
    from app.settings import Settings

    settings = Settings.from_env()
    models_dir = Path(settings.models_dir)
    with wave.open(str(wav), "rb") as source:
        minutes = source.getnframes() / source.getframerate() / 60
    started = time.perf_counter()
    if stage == "transcribing":
        transcriber = FasterWhisperTranscriber(
            model=settings.asr_model,
            device=settings.asr_device,
            compute_type=settings.asr_compute_type,
            language=settings.asr_language,
            models_dir=models_dir,
        )
        transcriber.load()
        transcriber.transcribe(wav)
        transcriber.close()
    else:
        diarizer = PyannoteDiarizer(models_dir=models_dir)
        diarizer.load()
        diarizer.diarize(wav, int(os.getenv("DIARIZATION_MAX_SPEAKERS", "2")))
        diarizer.close()
    _report(stage, time.perf_counter() - started, minutes, _peak_mib(resource.RUSAGE_SELF))


def main(audio: Path) -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    with tempfile.TemporaryDirectory() as temporary:
        from app.inference.normalization import FfmpegNormalizer

        started = time.perf_counter()
        wav = FfmpegNormalizer().normalize(audio, Path(temporary))
        elapsed = time.perf_counter() - started
        with wave.open(str(wav), "rb") as source:
            minutes = source.getnframes() / source.getframerate() / 60
        _report("normalizing", elapsed, minutes, _peak_mib(resource.RUSAGE_CHILDREN))
        for stage in ("transcribing", "diarizing"):
            subprocess.run([sys.executable, __file__, "--stage", stage, str(wav)], check=True)


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--stage":
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        run_stage(sys.argv[2], Path(sys.argv[3]))
    elif len(sys.argv) == 2:
        main(Path(sys.argv[1]))
    else:
        raise SystemExit("usage: python scripts/measure-stages.py <audio>")
