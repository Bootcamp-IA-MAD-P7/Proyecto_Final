"""Worker: takes queued jobs one by one and runs the InferencePipeline on them (ADR-0002).

A single worker. At start it returns the jobs left in progress to the queue, so that a restart
never leaves a job blocked; then it claims the oldest queued job, records each stage, and either
saves a contract result (`ready_for_review`) or moves the job to `failed` with a contract error.
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from app.contract import (
    CONTRACT_VERSION,
    Job,
    JobError,
    JobErrorCode,
    JobState,
    Publication,
    PublicationStatus,
    Result,
    Review,
    ReviewStatus,
)
from app.inference import InferencePipeline, PipelineError, PipelineInput, PipelineOutput
from app.jobs import JobStore, StoredClass
from app.jobs.store import InvalidJobTransitionError

logger = logging.getLogger("app.worker")

FAILED_MESSAGE = "No se ha podido procesar la clase."


class StoreError(Exception):
    """The JobStore failed while the pipeline was running: the job is not to blame."""


def _now() -> datetime:
    return datetime.now(UTC)


class Worker:
    def __init__(
        self,
        store: JobStore,
        pipeline: InferencePipeline,
        review_period: timedelta = timedelta(hours=24),
        clock: Callable[[], datetime] = _now,
    ) -> None:
        self._store = store
        self._pipeline = pipeline
        self._review_period = review_period
        self._clock = clock

    def start(self) -> int:
        """Expire jobs whose audio is past its date, then requeue those still in progress.

        Maintenance purges at startup too, but the worker must not resume an expired job even
        if it starts first (ADR-0004).
        """
        self._store.expire_jobs(self._clock())
        requeued = self._store.requeue_in_progress()
        logger.info("worker ready", extra={"count": requeued})
        return requeued

    def run_once(self) -> Job | None:
        """Process the next queued job, if any, and return it in its final state."""
        job = self._store.claim_next()
        if job is None:
            return None
        logger.info("job claimed", extra={"job_id": job.job_id, "stage": job.stage})
        stored = self._store.get_class(job.class_id)
        try:
            if stored is None:
                raise LookupError(f"Class of {job.job_id} not found")
            output = self._run_pipeline(job, stored)
            result = self._result(job, output)
        except StoreError as error:
            if isinstance(error.__cause__, InvalidJobTransitionError):
                discarded = self._discarded(job.job_id)
                if discarded is not None:
                    return discarded
            # Not a failure of the class: run() retries and the job goes back to the queue.
            raise error.__cause__ from None
        except InvalidJobTransitionError:
            discarded = self._discarded(job.job_id)
            if discarded is not None:
                return discarded
            raise
        except PipelineError as error:
            return self._fail(job, error.error, type(error).__name__)
        except Exception as error:
            # An invalid result or an unexpected error. Only its type is logged: the message
            # could carry data of the class.
            return self._fail(job, _processing_failed(), type(error).__name__)
        discarded = self._discarded(job.job_id)
        if discarded is not None:
            return discarded
        try:
            done = self._store.complete(job.job_id, result)
        except InvalidJobTransitionError:
            # Maintenance may have expired it between the check and the write (ADR-0002).
            discarded = self._discarded(job.job_id)
            if discarded is not None:
                return discarded
            raise
        logger.info("job ready for review", extra={"job_id": job.job_id, "state": done.state})
        return done

    def _discarded(self, job_id: str) -> Job | None:
        """The job if maintenance expired it; the late result is never saved (ADR-0002)."""
        current = self._store.get_job(job_id)
        if current is not None and current.state is JobState.EXPIRED:
            logger.info("expired job result discarded", extra={"job_id": job_id})
            return current
        return None

    def run(self, stop: threading.Event, poll_seconds: float = 1) -> None:
        """Process jobs until `stop` is set.

        If the store fails, the worker waits and starts again: the job it was processing goes
        back to the queue, which is safe because there is a single worker (ADR-0002).
        """
        started = False
        while not stop.is_set():
            try:
                if not started:
                    self.start()
                    started = True
                if self.run_once() is not None:
                    continue
            except Exception as error:
                # Usually the database is not available. Retries have no limit for now: a real
                # retry policy (retry_wait) arrives with E2.
                started = False
                logger.error("worker loop failed", extra={"error_type": type(error).__name__})
            stop.wait(poll_seconds)
        logger.info("worker stopped")

    def _run_pipeline(self, job: Job, stored: StoredClass) -> PipelineOutput:
        def on_stage(stage):
            try:
                self._store.advance(job.job_id, stage)
            except Exception as error:
                raise StoreError from error
            logger.info("job stage", extra={"job_id": job.job_id, "stage": stage})

        job_input = PipelineInput(class_id=job.class_id, metadata=stored.metadata, audio_path=None)
        return self._pipeline.run(job_input, on_stage)

    def _result(self, job: Job, output: PipelineOutput) -> Result:
        """First version of the result: pending review and unpublished. Validated by the model."""
        return Result.model_validate(
            {
                "schema_version": CONTRACT_VERSION,
                "class_id": job.class_id,
                "result_version": 1,
                "transcript": output.transcript,
                "analysis": output.analysis,
                "review": Review(
                    status=ReviewStatus.PENDING,
                    review_due_at=self._clock() + self._review_period,
                ),
                "publication": Publication(
                    status=PublicationStatus.UNPUBLISHED,
                    result_version=None,
                    published_at=None,
                    mode=None,
                ),
            }
        )

    def _fail(self, job: Job, error: JobError, error_type: str) -> Job:
        try:
            failed = self._store.fail(job.job_id, error)
        except InvalidJobTransitionError:
            # Maintenance may have expired it while the pipeline was failing.
            discarded = self._discarded(job.job_id)
            if discarded is not None:
                return discarded
            raise
        logger.warning(
            "job failed",
            extra={"job_id": job.job_id, "error_code": error.code, "error_type": error_type},
        )
        return failed


def _processing_failed() -> JobError:
    return JobError(code=JobErrorCode.PROCESSING_FAILED, message=FAILED_MESSAGE, retryable=False)
