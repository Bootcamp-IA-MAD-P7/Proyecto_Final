"""Retry policy of the worker (spec class-processing, «Seguimiento del trabajo por etapas»)."""

import json
import logging
import threading
from datetime import UTC, datetime, timedelta

import pytest

from app.contract import ClassMetadata, JobErrorCode, JobStage, JobState
from app.inference import FakePipeline, PipelineError, PipelineOutput
from app.jobs import InMemoryJobStore, JobStore, PostgresJobStore
from app.logs import JsonFormatter
from app.worker import Worker
from tests.conftest import load_fixture
from tests.test_worker import expired_audio

START = datetime(2026, 11, 27, 10, 0, tzinfo=UTC)


class Clock:
    """Simulated time that the tests move forward."""

    def __init__(self) -> None:
        self.now = START

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **delta: float) -> None:
        self.now += timedelta(**delta)


@pytest.fixture(params=["memory", "postgres"])
def store(request) -> JobStore:
    if request.param == "memory":
        return InMemoryJobStore()
    return PostgresJobStore(request.getfixturevalue("pg"))


@pytest.fixture
def metadata() -> ClassMetadata:
    return ClassMetadata.model_validate(load_fixture("valid/class-metadata.json"))


@pytest.fixture
def clock() -> Clock:
    return Clock()


def unavailable() -> PipelineError:
    return PipelineError(
        JobErrorCode.PROCESSING_UNAVAILABLE, "El modelo no está disponible.", retryable=True
    )


class FlakyPipeline:
    """Fails with `error` at `stage` in its first `failures` runs, then works like FakePipeline."""

    def __init__(self, failures: int, stage: JobStage = JobStage.TRANSCRIBING, error=None) -> None:
        self.failures = failures
        self.stage = stage
        self.error = error or unavailable()
        self.runs = 0

    def run(self, job_input, on_stage) -> PipelineOutput:
        self.runs += 1
        if self.runs > self.failures:
            return FakePipeline(stage_seconds=0).run(job_input, on_stage)
        for stage in JobStage:
            on_stage(stage)
            if stage == self.stage:
                raise self.error
        raise AssertionError("unreachable")


def worker(store: JobStore, pipeline, clock: Clock, max_attempts: int = 3) -> Worker:
    return Worker(
        store,
        pipeline,
        timedelta(hours=24),
        clock=clock,
        max_attempts=max_attempts,
        retry_delay=timedelta(seconds=60),
    )


def test_a_transient_failure_waits_for_a_retry(store, metadata, clock):
    stored = store.create_class(metadata, "demo-teacher")

    job = worker(store, FlakyPipeline(failures=1), clock).run_once()

    assert (job.state, job.stage, job.attempt) == (
        JobState.RETRY_WAIT,
        JobStage.TRANSCRIBING,
        1,
    )
    assert job.error.code is JobErrorCode.PROCESSING_UNAVAILABLE
    assert job.error.retryable is True
    assert store.get_job(stored.job_id) == job
    assert store.get_result(stored.class_id) is None


def test_the_retry_runs_after_its_wait_and_can_finish(store, metadata, clock):
    stored = store.create_class(metadata, "demo-teacher")
    processing = worker(store, FlakyPipeline(failures=1), clock)
    processing.run_once()

    clock.advance(seconds=59)
    assert processing.run_once() is None
    clock.advance(seconds=1)
    job = processing.run_once()

    assert (job.state, job.attempt, job.error) == (JobState.READY_FOR_REVIEW, 2, None)
    assert store.get_result(stored.class_id) is not None


def test_waits_grow_and_the_last_attempt_fails_for_good(store, metadata, clock):
    stored = store.create_class(metadata, "demo-teacher")
    processing = worker(store, FlakyPipeline(failures=3), clock)

    assert processing.run_once().state is JobState.RETRY_WAIT  # attempt 1, waits 60 s
    clock.advance(seconds=60)
    assert processing.run_once().state is JobState.RETRY_WAIT  # attempt 2, waits 120 s
    clock.advance(seconds=119)
    assert processing.run_once() is None
    clock.advance(seconds=1)
    job = processing.run_once()

    assert (job.state, job.stage, job.attempt) == (JobState.FAILED, JobStage.TRANSCRIBING, 3)
    assert job.error.code is JobErrorCode.PROCESSING_UNAVAILABLE
    assert job.error.retryable is False
    assert store.get_result(stored.class_id) is None
    clock.advance(hours=1)
    assert processing.run_once() is None


def test_a_failure_that_is_not_transient_is_not_retried(store, metadata, clock):
    stored = store.create_class(metadata, "demo-teacher")
    error = PipelineError(JobErrorCode.INVALID_AUDIO, "El audio no se puede leer.")
    pipeline = FlakyPipeline(failures=1, stage=JobStage.NORMALIZING, error=error)

    job = worker(store, pipeline, clock).run_once()

    assert (job.state, job.attempt, job.error) == (JobState.FAILED, 1, error.error)
    clock.advance(hours=1)
    assert worker(store, pipeline, clock).run_once() is None
    assert store.get_result(stored.class_id) is None


def test_an_unexpected_error_is_not_retried(store, metadata, clock):
    store.create_class(metadata, "demo-teacher")
    pipeline = FlakyPipeline(failures=1, error=RuntimeError("fallo del código"))

    job = worker(store, pipeline, clock).run_once()

    assert job.state is JobState.FAILED
    assert job.error.code is JobErrorCode.PROCESSING_FAILED
    assert job.error.retryable is False


def test_a_single_attempt_fails_at_once(store, metadata, clock):
    store.create_class(metadata, "demo-teacher")

    job = worker(store, FlakyPipeline(failures=1), clock, max_attempts=1).run_once()

    assert (job.state, job.attempt) == (JobState.FAILED, 1)
    assert job.error.retryable is False


def test_at_start_a_job_with_attempts_left_is_requeued_and_finished(store, metadata, clock):
    stored = store.create_class(metadata, "demo-teacher")
    store.claim_next(clock())
    store.advance(stored.job_id, JobStage.DIARIZING)

    restarted = worker(store, FakePipeline(stage_seconds=0), clock)
    assert restarted.start() == 1
    job = restarted.run_once()

    assert (job.state, job.attempt) == (JobState.READY_FOR_REVIEW, 2)


def test_at_start_a_job_that_used_every_attempt_fails(store, metadata, clock):
    stored = store.create_class(metadata, "demo-teacher")
    processing = worker(store, FlakyPipeline(failures=2), clock)
    processing.run_once()
    clock.advance(seconds=60)
    processing.run_once()
    clock.advance(seconds=120)
    store.claim_next(clock())  # attempt 3, and the worker dies during it

    restarted = worker(store, FakePipeline(stage_seconds=0), clock)
    assert restarted.start() == 0

    job = store.get_job(stored.job_id)
    assert (job.state, job.attempt) == (JobState.FAILED, 3)
    assert job.error.code is JobErrorCode.PROCESSING_FAILED
    assert job.error.retryable is False
    assert restarted.run_once() is None


def test_a_job_waiting_for_a_retry_expires_and_is_not_claimed(store, metadata, clock):
    stored = store.create_class(metadata, "demo-teacher", audio=expired_audio())
    processing = worker(store, FlakyPipeline(failures=1), clock)
    assert processing.run_once().state is JobState.RETRY_WAIT

    clock.advance(minutes=1)
    processing.start()

    assert processing.run_once() is None
    expired = store.get_job(stored.job_id)
    assert (expired.state, expired.error) == (JobState.EXPIRED, None)


def test_a_store_failure_in_the_last_attempt_does_not_fail_the_job(metadata, clock):
    class BlinkingStore(InMemoryJobStore):
        """The database drops once while the last attempt records a stage."""

        def __init__(self) -> None:
            super().__init__()
            self.dropped = False

        def advance(self, job_id, stage):
            job = self.get_job(job_id)
            if job.attempt == 3 and stage is JobStage.DIARIZING and not self.dropped:
                self.dropped = True
                raise ConnectionError("database down")
            return super().advance(job_id, stage)

        def complete(self, job_id, result):
            done = super().complete(job_id, result)
            stop.set()
            return done

    stop = threading.Event()
    store = BlinkingStore()
    stored = store.create_class(metadata, "demo-teacher")
    processing = worker(store, FlakyPipeline(failures=2), clock)
    processing.run_once()
    clock.advance(seconds=60)
    processing.run_once()
    clock.advance(seconds=120)

    processing.run(stop, poll_seconds=0)  # restarts after the drop and finishes the job

    job = store.get_job(stored.job_id)
    assert (job.state, job.attempt) == (JobState.READY_FOR_REVIEW, 4)


def test_retry_logs_carry_the_job_stage_attempt_error_and_wait(metadata, clock, caplog):
    store = InMemoryJobStore()
    stored = store.create_class(metadata, "demo-teacher")
    formatter = JsonFormatter("worker")

    with caplog.at_level(logging.INFO, logger="app.worker"):
        worker(store, FlakyPipeline(failures=1), clock).run_once()

    entry = next(
        json.loads(formatter.format(record))
        for record in caplog.records
        if record.message == "job will be retried"
    )
    assert entry["job_id"] == stored.job_id
    assert (entry["stage"], entry["attempt"]) == ("transcribing", 1)
    assert (entry["error_code"], entry["wait_seconds"]) == ("processing_unavailable", 60)
    assert "El modelo" not in json.dumps(entry)
