"""Prueba básica de diarización con pyannote.audio.

Uso:
    python scripts/test_diarization.py <audio1.wav> [audio2.wav ...]

Imprime, para cada segmento detectado: inicio - fin: speaker_id

Requiere:
    - Variable de entorno HF_TOKEN con un token de Hugging Face
    - Haber aceptado las condiciones del modelo en
      https://huggingface.co/pyannote/speaker-diarization-community-1

Nota sobre Windows + Python 3.14 + NumPy 2.0:
    pyannote.audio 3.x usa np.NaN (eliminado en NumPy 2.0). Se añade un
    parche al inicio para asignar np.NaN = np.nan y poder importarlo.
"""

from __future__ import annotations

import os
import sys

import numpy as np

# Parche para NumPy 2.0: np.NaN fue eliminado, usar np.nan
if not hasattr(np, "NaN"):
    np.NaN = np.nan  # type: ignore[attr-defined]

import soundfile as sf
import torch
from pyannote.audio import Pipeline


def diarize(audio_path: str, token: str | None = None) -> None:
    """Ejecuta la diarización sobre un archivo de audio e imprime los resultados.

    Si no se pasa token, se usa el guardado en la caché de huggingface_hub
    (después de hacer `hf auth login`).
    """
    token = token or os.environ.get("HF_TOKEN")

    print(f"\n=== Procesando: {audio_path} ===")

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-community-1",
        use_auth_token=token,
    )

    # Cargar audio con soundfile para evitar torchcodec en Windows
    data, sample_rate = sf.read(audio_path)

    # soundfile devuelve (samples,) para mono o (samples, channels) para estéreo
    if data.ndim == 1:
        audio_mono = data
    else:
        audio_mono = np.mean(data, axis=1)

    # pyannote.audio 3.x acepta dict con tensor de audio
    waveform = torch.from_numpy(audio_mono).float().unsqueeze(0)  # (1, samples)

    diarization = pipeline({"audio": waveform, "sample_rate": sample_rate})

    for segment, track, speaker in diarization.itertracks(yield_label=True):
        print(f"{segment.start:6.1f}s - {segment.end:6.1f}s: {speaker}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python scripts/test_diarization.py <audio1.wav> [audio2.wav ...]")
        sys.exit(1)

    for audio_path in sys.argv[1:]:
        diarize(audio_path)


if __name__ == "__main__":
    main()