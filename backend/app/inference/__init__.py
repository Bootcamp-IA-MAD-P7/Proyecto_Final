"""Inference: the InferencePipeline interface that the worker runs."""

from app.inference.diarization import Diarizer, DiaronSegment, run_diarization
from app.inference.fake import FakePipeline
from app.inference.pipeline import (
    InferencePipeline,
    PipelineError,
    PipelineInput,
    PipelineOutput,
    StageCallback,
)
from app.inference.real_pipeline import RealPipeline

__all__ = [
    "Diarizer",
    "DiaronSegment",
    "FakePipeline",
    "InferencePipeline",
    "PipelineError",
    "PipelineInput",
    "PipelineOutput",
    "RealPipeline",
    "StageCallback",
    "run_diarization",
]
