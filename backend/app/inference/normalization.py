"""FFmpeg normalizer: local file to 16 kHz mono WAV in the job's work directory.

Normalizing does not change the timeline, so word timestamps keep referring to the original
recording. An undecodable file fails the stage with `invalid_audio`, without retry.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from app.contract import JobErrorCode
from app.inference.pipeline import PipelineError
from app.inference.types import Normalizer

INVALID_AUDIO_MESSAGE = "No se ha podido decodificar el audio."
UNAVAILABLE_MESSAGE = "FFmpeg no está disponible."


class FfmpegNormalizer(Normalizer):
    def load(self) -> None:
        return None

    def close(self) -> None:
        return None

    def normalize(self, audio_path: Path, work_dir: Path) -> Path:
        target = work_dir / "audio.wav"
        command = [
            "ffmpeg",
            "-y",
            "-nostdin",
            "-loglevel",
            "error",
            "-i",
            str(audio_path),
            "-ar",
            "16000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(target),
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
        except OSError as error:
            raise PipelineError(
                JobErrorCode.PROCESSING_UNAVAILABLE, UNAVAILABLE_MESSAGE, retryable=True
            ) from error
        if result.returncode != 0:
            raise PipelineError(JobErrorCode.INVALID_AUDIO, INVALID_AUDIO_MESSAGE, retryable=False)
        return target
