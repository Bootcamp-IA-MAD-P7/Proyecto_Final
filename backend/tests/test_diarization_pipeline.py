"""Pruebas de Historia 2 de US-012 / E3: etapa DIARIZING en inference pipeline y worker.

Cubren:
- run_diarization sobre audio sintético produce segmentos con speaker_id y end_s > start_s.
- transcript_from_diarization genera un Transcript conforme al contrato v0.1
  (speakers distintos, segmentos referenciados y fin mayor que inicio).
- RealPipeline reporta la etapa DIARIZING y devuelve el transcript diarizado.
- Worker (InMemoryJobStore) avanza un trabajo por DIARIZING hasta ready_for_review
  usando RealPipeline.
"""

from __future__ import annotations

import wave

import numpy as np

from app.contract import JobStage, JobState
from app.inference.diarization import DiaronSegment, run_diarization
from app.inference.real_pipeline import RealPipeline, transcript_from_diarization


def _synthetic_wav(tmp_path):
    """Audio sintético de 2 tonos: 1 segundo de 200 Hz + 1 segundo de 400 Hz."""
    sample_rate = 16000
    t = np.linspace(0, 2, 2 * sample_rate, endpoint=False)
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
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())
    return audio_path


def test_run_diarization_two_speakers(tmp_path):
    """Audio sintético con dos tonos produce segmentos con fin mayor que inicio."""
    segments = run_diarization(str(_synthetic_wav(tmp_path)), n_speakers=2)

    assert segments
    for seg in segments:
        assert isinstance(seg, DiaronSegment)
        assert seg.end_s > seg.start_s
        assert seg.speaker_id


def test_transcript_from_diarization_complies_with_contract():
    """Transcript v0.1: speakers distintos y segmentos con end_ms > start_ms."""
    transcript = transcript_from_diarization(
        [
            DiaronSegment(0.0, 1.0, "speaker_0"),
            DiaronSegment(1.5, 2.5, "speaker_1"),
        ]
    )

    transcript.model_validate(transcript.model_dump())
    speakers = {s.speaker_id for s in transcript.speakers}
    assert speakers == {"speaker_0", "speaker_1"}
    for seg in transcript.segments:
        assert seg.speaker_id in speakers
        assert seg.end_ms > seg.start_ms


def test_real_pipeline_reports_diarizing_stage(tmp_path):
    """RealPipeline reporta DIARIZING entre estadígrafos y devuelve transcript real."""
    stages: list[JobStage] = []

    class Stages:
        def __call__(self, stage):
            stages.append(stage)

    audio_path = str(_synthetic_wav(tmp_path))
    out = RealPipeline().run(
        __import__("app.inference.pipeline", fromlist=["PipelineInput"]).PipelineInput(
            class_id="class-01", metadata=None, audio_path=audio_path
        ),
        Stages(),
    )

    assert JobStage.DIARIZING in stages
    assert out.transcript.speakers
    for seg in out.transcript.segments:
        assert seg.speaker_id in {s.speaker_id for s in out.transcript.speakers}


def test_worker_advances_through_diarizing(tmp_path):
    """Worker con RealPipeline trae un trabajo por DIARIZING hasta ready_for_review."""
    from app.jobs import InMemoryJobStore
    from app.worker import Worker
    from tests.conftest import load_fixture

    store = InMemoryJobStore()
    stored = store.create_class(
        __import__("app.contract", fromlist=["ClassMetadata"]).ClassMetadata.model_validate(
            load_fixture("valid/class-metadata.json")
        ),
        "demo-teacher",
    )
    job = Worker(store, RealPipeline()).run_once()

    assert job.job_id == stored.job_id
    assert job.state is JobState.READY_FOR_REVIEW
