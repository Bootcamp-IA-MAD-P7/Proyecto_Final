"""FakePipeline: simulated processing of the walking skeleton, until E3 and E4 bring real models.

It returns the synthetic result of the contract examples, validated against the contract, and
waits `FAKE_STAGE_SECONDS` in each stage so that the progress can be followed from the web.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from pathlib import Path

from app.contract import Analysis, JobStage, Transcript
from app.inference.pipeline import PipelineInput, PipelineOutput, StageCallback

SYNTHETIC_RESULT = (
    Path(__file__).resolve().parents[1] / "contract" / "examples" / "result-draft.json"
)


def load_synthetic_output() -> PipelineOutput:
    """Transcript and analysis of the draft example, validated against the contract."""
    example = json.loads(SYNTHETIC_RESULT.read_text(encoding="utf-8"))
    return PipelineOutput(
        transcript=Transcript.model_validate(example["transcript"]),
        analysis=Analysis.model_validate(example["analysis"]),
    )


class FakePipeline:
    """InferencePipeline that ignores the audio and always gives the same synthetic output."""

    def __init__(
        self, stage_seconds: float = 0, sleep: Callable[[float], object] = time.sleep
    ) -> None:
        self._stage_seconds = stage_seconds
        self._sleep = sleep
        self._output = load_synthetic_output()

    def run(self, job_input: PipelineInput, on_stage: StageCallback) -> PipelineOutput:
        for stage in JobStage:
            on_stage(stage)
            if self._stage_seconds:
                self._sleep(self._stage_seconds)
        return self._output
