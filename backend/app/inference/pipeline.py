"""InferencePipeline: from the audio and metadata of a class to its transcript and analysis.

Internal interface (design of add-walking-skeleton): the worker runs it without knowing which
models are behind. Section 3 brings FakePipeline; E3 and E4 replace it with real models.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from app.contract import Analysis, ClassMetadata, JobError, JobErrorCode, JobStage, Transcript


@dataclass(frozen=True)
class PipelineInput:
    class_id: str
    metadata: ClassMetadata
    audio_path: Path | None
    """Private copy of the audio. None until E2 stores it."""


@dataclass(frozen=True)
class PipelineOutput:
    """What the models produce. The worker adds the versions, review and publication."""

    transcript: Transcript
    analysis: Analysis


class PipelineError(Exception):
    """A stage failed. The job moves to `failed` with this contract error."""

    def __init__(self, code: JobErrorCode, message: str, retryable: bool = False) -> None:
        super().__init__(message)
        self.error = JobError(code=code, message=message, retryable=retryable)


StageCallback = Callable[[JobStage], None]
"""Called when a stage starts, so that the worker records it in the JobStore."""


@runtime_checkable
class InferencePipeline(Protocol):
    def run(self, job_input: PipelineInput, on_stage: StageCallback) -> PipelineOutput:
        """Run every stage in order, calling `on_stage` as each one starts.

        Raises PipelineError when a stage fails; the output must comply with the contract.
        """
        ...
