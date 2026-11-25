"""Pruebas de la prueba básica de diarización (historia 1 de US-012 / #20).

Cubren:
- group_segments agrupa frames consecutivos del mismo hablante en segmentos.
- SklearnDiarizer produce exactamente dos speaker_id sobre audio sintético de dos tonos.
- load_diarizer prefiere pyannote.audio y cae a sklearn si no está instalado.
- El script devuelve código 0 con un archivo de audio válido.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "test_diarization.py"


def _approx_segments(segments, expected, tol=1e-9):
    """Compara segmentos con tolerancia de punto flotante."""
    assert len(segments) == len(expected), f"{segments} != {expected}"
    for (s1, e1, sp1), (s2, e2, sp2) in zip(segments, expected, strict=True):
        assert abs(s1 - s2) < tol, f"{s1} != {s2}"
        assert abs(e1 - e2) < tol, f"{e1} != {e2}"
        assert sp1 == sp2, f"{sp1} != {sp2}"


def test_group_segments_groups_consecutive_speakers():
    """Frames consecutivos del mismo hablante forman un segmento; cambios crean nuevos."""
    from scripts.test_diarization import group_segments

    speaker_ids = [0, 0, 0, 1, 1, 0, 0]
    segments = group_segments(speaker_ids, hop_seconds=0.1, n_speakers=2)

    _approx_segments(
        segments,
        [
            (0.0, 0.2, "speaker_0"),
            (0.3, 0.4, "speaker_1"),
            (0.5, 0.6, "speaker_0"),
        ],
    )


def test_group_segments_empty_returns_empty():
    from scripts.test_diarization import group_segments

    assert group_segments([], hop_seconds=0.1, n_speakers=2) == []


def test_sklearn_diarizer_two_speakers_on_synthetic_audio(tmp_path):
    """Audio sintético con dos tonos distintos produce exactamente dos speaker_id."""
    import wave

    from scripts.test_diarization import SklearnDiarizer

    sample_rate = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Primer segundo: tono de 200 Hz (hablante 0), segundo segundo: tono de 400 Hz (hablante 1)
    audio = np.concatenate(
        [
            0.3 * np.sin(2 * np.pi * 200 * t[:sample_rate]),
            0.3 * np.sin(2 * np.pi * 400 * t[sample_rate:]),
        ]
    )

    audio_path = tmp_path / "synthetic.wav"
    with wave.open(str(audio_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        pcm = (audio * 32767).astype(np.int16).tobytes()
        wf.writeframes(pcm)

    diarizer = SklearnDiarizer()
    segments = diarizer.diarize(str(audio_path), n_speakers=2)

    speakers = {speaker for _, _, speaker in segments}
    assert len(segments) >= 2
    assert speakers == {"speaker_0", "speaker_1"}
    # Cada segmento tiene fin mayor que inicio
    for start, end, _ in segments:
        assert end > start


def test_load_diarizer_returns_available_engine():
    """load_diarizer devuelve un motor usable: SklearnDiarizer si pyannote no está instalado."""
    from scripts.test_diarization import PyannoteDiarizer, SklearnDiarizer, load_diarizer

    diarizer = load_diarizer()
    assert isinstance(diarizer, (SklearnDiarizer, PyannoteDiarizer))
    # En este entorno sin pyannote.audio, debe ser SklearnDiarizer.
    assert isinstance(diarizer, SklearnDiarizer)


def test_script_exits_zero_on_valid_audio(tmp_path):
    """El script termina con código 0 al recibir un archivo de audio válido."""
    import wave

    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio = 0.3 * np.sin(2 * np.pi * 440 * t)

    audio_path = tmp_path / "tone.wav"
    with wave.open(str(audio_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        pcm = (audio * 32767).astype(np.int16).tobytes()
        wf.writeframes(pcm)

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(audio_path), "--n-speakers", "2"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    assert "speaker_" in result.stdout
    assert "Segmentos detectados:" in result.stdout
