"""Prueba básica de diarización con pyannote.audio.

Uso:
    python scripts/test_diarization.py <audio1.wav> [audio2.wav ...]

Imprime, para cada segmento detectado: inicio - fin: speaker_id

Requiere:
    - Variable de entorno HF_TOKEN con un token de Hugging Face
    - Haber aceptado las condiciones del modelo en
      https://huggingface.co/pyannote/speaker-diarization-community-1
"""

from __future__ import annotations

import os
import sys

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
        token=token,
    )

    diarization = pipeline(audio_path)

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
