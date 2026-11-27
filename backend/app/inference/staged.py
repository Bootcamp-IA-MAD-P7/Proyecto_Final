"""Staged pipeline: one adapter per contract stage, loaded and released within its stage."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from app.contract import JobErrorCode, JobStage
from app.inference.pipeline import InferencePipeline, PipelineError, PipelineInput, PipelineOutput
from app.inference.speakers import assign_speakers
from app.inference.types import Analyzer, Diarizer, ModelAdapter, Normalizer, Transcriber

T = TypeVar("T")
FAILED_MESSAGE = "No se ha podido procesar la clase."


class StagedPipeline(InferencePipeline):
    def __init__(
        self,
        normalizer: Normalizer,
        transcriber: Transcriber,
        diarizer: Diarizer,
        analyzer: Analyzer,
    ) -> None:
        self._normalizer = normalizer
        self._transcriber = transcriber
        self._diarizer = diarizer
        self._analyzer = analyzer

    @staticmethod
    def _use(adapter: ModelAdapter, action: Callable[[], T]) -> T:
        adapter.load()
        try:
            return action()
        except PipelineError:
            raise
        except Exception as error:
            # The adapter's message may carry class data; only a safe contract message is kept.
            raise PipelineError(JobErrorCode.PROCESSING_FAILED, FAILED_MESSAGE) from error
        finally:
            adapter.close()

    def run(self, job_input: PipelineInput, on_stage: Callable[[JobStage], None]) -> PipelineOutput:
        if job_input.audio_path is None:
            raise PipelineError(JobErrorCode.PROCESSING_FAILED, FAILED_MESSAGE)

        work_dir = job_input.audio_path.parent

        on_stage(JobStage.NORMALIZING)
        wav_path = self._use(
            self._normalizer,
            lambda: self._normalizer.normalize(job_input.audio_path, work_dir),
        )

        on_stage(JobStage.TRANSCRIBING)
        phrases = self._use(self._transcriber, lambda: self._transcriber.transcribe(wav_path))

        on_stage(JobStage.DIARIZING)
        turns = self._use(
            self._diarizer,
            lambda: self._diarizer.diarize(wav_path, job_input.metadata.participant_count),
        )
        transcript = assign_speakers(phrases, turns)

        on_stage(JobStage.ANALYZING)
        analysis = self._use(self._analyzer, lambda: self._analyzer.analyze(transcript))

        return PipelineOutput(transcript=transcript, analysis=analysis)
