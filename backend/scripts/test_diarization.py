"""Prueba básica de diarización con pyannote.audio y fallback a librosa+scikit-learn.

Uso:
    python scripts/test_diarization.py <audio.wav> [--n-speakers N]

Imprime, para cada segmento detectado: inicio - fin: speaker_id

Motores (en orden de preferencia):
    1. pyannote.audio (speaker-diarization-community-1): modelo real de diarización.
    2. librosa + scikit-learn: clustering jerárquico con MFCC, funciona en Windows sin GPU.

Requisitos:
    - pyannote.audio, torch (motor real; requiere GPU recomendada y acceso a pesos)
    - librosa, scikit-learn, numpy, soundfile (fallback de código abierto, sin GPU)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Protocol

WINDOW_SECONDS = 0.5  # tamaño de cada ventana para clustering (fallback)
HOP_SECONDS = 0.1  # salto entre ventanas (fallback)
DEFAULT_N_SPEAKERS = 2  # número de hablantes por defecto


class Diarizer(Protocol):
    """Motor de diarización: devuelve lista de (inicio_s, fin_s, speaker_id)."""

    def diarize(self, audio_path: str, n_speakers: int) -> list[tuple[float, float, str]]:
        """Diariza el archivo y devuelve segmentos (start_s, end_s, speaker_id)."""
        ...


class PyannoteDiarizer:
    """Diarización real con pyannote.audio (speaker-diarization-community-1)."""

    def diarize(self, audio_path: str, n_speakers: int) -> list[tuple[float, float, str]]:
        try:
            from pyannote.audio import Pipeline
        except ImportError as error:
            raise ImportError(
                "pyannote.audio no está instalado. Instálalo con: pip install pyannote.audio"
            ) from error

        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=None,
        )
        diarization = pipeline(audio_path, num_speakers=n_speakers)

        segments: list[tuple[float, float, str]] = []
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            segments.append((segment.start, segment.end, speaker))
        return segments


class SklearnDiarizer:
    """Diarización de fallback con librosa + scikit-learn (clustering jerárquico, 2 hablantes).

    Extrae MFCC en ventanas, agrupa por clustering jerárquico y une frames consecutivos
    del mismo hablante en segmentos.
    """

    def diarize(self, audio_path: str, n_speakers: int) -> list[tuple[float, float, str]]:
        import librosa
        import numpy as np
        from sklearn.cluster import AgglomerativeClustering

        waveform, sr = librosa.load(audio_path, sr=16000, mono=True)
        mfcc = librosa.feature.mfcc(
            y=waveform,
            sr=sr,
            n_mfcc=13,
            hop_length=int(sr * HOP_SECONDS),
            n_fft=int(sr * WINDOW_SECONDS),
        ).T  # (n_frames, n_mfcc)

        if len(mfcc) < n_speakers:
            labels = np.zeros(len(mfcc), dtype=int)
        else:
            clustering = AgglomerativeClustering(
                n_clusters=n_speakers,
                linkage="average",
                metric="euclidean",
            )
            labels = clustering.fit_predict(mfcc)

        return group_segments(labels, HOP_SECONDS, n_speakers)


def group_segments(
    speaker_ids: list[int], hop_seconds: float, n_speakers: int
) -> list[tuple[float, float, str]]:
    """Agrupa frames consecutivos del mismo speaker en segmentos (start_s, end_s, speaker_id)."""
    if len(speaker_ids) == 0:
        return []

    segments: list[tuple[float, float, str]] = []
    current_speaker = speaker_ids[0]
    start_frame = 0

    for i in range(1, len(speaker_ids)):
        if speaker_ids[i] != current_speaker:
            end_frame = i - 1
            segments.append(
                (
                    start_frame * hop_seconds,
                    end_frame * hop_seconds,
                    f"speaker_{current_speaker}",
                )
            )
            current_speaker = speaker_ids[i]
            start_frame = i

    # Último segmento
    segments.append(
        (
            start_frame * hop_seconds,
            (len(speaker_ids) - 1) * hop_seconds,
            f"speaker_{current_speaker}",
        )
    )

    return segments


def load_diarizer() -> Diarizer:
    """Devuelve el mejor motor disponible: pyannote.audio primero, sklearn de fallback."""
    try:
        import pyannote.audio  # noqa: F401  (comprueba que el paquete existe)

        return PyannoteDiarizer()
    except ImportError:
        pass

    try:
        import librosa  # noqa: F401
        import sklearn  # noqa: F401

        return SklearnDiarizer()
    except ImportError as error:
        raise ImportError(
            "No hay motor de diarización disponible. Instala pyannote.audio "
            "o librosa + scikit-learn."
        ) from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Diariza un archivo de audio e imprime speaker_id por segmento."
    )
    parser.add_argument("audio", help="Ruta al archivo de audio (WAV u otro compatible).")
    parser.add_argument(
        "--n-speakers",
        type=int,
        default=DEFAULT_N_SPEAKERS,
        help="Número de hablantes a detectar (por defecto: 2).",
    )
    args = parser.parse_args(argv)

    audio_path = args.audio
    if not Path(audio_path).is_file():
        print(f"Archivo no encontrado: {audio_path}", file=sys.stderr)
        return 1

    try:
        diarizer = load_diarizer()
    except ImportError as error:
        print(str(error), file=sys.stderr)
        return 1

    print(f"\n=== Diarizando: {audio_path} ===")
    print(f"Motor: {type(diarizer).__name__}, hablantes: {args.n_speakers}")

    try:
        segments = diarizer.diarize(audio_path, args.n_speakers)
    except Exception as error:  # pyannote.audio puede fallar por falta de GPU o pesos
        print(f"Error al diarizar: {error}", file=sys.stderr)
        return 1

    for start, end, speaker in segments:
        print(f"{start:6.1f}s - {end:6.1f}s: {speaker}")

    print(f"\nSegmentos detectados: {len(segments)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
