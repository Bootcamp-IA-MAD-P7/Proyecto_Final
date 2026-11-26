"""Worker over every JobStore: in memory and, with TEST_DATABASE_URL, on PostgreSQL."""

import json
import logging
import threading
from datetime import UTC, datetime, timedelta

import pytest

from app.contract import (
    CONTRACT_VERSION,
    ClassMetadata,
    JobErrorCode,
    JobStage,
    JobState,
    PublicationStatus,
    ReviewStatus,
)
from app.inference import FakePipeline, PipelineError, PipelineOutput
from app.jobs import AudioAsset, InMemoryJobStore, JobStore, PostgresJobStore
from app.logs import JsonFormatter
from app.worker import Worker
from tests.conftest import load_fixture

NOW = datetime(2026, 11, 25, 10, 0, tzinfo=UTC)


@pytest.fixture(params=["memory", "postgres"])
def store(request) -> JobStore:
    if request.param == "memory":
        return InMemoryJobStore()
    return PostgresJobStore(request.getfixturevalue("pg"))


@pytest.fixture
def metadata() -> ClassMetadata:
    return ClassMetadata.model_validate(load_fixture("valid/class-metadata.json"))


def worker(store: JobStore, pipeline=None) -> Worker:
    return Worker(store, pipeline or FakePipeline(), timedelta(hours=24), clock=lambda: NOW)


class FailingPipeline:
    """Fails when a stage starts, as a real model could."""

    def __init__(self, at: JobStage, error: Exception) -> None:
        self.at = at
        self.error = error

    def run(self, job_input, on_stage) -> PipelineOutput:
        for stage in JobStage:
            on_stage(stage)
            if stage == self.at:
                raise self.error
        raise AssertionError("unreachable")


class RecordingStore(InMemoryJobStore):
    """Records the stage of the job each time it is read, to see the progress."""

    def __init__(self) -> None:
        super().__init__()
        self.stages: list[JobStage] = []

    def advance(self, job_id, stage):
        job = super().advance(job_id, stage)
        self.stages.append(job.stage)
        return job


class ExpiringStore(InMemoryJobStore):
    """Expires the job just before the worker saves the result (a late maintenance cycle)."""

    def complete(self, job_id, result):
        self.expire_jobs(NOW)
        return super().complete(job_id, result)


class ExpiringOnAdvanceStore(InMemoryJobStore):
    """Expires the job while a stage is being recorded (maintenance ran mid-pipeline)."""

    def advance(self, job_id, stage):
        self.expire_jobs(NOW)
        return super().advance(job_id, stage)


def expired_audio() -> AudioAsset:
    received_at = datetime(2026, 11, 20, 12, tzinfo=UTC)
    return AudioAsset(
        audio_id="audio-old",
        storage_key="audio-old",
        format="opus",
        size_bytes=1024,
        duration_seconds=60,
        sha256="a" * 64,
        received_at=received_at,
        expires_at=datetime(2026, 11, 21, 12, tzinfo=UTC),
    )


def test_does_not_claim_an_expired_job(metadata):
    store = InMemoryJobStore()
    store.create_class(metadata, "demo-teacher", audio=expired_audio())
    store.expire_jobs(NOW)

    assert worker(store).run_once() is None


def test_discards_a_result_that_arrived_after_the_job_expired(metadata, caplog):
    store = ExpiringStore()
    stored = store.create_class(metadata, "demo-teacher", audio=expired_audio())

    with caplog.at_level(logging.INFO, logger="app.worker"):
        done = worker(store).run_once()

    assert done.state is JobState.EXPIRED
    assert store.get_result(stored.class_id) is None
    assert "expired job result discarded" in [record.message for record in caplog.records]


def test_discards_a_job_that_expired_during_a_stage(metadata, caplog):
    store = ExpiringOnAdvanceStore()
    stored = store.create_class(metadata, "demo-teacher", audio=expired_audio())

    with caplog.at_level(logging.INFO, logger="app.worker"):
        done = worker(store).run_once()

    assert done.state is JobState.EXPIRED
    assert store.get_result(stored.class_id) is None
    assert "expired job result discarded" in [record.message for record in caplog.records]


def test_a_job_with_expired_audio_is_not_resumed_after_a_restart(metadata):
    store = InMemoryJobStore()
    stored = store.create_class(metadata, "demo-teacher", audio=expired_audio())
    job = store.claim_next()
    restarted = worker(store)

    assert restarted.start() == 0
    assert store.get_job(job.job_id).state is JobState.EXPIRED
    assert restarted.run_once() is None
    assert store.get_result(stored.class_id) is None


def test_takes_a_queued_job_through_every_stage_to_ready_for_review(metadata):
    store = RecordingStore()
    stored = store.create_class(metadata, "demo-teacher")

    job = worker(store).run_once()

    assert job.job_id == stored.job_id
    assert job.state is JobState.READY_FOR_REVIEW
    assert store.stages == list(JobStage)
    assert store.get_job(stored.job_id) == job


def test_saves_a_first_draft_that_complies_with_the_contract(store, metadata):
    stored = store.create_class(metadata, "demo-teacher")

    worker(store).run_once()

    result = store.get_result(stored.class_id)
    draft = load_fixture("valid/result-draft.json")
    assert result.class_id == stored.class_id
    assert result.schema_version == CONTRACT_VERSION
    assert result.result_version == 1
    assert result.review.status is ReviewStatus.PENDING
    assert result.review.review_due_at == NOW + timedelta(hours=24)
    assert result.publication.status is PublicationStatus.UNPUBLISHED
    assert result.transcript.model_dump(mode="json", exclude_unset=True) == draft["transcript"]
    assert result.analysis.model_dump(mode="json", exclude_unset=True) == draft["analysis"]


def test_with_an_empty_queue_does_nothing(store):
    assert worker(store).run_once() is None


def test_processes_jobs_in_the_order_they_arrived(store, metadata):
    first = store.create_class(metadata, "demo-teacher")
    second = store.create_class(metadata, "demo-teacher")
    processing = worker(store)

    assert processing.run_once().job_id == first.job_id
    assert processing.run_once().job_id == second.job_id


def test_a_failed_stage_leaves_the_job_failed_without_a_result(store, metadata):
    stored = store.create_class(metadata, "demo-teacher")
    error = PipelineError(JobErrorCode.INVALID_AUDIO, "El audio no se puede leer.")

    job = worker(store, FailingPipeline(JobStage.TRANSCRIBING, error)).run_once()

    assert job.state is JobState.FAILED
    assert job.stage is JobStage.TRANSCRIBING
    assert job.error == error.error
    assert store.get_result(stored.class_id) is None


def test_an_unexpected_error_fails_with_a_generic_contract_error(store, metadata):
    stored = store.create_class(metadata, "demo-teacher")
    pipeline = FailingPipeline(JobStage.ANALYZING, RuntimeError("Ana dijo algo privado"))

    job = worker(store, pipeline).run_once()

    assert job.state is JobState.FAILED
    assert job.error.code is JobErrorCode.PROCESSING_FAILED
    assert "Ana" not in job.error.message
    assert store.get_result(stored.class_id) is None


def test_an_output_that_breaks_the_contract_fails_without_a_result(store, metadata):
    stored = store.create_class(metadata, "demo-teacher")

    class InvalidPipeline:
        def run(self, job_input, on_stage):
            output = FakePipeline().run(job_input, on_stage)
            return PipelineOutput(transcript=output.transcript, analysis={"items": []})

    job = worker(store, InvalidPipeline()).run_once()

    assert job.state is JobState.FAILED
    assert job.error.code is JobErrorCode.PROCESSING_FAILED
    assert store.get_result(stored.class_id) is None


def test_at_start_returns_jobs_in_progress_to_the_queue_and_finishes_them(store, metadata):
    stored = store.create_class(metadata, "demo-teacher")
    store.claim_next()
    store.advance(stored.job_id, JobStage.DIARIZING)

    restarted = worker(store)
    assert restarted.start() == 1
    job = restarted.run_once()

    assert job.state is JobState.READY_FOR_REVIEW
    assert job.attempt == 2


def test_logs_that_it_is_ready_and_how_many_jobs_it_requeued(metadata, caplog):
    store = InMemoryJobStore()
    store.create_class(metadata, "demo-teacher")
    store.claim_next()

    with caplog.at_level(logging.INFO, logger="app.worker"):
        worker(store).start()

    ready = next(record for record in caplog.records if record.message == "worker ready")
    assert ready.count == 1


def test_logs_carry_ids_but_no_names_transcripts_or_tokens(metadata, caplog):
    store = InMemoryJobStore()
    store.create_class(metadata, "demo-teacher")
    store.create_class(metadata, "demo-teacher")
    failing = FailingPipeline(JobStage.ANALYZING, RuntimeError("Bearer secret-token"))
    formatter = JsonFormatter("worker")
    names = [p.display_name for p in metadata.participants if p.display_name]
    texts = [s["text"] for s in load_fixture("valid/result-draft.json")["transcript"]["segments"]]

    with caplog.at_level(logging.INFO, logger="app.worker"):
        worker(store).start()
        worker(store).run_once()
        worker(store, failing).run_once()

    lines = [formatter.format(record) for record in caplog.records]
    assert any(json.loads(line).get("job_id") for line in lines)
    for line in lines:
        for private in [*names, *texts, "secret-token", metadata.consent_reference]:
            assert private not in line


def test_run_processes_until_stopped_and_survives_an_unavailable_store(metadata):
    class FlakyStore(InMemoryJobStore):
        def __init__(self) -> None:
            super().__init__()
            self.calls = 0

        def claim_next(self):
            self.calls += 1
            if self.calls == 1:
                raise ConnectionError("database down")
            return super().claim_next()

    class StopWhenDone(FlakyStore):
        def complete(self, job_id, result):
            done = super().complete(job_id, result)
            stop.set()
            return done

    stop = threading.Event()
    store = StopWhenDone()
    stored = store.create_class(metadata, "demo-teacher")

    thread = threading.Thread(target=worker(store).run, args=(stop, 0.01))
    thread.start()
    thread.join(timeout=5)

    assert not thread.is_alive()
    assert store.calls == 2
    assert store.get_job(stored.job_id).state is JobState.READY_FOR_REVIEW


def test_a_store_failure_during_a_stage_does_not_fail_the_job(metadata):
    class BlinkingStore(InMemoryJobStore):
        """The database drops once while the pipeline records a stage, then comes back."""

        def __init__(self) -> None:
            super().__init__()
            self.dropped = False

        def advance(self, job_id, stage):
            if stage is JobStage.DIARIZING and not self.dropped:
                self.dropped = True
                raise ConnectionError("database down")
            return super().advance(job_id, stage)

    store = BlinkingStore()
    stored = store.create_class(metadata, "demo-teacher")
    processing = worker(store)

    with pytest.raises(ConnectionError):
        processing.run_once()
    assert store.get_job(stored.job_id).state is not JobState.FAILED

    processing.start()
    job = processing.run_once()

    assert job.state is JobState.READY_FOR_REVIEW
    assert job.attempt == 2
