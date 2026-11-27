"""Inference: staged pipeline, adapter interfaces and the worker's pipeline contract."""

# Importing the adapter registers its download and measurement in the model registry.
import app.inference.diarization  # noqa: F401
from app.inference.adapters import EmptyAnalyzer
from app.inference.fake import FakePipeline
from app.inference.pipeline import (
    InferencePipeline,
    PipelineError,
    PipelineInput,
    PipelineOutput,
    StageCallback,
)
from app.inference.speakers import assign_speakers
from app.inference.staged import StagedPipeline
from app.inference.types import (
    Analyzer,
    Diarizer,
    ModelAdapter,
    Normalizer,
    Phrase,
    Transcriber,
    Turn,
    Word,
)

__all__ = [
    "Analyzer",
    "Diarizer",
    "EmptyAnalyzer",
    "FakePipeline",
    "InferencePipeline",
    "ModelAdapter",
    "Normalizer",
    "Phrase",
    "PipelineError",
    "PipelineInput",
    "PipelineOutput",
    "StageCallback",
    "StagedPipeline",
    "Transcriber",
    "Turn",
    "Word",
    "assign_speakers",
]
