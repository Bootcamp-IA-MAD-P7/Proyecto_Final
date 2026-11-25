"""Inference: the InferencePipeline interface that the worker runs."""

from app.inference.fake import FakePipeline
from app.inference.pipeline import (
    InferencePipeline,
    PipelineError,
    PipelineInput,
    PipelineOutput,
    StageCallback,
)

__all__ = [
    "FakePipeline",
    "InferencePipeline",
    "PipelineError",
    "PipelineInput",
    "PipelineOutput",
    "StageCallback",
]
