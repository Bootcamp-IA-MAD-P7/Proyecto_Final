"""Diarización real para el pipeline de inferencia (Historia 2 de US-012 / E3).

Detecciona los hablantes de un archivo de audio y devuelve una lista de
``DiaronSegment`` con los intervalos de intervención y un ``speaker_id`` de
sesión por segmento. No equivale a participantes: según el ADR-0003 y el
scripts de prueba, se admite ``participant_id`` nulo (edición de asociaciones
pertenece a la historia 017).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

WINDOW_SECONDS = 0.5  # tamaño de cada ventana para clustering (fallback)
HOP_SECONDS = 0.1  # salto entre ventanas (fallback)
DEFAULT_N_SPEAKERS = 2  # número de hablantes por defecto


@dataclass(frozen=True)
class DiaronSegment:
    """Un segmento diarizado: [start_s, end_s) atribuido a un hablante de sesión."""

    start_s: float
    end_s: float
    speaker_id: str


class Diarizer(Protocol):
    """Motor de diarización: devuelve segmentos (start_s, end_s, speaker_id)."""

    def diarize(self, audio_path: str, n_speakers: int) -> list[DiaronSegment]: ...


class PyannoteDiarizer:
    """Diarización real con pyannote.audio (speaker-diarization-3.1)."""

    def diarize(self, audio_path: str, n_speakers: int) -> list[DiaronSegment]:
        try:
            from pyannote.audio import Pipeline
        except ImportError as error:
            raise ImportError(
                "pyannote.audio no está instalado. Instálalo con: pip install pyannote.audio"
            ) from error

        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
        diarization = pipeline(audio_path, num_speakers=n_speakers)

        return [
            DiaronSegment(start_s=turn.start, end_s=turn.end, speaker_id=speaker)
            for turn, _, speaker in diarization.itertracks(yield_label=True)
        ]


class SklearnDiarizer:
    """Diarización de fallback con librosa + scikit-learn (clustering jerárquico).

    Extrae MFCC en ventanas, agrupa por clustering jerárquico y une frames
    consecutivos del mismo hablante en segmentos.
    """

    def diarize(self, audio_path: str, n_speakers: int) -> list[DiaronSegment]:
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

        return group_segments(labels, HOP_SECONDS)


def group_segments(speaker_ids: list[int], hop_seconds: float) -> list[DiaronSegment]:
    """Agrupa frames consecutivos del mismo speaker en segmentos."""
    if len(speaker_ids) == 0:
        return []

    segments: list[DiaronSegment] = []
    current_speaker = speaker_ids[0]
    start_frame = 0

    for i in range(1, len(speaker_ids)):
        if speaker_ids[i] != current_speaker:
            segments.append(
                DiaronSegment(
                    start_s=start_frame * hop_seconds,
                    end_s=(i - 1) * hop_seconds,
                    speaker_id=f"speaker_{current_speaker}",
                )
            )
            current_speaker = speaker_ids[i]
            start_frame = i

    segments.append(
        DiaronSegment(
            start_s=start_frame * hop_seconds,
            end_s=(len(speaker_ids) - 1) * hop_seconds,
            speaker_id=f"speaker_{current_speaker}",
        )
    )
    return segments


def load_diarizer() -> Diarizer:
    """Devuelve el mejor motor disponible: pyannote.audio, Sklearn de fallback."""
    try:
        import pyannote.audio  # noqa: F401

        return PyannoteDiarizer()
    except Exception:
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


def run_diarization(
    audio_path: str | Path, n_speakers: int = DEFAULT_N_SPEAKERS
) -> list[DiaronSegment]:
    """Diariza un archivo de audio y devuelve sus segmentos."""
    return load_diarizer().diarize(str(audio_path), n_speakers)
