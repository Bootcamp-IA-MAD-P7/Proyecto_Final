"""Prueba básica de diarización con librerías open source (sin pyannote.audio).

Uso:
    python scripts/test_diarization.py <audio1.wav> [audio2.wav ...]

Imprime, para cada segmento detectado: inicio - fin: speaker_id

Método:
    1. Cargar audio con librosa (backend soundfile, sin torchcodec)
    2. Extraer MFCC en ventanas de 32 ms
    3. Clustering jerárquico con 2 clusters (2 hablantes) mediante scikit-learn
    4. Agrupar frames consecutivos del mismo hablante en segmentos

Requisitos:
    - librosa, scikit-learn, numpy, soundfile (open source, funcionan en Windows)
"""

from __future__ import annotations

import sys
from pathlib import Path

import librosa
import numpy as np
from sklearn.cluster import AgglomerativeClustering


WINDOW_SECONDS = 0.5   # tamaño de cada ventana para clustering
HOP_SECONDS = 0.1      # salto entre ventanas
N_SPEAKERS = 2         # número de hablantes a detectar


def load_audio(audio_path: str):
    """Carga audio mono a 16 kHz con librosa (backend soundfile)."""
    waveform, sr = librosa.load(audio_path, sr=16000, mono=True)
    return waveform, sr


def extract_mfcc(waveform: np.ndarray, sr: int) -> np.ndarray:
    """Extrae coeficientes MFCC: forma (n_frames, n_mfcc)."""
    mfcc = librosa.feature.mfcc(
        y=waveform,
        sr=sr,
        n_mfcc=13,
        hop_length=int(sr * HOP_SECONDS),
        n_fft=int(sr * 0.032),
    )
    return mfcc.T  # (n_frames, n_mfcc)


def cluster_speakers(mfcc: np.ndarray, n_speakers: int = N_SPEAKERS) -> np.ndarray:
    """Aplica clustering jerárquico con n_speakers clusters sobre los MFCC.

    Devuelve un array con el speaker_id asignado a cada frame.
    """
    if len(mfcc) < n_speakers:
        return np.zeros(len(mfcc), dtype=int)

    clustering = AgglomerativeClustering(
        n_clusters=n_speakers,
        linkage="average",
        metric="euclidean",
    )
    return clustering.fit_predict(mfcc)


def group_segments(speaker_ids: np.ndarray, hop_seconds: float) -> list[tuple[float, float, int]]:
    """Agrupa frames consecutivos del mismo speaker en segmentos.

    Devuelve lista de (inicio, fin, speaker_id).
    """
    if len(speaker_ids) == 0:
        return []

    segments = []
    current_speaker = speaker_ids[0]
    start_frame = 0

    for i in range(1, len(speaker_ids)):
        if speaker_ids[i] != current_speaker:
            end_frame = i - 1
            segments.append((
                start_frame * hop_seconds,
                end_frame * hop_seconds,
                current_speaker,
            ))
            current_speaker = speaker_ids[i]
            start_frame = i

    # Último segmento
    segments.append((
        start_frame * hop_seconds,
        (len(speaker_ids) - 1) * hop_seconds,
        current_speaker,
    ))

    return segments


def diarize(audio_path: str) -> None:
    """Ejecuta la diarización sobre un archivo de audio e imprime los resultados."""
    print(f"\n=== Procesando: {audio_path} ===")

    waveform, sr = load_audio(audio_path)
    duration = len(waveform) / sr
    print(f"Duración: {duration:.1f}s, muestreo: {sr} Hz")

    mfcc = extract_mfcc(waveform, sr)
    print(f"Frames extraídos: {len(mfcc)}")

    speaker_ids = cluster_speakers(mfcc, N_SPEAKERS)

    segments = group_segments(speaker_ids, HOP_SECONDS)

    # Unir segmentos cortos consecutivos del mismo speaker (menor a 1 segundo)
    merged = []
    for start, end, speaker in segments:
        if merged and merged[-1][2] == speaker and (start - merged[-1][1]) < 1.0:
            # Fusionar con el segmento anterior del mismo speaker si hay poca pausa
            merged[-1] = (merged[-1][0], end, speaker)
        else:
            merged.append((start, end, speaker))

    for start, end, speaker in merged:
        print(f"{start:6.1f}s - {end:6.1f}s: speaker_{speaker}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python scripts/test_diarization.py <audio1.wav> [audio2.wav ...]")
        sys.exit(1)

    for audio_path in sys.argv[1:]:
        diarize(audio_path)


if __name__ == "__main__":
    main()