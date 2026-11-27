"""The worker's pipeline, chosen with INFERENCE_PIPELINE (design of add-diarized-transcription).

`models` joins `StagedPipeline` with the real adapters: FFmpeg, faster-whisper, pyannote
Community-1 and the empty analysis until E4. `fake` keeps the synthetic result of the walking
skeleton, to work without models. Building loads nothing: each adapter loads its model inside its
stage, from MODELS_DIR, so a missing model fails the job and never the worker.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.contract import JobStage
from app.inference import diarization, normalization, transcription
from app.inference.adapters import EmptyAnalyzer
from app.inference.diarization import PyannoteDiarizer
from app.inference.fake import FakePipeline
from app.inference.normalization import FfmpegNormalizer
from app.inference.pipeline import InferencePipeline
from app.inference.staged import StagedPipeline
from app.inference.transcription import FasterWhisperTranscriber
from app.settings import Settings


@dataclass(frozen=True)
class StageModel:
    """What runs in a stage: model, fixed revision, device and compute type (ADR-0003)."""

    stage: JobStage
    model: str
    revision: str
    device: str
    compute_type: str


def stage_models(settings: Settings) -> list[StageModel]:
    """The model of each stage, with no class data, for the worker's startup log."""
    if settings.inference_pipeline == "fake":
        return [StageModel(stage, "fake", "-", "-", "-") for stage in JobStage]
    asr_model, asr_revision = transcription.SUPPORTED_MODELS[settings.asr_model]
    return [
        StageModel(JobStage.NORMALIZING, "ffmpeg", "-", "cpu", normalization.SAMPLE_FORMAT),
        StageModel(
            JobStage.TRANSCRIBING,
            asr_model,
            asr_revision,
            settings.asr_device,
            settings.asr_compute_type,
        ),
        StageModel(
            JobStage.DIARIZING,
            diarization.MODEL_ID,
            diarization.MODEL_REVISION,
            diarization.DEVICE,
            diarization.COMPUTE_TYPE,
        ),
        StageModel(JobStage.ANALYZING, "empty", "-", "-", "-"),
    ]


def build_pipeline(settings: Settings) -> InferencePipeline:
    if settings.inference_pipeline == "fake":
        return FakePipeline(settings.fake_stage_seconds)
    models_dir = Path(settings.models_dir)
    return StagedPipeline(
        normalizer=FfmpegNormalizer(),
        transcriber=FasterWhisperTranscriber(
            model=settings.asr_model,
            device=settings.asr_device,
            compute_type=settings.asr_compute_type,
            language=settings.asr_language,
            models_dir=models_dir,
        ),
        diarizer=PyannoteDiarizer(models_dir=models_dir),
        analyzer=EmptyAnalyzer(),
    )
