"""RealPipeline: provee la etapa DIARIZING real (Historia 2 de US-012 / E3).

Sobre los estadígrafos que el skeleton ya declara (NORMALIZING, TRANSCRIBING y
ANALYZING con la funcionalidad histórica del skeleton) ejecuta DIARIZING con
``run_diarization`` y devuelve un ``Transcript`` que cumple el contrato v0.1:
``speaker_id`` de sesión declarado en ``speakers``, segmentos con ``end_ms >
start_ms``. Como en el skeleton, ``audio_path`` es None hasta E2.
"""

from __future__ import annotations

from app.contract import JobStage, Segment, Speaker, Transcript
from app.inference.diarization import DEFAULT_N_SPEAKERS, DiaronSegment, run_diarization
from app.inference.fake import load_synthetic_output
from app.inference.pipeline import PipelineInput, PipelineOutput, StageCallback


def transcript_from_diarization(segments: list[DiaronSegment]) -> Transcript:
    """Convierte los segmentos diarizados en un Transcript conforme al contrato v0.1."""
    speakers = sorted({segment.speaker_id for segment in segments})
    return Transcript(
        speakers=[Speaker(speaker_id=sid, participant_id=None) for sid in speakers],
        segments=[
            Segment(
                segment_id=f"segment-{i + 1:04d}",
                start_ms=int(seg.start_s * 1000),
                end_ms=int(seg.end_s * 1000),
                speaker_id=seg.speaker_id,
                text="segmento diarizado (real, E3)",
            )
            for i, seg in enumerate(segments)
        ],
    )


class RealPipeline:
    """InferencePipeline con la etapa DIARIZING real; otros estadígrafos siguen los del skeleton."""

    def __init__(self, n_speakers: int = DEFAULT_N_SPEAKERS) -> None:
        self._n_speakers = n_speakers
        self._synthetic = load_synthetic_output()

    def run(self, job_input: PipelineInput, on_stage: StageCallback) -> PipelineOutput:
        on_stage(JobStage.NORMALIZING)
        on_stage(JobStage.TRANSCRIBING)
        on_stage(JobStage.DIARIZING)
        transcript = transcript_from_diarization(
            run_diarization(job_input.audio_path, self._n_speakers) if job_input.audio_path else []
        )
        on_stage(JobStage.ANALYZING)
        return PipelineOutput(transcript=transcript, analysis=self._synthetic.analysis)
